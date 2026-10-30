"""N5段の費用集計(実測cost_logから、level別・round別・initial/backfill別)。usage: <python> cost_table.py (cwd=repo root)
N5段 = stage が kp_n5_ で始まるもの(b1/sel/gen5/ver5/chk5)。segment='roundN:attemptM:initial|backfill'。"""
import sys, os, json, tempfile, collections
sys.path.insert(0, os.getcwd())
import er053_cost_aggregate_01 as agg
R = {
 "X": "er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_n5ev3/raw_usage_log.jsonl",
 "Y": "er121_output/family_y_production_01/redelivery_fee/run_n5ev3/cost_log.jsonl",
 "Z": "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_n5ev3/cost_log.jsonl",
}
def total(rows):
    if not rows: return 0.0
    fd, p = tempfile.mkstemp(suffix=".jsonl"); os.close(fd)
    with open(p, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    t = agg.compute_stage_cost_breakdown_multi(p)["total_jpy"]; os.remove(p); return round(t, 3)
out = {}
for k, p in R.items():
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    n5 = [r for r in rows if str(r.get("stage", "")).startswith("kp_n5_")]
    g = collections.defaultdict(list)
    for r in n5:
        seg = r.get("segment") or ""
        lvl = "a2" if str(r.get("theme", "")).endswith("a2") or "a2" in str(r.get("theme", "")).lower().split("_")[-1:] else ("b1b" if "b1b" in str(r.get("theme", "")).lower() else "?")
        g[(lvl, seg)].append(r)
    out[k] = {"total_all_stages": total(rows), "n5_total": total(n5),
              "n5_by_level_segment": {f"{lvl}|{seg}": total(v) for (lvl, seg), v in sorted(g.items())},
              "n5_initial": total([r for r in n5 if str(r.get("segment") or "").endswith(":initial")]),
              "n5_backfill": total([r for r in n5 if str(r.get("segment") or "").endswith(":backfill")]),
              "n5_by_round": {rd: total([r for r in n5 if str(r.get("segment") or "").startswith(rd + ":")]) for rd in sorted({str(r.get("segment") or "").split(":")[0] for r in n5})},
              "n5_calls": len(n5), "themes": sorted({str(r.get("theme")) for r in n5})}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cost_table.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))

# --- stage別(N5各段)内訳 ---
by_stage = {}
for k, p in R.items():
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    st = collections.defaultdict(list)
    for r in rows:
        if str(r.get("stage", "")).startswith("kp_n5_"):
            st[r["stage"]].append(r)
    by_stage[k] = {s: total(v) for s, v in sorted(st.items())}
out["n5_by_stage"] = by_stage
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cost_table.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(by_stage, ensure_ascii=False))
