# ============================================================
# er011_wake_before_alarm_trial12_a2_comment2_userfix_01.py
# 管理ID: FAMILY-A-DISCOVERY-TRIAL-12-USER-LISTENING-FEEDBACK-FIX-01
# ============================================================
# 目的: ユーザー視聴Feedback(2026-09-13、個別対応・新規一般仕様にはしない)
# のうち、A2 Comment 2の文言差替を実施する。
#   旧: "...決めた時間に近く起きられることはあるのでしょうか。"
#   新: "...決めた時間近くに起きられることはあるのでしょうか。"
#
# 方式: 新規ロジックを作らず、既存Production関数をそのまま呼ぶ。
#   1) a2_support_texts.json の comment_2 を新文言へ差替(バックアップ保存)。
#   2) tts_gen.generate_a2_japanese_with_reading_safety()(既存Production
#      関数、generate_a2_segments()内でcomment_1〜4に使われているものと
#      完全に同一の呼び出し)をcomment_2のみに対して直接呼ぶ。TTS Retry
#      Cascade・Human Review Lock(review_lock_state.json)は既存機構が
#      自動で読み書きする(このscriptは一切バイパスしない)。
#   3) tts_generation_results.json の segments.comment_2 のみを新結果で
#      置き換える(他segmentは無変更)。
#   4) run.assembly_stage("a2")(既存Production関数、Assembly+Audio
#      Validation Gate opt-in ON経路を両方実行)をそのまま呼ぶ。
#      full_story_part1等の他segmentは一切再生成しない(sha256で不変を
#      検証する)。
#
# 費用: cl.install()は本Trialの既存AUDIO_COST_LOG_PATH(raw_usage_
# log_audio_01.jsonl)をそのまま再利用し、新規APIコールのみ追記される
# (既存記録の上書きなし)。呼び出し前後でcompute_cost_jpy_so_far()を
# 比較し、本タスクの増分費用を算出する。
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import wave

import er005_cost_logger as cl
import er011_discovery_generalization_wake_before_alarm_trial_12_audio_run as run

A2_DIR = f"{run.OUT_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
SUPPORT_PATH = f"{A2_DIR}/a2_support_texts.json"
TTS_RESULTS_PATH = f"{A2_DIR}/audit/tts_generation_results.json"
RUN_SUMMARY_TTS_PATH = f"{A2_DIR}/run_summary_tts.json"
RESULT_DIR = f"{A2_DIR}/audit/user_listening_feedback_fix_01"

OLD_COMMENT_2 = ("ここまでで、体内時計は光や決まった生活リズムに合わせて動くことが分かりました。"
                 "では、外から合図がなくても、決めた時間に近く起きられることはあるのでしょうか。")
NEW_COMMENT_2 = ("ここまでで、体内時計は光や決まった生活リズムに合わせて動くことが分かりました。"
                 "では、外から合図がなくても、決めた時間近くに起きられることはあるのでしょうか。")

TS = time.strftime("%Y%m%d_%H%M%S")


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def wav_duration_seconds(path: str) -> float:
    with wave.open(path, "rb") as w:
        return round(w.getnframes() / w.getframerate(), 3)


def backup(path: str) -> str:
    ext = os.path.splitext(path)[1]
    backup_path = f"{path}.backup_before_userfix_{TS}{ext}"
    shutil.copy2(path, backup_path)
    return backup_path


