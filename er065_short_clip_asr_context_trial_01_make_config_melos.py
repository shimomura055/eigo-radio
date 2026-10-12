# -*- coding: utf-8 -*-
"""Melos(run_e2e_02複製音声)用のconfig_melos_01.jsonを生成する(config生成のみ・オフライン無料)。
作品固有の値(focus_word、canonical、clip選択)はここと出力configにだけ存在し、runner/lib/buildは汎用。"""
import glob
import json
import os
import re

OUT = "er065_output/short_clip_asr_context_trial_01"
SRC = OUT + "/audio_src/"


def clip_meta(level, cid):
    plan = json.load(open(SRC + f"segment_plan_{level}.json", encoding="utf-8"))
    c = next(x for x in plan["clips"] if x["id"] == cid)
    base = SRC + f"{level}_narration/{cid}"
    path = base + "_original.wav" if os.path.exists(base + "_original.wav") else base + ".wav"
    voice = model = None
    for j in sorted(glob.glob(SRC + f"{level}_narration/attempts/{cid}_attempt*.json")):
        d = json.load(open(j, encoding="utf-8"))
        voice, model = d.get("voice"), d.get("model")
    text = c["text"].replace("“", "").replace("”", "").replace('"', "").strip()
    return {"path": path, "text": text, "voice": voice, "model": model, "role": c["voice"]}


A2 = {"n_c1": "full_story_part1_c1", "n_c3": "full_story_part1_c3", "n_c7": "full_story_part1_c7",
      "n_c9": "full_story_part1_c9", "n_c11": "full_story_part1_c11", "n_p3c1": "full_story_part3_c1",
      "m_c2": "full_story_part1_c2", "m_c4": "full_story_part1_c4", "m_c6": "full_story_part1_c6",
      "m_p3c2": "full_story_part3_c2", "m_p3c4": "full_story_part3_c4", "k_c8": "full_story_part1_c8",
      "f_c10": "full_story_part1_c10"}
SLOTS = {
    "N3": ["n_c7"], "N8": ["n_c3"], "N8b": ["n_c9"], "N14": ["n_c11"], "N27": ["n_p3c1"],
    "N3x": ["n_c1"],
    "D3": ["m_p3c2"], "D5": ["m_c4"], "D6": ["m_c2"], "D8": ["k_c8"], "D11": ["m_c2", "m_c4"],
    "D14": ["m_c2", "m_c4", "m_c6"], "D25": ["m_c2", "m_c4", "m_c6", "m_p3c2", "k_c8"],
    "R_pre": ["m_c4"], "R_post": ["m_c6"], "R_pre2": ["n_c3", "m_c4"], "R_post2": ["m_c6", "n_c7"],
    "R_pre3": ["n_c1", "m_c2", "n_c3", "m_c4"],
    "NN3": ["n_c7"], "NN8": ["n_c3", "n_c7"], "NN8x": ["n_c3"],
}
# 注: 上のn_*はnarrator(target同一voice)、m_*はMelos台詞voice(Algieba)、k_*はking(Charon)、f_*はfriend(Erinome)

pools = {}
for level in ("a2", "b1b"):
    clips = {}
    for k, cid in A2.items():
        clips[k] = clip_meta(level, cid)
    pools[level] = {"slots": SLOTS, "clips": clips}

# ---- targets: c5「Melos said.」の各take(重複shaは1つに集約)
def tpath(level, name):
    return SRC + f"{level}_narration/" + name


