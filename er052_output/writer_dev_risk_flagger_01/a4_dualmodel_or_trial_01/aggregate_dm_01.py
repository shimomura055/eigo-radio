# -*- coding: utf-8 -*-
"""A4-DUALMODEL-OR-TRIAL-01 集計(API呼び出しなし)。PREREGISTRATION_01.md 7節の定義のみ。Human判定は不使用(Blind)。"""
import json, os, glob, collections
H = os.path.dirname(os.path.abspath(__file__)); PE = os.path.join(H, "..", "post_en_trial_01")
man = json.load(open(os.path.join(PE, "manifest_post_en_01.json"), encoding="utf-8"))
UN = [u["unit"] for u in man["units"]]; THEME = {u["unit"]: u["theme"] for u in man["units"]}
def sk(s): return int(s[1:])
def key(k): return (k[0], sk(k[1]))
# ---- 既存Sol(POST-EN)
SOL = {3: {}, 4: {}}; SENT = {}; FACTS = {}
for lv in (3, 4):
    for u in UN:
        p = glob.glob(os.path.join(PE, "flags", "A%d" % lv, u + "_*.json")); assert len(p) == 1
        d = json.load(open(p[0], encoding="utf-8")); SENT[u] = d["sentences"]; FACTS[u] = d["facts"]
        SOL[lv][u] = d["flags"]
# ---- 新規(Luna/Gemini)
MK = {"luna": "Luna", "gemini35fl": "Gemini 3.5 Flash-Lite"}
RUN = {}
for m in MK:
    for lv in (3, 4):
        for u in UN:
            d = json.load(open(os.path.join(H, "runs", m, u, "A%d.json" % lv), encoding="utf-8")); RUN[(m, lv, u)] = d
            assert d["sentences"] == SENT[u] and d["facts"] == FACTS[u]
CONDS = [("luna", 3), ("gemini35fl", 3), ("luna", 4), ("gemini35fl", 4)]
CN = {("luna", 3): "Luna A3", ("gemini35fl", 3): "Gemini A3", ("luna", 4): "Luna A4", ("gemini35fl", 4): "Gemini A4", ("sol", 3): "Sol A3(既存)", ("sol", 4): "Sol A4(既存)"}
def flags_of(c):
    """cond -> {(unit,sid): [flag,...]}。出力無効の回は含めず invalid に記録。"""
    m, lv = c; out = collections.OrderedDict(); inv = []
    for u in UN:
        if m == "sol": fl = SOL[lv][u]
        else:
            d = RUN[(m, lv, u)]
            if not d["valid_json"]: inv.append(u); continue
            fl = d["flags"]
        for f in fl: out.setdefault((u, f["sentence_id"]), []).append(f)
    return out, inv
F = {}; INV = {}
ALL6 = CONDS + [("sol", 3), ("sol", 4)]
for c in ALL6: F[c], INV[c] = flags_of(c)
def S(c): return set(F[c])
UNION29 = sorted(S(("sol", 3)) | S(("sol", 4)), key=key); assert len(UNION29) == 29, len(UNION29)
UID = {k: "%s-%s" % k for k in UNION29}
A3OR = S(("luna", 3)) | S(("gemini35fl", 3)); A4OR = S(("luna", 4)) | S(("gemini35fl", 4))
BUNDLE = {"U03": [["s1", "s5", "s13", "s33"], ["s17"]], "U04": [["s7", "s15"]], "U06": [["s8", "s9"]], "X11": [["s4", "s17"]]}
def n_issues(keys):
    seen = set(); n = 0
    for (u, s) in sorted(keys, key=key):
        b = next((tuple(x) for x in BUNDLE.get(u, []) if s in x), None)
        k = (u, b) if b else (u, s)
        if k not in seen: seen.add(k); n += 1
    return n
def trunc(s, n):
    s = (s or "").replace("\n", " ").replace("|", "/")
    return s if len(s) <= n else s[:n] + "…"
def facts_of(k, conds):
    return sorted({x for c in conds for f in F[c].get(k, []) for x in f["fact_ids"]})
def fcell(c, k):
    fl = F[c].get(k)
    if not fl: return "-"
    return "; ".join("%s %.2f" % (f["type"], f["confidence"]) for f in fl)
