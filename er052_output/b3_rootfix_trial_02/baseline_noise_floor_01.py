# -*- coding: utf-8 -*-
"""¥0。ROOTFIX-01 の既存C1出力だけを使い、選択Fact集合の再現性ノイズ床(C1 rep1 vs rep2、C0 vs C1)を測る。API不使用。"""
import sys, os, json, statistics as s
HERE = os.path.dirname(os.path.abspath(__file__))
T1 = os.path.join(HERE, "..", "b3_fact_instruction_separation_trial_01")
sys.path.insert(0, T1)
from b3sep_common_01 import THEMES, theme_inputs, rj


def J(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1


out = {}
for th in THEMES:
    ev = theme_inputs(th)["ev"]
    r1 = rj(f"{T1}/runs/C1/{th}/rep1/selection.json")["parsed"]["selected_fact_ids"]
    r2 = rj(f"{T1}/runs/C1/{th}/rep2/selection.json")["parsed"]["selected_fact_ids"]
    out[th] = {"C1r1_vs_r2": round(J(r1, r2), 2), "C0_vs_C1r1": round(J(ev["selected_fact_ids"], r1), 2),
               "C0_vs_C1r2": round(J(ev["selected_fact_ids"], r2), 2), "n_C0_C1r1_C1r2": [len(ev["selected_fact_ids"]), len(r1), len(r2)]}
    print(th, out[th])
summ = {"mean_C1_r1_vs_r2": round(s.mean(v["C1r1_vs_r2"] for v in out.values()), 3),
        "mean_C0_vs_C1": round(s.mean([v["C0_vs_C1r1"] for v in out.values()] + [v["C0_vs_C1r2"] for v in out.values()]), 3),
        "themes_exact_r1_eq_r2": sum(v["C1r1_vs_r2"] == 1 for v in out.values())}
print(summ)
json.dump({"per_theme": out, "summary": summ}, open(os.path.join(HERE, "baseline_selection_noise_floor_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
