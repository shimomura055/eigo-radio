"""委任_03 費用台帳(個別Cap¥70)。usage: <python> ledger.py [--check <今回起動の見積り円> [--inflight <他の実行中runの未実測見積り円>]]
実測=M10 cost_log + J2 part1/part2 + X/Y/Z evidence run(run_n5ev3)のcost/raw_usage log。実測+見積りがCapを超える見込みなら rc=3(起動しない)。"""
import sys, os, glob, json
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
import er053_cost_aggregate_01 as agg
EV3 = os.path.join(ROOT, "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03")
CAP = 70.0
parts = {}
parts["m10"] = sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(EV3 + "/m10/*/cost_log.jsonl"))
parts["j2_checks"] = sum(json.load(open(f, encoding="utf-8")).get("cost_jpy", 0.0) for f in glob.glob(EV3 + "/j2_part*_result.json"))
for k, p in (("X_a2", "er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_n5ev3/raw_usage_log.jsonl"),
             ("Y", "er121_output/family_y_production_01/redelivery_fee/run_n5ev3/cost_log.jsonl"),
             ("Z", "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_n5ev3/cost_log.jsonl")):
    parts[k] = agg.compute_stage_cost_breakdown_multi(os.path.join(ROOT, p))["total_jpy"] if os.path.exists(os.path.join(ROOT, p)) else 0.0
for f in glob.glob(EV3 + "/extra_cost_*.json"):
    parts[os.path.basename(f)] = json.load(open(f, encoding="utf-8")).get("cost_jpy", 0.0)
total = round(sum(parts.values()), 3)
print(json.dumps({"parts": {k: round(v, 3) for k, v in parts.items()}, "total_jpy": total, "cap_jpy": CAP}, ensure_ascii=False))
if "--check" in sys.argv:
    est = float(sys.argv[sys.argv.index("--check") + 1])
    infl = float(sys.argv[sys.argv.index("--inflight") + 1]) if "--inflight" in sys.argv else 0.0
    if total + infl + est > CAP:
        print(f"LEDGER GUARD: total={total} + inflight={infl} + est={est} > Cap {CAP}. 起動しない"); sys.exit(3)
