# ============================================================
# er011_open112_theme2_audio_review_fix_02_regenerate.py
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 サブタスクA
# ============================================================
# 目的: 診断で確定した2件の実在する音声重複バグ(A2 Point Two、
# A2 In One Line、いずれもTrial-13時点のTTS生成自体でGemini TTSが
# 一文まるごと逐語反復するhallucinationを起こし、既存ASR/disfluency QA
# の両方をすり抜けていたことをruntime evidenceで確認済み)を、
# 既存Production関数(er003_v1_n3_01_tts_generate.generate_a2_segment_
# with_slowdown、無変更・パラメータもProduction呼び出しと同一)を
# そのまま呼び直すことで再生成する。
#
# 本スクリプトは新しいValidator原則・判定ロジックを一切追加しない
# (existing production function をそのまま呼ぶだけ)。生成後の追加
# 検証(複数回ASR再確認+windowed再ASR+spectral self-similarity)は、
# この修正作業自体のGate 3 runtime evidence取得のためであり、
# Production Validatorへの新規配線ではない。
#
# 対象外(範囲外): B1 Full Story Part 1は診断の結果、現状のrerun-02
# audioに重複を確認できなかったため、本スクリプトでは再生成しない
# (再現しない症状を勝手に「直した」と主張しない)。

from __future__ import annotations

import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_tts_generate as n3_tts
import er005_cost_logger as cl

OUT_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_02/a2"
NARRATION_DIR = f"{OUT_DIR}/narration"
BACKUP_DIR = f"{OUT_DIR}/audit/pre_fix_buggy_audio_backup"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    cl.install(f"{OUT_DIR}/../fix02_regenerate_usage_log.jsonl")
    parts = load_json(f"{OUT_DIR}/parts.json")
    os.makedirs(BACKUP_DIR, exist_ok=True)

    targets = [
        ("point_two", parts["point_two_body"]),
        ("in_one_line", parts["in_one_line"]),
    ]

    # 修正前の(重複入り)音声をevidenceとして退避保存(上書きされる前に)。
    for name, _text in targets:
        for suffix in ("", "_original"):
            src = f"{NARRATION_DIR}/{name}{suffix}.wav"
            if os.path.exists(src):
                shutil.copyfile(src, f"{BACKUP_DIR}/{name}{suffix}_BUGGY_PRE_FIX.wav")

    results_path = f"{OUT_DIR}/audit/tts_generation_results.json"
    all_results = load_json(results_path)

    regen_log = {}
    for name, text in targets:
        tts_input = n3_tts.tts_safe_news_en(text)
        sub = n3_tts.first_words(text)
        out_path = f"{NARRATION_DIR}/{name}.wav"
        print(f"[FIX02] {name} 再生成開始(Production関数を無変更で再呼び出し)...")
        result = n3_tts.generate_a2_segment_with_slowdown(
            tts_input, out_path, sub,
            style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
            disfluency_qa=(name == "in_one_line"),
        )
        result["canonical_text"] = text
        print(f"[FIX02] {name} status={result.get('status')} "
              f"asr_verified={result.get('asr_verified')} "
              f"classification={result.get('audio_classification')} "
              f"post_slowdown_classification={result.get('post_slowdown_classification')}")
        regen_log[name] = result
        all_results["segments"][name] = result

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{OUT_DIR}/audit/fix02_regeneration_log.json", "w", encoding="utf-8") as f:
        json.dump(regen_log, f, ensure_ascii=False, indent=2, default=str)

    print("[FIX02] 完了。")
    return regen_log


if __name__ == "__main__":
    main()
