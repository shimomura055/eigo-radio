# ============================================================
# er011_discovery_stage4_cautionary_language_trial_10.py
# FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10 (Lane A, D-4派生)
# ============================================================
# 目的(ユーザー決定 2026-09-09): D-4目視で見つかった、A2記事の例
# "For unclear foods, check your own refrigerator's guide instead of relying
# on a simple category rule." のような、独立した保険文・取扱説明書的な
# 注意喚起がDiscovery記事のPoint value(面白さ)を削っている問題について、
# 現行Discovery Focus Module(Trial-09 current_focusと一字一句同一本体)
# へ最小のWriter表現制約(Part B案1、断定回避段落の末尾へ1文追加)を加えた
# 場合と比べる。
#
# 制約: 注意喚起そのものを禁止しない(Fact Safetyは一切緩めない)。事実の
# 限界(見解が分かれている・条件によって異なる等)は本文の説明として自然に
# 織り込むことを認めるが、聞き手へ「取扱説明書・メーカー案内・専門家等の
# 外部情報源を確認してください」と指示する独立した一文を、PointやIn One
# Lineの締めとして書かないことを求める。ただしVerified Fact Ledgerが、
# その注意喚起自体を記事の発見の一部として明示している場合はこの限り
# ではない(既存の断定回避規則[Ledgerが直接支持していない限り断定表現を
# 使わない]と矛盾しないよう、Ledger側の記述を優先する例外を明記する)。
#
# **Trial(Production実装ではない)**。Production/Prompt/共有module/
# registry/SSOT編集・Ledger改変・Fact Checker緩和・Git操作は一切行わない。
# TTSは実行しない(text-onlyまで)。
#
# ------------------------------------------------------------
# 再利用(import・無変更):
# ------------------------------------------------------------
#   - er011_discovery_stage3_rule_adjustment_trial_09(t9): CURRENT_FOCUS_BLOCK
#     (本体は一字一句不変、current_focus条件としてそのまま再利用)/
#     _BODY_AFTER_HEADER・_HEDGE_PARAGRAPH_ANCHOR(挿入位置の基準として再利用、
#     無変更)/ HOUSEHOLD_TOPIC_JA・HOUSEHOLD_LEDGER_PATH・LEVELS/
#     classify_claim_to_evidence・split_sentences_simple・
#     detect_near_duplicate_sentences・analyze_run・load_text(分析ロジック、
#     無変更)。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block/
#     build_prompt/run_one_pattern等。無変更。
#   - er005_cost_logger(cl): install / logging_context。無変更。
#
# 費用上限: ¥130(Trial-09実測、12本でおよそ¥100前後の実績を踏まえた
# 投影。超過見込みならN=2へ縮小し報告する。combo単位で実行し、都度
# cumulative費用を確認する)。
# ============================================================
from __future__ import annotations

import difflib
import json
import os
import time

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er011_discovery_stage3_rule_adjustment_trial_09 as t9

THEME_ID = "discovery_stage4_cautionary_language_trial_10"
OUT_DIR = f"er011_output/{THEME_ID}"

N_RUNS_PLANNED = 3
BUDGET_JPY = 130.0

HOUSEHOLD_TOPIC_JA = t9.HOUSEHOLD_TOPIC_JA
HOUSEHOLD_LEDGER_PATH = t9.HOUSEHOLD_LEDGER_PATH  # v5固定(t9と同一参照、無変更)
LEVELS = t9.LEVELS

# ------------------------------------------------------------
# current_focus: Trial-09のCURRENT_FOCUS_BLOCKをそのまま再利用(本体は
# t5/Trial-07/08/09と一字一句不変)。
# ------------------------------------------------------------
CURRENT_FOCUS_BLOCK = t9.CURRENT_FOCUS_BLOCK
_BODY_AFTER_HEADER = t9._BODY_AFTER_HEADER
_HEDGE_PARAGRAPH_ANCHOR = t9._HEDGE_PARAGRAPH_ANCHOR
assert _HEDGE_PARAGRAPH_ANCHOR in _BODY_AFTER_HEADER, (
    "断定回避段落の末尾アンカー文字列が本体に見つかりません(STOP条件)。")

