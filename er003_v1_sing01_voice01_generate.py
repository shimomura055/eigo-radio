# ============================================================
# er003_v1_sing01_voice01_generate.py
# ER-003-B1-NOVEL-AUDIO-01-VOICE-01: Voice role再配置 + Point見出し追加
# ============================================================
# 既存ER-003-B1-NOVEL-AUDIO-01のFact/Ledger/B1 Scaffold/記事本文は一切
# 変更しない。Aoede=本文Listening対象、Charon=Navigator/Explanationと
# いう役割分担へ、以下を新規Charon生成する:
#   Welcome / Topic intro / Preview intro / Point explanation /
#   Key phrases intro / Full story intro / num_one〜five(番号ラベル、
#   ユーザー確認済み) / Key Phrase日本語meaning5件 / Point One・Two本文 /
#   In One Line / 新規 "Point One." "Point Two." 見出し
# Aoedeのまま維持(無変更で再利用): Preview本文、Key Phrase英語
# Component5件、Full Story Part1/2
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_voice01_generate.py

from __future__ import annotations

import json

import er002_common as common
import er002_gemini_client as gclient
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p7a_audio as p7a
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"
CHARON = "Charon"
SAFETY_MARGIN = 0.35  # AUDIO-03/NOVEL-AUDIO-01のtail切れ修正と同じ値を継承


def generate_charon_english(text: str, out_path: str, max_attempts: int = 6) -> dict:
    """ENGLISH_STYLE_PREFIX主経路(voice=Charon)+MINIMAL_INSTRUCTION
    fallback。trim安全マージンはNOVEL-AUDIO-01のtail切れ修正と同じ
    0.35秒を使う。"""
    max_len = len(text) + 15
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        call_fn = gclient.make_tts_call_fn(CHARON)
        prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        instruction_type = "english_style_prefix"
        trimmed = None
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": str(err) if not ok else "発話区間検出失敗",
                                  "instruction_type": instruction_type})
            call_fn2 = gclient.make_tts_call_fn(CHARON)
            prompt2 = repro01.MINIMAL_INSTRUCTION_PREFIX + text
            pcm2, retries2, ok2, err2 = common._call_tts_with_retry(
                call_fn2, prompt2, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
            instruction_type = "minimal_fallback"
            if not ok2:
                attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err2),
                                      "instruction_type": instruction_type})
                continue
            samples_raw2 = common.pcm_bytes_to_float_mono(pcm2)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw2, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
            if trimmed is None:
                attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間検出失敗(fallback)",
                                      "instruction_type": instruction_type})
                continue

        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(text, asr_text, n=min(6, max(1, len(text.split()))), asr_error=asr_err)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = match["passed"] and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "asr_verdict": match["verdict"],
                              "length_ok": length_ok, "verified": verified, "trim_info": trim_info})
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "clipping_detected": metrics["clipping_detected"]}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


def generate_charon_japanese(text: str, out_path: str, expected_substring: str, max_attempts: int = 6) -> dict:
    """JAPANESE_STYLE_PREFIX経路、voice=Charon。既存generate_narration_
    snippet_verified_strictと同じ判定方式(部分一致+長さ)を使うが、
    voiceだけCharonへ差し替える(p9a.generate_narration_snippetは
    voice固定のため直接組み立てる)。"""
    max_len = len(text) + 15
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        call_fn = p7a.make_tts_call_fn_for_model(p9a.JAPANESE_MODEL_NAME, CHARON)
        prompt = p9a.JAPANESE_STYLE_PREFIX + text
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        if not ok:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err)})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間検出失敗"})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, err2 = p4.get_full_text_via_azure_stt_continuous(out_path, language="ja-JP")
        substring_ok = asr_text is not None and expected_substring.lower() in asr_text.lower()
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = substring_ok and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "substring_ok": substring_ok, "length_ok": length_ok, "verified": verified,
                              "trim_info": trim_info})
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"]}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


def main():
    with open(f"{OUT_DIR}/article/support_texts.json", encoding="utf-8") as f:
        support = json.load(f)  # noqa: F841 (未使用、Support本文は無変更のため参照のみ)
    with open(f"{OUT_DIR}/audit/article_parts.json", encoding="utf-8") as f:
        parts = json.load(f)
    with open(f"{OUT_DIR}/keyphrases/keywords_canonicalized.json", encoding="utf-8") as f:
        kp = json.load(f)
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])

    jobs_english = {
        "welcome": "Welcome to English Your Way.",
        "topic_intro": "Today's topic is Sam Altman Says We're in the Singularity. Not Everyone Agrees.",
        "preview_intro": "Here's a quick preview.",
        "point_explanation_en": "Here's the point.",
        "key_phrases_intro": "Here are today's key phrases.",
        "full_story_intro": "Now, the full story.",
        "num_one": "One.", "num_two": "Two.", "num_three": "Three.", "num_four": "Four.", "num_five": "Five.",
        "point_one_heading": "Point One.",
        "point_two_heading": "Point Two.",
        "point_one": f"{parts['point_one_heading']}. {parts['point_one_body']}",
        "point_two": f"{parts['point_two_heading']}. {parts['point_two_body']}",
        "in_one_line": parts["in_one_line"],
    }

    results = {}
    for name, text in jobs_english.items():
        print(f"[VOICE01] {name}(Charon)生成: {text[:40]!r}...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = generate_charon_english(text, out_path)
        results[name] = r
        print(f"[VOICE01] {name}: status={r.get('status')}")

    for item in kp_items:
        rank = item["rank"]
        ja_gloss = item["japanese_gloss"]
        ja_tts_text = ja_gloss.lstrip("～~・")
        name = f"kp{rank}_ja"
        print(f"[VOICE01] {name}(Charon)生成: {ja_tts_text!r}...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = generate_charon_japanese(ja_tts_text, out_path, ja_tts_text[:4])
        results[name] = r
        print(f"[VOICE01] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/voice01_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    if failed:
        print(f"[VOICE01] 生成失敗segmentあり: {failed}")
    else:
        print("[VOICE01] 全件成功。")


if __name__ == "__main__":
    main()
