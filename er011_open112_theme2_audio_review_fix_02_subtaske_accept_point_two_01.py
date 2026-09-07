# ============================================================
# er011_open112_theme2_audio_review_fix_02_subtaske_accept_point_two_01.py
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 サブタスクE
# ============================================================
# 背景: サブタスクDの診断で、A2 Point Two再生成2attempt(重複バグは
# 解消済み、`showed`(canonical)が`show`とASRされる不一致のみ残存)は
# 分類B(実音声は"showed"の可能性が高く、Primary ASRの連結・弱化に
# よる脱落)に最も整合すると報告した(確定[A]ではないためAgent自身は
# 判断せず、ユーザー試聴に委ねた)。
#
# ユーザー判断(2026-09-07): showed→show不一致は分類B確定(ユーザー
# 試聴で"showed"と聞こえる、Azure Secondary・faster-whisper local
# ローカルASRとも一致、Connected Speech下でのASR false rejectionと
# 分類、TTS誤発音とは扱わない)。重複が無く時制以外は正常な版を、
# 既存の人間承認メカニズム(record_human_approval())で正式にaccept
# することを承認。再生成は不要(新規TTS/ASR生成は行わない、既存音声
# のacceptのみ)。
#
# 本スクリプトが行うこと(既存Production関数を無変更のまま呼ぶだけ、
# 新しいValidator原則・判定ロジックの追加なし):
#   1. attempt1/attempt2のうち、FIX-02 §追補の診断raw evidence
#      (windowed Primary ASR・簡易音響分析)から、より"showed"の
#      音響手がかりが明瞭な方を選定(理由をログに記録)。
#   2. 選定したattempt音声を narration/point_two.wav へコピー(バック
#      アップ済みの旧・重複入りTrial-13音声は上書きするが、既存
#      pre_fix_buggy_audio_backup/に既にevidenceとして退避済み)。
#   3. tts_generation_results.json のsegments.point_twoを、実際に
#      起きたこと(2回のTTS生成、いずれもPrimary ASRでは内容不一致)を
#      正直に反映する形へ更新する(status="STOPPED"、fabricateしない)。
#   4. 既存API record_human_approval()(er003_v1_n3_01_assemble.py)を
#      呼び、audit/human_approved_segments.jsonへ承認記録を残す(手書き
#      JSON改変ではなく、既存メカニズム経由)。
#   5. 既存Production関数 stage_assemble_a2()(無変更)でepisodeを
#      再Assembly。
#   6. 検証専用ASR(Azure Secondary・faster-whisper local、既存診断
#      スクリプトと同じ関数を再利用、Production Cost Guard/retryとは
#      無関係)で、完成episode中のPoint Two区間の重複消失・内容を
#      再確認する(新規TTS呼び出しは一切無い)。
#
# 既知の限界(本スクリプトが独自に対処しないこと、レポートで開示):
#   - 選定したattempt音声は、標準ペース生成(generate_english_segment_
#     with_fallback)がstatus=="OK"に到達できなかったため、A2必須の
#     6% time-stretch後処理(apply_a2_slowdown_postprocess、TTS_STANDARD
#     の後段でASR再検証を伴う)を一度も通っていない(コード経路を確認
#     済み: generate_a2_segment_with_slowdown()は`result.get("status")
#     != "OK": break`でslowdown適用前に打ち切る)。既存Audio Validation
#     Gateの`_segment_missing_mandatory_a2_slowdown()`は、この narration_
#     dirに残る古い`point_two_original.wav`(Trial-13の重複入り原本、
#     本タスクでは無変更のまま)を「slowdown済みのevidence」として
#     誤って受理してしまう(既存の後方互換ロジックの意図しない抜け穴、
#     本スクリプトが作った穴ではない)。本スクリプトはこの抜け穴を
#     隠蔽せず、tts_generation_results.jsonへ`slowdown_applied: false`
#     と明示的な注記を残す。ペース差の是正(オフラインdsp再stretch等)
#     は、ユーザーが実際に試聴・承認した音声そのものを変えてしまう
#     ため本スクリプトの範囲外とし、USER_DECISION_REQUIREDとして
#     報告する(新規TTS/ASRなしのacceptという今回の指示範囲を超える)。
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er003_v1_n3_01_assemble as asm
import er005_cost_logger as cl
import er006_secondary_asr_01 as secondary_asr
import er008_disfluency_qa_18 as dq18
import er011_open121_tts_repetition_general_qa_trial_01 as open121

