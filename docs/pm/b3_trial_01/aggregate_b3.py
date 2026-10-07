#!/usr/bin/env python3
"""aggregate_b3.py: B3 brief構造Trial 集計(決定論・標準ライブラリのみ・API/生成なし)。
usage: python aggregate_b3.py [--in DIR] [--features FILE] [--map MAP_stage2.json] [--gate-stop FILE] [--out DIR]
B1(段階2版): 5条件(V0/V1/V3/V5/V6) x 3テーマ x b1〜b4 x w1=60 - WRITER_GATE_STOP(母数除外、5-A6)。判定は5-A4(b1〜b4の過半数同符号)
既定 in=er052_output/open233_b3_trial_01/eval/articles, features=<in親>/brief_features.json, out=<in親>
出力: B3_SUMMARY.md, b3_summary.json
"""
import argparse, glob, json, math, os, sys

VARS = ["V0", "V1", "V3", "V5", "V6"]  # B1: 段階2は V2 なし(design_01 5-A4)
GATE_STOP = {}
BS = (1, 2, 3, 4)  # brief b1〜b4、Writerはw1のみ(1本/brief)
THEMES = ["meta", "hormuz", "space_weapons"]
LABELS = ["correct", "ambiguous", "misread"]
EXPECT = [["V5"], ["V3"], ["V1", "V2"], ["V0"], ["V6"]]  # 設計の期待(誤りが少ない=良い順): V5 > V3 > V1/V2 > V0 > V6。V1/V2は同順位。(M1修正: 旧版は逆向き)
EXPECT_PAIRS = [("V0", "V6"), ("V1", "V0"), ("V3", "V1"), ("V5", "V3")]  # (良い=誤り少ない側, 悪い側)。参考表。主判定は下の(h)表(M3)
# M3: 事前登録の比較(左=処置側, 右=基準側)。P1/P2が主、他は副次
PAIRS_M3 = [("P1(主)", "V3", "V0"), ("P2(主,操作確認)", "V6", "V0"), ("副次", "V1", "V0"), ("副次", "V5", "V3")]
H1_KINDS = ("subject", "object", "scope")
H2_KINDS = ("causal", "scope")  # scopeはng_itemsのcross_fact=true(別fact連結由来)のものだけ
H3_KINDS = ("added_fact",)
STAGES3 = [("s0_r0", "s0", "R0(修正前原稿)"), ("s1_ja", "s1", "①JA R2"), ("s2_en", "s2", "②EN")]
MIN_DIFF = 0.5  # 件/記事
NOTE = ("注意: 各(条件 x テーマ)は最大4記事(b1〜b4 x w1、Writer1本/brief)、全テーマ合算でも1条件最大12記事の小標本。B3差とWriter差は分離できない(5-A4)。"
        "WRITER_GATE_STOPの記事は母数から除外(5-A6)、生成不能件数は副次指標として別表。重大/軽微は単独評価・人間確認なし。本表は採否判断を含まない(Production採用は人間のみ)。"
        "相関(d)はn小で参考値。")


def load_map(mpath):
    if not os.path.isfile(mpath):
        return None
    with open(mpath, encoding="utf-8") as fh:
        return json.load(fh)


def load(indir, mp=None):
    """記事JSON(評価者は slug+code のみ記入)を読み、MAP.json(集計時のみ使用)でvariant/b3_rep/writer_repを結合する。"""
    arts, errs = [], []
    for p in sorted(glob.glob(os.path.join(indir, "*.json"))):
        try:
            with open(p, encoding="utf-8") as fh:
                a = json.load(fh)
            a["_file"] = os.path.basename(p)
            if "code" in a and "variant" not in a:
                m = (mp or {}).get("articles", {}).get("%s/%s" % (a.get("slug"), a["code"]))
                if m is None:
                    errs.append("%s: MAPにcode解決不能 %s/%s" % (p, a.get("slug"), a["code"]))
                    continue
                a["variant"], a["b3_rep"], a["writer_rep"], a["bcode"] = m["variant"], m["b3_rep"], m["writer_rep"], m["bcode"]
            arts.append(a)
        except Exception as e:
            errs.append("%s: 読込失敗 %s" % (p, e))
    return arts, errs


