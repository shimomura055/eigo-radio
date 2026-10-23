# A-3 v3 追加検証 Step1: 既存Trialデータの再集計(API 0)
import sys, json, collections
sys.path.insert(0, r"C:\Users\tensh\eigo-radio")
import er112_kp_gm_eval_01 as ev
import er112_kp_gm_judge_01 as jd
res = ev.load_results()
caches = {j: jd.load_cache(j) for j in ("sonnet", "sol")}
rows = []
for (arm, rep, uid), r in res.items():
    if arm not in ("a1gE0", "a1gE3"): continue
    for it in r.get("items") or []:
        e = (r.get("expl") or {}).get(str(it["rank"])) or {}
        if not e.get("text"): continue
        key, sent = it["key_phrase"], it.get("source_sentence") or ""
        hard = it["display_phrase"].lower() in ev.HARD
        out = dict(arm=arm, rep=rep, unit=uid, rank=it["rank"], key=key, sent=sent, expl=e["text"], hard=hard)
        for kind in ("E", "E2"):
            rid = jd.rid(kind, key, sent, e["text"])
            for j in caches:
                v = caches[j].get(rid)
                out[f"{kind}_{j}"] = v["verdict"] if v else None
        rows.append(out)
json.dump(rows, open(r"C:\Users\tensh\eigo-radio\er112_output\kp_gm_trial_01\a3_verify\reuse_rows_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rows), collections.Counter((r["arm"], r["hard"]) for r in rows))
print("missing E2 judged:", sum(1 for r in rows if r["E2_sol"] is None or r["E2_sonnet"] is None), "missing E:", sum(1 for r in rows if r["E_sol"] is None or r["E_sonnet"] is None))
print(len({r["key"] for r in rows}))
