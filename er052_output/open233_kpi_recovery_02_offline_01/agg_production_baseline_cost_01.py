"""現行Production 1記事費用の基準算出(¥0)。raw_usage_log.jsonl(model_id別単価、USD_JPY=160=writer_run_summary記録)。"""
import glob, json, os, statistics
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = {"gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-6-luna": (0.10, 0.01, 0.50)}
JPY = 160.0
def c(x):
    p = P.get(x.get("model_id"))
    if not p: return None
    it, ct, ot = x.get("input_tokens") or 0, x.get("cached_input_tokens") or 0, x.get("output_tokens") or 0
    return (max(it - ct, 0) * p[0] + ct * p[1] + ot * p[2]) / 1e6 * JPY
rows = []
for f in glob.glob(ROOT + "/er019_output/**/raw_usage_log.jsonl", recursive=True):
    rs = [json.loads(l) for l in open(f, encoding="utf8")]
    if not any(r.get("stage") == "ja_original_check" for r in rs) or "ja_writer_stage" in f: continue
    ja = sum(c(r) or 0 for r in rs if (r.get("stage") or "").startswith("ja_"))
    chk = sum(c(r) or 0 for r in rs if "check" in (r.get("stage") or "") or "must_fix" in (r.get("stage") or ""))
    allt = sum(c(r) or 0 for r in rs if r.get("stage") not in ("tts", "scaffold"))
    ts = max(r.get("timestamp") or "" for r in rs)
    rows.append({"file": os.path.relpath(f, ROOT), "ts": ts[:10], "ja_stages_jpy": round(ja, 3), "check_plus_mustfix_jpy": round(chk, 3), "all_text_jpy": round(allt, 3)})
rows.sort(key=lambda r: r["ts"], reverse=True)
out = {"n": len(rows), "usd_jpy": JPY, "rows": rows}
for k in ("ja_stages_jpy", "check_plus_mustfix_jpy", "all_text_jpy"):
    v = [r[k] for r in rows]
    out[k] = {"mean": round(sum(v) / len(v), 3), "median": round(statistics.median(v), 3), "min": min(v), "max": max(v)} if v else None
json.dump(out, open(os.path.join(os.path.dirname(__file__), "agg_production_baseline_cost_01.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in out if k != "rows"}, ensure_ascii=False), rows[:2])
