# ============================================================
# er021_en_asr_semantic_equivalence_trial_01_run.py
# EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01: corpus + オフライン検証 + 実API
# 検証 + runtime計測のオーケストレーションスクリプト。
# ============================================================
# Production安全性: er006_preprod_hardening_01_validation.py等の既存
# Production moduleは一切変更しない(read-onlyでimportするだけ)。
# TTSを使う場合はTTS_EXECUTION_MODE=STANDARD、専用out-dir、既存記事
# artifactは無変更、cost loggerで実測費用を記録する。
from __future__ import annotations

import copy
import importlib.util
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import er021_en_asr_semantic_equivalence_trial_01 as sem
import er006_preprod_hardening_01_validation as val

OUT_DIR = sem.OUT_DIR
RESULTS_DIR = sem.RESULTS_DIR
AUDIT_DIR = sem.AUDIT_DIR
AUDIO_DIR = sem.AUDIO_DIR
CORPUS_PATH = sem.CORPUS_PATH
EXISTING_PROBE_PATH = sem.EXISTING_PROBE_PATH
FIXTURE_TEST_MODULE_PATH = sem.FIXTURE_TEST_MODULE_PATH


def log(msg):
    print(msg, flush=True)


# ============================================================
# corpus(POSITIVE >= 30, NEGATIVE >= 30)
# ============================================================
POSITIVE_CORPUS = [
    {"id": "P01_decimal_scale_currency_percent_real_probe", "mechanism": "tier1_numeric",
     "canonical": "The price rose to two point three million dollars, a fifteen percent increase from last year.",
     "asr": "The price rose to $2.3 million, a 15% increase from last year.",
     "label_source": "recon_en_asr_semantic_equivalence_01.md (a)",
     "evidence": EXISTING_PROBE_PATH},
    {"id": "P02_hundred_thousand_grouping_currency_percent", "mechanism": "tier1_numeric",
     "canonical": "The price rose to two million three hundred thousand dollars, a fifteen percent increase from last year.",
     "asr": "The price rose to $2.3 million, a 15% increase from last year.",
     "label_source": "recon_en_asr_semantic_equivalence_01.md (a) Local Rewrite candidate_2",
     "evidence": "TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md §12.3"},
    {"id": "P03_billion_scale_currency", "mechanism": "tier1_numeric",
     "canonical": "The company is now worth one point two billion dollars.",
     "asr": "The company is now worth $1.2 billion.",
     "label_source": "Fable review (billion missing from _SCALES)", "evidence": None},
    {"id": "P04_trillion_scale_currency", "mechanism": "tier1_numeric",
     "canonical": "Global spending reached three trillion dollars this year.",
     "asr": "Global spending reached $3 trillion this year.",
     "label_source": "Fable review (trillion)", "evidence": None},
    {"id": "P05_percent_word_vs_symbol", "mechanism": "tier1_numeric",
     "canonical": "Sales grew by twenty percent this quarter.",
     "asr": "Sales grew by 20% this quarter.",
     "label_source": "spec closed set (percent)", "evidence": None},
    {"id": "P06_currency_pounds", "mechanism": "tier1_numeric",
     "canonical": "The ticket costs fifty pounds.", "asr": "The ticket costs £50.",
     "label_source": "spec closed set (currency GBP)", "evidence": None},
    {"id": "P07_currency_euros", "mechanism": "tier1_numeric",
     "canonical": "The fee is seventy five euros.", "asr": "The fee is €75.",
     "label_source": "spec closed set (currency EUR)", "evidence": None},
    {"id": "P08_small_cardinal_regression", "mechanism": "baseline_normalized_match",
     "canonical": "Next, we will look at this issue from 2 more angles.",
     "asr": "Next, we will look at this issue from two more angles.",
     "label_source": "er006_preprod_hardening_01_validation_test.py POSITIVE_FIXTURES (existing, regression check)",
     "evidence": "er006_preprod_hardening_01_validation_test.py"},
    {"id": "P09_year_pair_1999", "mechanism": "tier1_numeric",
     "canonical": "The policy was introduced in 1999.",
     "asr": "The policy was introduced in nineteen ninety-nine.",
     "label_source": "Fable review A-3 (year pair reading)", "evidence": None},
    {"id": "P10_year_pair_2026", "mechanism": "tier1_numeric",
     "canonical": "The forecast covers the period through 2026.",
     "asr": "The forecast covers the period through twenty twenty-six.",
     "label_source": "Fable review A-3 (year pair reading)", "evidence": None},
    {"id": "P11_year_thousand_and", "mechanism": "tier1_numeric",
     "canonical": "The building opened in 2006.",
     "asr": "The building opened in two thousand and six.",
     "label_source": "Fable review A-3 (year pair reading)", "evidence": None},
    {"id": "P12_year_thousand_no_and", "mechanism": "tier1_numeric",
     "canonical": "The report was published in 2010.",
     "asr": "The report was published in two thousand ten.",
     "label_source": "Fable review A-3 (year pair reading)", "evidence": None},
    {"id": "P13_time_pm", "mechanism": "tier1_numeric",
     "canonical": "The meeting starts at 3:30 pm.",
     "asr": "The meeting starts at three thirty pm.",
     "label_source": "spec closed set (time h:mm + am/pm)", "evidence": None},
    {"id": "P14_time_am_oh", "mechanism": "tier1_numeric",
     "canonical": "The train departs at 6:05 am.",
     "asr": "The train departs at six oh five am.",
     "label_source": "spec closed set (time h:mm + am/pm)", "evidence": None},
    {"id": "P15_fraction_half", "mechanism": "tier1_numeric",
     "canonical": "About one half of the group agreed.", "asr": "About 1/2 of the group agreed.",
     "label_source": "spec closed set (simple fraction)", "evidence": None},
    {"id": "P16_fraction_third", "mechanism": "tier1_numeric",
     "canonical": "A third of respondents said yes.", "asr": "1/3 of respondents said yes.",
     "label_source": "spec closed set (simple fraction)", "evidence": None},
    {"id": "P17_fraction_two_thirds", "mechanism": "tier1_numeric",
     "canonical": "Two thirds of the students passed.", "asr": "2/3 of the students passed.",
     "label_source": "spec closed set (simple fraction)", "evidence": None},
    {"id": "P18_fraction_three_quarters", "mechanism": "tier1_numeric",
     "canonical": "Three quarters of the budget was spent.", "asr": "3/4 of the budget was spent.",
     "label_source": "spec closed set (simple fraction)", "evidence": None},
    {"id": "P19_roman_numeral_ww2", "mechanism": "tier1_numeric",
     "canonical": "The article discusses World War II history.",
     "asr": "The article discusses World War 2 history.",
     "label_source": "Fable review #3 (roman numeral risk)", "evidence": None},
    {"id": "P20_roman_numeral_henry", "mechanism": "tier1_numeric",
     "canonical": "The exhibit features Henry VIII portraits.",
     "asr": "The exhibit features Henry 8 portraits.",
     "label_source": "Fable review #3 (roman numeral risk)", "evidence": None},
    {"id": "P21_no_dot_number", "mechanism": "tier1_numeric",
     "canonical": "Model No. 5 was recalled.", "asr": "Model number 5 was recalled.",
     "label_source": "spec closed set (No. <-> number)", "evidence": None},
    {"id": "P22_ampersand_and", "mechanism": "tier1_numeric",
     "canonical": "The report covers Q3 & Q4 results.", "asr": "The report covers Q3 and Q4 results.",
     "label_source": "spec closed set (& <-> and)", "evidence": None},
    {"id": "P23_minus_dash", "mechanism": "tier1_numeric",
     "canonical": "The temperature dropped to minus five degrees.",
     "asr": "The temperature dropped to -5 degrees.",
     "label_source": "spec closed set (minus <-> -)", "evidence": None},
    {"id": "P24_comma_grouped_large_number", "mechanism": "tier1_numeric",
     "canonical": "The population is 2,300,000 people.",
     "asr": "The population is two million three hundred thousand people.",
     "label_source": "spec closed set (comma grouping, distinct from 7+ digit ID protection)",
     "evidence": None},
    {"id": "P25_point_points_real_production_case", "mechanism": "tier3_corroboration",
     "canonical": "We need to bring the main point together.",
     "asr": "We need to bring the main points together.",
     "secondary_text": "We need to bring the main point together.",
     "label_source": "recon_en_asr_semantic_equivalence_01.md (g), TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md §12.2 (comment_4)",
     "evidence": "TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md"},
    {"id": "P26_dollar_dollars_plural", "mechanism": "tier1_numeric_or_tier3",
     "canonical": "It costs one dollar.", "asr": "It costs one dollars.",
     "secondary_text": "It costs one dollar.",
     "label_source": "recon_en_asr_semantic_equivalence_02_tier2_tier3.md T3-1-f", "evidence": None},
    {"id": "P27_report_reports_plural", "mechanism": "tier3_corroboration",
     "canonical": "The team filed one report last week.",
     "asr": "The team filed one reports last week.",
     "secondary_text": "The team filed one report last week.",
     "label_source": "recon_en_asr_semantic_equivalence_02_tier2_tier3.md T3-1-b", "evidence": None},
    {"id": "P28_entity_ottoni_otani", "mechanism": "tier3_corroboration",
     "canonical": "Ottoni and colleagues found similar results.",
     "asr": "Otani and colleagues found similar results.",
     "secondary_text": "Ottoni and colleagues found similar results.",
     "label_source": "recon_en_asr_semantic_equivalence_02_tier2_tier3.md T3-1-d", "evidence": None},
    {"id": "P29_entity_triangeln_triangle", "mechanism": "tier3_corroboration",
     "canonical": "Triangeln station is nearby.", "asr": "Triangle station is nearby.",
     "secondary_text": "Triangeln station is nearby.",
     "label_source": "recon_en_asr_semantic_equivalence_02_tier2_tier3.md T3-1-e", "evidence": None},
    {"id": "P30_compound_word_boundary_regression", "mechanism": "baseline_normalized_match",
     "canonical": "blitzscaling", "asr": "Blitz scaling.",
     "label_source": "er006_preprod_hardening_01_validation_test.py POSITIVE_FIXTURES (existing, regression check)",
     "evidence": "er006_preprod_hardening_01_validation_test.py"},
    {"id": "P31_hyphenated_cardinal_28", "mechanism": "tier1_numeric",
     "canonical": "Item 28 was updated.", "asr": "Item twenty-eight was updated.",
     "label_source": "spec closed set (cardinal word <-> digit, generalized)", "evidence": None},
    {"id": "P32_hundred_currency_no_scale_word", "mechanism": "tier1_numeric",
     "canonical": "The device costs one hundred dollars.", "asr": "The device costs $100.",
     "label_source": "spec closed set (currency, hundred)", "evidence": None},
    {"id": "P33_percent_75", "mechanism": "tier1_numeric",
     "canonical": "Approval rating stands at seventy five percent.",
     "asr": "Approval rating stands at 75%.",
     "label_source": "spec closed set (percent)", "evidence": None},
    {"id": "P34_year_pair_1975", "mechanism": "tier1_numeric",
     "canonical": "The festival started in 1975.",
     "asr": "The festival started in nineteen seventy-five.",
     "label_source": "Fable review A-3 (year pair reading)", "evidence": None},
]

