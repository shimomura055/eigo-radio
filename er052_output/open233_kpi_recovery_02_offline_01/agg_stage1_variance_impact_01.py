# -*- coding: utf-8 -*-
# 委任_10 CORRECTION-02: Stage 1非決定性の影響分析(0円、既存データのみ、API呼出なし)。ユーザー判断の材料であり採用提案ではない。
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import er052_open233_stage1_phase1_recall_check_01 as P
runner = P.runner
A = "er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01"
OUTD = "er052_output/open233_kpi_recovery_02_offline_01"
SC = [("B3", "bgroup_B3"), ("B4-a", "bgroup_B4"), ("A2A3-0", "safety_A2A3"), ("A4-0", "safety_A4"), ("A5-0", "safety_A5"),
      ("B3-same@neg5", "neg5_hormuz_div_a2")]


def runs_of(k):
    out = []
    for i in range(1, 5):
        f = "%s/%s/run_%d.json" % (A, k, i)
        if os.path.exists(f):
            out.append(json.load(open(f, encoding="utf8")))
    return out


INS = P.instances()
INSA = P.instances_a()


def v0_rec(k):
    if k in INS:
        fx, vp = INS[k]
        return P.v0_record(fx, vp)
    fx, _ = INSA[k]
    return fx.get("baseline_parsed"), "fixture.baseline_parsed"


res = {"sc": {}, "hf011": {}, "neg": {}, "cost": {}}
for sub, k in SC:
    rr = runs_of(k)
    det = [any(P.sc_match(k, x) == sub for x in P.majors(r["parsed"])) for r in rr]
    v0, src = v0_rec(k)
    v0hit = (any(P.sc_match(k, x) == sub for x in P.majors(v0)) if v0 else None)
    fz = P.rep30_stage1(k)
    fzhit = [any(P.sc_match(k, x) == sub for x in st if x.get("severity") == "MAJOR") for st in fz]
    if k == "bgroup_B3" and v0:  # rep30はV0差替え=実使用
        fzhit = [bool(v0hit)] * len(fz)
    res["sc"][sub] = {"instance": k, "per_run_detect": det, "A_single_rate": "%d/%d" % (sum(det), len(det)),
                      "A_union_run1_run2": any(det[:2]),
                      "A_run1_or_V0": ((det[0] or bool(v0hit)) if v0 is not None else None),
                      "A_union_all_runs": any(det), "n_runs": len(det),
                      "V0_record": v0hit, "V0_src": src, "frozen_rep30_used": fzhit}
# B2_hormuz HF-011(SC定義外のB群既知重大: V0記録=rep30実使用)
rr = runs_of("bgroup_B2_hormuz")
fx = INSA["bgroup_B2_hormuz"][0]
v0m = P.majors(fx.get("baseline_parsed"))
det = [any(P.same_claim(d0, d) for d0 in v0m for d in P.majors(r["parsed"])) for r in rr]
res["hf011"] = {"per_run_detect": det, "A_single_rate": "%d/%d" % (sum(det), len(det)), "A_union_run1_run2": any(det),
                "A_run1_or_V0": True, "V0_record": bool(v0m), "frozen_rep30_used": True,
                "note": "V0記録=Production記録=rep30差替え元。AにV0記録を足せば当然検出(V0 n=1の再現性は未測定)"}
# (b) 負例/NORMAL群MAJOR出現率
rows = {}
for k in P.A_NEG:
    rr = runs_of(k)
    has = [bool(P.majors(r["parsed"])) for r in rr]
    nm = [len(P.majors(r["parsed"])) for r in rr]
    v0, src = v0_rec(k)
    v0m = P.majors(v0) if v0 else None
    fz = P.rep30_stage1(k)
    fzh = [any(d.get("severity") == "MAJOR" for d in st) for st in fz]
    rows[k] = {"A_run_has_major": has, "A_major_counts": nm, "A_union12": any(has[:2]),
               "V0_major_n": (len(v0m) if v0m is not None else None), "V0_src": src,
               "A_run1_or_V0": ((has[0] or bool(v0m)) if v0m is not None else None), "frozen_runs_has_major": fzh}
res["neg"]["per_instance"] = rows
n = len(rows)


def runrate(key):
    return sum(sum(r[key]) for r in rows.values()), sum(len(r[key]) for r in rows.values())


a = runrate("A_run_has_major")
z = runrate("frozen_runs_has_major")
u = sum(r["A_union12"] for r in rows.values())
S = {"A_single_run_rate": "%d/%d (%.1f%%)" % (a[0], a[1], 100 * a[0] / a[1]),
     "A_union_run1_run2_instance_rate": "%d/%d (%.1f%%)" % (u, n, 100 * u / n),
     "frozen_rep30_run_rate": "%d/%d (%.1f%%)" % (z[0], z[1], 100 * z[0] / z[1]),
     "V0_record_instance_rate": None, "A_run1_or_V0_instance_rate": None}
v0n = [r for r in rows.values() if r["V0_major_n"] is not None]
if v0n:
    S["V0_record_instance_rate"] = "%d/%d (V0記録のあるinstanceのみ)" % (sum(r["V0_major_n"] > 0 for r in v0n), len(v0n))
    S["A_run1_or_V0_instance_rate"] = "%d/%d (V0記録のあるinstanceのみ)" % (sum(bool(r["A_run1_or_V0"]) for r in v0n), len(v0n))
