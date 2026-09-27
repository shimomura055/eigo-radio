# ============================================================
# er025_pronunciation_resolution_phase4_a2_fallback_evidence_01_run.py
# PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-
# LIKE-01: A-2(A2 fallback経路EN resolver配線)のruntime evidence
# ============================================================
# 目的: er003_v1_crosslevel_audio_02_common._run_a2_minimal_fallback_
# attempt()へ配線したenable_pronunciation_resolver=True(A-2)が、実際の
# TTS/ASRパイプラインで発火することを、small_bag A2 full_story_part2の
# 実canonical text(Stage 3e、RESULT_PACKET_FXD1で診断対象になった実データ)
# を使って確認する。
#
# 安全設計(Guardrail ¥15、evidenceモード、Human Review Lock解除は行わない):
#   - out_pathを".../narration/<segment>.wav"という標準命名慣習に
#     **意図的に従わせない**(下記OUT_PATH参照)。これにより
#     er011_human_review_lock_01._has_valid_narration_layout()がFalseを
#     返し、Human Review Lock機構(review_lock_state.json)・attempt
#     audio保存(save_tts_attempt_audio)のいずれも一切読み書きしない
#     (assert文でも二重に確認する)。
#   - 出力先はer025_output/phase4_evidence_01/のみ(既存Production run
#     dir[er019_output/.../small_bag__run_02/]・Lock stateは非上書き)。
#   - ALLOW_PRONUNCIATION_WEB_LOOKUP=0(cache-only)を明示的に強制する
#     (Perplexity等の有料web lookupを一切発生させない)。
#   - TTS_EXECUTION_MODE=STANDARD(同期呼び出し)を明示的に強制する。
#   - 標準経路(generate_narration_snippet_verified_strict)は実TTS/ASRを
#     呼ばずSTOPPED(標準2回消費相当)を即座に返すようmockする(既存
#     unittest[er007_ja_tts_retry_path_fix_test_01.py等]と同じ手法)。
#     これによりfallback_budget=1となり、fallback(minimal instruction)
#     経路の実TTS+実ASRが正確に1回だけ実行される(retry予算は本evidence
#     で1 attemptに限定)。
#   - API呼び出し: 実TTS 1回+実ASR 1回のみ(Perplexity web lookupは
#     ALLOW_PRONUNCIATION_WEB_LOOKUP=0のため呼ばれない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er025_pronunciation_resolution_phase4_a2_fallback_evidence_01_run.py
from __future__ import annotations

import json
import os
import time
from unittest import mock

# 呼び出し先モジュールがos.environ.get()を呼び出し時(import時ではなく)に
# 読むことをコードで確認済み(resolve_tts_execution_mode/_web_lookup_
# allowed)。import前に設定して確実に反映させる。
os.environ["ALLOW_PRONUNCIATION_WEB_LOOKUP"] = "0"
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import er003_b1_p9a_audio as p9a  # noqa: E402
import er003_v1_crosslevel_audio_02_common as crosslevel_common  # noqa: E402
import er005_cost_logger as cost_logger  # noqa: E402
import er006_asr_provider_routing_01 as routing  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402

OUT_DIR = "er025_output/phase4_evidence_01"
cost_logger.init_logger(f"{OUT_DIR}/cost_log.jsonl")
# "narration"という名前を意図的に避ける(Lock機構を構造的に無効化する)。
AUDIO_DIR = f"{OUT_DIR}/audio_not_narration_layout"
os.makedirs(AUDIO_DIR, exist_ok=True)
OUT_PATH = f"{AUDIO_DIR}/full_story_part2.wav"

# small_bag A2 full_story_part2の実canonical text(Stage 3e、
# er019_output/family_x_audio_production_wiring_01/
# family_x_b3_diversity_trial_01/small_bag__run_02/a2/audit/
# tts_generation_results.json、segments.full_story_part2.canonical_text
# より転記。RESULT_PACKET_FXD1の診断対象そのもの)。
CANONICAL_TEXT = (
    "ELLE included mini bags among its fall and winter 2026 style trends. "
    "Its examples included Khaite’s palm-sized evening clutch and "
    "Chanel’s novelty minaudière. They mostly hold the basics: "
    "a phone, wallet, keys, and lip products. They cannot compete with "
    "roomy bags for storage. Their job is visual. They add a special "
    "feeling. They say, “This is today’s mood.”\n\n"
    "We see the season more clearly by looking at bags beside them.")

FAKE_STANDARD_RESULT = {
    "status": "STOPPED",
    "reason": ("runtime evidence: 標準経路2回相当を人為的にSTOPPEDとしfallbackへ"
               "強制進入させるためのmock(実TTS/ASR呼び出しは発生しない)"),
    "attempts_log": [
        {"attempt": 1, "status": "OK", "audio_classification": "TRUE_CONTENT_MISMATCH"},
        {"attempt": 2, "status": "OK", "audio_classification": "TRUE_CONTENT_MISMATCH"},
    ],
}


def _json_default(o):
    return str(o)


def main() -> None:
    assert not review_lock._has_valid_narration_layout(OUT_PATH), (
        "安全ガード: OUT_PATHがnarration層構造に一致してしまっている(Human Review Lock誤操作の恐れ)。"
        "評価を中止する。")

    started_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    with mock.patch.object(crosslevel_common, "generate_narration_snippet_verified_strict",
                            return_value=dict(FAKE_STANDARD_RESULT)) as mock_std:
        result = crosslevel_common.generate_english_segment_with_fallback(
            CANONICAL_TEXT, OUT_PATH, "ELLE included mini bags", max_attempts=3)
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    evidence = {
        "management_id": "PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01",
        "purpose": "A-2: A2 fallback経路(_run_a2_minimal_fallback_attempt)のEN resolver実発火runtime evidence",
        "started_at": started_at,
        "finished_at": finished_at,
        "env": {
            "ALLOW_PRONUNCIATION_WEB_LOOKUP": os.environ.get("ALLOW_PRONUNCIATION_WEB_LOOKUP"),
            "TTS_EXECUTION_MODE": os.environ.get("TTS_EXECUTION_MODE"),
        },
        "model_id_en_tts": p9a.ENGLISH_MODEL_NAME,
        "voice": p9a.VOICE_NAME,
        "asr_provider_routing": getattr(routing, "describe_active_provider", lambda: "unknown")()
        if hasattr(routing, "describe_active_provider") else None,
        "standard_path_mocked": True,
        "standard_path_mock_call_count": mock_std.call_count,
        "out_path": OUT_PATH,
        "narration_layout_detected": review_lock._has_valid_narration_layout(OUT_PATH),
        "canonical_text": CANONICAL_TEXT,
        "result": result,
    }
    out_json_path = f"{OUT_DIR}/evidence_result.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2, default=_json_default)

    print(f"[evidence] wrote {out_json_path}")
    print(f"[evidence] narration_layout_detected={evidence['narration_layout_detected']} (Falseであることを期待)")
    print(f"[evidence] result.status={result.get('status')} fallback_used={result.get('fallback_used')}")
    print(f"[evidence] result.fallback_en_pronunciation_resolver_info="
          f"{result.get('fallback_en_pronunciation_resolver_info')}")
    fb_log = result.get("fallback_attempts_log") or []
    for a in fb_log:
        print(f"[evidence] fallback_attempts_log[{a.get('attempt')}]: "
              f"status={a.get('status')} audio_classification={a.get('audio_classification')} "
              f"en_pronunciation_resolver_info={a.get('en_pronunciation_resolver_info')}")


if __name__ == "__main__":
    main()