def inv_note(c): return "(出力無効: %s)" % ",".join(INV[c]) if INV[c] else ""
# ---- 費用・retry・無効
cost = {}; retry = {}; models_ret = {}
for m in MK:
    ds = [RUN[(m, lv, u)] for lv in (3, 4) for u in UN]
    cost[m] = dict(jpy=round(sum(d["cost_jpy"] for d in ds), 3), n_calls=len(ds), in_tok=sum(x["input_tokens"] for d in ds for x in d["usage"]), out_tok=sum(x["output_tokens"] for d in ds for x in d["usage"]),
                   reasoning_tok=sum((x.get("reasoning_tokens") or 0) for d in ds for x in d["usage"]), n_http_calls=sum(len(d["usage"]) for d in ds))
    retry[m] = dict(cells_attempts_gt1=[(d["unit"], d["level"], d["attempts"]) for d in ds if d["attempts"] > 1], transient_errors=[(d["unit"], d["level"], e[:160]) for d in ds for e in d["errors"]],
                    invalid_cells=[(d["unit"], d["level"], d["violations"]) for d in ds if not d["valid_json"]])
    models_ret[m] = sorted({x for d in ds for x in d["model_ids_returned"]}); cost[m]["models_returned"] = models_ret[m]
total_cost = round(sum(v["jpy"] for v in cost.values()), 3)
EST = dict(luna_central=4.4, luna_high=9.4, gemini_central=5.9, gemini_high=24.2, total_central=10.3, total_high=33.6)
# ---- 表2
def row2(label, cs):
    keys = set().union(*[S(c) for c in cs]); raw = sum(len(v) for c in cs for v in F[c].values())
    mn = [k for k in keys if k in UID]; new = [k for k in keys if k not in UID]
    return dict(cond=label, raw_flags=raw, sentence_unique=len(keys), semantic_issues=n_issues(keys), union29_matched=len(mn), unreviewed_new=len(new), per_article_avg_sentence=round(len(keys) / 11, 2), per_article_avg_issue=round(n_issues(keys) / 11, 2),
                invalid_cells=sum(len(INV[c]) for c in cs))
T2 = [row2("Luna A4", [("luna", 4)]), row2("Gemini A4", [("gemini35fl", 4)]), row2("A4-OR(Luna A4 ∪ Gemini A4)", [("luna", 4), ("gemini35fl", 4)]), row2("参考: Sol A4(既存)", [("sol", 4)]),
      row2("Luna A3", [("luna", 3)]), row2("Gemini A3", [("gemini35fl", 3)]), row2("A3-OR(Luna A3 ∪ Gemini A3)", [("luna", 3), ("gemini35fl", 3)]), row2("参考: Sol A3(既存)", [("sol", 3)]),
      row2("参考: Sol A3∪A4(既存Union)", [("sol", 3), ("sol", 4)]), row2("参考: 4条件全部(A3-OR ∪ A4-OR)", CONDS)]
# ---- 表1
T1 = []
for k in sorted(A3OR, key=key):
    T1.append(dict(issue="%s %s" % (k[0], k[1]), key=list(k), related_facts=facts_of(k, CONDS), union29_id=UID.get(k), luna_a3=fcell(("luna", 3), k), gem_a3=fcell(("gemini35fl", 3), k), luna_a4=fcell(("luna", 4), k), gem_a4=fcell(("gemini35fl", 4), k),
                   in_a4_or=k in A4OR, a3_only=k not in A4OR, sentence=SENT[k[0]][k[1]]))
n_a3_only = sum(1 for r in T1 if r["a3_only"])
# ---- 表1b: Sol A3 flag
T1B = []
for k in sorted(S(("sol", 3)), key=key):
    T1B.append(dict(key=list(k), union29_id=UID[k], sol_a3=fcell(("sol", 3), k), sol_a4_too=k in F[("sol", 4)], luna_a4=k in F[("luna", 4)], gem_a4=k in F[("gemini35fl", 4)], a4_or=k in A4OR,
                    luna_a3=k in F[("luna", 3)], gem_a3=k in F[("gemini35fl", 3)], a3_or=k in A3OR))
