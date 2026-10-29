# -*- coding: utf-8 -*-
"""FY-STD-V2-FEMALE-VOICE-TRIAL-01: Std Full Story Voice 2(y_voice_2)の女性Voice 5候補比較(DEV/Trial専用。Production run_02には一切書かない)。
Voice名以外(本文・Style prefix[fx_20261017 FULL_STORY a2]・6%減速・model・ASR/Gate・retry)は Production と同じ関数 ya の部品を呼ぶ。出力: er121_output/family_y_voice_trial_01/surname_v2/"""
import json, os, sys, time, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er005_cost_logger as cl
OUT = "er121_output/family_y_voice_trial_01/surname_v2"
SRC_RUN = "er121_output/family_y_production_01/surname_choice/run_02"
CANDS = [("c1", "Zephyr"), ("c2", "Kore"), ("c3", "Leda"), ("c4", "Sulafat"), ("c5", "Erinome")]   # Y候補表 er121_family_y_structure_01.py:58 女性pool(=Z承認済み女性5)


def main(only=None):
    assert os.path.abspath(OUT).replace("\\", "/").find("/run_02") < 0
    os.makedirs(OUT, exist_ok=True)
    cl.install(f"{OUT}/cost_log.jsonl")
    import er121_family_y_audio_01 as ya
    import er003_v1_n3_01_tts_generate as n3_tts
    import er019_family_x_audio_production_runner_01 as xr
    sp = ya.style_profile_mod
    profile = ya.Y_APPROVED_STYLE_PROFILE
    role_style_slower, base, _ = None, None, None
    _role_style, _base, _fl = ya._style_resolvers("a2", ya.TTS_BACKEND, profile)

    def _base_slower(role):
        b = _base(role)
        if b is None:
            return None
        return f"{b}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"
    style = sp.resolve_role_style(profile, "FULL_STORY", "a2", _base_slower) or n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER
    parts = json.load(open(f"{SRC_RUN}/a2/parts.json", encoding="utf-8"))
    text = parts["segments"]["y_voice_2"]
    tts_input = xr._pnap_supply(text, n3_tts.tts_safe_news_en(text))
    sub = n3_tts.first_words(text)
    json.dump({"script_text": text, "tts_input": tts_input, "style_prefix": style, "style_profile": profile, "tts_backend": ya.TTS_BACKEND,
               "script_sha256": hashlib.sha256(text.encode()).hexdigest()}, open(f"{OUT}/common_conditions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    res_all = {}
    for cid, voice in CANDS:
        if only and cid not in only:
            continue
        d = f"{OUT}/{cid}_{voice}"
        os.makedirs(d, exist_ok=True)
        wav = f"{d}/y_voice_2.wav"
        t0 = time.time()
        with cl.segment_context(f"trial_{cid}_{voice}"):
            with ya.tts_voice(voice):
                r = n3_tts.generate_a2_segment_with_slowdown(
                    tts_input, wav, sub, style_prefix_override=style, disfluency_qa=False,
                    enable_connected_speech_equivalence_layer=ya.retry_primitive.connected_speech_enabled_for("y_voice_2"),
                    enable_repetition_qa=True, tts_backend=ya.TTS_BACKEND)
        r["requested_voice"] = voice
        r["elapsed_s"] = round(time.time() - t0, 1)
        json.dump(r, open(f"{d}/result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
        res_all[cid] = {"voice": voice, "status": r.get("status"), "duration": r.get("duration_seconds"), "model": r.get("model"), "voice_used": r.get("voice")}
        print(cid, voice, res_all[cid], flush=True)
    return res_all


if __name__ == "__main__":
    main(set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None)
