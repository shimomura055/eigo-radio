# ============================================================
# er011_point_quality_stage1_recomputation_01.py
# FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01 作業2 (a)-(d),(f)-(g)
# ============================================================
# 読み取り専用の事後再集計。既存JSON(point_overlap_article_retry_log.json/
# point_overlap_qa.json/analysis.json/point_role_planning_initial.json)を
# 読むだけで、新規API呼び出し・Production/Prompt編集は一切行わない。
# ============================================================
from __future__ import annotations

import json
import statistics
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path("C:/Users/tensh/eigo-radio")
OUT_DIR = ROOT / "er011_output" / "point_quality_stage1_recomputation_01"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ============================================================
# Enumerate all 50 runs across 4 trials (same structure as Haiku L0
# aggregation, er011_point_quality_retry_log_aggregation_l0_01.py)
# ============================================================
def enumerate_runs():
    runs = []

    t06 = ROOT / "er011_output" / "news_focus_hint_comparison_trial_06"
    for theme in ["a2", "b1b"]:
        for condition in ["baseline", "focus_hint", "hint_only"]:
            for run in ["run1", "run2", "run3"]:
                base = t06 / theme / condition / run
                if (base / "point_overlap_article_retry_log.json").exists():
                    runs.append({"trial": "trial_06", "theme": theme, "condition": condition,
                                 "run": run, "base": base})

    t04 = ROOT / "er011_output" / "daily_news_focus_layer_comparison_trial_04"
    for theme in ["a2", "b1b"]:
        for condition in ["baseline", "focus"]:
            for run in ["run1", "run2", "run3"]:
                base = t04 / theme / condition / run
                if (base / "point_overlap_article_retry_log.json").exists():
                    runs.append({"trial": "trial_04", "theme": theme, "condition": condition,
                                 "run": run, "base": base})

    t05 = ROOT / "er011_output" / "point_overlap_gap_fix_trial_05"
    for theme_root in ["hanshin", "theme2"]:
        for level in ["a2", "b1b"]:
            for condition in ["baseline", "gapfix"]:
                for run in ["run1", "run2"]:
                    base = t05 / theme_root / level / condition / run
                    if (base / "point_overlap_article_retry_log.json").exists():
                        runs.append({"trial": "trial_05", "theme": f"{theme_root}/{level}",
                                     "condition": condition, "run": run, "base": base})

    t07 = ROOT / "er011_output" / "discovery_layer3_focus_trial_07"
    for theme in ["a2", "b1b"]:
        for condition in ["baseline", "discovery_focus"]:
            for run in ["run1", "run2", "run3"]:
                base = t07 / theme / condition / run
                if (base / "point_overlap_article_retry_log.json").exists():
                    runs.append({"trial": "trial_07", "theme": theme, "condition": condition,
                                 "run": run, "base": base})

    return runs


def load_run_data(run):
    base = run["base"]
    retry_log = safe_read_json(base / "point_overlap_article_retry_log.json") or []
    analysis = safe_read_json(base / "analysis.json") or {}
    role_initial = (safe_read_json(base / "audit" / "point_role_planning_initial.json")
                     or safe_read_json(base / "point_role_planning_initial.json"))
    run["retry_log"] = retry_log
    run["analysis"] = analysis
    run["role_initial"] = role_initial
    return run


RUNS = [load_run_data(r) for r in enumerate_runs()]

print(f"Total runs enumerated: {len(RUNS)}", file=__import__("sys").stderr)
by_trial = Counter(r["trial"] for r in RUNS)
print(dict(by_trial), file=__import__("sys").stderr)

# ============================================================
# Fixed definitions (per Fable delegation)
# ============================================================
NG_STATUSES = {"NG_REVIEW_REQUIRED", "FAIL"}


def run_is_ng(run):
    status = run["analysis"].get("status")
    if status is not None:
        return status in NG_STATUSES or (isinstance(status, str) and status.startswith("FAIL"))
    # fallback: infer from last attempt flags if analysis.json missing/incomplete
    attempts = run["retry_log"]
    if not attempts:
        return None
    last = attempts[-1]
    return bool(last.get("lexical_flagged") or last.get("value_qa_flagged"))


