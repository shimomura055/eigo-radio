# 読取専用・オフライン: lookup poolの並べ替え案(希少語を含む2語を先頭へ)で time lag が予算60に入るかを机上シミュレート。
import sys, os, json
sys.path.insert(0, os.getcwd())
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er030_key_phrase_db_hybrid_core_01 as core
import er023_key_phrase_db_extraction as ext
CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS
dbs = core.load_group1_dbs()
A = {"coffee_v5_std": "er019_output/coffee_prices/run_v5_ms_01/a2/article.md", "coffee_v5_adv": "er019_output/coffee_prices/run_v5_ms_01/b1b/article.md",
     "meta_run03_adv": "er019_output/meta/run_03/b1b/article.md", "hormuz_run02_adv": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md"}
out = {}
for n, p in A.items():
    st = core.run_stage1_for_article(open(p, encoding="utf8").read(), dbs)
    ex = ({c["canonical_form"] for c in st["phrase_survivors"]} | {c["canonical_form"] for c in st["important_noun_candidates"]} | {c["canonical_form"] for c in st["word_survivors"]})
    sents = [u["tokens"] for u in st["sentence_units"]]
    pool = s1v2.select_unmatched_ngram_candidates_for_lookup(sents, ex, budget=10**6)
    rare = {c["canonical_form"] for c in st["word_survivors"][:10]}   # shortlistに入りうる希少語の上位(K=10の例)
    two = [x for x in pool if len(x.split()) == 2]
    pri = [x for x in two if any(t in rare for t in x.lower().split())]
    rest = [x for x in pool if x not in pri]
    new = pri + rest
    out[n] = {"pool": len(pool), "two_gram_pool": len(two), "priority_2grams_containing_top10_rare_word": len(pri),
              "time_lag_rank_old": (pool.index("time lag") + 1) if "time lag" in pool else None,
              "time_lag_rank_new": (new.index("time lag") + 1) if "time lag" in new else None,
              "priority_sample": pri[:15]}
json.dump(out, open("er064_output/kp_candidate_selection_design_01/budget_sim_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1)[:2500])
