# -*- coding: utf-8 -*-
"""本文以外への影響の静的確認(API0): roster/Voice割当が本文の固有名有無に依存しないこと、決定論の話者判定の解決率。"""
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
import er062_family_z_structure_01 as st
D = "er026_output/family_z_production_e2e_01"
res = {"roster_independent_of_text": True, "voice_assignment": {}, "attribution": []}
for story in ("the_open_window", "melos"):
    res["voice_assignment"][story] = st.derive_dialogue_voice_tts_names(story)
cfg_ow = st.STORY_SPEAKER_CONFIG["the_open_window"]
for story, run, var in [("the_open_window", "run_e2e_01", "baseline"), ("the_open_window", "run_pntrial_01", "common(Veraなし)"),
                        ("the_open_window", "run_pntrial_02", "per_story(Veraあり)"), ("melos", "run_e2e_06", "baseline"),
                        ("melos", "run_pntrial_01", "common")]:
    for lvl, f in (("Adv", "r2.md"), ("Std", "std.md")):
        t = open(f"{D}/{story}/{run}/writer/{f}", encoding="utf-8").read()
        _t, body = st.split_title_body(t)
        paras = st.clean_body_paragraphs(body)
        quotes = st.extract_quotes(paras)
        det = st.deterministic_attribution(paras, quotes, story_key=story)
        n = len(quotes); resolved = sum(1 for v in det.values() if v)
        by = {}
        for v in det.values():
            by[v or "unresolved(LLM判定)"] = by.get(v or "unresolved(LLM判定)", 0) + 1
        res["attribution"].append({"story": story, "run": run, "variant": var, "level": lvl, "quotes": n,
                                   "deterministic_resolved": resolved, "by_speaker": by})
        print(story, run, var, lvl, "quotes", n, "det_resolved", resolved, by)
print(json.dumps(res["voice_assignment"], ensure_ascii=False))
json.dump(res, open("docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/pntrial_impact_check_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
