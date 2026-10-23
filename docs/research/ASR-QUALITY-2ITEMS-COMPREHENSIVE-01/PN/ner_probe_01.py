# -*- coding: utf-8 -*-
"""設計入力の小規模実測(DEV/Trial専用・Production非接続): 保存済みX記事本文(a2)+Z脚本(std)に対し LLM NER(gpt-6-luna) 1回/本文 を実行し、
(1)Bertieのような未登録固有名詞の検出可否 (2)deterministic候補(inventing/canceling/fats/roasting/unwanted)の誤検出 (3)カテゴリ付与 (4)費用 を測る。
費用上限 8円(超過見込みで停止)。結果=ner_probe_01_result.json / raw usageは ner_probe_01_usage.jsonl。"""
import glob, json, os, sys, time
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
MODEL = "gpt-6-luna"
PRICE_IN, PRICE_OUT, USD_JPY = 0.10, 0.50, 160.0   # per 1M tokens (er006_model_routing_pricing_coverage_test_01.py:50-52)
CAP_JPY = 8.0
OUTD = "docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/"
files = []
for g in ("er019_output/*/run_*/a2/article.md", "er026_output/family_z_production_e2e_01/*/run_*/writer/std.md"):
    files += glob.glob(g)
best = {}
for f in files:
    fn = f.replace("\\", "/"); p = fn.split("/")
    if "mock" in fn: continue
    key = (p[1], p[2]) if "er019" in fn else (p[2],)
    if key not in best or os.path.getmtime(f) > os.path.getmtime(best[key]):
        best[key] = f.replace("\\", "/")
files = sorted(best.values())
SCHEMA = {"name": "entities", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["entities"], "properties": {"entities": {"type": "array", "items": {
    "type": "object", "additionalProperties": False, "required": ["surface", "category"],
    "properties": {"surface": {"type": "string"}, "category": {"type": "string", "enum": ["person", "place", "organization", "work_title", "brand_product", "other_named"]}}}}}}}
DEV = ("You list the proper nouns (named entities) in an English radio script, for a text-to-speech pronunciation QA step. "
       "Include: people (first names, surnames, nicknames, names inside quotations or song lyrics, names that start a sentence), places, organizations/media, "
       "titles of works, brands/products, other named things. Do NOT list ordinary words just because they are capitalized at the start of a sentence or heading, "
       "months/weekdays, nationality adjectives, or generic nouns. Give each entity once, with the exact surface form (multi-word names as one entity, e.g. 'Stephen Reicher'). "
       "Category is one of: person, place, organization, work_title, brand_product, other_named.")
client = OpenAI()
out, spent = {}, 0.0
log = open(OUTD + "ner_probe_01_usage.jsonl", "a", encoding="utf-8")
for f in files:
    text = open(f, encoding="utf-8").read()
    r = client.responses.create(model=MODEL, reasoning={"effort": "low"}, text={"format": {"type": "json_schema", **SCHEMA}},
                                input=[{"role": "developer", "content": DEV}, {"role": "user", "content": text}])
    u = r.usage; jpy = (u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT) / 1e6 * USD_JPY; spent += jpy
    log.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "file": f.replace("\\", "/"), "model": r.model, "in": u.input_tokens, "out": u.output_tokens, "jpy": round(jpy, 4)}) + "\n"); log.flush()
    out[f.replace("\\", "/")] = json.loads(r.output_text)["entities"]
    if spent > CAP_JPY - 1.0:
        print("COST GUARD stop at", f, spent); break
json.dump({"model": MODEL, "total_jpy": round(spent, 4), "n_articles": len(out), "entities": out}, open(OUTD + "ner_probe_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("articles", len(out), "jpy", round(spent, 4))
