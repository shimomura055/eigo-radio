# ============================================================
# er006_pool_pilot_01_rootfix_analysis.py
# ER-006-POOL-PILOT-COST-ROOTFIX-01: Attempt Ledgerを用いたClean/Actual/Waste再定義
# ============================================================
from __future__ import annotations

import json
from collections import defaultdict

USD_JPY = 160.0

with open("er006_output/pool_pilot_01/attempt_ledger.json", encoding="utf-8") as f:
    LEDGER = json.load(f)

rows = LEDGER["attempts"]
op_err_rows = LEDGER["operator_error"]

# segment内の実行順(seq)を付与(standard 1..N → fallback 1..M の継続番号)
by_seg = defaultdict(list)
for r in rows:
    by_seg[(r["theme"], r["level"], r["segment"])].append(r)
for key, lst in by_seg.items():
    # 元のtimestampで安定ソート(standard/fallbackの境界をまたいで正しい実行順にする)
    lst.sort(key=lambda r: r["timestamp_tts"])
    for i, r in enumerate(lst):
        r["seq"] = i + 1
    for r in lst:
        r["total_cost_jpy"] = r["tts_cost_jpy"] + r["asr_cost_jpy"]

# ------------------------------------------------------------
# セグメント単位サマリー(Clean=seq1、Retry=seq2以降)
# ------------------------------------------------------------
segment_summary = []
for (theme, level, seg), lst in by_seg.items():
    actual = sum(r["total_cost_jpy"] for r in lst)
    clean = lst[0]["total_cost_jpy"] if lst else 0
    retry = actual - clean
    final_status = lst[-1].get("segment_final_status")
    segment_summary.append({
        "theme": theme, "level": level, "segment": seg,
        "n_attempts": len(lst), "final_status": final_status,
        "actual_jpy": round(actual, 2), "clean_jpy": round(clean, 2), "retry_waste_jpy": round(retry, 2),
        "total_duration_seconds": round(sum((r.get("duration_seconds") or 0) for r in lst), 1),
    })

# ------------------------------------------------------------
# theme/level単位ロールアップ
# ------------------------------------------------------------
rollup = defaultdict(lambda: {"actual_jpy": 0.0, "clean_jpy": 0.0, "retry_waste_jpy": 0.0,
                               "n_segments": 0, "n_attempts": 0, "n_stopped": 0})
for s in segment_summary:
    key = (s["theme"], s["level"])
    rollup[key]["actual_jpy"] += s["actual_jpy"]
    rollup[key]["clean_jpy"] += s["clean_jpy"]
    rollup[key]["retry_waste_jpy"] += s["retry_waste_jpy"]
    rollup[key]["n_segments"] += 1
    rollup[key]["n_attempts"] += s["n_attempts"]
    if s["final_status"] == "STOPPED":
        rollup[key]["n_stopped"] += 1

rollup_out = {f"{t}/{l}": {k: (round(v, 2) if isinstance(v, float) else v) for k, v in d.items()}
              for (t, l), d in rollup.items()}

# ------------------------------------------------------------
# STOPPEDセグメントのCost(STOPPEDに費やした全attemptの合計)
# ------------------------------------------------------------
stopped_cost = defaultdict(float)
for s in segment_summary:
    if s["final_status"] == "STOPPED":
        stopped_cost[(s["theme"], s["level"])] += s["actual_jpy"]

# ------------------------------------------------------------
# B1 vs A2 差の分解(theme単位)
# ------------------------------------------------------------
decomposition = {}
for theme in ["pool_benches", "pool_subscriptions", "pool_startups"]:
    b1 = rollup_out.get(f"{theme}/b1", {})
    a2 = rollup_out.get(f"{theme}/a2", {})
    decomposition[theme] = {
        "b1_actual_jpy": b1.get("actual_jpy", 0), "a2_actual_jpy": a2.get("actual_jpy", 0),
        "diff_actual_jpy": round(a2.get("actual_jpy", 0) - b1.get("actual_jpy", 0), 2),
        "b1_clean_jpy": b1.get("clean_jpy", 0), "a2_clean_jpy": a2.get("clean_jpy", 0),
        "diff_clean_jpy": round(a2.get("clean_jpy", 0) - b1.get("clean_jpy", 0), 2),
        "b1_retry_waste_jpy": b1.get("retry_waste_jpy", 0), "a2_retry_waste_jpy": a2.get("retry_waste_jpy", 0),
        "diff_retry_waste_jpy": round(a2.get("retry_waste_jpy", 0) - b1.get("retry_waste_jpy", 0), 2),
        "b1_stopped_cost_jpy": round(stopped_cost.get((theme, "b1"), 0), 2),
        "a2_stopped_cost_jpy": round(stopped_cost.get((theme, "a2"), 0), 2),
        "b1_n_segments": b1.get("n_segments"), "a2_n_segments": a2.get("n_segments"),
        "b1_n_attempts": b1.get("n_attempts"), "a2_n_attempts": a2.get("n_attempts"),
        "b1_n_stopped": b1.get("n_stopped"), "a2_n_stopped": a2.get("n_stopped"),
    }

out = {
    "segment_summary": segment_summary,
    "rollup_by_theme_level": rollup_out,
    "b1_vs_a2_decomposition": decomposition,
    "operator_error_rows": op_err_rows,
    "grand_total_from_ledger": {
        "actual_jpy": round(sum(s["actual_jpy"] for s in segment_summary) + sum(r["tts_cost_jpy"] + r["asr_cost_jpy"] for r in op_err_rows), 2),
        "clean_jpy": round(sum(s["clean_jpy"] for s in segment_summary), 2),
        "retry_waste_jpy": round(sum(s["retry_waste_jpy"] for s in segment_summary), 2),
        "operator_error_jpy": round(sum(r["tts_cost_jpy"] + r["asr_cost_jpy"] for r in op_err_rows), 2),
        "n_stopped_segments": sum(1 for s in segment_summary if s["final_status"] == "STOPPED"),
    },
}

with open("er006_output/pool_pilot_01/rootfix_analysis.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(json.dumps(out["grand_total_from_ledger"], ensure_ascii=False, indent=2))
print("=== B1 vs A2 ===")
print(json.dumps(decomposition, ensure_ascii=False, indent=2))
