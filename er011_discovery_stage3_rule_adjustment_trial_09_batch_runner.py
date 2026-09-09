#!/usr/bin/env python3
"""Sequential batch runner for remaining Trial-09 combos (temp helper, not part
of the harness's own module surface; simply calls combo_stage() in a loop so
multiple combos can be launched as a single background process instead of many
separate Bash calls). Trial-only, no Production/shared-module edits."""
import sys

import er011_discovery_stage3_rule_adjustment_trial_09 as t9

COMBOS = [
    ("current_focus", "B1B", 2),
    ("current_focus", "B1B", 3),
    ("adjusted_focus", "A2", 1),
    ("adjusted_focus", "A2", 2),
    ("adjusted_focus", "A2", 3),
    ("adjusted_focus", "B1B", 1),
    ("adjusted_focus", "B1B", 2),
    ("adjusted_focus", "B1B", 3),
]

if __name__ == "__main__":
    for condition_name, label, run_idx in COMBOS:
        print(f"=== BATCH: starting {condition_name} {label} run{run_idx} ===", flush=True)
        t9.combo_stage(condition_name, label, run_idx)
        cost_so_far = t9.compute_cost_so_far_jpy()
        print(f"=== BATCH: cumulative cost so far = Y{cost_so_far:.1f} ===", flush=True)
        if cost_so_far > t9.BUDGET_JPY:
            print(f"=== BATCH: BUDGET_JPY({t9.BUDGET_JPY}) exceeded, stopping remaining combos ===", flush=True)
            sys.exit(1)
    print("=== BATCH: all remaining combos complete ===", flush=True)
