# ============================================================
# er011_no18_a2_evidence_compression_abc_precision_extension_trial_20.py
# ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-PRECISION-EXTENSION-TRIAL-20
# ============================================================
# 目的: Trial-19で再現性を確認したPattern A/B/Cに、新たに共通の
# 「Listener-Friendly Numeric Precision」ルールを追加し、各Patternが
# (1) 不要な小数精度を安全に落とせるか (2) Factを保持したまま聴取負荷を
# さらに下げられるか (3) 丸めによる意味変化・Fact統合・threshold消失等を
# 起こさないか (4) A/B/Cそれぞれの長所短所がどう変わるかを比較する。
#
# Pattern A/B/Cの既存ルール文(Trial-18/19と同一)・既存Evidence Compression
# Editor Prompt・Fact Ledger・pre_editor_articleは一切変更しない。Writerは
# 再生成しない。今回追加してよいのは3Pattern共通のPrecisionルールのみ。
# Baselineは再実行しない(Trial-19の結果を参考として引用するのみ)。
#
# 実行数: Pattern A x3, Pattern B x3, Pattern C x3 = 9 run。
# n=3のため統計的有意差は主張しない。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# Production Prompt変更・CURRENT_SPEC変更・No.18 article.md上書き・
# Writer再生成・TTS/Audio・OPEN-100 close・OPEN-112着手・Pattern Production
# wiring・Precision rule Production wiring・4つ目のPattern追加は一切行わない。
from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as artgen
import er011_no18_a2_evidence_compression_extension_abc_trial_18 as trial18
import er011_no18_a2_evidence_compression_abc_reproducibility_trial_19 as trial19

load_dotenv()

SRC_DIR = trial18.SRC_DIR
OUT_DIR = "er011_output/no18_a2_evidence_compression_abc_precision_extension_trial_20"
RUNS_PER_PATTERN = 3

RUN_PREFIX = {"A": "pattern_a_precision", "B": "pattern_b_precision", "C": "pattern_c_precision"}

EXPECTED_DELTAS = trial19.EXPECTED_DELTAS  # F-005: 9.24 / F-006: 10.09
ORIGINAL_VALUES = {
    "F-005": {"metric": "attention score", "low": 99.71, "high": 108.95},
    "F-006": {"metric": "processing speed", "low": 98.48, "high": 108.57},
}

# ------------------------------------------------------------
# 共通追加ルール(§3〜§6): Listener-Friendly Numeric Precision
# 3 Pattern共通・Pattern固有のカスタマイズなし。
# ------------------------------------------------------------
PRECISION_BLOCK_EN = """【追加ルール: 全Pattern共通 - Listener-Friendly Numeric Precision】

This rule applies AFTER each Pattern's own rule above has already decided which
numeric Facts to keep. First, decide whether a numeric value is worth retaining at
all, following the Pattern-specific rule above. Then, for values you keep, decide how
much precision the listener actually needs, following this rule. Do not conflate the
two decisions.

When a numeric value is worth keeping, preserve only as much precision as the
listener needs to understand its meaning.

Prefer simpler rounded values when extra decimal precision does not materially
affect:
- the direction of the comparison
- the magnitude that matters to the story
- an important threshold
- the interpretation of the evidence
- the distinction between materially different values

Do not remove decimals mechanically.

Keep decimal precision when rounding would:
- hide a meaningful difference
- cross or obscure an important threshold
- distort a small-scale measurement
- change the interpretation
- make two meaningfully different values appear equivalent
- reduce factual fidelity in a way relevant to the listener

When rounding is appropriate, use listener-friendly expressions such as "about",
"roughly", "nearly", etc. where suitable.

Most important: Rounding is NOT permission to merge separate facts, metrics,
groups, time points, survey questions, or experimental outcomes. Each retained
numeric expression must remain attributable to its original Fact / metric in the
Fact Ledger. Never combine separate Facts merely because their rounded values
become numerically similar. Before rounding, verify that each numeric expression
can still be traced to a single, specific Fact / metric / group / time point /
survey question. Do not combine numbers from different Facts or different
metrics (for example, an attention-score value and a processing-speed value)
into a single shared rounded expression, even if their rounded values happen to
look similar or identical.

The goal is not to remove decimal places. The goal is to use the least precision
necessary for accurate spoken understanding.

This is a judgment rule, not a mechanical one. Do NOT apply any fixed rule such as
"always drop decimals," "always round to a whole number," "always keep one decimal
place," or "always use two significant figures." Decide based on what each specific
number means in context.

For general guidance only (not a fixed instruction for this specific article):
decimal precision is more likely to matter for values such as small percentages
(for example 1.2% vs 1.8%), small absolute differences (for example 4.8 vs 5.2),
sub-one units (for example 0.3 seconds), multipliers (for example 1.5 times),
values near a meaningful threshold, or small differences that are themselves the
finding. These are illustrative examples of the general principle only, not
article-specific instructions."""


