# ============================================================
# full_story_part1_a2_regen_runtime_evidence.py
# 管理ID: OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01
# ============================================================
# 実行方法(root直下から):
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#     er011_output/open112_trend_theme2_b_final_audio_rerun_04/\
#     full_story_part1_a2_regen_runtime_evidence.py
#
# 目的: er011_open112_theme2_a2_numeric_minimal_fix_rerun_04.pyで24.1%→
# about 24%へ決定的置換したparts.json(part1)を、現行Productionの実生成
# 関数(er003_v1_n3_01_tts_generate.py::generate_a2_segments()がfull_story_
# part1に対して実際に使っているのと同一の
# generate_a2_segment_with_slowdown(style_prefix_override=
# A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=False,
# enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)
# の組み合わせ)へ通し、narration/full_story_part1.wavのみ上書きする
# (他segmentは一切呼ばない)。TTS/ASR経路自体は無変更(既存Production
# 関数をそのまま呼ぶだけ)。
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er005_cost_logger as cl
import er003_v1_n3_01_tts_generate as n3

OUT_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2"
NARRATION_DIR = f"{OUT_DIR}/narration"
PARTS_PATH = f"{OUT_DIR}/parts.json"
TTS_RESULTS_PATH = f"{OUT_DIR}/audit/tts_generation_results.json"
COST_LOG_PATH = "er011_output/open112_trend_theme2_b_final_audio_rerun_04/raw_usage_log_a2.jsonl"
RUN_SUMMARY_PATH = (
    "er011_output/open112_trend_theme2_b_final_audio_rerun_04/full_story_part1_a2_regen_run_summary.json"
)

TARGET_NAME = "full_story_part1"
TARGET_FIELD = "part1"


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD", (
        "TTS_EXECUTION_MODE=STANDARD を明示的に指定して実行すること"
        "(タスク仕様: Standard同期を明示)。"
    )
    parts = json.load(open(PARTS_PATH, encoding="utf-8"))
    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))

    cl.install(COST_LOG_PATH)

    canonical_text = parts[TARGET_FIELD]
    assert "24.1%" not in canonical_text and "about 24%" in canonical_text, (
        "置換後テキストが想定と異なります(about 24%が見つかりません)。"
    )
    tts_input = n3.tts_safe_news_en(canonical_text)
    sub = n3.first_words(parts[TARGET_FIELD])
    out_path = f"{NARRATION_DIR}/{TARGET_NAME}.wav"
    old_sha256 = sha256_of(out_path) if os.path.exists(out_path) else None

    t0 = time.time()
    with cl.logging_context(
        "OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01", "full_story_part1_a2_regen"
    ), cl.segment_context(TARGET_NAME):
        # er003_v1_n3_01_tts_generate.py::generate_a2_segments()が
        # full_story_part1に対して実際に渡している引数と同一
        # (style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER、
        # disfluency_qa=False既定、enable_connected_speech_equivalence_
        # layer=True、enable_repetition_qa=True)。
        result = n3.generate_a2_segment_with_slowdown(
            tts_input, out_path, sub,
            style_prefix_override=n3.A2_ENGLISH_STYLE_PREFIX_SLOWER,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True,
        )
    elapsed = time.time() - t0

    assert result.get("status") == "OK", (
        f"{TARGET_NAME}の生成がstatus={result.get('status')}で終了しました。"
        "Human Review Lock等が発動した可能性があるため、承認代行せず停止します。"
        f" result={result}"
    )

    new_sha256 = sha256_of(out_path)
    result["canonical_text"] = canonical_text
    result["sha256"] = new_sha256
    result["source_note"] = (
        "OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01: "
        "Part 1で確認した現行Production Evidence Compression Editorの"
        "実データ(24.1%->about 24%)に基づき、parts.json[part1]の"
        "24.1%->about 24%を決定的置換(Editor再実行なし、Theme 2 B1"
        "rerun_04と同一手順)した後、現行Production関数"
        "(generate_a2_segment_with_slowdown、"
        "style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER、"
        "enable_connected_speech_equivalence_layer=True、"
        "enable_repetition_qa=True)で再生成した。"
    )
    tts_results["segments"][TARGET_NAME] = result

    full_result_snapshot = json.loads(json.dumps(result, ensure_ascii=False, default=str))
    summary = {
        "full_result": full_result_snapshot,
        "segment": TARGET_NAME,
        "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"),
        "canonical_text": canonical_text,
        "tts_input": tts_input,
        "out_path": out_path,
        "elapsed_seconds": round(elapsed, 2),
        "status": result.get("status"),
        "voice": result.get("voice"),
        "asr_verified": result.get("asr_verified"),
        "asr_text": result.get("asr_text"),
        "audio_classification": result.get("audio_classification"),
        "connected_speech_info": result.get("connected_speech_info"),
        "disfluency_checked": result.get("disfluency_checked"),
        "repetition_qa_checked": result.get("repetition_qa_checked"),
        "repetition_qa_evidence": result.get("repetition_qa_evidence"),
        "slowdown_attempts_log": result.get("slowdown_attempts_log"),
        "old_sha256": old_sha256,
        "new_sha256": new_sha256,
        "attempts_log_summary": [
            {
                "attempt": a.get("attempt"), "status": a.get("status"),
                "verified": a.get("verified"),
                "repetition_qa_checked": a.get("repetition_qa_checked"),
                "repetition_qa_flagged": (
                    (a.get("repetition_qa_evidence") or {}).get("flagged")
                    if a.get("repetition_qa_evidence") else None
                ),
                "method_d_prime_best_run_seconds": (
                    ((a.get("repetition_qa_evidence") or {})
                     .get("method_d_prime_spectral_short_lag") or {}).get("best_run_length_seconds")
                    if a.get("repetition_qa_evidence") else None
                ),
            }
            for a in (result.get("attempts_log") or [])
        ],
    }

    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    with open(RUN_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    print(f"\n[full_story_part1_a2_regen] summary -> {RUN_SUMMARY_PATH}")
    print(f"[full_story_part1_a2_regen] tts_generation_results.json更新 -> {TTS_RESULTS_PATH}")


if __name__ == "__main__":
    main()
