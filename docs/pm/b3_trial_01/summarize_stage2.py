#!/usr/bin/env python3
"""summarize_stage2.py: 段階3(C1) 追加集計(決定論・API無し)。aggregate_b3の関数を再利用し、条件x テーマ表・pending・Gate STOP・brief_review・感度分析を出力。
usage: python summarize_stage2.py  -> eval/SUMMARY_STAGE2.md(本体)にB3_SUMMARY.mdの(h)節を同梱するための追加節を stdout/ファイルへ出す"""
import json, glob, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import aggregate_b3 as A
EV = "er052_output/open233_b3_trial_01/eval"
mp = A.load_map(EV + "/_private/MAP_stage2.json")
arts, errs = A.load(EV + "/articles", mp)
brs = A.load_brief_reviews(EV + "/brief_review", mp)
gs = json.load(open("er052_output/open233_b3_trial_01/runs/writer_gate_stop_final.json", encoding="utf-8"))
V, T = A.VARS, A.THEMES
def g(v, t=None): return [a for a in arts if a["variant"] == v and (t is None or a["slug"] == t)]
def cnt(xs):
    n = len(xs)
    mj = sum(a["stages"]["s2_en"]["major"] for a in xs); mn = sum(a["stages"]["s2_en"]["minor"] for a in xs)
    rg = sum(a["regressions"]["major"] + a["regressions"]["minor"] for a in xs)
    pd = sum(len(a.get("pending", [])) for a in xs)
    f = lambda x: "%d(%.2f)" % (x, x / n) if n else "-"
    return "| %d | %s | %s | %s | %s |" % (n, f(mj), f(mn), f(rg), f(pd))
L = ["### ① 条件別 x テーマ別(②EN基準。件数(1記事平均))", "", "| 条件 | テーマ | 評価記事数 | 重大NG | 軽微NG | 退行(R0->R2, 重大+軽微) | 保留(pending) |", "|---|---|---|---|---|---|---|"]
for v in V:
    for t in T + [None]:
        L.append("| %s | %s %s" % (v, t or "全体", cnt(g(v, t))))
L += ["", "### ② Gate STOP(記事生成不能)条件別(非盲検、5-A6副次指標)", "", "| 条件 | 生成不能/12 | 内訳 |", "|---|---|---|"]
for v in V:
    ks = [k for k in gs if k.split("/")[1] == v]
    L.append("| %s | %d | %s |" % (v, len(ks), ", ".join(ks) or "-"))
L += ["", "### ③ brief_review 条件別x テーマ別", "", "| 条件 | テーマ | briefs | 省略率(単位加重) | cross_fact_qualifier率 | 未提示チェックリスト命中(明記/項目) |", "|---|---|---|---|---|---|"]
for v in V:
    for t in T + [None]:
        rs = [r for k, r in brs.items() if k.split("|")[1] == v and (t is None or k.split("|")[0] == t)]
        ut = sum(r["units_total"] for r in rs); om = sum(r["omitted_units"] for r in rs)
        cf = sum(1 for r in rs if r["cross_fact_qualifier"])
        h = [x for r in rs for x in r.get("unprovided_checklist_hits", [])]; hs = sum(1 for x in h if x.get("stated"))
        L.append("| %s | %s | %d | %.3f (%d/%d) | %.2f (%d/%d) | %.2f (%d/%d) |" % (v, t or "全体", len(rs), om / ut if ut else 0, om, ut, cf / len(rs), cf, len(rs), hs / len(h) if h else 0, hs, len(h)))
# 感度分析
L += ["", "### 感度分析(事前登録外の補助情報): 境界判断を重大側に倒した場合", "",
      "評価JSONは修正しない。(S-a)全ての軽微NGと保留(pending)を重大扱い=『重大扱い件数=軽微+保留』を②ENで数える(保留は工程を持たないため記事単位1回計上、工程非依存の上限側の見積り)。(S-b)同指標で事前登録の判定規則(テーマ差>=0.5かつb1〜b4多数同符号、3テーマ中2以上同方向)を適用。", "",
      "| 条件 | 評価記事数 | ②EN 軽微(=重大扱い候補)/記事 | 保留/記事 | 合算(重大扱い)/記事 |", "|---|---|---|---|---|"]
fn = lambda a: a["stages"]["s2_en"]["major"] + a["stages"]["s2_en"]["minor"] + len(a.get("pending", []))
for v in V:
    xs = g(v); n = len(xs)
    L.append("| %s | %d | %.2f | %.2f | %.2f |" % (v, n, sum(a["stages"]["s2_en"]["minor"] for a in xs) / n, sum(len(a.get("pending", [])) for a in xs) / n, sum(fn(a) for a in xs) / n))
L += ["", "| 比較(処置 対 基準) | 事前登録指標(②EN合計)の判定 | S-b(②EN合計+保留)の判定 |", "|---|---|---|"]
base = lambda a: A.tot(a, "s2_en")
for lab, l, r in A.PAIRS_M3:
    L.append("| %s: %s 対 %s | %s | %s |" % (lab, l, r, A.judge_pair(arts, l, r, base)[0], A.judge_pair(arts, l, r, fn)[0]))
print("\n".join(L))
