# ============================================================
# er014_output/user_test_news_convenience_ai_01/convenience_ai/fix_02_pipeline.py
# 管理ID: USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02
#
# 目的: A2 point_two のみを、正式Production経路(既存retry/fallback、
# Ledger→Secondary ASR Phrase List)でユーザー承認のもと再生成する
# (approve_regenerate()で明示承認、新規TTS配線・新規instruction設計は
# しない)。full_story_part2・他segmentは一切呼ばない。
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as ttsgen
import er005_cost_logger as cl
import er011_human_review_lock_01 as review_lock

BASE_DIR = "er014_output/user_test_news_convenience_ai_01/convenience_ai"
A2_DIR = f"{BASE_DIR}/a2"
FIX_AUDIT_DIR = f"{BASE_DIR}/audit_fix_02"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def _update_tts_audit(out_dir: str, seg_name: str, result: dict) -> None:
    tts_results = load_json(f"{out_dir}/audit/tts_generation_results.json")
    tts_results["segments"][seg_name] = result
    save_json(f"{out_dir}/audit/tts_generation_results.json", tts_results)
    run_summary_tts = load_json(f"{out_dir}/run_summary_tts.json")
    run_summary_tts["segment_status"][seg_name] = result.get("status")
    save_json(f"{out_dir}/run_summary_tts.json", run_summary_tts)


def approve_stage() -> dict:
    """A2 point_two のみ、ユーザーREGEN REQUIRED判断に基づきapprove_
    regenerate()を呼ぶ。approve_regenerate()のtextは、実際にguarded
    関数へ渡されるtts_input(tts_safe_news_en適用後)と一致させる
    必要がある(review_lockのcanonical_text_sha256照合のため)。"""
    parts = load_json(f"{A2_DIR}/parts.json")
    text = parts["point_two_body"]
    tts_input = ttsgen.tts_safe_news_en(text)
    out_path = f"{A2_DIR}/narration/point_two.wav"
    entry = review_lock.approve_regenerate(out_path, tts_input, approved_by="user_via_fable_sandwich_pm")
    print(f"[FIX-02][approve] point_two REGENERATE_APPROVED: {entry}")
    save_json(f"{FIX_AUDIT_DIR}/approve_regenerate_result.json", entry)
    return entry


def retts_point_two_stage() -> dict:
    out_dir = A2_DIR
    narration_dir = f"{out_dir}/narration"
    parts = load_json(f"{out_dir}/parts.json")
    name = "point_two"
    text = parts["point_two_body"]
    sub = ttsgen.first_words(text)
    sc.assert_no_point_number_label(text, name)
    tts_input = ttsgen.tts_safe_news_en(text)
    print(f"[FIX-02][retts/a2] {name}生成: {tts_input!r}")
    with cl.segment_context(name):
        r = ttsgen.generate_a2_segment_with_slowdown(
            tts_input, f"{narration_dir}/{name}.wav", sub,
            style_prefix_override=ttsgen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True)
    r["canonical_text"] = text
    _update_tts_audit(out_dir, name, r)
    print(f"[FIX-02][retts/a2] {name} status={r.get('status')} "
          f"classification={r.get('audio_classification')} asr={r.get('asr_text')!r}")
    save_json(f"{FIX_AUDIT_DIR}/retts_a2_point_two_result.json", r)
    return r


STAGE_FUNCS = {
    "approve": approve_stage,
    "retts_point_two": retts_point_two_stage,
}


def main():
    cl.install(f"{BASE_DIR}/raw_usage_log.jsonl")
    stages = sys.argv[1:] or list(STAGE_FUNCS.keys())
    results = {}
    for s in stages:
        if s not in STAGE_FUNCS:
            raise SystemExit(f"unknown stage: {s} (choices={list(STAGE_FUNCS.keys())})")
        results[s] = STAGE_FUNCS[s]()
    return results


if __name__ == "__main__":
    main()
