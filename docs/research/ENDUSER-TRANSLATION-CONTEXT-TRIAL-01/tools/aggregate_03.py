# 集計(TRIAL_PLAN_02 §4,§5)。入力: parts_<cond>.jsonl / sheet_key_<split>.json / grades_<split>.txt(裁定。形式: 1行1行番号「<row> A0 B2P C1 Dx ...」。数字=0OK/1軽/2中/3重大、x=exclude、数字後の英字=類型 P/D/F/A/N/M/O)
# 出力: metrics_<split>.json と summary_<split>.md
import json, os, re, sys, argparse, statistics, collections
ap = argparse.ArgumentParser()
ap.add_argument("--evdir", required=True); ap.add_argument("--split", required=True); ap.add_argument("--conds", required=True)
ap.add_argument("--sets", required=True); ap.add_argument("--pool", required=True); ap.add_argument("--grades", required=True)
ap.add_argument("--base", default="A"); ap.add_argument("--noise", default="Ap")
a = ap.parse_args()
sets = json.load(open(a.sets, encoding="utf-8"))[a.split]
sinfo = {}
for e in sets:
    for s in e["sentences"]:
        sinfo[e["slug"] + "|" + s["sid"]] = {"slug": e["slug"], "family": e["family"], "level": e["level"], "part": e["part"], "kind": e["kind"], "stratum": e["stratum"], "en": s["en"]}
part_sids = {(e["slug"], e["level"], e["part"]): [e["slug"] + "|" + s["sid"] for s in e["sentences"]] for e in sets}
key = json.load(open(os.path.join(a.evdir, f"sheet_key_{a.split}.json"), encoding="utf-8"))
sheet = json.load(open(os.path.join(a.evdir, f"sheet_{a.split}.json"), encoding="utf-8"))
sheet_by_row = {str(r["row"]): r for r in sheet}
grades = {}   # row -> {letter: (grade|'x', type)}
for ln in open(a.grades, encoding="utf-8"):
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    toks = ln.split()
    row = toks[0]
    g = {L: (0, "") for L in key[row]["map"]} if row in key else {}
    for t in toks[1:]:
        m = re.match(r"^([A-Z])([0-3x])([A-Za-z]?)$", t)
        if not m:
            raise SystemExit(f"bad token {t!r} in row {row}")
        g[m.group(1)] = (m.group(2) if m.group(2) == "x" else int(m.group(2)), m.group(3))
    grades[row] = g
missing = [r for r in key if r not in grades or set(grades[r]) != set(key[r]["map"])]
if missing:
    print("UNGRADED rows:", len(missing), missing[:10])
conds = a.conds.split(",")
rows = {}   # cond -> list of part rows
for c in conds:
    rows[c] = [json.loads(l) for l in open(os.path.join(a.evdir, f"parts_{c}.jsonl"), encoding="utf-8")]
final_ja = {c: {} for c in conds}
for c in conds:
    for r in rows[c]:
        for sid, ja in r["ja"].items():
            final_ja[c][r["slug"] + "|" + sid] = ja
# grade lookup: (cond, kind) -> sid -> (grade|'x'|None(未表示), type)
G = collections.defaultdict(dict)
text_of = {}
for row, k in key.items():
    sid = k["sid"]
    for L, labels in k["map"].items():
        gr = grades.get(row, {}).get(L)
        for lab in labels:
            G[lab][sid] = gr
            text_of[(lab, sid)] = sheet_by_row[row]["variants"][L]
def gget(lab, sid):
    """None=非表示(fail-closed)または欠損、それ以外 (grade, type)"""
    return G.get(lab, {}).get(sid)
