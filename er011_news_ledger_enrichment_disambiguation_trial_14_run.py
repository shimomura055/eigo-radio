# ============================================================
# er011_news_ledger_enrichment_disambiguation_trial_14_run.py
# FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14
# (Lane A, Sonnet委任、段階2: 打ち切り記事へのFact Checker単独適用)
# ============================================================
# 目的(委任文どおり): Trial-12/12bで「Point Overlap Gate(Loop Budget=2)
# 到達後もNGのままFact Checkerへ未到達」だった記事(条件A/B/C/D、
# final_ng=True かつ fact_verdict=None)に対し、既存の本番Fact Checker関数
# (er002_ja_web_research_r3.build_fact_check_prompt / make_fact_checker_fn /
# run_fact_checker_with_gates、無改変)を単独適用し、「条件Aの真のfact誤り率」
# を条件B/C/D(Fact Checkerまで到達できた記事)と比較する。
#
# **Trial(Production実装ではない)**。Production/Prompt/QA/Validator/retry
# コード・SSOT編集・Git操作は一切行わない。monkeypatch・グローバル書き換え
# なし。既存Fact Checkerの呼び出しシーケンス(run_fact_checker_with_gates、
# 最大2 attempt、Web検索必須)をそのまま踏襲し、パラメータ改変なし。
# TTSは実行しない(text-onlyまで)。
#
# 対象抽出方法(機械的、委任文どおり): all_results_so_far.json(条件A/B)
# + reaggregation/all_results_cd.json(条件C/D)を読み、
# final_ng=True かつ fact_verdict is None の行を対象とする。
# (委任文の見込み「7本」に対し、実数は8本だった。内訳は本スクリプト実行時
# ログ・REPORTに記載。)
#
# 書き込み範囲: er011_output/news_ledger_enrichment_ab_trial_12/
# factcheck_censored/ 配下のみ(新規サブディレクトリ)。既存Trial-12/12bの
# 成果物は読み取り専用で一切変更しない。
#
# 費用上限: このスクリプト単独で¥150(委任文全体の禁止上限と同一値を
# 安全側の上限として転用)。combo単位で逐次実行し、実行前に都度
# compute_cost_so_far_jpy()で確認する(前面同期のみ、バックグラウンド
# 待機・二重起動なし)。
# ============================================================
from __future__ import annotations

import json
import os
import time
from collections import defaultdict

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er011_point_role_planning_focus_connection_trial_03 as t3

THEME_ID = "news_ledger_enrichment_disambiguation_trial_14"
BASE_DIR = "er011_output/news_ledger_enrichment_ab_trial_12"
OUT_DIR = f"{BASE_DIR}/factcheck_censored"
BUDGET_JPY = 150.0

TOPIC = t3.HANSHIN_TOPIC_JA

# 条件ごとのarticle.md実体パス(既存Trial-12/12bのディレクトリ構造どおり)
CONDITION_ARTICLE_DIR = {
    "current": f"{BASE_DIR}/{{level_dir}}/current/run{{run}}",
    "enriched": f"{BASE_DIR}/{{level_dir}}/enriched/run{{run}}",
    "leaveout_c": f"{BASE_DIR}/leaveout_c/{{level_dir}}/run{{run}}",
    "twofact_d": f"{BASE_DIR}/twofact_d/{{level_dir}}/run{{run}}",
}
LEVEL_DIR_MAP = {"A2": "a2", "B1B": "b1b"}


def _article_dir(condition: str, level: str, run: int) -> str:
    level_dir = LEVEL_DIR_MAP[level]
    return CONDITION_ARTICLE_DIR[condition].format(level_dir=level_dir, run=run)


