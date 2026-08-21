# ============================================================
# er006_pool_pilot_01_cost_time_compute.py
# ER-006-POOL-PILOT-01: raw_usage_log.jsonl -> Cost/Time集計
# ============================================================
# 単価はer005_llm_cost_structure_r1.py・cost_baseline_01/pricing_snapshot.json
# (共に本セッション内の既存Cost分析タスクで使用・確認済み)と同一の値を再利用する。
#   openai gpt-5.6-luna: input $0.20/1M, cached $0.02/1M, output $1.20/1M
#   gemini gemini-2.5-pro-preview-tts: input $1.00/1M, output $20.00/1M
#   azure  Speech-to-Text: $1.00/hour
# 為替は1USD=160円(タスク仕様で指定)固定。
#
# Actual Cost = ログに残る全callの実費用(discardなし、実際に支払った金額)。
# 「Clean」の定義: 各theme+stageを実行タイムスタンプのgapで「サブラン」に分割し、
# 最後(最終的に採用された)サブランのみを対象とする。サブラン内でさらに
# 同一provider/api呼び出しが複数回連続する場合(ASR再試行等)はlocal_attempt>1として
# Retry-Fallback Waste側に計上する。
#   - 最終サブラン以外の全costは Article-specific Rewrite Waste
#     (Topic1: Wikipedia出典修正によるResearch再実行、
#      Topic2: FTC Click-to-Cancel Rule失効の反映によるResearch再実行)
#   - 最終サブラン内でlocal_attempt>1のcostは Retry-Fallback Waste
#     (TTS/ASR検証ループ等、本番パイプライン設計内の再試行)
# Operator-error Waste(JAPANESE_TITLES KeyErrorによるA2 TTS再実行)は
# タイムスタンプ照合で個別に特定し、Retry-Fallback Wasteから除外して計上する。
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

USD_JPY = 160.0
LOG_PATH = "er006_output/pool_pilot_01/raw_usage_log.jsonl"

LUNA_IN, LUNA_CACHED, LUNA_OUT = 0.20, 0.02, 1.20
SOL_IN, SOL_CACHED, SOL_OUT = 5.00, 0.50, 30.00
GEMINI_IN, GEMINI_OUT = 1.00, 20.00
AZURE_HOUR = 1.00
SEARCH_PER_1K = 10.00

GAP_THRESHOLD_SECONDS = {
    "research_evidence_pack": 120, "research_vfl": 120, "research_verification": 120,
    "writer_b1": 300, "writer_a2": 300,
    "support_b1": 200, "support_a2": 200,
    "tts_b1": 90, "tts_a2": 90,
}

THEMES = ["pool_benches", "pool_subscriptions", "pool_startups"]


def record_cost_usd(r: dict) -> tuple[float, float]:
    if not r.get("success"):
        return 0.0, 0.0
    provider = r["provider"]
    if provider == "openai":
        it = r.get("input_tokens") or 0
        ct = r.get("cached_input_tokens") or 0
        ot = r.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        # ER-006-POOL-PREPROD-HARDENING-01で発見: raw_usage_logのmodel_idを見ると、
        # Writer段階は全てgpt-5.6-sol(本番Fact Checker、web_search対応)であり、
        # Support段階もscaffold/key phrase生成の大半がSolだった(Luna専用と誤って
        # 決め打ちしていた)。model_id別に単価を分岐する(以前はLuna単価固定で
        # 計算しており、Sol呼び出し分のCostを約25倍過小評価していた)。
        model_id = r.get("model_id") or ""
        if "sol" in model_id:
            in_price, cached_price, out_price = SOL_IN, SOL_CACHED, SOL_OUT
        else:
            in_price, cached_price, out_price = LUNA_IN, LUNA_CACHED, LUNA_OUT
        cost = (billable_in / 1_000_000) * in_price + (ct / 1_000_000) * cached_price + (ot / 1_000_000) * out_price
        search_calls = r.get("web_search_call_count") or 0
        search_cost = (search_calls / 1000) * SEARCH_PER_1K
        return cost, search_cost
    if provider == "gemini":
        it = r.get("input_tokens") or 0
        ot = r.get("output_tokens") or 0
        cost = (it / 1_000_000) * GEMINI_IN + (ot / 1_000_000) * GEMINI_OUT
        return cost, 0.0
    if provider == "azure":
        sec = r.get("audio_duration_submitted_seconds") or 0
        cost = (sec / 3600) * AZURE_HOUR
        return cost, 0.0
    return 0.0, 0.0


