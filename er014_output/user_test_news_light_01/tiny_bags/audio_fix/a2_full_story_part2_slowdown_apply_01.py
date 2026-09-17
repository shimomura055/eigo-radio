# ============================================================
# a2_full_story_part2_slowdown_apply_01.py
# 管理ID: USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03
# ============================================================
# 背景: ユーザー正式判断(2026-09-17)により、Tiny Bags A2 `full_story_part2`
# (Toteme/Kallmeyer)はRESUME-02のHuman Review確認ページで実読を確認の上
# 「現在の音声でOK、最終版として採用」となり、`er003_v1_n3_01_assemble.
# record_human_approval()`で正式承認記録済み(TTS新規生成なし)。
#
# ところが本segmentは一度もASR検証に合格していない(最終status=
# ASR_VALIDATION_UNCERTAIN、`attempt3_minimalfallback`採用)ため、A2必須
# post-process(6% time-stretch、`apply_a2_slowdown_postprocess()`)が
# 標準フロー内では一度も適用されていなかった(同関数はstatus=="OK"の
# 場合にのみ動作する既存の仕様、`er003_v1_n3_01_tts_generate.py`)。
# `er003_v1_n3_01_assemble.py::_segment_missing_mandatory_a2_slowdown()`
# が正しくこれを検知しGateがEPISODE_BLOCKED_BY_AUDIO_VALIDATIONで
# assemblyを止めた(override無し)。
#
# これはer011_open121_trial12_a2_full_story_part1_slowdown_apply_01.py・
# er011_open112_theme2_audio_review_fix_02_subtaskg_apply_slowdown_01.pyと
# 全く同型の既知パターン(Human Review Lock経由で承認された結果、6%
# time-stretchという必須post-processを一度も受けないままAssembleへ到達
# しようとするケース)であり、両先例と同じ既存Production関数を無変更で
# 適用する(TTS新規生成なし、承認済み音声[narration/full_story_part2.wav]
# への確定的なFFmpeg time-stretch + 内蔵Primary ASR再検証のみ)。
#
# 本スクリプトが行うこと:
#   1. 既存Production関数`apply_a2_slowdown_postprocess()`
#      (er003_v1_n3_01_tts_generate.py、無変更)を、ユーザー承認済みの
#      narration/full_story_part2.wavへ適用する(6% time-stretch + 内蔵
#      Primary ASR再検証、小額)。
#   2. tts_generation_results.json / review_lock_state.jsonへ、事実を
#      正直に反映するnoteを追記する(隠蔽なし。post-slowdown ASRが
#      再度Toteme/Kallmeyerで不一致になっても、それは想定内でありcanonical
#      textは変更しない=既存Human Approval記録の対象のまま)。
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

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "..", ".."))
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(_THIS_DIR))

import er003_v1_n3_01_tts_generate as n3_tts  # noqa: E402
import er005_cost_logger as cl  # noqa: E402

THEME_ID = "user_test_news_light_01_tiny_bags"
BASE_DIR = "er014_output/user_test_news_light_01/tiny_bags"
A2_DIR = f"{BASE_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
AUDIT_DIR = f"{A2_DIR}/audit"
OUT_EVIDENCE_DIR = f"{AUDIT_DIR}/closeout_03_a2_full_story_part2_slowdown_apply_01"
SEGMENT_NAME = "full_story_part2"


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
        f"(ユーザー承認済み: attempt3_minimalfallback、human_approved_segments.json記録済み)")

    pre_backup = f"{OUT_EVIDENCE_DIR}/{SEGMENT_NAME}_PRE_SLOWDOWN_user_approved_BACKUP.wav"
    shutil.copyfile(target_path, pre_backup)

    tts_input_text = prior_entry["canonical_text"]
    working_result = copy.deepcopy(prior_entry)
    working_result["status"] = "OK"  # 既存承認済み音声へのpost-process適用のためだけの一時値
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


