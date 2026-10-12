# Phase B6: V0/V1/V2(b1抜き)/V3 のshortlist単位ablation(決定論・API/ネットワークなし、stage1キャッシュ使用)
# 評価ターゲット(下のTARGETS)は『評価fixture』であり、Trial実装コードには入っていない。
import sys, os, json
sys.path.insert(0, os.getcwd())
import er030_key_phrase_db_hybrid_core_01 as core
import er064_kp_idiom_trial_01_matcher as M
import er064_kp_idiom_trial_01_pipeline as P
TARGETS = ["pumps its fist", "mark the date"]  # 評価fixture(Phase C/Dで再利用)
OUT = "er064_output/kp_idiom_trial_01/phase_b"
dbs = core.load_group1_dbs(); pats = M.build_pattern_index(dbs)
res = {}
for lv in ("std", "adv"):
    t = open(f"er064_output/kp_idiom_trial_01/phase_a/inputs/v4_{lv}_article.md", encoding="utf8").read()
    base = P.load_base(t); st = base["stage1"]; units = st["sentence_units"]; existing = P._canon_set(st)
    pc = M.placeholder_candidates(units, pats, dbs, existing)
    rc = M.rule_possessive_pattern_candidates(units, dbs, existing)
    row = {"phrase_survivors_total": len(st["phrase_survivors"]), "cut_by_cap15": [c["canonical_form"] for c in st["phrase_survivors"][15:]],
           "cut_online_hits": [c["canonical_form"] for c in P.cut_online_hits(st)],
           "placeholder_candidates": [(c["surface_form"], c["matched_title"]) for c in pc],
           "rule_pattern_candidates": [c["surface_form"] for c in rc], "variants": {}}
    for v, kw in (("V0", {}), ("V1", {"placeholder_cands": pc}), ("V2_without_b1", {"placeholder_cands": pc}), ("V3", {"rule_cands": rc})):
        r = P.build_variant_shortlist(base, v.split("_")[0], **kw)
        keys = P.shortlist_keys(r["shortlist_info"])
        row["variants"][v] = {"shortlist_total": len(keys), "phrase_included": r["shortlist_info"]["phrase_included_count"],
                              "reserved": [c["surface_form"] for c in r["reserved"]], "reserved_overflow": [c["surface_form"] for c in r["reserved_overflow"]],
                              "targets_in_shortlist": {x: any(x in k for k in keys) for x in TARGETS},
                              "v0_subset": set(P.shortlist_keys(base["shortlist_info"])) <= set(keys)}
    res[lv] = row
json.dump(res, open(f"{OUT}/ablation_shortlist_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
