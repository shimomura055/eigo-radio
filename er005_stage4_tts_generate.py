# ============================================================
# er005_stage4_tts_generate.py
# ER-005-COST-BASELINE-01: Stage 4(TTS/ASR全segment生成)
# ============================================================
# er003_v1_n3_01_tts_generate.py の generate_b1_segments/generate_a2_segments を
# そのまま再利用する(TTS/ASR呼び出し・fallback・safety margin等は無改変)。
# JAPANESE_TITLESはmodule変数への直接代入で拡張する(既存3テーマは変更しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er005_stage4_tts_generate.py <theme_id>

from __future__ import annotations

import sys

import er005_cost_logger as cl
import er003_v1_n3_01_tts_generate as tts
from er005_stage2_articles_generate import THEMES

tts.JAPANESE_TITLES["akb48"] = "AKB48の新曲『好きish』、伊藤百花が2作連続センター、近藤沙樹が初選抜"
tts.JAPANESE_TITLES["parenting"] = "親の育った環境が、今の子育てにどう関係するのか"


def run(theme_id: str) -> None:
    cl.install("er005_output/cost_baseline_01/raw_usage_log.jsonl")
    theme = THEMES[theme_id]

    with cl.logging_context(theme_id, "b1_tts_asr"):
        b1_result = tts.generate_b1_segments(theme)
    with cl.logging_context(theme_id, "a2_tts_asr"):
        a2_result = tts.generate_a2_segments(theme)

    print(f"[Stage4][{theme_id}] b1={b1_result['segment_status']}")
    print(f"[Stage4][{theme_id}] a2={a2_result['segment_status']}")


if __name__ == "__main__":
    run(sys.argv[1])
