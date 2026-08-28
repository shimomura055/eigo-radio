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
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er007_ja_secondary_asr_01 as ja_secondary
import er006_preprod_hardening_01_validation as audio_validation
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er011_human_review_lock_01 as review_lock

OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"
CHARON = "Charon"
SAFETY_MARGIN = 0.35  # AUDIO-03/NOVEL-AUDIO-01のtail切れ修正と同じ値を継承


@review_lock.guarded_generate("en")
def generate_charon_english(text: str, out_path: str,
                             max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS) -> dict:
    """ENGLISH_STYLE_PREFIX主経路(voice=Charon)+MINIMAL_INSTRUCTION
    fallback。trim安全マージンはNOVEL-AUDIO-01のtail切れ修正と同じ
    0.35秒を使う。"""
    max_len = len(text) + 15
    attempts_log = []
    classification_history = []
    for attempt in range(1, max_attempts + 1):
        # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
        # (声・モデルはgclient.make_tts_call_fn(CHARON)と同一)。
        call_fn = batch_wiring.make_batch_tts_call_fn(common.MODEL_NAME, CHARON, output_path=out_path)
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
            call_fn2 = batch_wiring.make_batch_tts_call_fn(common.MODEL_NAME, CHARON, output_path=out_path)
            # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: fallback経路にも
            # Structured Separationを適用する。
            prompt2 = p4c.build_tts_prompt(text, repro01.MINIMAL_INSTRUCTION_PREFIX)
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

        # ER-005-AUDIO-WASTE-REDUCTION-01: hallucinationを疑わせる異常長
        # 音声を、ASR実行前に検知して破棄する(kp5_en実例: association
        # という1語が17秒超の無関係な内容になった)。
        anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
        if anomaly["is_anomaly"]:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": anomaly["reason"],
                                  "instruction_type": instruction_type, "duration_anomaly": anomaly})
            continue

        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = routing.transcribe(out_path, language="en-US")
        # ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: safety.validate_asr_match
        # (word-subsequence一致)から、正規化+6分類+Protected Check+同一
        # signature retry guardrail方式へ切り替える。
        length_ok = asr_text is not None and len(asr_text) <= max_len
        ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
        verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
            text, asr_text, classification_history, out_path, language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
        verified = verified_content and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "audio_classification": cls.classification,
                              "length_ok": length_ok, "verified": verified, "trim_info": trim_info})
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "clipping_detected": metrics["clipping_detected"]}
        if stop_retrying:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "clipping_detected": metrics["clipping_detected"],
                    "reason": f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification})"}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


# ER-003-N3-ROOT-FIX-01(2026-08-17): 短い単独の日本語フレーズ(Key
# Phraseの日本語訳・語句)にJAPANESE_STYLE_PREFIX(長い演技指示、約1800
# 文字)を使うと、モデルが指示文自体を読み上げてしまう事例が高頻度で
# 確認された(POINT_LABEL_FIDELITY_RULE除去後も、Health B1「modeled
# differences」で5回中5回再現。同じ検証で、文単位の長さを持つJapanese
# Titleは0回中5回で再現せず — 短いフレーズに固有の問題と判明)。
# 英語Key Phraseに既存のMINIMAL_INSTRUCTION_PREFIX(repro01、"Speak the
# following text aloud naturally...")と同じ考え方を、日本語の短い
# フレーズにも適用する。
MINIMAL_INSTRUCTION_PREFIX_JA = (
    "次の文章だけを、翻訳・言い換え・追加をせず、自然で温かいpodcastの"
    "ナレーターの声でそのまま読み上げてください。\n\n"
)


def generate_charon_japanese_minimal_instruction(text: str, out_path: str) -> dict:
    # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: fallback経路もStructured
    # Separationを適用する(instruction内容・text内容は無変更)。
    prompt = p4c.build_tts_prompt(text, MINIMAL_INSTRUCTION_PREFIX_JA)
    # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
    # (声・モデルはp7a.make_tts_call_fn_for_modelと同一)。
    call_fn = batch_wiring.make_batch_tts_call_fn(p9a.JAPANESE_MODEL_NAME, CHARON, output_path=out_path)
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"minimal instructionでもTTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
            "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
            "instruction": "minimal (not JAPANESE_STYLE_PREFIX)"}


