# ============================================================
# er010_no9_a2_attempt4_oneoff_final_audio_25.py
# ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25
# ============================================================
# ユーザー正式決定: Trial 21(ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-
# TRIAL-21)のENGLISH_LOCK attempt=2(通し4回目のTTS呼び出し=「Attempt 4」)
# を、No.9 A2 kp2("default")限定のone-off固定assetとして正式採用する。
#
# 重要: Trial 21自身の記録(trial21_results.json)では、この音声は
# machine validator上 audio_classification="TTS_FAILURE"(ASRテキスト
# "デフォルト"=日本語カタカナ表記)としてFAILしている。ユーザーが実際に
# 試聴した上でNo.9 A2限定で採用を決定したため、本モジュールは
# 「machine FAIL / human-approved one-off override」として扱う。
#   - 元のmachine判定(trial21_results.json内のstatus/classification、
#     tts_generation_results.jsonのstatus/locked_entry/attempts_log)は
#     一切書き換えない。
#   - 承認はこのプロジェクトで既に確立している
#     er003_v1_n3_01_assemble.record_human_approval()の仕組み
#     (human_approved_segments.json)を使う。これはHUMAN_REVIEW_LOCKED/
#     STOPPEDのsegmentをEpisode Assembly Gateへ通すための、Production
#     が既に持つ正式な人間承認記録メカニズムであり、今回新設するもの
#     ではない。
#
# 一般Production仕様(Key Phrase英語TTS retry構成、Validator閾値等)は
# 一切変更しない。No.9 A2のkp2_en.wav 1ファイルのみを対象とした
# one-off差し替え。

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time

import er002_common as common
import er003_v1_n3_01_assemble as asm
import er006_asr_provider_routing_01 as routing
import er008_disfluency_qa_18 as dq18

THEME_ID = "pool_n9_tip_screens"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
A2_DIR = f"{OUT_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
AUDIT_DIR = f"{A2_DIR}/audit"

TRIAL21_RESULTS_PATH = "er010_output/no9_keyphrase_english_lock_fallback_trial_21/trial21_results.json"
ATTEMPT4_SOURCE_PATH = "er010_output/no9_keyphrase_english_lock_fallback_trial_21/audio/default_englishlock_attempt2.wav"
ATTEMPT4_EXPECTED_SHA256 = "5cfeaaa4133ea9c7996b547c3a1558012838259b565d8d1ec9310c3aeaea05f0"

KP2_EN_PATH = f"{NARRATION_DIR}/kp2_en.wav"
KP2_EN_MISLABELED_BACKUP_PATH = f"{NARRATION_DIR}/kp2_en_pre_oneoff_mislabeled_backup.wav"

TTS_RESULTS_PATH = f"{AUDIT_DIR}/tts_generation_results.json"
HUMAN_APPROVAL_PATH = asm.human_approval_path(A2_DIR)

MANAGEMENT_ID = "ER-010-NO9-A2-ATTEMPT4-ONEOFF-FINAL-AUDIO-25"

