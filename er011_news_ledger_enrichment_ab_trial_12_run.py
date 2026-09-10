# ============================================================
# er011_news_ledger_enrichment_ab_trial_12_run.py
# FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12 (Lane A, Sonnet委任)
# ============================================================
# 目的(ユーザー確定 2026-09-10): News Stage4の論点H(Verified Fact
# Ledgerのfact供給量/evidence allocationがPoint対Full Story overlap NG・
# retry成功率に影響するか)を、Hanshin型(single_event_boxscore)題材で
# N=3テーマの交絡を解消する形で直接検証する。設計根拠:
# `FAMILY-A-NEWS-STAGE4-STATUS-REPORT-01_REPORT.md` 9節「候補A」、
# `FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01_REPORT.md`
# USER_DECISION_REQUIRED候補1。
#
# 条件A(current): 現行Hanshin Ledger(er003_output/n3_01/hanshin/research/
#   verified_fact_ledger.txt、既存FACT-01〜07、無変更・無編集)。
# 条件B(enriched): 条件Aの全文 + 追加調査で得た新規fact(FACT-08〜)を
#   末尾へ追記した別ファイル(このTrial専用の新規ファイル、既存ファイルは
#   一切変更しない)。新規factの取得はOpenAI Responses API web_search tool
#   (既存er002_ja_web_research_r3.pyのmake_writer_research_fn/
#   make_fact_checker_fnと同一メカニズム、無改変で直接呼び出し)。
#
# 両条件とも editorial_type_module_block="" / point_role_hint_block=""
# (Production既定のbaseline、Focus Module/hintなし)に固定し、Ledgerの
# 差分だけを検証変数にする(Trial-06のfocus_hint条件とは無関係、独立変数)。
#
# **Trial(Production実装ではない)**。Production/Prompt/QA/Validator/retry
# コード・SSOT編集・Git操作は一切行わない。monkeypatch・グローバル書き換え
# なし。TTSは実行しない(text-onlyまで)。
#
# 並列条件(委任文より): docs/pm/ACTIVE_TASK.md・RESULT_PACKET.md・
# OPEN_ITEMS.md・DECISION_LOG.md・CURRENT_SPEC.md・ARTIFACT_REGISTRY.md・
# Production Prompt・Productionコード・QA閾値は編集しない。Git操作をしない。
# バックグラウンド待機・ポーリングを仕掛けない(本ファイルのCLIはすべて
# 前面同期実行、combo単位で逐次呼び出す)。
#
# 再利用(import・無変更、コピー改変はしない):
#   - er011_point_role_planning_focus_connection_trial_03(t3、既存
#     VALIDATED Trial): run_one_pattern_connected / HANSHIN_LEDGER_PATH /
#     HANSHIN_TOPIC_JA / load_text / vfl01 / ab01 / r3(t3内でimport済み、
#     t3.r3経由で再利用)。
#   - er011_daily_news_focus_layer_comparison_trial_04(t4): analyze_run /
#     load_role_planning_used / LEVELS(A2/B1B instruction一式、無改変で
#     完全再利用)。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block /
#     build_prompt / compute_metrics。
#   - er005_cost_logger(cl): install / logging_context。
#
# 費用上限: ¥200(見込み¥60〜150)。超過見込み検知でSTOP(詳細は
# budget監視ロジック参照)。二重起動防止(前面同期のみ、バックグラウンド
# 待機なし)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict

import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_daily_news_focus_layer_comparison_trial_04 as t4
import er011_point_role_planning_focus_connection_trial_03 as t3

THEME_ID = "news_ledger_enrichment_ab_trial_12"
OUT_DIR = f"er011_output/{THEME_ID}"

N_PER_CONDITION = 3  # A2×3 + B1B×3 = 6 run/条件(N=6の定義、委任文どおり)
BUDGET_JPY = 200.0

CONDITION_A_LEDGER_PATH = t3.HANSHIN_LEDGER_PATH  # 既存ファイル、無変更
CONDITION_B_LEDGER_PATH = f"{OUT_DIR}/hanshin_ledger_condition_b_enriched.txt"  # 新規ファイル

