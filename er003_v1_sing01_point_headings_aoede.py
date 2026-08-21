# ============================================================
# er003_v1_sing01_point_headings_aoede.py
# ER-003-B1-NOVEL-AUDIO-01-VOICE-02: Point見出しをAoedeへ変更
# ============================================================
# ユーザー指示: First point./Second point.とそれに続く英文は記事本体
# (Point One/Two本文)なのでAoede(女性)にする。
#
# 1回目の試行で、ASR検証が単語列の先頭一致(subsequence)のみを見ており、
# 末尾に長さチェックを付け忘れたため、"First point."の生成で無関係かつ
# 不適切な内容("First point sex is always on his mind.")が続けて
# hallucinationされたにもかかわらず誤ってPASS扱いになっていたことが
# 判明した。本スクリプトでは既存の長さチェック(max_extra_chars)を必ず
# 併用し、同じ誤りを再発させない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_point_headings_aoede.py

from __future__ import annotations

import json

import er002_common as common
import er002_gemini_client as gclient
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01

AOEDE = "Aoede"
SAFETY_MARGIN = 0.35
OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"


def generate(text: str, out_path: str, max_attempts: int = 8) -> dict:
    max_len = len(text) + 15
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        use_minimal = attempt > 4
        call_fn = gclient.make_tts_call_fn(AOEDE)
        if use_minimal:
            # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: fallback経路にも
            # Structured Separationを適用する。
            prompt = p4c.build_tts_prompt(text, repro01.MINIMAL_INSTRUCTION_PREFIX)
            instruction_type = "minimal_fallback"
        else:
            prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
            instruction_type = "english_style_prefix"
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        trimmed = None
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": str(err) if not ok else "no speech",
                                  "instruction_type": instruction_type})
            print(f"    attempt {attempt} ({instruction_type}): FAILED")
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(text, asr_text, asr_error=asr_err)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = match["passed"] and length_ok
        attempts_log.append({"attempt": attempt, "asr_text": asr_text, "verdict": match["verdict"],
                              "length_ok": length_ok, "verified": verified, "instruction_type": instruction_type})
        print(f"    attempt {attempt} ({instruction_type}): asr={asr_text!r} verdict={match['verdict']} length_ok={length_ok}")
        if verified:
            return {"status": "OK", "text": text, "path": out_path, "voice": AOEDE, "asr_verified": True,
                    "asr_text": asr_text, "attempts_log": attempts_log, "instruction_type": instruction_type,
                    "max_len": max_len}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証(内容+長さ)に合格しませんでした",
            "attempts_log": attempts_log}


def main():
    jobs = {"point_one_heading": "First point.", "point_two_heading": "Second point."}
    results = {}
    for name, text in jobs.items():
        print(f"[POINT-HEADINGS-AOEDE] {name}: {text!r}")
        out_path = f"{NARRATION_DIR}/{name}_aoede.wav"
        r = generate(text, out_path)
        results[name] = r
        print(f"[POINT-HEADINGS-AOEDE] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/point_headings_aoede_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    print("完了。失敗:" if failed else "完了。全件成功。", failed if failed else "")


if __name__ == "__main__":
    main()
