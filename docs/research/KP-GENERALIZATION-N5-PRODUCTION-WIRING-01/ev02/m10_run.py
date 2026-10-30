"""M10 統合replay: Production generate_candidates(公式経路・N5既定ON)を1 round実行する。usage: python m10_run.py <case_id> (cwd=repo root)
監督ループ・自動再試行なし。費用Cap(M10 ¥20)は呼出前に既存実測を合算して確認する。"""
import sys, os, json, glob
ROOT = os.path.abspath(os.getcwd())
sys.path.insert(0, ROOT)
EV = os.path.join(ROOT, "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev02")
CAP = 20.0
cid = sys.argv[1]
import er005_cost_logger as cl
import er053_cost_aggregate_01 as agg
spent = sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/m10/*/cost_log.jsonl"))
if spent >= CAP * 0.85:
    print(f"M10 Cap guard: spent={spent:.2f} >= 85% of {CAP}. 実行しない"); sys.exit(3)
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
text = fx["cases"][cid]["text"]
level = cid.rsplit("_", 1)[1]
source_level, process = ("A2", "A2_SUPPORT") if level == "a2" else ("B1", "B1_SUPPORT")
out = f"{EV}/m10/{cid}"; os.makedirs(out, exist_ok=True)
cl.install(f"{out}/cost_log.jsonl")
import er119_kp_candidates_01 as kcand
import er003_v1_n3_01_scaffold_generate as sc
gen = kcand.make_generate_fn(text, f"{out}/kp", f"M10_{cid}", source_level, level, process, stop_check_fn=sc.make_stop_check(EV))
with cl.logging_context(theme=f"M10_{cid}", stage="kp_candidates_m10"):
    r = gen(1, [])
json.dump(r, open(f"{out}/result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
b = agg.compute_stage_cost_breakdown_multi(f"{out}/cost_log.jsonl")
json.dump(b, open(f"{out}/cost.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(cid, "ok=", r.get("ok"), "cost_jpy=", b["total_jpy"], json.dumps(b["by_stage_jpy"], ensure_ascii=False))