# --- 比較 ---
def compare(M, B, kind="final", mode="main"):
    """Mの訳をBの訳と文単位で比較。戻り=dict(sid->('imp'|'worse'|'same'|'excl', Mgrade, Bgrade))。非表示規則はM-8(4)。"""
    out = {}
    for sid in sinfo:
        gm = gget(f"{M}:{kind}", sid); gb = gget(f"{B}:{kind}", sid)
        mshown = final_ja.get(M, {}).get(sid) is not None if kind == "final" else gm is not None
        bshown = final_ja.get(B, {}).get(sid) is not None if kind == "final" else gb is not None
        if kind == "final" and (M not in final_ja or B not in final_ja):
            continue
        if kind == "first" and (gm is None or gb is None):
            continue   # 1回目の訳が復元できない単位(parse不合格で再試行)は比較から除く
        if B == "PUB" and sid not in {s for s in G.get("PUB:final", {})}:
            continue
        if not mshown and not bshown:
            out[sid] = ("same", None, None); continue
        if not mshown and bshown:
            out[sid] = ("worse", "N", gb[0] if gb else None); continue   # 欠落=悪化(中)
        if mshown and not bshown:
            out[sid] = ("imp", gm[0] if gm else None, "N"); continue
        if gm is None or gb is None:
            continue
        if gm[0] == "x" or gb[0] == "x":
            out[sid] = ("worse" if mode == "unfav" else "excl", gm[0], gb[0]); continue
        d = gm[0] - gb[0]
        out[sid] = ("imp" if d < 0 else "worse" if d > 0 else "same", gm[0], gb[0])
    return out
def sev(entry):
    k, gm, gb = entry
    if gm == "N":
        return 2
    return gm if isinstance(gm, int) else 2
def summarize(cmp):
    c = collections.Counter(v[0] for v in cmp.values())
    n = len(cmp)
    worse = [(sid, v) for sid, v in cmp.items() if v[0] == "worse"]
    g1 = sum(1 for sid, v in worse if v[1] == 3 and isinstance(v[2], int) and v[2] <= 1)
    g2 = sum(1 for sid, v in worse if sev(v) >= 2)
    return {"n": n, "imp": c["imp"], "worse": c["worse"], "same": c["same"], "excl": c["excl"], "worse_rate": round(c["worse"] / n, 4) if n else None,
            "imp_rate": round(c["imp"] / n, 4) if n else None, "G1_A_le1_to_M3": g1, "G2_worse_to_ge2": g2,
            "worse_by_Msev": dict(collections.Counter(("fail-closed" if v[1] == "N" else v[1]) for sid, v in worse)),
            "imp_by_Bsev": dict(collections.Counter(("fail-closed" if v[2] == "N" else v[2]) for sid, v in cmp.items() if v[0] == "imp"))}
out = {"split": a.split, "missing_grades": len(missing), "cmp": {}, "by_cond": {}}
base, noise = a.base, a.noise
for M in conds:
    if M == base:
        continue
    cm = compare(M, base)
    s = summarize(cm); s_unfav = summarize(compare(M, base, mode="unfav"))
    out["cmp"][f"{M}_vs_{base}"] = {"main": s, "sens_exclude_as_worse": {k: s_unfav[k] for k in ("worse", "worse_rate", "G1_A_le1_to_M3", "G2_worse_to_ge2")}}
    if M != noise and noise in conds:
        out["cmp"][f"{M}_vs_{noise}"] = {"main": summarize(compare(M, noise))}
    # 家族/level別
    fam = collections.defaultdict(collections.Counter)
    for sid, v in cm.items():
        fam[(sinfo[sid]["family"], sinfo[sid]["level"])][v[0]] += 1
    out["cmp"][f"{M}_vs_{base}"]["by_family_level"] = {f"{k[0]}/{k[1]}": dict(v) for k, v in sorted(fam.items())}
if "PUB:final" in G:
    for lab in ("A",):
        # 公開版(A'')対A
        cm = {}
        for sid in G["PUB:final"]:
            gp = G["PUB:final"][sid]; ga = gget("A:final", sid)
            if gp is None or ga is None or gp[0] == "x" or ga[0] == "x":
                continue
            d = gp[0] - ga[0]
            cm[sid] = ("imp" if d < 0 else "worse" if d > 0 else "same", gp[0], ga[0])
        out["cmp"]["PUB_vs_A"] = {"main": summarize(cm)}
