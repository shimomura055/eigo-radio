# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_a2_ut06_regen.py
# 管理ID: USER-TEST-FINAL-AUDIO-BATCH-06 (A) item2
# ============================================================
# 目的: discovery/a2/article.md(530語版、ユーザー採用済み、本文は再生成
# しない)を固定入力として、既存Production関数のみ(er003_v1_n3_01_
# scaffold_generate.run_a2_scaffold/run_key_phrases、er003_v1_n3_01_
# tts_generate.generate_a2_segments、er003_v1_n3_01_assemble.
# stage_assemble_a2/verify_episode_audio_validation_gate、いずれも無変更)
# で、Key Phrase再選定(Canonicalization+Redundancy QA込み)/Support
# (Preview/Comment)生成/TTS/Assembly/Audio Validation/Web playerまで
# 完走させる。旧604語版由来のaudio/key_phrase artifactは事前に
# discovery/audio/a2_before_regeneration_604w/・discovery/key_phrases/
# a2_before_regeneration_604w/へ退避済み(本スクリプト実行前に完了)。
#
# 既存run_discovery_audio_completion.pyのprepare_key_phrases()は
# 「既存出力をそのままコピー再利用」する設計(A2/B1Bとも過去に既に
# 完成済みだったため)だが、本文が530語版へ変更されているため、まず
# discovery/key_phrases/a2/へ新規Key Phrase選定を行ってから同関数で
# audio/a2/側へコピーする(既存関数は無変更、投入するsource側のみ更新)。
#
# 実行方法:
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/discovery/run_discovery_a2_ut06_regen.py
from __future__ import annotations

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

import er003_v1_n3_01_scaffold_generate as sc  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import run_discovery_audio_completion as base  # noqa: E402 (既存driver、無変更で再利用)

TASK_ID = "USER-TEST-FINAL-AUDIO-BATCH-06"
BUDGET_JPY = 80.0
LEVEL = "a2"


def main() -> None:
    cl.install(base.LOG_PATH)
    baseline_cost = base.cost_so_far_jpy()
    print(f"[UT06-A][A2][BUDGET] task開始前の全累積コスト={baseline_cost:.2f} JPY "
          f"(本タスクPart3上限=¥{BUDGET_JPY}はこのdriverの新規発生分のみに適用)")

    def check_part_budget(note: str) -> None:
        now = base.cost_so_far_jpy()
        delta = now - baseline_cost
        print(f"[UT06-A][A2][BUDGET] 累積差分={delta:.2f} JPY / 上限={BUDGET_JPY} JPY (次段階: {note})")
        if delta >= BUDGET_JPY:
            raise RuntimeError(
                f"[UT06-A][A2] Part3費用上限到達のためSTOP: 差分={delta:.2f} JPY >= {BUDGET_JPY} JPY "
                f"(次段階「{note}」を実行せず停止)")

    article_text = base.prepare_article(LEVEL)
    word_count_split = len(article_text.split())
    print(f"[UT06-A][A2] article.md word_count(split()による簡易カウント)={word_count_split}")

    check_part_budget("scaffold(Preview/Comment)")
    parts = base.run_scaffold(LEVEL, article_text)

    check_part_budget("key phrase reselection(Canonicalization+Redundancy QA)")
    kp_dir_a2 = f"{base.DISCOVERY_DIR}/key_phrases/a2"
    kp_result = sc.run_key_phrases(
        article_text, kp_dir_a2, f"{base.THEME_ID}_a2_ut06a",
        "A2(N3-01, Discovery Focus S2, UT06A 530-word version)", process="A2_SUPPORT")
    sel_status = kp_result["selection"]["status"]
    canon_status = (kp_result.get("canonicalization") or {}).get("status")
    redundancy_status = (kp_result.get("redundancy_qa") or {}).get("status")
    print(f"[UT06-A][A2] Key Phrase再選定: selection={sel_status} canonicalization={canon_status} "
          f"redundancy_qa={redundancy_status}")
    if sel_status != "KEY_WORDS_STRUCTURE_PASS" or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED") or redundancy_status == "REDUNDANCY_NG":
        base.save_json(f"{base.OUT_DIR}/{LEVEL}/audit/ut06a_key_phrase_stop.json", kp_result)
        print("===== [UT06-A][A2] STOP: Key Phrase再選定がPASSしませんでした。TTS以降には進みません。 =====")
        return

    check_part_budget("Key Phrase reuse-copy into audio/a2")
    kp = base.prepare_key_phrases(LEVEL, article_text)

    check_part_budget("TTS(generate_a2_segments)")
    tts_result = base.run_tts(LEVEL)
    print(f"[UT06-A][A2] TTS完了。segment_status={ {k: v.get('status') if isinstance(v, dict) else v for k, v in (tts_result or {}).items()} if isinstance(tts_result, dict) else tts_result }")

    check_part_budget("Assembly")
    assemble_result = base.run_assembly(LEVEL)
    if assemble_result.get("gate_off_result") != "PASS":
        base.save_json(f"{base.OUT_DIR}/{LEVEL}/audit/ut06a_assembly_stop.json", assemble_result)
        print(f"===== [UT06-A][A2] STOP: Assembly(Gate OFF経路)がPASSしませんでした: {assemble_result} =====")
        return

    check_part_budget("Gate ON / Consistency / Web player")
    gate_on = base.run_gate_opt_in_check(LEVEL)
    consistency = base.build_consistency_check(LEVEL)
    web = base.build_player_and_web_delivery(LEVEL, assemble_result)

    cost_after = base.cost_so_far_jpy()
    level_result = {
        "level": LEVEL, "task_id": TASK_ID,
        "word_count_split": word_count_split,
        "kp_result_status": {"selection": sel_status, "canonicalization": canon_status,
                              "redundancy_qa": redundancy_status},
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),
        "cost_before_jpy": baseline_cost, "cost_after_jpy": cost_after,
        "incremental_cost_jpy": round(cost_after - baseline_cost, 2),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    base.save_json(f"{base.OUT_DIR}/{LEVEL}/run_result_ut06a_regen.json", level_result)
    print(f"[UT06-A][A2] 完了: gate_off=PASS gate_on={gate_on.get('gate_on_result')} "
          f"duration={assemble_result.get('duration_seconds')}s "
          f"consistency_all_pass={consistency.get('all_pass')} "
          f"incremental_cost_jpy={level_result['incremental_cost_jpy']}")


if __name__ == "__main__":
    main()
