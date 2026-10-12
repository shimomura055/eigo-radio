# Local-only what-if: inject hypothetical Wiktionary-style entries into an in-memory COPY of the DB (no file write)
# and check whether the CURRENT matching logic would find them and whether they would survive to phrase_survivors / shortlist cap.
import sys, os, json, copy
sys.path.insert(0, os.getcwd())
import er030_key_phrase_db_hybrid_core_01 as core
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
OUT = "er064_output/kp_idiom_trial_01/phase_a"
base = core.load_group1_dbs()
variants = {
  "inject_pump_one's_fist(Wiktionary-style placeholder heading)": ["pump one's fist", "mark the date"],
  "inject_pump_its_fist(literal surface form, unrealistic)": ["pump its fist", "mark the date on your calendar"],
  "inject_pump_fist+mark_date_heading_variants": ["pump fist", "mark the date"],
}
res = {}
for name, titles in variants.items():
    dbs = {k: dict(v) if isinstance(v, dict) else v for k, v in base.items()}
    dbs["wiktionary"] = dict(base["wiktionary"])
    for t in titles:
        dbs["wiktionary"][t.lower()] = {"categories": ["idiom"], "surface_titles": [t]}
    r = {}
    for lv in ["std", "adv"]:
        st = core.run_stage1_for_article(open(f"{OUT}/inputs/v4_{lv}_article.md", encoding="utf8").read(), dbs)
        ph = [c["canonical_form"] for c in st["phrase_survivors"]]
        r[lv] = {"phrase_survivors_count": len(ph), "phrase_survivors": ph,
                 "first15_alphabetical_cap_includes": [p for p in ph[:15] if any(w in p for w in ("pump", "mark the date"))],
                 "injected_found_in_phrase_survivors": [p for p in ph if any(w in p for w in ("pump", "mark the date"))]}
    res[name] = r
json.dump(res, open(f"{OUT}/sim_inject_db_entries_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
for n, r in res.items():
    print(n, {lv: r[lv]["injected_found_in_phrase_survivors"] for lv in r})