def level_of(stage: str) -> str:
    if stage.startswith("research_"):
        return "shared"
    if stage.endswith("_b1"):
        return "b1"
    if stage.endswith("_a2"):
        return "a2"
    return "other"


def ctype_of(stage: str, provider: str) -> str:
    if stage.startswith("research_"):
        return "research_llm"
    if stage.startswith("writer_"):
        return "writer_llm"
    if stage.startswith("support_"):
        return "support_llm"
    if stage.startswith("tts_"):
        return "tts" if provider == "gemini" else "asr" if provider == "azure" else "tts_other"
    return "other"


with open(LOG_PATH, encoding="utf-8") as f:
    RECORDS = [json.loads(l) for l in f]

for r in RECORDS:
    gen, search = record_cost_usd(r)
    r["_cost_usd"] = gen + search
    r["_cost_jpy"] = (gen + search) * USD_JPY

by_theme_stage = defaultdict(list)
for i, r in enumerate(RECORDS):
    by_theme_stage[(r["theme"], r["stage"])].append(i)

# サブラン分割(gapベース)
subrun_id = [None] * len(RECORDS)
subrun_count = {}
for (theme, stage), idxs in by_theme_stage.items():
    idxs_sorted = sorted(idxs, key=lambda i: RECORDS[i]["timestamp"])
    threshold = GAP_THRESHOLD_SECONDS.get(stage, 180)
    cur_run = 0
    subrun_id[idxs_sorted[0]] = 0
    for j in range(1, len(idxs_sorted)):
        t0 = datetime.fromisoformat(RECORDS[idxs_sorted[j - 1]]["timestamp"])
        t1 = datetime.fromisoformat(RECORDS[idxs_sorted[j]]["timestamp"])
        if (t1 - t0).total_seconds() > threshold:
            cur_run += 1
        subrun_id[idxs_sorted[j]] = cur_run
    subrun_count[(theme, stage)] = cur_run + 1

# Operator-error検知: pool_benches/tts_a2の最初のサブラン(KeyErrorで中断した回)
operator_error_idx = set()
if ("pool_benches", "tts_a2") in by_theme_stage:
    idxs = by_theme_stage[("pool_benches", "tts_a2")]
    idxs_sorted = sorted(idxs, key=lambda i: RECORDS[i]["timestamp"])
    first_run_ids = [i for i in idxs_sorted if subrun_id[i] == 0]
    # 最初のサブランが1〜2件だけ(topic_intro生成直後にKeyErrorでクラッシュ)なら
    # Operator-error(JAPANESE_TITLES未登録によるクラッシュ)として分離する
    if 0 < len(first_run_ids) <= 3 and subrun_count[("pool_benches", "tts_a2")] > 1:
        operator_error_idx.update(first_run_ids)

actual = defaultdict(float)
clean = defaultdict(float)
rewrite_waste = defaultdict(float)
retry_waste = defaultdict(float)
operator_waste = defaultdict(float)
call_counts = defaultdict(int)