# ------------------------------------------------------------
# cautionary_constrained: 未承認候補(Part B案1)。既存の断定回避段落の
# 末尾へ、以下の1文を追加するのみ。他の段落は一切変更しない(Trial-09の
# adjusted_focus[scope-generalization禁止文]とは別の、独立した最小変更。
# 本Trialでは両者を同時に適用しない)。
# ------------------------------------------------------------
_CAUTIONARY_CLAUSE = (
    " また、PointやIn One Lineの締めくくりとして、聞き手に「取扱説明書」「メーカーの"
    "案内」「専門家」など、記事の外にある情報源を確認するよう呼びかける、独立した注意"
    "喚起・保険的な一文を書かないでください。事実に限界がある場合(情報源同士で見解が"
    "分かれている、条件によって結果が異なる、等)は、聞き手に別の場所を確認させるので"
    "はなく、その限界がどこにあるかを本文の説明の一部として自然に書くところで止めて"
    "ください。ただし、Verified Fact Ledgerが、その注意喚起自体を記事の発見の一部として"
    "明示している場合はこの限りではありません(この例外は、直前の断定回避の原則と同じ"
    "く、Ledgerの記述を優先します)。"
)
_CAUTIONARY_BODY_AFTER_HEADER = _BODY_AFTER_HEADER.replace(
    _HEDGE_PARAGRAPH_ANCHOR, _HEDGE_PARAGRAPH_ANCHOR + _CAUTIONARY_CLAUSE, 1)
assert _CAUTIONARY_BODY_AFTER_HEADER != _BODY_AFTER_HEADER
_body_diff_ops = [op for op in difflib.SequenceMatcher(
    a=_BODY_AFTER_HEADER, b=_CAUTIONARY_BODY_AFTER_HEADER, autojunk=False).get_opcodes() if op[0] != "equal"]
assert len(_body_diff_ops) == 1 and _body_diff_ops[0][0] == "insert", (
    f"cautionary_constrained本体への変更が単一のinsertではありません(STOP条件、実際: {_body_diff_ops})")

CAUTIONARY_HEADER_LINE = (
    "【Discovery/Why Focus(記事タイプ固有の焦点、最小調整版[Part B案1、未承認候補]。"
    "既存の断定回避段落の末尾へ、独立した保険文・取扱説明書的な注意喚起を書かない旨の"
    "1文のみ追加[Ledgerがその注意喚起自体を発見として示す場合は例外]、他は現行版"
    "[Trial-05/07/08/09]と一字一句同一。FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-"
    "TRIAL-10でHousehold Ledger v5によるN=3検証中。Production未採用。"
    "editorial_mode=\"discovery_why\"は未登録の想定名)】"
)
CAUTIONARY_FOCUS_BLOCK = CAUTIONARY_HEADER_LINE + "\n" + _CAUTIONARY_BODY_AFTER_HEADER

CONDITIONS = {
    "current_focus": {"editorial_type_module_block": CURRENT_FOCUS_BLOCK},
    "cautionary_constrained": {"editorial_type_module_block": CAUTIONARY_FOCUS_BLOCK},
}

load_text = t9.load_text
classify_claim_to_evidence = t9.classify_claim_to_evidence
analyze_run = t9.analyze_run