def step2_finalize_records(postprocess_summary, result_after):
    results_path = f"{AUDIT_DIR}/tts_generation_results.json"
    all_results = load_json(results_path)

    # status/final_statusはHuman Approval記録の対象(canonical_text_sha256
    # 照合)であり続けるよう、Human Approval記録時点のcanonical_textを
    # 変更しない(record_human_approval()のcanonical_text_sha256は
    # entry["canonical_text"]に対して既に記録済み、post-processは
    # canonical_textを書き換えない)。
    final_entry = copy.deepcopy(result_after)
    final_entry["CLOSEOUT_03_A2_SLOWDOWN_APPLY_NOTE"] = (
        f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03: "
        "ユーザー正式判断(2026-09-17)によりHuman Approval記録済み"
        "(audit/human_approved_segments.json、TTS新規生成なし)だった"
        "narration/full_story_part2.wav(attempt3_minimalfallback採用)へ、"
        "既存Production関数apply_a2_slowdown_postprocess()(無変更)でA2必須6% time-stretchを適用した"
        "(他のA2本文segmentは既に適用済みだったが、本segmentのみHuman Review Lock由来のため未適用"
        "だった、er011_open121_trial12_a2_full_story_part1_slowdown_apply_01.py等と同型の既知パターン)。"
        f"pre-slowdown sha256={postprocess_summary['pre_slowdown_sha256'][:16]}... "
        f"duration={postprocess_summary['pre_slowdown_duration_seconds']}s -> "
        f"post-slowdown duration={postprocess_summary['post_slowdown_duration_seconds']}s "
        f"(比率{postprocess_summary['duration_ratio']}、目標6%=1.0600)。"
        f"post-process内蔵のPrimary ASR再検証: classification="
        f"{result_after.get('post_slowdown_classification')}(status={result_after.get('status')})。"
        "Toteme/Kallmeyerの読み方自体はTTS内容として既にユーザー承認済みのため、post-slowdown ASRが"
        "再度不一致(Toteme→Totem等)になってもcanonical_text自体は変更せず、既存のHuman Approval記録"
        "(canonical_text_sha256照合)がそのままGateのHUMAN_APPROVED判定に使われる。"
        "上書き前の旧ファイル(ユーザー承認済みだったpost-process前音声)は"
        f"{postprocess_summary['pre_slowdown_backup_path']} へ退避済み(隠蔽なし)。TTS新規生成は"
        "行っていない。"
    )
    all_results["segments"][SEGMENT_NAME] = final_entry
    save_json(results_path, all_results)
    log(f"[SlowdownApply] tts_generation_results.json のsegments.{SEGMENT_NAME} を更新完了 "
        f"(status={final_entry.get('status')}, slowdown_applied={final_entry.get('slowdown_applied')})。")
    return final_entry


def step3_sync_review_lock_state(final_entry):
    lock_path = f"{AUDIT_DIR}/review_lock_state.json"
    state = load_json(lock_path)
    entry = state[SEGMENT_NAME]
    entry["CLOSEOUT_03_A2_SLOWDOWN_APPLY_NOTE"] = (
        f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03: "
        "ユーザー承認済み音声(narration/full_story_part2.wav)へ、A2必須6% time-stretch post-process"
        f"を適用した(既存Production関数apply_a2_slowdown_postprocess()、無変更)。適用後の"
        f"post_slowdown_classification={final_entry.get('post_slowdown_classification')}"
        f"(status={final_entry.get('status')})。"
        "state/final_status(HUMAN_REVIEW_REQUIRED/ASR_VALIDATION_UNCERTAIN)自体はここでは変更していない"
        "(Gateの実際の許可判定はaudit/human_approved_segments.jsonのHuman Approval記録によるHUMAN_"
        "APPROVED分岐で行われる、record_human_approval()の既存設計どおり)。詳細は"
        f"tts_generation_results.json segments.{SEGMENT_NAME}参照。"
    )
    save_json(lock_path, state)
    log(f"[SlowdownApply] review_lock_state.json の{SEGMENT_NAME}エントリへnote追記完了。")


def main():
    os.makedirs(OUT_EVIDENCE_DIR, exist_ok=True)
    cl.install(f"{BASE_DIR}/audio_fix/raw_usage_log_audio_fix.jsonl")

    results_data = load_json(f"{AUDIT_DIR}/tts_generation_results.json")
    prior_entry = copy.deepcopy(results_data["segments"][SEGMENT_NAME])
    assert prior_entry.get("slowdown_applied") is None, (
        "slowdown_appliedが既に設定されています。想定外の状態のため停止します。")

    with cl.logging_context(f"{THEME_ID}_a2", "full_story_part2_slowdown_apply_closeout03"):
        postprocess_summary, result_after = step1_apply_slowdown(prior_entry)

    final_entry = step2_finalize_records(postprocess_summary, result_after)
    step3_sync_review_lock_state(final_entry)

    summary = {
        "postprocess_summary": postprocess_summary,
        "final_entry_status": final_entry.get("status"),
        "final_entry_slowdown_applied": final_entry.get("slowdown_applied"),
    }
    save_json(f"{OUT_EVIDENCE_DIR}/run_summary.json", summary)
    log("[SlowdownApply] 完了。詳細: " + f"{OUT_EVIDENCE_DIR}/run_summary.json")
    return summary


if __name__ == "__main__":
    main()