# 条件A: 既存Ledgerの「usable(非DISPENSABLE)」fact数。既存監査
# (FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01)と同一定義
# (FACT-01〜05がANCHOR/SUPPORTING、FACT-06/07はDISPENSABLE)。
USABLE_FACT_COUNT_A = 5
# 条件B: 追加後の非DISPENSABLE fact数。research_stage()の結果(FACT-08〜14
# の7件、いずれもSUPPORTING)を確認しhanshin_ledger_condition_b_enriched.txt
# を作成した後の実測値(5+7=12、ファイル末尾の集計セクションと一致)。
USABLE_FACT_COUNT_B = 12

CONDITIONS = {
    "current": {
        "ledger_path": CONDITION_A_LEDGER_PATH,
        "usable_fact_count": USABLE_FACT_COUNT_A,
        "label_ja": "条件A: 現行Ledger(既存、無変更)",
    },
    "enriched": {
        "ledger_path": CONDITION_B_LEDGER_PATH,
        "usable_fact_count": USABLE_FACT_COUNT_B,
        "label_ja": "条件B: 拡充Ledger(条件A全文+新規fact追記)",
    },
}

LEVELS = t4.LEVELS  # [("B1B", instruction, "b1b", "writer_b1"), ("A2", ..., "a2", "writer_a2")]


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Stage 0: 条件B用の追加fact調査(web_search toolを使った実API呼び出し、
# 費用発生・cl.install()で計測)。既存er002_ja_web_research_r3.pyの
# make_writer_research_fn/make_fact_checker_fnと同一メカニズム
# (client.responses.create + tools=[{"type": "web_search"}])を、
# そのモジュールを改変せずこのTrialから直接呼び出す。
# ============================================================
RESEARCH_PROMPT = """あなたは事実確認を重視する調査アシスタントです。
2026年8月16日にマツダスタジアムで行われたプロ野球公式戦(広島東洋カープ
vs 阪神タイガース、最終スコア 広島1-阪神8)について、既に確定している
以下7つの事実(FACT-01〜07)には含まれていない追加の検証済み事実を、
Web検索で調査してください。

【既に確定済み・変更しないFact(参考、再掲不要、これらと重複する内容は
出力しないこと)】
FACT-01: 最終スコア 阪神8-広島1
FACT-02: 阪神1回、佐藤輝明のセンターへの2ランホームランで2点先制
FACT-03: 阪神先発・伊原陵人が5回2安打1失点(今季4勝目、2敗)
FACT-04: 広島の得点はE・モンテロの5回裏ソロホームランの1点のみ
FACT-05: 阪神は7回に坂本誠志郎・代打伏見寅威の適時打、8回に坂本の適時
  二塁打で加点
FACT-06: 敗戦投手は森翔平(今季1勝3敗)
FACT-07: 試合時間3時間5分、観客数31,645人

【調査してほしいこと】
上記に含まれない、この試合に関する追加の検証済み事実を、複数の独立した
情報源(NPB公式・球団公式・報道機関等)を確認しながら6件程度調査して
ください。例えば次のような切り口が考えられます(必須ではなく例示、
実際にWebで確認できたものだけを採用してください):
- 伊原陵人・森翔平以降に登板した両チームの救援投手陣の内容
- 両チームのヒット数・失策数などのチーム成績
- 佐藤輝明のホームランの飛距離・打球の種類等の詳細
- この試合結果が両チームの順位表・借金貯金・連勝連敗に与えた影響
- 佐藤輝明・モンテロ・伊原陵人個人の、この試合と関連する特筆すべき
  シーズン記録(節目の記録等)
- 次戦(次の対戦カード)の予定

【出力形式(必須、既存Ledgerと同一形式)】
各Factについて、以下の形式で出力してください(FACT-08から開始し連番で)。
実際に複数ソースで確認できたことだけを書いてください。1ソースでしか
確認できなかった事実は confidence を「中」とし、その旨をnotesに明記して
ください。存在しない事実を創作しないでください。検証できなかった項目は
無理に含めないでください。

[CONFIRMED_FACT] FACT-XX: (事実の内容、1-3文程度)
  source: (実際に参照した情報源名)
  date_or_period: (試合内のいつの出来事か)
  confidence: 高 or 中
  number_classification: ANCHOR or SUPPORTING or DISPENSABLE
    (記事の核心に近いほどANCHOR/SUPPORTING、周辺情報はDISPENSABLE)
  exactness_requirement: EXACT_REQUIRED or APPROXIMATE_OK
  usable: yes
  notes: (検証時の注意点があれば)

最後に、参照した情報源のタイトルとURLを一覧で列挙してください。
"""


def research_stage() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = t3.vfl01.get_client()
    with cl.logging_context(f"{THEME_ID}_research", "ledger_enrichment_research"):
        response = client.responses.create(
            model=t3.r3.WRITER_MODEL,
            reasoning={"effort": "high"},
            tools=[{"type": "web_search"}],
            input=[
                {"role": "developer", "content": "あなたは事実確認を重視する調査アシスタントです。"},
                {"role": "user", "content": RESEARCH_PROMPT},
            ],
        )
    text = response.output_text
    search_usage = t3.r3.extract_web_search_usage(response)
    sources = t3.r3.extract_sources(response)
    result = {
        "model": response.model,
        "response_id": response.id,
        "raw_text": text,
        "web_search_call_count": search_usage["web_search_call_count"],
        "queries": search_usage["queries"],
        "sources": sources,
    }
    with open(f"{OUT_DIR}/research_raw_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] research_stage完了: web_search_call_count="
          f"{search_usage['web_search_call_count']}, sources={len(sources)}件")
    print(text)
    return result


# ============================================================
# Stage 1: setup(Gate相当の事前確認、既定値バイト一致テストの再確認)
# ============================================================
def setup_stage() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    unit_test_result = t3.test_default_hint_is_byte_identical_to_production()
    if unit_test_result["status"] != "PASS":
        raise RuntimeError(f"既定値バイト一致テスト失敗: {unit_test_result}")
    if not os.path.exists(CONDITION_B_LEDGER_PATH):
        raise RuntimeError(f"条件B Ledgerファイルが未作成です: {CONDITION_B_LEDGER_PATH}"
                            f"(research_stage()の結果を確認しWriteツールで作成すること)")
    ledger_a_text = load_text(CONDITION_A_LEDGER_PATH)
    ledger_b_text = load_text(CONDITION_B_LEDGER_PATH)
    assert ledger_b_text.startswith(ledger_a_text.rstrip("\n")), \
        "条件Bの先頭が条件Aの全文と一致しません(既存factを変更していない証拠として必須)"
    run_metadata = {
        "management_id": "FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-AB-TRIAL-12",
        "n_per_condition": N_PER_CONDITION,
        "n_definition": "N=6は条件ごとのrun数(A2×3+B1B×3)。条件A/B合計で12 run。",
        "conditions": {k: {"ledger_path": v["ledger_path"], "usable_fact_count": v["usable_fact_count"],
                            "label_ja": v["label_ja"]} for k, v in CONDITIONS.items()},
        "editorial_type_module_block": "常に空文字(Production既定、Focus Moduleなし)",
        "point_role_hint_block": "常に空文字(Production既定、hintなし)",
        "loop_budget_point_overlap_article_retry_max": prod_gen.POINT_OVERLAP_ARTICLE_RETRY_MAX,
        "condition_b_ledger_starts_with_condition_a_full_text": True,
    }
    with open(f"{OUT_DIR}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] setup_stage完了: unit_test={unit_test_result['status']}, "
          f"条件B Ledger確認OK(条件Aの全文を含む)")
    return {"unit_test_result": unit_test_result, "run_metadata": run_metadata}


# ============================================================
# Evidence allocation指標(FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-
# AUDIT-01の定義を踏襲、このTrial専用に簡潔に再実装。FACT-ID正規表現は
# Hanshin形式 FACT-\\d{2} のみ対象、既存監査スクリプトとテーマ・run単位が
# 異なるため、依存インポートはせず軽量に独立実装する)。
# ============================================================
FACT_ID_RE = re.compile(r"FACT-\d{2}")


def evidence_allocation_metrics(out_dir: str, retry_attempts: int, usable_fact_count: int) -> dict | None:
    role_plan = t4.load_role_planning_used(out_dir, retry_attempts)
    if not role_plan or not role_plan.get("parsed"):
        return None
    p1_anchor = role_plan["parsed"].get("point_one", {}).get("evidence_anchor", "") or ""
    p2_anchor = role_plan["parsed"].get("point_two", {}).get("evidence_anchor", "") or ""
    p1_ids = set(FACT_ID_RE.findall(p1_anchor))
    p2_ids = set(FACT_ID_RE.findall(p2_anchor))
    conflict_ids = p1_ids & p2_ids
    union_ids = p1_ids | p2_ids
    return {
        "point_one_anchor_ids": sorted(p1_ids),
        "point_two_anchor_ids": sorted(p2_ids),
        "anchor_conflict_count": len(conflict_ids),
        "anchor_conflict_ids": sorted(conflict_ids),
        "distinct_facts_referenced": len(union_ids),
        "usable_fact_count_condition": usable_fact_count,
        "fact_utilization_rate": round(len(union_ids) / usable_fact_count, 4) if usable_fact_count else None,
    }


def load_initial_flag(out_dir: str) -> dict:
    path = f"{out_dir}/point_overlap_article_retry_log.json"
    if not os.path.exists(path):
        return {"initial_attempt_flagged": None}
    with open(path, encoding="utf-8") as f:
        log = json.load(f)
    if not log:
        return {"initial_attempt_flagged": None}
    return {"initial_attempt_flagged": bool(log[0].get("flagged"))}


# ============================================================
# 費用実測ヘルパー(Trial-06/09と同一の参照元・同一ロジックをこのTrial
# 専用ログパス向けに再実装、budget監視のためrun中に呼び出す)。
# ============================================================
USD_JPY = 160.0
PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


_LUNA_IN, _LUNA_CACHED, _LUNA_OUT = _price("openai", "gpt-5.6-luna", "input_tokens"), \
    _price("openai", "gpt-5.6-luna", "cached_input_tokens"), _price("openai", "gpt-5.6-luna", "output_tokens")
_SOL_IN, _SOL_CACHED, _SOL_OUT = _price("openai", "gpt-5.6-sol", "input_tokens"), \
    _price("openai", "gpt-5.6-sol", "cached_input_tokens"), _price("openai", "gpt-5.6-sol", "output_tokens")
_WEB_SEARCH_CALL = _price("openai", "N/A (tool, all models)", "web_search_call")


def _call_cost_usd(r: dict) -> float:
    provider, model = r["provider"], r.get("model_id")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    if provider != "openai":
        raise ValueError(f"unpriced provider (text-only trial, no TTS/ASR expected): {provider}")
    billable_in = max(it - ct, 0)
    if model == "gpt-5.6-luna":
        cost = (billable_in / 1e6) * _LUNA_IN + (ct / 1e6) * _LUNA_CACHED + (ot / 1e6) * _LUNA_OUT
    elif model == "gpt-5.6-sol":
        cost = (billable_in / 1e6) * _SOL_IN + (ct / 1e6) * _SOL_CACHED + (ot / 1e6) * _SOL_OUT
    else:
        raise ValueError(f"unpriced openai model: {model}")
    web_search_calls = r.get("web_search_call_count") or 0
    cost += (web_search_calls / 1000) * _WEB_SEARCH_CALL
    return cost


def compute_cost_so_far_jpy() -> float:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return 0.0
    total_usd = 0.0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_usd += _call_cost_usd(json.loads(line))
    return total_usd * USD_JPY


def write_cost_summary() -> dict:
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    records = [json.loads(l) for l in open(log_path, encoding="utf-8")] if os.path.exists(log_path) else []
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-06/09 cost_computeと同一"
                       "参照元・同一ロジック)。text-onlyのためprovider=openaiのみを想定。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


# ============================================================
# combo実行(CLI分割実行用、前面同期・逐次実行。バックグラウンド待機なし)
# ============================================================
LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in LEVELS}
COMBO_RESULTS_DIR = f"{OUT_DIR}/_combo_results"


