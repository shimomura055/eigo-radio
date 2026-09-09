"""
er011_news_stage4_redesign_inventory_01.py

FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01 (Sonnet, PM-delegated, offline/Y0 only)

Read-only offline recompute over EXISTING Trial outputs (Hanshin Trial-04/06,
Theme2 gap-fix Trial-05, CAR-T Trial-09, Stage2 diagnostic-branch Trial-08).
No API calls. No Production/Prompt/QA/Validator/retry code is imported for
execution side-effects; only pure read + a local re-implementation of the
existing tokenizer logic (mirrors er008_point_overlap_qa_18.py's
`_content_words`/`lexical_overlap_ratio`, NOT an import of a mutable
Production object, so this script cannot accidentally trigger any
Production call). Output: JSON/CSV under
er011_output/news_stage4_redesign_inventory_01/.
"""
from __future__ import annotations

import csv
import glob
import io
import json
import os
import re
import statistics
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "er011_output", "news_stage4_redesign_inventory_01")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Tokenizer mirror (READ-ONLY reimplementation, values identical to
# er008_point_overlap_qa_18.py at the time of this task; not imported as a
# live Production object, no monkeypatch, no Production call).
# ---------------------------------------------------------------------------
_STOPWORDS = frozenset("""
a an the this that these those it its they them their there here
is are was were be been being do does did have has had will would
can could may might must shall should
to of in on at for with without by from as into onto over under
and or but so if then than because when while though although
he she his her him we us our you your i my me
not no nor
one two three
""".split())


def _content_words(text: str) -> set:
    words = re.findall(r"[A-Za-z']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


NUMBER_WORDS = set(
    """zero one two three four five six seven eight nine ten
    eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty
    thirty forty fifty sixty seventy eighty ninety hundred thousand million billion
    first second third fourth fifth sixth seventh eighth ninth tenth
    eleventh twelfth""".split()
)

# ---------------------------------------------------------------------------
# Source Trial inventory (existing outputs only, no new generation)
# ---------------------------------------------------------------------------
SOURCES = [
    dict(trial="trial04", root="er011_output/daily_news_focus_layer_comparison_trial_04",
         theme="hanshin", topic_structure="single_event_boxscore", g1_stage="pre_g1",
         conditions=["baseline", "focus"]),
    dict(trial="trial06", root="er011_output/news_focus_hint_comparison_trial_06",
         theme="hanshin", topic_structure="single_event_boxscore", g1_stage="post_g1",
         conditions=["baseline", "focus_hint", "hint_only"]),
    dict(trial="trial05_hanshin", root="er011_output/point_overlap_gap_fix_trial_05/hanshin",
         theme="hanshin", topic_structure="single_event_boxscore", g1_stage="post_g1",
         conditions=["gapfix"]),  # baseline subdir here is a reused pointer to trial04, skip (avoid dup)
    dict(trial="trial05_theme2", root="er011_output/point_overlap_gap_fix_trial_05/theme2",
         theme="theme2", topic_structure="survey_trend", g1_stage="post_g1",
         conditions=["baseline", "gapfix"]),
    dict(trial="trial08_branch", root="er011_output/news_stage2_diagnostic_branch_trial_08/parta",
         theme="hanshin", topic_structure="single_event_boxscore", g1_stage="post_g1",
         conditions=["branch_diagnostic"]),
    dict(trial="trial09_cart", root="er011_output/news_stage3_new_theme_ledger_trial_09",
         theme="car_t", topic_structure="mechanism_limitation", g1_stage="post_g1",
         conditions=["focus_hint"]),
]

BASELINE_CONDITIONS = {"baseline"}
TREATMENT_CONDITIONS = {"focus", "focus_hint", "hint_only", "gapfix", "branch_diagnostic"}

LEVELS = ["a2", "b1b"]


def load_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Step A: entity/number token dictionary per theme, built by scanning
# existing article.md text for words that are capitalized when NOT the
# first word of a sentence (proper-noun heuristic). Numbers are excluded by
# the tokenizer itself (`[A-Za-z']+`) EXCEPT spelled-out number words
# (five, seventh, etc.), which we add via NUMBER_WORDS.
# This is a Trial-only proxy metric; it does not modify or replace the
# Production Overlap Checker (er008_point_overlap_qa_18.py, threshold 0.40
# unchanged).
# ---------------------------------------------------------------------------

def build_entity_dict():
    cap_counts = defaultdict(lambda: defaultdict(int))
    total_counts = defaultdict(lambda: defaultdict(int))
    for src in SOURCES:
        root = os.path.join(BASE, src["root"])
        theme = src["theme"]
        for path in glob.glob(os.path.join(root, "**", "article.md"), recursive=True):
            with io.open(path, encoding="utf-8") as f:
                text = f.read()
            sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
            for sent in sentences:
                words = re.findall(r"[A-Za-z']+", sent)
                for i, w in enumerate(words):
                    lw = w.lower()
                    if lw in _STOPWORDS or len(lw) <= 2:
                        continue
                    total_counts[theme][lw] += 1
                    if i > 0 and w[0].isupper():
                        cap_counts[theme][lw] += 1
    entity_dict = defaultdict(set)
    for theme, counter in cap_counts.items():
        for w, c in counter.items():
            if total_counts[theme][w] > 0 and (c / total_counts[theme][w]) >= 0.5:
                entity_dict[theme].add(w)
    return entity_dict


def is_entity_or_number(word: str, theme: str, entity_dict) -> bool:
    if word in NUMBER_WORDS:
        return True
    if word in entity_dict.get(theme, set()):
        return True
    return False


# ---------------------------------------------------------------------------
# Step B: load all attempt-level Point-vs-FullStory overlap observations
# ---------------------------------------------------------------------------

def load_records():
    records = []
    run_records = []
    for src in SOURCES:
        root = os.path.join(BASE, src["root"])
        for level in LEVELS:
            for cond in src["conditions"]:
                cond_dir = os.path.join(root, level, cond)
                if not os.path.isdir(cond_dir):
                    continue
                for run_name in sorted(os.listdir(cond_dir)):
                    run_dir = os.path.join(cond_dir, run_name)
                    analysis_path = os.path.join(run_dir, "analysis.json")
                    retry_path = os.path.join(run_dir, "point_overlap_article_retry_log.json")
                    if not os.path.isfile(analysis_path):
                        continue
                    analysis = load_json(analysis_path)
                    final_status = analysis.get("status")
                    run_role = "baseline" if cond in BASELINE_CONDITIONS else (
                        "treatment" if cond in TREATMENT_CONDITIONS else "other")
                    run_meta = dict(
                        trial=src["trial"], theme=src["theme"],
                        topic_structure=src["topic_structure"], g1_stage=src["g1_stage"],
                        level=level, condition=cond, run_role=run_role, run=run_name,
                        final_status=final_status,
                        retry_attempts=analysis.get("retry_attempts"),
                        word_count=analysis.get("word_count"),
                        fact_verdict=analysis.get("fact_verdict"),
                    )
                    run_records.append(run_meta)
                    if not os.path.isfile(retry_path):
                        continue
                    retry_log = load_json(retry_path)
                    n_attempts = len(retry_log)
                    for entry in retry_log:
                        attempt = entry.get("attempt")
                        is_initial = (attempt == 0)
                        lexical_flagged_attempt = entry.get("lexical_flagged")
                        value_qa_flagged_attempt = entry.get("value_qa_flagged")
                        report = entry.get("report", {})
                        for label in ["point_one", "point_two"]:
                            pdata = report.get(label, {})
                            before = pdata.get("before_overlap", {})
                            cross = pdata.get("cross_point_overlap", {})
                            if not before:
                                continue
                            records.append(dict(
                                trial=src["trial"], theme=src["theme"],
                                topic_structure=src["topic_structure"], g1_stage=src["g1_stage"],
                                level=level, condition=cond, run_role=run_role, run=run_name,
                                attempt=attempt, is_initial=is_initial,
                                is_last_attempt=(attempt == n_attempts - 1),
                                point_label=label,
                                overlap_ratio=before.get("overlap_ratio"),
                                flagged=bool(before.get("flagged")),
                                shared_words=before.get("shared_words", []) or [],
                                point_word_count=before.get("point_word_count"),
                                story_word_count=before.get("story_word_count"),
                                cross_overlap_ratio=cross.get("overlap_ratio"),
                                cross_flagged=bool(cross.get("flagged")) if cross else None,
                                lexical_flagged_attempt=lexical_flagged_attempt,
                                value_qa_flagged_attempt=value_qa_flagged_attempt,
                                final_status=final_status,
                            ))
    return records, run_records


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    xs2, ys2 = zip(*pairs)
    try:
        return round(statistics.correlation(xs2, ys2), 4)
    except Exception:
        n = len(xs2)
        mx, my = sum(xs2) / n, sum(ys2) / n
        cov = sum((x - mx) * (y - my) for x, y in pairs)
        varx = sum((x - mx) ** 2 for x in xs2)
        vary = sum((y - my) ** 2 for y in ys2)
        if varx == 0 or vary == 0:
            return None
        return round(cov / ((varx ** 0.5) * (vary ** 0.5)), 4)


def rate(flags):
    flags = [f for f in flags if f is not None]
    if not flags:
        return None
    return round(sum(1 for f in flags if f) / len(flags), 4)


def mean(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return round(statistics.mean(vals), 4)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    entity_dict = build_entity_dict()
    records, run_records = load_records()

    result = {}
    result["meta"] = dict(
        n_point_attempt_observations=len(records),
        n_runs=len(run_records),
        entity_dict_sizes={k: len(v) for k, v in entity_dict.items()},
        note="Y0 offline recompute. Threshold 0.40 unchanged (Production checker not modified). "
             "entity_dict built via mid-sentence-capitalization heuristic over existing article.md "
             "text (Trial-only proxy, not a Production change).",
    )

    # ---- (C) threshold 0.40 evaluation by topic_structure / level / initial-vs-retry ----
    strat = defaultdict(list)
    for r in records:
        strat[(r["topic_structure"], r["level"], "initial" if r["is_initial"] else "retry")].append(r)
    c_table = []
    for (ts, level, phase), rows in sorted(strat.items()):
        c_table.append(dict(
            topic_structure=ts, level=level, phase=phase, n=len(rows),
            flag_rate=rate([r["flagged"] for r in rows]),
            mean_overlap=mean([r["overlap_ratio"] for r in rows]),
            mean_point_word_count=mean([r["point_word_count"] for r in rows]),
        ))
    result["c_threshold_by_topic_level_phase"] = c_table

    ts_table = []
    for ts in sorted({r["topic_structure"] for r in records}):
        rows = [r for r in records if r["topic_structure"] == ts]
        ts_table.append(dict(
            topic_structure=ts, n=len(rows),
            flag_rate=rate([r["flagged"] for r in rows]),
            mean_overlap=mean([r["overlap_ratio"] for r in rows]),
        ))
    result["c_threshold_by_topic_structure_overall"] = ts_table

    # ---- (C) FP-candidate classification over ALL flagged observations (rule-based) ----
    flagged_rows = [r for r in records if r["flagged"]]
    fp_rows = []
    for r in flagged_rows:
        shared = r["shared_words"]
        if not shared:
            entity_ratio = 0.0
        else:
            n_entity = sum(1 for w in shared if is_entity_or_number(w, r["theme"], entity_dict))
            entity_ratio = n_entity / len(shared)
        classification = "necessary_factual_reuse_candidate" if entity_ratio >= 0.5 else "true_duplication_candidate"
        fp_rows.append(dict(
            trial=r["trial"], theme=r["theme"], topic_structure=r["topic_structure"],
            level=r["level"], condition=r["condition"], run=r["run"], attempt=r["attempt"],
            point_label=r["point_label"], overlap_ratio=r["overlap_ratio"],
            shared_words=r["shared_words"], entity_ratio=round(entity_ratio, 3),
            classification=classification,
        ))
    n_fp_candidates = sum(1 for x in fp_rows if x["classification"] == "necessary_factual_reuse_candidate")
    result["c_fp_candidate_summary"] = dict(
        n_flagged_total=len(flagged_rows),
        n_necessary_factual_reuse_candidate=n_fp_candidates,
        fp_candidate_rate_tentative=round(n_fp_candidates / len(flagged_rows), 4) if flagged_rows else None,
        by_topic_structure={
            ts: dict(
                n_flagged=len([x for x in fp_rows if x["topic_structure"] == ts]),
                n_fp_candidate=len([x for x in fp_rows if x["topic_structure"] == ts
                                     and x["classification"] == "necessary_factual_reuse_candidate"]),
            )
            for ts in sorted({x["topic_structure"] for x in fp_rows})
        },
        note="LABEL IS A RULE-BASED (entity/number-token-share >= 0.5) TENTATIVE CLASSIFICATION, "
             "NOT human ground truth. A representative subset is eyeballed separately "
             "(see fp_classification_sample.md) and may disagree with the rule.",
    )
    with io.open(os.path.join(OUT_DIR, "fp_classification_all_flagged.json"), "w", encoding="utf-8") as f:
        json.dump(fp_rows, f, ensure_ascii=False, indent=2)

    # representative sample (10-20) spread across topic_structure x classification
    sample = []
    by_bucket = defaultdict(list)
    for x in fp_rows:
        by_bucket[(x["topic_structure"], x["classification"])].append(x)
    for bucket, items in sorted(by_bucket.items()):
        sample.extend(items[:3])
    sample = sample[:20]
    result["c_fp_sample_for_eyeball"] = sample

    # ---- (B) entity/number-token-excluded overlap recompute ----
    b_rows = []
    for r in records:
        shared = r["shared_words"]
        pwc = r["point_word_count"] or 0
        n_entity_shared = sum(1 for w in shared if is_entity_or_number(w, r["theme"], entity_dict))
        adjusted_shared_n = len(shared) - n_entity_shared
        adjusted_ratio = round(adjusted_shared_n / pwc, 4) if pwc else None
        adjusted_flagged = (adjusted_ratio is not None and adjusted_ratio >= 0.40)
        evidence_density = round(n_entity_shared / pwc, 4) if pwc else None
        b_rows.append(dict(
            r, n_entity_shared=n_entity_shared, adjusted_overlap_ratio=adjusted_ratio,
            adjusted_flagged=adjusted_flagged, evidence_density=evidence_density,
        ))
    orig_flag_rate = rate([r["flagged"] for r in b_rows])
    adj_flag_rate = rate([r["adjusted_flagged"] for r in b_rows])
    result["b_entity_excluded_recompute"] = dict(
        n=len(b_rows),
        original_flag_rate_at_0_40=orig_flag_rate,
        entity_excluded_flag_rate_at_0_40=adj_flag_rate,
        delta_pt=round((adj_flag_rate - orig_flag_rate) * 100, 2) if (orig_flag_rate is not None and adj_flag_rate is not None) else None,
        n_flag_flip_true_to_false=sum(1 for r in b_rows if r["flagged"] and not r["adjusted_flagged"]),
        n_flag_flip_false_to_true=sum(1 for r in b_rows if not r["flagged"] and r["adjusted_flagged"]),
        by_topic_structure={
            ts: dict(
                n=len([r for r in b_rows if r["topic_structure"] == ts]),
                original_flag_rate=rate([r["flagged"] for r in b_rows if r["topic_structure"] == ts]),
                adjusted_flag_rate=rate([r["adjusted_flagged"] for r in b_rows if r["topic_structure"] == ts]),
            )
            for ts in sorted({r["topic_structure"] for r in b_rows})
        },
        correlations=dict(
            point_word_count_vs_overlap_ratio=pearson(
                [r["point_word_count"] for r in b_rows], [r["overlap_ratio"] for r in b_rows]),
            n_entity_shared_vs_overlap_ratio=pearson(
                [r["n_entity_shared"] for r in b_rows], [r["overlap_ratio"] for r in b_rows]),
            evidence_density_vs_overlap_ratio=pearson(
                [r["evidence_density"] for r in b_rows], [r["overlap_ratio"] for r in b_rows]),
            point_word_count_vs_adjusted_overlap_ratio=pearson(
                [r["point_word_count"] for r in b_rows], [r["adjusted_overlap_ratio"] for r in b_rows]),
        ),
        note="Numerator-only adjustment (denominator = original point_word_count, unchanged) because "
             "shared_words/point_word_count are the only per-attempt fields persisted in the existing "
             "retry logs; full per-attempt Point/Story text is not stored for attempts other than the "
             "final one, so a full (numerator+denominator) entity-excluded retokenization is not "
             "possible for all attempts from existing artifacts alone.",
    )

    # ---- (G) topic-structure quantification (NG rate, retry avg, initial-flag rate) ----
    g_table = []
    for ts in sorted({rr["topic_structure"] for rr in run_records}):
        rows = [rr for rr in run_records if rr["topic_structure"] == ts]
        base_rows = [rr for rr in rows if rr["run_role"] == "baseline"]
        treat_rows = [rr for rr in rows if rr["run_role"] == "treatment"]
        g_table.append(dict(
            topic_structure=ts, n_runs=len(rows),
            ng_rate_overall=rate([rr["final_status"] != "OK" for rr in rows]),
            ng_rate_baseline=rate([rr["final_status"] != "OK" for rr in base_rows]) if base_rows else None,
            n_baseline=len(base_rows),
            ng_rate_treatment=rate([rr["final_status"] != "OK" for rr in treat_rows]) if treat_rows else None,
            n_treatment=len(treat_rows),
            mean_retry_attempts=mean([rr["retry_attempts"] for rr in rows]),
        ))
    result["g_topic_structure_ng_rates"] = g_table

    # initial-attempt "any flag" rate (lexical or value) per run, by topic structure
    run_initial_flag = {}
    for r in records:
        if r["is_initial"]:
            key = (r["trial"], r["theme"], r["topic_structure"], r["level"], r["condition"], r["run"])
            flag = bool(r.get("lexical_flagged_attempt")) or bool(r.get("value_qa_flagged_attempt"))
            run_initial_flag[key] = run_initial_flag.get(key, False) or flag
    g_initial = defaultdict(list)
    for key, flag in run_initial_flag.items():
        g_initial[key[2]].append(flag)
    result["g_initial_attempt_flag_rate_by_topic_structure"] = {
        ts: rate(flags) for ts, flags in sorted(g_initial.items())
    }

    # "true swap" (mogura-tataki narrow definition) rate per topic structure, run-level
    run_attempts = defaultdict(dict)
    for r in records:
        key = (r["trial"], r["theme"], r["topic_structure"], r["level"], r["condition"], r["run"])
        run_attempts[key][r["attempt"]] = (bool(r.get("lexical_flagged_attempt")), bool(r.get("value_qa_flagged_attempt")))
    swap_by_ts = defaultdict(lambda: [0, 0])  # [n_swaps, n_transitions]
    for key, attempts in run_attempts.items():
        ts = key[2]
        ordered = [attempts[a] for a in sorted(attempts.keys())]
        for i in range(len(ordered) - 1):
            cur, nxt = ordered[i], ordered[i + 1]
            swap_by_ts[ts][1] += 1
            if cur in [(True, False), (False, True)] and nxt in [(True, False), (False, True)] and cur != nxt:
                swap_by_ts[ts][0] += 1
    result["g_true_swap_rate_by_topic_structure"] = {
        ts: dict(true_swaps=v[0], transitions=v[1], rate=round(v[0] / v[1], 4) if v[1] else None)
        for ts, v in sorted(swap_by_ts.items())
    }

    # ---- write outputs ----
    with io.open(os.path.join(OUT_DIR, "stage4_recomputation_results.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # CSV of point-attempt records for external inspection
    csv_path = os.path.join(OUT_DIR, "point_attempt_observations.csv")
    fieldnames = ["trial", "theme", "topic_structure", "g1_stage", "level", "condition", "run_role",
                  "run", "attempt", "is_initial", "point_label", "overlap_ratio", "flagged",
                  "point_word_count", "story_word_count", "cross_overlap_ratio", "cross_flagged",
                  "n_shared_words"]
    with io.open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in records:
            row = {k: r.get(k) for k in fieldnames if k != "n_shared_words"}
            row["n_shared_words"] = len(r["shared_words"])
            w.writerow(row)

    # markdown sample table for human eyeball
    md_lines = ["# FP classification sample (10-20, rule-based tentative label + shared words for eyeball)", ""]
    md_lines.append("| topic_structure | trial | run | point | overlap | entity_ratio | classification(rule) | shared_words |")
    md_lines.append("|---|---|---|---|---|---|---|---|")
    for x in sample:
        md_lines.append(
            f"| {x['topic_structure']} | {x['trial']} | {x['run']} | {x['point_label']} | "
            f"{x['overlap_ratio']} | {x['entity_ratio']} | {x['classification']} | "
            f"{', '.join(x['shared_words'])} |"
        )
    with io.open(os.path.join(OUT_DIR, "fp_classification_sample.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print("n_point_attempt_observations:", len(records))
    print("n_runs:", len(run_records))
    print("entity_dict sizes:", {k: len(v) for k, v in entity_dict.items()})
    print("fp_candidate_rate_tentative:", result["c_fp_candidate_summary"]["fp_candidate_rate_tentative"])
    print("b: orig_flag_rate", orig_flag_rate, "adj_flag_rate", adj_flag_rate)
    print("g_topic_structure_ng_rates:", json.dumps(g_table, ensure_ascii=False))
    print("Wrote outputs to", OUT_DIR)


if __name__ == "__main__":
    main()
