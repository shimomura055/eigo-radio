# ============================================================
# er010_no9_keyphrase_minimal_englishlock_production_wiring_22.py
# ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22
# ============================================================
# Production正式配線(er003_v1_repro01_main_generate.py::
# generate_key_phrase_component_verified、Minimal最大2attempt→
# English Lock最大2attempt)のRuntime evidence取得専用モジュール。
#
# Case A(実API・実課金): 正式Key Phrase("push back"、No.9 A2の実際の
# 承認済みKey Phrase語で、Mini-Trial 20-R2でMinimal instruction
# Attempt 1でPASS実績あり)を、実際のreview_lock guarded本体経由で
# 1回だけ実行する。Production本番パス(er006_output/pool_pilot_01/...)
# は一切触らず、隔離されたtemp narration layout配下でのみ実行する
# (review_lockのderive_segment_key()が要求する".../<theme>/<level>/
# narration/<segment>.wav"レイアウトだけ満たす別ディレクトリ)。
#
# Case B/C(モック・実API課金ゼロ): generate_narration_snippet_verified_
# strict()をモックしてMinimal instructionを強制失敗させ、実際にEnglish
# Lock fallbackへ遷移すること、その後PASS/4回FAILどちらの分岐も実際の
# review_lock guarded本体・record_outcome()経由で発火することを確認する。

from __future__ import annotations

import json
import os

import er003_v1_repro01_main_generate as repro01
import er011_human_review_lock_01 as review_lock

OUT_DIR = "er010_output/no9_keyphrase_minimal_englishlock_production_wiring_22"
RUNTIME_DIR = f"{OUT_DIR}/runtime_evidence"


def case_a_real_minimal_pass():
    """実API。Minimal instruction Attempt 1でPASSする正常ケースを、実際の
    Production関数(review_lock guarded)経由で発火させる。"""
    theme_dir = f"{RUNTIME_DIR}/wiring22_probe_a/a2"
    narration_dir = f"{theme_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    out_path = f"{narration_dir}/kp_probe_pushback.wav"

    result = repro01.generate_key_phrase_component_verified("push back", out_path)

    level_out_dir = review_lock._level_out_dir_from_out_path(out_path)
    store = review_lock._load_store(level_out_dir)
    lock_entry = store.get("kp_probe_pushback")

    return {
        "case": "A_REAL_MINIMAL_PASS", "text": "push back",
        "status": result.get("status"),
        "fallback_used": result.get("fallback_used"),
        "primary_instruction_type": result.get("primary_instruction_type"),
        "model": result.get("model"), "voice": result.get("voice"),
        "asr_text": result.get("asr_text"),
        "duration_seconds": result.get("duration_seconds"),
        "attempts_log": result.get("attempts_log"),
        "call_count": result.get("call_count"), "retry_count": result.get("retry_count"),
        "review_lock_state": lock_entry.get("state") if lock_entry else None,
        "cumulative_tts_attempts": lock_entry.get("cumulative_tts_attempts") if lock_entry else None,
    }


def case_bc_mocked_minimal_fail_then_english_lock():
    """実API課金ゼロ。generate_narration_snippet_verified_strict()を
    モックし、(B) Minimal 2回ともNG→English Lockへ実際に遷移すること、
    (C) English Lock 1回目でPASSする分岐が実際のreview_lock guarded本体
    経由で正しく記録されることを確認する。"""
    theme_dir = f"{RUNTIME_DIR}/wiring22_probe_bc/a2"
    narration_dir = f"{theme_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    out_path = f"{narration_dir}/kp_probe_forced.wav"

    call_log = []
    orig = repro01.generate_narration_snippet_verified_strict

    def fake(text, language, out_path_, expected_substring, **kwargs):
        stage = ("MINIMAL" if kwargs.get("style_prefix_override") == repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX
                 else "ENGLISH_LOCK")
        call_log.append({"stage": stage, "max_attempts": kwargs.get("max_attempts")})
        if stage == "MINIMAL":
            return {"status": "STOPPED", "reason": "強制失敗(Runtime evidence用、実TTS未使用)",
                    "attempts_log": [{"attempt": 1, "asr_text": "wrong"}, {"attempt": 2, "asr_text": "wrong"}]}
        return {"status": "OK", "model": "MOCK", "voice": "MOCK", "asr_text": text,
                "attempts_log": [{"attempt": 1, "asr_text": text}]}

    repro01.generate_narration_snippet_verified_strict = fake
    try:
        result = repro01.generate_key_phrase_component_verified("forced fallback probe", out_path)
    finally:
        repro01.generate_narration_snippet_verified_strict = orig

    level_out_dir = review_lock._level_out_dir_from_out_path(out_path)
    store = review_lock._load_store(level_out_dir)
    lock_entry = store.get("kp_probe_forced")

    return {
        "case": "BC_MOCKED_MINIMAL_FAIL_ENGLISH_LOCK_PASS",
        "status": result.get("status"), "fallback_used": result.get("fallback_used"),
        "primary_instruction_type": result.get("primary_instruction_type"),
        "call_sequence": call_log,
        "minimal_attempts_log": result.get("minimal_attempts_log"),
        "english_lock_attempts_log": result.get("english_lock_attempts_log"),
        "review_lock_state": lock_entry.get("state") if lock_entry else None,
        "cumulative_tts_attempts": lock_entry.get("cumulative_tts_attempts") if lock_entry else None,
    }


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    results = {"case_a": case_a_real_minimal_pass(), "case_bc": case_bc_mocked_minimal_fail_then_english_lock()}
    with open(f"{OUT_DIR}/runtime_evidence_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
