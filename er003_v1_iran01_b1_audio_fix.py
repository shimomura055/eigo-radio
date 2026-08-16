# ============================================================
# er003_v1_iran01_b1_audio_fix.py
# ER-003-IRAN-A2-B1-01: num_one〜five / point_two のASR数詞正規化対応
# ============================================================
# Azure STTは "One." を "1." のように数字表記へ正規化して書き起こす
# (VOICE-01で確立済みの既知事象、共通モジュールは変更せず記事専用の
# ローカル等価判定で対応する方針を踏襲)。num_one〜fiveは
# er003_v1_sing01_voice01_labels_fix.generate_label(数詞/数字等価判定)
# をそのまま再利用する。point_twoは新たに"one-fifth"→"1/5"という同種の
# 分数正規化が起きたため、期待テキスト側を等価変換したうえで既存の
# safety.validate_asr_match(共通モジュール本体は無変更)にかける、
# 同じ設計方針のローカル判定を追加する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_b1_audio_fix.py

from __future__ import annotations

import json
import re

import er002_common as common
import er002_gemini_client as gclient
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_iran01_articles_generate as gen
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_labels_fix as labels_fix

OUT_DIR = f"{gen.OUT_DIR}/b1"
NARRATION_DIR = f"{OUT_DIR}/narration"
AOEDE = "Aoede"
SAFETY_MARGIN = 0.35

with open(f"{OUT_DIR}/fixed_news_parts.json", encoding="utf-8") as f:
    PARTS = json.load(f)


def normalize_fraction_words(text: str) -> str:
    return re.sub(r"\bone[\s-]fifth\b", "1/5", text, flags=re.IGNORECASE)


def generate_point_two_wide_margin(text: str, out_path: str, max_attempts: int = 6,
                                    max_extra_chars: int = 15) -> dict:
    """news_tail_fix.generate_news_narration_wide_marginと同一のTTS/trim経路
    (Aoede、安全マージン0.35秒)だが、ASR一致判定のみ、期待テキスト側の
    "one-fifth"を"1/5"へ正規化してから既存safety.validate_asr_matchへ渡す
    (Azure STTが分数を数字表記へ正規化する既知事象への、記事専用ローカル対応)。"""
    normalized_expected = normalize_fraction_words(text)
    max_len = len(text) + max_extra_chars
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        call_fn = gclient.make_tts_call_fn(AOEDE)
        prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        instruction_type = "english_style_prefix_wide_margin_fraction_fix"
        trimmed = None
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": str(err) if not ok else "発話区間検出失敗",
                                  "instruction_type": instruction_type})
            r = repro01.generate_english_component_minimal_instruction(text, out_path)
            instruction_type = "minimal_fallback"
            if r.get("status") != "OK":
                attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                      "instruction_type": instruction_type})
                continue
        else:
            common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)

        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(normalized_expected, asr_text, n=6, asr_error=asr_err)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = match["passed"] and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "asr_verdict": match["verdict"],
                              "length_ok": length_ok, "verified": verified})
        if verified:
            metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "asr_verified": True, "asr_text": asr_text,
                    "attempts_log": attempts_log, "instruction_type": instruction_type,
                    "safety_margin_seconds": SAFETY_MARGIN, "clipping_detected": metrics["clipping_detected"],
                    "validation_method": "normalize_fraction_words + safety.validate_asr_match(記事専用ローカル対応)"}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


def main():
    results = {}

    number_words = {"num_one": "One.", "num_two": "Two.", "num_three": "Three.",
                     "num_four": "Four.", "num_five": "Five."}
    for name, text in number_words.items():
        print(f"[IRAN01-B1-FIX] {name}再生成(Charon、数詞/数字等価判定): {text!r}...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = labels_fix.generate_label(text, out_path)
        results[name] = r
        print(f"[IRAN01-B1-FIX] {name}: status={r.get('status')}")

    print("[IRAN01-B1-FIX] point_two再生成(Aoede、分数正規化対応)...")
    point_two_path = f"{NARRATION_DIR}/point_two.wav"
    r = generate_point_two_wide_margin(PARTS["point_two_body"], point_two_path)
    results["point_two"] = r
    print(f"[IRAN01-B1-FIX] point_two: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/audio_fix_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    # segment_generation_results.jsonへ反映
    with open(f"{OUT_DIR}/audit/segment_generation_results.json", encoding="utf-8") as f:
        all_results = json.load(f)
    for name, r in results.items():
        if r.get("status") == "OK":
            all_results[name] = r
    with open(f"{OUT_DIR}/audit/segment_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    print("完了。失敗:" if failed else "完了。全件成功。", failed if failed else "")


if __name__ == "__main__":
    main()
