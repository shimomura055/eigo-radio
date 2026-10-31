"""ev01 診断(非Production・仕様候補ではない): 抽出Promptの『易しい表現の除外』1行だけを取り除いた変種で、同一本文に対しP7相当×N・B1相当×Nを呼ぶ。
目的=5表現が抽出段で拾われない原因が当該条件か(原因仮説の反証/再現)を切り分けるだけ。Production Prompt/コードは無変更(メモリ上の文字列置換のみ、出力はev01のみ)。
usage: python run_diag_no_easy_exclusion.py <repo_root> [N=3]"""
import sys, os, json, glob, re
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 3
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
EV = os.path.join(ROOT, "docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/ev01")
CAP = float(os.environ.get("N5Q_CAP", "13.0"))
import er005_cost_logger as cl, er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5
import er062_family_z_structure_01 as st
import er105_kp_fulltext_selector_01 as ft
import er119_kp_p7w5_prompts_01 as p7w5
import er119_kp_prompt_2v_01 as p2v
def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log*.jsonl"))
cl.install(f"{EV}/cost_log_diag.jsonl")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
text = fx["cases"]["untidi_b1b"]["text"]
model = ft.resolve_model("B1_SUPPORT")
LINE5_P7 = [l for l in p7w5.P7_TEXT.split("\n") if l.startswith("5. **易しい表現の除外**")]
assert len(LINE5_P7) == 1, LINE5_P7
p7_variant = p7w5.P7_TEXT.replace(LINE5_P7[0] + "\n", "")
assert p7_variant != p7w5.P7_TEXT
LINE5_B1 = n5.PROD_DIFFICULTY.split("\n")[1] + "\n"
assert LINE5_B1.startswith("5. **易しい表現の除外**")
b1_variant = n5.prompt_B1(text).replace(LINE5_B1, "")
assert b1_variant != n5.prompt_B1(text)
PATS = {"put away": r"\bput\b.{0,12}\baway\b", "in the way": r"in the way", "force away": r"\bforce\b.{0,10}\baway\b", "leave out": r"\b(leave|left)\b.{0,8}\bout\b", "in sight": r"in sight"}
out = {"note": "診断用変種(Production非採用・仕様候補ではない)。除去した行=P7/B1の条件5『易しい表現の除外』のみ", "removed_line_p7": LINE5_P7[0], "removed_line_b1": LINE5_B1.strip(), "p7_variant": [], "b1_variant": []}
for i in range(N):
    if spent() + 0.5 > CAP: raise SystemExit("cost guard")
    st.check_stop_sentinel("n5q_diag", EV)
    msg = p7_variant + ft.BODY_DELIMITER + text
    fn = p2v.make_vocab_selector_fn(msg, model=model)
    with cl.logging_context("N5Q_audit", "diag_p7_variant"):
        raw, mid, rid = fn()
    items = [x["phrase"] for x in json.loads(raw)["items"]]
    out["p7_variant"].append({"sample": i + 1, "phrases": items}); print("P7v", i + 1, items, round(spent(), 3)); sys.stdout.flush()
for i in range(N):
    if spent() + 0.5 > CAP: raise SystemExit("cost guard")
    ctx = n5.N5Ctx("B1_SUPPORT", tag=f"diag_b1_{i+1}", stop_check_fn=lambda w: st.check_stop_sentinel(w, EV), article_id="N5Q_untidi_b1b")
    with cl.logging_context("N5Q_audit", "diag_b1_variant"):
        o, m = n5.call_llm("b1", b1_variant, n5.B1_SCHEMA, ctx, label="B1_overgen")
    sp = [c["span"] for c in o["candidates"]]
    out["b1_variant"].append({"sample": i + 1, "spans": sp}); print("B1v", i + 1, sp, round(spent(), 3)); sys.stdout.flush()
out["hits"] = {k: {"p7v": [any(re.search(pat, p, re.I) for p in s["phrases"]) for s in out["p7_variant"]], "b1v": [any(re.search(pat, p, re.I) for p in s["spans"]) for s in out["b1_variant"]]} for k, pat in PATS.items()}
json.dump(out, open(f"{EV}/diag_no_easy_exclusion_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("hits", json.dumps(out["hits"])); print("DONE spent", round(spent(), 3))
