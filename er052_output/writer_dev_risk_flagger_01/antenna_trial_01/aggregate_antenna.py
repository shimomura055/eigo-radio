# -*- coding: utf-8 -*-
"""Phase 3 集計(API呼び出し0)。MATCHING_RULE_01.md の規則だけを実装。出力: aggregate_antenna_01.json"""
import json, glob, re, statistics, os
sys_dont = True
HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = ["streaming_price", "space_weapons", "byd_recall"]
MODELS = ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"]
KNOWN = [("C01","streaming_price","gpt-6-luna","s16","Disney+"),("C02","streaming_price","gpt-6-luna","s17","Disney+"),
         ("C03","streaming_price","gpt-6-luna","s18","Disney+"),("C04","streaming_price","gpt-6.1-sol","s7","Disney+"),
         ("C05","space_weapons","gpt-6.1-sol","s6","宇宙兵器"),("C06","space_weapons","gpt-6-astra","s19","宇宙兵器"),
         ("C07","byd_recall","gpt-6-luna","s6","BYD"),("C08","byd_recall","gpt-6-luna","s7","BYD"),
         ("S1","byd_recall","gpt-6-luna","s4","BYD(制動灯)"),("S2","byd_recall","gpt-6-luna","s12","BYD(制動灯)")]
norm = lambda s: re.sub(r"[\s、。,.，．「」『』・!?！？]", "", s)
cells = {}
unid = []
for L in range(1, 7):
    for th in THEMES:
        for m in MODELS:
            d = json.load(open(os.path.join(HERE, "flags", "A%d" % L, th, m + ".json"), encoding="utf-8"))
            cells[(L, th, m)] = d
            for x in d["flags"]:
                sid = x.get("sentence_id")
                if sid not in d["sentences"] or norm(d["sentences"][sid]) != norm(x.get("sentence", "")):
                    unid.append((L, th, m, sid))
# flags by level -> dict key -> list of flags
lv = {L: {} for L in range(1, 7)}
for (L, th, m), d in cells.items():
    for x in d["flags"]:
        lv[L].setdefault((th, m, x["sentence_id"]), []).append(x)
def info(L, k):
    fl = lv[L][k]
    return dict(types=sorted({f["type"] for f in fl}), conf=max(f["confidence"] for f in fl), n_flags=len(fl))
levels = {}
for L in range(1, 7):
    flags = [x for (l, th, m), d in cells.items() if l == L for x in d["flags"]]
    confs = [x["confidence"] for x in flags]
    arts = {(th, m) for (th, m, s) in lv[L]}
    per = {th: {m: sum(len(v) for k, v in lv[L].items() if k[0] == th and k[1] == m) for m in MODELS} for th in THEMES}
    types = {}
    for x in flags: types[x["type"]] = types.get(x["type"], 0) + 1
    levels[L] = dict(n_articles=len(arts), n_flags=len(flags), n_unique_sentences=len(lv[L]), per_article=per, types=types,
                     conf=dict(min=min(confs), max=max(confs), mean=round(statistics.mean(confs), 3), median=statistics.median(confs)) if confs else None,
                     high_conf_ge_0_5=sum(1 for c in confs if c >= 0.5))
known_keys = {(th, m, s): (cid, grp) for cid, th, m, s, grp in KNOWN}
trans = {}
cum = set()
for L in range(1, 6):
    a, b = set(lv[L]), set(lv[L + 1])
    kept, lost, new = sorted(a & b), sorted(a - b), sorted(b - a)
    tchg = [k for k in kept if set(info(L, k)["types"]) != set(info(L + 1, k)["types"])]
    imp = [k for k in lost if k in known_keys or info(L, k)["conf"] >= 0.5]
    trans["A%d->A%d" % (L, L + 1)] = dict(kept=kept, lost=lost, new=new, type_changed_in_kept=tchg, important_lost=imp)
cumul = {}
u = set()
for L in range(1, 7):
    u |= set(lv[L]); cumul[L] = dict(cumulative_union=len(u), present_now=len(lv[L]), union_not_present_now=sorted(u - set(lv[L])))
kn = []
for cid, th, m, s, grp in KNOWN:
    k = (th, m, s)
    pres = [k in lv[L] for L in range(1, 7)]
    first = next((i + 1 for i, p in enumerate(pres) if p), None)
    cont = None if first is None else all(pres[first - 1:])
    kn.append(dict(id=cid, group=grp, theme=th, model=m, sid=s, present=pres, first=first, continuous=cont,
                   sentence=cells[(1, th, m)]["sentences"][s],
                   confs=[info(L, k)["conf"] if k in lv[L] else None for L in range(1, 7)]))
# first-appearance level of every flagged sentence and persistence
allkeys = sorted(set().union(*[set(lv[L]) for L in lv]))
rows = []
for k in allkeys:
    pres = [k in lv[L] for L in range(1, 7)]
    first = pres.index(True) + 1
    rows.append(dict(key=list(k), present=pres, first=first, continuous=all(pres[first - 1:]), known=known_keys.get(k, [None])[0],
                     confs=[info(L, k)["conf"] if k in lv[L] else None for L in range(1, 7)],
                     types=[info(L, k)["types"] if k in lv[L] else None for L in range(1, 7)]))
cost = [json.loads(l) for l in open(os.path.join(HERE, "cost_ledger_antenna_01.jsonl"), encoding="utf-8")]
cl = {}
for r in cost:
    L = int(re.match(r"ant(\d)_", r["set"]).group(1)); c = cl.setdefault(L, dict(calls=0, jpy=0.0, inp=0, out=0, reas=0))
    c["calls"] += 1; c["jpy"] += r["cost_jpy"]; c["inp"] += r["usage"]["input_tokens"]; c["out"] += r["usage"]["output_tokens"]; c["reas"] += r["usage"].get("reasoning_tokens", 0)
out = dict(levels=levels, transitions=trans, cumulative=cumul, known=kn, rows=rows, unidentified_sentence=unid, cost_by_level=cl,
           cost_total_jpy=round(sum(c["jpy"] for c in cl.values()), 3), n_cells=len(cells),
           attempts=sorted({d["attempts"] for d in cells.values()}), valid=all(d["valid_json"] for d in cells.values()))
json.dump(out, open(os.path.join(HERE, "aggregate_antenna_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(dict(levels={L: {k: v for k, v in x.items() if k in ("n_articles", "n_flags", "n_unique_sentences", "conf", "high_conf_ge_0_5", "types")} for L, x in levels.items()}), ensure_ascii=False))
for t, v in trans.items(): print(t, "kept", len(v["kept"]), "lost", len(v["lost"]), "new", len(v["new"]), "typechg", len(v["type_changed_in_kept"]), "important_lost", v["important_lost"], "lost:", v["lost"])
print("cumul", {L: (c["cumulative_union"], c["present_now"]) for L, c in cumul.items()})
for k in kn: print(k["id"], k["present"], k["first"], k["continuous"], k["confs"])
print("unid", unid); print(cl, out["cost_total_jpy"], out["attempts"], out["valid"])
