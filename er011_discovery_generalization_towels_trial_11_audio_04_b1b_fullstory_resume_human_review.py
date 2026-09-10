# ============================================================
# er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME(補助)
# ============================================================
# B1BのHuman Review Lock(review_lock_state.json、state=HUMAN_REVIEW_REQUIRED)
# へ到達した2segment(full_story_part1、full_story_part2)について、A2側と同じ
# 既存Production機構(er011_human_review_lock_01.approve_regenerate→
# REGENERATE_APPROVED)を使い、自然な追加take(1round=既存の総試行回数上限
# 3回budgetの範囲内)を1回取得する。**新しいGate/閾値/retry仕様は追加しない**。
# 呼ぶのは既存Production関数(er003_v1_sing01_news_tail_fix.
# generate_news_narration_wide_margin、無変更)のみ。tts_generation_results.json
# は本scriptでは更新しない(既存のSTOPPED記録をそのまま保持、Human Review
# 承認後に別途同期する)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py
# ============================================================
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er011_human_review_lock_01 as review_lock
import er005_cost_logger as cl

THEME_ID = "discovery_generalization_towels_trial_11"
OUT_DIR = f"er011_output/{THEME_ID}"
B1_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{B1_DIR}/narration"
AUDIO_COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log_audio_01.jsonl"
APPROVED_BY = ("operator(Sonnet, per user 2026-09-11 decision "
               "'Human Review+必要segment再生成へ進める', "
               "管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME)")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def main() -> dict:
    cl.install(AUDIO_COST_LOG_PATH)
    parts = load_json(f"{B1_DIR}/parts.json")
    results = {}

    for name, raw_text in (("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"])):
        tts_input = tts_gen.tts_safe_news_en(raw_text)
        out_path = f"{NARRATION_DIR}/{name}.wav"
        approval = review_lock.approve_regenerate(out_path, tts_input, approved_by=APPROVED_BY)
        print(f"[RESUME][{name}] approve_regenerate -> state={approval['state']}")
        with cl.logging_context(f"{THEME_ID}_b1b", "tts_human_review_resume_04"):
            with cl.segment_context(name):
                r = news_tail_fix.generate_news_narration_wide_margin(
                    tts_input, out_path,
                    disfluency_qa=False,
                    enable_connected_speech_equivalence_layer=True,
                    enable_repetition_qa=True)
        r["canonical_text"] = raw_text
        results[name] = r
        print(f"[RESUME][{name}] status={r.get('status')}")

    save_json(f"{B1_DIR}/audit/human_review_resume_04_results.json", results)
    status_summary = {k: v.get("status") for k, v in results.items()}
    print(f"[RESUME] 完了。status={status_summary}")
    return results


if __name__ == "__main__":
    main()