res["neg"]["summary"] = S
# (c) 費用
calls = [json.load(open(os.path.join(dp, f), encoding="utf8"))["cost_jpy"] for dp, _, fs in os.walk(A) for f in fs if f.startswith("run_")]
avgA = sum(calls) / len(calls)
v0cost = []
for k, (fx, vp) in INS.items():
    if vp and os.path.exists(vp):
        x = json.load(open(vp, encoding="utf8"))
        if x.get("usage") and (x.get("model_returned") or x.get("model")) == "gpt-5.6-luna":
            v0cost.append(P.cost_for("gpt-5.6-luna", x["usage"]))
avgV0 = sum(v0cost) / len(v0cost) if v0cost else None
res["cost"] = {"A_calls_n": len(calls), "A_avg_per_call_jpy": round(avgA, 4), "A_single": round(avgA, 4),
               "A_union_2calls": round(2 * avgA, 4), "V0_5.6luna_n_records": len(v0cost),
               "V0_5.6luna_avg_per_call_jpy_est": round(avgV0, 4) if avgV0 else None,
               "A_single_plus_V0": round(avgA + avgV0, 4) if avgV0 else None, "frozen_rep30": 0.0,
               "note": "V0@5.6単価はer050 V0 prompt記録(gpt-5.6-luna)のusage tokensをRATES(0.20/0.02/1.20 USD per 1M、156.88円/USD)で換算した推定(委任_05 cell_cand_56luna実測0.728は候補promptのため不使用)。n=%d" % len(v0cost)}
json.dump(res, open(OUTD + "/agg_stage1_variance_impact_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)


def yn(b):
    return "-" if b is None else ("検出" if b else "見逃し")


L = ["# Stage 1非決定性の影響分析(委任_10 CORRECTION-02、0円・既存データのみ)", "",
     "**本資料はユーザー判断の材料(事実の集計)であり、採用提案ではない。Fable/Claudeは新Checker仕様を新設・選定していない。**",
     "出典: `a_frozen_fresh_01/`(A構成fresh、n=2、A4はn=4)、rep30 frozen記録、V0記録(Production記録n=1)。集計: `agg_stage1_variance_impact_01.py`、数値は同名json。", "",
     "## (a) Safety-critical 6 claim + B2_hormuz HF-011 の検出有無", "",
     "| claim | A単発(run別) | A 2回和集合(run1∪run2) | A run1∪V0記録 | V0記録(n=1) | frozen(rep30実使用) |", "|---|---|---|---|---|---|"]
for sub, v in res["sc"].items():
    L.append("| %s | %s (%s) | %s | %s | %s | %s |" % (
        sub, v["A_single_rate"], "/".join("○" if x else "×" for x in v["per_run_detect"]),
        yn(v["A_union_run1_run2"]), yn(v["A_run1_or_V0"]), yn(v["V0_record"]),
        "/".join("検出" if x else "見逃し" for x in v["frozen_rep30_used"])))
h = res["hf011"]
L.append("| B2_hormuz HF-011 | %s (%s) | %s | 検出(V0記録を足したため) | %s | 検出(V0差替え) |" % (
    h["A_single_rate"], "/".join("○" if x else "×" for x in h["per_run_detect"]), yn(h["A_union_run1_run2"]), yn(h["V0_record"])))
L += ["", "注: A4-0はn=4(和集合はrun1∪run2で表記、全run和集合はjson `A_union_all_runs`)。V0記録が当該instanceに存在しない場合は`-`。", "",
      "## (b) 負例/NORMAL群(neg1〜3+NORMAL3)のMAJOR出現率", "", "| 方式 | MAJOR出現率 |", "|---|---|",
      "| A単発(run単位) | %s |" % S["A_single_run_rate"],
      "| A 2回和集合(instance単位) | %s |" % S["A_union_run1_run2_instance_rate"],
      "| frozen(rep30、run単位) | %s |" % S["frozen_rep30_run_rate"],
      "| V0記録(instance単位) | %s |" % S["V0_record_instance_rate"],
      "| A run1∪V0(instance単位) | %s |" % S["A_run1_or_V0_instance_rate"], "",
      "和集合の率は単発以上になる(各runのMAJORの和)。instance別内訳はjson `neg.per_instance`。", "",
      "## (c) 1記事あたりStage 1追加費用の推定", "", "| 方式 | 円/記事 |", "|---|---|"]
c = res["cost"]
L += ["| A単発(1 call、実測平均 n=%d) | %.3f |" % (c["A_calls_n"], c["A_single"]),
      "| A 2回和集合(2 call) | %.3f |" % c["A_union_2calls"],
      "| A単発+V0(2 call) | %s |" % c["A_single_plus_V0"],
      "| frozen再利用 | 0(ただしfrozen出力は新記事には存在しない) |", "",
      "V0@gpt-5.6-luna 1 call単価の推定=%s円。%s" % (c["V0_5.6luna_avg_per_call_jpy_est"], c["note"]), "",
      "## 限界(確認/推測)",
      "- 確認: 上記数値は既存jsonの機械集計。n=2(A4のみ4)でサンプルが小さく、率の差は統計的に確定的ではない。",
      "- 確認: V0記録はn=1で、V0自体のrun間変動は本資料では測っていない(V0が安定だとは言えない)。",
      "- 推測: run数を増やせば検出が増える可能性とMAJOR誤検出が増える可能性の双方がある。"]
open(OUTD + "/agg_stage1_variance_impact_01.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("\n".join(L))
print(json.dumps(res["cost"], ensure_ascii=False))