NEGATIVE_CORPUS = [
    {"id": "N01_million_value_2_3_vs_2_5", "canonical": "The price rose to $2.3 million.",
     "asr": "The price rose to $2.5 million.",
     "label_source": "Fable review #2 (NEGATIVE corpus requirement)", "evidence": None},
    {"id": "N02_fifteen_vs_fifty", "canonical": "There were fifteen participants.",
     "asr": "There were fifty participants.",
     "label_source": "Fable review #2 (fifteen vs fifty)", "evidence": None},
    {"id": "N03_15_percent_vs_50_percent", "canonical": "15% of users clicked.",
     "asr": "50% of users clicked.",
     "label_source": "Fable review #2 (15% vs 50%)", "evidence": None},
    {"id": "N04_percent_vs_percentage_points", "canonical": "Inflation rose by five percent.",
     "asr": "Inflation rose by five percentage points.",
     "label_source": "Fable review #2 (percent vs percentage points, protected)", "evidence": None},
    {"id": "N05_currency_presence", "canonical": "The device costs $100.",
     "asr": "The device costs 100.",
     "label_source": "Fable review #2 ($ present/absent, protected)", "evidence": None},
    {"id": "N06_year_1999_vs_1990", "canonical": "The law passed in 1999.",
     "asr": "The law passed in nineteen ninety.",
     "label_source": "Fable review #2 (1999 vs 1990)", "evidence": None},
    {"id": "N07_million_vs_billion", "canonical": "The company is worth two point three million dollars.",
     "asr": "The company is worth $2.3 billion.",
     "label_source": "Fable review #2 (million vs billion)", "evidence": None},
    {"id": "N08_minus_vs_plus", "canonical": "The adjustment was minus five points.",
     "asr": "The adjustment was plus five points.",
     "label_source": "Fable review #2 (minus vs plus, protected)", "evidence": None},
    {"id": "N09_about_20_vs_20", "canonical": "About 20 people attended.",
     "asr": "20 people attended.",
     "label_source": "Fable review #6 (approximate protected)", "evidence": None},
    {"id": "N10_tense_will_vs_was", "canonical": "The bridge will be rolled out next year.",
     "asr": "The bridge was rolled out next year.",
     "label_source": "recon_en_asr_semantic_equivalence_02_tier2_tier3.md T3-2 (時列1)", "evidence": None},
    {"id": "N11_tense_rising_vs_rose", "canonical": "Prices are rising.", "asr": "Prices rose.",
     "label_source": "recon_02 T3-2 (時列2)", "evidence": None},
    {"id": "N12_tense_will_complete_vs_completed", "canonical": "She will complete the project.",
     "asr": "She completed the project.",
     "label_source": "recon_02 T3-2 (時列3)", "evidence": None},
    {"id": "N13_negation_effective", "canonical": "The vaccine is effective.",
     "asr": "The vaccine is not effective.",
     "label_source": "recon_02 T3-2 (否定1)", "evidence": None},
    {"id": "N14_negation_can_cannot", "canonical": "He can attend.", "asr": "He cannot attend.",
     "label_source": "recon_02 T3-2 (否定2)", "evidence": None},
    {"id": "N15_negation_prefix_unsafe", "canonical": "This is safe.", "asr": "This is unsafe.",
     "label_source": "recon_02 T3-2 (否定3)", "evidence": None},
    {"id": "N16_value_5_vs_15_percent", "canonical": "The price rose 5 percent.",
     "asr": "The price rose 15 percent.",
     "label_source": "recon_02 T3-2 (値1)", "evidence": None},
    {"id": "N17_value_2_vs_3_million", "canonical": "The population is 2 million.",
     "asr": "The population is 3 million.",
     "label_source": "recon_02 T3-2 (値2)", "evidence": None},
    {"id": "N18_value_10_vs_100_dollars", "canonical": "Revenue increased by $10.",
     "asr": "Revenue increased by $100.",
     "label_source": "recon_02 T3-2 (値3)", "evidence": None},
    {"id": "N19_cant_vs_can", "canonical": "You can't enter without a badge.",
     "asr": "You can enter without a badge.",
     "label_source": "recon_02 T2-2-2 (negation reversal)", "evidence": None},
    {"id": "N20_wont_vs_will", "canonical": "The system won't restart automatically.",
     "asr": "The system will restart automatically.",
     "label_source": "recon_02 (negation reversal, will/won't)", "evidence": None},
    {"id": "N21_point_points_no_corroboration", "canonical": "The team is down one point.",
     "asr": "The team is down one points.",
     "label_source": "Fable final review (point is polysemous, rescue must require corroboration; here none given)",
     "evidence": None},
    {"id": "N22_different_place_entity_no_corroboration", "canonical": "The plant is located in Georgia.",
     "asr": "The plant is located in Jordan.",
     "label_source": "Fable review #13/T3-1-e note (different real-world referent, no corroboration given)",
     "evidence": None},
    {"id": "N23_entity_corroboration_contradicts", "canonical": "Ottoni and colleagues found similar results.",
     "asr": "Otani and colleagues found similar results.",
     "secondary_text": "Otani and colleagues found similar results.",
     "label_source": "corroboration robustness (secondary ASR repeats the same error, must not rescue)",
     "evidence": None},
    {"id": "N24_homophone_wait_weight_not_rescued", "canonical": "Please wait for the results.",
     "asr": "Please weight for the results.",
     "label_source": "recon_02 T3-1-c (homophone_only is out of Tier3 corroboration scope)",
     "evidence": None},
    {"id": "N25_dunno_out_of_scope", "canonical": "I don't know the answer.",
     "asr": "I dunno the answer.",
     "label_source": "recon_02 T2-2-10 (Phase C/Tier2 excluded from this Trial)", "evidence": None},
    {"id": "N26_wanna_out_of_scope", "canonical": "Do you want to join us?",
     "asr": "Do you wanna join us?",
     "label_source": "OPEN-123 2026-09-07 decision (Tier2 excluded from this Trial)", "evidence": None},
    {"id": "N27_digit_by_digit_id_words", "canonical": "The code is one two three.",
     "asr": "The code is 123.",
     "label_source": "spec safety rule (consecutive lone digit words must not combine)", "evidence": None},
    {"id": "N28_seven_digit_id_spelled", "canonical": "The reference number is 1234567.",
     "asr": "The reference number is one two three four five six seven.",
     "label_source": "spec safety rule (7+ digit raw ID must not combine)", "evidence": None},
    {"id": "N29_date_slash_ambiguity", "canonical": "The event is on 4/3.",
     "asr": "The event is on 3/4.",
     "label_source": "safety net (N/M pattern reused for fractions, must not collide with dates)",
     "evidence": None},
    {"id": "N30_minus_word_missing", "canonical": "The margin was minus five percent.",
     "asr": "The margin was five percent.",
     "label_source": "safety net (minus word must be protected, not silently dropped)", "evidence": None},
    {"id": "N31_currency_type_mismatch", "canonical": "The fee is fifty dollars.",
     "asr": "The fee is £50.",
     "label_source": "Trial design choice (currency type protected in addition to presence)",
     "evidence": None},
    {"id": "N32_time_meridiem_mismatch", "canonical": "The meeting starts at 3:30 pm.",
     "asr": "The meeting starts at 3:30 am.",
     "label_source": "spec closed set (meridiem protected)", "evidence": None},
    {"id": "N33_time_value_mismatch_spelled", "canonical": "The train departs at six oh five am.",
     "asr": "The train departs at 6:50 am.",
     "label_source": "safety net (spoken time value precision)", "evidence": None},
    {"id": "N34_roman_numeral_mismatch", "canonical": "The exhibit features Henry VIII portraits.",
     "asr": "The exhibit features Henry 7 portraits.",
     "label_source": "safety net (roman numeral value precision)", "evidence": None},
]


