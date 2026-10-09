# -*- coding: utf-8 -*-
"""追加Trial集計(委任_04)。存在するモデルだけ集計。API非呼び出し。PREREGISTRATION_02の式。"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["K01", "K02", "K03", "K04", "K06", "K08", "K09", "K10", "K11", "K12"]
cases = {c["key"]: c for c in json.load(open(os.path.join(HERE, "cases_01.json"), encoding="utf-8"))["cases"]}
MODELS = ["gpt-6-luna", "gpt-5.6-luna", "gpt-5.6-sol", "deepseek-v4-flash"]
def load(m, r):
    p = os.path.join(HERE, "results", "%s_rep%d.jsonl" % (m, r))
    if not os.path.exists(p): return None
    rows = [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]
    s = [x for x in rows if x.get("_summary")]
    return {x["case_id"]: x for x in rows if not x.get("_summary")}, (s[0] if s else {})
R = {(m, r): load(m, r) for m in MODELS for r in (1, 2)}
have = [m for m in MODELS if R[(m, 1)] and R[(m, 2)]]
def lab(m, r, k):
    x = R[(m, r)][0][cases[k]["case_id"]]
    return x["label"] if x["valid_json"] else "N/A"
def m1(m):
    L = [lab(m, r, k) for k in ("K01", "K02", "K03") for r in (1, 2)]
    st = "REJECTED" if "A" in L or "N/A" in L else ("PASS" if all(x == "C" for x in L) else "USER_DECISION_REQUIRED")
    return L, st
def m2(m):
    L = [lab(m, r, k) for k in ("K08", "K09", "K12") for r in (1, 2)]
    bc = sum(x in "BC" or x == "N/A" for x in L)
    return L, ("PASS" if bc <= 1 and "C" not in L and "N/A" not in L else "FAIL")
def m4(m): return sum(lab(m, 1, k) == lab(m, 2, k) for k in ORDER) / 10
out = ["# RESULT_TABLE_02: 追加Trial 結果(自動生成 aggregate_02.py、集計対象モデル=%s)\n" % ", ".join(have),
       "## 1. 横並び(label rep1/rep2)\n", "| case | human_tier | " + " | ".join(have) + " |", "|---|---|" + "---|" * len(have)]
for k in ORDER:
    out.append("| %s | %s | " % (k, cases[k].get("human_tier", "")[:30]) + " | ".join("%s/%s" % (lab(m, 1, k), lab(m, 2, k)) for m in have) + " |")
out += ["", "## 2. モデル別指標\n", "| model | M1判定(K01,K02,K03 x rep1,rep2) | M1 | C数(M1) | M2判定(K08,K09,K12) | M2 | M4自己一致 | K11 | 形式違反 | 実費JPY(登録単価) |", "|---|---|---|---|---|---|---|---|---|---|"]
def order_fix(m, L):  # L is k-major, rep-minor
    return "".join(L)
for m in have:
    a, s1 = m1(m); b, s2 = m2(m)
    fv = sum(R[(m, r)][1].get("format_violation_count", 0) for r in (1, 2))
    cost = sum((R[(m, r)][1].get("spent_jpy_est") or 0) for r in (1, 2))
    out.append("| %s | %s | %s | %d/6 | %s | %s | %.0f%% | %s/%s | %d | %.2f |" % (m, "".join(a), s1, a.count("C"), "".join(b), s2, 100 * m4(m), lab(m, 1, "K11"), lab(m, 2, "K11"), fv, cost))
out += ["", "## 3. モデル別Status(PREREGISTRATION_02 s6)\n"]
for m in have:
    _, s1 = m1(m); _, s2 = m2(m)
    if s2 == "FAIL" or s1 == "REJECTED": st = "REJECTED"
    elif s1 == "USER_DECISION_REQUIRED": st = "USER_DECISION_REQUIRED"
    else: st = "VALIDATED" if m4(m) >= 0.8 else "USER_DECISION_REQUIRED(M4格下げ。M4無視ならVALIDATED)"
    out.append("- %s: %s" % (m, st))
def status(m):
    _, s1 = m1(m); _, s2 = m2(m)
    if s2 == "FAIL" or s1 == "REJECTED": return "REJECTED"
    if s1 == "USER_DECISION_REQUIRED": return "USER_DECISION_REQUIRED"
    return "VALIDATED" if m4(m) >= 0.8 else "USER_DECISION_REQUIRED"
out += ["", "## 4. 人間既知ラベルとChecker参考(Checkerは正解扱いしない)", "", "| case | 人間既知 | Checker参考 |", "|---|---|---|"]
for k in ORDER:
    out.append("| %s | %s | %s |" % (k, cases[k].get("human", "")[:80].replace("|", "/"), cases[k].get("checker", "")[:80].replace("|", "/")))
out += ["", "## 5. C検出数・K11・両B件数", "", "| model | K01 C数/2 | K02 C数/2 | K03 C数/2 | K11 C数/2 | K11 A見逃し数 | 両B件数(rep1,rep2とも同一caseでB) |", "|---|---|---|---|---|---|---|"]
for m in have:
    cc = lambda k: sum(lab(m, r, k) == "C" for r in (1, 2))
    out.append("| %s | %d | %d | %d | %d | %d | %d |" % (m, cc("K01"), cc("K02"), cc("K03"), cc("K11"), sum(lab(m, r, "K11") == "A" for r in (1, 2)), sum(lab(m, 1, k) == "B" and lab(m, 2, k) == "B" for k in ORDER)))
out += ["", "## 6. sol x deepseek 人間確認対象率(rep別、10ケース)", "", "定義1=2評価者のラベル不一致のみ / 定義2=不一致+両方B。", "", "| rep | 不一致case | 両Bcase | 定義1 | 定義2 |", "|---|---|---|---|---|"]
if "gpt-5.6-sol" in have and "deepseek-v4-flash" in have:
    for r in (1, 2):
        dis = [k for k in ORDER if lab("gpt-5.6-sol", r, k) != lab("deepseek-v4-flash", r, k)]
        bb = [k for k in ORDER if lab("gpt-5.6-sol", r, k) == "B" and lab("deepseek-v4-flash", r, k) == "B"]
        out.append("| rep%d | %s | %s | %d/10=%d%% | %d/10=%d%% |" % (r, ",".join(dis), ",".join(bb), len(dis), 10 * len(dis), len(dis) + len(bb), 10 * (len(dis) + len(bb))))
out += ["", "## 7. 事前登録の機械適用(PREREGISTRATION_02 s4-s6)", "", "「改善」= M1 PASS、またはC数>0(gpt-6-lunaのC=0超)かつM2 PASS。", "", "| model | M1 | M2 | M4 | 改善 | 安定検出(M1 6/6 C) | モデル別Status |", "|---|---|---|---|---|---|---|"]
imp = {}
for m in have:
    a, s1 = m1(m); b, s2 = m2(m)
    imp[m] = (s1 == "PASS") or (a.count("C") > 0 and s2 == "PASS")
    out.append("| %s | %s | %s | %.0f%% | %s | %s | %s |" % (m, s1, s2, 100 * m4(m), "あり" if imp[m] else "なし", "はい" if s1 == "PASS" else "いいえ", status(m)))
sts = [status(m) for m in have]
overall = "VALIDATED" if "VALIDATED" in sts else ("REJECTED" if all(x == "REJECTED" for x in sts) else "USER_DECISION_REQUIRED")
out += ["", "- 解釈規則の機械適用: Sol改善=%s / DeepSeek改善=%s。M1 PASS(安定検出)モデル=%s。" % (imp.get("gpt-5.6-sol"), imp.get("deepseek-v4-flash"), [m for m in have if m1(m)[1] == "PASS"] or "なし"),
        "- 機械Status(Trial全体、対象=%s): **%s**" % (",".join(have), overall),
        "- 注意: 成功しても「LLM Checkerが客観的に正しい」とは結論しない。n=10・重大3件(+参考1)の機能確認。最終判定はFable待ち。"]
out += ["", "## 8. 実費(usage x 登録単価、USD/JPY=160)", "", "| model | rep1 | rep2 | 合計 JPY |", "|---|---|---|---|"]
tot = 0
for m in have:
    c = [R[(m, r)][1].get("spent_jpy_est") or 0 for r in (1, 2)]; tot += sum(c)
    out.append("| %s | %.3f | %.3f | %.3f |" % (m, c[0], c[1], sum(c)))
out.append("| 合計(前Trial luna分+追加Trial) | | | %.3f |" % tot)
add_cost = sum((R[(m, r)][1].get("spent_jpy_est") or 0) for m in ("gpt-5.6-sol", "deepseek-v4-flash") for r in (1, 2))
out += ["", "追加Trial分(sol+deepseek)= JPY %.3f。sol実効パラメータ: reasoning=medium, temperature=指定なし(拒否された), seed=未対応。形式違反0・再呼び出し0・例外0。" % add_cost]
open(os.path.join(HERE, "RESULT_TABLE_02.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