RERUN02_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_02"
A2_DIR = f"{RERUN02_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
ATTEMPTS_DIR = f"{NARRATION_DIR}/attempts"
AUDIT_DIR = f"{A2_DIR}/audit"
OUT_DIR = f"{RERUN02_DIR}/audit/subtask_e_point_two_accept"
THEME_ID = "open112_trend_theme2_b_final_audio_rerun_02"

CANONICAL_TEXT = (
    "Young travelers are not one single market. Women aged 29 and under still "
    "showed strong interest in famous tourist places, at about 45%. Gourmet travel "
    "was even higher, at about 52%. This is not the same picture as the male interest "
    "in solo and hobby-based trips. The useful lesson is not that sightseeing is ending. "
    "Different young travelers may be looking for different kinds of value from the same holiday."
)

# サブタスクDの診断raw evidence(er011_output/.../point_two_showed_show_diag/)
# から、attempt2をより音響的手がかりが明瞭な方として選定した根拠:
#  (a) windowed Primary ASR(中立prompt付き)は、他の全条件(全文/windowed
#      no-prompt)で一貫して"show"を返したPrimary ASRエンジン自身が、
#      唯一この条件でattempt2のみ"showed"を検知した(attempt1は同条件
#      でも"show"のまま)。
#  (b) 簡易音響分析(8msフレーム/2msホップRMS+高域比)で、目的語境界
#      付近の低エネルギー(closure候補)区間がattempt2で3件(attempt1は
#      1件)検出され、より複雑な閉鎖的な音響活動が見られた。
#  相反する弱い証拠: faster-whisper word-level確率はattempt1の方が
#  わずかに高い(0.9903 vs 0.9831、差は僅少で有意ではないと判断)。
SELECTED_ATTEMPT = "attempt2"
SELECTED_ATTEMPT_PATH = f"{ATTEMPTS_DIR}/point_two_attempt2_custom35d6860b.wav"
SELECTION_REASON = (
    "attempt2を選定。根拠(診断raw evidence: audit/point_two_showed_show_diag/"
    "diag_raw_evidence.json, diag_log.txt): "
    "(a) windowed Primary ASR(中立prompt付き)は、他の全条件で一貫して"
    "'show'を返したPrimary ASRが、この条件でのみattempt2から'showed'を検知した"
    "(attempt1は同条件でも'show'のまま) — 'show'寄りにバイアスされたエンジン"
    "自身が'showed'を認識できた唯一の条件。"
    "(b) 簡易音響分析(8ms/2msホップRMS+高域比)で、目的語境界付近の低エネル"
    "ギー(closure候補)区間がattempt2で3件(attempt1は1件)検出され、より複雑な"
    "閉鎖的な音響活動が見られた。"
    "相反する弱い証拠として、faster-whisper word-level確率はattempt1の方が"
    "わずかに高い(0.9903 vs 0.9831)が、差は僅少(<1%)でありphonetic clarity"
    "の指標として決定的ではないと判断した。"
)


def log(msg):
    print(msg)


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def snapshot_narration_hashes():
    hashes = {}
    for fname in sorted(os.listdir(NARRATION_DIR)):
        fpath = f"{NARRATION_DIR}/{fname}"
        if os.path.isfile(fpath) and fname.endswith(".wav"):
            hashes[fname] = sha256_of(fpath)
    return hashes


