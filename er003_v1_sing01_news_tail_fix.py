# ============================================================
# er003_v1_sing01_news_tail_fix.py
# ER-003-B1-NOVEL-AUDIO-01: News本文(ENGLISH_STYLE_PREFIX経路)の
# tail安全マージン修正・再生成
# ============================================================
# QA中に、point_one(および軽微にfull_story_part1)の末尾10ms RMSが
# 他segmentより明確に高い(=末尾が自然に減衰しきる前に終わっている)
# ことを発見した。原因を追跡した結果、p9a.generate_narration_snippet
# (ENGLISH_STYLE_PREFIX経路、Full Story/Point/In One Line生成の主経路)
# 内部でp3u.trim_english_keyword_silenceが既定の安全マージン0.08秒
# (Key Phrase単語向け)のまま呼ばれており、AUDIO-03で発見・修正した
# Preview"prove"語尾切れと同一クラスのバグが、当時は対象にしなかった
# 別のコードパス(ENGLISH_STYLE_PREFIX経路)にも存在していたことが
# 判明した。p9a.generate_narration_snippet自体(Production隣接の
# 既存共有関数)は変更せず、この生成スクリプト側でTTS呼び出しと
# trimを直接組み立て、安全マージンのみ0.35秒(AUDIO-03と同じ値)へ
# 広げる。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_news_tail_fix.py

from __future__ import annotations

import json

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_audio_tts_asr_safety as safety
import er003_v1_repro01_main_generate as repro01
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er006_preprod_hardening_01_validation as audio_validation
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er011_human_review_lock_01 as review_lock

OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"
LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS = 0.35


# ER-010-ENTITY-PHONETIC-CORROBORATION-01: 固有名詞由来のASR_VALIDATION_
# UNCERTAINが、retryを重ねても解消しないまま(No.5 pool_n5_cafes B1
# full_story_part1で実際に発生)Human Reviewへ滞留するのを緩和する。
# この集約関数自体は新規TTS/ASR呼び出しを行わない(このループ内で既に
# 得られた各attemptのasr_textをローカルで再分類・集約するだけ)。ただし
# 呼び出し側(下記ループ)は、集約結果がまだ「複数の異なる誤認識」という
# 裏付けを得られていない場合、既存のmax_attempts上限内で追加のTTS
# attemptを試みることがある(既存の他の失敗理由と同じコスト上限のまま)。
def _try_entity_phonetic_corroboration(text: str, attempts_log: list) -> dict:
    asr_texts = [a["asr_text"] for a in attempts_log if a.get("asr_text")]
    return audio_validation.aggregate_entity_only_phonetic_corroboration(text, asr_texts)


