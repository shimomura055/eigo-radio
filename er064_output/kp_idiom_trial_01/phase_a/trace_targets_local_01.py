# KP-IDIOM Phase A: local (no API, no network) trace of why target expressions vanish.
# Calls only er030.run_stage1_for_article (pure local DB match) + er023 ngram/match helpers. Production code is imported read-only.
import sys, json, os
sys.path.insert(0, os.getcwd())
import er023_key_phrase_db_extraction as ext
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er030_key_phrase_db_hybrid_core_01 as core

OUT = "er064_output/kp_idiom_trial_01/phase_a"
dbs = core.load_group1_dbs()
TARGET_PAT = {"pumps its fist": "pumps its fist", "mark the date on your calendar": "mark the date on your calendar"}
res = {"db_sizes": {k: len(v) for k, v in dbs.items()}, "levels": {}}
for lv in ["std", "adv"]:
    text = open(f"{OUT}/inputs/v4_{lv}_article.md", encoding="utf8").read()
    st = core.run_stage1_for_article(text, dbs)
    units = st["sentence_units"]
    lvres = {"counts": {k: st[k] for k in ["tokens_total", "before_dedup_count", "after_dedup_count",
             "stage_a_survivors_count", "stage_b_survivors_count"]}, "targets": {}}
    surv_phr = {c["canonical_form"] for c in st["phrase_survivors"]}
    surv_word = {c["canonical_form"] for c in st["word_survivors"]}
    for tname, tphrase in TARGET_PAT.items():
        sent = None
        for u in units:
            if tphrase in " ".join(u["tokens"]).lower():
                sent = u; break
        if sent is None:
            lvres["targets"][tname] = {"found_in_article": False}; continue
        toks = sent["tokens"]; low = " ".join(t.lower() for t in toks)
        start = low.index(tphrase); pre = len(low[:start].split())
        tw = tphrase.split(); span = range(pre, pre + len(tw))
        rows = []
        for ng in ext.generate_ngrams([toks]):
            s, n = ng["start"], ng["n"]
            if not (s >= pre - 0 and s + n <= pre + len(tw)):
                continue  # sub-ngrams fully inside the target span
            m = s1v2.match_candidate_with_irregular_rescue(ng, dbs)
            cf = m["canonical_form"]
            rows.append({"ngram": ng["surface_form"], "n": n, "db_match_count": m["db_match_count"],
                         "matched_dbs": m["matched_dbs"], "db_categories": m["db_categories"],
                         "unit_type": m["unit_type"], "in_phrase_survivors": cf in surv_phr,
                         "in_word_survivors": cf in surv_word})
        # also: any n>=2 ngram (any hit) overlapping the target span
        lvres["targets"][tname] = {"found_in_article": True, "sentence": sent["raw_text"],
                                   "subngram_count": len(rows), "subngram_hits": [r for r in rows if r["db_match_count"] > 0],
                                   "multiword_subngram_hits": [r for r in rows if r["db_match_count"] > 0 and r["n"] >= 2],
                                   "any_multiword_hit": any(r["db_match_count"] > 0 and r["n"] >= 2 for r in rows)}
    # phrase survivors overlapping targets
    lvres["phrase_survivors_all"] = [{"cf": c["canonical_form"], "type": c["unit_type"], "dbs": c["matched_dbs"]} for c in st["phrase_survivors"]]
    lvres["word_survivors_rarity_order_top20"] = [c["canonical_form"] for c in st["word_survivors"][:20]]
    lvres["word_survivors_total"] = len(st["word_survivors"])
    lvres["word_rank_of"] = {w: (st["word_survivors"].index(next(c for c in st["word_survivors"] if c["canonical_form"] == w)) + 1)
                             for w in ["pumps", "fist", "mark", "calendar", "date", "lag"]
                             if any(c["canonical_form"] == w for c in st["word_survivors"])}
    lvres["important_noun_candidates"] = [c["canonical_form"] for c in st["important_noun_candidates"]]
    res["levels"][lv] = lvres
json.dump(res, open(f"{OUT}/trace_targets_local_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1)[:9000])