def load_brief_reviews(bdir, mp):
    """eval/brief_review/<slug>_<bcode>.json -> {bkey: review}"""
    out = {}
    for p in sorted(glob.glob(os.path.join(bdir, "*.json"))):
        with open(p, encoding="utf-8") as fh:
            r = json.load(fh)
        m = (mp or {}).get("briefs", {}).get("%s/%s" % (r.get("slug"), r.get("bcode")))
        if m is None:
            continue
        out["%s|%s|b%d" % (r["slug"], m["variant"], m["b3_rep"])] = r
    return out


def bkey(a):
    return "%s|%s|b%d" % (a["slug"], a["variant"], a["b3_rep"])


def tot(a, stage):
    s = a["stages"][stage]
    return s["major"] + s["minor"]


def agg(g):
    n = len(g)
    r = {"n": n}
    for key, fn in (("s0_major", lambda a: a["stages"]["s0_r0"]["major"]), ("s0_minor", lambda a: a["stages"]["s0_r0"]["minor"]),
                    ("s1_major", lambda a: a["stages"]["s1_ja"]["major"]), ("s1_minor", lambda a: a["stages"]["s1_ja"]["minor"]),
                    ("s2_major", lambda a: a["stages"]["s2_en"]["major"]), ("s2_minor", lambda a: a["stages"]["s2_en"]["minor"]),
                    ("reg_major", lambda a: a["regressions"]["major"]), ("reg_minor", lambda a: a["regressions"]["minor"])):
        r[key] = sum(fn(a) for a in g)
    for lb in LABELS:
        r["f_" + lb] = sum(1 for a in g for d in a.get("direction_facts", []) if d["label"] == lb)
    r["per"] = {k: (round(v / n, 2) if n else None) for k, v in r.items() if k not in ("n", "per")}
    return r


def f(v):
    return "-" if v is None else "%.2f" % v


def row(name, r):
    p = r["per"]
    return "| %s | %d | %s / %s | %s / %s | %s / %s | %s / %s | %d / %d / %d |" % (
        name, r["n"], f(p["s0_major"]), f(p["s0_minor"]), f(p["s1_major"]), f(p["s1_minor"]), f(p["s2_major"]), f(p["s2_minor"]),
        f(p["reg_major"]), f(p["reg_minor"]), r["f_correct"], r["f_ambiguous"], r["f_misread"])


HDR = ("| 区分 | 記事数 | R0(修正前原稿) 重大/軽微 (件/記事) | ①JA R2 重大/軽微 (件/記事) | ②EN 重大/軽微 (件/記事) | R0->R2退行 重大/軽微 (件/記事) | ★ 正しい/曖昧/重大誤読 (合計) |\n"
       "|---|---|---|---|---|---|---|")


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = mean(x), mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def fr(v):
    return "-" if v is None else "%.2f" % v


def variance_split(arts, stage):
    """5-A4: Writer1本/briefのためB3差とWriter差は分離不可。同(variant,theme)内のb1〜b4(存在分)の誤り件数(重大+軽微)の範囲(max-min)のテーマ平均(記述のみ)。"""
    out = {}
    for v in VARS:
        rg = []
        for t in THEMES:
            xs = [tot(a, stage) for a in arts if a["variant"] == v and a["slug"] == t]
            if len(xs) >= 2:
                rg.append(max(xs) - min(xs))
        out[v] = {"cells": len(rg), "b_range": mean(rg)}
    return out


def kcount(a, stage_flag, kinds, need_cross=False):
    """ng_itemsのうち、その工程(s0/s1/s2)に存在しkindがkindsに含まれる件数。need_cross=True: scopeはcross_fact=trueのみ。"""
    n = 0
    for i in a.get("ng_items", []):
        if not i["stage"].get(stage_flag):
            continue
        k = i["kind"]
        if k not in kinds:
            continue
        if need_cross and k == "scope" and not i.get("cross_fact"):
            continue
        n += 1
    return n