# R-11: verify前の1回目の訳どうし
for M in conds:
    if M == base:
        continue
    cm = compare(M, base, kind="first")
    out["cmp"][f"{M}_vs_{base}__first_translation_only"] = {"main": summarize(cm)}
# 条件ごとの3区分表(観点6)・運用指標
def part_failed(r, sids):
    return any(r["ja"].get(s) is None for s in sids)
for c in conds:
    tab = collections.Counter()
    for sid in sinfo:
        if c not in final_ja or sid not in final_ja[c]:
            continue
        if final_ja[c][sid] is None:
            tab["非表示(fail-closed)"] += 1; continue
        g = gget(f"{c}:final", sid)
        if g is None:
            tab["未採点"] += 1
        elif g[0] == "x":
            tab["exclude"] += 1
        else:
            tab[{0: "表示正しい(OK)", 1: "表示正しい(軽)", 2: "表示誤り(中)", 3: "表示誤り(重大)"}[g[0]]] += 1
    nfc_parts = 0; nparts = 0
    for (slug, lv, part), sids in part_sids.items():
        if not all(s in final_ja[c] for s in sids):
            continue
        nparts += 1
        if any(final_ja[c][s] is None for s in sids):
            nfc_parts += 1
    calls = collections.Counter()
    cost = 0.0; cost_gen = 0.0; wall = 0.0; per_call = []; nrows = len(rows[c])
    for r in rows[c]:
        calls["translate"] += r["api_calls"]["translate"]; calls["verify"] += r["api_calls"]["verify"]
        cost += r["cost_jpy"]; wall += r["wall_s"]
        per_call += [x["wall_s"] for x in r["calls"]]
        ng = sum(len(p["sids"]) for p in r["parts"] if p["stratum"] == "gen"); nt = sum(len(p["sids"]) for p in r["parts"])
        cost_gen += r["cost_jpy"] * (ng / nt if nt else 0)
    dbl = sum(1 for r in rows[c] if r.get("double_ctx_block"))
    out["by_cond"][c] = {"table_sentences": dict(tab), "parts": nparts, "fail_closed_parts": nfc_parts, "fail_closed_sentences": tab["非表示(fail-closed)"],
                         "calls": dict(calls), "calls_total": calls["translate"] + calls["verify"], "cost_jpy": round(cost, 4), "cost_jpy_gen_stratum_alloc": round(cost_gen, 4),
                         "wall_total_s": round(wall, 1), "call_wall_median_s": round(statistics.median(per_call), 3) if per_call else None, "rows": nrows,
                         "ctx_sentences_mean": round(statistics.mean(r["ctx_sentences"] for r in rows[c]), 2), "double_ctx_rows": dbl,
                         "retry_rate_rows": round(sum(1 for r in rows[c] if r["api_calls"]["translate"] > 1 or r["api_calls"]["verify"] > 1) / nrows, 3)}
# G4/C1/T1 vs base
n_articles = len({v["slug"] for v in sinfo.values() if v["stratum"] == "gen"})
for c in conds:
    if c == base:
        continue
    b = out["by_cond"][base]; m = out["by_cond"][c]
    out["by_cond"][c]["G4_failclosed_parts_le_A"] = m["fail_closed_parts"] <= b["fail_closed_parts"]
    out["by_cond"][c]["G4_calls_ratio"] = round(m["calls_total"] / b["calls_total"], 3)
    out["by_cond"][c]["C1_extra_cost_per_article_jpy"] = round((m["cost_jpy_gen_stratum_alloc"] - b["cost_jpy_gen_stratum_alloc"]) / n_articles, 4)
    out["by_cond"][c]["C1_total_cost_ratio"] = round(m["cost_jpy"] / b["cost_jpy"], 3) if b["cost_jpy"] else None
    out["by_cond"][c]["T1_call_wall_median_ratio"] = round(m["call_wall_median_s"] / b["call_wall_median_s"], 3)
