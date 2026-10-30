# -*- coding: utf-8 -*-
"""方式N1a/N1/N2/N4/N5の実行(記事case)と検証ケース(probe)の実行。--mockでAPI 0のdry-run(結果はkpg04_work/mock_results)。
KPG4_CAP未設定(既定0)では有料callは全て拒否(CapReached、rc=3)。Capはkpg04_llm.CAP(環境変数KPG4_CAP。Fableが委任_02で確定)。
--phase-cap=その起動での新規費用の上限(停止点)。再起動・再試行ラッパは作らない。CapReachedで停止したら実行を終えFableへ報告する。
使い方(委任_02): KPG4_CAP=<Fable確定額> PYTHONUTF8=1 .venv\\Scripts\\python.exe kpg04_run.py --probes P0,P1,P2 --phase-cap 12
                  KPG4_CAP=<額> ... kpg04_run.py --cases ALL14 --arms N1,N2 --phase-cap 40"""
import os, sys, json, argparse, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L

OLD1 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
ALL14 = ["untidi_a2", "ai_cha_b1b", "jwst_m_a2", "jwst_m_b1b", "meta_w_b1b", "untidi_b1b", "ai_cha_a2", "meta_w_a2", "aiisland_b1b", "surname_b1b", "melos_a2",
         "ignobel_a2", "ignobel_b1b", "tesla_b1b"]
HELDOUT = ["aiisland_a2", "moon_a2", "moon_b1b", "surname_a2", "melos_b1b", "tesla_a2"]       # TRIAL-01/02のどのarmでも未実行の記事レベル
HARD6 = ["untidi_a2", "ai_cha_b1b", "jwst_m_a2", "jwst_m_b1b", "meta_w_b1b", "untidi_b1b"]


def load_corpus():
    corpus = {c["id"]: c for c in json.load(open(os.path.join(OLD1, "kpg01_work", "corpus.json"), encoding="utf-8"))}
    for cid, c in corpus.items():
        p = os.path.join(OLD1, "kpg01_work", "before_replica", cid, "before_replica.json")
        if c["before"] is None and os.path.exists(p):
            its = json.load(open(p, encoding="utf-8"))["items"]
            if its:
                c["before"] = {"candidates": its}
    return corpus


def res_dir(mock, sub="results"):
    d = os.path.join(L.WORK, "mock_results" if mock else sub); os.makedirs(d, exist_ok=True)
    return d


def do_case(corpus, cid, arm, mock, suffix=""):
    import kpg04_methods as M
    r = M.ARMS[arm](corpus[cid])
    r["case"], r["arm"] = cid, arm + suffix
    r["cost_jpy"] = round(sum(s["cost_jpy"] for s in r["log"]["stages"]), 3)
    r["sec"] = round(sum(s["sec"] for s in r["log"]["stages"]), 1)
    json.dump(r, open(os.path.join(res_dir(mock), f"{cid}__{arm}{suffix}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return r


def do_probe(cfg, mock, suffix=""):
    import kpg04_methods as M
    probes = [p for p in json.load(open(os.path.join(HERE, "kpg04_probes.json"), encoding="utf-8")) if p["type"] != "FREE_COMBINATION"]
    r = M.run_probe(cfg, probes)
    for it in r["items"]:
        pr = next(p for p in probes if p["id"] == it["probe_id"])
        it["score"] = M.score_probe(it, pr)
    r["cost_jpy"] = round(sum(s["cost_jpy"] for s in r["log"]["stages"]), 3)
    json.dump(r, open(os.path.join(res_dir(mock, "probe_results"), f"probes__{cfg}{suffix}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", help="カンマ区切り、またはグループ名 ALL14/HELDOUT/HARD6")
    ap.add_argument("--arms", help="N1a,N1,N2,N4,N5")
    ap.add_argument("--probes", help="P0,P1,P2,P4,P5(検証ケース48件から自由な組合せ6件を除く42件)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--phase-cap", type=float, default=0, help="この起動の新規費用上限(円)")
    ap.add_argument("--suffix", default="", help="再実行ばらつき用(例 _r2)。KPG_SALTも併せて設定すること")
    a = ap.parse_args()
    L.set_mock(a.mock)
    if a.phase_cap and not a.mock:
        L.set_phase_cap(a.phase_cap)
    stop = False
    jobs = []
    if a.arms:
        cases = {"ALL14": ALL14, "HELDOUT": HELDOUT, "HARD6": HARD6}.get(a.cases) or a.cases.split(",")
        corpus = load_corpus()
        jobs += [("case", (corpus, c, m, a.mock, a.suffix)) for c in cases for m in a.arms.split(",")]
    if a.probes:
        jobs += [("probe", (m, a.mock, a.suffix)) for m in a.probes.split(",")]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(do_case if k == "case" else do_probe, *args): (k, args) for k, args in jobs}
        for f in cf.as_completed(futs):
            k, args = futs[f]
            name = f"{args[1]} {args[2]}" if k == "case" else f"probes {args[0]}"
            try:
                r = f.result()
                print(f"{name}: {len(r['items'])} items, ¥{r['cost_jpy']}", flush=True)
            except L.CapReached as e:
                stop = True
                print(f"{name}: CAP_REACHED {e}", flush=True)
            except Exception as e:
                print(f"{name}: ERR {type(e).__name__} {str(e)[:300]}", flush=True)
    print(("MOCK " if a.mock else "") + "TOTAL ¥(kpg04 ledger)", round(L.total_cost(), 2), "CAP_REACHED" if stop else "")
    sys.exit(3 if stop else 0)
