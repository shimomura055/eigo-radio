"""KPN5(委任_02/03/04)の実費をJST日次で集計(daily_cost.pyと同じ区切り: 10-30=[2026-10-29T15:00:00Z,2026-10-30T15:00:00Z)、10-31=それ以降)。
対象: ev02/ev03配下のcost_log系jsonl(複製run dirの原本は同内容のため二重計上しない)。単価はer053 compute_stage_cost_breakdown_multi(TTS等の無い、LLM costの下限値)。usage: <python> cost_by_jst_day.py (cwd=repo root)"""
import sys, os, json, glob, tempfile, collections
sys.path.insert(0, os.getcwd())
import er053_cost_aggregate_01 as agg
B = "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01"
def grp(p):
    p = p.replace("\\", "/")
    if "/ev02/" in p: return "委任_02"
    if "/m10/untidi_b1b/" in p or "/ev03/p11/" in p: return "委任_04"
    return "委任_03"
files = [p for p in glob.glob(f"{B}/ev0[23]/**/*.jsonl", recursive=True) if ("cost_log" in p or "usage" in p) and "inject_log" not in p]
seen, rows = set(), collections.defaultdict(list)
for p in sorted(files):
    for l in open(p, encoding="utf-8", errors="replace"):
        try: r = json.loads(l)
        except Exception: continue
        if not isinstance(r, dict) or r.get("success") is False or not r.get("timestamp"): continue
        k = (r["timestamp"], r.get("model_id") or r.get("model"), r.get("input_tokens"), r.get("output_tokens"), r.get("stage"))
        if k in seen: continue
        seen.add(k)
        day = "10-30(JST)" if r["timestamp"][:19] < "2026-10-30T15:00:00" else "10-31(JST)"
        rows[(grp(p), day)].append(r)
def total(rs):
    fd, p = tempfile.mkstemp(suffix=".jsonl"); os.close(fd)
    with open(p, "w", encoding="utf-8") as f:
        for r in rs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    t = agg.compute_stage_cost_breakdown_multi(p)["total_jpy"]; os.remove(p); return round(t, 2)
out = {f"{g}|{d}": {"jpy": total(v), "records": len(v), "ts_min": min(r['timestamp'] for r in v), "ts_max": max(r['timestamp'] for r in v)} for (g, d), v in sorted(rows.items())}
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open("docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03/cost_by_jst_day.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