@review_lock.guarded_generate("ja")
def generate_charon_japanese(text: str, out_path: str, expected_substring: str,
                              max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS) -> dict:
    """JAPANESE_STYLE_PREFIX経路、voice=Charon。既存generate_narration_
    snippet_verified_strictと同じ判定方式(部分一致+長さ)を使うが、
    voiceだけCharonへ差し替える(p9a.generate_narration_snippetは
    voice固定のため直接組み立てる)。標準経路がmax_attempts回で合格
    しない場合、minimal instructionへフォールバックする(声・モデルは
    変えない、テキストも変えない。ER-003-N3-ROOT-FIX-01)。

    ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B: 同一segmentの
    TTS総試行回数(標準経路+fallback経路の合計)がmax_attempts回を
    超えないよう、fallback経路には標準経路で実際に消費した試行回数を
    差し引いた残り予算だけを渡す(標準・fallbackそれぞれが独立に
    max_attempts回ずつ試行すると、合計で最大2×max_attempts回に達して
    しまうため)。"""
    max_len = len(text) + 15
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
        # (声・モデルはp7a.make_tts_call_fn_for_modelと同一)。
        call_fn = batch_wiring.make_batch_tts_call_fn(p9a.JAPANESE_MODEL_NAME, CHARON, output_path=out_path)
        # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: build_tts_prompt()経由
        # にする(以前は直接連結、Structured Separationの抜け穴だった)。
        prompt = p4c.build_tts_prompt(text, p9a.JAPANESE_STYLE_PREFIX)
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
        # ER-005-AUDIO-WASTE-REDUCTION-01: hallucination(指示文の
        # パラフレーズ等、無関係な内容の生成)を疑わせる異常長音声を、
        # ASR実行前に検知して破棄する(kp5_ja実例: 数秒のはずが100秒超)。
        anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "ja")
        if anomaly["is_anomaly"]:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": anomaly["reason"], "duration_anomaly": anomaly})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, err2 = routing.transcribe(out_path, language="ja-JP")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        # ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01: 旧prefix+length
        # (文頭一致+文字数)方式を廃止し、全文sequence比較+Protected Check
        # (数字/否定/内容語/固有名詞)による新Validatorを使う。固有名詞・
        # 略語らしき語のみの差はTTSを再生成せず、Cascade(Primary#2->
        # Secondary Azure#1->#2)で同じ音声のASRだけをやり直す。
        verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
            text, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI)
        verified = verified_content and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "length_ok": length_ok, "audio_classification": cls.classification,
                              "verified": verified, "trim_info": trim_info})
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
                    "fallback_used": False}
        if stop_retrying:
            # ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part A: Cascadeが尽きて
            # 「これ以上retryしても解決しない」と判定した場合、TTSを再生成
            # せずここで打ち切る(英語側generate_english_segment_with_
            # fallback()と同じ契約)。従来はこの分岐がなく、attempt+1へ
            # 進んで無駄なTTS再生成を繰り返していた(bug)。
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                    "trim_info": trim_info, "fallback_used": False,
                    "reason": f"ASR Cascadeを尽くしても解決せず、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification})"}

    fallback_attempts = []
    fallback_budget = max(0, max_attempts - len(attempts_log))
    for attempt in range(1, fallback_budget + 1):
        r = generate_charon_japanese_minimal_instruction(text, out_path)
        if r.get("status") != "OK":
            fallback_attempts.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err2 = routing.transcribe(out_path, language="ja-JP")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
            text, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI)
        verified = verified_content and length_ok
        fallback_attempts.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                                   "length_ok": length_ok, "audio_classification": cls.classification,
                                   "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = attempts_log
            r["fallback_attempts_log"] = fallback_attempts
            return r
        if stop_retrying:
            r["status"] = "ASR_VALIDATION_UNCERTAIN"
            r["asr_verified"] = False
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = attempts_log
            r["fallback_attempts_log"] = fallback_attempts
            r["reason"] = (f"ASR Cascadeを尽くしても解決せず、retryでの改善が見込めないため打ち切り"
                           f"(最終classification={cls.classification})")
            return r
    return {"status": "STOPPED",
            "reason": f"標準経路{len(attempts_log)}回+fallback経路{len(fallback_attempts)}回"
                      f"(合計上限{max_attempts}回)とも不合格",
            "standard_attempts_log": attempts_log, "fallback_attempts_log": fallback_attempts}


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
