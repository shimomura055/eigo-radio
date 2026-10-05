"""rep30 38 instanceの後段費用内訳の再確認(委任_16、¥0)。instances_s*/*.jsonのcall_log.cost_jpyをlabel区分で集計。"""
import json, glob, collections, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
agg = collections.defaultdict(float); cnt = collections.Counter(); cyc = collections.Counter(); st = collections.Counter(); tot = 0
fs = glob.glob(ROOT + "/er052_output/open233_self_recovery_flow_runner_01_rep30/instances_s*/*.json")
for f in fs:
    d = json.load(open(f, encoding="utf8"))
    for c in d.get("call_log", []):
        lab = c.get("label") or ""
        k = "recheck" if "recheck" in lab else "stage2" if "stage2" in lab else "rewrite" if "rewrite" in lab else "stage1" if lab.endswith("stage1") else "other"
        agg[k] += c.get("cost_jpy") or 0; cnt[k] += 1; tot += c.get("cost_jpy") or 0
    cyc[len(d.get("cycles") or [])] += 1; st[d.get("final_state")] += 1
out = {"n": len(fs), "per_run_jpy": {k: round(v / len(fs), 3) for k, v in agg.items()}, "calls": dict(cnt), "total_per_run": round(tot / len(fs), 3), "cycles_dist": dict(cyc), "final_state": dict(st)}
json.dump(out, open(os.path.join(os.path.dirname(__file__), "agg_rep30_cost_breakdown_01.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(out)