def write_corpus_jsonl():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        for item in POSITIVE_CORPUS:
            rec = dict(item)
            rec["expected"] = "PASS"
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        for item in NEGATIVE_CORPUS:
            rec = dict(item)
            rec["expected"] = "FAIL"
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    log(f"corpus written: {CORPUS_PATH} (POSITIVE={len(POSITIVE_CORPUS)}, NEGATIVE={len(NEGATIVE_CORPUS)})")


# ============================================================
# オフライン検証(Part 1: 自作corpus、Part 2: OPEN-123既存fixture 59件)
# ============================================================
def run_offline_corpus_validation():
    log("\n=== オフライン検証: corpus(POSITIVE/NEGATIVE) ===")
    rows = []
    positive_rescued = 0
    negative_false_accept = 0
    for item in POSITIVE_CORPUS:
        baseline = val.classify_asr_match(item["canonical"], item["asr"])
        new = sem.classify_semantic_equivalence(
            item["canonical"], item["asr"],
            secondary_text=item.get("secondary_text"), local_text=item.get("local_text"))
        rescued = (not baseline.should_pass) and new["should_pass"]
        if new["should_pass"]:
            positive_rescued += 1
        rows.append({
            "id": item["id"], "category": "POSITIVE", "canonical": item["canonical"], "asr": item["asr"],
            "baseline_classification": baseline.classification, "baseline_should_pass": baseline.should_pass,
            "new_classification": new["classification"], "new_should_pass": new["should_pass"],
            "sub_reason": new["sub_reason"], "tier_applied": new["tier_applied"], "rescued": rescued,
            "label_source": item["label_source"], "evidence": item.get("evidence"),
        })
        log(f"  [{'PASS' if new['should_pass'] else 'FAIL'}] {item['id']}: "
            f"baseline={baseline.classification} -> new={new['classification']} (tier={new['tier_applied']})")
    for item in NEGATIVE_CORPUS:
        baseline = val.classify_asr_match(item["canonical"], item["asr"])
        new = sem.classify_semantic_equivalence(
            item["canonical"], item["asr"],
            secondary_text=item.get("secondary_text"), local_text=item.get("local_text"))
        if new["should_pass"]:
            negative_false_accept += 1
        rows.append({
            "id": item["id"], "category": "NEGATIVE", "canonical": item["canonical"], "asr": item["asr"],
            "baseline_classification": baseline.classification, "baseline_should_pass": baseline.should_pass,
            "new_classification": new["classification"], "new_should_pass": new["should_pass"],
            "sub_reason": new["sub_reason"], "tier_applied": new["tier_applied"],
            "false_accept": new["should_pass"],
            "label_source": item["label_source"], "evidence": item.get("evidence"),
        })
        tag = "FALSE_ACCEPT!!" if new["should_pass"] else "OK(correctly rejected)"
        log(f"  [{tag}] {item['id']}: baseline={baseline.classification} -> new={new['classification']}")

    summary = {
        "positive_count": len(POSITIVE_CORPUS), "positive_rescued_or_pass": positive_rescued,
        "negative_count": len(NEGATIVE_CORPUS), "negative_false_accept": negative_false_accept,
    }
    log(f"corpus summary: {summary}")
    return rows, summary