# B1(b): 訳語整合
TERMS = [
 ("family_z_melos", "city", r"\bcity\b|\bcities\b", r"city gate", [("都市", r"都市"), ("都", r"都(?!市)"), ("街", r"街"), ("町", r"町"), ("城下", r"城下"), ("市", r"市(?!場)"), ("城", r"城(?!門)")]),
 ("family_z_melos", "city gates", r"city gates?", None, [("城門", r"城門"), ("町の門", r"町の?門"), ("街の門", r"街の?門"), ("都の門", r"都の?門")]),
 ("family_z_melos", "sister", r"\bsisters?\b", None, [("妹", r"妹"), ("姉妹", r"姉妹"), ("姉", r"姉(?!妹)")]),
 ("family_x_jwst", "line", r"\bline(?:s)?\b", None, [("輝線", r"輝線"), ("光の筋", r"光の筋"), ("光の線", r"光の線"), ("線", r"線")]),
 ("family_z_yuki", "master", r"\bmaster\b", None, [("師匠", r"師匠"), ("主人", r"主人"), ("親方", r"親方")]),
 ("family_z_yuki", "straw coats", r"straw coats?", None, [("蓑", r"蓑|みの"), ("藁の上着", r"藁の上着"), ("藁の外套", r"藁の外套"), ("藁のコート", r"藁のコート")]),
 ("family_z_yuki", "bar", r"\bbar\b", None, [("棒", r"棒"), ("横木", r"横木"), ("かんぬき", r"かんぬき|閂")]),
]
cells = []
for slugp, term, en_re, en_ex, classes in TERMS:
    for lv in ("std", "adv"):
        sids = [sid for sid, v in sinfo.items() if v["slug"].startswith(slugp) and v["level"] == lv and re.search(en_re, v["en"], re.I) and not (en_ex and re.search(en_ex, v["en"], re.I))]
        if len(sids) >= 2:
            cells.append((slugp, term, lv, sids, classes))
def distinct(c, sids, classes):
    got = set()
    for sid in sids:
        ja = final_ja[c].get(sid)
        if ja is None:
            continue
        for name, rx in classes:
            if re.search(rx, ja):
                got.add(name); break
        else:
            got.add("other")
    return len(got)
tm = {}
for c in conds:
    if c not in final_ja:
        continue
    tm[c] = {f"{s}/{t}/{lv}": distinct(c, sids, cl) for s, t, lv, sids, cl in cells if all(x in final_ja[c] for x in sids)}
out["term_cells"] = tm
if base in tm and noise in tm:
    for c in conds:
        if c in (base, noise) or c not in tm:
            continue
        ks = [k for k in tm[c] if k in tm[base] and k in tm[noise]]
        if not ks:
            continue
        mM = statistics.mean(tm[c][k] for k in ks); mA = statistics.mean((tm[base][k] + tm[noise][k]) / 2 for k in ks)
        wc = sum(1 for k in ks if tm[c][k] > max(tm[base][k], tm[noise][k]))
        out["by_cond"][c]["B1b_cells"] = len(ks); out["by_cond"][c]["B1b_M_mean"] = round(mM, 3); out["by_cond"][c]["B1b_A_mean"] = round(mA, 3)
        out["by_cond"][c]["B1b_worse_cells"] = wc; out["by_cond"][c]["B1b_pass"] = (mM <= mA - 0.25) and wc <= 1
# R-2 混入候補(決定論・補助)
KATA = re.compile(r"[ァ-ヴー]{3,}"); NUM = re.compile(r"\d+")
by_slug_ja = collections.defaultdict(str)
for sid, v in sinfo.items():
    by_slug_ja[v["slug"]] += " " + (final_ja.get(base, {}).get(sid) or "")
mix = {}
for c in conds:
    if c in (base, noise) or c not in final_ja:
        continue
    cand = []
    for sid, v in sinfo.items():
        ja = final_ja[c].get(sid)
        if not ja:
            continue
        ref = " ".join(x for x in (final_ja.get(base, {}).get(sid), final_ja.get(noise, {}).get(sid)) if x)
        mk = set(KATA.findall(ja)) - set(KATA.findall(ref))
        mk = {t for t in mk if t in by_slug_ja[v["slug"]].replace(final_ja.get(base, {}).get(sid) or "\0", "")}
        mn = set(NUM.findall(ja)) - set(NUM.findall(v["en"])) - set(NUM.findall(ref))
        mn = {t for t in mn if t in by_slug_ja[v["slug"]]}
        if mk or mn:
            cand.append({"sid": sid, "kata": sorted(mk), "num": sorted(mn)})
    mix[c] = cand
