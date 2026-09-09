#!/usr/bin/env python3
"""
Machine-readable point quality retry log aggregation (L0).
No interpretation, no judgment — pure data collection and counting.

Management ID: FAMILY-A-POINT-QUALITY-RETRY-LOG-AGGREGATION-L0-01
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter

# ============================================================================
# CONFIG
# ============================================================================

ROOT = Path("C:/Users/tensh/eigo-radio")
OUTPUT_DIR = ROOT / "er011_output" / "point_quality_retry_log_aggregation_l0_01"
TRIALS = [
    {
        "name": "trial_06",
        "dir": "news_focus_hint_comparison_trial_06",
        "themes": ["a2", "b1b"],
        "conditions": ["baseline", "focus_hint", "hint_only"],
        "runs": ["run1", "run2", "run3"],
    },
    {
        "name": "trial_04",
        "dir": "daily_news_focus_layer_comparison_trial_04",
        "themes": ["a2", "b1b"],
        "conditions": ["baseline", "focus"],
        "runs": ["run1", "run2", "run3"],
    },
    {
        "name": "trial_05",
        "dir": "point_overlap_gap_fix_trial_05",
        "themes_alt": True,  # hanshin/theme2 structure
        "levels": ["a2", "b1b"],
        "conditions": ["baseline", "gapfix"],
        "runs": ["run1", "run2"],
    },
    {
        "name": "trial_07",
        "dir": "discovery_layer3_focus_trial_07",
        "themes": ["a2", "b1b"],
        "conditions": ["baseline", "discovery_focus"],
        "runs": ["run1", "run2", "run3"],
    },
]

# ============================================================================
# HELPERS
# ============================================================================

def safe_read_json(path):
    """Try reading JSON, return None if fails."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return None

def extract_attempt_flags(retry_log):
    """
    Extract attempt-level flags from point_overlap_article_retry_log.json.
    The file is an array of attempt records.
    Returns list of (attempt_num, lexical_flagged, value_qa_flagged, point_one_ratio, point_two_ratio).
    """
    if not retry_log:
        return []

    # retry_log is expected to be a list of attempt records
    if not isinstance(retry_log, list):
        return []

    attempts = []
    for att in retry_log:
        attempt_num = att.get("attempt")
        lexical_flagged = att.get("lexical_flagged")
        value_qa_flagged = att.get("value_qa_flagged")

        # Extract ratios from report if available
        point_one_ratio = None
        point_two_ratio = None

        report = att.get("report", {})
        if "point_one" in report:
            point_one_ratio = report["point_one"].get("before_overlap", {}).get("overlap_ratio")
        if "point_two" in report:
            point_two_ratio = report["point_two"].get("before_overlap", {}).get("overlap_ratio")

        attempts.append({
            "attempt_num": attempt_num,
            "lexical_flagged": lexical_flagged,
            "value_qa_flagged": value_qa_flagged,
            "point_one_ratio": point_one_ratio,
            "point_two_ratio": point_two_ratio,
        })

    return sorted(attempts, key=lambda x: x["attempt_num"] if x["attempt_num"] is not None else -1)

def extract_analysis_status(analysis_file):
    """Extract final status and fact_checker_verdict from analysis.json."""
    if not analysis_file:
        return None, None

    # Try various field names
    final_status = analysis_file.get("status") or analysis_file.get("final_status")
    fact_checker_verdict = analysis_file.get("fact_verdict") or analysis_file.get("fact_checker_verdict")

    return final_status, fact_checker_verdict

def extract_roles(point_role_file):
    """Extract role names from point_role_planning_initial.json."""
    if not point_role_file:
        return []

    roles = []

    # Try structure with "parsed" field
    parsed = point_role_file.get("parsed", {})
    if parsed:
        for point_key in ["point_one", "point_two"]:
            point = parsed.get(point_key, {})
            role = point.get("role")
            if role:
                roles.append(role)
    else:
        # Alternative structure (list of points)
        for point in point_role_file.get("points", []):
            role = point.get("role")
            if role:
                roles.append(role)

    return roles

