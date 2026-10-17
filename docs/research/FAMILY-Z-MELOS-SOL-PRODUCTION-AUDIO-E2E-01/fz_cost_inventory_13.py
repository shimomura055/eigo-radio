# read-only cost inventory (JPY0). Aggregates cost_log.jsonl per run using er019 compute logic.
import argparse, json, os, sys, glob, collections
sys.path.insert(0, os.getcwd())
import er019_family_x_audio_production_runner_01 as r
ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
res = {}
for p in sorted(glob.glob(os.path.join(a.root, "**", "cost_log.jsonl"), recursive=True)):
    if "evidence" in p or "pre_regen" in p:
        continue
    try:
        total, byp = r.compute_cost_jpy_so_far(p)
    except Exception as e:
        res[p] = {"error": repr(e)}; continue
    # per-stage + per-JST-day via single-record cost
    stage = collections.defaultdict(float); day = collections.defaultdict(float); n = 0
    import tempfile
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            n += 1
            rec = json.loads(line)
            with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as t:
                t.write(line + "\n"); tn = t.name
            try:
                c, _ = r.compute_cost_jpy_so_far(tn)
            except Exception:
                c = 0.0
            os.unlink(tn)
            stage[rec.get("stage")] += c
            ts = rec.get("timestamp", "")[:19]
            try:
                import datetime
                d = (datetime.datetime.fromisoformat(ts) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
            except Exception:
                d = "?"
            day[d] += c
    res[os.path.relpath(p, a.root).replace("\\", "/")] = {"rows": n, "total_jpy": round(total, 4), "by_provider": {k: round(v, 4) for k, v in byp.items()} if isinstance(byp, dict) else str(byp),
        "by_stage": {str(k): round(v, 4) for k, v in stage.items()}, "by_jst_day": {k: round(v, 4) for k, v in day.items()}}
json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, v.get("rows"), v.get("total_jpy"), v.get("by_jst_day"), v.get("error", ""))