for i, r in enumerate(RECORDS):
    theme, stage, provider = r["theme"], r["stage"], r["provider"]
    level = level_of(stage)
    ctype = ctype_of(stage, provider)
    key = (theme, level, ctype)
    cost = r["_cost_jpy"]

    actual[key] += cost
    call_counts[key] += 1

    n_subruns = subrun_count[(theme, stage)]
    is_last_subrun = (subrun_id[i] == n_subruns - 1)

    if i in operator_error_idx:
        operator_waste[key] += cost
        continue

    if not is_last_subrun:
        rewrite_waste[key] += cost
        continue

    clean_within_run_key = (theme, stage, provider, r.get("api"), subrun_id[i])
    clean[key] += cost  # 後でlocal_attemptベースで再分割
    call_counts[key] += 0  # no-op, keep structure

# ------------------------------------------------------------
# research_*/writer_*/support_* (LLM系、呼び出し回数が少なく1呼び出し=1意味のある
# 処理ステップ): 最終サブラン内でのlocal_attempt(theme,stage,provider,api,subrun)
# 単位の初回のみCleanとする。この手法はtts_*には使わない(下記の注記参照)。
# ------------------------------------------------------------
local_attempt = defaultdict(int)
clean2 = defaultdict(float)
retry2 = defaultdict(float)
for i, r in enumerate(RECORDS):
    theme, stage, provider = r["theme"], r["stage"], r["provider"]
    if stage.startswith("tts_"):
        continue  # TTS/ASRは下のブロックで別手法により算出する
    if i in operator_error_idx:
        continue
    n_subruns = subrun_count[(theme, stage)]
    if subrun_id[i] != n_subruns - 1:
        continue
    lkey = (theme, stage, provider, r.get("api"), subrun_id[i])
    local_attempt[lkey] += 1
    level = level_of(stage)
    ctype = ctype_of(stage, provider)
    key = (theme, level, ctype)
    if local_attempt[lkey] == 1:
        clean2[key] += r["_cost_jpy"]
    else:
        retry2[key] += r["_cost_jpy"]

# ------------------------------------------------------------
# tts_b1/tts_a2: raw_usage_log.jsonlにはsegment名(topic_intro/comment_1等)が
# 記録されておらず、"attempt_number"はセグメントをまたいだ通し番号(段落Aの1回目の
# 試行も、段落Bの1回目の試行も、ログ上は連番の別attemptとして記録される)である
# ことをprintログとの突き合わせで確認済み。そのため、Research/Writer/Supportと
# 同じ「local_attempt==1のみClean」手法をtts_*にそのまま適用すると、"別セグメントの
# 初回呼び出し"まで丸ごとRetry-Waste扱いになってしまい、過大評価になる(実際に
# 検証中に発生したバグ)。
#
# 正確なセグメント単位の再試行回数は、この生ログだけでは復元できない
# (produciton側がcl.record()にsegment名を渡していないため)。そのため、tts_*の
# Clean/Waste分離は「1セグメントにつきTTS 1回+ASR 1回」を理論上のClean最小値と
# みなす推定(ESTIMATE、実測ではない)で行う。実測なのはActual Cost(全呼び出しの
# 合計)のみ。
N_SEGMENTS = {
    ("pool_benches", "b1"): 23, ("pool_benches", "a2"): 24,
    ("pool_subscriptions", "b1"): 23, ("pool_subscriptions", "a2"): 24,
    ("pool_startups", "b1"): 23, ("pool_startups", "a2"): 24,
}
tts_asr_estimate = {}
for (theme, tts_stage) in [(t, s) for t in THEMES for s in ("tts_b1", "tts_a2")]:
    level = "b1" if tts_stage == "tts_b1" else "a2"
    n_seg = N_SEGMENTS[(theme, level)]
    idxs = by_theme_stage.get((theme, tts_stage), [])
    gemini_idxs = [i for i in idxs if RECORDS[i]["provider"] == "gemini" and i not in operator_error_idx]
    azure_idxs = [i for i in idxs if RECORDS[i]["provider"] == "azure" and i not in operator_error_idx]
    gemini_actual_calls, azure_actual_calls = len(gemini_idxs), len(azure_idxs)
    gemini_actual_cost = sum(RECORDS[i]["_cost_jpy"] for i in gemini_idxs)
    azure_actual_cost = sum(RECORDS[i]["_cost_jpy"] for i in azure_idxs)
    # Clean推定 = セグメント数分の呼び出しのみで済んだ場合の按分コスト(平均単価×n_seg)
    gemini_clean_est = (gemini_actual_cost / gemini_actual_calls * n_seg) if gemini_actual_calls else 0
    azure_clean_est = (azure_actual_cost / azure_actual_calls * n_seg) if azure_actual_calls else 0
    gemini_clean_est = min(gemini_clean_est, gemini_actual_cost)
    azure_clean_est = min(azure_clean_est, azure_actual_cost)
    tts_asr_estimate[(theme, level, "tts")] = {
        "actual_jpy": round(gemini_actual_cost, 1), "actual_calls": gemini_actual_calls,
        "n_segments": n_seg,
        "clean_estimate_jpy": round(gemini_clean_est, 1),
        "retry_overhead_estimate_jpy": round(gemini_actual_cost - gemini_clean_est, 1),
    }
    tts_asr_estimate[(theme, level, "asr")] = {
        "actual_jpy": round(azure_actual_cost, 1), "actual_calls": azure_actual_calls,
        "n_segments": n_seg,
        "clean_estimate_jpy": round(azure_clean_est, 1),
        "retry_overhead_estimate_jpy": round(azure_actual_cost - azure_clean_est, 1),
    }
    clean2[(theme, level, "tts")] = gemini_clean_est
    clean2[(theme, level, "asr")] = azure_clean_est
    retry2[(theme, level, "tts")] = gemini_actual_cost - gemini_clean_est
    retry2[(theme, level, "asr")] = azure_actual_cost - azure_clean_est

