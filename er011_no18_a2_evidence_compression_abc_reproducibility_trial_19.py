# ============================================================
# er011_no18_a2_evidence_compression_abc_reproducibility_trial_19.py
# ER-011-NO18-A2-EVIDENCE-COMPRESSION-ABC-REPRODUCIBILITY-TRIAL-19
# ============================================================
# 目的: Trial-18で比較したBaseline / Pattern A / Pattern B / Pattern Cを、
# 完全に同一のpre-editor入力・同一model・同一reasoning設定で各5回ずつ
# (計20回)実行し、Evidence Compression Editor出力の再現性・Fact safety
# 安定性・聴取負荷低減の安定性・記事全体への副作用を比較する。
#
# Writerは再生成しない(全runで同一のpre_editor_article.mdを使用)。
# Prompt定義(共通目的文・Pattern A/B/Cルール文)はTrial-18のモジュールを
# そのままimportして再利用し、一切変更しない。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# Production Prompt変更・CURRENT_SPEC変更・No.18 article.md上書き・
# Writer再生成・TTS/Audio・OPEN-100 close・OPEN-112着手・4つ目のPattern
# 追加は一切行わない。
from __future__ import annotations

import difflib
import html
import json
import os
import re
import time

from dotenv import load_dotenv

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as artgen
import er011_no18_a2_evidence_compression_extension_abc_trial_18 as trial18

load_dotenv()

SRC_DIR = trial18.SRC_DIR
OUT_DIR = "er011_output/no18_a2_evidence_compression_abc_reproducibility_trial_19"
RUNS_PER_PATTERN = 5

RUN_PREFIX = {"baseline": "baseline", "A": "pattern_a", "B": "pattern_b", "C": "pattern_c"}

EXPECTED_DELTAS = {"F-005": 108.95 - 99.71, "F-006": 108.57 - 98.48}  # 9.24 / 10.09

TREND_PHRASE_MARKERS = [
    "same pattern", "showed the same", "also lower", "also higher", "as well",
    "similarly", "the same way", "also showed", "likewise",
]
DELTA_EXPRESSION_MARKERS = [
    "points lower", "points higher", "point lower", "point higher", "about ",
    "roughly ", "nearly ", "almost ", "difference of", "fewer points", "lower by",
    "higher by",
]

_SENT_RE = artgen._SENTENCE_SPLIT_RE


