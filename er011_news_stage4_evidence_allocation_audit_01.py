"""
er011_news_stage4_evidence_allocation_audit_01.py

FAMILY-A-NEWS-STAGE4-EVIDENCE-ALLOCATION-AUDIT-01 (Sonnet, PM-delegated,
offline/Y0 only, read-only aggregation over EXISTING outputs).

Part 1: Evidence-allocation conflict audit over existing 48 runs (Hanshin
Trial-04/06, Theme2 Trial-05 gapfix, CAR-T Trial-09, Stage2 diagnostic-branch
Trial-08). Extracts Fact-ID anchors referenced in each attempt's
`point_role_planning_{initial,retry*}.json` (`evidence_anchor` free-text
field) via a read-only regex scan (no Production code executed, no API
calls), and cross-references with existing `point_overlap_article_retry_log
.json` overlap_ratio / flagged data and `analysis.json` final status.

Part 2: Recalibration of the "entity/number-excluded overlap" candidate
metric from FAMILY-A-NEWS-STAGE4-REDESIGN-INVENTORY-01 (denominator also
entity-excluded on last-attempt full text; ordinal words removed from
NUMBER_WORDS; percentile-matched threshold rank-correlation check).

Part 3: Attempt-level overlap_ratio (continuous) distribution vs binary NG
rate, statistical power illustration using Trial-08 data.

No Production/Prompt/QA/Validator/retry code is imported for execution;
only a read-only local re-implementation of the existing tokenizer logic
(mirrors er008_point_overlap_qa_18.py `_content_words`/
`lexical_overlap_ratio`, values unchanged, threshold 0.40 unchanged).
Output: er011_output/news_stage4_evidence_allocation_audit_01/.
"""
from __future__ import annotations

import csv
import glob
import io
import json
import os
import re
import statistics
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "er011_output", "news_stage4_evidence_allocation_audit_01")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Tokenizer mirror (read-only re-implementation, identical logic/values to
# er008_point_overlap_qa_18.py at the time of this task; not imported as a
# live Production object).
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

# Candidate (ii): ordinal words removed from NUMBER_WORDS (Opus point (i)).
ORDINALS = set(
    "first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth".split()
)
NUMBER_WORDS_NO_ORDINALS = NUMBER_WORDS - ORDINALS


def lexical_overlap_ratio(point_words: set, story_words: set):
    if not point_words:
        return 0.0, set()
    shared = point_words & story_words
    return len(shared) / len(point_words), shared


# ---------------------------------------------------------------------------
# Source Trial inventory (existing outputs only, no new generation). Mirrors
# er011_news_stage4_redesign_inventory_01.py SOURCES (read-only reuse of the
# same inventory list, not an import).
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
         conditions=["gapfix"]),
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

# Ledger usable-fact registries per theme (read from Ledger source text /
# prompt.txt during this task's investigation; hard-coded here as a
# read-only summary, NOT re-derived from a live Production call).
#   hanshin: FACT-01..07, number_classification tags: FACT-06/07 = DISPENSABLE
#            (scope-excluded per Ledger's own "この記事で扱わない情報"), so
#            usable-for-writing = FACT-01..05 (5 facts).
#   theme2:  F-201..F-209 (9 facts). verification: CONFIRMED for all except
#            F-207 (COULD_NOT_CONFIRM). The Ledger text ALSO contains a
#            citation of "F-211" in the central_claim narrative pointing at
#            content that matches F-206, and an explicit correction note
#            mentioning "F-210" as a "number that does not exist in the Fact
#            list" (Trial-12 self-correction) -- flagged here as a Ledger
#            ID-consistency data-quality note, not corrected by this script.
#   car_t:   FACT-001..015, FACT-005 is absent from the source Ledger (no
#            such ID appears in the text), so 14 IDs exist (FACT-001..004,
#            006..015). No DISPENSABLE/COULD_NOT_CONFIRM tag present; all 14
#            are VERIFIED.
LEDGER_REGISTRY = {
    "hanshin": dict(
        all_ids=[f"FACT-{i:02d}" for i in range(1, 8)],
        usable_ids=[f"FACT-{i:02d}" for i in range(1, 6)],
        dispensable_ids=["FACT-06", "FACT-07"],
        total_facts=7, usable_facts=5,
        id_pattern=re.compile(r"FACT-(\d{2})"),
        id_fmt=lambda n: f"FACT-{int(n):02d}",
    ),
    "theme2": dict(
        all_ids=[f"F-{i}" for i in range(201, 210)],
        usable_ids=[f"F-{i}" for i in range(201, 210) if i != 207],
        dispensable_ids=[],
        could_not_confirm_ids=["F-207"],
        total_facts=9, usable_facts=8,  # CONFIRMED-only; F-207 also usable-with-caveat per Ledger note
        id_pattern=re.compile(r"\bF-(\d{3})\b"),
        id_fmt=lambda n: f"F-{int(n)}",
        id_quality_note=(
            "Ledger text also cites 'F-211' in the central_claim narrative "
            "(content matches F-206) and an explicit self-correction note "
            "mentions 'F-210' as a number absent from the Fact list "
            "(Trial-12 correction of a prior Trial-11 mis-citation). "
            "These are Ledger-internal ID-consistency issues, observed as-is."
        ),
    ),
    "car_t": dict(
        all_ids=[f"FACT-{i:03d}" for i in list(range(1, 5)) + list(range(6, 16))],
        usable_ids=[f"FACT-{i:03d}" for i in list(range(1, 5)) + list(range(6, 16))],
        dispensable_ids=[],
        total_facts=14, usable_facts=14,
        id_pattern=re.compile(r"FACT-(\d{3})"),
        id_fmt=lambda n: f"FACT-{int(n):03d}",
    ),
}


