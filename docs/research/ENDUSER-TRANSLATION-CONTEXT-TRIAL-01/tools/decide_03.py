# TRIAL_PLAN_02 §5 の基準を metrics_<split>.json に機械適用する(基準は事前登録どおり。緩和なし)。
import json, sys
mf = sys.argv[1]; vel = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}   # V適格 {"CV":true,...}
m = json.load(open(mf, encoding="utf-8"))
noise = m["cmp"].get("Ap_vs_A", {}).get("main", {})
g2_noise = noise.get("G2_worse_to_ge2"); g3_noise = noise.get("worse_rate")
res = {}
for c, b in m["by_cond"].items():
    if c in ("A", "Ap"):
        continue
    mm = m["cmp"][f"{c}_vs_A"]["main"]
    r = {}
    r["G1"] = mm["G1_A_le1_to_M3"] == 0
    r["G2"] = mm["G2_worse_to_ge2"] <= g2_noise + 1
    r["G3"] = mm["worse_rate"] <= g3_noise + 0.03
    r["G4a"] = b["fail_closed_parts"] <= m["by_cond"]["A"]["fail_closed_parts"]
    r["G4b"] = b["G4_calls_ratio"] <= 1.25
    r["B1b"] = bool(b.get("B1b_pass"))
    r["C1a"] = b["C1_extra_cost_per_article_jpy"] <= 1.0
    r["C1b"] = (b["C1_total_cost_ratio"] or 0) <= 1.30
    r["T1"] = b["T1_call_wall_median_ratio"] <= 1.3
    if c.endswith("V"):
        r["Veligible"] = bool(vel.get(c, False))
    r["ALL"] = all(r.values())
    res[c] = r
print("noise: G2(Ap)=", g2_noise, " worse_rate(Ap)=", g3_noise)
hdr = ["G1", "G2", "G3", "G4a", "G4b", "B1b", "C1a", "C1b", "T1", "Veligible", "ALL"]
print("cond", *hdr)
for c, r in res.items():
    print(c, *["-" if k not in r else ("PASS" if r[k] else "FAIL") for k in hdr])
cand = [c for c, r in res.items() if r["ALL"]]
cand.sort(key=lambda c: m["by_cond"][c]["C1_extra_cost_per_article_jpy"])
print("passing:", cand, "extra_cost/article:", {c: m["by_cond"][c]["C1_extra_cost_per_article_jpy"] for c in cand})
print("FINAL_CANDIDATE:", cand[0] if cand else None)
