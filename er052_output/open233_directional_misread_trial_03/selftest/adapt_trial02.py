"""TRIAL-02 results_merged を TRIAL-03 入力契約へ変換(phase/fallbackは空)し aggregate_trial_03 を実行、整合を検証。"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T3 = os.path.dirname(HERE)
T2 = os.path.join(os.path.dirname(T3), "open233_directional_misread_trial_02")
T1 = os.path.join(os.path.dirname(T3), "open233_directional_misread_trial_01")
rows = [json.loads(x) for x in open(os.path.join(T2, "run", "results_merged.jsonl"), encoding="utf-8") if x.strip()]
for r in rows:
    r["heldout"] = False
    r.setdefault("final_compares", [x["compare"] for x in r["repeats"]])
    for x in r["repeats"]:
        x.update({"article_phase": None, "matched_event_phase": None, "fallback_used": False, "fallback_calls": 0, "fallback_details": None})
p = os.path.join(HERE, "results_adapted.jsonl")
open(p, "w", encoding="utf-8").write("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
cmd = [sys.executable, os.path.join(T3, "aggregate_trial_03.py"), "--results-x", p, "--results-y", p,
       "--ledger-cache", os.path.join(T2, "run", "ledger_cache.json"), "--truth", os.path.join(T2, "ledger_truth_02.json"),
       "--testset", os.path.join(T2, "testset_02.json"), "--population", os.path.join(T1, "population_01.json"),
       "--prev-summary", os.path.join(T2, "trial_summary_02.json"), "--prev-results", os.path.join(T2, "run", "results_merged.jsonl"),
       "--out", os.path.join(HERE, "out")]
print(subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8").stdout or "NO STDOUT (error)")
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if r.returncode:
    print(r.stderr)
    sys.exit(1)
S = json.load(open(os.path.join(HERE, "out", "trial_summary_03.json"), encoding="utf-8"))["configs"]["X"]
g = S["items"]["gold"]
chk = {"HC-012 3/3": g["G-01"]["k"] == 3, "A5-0 3/3": g["G-02"]["k"] == 3, "D61 0/3": g["G-03"]["k"] == 0,
       "normal false=0": S["items"]["normal_pool"]["false_reversal"] == 0, "n_items=63": S["items"]["n_items"] == 63,
       "prev changed none": not S["regression_vs_trial02"]["changed_rep0"],
       "prev_false recurred none": not any(v["recurred"] for v in S["items"]["prev_false_alarms"].values())}
print(json.dumps(chk, ensure_ascii=False))
print("SELFTEST", "PASS" if all(chk.values()) else "FAIL")
