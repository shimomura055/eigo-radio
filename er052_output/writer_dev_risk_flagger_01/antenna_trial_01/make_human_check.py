# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
a = json.load(open(os.path.join(HERE, "aggregate_antenna_01.json"), encoding="utf-8"))
KN = {(k["theme"], k["model"], k["sid"]): k["id"] for k in a["known"]}
def cell(L, th, m): return json.load(open(os.path.join(HERE, "flags", "A%d" % L, th, m + ".json"), encoding="utf-8"))
def lab(k): return "%s/%s/%s" % (k[0], k[1], k[2])
o = ["# HUMAN_CHECK_ANTENNA_01: レベル別 人間確認一覧(新規追加分を区別)", "",
     "WRITER-DEV-RISK-FLAGGER-ANTENNA-TRIAL-01 Phase 3。各Flagは『人間が確認する価値があるか』をAIが示した候補であり、誤りの確定ではない。有用/ノイズの最終判定はユーザー。",
     "確信度は絶対評価に使わない。【既知】= 事前登録の既知候補10文(C01-C08, S1, S2)。Disney+(C01-C04)は完全台帳F07に根拠がある可能性が高い別区分。", ""]
for L in range(1, 7):
    cur = {}
    for th in ["streaming_price", "space_weapons", "byd_recall"]:
        for m in ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"]:
            d = cell(L, th, m)
            for x in d["flags"]: cur[(th, m, x["sentence_id"])] = (x, d)
    prev = set(tuple(k) for k in (a["transitions"]["A%d->A%d" % (L - 1, L)]["kept"] if L > 1 else []))
    new = [k for k in cur if k not in prev]
    lost = a["transitions"]["A%d->A%d" % (L - 1, L)]["lost"] if L > 1 else []
    o += ["## Antenna %d: %d記事 / %d件(前段から 維持%d・消失%d・新規%d)" % (L, a["levels"][str(L)]["n_articles"], len(cur), len(prev), len(lost), len(new)), ""]
    if L > 1 and lost:
        o.append("消失(前段にあって今回出なかった): " + "、".join(lab(tuple(k)) + ("【既知%s】" % KN[tuple(k)] if tuple(k) in KN else "") for k in lost)); o.append("")
    if prev: o.append("維持(詳細は前段を参照): " + "、".join(lab(tuple(k)) + ("【既知%s】" % KN[tuple(k)] if tuple(k) in KN else "") for k in sorted(prev))); o.append("")
    if not cur: o += ["Flagなし(9記事すべて0件)。", ""]; continue
    if new:
        o.append("### 新規追加分"); o.append("")
        for k in sorted(new, key=lambda k: -cur[k][0]["confidence"]):
            x, d = cur[k]
            o.append("- **%s** %s%s / type=%s / 確信度=%s" % (lab(k), "【既知%s】" % KN[k] if k in KN else "", "", x["type"], x["confidence"]))
            o.append("  - 該当文: " + x["sentence"])
            for fid in x["fact_ids"]:
                o.append("  - 対応Fact %s: %s" % (fid, d["facts"].get(fid, "(台帳に見出し無し)").split("\n")[0][:160]))
            if not x["fact_ids"]: o.append("  - 対応Fact: なし(台帳に対応記述なし)")
            o.append("  - 理由(Flagger原文): " + x["question"])
        o.append("")
open(os.path.join(HERE, "HUMAN_CHECK_ANTENNA_01.md"), "w", encoding="utf-8").write("\n".join(o) + "\n")