# ============================================================
# (a) Point distinct content word count vs overlap_ratio
# ============================================================
def analyze_a():
    rows = []
    for run in RUNS:
        for att in run["retry_log"]:
            report = att.get("report") or {}
            for point_key in ("point_one", "point_two"):
                pdata = report.get(point_key, {}).get("before_overlap")
                if not pdata:
                    continue
                wc = pdata.get("point_word_count")
                ratio = pdata.get("overlap_ratio")
                if wc is None or ratio is None:
                    continue
                rows.append({
                    "trial": run["trial"], "theme": run["theme"], "condition": run["condition"],
                    "run": run["run"], "attempt": att.get("attempt"), "point": point_key,
                    "point_word_count": wc, "overlap_ratio": ratio,
                })

    word_counts = [r["point_word_count"] for r in rows]
    ratios = [r["overlap_ratio"] for r in rows]
    n = len(rows)
    corr = None
    if n > 1 and len(set(word_counts)) > 1:
        corr = statistics.correlation(word_counts, ratios)

    # per-word-count bucket means (stratification)
    by_wc_bucket = defaultdict(list)
    for r in rows:
        wc = r["point_word_count"]
        bucket = f"{(wc // 5) * 5}-{(wc // 5) * 5 + 4}"
        by_wc_bucket[bucket].append(r["overlap_ratio"])
    bucket_means = {k: {"n": len(v), "mean_ratio": round(statistics.mean(v), 4)}
                     for k, v in sorted(by_wc_bucket.items())}

    # per-word "shared word count" reconstruction: shared = ratio * wc (approx int)
    per_word_deltas = []
    for r in rows:
        shared_est = r["overlap_ratio"] * r["point_word_count"]
        per_word_deltas.append(shared_est / r["point_word_count"] if r["point_word_count"] else None)

    # baseline vs focus/focus_hint/discovery_focus/gapfix/focus, stratified by word-count decile
    condition_labels = {
        "trial_06": {"control": "baseline", "treatment": ["focus_hint", "hint_only"]},
        "trial_04": {"control": "baseline", "treatment": ["focus"]},
        "trial_05": {"control": "baseline", "treatment": ["gapfix"]},
        "trial_07": {"control": "baseline", "treatment": ["discovery_focus"]},
    }
    strat_results = {}
    for trial, labels in condition_labels.items():
        control_rows = [r for r in rows if r["trial"] == trial and r["condition"] == labels["control"]]
        for treat_label in labels["treatment"]:
            treat_rows = [r for r in rows if r["trial"] == trial and r["condition"] == treat_label]
            if not control_rows or not treat_rows:
                continue
            control_wc_mean = statistics.mean(r["point_word_count"] for r in control_rows)
            treat_wc_mean = statistics.mean(r["point_word_count"] for r in treat_rows)
            control_ratio_mean = statistics.mean(r["overlap_ratio"] for r in control_rows)
            treat_ratio_mean = statistics.mean(r["overlap_ratio"] for r in treat_rows)

            # word-count-matched stratification: bucket by 5-word bins, compare only
            # buckets present in both control and treatment
            control_by_bucket = defaultdict(list)
            treat_by_bucket = defaultdict(list)
            for r in control_rows:
                b = r["point_word_count"] // 5
                control_by_bucket[b].append(r["overlap_ratio"])
            for r in treat_rows:
                b = r["point_word_count"] // 5
                treat_by_bucket[b].append(r["overlap_ratio"])
            common_buckets = sorted(set(control_by_bucket) & set(treat_by_bucket))
            matched_control_vals = []
            matched_treat_vals = []
            for b in common_buckets:
                matched_control_vals.extend(control_by_bucket[b])
                matched_treat_vals.extend(treat_by_bucket[b])

            strat_results[f"{trial}:{treat_label}"] = {
                "n_control": len(control_rows), "n_treat": len(treat_rows),
                "control_wc_mean": round(control_wc_mean, 2), "treat_wc_mean": round(treat_wc_mean, 2),
                "control_ratio_mean_unstratified": round(control_ratio_mean, 4),
                "treat_ratio_mean_unstratified": round(treat_ratio_mean, 4),
                "unstratified_diff": round(treat_ratio_mean - control_ratio_mean, 4),
                "common_wc_buckets(5-word bins)": len(common_buckets),
                "n_control_in_common_buckets": len(matched_control_vals),
                "n_treat_in_common_buckets": len(matched_treat_vals),
                "control_ratio_mean_matched": (round(statistics.mean(matched_control_vals), 4)
                                                if matched_control_vals else None),
                "treat_ratio_mean_matched": (round(statistics.mean(matched_treat_vals), 4)
                                              if matched_treat_vals else None),
                "matched_diff": (round(statistics.mean(matched_treat_vals) - statistics.mean(matched_control_vals), 4)
                                  if matched_control_vals and matched_treat_vals else None),
            }

    return {
        "n_point_observations": n,
        "point_word_count_range": [min(word_counts), max(word_counts)] if word_counts else None,
        "overlap_ratio_range": [min(ratios), max(ratios)] if ratios else None,
        "pearson_correlation_wordcount_vs_ratio": round(corr, 4) if corr is not None else None,
        "overlap_ratio_by_wordcount_bucket": bucket_means,
        "baseline_vs_treatment_stratified": strat_results,
        "note": "overlap_ratio = shared_content_words / point_distinct_content_words "
                "(er008_point_overlap_qa_18.py:56, point_word_count=len(point_words) where "
                "point_words is a set() = distinct content words after stopword removal). "
                "'matched' figures restrict to word-count 5-word bins present in both conditions "
                "(confound control for Point length).",
    }