def run_existing_fixture_regression():
    log("\n=== 既存Regression fixture(er006_preprod_hardening_01_validation_test.py、59件)無回帰確認 ===")
    spec = importlib.util.spec_from_file_location("_er006_fixtures", FIXTURE_TEST_MODULE_PATH)
    fixmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixmod)

    rows = []
    regressions = 0
    false_accepts = 0
    for fx in fixmod.POSITIVE_FIXTURES:
        baseline = val.classify_asr_match(fx["canonical"], fx["asr"])
        new = sem.classify_semantic_equivalence(fx["canonical"], fx["asr"])
        # POSITIVE fixtureの受入条件は既存fixtureのdocstring通り
        # 「should_pass=True または should_retry=False」(不要retryを
        # 起こさない)であり、should_pass=True一択ではない。
        ok = new["should_pass"] or not new["should_retry"]
        if not ok:
            regressions += 1
        rows.append({"name": fx["name"], "group": "POSITIVE",
                      "baseline_classification": baseline.classification,
                      "new_classification": new["classification"], "ok": ok})
        log(f"  [{'OK' if ok else 'REGRESSION'}] POSITIVE {fx['name'][:60]}: "
            f"baseline={baseline.classification} new={new['classification']}")
    for fx in fixmod.NEGATIVE_FIXTURES:
        baseline = val.classify_asr_match(fx["canonical"], fx["asr"])
        new = sem.classify_semantic_equivalence(fx["canonical"], fx["asr"])
        false_accept = new["should_pass"]
        if false_accept:
            false_accepts += 1
        rows.append({"name": fx["name"], "group": "NEGATIVE",
                      "baseline_classification": baseline.classification,
                      "new_classification": new["classification"], "false_accept": false_accept})
        log(f"  [{'FALSE_ACCEPT!!' if false_accept else 'OK'}] NEGATIVE {fx['name'][:60]}: "
            f"baseline={baseline.classification} new={new['classification']}")
    for fx in fixmod.AMBIGUOUS_FIXTURES:
        baseline = val.classify_asr_match(fx["canonical"], fx["asr"])
        new = sem.classify_semantic_equivalence(fx["canonical"], fx["asr"])
        unchanged = new["classification"] == baseline.classification or new["tier_applied"] == "baseline"
        rows.append({"name": fx["name"], "group": "AMBIGUOUS",
                      "baseline_classification": baseline.classification,
                      "new_classification": new["classification"], "unchanged": unchanged})
        log(f"  [{'OK' if unchanged else 'CHANGED'}] AMBIGUOUS {fx['name'][:60]}: "
            f"baseline={baseline.classification} new={new['classification']}")

    total = len(fixmod.POSITIVE_FIXTURES) + len(fixmod.NEGATIVE_FIXTURES) + len(fixmod.AMBIGUOUS_FIXTURES)
    summary = {"total": total, "positive": len(fixmod.POSITIVE_FIXTURES),
               "negative": len(fixmod.NEGATIVE_FIXTURES), "ambiguous": len(fixmod.AMBIGUOUS_FIXTURES),
               "regressions": regressions, "false_accepts": false_accepts}
    log(f"fixture regression summary: {summary}")
    return rows, summary


