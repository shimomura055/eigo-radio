# Local-only: reproduce which 2-3gram surfaces the Wiktionary multiword targeted-lookup would be asked about (budget 60). NO network call is made.
import sys, os, json
sys.path.insert(0, os.getcwd())
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er030_key_phrase_db_hybrid_core_01 as core
OUT = "er064_output/kp_idiom_trial_01/phase_a"
dbs = core.load_group1_dbs(); res = {}
for lv in ["std", "adv"]:
    st = core.run_stage1_for_article(open(f"{OUT}/inputs/v4_{lv}_article.md", encoding="utf8").read(), dbs)
    ex = ({c["canonical_form"] for c in st["phrase_survivors"]} | {c["canonical_form"] for c in st["important_noun_candidates"]} | {c["canonical_form"] for c in st["word_survivors"]})
    sents = [u["tokens"] for u in st["sentence_units"]]
    cand = s1v2.select_unmatched_ngram_candidates_for_lookup(sents, ex, budget=60)
    allc = s1v2.select_unmatched_ngram_candidates_for_lookup(sents, ex, budget=10**6)
    probes = ["pumps its", "its fist", "pumps its fist", "mark the", "mark the date", "the date on", "date on", "the date", "on your calendar", "your calendar", "date on your"]
    res[lv] = {"budget_60_list_len": len(cand), "unfiltered_unmatched_2_3gram_total": len(allc),
               "budget_60_list_tail": cand[-5:], "n2_in_list": sum(1 for c in cand if len(c.split()) == 2),
               "probe_in_unmatched_pool": {p: (p in [a.lower() for a in allc]) for p in probes},
               "probe_in_budget60": {p: (p in [a.lower() for a in cand]) for p in probes}}
json.dump(res, open(f"{OUT}/trace_wiktionary_lookup_budget_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
