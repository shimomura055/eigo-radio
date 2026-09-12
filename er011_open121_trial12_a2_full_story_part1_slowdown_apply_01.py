# ============================================================
# er011_open121_trial12_a2_full_story_part1_slowdown_apply_01.py
# 管理ID: PM-CLOSEOUT-CONSOLIDATION-96-TRIAL-12-A2-COMPLETION-...(Part A)
# ============================================================
# 背景: PM-CLOSEOUT-CONSOLIDATION-95でHuman Review Lockの`full_story_part1`
# エントリはRESOLVED(採用: standard attempt1 = full_story_part1_attempt1_
# custom35d6860b.wav)へ遷移済みで、narration/full_story_part1.wavへ複製
# 済み。しかしA2必須post-process(6% time-stretch、`apply_a2_slowdown_
# postprocess()`)がこのsegmentにはまだ一度も適用されておらず
# (`full_story_part1_original.wav`が存在しない、他のA2本文segmentは全て
# 適用済み)、Audio Validation Gateの`_segment_missing_mandatory_a2_
# slowdown()`でblockされる状態だった。
#
# 本スクリプトが行うこと(TTS新規生成なし、既存採用済み音声への必須
# post-processのみを既存Production関数[無変更]で適用):
#   1. 既存Production関数`apply_a2_slowdown_postprocess()`
#      (er003_v1_n3_01_tts_generate.py、無変更)を、既に採用済みの
#      narration/full_story_part1.wavへ適用する(6% time-stretch +
#      内蔵Primary ASR再検証、小額・Fable許可範囲内、上限¥50)。
#   2. 上記以外の追加ASR呼び出し(Secondary ASR等)は行わない(Fable
#      許可外)。ただし、OPEN-121対称正規化が実際に発火することを
#      記録するため、既存Production module`er011_open121_repetition_
#      qa_production_01.evaluate_repetition_qa()`(ローカルfaster-whisper、
#      ¥0)をpost-slowdown音声へ実行し、flagged状態を記録する。
#   3. tts_generation_results.json / review_lock_state.jsonへ、事実を
#      正直に反映するnoteを追記する(隠蔽なし)。
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sys
import time
import wave

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er003_v1_n3_01_tts_generate as n3_tts
import er005_cost_logger as cl
import er011_open121_repetition_qa_production_01 as rqa
import er011_discovery_generalization_wake_before_alarm_trial_12_audio_run as run_mod

THEME_ID = run_mod.THEME_ID
OUT_DIR = run_mod.OUT_DIR
A2_DIR = f"{OUT_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
AUDIT_DIR = f"{A2_DIR}/audit"
OUT_EVIDENCE_DIR = f"{A2_DIR}/audit/open121_trial12_a2_full_story_part1_slowdown_apply_01"
SEGMENT_NAME = "full_story_part1"


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


def wav_duration_seconds(path):
    import contextlib
    with contextlib.closing(wave.open(path, "r")) as wf:
        return wf.getnframes() / wf.getframerate()