@review_lock.guarded_generate("en")
def generate_news_narration_wide_margin(text: str, out_path: str, max_attempts: int = 6,
                                         max_extra_chars: int = 15) -> dict:
    """p9a.generate_narration_snippet(ENGLISH_STYLE_PREFIX経路)と同じ
    prompt/model/voiceを使うが、末尾trim安全マージンのみ0.35秒に広げる。
    失敗時はMINIMAL_INSTRUCTION経路(同じく広いマージン)へfallbackする。"""
    max_len = len(text) + max_extra_chars
    attempts_log = []
    classification_history = []
    for attempt in range(1, max_attempts + 1):
        # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線(声・モデルは
        # p9a._make_english_call_fn()と同一)。
        call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, p9a.VOICE_NAME, output_path=out_path)
        prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        instruction_type = "english_style_prefix_wide_margin"
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE, safety_margin_seconds=LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS)
            # ER-005-AUDIO-WASTE-REDUCTION-01: hallucinationを疑わせる
            # 異常長音声を、ASR実行前に検知して破棄する。
            if trimmed is not None:
                anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
                if anomaly["is_anomaly"]:
                    trimmed = None
                    err = anomaly["reason"]
        else:
            trimmed, trim_info = None, None

        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err) if not ok else "発話区間検出失敗",
                                  "instruction_type": instruction_type})
            r = repro01.generate_english_component_minimal_instruction(text, out_path)
            instruction_type = "minimal_fallback"
            if r.get("status") != "OK":
                attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                      "instruction_type": instruction_type})
                continue
        else:
            common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)

        asr_text, asr_err = routing.transcribe(out_path, language="en-US")
        # ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: safety.validate_asr_match
        # から正規化+6分類+Protected Check+retry guardrail方式へ切り替え。
        length_ok = asr_text is not None and len(asr_text) <= max_len
        ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
        verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
            text, asr_text, classification_history, out_path, language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
        verified = verified_content and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "audio_classification": cls.classification,
                              "length_ok": length_ok, "verified": verified,
                              "trim_info": trim_info})
        if verified:
            metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "asr_verified": True, "asr_text": asr_text,
                    "attempts_log": attempts_log, "instruction_type": instruction_type,
                    "trim_info": trim_info, "safety_margin_seconds": LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                    "clipping_detected": metrics["clipping_detected"]}
        if stop_retrying:
            corroboration = _try_entity_phonetic_corroboration(text, attempts_log)
            if corroboration["accept"]:
                metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
                return {"status": "OK", "text": text, "path": out_path, "asr_verified": False, "asr_text": asr_text,
                        "attempts_log": attempts_log, "instruction_type": instruction_type,
                        "trim_info": trim_info, "safety_margin_seconds": LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                        "clipping_detected": metrics["clipping_detected"],
                        "classification": audio_validation.ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED,
                        "phonetic_corroboration": corroboration,
                        "reason": "固有名詞らしき語の音訳差のみで、複数の独立したTTS takeを軽量な音韻類似度"
                                  "チェックで集約評価した結果、同一固有名詞の表記揺れと判定し自動採用した"
                                  "(ER-010-ENTITY-PHONETIC-CORROBORATION-01)"}
            # ER-010-ENTITY-PHONETIC-CORROBORATION-01: 固有名詞由来のASR_
            # VALIDATION_UNCERTAIN(is_entity_like_mismatch)は、複数の独立
            # したTTS takeが揃わないと音韻類似度チェックが判断材料不足のまま
            # (No.5 full_story_part1で実際に発生: 1回目のtakeだけでは
            # 「異なる誤認識が複数回観測された」という多様性の裏付けが得られ
            # ない)。この場合に限り、まだ試行回数に余裕があればここで
            # 打ち切らずattemptを継続する(既存の「同一signatureが連続したら
            # 打ち切る」という他の打ち切り理由には一切影響しない、Cost上限は
            # 既存のmax_attempts=6のまま変わらない)。
            entity_only = secondary_asr.is_entity_like_mismatch(cls)
            if entity_only and attempt < max_attempts:
                continue
            metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "asr_verified": False,
                    "asr_text": asr_text, "attempts_log": attempts_log, "instruction_type": instruction_type,
                    "trim_info": trim_info, "safety_margin_seconds": LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                    "clipping_detected": metrics["clipping_detected"],
                    "phonetic_corroboration": corroboration,
                    "reason": f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification}、音韻類似度チェックも不採用: "
                              f"{corroboration['reason']})"}
    corroboration = _try_entity_phonetic_corroboration(text, attempts_log)
    if corroboration["accept"]:
        metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
        return {"status": "OK", "text": text, "path": out_path, "asr_verified": False,
                "attempts_log": attempts_log, "trim_info": attempts_log[-1].get("trim_info") if attempts_log else None,
                "safety_margin_seconds": LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                "clipping_detected": metrics["clipping_detected"],
                "classification": audio_validation.ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED,
                "phonetic_corroboration": corroboration,
                "reason": "固有名詞らしき語の音訳差のみで、複数の独立したTTS takeを軽量な音韻類似度チェックで"
                          "集約評価した結果、同一固有名詞の表記揺れと判定し自動採用した"
                          "(ER-010-ENTITY-PHONETIC-CORROBORATION-01)"}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log, "phonetic_corroboration": corroboration}


def tail_rms(path: str, ms: int = 10) -> float:
    import numpy as np
    samples, sr, _, _ = common.read_wav_float(path)
    tail = samples[-int(sr * ms / 1000):]
    return float(np.sqrt(np.mean(tail.astype(np.float64) ** 2)))


def main():
    targets = {
        "point_one": ("Nobody quite agrees on what \"singularity\" even means. Part of the disagreement comes down "
                       "to definitions. Computer scientist Stuart Russell says AI hasn't reached that threshold "
                       "yet. Researcher Roman Yampolskiy argues fast progress alone isn't the singularity. "
                       "Philosopher Nick Bostrom points to a missing piece: today's models mostly stop learning "
                       "once they're released, instead of continuing to grow on their own."),
        "full_story_part1": ("In a podcast released in July, OpenAI's Sam Altman said, \"We're now, like, in the "
                              "singularity.\" It echoed something he had written the year before: \"We are past "
                              "the event horizon; the takeoff has started.\" Elon Musk has made a related but "
                              "different claim, posting in January that 2026, this year, will be the year the "
                              "singularity arrives. So what does the evidence actually show?"),
    }
    results = {}
    for name, text in targets.items():
        before = tail_rms(f"{NARRATION_DIR}/{name}.wav")
        print(f"[TAIL-FIX] {name}: before tail_10ms_rms={before:.5f}")
        out_path = f"{NARRATION_DIR}/{name}.wav"
        r = generate_news_narration_wide_margin(text, out_path)
        results[name] = r
        if r.get("status") == "OK":
            after = tail_rms(out_path)
            r["tail_10ms_rms_before"] = round(before, 5)
            r["tail_10ms_rms_after"] = round(after, 5)
            print(f"[TAIL-FIX] {name}: status=OK after tail_10ms_rms={after:.5f}")
        else:
            print(f"[TAIL-FIX] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/news_tail_fix_result.json", "w", encoding="utf-8") as f:
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