def run_python_regression_suite():
    log("\n=== 既存regression(python -m unittest discover)無変化確認 ===")
    import subprocess
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "*_test_01.py"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        cwd=os.path.dirname(os.path.abspath(__file__)) or ".")
    tail = "\n".join(((r.stdout or "") + (r.stderr or "")).splitlines()[-15:])
    log(tail)
    return {"returncode": r.returncode, "tail": tail}


# ============================================================
# runtime影響計測(1,000回平均)
# ============================================================
def run_latency_benchmark(n=1000):
    log(f"\n=== runtime影響計測({n}回平均) ===")
    canonical = POSITIVE_CORPUS[0]["canonical"]
    asr = POSITIVE_CORPUS[0]["asr"]

    t0 = time.perf_counter()
    for _ in range(n):
        val.classify_asr_match(canonical, asr)
    t_baseline = (time.perf_counter() - t0) / n

    t0 = time.perf_counter()
    for _ in range(n):
        sem.classify_semantic_equivalence(canonical, asr)
    t_new = (time.perf_counter() - t0) / n

    # Tier1が発火しないケース(baselineへフォールスルーする分の追加コスト)
    canonical2 = "The team increased the budget for next quarter."
    asr2 = "The team decreased the budget for next quarter."
    t0 = time.perf_counter()
    for _ in range(n):
        val.classify_asr_match(canonical2, asr2)
    t_baseline_fallthrough = (time.perf_counter() - t0) / n
    t0 = time.perf_counter()
    for _ in range(n):
        sem.classify_semantic_equivalence(canonical2, asr2)
    t_new_fallthrough = (time.perf_counter() - t0) / n

    result = {
        "iterations": n,
        "tier1_hit_case": {
            "baseline_ms": round(t_baseline * 1000, 4), "new_module_ms": round(t_new * 1000, 4),
            "delta_ms": round((t_new - t_baseline) * 1000, 4),
        },
        "tier1_fallthrough_case": {
            "baseline_ms": round(t_baseline_fallthrough * 1000, 4),
            "new_module_ms": round(t_new_fallthrough * 1000, 4),
            "delta_ms": round((t_new_fallthrough - t_baseline_fallthrough) * 1000, 4),
        },
    }
    log(json.dumps(result, ensure_ascii=False, indent=2))
    return result


