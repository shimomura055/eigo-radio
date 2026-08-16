# ============================================================
# er003_v1_b1redesign_audio02_generate.py
# ER-003-B1-REDESIGN-AUDIO-02: Point Cue再設計・Comment3変更・
# In One Line Voice変更(変更segmentのみ新規生成)
# ============================================================
# B1-B News English(Full Story Part1/2・Point One/Two本文・In One Line
# 本文)は一切書き換えない。既存のAUDIO-01成果物のうち変更不要な
# segmentは再利用し、以下のみ新規生成する:
#   - comment_3(新しいBridge文言、Charon)
#   - in_one_line(voice変更、Charon→Aoede、本文は無変更)
#   - point_one_heading(semantic heading、新規、Aoede)
#   - point_two_heading(semantic heading、新規、Aoede)
# 「First point.」「Second point.」は使用しない(削除)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1redesign_audio02_generate.py

from __future__ import annotations

import json

import er003_v1_b1redesign_audio_scaffold_generate as scaf
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = scaf.OUT_DIR
NARRATION_DIR = f"{OUT_DIR}/narration"

NEW_COMMENT_3_TEXT = ("This story shows a clear difference between political claims and practical "
                       "talks about shipping. Next, let's look at two ideas that help put this story "
                       "in context.")

POINT_ONE_SEMANTIC_HEADING = "“Control” can mean different things."
POINT_TWO_SEMANTIC_HEADING = "Why a technical map matters worldwide."

with open(f"{OUT_DIR}/audit/text_identity.json", encoding="utf-8") as f:
    PARTS = json.load(f)["parts"]


def main():
    results = {}

    print("[B1REDESIGN-AUDIO02] comment_3再生成(Charon、新しいBridge文言)...")
    r = voice01.generate_charon_english(NEW_COMMENT_3_TEXT, f"{NARRATION_DIR}/comment_3_charon.wav")
    results["comment_3"] = r
    print(f"[B1REDESIGN-AUDIO02] comment_3: status={r.get('status')}")

    print("[B1REDESIGN-AUDIO02] in_one_line再生成(Voice変更: Charon→Aoede、本文は無変更)...")
    r = news_tail_fix.generate_news_narration_wide_margin(
        PARTS["in_one_line"], f"{NARRATION_DIR}/in_one_line_aoede.wav")
    results["in_one_line_aoede"] = r
    print(f"[B1REDESIGN-AUDIO02] in_one_line_aoede: status={r.get('status')}")

    print(f"[B1REDESIGN-AUDIO02] point_one_heading(semantic、Aoede): {POINT_ONE_SEMANTIC_HEADING!r}...")
    r = point_headings.generate(POINT_ONE_SEMANTIC_HEADING, f"{NARRATION_DIR}/point_one_heading_semantic_aoede.wav")
    results["point_one_heading_semantic"] = r
    print(f"[B1REDESIGN-AUDIO02] point_one_heading_semantic: status={r.get('status')}")

    print(f"[B1REDESIGN-AUDIO02] point_two_heading(semantic、Aoede): {POINT_TWO_SEMANTIC_HEADING!r}...")
    r = point_headings.generate(POINT_TWO_SEMANTIC_HEADING, f"{NARRATION_DIR}/point_two_heading_semantic_aoede.wav")
    results["point_two_heading_semantic"] = r
    print(f"[B1REDESIGN-AUDIO02] point_two_heading_semantic: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/audio02_segment_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    print("完了。失敗:" if failed else "完了。全件成功。", failed if failed else "")


if __name__ == "__main__":
    main()
