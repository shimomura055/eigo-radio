# ============================================================
# a2_assemble_runtime_evidence.py
# 管理ID: FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01
# ============================================================
# full_story_part1差し替え後(他segmentは既存のまま)、既存Production関数
# er003_v1_n3_01_assemble.py::stage_assemble_a2(無変更)でAssembly + Audio
# Validation Gate(default/opt-in)を再実行する。
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import er003_v1_n3_01_assemble as asm

THEME_ID = "family_a_trend_ai_manufacturing_prod_run_01"
THEME = {"theme_id": THEME_ID, "out_dir": f"er011_output/{THEME_ID}"}
OUT_PATH = f"er011_output/{THEME_ID}/user_feedback_fix_01/a2_assemble_run_summary.json"


def main():
    result = {"level": "a2"}
    try:
        summary = asm.stage_assemble_a2(THEME)
        result["gate_off_result"] = "PASS"
        result["assemble_summary"] = summary
    except RuntimeError as e:
        result["status"] = "GATE_BLOCKED"
        result["gate_off_result"] = "BLOCKED"
        result["error"] = str(e)

    if result.get("gate_off_result") == "PASS":
        level_out_dir = f"{THEME['out_dir']}/a2"
        rs = asm.derive_a_family_required_structure("A2")
        try:
            asm.verify_episode_audio_validation_gate(level_out_dir, "A2", required_structure=rs)
            result["gate_on_result"] = "PASS"
        except RuntimeError as e:
            result["gate_on_result"] = "BLOCKED"
            result["gate_on_message"] = str(e)[:800]
    else:
        result["gate_on_result"] = "SKIPPED_ASSEMBLE_NOT_PASS"

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