# ============================================================
# 実API検証(既存probeの再判定 + 新規probe少数、TTS_EXECUTION_MODE=STANDARD)
# ============================================================
def reclassify_existing_probe():
    log("\n=== 既存probe再判定(comment_test2、再生成せず、¥0) ===")
    if not os.path.exists(EXISTING_PROBE_PATH):
        log(f"  !! {EXISTING_PROBE_PATH} が見つかりません、スキップ")
        return None
    probe = json.load(open(EXISTING_PROBE_PATH, encoding="utf-8"))
    canonical = "The price rose to two point three million dollars, a fifteen percent increase from last year."
    rows = []
    for log_name in ("standard_attempts_log", "fallback_attempts_log"):
        for att in probe.get(log_name, []):
            asr_text = att.get("asr_text")
            baseline_label = att.get("audio_classification")
            new = sem.classify_semantic_equivalence(canonical, asr_text)
            rows.append({
                "log": log_name, "attempt": att.get("attempt"), "asr_text": asr_text,
                "original_audio_classification": baseline_label,
                "new_classification": new["classification"], "new_should_pass": new["should_pass"],
                "tier_applied": new["tier_applied"],
            })
            log(f"  attempt {att.get('attempt')} ({log_name}): {baseline_label} -> "
                f"{new['classification']} (should_pass={new['should_pass']})")
    return {"canonical": canonical, "probe_path": EXISTING_PROBE_PATH, "attempts": rows,
            "would_have_avoided_human_review_lock": all(r["new_should_pass"] for r in rows)}


