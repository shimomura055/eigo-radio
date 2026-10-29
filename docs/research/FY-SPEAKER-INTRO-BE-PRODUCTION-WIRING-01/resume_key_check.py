import json, os, sys
sys.path.insert(0,".")
import er121_family_y_text_core_01 as tc
R="er121_output/family_y_production_01/redelivery_fee/run_fybe_ev_01"
TP="docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json"
MAN="docs/research/FY-SPEAKER-INTRO-BE-PRODUCTION-WIRING-01/reuse_redelivery_no_intros_copy.json"
tpl=tc.load_theme_package(json.load(open(TP,encoding="utf-8")),path=TP)
theme,pkg=tpl["theme"],tpl["sha256"]
ri=tc.load_reuse(MAN,theme,"redelivery_fee")
spec=tc.intro_spec(theme,ri.get("intro_checks"))
parts_i=tc.load_article_prompt("intro")
common=dict(pkg=pkg,slug="redelivery_fee",module=tc._module_sha(),mgmt=tc.MANAGEMENT_ID)
reuse_key=tc._key(manifest=ri["manifest"],r0=ri["voice_r0_sha256"],lead=ri.get("lead_file_sha256"),intros=ri.get("intros_file_sha256"))
voices=ri["voices"]
lkey=tc._key(stage="lead_intro",voices=tc.voices_sha256(voices),reuse=reuse_key,lead=None,intro=parts_i["sha256"],spec=spec["mode"],**common)
saved=json.load(open(R+"/text/lead_intro/stage_lead_intro.json",encoding="utf-8"))["input_key"]
print("recomputed",lkey); print("saved     ",saved); print("MATCH",lkey==saved)
# old prompt sha -> different key (旧Prompt生成物は再利用されない)
lk_old=tc._key(stage="lead_intro",voices=tc.voices_sha256(voices),reuse=reuse_key,lead=None,intro="787794d635587053d20a411aa98da70b00dc7a45bc182f1483c1ae6a7267afc4",spec=spec["mode"],**common)
print("old-prompt key differs",lk_old!=saved)