out["mix_candidates_counts"] = {c: len(v) for c, v in mix.items()}

# R-11: 1回目の訳(verify前) と 最終訳 の関係(verify/再試行が結果を良くしたか悪くしたか)
ff = {}
for c in conds:
    cnt = collections.Counter()
    for sid in sinfo:
        gf = gget(f"{c}:first", sid)
        if gf is None or gf[0] == "x":
            continue
        fin = final_ja.get(c, {}).get(sid, "NA")
        if fin == "NA":
            continue
        if fin is None:
            cnt["first_ok_but_failclosed" if gf[0] <= 1 else "first_bad_failclosed"] += 1; continue
        gl = gget(f"{c}:final", sid)
        if gl is None or gl[0] == "x":
            continue
        if text_of.get((f"{c}:first", sid)) == text_of.get((f"{c}:final", sid)):
            cnt["same_text"] += 1
        elif gl[0] > gf[0]:
            cnt["final_worse_than_first"] += 1
        elif gl[0] < gf[0]:
            cnt["final_better_than_first"] += 1
        else:
            cnt["changed_same_grade"] += 1
    ff[c] = dict(cnt)
out["first_vs_final"] = ff
json.dump({"mix_candidates": mix}, open(os.path.join(a.evdir, f"mix_candidates_{a.split}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

detail = {}
for M in conds:
    if M == base:
        continue
    cm = compare(M, base)
    detail[M] = [{"sid": sid, "status": v[0], "grade_M": v[1], "grade_A": v[2], "family": sinfo[sid]["family"], "level": sinfo[sid]["level"], "kind": sinfo[sid]["kind"], "stratum": sinfo[sid]["stratum"], "en": sinfo[sid]["en"],
                  "ja_M": final_ja[M].get(sid), "ja_A": final_ja[base].get(sid)} for sid, v in cm.items() if v[0] in ("imp", "worse")]
json.dump(detail, open(os.path.join(a.evdir, f"cmp_detail_{a.split}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(out, open(os.path.join(a.evdir, f"metrics_{a.split}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# 要約出力
print("missing grades", out["missing_grades"])
print("cond | fcParts fcSents calls ratio cost(gen alloc) costRatio wallMedRatio C1/art | vsA: imp worse G1 G2 worseRate | sens worseRate | vsAp: worse | first-only imp/worse | B1b")
for c in conds:
    b = out["by_cond"][c]
    if c == base:
        print(c, b["fail_closed_parts"], b["fail_closed_sentences"], b["calls_total"], "-", b["cost_jpy"], b["table_sentences"]); continue
    m = out["cmp"][f"{c}_vs_{base}"]; mm = m["main"]
    ap_ = out["cmp"].get(f"{c}_vs_{noise}", {}).get("main", {})
    fo = out["cmp"][f"{c}_vs_{base}__first_translation_only"]["main"]
    print(c, "|", b["fail_closed_parts"], b["fail_closed_sentences"], b["calls_total"], b["G4_calls_ratio"], b["cost_jpy"], b["C1_total_cost_ratio"], b["T1_call_wall_median_ratio"], b["C1_extra_cost_per_article_jpy"],
          "|", mm["imp"], mm["worse"], mm["G1_A_le1_to_M3"], mm["G2_worse_to_ge2"], mm["worse_rate"], "|", m["sens_exclude_as_worse"]["worse_rate"], "|", ap_.get("worse"), "|", fo["imp"], fo["worse"], "|",
          b.get("B1b_pass"), b.get("B1b_M_mean"), b.get("B1b_A_mean"), b.get("B1b_worse_cells"))
