# ============================================================
# er011_news_focus_hint_comparison_trial_06_stats.py
# FAMILY-A-COMPLETION-A3-NEWS-FOCUS-HINT-COMPARISON-TRIAL-06 補助
# ============================================================
# all_results_so_far.json(er011_news_focus_hint_comparison_trial_06.py
# analyze_run()の出力、Trial-04と同一ロジックのt4.analyze_run()を再利用)を
# 条件別・レベル別に集計し、stats_summary.jsonへ保存する。新しい判定
# ロジックは追加しない(単純集計のみ)。
from __future__ import annotations

import json
from collections import defaultdict

THEME_ID = "news_focus_hint_comparison_trial_06"
OUT_DIR = f"er011_output/{THEME_ID}"

with open(f"{OUT_DIR}/all_results_so_far.json", encoding="utf-8") as f:
    data = json.load(f)


def avg(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 4) if values else None


def summarize(rows: list) -> dict:
    n = len(rows)
    ok = sum(1 for r in rows if r["status"] == "OK")
    ng = sum(1 for r in rows if r["status"] != "OK")
    p1_role_counts = defaultdict(int)
    p2_role_counts = defaultdict(int)
    for r in rows:
        p1_role_counts[r.get("point_one_role_category") or "n/a"] += 1
        p2_role_counts[r.get("point_two_role_category") or "n/a"] += 1
    p1_body_match = sum(1 for r in rows if (r.get("point_one_body_embodies_role") or {}).get("match"))
    p2_body_match = sum(1 for r in rows if (r.get("point_two_body_embodies_role") or {}).get("match"))
    p1_role_classifiable = sum(1 for r in rows if r.get("point_one_role_category") not in (None, "other"))
    p2_role_classifiable = sum(1 for r in rows if r.get("point_two_role_category") not in (None, "other"))
    return {
        "n": n, "ok": ok, "ng": ng, "ng_rate": round(ng / n, 4) if n else None,
        "retry_avg": avg([r["retry_attempts"] for r in rows]),
        "point_one_overlap_avg": avg([r["point_one_overlap_ratio"] for r in rows]),
        "point_two_overlap_avg": avg([r["point_two_overlap_ratio"] for r in rows]),
        "point_one_overlap_flagged_count": sum(1 for r in rows if r.get("point_one_overlap_flagged")),
        "point_two_overlap_flagged_count": sum(1 for r in rows if r.get("point_two_overlap_flagged")),
        "word_count_avg": avg([r["word_count"] for r in rows]),
        "elapsed_seconds_avg": avg([r["elapsed_seconds"] for r in rows]),
        "point_one_role_category_counts": dict(p1_role_counts),
        "point_two_role_category_counts": dict(p2_role_counts),
        "point_one_role_classifiable_rate": round(p1_role_classifiable / n, 4) if n else None,
        "point_two_role_classifiable_rate": round(p2_role_classifiable / n, 4) if n else None,
        "point_one_body_embodies_role_match_count": p1_body_match,
        "point_two_body_embodies_role_match_count": p2_body_match,
    }


by_condition = defaultdict(list)
by_condition_level = defaultdict(list)
for r in data:
    by_condition[r["condition"]].append(r)
    by_condition_level[(r["condition"], r["level"])].append(r)

result = {
    "by_condition": {k: summarize(v) for k, v in by_condition.items()},
    "by_condition_level": {f"{k[0]}_{k[1]}": summarize(v) for k, v in by_condition_level.items()},
    "total_runs": len(data),
}

with open(f"{OUT_DIR}/stats_summary.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps(result, ensure_ascii=False, indent=2))
