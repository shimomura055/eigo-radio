# 読取専用・オフライン: 既存stage1候補の中で「A ⊂ B(連続token部分列、小文字、単純な活用語尾差を許容)」の組を数え、U2(包含候補の整理規則)の適用範囲と誤爆を机上確認。費用0。
import sys, os, json
sys.path.insert(0, os.getcwd())
import er030_key_phrase_db_hybrid_core_01 as core
import er023_key_phrase_db_extraction as ext
dbs = core.load_group1_dbs()
ARTS = {
    "coffee_v5_std": "er019_output/coffee_prices/run_v5_ms_01/a2/article.md", "coffee_v5_adv": "er019_output/coffee_prices/run_v5_ms_01/b1b/article.md",
    "meta_run03_std": "er019_output/meta/run_03/a2/article.md", "meta_run03_adv": "er019_output/meta/run_03/b1b/article.md",
    "hormuz_run02_std": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md", "hormuz_run02_adv": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md"}
def stem(t):
    for s in ("ing", "ed", "es", "s"):
        if t.endswith(s) and len(t) - len(s) >= 3:
            return t[: -len(s)]
    return t
def contains(big, small):
    b = [stem(t) for t in big.lower().split()]; s = [stem(t) for t in small.lower().split()]
    return len(s) < len(b) and any(b[i:i + len(s)] == s for i in range(len(b) - len(s) + 1))
out = {}
for n, p in ARTS.items():
    st = core.run_stage1_for_article(open(p, encoding="utf8").read(), dbs)
    words = [c["canonical_form"] for c in st["word_survivors"]]
    phr = [(c["canonical_form"], "db_registered" if c["matched_dbs"] and c["matched_dbs"] != ["repeated_compound_noun_heuristic"] else "heuristic") for c in st["phrase_survivors"]]
    imp = [(c["canonical_form"], "db_registered" if (c["matched_dbs"] and "repeated_compound_noun_heuristic" not in c["matched_dbs"]) else "heuristic") for c in st["important_noun_candidates"]]
    big = phr + imp
    pairs = []
    for b, kind in big:
        for w in words:
            if contains(b, w):
                pairs.append({"small": w, "small_type": "word", "big": b, "big_evidence": kind})
        for b2, k2 in big:
            if b2 != b and contains(b, b2):
                pairs.append({"small": b2, "small_type": "phrase", "big": b, "big_evidence": kind})
    out[n] = pairs
    print(n, len(pairs), [(x["small"], "<", x["big"], x["big_evidence"]) for x in pairs][:14])
json.dump(out, open("er064_output/kp_candidate_selection_design_01/containment_pairs_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