def identify_censored_targets() -> list:
    """final_ng=True かつ fact_verdict is None の行を機械的に抽出する。"""
    with open(f"{BASE_DIR}/all_results_so_far.json", encoding="utf-8") as f:
        ab_results = json.load(f)
    with open(f"{BASE_DIR}/reaggregation/all_results_cd.json", encoding="utf-8") as f:
        cd_results = json.load(f)
    targets = []
    for r in ab_results + cd_results:
        if r.get("final_ng") is True and r.get("fact_verdict") is None:
            targets.append({
                "condition": r["condition"], "level": r["level"], "run": r["run"],
                "status": r["status"], "retry_attempts": r.get("retry_attempts"),
            })
    return targets


def load_article_text(condition: str, level: str, run: int) -> str:
    path = f"{_article_dir(condition, level, run)}/article.md"
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_one_factcheck(condition: str, level: str, run: int) -> dict:
    article_text = load_article_text(condition, level, run)
    out_dir = f"{OUT_DIR}/{condition}_{level.lower()}_run{run}"
    os.makedirs(out_dir, exist_ok=True)

    # 既存Production関数をそのまま呼び出す(無改変、writer_sourcesは既存
    # Trial-12/12bのcombo実行と同様に空リストで固定=Production A-Family
    # 経路[er003_v1_n3_01_articles_generate.py]と同一呼び出し形)。
    fc_prompt = r3.build_fact_check_prompt(TOPIC, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    theme_tag = f"{THEME_ID}_{condition}_{level.lower()}_run{run}"
    t0 = time.time()
    with cl.logging_context(theme_tag, "fact_check_censored"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    elapsed = round(time.time() - t0, 2)
    verdict = fc_result.get("verdict") if fc_result else None

    fact_qa_record = {
        "condition": condition, "level": level, "run": run,
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "verdict": verdict, "result": fc_result,
        "elapsed_seconds": elapsed,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] {condition} {level} run{run}: status={fc_status} verdict={verdict} "
          f"elapsed={elapsed}s")
    return fact_qa_record


# ============================================================
# 費用実測ヘルパー(Trial-12/12bと同一ロジック、無改変で再利用)
# ============================================================
import er011_news_ledger_enrichment_ab_trial_12_run as t12  # noqa: E402

USD_JPY = t12.USD_JPY
_call_cost_usd = t12._call_cost_usd


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
    records = []
    if os.path.exists(log_path):
        records = [json.loads(l) for l in open(log_path, encoding="utf-8")]
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-12/12bと同一参照元・"
                       "同一ロジック)。Fact Checker単独適用のみ(記事生成は行っていない)。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_DIR}/cost_summary_censored.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def combo_stage(condition: str, level: str, run: int) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    cost_so_far = compute_cost_so_far_jpy()
    if cost_so_far > BUDGET_JPY:
        raise RuntimeError(f"費用上限超過見込み(実測¥{cost_so_far:.1f} > 上限¥{BUDGET_JPY})。STOPします。")
    return run_one_factcheck(condition, level, run)


# ============================================================
# 段階3: 条件E(A5件+FACT-11+FACT-14の2件のみ=usable 7件)、N=6
# (A2×3+B1B×3)。既存Trial-12/12b harnessと同一のProduction関数
# (build_common_block/build_prompt/run_one_pattern_connected、無改変)を
# 再利用する。Ledgerは既存条件Bファイル(hanshin_ledger_condition_b_
# enriched.txt、無変更)からFACT-11/14ブロックのみ機械的に正規表現抽出
# する(新規Web調査なし、¥0)。抽出ロジックはTrial-12bの
# `_extract_fact_blocks`(無改変、importして再利用)をそのまま使う。
# 書き込み範囲: er011_output/news_ledger_enrichment_ab_trial_12/twofact_e/
# のみ(新規サブディレクトリ)。
# ============================================================
import er003_v1_n3_01_articles_generate as prod_gen  # noqa: E402
import er011_daily_news_focus_layer_comparison_trial_04 as t4  # noqa: E402
import er011_news_ledger_enrichment_leaveout_trial_12b_run as t12b  # noqa: E402

TWOFACT_E_DIR = f"{BASE_DIR}/twofact_e"
LEDGER_E_PATH = f"{TWOFACT_E_DIR}/hanshin_ledger_condition_e_twofact.txt"
CONDITION_E_FACT_IDS = ["11", "14"]
USABLE_FACT_COUNT_E = 5 + len(CONDITION_E_FACT_IDS)  # 7(条件Dと同数)

LEVELS = t4.LEVELS
LABEL_LOOKUP_E = {label: (label, instruction, level_dir, stage_tag)
                  for (label, instruction, level_dir, stage_tag) in LEVELS}


def build_ledger_e_stage() -> dict:
    os.makedirs(TWOFACT_E_DIR, exist_ok=True)
    condition_a_text = t12b.load_text(t12b.CONDITION_A_LEDGER_PATH).rstrip("\n")
    condition_b_text = t12b.load_text(t12b.CONDITION_B_LEDGER_PATH)
    fact_blocks = t12b._extract_fact_blocks(condition_b_text)  # noqa: SLF001 (無改変・再利用のみ)
    for fid in CONDITION_E_FACT_IDS:
        if not fact_blocks[fid].startswith(f"[CONFIRMED_FACT] FACT-{fid}:"):
            raise RuntimeError(f"FACT-{fid}ブロックの抽出結果が不正です")
    header_note = (
        "\n\n=== 追加Fact(Trial-14 条件E: A+FACT-11/14の2件のみ、機械的抜粋) ===\n"
        "管理ID: FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14\n"
        "作成方法: 新規Web調査は行っていない(追加research費用¥0)。既存の\n"
        "Trial-12条件B用Ledger(hanshin_ledger_condition_b_enriched.txt、無変更)\n"
        "から、FACT-11(佐藤輝明28号本塁打の球種)・FACT-14(順位・ゲーム差)の\n"
        "ブロックのみを正規表現で機械的に抽出し、文言を一切変更せずそのまま\n"
        "連結したものである。\n\n"
    )
    blocks_text = "\n\n".join(fact_blocks[fid] for fid in CONDITION_E_FACT_IDS)
    summary = (
        "\n\n=== 条件E usable fact数の集計(Trial実施者による機械集計) ===\n"
        "条件A由来(ANCHOR+SUPPORTING、FACT-01〜05): 5件\n"
        f"条件B由来(このLedgerで採用したSUPPORTING、FACT-{'/'.join(CONDITION_E_FACT_IDS)}): "
        f"{len(CONDITION_E_FACT_IDS)}件\n"
        f"usable(ANCHOR+SUPPORTING)合計 = {USABLE_FACT_COUNT_E}件\n"
    )
    full_text = condition_a_text + header_note + blocks_text + summary
    with open(LEDGER_E_PATH, "w", encoding="utf-8") as f:
        f.write(full_text)
    assert full_text.startswith(condition_a_text)
    for fid in ("08", "09", "10", "12", "13"):
        assert f"[CONFIRMED_FACT] FACT-{fid}:" not in full_text, f"条件EにFACT-{fid}が誤混入しています"
    for fid in CONDITION_E_FACT_IDS:
        assert f"[CONFIRMED_FACT] FACT-{fid}:" in full_text, f"条件EにFACT-{fid}が欠落しています"
    print(f"[{THEME_ID}] build_ledger_e_stage完了: {len(full_text)}文字")
    return {"condition_e_chars": len(full_text)}


def run_one_combo_e(client, master_full_text: str, run_idx: int, label: str, instruction: str,
                     level_dir: str, stage_tag: str) -> dict:
    ledger_text = t12b.load_text(LEDGER_E_PATH)
    out_dir = f"{TWOFACT_E_DIR}/{level_dir}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, t3.HANSHIN_TOPIC_JA, ledger_text, editorial_type_module_block="")
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_twofact_e_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, ledger_text, t3.HANSHIN_TOPIC_JA, out_dir,
            point_role_hint_block="")
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = "twofact_e"
    analysis["level"] = label
    analysis["run"] = run_idx
    analysis.update(t12b.load_initial_flag(out_dir))
    analysis.update(t12b.load_initial_attempt0_qa(out_dir))
    analysis["evidence_allocation"] = t12b.evidence_allocation_metrics(
        out_dir, analysis["retry_attempts"], USABLE_FACT_COUNT_E)
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
    print(f"[{THEME_ID}] twofact_e run{run_idx} {label}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} initial_value_qa={analysis['initial_value_qa_label']} "
          f"elapsed={elapsed}s")
    return analysis


