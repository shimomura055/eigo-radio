# XRG1 委任_01: run_mey_01 Research記録の追跡(read-only、API 0)。検索クエリの語分類と、Ledger/検証notesの主体語の有無を機械集計する。
import json, re, sys
R = "er019_output/middle_east_yemen_saudi/run_mey_01/research_ledger/"
rec = json.load(open(R + "audit/researcher_full_record.json", encoding="utf-8"))
ver = json.load(open(R + "audit/verification_full_record.json", encoding="utf-8"))
draft = json.load(open(R + "fact_ledger_draft.json", encoding="utf-8"))
vres = json.load(open(R + "fact_ledger_verification.json", encoding="utf-8"))
cats = {
    "actor_name(Houthi/Ansar)": r"houthi|ansar|الحوثي",
    "responsibility(claimed/responsib/who)": r"claim(ed)? responsib|responsib|\bwho\b|perpetrat|behind",
    "motive/why/reason": r"\bwhy\b|motive|reason|retaliat|in response",
    "background(conflict/coalition/Iran/Red Sea)": r"background|conflict|coalition|iran|red sea|bab al|escalat",
    "casualty/number-oriented": r"\b\d{2,3}\b|casualt|injured|killed|fatalit",
}
qs = rec["search_usage"]["queries"]
out = {"researcher_queries_n": len(qs), "web_search_call_count": rec["search_usage"]["web_search_call_count"],
       "verification_queries_n": len(ver["search_usage"]["queries"]), "categories": {}}
for k, p in cats.items():
    hits = [i for i, q in enumerate(qs) if re.search(p, q, re.I)]
    vh = [i for i, q in enumerate(ver["search_usage"]["queries"]) if re.search(p, q, re.I)]
    out["categories"][k] = {"researcher_hit_idx": hits, "verification_hit_idx": vh}
# 主体語がLedger claimに現れるFact
pat = r"フーシ|Houthi|アンサール|Ansar"
out["draft_claims_with_actor_term"] = [f["fact_id"] for f in draft["facts"] if re.search(pat, f["claim"], re.I)]
out["draft_fields_with_actor_term"] = {f["fact_id"]: [k for k, v in f.items() if isinstance(v, str) and re.search(pat, v, re.I)] for f in draft["facts"] if any(isinstance(v, str) and re.search(pat, v, re.I) for v in f.values())}
out["verification_notes_with_actor_term"] = [v["fact_id"] for v in vres["verifications"] if re.search(pat, v["verification_notes"], re.I)]
out["verdicts"] = {v["fact_id"]: v["verdict"] for v in vres["verifications"]}
out["draft_facts_n"] = len(draft["facts"])
out["notes_saying_actor_unspecified"] = [f["fact_id"] for f in draft["facts"] if re.search(r"攻撃主体", " ".join(str(v) for v in f.values()))]
json.dump(out, open("docs/research/FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01/xrg1_trace_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
