# ============================================================
# er011_discovery_generalization_towels_trial_11_audio_02_resume_human_review.py
# 管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-02-RESUME
# ============================================================
# 目的: A2のHuman Review Lock(review_lock_state.json、state=
# HUMAN_REVIEW_REQUIRED)へ到達した2segment(comment_2、meaning_4=
# kp4_japanese_meaning)について、既存Production機構(ER-011-HUMAN-
# REVIEW-COST-GUARD-01、er011_human_review_lock_01.approve_regenerate→
# REGENERATE_APPROVED)を使い、自然な追加take(1回のapprove_regenerateに
# つき標準2回+fallback1回=最大3attempts、既存の総試行回数上限3回budget
# をそのまま消費するだけ)を1round取得する。
#
# **新しいGate/閾値/retry仕様は一切発明しない**。呼ぶのは既存Production
# 関数(er003_v1_n3_01_tts_generate.generate_a2_japanese_with_reading_
# safety、無変更)のみ。tts_generation_results.json(Gateが正として読む
# 既存監査ファイル)は本scriptでは更新しない(Gate判定・Assemblyは
# ユーザーのHuman Review承認後に別途行う、既存のSTOPPED記録をそのまま
# 保持する)。本scriptの結果は別ファイル
# (a2/audit/human_review_resume_02_results.json)へ記録するのみ。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_discovery_generalization_towels_trial_11_audio_02_resume_human_review.py
# ============================================================
from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_n3_01_tts_generate as tts_gen
import er011_human_review_lock_01 as review_lock
import er005_cost_logger as cl

THEME_ID = "discovery_generalization_towels_trial_11"
OUT_DIR = f"er011_output/{THEME_ID}"
A2_DIR = f"{OUT_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
AUDIO_COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log_audio_01.jsonl"  # 既存AUDIO-01タスクと同一ログへ追記(費用集計は既存cost_stageロジックが理由で分離できる: theme tagにlevelを含めているため)
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
    results = {}

    # --- comment_2 ---
    support = load_json(f"{A2_DIR}/a2_support_texts.json")
    comment_2_text = support["comment_2"]
    out_path = f"{NARRATION_DIR}/comment_2.wav"
    approval = review_lock.approve_regenerate(out_path, comment_2_text, approved_by=APPROVED_BY)
    print(f"[RESUME][comment_2] approve_regenerate -> state={approval['state']}")
    with cl.logging_context(f"{THEME_ID}_a2", "tts_human_review_resume_02"):
        with cl.segment_context("comment_2"):
            r = tts_gen.generate_a2_japanese_with_reading_safety(
                comment_2_text, out_path, tts_gen.expected_substring_ja(comment_2_text))
    results["comment_2"] = r
    print(f"[RESUME][comment_2] status={r.get('status')}")

    # --- meaning_4 (kp4 japanese_meaning) ---
    kp = load_json(f"{A2_DIR}/key_phrases/keywords_canonicalized.json")
    item = next(it for it in kp["items"] if it["rank"] == 4)
    ja_gloss_tts = item.get("japanese_gloss_tts") or item["japanese_gloss"]
    used_form = item["used_form"]
    out_path4 = f"{NARRATION_DIR}/meaning_4.wav"
    approval4 = review_lock.approve_regenerate(out_path4, ja_gloss_tts, approved_by=APPROVED_BY)
    print(f"[RESUME][meaning_4] approve_regenerate -> state={approval4['state']}")
    with cl.logging_context(f"{THEME_ID}_a2", "tts_human_review_resume_02"):
        with cl.segment_context("kp4_japanese_meaning"):
            r4 = tts_gen.generate_a2_japanese_with_reading_safety(
                ja_gloss_tts, out_path4, tts_gen.expected_substring_ja(ja_gloss_tts),
                max_extra_chars=30, known_key_phrase_terms=[used_form])
    results["meaning_4"] = r4
    print(f"[RESUME][meaning_4] status={r4.get('status')}")

    save_json(f"{A2_DIR}/audit/human_review_resume_02_results.json", results)
    status_summary = {k: v.get("status") for k, v in results.items()}
    print(f"[RESUME] 完了。status={status_summary}")
    return results


if __name__ == "__main__":
    main()
