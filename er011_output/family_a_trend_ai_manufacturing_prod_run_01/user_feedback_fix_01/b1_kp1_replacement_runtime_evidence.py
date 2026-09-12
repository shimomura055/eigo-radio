# ============================================================
# b1_kp1_replacement_runtime_evidence.py
# 管理ID: FAMILY-A-TREND-AI-MANUFACTURING-USER-LISTENING-FEEDBACK-FIX-01
# ============================================================
# 目的: b1b/key_phrases/keywords_canonicalized.json rank1を
# 'not there yet' -> 'autonomous' へ手動差し替え済み(このscriptの外で
# 編集済み、既存Production canonicalization関数は再実行しない=ユーザー
# 指定の個別差替)の後、既存Production関数
# er003_v1_n3_01_tts_generate.py::generate_b1_segments()がKey Phrase 1に
# 実際に渡しているのと同一の呼び出し
# (shared_narration.ensure_key_phrase_english_component /
# generate_charon_japanese_with_reading_safety、いずれも無変更)で
# kp1_en.wav / kp1_ja_charon.wavのみ再生成する(他segmentは呼ばない)。
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er005_cost_logger as cl
import er003_v1_n3_01_tts_generate as n3

THEME_ID = "family_a_trend_ai_manufacturing_prod_run_01"
OUT_DIR = f"er011_output/{THEME_ID}/b1b"
NARRATION_DIR = f"{OUT_DIR}/narration"
KP_PATH = f"{OUT_DIR}/key_phrases/keywords_canonicalized.json"
TTS_RESULTS_PATH = f"{OUT_DIR}/audit/tts_generation_results.json"
COST_LOG_PATH = f"er011_output/{THEME_ID}/user_feedback_fix_01/raw_usage_log_b1_kp1_fix.jsonl"
RUN_SUMMARY_PATH = f"er011_output/{THEME_ID}/user_feedback_fix_01/b1_kp1_replacement_run_summary.json"

RANK = 1


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    assert os.environ.get("TTS_EXECUTION_MODE", "").upper() == "STANDARD"

    kp = json.load(open(KP_PATH, encoding="utf-8"))
    item = next(it for it in kp["items"] if it["rank"] == RANK)
    assert item["used_form"] == "autonomous", f"rank{RANK}のused_formが想定外です: {item['used_form']!r}"

    used_form = item["used_form"]
    ja_gloss = item["japanese_gloss"]
    ja_gloss_tts, ja_gloss_tts_fallback = n3.resolve_key_phrase_ja_gloss_tts(item)

    cl.install(COST_LOG_PATH)

    en_path = f"{NARRATION_DIR}/kp{RANK}_en.wav"
    ja_path = f"{NARRATION_DIR}/kp{RANK}_ja_charon.wav"
    old_en_sha = sha256_of(en_path) if os.path.exists(en_path) else None
    old_ja_sha = sha256_of(ja_path) if os.path.exists(ja_path) else None

    with cl.logging_context(THEME_ID, "b1_kp1_replacement"), cl.segment_context(f"kp{RANK}_english"):
        en_r = n3.shared_narration.ensure_key_phrase_english_component(
            n3.tts_safe_kp_en(used_form), en_path)

    with cl.logging_context(THEME_ID, "b1_kp1_replacement"), cl.segment_context(f"kp{RANK}_japanese"):
        ja_r = n3.generate_charon_japanese_with_reading_safety(
            ja_gloss_tts, ja_path, n3.expected_substring_ja(ja_gloss_tts),
            known_key_phrase_terms=[used_form])
    ja_r["display_gloss"] = ja_gloss
    ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback

    assert en_r.get("status") == "OK", f"kp{RANK}_en生成がstatus={en_r.get('status')}で終了しました。result={en_r}"
    assert ja_r.get("status") == "OK", f"kp{RANK}_ja生成がstatus={ja_r.get('status')}で終了しました。result={ja_r}"

    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))
    tts_results["key_phrases"][str(RANK)] = {"english": en_r, "japanese": ja_r}
    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    summary = {
        "rank": RANK,
        "used_form": used_form,
        "japanese_gloss": ja_gloss,
        "japanese_gloss_tts": ja_gloss_tts,
        "old_en_sha256": old_en_sha, "new_en_sha256": sha256_of(en_path),
        "old_ja_sha256": old_ja_sha, "new_ja_sha256": sha256_of(ja_path),
        "english_result": en_r, "japanese_result": ja_r,
    }
    os.makedirs(os.path.dirname(RUN_SUMMARY_PATH), exist_ok=True)
    with open(RUN_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
