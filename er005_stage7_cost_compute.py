# ============================================================
# er005_stage7_cost_compute.py
# ER-005-COST-BASELINE-01: Stage 7(raw usage log + pricing snapshotからのCost集計)
# ============================================================
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

LOG_PATH = "er005_output/cost_baseline_01/raw_usage_log.jsonl"
PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"

with open(LOG_PATH, encoding="utf-8") as f:
    RECORDS = [json.loads(l) for l in f]
with open(PRICING_PATH, encoding="utf-8") as f:
    PRICING = json.load(f)["prices"]


def price_lookup(provider, model, meter):
    for p in PRICING:
        if p["provider"] == provider and p["meter"] == meter and (
            model is None or p["model"] == model or model in p["model"]
        ):
            return p
    return None


OPENAI_IN = price_lookup("openai", "gpt-5.6-sol", "input_tokens")
OPENAI_CACHED = price_lookup("openai", "gpt-5.6-sol", "cached_input_tokens")
OPENAI_OUT = price_lookup("openai", "gpt-5.6-sol", "output_tokens")
OPENAI_SEARCH = price_lookup("openai", None, "web_search_call")
GEMINI_IN = price_lookup("gemini", "gemini-2.5-pro-preview-tts", "input_tokens")
GEMINI_OUT = price_lookup("gemini", "gemini-2.5-pro-preview-tts", "output_tokens")
AZURE_HOUR = price_lookup("azure", None, "audio_hour")

# ER-008-N8-FINAL-CLOSEOUT-24で発見: 本モジュールはER-005-COST-BASELINE-01
# 当時(gpt-5.6-solのみ使用)のraw_usage_logを前提に、OPENAI_IN/OUT/CACHEDを
# "gpt-5.6-sol"の単価に固定していた。ER-006-MODEL-ROUTING-CONTRACT-01以降、
# Writer/Fact Checker/Deviation Check等はApproved Model(gpt-5.6-luna、
# 入力$0.2/M・出力$1.2M、sol比で概ね1/25)へ切り替わったため、このモジュールを
# sol以外のrecord(model_id="gpt-5.6-luna"等)へ流用すると、生成costがおよそ
# 25倍過大になる(No.8/ER-23の過去のcost試算で実際にこの過大値が使われて
# いたことをER-24監査で確認した)。record_cost()は各recordのmodel_idで
# 都度価格を引き直すよう修正し、sol専用の値だったOPENAI_IN等は「model_id
# フィールドが無い古いrecord」向けのfallbackとしてのみ残す(ER-005当時の
# 呼び出し結果は変わらない、後方互換)。
def _openai_prices_for_model(model_id: str | None):
    if model_id:
        in_p = price_lookup("openai", model_id, "input_tokens")
        cached_p = price_lookup("openai", model_id, "cached_input_tokens")
        out_p = price_lookup("openai", model_id, "output_tokens")
        if in_p and out_p:
            return in_p, cached_p or OPENAI_CACHED, out_p
    return OPENAI_IN, OPENAI_CACHED, OPENAI_OUT


def record_cost(r: dict) -> tuple[float, float]:
    """(generation_cost, search_tool_cost) をUSDで返す。失敗callはusageが無いので0。"""
    if not r.get("success"):
        return 0.0, 0.0
    provider = r["provider"]
    if provider == "openai":
        input_tokens = r.get("input_tokens") or 0
        cached = r.get("cached_input_tokens") or 0
        output_tokens = r.get("output_tokens") or 0
        in_price, cached_price, out_price = _openai_prices_for_model(r.get("model_id"))
        billable_input = max(input_tokens - cached, 0)
        cost = (billable_input / 1_000_000) * in_price["price"]
        cost += (cached / 1_000_000) * cached_price["price"]
        cost += (output_tokens / 1_000_000) * out_price["price"]
        search_calls = r.get("web_search_call_count") or 0
        search_cost = (search_calls / 1000) * OPENAI_SEARCH["price"]
        return cost, search_cost
    if provider == "gemini":
        input_tokens = r.get("input_tokens") or 0
        output_tokens = r.get("output_tokens") or 0
        cost = (input_tokens / 1_000_000) * GEMINI_IN["price"]
        cost += (output_tokens / 1_000_000) * GEMINI_OUT["price"]
        return cost, 0.0
    if provider == "azure":
        seconds = r.get("audio_duration_submitted_seconds") or 0
        cost = (seconds / 3600) * AZURE_HOUR["price"]
        return cost, 0.0
    return 0.0, 0.0