def compute_cost_so_far_jpy_e() -> float:
    log_path = f"{TWOFACT_E_DIR}/raw_usage_log.jsonl"
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


def compute_cost_so_far_jpy_all_stages() -> float:
    """段階2(factcheck_censored)+段階3(twofact_e)の累計(委任文の禁止条件
    「¥150超の実行禁止」はTrial-14全体が対象と解釈し、両段階合計で監視する)。"""
    return compute_cost_so_far_jpy() + compute_cost_so_far_jpy_e()


def combo_e_stage(label: str, run_idx: int) -> dict:
    os.makedirs(TWOFACT_E_DIR, exist_ok=True)
    cl.install(f"{TWOFACT_E_DIR}/raw_usage_log.jsonl")
    cost_so_far = compute_cost_so_far_jpy_all_stages()
    if cost_so_far > BUDGET_JPY:
        raise RuntimeError(f"費用上限超過見込み(実測¥{cost_so_far:.1f} > 上限¥{BUDGET_JPY})。STOPします。")
    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP_E[label]
    analysis = run_one_combo_e(client, master_full_text, run_idx, label, instruction, level_dir, stage_tag)
    combo_results_dir = f"{TWOFACT_E_DIR}/_combo_results"
    os.makedirs(combo_results_dir, exist_ok=True)
    with open(f"{combo_results_dir}/{level_dir}_run{run_idx}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    return analysis


def write_cost_summary_e() -> dict:
    log_path = f"{TWOFACT_E_DIR}/raw_usage_log.jsonl"
    records = []
    if os.path.exists(log_path):
        records = [json.loads(l) for l in open(log_path, encoding="utf-8")]
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    result = {
        "usd_jpy_rate": USD_JPY,
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{TWOFACT_E_DIR}/cost_summary_e.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def aggregate_e_stage() -> list:
    all_results = []
    combo_results_dir = f"{TWOFACT_E_DIR}/_combo_results"
    if os.path.isdir(combo_results_dir):
        for fname in sorted(os.listdir(combo_results_dir)):
            with open(f"{combo_results_dir}/{fname}", encoding="utf-8") as f:
                all_results.append(json.load(f))
    with open(f"{BASE_DIR}/reaggregation/all_results_e.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_e_stage: {len(all_results)}本を集約しました。")
    return all_results


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "list_targets"
    if which == "list_targets":
        for t in identify_censored_targets():
            print(t)
    elif which == "combo":
        # 例: python er011_news_ledger_enrichment_disambiguation_trial_14_run.py combo current A2 1
        combo_stage(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif which == "cost":
        r = write_cost_summary()
        print(f"[{THEME_ID}] 費用実測合計(factcheck_censored): {r['total_jpy']}")
    elif which == "build_ledger_e":
        build_ledger_e_stage()
    elif which == "combo_e":
        # 例: python er011_news_ledger_enrichment_disambiguation_trial_14_run.py combo_e A2 1
        combo_e_stage(sys.argv[2], int(sys.argv[3]))
    elif which == "cost_e":
        r = write_cost_summary_e()
        print(f"[{THEME_ID}] 費用実測合計(twofact_e): {r['total_jpy']} / 累計(段階2+3): "
              f"{round(compute_cost_so_far_jpy_all_stages(), 1)}")
    elif which == "aggregate_e":
        aggregate_e_stage()
    else:
        print("usage: python er011_news_ledger_enrichment_disambiguation_trial_14_run.py "
              "[list_targets|combo <condition> <A2|B1B> <run>|cost|"
              "build_ledger_e|combo_e <A2|B1B> <run>|cost_e|aggregate_e]")