# ============================================================
# (b) Full lexical/value flag transition table (all attempts, all conditions)
# ============================================================
def analyze_b():
    attempt_rows = []
    for run in RUNS:
        for att in run["retry_log"]:
            if "lexical_flagged" not in att:
                continue
            attempt_rows.append({
                "trial": run["trial"], "theme": run["theme"], "condition": run["condition"],
                "run": run["run"], "attempt": att.get("attempt"),
                "lexical_flagged": att.get("lexical_flagged"),
                "value_qa_flagged": att.get("value_qa_flagged"),
            })

    total = len(attempt_rows)
    lexical_true = sum(1 for a in attempt_rows if a["lexical_flagged"] is True)
    value_true = sum(1 for a in attempt_rows if a["value_qa_flagged"] is True)

    # per trial/condition breakdown
    by_cond = defaultdict(lambda: {"n": 0, "lexical_true": 0, "value_true": 0})
    for a in attempt_rows:
        key = f"{a['trial']}:{a['condition']}"
        by_cond[key]["n"] += 1
        if a["lexical_flagged"] is True:
            by_cond[key]["lexical_true"] += 1
        if a["value_qa_flagged"] is True:
            by_cond[key]["value_true"] += 1

    # Opus-specific claim check: trial_06 baseline (18 attempts total: 2 themes x 3 runs x 3 attempts)
    t06_baseline_attempts = [a for a in attempt_rows if a["trial"] == "trial_06" and a["condition"] == "baseline"]
    t06_baseline_lexical_true = sum(1 for a in t06_baseline_attempts if a["lexical_flagged"] is True)

    # "True swap" transitions: (T,F)->(F,T) or (F,T)->(T,F) between consecutive attempts
    # within the same run (fixed definition per Fable delegation, distinct from Haiku L0's
    # "any change" definition)
    swap_transitions = []
    any_change_transitions = []
    for run in RUNS:
        atts = sorted([a for a in run["retry_log"] if "lexical_flagged" in a],
                       key=lambda x: x.get("attempt", -1))
        for i in range(len(atts) - 1):
            curr = (atts[i]["lexical_flagged"], atts[i]["value_qa_flagged"])
            nxt = (atts[i + 1]["lexical_flagged"], atts[i + 1]["value_qa_flagged"])
            if curr != nxt:
                any_change_transitions.append({
                    "trial": run["trial"], "theme": run["theme"], "condition": run["condition"],
                    "run": run["run"], "from_attempt": atts[i].get("attempt"),
                    "to_attempt": atts[i + 1].get("attempt"), "from": curr, "to": nxt,
                })
            is_swap = (curr == (True, False) and nxt == (False, True)) or \
                      (curr == (False, True) and nxt == (True, False))
            if is_swap:
                swap_transitions.append({
                    "trial": run["trial"], "theme": run["theme"], "condition": run["condition"],
                    "run": run["run"], "from_attempt": atts[i].get("attempt"),
                    "to_attempt": atts[i + 1].get("attempt"), "from": curr, "to": nxt,
                })

    return {
        "total_attempts_all_trials_all_conditions": total,
        "lexical_flagged_true_count": lexical_true,
        "lexical_flagged_true_rate": round(lexical_true / total, 4) if total else None,
        "value_qa_flagged_true_count": value_true,
        "value_qa_flagged_true_rate": round(value_true / total, 4) if total else None,
        "by_trial_condition": dict(by_cond),
        "trial06_baseline_attempt_count": len(t06_baseline_attempts),
        "trial06_baseline_lexical_true_count": t06_baseline_lexical_true,
        "trial06_baseline_lexical_true_rate": (round(t06_baseline_lexical_true / len(t06_baseline_attempts), 4)
                                                 if t06_baseline_attempts else None),
        "opus_claim_17_of_18_check": {
            "opus_claimed": "17/18",
            "recomputed_n": len(t06_baseline_attempts),
            "recomputed_lexical_true": t06_baseline_lexical_true,
        },
        "any_change_transition_count_all_runs": len(any_change_transitions),
        "true_swap_transition_count_all_runs (fixed def: (T,F)<->(F,T) only)": len(swap_transitions),
        "swap_transitions_detail": swap_transitions,
        "haiku_l0_definition_note": "Haiku L0 aggregation (er011_point_quality_retry_log_aggregation_l0_01.py) "
                                     "counts ANY change between consecutive attempts (curr != next_att) as a "
                                     "'transition', including e.g. (True,True)->(True,False) which is not a "
                                     "swap. This recomputation uses the Fable-fixed narrower definition: only "
                                     "(T,F)<->(F,T) exact swaps count. any_change_transition_count is reported "
                                     "for direct comparison to Haiku L0's transitions field.",
    }


