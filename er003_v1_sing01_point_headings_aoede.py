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
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er006_preprod_hardening_01_validation as audio_validation
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er008_disfluency_qa_18 as dq18
import er011_human_review_lock_01 as review_lock

AOEDE = "Aoede"
SAFETY_MARGIN = 0.35
OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"


@review_lock.guarded_generate("en")
def generate(text: str, out_path: str, max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
             # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: Point見出しはPRODUCTION
             # 承認済みのdisfluency QA対象segmentのため既定True。
             disfluency_qa: bool = True) -> dict:
    max_len = len(text) + 15
    attempts_log = []
    classification_history = []
    # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B: 旧max_attempts=8
    # 時代は「前半4回=標準prompt、後半4回=minimal instruction」という
    # 固定分割だった。max_attempts=3では同じ固定しきい値(>4)だと
    # minimal instructionへ一度も切り替わらなくなるため、総試行回数の
    # 半分(端数切り上げ、最低1回は標準を試す)を基準に比率を維持する。
    minimal_after = max(1, max_attempts // 2)
    for attempt in range(1, max_attempts + 1):
        use_minimal = attempt > minimal_after
        # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
        # (声・モデルはgclient.make_tts_call_fn(AOEDE)と同一)。
        call_fn = batch_wiring.make_batch_tts_call_fn(common.MODEL_NAME, AOEDE, output_path=out_path)
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
        asr_text, asr_err = routing.transcribe(out_path, language="en-US")
        # ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: 正規化+6分類+
        # Protected Check+retry guardrail方式へ切り替え。
        length_ok = asr_text is not None and len(asr_text) <= max_len
        ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
        verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
            text, asr_text, classification_history, out_path, language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
        verified = verified_content and length_ok
        gate = dq18.apply_disfluency_gate(verified, out_path, language="en", enabled=disfluency_qa)
        verified = gate["verified"]
        attempts_log.append({"attempt": attempt, "asr_text": asr_text, "audio_classification": cls.classification,
                              "length_ok": length_ok, "verified": verified, "instruction_type": instruction_type,
                              "disfluency_checked": gate["disfluency_checked"],
                              "disfluency_evidence": gate.get("disfluency_evidence")})
        print(f"    attempt {attempt} ({instruction_type}): asr={asr_text!r} classification={cls.classification} length_ok={length_ok}")
        if verified:
            return {"status": "OK", "text": text, "path": out_path, "voice": AOEDE, "asr_verified": True,
                    "asr_text": asr_text, "attempts_log": attempts_log, "instruction_type": instruction_type,
                    "max_len": max_len}
        if stop_retrying:
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": AOEDE,
                    "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "max_len": max_len,
                    "reason": f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification})"}
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
