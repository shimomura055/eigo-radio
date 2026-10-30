# -*- coding: utf-8 -*-
"""方式E1L/E1S/E2/E3/E4の実行。--mockでAPI 0のdry-run(結果はkpg03_work/mock_results)。
使い方(委任_02): PYTHONUTF8=1 .venv\\Scripts\\python.exe kpg03_run.py --cases untidi_a2,... --arms E1L,E2,E3 --phase-cap 55
Capはkpg03_llm.CAP(¥120、環境変数KPG3_CAPで下げることのみ可)。--phase-cap=その起動での新規費用の上限(停止点)。
再起動・再試行ラッパは作らない。CapReachedで停止したら実行を終えFableへ報告する。"""
import os, sys, json, argparse, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg03_llm as L

OLD = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
GROUPS = {"A": ["untidi_a2", "ai_cha_b1b", "jwst_m_a2", "jwst_m_b1b", "meta_w_b1b", "untidi_b1b"],        # Phase A(失敗例を含む6ケース)
          "B": ["ai_cha_a2", "meta_w_a2", "aiisland_b1b", "surname_b1b", "melos_a2", "ignobel_a2", "ignobel_b1b", "tesla_b1b"],
          "C": ["moon_a2", "moon_b1b", "melos_b1b"]}
ALL14 = GROUPS["A"] + GROUPS["B"]


def load_corpus():
    corpus = {c["id"]: c for c in json.load(open(os.path.join(OLD, "kpg01_work", "corpus.json"), encoding="utf-8"))}
    for cid, c in corpus.items():
        p = os.path.join(OLD, "kpg01_work", "before_replica", cid, "before_replica.json")
        if c["before"] is None and os.path.exists(p):
            its = json.load(open(p, encoding="utf-8"))["items"]
            if its:
                c["before"] = {"candidates": its}
    return corpus


def res_dir(mock):
    d = os.path.join(L.WORK, "mock_results" if mock else "results"); os.makedirs(d, exist_ok=True)
    return d


def do(corpus, cid, arm, mock, suffix=""):
    import kpg03_methods as M
    r = M.ARMS[arm](corpus[cid])
    r["case"], r["arm"] = cid, arm + suffix
    r["cost_jpy"] = round(sum(s["cost_jpy"] for s in r["log"]["stages"]), 3)
    r["sec"] = round(sum(s["sec"] for s in r["log"]["stages"]), 1)
    json.dump(r, open(os.path.join(res_dir(mock), f"{cid}__{arm}{suffix}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", help="カンマ区切り、またはグループ名 A/B/C/ALL14")
    ap.add_argument("--arms", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--phase-cap", type=float, default=0, help="この起動の新規費用上限(円)")
    ap.add_argument("--suffix", default="", help="再実行ばらつき用(例 _r2)。KPG_SALTも併せて設定すること")
    a = ap.parse_args()
    L.set_mock(a.mock)
    if a.phase_cap and not a.mock:
        L.set_phase_cap(a.phase_cap)
    cs = a.cases
    cases = GROUPS.get(cs) or (ALL14 if cs == "ALL14" else cs.split(","))
    corpus = load_corpus()
    jobs = [(c, m) for c in cases for m in a.arms.split(",")]
    stop = False
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(do, corpus, c, m, a.mock, a.suffix): (c, m) for c, m in jobs}
        for f in cf.as_completed(futs):
            c, m = futs[f]
            try:
                r = f.result()
                print(f"{c} {m}: {len(r['items'])} items, ¥{r['cost_jpy']}, {r['sec']}s", flush=True)
            except L.CapReached as e:
                stop = True
                print(f"{c} {m}: CAP_REACHED {e}", flush=True)
            except Exception as e:
                print(f"{c} {m}: ERR {type(e).__name__} {str(e)[:300]}", flush=True)
    print(("MOCK " if a.mock else "") + "TOTAL ¥(kpg03 ledger)", round(L.total_cost(), 2), "CAP_REACHED" if stop else "")
    sys.exit(3 if stop else 0)
