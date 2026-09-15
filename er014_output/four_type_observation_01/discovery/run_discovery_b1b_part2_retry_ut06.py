# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_b1b_part2_retry_ut06.py
# 管理ID: USER-TEST-FINAL-AUDIO-BATCH-06 (A) item1
# ============================================================
# 目的: Discovery B1(discovery/audio/b1b) full_story_part2 segmentの
# Human Review Lock(state=HUMAN_REVIEW_REQUIRED、3attempt上限到達済み)を
# ユーザー明示承認により1回だけ解除し、既に確定済みのcanonical本文
# (parts.json part2、discovery/audio/tts_reading_transforms.json記録の
# 読み整形適用後テキストと完全一致、本文・Factは無変更)で既存Production
# 関数(news_tail_fix.generate_news_narration_wide_margin、無変更)を
# もう1回だけ呼ぶ。approve_regenerate()はer011_human_review_lock_01の
# 正規APIであり、「同じスクリプトの再実行では到達しない経路」を
# 本スクリプト(対話的オペレーター操作に相当する単発driver)が担う。
#
# 成功(status=OK かつ asr_verified=True)した場合のみAssembly/Gate/
# Consistency/Web playerまで既存関数(base=run_discovery_audio_completion、
# 無変更)で進める。失敗した場合はSTOPし、Assembly以降には進まない
# (既存Human Review Lockの安全設計どおり)。
#
# 実行方法:
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/discovery/run_discovery_b1b_part2_retry_ut06.py
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_THIS_DIR = os.path.dirname(__file__)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import er003_v1_n3_01_tts_generate as tts_gen  # noqa: E402
import er003_v1_sing01_news_tail_fix as news_tail_fix  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402
import run_discovery_audio_completion as base  # noqa: E402 (既存driver、TTS/Assembly/Gate/Web、無変更で再利用)

TASK_ID = "USER-TEST-FINAL-AUDIO-BATCH-06"
DISCOVERY_DIR = base.DISCOVERY_DIR
B1B_AUDIO_DIR = f"{base.OUT_DIR}/b1b"
NARRATION_DIR = f"{B1B_AUDIO_DIR}/narration"
WAV_PATH = f"{NARRATION_DIR}/full_story_part2.wav"
RESULTS_PATH = f"{B1B_AUDIO_DIR}/audit/tts_generation_results.json"
SUMMARY_PATH = f"{B1B_AUDIO_DIR}/run_summary_tts.json"
TRANSFORMS_PATH = f"{base.OUT_DIR}/tts_reading_transforms.json"
PARTS_PATH = f"{B1B_AUDIO_DIR}/parts.json"

APPROVED_BY = ("user (USER-TEST-FINAL-AUDIO-BATCH-06 item1, 2026-09-15 explicit single "
               "retry approval; Human Review found 2,500-students/11-countries paragraph "
               "block dropped in prior attempts; canonical text unchanged)")


def main() -> None:
    cl.install(base.LOG_PATH)
    baseline_cost = base.cost_so_far_jpy()
    print(f"[UT06-A][BUDGET] task開始前の全累積コスト(audio_completion log)={baseline_cost:.2f} JPY")

    transforms_record = base.load_json(TRANSFORMS_PATH)
    original_text = transforms_record["original_text"]
    transformed_text = transforms_record["transformed_text"]

    parts = base.load_json(PARTS_PATH)
    assert parts["part2"] == original_text, (
        "[UT06-A] STOP: parts.json part2 と tts_reading_transforms.json original_text が不一致。"
        "本文が変更されている可能性があるため実行を中止します。")

    tts_input = tts_gen.tts_safe_news_en(transformed_text)

    print(f"[UT06-A] Human Review Lock解除(approve_regenerate, 1回限り)。approved_by={APPROVED_BY}")
    approve_entry = review_lock.approve_regenerate(WAV_PATH, tts_input, approved_by=APPROVED_BY)
    print(f"[UT06-A] approve_regenerate結果: state={approve_entry.get('state')}")

    print("[UT06-A] full_story_part2 再生成(既存Production関数、無変更、attempt4)...")
    with cl.logging_context(base.THEME_ID, "tts_b1b_ut06a_retry"):
        result = news_tail_fix.generate_news_narration_wide_margin(
            tts_input, WAV_PATH,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True,
        )
    result["canonical_text"] = original_text
    result["tts_input_text"] = tts_input
    result["task_id"] = TASK_ID
    result["fix_label"] = "ut06a_attempt4_unchanged_canonical"

    data = base.load_json(RESULTS_PATH)
    data["segments"]["full_story_part2"] = result
    base.save_json(RESULTS_PATH, data)
    summary = base.load_json(SUMMARY_PATH)
    summary["segment_status"]["full_story_part2"] = result.get("status")
    base.save_json(SUMMARY_PATH, summary)

    status = result.get("status")
    asr_verified = result.get("asr_verified")
    attempts_log = result.get("attempts_log") or []
    print(f"[UT06-A] full_story_part2 status={status} asr_verified={asr_verified} "
          f"attempts={len(attempts_log)}")
    for a in attempts_log:
        print(f"  attempt={a.get('attempt')} audio_classification={a.get('audio_classification')} "
              f"verified={a.get('verified')}")
        print(f"    asr_text={a.get('asr_text')!r}")

    cost_after = base.cost_so_far_jpy()
    print(f"[UT06-A][BUDGET] task完了後の全累積コスト={cost_after:.2f} JPY "
          f"(本タスク差分=¥{cost_after - baseline_cost:.2f})")

    outcome = {
        "task_id": TASK_ID,
        "status": status,
        "asr_verified": asr_verified,
        "attempts_log": attempts_log,
        "cost_before_jpy": baseline_cost,
        "cost_after_jpy": cost_after,
        "incremental_cost_jpy": round(cost_after - baseline_cost, 2),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    base.save_json(f"{B1B_AUDIO_DIR}/audit/ut06a_part2_retry_result.json", outcome)

    if status != "OK" or not asr_verified:
        print("===== [UT06-A] STOP: attempt4もASR検証に合格しませんでした。"
              "Assembly以降には進みません。個別対応候補は別途RESULT_PACKETへ記載します。 =====")
        return

    print("[UT06-A] attempt4 PASS。Assembly/Gate/Consistency/Web playerへ進みます。")
    assemble_result = base.run_assembly("b1b")
    if assemble_result.get("gate_off_result") != "PASS":
        raise RuntimeError(f"[UT06-A] Assembly(Gate OFF経路)がPASSしませんでした、STOP: {assemble_result}")
    gate_on = base.run_gate_opt_in_check("b1b")
    consistency = base.build_consistency_check("b1b")
    web = base.build_player_and_web_delivery("b1b", assemble_result)

    level_result = {
        "level": "b1b", "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),
    }
    base.save_json(f"{B1B_AUDIO_DIR}/run_result_ut06a_retry.json", level_result)
    print(f"[UT06-A] Assembly完了: gate_off=PASS gate_on={gate_on.get('gate_on_result')} "
          f"duration={assemble_result.get('duration_seconds')}s "
          f"consistency_all_pass={consistency.get('all_pass')}")


if __name__ == "__main__":
    main()