sol3_total = len(T1B); cov_or = sum(1 for r in T1B if r["a4_or"]); cov_l = sum(1 for r in T1B if r["luna_a4"]); cov_g = sum(1 for r in T1B if r["gem_a4"])
sol3_only = [r for r in T1B if not r["sol_a4_too"]]
sol4_total = len(S(("sol", 4))); sol4_cov_or = sum(1 for k in S(("sol", 4)) if k in A4OR)
sol_u_cov_or = sum(1 for k in UNION29 if k in A4OR); sol_u_cov_l = sum(1 for k in UNION29 if k in F[("luna", 4)]); sol_u_cov_g = sum(1 for k in UNION29 if k in F[("gemini35fl", 4)])
# ---- 表3
def t3(a, b):
    out = []
    for k in sorted(S(a) - S(b), key=key):
        fl = F[a][k]
        out.append(dict(key=list(k), related_facts=sorted({x for f in fl for x in f["fact_ids"]}), reason=fl[0]["question"], types=[f["type"] for f in fl], confidence=[f["confidence"] for f in fl], union29_id=UID.get(k), unreviewed=k not in UID, sentence=SENT[k[0]][k[1]]))
    return out
T3L = t3(("luna", 4), ("gemini35fl", 4)); T3G = t3(("gemini35fl", 4), ("luna", 4))
both_a4 = sorted(S(("luna", 4)) & S(("gemini35fl", 4)), key=key)
# ---- 未評価
newkeys = sorted({k for c in CONDS for k in F[c] if k not in UID}, key=key)
NEW = []
for i, k in enumerate(newkeys, 1):
    u, s = k; n = sk(s); sent = SENT[u]
    ctx = {("s%d" % j): sent.get("s%d" % j) for j in range(n - 2, n + 3) if "s%d" % j in sent}
    cs = [c for c in CONDS if k in F[c]]
    NEW.append(dict(id="N%02d" % i, key=list(k), article=u, theme=THEME[u], sentence=sent[s], context=ctx, facts={x: FACTS[u][x] for x in facts_of(k, CONDS) if x in FACTS[u]},
                    flags=[dict(cond=CN[c], type=f["type"], confidence=f["confidence"], reason=f["question"], fact_ids=f["fact_ids"]) for c in cs for f in F[c][k]]))
# ---- 照合パケット
MP = []
for c in ALL6:
    for k in sorted(F[c], key=key):
        for f in F[c][k]:
            MP.append(dict(cond=CN[c], article=k[0], sid=k[1], type=f["type"], confidence=f["confidence"], fact_ids=f["fact_ids"], union29_id=UID.get(k), status="既存Union29一致" if k in UID else "未評価(新規)"))
union_match = {UID[k]: {CN[c]: (k in F[c]) for c in ALL6} for k in UNION29}
# ---- META参考
xm = json.load(open(os.path.join(H, "..", "meta_rollback_crossmodel_01", "aggregate_xm_01.json"), encoding="utf-8"))
META_REF = {k: dict(closeout=xm["models"][k]["closeout"], A3=xm["models"][k]["levels"]["A3"]["s23_class"], A4=xm["models"][k]["levels"]["A4"]["s23_class"]) for k in ("luna", "gemini35fl")}
agg = dict(task="WRITER-RISK-FLAGGER-A4-DUALMODEL-OR-TRIAL-01", n_articles=11, union29=[UID[k] for k in UNION29], table1=T1, a3_only_count=n_a3_only, table1b=T1B,
           sol_a3_total=sol3_total, sol_a3_cov_a4or=cov_or, sol_a3_cov_luna_a4=cov_l, sol_a3_cov_gem_a4=cov_g, sol_a3_only_not_in_sol_a4=len(sol3_only), sol_a3_only_covered=sum(1 for r in sol3_only if r["a4_or"]),
           sol_a4_total=sol4_total, sol_a4_cov_a4or=sol4_cov_or, union29_cov_a4or=sol_u_cov_or, union29_cov_luna_a4=sol_u_cov_l, union29_cov_gem_a4=sol_u_cov_g,
           table2=T2, table3_luna_only=T3L, table3_gem_only=T3G, a4_both=[list(k) for k in both_a4], unreviewed=NEW, union_match=union_match, matching_packet_rows=len(MP),
           cost=cost, total_cost_jpy=total_cost, estimate=EST, retry=retry, invalid={CN[c]: INV[c] for c in CONDS}, meta_rollback_ref=META_REF,
           flags={CN[c]: [dict(article=k[0], sid=k[1], type=f["type"], confidence=f["confidence"], fact_ids=f["fact_ids"], reason=f["question"], sentence=f["sentence"]) for k in sorted(F[c], key=key) for f in F[c][k]] for c in ALL6})