clean = clean2
retry_waste = retry2


# ============================================================
# 出力
# ============================================================
result = {
    "usd_jpy_rate": USD_JPY,
    "per_theme_level_type": {},
    "totals_by_theme": {},
    "grand_total": {},
}

all_keys = set(actual) | set(clean) | set(rewrite_waste) | set(retry_waste) | set(operator_waste)
for key in sorted(all_keys):
    theme, level, ctype = key
    result["per_theme_level_type"].setdefault(theme, {})[f"{level}/{ctype}"] = {
        "actual_jpy": round(actual.get(key, 0), 1),
        "clean_jpy": round(clean.get(key, 0), 1),
        "rewrite_waste_jpy": round(rewrite_waste.get(key, 0), 1),
        "retry_fallback_waste_jpy": round(retry_waste.get(key, 0), 1),
        "operator_error_waste_jpy": round(operator_waste.get(key, 0), 1),
        "call_count": call_counts.get(key, 0),
    }

for theme in THEMES:
    keys = [k for k in all_keys if k[0] == theme]
    result["totals_by_theme"][theme] = {
        "actual_jpy": round(sum(actual.get(k, 0) for k in keys), 1),
        "clean_jpy": round(sum(clean.get(k, 0) for k in keys), 1),
        "rewrite_waste_jpy": round(sum(rewrite_waste.get(k, 0) for k in keys), 1),
        "retry_fallback_waste_jpy": round(sum(retry_waste.get(k, 0) for k in keys), 1),
        "operator_error_waste_jpy": round(sum(operator_waste.get(k, 0) for k in keys), 1),
        "shared_jpy": round(sum(actual.get(k, 0) for k in keys if k[1] == "shared"), 1),
        "b1_jpy": round(sum(actual.get(k, 0) for k in keys if k[1] == "b1"), 1),
        "a2_jpy": round(sum(actual.get(k, 0) for k in keys if k[1] == "a2"), 1),
    }
    shared = result["totals_by_theme"][theme]["shared_jpy"]
    b1 = result["totals_by_theme"][theme]["b1_jpy"]
    a2 = result["totals_by_theme"][theme]["a2_jpy"]
    result["totals_by_theme"][theme]["actual_pair_production_jpy"] = round(shared + b1 + a2, 1)
    result["totals_by_theme"][theme]["allocated_b1_episode_jpy"] = round(shared / 2 + b1, 1)
    result["totals_by_theme"][theme]["allocated_a2_episode_jpy"] = round(shared / 2 + a2, 1)

    # TTS/ASR個別(Clean/Actual/Waste、B1・A2別)
    for level in ["b1", "a2"]:
        for ctype in ["tts", "asr"]:
            k = (theme, level, ctype)
            result["totals_by_theme"][theme][f"{level}_{ctype}_actual_jpy"] = round(actual.get(k, 0), 1)
            result["totals_by_theme"][theme][f"{level}_{ctype}_clean_jpy"] = round(clean.get(k, 0), 1)
            result["totals_by_theme"][theme][f"{level}_{ctype}_retry_waste_jpy"] = round(retry_waste.get(k, 0), 1)
            result["totals_by_theme"][theme][f"{level}_{ctype}_operator_waste_jpy"] = round(operator_waste.get(k, 0), 1)

