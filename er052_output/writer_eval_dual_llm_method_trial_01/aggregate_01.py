# -*- coding: utf-8 -*-
"""集計(評価完了後にのみ実行)。results/*.jsonl と cases_01.json を結合し RESULT_TABLE_01.md と aggregate_01.json を作る。
事前登録 PREREGISTRATION_01.md 0-R の式を機械適用する。API非呼び出し。"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["K01", "K02", "K03", "K04", "K06", "K08", "K09", "K10", "K11", "K12"]
M1_KEYS, M2_KEYS = ["K01", "K02", "K03"], ["K08", "K09", "K12"]
PRIM, SEC = "gpt-6-luna", "gpt-5.6-luna"


def jl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


cases = {c["key"]: c for c in json.load(open(os.path.join(HERE, "cases_01.json"), encoding="utf-8"))["cases"]}


def load(model, rep, prefix=""):
    rows = jl(os.path.join(HERE, "results", "%s%s_rep%d.jsonl" % (prefix, model, rep)))
    summ = [r for r in rows if r.get("_summary")][0]
    return {r["case_id"]: r for r in rows if not r.get("_summary")}, summ


R = {(m, r): load(m, r) for m in (PRIM, SEC) for r in (1, 2)}


def lab(m, r, k):
    return R[(m, r)][0][cases[k]["case_id"]]["label"] or "N/A"


def cell(m, r, k):
    x = R[(m, r)][0][cases[k]["case_id"]]
    if not x["valid_json"]:
        return "N/A(形式違反)"
    return "%s / %s / %s" % (x["label"], x["misread_type"], (x["reason"] or "")[:34])


def m1(m):
    L = [lab(m, r, k) for k in M1_KEYS for r in (1, 2)]
    stage = "REJECTED" if "A" in L else ("USER_DECISION_REQUIRED" if any(x != "C" for x in L) else "PASS")
    return L, stage


def m2(m):
    L = [lab(m, r, k) for k in M2_KEYS for r in (1, 2)]
    bc = sum(1 for x in L if x != "A")
    c = sum(1 for x in L if x == "C")
    return L, bc, c, ("PASS" if bc <= 1 and c == 0 else "FAIL")


def m4(m):
    same = [k for k in ORDER if lab(m, 1, k) == lab(m, 2, k)]
    return len(same), [k for k in ORDER if k not in same]


def pair(a, b):
    dis = [k for k in ORDER if lab(*a, k) != lab(*b, k)]
    cdis = [k for k in dis if "C" in (lab(*a, k), lab(*b, k))]
    bothB = [k for k in ORDER if lab(*a, k) == "B" == lab(*b, k)]
    return dis, cdis, bothB


out = {m: dict(m1=m1(m), m2=m2(m), m4=m4(m)) for m in (PRIM, SEC)}
pairs = {"rep1(6luna-vs-5.6luna)": pair((PRIM, 1), (SEC, 1)), "rep2(6luna-vs-5.6luna)": pair((PRIM, 2), (SEC, 2)),
         "6luna rep1-vs-rep2": pair((PRIM, 1), (PRIM, 2)), "5.6luna rep1-vs-rep2": pair((SEC, 1), (SEC, 2))}
m3_max = max(len(pairs["rep1(6luna-vs-5.6luna)"][0]), len(pairs["rep2(6luna-vs-5.6luna)"][0]))
m4_6 = out[PRIM]["m4"][0] / 10
s6, s2 = out[PRIM]["m1"][1], out[PRIM]["m2"][3]
if s2 == "FAIL" or s6 == "REJECTED":
    primary = "REJECTED"
elif s6 == "USER_DECISION_REQUIRED":
    primary = "USER_DECISION_REQUIRED"
else:
    primary = "VALIDATED" if m4_6 >= 0.8 else "USER_DECISION_REQUIRED"
if primary == "VALIDATED":
    reference = "REJECTED" if m3_max >= 7 else ("USER_DECISION_REQUIRED" if m3_max >= 5 else "VALIDATED")
else:
    reference = primary

L = []
P = L.append
P("# RESULT_TABLE_01: 結果表(委任_02、事前登録 PREREGISTRATION_01.md 0-R の式を機械適用。自動生成 aggregate_01.py)\n")
P("Model A=gpt-6-luna(主評価者)、Model B=gpt-5.6-luna(同じLuna系の参考第2評価者。別vendorではない)。各セルは `label / misread_type / reason(先頭34字)`。\n")
P("## 表1: ケース別判定\n")
P("| K | case_id | Fact(短縮) | Writer文(短縮) | Model A rep1 | Model A rep2 | Model B rep1 | Model B rep2 | 人間既知 | Checker参考 | A-B一致(rep1 / rep2) | 期待との照合(Model A rep1/rep2) |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|")


def fm(x, y):
    return ("一致(%s)" % x) if x == y else ("不一致(%s-%s)" % (x, y))


for k in ORDER:
    c = cases[k]
    a1, a2, b1, b2 = lab(PRIM, 1, k), lab(PRIM, 2, k), lab(SEC, 1, k), lab(SEC, 2, k)
    P("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | 期待%s: %s/%s |" % (
        k, c["case_id"], c["fact"][:40].replace("|", "/"), c["sentence"][:60].replace("|", "/"),
        cell(PRIM, 1, k), cell(PRIM, 2, k), cell(SEC, 1, k), cell(SEC, 2, k),
        c["human_tier"][:36].replace("|", "/"), c["checker"][:30].replace("|", "/"), fm(a1, b1), fm(a2, b2), c["expect"], a1, a2))
P("\n(人間既知・Checker参考の全文は `CASES_01.md`。Checkerは正解扱いしない。)\n")
P("## 表2: 事前登録指標\n")
P("| 指標 | gpt-6-luna(主・判定に使用) | gpt-5.6-luna(参考集計) |")
P("|---|---|---|")
l6, st6 = out[PRIM]["m1"]
l5, st5 = out[SEC]["m1"]
P("| M1 K01,K02,K03 x rep1,rep2 (K01r1,r2,K02r1,r2,K03r1,r2) | %s -> %s | %s -> %s |" % (",".join(l6), st6, ",".join(l5), st5))
a6 = out[PRIM]["m2"]
a5 = out[SEC]["m2"]
P("| M2 K08,K09,K12 x rep1,rep2 (K08r1,r2,K09r1,r2,K12r1,r2) | %s: B/C=%d, C=%d -> %s | %s: B/C=%d, C=%d -> %s |" % (",".join(a6[0]), a6[1], a6[2], a6[3], ",".join(a5[0]), a5[1], a5[2], a5[3]))
P("| M4 自己一致(rep1=rep2, 10ケース) | %d/10, 不一致: %s | %d/10, 不一致: %s |" % (out[PRIM]["m4"][0], ",".join(out[PRIM]["m4"][1]) or "なし", out[SEC]["m4"][0], ",".join(out[SEC]["m4"][1]) or "なし"))
P("| 実効temperature | %s | %s |" % (R[(PRIM, 1)][1]["effective_params"]["temperature"], R[(SEC, 1)][1]["effective_params"]["temperature"]))
P("\n## 表3: 2評価者の不一致(M3、参考)と人間確認対象(定義1=不一致のみ、定義2=不一致+両B)\n")
P("| 比較 | M3 不一致件数(case_id) | C不一致(片方がC他方C以外) | 両B件数(case_id) | 確認対象 定義1 | 確認対象 定義2 |")
P("|---|---|---|---|---|---|")
for name, (dis, cdis, bb) in pairs.items():
    d2 = sorted(set(dis) | set(bb), key=ORDER.index)
    P("| %s | %d/10 (%s) | %d (%s) | %d (%s) | %d/10 | %d/10 (%s) |" % (name, len(dis), ",".join(dis) or "-", len(cdis), ",".join(cdis) or "-", len(bb), ",".join(bb) or "-", len(dis), len(d2), ",".join(d2) or "-"))
P("\n## 表4: ラベル分布(各10判定)\n")
for m in (PRIM, SEC):
    for r in (1, 2):
        cnt = {x: sum(1 for k in ORDER if lab(m, r, k) == x) for x in ("A", "B", "C", "N/A")}
        P("- %s rep%d: A=%d B=%d C=%d N/A=%d" % (m, r, cnt["A"], cnt["B"], cnt["C"], cnt["N/A"]))
P("\n## 表5: 事前登録式のStatus(機械割当)\n")
P("- (主) M1/M2/M4: M1段階=%s、M2=%s、gpt-6-luna M4=%d/10 -> **%s**" % (st6, s2, out[PRIM]["m4"][0], primary))
P("- (参考) 元3節の表にM3(6luna vs 5.6luna、rep別の大きい方=%d件)を当てはめた場合 -> **%s**" % (m3_max, reference))
P("- いずれもProduction採用ではない。大規模Writer比較Trialへ直行しない。最終Status判定はFable。")

ob, obs = load(PRIM, 1, "optional_block_")
items = json.load(open(os.path.join(HERE, "optional_block_items_01.json"), encoding="utf-8"))["items"]
P("\n## 表6: 任意ブロック(合否外、gpt-6-luna 1rep、方式A、22文)\n")
P("| case_id | idx | 対応Fact | 対応品質 | 文(短縮) | label / misread_type / reason |")
P("|---|---|---|---|---|---|")
cnt = {"A": 0, "B": 0, "C": 0, "N/A": 0}
dB = dT = 0
byq = {q: {x: 0 for x in ("A", "B", "C", "N/A")} for q in ("direct", "partial", "weak")}
for it in items:
    r = ob[it["case_id"]]
    lb = r["label"] or "N/A"
    cnt[lb] += 1
    byq[it["mapping_quality"]][lb] += 1
    if it["mapping_quality"] == "direct":
        dT += 1
        dB += (lb == "B")
    P("| %s | %d | %s | %s | %s | %s |" % (it["case_id"], it["sentence_index"], it["mapped_fact_id"], it["mapping_quality"], it["target_sentence"][:56].replace("|", "/"),
                                          ("%s / %s / %s" % (lb, r["misread_type"], (r["reason"] or "")[:40])) if r["valid_json"] else "N/A"))
nc = cnt["B"] + cnt["C"] + cnt["N/A"]
P("\n- 件数: A=%d B=%d C=%d N/A=%d (計22)" % (cnt["A"], cnt["B"], cnt["C"], cnt["N/A"]))
P("- 記事1本あたりの確認対象数: C+B(+N/A) = %d 文 / 22文 (%.0f%%)" % (nc, 100 * nc / 22))
P("- 対応品質別(A/B/C/N/A): " + "; ".join("%s=%s" % (q, "/".join(str(byq[q][x]) for x in ("A", "B", "C", "N/A"))) for q in byq))
P("- A文への過剰B率: 対応品質direct %d文中B=%d (%.0f%%)。参考: 全22文中B=%d (%.0f%%)" % (dT, dB, 100 * dB / dT if dT else 0, cnt["B"], 100 * cnt["B"] / 22))
P("- partial/weakでのB/Cは『対応付け不良由来』か『文の逸脱』か区別が必要(reasonを人が確認する)。")

P("\n## 表7: 実費(usage実測x登録単価)・形式違反・再呼び出し\n")
P("| run | 試行数 | 採用(例外除く) | 形式違反数 | API例外試行 | input tok | output tok | reasoning tok | 実費(円) | temperature |")
P("|---|---|---|---|---|---|---|---|---|---|")
tot = tot_main = 0.0
runs = [(m, r, "") for m in (PRIM, SEC) for r in (1, 2)] + [(PRIM, 1, "optional_block_")]
for m, r, pre in runs:
    raw = jl(os.path.join(HERE, "logs", "%s%s_rep%d_raw.jsonl" % (pre, m, r)))
    err = sum(1 for x in raw if x.get("error"))
    good = [x for x in raw if not x.get("error")]
    vio = sum(1 for x in good if x.get("violations"))
    ti = sum((x["usage"].get("input_tokens") or 0) for x in good)
    to = sum((x["usage"].get("output_tokens") or 0) for x in good)
    tr = sum((x["usage"].get("reasoning_tokens") or 0) for x in good)
    cost = sum((x.get("cost_jpy_est") or 0) for x in good)
    tot += cost
    if not pre:
        tot_main += cost
    eff = (obs if pre else R[(m, r)][1])["effective_params"]["temperature"]
    P("| %s%s rep%d | %d | %d | %d | %d | %d | %d | %d | %.3f | %s |" % (pre, m, r, len(raw), len(good), vio, err, ti, to, tr, cost, eff))
P("\n- 実費合計: 約 JPY %.3f(本体 %.3f / 任意ブロック %.3f。登録単価x実usage。見積: 本体 4.7-23.2円 + 任意 1.57-7.55円)。" % (tot, tot_main, tot - tot_main))
open(os.path.join(HERE, "RESULT_TABLE_01.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
json.dump(dict(primary=primary, reference=reference, m3_max=m3_max, m1={m: out[m]["m1"] for m in out}, m2={m: out[m]["m2"] for m in out},
               m4={m: out[m]["m4"] for m in out}, pairs={k: v for k, v in pairs.items()}, optional_counts=cnt, cost_total=tot, cost_main=tot_main),
          open(os.path.join(HERE, "aggregate_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok primary=%s reference=%s" % (primary, reference))