targets = [
    {"id": "a2_att1", "path": tpath("a2", "attempts/full_story_part1_c5_attempt1_customadfcf33f.wav"), "pool": "a2",
     "voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "note": "Std OK take(Prod: Tier3 Azure=Melos said.)", "label_hint": "prod_ok"},
    {"id": "a2_att2", "path": tpath("a2", "attempts/full_story_part1_c5_attempt2_customadfcf33f.wav"), "pool": "a2",
     "voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "note": "Std NG take(Prod: UNCERTAIN, Azure=Mellow x3)", "label_hint": "prod_ng"},
    {"id": "a2_att3", "path": tpath("a2", "attempts/full_story_part1_c5_attempt3_minimalfallback.wav"), "pool": "a2",
     "voice": "Aoede", "model": "gemini-2.5-pro-preview-tts", "note": "Std fallback take(Prod: Pattern A ACCEPT, =_original.wav)", "label_hint": "prod_ok"},
    {"id": "a2_att4", "path": tpath("a2", "attempts/full_story_part1_c5_attempt4_customadfcf33f.wav"), "pool": "a2",
     "voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "note": "Std NG take(Prod ASR: 'Mellis said')", "label_hint": "prod_ng"},
    {"id": "a2_att5", "path": tpath("a2", "attempts/full_story_part1_c5_attempt5_minimalfallback.wav"), "pool": "a2",
     "voice": "Aoede", "model": "gemini-2.5-pro-preview-tts", "note": "Std NG take(Prod ASR: 'melloset' TTS_FAILURE)", "label_hint": "prod_ng"},
    {"id": "a2_att6", "path": tpath("a2", "attempts/full_story_part1_c5_attempt6_minimalfallback.wav"), "pool": "a2",
     "voice": "Aoede", "model": "gemini-2.5-pro-preview-tts", "note": "Std NG take(Prod ASR: 'Mellowset' TTS_FAILURE, =現行final)", "label_hint": "prod_ng"},
    {"id": "b1b_att1", "path": tpath("b1b", "attempts/full_story_part1_c5_attempt1_englishstyleprefixwidemargin.wav"), "pool": "b1b",
     "voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "note": "Adv take(Prod: UNCERTAIN 'Mello said.'; Azure=Mellow x3)", "label_hint": "prod_ng"},
]

recipes = [
    {"id": "R00_alone", "pre": [], "post": [], "kind": "alone"},
    # 同一ナレーター(同voice)文脈
    {"id": "Npre3", "pre": ["N3"], "post": [], "kind": "same_voice"},
    {"id": "Npre8", "pre": ["N8"], "post": [], "kind": "same_voice"},
    {"id": "Npre14", "pre": ["N14"], "post": [], "kind": "same_voice"},
    {"id": "Npre27", "pre": ["N27"], "post": [], "kind": "same_voice"},
    {"id": "Npost3", "pre": [], "post": ["N3"], "kind": "same_voice"},
    {"id": "Npost8", "pre": [], "post": ["N8b"], "kind": "same_voice"},
    {"id": "Npost14", "pre": [], "post": ["N14"], "kind": "same_voice"},
    {"id": "Nboth", "pre": ["N8"], "post": ["N3"], "kind": "same_voice"},
    # 異なるナレーター(台詞voice)文脈
    {"id": "Dpre3", "pre": ["D3"], "post": [], "kind": "diff_voice"},
    {"id": "Dpre5", "pre": ["D5"], "post": [], "kind": "diff_voice"},
    {"id": "Dpre6", "pre": ["D6"], "post": [], "kind": "diff_voice"},
    {"id": "Dpre8", "pre": ["D8"], "post": [], "kind": "diff_voice"},
    {"id": "Dpre11", "pre": ["D11"], "post": [], "kind": "diff_voice"},
    {"id": "Dpre14", "pre": ["D14"], "post": [], "kind": "diff_voice"},
    {"id": "Dpre25", "pre": ["D25"], "post": [], "kind": "diff_voice"},
    {"id": "Dpost3", "pre": [], "post": ["D3"], "kind": "diff_voice"},
    {"id": "Dpost8", "pre": [], "post": ["D8"], "kind": "diff_voice"},
    {"id": "Dboth", "pre": ["D5"], "post": ["D3"], "kind": "diff_voice"},
    # 実ストーリー順の隣接clip(c3 c4 [T] c6 c7)
    {"id": "Rpre", "pre": ["R_pre"], "post": [], "kind": "mixed_real"},
    {"id": "Rpost", "pre": [], "post": ["R_post"], "kind": "mixed_real"},
    {"id": "Rboth", "pre": ["R_pre"], "post": ["R_post"], "kind": "mixed_real"},
    {"id": "Rwin5", "pre": ["R_pre2"], "post": ["R_post2"], "kind": "mixed_real"},
    {"id": "Rwin7", "pre": ["R_pre3"], "post": ["R_post2"], "kind": "mixed_real"},
]

cfg = {"work_id": "family_z_melos_run_e2e_02", "group": "main", "focus_word": "Melos",
       "target_canonical": "Melos said.", "gap_ms": 300, "pools": pools, "targets": targets, "recipes": recipes,
       "targets_recipes": {}}
json.dump(cfg, open(OUT + "/config_melos_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("targets", len(targets), "recipes", len(recipes))
for k in ("n_c7", "n_c3", "n_c11", "m_c4", "k_c8", "m_p3c2"):
    print(k, pools["a2"]["clips"][k]["voice"], pools["a2"]["clips"][k]["text"][:50], pools["b1b"]["clips"][k]["text"][:50])
