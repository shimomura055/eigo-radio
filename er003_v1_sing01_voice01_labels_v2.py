# ============================================================
# er003_v1_sing01_voice01_labels_v2.py
# ER-003-B1-NOVEL-AUDIO-01-VOICE-01: Point見出し代替文言生成
# ============================================================
# "Point One."/"Point Two."は、英語の小数点読み("point one"="0.1")と
# 完全に同じ語列であるため、voice/大文字小文字/文中埋め込みのいずれを
# 試してもTTSモデルが小数点表現として発音し、"1."/"2."としか認識され
# ないことをユーザーへ報告・確認した。ユーザー判断により、意味を保ち
# つつ字面だけ変える代替文言"First point."/"Second point."を採用する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_voice01_labels_v2.py

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

CHARON = "Charon"
SAFETY_MARGIN = 0.35
OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"


def generate(text: str, out_path: str, max_attempts: int = 6) -> dict:
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        call_fn = gclient.make_tts_call_fn(CHARON)
        prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        trimmed = None
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": str(err) if not ok else "発話区間検出失敗"})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(text, asr_text, asr_error=asr_err)
        attempts_log.append({"attempt": attempt, "asr_text": asr_text,
                              "verdict": match["verdict"], "passed": match["passed"]})
        print(f"    attempt {attempt}: asr={asr_text!r} verdict={match['verdict']}")
        if match["passed"]:
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


def main():
    jobs = {"point_one_heading": "First point.", "point_two_heading": "Second point."}
    results = {}
    for name, text in jobs.items():
        print(f"[LABEL-V2] {name}: {text!r}")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = generate(text, out_path)
        results[name] = r
        print(f"[LABEL-V2] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/voice01_labels_v2_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{OUT_DIR}/audit/voice01_generation_results.json", encoding="utf-8") as f:
        all_results = json.load(f)
    for name, r in results.items():
        if r.get("status") == "OK":
            all_results[name] = r
    with open(f"{OUT_DIR}/audit/voice01_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    print("完了。失敗:" if failed else "完了。全件成功。", failed if failed else "")


if __name__ == "__main__":
    main()
