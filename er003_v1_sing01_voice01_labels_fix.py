# ============================================================
# er003_v1_sing01_voice01_labels_fix.py
# ER-003-B1-NOVEL-AUDIO-01-VOICE-01: 短い番号ラベルの個別再生成
# ============================================================
# num_one〜five("One."〜"Five.")とPoint One/Two見出し("Point One."/
# "Point Two.")は、Azure STTが数詞を数字表記へ正規化して書き起こす
# ("One." → "1.")ため、単語一致検証(er003_audio_tts_asr_safety.
# validate_asr_match)がこの用途では毎回不一致になっていた。これは
# 内容の誤りではなく、綴り正規化(HARDENING-01)ではカバーしていない
# 「数詞⇔数字」の等価性の問題であり、共通モジュール自体は変更せず、
# この記事専用のローカルな等価判定を追加して対応する(OPEN-28と同種の
# 個別記事対応)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_voice01_labels_fix.py

from __future__ import annotations

import json
import re

import er002_common as common
import er002_gemini_client as gclient
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"
CHARON = "Charon"
SAFETY_MARGIN = 0.35

NUMBER_WORD_TO_DIGIT = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}


def _tokens(text: str) -> list:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def validate_number_label(expected_text: str, asr_text: str) -> bool:
    """数詞("one")と数字("1")を同義として扱う、この用途専用の緩和判定。
    それ以外の語(例: "point")は完全一致のまま要求するため、無関係な
    内容までは通さない。"""
    expected_words = _tokens(expected_text)
    if not expected_words:
        return False
    asr_words = _tokens(asr_text)
    acceptable = [{w, NUMBER_WORD_TO_DIGIT[w]} if w in NUMBER_WORD_TO_DIGIT else {w} for w in expected_words]
    n = len(acceptable)
    for i in range(len(asr_words) - n + 1):
        if all(asr_words[i + j] in acceptable[j] for j in range(n)):
            return True
    return False


def generate_label(text: str, out_path: str, max_attempts: int = 8) -> dict:
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        # 前半はENGLISH_STYLE_PREFIX、後半はMINIMAL_INSTRUCTION(短文hallucination対策の既存fallback方針)
        use_minimal = attempt > max_attempts // 2
        call_fn = gclient.make_tts_call_fn(CHARON)
        if use_minimal:
            prompt = repro01.MINIMAL_INSTRUCTION_PREFIX + text
            instruction_type = "minimal_fallback"
        else:
            prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
            instruction_type = "english_style_prefix"
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        if not ok:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err),
                                  "instruction_type": instruction_type})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間検出失敗",
                                  "instruction_type": instruction_type})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        verified = (not asr_err) and validate_number_label(text, asr_text)
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "verified": verified,
                              "trim_info": trim_info})
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "clipping_detected": metrics["clipping_detected"],
                    "validation_method": "validate_number_label(数詞/数字等価、記事専用ローカル判定)"}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


def main():
    targets = {
        "num_one": "One.", "num_two": "Two.", "num_three": "Three.",
        "num_four": "Four.", "num_five": "Five.",
        "point_one_heading": "Point One.", "point_two_heading": "Point Two.",
    }
    results = {}
    for name, text in targets.items():
        print(f"[LABEL-FIX] {name}(Charon)再生成: {text!r}...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = generate_label(text, out_path)
        results[name] = r
        print(f"[LABEL-FIX] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/voice01_labels_fix_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{OUT_DIR}/audit/voice01_generation_results.json", encoding="utf-8") as f:
        all_results = json.load(f)
    for name, r in results.items():
        if r.get("status") == "OK":
            all_results[name] = r
    with open(f"{OUT_DIR}/audit/voice01_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    print("失敗:" if failed else "全件成功。", failed if failed else "")


if __name__ == "__main__":
    main()
