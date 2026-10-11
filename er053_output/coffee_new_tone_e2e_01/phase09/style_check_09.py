# -*- coding: utf-8 -*-
"""委任_09: Standard/Advanced の role別 style_prefix(実送信値)を承認逐語定数と照合。API呼出0。worktree rootで PYTHONPATH=. 実行。"""
import json
import er033_tts_flash_lite_family_x_styles_01 as fl
import er003_v1_n3_01_tts_generate as n3
R = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01"
out = []
def chk(level, name, v, expect, label):
    sp = v.get("style_prefix") or ""
    out.append((level, name, v.get("status"), "MATCH" if sp == expect else "DIFF", label))
for level, d in (("Standard", json.load(open(R + "/a2/audit/tts_generation_results.json", encoding="utf-8"))),
                 ("Advanced", json.load(open(R + "/b1b/audit/tts_generation_results.json", encoding="utf-8")))):
    for name, v in d["segments"].items():
        if name in ("japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4") and level == "Standard":
            chk(level, name, v, fl.FAMILY_X_ROLE_STYLE_JA, "J2 verbatim")
        elif name in ("full_story_part1", "full_story_part3") and level == "Standard":
            chk(level, name, v, fl.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"] + "\n" + n3.A2_SLOWER_PACE_INSTRUCTION.strip(), "F1_5 + A2 slower verbatim")
        elif name in ("full_story_part1", "full_story_part2", "full_story_part3") and level == "Advanced":
            chk(level, name, v, fl.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"], "F1_5 verbatim")
        elif name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4") and level == "Advanced":
            chk(level, name, v, fl.FAMILY_X_ROLE_STYLE_EN["COMMENT"] if "COMMENT" in fl.FAMILY_X_ROLE_STYLE_EN else "?", "E2_UPBEAT verbatim")
d2 = json.load(open(R + "/a2/audit/tts_generation_results.json", encoding="utf-8"))
for rk, kpd in d2["key_phrases"].items():
    sp = (kpd["japanese_meaning"].get("style_prefix") or "")
    out.append(("Standard", "KP%s 日本語意味" % rk, kpd["japanese_meaning"].get("status"), "MATCH" if sp == fl.FAMILY_X_ROLE_STYLE_JA else "DIFF", "J2 verbatim"))
lr = json.load(open("er011_output/local_rewrite_recovery/coffee_prices__run_e_tone_01/a2/local_rewrite_recovery_full_story_part2.json", encoding="utf-8"))["retts_result"]
exp = fl.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"] + "\n" + n3.A2_SLOWER_PACE_INSTRUCTION.strip()
out.append(("Standard", "full_story_part2(Attempt4=LR retts)", "HUMAN_APPROVED", "MATCH(先頭200字。ログ側が200字で切詰め保存)" if lr["style_prefix"] == exp[:200] else "DIFF", "F1_5 + A2 slower verbatim / style_source=%s / model=%s / voice=%s" % (lr["style_source"], lr["tts_model_id"], lr["voice"])))
with open("er053_output/coffee_new_tone_e2e_01/phase09/STYLE_CHECK_09.md", "w", encoding="utf-8") as f:
    f.write("# STYLE_CHECK_09 (style_version=%s)\n\n| level | segment | status | vs 承認逐語 | 基準 |\n|---|---|---|---|---|\n" % json.load(open(R + "/a2/audit/tts_generation_results.json", encoding="utf-8"))["style_version"])
    for r in out:
        f.write("| " + " | ".join(str(x) for x in r) + " |\n")
print(open("er053_output/coffee_new_tone_e2e_01/phase09/STYLE_CHECK_09.md", encoding="utf-8").read())
