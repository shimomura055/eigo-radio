# ============================================================
# er003_v1_a2_point_heading_audio_01_generate.py
# ER-003-A2-POINT-HEADING-AUDIO-01: A2 Point One/Two semantic heading新規TTS
# ============================================================
# 記事データ(fixed_news_parts.json)には point_one_heading/point_two_heading
# が存在していたが、A2の音声生成scriptのSEGMENTS一覧には一度も含まれて
# おらず、音声化されていなかった(Artifact transcriptには表示されていた
# ため、表示Transcriptと実際のAudioが不一致になっていた)。
# 今回この2件のみを、A2の既存英語生成経路(単一Aoede、
# generate_english_segment_with_fallback)で新規TTS生成する。
# 本文・Comment・Voice構成・Point専用Notification等は一切変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_a2_point_heading_audio_01_generate.py

from __future__ import annotations

import json
import os

import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_a2_audio_generate as a2gen

OUT_DIR = a2gen.OUT_DIR
NARRATION_DIR = f"{OUT_DIR}/narration"

POINT_ONE_HEADING_TEXT = a2gen.A2_PARTS["point_one_heading"] + "."
POINT_TWO_HEADING_TEXT = a2gen.A2_PARTS["point_two_heading"] + "."

JOBS = [
    ("point_one_heading", POINT_ONE_HEADING_TEXT, "shipping map"),
    ("point_two_heading", POINT_TWO_HEADING_TEXT, "create trust"),
]


def main():
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    results = {}
    for name, text, expected_substring in JOBS:
        out_path = f"{NARRATION_DIR}/{name}.wav"
        print(f"[A2-POINT-HEADING] 生成開始: {name} = {text!r}")
        r = c.generate_english_segment_with_fallback(text, out_path, expected_substring, max_extra_chars=20)
        results[name] = r
        print(f"[A2-POINT-HEADING] {name} status:", r.get("status"))

    with open(f"{OUT_DIR}/audit/point_heading_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_ok = all(r.get("status") == "OK" for r in results.values())
    print("[A2-POINT-HEADING] 完了。all_ok:", all_ok)


if __name__ == "__main__":
    main()
