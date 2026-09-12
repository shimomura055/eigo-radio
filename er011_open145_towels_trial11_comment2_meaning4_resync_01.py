# ============================================================
# er011_open145_towels_trial11_comment2_meaning4_resync_01.py
# OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01
# ============================================================
# タスク項目4: タオルTrial-11 A2 comment_2の既存6 take(wav+既存ASR
# 書き起こし、offline再判定、新規ASR呼び出しなし・¥0)を、配線後の
# Production Validator(er007_ja_asr_validator_01.classify_ja_asr_match、
# Candidate B/C/D-1/D-2配線済み)で再判定する。TTS再生成は一切行わない。
#
# 既存採用規則: 現在narration/comment_2.wavとして実際に存在するファイル
# (=attempt6、既存採用済みの最終takeそのもの)が再判定でPASSすれば、
# そのファイルをそのまま採用する(新しいtakeへの差し替えは行わない)。
#
# あわせて、meaning_4(Key Phrase 4 japanese_meaning)がreview_lock_state.
# jsonでは既にRESOLVED/OK(attempt4、EXACT_MATCH、旧pykakasi判定のみで
# 解決済み、Variant Layerは無関係)なのに、tts_generation_results.json
# 側だけが古いSTOPPED状態のまま同期されていなかった(pre-existing sync
# gap、本タスクのVariant Layerとは無関係な既存の記録漏れ)。ユーザー
# タスク指示「meaning_4分も同時」に従い、review_lock_state.jsonの実際の
# 解決済みattemptを正としてtts_generation_results.json側を同期する
# (TTS再生成なし、新規ASR呼び出しなし、¥0)。
#
# バックアップ: 両JSONファイルを変更前に同ディレクトリへtimestamp付きで
# 保存する。
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import wave

import er007_ja_asr_validator_01 as javal

AUDIT_DIR = "er011_output/discovery_generalization_towels_trial_11/a2/audit"
NARRATION_DIR = "er011_output/discovery_generalization_towels_trial_11/a2/narration"
REVIEW_LOCK_PATH = f"{AUDIT_DIR}/review_lock_state.json"
TTS_RESULTS_PATH = f"{AUDIT_DIR}/tts_generation_results.json"
RESULT_DIR = "er011_output/open145_ja_asr_variant_production_wiring_01"

TS = time.strftime("%Y%m%d_%H%M%S")


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def wav_duration_seconds(path: str) -> float:
    with wave.open(path, "rb") as w:
        return round(w.getnframes() / w.getframerate(), 3)


def backup(path: str) -> str:
    backup_path = f"{path}.backup_before_open145_resync_{TS}.json"
    shutil.copy2(path, backup_path)
    return backup_path