def step1_apply_slowdown(prior_entry):
    os.makedirs(OUT_EVIDENCE_DIR, exist_ok=True)
    target_path = f"{NARRATION_DIR}/{SEGMENT_NAME}.wav"
    original_path = f"{NARRATION_DIR}/{SEGMENT_NAME}_original.wav"
    assert not os.path.exists(original_path), (
        f"{original_path}が既に存在します。slowdownが既に適用済みの可能性があり、"
        "本スクリプトの前提(未適用)と矛盾するため停止します。")

    pre_sha = sha256_of(target_path)
    pre_duration = wav_duration_seconds(target_path)
    log(f"[SlowdownApply] post-process前 narration/{SEGMENT_NAME}.wav "
        f"sha256={pre_sha[:16]}... duration={pre_duration:.3f}s "
        f"(Lock RESOLVED採用済み: standard attempt1)")

    pre_backup = f"{OUT_EVIDENCE_DIR}/{SEGMENT_NAME}_PRE_SLOWDOWN_adopted_attempt1_BACKUP.wav"
    shutil.copyfile(target_path, pre_backup)

    tts_input_text = prior_entry["canonical_text"]
    working_result = copy.deepcopy(prior_entry)
    working_result["status"] = "OK"  # 既存accept済み音声へのpost-process適用のためだけの一時値
    result_after = n3_tts.apply_a2_slowdown_postprocess(
        SEGMENT_NAME, NARRATION_DIR, tts_input_text, working_result)

    log(f"[SlowdownApply] apply_a2_slowdown_postprocess実行結果: "
        f"status={result_after.get('status')} slowdown_applied={result_after.get('slowdown_applied')} "
        f"post_slowdown_classification={result_after.get('post_slowdown_classification')} "
        f"post_slowdown_asr_text={result_after.get('post_slowdown_asr_text')!r}")

    post_duration = wav_duration_seconds(target_path)
    ratio = post_duration / pre_duration
    log(f"[SlowdownApply] post-process後 duration={post_duration:.3f}s "
        f"(pre-slowdown比 {ratio:.4f}、目標6%=1.0600)")

    return {
        "pre_slowdown_sha256": pre_sha,
        "pre_slowdown_duration_seconds": round(pre_duration, 3),
        "pre_slowdown_backup_path": pre_backup,
        "post_slowdown_duration_seconds": round(post_duration, 3),
        "duration_ratio": round(ratio, 4),
        "postprocess_result": {k: v for k, v in result_after.items() if k != "attempts_log"},
    }, result_after


def step2_repetition_qa_recheck():
    """既存Production module(OPEN-121対称正規化配線済み)のevaluate_
    repetition_qa()を、post-slowdown音声(narration/full_story_part1.wav、
    実際にA2 Assemblyへ渡される最終音声)へ直接実行する(ローカル
    faster-whisper、追加API課金なし、¥0)。対称正規化が実際にこの最終
    音声上で発火し、flagged=Falseとなることを確認する。"""
    target_path = f"{NARRATION_DIR}/{SEGMENT_NAME}.wav"
    seg = load_json(f"{AUDIT_DIR}/tts_generation_results.json")["segments"][SEGMENT_NAME]
    canonical_text = seg["canonical_text"]
    evidence = rqa.evaluate_repetition_qa(target_path, canonical_text, language="en")
    log(f"[SlowdownApply] post-slowdown repetition_qa再判定(OPEN-121対称正規化、¥0): "
        f"flagged={evidence['flagged']} "
        f"method_a_canon_count={[m.get('canonical_repeat_count') for m in evidence['method_a_ngram']['matches']]} "
        f"method_d_flagged={evidence['method_d_spectral_long_lag']['flagged']} "
        f"method_d_prime_flagged={evidence['method_d_prime_spectral_short_lag']['flagged']}")
    return evidence


