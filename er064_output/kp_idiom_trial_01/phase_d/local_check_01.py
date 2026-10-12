# Phase D 準備: 凍結前の¥0ローカル判定(V0/V1/V3 shortlistに各表現が入るか)。API不使用(Wiktionary公開APIのみ、stage1キャッシュ)。
import json, sys, glob, os
sys.path.insert(0, ".")
import er030_key_phrase_db_hybrid_core_01 as core
import er064_kp_idiom_trial_01_matcher as M
import er064_kp_idiom_trial_01_pipeline as P
D = "er064_output/kp_idiom_trial_01/phase_d"
dbs = core.load_group1_dbs(); pats = M.build_pattern_index(dbs)
out = {}
for f in sorted(glob.glob(f"{D}/inputs/*.md")):
    name = os.path.basename(f)[:-3]
    t = open(f, encoding="utf-8").read()
    base = P.load_base(t)
    st = base["stage1"]
    ex = P._canon_set(st)
    pc = M.placeholder_candidates(st["sentence_units"], pats, dbs, ex)
    rc = M.rule_possessive_pattern_candidates(st["sentence_units"], dbs, ex)
    sl = base["shortlist_info"]["shortlist"]
    out[name] = {"v0_total": len(sl),
                 "v0_non_word": [c["surface_form"] for c in sl if c["unit_type"] != "word"],
                 "v0_words": [c["surface_form"] for c in sl if c["unit_type"] == "word"],
                 "placeholder": [(c["surface_form"], c.get("matched_title")) for c in pc],
                 "rule": [c["surface_form"] for c in rc],
                 "all_canon_multiword": sorted(c for c in ex if len(c.split()) >= 2)}
    print(name, out[name]["v0_total"]); print("  nonword:", out[name]["v0_non_word"]); print("  placeholder:", out[name]["placeholder"]); print("  rule:", out[name]["rule"])
json.dump(out, open(f"{D}/local_check_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
