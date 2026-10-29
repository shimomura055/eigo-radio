# -*- coding: utf-8 -*-
"""FY-FZ-FEMALE-VOICE-RANK-01 Z runtime evidence driver(Std/Adv各1 clip、実TTS送信)。
新規(pin無し)作品の女性話者が正式経路(derive_dialogue_voice_tts_names -> resolve_dialogue_voice -> er063 real_generators()['dialogue'])で
Leda(女性1位)になり、SDK境界の実送信voice(cost_logのtts_voice_sent)もLedaであることを記録する。
合成story(fvr_ev_story)はこのdriverのprocess内にだけ登録(Production registryは変更しない)。API費用は小(各1文)。"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "netblock_harness_01"))
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")
OUT = os.path.join(ROOT, "docs/research/FY-FZ-FEMALE-VOICE-RANK-01/evidence/z")
os.makedirs(OUT, exist_ok=True)

import er005_cost_logger as cl  # noqa: E402
cl.install(os.path.join(OUT, "cost_log.jsonl"))
import er062_family_z_structure_01 as st  # noqa: E402
import er063_family_z_audio_01 as a63  # noqa: E402

KEY = "fvr_ev_story"
st.STORY_VOICE_ROSTER[KEY] = (
    {"speaker": "heroine", "gender": "female", "order": 1, "first_appearance": "evidence driver(合成)"},
    {"speaker": "hero", "gender": "male", "order": 2, "first_appearance": "evidence driver(合成)"},
)
st.STORY_SPEAKER_CONFIG[KEY] = {"speaker_aliases": {"heroine": "heroine", "hero": "hero", "narrator": "narrator"},
                                "dialogue_voice_tts_names": st.derive_dialogue_voice_tts_names(KEY)}
assert KEY not in st.STORY_VOICE_PINS
voice = a63.resolve_dialogue_voice("heroine", KEY)
male = a63.resolve_dialogue_voice("hero", KEY)
rec = st.derive_voice_assignment(KEY)
print("resolved heroine:", voice, " hero:", male)
assert voice == "Leda" and male == "Algieba", (voice, male)
gens = a63.real_generators()
TEXT = {"a2": "I will wait for you here until the sun goes down.",
        "b1b": "I will wait for you here until the sun goes down, and I will not leave."}
res = {"story_key": KEY, "voice_assignment_record": rec, "clips": {}}
for level in (sys.argv[1:] or ["a2", "b1b"]):
    spec = a63.ClipSpec(clip_id=f"fvr_ev_{level}_heroine", level=level, kind="dialogue", text=TEXT[level], voice=voice, speaker="heroine")
    path = os.path.join(OUT, level, "narration", f"{spec.clip_id}.wav").replace("\\", "/")   # 本番は/区切り(減速後処理がrsplit("/")で親dirを求める)
    os.makedirs(os.path.dirname(path), exist_ok=True)   # er063と同じ <run>/<level>/narration/ 配置(減速後処理が親dirを参照する)
    with cl.logging_context("FVR_Z_EVIDENCE", f"tts_{level}"), cl.segment_context(spec.clip_id):
        r = gens["dialogue"](spec, path)
    res["clips"][level] = {"status": r.get("status"), "voice_planned": spec.voice, "voice_result": r.get("voice"), "path": path,
                           "attempts": len(r.get("attempts_log") or []), "asr_text": r.get("asr_text")}
    print(level, res["clips"][level])
with open(os.path.join(OUT, "z_voice_evidence_" + "_".join(sys.argv[1:] or ["all"]) + ".json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