def normalize_ids(text: str, theme: str) -> set:
    """Extract Fact-ID references from free text, theme-specific pattern."""
    reg = LEDGER_REGISTRY[theme]
    pat = reg["id_pattern"]
    fmt = reg["id_fmt"]
    return {fmt(m.group(1)) for m in pat.finditer(text or "")}


def load_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Entity dictionary (mirrors news_stage4_redesign_inventory_01 Step A, for
# Part 2 recalibration; read-only, Trial-scope proxy metric only).
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


def is_num(word, number_words):
    return word in number_words


# ---------------------------------------------------------------------------
# PART 1: Evidence allocation / anchor extraction
# ---------------------------------------------------------------------------

ATTEMPT_FILE_ORDER = ["initial", "retry1", "retry2", "retry3"]


def load_run_role_planning(run_dir, theme):
    """Return list of dicts: attempt, p1_anchor_ids(set), p2_anchor_ids(set),
    p1_anchor_text, p2_anchor_text -- one per attempt file found, in order."""
    audit_dir = os.path.join(run_dir, "audit")
    out = []
    for i, tag in enumerate(ATTEMPT_FILE_ORDER):
        fname = f"point_role_planning_{tag}.json"
        fpath = os.path.join(audit_dir, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            d = load_json(fpath)
        except Exception:
            continue
        parsed = d.get("parsed", {})
        p1 = parsed.get("point_one", {}) or {}
        p2 = parsed.get("point_two", {}) or {}
        p1_text = p1.get("evidence_anchor", "") or ""
        p2_text = p2.get("evidence_anchor", "") or ""
        out.append(dict(
            attempt=i,
            tag=tag,
            p1_anchor_text=p1_text,
            p2_anchor_text=p2_text,
            p1_anchor_ids=normalize_ids(p1_text, theme),
            p2_anchor_ids=normalize_ids(p2_text, theme),
        ))
    return out


def load_run_overlap_log(run_dir):
    path = os.path.join(run_dir, "point_overlap_article_retry_log.json")
    if not os.path.isfile(path):
        return []
    return load_json(path)


def spearman(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None, len(pairs)
    xs2, ys2 = zip(*pairs)

    def rank(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg_rank
            i = j + 1
        return ranks

    rx = rank(xs2)
    ry = rank(ys2)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    varx = sum((a - mx) ** 2 for a in rx)
    vary = sum((b - my) ** 2 for b in ry)
    if varx == 0 or vary == 0:
        return None, n
    return round(cov / ((varx ** 0.5) * (vary ** 0.5)), 4), n


def mean(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return round(statistics.mean(vals), 4)


def rate(flags):
    flags = [f for f in flags if f is not None]
    if not flags:
        return None
    return round(sum(1 for f in flags if f) / len(flags), 4)


def part1_evidence_allocation():
    attempt_rows = []       # per attempt-per-run: conflict metrics + overlap + final status
    run_rows = []            # per-run summary: fact usage, initial->final anchor transitions
    missing_role_planning_runs = []
    missing_overlap_log_runs = []
    global_conflict_recurrence_events = 0
    global_conflict_events_total = 0

    for src in SOURCES:
        root = os.path.join(BASE, src["root"])
        theme = src["theme"]
        for level in LEVELS:
            for cond in src["conditions"]:
                cond_dir = os.path.join(root, level, cond)
                if not os.path.isdir(cond_dir):
                    continue
                for run_name in sorted(os.listdir(cond_dir)):
                    run_dir = os.path.join(cond_dir, run_name)
                    analysis_path = os.path.join(run_dir, "analysis.json")
                    if not os.path.isfile(analysis_path):
                        continue
                    analysis = load_json(analysis_path)
                    final_status = analysis.get("status")
                    final_ng = (final_status == "NG_REVIEW_REQUIRED")
                    run_role = "baseline" if cond in BASELINE_CONDITIONS else (
                        "treatment" if cond in TREATMENT_CONDITIONS else "other")

                    role_plans = load_run_role_planning(run_dir, theme)
                    overlap_log = load_run_overlap_log(run_dir)
                    if not role_plans:
                        missing_role_planning_runs.append(dict(
                            trial=src["trial"], theme=theme, level=level,
                            condition=cond, run=run_name))
                    if not overlap_log:
                        missing_overlap_log_runs.append(dict(
                            trial=src["trial"], theme=theme, level=level,
                            condition=cond, run=run_name))

                    # index overlap_log by attempt number
                    overlap_by_attempt = {}
                    for entry in overlap_log:
                        overlap_by_attempt[entry.get("attempt")] = entry

                    run_p1_union = set()
                    run_p2_union = set()
                    run_all_anchor_union = set()

                    prev_p1_ids = None
                    prev_p2_ids = None
                    p1_seen_sets = []
                    p2_seen_sets = []
                    conflict_ids_ever_seen = set()
                    conflict_recurrence_events = 0
                    conflict_events_total = 0

                    for rp in role_plans:
                        attempt = rp["attempt"]
                        p1_ids = rp["p1_anchor_ids"]
                        p2_ids = rp["p2_anchor_ids"]
                        conflict_ids = p1_ids & p2_ids
                        union_ids = p1_ids | p2_ids
                        conflict_count = len(conflict_ids)
                        union_count = len(union_ids)
                        jaccard = (conflict_count / union_count) if union_count else None

                        oentry = overlap_by_attempt.get(attempt, {})
                        report = oentry.get("report", {})
                        cross_ratio = None
                        p12 = report.get("point_one_vs_point_two")
                        if p12:
                            cross_ratio = p12.get("overlap_ratio")
                        p1_story_ratio = (report.get("point_one", {}) or {}).get(
                            "before_overlap", {}).get("overlap_ratio")
                        p2_story_ratio = (report.get("point_two", {}) or {}).get(
                            "before_overlap", {}).get("overlap_ratio")
                        lexical_flagged_attempt = oentry.get("lexical_flagged")

                        # transition classification for each point vs previous attempt
                        def classify(cur, prev, seen_list):
                            if prev is None:
                                status = "n/a_first_attempt"
                            elif cur == prev:
                                status = "fixed"
                            elif any(cur == s for s in seen_list[:-1]):
                                status = "regressed_to_earlier_state"
                            else:
                                status = "changed"
                            return status

                        p1_transition = classify(p1_ids, prev_p1_ids, p1_seen_sets)
                        p2_transition = classify(p2_ids, prev_p2_ids, p2_seen_sets)

                        if conflict_count > 0:
                            conflict_events_total += 1
                            if conflict_ids & conflict_ids_ever_seen:
                                conflict_recurrence_events += 1
                            conflict_ids_ever_seen |= conflict_ids

                        attempt_rows.append(dict(
                            trial=src["trial"], theme=theme,
                            topic_structure=src["topic_structure"],
                            g1_stage=src["g1_stage"], level=level, condition=cond,
                            run_role=run_role, run=run_name, attempt=attempt,
                            p1_anchor_ids="|".join(sorted(p1_ids)),
                            p2_anchor_ids="|".join(sorted(p2_ids)),
                            conflict_ids="|".join(sorted(conflict_ids)),
                            conflict_count=conflict_count,
                            union_count=union_count,
                            jaccard_conflict_rate=jaccard,
                            cross_overlap_ratio=cross_ratio,
                            p1_story_overlap_ratio=p1_story_ratio,
                            p2_story_overlap_ratio=p2_story_ratio,
                            lexical_flagged_attempt=lexical_flagged_attempt,
                            p1_transition=p1_transition,
                            p2_transition=p2_transition,
                            final_status=final_status,
                            final_ng=final_ng,
                        ))

                        run_p1_union |= p1_ids
                        run_p2_union |= p2_ids
                        run_all_anchor_union |= union_ids
                        p1_seen_sets.append(p1_ids)
                        p2_seen_sets.append(p2_ids)
                        prev_p1_ids, prev_p2_ids = p1_ids, p2_ids

                    global_conflict_recurrence_events += conflict_recurrence_events
                    global_conflict_events_total += conflict_events_total

                    if role_plans:
                        first = role_plans[0]
                        last = role_plans[-1]
                        reg = LEDGER_REGISTRY[theme]
                        usable = set(reg["usable_ids"])
                        facts_referenced_by_points = run_all_anchor_union & usable
                        facts_never_referenced_by_points = usable - run_all_anchor_union
                        run_rows.append(dict(
                            trial=src["trial"], theme=theme,
                            topic_structure=src["topic_structure"],
                            level=level, condition=cond, run_role=run_role,
                            run=run_name, n_attempts=len(role_plans),
                            final_status=final_status, final_ng=final_ng,
                            usable_fact_count=reg["usable_facts"],
                            facts_referenced_by_any_point=len(facts_referenced_by_points),
                            facts_never_referenced_by_points=len(facts_never_referenced_by_points),
                            never_referenced_ids="|".join(sorted(facts_never_referenced_by_points)),
                            initial_p1_ids="|".join(sorted(first["p1_anchor_ids"])),
                            initial_p2_ids="|".join(sorted(first["p2_anchor_ids"])),
                            final_p1_ids="|".join(sorted(last["p1_anchor_ids"])),
                            final_p2_ids="|".join(sorted(last["p2_anchor_ids"])),
                            initial_conflict_count=len(first["p1_anchor_ids"] & first["p2_anchor_ids"]),
                            final_conflict_count=len(last["p1_anchor_ids"] & last["p2_anchor_ids"]),
                        ))

    conflict_recurrence_rate = (
        round(global_conflict_recurrence_events / global_conflict_events_total, 4)
        if global_conflict_events_total else None
    )
    return (attempt_rows, run_rows, missing_role_planning_runs, missing_overlap_log_runs,
            dict(conflict_recurrence_events=global_conflict_recurrence_events,
                 conflict_events_total=global_conflict_events_total,
                 conflict_recurrence_rate=conflict_recurrence_rate))


def part1_aggregate(attempt_rows, run_rows):
    # (a) P1/P2 anchor conflict rate by attempt-phase / theme / level
    def phase(a):
        return "initial" if a == 0 else "retry"

    groups = defaultdict(list)
    for r in attempt_rows:
        groups[(r["theme"], r["level"], phase(r["attempt"]))].append(r)

    conflict_by_group = []
    for (theme, level, ph), rows in sorted(groups.items()):
        n = len(rows)
        conflict_present_rate = rate([rw["conflict_count"] > 0 for rw in rows])
        mean_conflict_count = mean([rw["conflict_count"] for rw in rows])
        mean_jaccard = mean([rw["jaccard_conflict_rate"] for rw in rows])
        mean_cross_overlap = mean([rw["cross_overlap_ratio"] for rw in rows])
        conflict_by_group.append(dict(
            theme=theme, level=level, phase=ph, n=n,
            conflict_present_rate=conflict_present_rate,
            mean_conflict_count=mean_conflict_count,
            mean_jaccard_conflict_rate=mean_jaccard,
            mean_cross_overlap_ratio=mean_cross_overlap,
        ))

    # (b) initial -> retry anchor change rate (fixed / regressed / changed), per point
    transition_counts = Counter()
    for r in attempt_rows:
        if r["attempt"] == 0:
            continue
        transition_counts[("point_one", r["p1_transition"])] += 1
        transition_counts[("point_two", r["p2_transition"])] += 1
    transition_summary = [
        dict(point=k[0], transition=k[1], count=v) for k, v in sorted(transition_counts.items())
    ]

    # (c) correlation: conflict_count / jaccard vs cross_overlap_ratio, and vs final_ng
    conflict_counts = [r["conflict_count"] for r in attempt_rows]
    jaccards = [r["jaccard_conflict_rate"] for r in attempt_rows]
    cross_ratios = [r["cross_overlap_ratio"] for r in attempt_rows]
    final_ng_bin = [1 if r["final_ng"] else 0 for r in attempt_rows]

    spearman_conflict_vs_overlap, n1 = spearman(conflict_counts, cross_ratios)
    spearman_jaccard_vs_overlap, n2 = spearman(jaccards, cross_ratios)
    spearman_conflict_vs_ng, n3 = spearman(conflict_counts, final_ng_bin)
    spearman_jaccard_vs_ng, n4 = spearman(jaccards, final_ng_bin)

    # Supplementary: the Production retry GATE actually keys off Point-vs-
    # FullStory overlap (before_overlap, "lexical_flagged"), NOT point-to-
    # point cross_overlap (OPEN-133: cross_point_overlap computed but
    # DEFERRED/unused in retry decisions). So we also test conflict_count
    # against max(point_vs_story overlap) -- the metric that actually drives
    # lexical_flagged / NG -- as a more direct test of the "evidence supply
    # conflict -> the metric that actually gates" pathway.
    max_story_ratio = []
    for r in attempt_rows:
        vals = [v for v in (r["p1_story_overlap_ratio"], r["p2_story_overlap_ratio"]) if v is not None]
        max_story_ratio.append(max(vals) if vals else None)
    spearman_conflict_vs_story, n5 = spearman(conflict_counts, max_story_ratio)
    spearman_jaccard_vs_story, n6 = spearman(jaccards, max_story_ratio)
    lexical_flagged_bin = [1 if r.get("lexical_flagged_attempt") else 0 for r in attempt_rows]
    spearman_conflict_vs_lexflag, n7 = spearman(conflict_counts, lexical_flagged_bin)

    # (d) usable-fact-count vs run-level final NG rate, by theme
    fact_supply_rows = []
    by_theme_runs = defaultdict(list)
    for rr in run_rows:
        by_theme_runs[rr["theme"]].append(rr)
    for theme, rows in sorted(by_theme_runs.items()):
        reg = LEDGER_REGISTRY[theme]
        ng_rate = rate([rw["final_ng"] for rw in rows])
        mean_referenced = mean([rw["facts_referenced_by_any_point"] for rw in rows])
        fact_supply_rows.append(dict(
            theme=theme, usable_fact_count=reg["usable_facts"],
            n_runs=len(rows), final_ng_rate=ng_rate,
            mean_facts_referenced_by_points=mean_referenced,
        ))

    # (e) point-to-point anchor conflict rate at run level (initial vs final)
    initial_conflict_rate = rate([rr["initial_conflict_count"] > 0 for rr in run_rows])
    final_conflict_rate = rate([rr["final_conflict_count"] > 0 for rr in run_rows])

    return dict(
        conflict_by_group=conflict_by_group,
        transition_summary=transition_summary,
        correlation=dict(
            spearman_conflict_count_vs_cross_overlap=spearman_conflict_vs_overlap,
            n_conflict_vs_overlap=n1,
            spearman_jaccard_vs_cross_overlap=spearman_jaccard_vs_overlap,
            n_jaccard_vs_overlap=n2,
            spearman_conflict_count_vs_final_ng=spearman_conflict_vs_ng,
            n_conflict_vs_ng=n3,
            spearman_jaccard_vs_final_ng=spearman_jaccard_vs_ng,
            n_jaccard_vs_ng=n4,
            spearman_conflict_count_vs_max_point_vs_story_overlap=spearman_conflict_vs_story,
            n_conflict_vs_story=n5,
            spearman_jaccard_vs_max_point_vs_story_overlap=spearman_jaccard_vs_story,
            n_jaccard_vs_story=n6,
            spearman_conflict_count_vs_lexical_flagged_attempt=spearman_conflict_vs_lexflag,
            n_conflict_vs_lexflag=n7,
        ),
        fact_supply_by_theme=fact_supply_rows,
        run_level_conflict_rate=dict(
            initial_conflict_present_rate=initial_conflict_rate,
            final_conflict_present_rate=final_conflict_rate,
            n_runs=len(run_rows),
        ),
    )


# ---------------------------------------------------------------------------
# PART 2: Candidate-4 (entity-excluded overlap) recalibration
# ---------------------------------------------------------------------------

def load_prior_stage4_observations():
    """Read-only reuse of Stage4 Redesign Inventory's own recompute output
    (point_attempt_observations.csv), which already carries per-observation
    overlap_ratio/point_word_count/story_word_count/shared_words/flag. We
    do NOT re-run that script; we only read its already-materialized CSV
    output (existing artifact) to avoid duplicating the full pipeline."""
    path = os.path.join(BASE, "er011_output", "news_stage4_redesign_inventory_01",
                         "point_attempt_observations.csv")
    if not os.path.isfile(path):
        return None
    rows = []
    with io.open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def part2_recalibration(entity_dict):
    """
    Recompute, PER RUN'S LAST ATTEMPT ONLY (where full Point + Full Story
    text is guaranteed saved as article.md's Point sections + Main Story),
    a fully-normalized (numerator AND denominator entity-excluded) overlap
    ratio, both with and without ordinal words in NUMBER_WORDS, and compare
    percentile-matched-threshold rank correlation against the raw metric.
    """
    rows = []
    for src in SOURCES:
        root = os.path.join(BASE, src["root"])
        theme = src["theme"]
        for level in LEVELS:
            for cond in src["conditions"]:
                cond_dir = os.path.join(root, level, cond)
                if not os.path.isdir(cond_dir):
                    continue
                for run_name in sorted(os.listdir(cond_dir)):
                    run_dir = os.path.join(cond_dir, run_name)
                    article_path = os.path.join(run_dir, "article.md")
                    if not os.path.isfile(article_path):
                        continue
                    with io.open(article_path, encoding="utf-8") as f:
                        text = f.read()
                    # Split Main Story (before first ###) vs Point sections
                    parts = re.split(r"\n###\s+", text)
                    if len(parts) < 3:
                        continue
                    main_story = parts[0]
                    # strip leading title line
                    main_story = re.sub(r"^#\s+.*\n", "", main_story, count=1)
                    point_blocks = parts[1:]
                    # last point_block may contain "## In one line" trailer; split it off
                    def strip_trailer(block):
                        m = re.search(r"\n##\s+In one line", block)
                        if m:
                            return block[:m.start()]
                        return block
                    point_texts = [strip_trailer(b) for b in point_blocks[:2]]
                    if len(point_texts) < 2:
                        continue
                    story_words_all = _content_words(main_story)
                    for label, ptext in zip(["point_one", "point_two"], point_texts):
                        point_words_all = _content_words(ptext)
                        # raw metric (Production-identical logic)
                        raw_ratio, raw_shared = lexical_overlap_ratio(point_words_all, story_words_all)
                        raw_flag = raw_ratio >= 0.40

                        def filtered(words, number_set):
                            return {w for w in words if not (
                                w in number_set or w in entity_dict.get(theme, set()))}

                        # candidate: numerator AND denominator entity-excluded, ordinals kept as numbers
                        pw_f = filtered(point_words_all, NUMBER_WORDS)
                        sw_f = filtered(story_words_all, NUMBER_WORDS)
                        cand_ratio, cand_shared = lexical_overlap_ratio(pw_f, sw_f)
                        cand_flag = cand_ratio >= 0.40

                        # candidate variant: ordinals excluded from NUMBER_WORDS (treated as normal words)
                        pw_f2 = filtered(point_words_all, NUMBER_WORDS_NO_ORDINALS)
                        sw_f2 = filtered(story_words_all, NUMBER_WORDS_NO_ORDINALS)
                        cand2_ratio, cand2_shared = lexical_overlap_ratio(pw_f2, sw_f2)
                        cand2_flag = cand2_ratio >= 0.40

                        rows.append(dict(
                            trial=src["trial"], theme=theme,
                            topic_structure=src["topic_structure"], level=level,
                            condition=cond, run=run_name, point_label=label,
                            point_word_count_raw=len(point_words_all),
                            story_word_count_raw=len(story_words_all),
                            raw_overlap_ratio=round(raw_ratio, 4), raw_flag=raw_flag,
                            point_word_count_filtered=len(pw_f),
                            story_word_count_filtered=len(sw_f),
                            candidate_full_norm_overlap_ratio=round(cand_ratio, 4),
                            candidate_full_norm_flag=cand_flag,
                            candidate_no_ordinal_overlap_ratio=round(cand2_ratio, 4),
                            candidate_no_ordinal_flag=cand2_flag,
                        ))
    return rows


def percentile_threshold(values, target_flag_rate):
    """Find threshold t such that P(value >= t) approx target_flag_rate."""
    vals = sorted([v for v in values if v is not None])
    if not vals:
        return None
    n = len(vals)
    target_count = round(target_flag_rate * n)
    if target_count <= 0:
        return vals[-1] + 0.0001
    if target_count >= n:
        return vals[0]
    idx = n - target_count
    return vals[idx]


def part2_percentile_analysis(part2_rows):
    raw_ratios = [r["raw_overlap_ratio"] for r in part2_rows]
    cand_ratios = [r["candidate_full_norm_overlap_ratio"] for r in part2_rows]
    n = len(raw_ratios)
    raw_flag_rate = rate([r["raw_flag"] for r in part2_rows])
    cand_flag_rate_at_040 = rate([r["candidate_full_norm_flag"] for r in part2_rows])

    # percentile-matched threshold for candidate metric (same flag rate as raw @0.40)
    matched_thresh = percentile_threshold(cand_ratios, raw_flag_rate) if raw_flag_rate else None
    matched_flags = [ratio >= matched_thresh for ratio in cand_ratios] if matched_thresh is not None else []
    matched_flag_rate = rate(matched_flags) if matched_flags else None

    sp, n_sp = spearman(raw_ratios, cand_ratios)

    # rank-order swap count: compare binary classification (raw@0.40 vs candidate@matched_thresh)
    swaps = 0
    if matched_thresh is not None:
        for r, cflag in zip(part2_rows, matched_flags):
            if bool(r["raw_flag"]) != bool(cflag):
                swaps += 1

    return dict(
        n=n,
        raw_flag_rate_at_040=raw_flag_rate,
        candidate_full_norm_flag_rate_at_040=cand_flag_rate_at_040,
        candidate_percentile_matched_threshold=round(matched_thresh, 4) if matched_thresh is not None else None,
        candidate_flag_rate_at_matched_threshold=matched_flag_rate,
        spearman_raw_vs_candidate_ratio=sp,
        n_pairs=n_sp,
        classification_swap_count=swaps,
        classification_swap_rate=round(swaps / n, 4) if n else None,
    )


def part2_ledger_word_share(entity_dict):
    """(iii) share of Point content words that are Ledger-derived (theme
    entity-dict words or NUMBER_WORDS), by theme x level."""
    groups = defaultdict(lambda: [0, 0])  # (theme, level) -> [ledger_word_occurrences, total_word_occurrences]
    for src in SOURCES:
        root = os.path.join(BASE, src["root"])
        theme = src["theme"]
        for level in LEVELS:
            for cond in src["conditions"]:
                cond_dir = os.path.join(root, level, cond)
                if not os.path.isdir(cond_dir):
                    continue
                for run_name in sorted(os.listdir(cond_dir)):
                    run_dir = os.path.join(cond_dir, run_name)
                    article_path = os.path.join(run_dir, "article.md")
                    if not os.path.isfile(article_path):
                        continue
                    with io.open(article_path, encoding="utf-8") as f:
                        text = f.read()
                    parts = re.split(r"\n###\s+", text)
                    if len(parts) < 3:
                        continue
                    for block in parts[1:3]:
                        m = re.search(r"\n##\s+In one line", block)
                        if m:
                            block = block[:m.start()]
                        words = re.findall(r"[A-Za-z']+", block.lower())
                        words = [w for w in words if w not in _STOPWORDS and len(w) > 2]
                        for w in words:
                            groups[(theme, level)][1] += 1
                            if w in NUMBER_WORDS or w in entity_dict.get(theme, set()):
                                groups[(theme, level)][0] += 1
    out = []
    for (theme, level), (ledger_n, total_n) in sorted(groups.items()):
        out.append(dict(theme=theme, level=level, ledger_word_occurrences=ledger_n,
                         total_content_word_occurrences=total_n,
                         ledger_word_share=round(ledger_n / total_n, 4) if total_n else None))
    return out


# ---------------------------------------------------------------------------
# PART 3: Measurement design (continuous overlap_ratio vs binary NG, power)
# ---------------------------------------------------------------------------

def part3_measurement_design(attempt_rows):
    # Trial-08 branch_diagnostic vs baseline-equivalent comparison illustration:
    # Use existing final-attempt cross_overlap_ratio distribution by condition
    trial08_rows = [r for r in attempt_rows if r["trial"] == "trial08_branch"]

    # final-attempt only, per run
    by_run_final = {}
    for r in trial08_rows:
        key = (r["level"], r["condition"], r["run"])
        cur = by_run_final.get(key)
        if cur is None or r["attempt"] > cur["attempt"]:
            by_run_final[key] = r

    final_ratios = [r["cross_overlap_ratio"] for r in by_run_final.values()]
    final_ng = [1 if r["final_ng"] else 0 for r in by_run_final.values()]

    n = len(final_ratios)
    mean_ratio_ng = mean([r for r, g in zip(final_ratios, final_ng) if g == 1])
    mean_ratio_ok = mean([r for r, g in zip(final_ratios, final_ng) if g == 0])

    # Same illustration using the actual GATE metric (max of point_vs_story
    # overlap_ratio across P1/P2, since this -- not cross_point_overlap --
    # is what determines lexical_flagged/NG in Production).
    def max_story(r):
        vals = [v for v in (r["p1_story_overlap_ratio"], r["p2_story_overlap_ratio"]) if v is not None]
        return max(vals) if vals else None

    final_story_ratios = [max_story(r) for r in by_run_final.values()]
    mean_story_ng = mean([r for r, g in zip(final_story_ratios, final_ng) if g == 1])
    mean_story_ok = mean([r for r, g in zip(final_story_ratios, final_ng) if g == 0])

    # overall attempt-level distribution by phase (continuous measure) across ALL trials
    initial_ratios = [r["cross_overlap_ratio"] for r in attempt_rows if r["attempt"] == 0
                       and r["cross_overlap_ratio"] is not None]
    retry_ratios = [r["cross_overlap_ratio"] for r in attempt_rows if r["attempt"] > 0
                    and r["cross_overlap_ratio"] is not None]

    def describe(vals):
        if not vals:
            return dict(n=0)
        return dict(n=len(vals), mean=round(statistics.mean(vals), 4),
                     stdev=round(statistics.stdev(vals), 4) if len(vals) > 1 else None,
                     min=round(min(vals), 4), max=round(max(vals), 4))

    all_final_story_ratios_by_run = [max_story(r) for r in by_run_final.values()]

    return dict(
        trial08_n_runs=n,
        trial08_mean_cross_overlap_ratio_final_ng=mean_ratio_ng,
        trial08_mean_cross_overlap_ratio_final_ok=mean_ratio_ok,
        trial08_mean_max_point_vs_story_overlap_final_ng=mean_story_ng,
        trial08_mean_max_point_vs_story_overlap_final_ok=mean_story_ok,
        trial08_final_max_point_vs_story_overlap_distribution=describe(
            [v for v in all_final_story_ratios_by_run if v is not None]),
        all_trials_initial_cross_overlap_distribution=describe(initial_ratios),
        all_trials_retry_cross_overlap_distribution=describe(retry_ratios),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_csv(path, rows):
    if not rows:
        with io.open(path, "w", encoding="utf-8") as f:
            f.write("")
        return
    fieldnames = list(rows[0].keys())
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    (attempt_rows, run_rows, missing_role_planning, missing_overlap_log,
     conflict_recurrence) = part1_evidence_allocation()
    part1_agg = part1_aggregate(attempt_rows, run_rows)

    entity_dict = build_entity_dict()
    part2_rows = part2_recalibration(entity_dict)
    part2_summary = part2_percentile_analysis(part2_rows)
    part2_ledger_share = part2_ledger_word_share(entity_dict)

    part3 = part3_measurement_design(attempt_rows)

    write_csv(os.path.join(OUT_DIR, "part1_attempt_observations.csv"), attempt_rows)
    write_csv(os.path.join(OUT_DIR, "part1_run_summary.csv"), run_rows)
    write_csv(os.path.join(OUT_DIR, "part2_candidate4_recalibration.csv"), part2_rows)

    results = dict(
        part1=dict(
            aggregate=part1_agg,
            n_attempt_observations=len(attempt_rows),
            n_runs=len(run_rows),
            missing_role_planning_runs=missing_role_planning,
            missing_overlap_log_runs=missing_overlap_log,
            conflict_recurrence=conflict_recurrence,
        ),
        part2=dict(
            summary=part2_summary,
            ledger_word_share_by_theme_level=part2_ledger_share,
            entity_dict_sizes={k: len(v) for k, v in entity_dict.items()},
        ),
        part3=part3,
    )
    with io.open(os.path.join(OUT_DIR, "evidence_allocation_audit_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("=== PART 1 aggregate ===")
    print(json.dumps(part1_agg, indent=2, ensure_ascii=False))
    print("=== PART 2 summary ===")
    print(json.dumps(part2_summary, indent=2, ensure_ascii=False))
    print("=== PART 3 ===")
    print(json.dumps(part3, indent=2, ensure_ascii=False))
    print(f"missing_role_planning_runs: {len(missing_role_planning)}")
    print(f"missing_overlap_log_runs: {len(missing_overlap_log)}")


if __name__ == "__main__":
    main()
