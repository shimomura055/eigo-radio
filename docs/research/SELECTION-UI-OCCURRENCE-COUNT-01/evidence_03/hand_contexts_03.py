# -*- coding: utf-8 -*-
"""OCC-03 手計算用: 緩いregexで区分本文の該当行を表示するだけ(判定はしない)。人が読んで期待回数を決め、hand_check_03.pyに書く。API 0。"""
import re, sys, os, json
sys.path.insert(0, os.getcwd())
import er140_selection_occurrence_sections_01 as sl
CASES = [
 ("X","a2","er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01/a2/key_phrases/kp_candidates.json", {"hear it out": r"hear\w*\b.{0,12}out", "supplement": r"supplement"}),
 ("X","b1b","er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01/b1b/key_phrases/kp_candidates.json", {"hear it out": r"hear\w*\b.{0,12}out", "clutter": r"clutter"}),
 ("Y","a2","er121_output/family_y_production_01/surname_choice/run_02/key_phrases/a2/kp_candidates.json", {"give something up": r"(give|giving|gave|given|gives)\b.{0,14}\bup\b", "thankful": r"thank", "bothered": r"bother"}),
 ("Y","b1b","er121_output/family_y_production_01/surname_choice/run_02/key_phrases/b1b/kp_candidates.json", {"hold someone back": r"(hold|held|holding|holds)\b.{0,14}\bback\b", "grateful": r"grate"}),
 ("Z","a2","er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/key_phrases/a2/kp_candidates.json", {"slip away": r"(slip|slipp)\w*\b.{0,10}away", "mist": r"\bmist"}),
 ("Z","b1b","er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/key_phrases/b1b/kp_candidates.json", {"slip away": r"(slip|slipp)\w*\b.{0,10}away", "bar": r"\bbar"}),
]
for fam, lv, cand, items in CASES:
    sec, src = sl.load_sections(fam, cand, lv)
    print("=====", fam, lv, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(cand)))) if fam=="X" else cand.split("/")[3], {k: (None if v is None else len(v)) for k, v in sec.items()})
    for term, rx in items.items():
        print("--- ", term, "/", rx)
        for k in ("story", "comment", "preview", "oneline", "title"):
            for i, u in enumerate(sec.get(k) or []):
                for m in re.finditer(rx, u, re.I):
                    a = max(0, m.start() - 40); b = min(len(u), m.end() + 40)
                    print("   [%s#%d] ...%s[[%s]]%s..." % (k, i, u[a:m.start()], m.group(0), u[m.end():b]))