def step1_accept_and_update_records():
    os.makedirs(OUT_DIR, exist_ok=True)
    assert os.path.exists(SELECTED_ATTEMPT_PATH), f"選定attemptが見つかりません: {SELECTED_ATTEMPT_PATH}"
    attempt_sha = sha256_of(SELECTED_ATTEMPT_PATH)
    log(f"[SubtaskE] 選定attempt={SELECTED_ATTEMPT} path={SELECTED_ATTEMPT_PATH} sha256={attempt_sha[:16]}...")
    log(f"[SubtaskE] 選定理由: {SELECTION_REASON}")

    # narration/point_two.wav(現在は重複入りTrial-13原本、
    # pre_fix_buggy_audio_backup/へは既にサブタスクAで退避済み)を、
    # 選定attemptで置き換える。
    target_path = f"{NARRATION_DIR}/point_two.wav"
    pre_replace_sha = sha256_of(target_path) if os.path.exists(target_path) else None
    log(f"[SubtaskE] 置き換え前 narration/point_two.wav sha256={pre_replace_sha}")
    backup_path = f"{AUDIT_DIR}/pre_fix_buggy_audio_backup/point_two_BUGGY_PRE_FIX.wav"
    if os.path.exists(backup_path):
        assert sha256_of(backup_path) == pre_replace_sha, (
            "置き換え前point_two.wavが既存バックアップと一致しません。想定外の状態のため中断します。")
        log("[SubtaskE] 既存バックアップ(pre_fix_buggy_audio_backup/point_two_BUGGY_PRE_FIX.wav)と一致確認済み。")
    shutil.copyfile(SELECTED_ATTEMPT_PATH, target_path)
    new_sha = sha256_of(target_path)
    assert new_sha == attempt_sha
    log(f"[SubtaskE] narration/point_two.wav を {SELECTED_ATTEMPT} で置き換え完了。sha256={new_sha[:16]}...")

    # tts_generation_results.json: 実際に起きたこと(2回のTTS生成、いずれも
    # Primary ASRで内容不一致)を正直に反映する。fix02_regeneration_log.json
    # (review_lock台帳のlocked_entry)から実データを引用する(新規ASR呼び出し
    # は行わない)。
    results_path = f"{AUDIT_DIR}/tts_generation_results.json"
    all_results = load_json(results_path)
    prior_entry = all_results["segments"]["point_two"]

    regen_log = load_json(f"{AUDIT_DIR}/fix02_regeneration_log.json")
    locked_entry = regen_log["point_two"]["locked_entry"]
    selected_attempt_index = int(SELECTED_ATTEMPT.replace("attempt", "")) - 1
    selected_attempt_record = locked_entry["last_attempts_log"][selected_attempt_index]

    import wave
    import contextlib
    with contextlib.closing(wave.open(target_path, "r")) as wf:
        measured_duration = wf.getnframes() / wf.getframerate()

    new_entry = {
        "status": "STOPPED",
        "text": CANONICAL_TEXT,
        "canonical_text": CANONICAL_TEXT,
        "language": "en",
        "path": target_path,
        "model": prior_entry.get("model"),
        "voice": prior_entry.get("voice"),
        "call_count": selected_attempt_record.get("attempt"),
        "retry_count": selected_attempt_record.get("attempt", 1) - 1,
        "sha256": new_sha,
        "duration_seconds": round(measured_duration, 3),
        "trim_info": None,
        "clipping_detected": None,
        "asr_verified": False,
        "asr_text": selected_attempt_record.get("asr_text"),
        "attempts_log": locked_entry["last_attempts_log"],
        "audio_classification": selected_attempt_record.get("audio_classification"),
        "connected_speech_info": selected_attempt_record.get("connected_speech_info"),
        "reading_resolver_info": selected_attempt_record.get("reading_resolver_info"),
        "disfluency_checked": selected_attempt_record.get("disfluency_checked", False),
        "disfluency_evidence": selected_attempt_record.get("disfluency_evidence"),
        "fallback_used": False,
        "original_path": None,
        # 正直な記録: このsegmentは6% A2 slowdown post-processを一度も
        # 通っていない(generate_a2_segment_with_slowdownはstandard結果が
        # status=="OK"の場合のみslowdownを適用する設計だが、この2attemptは
        # いずれもTRUE_CONTENT_MISMATCHでstatus!="OK"だったため未適用)。
        "slowdown_applied": False,
        "slowdown_info": None,
        "post_slowdown_asr_text": None,
        "post_slowdown_classification": None,
        "slowdown_attempts_log": [],
        "OPEN112_THEME2_AUDIO_REVIEW_FIX_02_NOTE": prior_entry.get("OPEN112_THEME2_AUDIO_REVIEW_FIX_02_NOTE"),
        "OPEN112_THEME2_AUDIO_REVIEW_FIX_02_SUBTASK_E_HUMAN_APPROVAL_NOTE": (
            f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 サブタスクE: "
            f"ユーザーが2026-09-07に実際に試聴し、'showed'と聞こえることを確認(Azure Secondary・"
            "faster-whisper localの独立ASRとも一致、Connected Speech下でのASR false rejectionと分類=B確定、"
            "TTS誤発音とは扱わない)。重複バグは解消済み(FIX-02サブタスクAで既に windowed再ASR+spectral "
            f"self-similarityで確認済み)の{SELECTED_ATTEMPT}を、既存メカニズムrecord_human_approval()で"
            "正式にaccept。新規TTS/ASR生成は行っていない(既存音声のacceptのみ)。"
            f"選定理由: {SELECTION_REASON} "
            "既知の限界: このsegmentは6% A2 slowdown post-process(apply_a2_slowdown_postprocess)を"
            "一度も通っていない(標準生成がstatus=='OK'に到達できなかったため、コード経路上slowdown適用前に"
            "打ち切られた)。narration_dir内に残るpoint_two_original.wavはTrial-13の重複入り原本であり、"
            "この新しいpoint_two.wavとは無関係(既存Audio Validation Gateの`_segment_missing_mandatory_"
            "a2_slowdown()`後方互換ロジックが、この無関係な旧ファイルの存在だけでslowdown済みとみなして"
            "しまう既知の抜け穴。本注記で明示し、隠蔽しない)。"
        ),
    }
    all_results["segments"]["point_two"] = new_entry
    save_json(results_path, all_results)
    log("[SubtaskE] tts_generation_results.json のsegments.point_two を更新完了(status=STOPPED、"
        "slowdown_applied=false、accept注記付き)。")

    # 既存の人間承認メカニズム(手書きJSON改変ではなく既存API経由)。
    asm.record_human_approval(A2_DIR, "point_two", CANONICAL_TEXT, approved_by="user")
    log(f"[SubtaskE] record_human_approval(out_dir={A2_DIR!r}, segment_key='point_two') 呼び出し完了。"
        f"audit/human_approved_segments.jsonへ記録。")

    return {"selected_attempt": SELECTED_ATTEMPT, "new_sha256": new_sha,
            "duration_seconds": round(measured_duration, 3)}


