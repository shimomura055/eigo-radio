# -*- coding: utf-8 -*-
import json, os, sys, argparse, concurrent.futures as cf
import kpg01_llm as L, kpg01_methods2 as M, kpg01_methods3 as M3
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "kpg01_work", "results"); os.makedirs(RES, exist_ok=True)
corpus = {c["id"]: c for c in json.load(open(os.path.join(HERE, "kpg01_work", "corpus.json"), encoding="utf-8"))}
for _cid, _c in corpus.items():
    _p = os.path.join(HERE, "kpg01_work", "before_replica", _cid, "before_replica.json")
    if _c["before"] is None and os.path.exists(_p):
        _its = json.load(open(_p, encoding="utf-8"))["items"]
        if _its: _c["before"] = {"candidates": _its}
METHODS = {
    "A_luna": lambda c: M.run_A(c, model="gpt-6-luna", tag="A_luna"),
    "A_sol": lambda c: M.run_A(c, model="gpt-6.1-sol", effort="low", tag="A_sol"),
    "B_luna": lambda c: M.run_B(c, tag="B_luna"),
    "B_mix": lambda c: M.run_B(c, m_rank="gpt-6.1-sol", m_gen="gpt-6.1-sol", eff_rank="low", eff_gen="low", tag="B_mix"),
    "A2_sol": lambda c: M.run_A2(c, model="gpt-6.1-sol", effort="low", tag="A2_sol"),
    "A2_luna": lambda c: M.run_A2(c, model="gpt-6-luna", effort=None, tag="A2_luna"),
    "C2_sol": lambda c: M.run_C2(c, tag="C2_sol"),
    "C2_sol_nov": lambda c: M.run_C2(c, tag="C2_sol_nov", do_verify=False),
    "C2_luna": lambda c: M.run_C2(c, m_rg="gpt-6-luna", eff=None, tag="C2_luna"),
    "C3_luna": lambda c: M.run_C3(c, tag="C3_luna"),
    "C3_sol": lambda c: M.run_C3(c, m_rg="gpt-6.1-sol", eff="low", tag="C3_sol"),
    "D_luna": lambda c: M3.run_D(c, tag="D_luna"),
    "D_sol": lambda c: M3.run_D(c, m_sel="gpt-6.1-sol", eff_sel="low", tag="D_sol"),
    "D1_luna": lambda c: M3.run_D(c, source="p7", tag="D1_luna"),
    "C1_luna": lambda c: M.run_B(c, cands_override=M.prod_p7_cands(c), tag="C1_luna"),
    "C1_mix": lambda c: M.run_B(c, cands_override=M.prod_p7_cands(c), m_rank="gpt-6.1-sol", m_gen="gpt-6.1-sol", eff_rank="low", eff_gen="low", tag="C1_mix"),
}
def do(cid, mname):
    c = corpus[cid]
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
                r = f.result(); print(f"{c} {m}: {len(r['items'])} items, ¥{r['cost_jpy']}, {r['sec']}s")
            except Exception as e:
                print(f"{c} {m}: ERR {type(e).__name__} {str(e)[:200]}")
    print("TOTAL ¥", round(L.total_cost(), 2))
