# ============================================================
# er008_a2_speed_same_text_abc_09.py
# ER-008-A2-SPEED-SAME-TEXT-ABC-09:
# No.7 A2 Full Story Part 1のみ、本文/voice/model/segment境界を完全
# 固定し、速度指示(style_prefix_override)だけを変えたA/B/C 3候補を
# standard path限定で生成し、WPMを比較する。
# ============================================================
# Production本体(er003_v1_n3_01_tts_generate.py等)は一切変更しない。
# 生成先はProductionのNo.7 A2 narration/ディレクトリとは別の専用
# ディレクトリとし、既存の完成candidateへは一切触れない(Part A:
# 「まだProduction既定速度は変更しない」)。
from __future__ import annotations

import json
import os

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_tts_generate as tts_gen

OUT_DIR = "er008_output/n7_a2_speed_same_text_abc_09"

# Part A: 本文はNo.7 A2の現行Production parts.json[part1]と一字一句同一
# (別途diffで検証する)。
FULL_STORY_PART1_TEXT = (
    "After the pandemic, many offices changed how people sit at work.\n\n"
    "Instead of giving each person a desk, they introduced hot-desking. A worker comes in, "
    "finds an empty desk, and uses it for the day. No personal desk is waiting.\n\n"
    "Now, some offices are changing again. Reports show some companies bringing back assigned "
    "desks for certain workers or teams. In this system, a person or team has a regular place."
)

# --- Part B: 条件A(現行Production、control) ---
# tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWERをそのまま使う(新規に文字列を
# 再定義しない=controlの一字一句の同一性を保証する)。
INSTRUCTION_A = tts_gen.A2_SLOWER_PACE_INSTRUCTION
PREFIX_A = tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER

# --- Part B: 条件B(やや強め) ---
INSTRUCTION_B = (
    "\nSpeak at a clearly but only slightly slower pace than natural adult narration. Keep "
    "the delivery relaxed, smooth, and conversational. Give each phrase enough space to be "
    "easy to follow, but do not sound slow, exaggerated, or instructional.\n"
)
PREFIX_B = p9a.ENGLISH_STYLE_PREFIX + INSTRUCTION_B

# --- Part B: 条件C(Bよりもう一段強め) ---
INSTRUCTION_C = (
    "\nSpeak at a moderately relaxed pace, slightly slower than normal conversational "
    "narration, so an English learner can follow comfortably. Keep the rhythm natural and "
    "connected. Do not over-pause, separate words unnaturally, or sound like a classroom "
    "recording.\n"
)
PREFIX_C = p9a.ENGLISH_STYLE_PREFIX + INSTRUCTION_C

CANDIDATES = {
    "A": {"instruction": INSTRUCTION_A, "prefix": PREFIX_A, "label": "現行Production(control)"},
    "B": {"instruction": INSTRUCTION_B, "prefix": PREFIX_B, "label": "やや強め"},
    "C": {"instruction": INSTRUCTION_C, "prefix": PREFIX_C, "label": "Bよりもう一段強め"},
}

for _key, _cfg in CANDIDATES.items():
    common.assert_no_wpm_specification(_cfg["prefix"])


def run_candidate_standard_only(key: str) -> dict:
    """standard pathの結果だけを見るため、generate_english_segment_with_
    fallback()を直接呼ばず、内部で使われているverified_strict関数を
    style_prefix_override付きで直接呼び出す(fallbackへの自動遷移
    そのものを起こさせない設計。Part D「fallback未使用」を構造的に
    保証する)。"""
    import er003_v1_repro01_main_generate as repro01

    cfg = CANDIDATES[key]
    out_dir = f"{OUT_DIR}/{key}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/full_story_part1.wav"
    tts_input = tts_gen.tts_safe_news_en(FULL_STORY_PART1_TEXT)
    expected_substring = tts_gen.first_words(FULL_STORY_PART1_TEXT)
    print(f"[ABC-09][{key}] {cfg['label']} 生成開始(standard path限定)...")
    result = repro01.generate_narration_snippet_verified_strict(
        tts_input, "en", out_path, expected_substring, style_prefix_override=cfg["prefix"])
    result["fallback_used"] = False
    result["candidate"] = key
    result["candidate_label"] = cfg["label"]
    result["instruction_text"] = cfg["instruction"]
    result["canonical_text"] = FULL_STORY_PART1_TEXT
    return result


def word_count(text: str) -> int:
    return len(text.split())


def compute_wpm(result: dict) -> dict:
    trim_info = result.get("trim_info") or {}
    trimmed_duration = trim_info.get("trimmed_duration_seconds")
    leading_margin = trim_info.get("leading_margin_retained_seconds", 0.0)
    trailing_margin = trim_info.get("trailing_margin_retained_seconds", 0.0)
    wc = word_count(FULL_STORY_PART1_TEXT)
    active_speech_duration = None
    active_speech_wpm = None
    total_duration_wpm = None
    if trimmed_duration:
        active_speech_duration = round(trimmed_duration - leading_margin - trailing_margin, 3)
        if active_speech_duration > 0:
            active_speech_wpm = round(wc / (active_speech_duration / 60.0), 2)
        total_duration_wpm = common.effective_wpm(wc, trimmed_duration)
    return {
        "word_count": wc,
        "total_audio_duration_seconds": trimmed_duration,
        "active_speech_duration_seconds": active_speech_duration,
        "active_speech_wpm": active_speech_wpm,
        "total_duration_wpm": total_duration_wpm,
    }


if __name__ == "__main__":
    import er008_n7_pilot_run_01 as pilot

    pilot.enable_sync_tts_mode()
    all_results = {}
    try:
        for key in ("A", "B", "C"):
            r = run_candidate_standard_only(key)
            wpm = compute_wpm(r) if r.get("status") == "OK" else {}
            all_results[key] = {**r, "wpm_metrics": wpm}
            print(f"[ABC-09][{key}] status={r.get('status')} wpm_metrics={wpm}")
            if r.get("status") != "OK":
                print(f"[ABC-09][{key}] STANDARD PATHが失敗しました。fallbackへは"
                      f"進めていません(Part D遵守)。この候補は速度比較から除外してください。")
    finally:
        pilot.disable_sync_tts_mode()

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/abc_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print("[ABC-09] 完了。結果を保存しました:", f"{OUT_DIR}/abc_comparison_results.json")
