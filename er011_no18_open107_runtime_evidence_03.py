# ============================================================
# er011_no18_open107_runtime_evidence_03.py
# ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03
# ============================================================
# No.18本番Audio Stage実行(er011_no18_open107_audio_stage_03.py)では、B1の
# News本文5segment(full_story_part1/2, point_one, point_two, in_one_line)
# はいずれも通常経路の初回attemptでPASSしたため、Ending-Clarity fallback
# 自体は発火しなかった(=常時適用ではないことの裏付けにはなるが、fallback
# 自体の実発火evidenceにはならない)。
#
# ユーザー指示(§6)は「DEV/Trial scriptだけでの確認は不可」であり、
# Production正式path自体でfallbackが実際に発火する場面を明示的に確認する
# 必要がある。本scriptは、er003_v1_n3_01_tts_generate.pyのB1 News本文
# call siteが実際に呼んでいるのと全く同じ関数
# (er011_ending_clarity_fallback_01.generate_news_narration_with_ending_
# clarity_fallback、コピーではなく同一モジュールを直接import)を、既に
# 実証済みの語尾脱落再現条件(ER-011-NO18-OPEN108-LEDGER-REFINE-AND-
# OPEN107-ENDING-FALLBACK-TRIAL-02のcondition 6と同一のIn One Line文言、
# 実Production同一のmodel/voice/instruction)に対して直接呼び出し、
# fallbackが実際に発火しPASSする様子を、No.18の実segmentとは別の隔離
# 出力先(review_lockのnarrationパス規約は満たすが、No.18のtheme_idとは
# 別のtheme_idを使う)で記録する。No.18の実segment(narration/*.wav、
# tts_generation_results.json等)には一切書き込まない。

from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er005_cost_logger as cl
import er011_ending_clarity_fallback_01 as ending_clarity
import er011_open107_opened_tts_diagnostic_trial_01 as diag01

OUT_DIR = "er011_output/open107_production_wiring_runtime_evidence_03"
THEME_ID = "open107_runtime_evidence_theme"
NARRATION_DIR = f"{OUT_DIR}/b1b/narration"

TEXT = diag01.PRODUCTION_IN_ONE_LINE_FULL_TEXT


def run_one(segment_name: str) -> dict:
    out_path = f"{NARRATION_DIR}/{segment_name}.wav"
    print(f"[OPEN-107][Runtime Evidence] 実Production wrapper "
          f"(er011_ending_clarity_fallback_01.generate_news_narration_with_ending_clarity_fallback)"
          f"を直接呼び出します(segment={segment_name})。text={TEXT!r}")
    with cl.logging_context(THEME_ID, "runtime_evidence_open107_03"), cl.segment_context(segment_name):
        result = ending_clarity.generate_news_narration_with_ending_clarity_fallback(
            TEXT, out_path, disfluency_qa=True)
    print(f"[OPEN-107][Runtime Evidence][{segment_name}] status={result.get('status')} "
          f"ending_clarity_fallback_used={result.get('ending_clarity_fallback_used')} "
          f"ending_clarity_trigger={result.get('ending_clarity_trigger')} "
          f"asr_text={result.get('asr_text')!r}")
    return result


def main():
    os.makedirs(NARRATION_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    names = sys.argv[1:] or ["in_one_line"]
    all_results = {}
    for name in names:
        all_results[name] = run_one(name)
    results_path = f"{OUT_DIR}/runtime_evidence_result.json"
    existing = {}
    if os.path.exists(results_path):
        with open(results_path, encoding="utf-8") as f:
            existing = json.load(f)
    existing.update(all_results)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
