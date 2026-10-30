"""任意(委任_02): er125.qa_rejudge をN5形(used_form!=source_span)に record-only で適用する。Production出力は変更しない。usage: python qa12_on_n5_forms.py <label> <level> <kp_candidates.json> <article_text> <process>"""
import sys, os, json, copy
ROOT = os.path.abspath(os.getcwd()); sys.path.insert(0, ROOT)
label, level, cpath, tpath, process = sys.argv[1:6]
import er005_cost_logger as cl, er003_key_words_canonicalization as kc, er006_model_routing_contract_01 as routing, er125_kp_rescue_production_01 as er125
OUT = os.path.join(ROOT, "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev02/qa12"); os.makedirs(OUT, exist_ok=True)
cl.install(f"{OUT}/{label}_cost.jsonl")
doc = json.load(open(cpath, encoding="utf-8")); text = open(tpath, encoding="utf-8").read()
items = []
for c in doc["candidates"]:
    it = copy.deepcopy(c["item"])
    if it.get("n5") and (it.get("used_form") or "").lower() != (it.get("source_span") or "").lower():
        it["key_phrase"] = it["used_form"]; items.append(it)
model = routing.require_model(process, routing.SUPPORT_MODEL)
def qa_call(msg):
    with cl.logging_context(f"QA12_{label}", "qa12_on_n5_forms"):
        return kc.make_canonicalization_fn(msg, model=model, schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)()
res = er125.qa_rejudge(text, items, qa_call, {})
rows = [{"rank": it["rank"], "source_span": it["source_span"], "used_form": it["used_form"], "canon_pre": (it["n5"] or {}).get("canon_pre"), "status": res["by_rank"][it["rank"]]["status"],
         "qa_fail_fields": [k for k, v in (res["by_rank"][it["rank"]].get("qa") or {}).items() if v == "FAIL"], "stored_qa_overall": it.get("qa_overall_status")} for it in items]
json.dump({"label": label, "model_id": res.get("model_id"), "rows": rows}, open(f"{OUT}/{label}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in rows: print(r)