def main():
    os.makedirs(RESULT_DIR, exist_ok=True)

    review_lock = json.load(open(REVIEW_LOCK_PATH, encoding="utf-8"))
    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))

    backups = {"review_lock_state.json": backup(REVIEW_LOCK_PATH),
               "tts_generation_results.json": backup(TTS_RESULTS_PATH)}

    evidence = {"backups": backups, "comment_2": {}, "meaning_4": {}}

    # ------------------------------------------------------------
    # comment_2: 既存6 takeを配線後Production Validatorで再判定する
    # ------------------------------------------------------------
    seg = tts_results["segments"]["comment_2"]
    canonical_text = seg["canonical_text"]

    takes = []
    for entry in seg["standard_attempts_log"]:
        takes.append({"attempt_audio_path": entry["attempt_audio_path"], "asr_text": entry["asr_text"],
                      "source": "standard_attempts_log"})
    for entry in seg["fallback_attempts_log"]:
        takes.append({"attempt_audio_path": entry["attempt_audio_path"], "asr_text": entry["asr_text"],
                      "source": "fallback_attempts_log"})
    # review_lock_state.last_attempts_logは2回目resumeの標準経路2回分
    # (attempt_audio_path=attempt4/attempt5)。attempt6(minimal fallback)
    # はnarration/attemptsディレクトリの実ファイルから直接読む(この
    # resumeサイクルの記録がtts_generation_results.json側に未反映
    # だったため)。
    for entry in review_lock["comment_2"]["last_attempts_log"]:
        takes.append({"attempt_audio_path": entry["attempt_audio_path"], "asr_text": entry["asr_text"],
                      "source": "review_lock_state.last_attempts_log"})
    attempt6_json_path = f"{NARRATION_DIR}/attempts/comment_2_attempt6_minimalfallback.json"
    attempt6 = json.load(open(attempt6_json_path, encoding="utf-8"))
    takes.append({"attempt_audio_path": f"{NARRATION_DIR}/attempts/comment_2_attempt6_minimalfallback.wav",
                  "asr_text": attempt6["asr_text"], "source": "narration/attempts (attempt6 json, "
                  "tts_generation_results.json未反映分)"})

    main_wav_path = f"{NARRATION_DIR}/comment_2.wav"
    main_sha256 = sha256_of(main_wav_path)

    reclassified_takes = []
    adopted = None
    for t in takes:
        result = javal.classify_ja_asr_match(canonical_text, t["asr_text"])
        take_sha256 = sha256_of(t["attempt_audio_path"]) if os.path.exists(t["attempt_audio_path"]) else None
        entry = {**t, "sha256": take_sha256, "is_current_main_wav": (take_sha256 == main_sha256),
                  "classification": result.classification, "should_pass": result.should_pass,
                  "reason": result.reason}
        reclassified_takes.append(entry)
        if entry["is_current_main_wav"]:
            adopted = entry

    evidence["comment_2"]["canonical_text"] = canonical_text
    evidence["comment_2"]["reclassified_takes"] = reclassified_takes
    evidence["comment_2"]["main_wav_sha256"] = main_sha256
    evidence["comment_2"]["adopted_take"] = adopted

    if adopted is None or not adopted["should_pass"]:
        print("[comment_2] 現在採用済みのnarration/comment_2.wav(主ファイル)が"
              "配線後の再判定でもPASSしなかった。既存採用規則に従い、状態は変更しない(STOPPEDのまま)。")
    else:
        print(f"[comment_2] 現在採用済みのnarration/comment_2.wav(主ファイル、{adopted['source']}由来)が"
              f"配線後の再判定でPASS({adopted['classification']})。既存採用規則に従いこのファイルのまま採用、"
              f"状態をRESOLVED/OKへ更新する(TTS再生成なし)。")

        duration = wav_duration_seconds(main_wav_path)
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        prior_review_lock_last_attempts_log = review_lock["comment_2"]["last_attempts_log"]

        # --- review_lock_state.json: HUMAN_REVIEW_REQUIRED -> RESOLVED ---
        review_lock["comment_2"] = {
            **review_lock["comment_2"],
            "state": "RESOLVED",
            "updated_at": now,
            "reason": (f"OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01配線後、"
                       f"既存採用済み音声(現在のnarration/comment_2.wav、旧attempt6由来)をProduction"
                       f"Validator(er007_ja_asr_validator_01.classify_ja_asr_match、Candidate B配線済み)"
                       f"でoffline再判定した結果PASS({adopted['classification']})。TTS再生成・新規ASR"
                       f"呼び出しは行っていない(既存ASR書き起こしの再判定のみ)。"),
            "final_status": "OK",
        }

        # --- tts_generation_results.json: segments.comment_2 STOPPED -> OK ---
        tts_results["segments"]["comment_2"] = {
            "status": "OK",
            "text": canonical_text,
            "language": "ja",
            "path": main_wav_path,
            "model": attempt6.get("model"),
            "voice": attempt6.get("voice"),
            "sha256": main_sha256,
            "duration_seconds": duration,
            "asr_verified": True,
            "asr_text": adopted["asr_text"],
            "audio_classification": adopted["classification"],
            "reading_resolver_info": None,
            "disfluency_checked": False,
            "disfluency_evidence": None,
            "repetition_qa_checked": False,
            "repetition_qa_evidence": None,
            "fallback_used": True,
            "canonical_text": canonical_text,
            "tts_input_text_after_reading_safety": seg.get("tts_input_text_after_reading_safety"),
            "reading_safety_changed_text": seg.get("reading_safety_changed_text"),
            # 過去6 takeの履歴を保全する(旧schemaのstandard_attempts_log/
            # fallback_attempts_logをそのまま残し、透明性のため今回の
            # 再判定結果も別フィールドで追記する。単一attemptのOK schemaへ
            # 無理に丸めず、再判定という事実を明示する)。
            "standard_attempts_log": seg["standard_attempts_log"],
            "fallback_attempts_log": seg["fallback_attempts_log"],
            "resumed_attempts_log_from_review_lock_state": prior_review_lock_last_attempts_log,
            "open145_reclassification": {
                "reclassified_at": now,
                "reclassified_by": "OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01",
                "method": "offline re-judgment of existing ASR transcripts via wired "
                          "er007_ja_asr_validator_01.classify_ja_asr_match() (Candidate B/C/D-1/D-2 wired), "
                          "no new TTS/ASR calls",
                "all_takes_reclassified": reclassified_takes,
                "adopted_take_source": adopted["source"],
            },
        }
        print(f"[comment_2] duration_seconds={duration}, sha256={main_sha256}")

    # ------------------------------------------------------------
    # meaning_4: pre-existing sync gap(review_lock_state.jsonは既にOK/
    # RESOLVED、tts_generation_results.jsonのkey_phrases["4"].
    # japanese_meaningだけが古いSTOPPEDのまま)を同期する。
    # 注意: これはVariant Layerの再判定とは無関係(元々旧pykakasi判定の
    # EXACT_MATCHで解決済み)。純粋な記録同期。
    # ------------------------------------------------------------
    mj = tts_results["key_phrases"]["4"]["japanese_meaning"]
    rl4 = review_lock["meaning_4"]
    if rl4["state"] == "RESOLVED" and mj.get("status") != "OK":
        resolved_attempt = rl4["last_attempts_log"][0]
        main_wav_path4 = f"{NARRATION_DIR}/meaning_4.wav"
        main_sha256_4 = sha256_of(main_wav_path4)
        duration4 = wav_duration_seconds(main_wav_path4)
        attempt4_json = json.load(open(
            f"{NARRATION_DIR}/attempts/meaning_4_attempt4_standard.json", encoding="utf-8"))

        evidence["meaning_4"]["pre_sync_status"] = mj.get("status")
        evidence["meaning_4"]["review_lock_resolved_attempt"] = resolved_attempt
        evidence["meaning_4"]["main_wav_sha256"] = main_sha256_4

        tts_results["key_phrases"]["4"]["japanese_meaning"] = {
            "status": "OK",
            "text": mj.get("canonical_text"),
            "language": "ja",
            "path": main_wav_path4,
            "model": attempt4_json.get("model"),
            "voice": attempt4_json.get("voice"),
            "sha256": main_sha256_4,
            "duration_seconds": duration4,
            "asr_verified": True,
            "asr_text": resolved_attempt["asr_text"],
            "audio_classification": resolved_attempt["audio_classification"],
            "reading_resolver_info": None,
            "disfluency_checked": False,
            "disfluency_evidence": None,
            "repetition_qa_checked": False,
            "repetition_qa_evidence": None,
            "fallback_used": False,
            "canonical_text": mj.get("canonical_text"),
            "tts_input_text_after_reading_safety": mj.get("tts_input_text_after_reading_safety"),
            "reading_safety_changed_text": mj.get("reading_safety_changed_text"),
            "display_gloss": mj.get("display_gloss"),
            "japanese_gloss_tts_fallback_derived": mj.get("japanese_gloss_tts_fallback_derived"),
            "standard_attempts_log": mj.get("standard_attempts_log"),
            "fallback_attempts_log": mj.get("fallback_attempts_log"),
            "open145_resync_note": (
                "pre-existing sync gap(OPEN-145のVariant Layerとは無関係、旧pykakasi判定のEXACT_MATCH"
                "で元々解決済み): review_lock_state.jsonでは既にRESOLVED/OK(attempt4)だったが、"
                "tts_generation_results.json側のkey_phrases['4'].japanese_meaningだけがSTOPPEDのまま"
                "未同期だった。review_lock_state.jsonの実際の解決済みattemptを正として同期した。"
                "TTS再生成・新規ASR呼び出しは行っていない。"),
        }
        print(f"[meaning_4] pre-existing sync gap検出、review_lock_state.json(RESOLVED/OK)を正として同期した。"
              f"duration_seconds={duration4}, sha256={main_sha256_4}")
    else:
        print(f"[meaning_4] 同期不要(review_lock_state.state={rl4['state']}, "
              f"tts_generation_results.status={mj.get('status')})")

    with open(REVIEW_LOCK_PATH, "w", encoding="utf-8") as f:
        json.dump(review_lock, f, ensure_ascii=False, indent=2)
    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2)

    with open(f"{RESULT_DIR}/comment2_meaning4_resync_evidence.json", "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)

    print(f"\nbackups: {backups}")
    print(f"evidence saved: {RESULT_DIR}/comment2_meaning4_resync_evidence.json")


if __name__ == "__main__":
    main()
