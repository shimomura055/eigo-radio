# ============================================================
# pm_governance_audio_review_player_standard_format_11_regen.py
# 管理ID: PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11
# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-09の player.html を、共通module
# audio_review_player.py 経由の標準フォーマット(Source列削除・Script列拡幅・
# 個別音声幅拡大)で再生成する。
#
# 音声・TTS・ASR・Assemblyは一切実行しない(費用ゼロ・音声/wav無変更)。
# 既存の audit JSON(b1b/parts.json・b1b/b1_support_texts.json・
# b1b/audit/timeline.json・b1b/key_phrases/keywords_canonicalized.json・
# b1b/audit/heading_regen_03_full_run_summary.json)だけを読み、
# er012_editorial_b_voices_trial_09_heading_regen_03.build_full_player_html_03()
# (本タスクで標準フォーマット対応済み、無変更のまま呼ぶだけ)を直接呼んで
# player.htmlだけを上書きする。
from __future__ import annotations

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er012_editorial_b_voices_trial_09_heading_regen_03 as t9r3

OUT_DIR = t9r3.OUT_DIR
OUT_B1_DIR = t9r3.OUT_B1_DIR


def load_json(path: str) -> dict:
    return t9r3.load_json(path)


def main() -> None:
    full_summary = load_json(f"{OUT_B1_DIR}/audit/heading_regen_03_full_run_summary.json")
    heading_regen_summary = full_summary["heading_regen"]
    assemble_summary = full_summary["assembly"]
    assert assemble_summary.get("status") == "OK", (
        "既存assembly summaryのstatusがOKではない(音声再Assemblyは行わない方針のため中断)")

    voice_resolution = load_json(f"{OUT_DIR}/audit/voice_resolution.json")
    voice_a, voice_b = voice_resolution["voice_a"], voice_resolution["voice_b"]

    timeline = load_json(f"{OUT_B1_DIR}/audit/timeline.json")
    parts = load_json(f"{OUT_B1_DIR}/parts.json")
    support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")

    assembled_wav = assemble_summary["out_path"]
    assert os.path.exists(assembled_wav), (
        f"既存assembled wavが見つからない(新規Assemblyは行わない方針のため中断): {assembled_wav}")

    player_path = t9r3.build_full_player_html_03(
        assemble_summary, timeline, parts, support_texts, voice_a, voice_b, heading_regen_summary)
    print(f"[PM-GOV-11] 標準フォーマットでplayer.htmlを再生成: {os.path.abspath(player_path)}")
    print("[PM-GOV-11] 音声・JSON・wavは一切変更していない(player.htmlのみ上書き)。")


if __name__ == "__main__":
    main()