gt_actual = sum(v["actual_jpy"] for v in result["totals_by_theme"].values())
gt_clean = sum(v["clean_jpy"] for v in result["totals_by_theme"].values())
gt_rewrite = sum(v["rewrite_waste_jpy"] for v in result["totals_by_theme"].values())
gt_retry = sum(v["retry_fallback_waste_jpy"] for v in result["totals_by_theme"].values())
gt_operator = sum(v["operator_error_waste_jpy"] for v in result["totals_by_theme"].values())
result["grand_total"] = {
    "actual_jpy": round(gt_actual, 1),
    "clean_jpy": round(gt_clean, 1),
    "rewrite_waste_jpy": round(gt_rewrite, 1),
    "retry_fallback_waste_jpy": round(gt_retry, 1),
    "operator_error_waste_jpy": round(gt_operator, 1),
    "average_actual_pair_production_jpy": round(
        sum(v["actual_pair_production_jpy"] for v in result["totals_by_theme"].values()) / 3, 1),
    "min_pair_production_jpy": round(
        min(v["actual_pair_production_jpy"] for v in result["totals_by_theme"].values()), 1),
    "max_pair_production_jpy": round(
        max(v["actual_pair_production_jpy"] for v in result["totals_by_theme"].values()), 1),
}

result["subrun_counts"] = {f"{t}/{s}": n for (t, s), n in sorted(subrun_count.items())}
result["operator_error_call_indices"] = sorted(operator_error_idx)
result["tts_asr_retry_overhead_ESTIMATE"] = {
    f"{t}/{lvl}/{ctype}": v for (t, lvl, ctype), v in sorted(tts_asr_estimate.items())
}
result["_note_tts_asr_methodology"] = (
    "tts_b1/tts_a2のClean/Retry-Overheadはraw_usage_log.jsonlにsegment名が無いための推定値"
    "(1segmentにつきTTS1回+ASR1回を理論Clean最小値とし、平均単価×segment数で按分)。"
    "Actual Costのみ実測。Research/Writer/Supportのsubrun分割によるRewrite Waste判定は、"
    "呼び出し回数が少なく既知の再実行タイミングと整合するため実測に近い。"
)