json.dump(agg, open(os.path.join(H, "aggregate_dm_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(dict(note="全Flag x 4条件(+既存Sol)を既存Union 29のIDへ突合。Human判定は含まない(Blind)。", union29=[UID[k] for k in UNION29], union_match=union_match, rows=MP),
          open(os.path.join(H, "matching_packet_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# ---- matching_packet_01.md
M = ["# matching_packet_01: 全Flag x 4条件 -> 既存Union 29 ID 突合(Human判定なし、Blind)", "",
     "主キー=(記事ID, 文ID)。type差は別issueにしない。ChatGPT側でUser判定(A/B/C/D)と照合するための突合表。", "",
     "## 1. Union 29 x 条件(○=その条件がFlag)", "", "| Union29 ID | " + " | ".join(CN[c] for c in ALL6) + " | A3-OR | A4-OR |", "|---|" + "---|" * (len(ALL6) + 2)]
for k in UNION29:
    M.append("| %s | " % UID[k] + " | ".join("○" if k in F[c] else "-" for c in ALL6) + " | %s | %s |" % ("○" if k in A3OR else "-", "○" if k in A4OR else "-"))
M += ["", "## 2. 未評価(Union 29に無い新規Flag。N-IDはRESULT_01.md/unreviewed_packet_01.md)", "", "| N-ID | 記事-文 | 条件 |", "|---|---|---|"]
for n in NEW: M.append("| %s | %s-%s | %s |" % (n["id"], n["key"][0], n["key"][1], ", ".join(sorted({f["cond"] for f in n["flags"]}))))
M += ["", "## 3. 全Flag行(%d行)" % len(MP), "", "| 条件 | 記事 | 文 | type | conf | Fact | Union29 ID/状態 |", "|---|---|---|---|---|---|---|"]
for r in MP: M.append("| %s | %s | %s | %s | %.2f | %s | %s |" % (r["cond"], r["article"], r["sid"], r["type"], r["confidence"], ",".join(r["fact_ids"]) or "(なし)", r["union29_id"] or "未評価"))
open(os.path.join(H, "matching_packet_01.md"), "w", encoding="utf-8").write("\n".join(M) + "\n")
# ---- RESULT_01.md
R = ["# RESULT_01: WRITER-RISK-FLAGGER-A4-DUALMODEL-OR-TRIAL-01 結果(Trial/DEV、2026-10-10)", "",
     "**Status提案: USER_DECISION_REQUIRED**(ChatGPT側でUser A/B/C/D判定と照合後に判定)。Claude側はBlind(Human判定不使用)。A3を外せるかの最終判定は確定しない。APPROVED項目Status不変更、Production変更ゼロ、やらないこと9項目未実施。", "",
     "## 0. 非エンジニア向け3点", "",
     "- **A: A3を外せそうか** = Claude側では未確定(Human照合待ち)。機械的事実: A3-ORのみ検出(A4-ORでは拾えない)= **%d件**(A3-OR全 %d文のうち)。既存Sol A3 Flag %d文のうちA4-ORで拾えたのは %d文(Luna A4 %d / Gemini A4 %d)。既存Union 29のうちA4-ORで拾えたのは %d文。" % (n_a3_only, len(A3OR), sol3_total, cov_or, cov_l, cov_g, sol_u_cov_or),
     "- **B: Human Review量の変化** = A4-OR は %d文(%d issue、1記事平均 %.2f文)。参考: Sol A4(既存)%d文、Sol A3∪A4(既存Union)29文(2.64文/記事)。新規(未評価)Flagは %d文。" % (T2[2]["sentence_unique"], T2[2]["semantic_issues"], T2[2]["per_article_avg_sentence"], T2[3]["sentence_unique"], len(NEW)),
     "- **C: 推奨次判断**: ChatGPT側で matching_packet_01.md と User判定(A/B/C/D)を照合し、A3-OR/A4-ORで失う有用Flag(A/B)の有無を確認したうえで、A3省略の可否を判断する(Production採用判断はしない)。", "",
     "## 1. 実施概要", "",
     "- 評価セット: POST-EN-TRIAL-01 英語稿11本(U01-U08, X09-X11)。A3 sha `9d995042…` / A4 sha `c87b95e5…`、既存raw requestと記事ごとに system/user 完全一致(dry-run assert 22/22、`dry_run/dry_run_report_01.json`)。",
     "- 実行: Luna(`gpt-6-luna`, effort=medium) 22 call、Gemini(`gemini-3.5-flash-lite`, Provider既定thinking) 22 call。既存Sol A3/A4(22 call)は再実行せず補助指標。",
     "- 出力無効: %s。" % (json.dumps({CN[c]: INV[c] for c in CONDS if INV[c]}, ensure_ascii=False) if any(INV[c] for c in CONDS) else "なし(44 cell全て valid JSON)"),
     "- retry: " + "; ".join("%s: attempts>1 のセル %s、transient例外 %d件" % (MK[m], retry[m]["cells_attempts_gt1"] or "0件", len(retry[m]["transient_errors"])) for m in MK) + "。",
     "", "## 2. 使用モデル(PM_GOVERNANCE 25節)", "",
     "| 条件 | 指定model_id | API応答のmodel | 最新か | 最新でない場合の理由 |", "|---|---|---|---|---|",
     "| Luna | `gpt-6-luna` | %s | 現行世代のLuna(OpenAI効率系。ユーザー指定条件) | 該当なし(旧世代 gpt-5.6-luna は不使用) |" % ", ".join(models_ret["luna"]),
     "| Gemini | `gemini-3.5-flash-lite` | %s | 最新世代のFlash-Lite(ユーザー指定名と同一) | **旧世代 gemini-3.1-flash-lite($0.25/$1.50)・gemini-2.5-flash-lite($0.10/$0.40)がより安価に実在するが、置換せず。** 呼出は成功 |" % ", ".join(models_ret["gemini35fl"]),
     "| Sol(既存・補助) | `gpt-6.1-sol` | POST-EN-TRIAL-01実測 | 最新世代最上位系 | - |", ""]
R += ["## 3. 4条件のFlag一覧(記事ID / 文ID / type / confidence / related Fact / reason原文)", "", "confidenceは相対比較のみ(絶対評価に使わない)。", ""]
for c in CONDS:
    R += ["### %s %s(Flag %d件 / 文 %d)" % (CN[c], inv_note(c), sum(len(v) for v in F[c].values()), len(F[c])), ""]
    if not F[c]: R += ["Flagなし。", ""]; continue
    R += ["| 記事 | 文 | type | conf | Fact | Union29 | reason原文 |", "|---|---|---|---|---|---|---|"]
    for k in sorted(F[c], key=key):
        for f in F[c][k]: R.append("| %s | %s | %s | %.2f | %s | %s | %s |" % (k[0], k[1], f["type"], f["confidence"], ",".join(f["fact_ids"]) or "(なし)", UID.get(k, "未評価"), f["question"].replace("|", "/")))
    R.append("")
R += ["### A3-OR / A4-OR(sentence単位の和)", "", "- A3-OR(Luna A3 ∪ Gemini A3): %d文 %s" % (len(A3OR), ", ".join("%s-%s" % k for k in sorted(A3OR, key=key)) or "なし"), "- A4-OR(Luna A4 ∪ Gemini A4): %d文 %s" % (len(A4OR), ", ".join("%s-%s" % k for k in sorted(A4OR, key=key)) or "なし"), "- A4 両モデル一致: %d文 %s" % (len(both_a4), ", ".join("%s-%s" % k for k in both_a4) or "なし"), ""]
R += ["## 4. 表1(主評価): A3-ORの全項目とA4-ORカバー(Human列は空欄)", "",
      "機械的事実: A3-OR %d文のうちA4-ORでカバーされない(A3のみ検出)= **%d件**。" % (len(A3OR), n_a3_only), "",
      "| Issue(記事+文+related Fact) | 既存Union29一致ID | Luna A3 | Gemini A3 | Luna A4 | Gemini A4 | A4-OR | A4-ORでカバー | Human評価 | A3なしで失うか |", "|---|---|---|---|---|---|---|---|---|---|"]
for r in T1:
    R.append("| %s / Fact: %s / %s | %s | %s | %s | %s | %s | %s | %s | | |" % (r["issue"], ",".join(r["related_facts"]) or "(なし)", trunc(r["sentence"], 60), r["union29_id"] or "未評価", r["luna_a3"], r["gem_a3"], r["luna_a4"], r["gem_a4"], "○" if r["in_a4_or"] else "-", "カバー" if r["in_a4_or"] else "**A3のみ**"))
if not T1: R.append("| (A3-ORにFlagなし) | | | | | | | | | |")
R += ["", "## 5. 補助表1b: 既存Sol A3 Flag(Union 29のA3側 %d文)をA4で拾えたか(Human列は空欄)" % sol3_total, "",
      "カバー率: A4-OR %d/%d、Luna A4 %d/%d、Gemini A4 %d/%d。Sol A3のみ(Sol A4で未Flag)の項目 %d文のうちA4-ORカバー %d。参考: Sol A4 %d文のうちA4-ORカバー %d。Union 29全体のA4-ORカバー %d/29(Luna A4 %d、Gemini A4 %d)。" % (cov_or, sol3_total, cov_l, sol3_total, cov_g, sol3_total, len(sol3_only), agg["sol_a3_only_covered"], sol4_total, sol4_cov_or, sol_u_cov_or, sol_u_cov_l, sol_u_cov_g), "",
      "| Union29 ID | Sol A3 type conf | Sol A4でも検出 | Luna A4 | Gemini A4 | A4-OR | (参考)Luna A3 | (参考)Gemini A3 | Human評価 | A3なしで失うか |", "|---|---|---|---|---|---|---|---|---|---|"]
for r in T1B: R.append("| %s | %s | %s | %s | %s | %s | %s | %s | | |" % (r["union29_id"], r["sol_a3"], "○" if r["sol_a4_too"] else "-", "○" if r["luna_a4"] else "-", "○" if r["gem_a4"] else "-", "○" if r["a4_or"] else "-", "○" if r["luna_a3"] else "-", "○" if r["gem_a3"] else "-"))
R += ["", "## 6. 表2(副評価): Human Review量(A/B/C/D列は空欄)", "", "1記事平均=件数/11記事。出力無効の回は件数に含まない(出力無効セル数を併記)。", "",
      "| 条件 | raw Flag数 | sentence重複除去後 | semantic issue数 | 既存Union29一致数 | 未評価(新規)数 | 1記事平均(sentence) | 1記事平均(issue) | 出力無効セル | A | B | C | D |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in T2: R.append("| %s | %d | %d | %d | %d | %d | %.2f | %.2f | %d | | | | |" % (r["cond"], r["raw_flags"], r["sentence_unique"], r["semantic_issues"], r["union29_matched"], r["unreviewed_new"], r["per_article_avg_sentence"], r["per_article_avg_issue"], r["invalid_cells"]))
def t3tab(title, rows):
    o = ["### " + title, ""]
    if not rows: return o + ["なし(0件)。", ""]
    o += ["| 記事 | 文 | related Fact | reason要約 | 既存Union29 ID / 未評価 | Human評価 | 有用/ノイズ |", "|---|---|---|---|---|---|---|"]
    for r in rows: o.append("| %s | %s | %s | %s | %s | | |" % (r["key"][0], r["key"][1], ",".join(r["related_facts"]) or "(なし)", trunc(r["reason"], 130), r["union29_id"] or "未評価"))
    return o + [""]
R += ["", "## 7. 表3(相互補完): A4で片方のモデルのみがFlagした項目", "", "Luna A4のみ %d件 / Gemini A4のみ %d件 / 両方 %d件。" % (len(T3L), len(T3G), len(both_a4)), ""]
R += t3tab("Luna A4のみ(%d件)" % len(T3L), T3L) + t3tab("Gemini A4のみ(%d件)" % len(T3G), T3G)
R += ["## 8. 未評価Flag一覧(既存Union 29に記事ID+文IDで一致しないFlag、%d文)" % len(NEW), "", "ChatGPT側追加判定用。版A(confidence・モデル名あり)と版B(なし、Blind packet形式)。版Bは `unreviewed_packet_01.md` にも単体出力。", "", "### 版A(confidence・モデル名あり)", ""]
def render_new(blind):
    o = []
    for n in NEW:
        o += ["#### %s: %s %s" % (n["id"], n["article"], n["key"][1]), "", "- 記事: %s(%s)" % (n["article"], n["theme"]), "- 対象文: %s" % n["sentence"], "- ±2文:"]
        for sid, t in n["context"].items(): o.append("  - %s%s: %s" % (sid, "(対象)" if sid == n["key"][1] else "", t))
        o.append("- Fact本文:")
        for fid, t in n["facts"].items(): o.append("  - %s: %s" % (fid, t))
        if not n["facts"]: o.append("  - (related Factなし)")
        rs = []
        for f in n["flags"]:
            if blind:
                if f["reason"] not in rs: rs.append(f["reason"])
            else: rs.append("[%s / %s conf %.2f] %s" % (f["cond"], f["type"], f["confidence"], f["reason"]))
        o += ["- reason:"] + ["  - " + r for r in rs] + [""]
    return o
R += render_new(False) + ["### 版B(confidence・モデル名なし)", ""] + render_new(True)
open(os.path.join(H, "unreviewed_packet_01.md"), "w", encoding="utf-8").write("# 未評価Flag一覧(Blind packet、confidence・モデル名なし)\n\n" + "\n".join(render_new(True)) + "\n")
R += ["## 9. 費用実測", "", "| モデル | call数(HTTP) | 入力tok | 出力tok(thinking込み) | 実費JPY | 見積(中央/高位) |", "|---|---|---|---|---|---|",
      "| Luna | %d(%d) | %d | %d | %.3f | %.1f / %.1f |" % (cost["luna"]["n_calls"], cost["luna"]["n_http_calls"], cost["luna"]["in_tok"], cost["luna"]["out_tok"], cost["luna"]["jpy"], EST["luna_central"], EST["luna_high"]),
      "| Gemini 3.5 Flash-Lite | %d(%d) | %d | %d | %.3f | %.1f / %.1f |" % (cost["gemini35fl"]["n_calls"], cost["gemini35fl"]["n_http_calls"], cost["gemini35fl"]["in_tok"], cost["gemini35fl"]["out_tok"], cost["gemini35fl"]["jpy"], EST["gemini_central"], EST["gemini_high"]),
      "| **合計** | 44 | | | **%.3f** | %.1f / %.1f |" % (total_cost, EST["total_central"], EST["total_high"]), "", "累計JPY100ガード: 未到達。台帳 `cost_ledger_dm_01.jsonl`。見積差(実費-中央): %+.2f。" % (total_cost - EST["total_central"]), ""]
R += ["## 10. 参考: META rollback(母集団外)", "", "CROSSMODEL-01(`meta_rollback_crossmodel_01/RESULT_01.md`)の結果を参考付記のみ(本Trialの集計に含めない)。機械読取: %s。" % json.dumps(META_REF, ensure_ascii=False), "",
      "## 11. Status提案・不変更", "", "- Status提案: **USER_DECISION_REQUIRED**(ChatGPT側照合後に判定)。A3_REMOVAL_SUPPORTED等はClaude側で確定しない。", "- APPROVED項目(OPEN-244運用コンセプト、R0後/翻訳後Hard STOP除去)は不変更、未PRODUCTION_WIRED。A3+A4英訳後配置=VALIDATED不変。", "- やらないこと9項目(PREREGISTRATION_01.md 9節)未実施。Production・CURRENT_SPEC・Prompt変更なし。", ""]
open(os.path.join(H, "RESULT_01.md"), "w", encoding="utf-8").write("\n".join(R) + "\n")
print("A3OR", len(A3OR), "A4OR", len(A4OR), "a3_only", n_a3_only, "new", len(NEW), "cost", total_cost)
