# -*- coding: utf-8 -*-
"""委任_03 A-7: 『Melos said → ASR別綴り』を現行機構が説明できるか/Trial音韻判定が説明できるかの表(オフライン、ASR呼出なし)"""
import sys, json
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_p2_phon as P
import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er021_en_asr_semantic_equivalence_production_01 as _se
_se.append_telemetry_log = lambda *a, **k: None
rows = []
canon = "Melos said."
obs = {"Mello said.": "OpenAI Primary(att1/2/3/4, b1b)", "Mellow said.": "Azure(att2, b1b, 減速後8/8)", "Melo said.": "Azure(att3,4,6)/whisper", "Mellis said.": "OpenAI(att4 Prod)",
       "meloset": "OpenAI(att5 Prod TTS_FAILURE)", "Mellowset.": "OpenAI(att6 Prod TTS_FAILURE)", "Melos said.": "Azure(att1)=正解", "Mellos said.": "OpenAI(a2 part1_c1等)",
       "Melon said.": "[反例synthetic]別語", "Marcus said.": "[反例]別語", "Melos aid.": "[反例]said語頭sの欠落", "Melos.": "[反例]said欠落", "Mel said.": "[反例]語幹欠落"}
for a, src in obs.items():
    r = val.classify_asr_match(canon, a, segment_id="full_story_part1")
    cs = csv3.classify_connected_speech(canon, a)["new_judgment"]
    e = eq.classify_connected_speech_equivalence(canon, a)["layer_judgment"]
    ex = P.explain_diff(canon, a)
    tw = P.three_way(ex)
    rows.append({"asr": a, "obs": src, "prod": r.classification, "prod_pass": bool(r.should_pass), "cs_validator": cs, "eq_layer_cheap": e,
                 "phon": ex["verdict"], "phon_rule": [x.get("rule") for x in ex["regions"]], "three_way_no_evidence": tw["class"]})
json.dump(rows, open("er065_output/short_clip_asr_context_trial_01/phase2/a7_table_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("| ASR転写(出所) | 現行Production判定 | CS Validator(A/B/C) | Equivalence Layer(入口,cheap) | Trial音韻判定 | Trial 3分類(独立証拠なし) |")
print("|---|---|---|---|---|---|")
for r in rows:
    print(f"| `{r['asr']}` ({r['obs']}) | {r['prod']}{' (PASS)' if r['prod_pass'] else ''} | {r['cs_validator']} | {r['eq_layer_cheap']} | {r['phon']} {r['phon_rule'] if r['phon_rule'] and r['phon_rule'][0] else ''} | {r['three_way_no_evidence']} |")