OUT_RESULT_DIR = "er010_output/no9_a2_attempt4_oneoff_final_audio_25"


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def step1_verify_attempt4_lineage() -> dict:
    """Trial 21自身のresults.jsonから「Attempt 4」に相当するattemptを
    特定し、実ファイルのsha256と一致するか、Trial 21レポート
    (DECISION_LOG記載)の内容と一致するかを確認する。不一致ならSTOP。"""
    with open(TRIAL21_RESULTS_PATH, "r", encoding="utf-8") as f:
        trial21 = json.load(f)

    attempts = trial21["attempts"]
    if len(attempts) != 4:
        raise RuntimeError(f"LINEAGE_CHECK_FAILED: Trial 21のattempt数が4ではありません({len(attempts)})")

    # 通し番号4回目 = attempts[3]。仕様上、これがENGLISH_LOCKのattempt=2で
    # あることを確認する(ユーザー指示の「English Lock attempt 2に相当」)。
    attempt4 = attempts[3]
    if not (attempt4["attempt_type"] == "ENGLISH_LOCK" and attempt4["attempt"] == 2):
        raise RuntimeError(
            f"LINEAGE_CHECK_FAILED: 通し4回目のattemptがENGLISH_LOCK attempt=2ではありません"
            f"(実際: {attempt4['attempt_type']} attempt={attempt4['attempt']})")

    recorded_path = attempt4["audio_path"]
    recorded_sha256 = attempt4["sha256"]
    if recorded_path != ATTEMPT4_SOURCE_PATH:
        raise RuntimeError(
            f"LINEAGE_CHECK_FAILED: audio_pathが想定と異なります(記録: {recorded_path})")
    if recorded_sha256 != ATTEMPT4_EXPECTED_SHA256:
        raise RuntimeError(
            f"LINEAGE_CHECK_FAILED: trial21_results.json記載のsha256が想定と異なります")
    if not os.path.exists(ATTEMPT4_SOURCE_PATH):
        raise RuntimeError(f"LINEAGE_CHECK_FAILED: 実ファイルが存在しません: {ATTEMPT4_SOURCE_PATH}")

    actual_sha256 = _sha256(ATTEMPT4_SOURCE_PATH)
    if actual_sha256 != recorded_sha256:
        raise RuntimeError(
            f"LINEAGE_CHECK_FAILED: 実ファイルのsha256がtrial21_results.json記録と不一致"
            f"(記録={recorded_sha256}, 実際={actual_sha256})。ファイルが差し替わっている疑いがあり"
            "採用できません。")

    samples, sr, channels, _meta = common.read_wav_float(ATTEMPT4_SOURCE_PATH)
    duration = len(samples) / sr

    return {
        "management_id": MANAGEMENT_ID,
        "trial_management_id": "ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21",
        "attempt_index_overall": 4,
        "attempt_type": attempt4["attempt_type"],
        "attempt_number_within_type": attempt4["attempt"],
        "target_source_text": "default",
        "audio_path": ATTEMPT4_SOURCE_PATH,
        "sha256": actual_sha256,
        "sha256_matches_trial21_report": True,
        "model": "gemini-2.5-pro-preview-tts",
        "voice": "Aoede",
        "duration_seconds": round(duration, 4),
        "sample_rate": sr,
        "channels": channels,
        "trial21_machine_classification": attempt4["audio_classification"],
        "trial21_classification_reason": attempt4["classification_reason"],
        "trial21_asr_text": attempt4["asr_text"],
        "trial21_final_status_of_whole_trial": trial21["final_status"],
        "instruction_full_text": attempt4["instruction_full_text"],
        "lineage_verified": True,
    }


def step2_run_real_disfluency_qa() -> dict:
    """Production Assembly Gate(_segment_missing_mandatory_disfluency_qa)
    が"_english"で終わるsegmentすべてに要求しているdisfluency QAを、
    実際にこのAttempt 4音声に対して実行する(ローカルfaster-whisper、
    追加API課金なし)。verified=Trueを前提に実施(machine validatorの
    TTS_FAILURE判定は覆さないが、disfluency自体の有無は別軸のQAとして
    実測する)。"""
    gate = dq18.apply_disfluency_gate(True, ATTEMPT4_SOURCE_PATH, language="en", enabled=True)
    return gate


def step3_reverify_asr_before_adoption() -> dict:
    """採用直前に、Production ASR(実API、単体の少額課金)でも再確認する。
    Trial 21実行時点との差分がないか(古い音声ファイルの破損等がないか)
    の最終チェック。"""
    asr_text, err = routing.transcribe(ATTEMPT4_SOURCE_PATH, language="en-US")
    return {"asr_text": asr_text, "asr_error": err}


def step4_splice_asset(disfluency_evidence: dict) -> dict:
    """kp2_en.wavをAttempt 4音声に差し替える。旧ファイル(実際は
    "Guilt tipping"の取り違えファイルだったことがWIRING-23-R1で判明済み)
    はbackupとして残す(削除しない)。"""
    os.makedirs(NARRATION_DIR, exist_ok=True)
    old_existed = os.path.exists(KP2_EN_PATH)
    old_sha256 = _sha256(KP2_EN_PATH) if old_existed else None
    if old_existed and not os.path.exists(KP2_EN_MISLABELED_BACKUP_PATH):
        shutil.copyfile(KP2_EN_PATH, KP2_EN_MISLABELED_BACKUP_PATH)
    shutil.copyfile(ATTEMPT4_SOURCE_PATH, KP2_EN_PATH)
    new_sha256 = _sha256(KP2_EN_PATH)
    return {
        "old_kp2_en_existed": old_existed,
        "old_kp2_en_sha256": old_sha256,
        "old_kp2_en_backup_path": KP2_EN_MISLABELED_BACKUP_PATH if old_existed else None,
        "new_kp2_en_sha256": new_sha256,
        "new_kp2_en_sha256_matches_attempt4": new_sha256 == ATTEMPT4_EXPECTED_SHA256,
    }