def main() -> None:
    os.makedirs(RESULT_DIR, exist_ok=True)
    evidence = {"managed_id": "FAMILY-A-DISCOVERY-TRIAL-12-USER-LISTENING-FEEDBACK-FIX-01"}

    # --- 変更対象外segmentのsha256事前記録(不変確認用) ---
    unaffected_wavs = ["full_story_part1", "full_story_part2", "comment_1", "comment_3", "comment_4",
                        "point_one", "point_two", "topic_intro", "japanese_title", "in_one_line"]
    before_sha = {name: sha256_of(f"{NARRATION_DIR}/{name}.wav") for name in unaffected_wavs}
    evidence["unaffected_segments_sha256_before"] = before_sha

    # --- 1) a2_support_texts.json 差替 ---
    support = run.load_json(SUPPORT_PATH)
    actual_old_text = support.get("comment_2")
    assert actual_old_text == OLD_COMMENT_2, (
        f"想定外の既存comment_2文言です。差替を中止します。actual={actual_old_text!r}")
    support_backup_path = backup(SUPPORT_PATH)
    support["comment_2"] = NEW_COMMENT_2
    run.save_json(SUPPORT_PATH, support)
    evidence["support_text_change"] = {
        "backup_path": support_backup_path, "old_text": OLD_COMMENT_2, "new_text": NEW_COMMENT_2,
    }
    print(f"[1/4] a2_support_texts.json comment_2 差替完了。backup={support_backup_path}")

    # --- 2) TTS再生成(既存Production関数を直接呼ぶ、¥課金あり) ---
    cl.install(run.AUDIO_COST_LOG_PATH)
    cost_before = run.compute_cost_jpy_so_far()
    evidence["cost_jpy_before"] = cost_before

    comment2_wav_path = f"{NARRATION_DIR}/comment_2.wav"
    with cl.logging_context(f"{run.THEME_ID}_a2", "tts"):
        with cl.segment_context("comment_2"):
            tts_result = run.tts_gen.generate_a2_japanese_with_reading_safety(
                NEW_COMMENT_2, comment2_wav_path, run.tts_gen.expected_substring_ja(NEW_COMMENT_2))

    cost_after_tts = run.compute_cost_jpy_so_far()
    evidence["cost_jpy_after_tts"] = cost_after_tts
    evidence["tts_result_status"] = tts_result.get("status")
    evidence["tts_result_full"] = tts_result
    print(f"[2/4] comment_2 TTS+ASR再検証結果: status={tts_result.get('status')} "
          f"asr_verified={tts_result.get('asr_verified')} classification={tts_result.get('audio_classification')} "
          f"reading_resolver_info={tts_result.get('reading_resolver_info')}")

    if tts_result.get("status") != "OK":
        evidence["stopped_reason"] = ("既存Human Review Lock/Retry Cascadeが未解決のためSTOP。"
                                       "独自判断での回避・再試行は行わない。")
        run.save_json(f"{RESULT_DIR}/userfix_evidence.json", evidence)
        print("[STOP] comment_2のTTS/ASR検証が既存機構でPASSしませんでした。"
              "USER_DECISION_REQUIREDとして報告してください。以降のAssembly/player再生成は行いません。")
        return

    # --- 3) tts_generation_results.json / run_summary_tts.json 同期 ---
    tts_results_backup_path = backup(TTS_RESULTS_PATH)
    tts_results = run.load_json(TTS_RESULTS_PATH)
    tts_results["segments"]["comment_2"] = tts_result
    run.save_json(TTS_RESULTS_PATH, tts_results)
    evidence["tts_generation_results_backup_path"] = tts_results_backup_path

    run_summary_tts_backup_path = backup(RUN_SUMMARY_TTS_PATH)
    run_summary_tts = run.load_json(RUN_SUMMARY_TTS_PATH)
    run_summary_tts["segment_status"]["comment_2"] = tts_result.get("status")
    run.save_json(RUN_SUMMARY_TTS_PATH, run_summary_tts)
    evidence["run_summary_tts_backup_path"] = run_summary_tts_backup_path
    print(f"[3/4] tts_generation_results.json / run_summary_tts.json 同期完了。"
          f"backups={tts_results_backup_path}, {run_summary_tts_backup_path}")

    # --- 不変確認(他segmentのnarration wavが変わっていないこと) ---
    after_sha = {name: sha256_of(f"{NARRATION_DIR}/{name}.wav") for name in unaffected_wavs}
    evidence["unaffected_segments_sha256_after"] = after_sha
    unchanged = {name: (before_sha[name] == after_sha[name]) for name in unaffected_wavs}
    evidence["unaffected_segments_unchanged"] = unchanged
    if not all(unchanged.values()):
        print(f"[WARN] 対象外segmentに変化を検出: {unchanged}")
    else:
        print("[確認] full_story_part1等、対象外segmentのnarration wavは全て不変(sha256一致)。"
              "A2英語Full Storyの6% slowdown post-processは再適用不要と確認。")

    # --- 4) Assembly + Audio Validation Gate(既存Production関数) ---
    assembly_result = run.assembly_stage("a2")
    evidence["assembly_result"] = assembly_result
    print(f"[4/4] Assembly結果: gate_off={assembly_result.get('gate_off_result')} "
          f"gate_on={assembly_result.get('gate_opt_in_result', {}).get('gate_on_result')}")

    cost_after_assembly = run.compute_cost_jpy_so_far()
    evidence["cost_jpy_after_assembly"] = cost_after_assembly
    evidence["this_task_incremental_jpy"] = round(
        cost_after_assembly["total_jpy"] - cost_before["total_jpy"], 2)

    run.cost_stage()

    run.save_json(f"{RESULT_DIR}/userfix_evidence.json", evidence)
    print(f"\n本タスク増分費用(今回): 約¥{evidence['this_task_incremental_jpy']}")
    print(f"Trial-12累計(audio側、compute_cost_jpy_so_far): ¥{cost_after_assembly['total_jpy']}")
    print(f"evidence保存先: {RESULT_DIR}/userfix_evidence.json")


if __name__ == "__main__":
    main()
