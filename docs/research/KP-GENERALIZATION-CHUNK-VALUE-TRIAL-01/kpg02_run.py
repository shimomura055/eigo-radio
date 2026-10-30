# -*- coding: utf-8 -*-
import json, os, sys, argparse, concurrent.futures as cf
import kpg01_llm as L1
import kpg02_llm as L
L1.LEDGER = L.LEDGER   # kpg01系のcallも費用はkpg02 ledgerへ
import kpg01_methods2 as M
import kpg01_methods3 as M3
import kpg02_methods as M2
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "kpg02_work", "results"); os.makedirs(RES, exist_ok=True)
corpus = {c["id"]: c for c in json.load(open(os.path.join(HERE, "kpg01_work", "corpus.json"), encoding="utf-8"))}
for _cid, _c in corpus.items():
    _p = os.path.join(HERE, "kpg01_work", "before_replica", _cid, "before_replica.json")
    if _c["before"] is None and os.path.exists(_p):
        _its = json.load(open(_p, encoding="utf-8"))["items"]
        if _its: _c["before"] = {"candidates": _its}
METHODS = {
    "D2_luna": lambda c: M2.run_D2(c, tag="D2_luna"),
    "D2_luna_r2": lambda c: M2.run_D2(c, tag="D2_luna_r2"),      # 再実行ばらつき用(同一入力。cacheを使わない)
    "D2_sol": lambda c: M2.run_D2(c, m_sel="gpt-6.1-sol", eff_sel="low", tag="D2_sol"),
    "A_luna": lambda c: M.run_A(c, model="gpt-6-luna", tag="A_luna"),
    "D_luna": lambda c: M3.run_D(c, tag="D_luna"),
}
def do(cid, mname, nocache=False):
    c = corpus[cid]
    if nocache: L.USE_NOCACHE = True
    r = METHODS[mname](c)
    r["case"] = cid; r["method"] = mname
    r["cost_jpy"] = round(sum(s["cost_jpy"] for s in r["log"]["stages"]), 3)
    r["sec"] = round(sum(s["sec"] for s in r["log"]["stages"]), 1)
    json.dump(r, open(os.path.join(RES, f"{cid}__{mname}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return r
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--cases"); ap.add_argument("--methods"); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    jobs = [(c, m) for c in a.cases.split(",") for m in a.methods.split(",")]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(do, c, m): (c, m) for c, m in jobs}
        for f in cf.as_completed(futs):
            c, m = futs[f]
            try:
                r = f.result(); print(f"{c} {m}: {len(r['items'])} items (+alt {len(r.get('alt_items', []))}), ¥{r['cost_jpy']}, {r['sec']}s", flush=True)
            except Exception as e:
                print(f"{c} {m}: ERR {type(e).__name__} {str(e)[:300]}", flush=True)
    print("TOTAL ¥(kpg02 ledger)", round(L.total_cost(), 2))