METRICS = [("合計(重大+軽微)", lambda a, sk, sf: tot(a, sk)),
           ("H1 subject/object/scope", lambda a, sk, sf: kcount(a, sf, H1_KINDS)),
           ("H2 causal/scope(連結由来)", lambda a, sk, sf: kcount(a, sf, H2_KINDS, True)),
           ("H3 added_fact", lambda a, sk, sf: kcount(a, sf, H3_KINDS))]


def cell_mean(arts, v, t, b, fn):
    xs = [fn(a) for a in arts if a["variant"] == v and (t is None or a["slug"] == t) and (b is None or a["b3_rep"] == b)]
    return mean(xs)


def sign(d):
    return 0 if d is None or d == 0 else (1 if d > 0 else -1)


def majority_sign(ds, d):
    """5-A4: b1〜b4(比較可能なb)の差のうち、dと同符号(非0)が比較可能b数の過半数(>半数)を占めれば True。同数・過半数不成立は保留(False)。"""
    cmp_ = [x for x in ds if x is not None]
    if not cmp_ or sign(d) == 0:
        return False
    return sum(1 for x in cmp_ if sign(x) == sign(d)) * 2 > len(cmp_)


def judge_pair(arts, left, right, fn):
    """事前登録の判定規則(M3+5-A4): 3テーマ中2以上で『テーマ差の絶対値>=0.5件/記事 かつ b1〜b4(両条件の記事が存在するb)の差の過半数が同符号(非0)』かつ同方向 -> 傾向あり、それ以外(同数・過半数不成立含む) -> 未判定。差=left-right。Gate STOPで欠けたbは比較可能bから除外。"""
    dirs, detail = [], []
    for t in THEMES:
        dl, dr = cell_mean(arts, left, t, None, fn), cell_mean(arts, right, t, None, fn)
        if dl is None or dr is None:
            dirs.append(0)
            detail.append("%s:-" % t)
            continue
        d = dl - dr
        db = []
        for b in BS:
            bl, br = cell_mean(arts, left, t, b, fn), cell_mean(arts, right, t, b, fn)
            db.append(None if bl is None or br is None else bl - br)
        ok = abs(d) >= MIN_DIFF and majority_sign(db, d)
        dirs.append(sign(d) if ok else 0)
        detail.append("%s:%+.2f(%s)%s" % (t, d, "/".join("b%d %s" % (b, "-" if x is None else "%+.2f" % x) for b, x in zip(BS, db)), "*" if ok else ""))
    up, dn = dirs.count(1), dirs.count(-1)
    if up >= 2:
        verdict = "傾向あり(%s>%s)" % (left, right)
    elif dn >= 2:
        verdict = "傾向あり(%s<%s)" % (left, right)
    else:
        verdict = "未判定"
    return verdict, detail


def BRIEF_KEYS_EXPECTED(arts):
    return {bkey(a) for a in arts}


def expected_keys():
    return {(t, v, b) for t in THEMES for v in VARS for b in BS}