def step5_update_audit_records(lineage: dict, disfluency_evidence: dict, reverify: dict) -> dict:
    """tts_generation_results.jsonのkp2/english entryへ、one-off override
    のevidenceを追記する(status/locked_entry/attempts_logは一切変更
    しない=元のmachine FAIL判定を保持)。human_approved_segments.jsonへ
    Production Assembly Gateが要求する形式で承認を記録する
    (record_human_approval()、このプロジェクトの既存メカニズム)。"""
    with open(TTS_RESULTS_PATH, "r", encoding="utf-8") as f:
        tts_results = json.load(f)

    kp2_english = tts_results["key_phrases"]["2"]["english"]
    kp2_english["disfluency_checked"] = disfluency_evidence["disfluency_checked"]
    kp2_english["disfluency_evidence"] = disfluency_evidence["disfluency_evidence"]
    kp2_english["one_off_fixed_asset_override"] = {
        "management_id": MANAGEMENT_ID,
        "applied_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "override_type": "MACHINE_FAIL_HUMAN_APPROVED_ONEOFF",
        "note": ("元のstatus(HUMAN_REVIEW_LOCKED)・locked_entry・attempts_logは"
                 "Trial 19/Mini-Trial 20-R2/本番3回のいずれも失敗だった正確な履歴として"
                 "そのまま保持する。本フィールドのみ追記。"
                 "採用音声はTrial 21(ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21)"
                 "のENGLISH_LOCK attempt=2(通しAttempt 4)。"
                 "Trial 21内でもmachine validator上はTTS_FAILURE(ASR=\"デフォルト\"、"
                 "日本語カタカナ表記)だったが、ユーザーが実際に試聴の上でNo.9 A2 "
                 "kp2(\"default\")限定のone-off固定assetとして正式採用した。"),
        "source_trial_management_id": "ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21",
        "source_audio_path": ATTEMPT4_SOURCE_PATH,
        "source_sha256": lineage["sha256"],
        "adopted_kp2_en_sha256": _sha256(KP2_EN_PATH),
        "trial21_machine_classification": lineage["trial21_machine_classification"],
        "trial21_asr_text": lineage["trial21_asr_text"],
        "reverification_asr_text_before_adoption": reverify["asr_text"],
        "model": lineage["model"], "voice": lineage["voice"],
        "duration_seconds": lineage["duration_seconds"],
    }
    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    # Production Assembly Gateの既存メカニズムで承認を記録する。
    # kp2の"english"sub-entryは(既存の他key phraseと同様)canonical_text/
    # textフィールドを持たないため、_segment_gate_status()が計算する
    # canonは""になる(このプロジェクトの既存仕様であり、今回新たに
    # 発生させたものではない)。
    asm.record_human_approval(A2_DIR, "kp2_english", "",
                               approved_by=f"user_2026-09-01_{MANAGEMENT_ID}")

    # 承認記録に追加のcontextを追記(record_human_approval()の標準
    # フィールドに加えて、監査用の説明を追加する。ゲート判定は
    # canonical_text_sha256のみを見るため、これらの追加フィールドは
    # ゲート挙動に影響しない)。
    with open(HUMAN_APPROVAL_PATH, "r", encoding="utf-8") as f:
        approvals = json.load(f)
    approvals["kp2_english"]["management_id"] = MANAGEMENT_ID
    approvals["kp2_english"]["override_type"] = "MACHINE_FAIL_HUMAN_APPROVED_ONEOFF"
    approvals["kp2_english"]["note"] = (
        "Trial 21 ENGLISH_LOCK attempt=2(通しAttempt 4)をNo.9 A2 kp2(\"default\")"
        "限定のone-off固定assetとして正式採用。machine validator上はTTS_FAILURE。")
    approvals["kp2_english"]["source_audio_path"] = ATTEMPT4_SOURCE_PATH
    approvals["kp2_english"]["source_sha256"] = lineage["sha256"]
    with open(HUMAN_APPROVAL_PATH, "w", encoding="utf-8") as f:
        json.dump(approvals, f, ensure_ascii=False, indent=2)

    return {"tts_results_updated": True, "human_approval_recorded": True}


