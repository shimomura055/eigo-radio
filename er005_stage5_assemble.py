# ============================================================
# er005_stage5_assemble.py
# ER-005-COST-BASELINE-01: Stage 5(Full Audio組み立て、ローカル処理のみ)
# ============================================================
# er003_v1_n3_01_assemble.py の run_theme(theme) をそのまま再利用する。
# ローカル処理(ffmpeg等)のみでAPI課金は発生しないが、Cost Loggerの
# theme/stageコンテキストだけ設定しておく(将来ここでAPI呼び出しが
# 追加された場合に備えた計測フックとして)。
#
# 実行方法:
#   .venv/Scripts/python.exe er005_stage5_assemble.py <theme_id>

from __future__ import annotations

import sys

import er005_cost_logger as cl
import er003_v1_n3_01_assemble as asm
from er005_stage2_articles_generate import THEMES


def run(theme_id: str) -> None:
    cl.install("er005_output/cost_baseline_01/raw_usage_log.jsonl")
    theme = THEMES[theme_id]

    with cl.logging_context(theme_id, "audio_assembly_local"):
        result = asm.run_theme(theme)

    print(f"[Stage5][{theme_id}] done.")
    for k, v in result.items():
        print(f"  {k}: {v.get('status') if isinstance(v, dict) else v}")


if __name__ == "__main__":
    run(sys.argv[1])