def split_sentences(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            out.append(line)
            continue
        out.extend([s.strip() for s in _SENT_RE.split(line) if s.strip()])
    return out


def tokenize_preserve_ws(text: str) -> list[str]:
    return re.findall(r"\s+|\S+", text)


def render_word_diff_html(a_text: str, b_text: str) -> str:
    a = tokenize_preserve_ws(a_text)
    b = tokenize_preserve_ws(b_text)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            out.append(html.escape("".join(a[i1:i2])))
        elif tag == "delete":
            seg = html.escape("".join(a[i1:i2]))
            if seg.strip():
                out.append(f'<del class="diff-del">{seg}</del>')
        elif tag == "insert":
            seg = html.escape("".join(b[j1:j2]))
            if seg.strip():
                out.append(f'<ins class="diff-add">{seg}</ins>')
        elif tag == "replace":
            seg_a = html.escape("".join(a[i1:i2]))
            seg_b = html.escape("".join(b[j1:j2]))
            out.append(f'<del class="diff-del">{seg_a}</del><ins class="diff-add">{seg_b}</ins>')
    return "".join(out)


def sentence_diff_stats(a_text: str, b_text: str) -> dict:
    a = split_sentences(a_text)
    b = split_sentences(b_text)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    added = deleted = replaced = equal = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            equal += i2 - i1
        elif tag == "delete":
            deleted += i2 - i1
        elif tag == "insert":
            added += j2 - j1
        elif tag == "replace":
            replaced += max(i2 - i1, j2 - j1)
    return {
        "baseline_sentence_count": len(a), "variant_sentence_count": len(b),
        "unchanged_sentences": equal, "deleted_sentences": deleted,
        "added_sentences": added, "replaced_sentences": replaced,
    }


def extract_f005_f006_area(text: str) -> dict:
    sentences = split_sentences(text)
    area = [s for s in sentences if re.search(r"attention (score|performance)|processing speed", s, re.IGNORECASE)]
    area_text = " ".join(area)
    return {
        "area_text": area_text,
        "number_count": trial18.count_numbers(area_text),
        "sentence_count": len(area),
        "mentions_attention": bool(re.search(r"attention", area_text, re.IGNORECASE)),
        "mentions_processing_speed": bool(re.search(r"processing speed", area_text, re.IGNORECASE)),
    }


def classify_number_bucket(n: int) -> str:
    if n == 4:
        return "4nums"
    if n == 2:
        return "2nums"
    if n == 0:
        return "0nums"
    return "other"


def numeric_accuracy_check(area_text: str) -> dict:
    nums = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*\.?\d*", area_text)]
    matches = {}
    for fid, expected in EXPECTED_DELTAS.items():
        hit = any(abs(n - expected) <= 1.0 for n in nums)
        matches[fid] = {"expected_delta": round(expected, 2), "matched_within_1_0": hit}
    return {"numbers_found_in_area": nums, "delta_matches": matches}


def intended_outcome_check(key: str, area: dict, deviations: list[dict], causal_new: list[str]) -> dict:
    fact_safety_ok = not any(d.get("severity") in ("MAJOR", "CRITICAL") for d in deviations)
    causal_ok = len(causal_new) == 0
    both_facts = area["mentions_attention"] and area["mentions_processing_speed"]
    area_lower = area["area_text"].lower()

    if key == "baseline":
        bucket = classify_number_bucket(area["number_count"])
        return {"bucket": bucket, "fact_safety_ok": fact_safety_ok, "causal_ok": causal_ok,
                "both_facts_mentioned": both_facts}

    if key == "A":
        has_trend_phrase = any(m in area_lower for m in TREND_PHRASE_MARKERS)
        has_some_number = area["number_count"] >= 1
        intended = bool(has_trend_phrase and has_some_number and both_facts and fact_safety_ok and causal_ok)
        return {"intended_pattern_a": intended, "has_trend_phrase": has_trend_phrase,
                "has_representative_number": has_some_number, "both_facts_mentioned": both_facts,
                "fact_safety_ok": fact_safety_ok, "causal_ok": causal_ok}

    if key == "B":
        numbers_reduced = area["number_count"] < 4
        zero_numbers = area["number_count"] == 0
        intended = bool(both_facts and fact_safety_ok and causal_ok)
        return {"intended_pattern_b": intended, "numbers_reduced_vs_original_4": numbers_reduced,
                "zero_numbers_in_area": zero_numbers, "both_facts_mentioned": both_facts,
                "fact_safety_ok": fact_safety_ok, "causal_ok": causal_ok}

    if key == "C":
        has_delta_expr = any(m in area_lower for m in DELTA_EXPRESSION_MARKERS)
        acc = numeric_accuracy_check(area["area_text"])
        acc_ok = all(v["matched_within_1_0"] for v in acc["delta_matches"].values()) if has_delta_expr else False
        intended = bool(has_delta_expr and acc_ok and both_facts and fact_safety_ok and causal_ok)
        return {"intended_pattern_c": intended, "has_delta_expression": has_delta_expr,
                "numeric_accuracy": acc, "both_facts_mentioned": both_facts,
                "fact_safety_ok": fact_safety_ok, "causal_ok": causal_ok}

    return {}


def run_single(client, ledger_model, key: str, run_id: str, baseline_article_text: str,
                verified_ledger_text: str, extra_block: str | None) -> dict:
    print(f"[TRIAL-19] run={run_id}: Evidence Compression Editor呼び出し...")
    editor_result = trial18.run_editor_variant(client, baseline_article_text, extra_block)
    variant_text = editor_result["raw_text"]
    with open(f"{OUT_DIR}/audit/editor_raw_{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/article_{run_id}.md", "w", encoding="utf-8") as f:
        f.write(variant_text)

    print(f"[TRIAL-19] run={run_id}: Ledger Deviation Check...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, variant_text, model=ledger_model, hook_aware=True)
    with open(f"{OUT_DIR}/audit/ledger_deviation_{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)

    print(f"[TRIAL-19] run={run_id}: Fact Checker呼び出し...")
    fact_qa = trial18.run_fact_checker(client, trial18.TOPIC_EN, variant_text)
    with open(f"{OUT_DIR}/audit/fact_qa_{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa, f, ensure_ascii=False, indent=2, default=str)

    metrics = artgen.compute_metrics(variant_text)
    causal_found = trial18.scan_causal_markers(variant_text)
    causal_baseline = trial18.scan_causal_markers(baseline_article_text)
    causal_new = [m for m in causal_found if m not in causal_baseline]

    area = extract_f005_f006_area(variant_text)
    sent_stats = sentence_diff_stats(baseline_article_text, variant_text)
    diff_html = render_word_diff_html(baseline_article_text, variant_text)
    with open(f"{OUT_DIR}/audit/diff_{run_id}.html", "w", encoding="utf-8") as f:
        f.write(diff_html)

    deviations = deviation_result["parsed"]["deviations"]
    intended = intended_outcome_check(key, area, deviations, causal_new)

    run_summary = {
        "run_id": run_id, "pattern": key,
        "response_id": editor_result["response_id"],
        "metrics": metrics,
        "number_count_total": trial18.count_numbers(variant_text),
        "f005_f006_area": area,
        "sentence_diff_stats": sent_stats,
        "ledger_overall_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviations),
        "ledger_deviations": deviations,
        "fact_checker_status": fact_qa["final_status"],
        "fact_checker_verdict": (fact_qa["result"] or {}).get("verdict") if fact_qa["result"] else None,
        "fact_checker_unsupported_claim_count": len((fact_qa["result"] or {}).get("unsupported_specific_claims", [])) if fact_qa["result"] else None,
        "causal_markers_found": causal_found,
        "new_causal_markers_vs_baseline_input": causal_new,
        "intended_outcome_check": intended,
    }
    print(f"[TRIAL-19] run={run_id}: 完了。ledger={run_summary['ledger_overall_status']} "
          f"fact_verdict={run_summary['fact_checker_verdict']} "
          f"area_numbers={area['number_count']} new_causal={causal_new}")
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
        "runs_per_pattern": RUNS_PER_PATTERN,
        "runs": {},
    }

    for key, cfg in trial18.PATTERNS.items():
        for i in range(1, RUNS_PER_PATTERN + 1):
            run_id = f"{RUN_PREFIX[key]}_{i:02d}"
            run_summary = run_single(
                client, ledger_model, key, run_id, baseline_article_text,
                verified_ledger_text, cfg["extra"])
            summary["runs"][run_id] = run_summary
            with open(f"{OUT_DIR}/trial_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-19] 全20 run完了。summary -> {OUT_DIR}/trial_summary.json")


if __name__ == "__main__":
    main()
