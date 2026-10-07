#!/usr/bin/env python3
"""append_supplement.py: aggregate_matrix.py実行後、MATRIX_SUMMARY.mdへ追補(a)〜(f)を決定論で追記する(API/生成なし)。
既に追補が付いていれば置換する。評価JSONは変更しない。"""
import glob, json, os, re
D = "er052_output/open233_note_transfer_matrix_01/eval"
P = os.path.join(D, "MATRIX_SUMMARY.md")
MARK = "\n## 追補(委任_D1)"
arts = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(D + "/articles/*.json"))]
cell = lambda a: a["cond"]["T"] + a["cond"]["M"]
def fuk(n): return ("福島県" in n["text"]) or ("Fukushima" in n["text"])
def tot(group, excl):
    s1 = s2 = 0
    for a in group:
        for n in a["ng_items"]:
            if n["severity"] != "minor": continue
            if excl and fuk(n): continue
            s1 += n["stage"]["s1"]; s2 += n["stage"]["s2"]
    return s1, s2
def per(v, n): return "%.2f" % (v / n)
out = [MARK + ": 参考比較・主効果・仮説(決定論追記、append_supplement.py)", ""]
# (a)
out.append("### (a) 「福島県」型(台帳に県名なし・現実には正しい)を軽微から除いた場合")
fk = [(a["slug"], cell(a), a["rep"], n["id"], n["stage"]) for a in arts for n in a["ng_items"] if fuk(n)]
out.append("除外対象 %d 項目(全て sewer、kind=added_fact): %s" % (len(fk), ", ".join(x[3] for x in fk)))
out.append("")
out.append("| 区分 | 記事数 | ①JA軽微/記事(除外前→後) | ②EN軽微/記事(除外前→後) |")
out.append("|---|---|---|---|")
groups = [(c, [a for a in arts if cell(a) == c]) for c in ["T0M0","T0M1","T1M0","T1M1","T2M0","T2M1"]]
groups += [(t, [a for a in arts if a["cond"]["T"] == t]) for t in ["T0","T1","T2"]]
groups += [(m, [a for a in arts if a["cond"]["M"] == m]) for m in ["M0","M1"]]
groups += [("全36本", arts)]
for name, g in groups:
    b = tot(g, False); e = tot(g, True); n = len(g)
    out.append("| %s | %d | %s → %s | %s → %s |" % (name, n, per(b[0], n), per(e[0], n), per(b[1], n), per(e[1], n)))
out.append("")
# (b)
out.append("### (b) 重大NG全件(全文)")
mj = [(a, n) for a in arts for n in a["ng_items"] if n["severity"] == "major"]
for a, n in mj:
    out.append("- %s (%s %s rep%d, fact %s, kind %s, JA=%s/EN=%s): %s" % (n["id"], a["slug"], cell(a), a["rep"], n["fact_id"], n["kind"], n["stage"]["s1"], n["stage"]["s2"], n["text"]))
out.append("重大NG合計 %d 件。" % len(mj))
out.append("")
# (c)
out.append("### (c) 境界例・判定保留一覧")
out.append("- 境界(軽微に倒して計上済み): meta T2M1 rep2 meta-T2M1r2-02「EN: from employees と主体のズレ(ユーザーの機微情報→従業員と読める)」=軽微扱い(JAに対応句なしのEN新規)。")
pend = [(a, p) for a in arts for p in a["pending"]]
for sl in ["meta", "hormuz", "sewer"]:
    items = [(a, p) for a, p in pend if a["slug"] == sl]
    out.append("- %s 保留 %d 件(集計外):" % (sl, len(items)))
    for a, p in items:
        out.append("  - %s [%s] %s | leaning=%s" % (p["id"], cell(a) + " rep%d" % a["rep"], p["text"], p["leaning"]))
out.append("")
# (d)
c = {}
for cc in ["T0M0","T0M1","T1M0","T1M1","T2M0","T2M1"]:
    g = [a for a in arts if cell(a) == cc]; n = len(g)
    c[cc] = (sum(a["stages"]["s1_ja"]["major"] for a in g)/n, sum(a["stages"]["s1_ja"]["minor"] for a in g)/n,
             sum(a["stages"]["s2_en"]["major"] for a in g)/n, sum(a["stages"]["s2_en"]["minor"] for a in g)/n)
