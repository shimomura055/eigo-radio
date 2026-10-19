# -*- coding: utf-8 -*-
"""開発費承認ルール(PM_GOVERNANCE 7-7, 2026-10-19ユーザー正式決定)の判定表check。

PM-DEV-COST-APPROVAL-RULE-300-01。文書のみ・API呼出0・Production非接触。
閾値(300円/1,000円)は7-7の表から読み取り、テスト側で二重定義しない。
daily_dev_cost_01.pyは日次集計(当日累計の取得)であり承認判定を持たないため、本scriptは判定表の検証のみ担当。
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GOV = ROOT / "docs/pm/PM_GOVERNANCE.md"


def load_thresholds():
    t = GOV.read_text(encoding="utf8").replace("\r\n", "\n")
    s = t.index("### 7-7. "); e = t.index("### 7-8. ")
    sec = t[s:e]
    rows = [l for l in sec.split("\n") if l.startswith("|")]
    case = next(l for l in rows if "案件見積" in l and "超" in l and "ユーザーの事前費用承認" in l)
    daily = next(l for l in rows if "日次累計" in l and "超過見込み" in l)
    return sec, int(re.search(r"案件見積(\d+)円超", case).group(1)), int(re.search(r"日次累計([\d,]+)円超過", daily).group(1).replace(",", ""))


def decide(est, cost_thr, daily_thr, scope_ok=True, new_spec=False, daily_used=0, cap_remaining=None, prior_same_case=()):
    """戻り値: (判定, 理由)。prior_same_case=同一案件の分割済み見積[(date, yen)]。日付が違っても合算。"""
    case_total = est + sum(y for _, y in prior_same_case)
    if new_spec or not scope_ok:
        return "USER_APPROVAL_SCOPE", "新仕様/未承認Trial範囲/Scope変更は金額無関係"
    if cap_remaining is not None and case_total > cap_remaining:
        return "USER_APPROVAL_CAP", "個別Cap超過(300円以下でも承認)"
    if case_total > cost_thr:
        return "USER_COST_APPROVAL", "案件合算見積が%d円超" % cost_thr
    if daily_used + est > daily_thr:
        return "USER_BUDGET_APPROVAL", "日次累計が%d円超過見込み" % daily_thr
    return "AUTONOMOUS", "承認済みScope内・案件見積%d円以下・日次内" % cost_thr


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json-out")
    a = ap.parse_args()
    sec, C, D = load_thresholds()
    res = []
    def chk(name, got, want):
        res.append({"case": name, "got": got[0], "want": want, "ok": got[0] == want, "reason": got[1]})
    d = lambda est, **k: decide(est, C, D, **k)
    chk("(a) Scope内20円・日次残あり", d(20, daily_used=100), "AUTONOMOUS")
    chk("(b) Scope内50円", d(50), "AUTONOMOUS")
    chk("(c) 300円ちょうど", d(C), "AUTONOMOUS")
    chk("(d) 301円", d(C + 1), "USER_COST_APPROVAL")
    chk("(e) 120円だが日次累計1,000円超過見込み", d(120, daily_used=D - 100), "USER_BUDGET_APPROVAL")
    chk("(f) 80円だが個別Cap超過", d(80, cap_remaining=50), "USER_APPROVAL_CAP")
    chk("(g) 40円だが未承認新仕様", d(40, new_spec=True), "USER_APPROVAL_SCOPE")
    chk("(g2) 40円だが未承認Trial範囲(Scope外)", d(40, scope_ok=False), "USER_APPROVAL_SCOPE")
    prior = [("2026-10-19", 200), ("2026-10-19", 200)]
    chk("(h) 600円を200円x3分割(3つ目の判定=合算)", d(200, prior_same_case=prior), "USER_COST_APPROVAL")
    chk("(i) 日付をまたぐ分割(前日200+前日200+当日200)", d(200, prior_same_case=[("2026-10-18", 200), ("2026-10-18", 200)]), "USER_COST_APPROVAL")
    chk("(j) 日次ちょうど1,000円は超過でない", d(100, daily_used=D - 100), "AUTONOMOUS")
    # 文書整合
    def doc(name, ok):
        res.append({"case": name, "got": "OK" if ok else "NG", "want": "OK", "ok": bool(ok), "reason": ""})
    doc("doc: 閾値 300/1000 を7-7表から取得", (C, D) == (300, 1000))
    for k in ["分割", "日付を分割", "既存Capを超える場合は、300円以下でも承認が必要", "金額に関係なく", "超過前に承認", "自律的に実行する"]:
        doc("doc: 7-7に『%s』" % k, k in sec)
    old = re.sub(r"改定履歴:.*", "", sec)
    doc("doc: 7-7本文(改定履歴行除く)に旧100円基準なし", not re.search(r"100円|JPY100", old))
    cl = (ROOT / "CLAUDE.md").read_text(encoding="utf8")
    doc("doc: CLAUDE.md安全・承認境界に300円/7-7参照", "案件見積300円超" in cl and "7-7" in cl)
    gov = GOV.read_text(encoding="utf8")
    doc("doc: 7-9承認要否が300円基準", "案件見積300円以下かつ当日累計+見積が1,000円以内" in gov and "見積100円超=従来どおり" not in gov)
    doc("doc: 29節にC-13実質変更行", "| C-13 |" in gov and "実質変更(ユーザー正式決定2026-10-19" in gov)
    out = {"all_ok": all(r["ok"] for r in res), "n": len(res), "thresholds": {"case_yen": C, "daily_yen": D}, "results": res}
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    for r in res:
        print(("PASS " if r["ok"] else "FAIL ") + r["case"] + " -> " + r["got"])
    print("all_ok=%s n=%d" % (out["all_ok"], len(res)))
    return 0 if out["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