NEW_PROBES = [
    {"id": "probe_a_billion_decimal_currency",
     "canonical": "The company reported profits of four point seven billion dollars this quarter."},
    {"id": "probe_b_percent_decimal",
     "canonical": "Growth came in at two point five percent this month."},
    {"id": "probe_c_plural_regular_noun",
     "canonical": "We identified one clear trend in the data."},
    {"id": "probe_d_year_spelled",
     "canonical": "The measure passed in twenty twenty-six."},
    {"id": "probe_e_roman_numeral",
     "canonical": "The report cites World War II casualties."},
    {"id": "probe_f_currency_no_scale",
     "canonical": "The kit costs one hundred twenty five dollars."},
]


def run_new_tts_probes():
    log("\n=== 新規実TTS/ASR probe(TTS_EXECUTION_MODE=STANDARD) ===")
    import er003_b1_p9a_audio as p9a
    import er006_asr_provider_routing_01 as asr_routing
    import er006_secondary_asr_01 as secondary_asr
    import er008_disfluency_qa_18 as disfluency_qa
    import er005_cost_logger as cost_logger
    import soundfile as sf

    cost_logger.install(sem.COST_LOG_PATH)

    results = []
    for item in NEW_PROBES:
        item_id, canonical = item["id"], item["canonical"]
        out_path = f"{AUDIO_DIR}/{item_id}.wav"
        log(f"\n--- {item_id} ---\n  canonical: {canonical!r}")
        if os.path.exists(out_path):
            log(f"  [reuse] {out_path} 既存のためTTS再生成をスキップ(二重課金防止)")
        else:
            gen = p9a.generate_narration_snippet(canonical, "en", out_path)
            sem.assert_budget_ok(f"after TTS {item_id}")
            if gen.get("status") != "OK":
                log(f"  !! TTS failed: {gen.get('reason')}")
                results.append({"id": item_id, "status": "TTS_FAILED", "canonical": canonical})
                continue

        primary_text, primary_err = asr_routing.transcribe(out_path, language="en")
        sem.assert_budget_ok(f"after PrimaryASR {item_id}")

        baseline = val.classify_asr_match(canonical, primary_text)
        new_primary_only = sem.classify_semantic_equivalence(canonical, primary_text)

        secondary_text = None
        local_text = None
        if not new_primary_only["should_pass"]:
            # Cascadeが既存で持つSecondary/Local ASR呼び出しをそのまま
            # 「呼ぶだけ」で再利用する(判定層の検証のみ、cool-down/Local
            # Rewriteは一切発火させない)。
            dur = sf.info(out_path).duration
            secondary_text, secondary_err = secondary_asr.get_full_text_via_azure_stt_with_phrase_list(
                out_path, language="en-US", phrases=None)
            sem.record_azure_call(dur)
            sem.assert_budget_ok(f"after SecondaryASR {item_id}")
            local_text = disfluency_qa.transcribe_verbatim(out_path, language="en", model_size="small")
            local_text = " ".join(w["text"].strip() for w in local_text).strip()

        new_full = sem.classify_semantic_equivalence(
            canonical, primary_text, secondary_text=secondary_text, local_text=local_text)

        row = {
            "id": item_id, "status": "OK", "canonical": canonical,
            "audio_sha256": sem.sha256_of(out_path),
            "primary_asr_text": primary_text, "primary_asr_error": primary_err,
            "secondary_asr_text": secondary_text, "local_asr_text": local_text,
            "baseline_classification": baseline.classification, "baseline_should_pass": baseline.should_pass,
            "new_classification": new_full["classification"], "new_should_pass": new_full["should_pass"],
            "tier_applied": new_full["tier_applied"], "sub_reason": new_full["sub_reason"],
            "corroborated_by": new_full["corroborated_by"],
        }
        results.append(row)
        log(f"  primary_asr={primary_text!r}")
        log(f"  baseline={baseline.classification} should_pass={baseline.should_pass}")
        log(f"  new={new_full['classification']} should_pass={new_full['should_pass']} tier={new_full['tier_applied']}")
    return results


