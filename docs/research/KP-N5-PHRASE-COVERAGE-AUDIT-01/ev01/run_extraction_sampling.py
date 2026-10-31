"""ev01 step3: 候補抽出段の再現性確認。現行ProductionのP7(call1)とN5のB1過剰生成を、同一本文・同一Promptで各N回だけ呼ぶ(後段なし)。
5表現が抽出候補に出るか(出ないのは1回の揺れか構造的か)を見る。記事・音声の再生成なし。usage: python run_extraction_sampling.py <repo_root> [N=3]"""
import sys, os, json, glob, re
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 3
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
EV = os.path.join(ROOT, "docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/ev01")
CAP = float(os.environ.get("N5Q_CAP", "13.0"))
import er005_cost_logger as cl
import er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5
import er003_v1_n3_01_scaffold_generate as sc
import er105_kp_fulltext_selector_01 as ft
import er119_kp_p7w5_prompts_01 as p7w5
def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log*.jsonl"))
cl.install(f"{EV}/cost_log_sampling.jsonl")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
text = fx["cases"]["untidi_b1b"]["text"]
model = ft.resolve_model("B1_SUPPORT")
PATS = {"put away": r"\bput\b.{0,12}\baway\b", "in the way": r"in the way", "force away": r"\bforce\b.{0,10}\baway\b", "leave out": r"\b(leave|left)\b.{0,8}\bout\b", "in sight": r"in sight"}
out = {"model_p7": model, "p7_sha256": p7w5.P7_SHA256, "b1_prompt_sha16": n5.prompt_shas().get("B1"), "p7": [], "b1": []}
for i in range(N):
    if spent() + 0.5 > CAP: raise SystemExit("cost guard")
    msg = p7w5.build_p7_message(text, shown_phrases=None)
    fn = p7w5.make_p7_selector_fn(msg, model=model)
    with cl.logging_context(theme="N5Q_audit", stage="sample_p7"):
        raw, mid, rid = fn()
    items = [x["phrase"] for x in json.loads(raw)["items"]]
    out["p7"].append({"sample": i + 1, "model_id": mid, "response_id": rid, "phrases": items})
    print("P7", i + 1, items, "spent", round(spent(), 3)); sys.stdout.flush()
for i in range(N):
    if spent() + 0.5 > CAP: raise SystemExit("cost guard")
    ctx = n5.N5Ctx("B1_SUPPORT", tag=f"sample_b1_{i+1}", stop_check_fn=sc.make_stop_check(EV), article_id="N5Q_untidi_b1b")
    with cl.logging_context(theme="N5Q_audit", stage="sample_b1"):
        o, m = n5.call_llm("b1", n5.prompt_B1(text), n5.B1_SCHEMA, ctx, label="B1_overgen")
    sp = [c["span"] for c in o["candidates"]]
    out["b1"].append({"sample": i + 1, "model_id": m.get("model_id"), "spans": sp, "cost_jpy": m.get("cost_jpy")})
    print("B1", i + 1, sp, "spent", round(spent(), 3)); sys.stdout.flush()
hits = {}
for k, pat in PATS.items():
    hits[k] = {"p7": [any(re.search(pat, p, re.I) for p in s["phrases"]) for s in out["p7"]], "b1": [any(re.search(pat, p, re.I) for p in s["spans"]) for s in out["b1"]]}
out["hits_5phrases"] = hits
json.dump(out, open(f"{EV}/extraction_sampling_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("hits", json.dumps(hits)); print("DONE spent", round(spent(), 3))
