# -*- coding: utf-8 -*-
"""委任_03 追加分析(API 0): (1)事前登録ラベル(strict)と、承認済みNumeric Precision既定に整合させた事後再ラベル(post-hoc, v2)の両方での正解率
(2)提案(未採用)の追加検証V8『概数の相対誤差上限』を保存済みLuna判断へ適用したときの効果(誤丸め阻止数/正解丸め阻止数)。
事後再ラベルは事前登録ラベルを置き換えない(両方報告)。出力: evidence/label_v2_analysis.json
"""
from __future__ import annotations

import json
import os
from decimal import Decimal

import er090_b3_core_number_rounding_trial_01_overlay as ov
import er090_b3_core_number_rounding_trial_02_labels as lab
import er090_b3_core_number_rounding_trial_02_run as r2

ROOT = r2.ROOT
# 事後再ラベル(post-hoc。根拠=NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK『小数%は概数が既定: 25.2%→約25%、44.7%→約45%、89.6%→約90%』
#  er003_v1_n3_01_evidence_compression_editor.py:121-131 / 既に概数・CEO丸め値の再丸めは承認済み規定が無く境界扱い)
RELABEL = {
    ("art_e94a50c1", "8.7%"): "O", ("art_e94a50c1", "6.1%"): "O", ("art_7a5593c4", "5.98％"): "O", ("art_9bd6834e", "9.59％"): "O",
    ("art_9bd6834e", "7.29ドル"): "O",
    ("art_9bd6834e", "約2.6％"): "B", ("art_36b2c87d", "約348億ドル"): "B", ("art_36b2c87d", "167億ドル"): "B", ("art_36b2c87d", "54％"): "B",
}
V8_MAX_REL = Decimal("0.10")      # 提案(未採用)の閾値例


def rel_change(exact_surface, approx_surface):
    e, a = ov.parse_surface(exact_surface)["value"], ov.parse_surface(approx_surface)["value"]
    if e is None or a is None or e == 0:
        return None
    return abs(a - e) / e


def score(rows, labels, v8=False):
    s = {"n_A": 0, "n_E": 0, "n_O": 0, "n_B": 0, "correct_A_E": 0, "over_round": 0, "missed_round": 0, "O_rounded": 0, "B_rounded": 0, "v8_blocked_wrong": 0, "v8_blocked_right": 0}
    for r in rows:
        L = labels.get((r["article"], r["surface"]))
        if L is None:
            continue
        final = r["final"] == ov.DECISION_APPROX
        if v8 and final and r["approx"]:
            rc = [rel_change(r["surface"], r["approx"][0])]
            if rc[0] is not None and rc[0] > V8_MAX_REL:
                final = False
                s["v8_blocked_wrong" if L == "A" else "v8_blocked_right"] += 1
        if L == "B":
            s["n_B"] += 1
            s["B_rounded"] += int(final)
        elif L == "O":
            s["n_O"] += 1
            s["O_rounded"] += int(final)
        else:
            s["n_" + L] += 1
            ok = final == (L == "A")
            s["correct_A_E"] += int(ok)
            if L == "E" and final:
                s["over_round"] += 1
            if L == "A" and not final:
                s["missed_round"] += 1
    return s


def main():
    ev = r2.load_json(os.path.join(ROOT, "evidence", "judge_eval.json"))
    labels1 = {k: v for k, v in lab.LABELS.items()}
    labels2 = dict(labels1)
    labels2.update(RELABEL)
    out = {"v8_max_rel_change": str(V8_MAX_REL), "by_run": {}}
    runs = sorted({r["run"] for r in ev["rows"] if r["run"].startswith("luna_")}) + ["sol_matched4(Trial_01 v2 x3 + sol_v2 semi)"]
    four = {"art_a31992b5", "art_1e4c771e", "art_701612d8", "art_36b2c87d"}
    for run in runs:
        if run.startswith("sol_"):
            rows = [r for r in ev["rows"] if r["run"].startswith("sol_")]
        else:
            rows = [r for r in ev["rows"] if r["run"] == run]
        out["by_run"][run + "|all_articles"] = None
        if run.startswith("luna_"):
            sub = [r for r in rows if r["article"] in four]
            out["by_run"][run + "|matched4"] = {"strict_prereg": score(sub, labels1), "posthoc_v2": score(sub, labels2)}
        out["by_run"].pop(run + "|all_articles")
        out["by_run"][run] = {"strict_prereg": score(rows, labels1), "posthoc_v2": score(rows, labels2),
                              "posthoc_v2_plus_V8": score(rows, labels2, v8=True), "strict_plus_V8": score(rows, labels1, v8=True)}
    # 全final APPROXの相対誤差分布(Luna全run)
    dist = []
    for r in ev["rows"]:
        if r["run"].startswith("luna_") and r["final"] == ov.DECISION_APPROX and r["approx"]:
            rc = rel_change(r["surface"], r["approx"][0])
            dist.append({"run": r["run"], "article": r["article"], "surface": r["surface"], "approx": r["approx"][0],
                         "rel_change": None if rc is None else round(float(rc), 4), "label_prereg": labels1.get((r["article"], r["surface"]))})
    dist.sort(key=lambda x: -(x["rel_change"] or 0))
    out["approx_rel_change_top"] = dist[:15]
    out["n_final_approx_total"] = len(dist)
    out["n_over_10pct"] = sum(1 for x in dist if (x["rel_change"] or 0) > float(V8_MAX_REL))
    r2.save_json(os.path.join(ROOT, "evidence", "label_v2_analysis.json"), out)
    for run, v in out["by_run"].items():
        if "posthoc_v2_plus_V8" not in v:
            print(run, "strict", {k: v["strict_prereg"][k] for k in ("correct_A_E", "over_round", "missed_round", "n_A", "n_E")}, "| v2", {k: v["posthoc_v2"][k] for k in ("correct_A_E", "over_round", "missed_round", "n_E", "O_rounded", "B_rounded")})
            continue
        print(run, "strict", {k: v["strict_prereg"][k] for k in ("correct_A_E", "over_round", "missed_round", "n_A", "n_E")},
              "| v2", {k: v["posthoc_v2"][k] for k in ("correct_A_E", "over_round", "missed_round", "n_E", "O_rounded", "B_rounded")},
              "| v2+V8", {k: v["posthoc_v2_plus_V8"][k] for k in ("correct_A_E", "over_round", "missed_round", "v8_blocked_right", "v8_blocked_wrong")})
    print("approx top rel:", [(x["surface"], x["approx"], x["rel_change"], x["label_prereg"]) for x in dist[:8]], "n>10%:", out["n_over_10pct"], "/", len(dist))


if __name__ == "__main__":
    main()