# ER-008-N8-CLOSEOUT-GOVERNANCE-25: ユーザー決定により、今後Claudeがユーザーへ
# 提示するコストは円ベースを主表示とする(1 USD = 160円固定換算)。この値は
# 既に`er006_pool_pilot_01_cost_time_compute.py`/`compute_topic_cost.py`が
# 個別に使っていたレートと同一(そちらとの整合を取り、本モジュールを
# 円換算のSSOTとする)。単価表・トークン集計ロジックそのものは変更しない。
USD_TO_JPY = 160.0


def usd_to_jpy(usd: float) -> float:
    """USD建てのコストを円へ換算する(1 USD = 160円固定)。"""
    return usd * USD_TO_JPY


# ============================================================
# KEPT (final, on-topic, quota-working) vs DISCARDED_OVERHEAD の分類
# ============================================================
# Research系: theme+stageごとに最後のrecordだけKEPT(topic引数バグ+テーマ非依存
# template化以前の汚染callは全て破棄)
# TTS/ASR系: AKB48は単発run(全KEPT)。ParentingはAzureクォータ枯渇で1回目が
# 全滅したため、実測したtimestamp gapを境に2回目(クォータ回復後)だけKEPT。
def classify_kept(records: list[dict]) -> list[bool]:
    kept = [False] * len(records)
    by_group = defaultdict(list)
    for i, r in enumerate(records):
        by_group[(r["theme"], r["stage"])].append(i)

    for (theme, stage), idxs in by_group.items():
        idxs_sorted = sorted(idxs, key=lambda i: records[i]["timestamp"])
        if stage in ("research_ledger_draft", "research_ledger_verification"):
            # 最後の1件だけKEPT(テーマ非依存Template修正後の再実行)
            kept[idxs_sorted[-1]] = True
        elif stage in ("b1_tts_asr", "a2_tts_asr") and theme == "parenting":
            # 実測タイムスタンプの大きなgapを境に、gap後だけKEPT
            cutoff = None
            for j in range(1, len(idxs_sorted)):
                t0 = datetime.fromisoformat(records[idxs_sorted[j - 1]]["timestamp"])
                t1 = datetime.fromisoformat(records[idxs_sorted[j]]["timestamp"])
                if (t1 - t0).total_seconds() > 3000:  # 50分以上のgap = quota障害の境界
                    cutoff = j
            if cutoff is not None:
                for j in range(cutoff, len(idxs_sorted)):
                    kept[idxs_sorted[j]] = True
            else:
                for j in idxs_sorted:
                    kept[j] = True
        else:
            # AKB48 TTS/ASR、Writer/FactQA、Support、Key Phraseは単発runなので全件KEPT
            for j in idxs_sorted:
                kept[j] = True
    return kept


KEPT = classify_kept(RECORDS)

# ============================================================
# KEPT内でのローカルattempt番号(theme,stage,provider,api単位)を振り直す
# (Clean-run = ローカルattempt=1のみ)
# ============================================================
local_attempt = {}
LOCAL_ATTEMPT_NO = [None] * len(RECORDS)
kept_indices_sorted = sorted(
    [i for i in range(len(RECORDS)) if KEPT[i]],
    key=lambda i: RECORDS[i]["timestamp"],
)
for i in kept_indices_sorted:
    r = RECORDS[i]
    key = (r["theme"], r["stage"], r["provider"], r.get("api"))
    local_attempt[key] = local_attempt.get(key, 0) + 1
    LOCAL_ATTEMPT_NO[i] = local_attempt[key]

