# ============================================================
# er003_v1_iran01_b1_kp_homophone_fix.py
# ER-003-IRAN-A2-B1-01: Key Phrase 1(strait/海峡)・4(応酬/押収)の
# ASR同音異義語ambiguity対応(ADD03 meaning_3と同種の既知パターン)
# ============================================================
# kp1英語"strait"はASRが同音異義語"straight"として書き起こす、
# kp4日本語"言葉で応酬する"はASRが同音異義語"言葉で押収する"
# (応酬/押収はどちらも「おうしゅう」)として書き起こす既知パターン。
# TTS音声自体は正常である可能性が高いが、ADD03の前例に倣い、機械QAの
# みでは確定とせず、最終報告でhuman review(ユーザー試聴)を明示的に
# 求める形で扱う。kp1日本語"海峡"は明確な同音異義語候補が出ていない
# ため、まず追加試行する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_b1_kp_homophone_fix.py

from __future__ import annotations

import json

import er003_v1_iran01_articles_generate as gen
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = f"{gen.OUT_DIR}/b1"
NARRATION_DIR = f"{OUT_DIR}/narration"


def main():
    results = {}

    print("[IRAN01-B1-KP-HOMOPHONE] kp1_ja(海峡)追加試行...")
    kp1_ja_path = f"{NARRATION_DIR}/kp1_ja_charon.wav"
    r = voice01.generate_charon_japanese("海峡", kp1_ja_path, "海峡", max_attempts=10)
    results["kp1_ja_retry"] = r
    print(f"[IRAN01-B1-KP-HOMOPHONE] kp1_ja: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/kp_homophone_fix_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("完了。")


if __name__ == "__main__":
    main()
