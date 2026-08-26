# -*- coding: utf-8 -*-
# ============================================================
# er009_pool_n4_comment2_fix_01.py
# ============================================================
# ER-009-JA-FOREIGN-TOKEN-GATE-01: pool_n4_supermarket(No.4)のA2
# comment_2は、内部制作ラベル「Part 1」がリスナー向け日本語にそのまま
# 残っていたため、ASR_VALIDATION_UNCERTAIN(Human Review待ち)のまま
# Audio Validation Gateをブロックしていた。ユーザー指示により、
# canonical text(a2_support_texts.json)を「物語の前半では」へ言い換え
# 済み(内容・意味は変更しない)。本スクリプトは、修正後のcomment_2
# だけを再生成し、tts_generation_results.jsonを更新する薄いラッパー
# (既存のgenerate_a2_japanese_with_reading_safety()をそのまま再利用)。
from __future__ import annotations

import json

import er005_cost_logger as cl

cl.install("er006_output/pool_pilot_01/pool_n4_supermarket/a2/audit/pool_n4_qa_sync_raw_usage_log.jsonl")

import er003_v1_n3_01_tts_generate as tg

OUT_DIR_A2 = "er006_output/pool_pilot_01/pool_n4_supermarket/a2"
NARRATION_DIR = f"{OUT_DIR_A2}/narration"
RESULTS_PATH = f"{OUT_DIR_A2}/audit/tts_generation_results.json"


def main():
    support = tg.load_json(f"{OUT_DIR_A2}/a2_support_texts.json")
    results = tg.load_json(RESULTS_PATH)

    text = support["comment_2"]
    print(f"[COMMENT2-FIX][a2] comment_2 再生成(修正後の内容): {text!r}")
    with cl.logging_context("pool_n4_supermarket", "comment2_fix"), cl.segment_context("comment_2"):
        r = tg.generate_a2_japanese_with_reading_safety(
            text, f"{NARRATION_DIR}/comment_2.wav", tg.expected_substring_ja(text))
    results["segments"]["comment_2"] = r
    print(f"[COMMENT2-FIX][a2] comment_2 status={r.get('status')}")
    if r.get("status") != "OK":
        print(f"[COMMENT2-FIX][a2] reason={r.get('reason')}")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_status = {k: v.get("status") for k, v in results["segments"].items()}
    print("[COMMENT2-FIX][a2] segment_status:", json.dumps(all_status, ensure_ascii=False))


if __name__ == "__main__":
    main()