# ============================================================
# Stage名 -> Shared/B1/A2 カテゴリ分類
# ============================================================
def category_of(stage: str) -> str:
    if stage.startswith("research_ledger"):
        return "shared"
    if stage.startswith("b1_"):
        return "b1"
    if stage.startswith("a2_"):
        return "a2"
    return "other"


def cost_type_of(record: dict) -> str:
    stage = record["stage"]
    provider = record["provider"]
    if stage.startswith("research_ledger"):
        return "llm"
    if provider == "gemini":
        return "tts"
    if provider == "azure":
        return "asr"
    return "llm"


# ============================================================
# 集計
# ============================================================
summary = defaultdict(lambda: defaultdict(float))
overhead_summary = defaultdict(lambda: defaultdict(float))
retry_overhead_summary = defaultdict(lambda: defaultdict(float))
call_counts = defaultdict(lambda: defaultdict(int))
discarded_call_counts = defaultdict(lambda: defaultdict(int))
retry_call_counts = defaultdict(lambda: defaultdict(int))

for i, r in enumerate(RECORDS):
    gen_cost, search_cost = record_cost(r)
    total_cost = gen_cost + search_cost
    theme = r["theme"]
    cat = category_of(r["stage"])
    ctype = cost_type_of(r)

    if not KEPT[i]:
        overhead_summary[theme]["template_or_quota_overhead_usd"] += total_cost
        discarded_call_counts[theme]["discarded_calls"] += 1
        continue

    key = f"{cat}_{ctype}"
    summary[theme][key] += total_cost
    if search_cost:
        summary[theme]["search_grounding"] += search_cost
    call_counts[theme][key] += 1

    if LOCAL_ATTEMPT_NO[i] and LOCAL_ATTEMPT_NO[i] > 1:
        retry_overhead_summary[theme][key] += total_cost
        retry_call_counts[theme][key] += 1

# ============================================================
# Clean-run cost(KEPT内の各theme/stage/provider/apiでlocal_attempt=1のみ)
# ============================================================
clean_summary = defaultdict(lambda: defaultdict(float))
for i, r in enumerate(RECORDS):
    if not KEPT[i]:
        continue
    if LOCAL_ATTEMPT_NO[i] != 1:
        continue
    gen_cost, search_cost = record_cost(r)
    total_cost = gen_cost + search_cost
    theme = r["theme"]
    cat = category_of(r["stage"])
    ctype = cost_type_of(r)
    key = f"{cat}_{ctype}"
    clean_summary[theme][key] += total_cost
    if search_cost:
        clean_summary[theme]["search_grounding"] += search_cost

# ============================================================
# 出力
# ============================================================
output = {
    "pricing_checked_date": PRICING and __import__("json").load(open(PRICING_PATH, encoding="utf-8"))["checked_date"],
    "actual_cost_by_theme": {t: dict(v) for t, v in summary.items()},
    "clean_run_cost_by_theme": {t: dict(v) for t, v in clean_summary.items()},
    "template_or_quota_overhead_by_theme": {t: dict(v) for t, v in overhead_summary.items()},
    "retry_overhead_by_theme": {t: dict(v) for t, v in retry_overhead_summary.items()},
    "call_counts_kept": {t: dict(v) for t, v in call_counts.items()},
    "discarded_call_counts": {t: dict(v) for t, v in discarded_call_counts.items()},
    "retry_call_counts": {t: dict(v) for t, v in retry_call_counts.items()},
}

for theme in ["akb48", "parenting"]:
    actual_total = sum(summary[theme].values())
    clean_total = sum(clean_summary[theme].values())
    output.setdefault("totals", {})[theme] = {
        "actual_total_usd": round(actual_total, 4),
        "clean_run_total_usd": round(clean_total, 4),
        "retry_overhead_usd": round(actual_total - clean_total, 4),
        "retry_overhead_pct": round((actual_total - clean_total) / actual_total * 100, 2) if actual_total else 0,
        "template_or_quota_overhead_usd": round(sum(overhead_summary[theme].values()), 4),
    }

with open("er005_output/cost_baseline_01/cost_summary.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(json.dumps(output["totals"], indent=2))
