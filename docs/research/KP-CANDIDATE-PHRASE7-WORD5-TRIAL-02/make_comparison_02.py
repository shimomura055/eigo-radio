# -*- coding: utf-8 -*-
"""trial_runs_02.json から COMPARISON_02.md の表部分(数値のみ。判断文は含めない)を stdout へ出す。"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "trial_runs_02.json"), encoding="utf-8"))
LV = D["levels"]
TRACK = ["performance", "audience", "responsibility", "discovery", "strategy", "technique", "carriage", "automatically"]


def c(rows, kind=None, f=None, v=None):
    return sum(1 for x in rows if (kind is None or x["kind"] == kind) and (f is None or x[f] == v))


def forms(rows, kind):
    return [x["used_form"] for x in rows if x["kind"] == kind]


def stat(rows):
    ph = [x for x in rows if x["kind"] == "phrase"]
    wd = [x for x in rows if x["kind"] == "word"]
    return {"ph": len(ph), "wd": len(wd), "phY": c(ph, f="own", v="Y"), "phB": c(ph, f="own", v="B"), "phN": c(ph, f="own", v="N"),
            "wY": c(wd, f="own", v="Y"), "wB": c(wd, f="own", v="B"), "wN": c(wd, f="own", v="N"),
            "wJY": c(wd, f="judge", v="Y"), "wJB": c(wd, f="judge", v="B"), "wJN": c(wd, f="judge", v="N"),
            "adv_ok": c(wd, f="adv_fit", v="適合"), "adv_mid": c(wd, f="adv_fit", v="境界"), "adv_ng": c(wd, f="adv_fit", v="不適合")}


print("## A. レベル別(件数・Y/B/N)")
print("| level | 方式 | フレーズ | 単語 | 計 | フレーズ自Y/B/N | 単語自Y/B/N | 単語judge Y/B/N | ③④適合/境界/不適合 | 費用¥ | 秒 |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
T = {"cur": [], "w3": [], "w5": []}
for k, v in LV.items():
    for name, rows, cost, sec in (("現行", v["current_final"], None, None), ("前回P7+W3 r1", v["w3_r1_final"], v["w3_r1_cost"]["jpy"], v["w3_r1_elapsed_sec"]),
                                  ("今回P7+W5", v["w5_final"], v["cost"]["jpy"], v["elapsed_sec"])):
        s = stat(rows)
        T[{"現行": "cur", "前回P7+W3 r1": "w3", "今回P7+W5": "w5"}[name]].append(s)
        print(f"| {k} | {name} | {s['ph']} | {s['wd']} | {s['ph']+s['wd']} | {s['phY']}/{s['phB']}/{s['phN']} | {s['wY']}/{s['wB']}/{s['wN']} | {s['wJY']}/{s['wJB']}/{s['wJN']} | {s['adv_ok']}/{s['adv_mid']}/{s['adv_ng']} | {cost if cost is not None else '—'} | {sec if sec is not None else '—'} |")

print("\n## B. 総括(6 level合計)")
print("| 項目 | 現行 | 前回P7+W3 r1 | 今回P7+W5 |")
print("|---|---|---|---|")
rows_out = []
for lab, fn in (("フレーズ件数", lambda s: s["ph"]), ("単語件数", lambda s: s["wd"]), ("総件数", lambda s: s["ph"] + s["wd"]),
                ("フレーズ 自Y", lambda s: s["phY"]), ("フレーズ 自B", lambda s: s["phB"]), ("フレーズ 自N", lambda s: s["phN"]),
                ("単語 自Y", lambda s: s["wY"]), ("単語 自B", lambda s: s["wB"]), ("単語 自N", lambda s: s["wN"]),
                ("単語 judge Y", lambda s: s["wJY"]), ("単語 judge N", lambda s: s["wJN"]),
                ("単語 ③④適合", lambda s: s["adv_ok"]), ("単語 ③④境界(基本寄り)", lambda s: s["adv_mid"]), ("単語 ③④不適合(易しい語)", lambda s: s["adv_ng"])):
    print(f"| {lab} | {sum(fn(s) for s in T['cur'])} | {sum(fn(s) for s in T['w3'])} | {sum(fn(s) for s in T['w5'])} |")
print("単語Y(自)≥3件のlevel数: 現行 %d / W3 %d / W5 %d" % tuple(sum(1 for s in T[n] if s["wY"] >= 3) for n in ("cur", "w3", "w5")))
print("単語Y(自)≥1件のlevel数: 現行 %d / W3 %d / W5 %d" % tuple(sum(1 for s in T[n] if s["wY"] >= 1) for n in ("cur", "w3", "w5")))
tw3, tw5 = sum(s["wd"] for s in T["w3"]), sum(s["wd"] for s in T["w5"])
print("自N(単語)割合 W3 %d/%d W5 %d/%d; 易語(境界+不適合)割合 W3 %d/%d W5 %d/%d; 自Y割合 W3 %d/%d W5 %d/%d" % (
    sum(s["wN"] for s in T["w3"]), tw3, sum(s["wN"] for s in T["w5"]), tw5,
    sum(s["adv_mid"] + s["adv_ng"] for s in T["w3"]), tw3, sum(s["adv_mid"] + s["adv_ng"] for s in T["w5"]), tw5,
    sum(s["wY"] for s in T["w3"]), tw3, sum(s["wY"] for s in T["w5"]), tw5))
print("全体(フレーズ+単語)自Y 現行/W3/W5:", [sum(s["phY"] + s["wY"] for s in T[n]) for n in ("cur", "w3", "w5")],
      " 自N:", [sum(s["phN"] + s["wN"] for s in T[n]) for n in ("cur", "w3", "w5")], " 総件数:", [sum(s["ph"] + s["wd"] for s in T[n]) for n in ("cur", "w3", "w5")])

print("\n## C. 単語側 W3 r1 vs W5(level別・順位順)")
for k, v in LV.items():
    w3 = [(x["used_form"], x["own"], x["adv_fit"]) for x in v["w3_r1_final"] if x["kind"] == "word"]
    w5 = [(x["used_form"], x["own"], x["adv_fit"]) for x in v["w5_final"] if x["kind"] == "word"]
    print(f"- {k}: W3 r1 = {w3}\n    W5 = {w5}\n    W5返答(生) = {v['w5_raw_phrases']}  / 返答→最終: {v['w5_returned']}→{len(w5)}")

print("\n## D. 前回易語の扱い(W5での出現)")
for tr in TRACK:
    P1R = json.load(open(os.path.join(HERE, "..", "KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01", "trial_runs_01.json"), encoding="utf-8"))["runs"]
    prevhit = [(t_, x["used_form"], x["ai_rank"]) for t_, r_ in P1R.items() if "p7w3" in t_ for x in r_["candidates"] if x["kind"] == "word" and x["used_form"].lower() == tr]
    newhit = [(k, x["used_form"], x["rank"], x["own"], x["adv_fit"]) for k, v in LV.items() for x in v["w5_final"] if x["kind"] == "word" and x["used_form"].lower() == tr]
    rawhit = [(k, v["w5_raw_phrases"].index(next(p for p in v["w5_raw_phrases"] if p.lower() == tr)) + 1) for k, v in LV.items() if tr in [p.lower() for p in v["w5_raw_phrases"]]]
    print(f"- {tr}: 前回W3(r1+r2)出現={prevhit} / W5最終出現={newhit} / W5生返答内順位={rawhit}")

print("\n## E. フレーズ側 W3 r1 vs W5(同一P7返答。差はcanonicalization等の再実行のみ)")
for k, v in LV.items():
    a, b = forms(v["w3_r1_final"], "phrase"), forms(v["w5_final"], "phrase")
    print(f"- {k}: W3 r1={a}\n    W5    ={b}\n    差: -{[x for x in a if x not in b]} +{[x for x in b if x not in a]}")

print("\n## F. Gate除外(全件)")
for k, v in LV.items():
    for d in v["p7_dropped"] + (v["doc_dropped"] or []):
        print(f"- {k}: [{d.get('origin')}] {d['phrase']} stage={d['stage']} {d['reasons']}")

print("\n## G. 費用・時間")
rc, jc = D["run_cost"], D["judge_cost"]
w3c = sum(v["w3_r1_cost"]["jpy"] for v in LV.values())
w3calls = sum(v["w3_r1_cost"]["calls"] for v in LV.values())
print(f"今回run: {rc['calls']} call ¥{rc['jpy']} (平均/level ¥{round(rc['jpy']/6,3)}, {round(rc['calls']/6,2)} call)  judge: {jc['calls']} call ¥{jc['jpy']}")
print(f"前回W3 r1 6 run: {w3calls} call ¥{round(w3c,3)} (平均/level ¥{round(w3c/6,3)}, {round(w3calls/6,2)} call)")
print("elapsed 今回平均 %.1f秒 / 前回r1平均 %.1f秒" % (sum(v["elapsed_sec"] for v in LV.values()) / 6, sum(v["w3_r1_elapsed_sec"] or 0 for v in LV.values()) / 6))
print("RQA:", {k: v["redundancy_qa"] for k, v in LV.items()})
