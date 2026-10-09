# -*- coding: utf-8 -*-
"""P2 詳細表(委任_02): ユニット別に、ラベル・D0(rollback)・D2 rep1/rep2・D1full(gate)・D1の呼び出しタイプを並べ、再現性と誤Flag/見逃しを可視化。
ラベルはここ(集計側)でのみ読む。出力: results/P2_DETAIL_01.md"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
LABELS = os.path.join(HERE, "..", "casebank", "casebank_01_labels.json")


def load(name):
    p = os.path.join(RES, name + ".jsonl")
    return {json.loads(l)["unit_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()}


def cell(row, exclude_gate=False):
    if row is None:
        return "-"
    fl = [f for f in row["flags"] if f.get("severity") == "重大" and not (exclude_gate and f.get("gate_only"))]
    return ", ".join("%s(%.2f)" % (f["type"], f["confidence"]) for f in fl) or "."


def main():
    labels = json.load(open(LABELS, encoding="utf-8"))
    out = ["# P2_DETAIL_01(ユニット別、dev + 合成dev)", "", "凡例: `.`=Flagなし。括弧内=confidence。D1の『呼び出し』=D0ゲートで実際に呼んだタイプ数/5。", ""]
    agree = {"units": 0, "same": 0, "flag_units_r1": 0, "flag_units_r2": 0, "flag_units_both": 0}
    for sp in ("dev", "synthetic_dev"):
        d0 = load("d0_none_" + sp)
        r1, r2 = load("d2_gpt-6.1-sol_%s_rep1" % sp), load("d2_gpt-6.1-sol_%s_rep2" % sp)
        d1 = load("d1full_gpt-6.1-sol_%s_gate" % sp)
        out += ["## %s" % sp, "| unit | 正解 | 根拠/種別 | D0(rollbackのみ) | D2 rep1 | D2 rep2 | D1full gate(呼び出し) |", "|---|---|---|---|---|---|---|"]
        for uid in d1:
            l = labels[uid]
            lab = "重大" if l["label"].startswith("重大") else "非重大(%s)" % (l.get("neg_group") or "")
            out.append("| %s | %s | %s / %s | %s | %s | %s | %s (%d/5) |" % (
                uid, lab, l.get("label_basis", ""), l.get("accident_type", ""), cell(d0[uid], True), cell(r1[uid]), cell(r2[uid]),
                cell(d1[uid]), len(d1[uid].get("calls", []))))
            a = bool([f for f in r1[uid]["flags"]])
            b = bool([f for f in r2[uid]["flags"]])
            agree["units"] += 1
            agree["same"] += int(a == b)
            agree["flag_units_r1"] += int(a)
            agree["flag_units_r2"] += int(b)
            agree["flag_units_both"] += int(a and b)
        out.append("")
    out += ["## D2の再現性(rep1 vs rep2、Flagが立つ/立たないのユニット単位一致)",
            "- 一致 %d/%d ユニット / rep1でFlag %d・rep2でFlag %d・両方でFlag %d" % (
                agree["same"], agree["units"], agree["flag_units_r1"], agree["flag_units_r2"], agree["flag_units_both"]), ""]
    # 誤Flag・見逃しの文面
    out += ["## 誤Flag(非重大に立ったFlag)と見逃し(重大)の文"]
    cb = json.load(open(os.path.join(HERE, "..", "casebank", "casebank_01_dev_blind.json"), encoding="utf-8"))["cases"]
    sy = json.load(open(os.path.join(HERE, "..", "casebank", "casebank_01_synthetic_dev_blind.json"), encoding="utf-8"))["cases"]
    sent = {c["case_id"]: c["sentence"] for c in cb + sy}
    d1all = {}
    for sp in ("dev", "synthetic_dev"):
        d1all.update(load("d1full_gpt-6.1-sol_%s_gate" % sp))
        r1 = load("d2_gpt-6.1-sol_%s_rep1" % sp)
        for uid, row in r1.items():
            l = labels[uid]
            sev = l["label"].startswith("重大")
            fl = [f for f in row["flags"] if f.get("severity") == "重大"]
            if (not sev and fl) or (sev and not fl):
                out.append("- **%s** [%s] %s\n  - 文: %s\n  - D2 rep1: %s" % (uid, "見逃し" if sev else "誤Flag", l.get("accident_type", ""), sent[uid],
                                                                          "; ".join(f["question"] for f in fl) or "(Flagなし)"))
    out.append("")
    out.append("## D1fullの誤Flag(非重大に立ったFlag)")
    for uid, row in d1all.items():
        l = labels[uid]
        if not l["label"].startswith("重大") and row["flags"]:
            for f in row["flags"]:
                out.append("- **%s** %s(%.2f) %s\n  - 文: %s" % (uid, f["type"], f["confidence"], f["question"], sent[uid]))
    with open(os.path.join(RES, "P2_DETAIL_01.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
