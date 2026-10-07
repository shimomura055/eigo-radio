#!/usr/bin/env python3
"""aggregate_rca.py: NG原因分析 再採点27記事の集計(決定論・標準ライブラリのみ・API/生成なし)。
入力: eval/articles/*.json(再採点)、_private/MAP_rca.json(集計時のみ開封)、
      E2E_02 STAGEWISE_SUMMARY.md 記事別表(元評価)、B3 eval/articles/<slug>_<旧code>.json(B3 V0元採点)、MAP_stage2.json(B3 V0旧code解決)
出力: eval/aggregate_rca.json, eval/SUMMARY_RCA.md
"""
import glob, json, os, re, collections, statistics
R = "er052_output/open233_ng_root_cause_01"
E2E = "er052_output/open233_allfact_note_e2e_02/eval"
B3 = "er052_output/open233_b3_trial_01/eval"


def J(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


mp = J(f"{R}/_private/MAP_rca.json")["articles"]
m2 = J(f"{B3}/_private/MAP_stage2.json")["articles"]
ev = {}
for X in "ABC":
    for l in open(f"{R}/eval_pack/assignment_rca_{X}.md", encoding="utf-8"):
        mm = re.match(r"\| \d+ \| (\w+) \| (\w+) \|", l)
        if mm:
            ev[f"{mm.group(1)}/{mm.group(2)}"] = X
# 元評価(STAGEWISE記事別表: ①,②,③,④,⑤a,⑤b = 重大 / 軽微)
orig = {}
txt = open(f"{E2E}/stagewise/STAGEWISE_SUMMARY.md", encoding="utf-8").read()
sec = txt.split("## 2. 記事別表")[1].split("検算")[0]
for l in sec.splitlines():
    mm = re.match(r"\| (\w+) (従来版|P2) ?(rep\d) \|(.*)\|", l)
    if mm:
        cells = [tuple(int(x) for x in c.strip().split("/")) for c in mm.group(4).split("|")]
        orig[(mm.group(1), "control" if mm.group(2) == "従来版" else "P2", int(mm.group(3)[3:]))] = dict(j1=cells[0], e2=cells[1], e3=cells[2], a=cells[4], b=cells[5])
# 元評価(E_*のFact誤り合計。SUMMARY.md 1節。重大/軽微分離なし。space_weaponsはJA値)
fe = {("meta", "P2", 1): 5, ("meta", "P2", 2): 7, ("meta", "control", 1): 4, ("hormuz", "P2", 1): 8, ("hormuz", "P2", 2): 10, ("hormuz", "control", 1): 2,
      ("space_weapons", "P2", 1): 1, ("space_weapons", "P2", 2): 7, ("space_weapons", "control", 1): 3, ("sewer", "P2", 1): 4, ("sewer", "P2", 2): 5, ("sewer", "control", 1): 6,
      ("ai_control", "P2", 1): 6, ("ai_control", "P2", 2): 4, ("ai_control", "control", 1): 5}


def stage_counts(a):
    c = {k: {"major": 0, "minor": 0} for k in ("s0", "s1", "s2", "any", "s1or2")}
    kinds = collections.Counter()
    org = collections.Counter()
    for it in a["ng_items"]:
        sv = it["severity"]
        st = it["stage"]
        for s in ("s0", "s1", "s2"):
            if st[s]:
                c[s][sv] += 1
        c["any"][sv] += 1
        if st["s1"] or st["s2"]:
            c["s1or2"][sv] += 1
        kinds[(it["kind"], sv)] += 1
        o = "R0" if st["s0"] else ("R2" if st["s1"] else ("EN" if st["s2"] else "none"))
        org[(o, sv)] += 1
    return c, kinds, org


arts = []
errs = []
for k, m in sorted(mp.items()):
    slug, code = k.split("/")
    a = J(f"{R}/eval/articles/{slug}_{code}.json")
    c, kinds, org = stage_counts(a)
    for s, f_ in (("s0", "s0_r0"), ("s1", "s1_ja"), ("s2", "s2_en")):
        if a["stages"][f_]["major"] != c[s]["major"] or a["stages"][f_]["minor"] != c[s]["minor"]:
            errs.append(f"{k} {s}: stages={a['stages'][f_]} items={c[s]}")
    o = m["origin"]
    src = m["src"]
    if o == "E2E02_control":
        grp, rep = "control", 1
    elif o == "E2E02_P2":
        grp, rep = "P2", int(src[-1])
    else:
        grp, rep = "V0", None
    rec = dict(key=k, slug=slug, code=code, group=grp, rep=rep, evaluator=ev[k], cnt=c, kinds={f"{a_}|{b}": n for (a_, b), n in kinds.items()},
               org={f"{a_}|{b}": n for (a_, b), n in org.items()}, pending=len(a.get("pending", [])), regress=dict(a["regressions"]),
               items=[dict(id=i["id"], sev=i["severity"], kind=i["kind"], fact=i["fact_id"], stage=i["stage"]) for i in a["ng_items"]])
    if grp in ("control", "P2"):
        rec["orig"] = orig[(slug, grp, rep)]
        rec["orig_fact_errors"] = fe[(slug, grp, rep)]
    else:
        src_code = src.rstrip("/").split("/")[-1]
        oa = J(f"{B3}/articles/{slug}_{src_code}.json")
        oc, okinds, oorg = stage_counts(oa)
        rec["b3_orig_code"] = src_code
        rec["orig_cnt"] = oc
        rec["orig_pending"] = len(oa.get("pending", []))
        rec["orig_facts_s2"] = sorted({i["fact_id"] for i in oa["ng_items"] if i["stage"]["s2"]})
        rec["new_facts_s2"] = sorted({i["fact_id"] for i in a["ng_items"] if i["stage"]["s2"]})
        rec["orig_variant"] = m2[f"{slug}/{src_code}"]["variant"]
    arts.append(rec)


def agg(rs):
    n = len(rs)
    d = dict(n=n)
    for s in ("s0", "s1", "s2", "any", "s1or2"):
        d[s] = dict(major=sum(r["cnt"][s]["major"] for r in rs), minor=sum(r["cnt"][s]["minor"] for r in rs))
    d["pending"] = sum(r["pending"] for r in rs)
    d["regress"] = sum(r["regress"]["major"] + r["regress"]["minor"] for r in rs)
    kd = collections.Counter()
    od = collections.Counter()
    for r in rs:
        for k_, v in r["kinds"].items():
            kd[k_] += v
        for k_, v in r["org"].items():
            od[k_] += v
    d["kinds"] = dict(kd)
    d["org"] = dict(od)
    return d


groups = ["control", "P2", "V0"]
by = {g: [r for r in arts if r["group"] == g] for g in groups}
out = dict(opened="2026-10-07 17:50頃(MAP_rca.json読込=本スクリプト実行)", check_errors=errs, group={g: agg(by[g]) for g in groups},
           by_evaluator={x: {g: agg([r for r in by[g] if r["evaluator"] == x]) for g in groups} for x in "ABC"},
           by_theme={t: {g: agg([r for r in by[g] if r["slug"] == t]) for g in groups} for t in sorted({r["slug"] for r in arts})},
           articles=arts)


def ratio(rs, oi, ni):
    o = sum(oi(r) for r in rs)
    n = sum(ni(r) for r in rs)
    return o, n, (o / n if n else None)


rat = {}
tot = lambda r: r["cnt"]["any"]["major"] + r["cnt"]["any"]["minor"]
s12 = lambda r: r["cnt"]["s1or2"]["major"] + r["cnt"]["s1or2"]["minor"]
s2f = lambda r: r["cnt"]["s2"]["major"] + r["cnt"]["s2"]["minor"]
s1f = lambda r: r["cnt"]["s1"]["major"] + r["cnt"]["s1"]["minor"]
for g in ("control", "P2", "both"):
    rs = by["control"] + by["P2"] if g == "both" else by[g]
    rat[g] = dict(
        factErr_vs_rescore_s1or2=ratio(rs, lambda r: r["orig_fact_errors"], s12),
        factErr_vs_rescore_any=ratio(rs, lambda r: r["orig_fact_errors"], tot),
        stagewise_5b_vs_rescore_s1or2=ratio(rs, lambda r: sum(r["orig"]["b"]), s12),
        stagewise_5a_vs_rescore_s2=ratio(rs, lambda r: sum(r["orig"]["a"]), s2f),
        stagewise_1_vs_rescore_s1=ratio(rs, lambda r: sum(r["orig"]["j1"]), s1f),
        major_5b_vs_rescore_s1or2=ratio(rs, lambda r: r["orig"]["b"][0], lambda r: r["cnt"]["s1or2"]["major"]))
out["ratios"] = rat
v0 = by["V0"]
d = []
for r in v0:
    on = r["orig_cnt"]["s2"]
    nn = r["cnt"]["s2"]
    d.append(dict(key=r["key"], variant=r["orig_variant"], orig_code=r["b3_orig_code"], new_eval=r["evaluator"], orig_s2=(on["major"], on["minor"]), new_s2=(nn["major"], nn["minor"]),
                  orig_any=(r["orig_cnt"]["any"]["major"], r["orig_cnt"]["any"]["minor"]), new_any=(r["cnt"]["any"]["major"], r["cnt"]["any"]["minor"]),
                  orig_pending=r["orig_pending"], new_pending=r["pending"], facts_orig=r["orig_facts_s2"], facts_new=r["new_facts_s2"]))
out["v0_pairs"] = d
mi = [x["new_s2"][1] - x["orig_s2"][1] for x in d]
out["v0_agree"] = dict(n=len(d), orig_s2_minor_total=sum(x["orig_s2"][1] for x in d), new_s2_minor_total=sum(x["new_s2"][1] for x in d),
                       major_agree=sum(1 for x in d if x["orig_s2"][0] == x["new_s2"][0]), minor_exact=sum(1 for x in d if x["orig_s2"][1] == x["new_s2"][1]),
                       mean_abs_diff=statistics.mean(abs(x) for x in mi), mean_signed_diff=statistics.mean(mi),
                       orig_any_minor=sum(x["orig_any"][1] for x in d), new_any_minor=sum(x["new_any"][1] for x in d),
                       any_mean_abs=statistics.mean(abs(x["new_any"][1] - x["orig_any"][1]) for x in d),
                       orig_pending=sum(x["orig_pending"] for x in d), new_pending=sum(x["new_pending"] for x in d),
                       fact_overlap_any=sum(1 for x in d if set(x["facts_orig"]) & set(x["facts_new"])), both_zero=sum(1 for x in d if not x["facts_orig"] and not x["facts_new"]))
out["major_items"] = [dict(key=r["key"], group=r["group"], rep=r["rep"], items=[i for i in r["items"] if i["sev"] == "major"]) for r in arts if r["cnt"]["any"]["major"]]
json.dump(out, open(f"{R}/eval/aggregate_rca.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=list)

# ---- MD
L = []
f = lambda x, n: "%.2f" % (x / n) if n else "-"
GN = {"control": "E2E_02 従来(Note無)", "P2": "E2E_02 P2(全fact Note)", "V0": "B3 V0(Checker無)"}
L.append("# SUMMARY_RCA: 盲検再採点27記事の集計(OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 委任_C1、¥0、2026-10-07)\n")
L.append(f"MAP開封: 2026-10-07 17:50頃(本集計 `tools/aggregate_rca.py` 実行時に `_private/MAP_rca.json` を読込、評価JSONは未修正)。検算(stages欄 vs ng_items): 不整合 {len(errs)} 件。\n")
L.append("定義: 重大/軽微=評価JSONのseverity。「全工程」=ng_items全件(R0/R2/ENのいずれかで存在)、「JA/EN最終」=s1(JA R2)またはs2(EN)に残存=STAGEWISE⑤b相当、「EN」=s2のみ=⑤a相当。同一誤りは1件。単独LLM評価(3名)・人間確認なし。\n")
L.append("## 1. 出所別 再採点結果(件数 / 1記事平均)\n")
L.append("| 出所 | N | 重大(全工程) | 軽微(全工程) | 軽微/記事 | 重大(JA/EN最終) | 軽微(JA/EN最終) | 軽微/記事(JA/EN最終) | 軽微(EN) | 退行 | 保留 |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
for g in groups:
    a = out["group"][g]
    n = a["n"]
    L.append(f"| {GN[g]} | {n} | {a['any']['major']} | {a['any']['minor']} | {f(a['any']['minor'], n)} | {a['s1or2']['major']} | {a['s1or2']['minor']} | {f(a['s1or2']['minor'], n)} | {a['s2']['minor']}({f(a['s2']['minor'], n)}) | {a['regress']}({f(a['regress'], n)}) | {a['pending']}({f(a['pending'], n)}) |")
L.append("\n## 2. 工程別(s0=R0 / s1=JA R2 / s2=EN、重大/軽微)\n")
L.append("| 出所 | s0 R0 | s1 JA R2 | s2 EN | 初出R0 | 初出R2(R0に無) | 初出ENのみ |")
L.append("|---|---|---|---|---|---|---|")
for g in groups:
    a = out["group"][g]
    o = a["org"]
    og = lambda k: f"{o.get(k + '|major', 0)}/{o.get(k + '|minor', 0)}"
    L.append(f"| {GN[g]} | {a['s0']['major']}/{a['s0']['minor']} | {a['s1']['major']}/{a['s1']['minor']} | {a['s2']['major']}/{a['s2']['minor']} | {og('R0')} | {og('R2')} | {og('EN')} |")
L.append("\n(初出 = 項目のstageフラグで、s0=trueならR0初出、s0=falseかつs1=trueならR2で新規、s1も偽でs2のみならENのみ。評価者のフラグに依存。)\n")
L.append("## 3. 機序別(kind、重大/軽微。全工程)\n")
ks = sorted({k.split("|")[0] for g in groups for k in out["group"][g]["kinds"]})
L.append("| kind | " + " | ".join(GN[g] for g in groups) + " |")
L.append("|---|---|---|---|")
for k in ks:
    L.append(f"| {k} | " + " | ".join(f"{out['group'][g]['kinds'].get(k + '|major', 0)}/{out['group'][g]['kinds'].get(k + '|minor', 0)}" for g in groups) + " |")
L.append("\n## 4. 評価者別(評価者効果の確認。N, 軽微(軽微/記事), 重大。全工程)\n")
L.append("| 評価者 | " + " | ".join(GN[g] for g in groups) + " | 全体 軽微/記事 |")
L.append("|---|---|---|---|---|")
for x in "ABC":
    cells = []
    tn = tm = 0
    for g in groups:
        a = out["by_evaluator"][x][g]
        cells.append(f"{a['n']}, {a['any']['minor']}({f(a['any']['minor'], a['n'])}), {a['any']['major']}")
        tn += a["n"]
        tm += a["any"]["minor"]
    L.append(f"| {x} | " + " | ".join(cells) + f" | {f(tm, tn)} |")
L.append("\n## 5. テーマ別(N, 軽微/記事 全工程, 軽微/記事 JA/EN最終)\n")
L.append("| テーマ | " + " | ".join(GN[g] for g in groups) + " |")
L.append("|---|---|---|---|")
for t, d_ in out["by_theme"].items():
    cells = []
    for g in groups:
        a = d_[g]
        n = a["n"]
        cells.append(f"{n}, {f(a['any']['minor'], n)}, {f(a['s1or2']['minor'], n)}" if n else "-")
    L.append(f"| {t} | " + " | ".join(cells) + " |")
L.append("\n## 6. E2E_02 15記事: 元評価 vs 今回再採点(重大/軽微)\n")
L.append("元評価: 「E_*Fact誤り」=E2E_02独立評価の合計(重大/軽微分離なし。space_weaponsはJA値)、「元⑤b」=STAGEWISE再集計(JA/EN最終残存)、「元⑤a」=EN最終残存、「元①」=JA R2。再採点: 「再JA」「再EN」「再JA/EN最終」「再全工程」「再R0」。\n")
L.append("| 記事 | 評価者 | E_*Fact誤り | 元①JA | 元⑤a | 元⑤b | 再JA(s1) | 再EN(s2) | 再JA/EN最終 | 再全工程 | 再R0 |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
sx = lambda c: f"{c['major']}/{c['minor']}"
for r in sorted([r for r in arts if r["group"] != "V0"], key=lambda r: (r["slug"], r["group"], r["rep"])):
    o = r["orig"]
    c = r["cnt"]
    L.append(f"| {r['slug']} {r['group']} r{r['rep']} ({r['code']}) | {r['evaluator']} | {r['orig_fact_errors']} | {o['j1'][0]}/{o['j1'][1]} | {o['a'][0]}/{o['a'][1]} | {o['b'][0]}/{o['b'][1]} | {sx(c['s1'])} | {sx(c['s2'])} | {sx(c['s1or2'])} | {sx(c['any'])} | {sx(c['s0'])} |")
L.append("\n### 件数比(元 / 再。大きいほど前回評価が多く数えた)\n")
L.append("| 比較(分子=元評価、分母=再採点) | 従来5本 元,再,比 | P2 10本 元,再,比 | 15本 元,再,比 |")
L.append("|---|---|---|---|")
names = dict(factErr_vs_rescore_s1or2="E_*Fact誤り / 再JA・EN最終(重大+軽微)", factErr_vs_rescore_any="E_*Fact誤り / 再全工程",
             stagewise_5b_vs_rescore_s1or2="元⑤b / 再JA・EN最終", stagewise_5a_vs_rescore_s2="元⑤a / 再EN", stagewise_1_vs_rescore_s1="元① / 再JA", major_5b_vs_rescore_s1or2="重大: 元⑤b / 再JA・EN最終")
for k, nm in names.items():
    cells = []
    for g in ("control", "P2", "both"):
        o, n, r_ = rat[g][k]
        cells.append(f"{o}, {n}, " + ("%.2f" % r_ if r_ is not None else "元%d/再0" % o))
    L.append(f"| {nm} | " + " | ".join(cells) + " |")
L.append("\n## 7. B3 V0 12記事: 今回B3評価者(元) vs 再採点評価者(盲検、別人)\n")
L.append("元=B3段階3のテーマ別評価者、再=本RCA評価者A/B/C。EN(s2)の重大/軽微、全工程の軽微、保留を並べる。\n")
L.append("| 記事(再code) | 元code | 再評価者 | 元EN | 再EN | 元全工程軽微 | 再全工程軽微 | 元保留 | 再保留 | ENのNG fact(元 / 再) |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for x in d:
    L.append(f"| {x['key']} | {x['orig_code']} | {x['new_eval']} | {x['orig_s2'][0]}/{x['orig_s2'][1]} | {x['new_s2'][0]}/{x['new_s2'][1]} | {x['orig_any'][1]} | {x['new_any'][1]} | {x['orig_pending']} | {x['new_pending']} | {','.join(x['facts_orig']) or '-'} / {','.join(x['facts_new']) or '-'} |")
va = out["v0_agree"]
L.append(f"\n一致: 重大(EN)一致 {va['major_agree']}/{va['n']}(両者とも全0)。EN軽微の記事別完全一致 {va['minor_exact']}/{va['n']}、|差|平均 {va['mean_abs_diff']:.2f}、符号付き差(再-元)平均 {va['mean_signed_diff']:+.2f}。EN軽微合計 元{va['orig_s2_minor_total']}/再{va['new_s2_minor_total']}。全工程軽微合計 元{va['orig_any_minor']}/再{va['new_any_minor']}(|差|平均 {va['any_mean_abs']:.2f}/記事)。保留合計 元{va['orig_pending']}/再{va['new_pending']}。ENのNG factが元・再で共通する記事 {va['fact_overlap_any']}/{va['n']}、両者ともENのNGなし {va['both_zero']}/{va['n']}。\n")
L.append("## 8. 重大NG(全再採点27記事中)\n")
for mi_ in out["major_items"]:
    for i in mi_["items"]:
        L.append(f"- {mi_['key']}({mi_['group']} rep{mi_['rep']}): {i['id']} kind={i['kind']} fact={i['fact']} stage={i['stage']}")
L.append("\n(出所と元評価での扱いは root_cause_draft.md 6節)")
open(f"{R}/eval/SUMMARY_RCA.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ok", errs)
