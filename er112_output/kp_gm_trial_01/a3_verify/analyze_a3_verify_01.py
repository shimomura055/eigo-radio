# -*- coding: utf-8 -*-
import json, glob, sys, collections
from pathlib import Path
ROOT = Path(r"C:\Users\tensh\eigo-radio"); sys.path.insert(0, str(ROOT))
import er112_kp_gm_judge_01 as jd
V = ROOT / "er112_output/kp_gm_trial_01/a3_verify"
C = {j: jd.load_cache(j) for j in ("sonnet", "sol")}
rows = []
# new normal set
for f in glob.glob(str(V / "runs" / "*" / "*" / "*.json")):
    d = json.load(open(f, encoding="utf-8"))
    for it in d["items"]:
        e = (d["expl"] or {}).get(str(it["rank"]))
        if e: rows.append(dict(set="new25", arm=d["arm"], rep=d["rep"], key=it["key_phrase"], sent=it["source_sentence"], text=e["text"], status=e["status"]))
# reused hard set
for r in json.load(open(V / "reuse_rows_01.json", encoding="utf-8")):
    if r["hard"]: rows.append(dict(set="hard14", arm=r["arm"], rep=r["rep"], key=r["key"], sent=r["sent"], text=r["text"] if "text" in r else r["expl"], status="OK"))
for r in rows:
    rid = jd.rid("E2", r["key"], r["sent"], r["text"])
    for j in C:
        v = C[j].get(rid); r[j] = v["verdict"] if v else None
    assert r["sonnet"] and r["sol"], r
def ok(v): return v["sense_ok"] == 1 and v["core"] == 1 and v["single"] == 1
for r in rows:
    r["p_son"] = ok(r["sonnet"]); r["p_sol"] = ok(r["sol"]); r["p_both"] = r["p_son"] and r["p_sol"]; r["p_any"] = r["p_son"] or r["p_sol"]
    r["sense_both"] = r["sonnet"]["sense_ok"] == 1 and r["sol"]["sense_ok"] == 1
    r["core_both"] = r["sonnet"]["core"] == 1 and r["sol"]["core"] == 1
    r["single_both"] = r["sonnet"]["single"] == 1 and r["sol"]["single"] == 1
    r["words"] = len(r["text"].split())
json.dump(rows, open(V / "all_rows_judged_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def rate(rs, f): return f"{sum(1 for r in rs if r[f])}/{len(rs)} ({100*sum(1 for r in rs if r[f])/max(len(rs),1):.0f}%)"
print("== arm別 rate ==")
for s in ("new25", "hard14", "ALL"):
    for arm in ("a1gE0", "a1gE3"):
        rs = [r for r in rows if (s == "ALL" or r["set"] == s) and r["arm"] == arm]
        print(f"{s:7s} {arm}: n={len(rs)} PASS(両Judge)={rate(rs,'p_both')} PASS(sonnet)={rate(rs,'p_son')} PASS(sol)={rate(rs,'p_sol')} sense_ok両={rate(rs,'sense_both')} core両={rate(rs,'core_both')} single両={rate(rs,'single_both')} avg_words={sum(r['words'] for r in rs)/len(rs):.1f}")
# per KP classification
by = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows: by[(r["set"], r["key"], r["sent"])][r["arm"]].append(r)
cls = {}
def cnt(rs, f): return sum(1 for r in rs if r[f])
for k, d in by.items():
    e0, e3 = d["a1gE0"], d["a1gE3"]
    n0, n3 = len(e0), len(e3)
    # 比率で比較(rep数差を吸収)
    def diff(f): return cnt(e3, f) / n3 - cnt(e0, f) / n0
    ds, dl, db = diff("p_son"), diff("p_sol"), diff("p_both")
    if ds * dl < 0: c = "判断分かれ"
    elif db > 0.2 or (ds + dl) > 0.2 and min(ds, dl) >= 0: c = "改善"
    elif db < -0.2 or (ds + dl) < -0.2 and max(ds, dl) <= 0: c = "悪化"
    else: c = "維持"
    cls[k] = dict(cls=c, ds=round(ds, 2), dl=round(dl, 2), db=round(db, 2), pass0=f"{cnt(e0,'p_both')}/{n0}", pass3=f"{cnt(e3,'p_both')}/{n3}",
                  sense0=f"{cnt(e0,'sense_both')}/{n0}", sense3=f"{cnt(e3,'sense_both')}/{n3}")
json.dump({f"{k[0]}|{k[1]}": v for k, v in cls.items()}, open(V / "kp_classification_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for s in ("new25", "hard14", "ALL"):
    cc = collections.Counter(v["cls"] for k, v in cls.items() if s == "ALL" or k[0] == s)
    print(s, dict(cc), "n_kp", sum(cc.values()))
print("== 詳細 ==")
for k, d in sorted(by.items(), key=lambda x: (x[0][0], cls[x[0]]["cls"], x[0][1])):
    c = cls[k]
    print(f"\n[{k[0]}] {k[1]} => {c['cls']} E0pass={c['pass0']} E3pass={c['pass3']} sense E0={c['sense0']} E3={c['sense3']} (dSon={c['ds']},dSol={c['dl']})\n  SENT: {k[2]}")
    for arm in ("a1gE0", "a1gE3"):
        for r in sorted(d[arm], key=lambda x: x["rep"]):
            s_, l_ = r["sonnet"], r["sol"]
            print(f"  {arm[-2:]} r{r['rep']} son={s_['sense_ok']}{s_['core']}{s_['single']} sol={l_['sense_ok']}{l_['core']}{l_['single']} | {r['text']}" + (f"  ##son:{s_['note']}" if s_.get('note') else "") + (f"  ##sol:{l_['note']}" if l_.get('note') else ""))