def extract_ledger_deviation(analysis_file):
    """Extract ledger_deviation_status from analysis.json if available."""
    if not analysis_file:
        return None

    return analysis_file.get("ledger_status") or analysis_file.get("ledger_deviation_status")

# ============================================================================
# MAIN AGGREGATION
# ============================================================================

def main():
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Storage structures
    run_table = []  # List of run records
    attempt_transitions = []  # List of (run_id, transitions_count)
    all_roles = []  # For Point Role distribution
    missing_files = []  # Missing or unreadable files

    total_runs = 0

    # ========================================================================
    # TRIAL 06
    # ========================================================================
    print("Processing trial_06...", file=sys.stderr)
    trial_06_dir = ROOT / "er011_output" / "news_focus_hint_comparison_trial_06"

    trial_06_runs = 0
    for theme in ["a2", "b1b"]:
        for condition in ["baseline", "focus_hint", "hint_only"]:
            for run in ["run1", "run2", "run3"]:
                base_path = trial_06_dir / theme / condition / run

                retry_log_path = base_path / "point_overlap_article_retry_log.json"
                analysis_path = base_path / "analysis.json"
                role_path = base_path / "audit" / "point_role_planning_initial.json"

                retry_log = safe_read_json(retry_log_path)
                analysis_file = safe_read_json(analysis_path)
                role_file = safe_read_json(role_path)

                if retry_log is None:
                    missing_files.append(str(retry_log_path))
                    continue

                trial_06_runs += 1
                total_runs += 1

                attempts = extract_attempt_flags(retry_log)
                final_status, fact_checker_verdict = extract_analysis_status(analysis_file)
                ledger_deviation = extract_ledger_deviation(analysis_file)
                roles = extract_roles(role_file)

                # Determine final status
                if not attempts:
                    final_status_str = "NO_ATTEMPTS"
                    attempt_count = 0
                    last_flags = (None, None)
                else:
                    attempt_count = len(attempts)
                    last = attempts[-1]
                    last_flags = (last["lexical_flagged"], last["value_qa_flagged"])
                    if last["lexical_flagged"] or last["value_qa_flagged"]:
                        final_status_str = "NG"
                    else:
                        final_status_str = "OK"

                run_id = f"trial_06/{theme}/{condition}/{run}"

                # Build run record
                run_record = {
                    "trial": "trial_06",
                    "theme": theme,
                    "condition": condition,
                    "run": run,
                    "run_id": run_id,
                    "final_status": final_status_str,
                    "attempt_count": attempt_count,
                    "attempts": attempts,
                    "fact_checker_verdict": fact_checker_verdict,
                    "ledger_deviation_status": ledger_deviation,
                }

                run_table.append(run_record)
                all_roles.extend(roles)

                # Count attempt transitions (flag flips)
                transitions = 0
                for i in range(len(attempts) - 1):
                    curr = (attempts[i]["lexical_flagged"], attempts[i]["value_qa_flagged"])
                    next_att = (attempts[i+1]["lexical_flagged"], attempts[i+1]["value_qa_flagged"])

                    # Transition if exactly one flag changed (is_flag_flip)
                    curr_count = sum(1 for x in curr if x is True)
                    next_count = sum(1 for x in next_att if x is True)

                    if curr != next_att:
                        transitions += 1

                attempt_transitions.append({"run_id": run_id, "transitions": transitions})

    print(f"  trial_06: {trial_06_runs} runs", file=sys.stderr)

    # ========================================================================
    # TRIAL 04
    # ========================================================================
    print("Processing trial_04...", file=sys.stderr)
    trial_04_dir = ROOT / "er011_output" / "daily_news_focus_layer_comparison_trial_04"

    trial_04_runs = 0
    for theme in ["a2", "b1b"]:
        for condition in ["baseline", "focus"]:
            for run in ["run1", "run2", "run3"]:
                base_path = trial_04_dir / theme / condition / run

                retry_log_path = base_path / "point_overlap_article_retry_log.json"
                analysis_path = base_path / "analysis.json"
                role_path = base_path / "audit" / "point_role_planning_initial.json"

                retry_log = safe_read_json(retry_log_path)
                analysis_file = safe_read_json(analysis_path)
                role_file = safe_read_json(role_path)

                if retry_log is None:
                    missing_files.append(str(retry_log_path))
                    continue

                trial_04_runs += 1
                total_runs += 1

                attempts = extract_attempt_flags(retry_log)
                final_status, fact_checker_verdict = extract_analysis_status(analysis_file)
                ledger_deviation = extract_ledger_deviation(analysis_file)
                roles = extract_roles(role_file)

                if not attempts:
                    final_status_str = "NO_ATTEMPTS"
                    attempt_count = 0
                else:
                    attempt_count = len(attempts)
                    last = attempts[-1]
                    if last["lexical_flagged"] or last["value_qa_flagged"]:
                        final_status_str = "NG"
                    else:
                        final_status_str = "OK"

                run_id = f"trial_04/{theme}/{condition}/{run}"

                run_record = {
                    "trial": "trial_04",
                    "theme": theme,
                    "condition": condition,
                    "run": run,
                    "run_id": run_id,
                    "final_status": final_status_str,
                    "attempt_count": attempt_count,
                    "attempts": attempts,
                    "fact_checker_verdict": fact_checker_verdict,
                    "ledger_deviation_status": ledger_deviation,
                }

                run_table.append(run_record)
                all_roles.extend(roles)

                transitions = 0
                for i in range(len(attempts) - 1):
                    if attempts[i] != attempts[i+1]:
                        transitions += 1

                attempt_transitions.append({"run_id": run_id, "transitions": transitions})

    print(f"  trial_04: {trial_04_runs} runs", file=sys.stderr)

    # ========================================================================
    # TRIAL 05
    # ========================================================================
    print("Processing trial_05...", file=sys.stderr)
    trial_05_dir = ROOT / "er011_output" / "point_overlap_gap_fix_trial_05"

    trial_05_runs = 0
    for theme_root in ["hanshin", "theme2"]:
        for level in ["a2", "b1b"]:
            for condition in ["baseline", "gapfix"]:
                for run in ["run1", "run2"]:
                    base_path = trial_05_dir / theme_root / level / condition / run

                    retry_log_path = base_path / "point_overlap_article_retry_log.json"
                    analysis_path = base_path / "analysis.json"
                    role_path = base_path / "audit" / "point_role_planning_initial.json"

                    retry_log = safe_read_json(retry_log_path)
                    analysis_file = safe_read_json(analysis_path)
                    role_file = safe_read_json(role_path)

                    if retry_log is None:
                        missing_files.append(str(retry_log_path))
                        continue

                    trial_05_runs += 1
                    total_runs += 1

                    attempts = extract_attempt_flags(retry_log)
                    final_status, fact_checker_verdict = extract_analysis_status(analysis_file)
                    ledger_deviation = extract_ledger_deviation(analysis_file)
                    roles = extract_roles(role_file)

                    if not attempts:
                        final_status_str = "NO_ATTEMPTS"
                        attempt_count = 0
                    else:
                        attempt_count = len(attempts)
                        last = attempts[-1]
                        if last["lexical_flagged"] or last["value_qa_flagged"]:
                            final_status_str = "NG"
                        else:
                            final_status_str = "OK"

                    run_id = f"trial_05/{theme_root}/{level}/{condition}/{run}"

                    run_record = {
                        "trial": "trial_05",
                        "theme": theme_root,
                        "level": level,
                        "condition": condition,
                        "run": run,
                        "run_id": run_id,
                        "final_status": final_status_str,
                        "attempt_count": attempt_count,
                        "attempts": attempts,
                        "fact_checker_verdict": fact_checker_verdict,
                        "ledger_deviation_status": ledger_deviation,
                    }

                    run_table.append(run_record)
                    all_roles.extend(roles)

                    transitions = 0
                    for i in range(len(attempts) - 1):
                        if attempts[i] != attempts[i+1]:
                            transitions += 1

                    attempt_transitions.append({"run_id": run_id, "transitions": transitions})

    print(f"  trial_05: {trial_05_runs} runs", file=sys.stderr)

    # ========================================================================
    # TRIAL 07
    # ========================================================================
    print("Processing trial_07...", file=sys.stderr)
    trial_07_dir = ROOT / "er011_output" / "discovery_layer3_focus_trial_07"

    trial_07_runs = 0
    for theme in ["a2", "b1b"]:
        for condition in ["baseline", "discovery_focus"]:
            for run in ["run1", "run2", "run3"]:
                base_path = trial_07_dir / theme / condition / run

                retry_log_path = base_path / "point_overlap_article_retry_log.json"
                analysis_path = base_path / "analysis.json"
                role_path = base_path / "audit" / "point_role_planning_initial.json"

                retry_log = safe_read_json(retry_log_path)
                analysis_file = safe_read_json(analysis_path)
                role_file = safe_read_json(role_path)

                if retry_log is None:
                    missing_files.append(str(retry_log_path))
                    continue

                trial_07_runs += 1
                total_runs += 1

                attempts = extract_attempt_flags(retry_log)
                final_status, fact_checker_verdict = extract_analysis_status(analysis_file)
                ledger_deviation = extract_ledger_deviation(analysis_file)
                roles = extract_roles(role_file)

                if not attempts:
                    final_status_str = "NO_ATTEMPTS"
                    attempt_count = 0
                else:
                    attempt_count = len(attempts)
                    last = attempts[-1]
                    if last["lexical_flagged"] or last["value_qa_flagged"]:
                        final_status_str = "NG"
                    else:
                        final_status_str = "OK"

                run_id = f"trial_07/{theme}/{condition}/{run}"

                run_record = {
                    "trial": "trial_07",
                    "theme": theme,
                    "condition": condition,
                    "run": run,
                    "run_id": run_id,
                    "final_status": final_status_str,
                    "attempt_count": attempt_count,
                    "attempts": attempts,
                    "fact_checker_verdict": fact_checker_verdict,
                    "ledger_deviation_status": ledger_deviation,
                }

                run_table.append(run_record)
                all_roles.extend(roles)

                transitions = 0
                for i in range(len(attempts) - 1):
                    if attempts[i] != attempts[i+1]:
                        transitions += 1

                attempt_transitions.append({"run_id": run_id, "transitions": transitions})

    print(f"  trial_07: {trial_07_runs} runs", file=sys.stderr)

    # ========================================================================
    # STATISTICS
    # ========================================================================

    # Condition-based aggregation
    condition_stats = defaultdict(lambda: {"total": 0, "ng_count": 0, "ok_count": 0, "attempt_counts": []})
    for run in run_table:
        cond_key = f"{run['trial']}/{run['condition']}"
        condition_stats[cond_key]["total"] += 1
        if run["final_status"] == "NG":
            condition_stats[cond_key]["ng_count"] += 1
        elif run["final_status"] == "OK":
            condition_stats[cond_key]["ok_count"] += 1
        condition_stats[cond_key]["attempt_counts"].append(run["attempt_count"])

    # Point Role distribution
    role_counter = Counter(all_roles)

    # ========================================================================
    # OUTPUT: JSON
    # ========================================================================

    aggregation_data = {
        "metadata": {
            "task_id": "FAMILY-A-POINT-QUALITY-RETRY-LOG-AGGREGATION-L0-01",
            "total_runs": total_runs,
            "runs_by_trial": {
                "trial_06": trial_06_runs,
                "trial_04": trial_04_runs,
                "trial_05": trial_05_runs,
                "trial_07": trial_07_runs,
            },
        },
        "run_table": run_table,
        "attempt_transitions": attempt_transitions,
        "condition_stats": dict(condition_stats),
        "point_role_distribution": dict(role_counter),
        "missing_files": missing_files,
    }

    json_output = output_dir / "aggregation.json"
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(aggregation_data, f, indent=2, ensure_ascii=False)

    # ========================================================================
    # OUTPUT: MARKDOWN
    # ========================================================================

    md_lines = []
    md_lines.append("# Point Quality Retry Log Aggregation (L0)")
    md_lines.append("")
    md_lines.append(f"**Task ID**: FAMILY-A-POINT-QUALITY-RETRY-LOG-AGGREGATION-L0-01")
    md_lines.append("")
    md_lines.append(f"**Total Runs**: {total_runs}")
    md_lines.append("")

    md_lines.append("## Runs by Trial")
    md_lines.append("")
    md_lines.append("| Trial | Count |")
    md_lines.append("|-------|-------|")
    for trial_name in ["trial_06", "trial_04", "trial_05", "trial_07"]:
        count = aggregation_data["metadata"]["runs_by_trial"].get(trial_name, 0)
        md_lines.append(f"| {trial_name} | {count} |")
    md_lines.append("")

    # Condition-based NG rate and attempt average
    md_lines.append("## Condition-based Statistics")
    md_lines.append("")
    md_lines.append("| Trial | Condition | Total | OK | NG | NG Rate | Avg Attempts |")
    md_lines.append("|-------|-----------|-------|-----|-----|---------|---------------|")

    for cond_key in sorted(condition_stats.keys()):
        stats = condition_stats[cond_key]
        trial, condition = cond_key.split("/")
        total = stats["total"]
        ok = stats["ok_count"]
        ng = stats["ng_count"]
        ng_rate = (ng / total * 100) if total > 0 else 0
        avg_att = (sum(stats["attempt_counts"]) / len(stats["attempt_counts"])) if stats["attempt_counts"] else 0

        md_lines.append(f"| {trial} | {condition} | {total} | {ok} | {ng} | {ng_rate:.1f}% | {avg_att:.1f} |")
    md_lines.append("")

    # Attempt transitions by condition
    md_lines.append("## Attempt Transitions (Flag Flips)")
    md_lines.append("")
    transition_by_cond = defaultdict(lambda: [])
    for trans in attempt_transitions:
        parts = trans["run_id"].split("/")
        cond_key = f"{parts[0]}/{parts[2]}" if len(parts) >= 3 else trans["run_id"]
        transition_by_cond[cond_key].append(trans["transitions"])

    md_lines.append("| Trial | Condition | Total Transitions |")
    md_lines.append("|-------|-----------|-------------------|")
    for cond_key in sorted(transition_by_cond.keys()):
        trans_list = transition_by_cond[cond_key]
        total_trans = sum(trans_list)
        trial, condition = cond_key.split("/")
        md_lines.append(f"| {trial} | {condition} | {total_trans} |")
    md_lines.append("")

    # Top Point Roles
    md_lines.append("## Top Point Roles by Frequency")
    md_lines.append("")
    md_lines.append("| Role | Count |")
    md_lines.append("|------|-------|")
    top_roles = role_counter.most_common(20)
    for role, count in top_roles:
        md_lines.append(f"| {role} | {count} |")
    md_lines.append("")

    # Missing files
    if missing_files:
        md_lines.append("## Missing or Unreadable Files")
        md_lines.append("")
        for filepath in missing_files:
            md_lines.append(f"- {filepath}")
        md_lines.append("")
    else:
        md_lines.append("## Missing or Unreadable Files")
        md_lines.append("")
        md_lines.append("None detected.")
        md_lines.append("")

    md_output = output_dir / "aggregation.md"
    with open(md_output, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"\nOutput written to:", file=sys.stderr)
    print(f"  JSON: {json_output}", file=sys.stderr)
    print(f"  Markdown: {md_output}", file=sys.stderr)

if __name__ == "__main__":
    main()
