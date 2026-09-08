# ============================================================
# assemble_runtime_evidence.py
# 管理ID: OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04
# ============================================================
# rerun_04/b1b(point_one/point_two差し替え後、他segmentはrerun_03の
# byte-for-byte reuse)を、既存Production関数
# er003_v1_n3_01_assemble.py::stage_assemble_b1(無変更)で再Assemblyする。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe \
#     er011_output/open112_trend_theme2_b_final_audio_rerun_04/\
#     assemble_runtime_evidence.py
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er003_v1_n3_01_assemble as asm

THEME = {
    "theme_id": "open112_trend_theme2_b_final_audio_rerun_04",
    "out_dir": "er011_output/open112_trend_theme2_b_final_audio_rerun_04",
}


def main():
    summary = asm.stage_assemble_b1(THEME)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