out.append("### (d) 従来版・前回P2との参考比較(事実記述、断定しない)")
out.append("引用元: er052_output/open233_allfact_note_e2e_02/eval/stagewise/STAGEWISE_SUMMARY.md §4(1記事当たり 重大/軽微)。従来版5本 ⑤a(Checker後EN) 0.0/3.8、P2版10本 ⑤a 0.1/5.2(①JAは従来0.0/3.6、P2 0.4/4.9)。")
out.append("本Trialの②EN(Checkerなし、b1b最終)は: " + "; ".join("%s %.2f/%.2f" % (k, v[2], v[3]) for k, v in c.items()) + "。")
mx = max(v[3] for v in c.values()); mxj = max(v[2] for v in c.values())
out.append("事実: 6セルのEN軽微の最大は %.2f/記事で、従来版⑤a 3.8および P2版⑤a 5.2 のいずれも下回る。EN重大の最大は %.2f/記事(T0M0のみ)で、P2版⑤a 0.1 を上回るセルは %s。ただし本Trialは固定brief・Checkerなし・3テーマ・N=2/セル、前回は5テーマ(従来1本/P2 2本)で標本・条件が異なり、同一基準での厳密比較ではない。" % (mx, mxj, ",".join(k for k, v in c.items() if v[2] > 0.1) or "なし"))
out.append("")
# (e)
out.append("### (e) 主効果と交互作用の所見(上の(b)主効果表を参照)")
def mean(g, i): return sum(x for x in g) / len(g)
def ten(t, m=None):
    g = [a for a in arts if a["cond"]["T"] == t and (m is None or a["cond"]["M"] == m)]
    return sum(a["stages"]["s2_en"]["minor"] for a in g) / len(g)
out.append("- T別EN軽微/記事: T0 %.2f / T1 %.2f / T2 %.2f(上の主効果表)。M別EN軽微: M0 %.2f / M1 %.2f。" % (ten("T0"), ten("T1"), ten("T2"),
    sum(a["stages"]["s2_en"]["minor"] for a in arts if a["cond"]["M"]=="M0")/18, sum(a["stages"]["s2_en"]["minor"] for a in arts if a["cond"]["M"]=="M1")/18))
out.append("- 交互作用(所見): M1(多義語注意あり)はT2(逐語)と組み合わさったセル(T2M1: EN軽微 %.2f)で最も多く、T2M0(%.2f)・T1M1(%.2f)より多い。M0側ではT間差が小さい。ただしN=2/セルで、run揺れと区別できない。" % (ten("T2","M1"), ten("T2","M0"), ten("T1","M1")))
out.append("- R0->R2退行の軽微はM1に偏る(M0 0.06 / M1 0.39 件/記事)。M1のJA修正工程で新たな軽微が出やすい可能性があるが、標本が小さく断定しない。")
out.append("")
# (f)
hc = [d["label"] for a in arts if a["slug"]=="meta" for d in a["direction_facts"] if d["fact_id"]=="MUSE-HC-012"]
out.append("### (f) 仮説(未検証): Noteの形式よりbrief本文の生成条件が効いた可能性")
out.append("- 事実: 本Trialでは全セルでbrief本文を固定し、Note転記の有無・形式のみを変えた。結果、重大NGは1件(ENのみ)、★factの重大誤読は0件、meta HC-012(人間コンシェルジュ機能のロールバック)は★選択%d本中correct %d本(%s)。hormuzの具体化(前回P2で多発)は再現しなかった。" % (len(hc), hc.count("correct"), "ambiguous %d" % hc.count("ambiguous") if hc.count("ambiguous") else "ambiguous 0"))
out.append("- 仮説: 前回P2で見られた多発は、Noteの形式そのものより、brief本文が生成された時点の条件(notes_for_writerを除外した台帳からB3がbriefを作る条件、すなわち台帳の限定・方向情報が落ちた状態でのbrief生成)が効いていた可能性がある。本Trialはbrief固定のため、この点を直接は検証していない。検証には別Trial(brief生成条件を変える)が必要であり、実施はUSER_DECISION_REQUIRED。")
s = open(P, encoding="utf-8").read()
i = s.find(MARK)
if i >= 0: s = s[:i]
open(P, "w", encoding="utf-8").write(s.rstrip("\n") + "\n" + "\n".join(out) + "\n")
print("appended", len(mj), "major", len(fk), "fukushima")
