# ============================================================
# assemble_revision3.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続)
# ============================================================
# revision3a(point_one.wav再生成、ASR照合PASS)を含むfact03_fix_02/b1bを、
# 既存Production Assembly関数(er003_v1_n3_01_assemble.py::stage_assemble_b1)
# でそのまま組み立てる。Gate OFF経路(既定)で成功後、opt-in構造完全性
# Gate(derive_a_family_required_structure + verify_episode_audio_
# validation_gate)を追加で確認する
# (er011_family_a_completion_a2_trend_end_to_end_01_run.pyと同一パターン)。
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er003_v1_n3_01_assemble as asm

THEME_ID = "household"
OUT_DIR = "er003_output/n3_01/household/fact03_fix_02"
B1_OUT_DIR = f"{OUT_DIR}/b1b"
SUMMARY_PATH = "er011_output/open138_household_fact03_b1b_minimal_fix_02/assemble_revision3_summary.json"


def main():
    assemble_result = None
    gate_off_result = None
    try:
        assemble_result = asm.stage_assemble_b1({"theme_id": THEME_ID, "out_dir": OUT_DIR})
        gate_off_result = "PASS"
    except RuntimeError as e:
        assemble_result = {"status": "GATE_BLOCKED", "error": str(e)}
        gate_off_result = "BLOCKED"
    print(f"[ASSEMBLE-REVISION3] Gate OFF経路結果: {gate_off_result}")

    gate_on_result = None
    if gate_off_result == "PASS":
        rs = asm.derive_a_family_required_structure("B1")
        try:
            asm.verify_episode_audio_validation_gate(B1_OUT_DIR, "B1", required_structure=rs)
            gate_on_result = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            gate_on_result = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:1500]}
    else:
        gate_on_result = {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    print(f"[ASSEMBLE-REVISION3] Gate opt-in ON経路結果: {gate_on_result.get('gate_on_result')}")

    summary = {
        "assemble_result": assemble_result,
        "gate_off_result": gate_off_result,
        "gate_opt_in_result": gate_on_result,
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(summary, ensure_ascii=True, indent=2, default=str))
    print(f"\n[assemble_revision3] -> {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
