"""route runtime evidence 収集(読取のみ)。usage: python ev_collect.py <route_label> <level> <kp_candidates.json> <cost_log.jsonl> <article_text_file> <out.json>"""
import sys, os, json, re, collections
ROOT = os.path.abspath(os.getcwd()); sys.path.insert(0, ROOT)
label, level, cpath, clog, tpath, outp = sys.argv[1:7]
doc = json.load(open(cpath, encoding="utf-8"))
text = open(tpath, encoding="utf-8").read() if os.path.exists(tpath) else ""
def nz(s): return " ".join((s or "").replace(chr(0x2019), chr(39)).lower().split())
g = doc.get("generalization") or {}
cands = doc.get("candidates") or []
rows, wc = [], collections.Counter()
for c in cands:
    it = c.get("item") or {}
    n5 = it.get("n5")
    uf, kp, sp = it.get("used_form"), it.get("key_phrase"), it.get("source_span")
    ok_sp = nz(sp) in nz(text) if text else None
    rows.append({"candidate_id": c.get("candidate_id"), "kind": c.get("kind"), "origin": c.get("origin"), "source_span": sp, "display_phrase": it.get("display_phrase"),
                 "used_form": uf, "key_phrase": kp, "japanese_gloss": it.get("japanese_gloss"), "n5": bool(n5),
                 "used_eq_key_eq_n5": (uf == kp == (n5 or {}).get("display_form")) if n5 else None,
                 "gloss_eq_n5": (it.get("japanese_gloss") == (n5 or {}).get("gloss_ja")) if n5 else None,
                 "reverted": (n5 or {}).get("reverted"), "flags": (n5 or {}).get("flags"), "check_relation": ((n5 or {}).get("check") or {}).get("relation"),
                 "gloss_alignment_status": it.get("gloss_alignment_status"), "qa_overall_status": it.get("qa_overall_status"),
                 "normalization_reason": it.get("normalization_reason"), "source_span_in_text": ok_sp,
                 "words_used_form": len((uf or "").split()), "canon_pre": (n5 or {}).get("canon_pre"), "person_repair_gloss": (n5 or {}).get("person_repair")})
    if n5: wc[len((uf or "").split())] += 1
dropped = collections.Counter(d.get("stage") for d in doc.get("dropped") or [])
metas = [m for a in g.get("attempts") or [] for m in a.get("llm_calls") or []]
models = collections.defaultdict(set); versions = collections.defaultdict(set)
for m in metas:
    models[m["stage"]].add(m.get("model_id")); versions[m["stage"]].add(str(m.get("model_version")))
l1 = [x for a in g.get("attempts") or [] for x in a.get("l1") or []]
pool_rej = collections.Counter(); pool_rej_reason = collections.Counter()
for x in l1:
    for r in (json.loads(x["pool_rejected"]) if isinstance(x.get("pool_rejected"), str) else (x.get("pool_rejected") or [])):
        pool_rej[r.get("stage")] += 1; pool_rej_reason[(r.get("reasons") or [""])[0][:40]] += 1
l3 = [x for a in g.get("attempts") or [] for x in a.get("l3") or []]
pr = [x for a in g.get("attempts") or [] for x in a.get("person_repair") or []]
import er053_cost_aggregate_01 as agg
cost = agg.compute_stage_cost_breakdown_multi(clog) if os.path.exists(clog) else None
out = {"route": label, "level": level, "method": g.get("method"), "models_requested": g.get("models_requested"), "prompt_sha16": g.get("prompt_sha16"),
       "wordnet_sha256": g.get("wordnet_sha256"), "n_candidates": len(cands), "n_n5": sum(1 for r in rows if r["n5"]), "word_count_dist_n5": dict(wc),
       "actual_model_ids_by_stage": {k: sorted(v) for k, v in models.items()}, "model_versions_by_stage": {k: sorted(v) for k, v in versions.items()},
       "dropped_by_stage": dict(dropped), "pool_rejected_by_stage": dict(pool_rej), "pool_rejected_by_reason": dict(pool_rej_reason),
       "l1": [{k: x.get(k) for k in ("include_b1", "n_p7_in", "n_b1_returned", "pool_size", "n_judged", "n_keep", "n_picked", "picked_origin", "pool_rejected_by_reason")} for x in l1],
       "l3_summaries": [x.get("summary") for x in l3], "person_repair": pr, "backfill": {k: (doc.get("backfill") or {}).get(k) for k in ("status", "n_added", "n_requested", "rounds", "triggered")} if doc.get("backfill") else None,
       "backfill_raw_keys": list((doc.get("backfill") or {}).keys()), "presentable_filter": doc.get("presentable_filter"), "shortfall": doc.get("shortfall"),
       "n_llm_calls": len(metas), "n_truncation_retries": sum(1 for m in metas if m.get("json_ok") is False), "cost": cost, "rows": rows}
json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(label, level, "cands", len(cands), "n5", out["n_n5"], "wc", dict(wc), "drops", dict(dropped), "models", out["actual_model_ids_by_stage"], "ver", out["model_versions_by_stage"])
print(" bad consistency:", [r["source_span"] for r in rows if r["n5"] and (not r["used_eq_key_eq_n5"] or not r["gloss_eq_n5"] or r["source_span_in_text"] is False)], " gloss_status:", dict(collections.Counter(r["gloss_alignment_status"] for r in rows)))
