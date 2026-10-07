#!/usr/bin/env python3
"""aggregate_matrix.py: note transfer matrix 集計(決定論・標準ライブラリのみ・API/生成なし)。
usage: python aggregate_matrix.py [--in DIR] [--out DIR]
既定 in =er052_output/open233_note_transfer_matrix_01/eval/articles, out=その親(eval/)
"""
import argparse, glob, json, os, sys

TS = ["T0", "T1", "T2"]
MS = ["M0", "M1"]
CELLS = [t + m for t in TS for m in MS]
THEMES = ["meta", "hormuz", "sewer"]
LABELS = ["correct", "ambiguous", "misread"]
NOTE = ("注意: 各セルN=2/テーマ(全テーマ合算でも6記事)の小標本であり、差が転記条件由来かrun揺れかは判別できない。"
        "重大/軽微の判定は単独評価で人間確認なし。本表は採否判断を含まない。")


def load(indir):
    arts, errs = [], []
    for p in sorted(glob.glob(os.path.join(indir, "*.json"))):
        try:
            with open(p, encoding="utf-8") as fh:
                a = json.load(fh)
            a["_file"] = os.path.basename(p)
            arts.append(a)
        except Exception as e:
            errs.append("%s: 読込失敗 %s" % (p, e))
    return arts, errs


def cell(a):
    return a["cond"]["T"] + a["cond"]["M"]


def agg(group):
    n = len(group)
    r = {"n": n}
    getters = (("s1_major", lambda a: a["stages"]["s1_ja"]["major"]),
               ("s1_minor", lambda a: a["stages"]["s1_ja"]["minor"]),
               ("s2_major", lambda a: a["stages"]["s2_en"]["major"]),
               ("s2_minor", lambda a: a["stages"]["s2_en"]["minor"]),
               ("reg_major", lambda a: a["regressions"]["major"]),
               ("reg_minor", lambda a: a["regressions"]["minor"]))
    for key, get in getters:
        r[key] = sum(get(a) for a in group)
    for lb in LABELS:
        r["f_" + lb] = sum(1 for a in group for d in a.get("direction_facts", []) if d["label"] == lb)
    r["per"] = {k: (round(v / n, 2) if n else None) for k, v in r.items() if k not in ("n", "per")}
    return r


def f(v):
    return "-" if v is None else "%.2f" % v


def row_cells(name, r):
    p = r["per"]
    return ("| %s | %d | %s / %s | %s / %s | %s / %s | %d / %d / %d (%s/%s/%s) |" % (
        name, r["n"], f(p["s1_major"]), f(p["s1_minor"]), f(p["s2_major"]), f(p["s2_minor"]),
        f(p["reg_major"]), f(p["reg_minor"]), r["f_correct"], r["f_ambiguous"], r["f_misread"],
        f(p["f_correct"]), f(p["f_ambiguous"]), f(p["f_misread"])))


HDR = ("| 区分 | 記事数 | ①JA 重大/軽微 (件/記事) | ②EN 重大/軽微 (件/記事) | R0->R2退行 重大/軽微 (件/記事) | "
       "★ 正しい/曖昧/重大誤読 (合計; 件/記事) |\n|---|---|---|---|---|---|")


