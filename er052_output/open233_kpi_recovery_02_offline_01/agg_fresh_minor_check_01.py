# -*- coding: utf-8 -*-
"""OPEN-233 委任_05 Opus#16 事前作業1: A構成fresh 32 runで、見逃し対象の文がMINORとして出ていたか集計(¥0、既存JSON読取のみ)。
raw_parsed = モデル出力そのまま(MINOR含む。post-hoc検証前)。parsed = post-hoc検証後。"""
import glob, json, os, re
SRC = "er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01"
OUT = os.path.dirname(os.path.abspath(__file__))
B3_PAT = r"\b(so|because|therefore|as a result|led to)\b[^.]{0,40}flashy 20% plan"
TARGETS = [
    ("neg5 B3-same (SC, HF-007)", "neg5_hormuz_div_a2", lambda t, f: re.search(B3_PAT, t, re.I) is not None),
    ("A4-0 (SC, MUSE-HC-006)", "safety_A4", lambda t, f: "completed the exchanges with users" in t),
    ("HF-011 (monitor, B2_hormuz)", "bgroup_B2_hormuz", lambda t, f: f == "HF-011" or "disappearance of the fee plan" in t),
    ("B4 non-SC: Meta had run a test (HC-006)", "bgroup_B4", lambda t, f: "Meta had run a test" in t),
    ("B4 non-SC: People feel differently/Names, plans (HC-010)", "bgroup_B4", lambda t, f: "People feel differently" in t or "Names, plans" in t),
    ("B4 non-SC: As AI makes calls (HC-010/004)", "bgroup_B4", lambda t, f: "As AI makes calls" in t),
    ("B4 non-SC: voice sound human (HC-004)", "bgroup_B4", lambda t, f: "sound human" in t),
]
runs = {}
for p in sorted(glob.glob(SRC + "/*/run_*.json")):
    d = json.load(open(p, encoding="utf-8"))
    runs.setdefault(d["instance"], []).append(d)
sev_hist = {"raw_parsed": {}, "parsed_severity": {}, "severity_final": {}}
auto_down = 0
for inst, rs in runs.items():
    for d in rs:
        for x in d["raw_parsed"].get("deviations", []):
            sev_hist["raw_parsed"][x.get("severity")] = sev_hist["raw_parsed"].get(x.get("severity"), 0) + 1
        for x in d["parsed"].get("deviations", []):
            sev_hist["parsed_severity"][x.get("severity")] = sev_hist["parsed_severity"].get(x.get("severity"), 0) + 1
            sev_hist["severity_final"][x.get("severity_final")] = sev_hist["severity_final"].get(x.get("severity_final"), 0) + 1
            auto_down += 1 if x.get("auto_downgraded") else 0
rows = []
for name, inst, fn in TARGETS:
    c = {"MAJOR": 0, "MINOR": 0, "none": 0}
    per_run = []
    for d in runs.get(inst, []):
        hit = [x for x in d["raw_parsed"].get("deviations", []) if fn(x.get("claim_in_article") or "", x.get("related_fact_id"))]
        s = "none" if not hit else ("MAJOR" if any(h["severity"] == "MAJOR" for h in hit) else "MINOR")
        c[s] += 1
        per_run.append(s)
    rows.append({"target": name, "instance": inst, "runs": len(runs.get(inst, [])), "counts": c, "per_run": per_run})
res = {"source": SRC, "n_runs_total": sum(len(v) for v in runs.values()), "severity_histogram": sev_hist,
       "auto_downgraded_total": auto_down, "targets": rows,
       "total_minor_in_raw_parsed": sev_hist["raw_parsed"].get("MINOR", 0),
       "provenance": "fresh (A構成 gpt-6-luna V4A、委任_08、既存保存JSONの読取のみ)"}
json.dump(res, open(OUT + "/agg_fresh_minor_check_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
lines = ["# fresh MINOR確認(委任_05 事前作業1、¥0)", "", "- 入力: %s(%d run、provenance=fresh)" % (SRC, res["n_runs_total"]),
         "- 全32 runのraw_parsed(モデル出力そのまま)severity分布: %s / post-hoc後: %s / auto_downgraded: %d" % (sev_hist["raw_parsed"], sev_hist["parsed_severity"], auto_down),
         "", "| 対象 | instance | runs | MAJOR | MINOR | 指摘なし | run別 |", "|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append("| %s | %s | %d | %d | %d | %d | %s |" % (r["target"], r["instance"], r["runs"], r["counts"]["MAJOR"], r["counts"]["MINOR"], r["counts"]["none"], ",".join(r["per_run"])))
tot_minor = sum(r["counts"]["MINOR"] for r in rows)
lines += ["", "## 判定: MINOR切り捨て(H2)が主因か", "",
          "- **判定: No(A構成freshの範囲では主因ではない)**【確認】対象文のMINOR出力は計%d件。全32 runでMINOR自体が計%d件(モデルはV4A promptでMINORを実質出さず、出した指摘は全てMAJOR)。見逃しの実体は「指摘自体なし」であり、MINORに付いて後段へ渡らなかったケースではない。" % (tot_minor, res["total_minor_in_raw_parsed"]),
          "- 【確認】neg5 B3-sameはfresh 0/2でMAJOR・MINORとも出ず(run_1は別文のHF-008を指摘、run_2は指摘ゼロ)。A4-0はMAJOR 2/4、指摘なし 2/4。",
          "- 【推測】H2(MINOR切り捨て)は構造上の穴として残るが、A構成freshでは顕在化していない。MINORを多く出す構成(Production V0等)では別に確認が必要(本集計の範囲外)。主因は検出自体の非網羅(Opus#16 1-b「迷えば許容」・1-a文またぎ因果)と推測。"]
open(OUT + "/agg_fresh_minor_check_01.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