with open("er006_output/pool_pilot_01/cost_time_summary.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps(result["totals_by_theme"], ensure_ascii=False, indent=2))
print("=== GRAND TOTAL ===")
print(json.dumps(result["grand_total"], ensure_ascii=False, indent=2))
print("=== SUBRUN COUNTS (2以上 = Article-specific Rewrite発生) ===")
print(json.dumps(result["subrun_counts"], ensure_ascii=False, indent=2))

# ============================================================
# Time集計(追記)
# ============================================================
import os

time_result = {}
for theme in THEMES:
    d = f"er006_output/pool_pilot_01/{theme}"
    research_t = json.load(open(f"{d}/research/research_timing.json", encoding="utf-8"))
    writer_t = json.load(open(f"{d}/writer_timing.json", encoding="utf-8"))
    support_t = json.load(open(f"{d}/support_timing.json", encoding="utf-8"))
    audio_path = f"{d}/audio_timing.json"
    if os.path.exists(audio_path):
        audio_t = json.load(open(audio_path, encoding="utf-8"))
    else:
        ts = defaultdict(list)
        for r in RECORDS:
            if r["theme"] == theme and r["stage"] in ("tts_b1", "tts_a2"):
                ts[r["stage"]].append(datetime.fromisoformat(r["timestamp"]))
        audio_t = {
            "tts_b1": round((max(ts["tts_b1"]) - min(ts["tts_b1"])).total_seconds(), 2) if ts["tts_b1"] else None,
            "tts_a2": round((max(ts["tts_a2"]) - min(ts["tts_a2"])).total_seconds(), 2) if ts["tts_a2"] else None,
            "assemble_b1": None, "assemble_a2": None,
            "_note": "audio_timing.jsonが無いためlog timestampのspanから再構成(assemble時間は他topic実績から2秒程度と推定)",
        }

    ts_all = [datetime.fromisoformat(r["timestamp"]) for r in RECORDS if r["theme"] == theme]
    observed_span_sec = (max(ts_all) - min(ts_all)).total_seconds()

    stage_sum_sec = (
        research_t["research_total_seconds"]
        + writer_t["writer_b1"] + writer_t["writer_a2"]
        + support_t["support_b1"] + support_t["support_a2"]
        + (audio_t["tts_b1"] or 0) + (audio_t["tts_a2"] or 0)
        + (audio_t.get("assemble_b1") or 2) + (audio_t.get("assemble_a2") or 2)
    )

    time_result[theme] = {
        "research_total_sec": research_t["research_total_seconds"],
        "writer_b1_sec": writer_t["writer_b1"], "writer_a2_sec": writer_t["writer_a2"],
        "support_b1_sec": support_t["support_b1"], "support_a2_sec": support_t["support_a2"],
        "tts_b1_sec": audio_t["tts_b1"], "tts_a2_sec": audio_t["tts_a2"],
        "assemble_b1_sec": audio_t.get("assemble_b1"), "assemble_a2_sec": audio_t.get("assemble_a2"),
        "stage_sum_sec_CLEAN_RUN_ONLY": round(stage_sum_sec, 1),
        "stage_sum_min_CLEAN_RUN_ONLY": round(stage_sum_sec / 60, 1),
        "observed_wall_clock_span_sec": round(observed_span_sec, 1),
        "observed_wall_clock_span_min": round(observed_span_sec / 60, 1),
    }

time_result["_note"] = (
    "stage_sum_*_CLEAN_RUN_ONLYは各ステージの最終(採用された)実行分のみの合計で、"
    "Article-specific Rewriteで破棄された1回目のResearch/Writer実行時間や、"
    "手動でのraw_sources.json修正作業時間、OpenAI API支出上限による中断待ち時間は含まない。"
    "observed_wall_clock_span_*は生ログの最初〜最後のtimestamp差(実測)だが、"
    "本Pilotでは「Topic1を先に単独でチェックポイント検証してからTopic2・3をまとめて処理」"
    "したため、3トピックの厳密な逐次(1トピックずつ完全に独立)処理ではない区間を含み、"
    "かつAPI支出上限による中断(ユーザー対応待ち)も含まれる。したがって今後の18トピック分の"
    "所要時間見積もりには、observed_wall_clock_spanよりstage_sum(CLEAN_RUN_ONLY)を基準にする方が"
    "妥当と考えられる。"
)

with open("er006_output/pool_pilot_01/time_summary.json", "w", encoding="utf-8") as f:
    json.dump(time_result, f, ensure_ascii=False, indent=2)

print("=== TIME SUMMARY ===")
print(json.dumps(time_result, ensure_ascii=False, indent=2))
