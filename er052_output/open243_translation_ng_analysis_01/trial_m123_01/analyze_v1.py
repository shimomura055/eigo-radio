# -*- coding: utf-8 -*-
"""V1 集計。"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

V1 = f"{C.TRIAL}/v1"
ORDER = ["G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10", "G11", "G12", "G13", "G14", "EV28"]
STOP8 = {"G02", "G03", "G06", "G07", "G08", "G09", "G12", "G14"}
# 判定: 手動(ユーザー回答で「許容」とした型を attempt1 の MAJOR が含む世代: users=開示の相手 / oil prices=指標の一般化 / so=因果の接続詞)
ALLOWED_TYPE_ATTEMPT1 = {"G02": "users(+prompting因果)", "G06": "oil prices", "G07": "users", "G09": "users", "G12": "users"}
FLAGS = C.vfl01.DEVIATION_FLAG_KEYS


def located(claim, summary, body):
    c = C.norm(claim)
    import re
    c = C.norm(re.sub(r"^\s*(##\s*)?in one line\s*:?", "", claim or "", flags=re.I))
    if not c:
        return "?"
    if c in C.norm(body):
        return "body"
    s = C.norm(summary)
    if c in s or s in c:
        return "summary"
    return "?"


def main():
    out = []
    A = {}
    B = {}
    for g in ORDER:
        A[g] = json.load(open(f"{V1}/{g}_phaseA.json", encoding="utf-8"))
        p = f"{V1}/{g}_phaseB.json"
        B[g] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    # 本文は fixture から取る(位置判定用)
    import v1_summary_regen as v1
    fx = {g[0]: v1.load_fixture(*g) for g in v1.GENS}
    out.append("| 世代 | 従来(本文ごと再生成) | 旧attempt1 MAJOR(要約) | 許容型を含む | 新・腕R: 要約のみ再生成 | 解消(COMPLIANT+前回指摘解消) | 前回指摘の解消 | 腕R後の新規MAJOR(位置/origin/型) | 腕F(初回JA+台帳入力)のMAJOR(要約/本文) | M1+M2 最終check |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    n_ok = n_prior = 0
    stop_remaining = []
    resolved_prior6 = 0
    for g in ORDER:
        a = A[g]
        R = a.get("armR")
        conv = {True: "解消", False: "STOP", None: "-"}[a["conventional_resolved"]]
        a1 = "; ".join("+".join(m["flags"]) for m in a["attempt1_majors"]) or "(指摘なし=EV-28見逃し)"
        if R:
            last = R["attempts"][-1]
            ok = R["success"]
            pri = last["all_prior_issues_resolved"]
            n_ok += ok
            n_prior += pri
            if not ok and g in STOP8:
                stop_remaining.append(g)
            if ok and g not in STOP8:
                resolved_prior6 += 1
            newm = [d for d in last["deviations"] if d["severity"] == "MAJOR"]
            newm_s = "; ".join(f"{located(d['claim'], last['summary'], fx[g]['body'])}/{d['origin']}/{'+'.join(d['flags'])}" for d in newm) or "-"
            rs = f"{len(R['attempts'])}回: {last['summary']}"
            okc = "○" if ok else "×"
            pr = "○" if pri else "×"
        else:
            rs, okc, pr, newm_s = "(対象外)", "-", "-", "-"
        F = a["armF"]
        fm = [d for d in F["deviations"] if d["severity"] == "MAJOR"]
        fs = "; ".join(f"{located(d['claim'], F['summary'], fx[g]['body'])}/{d['origin']}/{'+'.join(d['flags'])}" for d in fm) or "なし"
        b = B[g]
        bs = "-"
        if b and "armR_M2" in b:
            m2 = [d for d in b["armR_M2"]["deviations"] if d["severity"] == "MAJOR"]
            bs = ("MAJOR " + "; ".join(f"{located(d['claim'], R['final_summary'], fx[g]['body'])}/{d['origin']}/{'+'.join(d['flags'])}" for d in m2)) if m2 else "COMPLIANT"
        out.append(f"| {g} | {conv} | {a1} | {ALLOWED_TYPE_ATTEMPT1.get(g, '-')} | {rs} | {okc} | {pr} | {newm_s} | {fs} | {bs} |")
    out.append("")
    out.append(f"要約MAJOR 14世代: 厳密解消(COMPLIANT かつ 前回指摘が全て解消) = {n_ok}/14、前回指摘(要約のMAJOR)の解消 = {n_prior}/14 (従来方式は 6/14)")
    out.append(f"STOP相当(未解消MAJOR)だった8世代のうち、なお未解消: {len(stop_remaining)}件 {stop_remaining} (従来は 8件)")
    out.append(f"従来で解消していた6世代のうち、新方式でも解消: {resolved_prior6}/6")
    # 費用
    tot = 0.0
    for g in ORDER:
        a = A[g]
        tot += a["armF"]["iol_cost_jpy"] + a["armF"]["check_cost_jpy"]
        for x in (a.get("armR") or {}).get("attempts", []):
            tot += x["iol_cost_jpy"] + x["check_cost_jpy"]
        if B[g] and "armR_M2" in B[g]:
            tot += B[g]["armR_M2"]["check_cost_jpy"]
    out.append(f"V1 実費 ¥{tot:.3f} (要約生成+check の実測トークン x 登録単価)")
    # 要約call単体の費用
    ic = [a["armF"]["iol_cost_jpy"] for a in A.values()] + [x["iol_cost_jpy"] for a in A.values() for x in (a.get("armR") or {}).get("attempts", [])]
    out.append(f"要約生成1call平均 ¥{sum(ic) / len(ic):.4f} (n={len(ic)}) (JA+台帳入力あり)")
    txt = "\n".join(out)
    open(f"{V1}/V1_RESULTS.md", "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
