# ============================================================
# er008_n7_content_audio_qa_02.py
# ER-008-N7-CONTENT-AUDIO-QA-02
# ============================================================
# No.7正式Baselineのユーザー試聴で見つかった問題の調査・必要な範囲の
# 修正専用runner。B1 Key Phrase rank2の再生成(Part A)、A2 Key Phrase
# pause計測(Part B)、A2 Point One見出しRCA用の音声再生成(Part C)を
# 担当する。

from __future__ import annotations

import json
import time

import er008_n7_baseline_reset_01 as baseline

THEME_ID = baseline.THEME_ID
OUT_DIR = baseline.OUT_DIR


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


# ============================================================
# Part A: B1 Key Phrase rank2("compare poorly with")の再生成
# ============================================================
def regenerate_b1_kp2() -> dict:
    import er003_v1_n3_01_tts_generate as tts_gen
    import er006_audio_cost_pilot_02_shared_narration as shared_narration

    out_dir = f"{OUT_DIR}/b1b"
    narration_dir = f"{out_dir}/narration"
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    item = next(it for it in kp["items"] if it["rank"] == 2)
    used_form = item["used_form"]
    ja_gloss = item["japanese_gloss"]

    baseline.pilot.enable_sync_tts_mode()
    try:
        en_r = shared_narration.ensure_key_phrase_english_component(
            tts_gen.tts_safe_kp_en(used_form), f"{narration_dir}/kp2_en.wav")
        ja_r = tts_gen.generate_charon_japanese_with_reading_safety(
            ja_gloss, f"{narration_dir}/kp2_ja_charon.wav", tts_gen.expected_substring_ja(ja_gloss))
    finally:
        baseline.pilot.disable_sync_tts_mode()

    result_path = f"{out_dir}/audit/tts_generation_results.json"
    data = load_json(result_path)
    data["key_phrases"]["2"] = {"english": en_r, "japanese": ja_r}
    save_json(result_path, data)

    print(f"[{THEME_ID}] B1 kp2再生成完了。english status={en_r.get('status')} "
          f"asr_text={en_r.get('asr_text')!r} | japanese status={ja_r.get('status')}")
    return {"english": en_r, "japanese": ja_r}


def reassemble_b1() -> dict:
    import er003_v1_n3_01_assemble as asm
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    result = asm.stage_assemble_b1(theme)
    print(f"[{THEME_ID}] B1再組み立て完了。{result}")
    return result


# ============================================================
# Part C: A2 Point One見出しのTTS発音RCA
# ============================================================
def rca_a2_point_one_heading() -> dict:
    """canonical/TTS input/生成WAV/Primary(OpenAI)/Secondary(Azure)ASR/
    Validator判定を全て記録する。Azure Secondary ASRは通常の生成フローでは
    Primary ASRがmismatchを返した場合のみ起動する(cascadeのgate条件)ため、
    RCA目的でここでは無条件に両方呼ぶ。"""
    import er006_asr_provider_routing_01 as routing
    import er006_secondary_asr_01 as sec

    path = f"{OUT_DIR}/a2/narration/point_one_heading.wav"
    d = load_json(f"{OUT_DIR}/a2/audit/tts_generation_results.json")
    seg = d["segments"]["point_one_heading"]

    primary_text, primary_err = routing.transcribe(path, language="en-US")
    secondary_text, secondary_err = sec.get_full_text_via_azure_stt_with_phrase_list(
        path, language="en-US", phrases=None)

    print(f"[{THEME_ID}] A2 point_one_heading RCA")
    print(f"  canonical_text={seg.get('canonical_text')!r}")
    print(f"  original asr_verified={seg.get('asr_verified')} classification(fallback attempt1)="
          f"{seg.get('fallback_attempts_log', [{}])[0].get('audio_classification')}")
    print(f"  Primary(OpenAI) re-transcribe now: {primary_text!r} err={primary_err}")
    print(f"  Secondary(Azure) transcribe now:   {secondary_text!r} err={secondary_err}")
    return {"canonical_text": seg.get("canonical_text"), "primary_text": primary_text,
            "secondary_text": secondary_text}


def regenerate_a2_point_one_heading(out_name: str = "point_one_heading") -> dict:
    """point_one_headingを同じ経路(generate_english_segment_with_fallback)で
    再生成する。out_nameを変えれば試聴用の別ファイルとして残せる。"""
    import er003_v1_crosslevel_audio_02_common as c
    import er003_v1_n3_01_tts_generate as tts_gen

    parts = load_json(f"{OUT_DIR}/a2/parts.json")
    text = parts["point_one_heading"]
    out_path = f"{OUT_DIR}/a2/narration/{out_name}.wav"

    baseline.pilot.enable_sync_tts_mode()
    try:
        result = c.generate_english_segment_with_fallback(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), out_path,
            tts_gen.first_words(text, 3), max_extra_chars=20)
    finally:
        baseline.pilot.disable_sync_tts_mode()
    result["canonical_text"] = text
    print(f"[{THEME_ID}] A2 point_one_heading再生成({out_name})完了。status={result.get('status')} "
          f"asr_text={result.get('asr_text')!r}")
    return result


if __name__ == "__main__":
    import sys
    import er005_cost_logger as cl
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage == "kp2_fix":
        regenerate_b1_kp2()
    elif stage == "reassemble_b1":
        reassemble_b1()
    elif stage == "point_one_rca":
        rca_a2_point_one_heading()
    elif stage == "point_one_regen":
        out_name = sys.argv[2] if len(sys.argv) > 2 else "point_one_heading_candidate"
        regenerate_a2_point_one_heading(out_name)
    else:
        print("usage: er008_n7_content_audio_qa_02.py [kp2_fix|reassemble_b1|point_one_rca|point_one_regen]")