def main():
    write_corpus_jsonl()
    corpus_rows, corpus_summary = run_offline_corpus_validation()
    fixture_rows, fixture_summary = run_existing_fixture_regression()
    regression = run_python_regression_suite()
    latency = run_latency_benchmark()
    existing_probe = reclassify_existing_probe()

    jpy_before_tts, _ = sem.compute_cost_jpy_so_far()
    log(f"\n[budget] before real TTS probes: {jpy_before_tts:.2f} JPY (cap {sem.BUDGET_JPY_CAP})")
    new_probes = run_new_tts_probes()
    jpy_final, by_provider = sem.compute_cost_jpy_so_far()

    output = {
        "management_id": "EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01",
        "corpus_summary": corpus_summary, "corpus_rows": corpus_rows,
        "fixture_regression_summary": fixture_summary, "fixture_regression_rows": fixture_rows,
        "python_unittest_regression": regression,
        "latency_benchmark": latency,
        "existing_probe_reclassification": existing_probe,
        "new_tts_probes": new_probes,
        "final_cost_jpy": round(jpy_final, 2), "cost_by_provider_jpy": by_provider,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = f"{RESULTS_DIR}/trial_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    log(f"\n=== 完了。結果: {out_path} ===")
    log(f"最終費用: {jpy_final:.2f} JPY (内訳 {by_provider})")
    return output


if __name__ == "__main__":
    main()