def step3_finalize_records(postprocess_summary, result_after, post_slowdown_repetition_qa_evidence):
    results_path = f"{AUDIT_DIR}/tts_generation_results.json"
    all_results = load_json(results_path)

    final_entry = copy.deepcopy(result_after)
    final_entry["post_slowdown_repetition_qa_evidence"] = post_slowdown_repetition_qa_evidence
    final_entry["PM_CLOSEOUT_CONSOLIDATION_96_A2_SLOWDOWN_APPLY_NOTE"] = (
        f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] PM-CLOSEOUT-CONSOLIDATION-96 Part A: "
        f"PM-CLOSEOUT-CONSOLIDATION-95でHuman Review Lock RESOLVE済み(採用: standard attempt1 = "
        "full_story_part1_attempt1_custom35d6860b.wav)だったnarration/full_story_part1.wavへ、"
        "既存Production関数apply_a2_slowdown_postprocess()(無変更)でA2必須6% time-stretchを適用した"
        "(他のA2本文segmentは既に適用済みだったが、本segmentのみHuman Review Lock由来のため未適用"
        "だった)。"
        f"pre-slowdown sha256={postprocess_summary['pre_slowdown_sha256'][:16]}... "
        f"duration={postprocess_summary['pre_slowdown_duration_seconds']}s -> "
        f"post-slowdown duration={postprocess_summary['post_slowdown_duration_seconds']}s "
        f"(比率{postprocess_summary['duration_ratio']}、目標6%=1.0600)。"
        f"post-process内蔵のPrimary ASR再検証(小額、Fable許可範囲): classification="
        f"{result_after.get('post_slowdown_classification')}。"
        f"独立の追加ASR呼び出し(Secondary ASR等)は本タスクの許可範囲外のため実施していない。"
        "post-slowdown音声への既存Production module(OPEN-121対称正規化配線済み)"
        f"evaluate_repetition_qa()再判定(ローカルfaster-whisper、¥0): "
        f"flagged={post_slowdown_repetition_qa_evidence['flagged']}。"
        "上書き前の旧ファイル(Lock採用済みだったpost-process前音声)は"
        f"{postprocess_summary['pre_slowdown_backup_path']} へ退避済み(隠蔽なし)。TTS新規生成は"
        "行っていない。"
    )
    all_results["segments"][SEGMENT_NAME] = final_entry
    save_json(results_path, all_results)
    log(f"[SlowdownApply] tts_generation_results.json のsegments.{SEGMENT_NAME} を更新完了 "
        f"(status={final_entry.get('status')}, slowdown_applied={final_entry.get('slowdown_applied')})。")
    return final_entry


def step4_sync_review_lock_state(final_entry):
    lock_path = f"{AUDIT_DIR}/review_lock_state.json"
    state = load_json(lock_path)
    entry = state[SEGMENT_NAME]
    entry["PM_CLOSEOUT_CONSOLIDATION_96_A2_SLOWDOWN_APPLY_NOTE"] = (
        f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] PM-CLOSEOUT-CONSOLIDATION-96 Part A: "
        "RESOLVED採用済み音声(narration/full_story_part1.wav)へ、A2必須6% time-stretch post-process"
        f"を適用した(既存Production関数apply_a2_slowdown_postprocess()、無変更)。適用後の"
        f"post_slowdown_classification={final_entry.get('post_slowdown_classification')}、"
        f"post-slowdown repetition_qa再判定flagged="
        f"{final_entry['post_slowdown_repetition_qa_evidence']['flagged']}。"
        "final_status/stateの値自体は変更していない(既にOK/RESOLVED)。詳細は"
        f"tts_generation_results.json segments.{SEGMENT_NAME}参照。"
    )
    save_json(lock_path, state)
    log(f"[SlowdownApply] review_lock_state.json の{SEGMENT_NAME}エントリへnote追記完了。")


def main():
    os.makedirs(OUT_EVIDENCE_DIR, exist_ok=True)
    cl.install(run_mod.AUDIO_COST_LOG_PATH)

    results_data = load_json(f"{AUDIT_DIR}/tts_generation_results.json")
    prior_entry = copy.deepcopy(results_data["segments"][SEGMENT_NAME])
    assert prior_entry.get("slowdown_applied") is None, (
        "slowdown_appliedが既に設定されています。想定外の状態のため停止します。")

    with cl.logging_context(f"{THEME_ID}_a2", "full_story_part1_slowdown_apply"):
        postprocess_summary, result_after = step1_apply_slowdown(prior_entry)

    post_slowdown_repetition_qa_evidence = step2_repetition_qa_recheck()
    final_entry = step3_finalize_records(postprocess_summary, result_after, post_slowdown_repetition_qa_evidence)
    step4_sync_review_lock_state(final_entry)

    summary = {
        "postprocess_summary": postprocess_summary,
        "final_entry_status": final_entry.get("status"),
        "final_entry_slowdown_applied": final_entry.get("slowdown_applied"),
        "post_slowdown_repetition_qa_evidence": post_slowdown_repetition_qa_evidence,
    }
    save_json(f"{OUT_EVIDENCE_DIR}/run_summary.json", summary)
    log("[SlowdownApply] 完了。詳細: " + f"{OUT_EVIDENCE_DIR}/run_summary.json")
    return summary


if __name__ == "__main__":
    main()