# ============================================================
# Gate 4: 静的diff(Production関数を再定義・monkeypatchしていないことの
# 機械確認、Trial-09と同一ロジック)。
# ============================================================
def gate4_static_check() -> dict:
    used_names = ["THEMES", "build_common_block", "build_prompt", "A2_KAI1_INSTRUCTION",
                  "B1_B_DIRECT_INSTRUCTION", "compute_metrics", "split_common_sections_for_point_qa",
                  "run_one_pattern", "POINT_TARGET_LOWER", "POINT_TARGET_UPPER",
                  "POINT_TOLERANCE_LOWER", "POINT_TOLERANCE_UPPER"]
    not_reassigned = all(name in vars(prod_gen) for name in used_names)

    placeholder_present = "{editorial_type_module_block}" in prod_gen.COMMON_BLOCK_TEMPLATE

    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(HOUSEHOLD_LEDGER_PATH)
    baseline_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text, editorial_type_module_block="")

    current_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=CURRENT_FOCUS_BLOCK)
    cautionary_common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=CAUTIONARY_FOCUS_BLOCK)
    current_vs_baseline_ops = [op for op in difflib.SequenceMatcher(
        a=baseline_common_block, b=current_common_block, autojunk=False).get_opcodes() if op[0] != "equal"]
    cautionary_vs_baseline_ops = [op for op in difflib.SequenceMatcher(
        a=baseline_common_block, b=cautionary_common_block, autojunk=False).get_opcodes() if op[0] != "equal"]
    current_single_clean_insert = (len(current_vs_baseline_ops) == 1 and current_vs_baseline_ops[0][0] == "insert")
    cautionary_single_clean_insert = (
        len(cautionary_vs_baseline_ops) == 1 and cautionary_vs_baseline_ops[0][0] == "insert")
    body_diff_op_count = len(_body_diff_ops)

    ledger_has_v5_marker = "v5" in verified_ledger_text

    conclusion = ("PASS" if (not_reassigned and placeholder_present
                              and current_single_clean_insert and cautionary_single_clean_insert
                              and body_diff_op_count == 1 and ledger_has_v5_marker)
                  else "FAIL_NEEDS_REVIEW")

    result = {
        "prod_gen_used_names_present_and_not_reassigned": not_reassigned,
        "common_block_template_has_editorial_type_module_block_placeholder": placeholder_present,
        "current_vs_baseline_diff_is_single_clean_insert": current_single_clean_insert,
        "cautionary_vs_baseline_diff_is_single_clean_insert": cautionary_single_clean_insert,
        "current_vs_cautionary_body_diff_op_count": body_diff_op_count,
        "ledger_has_v5_marker": ledger_has_v5_marker,
        "conclusion": conclusion,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/gate4_static_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit_current_focus_block.txt", "w", encoding="utf-8") as f:
        f.write(CURRENT_FOCUS_BLOCK)
    with open(f"{OUT_DIR}/audit_cautionary_focus_block.txt", "w", encoding="utf-8") as f:
        f.write(CAUTIONARY_FOCUS_BLOCK)
    diff_lines = list(difflib.unified_diff(
        CURRENT_FOCUS_BLOCK.splitlines(keepends=True), CAUTIONARY_FOCUS_BLOCK.splitlines(keepends=True),
        fromfile="current_focus_block", tofile="cautionary_focus_block", n=2))
    with open(f"{OUT_DIR}/audit_current_vs_cautionary_diff.txt", "w", encoding="utf-8") as f:
        f.writelines(diff_lines)
    print(f"[{THEME_ID}] gate4_static_check: {result['conclusion']}")
    if conclusion != "PASS":
        raise RuntimeError(f"Gate 4静的diff失敗: {result}")
    return result


def build_run_metadata() -> dict:
    return {
        "management_id": "FAMILY-A-DISCOVERY-STAGE4-CAUTIONARY-LANGUAGE-TRIAL-10",
        "mode_supply_path": "手動Mode判定+手動Ledger供給(Trial-07/08/09と同じ機構)。",
        "editorial_mode_determination": "DISCOVERY_WHY",
        "ledger_version": "v5(Trial-09と同一。本Trialではファイルを一切書き換えない)。",
        "role_string_classification": "実施しない(D-2=(a)を踏襲、Point本文の目視比較[comparison.html]へ切り替え)。",
        "fact_checker_side_changes": "なし(Fact Checker緩和は禁止。Writer側[Focus Module文言]の最小調整のみを検証)。",
        "part_b_candidate_used": "案1(独立した保険文・取扱説明書的注意喚起の禁止、Ledgerが発見として示す場合は例外)。",
    }


# ============================================================
# 費用実測ヘルパー(Trial-09と同一の参照元・同一ロジック)。
# ============================================================
USD_JPY = t9.USD_JPY
_call_cost_usd = t9._call_cost_usd


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
    from collections import defaultdict
    log_path = f"{OUT_DIR}/raw_usage_log.jsonl"
    records = [json.loads(l) for l in open(log_path, encoding="utf-8")] if os.path.exists(log_path) else []
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    by_condition, by_level, by_run = defaultdict(float), defaultdict(float), defaultdict(float)
    for theme, cost in by_theme.items():
        rest = theme[len(THEME_ID) + 1:]
        parts = rest.rsplit("_run", 1)
        if len(parts) == 2:
            cond_level, run_idx = parts
            cond_parts = cond_level.rsplit("_", 1)
            if len(cond_parts) == 2:
                condition, level = cond_parts
                by_run[f"run{run_idx}"] += cost
                by_condition[condition] += cost
                by_level[level] += cost
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-09と同一参照元・同一ロジック)。"
                       "text-onlyのためprovider=openaiのみを想定。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "by_run_jpy": {k: round(v * USD_JPY, 1) for k, v in by_run.items()},
        "by_condition_jpy": {k: round(v * USD_JPY, 1) for k, v in by_condition.items()},
        "by_level_jpy": {k: round(v * USD_JPY, 1) for k, v in by_level.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def run_one_combo(client, master_full_text: str, verified_ledger_text: str,
                   condition_name: str, run_idx: int, label: str, instruction: str,
                   level_dir: str, stage_tag: str) -> dict:
    cond = CONDITIONS[condition_name]
    out_dir = f"{OUT_DIR}/{level_dir}/{condition_name}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, HOUSEHOLD_TOPIC_JA, verified_ledger_text,
        editorial_type_module_block=cond["editorial_type_module_block"])
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = prod_gen.run_one_pattern(
            client, theme_tag, label, prompt, verified_ledger_text, HOUSEHOLD_TOPIC_JA, out_dir)
    elapsed = round(time.time() - t0, 2)
    analysis = analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = condition_name
    analysis["level"] = label
    analysis["run"] = run_idx

    analysis["claim_to_evidence_table"] = [
        {"claim": c, **classify_claim_to_evidence(c)}
        for c in analysis["fact_unsupported_specific_claims"]
    ] if analysis["fact_unsupported_specific_claims"] else []

    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False,
                   indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] run{run_idx} {condition_name} {label}: status={result.get('status')} "
          f"fact_verdict={analysis['fact_verdict']} unsupported_claims={analysis['fact_unsupported_specific_claims_count']} "
          f"ledger_status={analysis['ledger_status']} local_rewrite_items={analysis['local_rewrite_item_count']} "
          f"word_count={analysis['word_count']} elapsed={elapsed}s")
    return analysis


LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in LEVELS}
COMBO_RESULTS_DIR = f"{OUT_DIR}/_combo_results"


def setup_stage() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    gate4_result = gate4_static_check()
    run_metadata = build_run_metadata()
    with open(f"{OUT_DIR}/run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] setup_stage完了: gate4={gate4_result['conclusion']}")
    return {"gate4_result": gate4_result, "run_metadata": run_metadata}


def combo_stage(condition_name: str, label: str, run_idx: int) -> dict:
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = load_text(HOUSEHOLD_LEDGER_PATH)
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo(client, master_full_text, verified_ledger_text, condition_name,
                              run_idx, label, instruction, level_dir, stage_tag)
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


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "setup"
    if which == "setup":
        setup_stage()
    elif which == "combo":
        condition_name, label, run_idx = sys.argv[2], sys.argv[3], int(sys.argv[4])
        combo_stage(condition_name, label, run_idx)
    elif which == "cost":
        cost_stage()
    elif which == "aggregate":
        aggregate_stage()
    else:
        print("usage: python er011_discovery_stage4_cautionary_language_trial_10.py "
              "[setup|combo <condition> <A2|B1B> <run_idx>|cost|aggregate]")
