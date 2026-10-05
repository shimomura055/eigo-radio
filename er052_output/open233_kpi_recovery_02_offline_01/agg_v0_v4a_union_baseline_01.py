# -*- coding: utf-8 -*-
"""OPEN-233 委任_05 Opus#16 事前作業5: 「V0 ∪ V4A」(既存データのみ、¥0)の正式SC検出・候補数の基準線。採用提案ではない(基準線のみ)。
provenance: V0記録=Production V0実記録(fixture.baseline_parsed/er050 run_1)n=1、V0@6luna=cell_v0_6luna n=2、V4A=A構成fresh(a_frozen_fresh_01)n=2、
候補@5.6=cell_cand_56luna n=1(参考行)。pairing=同一run番号。"""
import json, os, sys
sys.path.insert(0, os.getcwd())
import er052_open233_stage1_phase1_recall_check_01 as p1
R = p1.runner
BASE = p1.OUT_BASE
SC = [("B3", "bgroup_B3"), ("B4-a", "bgroup_B4"), ("A2A3-0", "safety_A2A3"), ("A4-0", "safety_A4"), ("A5-0", "safety_A5"), ("B3-same@neg5", "neg5_hormuz_div_a2")]
NEG = ["neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b"]
NORMAL = ["hormuz_run02_advanced", "hormuz_run03_advanced", "meta_run03_advanced", "meta_run03_standard"]
INST_A = p1.instances_a()
INST_P = p1.instances()


def load(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def runs_of(sub, inst, n):
    out = []
    for j in range(1, n + 1):
        x = load("%s/%s/%s/run_%d.json" % (BASE, sub, inst, j) if sub else "%s/%s/run_%d.json" % (BASE, inst, j))
        out.append(x["parsed"] if x else None)
    return out


V4A_DIR = "a_frozen_fresh_01"
def v4a(inst): return runs_of(V4A_DIR, inst, 2)
def v0_6(inst): return runs_of("cell_v0_6luna", inst, 2)
def cand56(inst): return runs_of("cell_cand_56luna", inst, 1)
def v0rec(inst):
    if inst in INST_P:
        fx, vp = INST_P[inst]
    elif inst in INST_A:
        fx, vp = INST_A[inst]; vp = None
    else:
        return None
    parsed, src = p1.v0_record(fx, vp)
    return parsed


def sc_hit(inst, sub, parsed):
    if parsed is None: return None
    return any(p1.sc_match(inst, d) == sub for d in p1.majors(parsed))


rows = []
for sub, inst in SC:
    rec = v0rec(inst)
    a, b, c = v4a(inst), v0_6(inst), cand56(inst)
    row = {"sc": sub, "instance": inst,
           "V0_record(n=1)": sc_hit(inst, sub, rec),
           "V0@6luna": [sc_hit(inst, sub, x) for x in b],
           "V4A_fresh(first2)": [sc_hit(inst, sub, x) for x in a],
           "cand@5.6luna(n=1)": [sc_hit(inst, sub, x) for x in c]}
    un6 = [None if (x is None or y is None) else (x or y) for x, y in zip([sc_hit(inst, sub, x) for x in b], row["V4A_fresh(first2)"])]
    unrec = [None if (row["V0_record(n=1)"] is None or y is None) else (row["V0_record(n=1)"] or y) for y in row["V4A_fresh(first2)"]]
    row["union_V0@6luna_V4A(paired)"] = un6
    row["union_V0record_V4A(run_j)"] = unrec
    rows.append(row)


def frac(l):
    v = [x for x in l if x is not None]
    return "N/A" if not v else "%d/%d" % (sum(bool(x) for x in v), len(v))


def cnt_union(v0p, v4p):
    mv = p1.majors(v0p) if v0p else []
    m4 = p1.majors(v4p) if v4p else []
    extra = [d for d in m4 if not any(p1.same_claim(d, e) for e in mv)]
    return len(mv), len(m4), len(mv) + len(extra)


cand_rows = []
for inst in NEG + NORMAL:
    rec = v0rec(inst)
    a, b = v4a(inst), v0_6(inst)
    per = {"instance": inst, "kind": "neg" if inst in NEG else "NORMAL/B群",
           "V0_record_majors": len(p1.majors(rec)) if rec else None,
           "V4A_majors_per_run": [len(p1.majors(x)) if x else None for x in a],
           "V0@6luna_majors_per_run": [len(p1.majors(x)) if x else None for x in b],
           "union_V0@6luna_V4A_per_run": [cnt_union(y, x)[2] if (x and y) else None for x, y in zip(a, b)],
           "union_V0record_V4A_per_run": [cnt_union(rec, x)[2] if (x and rec) else None for x in a]}
    cand_rows.append(per)
res = {"provenance": "V0記録=Production V0実記録 n=1 / V0@6luna n=2(cell_v0_6luna) / V4A=A構成fresh n=2 / 候補@5.6 n=1。既存保存データのみ(新規API 0)",
       "sc": rows, "candidates": cand_rows,
       "note": "基準線のみ。採用提案ではない。n=1〜2のため見逃しゼロの証明ではない。neg5はV0実記録(fixture.baseline_parsed、Productionで流出した出力)が見逃し、V0@6luna/候補@5.6のrunは存在しない(N/A)。V0@6luna cellにはNORMAL群のrunが無い。"}
OUT = os.path.dirname(os.path.abspath(__file__))
json.dump(res, open(OUT + "/agg_v0_v4a_union_baseline_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
L = ["# V0∪V4A基準線(委任_05 事前作業5、¥0、採用提案ではない)", "", "- " + res["provenance"], "",
     "## 正式SC 6件の検出(MAJOR claimがtext_pattern/substringに一致)", "",
     "| SC | V0記録(n=1) | V0@6luna | V4A fresh | V0@6luna∪V4A(run対応) | V0記録∪V4A | 候補@5.6 |", "|---|---|---|---|---|---|---|"]
for r in rows:
    L.append("| %s | %s | %s | %s | **%s** | **%s** | %s |" % (r["sc"], r["V0_record(n=1)"], frac(r["V0@6luna"]), frac(r["V4A_fresh(first2)"]),
             frac(r["union_V0@6luna_V4A(paired)"]), frac(r["union_V0record_V4A(run_j)"]), frac(r["cand@5.6luna(n=1)"])))
L += ["", "## 候補数(MAJOR claim数/記事・run、neg=誤検出側、NORMAL=本来0が望ましい)", "",
      "| instance | 種別 | V0記録 | V0@6luna/run | V4A/run | ∪(V0@6luna,V4A)/run | ∪(V0記録,V4A)/run |", "|---|---|---|---|---|---|---|"]
for c in cand_rows:
    L.append("| %s | %s | %s | %s | %s | %s | %s |" % (c["instance"], c["kind"], c["V0_record_majors"], c["V0@6luna_majors_per_run"], c["V4A_majors_per_run"],
             c["union_V0@6luna_V4A_per_run"], c["union_V0record_V4A_per_run"]))
L += ["", "注: " + res["note"]]
open(OUT + "/agg_v0_v4a_union_baseline_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