# ============================================================
# (c) Value-only NG -> next attempt outcome (all trials)
# ============================================================
def analyze_c():
    cases = []
    for run in RUNS:
        atts = sorted([a for a in run["retry_log"] if "lexical_flagged" in a],
                       key=lambda x: x.get("attempt", -1))
        for i in range(len(atts) - 1):
            lex = atts[i]["lexical_flagged"]
            val = atts[i]["value_qa_flagged"]
            if lex is False and val is True:
                nxt = atts[i + 1]
                cases.append({
                    "trial": run["trial"], "theme": run["theme"], "condition": run["condition"],
                    "run": run["run"], "value_only_ng_attempt": atts[i].get("attempt"),
                    "next_attempt": nxt.get("attempt"),
                    "next_lexical_flagged": nxt.get("lexical_flagged"),
                    "next_value_qa_flagged": nxt.get("value_qa_flagged"),
                    "next_attempt_new_lexical_flag": nxt.get("lexical_flagged") is True,
                })
    n = len(cases)
    new_lexical = sum(1 for c in cases if c["next_attempt_new_lexical_flag"])
    return {
        "n_value_only_ng_cases_all_trials": n,
        "n_next_attempt_shows_new_lexical_flag": new_lexical,
        "rate": round(new_lexical / n, 4) if n else None,
        "cases": cases,
        "opus_claim": "2/2 (Trial-06 only) showed next attempt with new lexical flag",
    }