def build_precision_prompt(article_text: str, pattern_block: str) -> str:
    combined = pattern_block + "\n\n" + PRECISION_BLOCK_EN
    return trial18.build_prompt(article_text, combined)


def run_editor_precision_variant(client, article_text: str, pattern_block: str) -> dict:
    combined = pattern_block + "\n\n" + PRECISION_BLOCK_EN
    return trial18.run_editor_variant(client, article_text, combined)


def extract_f005_f006_area_v2(text: str) -> dict:
    """Trial-19のregex('attention (score|performance)|processing speed')は
    'Attention averaged...'のような言い回しを取りこぼした(baseline_04で実証済み)。
    本Trialでは判定を緩め、'attention'単独/'processing speed'を含む文を拾う。"""
    sentences = trial19.split_sentences(text)
    area = [s for s in sentences if re.search(r"attention|processing speed", s, re.IGNORECASE)]
    attention_sentences = [s for s in area if re.search(r"attention", s, re.IGNORECASE)]
    processing_sentences = [s for s in area if re.search(r"processing speed", s, re.IGNORECASE)]
    area_text = " ".join(area)
    return {
        "area_text": area_text,
        "attention_sentences": attention_sentences,
        "processing_sentences": processing_sentences,
        "number_count": trial18.count_numbers(area_text),
        "sentence_count": len(area),
        "mentions_attention": bool(attention_sentences),
        "mentions_processing_speed": bool(processing_sentences),
    }


def scan_precision_numbers(area_text: str) -> dict:
    raw = re.findall(r"\d[\d,]*\.?\d*", area_text)
    decimals = [m for m in raw if "." in m]
    wholes = [m for m in raw if "." not in m]
    return {
        "all_numbers_raw": raw,
        "decimal_numbers": decimals,
        "whole_numbers": wholes,
        "decimal_count": len(decimals),
        "whole_count": len(wholes),
    }


def fact_separation_check(area: dict) -> dict:
    """attention文とprocessing speed文が、異なる文として分離されたまま残っているか、
    それとも1文へ統合され丸め値が共有されていないかを粗くチェックする(手動検証の下地)。"""
    att_nums = set()
    for s in area["attention_sentences"]:
        att_nums |= set(re.findall(r"\d[\d,]*\.?\d*", s))
    proc_nums = set()
    for s in area["processing_sentences"]:
        proc_nums |= set(re.findall(r"\d[\d,]*\.?\d*", s))
    shared_sentence = bool(
        set(area["attention_sentences"]) & set(area["processing_sentences"])
    )
    shared_numbers = att_nums & proc_nums
    return {
        "attention_numbers": sorted(att_nums),
        "processing_numbers": sorted(proc_nums),
        "shared_sentence_between_metrics": shared_sentence,
        "shared_numeric_tokens": sorted(shared_numbers),
        "possible_fact_merge_risk": shared_sentence and bool(shared_numbers),
    }