def check(arts, feats, brs):
    out, ok = [], True
    gs = {(k.split("/")[0], k.split("/")[1], int(k.split("/")[2][1:])) for k in GATE_STOP}
    exp = expected_keys() - gs
    out.append("- 記事数 %d (期待 %d = 60 - WRITER_GATE_STOP %d): %s" % (len(arts), len(exp), len(gs), "OK" if len(arts) == len(exp) else "NG"))
    ok = ok and len(arts) == len(exp)
    keys = [(a["slug"], a["variant"], a["b3_rep"]) for a in arts]
    have = set(keys)
    miss = sorted(exp - have)
    extra = sorted(have - exp)
    if miss:
        ok = False
        out.append("- 欠損(Gate STOP宣言以外): %s NG" % miss)
    if extra:
        ok = False
        out.append("- 想定外のセル(Gate STOP宣言分または範囲外): %s NG" % extra)
    if any(a.get("writer_rep") != 1 for a in arts):
        ok = False
        out.append("- writer_rep!=1の記事あり NG")
    if not miss and not extra:
        out.append("- 5条件 x 3テーマ x b1〜b4 (Gate STOP %d件除く) 全て1記事: OK" % len(gs))
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        ok = False
        out.append("- 重複: %s NG" % dup)
    bad_n = 0
    for a in arts:
        items = a.get("ng_items", [])
        for sk, sn in (("s0", "s0_r0"), ("s1", "s1_ja"), ("s2", "s2_en")):
            for sev in ("major", "minor"):
                c = sum(1 for i in items if i["severity"] == sev and i["stage"].get(sk))
                if c != a["stages"][sn][sev]:
                    ok = False
                    bad_n += 1
                    out.append("- 件数不一致 %s %s %s: stages=%d ng_items=%d NG" % (a["_file"], sn, sev, a["stages"][sn][sev], c))
        for sev in ("major", "minor"):
            c = sum(1 for i in items if i["severity"] == sev and i.get("regression"))
            if c != a["regressions"][sev]:
                ok = False
                bad_n += 1
                out.append("- 件数不一致 %s regressions %s: 記録=%d ng_items=%d NG" % (a["_file"], sev, a["regressions"][sev], c))
        ids = [i["id"] for i in items]
        if len(ids) != len(set(ids)):
            ok = False
            bad_n += 1
            out.append("- ng_items ID重複 %s NG" % a["_file"])
    out.append("- ng_items vs stages/regressions/ID 照合: %s" % ("不一致あり(上記)" if bad_n else "全記事OK"))
    miss_br = sorted(BRIEF_KEYS_EXPECTED(arts) - set(brs))
    out.append("- brief_review(別インスタンス記入): %d briefs、記事に対応するもの欠落 %d%s" % (len(brs), len(miss_br), (" " + ", ".join(miss_br)) if miss_br else ""))
    if miss_br:
        ok = False
    if feats is None:
        out.append("- brief_features: なし(注意)")
    else:
        missf = sorted({bkey(a) for a in arts} - set(feats))
        out.append("- brief_features: %d briefs(期待60)、記事に対応するもの欠落 %d%s" % (len(feats), len(missf), (" " + ", ".join(missf)) if missf else ""))
        if missf:
            ok = False
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="indir", default="er052_output/open233_b3_trial_01/eval/articles")
    ap.add_argument("--features", default=None)
    ap.add_argument("--map", default=None, help="eval/_private/MAP_stage2.json(集計時のみ使用。評価者には渡さない)")
    ap.add_argument("--gate-stop", default="er052_output/open233_b3_trial_01/runs/writer_gate_stop_final.json", help="WRITER_GATE_STOP宣言(キー theme/V/bN。5-A6で母数除外)")
    ap.add_argument("--brief-reviews", default=None)
    ap.add_argument("--out", dest="outdir", default=None)
    ns = ap.parse_args()
    outdir = ns.outdir or os.path.dirname(os.path.normpath(ns.indir))
    fpath = ns.features or os.path.join(os.path.dirname(os.path.normpath(ns.indir)), "brief_features_stage2.json")
    ev = os.path.dirname(os.path.normpath(ns.indir))
    mp = load_map(ns.map or os.path.join(ev, "_private", "MAP_stage2.json"))
    global GATE_STOP
    GATE_STOP = {}
    if os.path.isfile(ns.gate_stop):
        with open(ns.gate_stop, encoding="utf-8") as fh:
            GATE_STOP = json.load(fh)
    arts, errs = load(ns.indir, mp)
    brs = load_brief_reviews(ns.brief_reviews or os.path.join(ev, "brief_review"), mp)
    for a in arts:
        for k in ("slug", "variant", "b3_rep", "writer_rep", "stages", "regressions"):
            if k not in a:
                print("schema欠落 %s: %s" % (a["_file"], k))
                sys.exit(2)
        if "s0_r0" not in a["stages"]:
            print("schema欠落 %s: stages.s0_r0(M3: R0記録)" % a["_file"])
            sys.exit(2)
    feats = None
    if os.path.isfile(fpath):
        with open(fpath, encoding="utf-8") as fh:
            feats = json.load(fh).get("briefs", {})
    res = {"variants": {}, "by_theme": {}}
    L = ["# B3_SUMMARY: B3 brief構造Trial (OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01)", "",
         "決定論集計(aggregate_b3.py)。評価判定は各記事JSONに従い再判定しない。", "", "## (g) 注意", NOTE, ""]
    L += ["## (a) 条件別(全テーマ合算)", HDR]
    for v in VARS:
        r = agg([a for a in arts if a["variant"] == v])
        res["variants"][v] = r
        L.append(row(v, r))
    for t in THEMES:
        L += ["", "### (a) テーマ別: %s" % t, HDR]
        res["by_theme"][t] = {}
        for v in VARS:
            r = agg([a for a in arts if a["variant"] == v and a["slug"] == t])
            res["by_theme"][t][v] = r
            L.append(row(v, r))
    # (b)
    L += ["", "## (b) brief間のばらつき(同条件 x 同テーマ内のb1〜b4。値=誤り件数(重大+軽微)の範囲 max-min、テーマ平均)",
          "Writerが1本/briefのためB3差とWriter差は分離できない(design_01 5-A4)。記述のみ。", "",
          "| 条件 | セル数(>=2記事) | ①JA b間範囲 | ②EN b間範囲 |", "|---|---|---|---|"]
    vs1, vs2 = variance_split(arts, "s1_ja"), variance_split(arts, "s2_en")
    res["variance"] = {"s1_ja": vs1, "s2_en": vs2}
    for v in VARS:
        L.append("| %s | %d | %s | %s |" % (v, vs2[v]["cells"], fr(vs1[v]["b_range"]), fr(vs2[v]["b_range"])))
    L += ["", "### WRITER_GATE_STOP(生成不能、母数除外、副次指標 5-A6。非盲検)", "",
          "| 条件 | 生成不能件数 | 期待run数 | 評価対象記事数 |", "|---|---|---|---|"]
    res["gate_stop"] = {}
    for v in VARS:
        gs = [k for k in GATE_STOP if k.split("/")[1] == v]
        na = sum(1 for a in arts if a["variant"] == v)
        res["gate_stop"][v] = {"gate_stop": len(gs), "articles": na}
        L.append("| %s | %d | %d | %d |" % (v, len(gs), len(THEMES) * len(BS), na))
    # (c)
    L += ["", "## (c) 設計の期待順位 V5>V3>V1/V2>V0>V6(誤りが少ない=良い順、参考。主判定は(h))に対する実測",
          "実測順位の指標=②EN 記事当たり (重大, 軽微) の辞書式昇順(重大が少ない方が上位、同数なら軽微が少ない方)。JAは参考列。", "",
          "| 条件 | ②EN 重大/記事 | ②EN 軽微/記事 | ①JA 重大/記事 | ①JA 軽微/記事 | EN実測順位 | 事前順位 |", "|---|---|---|---|---|---|---|"]
    key = {v: (res["variants"][v]["per"]["s2_major"] or 0, res["variants"][v]["per"]["s2_minor"] or 0) for v in VARS}
    rank = {v: 1 + sum(1 for u in VARS if key[u] < key[v]) for v in VARS}
    exp_rank, pos = {}, 1
    for grp in EXPECT:
        grp = [v for v in grp if v in VARS]  # V2は段階2に無いので除く
        for v in grp:
            exp_rank[v] = pos
        pos += len(grp)
    for v in VARS:
        p = res["variants"][v]["per"]
        L.append("| %s | %s | %s | %s | %s | %d | %d |" % (v, f(p["s2_major"]), f(p["s2_minor"]), f(p["s1_major"]), f(p["s1_minor"]), rank[v], exp_rank[v]))
    L += ["", "ペア比較(良い側が悪い側より②EN誤りが少ない=事前の読みと一致 / 同値 / 逆):", "", "| 良い | 悪い | 判定 |", "|---|---|---|"]
    pairs = {}
    for g, b in EXPECT_PAIRS:
        verdict = "一致" if key[g] < key[b] else ("同値" if key[g] == key[b] else "逆")
        pairs["%s<%s" % (g, b)] = verdict
        L.append("| %s | %s | %s |" % (g, b, verdict))
    res["expected_pairs"] = pairs
    res["en_rank"] = rank
    # (h) M3 事前登録比較
    L += ["", "## (h) 事前登録の比較(M3、Opus条件Aレビュー反映)",
          "差=左(処置)-右(基準)の記事当たり件数。判定規則: 3テーマ中2以上で『テーマ差の絶対値>=%.1f件/記事 かつ b1〜b4(比較可能なb)の差の過半数が同符号(非0)』かつ同方向 -> 傾向あり、同数・過半数不成立・それ以外 -> 未判定(5-A4)。*=そのテーマが規則を満たす。" % MIN_DIFF,
          "H2のscopeは ng_items.cross_fact=true(別fact連結由来)のみ数える。独立反復の単位はbrief(1条件6本)で、傾向は仮説判定でありProduction採否ではない。", ""]
    res["m3"] = {}
    for label, left, right in PAIRS_M3:
        L += ["### %s: %s 対 %s" % (label, left, right), "", "| 工程 | 指標 | %s 平均 | %s 平均 | 差 | テーマ別差(b1〜b4) | 判定 |" % (left, right), "|---|---|---|---|---|---|---|"]
        for sk, sf, sname in STAGES3:
            for mname, mf in METRICS:
                fn = (lambda a, sk=sk, sf=sf, mf=mf: mf(a, sk, sf))
                ml, mr = cell_mean(arts, left, None, None, fn), cell_mean(arts, right, None, None, fn)
                verdict, detail = judge_pair(arts, left, right, fn)
                res["m3"]["%s_vs_%s|%s|%s" % (left, right, sf, mname)] = verdict
                L.append("| %s | %s | %s | %s | %s | %s | %s |" % (sname, mname, f(ml), f(mr), "-" if ml is None or mr is None else "%+.2f" % (ml - mr), "; ".join(detail), verdict))
        L.append("")
    # (d)
    L += ["", "## (d) brief特徴量(条件別平均)と誤りの相関",
          "特徴量は brief_features.py(決定論)。brief品質は評価者の目視記録(brief単位、w1採用)。誤り=その記事の②EN重大+軽微。", ""]
    if feats is None:
        L.append("brief_features.json なし: 特徴量表はスキップ。")
    else:
        L += ["| 条件 | briefs | 採用fact数 | 行数 | 文字数 | 箇条書き数 | 12字一致率 | fact_id有 | Storyline行有 | ②EN誤り/記事 |", "|---|---|---|---|---|---|---|---|---|---|"]
        for v in VARS:
            bs = [x for k, x in feats.items() if k.split("|")[1] == v]
            gi = [a for a in arts if a["variant"] == v]

            def m(k, bs=bs):
                return f(mean([x[k] for x in bs if x.get(k) is not None]))
            L.append("| %s | %d | %s | %s | %s | %s | %s | %d/%d | %d/%d | %s |" % (
                v, len(bs), m("n_fact"), m("lines"), m("chars"), m("bullets"), m("ledger_12gram_rate"),
                sum(1 for x in bs if x.get("fact_id")), len(bs), sum(1 for x in bs if x.get("storyline_line_in_facts")), len(bs),
                f(mean([tot(a, "s2_en") for a in gi]))))
        L += ["", "相関(記事単位Pearson r。briefを共有する2記事は独立でない):", "", "| 特徴量 | n | r(②EN誤り) | r(①JA誤り) |", "|---|---|---|---|"]
        res["corr"] = {}
        for k in ("n_fact", "lines", "chars", "bullets", "ledger_12gram_rate"):
            xs, y2, y1 = [], [], []
            for a in arts:
                x = feats.get(bkey(a), {}).get(k)
                if x is None:
                    continue
                xs.append(float(x))
                y2.append(tot(a, "s2_en"))
                y1.append(tot(a, "s1_ja"))
            r2, r1 = pearson(xs, y2), pearson(xs, y1)
            res["corr"][k] = {"n": len(xs), "r_en": r2, "r_ja": r1}
            L.append("| %s | %d | %s | %s |" % (k, len(xs), fr(r2), fr(r1)))
    L += ["", "### brief品質(別インスタンスによる匿名brief目視記録、brief単位。単位=箇条書き1項目または句点区切り1文)", "",
          "| 条件 | briefs | 評価単位数/brief | 省略単位数/brief | 省略率(単位数加重) | 別fact限定語連結あり | 未提示チェックリスト明記 件/項目 | ②EN誤り/記事 |", "|---|---|---|---|---|---|---|---|"]
    res["brief_review"] = {}
    for v in VARS:
        ks = [k for k in brs if k.split("|")[1] == v]
        rs = [brs[k] for k in ks]
        ut = sum(r["units_total"] for r in rs)
        om = sum(r["omitted_units"] for r in rs)
        cf = sum(1 for r in rs if r["cross_fact_qualifier"])
        hits = [h for r in rs for h in r.get("unprovided_checklist_hits", [])]
        gi = [a for a in arts if a["variant"] == v]
        res["brief_review"][v] = {"briefs": len(rs), "units": ut, "omitted": om, "cross_fact": cf}
        L.append("| %s | %d | %s | %s | %s | %d/%d | %d/%d | %s |" % (v, len(rs), f(mean([r["units_total"] for r in rs])), f(mean([r["omitted_units"] for r in rs])),
                 ("%.3f" % (om / ut)) if ut else "-", cf, len(rs), sum(1 for h in hits if h.get("stated")), len(hits), f(mean([tot(a, "s2_en") for a in gi]))))
    xs, ys = [], []
    for a in arts:
        r = brs.get(bkey(a))
        if r and r["units_total"]:
            xs.append(float(r["omitted_rate"]))
            ys.append(tot(a, "s2_en"))
    L += ["", "省略率 vs ②EN誤り(記事単位) r = %s (n=%d)" % (fr(pearson(xs, ys)), len(xs))]
    # (e)
    L += ["", "## (e) 重大NG全件"]
    n = 0
    for a in sorted(arts, key=lambda a: (a["slug"], a["variant"], a["b3_rep"], a["writer_rep"])):
        for i in a.get("ng_items", []):
            if i["severity"] == "major":
                n += 1
                L += ["", "### %s (%s %s b%s w%s, fact %s, kind %s)" % (i["id"], a["slug"], a["variant"], a["b3_rep"], a["writer_rep"], i["fact_id"], i["kind"]),
                      "- 工程: JA=%s / EN=%s / 退行=%s" % ("あり" if i["stage"].get("s1") else "なし", "あり" if i["stage"].get("s2") else "なし",
                                                         "はい" if i.get("regression") else "いいえ"),
                      "- 該当文: " + i["text"]]
    L += ["", "重大NG %d 件" % n]
    ok, chk = check(arts, feats, brs)
    L += ["", "## (f) 検算"] + chk
    L.append(("- 読込エラー: " + "; ".join(errs)) if errs else "- 読込エラー: なし")
    L.append("- 総合: %s" % ("PASS" if ok and not errs else "FAIL"))
    pend = [(a["_file"], p) for a in arts for p in a.get("pending", [])]
    L += ["", "## 判定保留(集計外) %d 件" % len(pend)] + ["- %s: %s" % (fn, json.dumps(p, ensure_ascii=False)) for fn, p in pend]
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "B3_SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    res["check_pass"] = bool(ok and not errs)
    res["n_articles"] = len(arts)
    res["major_total"] = n
    with open(os.path.join(outdir, "b3_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("n=%d check=%s major=%d out=%s" % (len(arts), "PASS" if res["check_pass"] else "FAIL", n, outdir))


if __name__ == "__main__":
    main()