def check(arts):
    out = []
    ok = True
    out.append("- 記事数 %d (期待36): %s" % (len(arts), "OK" if len(arts) == 36 else "NG"))
    ok &= len(arts) == 36
    allok = True
    for c in CELLS:
        for t in THEMES:
            k = sum(1 for a in arts if cell(a) == c and a["slug"] == t)
            if k != 2:
                allok = False
                ok = False
                out.append("- セル %s x %s = %d (期待2): NG" % (c, t, k))
    if allok:
        out.append("- 6セル x 3テーマ 全て2記事: OK")
    keys = [(a["slug"], cell(a), a["rep"]) for a in arts]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        ok = False
        out.append("- 重複(slug,cell,rep): %s NG" % dup)
    mism = False
    for a in arts:
        items = a.get("ng_items", [])
        for sk, sn in (("s1", "s1_ja"), ("s2", "s2_en")):
            for sev in ("major", "minor"):
                c = sum(1 for i in items if i["severity"] == sev and i["stage"].get(sk))
                if c != a["stages"][sn][sev]:
                    ok = False
                    mism = True
                    out.append("- 件数不一致 %s %s %s: stages=%d ng_items=%d NG" % (a["_file"], sn, sev, a["stages"][sn][sev], c))
        for sev in ("major", "minor"):
            c = sum(1 for i in items if i["severity"] == sev and i.get("regression"))
            if c != a["regressions"][sev]:
                ok = False
                mism = True
                out.append("- 件数不一致 %s regressions %s: 記録=%d ng_items=%d NG" % (a["_file"], sev, a["regressions"][sev], c))
        ids = [i["id"] for i in items]
        if len(ids) != len(set(ids)):
            ok = False
            mism = True
            out.append("- ng_items ID重複 %s NG" % a["_file"])
    out.append("- ng_items vs stages/regressions 照合: %s" % ("不一致あり(上記)" if mism else "全記事OK"))
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="indir", default="er052_output/open233_note_transfer_matrix_01/eval/articles")
    ap.add_argument("--out", dest="outdir", default=None)
    ns = ap.parse_args()
    outdir = ns.outdir or os.path.dirname(os.path.normpath(ns.indir))
    arts, errs = load(ns.indir)
    for a in arts:
        for k in ("slug", "cond", "rep", "stages", "regressions"):
            if k not in a:
                print("schema欠落 %s: %s" % (a["_file"], k))
                sys.exit(2)
    L = ["# MATRIX_SUMMARY: 転記方式 x 多義語注意 マトリクス (OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01)", "",
         "決定論集計(aggregate_matrix.py)。評価判定は各記事JSONに従い再判定しない。", "", "## (f) 注意", NOTE, ""]
    res = {"cells": {}, "by_theme": {}, "main_T": {}, "main_M": {}}
    L += ["## (a) 6セル別(全テーマ合算)", HDR]
    for c in CELLS:
        r = agg([a for a in arts if cell(a) == c])
        res["cells"][c] = r
        L.append(row_cells(c, r))
    for t in THEMES:
        L += ["", "### (a) テーマ別: %s" % t, HDR]
        res["by_theme"][t] = {}
        for c in CELLS:
            r = agg([a for a in arts if cell(a) == c and a["slug"] == t])
            res["by_theme"][t][c] = r
            L.append(row_cells(c, r))
    L += ["", "## (b) 主効果(1記事当たり平均)", "", "### T別(M合算)", HDR]
    for t in TS:
        r = agg([a for a in arts if a["cond"]["T"] == t])
        res["main_T"][t] = r
        L.append(row_cells(t, r))
    L += ["", "### M別(T合算)", HDR]
    for m in MS:
        r = agg([a for a in arts if a["cond"]["M"] == m])
        res["main_M"][m] = r
        L.append(row_cells(m, r))
    L += ["", "## (c) 並記: P2相当(T2M1) / 従来相当(T1M0) / 転記なし(T0M0)", HDR]
    for c, nm in (("T2M1", "P2相当 T2M1"), ("T1M0", "従来相当 T1M0"), ("T0M0", "転記なし T0M0")):
        L.append(row_cells(nm, res["cells"][c]))
    L += ["", "## (d) 重大NG全件"]
    n = 0
    for a in sorted(arts, key=lambda a: (a["slug"], cell(a), a["rep"])):
        for i in a.get("ng_items", []):
            if i["severity"] == "major":
                n += 1
                L += ["", "### %s (%s %s rep%s, fact %s, kind %s)" % (i["id"], a["slug"], cell(a), a["rep"], i["fact_id"], i["kind"]),
                      "- 工程: JA=%s / EN=%s / 退行=%s" % ("あり" if i["stage"].get("s1") else "なし",
                                                         "あり" if i["stage"].get("s2") else "なし",
                                                         "はい" if i.get("regression") else "いいえ"),
                      "- 該当文: " + i["text"]]
    L += ["", "重大NG %d 件" % n]
    ok, chk = check(arts)
    L += ["", "## (e) 検算"] + chk
    L.append(("- 読込エラー: " + "; ".join(errs)) if errs else "- 読込エラー: なし")
    L.append("- 総合: %s" % ("PASS" if ok and not errs else "FAIL"))
    pend = [(a["_file"], p) for a in arts for p in a.get("pending", [])]
    L += ["", "## 判定保留(集計外) %d 件" % len(pend)]
    L += ["- %s: %s" % (fn, json.dumps(p, ensure_ascii=False)) for fn, p in pend]
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "MATRIX_SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    res["check_pass"] = bool(ok and not errs)
    res["n_articles"] = len(arts)
    res["major_total"] = n
    with open(os.path.join(outdir, "matrix_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("n=%d check=%s major=%d out=%s" % (len(arts), "PASS" if res["check_pass"] else "FAIL", n, outdir))


if __name__ == "__main__":
    main()