def run_single(client, ledger_model, key: str, run_id: str, baseline_article_text: str,
               verified_ledger_text: str, pattern_block: str) -> dict:
    print(f"[TRIAL-20] run={run_id}: Evidence Compression Editor(Precision付き)呼び出し...")
    editor_result = run_editor_precision_variant(client, baseline_article_text, pattern_block)
    variant_text = editor_result["raw_text"]
    with open(f"{OUT_DIR}/audit/editor_raw_{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/article_{run_id}.md", "w", encoding="utf-8") as f:
        f.write(variant_text)

    print(f"[TRIAL-20] run={run_id}: Ledger Deviation Check...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, variant_text, model=ledger_model, hook_aware=True)
    with open(f"{OUT_DIR}/audit/ledger_deviation_{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)

    print(f"[TRIAL-20] run={run_id}: Fact Checker呼び出し...")
    fact_qa = trial18.run_fact_checker(client, trial18.TOPIC_EN, variant_text)
    with open(f"{OUT_DIR}/audit/fact_qa_{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa, f, ensure_ascii=False, indent=2, default=str)

    metrics = artgen.compute_metrics(variant_text)
    causal_found = trial18.scan_causal_markers(variant_text)
    causal_baseline = trial18.scan_causal_markers(baseline_article_text)
    causal_new = [m for m in causal_found if m not in causal_baseline]

    area = extract_f005_f006_area_v2(variant_text)
    precision_numbers = scan_precision_numbers(area["area_text"])
    separation = fact_separation_check(area)
    numeric_accuracy = trial19.numeric_accuracy_check(area["area_text"])
    sent_stats = trial19.sentence_diff_stats(baseline_article_text, variant_text)
    diff_html = trial19.render_word_diff_html(baseline_article_text, variant_text)
    with open(f"{OUT_DIR}/audit/diff_{run_id}.html", "w", encoding="utf-8") as f:
        f.write(diff_html)

    deviations = deviation_result["parsed"]["deviations"]
    has_trend_phrase = any(m in area["area_text"].lower() for m in trial19.TREND_PHRASE_MARKERS)
    has_delta_expr = any(m in area["area_text"].lower() for m in trial19.DELTA_EXPRESSION_MARKERS)

    run_summary = {
        "run_id": run_id, "pattern": key,
        "response_id": editor_result["response_id"],
        "metrics": metrics,
        "number_count_total": trial18.count_numbers(variant_text),
        "f005_f006_area": area,
        "precision_numbers": precision_numbers,
        "fact_separation_check": separation,
        "numeric_accuracy": numeric_accuracy,
        "has_trend_phrase": has_trend_phrase,
        "has_delta_expression": has_delta_expr,
        "sentence_diff_stats": sent_stats,
        "ledger_overall_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviations),
        "ledger_deviations": deviations,
        "fact_checker_status": fact_qa["final_status"],
        "fact_checker_verdict": (fact_qa["result"] or {}).get("verdict") if fact_qa["result"] else None,
        "fact_checker_unsupported_claim_count": len((fact_qa["result"] or {}).get("unsupported_specific_claims", [])) if fact_qa["result"] else None,
        "causal_markers_found": causal_found,
        "new_causal_markers_vs_baseline_input": causal_new,
    }
    print(f"[TRIAL-20] run={run_id}: 完了。ledger={run_summary['ledger_overall_status']} "
          f"fact_verdict={run_summary['fact_checker_verdict']} "
          f"area_numbers={area['number_count']} decimals={precision_numbers['decimal_count']} "
          f"merge_risk={separation['possible_fact_merge_risk']} new_causal={causal_new}")
    return run_summary


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    with open(f"{SRC_DIR}/a2/audit/pre_editor_article.md", encoding="utf-8") as f:
        baseline_article_text = f.read()
    with open(f"{SRC_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        verified_ledger_text = f.read()

    client = vfl01.get_client()
    ledger_model = "gpt-5.6-luna"

    fact_lines = trial18.find_ledger_fact_lines(verified_ledger_text, ["F-005", "F-006"])

    summary = {
        "input_article": baseline_article_text,
        "fact_lines_F005_F006": fact_lines,
        "expected_deltas": EXPECTED_DELTAS,
        "original_values": ORIGINAL_VALUES,
        "precision_rule_text": PRECISION_BLOCK_EN,
        "runs_per_pattern": RUNS_PER_PATTERN,
        "runs": {},
    }

    for key in ["A", "B", "C"]:
        pattern_block = trial18.PATTERNS[key]["extra"]
        for i in range(1, RUNS_PER_PATTERN + 1):
            run_id = f"{RUN_PREFIX[key]}_{i:02d}"
            run_summary = run_single(
                client, ledger_model, key, run_id, baseline_article_text,
                verified_ledger_text, pattern_block)
            summary["runs"][run_id] = run_summary
            with open(f"{OUT_DIR}/trial_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-20] 全9 run完了。summary -> {OUT_DIR}/trial_summary.json")


if __name__ == "__main__":
    main()
