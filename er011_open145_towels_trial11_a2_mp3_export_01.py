# ============================================================
# er011_open145_towels_trial11_a2_mp3_export_01.py
# 管理ID: PM-CLOSEOUT-CONSOLIDATION-84-OPEN145-OPEN146-WIRING-AND-A2-DISTRIBUTION
# ============================================================
# 目的: タオルTrial-11 A2完成episode(OPEN-145配線後のcomment_2/meaning_4
# resync・A2 Assembly PASS[`OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-
# PRODUCTION-WIRING-01_REPORT.md`5-2節]済み)の最終wavから、B1B側で既に
# 前例のあるsoundfile MP3書き出し(`er011_discovery_generalization_towels_
# trial_11_audio_03_b1b_individual_approval_and_assemble_01.py::
# step6_export_mp3()`、元は`er003_v1_b1_scaffold_audio_01_generate.py`)を
# 再利用し、ユーザー配布用mp3を追加生成する。
#
# 既存Production assemble関数(`er003_v1_n3_01_assemble.stage_assemble_a2`)
# 自体は無変更・再実行しない(既存A2 assembled wavをそのまま読み込むだけ)。
# 新規TTS/ASR API呼び出しは一切行わない(¥0)。
from __future__ import annotations

import json
import os

A2_DIR = "er011_output/discovery_generalization_towels_trial_11/a2"
WAV_PATH = f"{A2_DIR}/assembled/English_Your_Way_A2_DISCOVERY_GENERALIZATION_TOWELS_TRIAL_11.wav"
MP3_PATH = f"{A2_DIR}/assembled/English_Your_Way_A2_DISCOVERY_GENERALIZATION_TOWELS_TRIAL_11.mp3"


def export_mp3() -> dict:
    import soundfile as sf
    data, sr = sf.read(WAV_PATH)
    sf.write(MP3_PATH, data, sr, format="MP3")
    wav_bytes = os.path.getsize(WAV_PATH)
    mp3_bytes = os.path.getsize(MP3_PATH)
    result = {"wav_path": WAV_PATH, "mp3_path": MP3_PATH, "wav_bytes": wav_bytes, "mp3_bytes": mp3_bytes,
              "sample_rate": sr}
    print(f"[A2-MP3-EXPORT] {MP3_PATH} ({mp3_bytes} bytes, from {wav_bytes} bytes wav)")
    return result


if __name__ == "__main__":
    r = export_mp3()
    os.makedirs(f"{A2_DIR}/audit", exist_ok=True)
    with open(f"{A2_DIR}/audit/a2_mp3_export_01_result.json", "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
