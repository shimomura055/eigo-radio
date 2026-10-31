"""ev01 補足: (1) 'gets heated' が2回の独立runで落ちた経路(救済のQA再判定がNOT_REJUDGED)を、公式 er125.qa_rejudge で1 call再現。
(2) 追加の定型表現候補('Not so fast'等)の単独SEL判定。記事・音声の再生成なし。usage: python run_supplement.py <repo_root>"""
import sys, os, json, glob
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
EV = os.path.join(ROOT, "docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/ev01")
CAP = float(os.environ.get("N5Q_CAP", "13.0"))
import er005_cost_logger as cl, er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5
import er062_family_z_structure_01 as st
import er125_kp_rescue_production_01 as r125
import er003_key_words_canonicalization as kc
import er006_model_routing_contract_01 as routing
def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log*.jsonl"))
cl.install(f"{EV}/cost_log_supplement.jsonl")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
text = fx["cases"]["untidi_b1b"]["text"]
out = {}
if spent() + 0.6 > CAP: raise SystemExit("cost guard")
st.check_stop_sentinel("n5q_supp", EV)
sent = "No wonder the kitchen meeting gets heated."
model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
cap = {}
def qa_call(msg):
    with cl.logging_context("N5Q_audit", "supp_qa_rejudge"):
        r = kc.make_canonicalization_fn(msg, model=model, schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)()
    cap["raw"] = r[0]; cap["model"] = r[1]; cap["rid"] = r[2]
    return r
items = [{"rank": 5, "key_phrase": "gets heated", "display_phrase": "gets heated", "source_span": "gets heated", "source_sentence": sent, "normalization_reason": "none"}]
res = r125.qa_rejudge(text, items, qa_call, {5: ()})
out["gets_heated_qa_rejudge"] = {"model": model, "result": res, "raw_response_text": cap.get("raw"), "response_id": cap.get("rid")}
print("qa_rejudge status:", res["by_rank"].get(5), "spent", round(spent(), 3)); sys.stdout.flush()
# (2) 追加定型表現の単独SEL
spans = ["Not so fast", "It's not so simple", "without question", "just because", "support daily life", "get heated" if False else "gets heated", "taking up space"]
spans = [s for s in spans if n5.span_in_text(s, text)]
ctx = n5.N5Ctx("B1_SUPPORT", tag="supp_sel", stop_check_fn=lambda w: st.check_stop_sentinel(w, EV), article_id="N5Q_untidi_b1b")
log = n5.new_log("supp_sel"); cs = []
for s in spans:
    c = {"span": s, "sentence": "", "n5_origin": "B1"}; n5._fill_sentence(text, c); cs.append(c)
with cl.logging_context("N5Q_audit", "supp_sel"):
    judged = n5.select(text, cs, log, ctx)
out["supp_sel"] = [{k: c.get(k) for k in ("span", "cls", "chunk_type", "difficulty", "keep", "chunk_reason_ja", "sentence")} for c in judged]
for j in out["supp_sel"]: print(j["span"], j["cls"], j["difficulty"], j["keep"], j["chunk_reason_ja"])
json.dump(out, open(f"{EV}/supplement_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("DONE spent", round(spent(), 3))