# ============================================================
# (d) cross_point_overlap distribution
# ============================================================
def analyze_d():
    rows = []
    for run in RUNS:
        for att in run["retry_log"]:
            report = att.get("report") or {}
            for key, label in (("point_one_vs_point_two", "p1_vs_p2"), ("point_two_vs_point_one", "p2_vs_p1")):
                d = report.get(key)
                if not d or d.get("overlap_ratio") is None:
                    continue
                rows.append({
                    "trial": run["trial"], "condition": run["condition"], "direction": label,
                    "overlap_ratio": d["overlap_ratio"], "flagged": d.get("flagged"),
                })
    ratios = [r["overlap_ratio"] for r in rows]
    by_cond = defaultdict(list)
    for r in rows:
        by_cond[f"{r['trial']}:{r['condition']}"].append(r["overlap_ratio"])
    cond_stats = {k: {"n": len(v), "mean": round(statistics.mean(v), 4),
                       "median": round(statistics.median(v), 4), "max": round(max(v), 4)}
                  for k, v in sorted(by_cond.items())}
    flagged_count = sum(1 for r in rows if r["flagged"])
    return {
        "n_observations": len(rows),
        "overall_mean": round(statistics.mean(ratios), 4) if ratios else None,
        "overall_median": round(statistics.median(ratios), 4) if ratios else None,
        "overall_stdev": round(statistics.stdev(ratios), 4) if len(ratios) > 1 else None,
        "min_max": [min(ratios), max(ratios)] if ratios else None,
        "flagged_at_existing_threshold_0.40_count": flagged_count,
        "flagged_rate_at_0.40": round(flagged_count / len(rows), 4) if rows else None,
        "by_trial_condition": cond_stats,
    }


# ============================================================
# (f) G1 vocabulary priming: Trial-04 (pre-G1) vs Trial-06 (post-G1) baseline
# ============================================================
def analyze_f():
    def collect(trial_name):
        p1_ratios, p2_ratios, p1_wc, p2_wc = [], [], [], []
        for run in RUNS:
            if run["trial"] != trial_name or run["condition"] != "baseline":
                continue
            for att in run["retry_log"]:
                report = att.get("report") or {}
                p1 = report.get("point_one", {}).get("before_overlap")
                p2 = report.get("point_two", {}).get("before_overlap")
                if p1:
                    p1_ratios.append(p1["overlap_ratio"])
                    p1_wc.append(p1["point_word_count"])
                if p2:
                    p2_ratios.append(p2["overlap_ratio"])
                    p2_wc.append(p2["point_word_count"])
        return p1_ratios, p2_ratios, p1_wc, p2_wc

    t04_p1, t04_p2, t04_p1wc, t04_p2wc = collect("trial_04")
    t06_p1, t06_p2, t06_p1wc, t06_p2wc = collect("trial_06")

    def mean_or_none(lst):
        return round(statistics.mean(lst), 4) if lst else None

    return {
        "trial_04_baseline_pre_G1": {
            "n_p1": len(t04_p1), "p1_mean_ratio": mean_or_none(t04_p1), "p1_mean_wc": mean_or_none(t04_p1wc),
            "n_p2": len(t04_p2), "p2_mean_ratio": mean_or_none(t04_p2), "p2_mean_wc": mean_or_none(t04_p2wc),
        },
        "trial_06_baseline_post_G1": {
            "n_p1": len(t06_p1), "p1_mean_ratio": mean_or_none(t06_p1), "p1_mean_wc": mean_or_none(t06_p1wc),
            "n_p2": len(t06_p2), "p2_mean_ratio": mean_or_none(t06_p2), "p2_mean_wc": mean_or_none(t06_p2wc),
        },
        "opus_claim": "P2 ratio 0.339 -> 0.458 (baseline, pre-G1 to post-G1)",
        "note": "G1 = OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01 (2026-09-09, commit "
                "8596f34), which fixed build_diagnostic_section() to pass real previous Point One/Two "
                "body text instead of hardcoded placeholder strings, during Diagnostic Full Retry "
                "(i.e. attempt>=1 prompts only). Trial dates must be checked separately to confirm "
                "pre/post-G1 status; this function only recomputes the ratio distributions themselves.",
    }


# ============================================================
# Run all and save
# ============================================================
if __name__ == "__main__":
    results = {
        "a_point_wordcount_vs_overlap_ratio": analyze_a(),
        "b_flag_transition_table": analyze_b(),
        "c_value_only_ng_next_attempt": analyze_c(),
        "d_cross_point_overlap": analyze_d(),
        "f_g1_vocabulary_priming": analyze_f(),
        "meta": {"total_runs": len(RUNS), "runs_by_trial": dict(by_trial)},
    }
    with open(OUT_DIR / "stage1_recomputation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("Saved to", OUT_DIR / "stage1_recomputation_results.json")
