# KP-CANDIDATE-SELECTION-QUALITY-DESIGN-01: 読取・集計専用script(Production非接続、API/ネットワーク呼出なし、費用0)。
# 既存Production関数(core.run_stage1_for_article等)を読み取り専用で呼び、候補供給の状況を記録する。
import sys, os, json, re
sys.path.insert(0, os.getcwd())
import wordfreq
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er030_key_phrase_db_hybrid_core_01 as core
import er023_key_phrase_db_extraction as ext

OUT = "er064_output/kp_candidate_selection_design_01"
ARTICLES = {
    "coffee_v5_std": "er019_output/coffee_prices/run_v5_ms_01/a2/article.md",
    "coffee_v5_adv": "er019_output/coffee_prices/run_v5_ms_01/b1b/article.md",
    "meta_run03_std": "er019_output/meta/run_03/a2/article.md",
    "meta_run03_adv": "er019_output/meta/run_03/b1b/article.md",
    "hormuz_run02_std": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md",
    "hormuz_run02_adv": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md",
}
PROBES = ["time lag", "lag", "in the ring", "the ring", "been behind", "behind price", "been behind price increases",
          "pushed prices up", "prices up", "pumps its fist", "hidden clock", "its own hidden clock", "raw beans", "raw-bean",
          "price measure", "take time", "right away", "show up", "comes with", "come down"]
CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS
dbs = core.load_group1_dbs()
wik = dbs.get("wiktionary") if isinstance(dbs, dict) else None

def zipf2(surface):  # wordfreq: multi-word Zipf is an estimate (harmonic-style), reference signal only
    return round(wordfreq.zipf_frequency(surface.lower(), "en"), 2)

def content(t):
    return t.lower() not in CLOSED

res = {}
for name, path in ARTICLES.items():
    txt = open(path, encoding="utf8").read()
    st = core.run_stage1_for_article(txt, dbs)
    ex = ({c["canonical_form"] for c in st["phrase_survivors"]} | {c["canonical_form"] for c in st["important_noun_candidates"]} |
          {c["canonical_form"] for c in st["word_survivors"]})
    sents = [u["tokens"] for u in st["sentence_units"]]
    pool = s1v2.select_unmatched_ngram_candidates_for_lookup(sents, ex, budget=10**6)
    pool_l = [p.lower() for p in pool]
    rank = {p: (pool_l.index(p) + 1 if p in pool_l else None) for p in PROBES}
    article_l = re.sub(r"[“”]", '"', txt.lower())
    present = {p: (p in article_l) for p in PROBES}
    # word_survivors sorted by rarity -> what enters the shortlist (word_min=5 fill)
    ws = [c["canonical_form"] for c in st["word_survivors"]]
    ps = [c["canonical_form"] for c in st["phrase_survivors"]]
    # containment: for each of the first 12 rarest word survivors, adjacent content-bigrams in article containing it
    cont = []
    for w in ws[:12]:
        found = set()
        for toks in sents:
            low = [t.lower() for t in toks]
            for i, t in enumerate(low):
                if t == w:
                    for a, b in ((i - 1, i), (i, i + 1)):
                        if a >= 0 and b < len(low) and content(low[a]) and content(low[b]) and low[a].isalpha() and low[b].isalpha():
                            found.add(" ".join(low[a:b + 1]))
        cont.append({"word": w, "zipf": zipf2(w), "adjacent_content_bigrams": sorted((f, zipf2(f)) for f in found)})
    res[name] = {
        "tokens": st["tokens_total"], "phrase_survivors": len(ps), "phrase_survivors_list": ps,
        "important_noun_candidates": [c["canonical_form"] for c in st["important_noun_candidates"]],
        "word_survivors_total": len(ws), "word_survivors_rarest12": ws[:12],
        "unmatched_2_3gram_pool": len(pool), "wiktionary_lookup_budget": core.DEFAULT_WIKTIONARY_MULTIWORD_LOOKUP_BUDGET,
        "probe_in_article": present, "probe_rank_in_lookup_pool(1=first, budget=60)": rank,
        "word_containing_bigrams": cont,
    }
json.dump(res, open(f"{OUT}/upstream_trace_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("saved")