def run_one_combo(client, master_full_text: str, condition_name: str, run_idx: int,
                   label: str, instruction: str, level_dir: str, stage_tag: str) -> dict:
    cond = CONDITIONS[condition_name]
    ledger_text = load_text(cond["ledger_path"])
    out_dir = f"{OUT_DIR}/{level_dir}/{condition_name}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, t3.HANSHIN_TOPIC_JA, ledger_text, editorial_type_module_block="")
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, ledger_text, t3.HANSHIN_TOPIC_JA, out_dir,
            point_role_hint_block="")
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = condition_name
    analysis["level"] = label
    analysis["run"] = run_idx
    analysis.update(load_initial_flag(out_dir))
    analysis["evidence_allocation"] = evidence_allocation_metrics(
        out_dir, analysis["retry_attempts"], cond["usable_fact_count"])
    if analysis["point_one_overlap_ratio"] is not None and analysis["point_two_overlap_ratio"] is not None:
        analysis["gate_indicator_max_overlap"] = max(
            analysis["point_one_overlap_ratio"], analysis["point_two_overlap_ratio"])
    else:
        analysis["gate_indicator_max_overlap"] = None
    analysis["final_ng"] = result.get("status") != "OK"
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] run{run_idx} {condition_name} {label}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} p1_overlap={analysis['point_one_overlap_ratio']} "
          f"p2_overlap={analysis['point_two_overlap_ratio']} initial_flag="
          f"{analysis['initial_attempt_flagged']} elapsed={elapsed}s")
    return analysis


