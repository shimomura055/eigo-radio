# ============================================================
# er021_output/coverage_review_02/runtime_evidence_live_tts_asr_01_run.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(Phase 2)
# ============================================================
# 目的: strict版Tier1合成規則(diff-anchored比較+punctuation由来局所差分
# 吸収)実装後のer021_en_asr_semantic_equivalence_production_01が、実際の
# TTS(1回)+実ASR(1回)を経由した本物のProduction呼び出し経路
# (er003_v1_repro01_main_generate.generate_narration_snippet_verified_
# strict、role gating込みのval.classify_asr_match)で発火することを、
# end-to-endの実runtime evidenceとして記録する(Guardrail ¥15、
# evidenceモード)。
#
# 安全設計(er025_pronunciation_resolution_phase4_a2_fallback_evidence_01_
# runと同じ手法):
#   - out_pathを".../narration/<segment>.wav"という標準命名慣習に
#     意図的に従わせない(下記OUT_PATH)。これによりHuman Review Lock
#     機構(review_lock_state.json)・attempt audio保存のいずれも一切
#     読み書きしない(assert文で二重に確認)。
#   - 出力先はer021_output/coverage_review_02/のみ(既存Production run
#     dir・Lock stateは非接触)。
#   - TTS_EXECUTION_MODE=STANDARD(同期実行)を明示的に強制する。
#   - max_attempts=1(実TTS 1回+実ASR 1回のみに限定、¥5前後を想定)。
#   - tts_backend既定("structured_separation")のまま(Flash-Lite関連
#     ファイルは一切importしない、衝突回避)。
#   - segment_id="full_story_part1"(role=FULL_STORY、Tier1適用対象)を
#     明示的に渡す。
#
# 実行方法:
#   .venv/Scripts/python.exe er021_output/coverage_review_02/runtime_evidence_live_tts_asr_01_run.py
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, ".")
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import er003_b1_p9a_audio as p9a  # noqa: E402
import er003_v1_repro01_main_generate as repro01  # noqa: E402
import er005_cost_logger as cost_logger  # noqa: E402
import er006_asr_provider_routing_01 as routing  # noqa: E402
import er006_preprod_hardening_01_validation as val  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402

OUT_DIR = "er021_output/coverage_review_02"
cost_logger.init_logger(f"{OUT_DIR}/runtime_evidence_live_cost_log.jsonl")
# "narration"という名前を意図的に避ける(Lock機構を構造的に無効化する)。
AUDIO_DIR = f"{OUT_DIR}/live_evidence_audio_not_narration_layout"
os.makedirs(AUDIO_DIR, exist_ok=True)
OUT_PATH = f"{AUDIO_DIR}/full_story_part1_run2.wav"

# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02の対象パターン
# (番号ラベル"Part One"、Hormuz"Act One"実例と同型)を含む短い実テキスト
# (コスト抑制のため最小限の長さにする)。1回目(runtime_evidence_live_tts_
# asr_01_result.json、U.S.パターン)ではASRが句読点を保持したため新規則の
# 発火までは確認できなかった(既存Tier1の完全一致経路でPASS)。2回目として
# 番号ラベルパターンを追加試行する。
CANONICAL_TEXT = (
    "The report is divided into three parts. Part One covers the background."
)


def _json_default(o):
    return str(o)


def main() -> None:
    assert not review_lock._has_valid_narration_layout(OUT_PATH), (
        "安全ガード: OUT_PATHがnarration層構造に一致してしまっている(Human Review Lock誤操作の恐れ)。"
        "評価を中止する。")

    started_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    result = repro01.generate_narration_snippet_verified_strict.__wrapped__(
        CANONICAL_TEXT, "en", OUT_PATH, "The report is divided",
        max_attempts=1, segment_id="full_story_part1")
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    # 独立してTier1(strict版合成規則)を直接呼び、absorbed_ops/diff_anchored
    # の内訳をそのまま記録する(result自体が既にProduction wrapper経由の
    # 判定結果を含むが、attempts_logのasr_textを使って明示的に再確認する)。
    attempts_log = result.get("attempts_log", [])
    tier1_reclassify = None
    if attempts_log:
        last_asr_text = attempts_log[-1].get("asr_text")
        if last_asr_text:
            reclass = val.classify_asr_match(CANONICAL_TEXT, last_asr_text, segment_id="full_story_part1")
            tier1_reclassify = {
                "classification": reclass.classification,
                "should_pass": reclass.should_pass,
                "semantic_equivalence_info": reclass.semantic_equivalence_info,
            }

    evidence = {
        "management_id": "EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02",
        "purpose": "strict版Tier1合成規則(diff-anchored+punctuation局所差分吸収)の実TTS+実ASR end-to-end runtime evidence",
        "started_at": started_at,
        "finished_at": finished_at,
        "env": {"TTS_EXECUTION_MODE": os.environ.get("TTS_EXECUTION_MODE")},
        "model_id_en_tts": p9a.ENGLISH_MODEL_NAME,
        "voice": p9a.VOICE_NAME,
        "asr_provider_routing": getattr(routing, "describe_active_provider", lambda: "unknown")()
        if hasattr(routing, "describe_active_provider") else None,
        "tts_backend": "structured_separation (既定、Flash-Lite非対象)",
        "segment_id": "full_story_part1",
        "out_path": OUT_PATH,
        "narration_layout_detected": review_lock._has_valid_narration_layout(OUT_PATH),
        "canonical_text": CANONICAL_TEXT,
        "result_status": result.get("status"),
        "attempts_log": attempts_log,
        "tier1_reclassify_via_production_wrapper": tier1_reclassify,
    }
    out_json_path = f"{OUT_DIR}/runtime_evidence_live_tts_asr_01_result_run2.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2, default=_json_default)

    print(f"[evidence] wrote {out_json_path}")
    print(f"[evidence] narration_layout_detected={evidence['narration_layout_detected']} (Falseであることを期待)")
    print(f"[evidence] result.status={result.get('status')}")
    for a in attempts_log:
        print(f"[evidence] attempt={a.get('attempt')} asr_text={a.get('asr_text')!r} "
              f"audio_classification={a.get('audio_classification')}")
    print(f"[evidence] tier1_reclassify_via_production_wrapper={tier1_reclassify}")


if __name__ == "__main__":
    main()