def step6_assemble() -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    summary = asm.stage_assemble_a2(theme)
    return summary


def step7_verify_assembled(assemble_summary: dict) -> dict:
    """完成episodeのtimelineから、Key Phrase 2(default)のsegmentが
    1回だけ・想定位置に存在することを確認し、その区間を切り出して
    ASR再確認する。"""
    timeline_path = f"{A2_DIR}/audit/timeline.json"
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    kp2_entries = [t for t in timeline if t["part"] == "Key Phrase 2"]
    kp_labels = [t["part"] for t in timeline if t["part"].startswith("Key Phrase")]
    part_names = [t["part"] for t in timeline]
    duplicates = [p for p in set(part_names) if part_names.count(p) > 1
                  and not p.startswith("pause_") and p not in ("Notification 1", "Notification 2", "Notification 3",
                                                                 "Point Notification (Point One cue)",
                                                                 "Point Notification (Point Two cue)")]

    assembled_path = assemble_summary["out_path"]
    samples, sr, channels, _nframes = common.read_wav_float(assembled_path)
    # read_wav_float()はチャンネルをinterleaveしたままの1次元配列を返すため、
    # 多チャンネルの場合はここで(frames, channels)へreshapeする。
    if channels > 1:
        samples = samples.reshape(-1, channels)
    total_duration = len(samples) / sr

    result = {
        "assembled_path": assembled_path,
        "total_duration_seconds": round(total_duration, 3),
        "total_duration_from_summary": assemble_summary["duration_seconds"],
        "clipping_detected": assemble_summary["clipping_detected"],
        "sample_rate": assemble_summary["sample_rate"],
        "channels": assemble_summary["channels"],
        "kp_labels_present": kp_labels,
        "kp2_appears_exactly_once": len(kp2_entries) == 1,
        "kp2_timeline_entry": kp2_entries[0] if kp2_entries else None,
        "unexpected_duplicate_named_segments": duplicates,
        "segment_count": len(timeline),
    }

    if kp2_entries:
        entry = kp2_entries[0]
        start_idx = int(entry["start_seconds"] * sr)
        end_idx = int((entry["start_seconds"] + entry["duration_seconds"]) * sr)
        clip = samples[start_idx:end_idx, 0] if samples.ndim == 2 else samples[start_idx:end_idx]
        clip_path = f"{OUT_RESULT_DIR}/assembled_kp2_default_clip_check.wav"
        os.makedirs(OUT_RESULT_DIR, exist_ok=True)
        common.write_wav_float(clip_path, clip, sr, 1)
        asr_text, asr_err = routing.transcribe(clip_path, language="en-US")
        result["assembled_kp2_clip_check_path"] = clip_path
        result["assembled_kp2_clip_asr_text"] = asr_text
        result["assembled_kp2_clip_asr_error"] = asr_err

    return result


def run_all() -> dict:
    os.makedirs(OUT_RESULT_DIR, exist_ok=True)
    lineage = step1_verify_attempt4_lineage()
    disfluency = step2_run_real_disfluency_qa()
    reverify = step3_reverify_asr_before_adoption()
    splice = step4_splice_asset(disfluency)
    audit_update = step5_update_audit_records(lineage, disfluency, reverify)
    assemble_summary = step6_assemble()
    verify = step7_verify_assembled(assemble_summary)

    result = {
        "management_id": MANAGEMENT_ID,
        "lineage": lineage,
        "disfluency_qa": disfluency,
        "reverification_before_adoption": reverify,
        "splice": splice,
        "audit_update": audit_update,
        "assemble_summary": assemble_summary,
        "verify": verify,
    }
    with open(f"{OUT_RESULT_DIR}/final_audio_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


if __name__ == "__main__":
    run_all()
