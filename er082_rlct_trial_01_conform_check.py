# ============================================================
# er082_rlct_trial_01_conform_check.py  (委任_07 D7、JPY0・機械照合・読み取り専用)
# FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01: 既存Stage 1a結果が「最終B3確認」条件(D1)を満たすか照合する。
#   D1 = (i)選定FactにREJECTEDが無い かつ
#        (ii)選定FactのうちAMBIGUOUSは全て、そのselを生成したB3呼出の候補Ledgerに[AMBIGUOUS]として提示済み。
# 方式: M0/M0b/M0p/M1 = N/A(全Fact検証後にB3を呼ぶため候補Ledgerは常に検証済み)。M2/M3のみ照合。
# 判定根拠は2系統: (a) result.jsonのrounds(どのroundで検証されたか)、(b) 保存済みB3 prompt上の[AMBIGUOUS]タグ(あれば)。
# 出力: --out のJSON。Production/既存成果物には書き込まない(--out はTrial領域内のみ)。
# ============================================================
from __future__ import annotations

import argparse
import os
import re
import sys

import er082_rlct_trial_01_lib as lib
from er082_rlct_trial_01_lib import ARTICLES, METHODS, OUT_ROOT, load_json, save_json

ARTICLES_1A = [a for a, v in ARTICLES.items() if v["stage"] == "1a"]
NA_REASON = "全Fact検証後にB3を呼ぶ方式(候補Ledgerは検証済みタグ付き)。確認パスの対象外"


def _prompt_shows_ambiguous(prompt: str, fid: str) -> bool:
    return bool(re.search(rf"^\[AMBIGUOUS[^\]]*\]\s+{re.escape(fid)}:", prompt or "", re.MULTILINE))


def check_method(root: str, article: str, method: str) -> dict:
    row = {"article": article, "method": method}
    if method not in ("M2", "M3"):
        return {**row, "conform_d1": "N/A", "reason": NA_REASON}
    rp = f"{root}/{article}/{method}/result.json"
    if not os.path.isfile(rp):
        return {**row, "conform_d1": "N/A", "reason": f"result.jsonが無い: {rp}"}
    res = load_json(rp)
    if res.get("status") != "COMPLETED":
        return {**row, "conform_d1": "N/A", "reason": f"status={res.get('status')}(確定Briefなし)"}
    rounds = res["reselect"]["rounds"]
    r_last = len(rounds) - 1
    sel_ids = rounds[-1]["selected_fact_ids"]
    fv = {k: v["verdict"] for k, v in res["final_verdicts"].items()}
    # (a) rounds由来: round<r_last で検証済みのFactが、最終sel生成B3呼出の候補Ledgerに判定タグ付きで見えていた
    visible = set()
    for rd in rounds[:r_last]:
        visible.update(rd.get("verified_now", []))
    rejected = [i for i in sel_ids if fv.get(i) == "REJECTED"]
    amb = [i for i in sel_ids if fv.get(i) == "AMBIGUOUS"]
    unseen = [i for i in amb if i not in visible]
    # (b) 保存済みB3 promptによる裏取り(あれば)
    wd = f"{root}/{article}/{method}/_work"
    label = rounds[-1].get("b3_label") or ("initial" if r_last == 0 else f"reselect{r_last}")
    cands = [f"{wd}/b3_{label}.json"]
    if r_last == 0 and method == "M3":
        cands.append(f"{root}/{article}/M2/_work/b3_initial.json")      # M3は初回B3をM2と共有
    pp = next((p for p in cands if os.path.isfile(p)), None)
    prompt_evidence = None
    if pp:
        prompt = load_json(pp).get("user_prompt", "")
        shown = {i: _prompt_shows_ambiguous(prompt, i) for i in amb}
        prompt_evidence = {"path": pp, "ambiguous_shown_in_b3_prompt": shown,
                           "agrees_with_rounds": all(shown[i] == (i not in unseen) for i in amb)}
    ok = not rejected and not unseen
    why = []
    if rejected:
        why.append(f"REJECTEDが最終選定に含まれる: {rejected}")
    if unseen:
        why.append(f"AMBIGUOUSだが、selを生成したB3呼出({label})の候補Ledgerでは未検証[UNVERIFIED]として提示され、"
                   f"検証結果(AMBIGUOUS/notes)がB3へ返されていない: {unseen}")
    if ok and not amb:
        why.append("選定Factは全てVERIFIED(確認パス不要)")
    if ok and amb:
        why.append(f"AMBIGUOUS {amb} は生成B3呼出({label})の候補Ledgerに判定付きで提示済み")
    return {**row, "conform_d1": "PASS" if ok else "FAIL", "reason": " / ".join(why),
            "final_sel_b3_label": label, "selected_fact_ids": sel_ids, "final_verdicts_of_selected":
            {i: fv.get(i) for i in sel_ids}, "ambiguous_selected": amb, "ambiguous_unseen_by_b3": unseen,
            "rejected_selected": rejected, "prompt_evidence": prompt_evidence,
            "action": "補正対象(M2c/M3c: 確認パスのみ追加実行)" if not ok else "再生成不要"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=OUT_ROOT)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    lib.assert_under_out_root(a.out, OUT_ROOT)
    rows = [check_method(a.root, art, m) for art in ARTICLES_1A for m in METHODS]
    summary = {"pass": [f"{r['article']}/{r['method']}" for r in rows if r["conform_d1"] == "PASS"],
               "fail": [f"{r['article']}/{r['method']}" for r in rows if r["conform_d1"] == "FAIL"],
               "n_a": [f"{r['article']}/{r['method']}" for r in rows if r["conform_d1"] == "N/A"]}
    save_json(a.out, {"root": a.root, "rule": "D1: (i)REJECTED無し かつ (ii)AMBIGUOUSは全て生成B3呼出の候補Ledgerで提示済み",
                      "n_methods": len(rows), "summary": summary, "rows": rows})
    print(f"[conform] {len(rows)} methods PASS={summary['pass']} FAIL={summary['fail']} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