def combo_stage(condition_name: str, label: str, run_idx: int) -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo(client, master_full_text, condition_name, run_idx, label, instruction,
                              level_dir, stage_tag)
    os.makedirs(COMBO_RESULTS_DIR, exist_ok=True)
    with open(f"{COMBO_RESULTS_DIR}/{condition_name}_{level_dir}_run{run_idx}.json", "w",
              encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def cost_stage() -> dict:
    result = write_cost_summary()
    print(f"[{THEME_ID}] 費用実測合計: ¥{result['total_jpy']}")
    return result


def aggregate_stage() -> list:
    all_results = []
    if os.path.isdir(COMBO_RESULTS_DIR):
        for fname in sorted(os.listdir(COMBO_RESULTS_DIR)):
            with open(f"{COMBO_RESULTS_DIR}/{fname}", encoding="utf-8") as f:
                all_results.append(json.load(f))
    with open(f"{OUT_DIR}/all_results_so_far.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_stage: {len(all_results)}本を集約しました。")
    return all_results


def mean(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


def rate(flags):
    flags = [f for f in flags if f is not None]
    return round(sum(1 for f in flags if f) / len(flags), 4) if flags else None


def final_analysis_stage() -> dict:
    all_results = aggregate_stage()
    by_condition = defaultdict(list)
    for r in all_results:
        by_condition[r["condition"]].append(r)
    summary = {}
    for cond_name, rows in by_condition.items():
        ng_rows = [r for r in rows if r["final_ng"]]
        ok_rows = [r for r in rows if not r["final_ng"]]
        summary[cond_name] = {
            "n": len(rows),
            "usable_fact_count": CONDITIONS[cond_name]["usable_fact_count"],
            "initial_attempt_flag_rate": rate([r["initial_attempt_flagged"] for r in rows]),
            "final_ng_rate": rate([r["final_ng"] for r in rows]),
            "retry_attempts_avg": mean([r["retry_attempts"] for r in rows]),
            "point_one_overlap_avg": mean([r["point_one_overlap_ratio"] for r in rows]),
            "point_two_overlap_avg": mean([r["point_two_overlap_ratio"] for r in rows]),
            "gate_indicator_max_overlap_avg": mean([r["gate_indicator_max_overlap"] for r in rows]),
            "gate_indicator_max_overlap_avg_NG_group": mean([r["gate_indicator_max_overlap"] for r in ng_rows]),
            "gate_indicator_max_overlap_avg_OK_group": mean([r["gate_indicator_max_overlap"] for r in ok_rows]),
            "ledger_deviation_count_avg": mean([r["ledger_deviation_count"] for r in rows]),
            "fact_verdict_counts": dict(
                (v, sum(1 for r in rows if r.get("fact_verdict") == v))
                for v in set(r.get("fact_verdict") for r in rows)),
            "anchor_conflict_count_avg": mean([
                (r["evidence_allocation"] or {}).get("anchor_conflict_count") for r in rows]),
            "fact_utilization_rate_avg": mean([
                (r["evidence_allocation"] or {}).get("fact_utilization_rate") for r in rows]),
            "distinct_facts_referenced_avg": mean([
                (r["evidence_allocation"] or {}).get("distinct_facts_referenced") for r in rows]),
        }
    with open(f"{OUT_DIR}/final_analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if which == "research":
        research_stage()
    elif which == "setup":
        setup_stage()
    elif which == "combo":
        # 例: python er011_news_ledger_enrichment_ab_trial_12_run.py combo current A2 1
        condition_name, label, run_idx = sys.argv[2], sys.argv[3], int(sys.argv[4])
        combo_stage(condition_name, label, run_idx)
    elif which == "cost":
        cost_stage()
    elif which == "aggregate":
        aggregate_stage()
    elif which == "final_analysis":
        final_analysis_stage()
    else:
        print("usage: python er011_news_ledger_enrichment_ab_trial_12_run.py "
              "[research|setup|combo <condition> <A2|B1B> <run_idx>|cost|aggregate|final_analysis]")
