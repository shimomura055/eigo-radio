# ============================================================
# er008_n7_baseline_reset_01.py
# ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01
# ============================================================
# No.7("Assigned Desks Are Back in Some Offices")を、Middle Pilot検証
# (ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01 / ER-008-N7-MIDDLE-
# SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01)以前の正式Production仕様(B1/A2
# のみ、Shared Point Blueprint不使用・comment anchor制約不使用・Full
# Story延長処理不使用・Key Phrase pause調整不使用)へ戻して再生成する
# 専用runner。
#
# Research(Evidence Pack/VFL/Ledger)は元々Blueprintに依存していないため
# 再利用する(新規Research呼び出しはしない)。Writer/Supportは
# er006_pool_pilot_01_writer.py/er006_pool_pilot_01_support.pyの
# blueprint=None(既定値)を明示的に使うことで、既存Topic(No.1〜6)と
# 完全に同一の挙動で再生成する。
#
# 【今回だけの例外】TTS呼び出し方式のみ、検証速度優先で同期
# (client.models.generate_content)を使う(DEV/VALIDATION用)。
# Production標準のGemini Batch APIは変更しない。

from __future__ import annotations

import json
import time

import er008_n7_pilot_run_01 as pilot

THEME_ID = pilot.THEME_ID
OUT_DIR = pilot.OUT_DIR
TITLE_EN = pilot.TITLE_EN
TOPIC_JA = pilot.TOPIC_JA


def run_writer_stage_baseline() -> dict:
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"

    t0 = time.time()
    result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TOPIC_JA, ledger_path, OUT_DIR, blueprint=None)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Baseline Writer完了(blueprint=None)。elapsed={elapsed}s")
    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return result


def run_support_stage_baseline() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_support as support_mod

    client = vfl01.get_client()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    t0 = time.time()
    result = support_mod.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text, blueprint=None)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Baseline Support完了(blueprint=None, comment anchor不使用)。elapsed={elapsed}s")
    return result


if __name__ == "__main__":
    import sys
    import er005_cost_logger as cl
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage == "writer":
        run_writer_stage_baseline()
    elif stage == "support":
        run_support_stage_baseline()
    elif stage == "audio":
        pilot.run_audio_stage()
    else:
        print("usage: er008_n7_baseline_reset_01.py [writer|support|audio]")