def step2_reassemble():
    before_hashes = snapshot_narration_hashes()
    theme = {"theme_id": THEME_ID, "out_dir": RERUN02_DIR}
    try:
        summary = asm.stage_assemble_a2(theme)
    except RuntimeError as e:
        log(f"[SubtaskE] Assemble GATE_BLOCKED: {e}")
        raise
    after_hashes = snapshot_narration_hashes()

    unexpected_changes = {
        k: (before_hashes.get(k), after_hashes.get(k))
        for k in set(before_hashes) | set(after_hashes)
        if k != "point_two.wav" and before_hashes.get(k) != after_hashes.get(k)
    }
    log(f"[SubtaskE] Assemble完了: status={summary['status']} duration={summary['duration_seconds']}s "
        f"peak={summary['peak']} clipping={summary['clipping_detected']} "
        f"headroom_applied={summary['headroom_safety_valve']['applied']}")
    log(f"[SubtaskE] narration/*.wav のうちpoint_two.wav以外で変化したファイル数: {len(unexpected_changes)} "
        f"(0であるべき): {unexpected_changes}")
    assert not unexpected_changes, "point_two.wav以外のnarration資産がAssembly前後で変化しました(想定外)。"
    return summary


def step3_verify_final_episode():
    timeline = load_json(f"{AUDIT_DIR}/timeline.json")
    point_two_entry = next(t for t in timeline if t["part"] == "Point Two")
    start_s = point_two_entry["start_seconds"]
    dur_s = point_two_entry["duration_seconds"]
    log(f"[SubtaskE] 完成episode timeline上のPoint Two: start={start_s}s duration={dur_s}s")

    assembled_path = f"{A2_DIR}/assembled/English_Your_Way_A2_{THEME_ID.upper()}.wav"
    data, sr = open121.load_wav(assembled_path)
    mono = open121.to_mono(data)
    pad = 1.0
    clip_start = max(0.0, start_s - pad)
    clip_end = start_s + dur_s + pad
    clip = mono[int(clip_start * sr):int(clip_end * sr)]
    clip_path = f"{OUT_DIR}/final_episode_point_two_extract.wav"
    open121.write_wav(clip_path, clip, sr)

    # (a) 窓ASR+自己相関で重複消失を確認(既存OPEN-121 Trial関数を再利用、
    # 新規判定ロジックの追加なし)。
    self_sim = open121.spectral_self_similarity(clip_path, min_lag_s=1.0, top_k=5)
    max_run = max((m.get("run_length_seconds_at_thresh_0.85", 0.0) for m in self_sim["top_matches"]), default=0.0)
    log(f"[SubtaskE] spectral_self_similarity: top_matches={len(self_sim['top_matches'])} "
        f"max_run_length_seconds={max_run} (参考: FIX-02診断で確認済みの実重複はrun長0.60秒)")

    # (b) Azure Secondary ASR(既存関数、無バイアス=phrase list無し)で内容確認。
    azure_text, azure_err = secondary_asr.get_full_text_via_azure_stt_with_phrase_list(
        clip_path, language="en-US", phrases=None)
    log(f"[SubtaskE] Azure Secondary ASR(完成episode切り出し, phrase list無し): {azure_text!r} err={azure_err}")

    # (c) faster-whisper local verbatim(既存関数)で内容確認。
    local_evidence = dq18.check_segment_for_disfluency(clip_path, language="en", model_size="small")
    log(f"[SubtaskE] faster-whisper local verbatim(完成episode切り出し): {local_evidence['transcript']!r}")

    verification = {
        "timeline_point_two": point_two_entry,
        "extract_clip_path": clip_path,
        "self_similarity": self_sim,
        "self_similarity_max_run_length_seconds": max_run,
        "azure_secondary_asr_text": azure_text,
        "azure_secondary_asr_error": azure_err,
        "local_verbatim_transcript": local_evidence["transcript"],
        "local_verbatim_evidence": local_evidence,
    }
    save_json(f"{OUT_DIR}/final_episode_verification.json", verification)
    return verification


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.init_logger(f"{OUT_DIR}/verification_cost_log.jsonl")

    accept_result = step1_accept_and_update_records()
    assemble_summary = step2_reassemble()
    verification = step3_verify_final_episode()

    final = {
        "accept_result": accept_result,
        "assemble_summary": assemble_summary,
        "verification": verification,
    }
    save_json(f"{OUT_DIR}/subtask_e_run_summary.json", final)
    log("[SubtaskE] 完了。詳細: " + f"{OUT_DIR}/subtask_e_run_summary.json")
    return final


if __name__ == "__main__":
    main()
