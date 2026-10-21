# -*- coding: utf-8 -*-
"""委任_05 C-1: 保存済みLuna判断(Trial_02 judge_eval.json、final=APPROXIMATE_OK の90件)からV8回帰fixtureを生成する(API 0、決定論)。
出力: er090_output/b3_core_number_rounding_trial_02/evidence/v8_regression_90.json
期待(固定): V8(相対誤差10%超)=6件拒否、V8b(元surfaceが既に概数[約/およそ等]の再丸め)=別の6件拒否(約348億ドル→約350億ドル x6、いずれも事前登録ラベルE)、
V8/V8bで拒否される事前登録ラベルA(正しい丸め)=0件。
rel_change はTrial_02分析(label_v2_analysis.json)のDecimal計算と独立に、fixture内で整数演算(分数)でも再計算して保存する。
"""
from __future__ import annotations

import json
import os
from fractions import Fraction

import er090_b3_core_number_rounding_trial_02_labels as lab
import er095_b3_core_number_rounding_01 as m

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er090_output", "b3_core_number_rounding_trial_02")
OUT = os.path.join(ROOT, "evidence", "v8_regression_90.json")


def main():
    ev = json.load(open(os.path.join(ROOT, "evidence", "judge_eval.json"), encoding="utf-8"))
    rows = [r for r in ev["rows"] if r["run"].startswith("luna_") and r["final"] == "APPROXIMATE_OK" and r["approx"]]
    items = []
    for r in rows:
        ex, ap = m.parse_surface(r["surface"])["value"], m.parse_surface(r["approx"][0])["value"]
        rel = abs(Fraction(ap) - Fraction(ex)) / Fraction(ex)
        items.append({"run": r["run"], "article": r["article"], "concept": r["concept"], "surface": r["surface"],
                      "approx": r["approx"][0], "label_prereg": lab.LABELS.get((r["article"], r["surface"])),
                      "rel_error": float(rel), "expected_v8": "REJECT" if rel > Fraction(1, 10) else "PASS",
                      "expected_v8b_already_approx": "REJECT" if any(h in r["surface"] for h in m.HEDGE_WORDS) else "PASS"})
    out = {"n": len(items), "n_expected_reject": sum(1 for i in items if i["expected_v8"] == "REJECT"),
           "n_expected_reject_v8b": sum(1 for i in items if i["expected_v8b_already_approx"] == "REJECT"),
           "n_expected_reject_label_A": sum(1 for i in items if "REJECT" in (i["expected_v8"], i["expected_v8b_already_approx"]) and i["label_prereg"] == "A"),
           "source": "er090_output/b3_core_number_rounding_trial_02/evidence/judge_eval.json (run=luna_*, final=APPROXIMATE_OK)",
           "items": items}
    json.dump(out, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(out["n"], out["n_expected_reject"], out["n_expected_reject_label_A"])


if __name__ == "__main__":
    main()
