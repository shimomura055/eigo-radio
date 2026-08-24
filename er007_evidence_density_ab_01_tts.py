# ============================================================
# er007_evidence_density_ab_01_tts.py
# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part A-8: B版spoken scriptの
# 変更されたsegmentだけを新規TTS対象にする(無関係な音声は再生成しない)。
# Production TTS仕様(Batch API・Master Audio Store・Validator・
# ASR-first Retry Cascade)をそのまま再利用し、専用の出力先(B_OUT_ROOT)
# へ書き込む。既存のA版完成音声には一切触れない。
# ============================================================
from __future__ import annotations

import json
import os

import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/evidence_density_ab_01/tts_usage_log.jsonl")

import er003_v1_crosslevel_audio_02_common as c
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
from er007_evidence_density_ab_01_scripts import B_SCRIPTS

THEME_CONFIG = {
    "n4_supermarket": "er006_output/pool_pilot_01/pool_n4_supermarket",
    "n5_cafes": "er006_output/pool_pilot_01/pool_n5_cafes",
    "n6_delivery": "er006_output/pool_pilot_01/pool_n6_delivery",
}

B_OUT_ROOT = "er006_output/pool_pilot_01/evidence_density_ab_01/b_audio"

SEGMENT_TO_PARTKEY = {
    "full_story_part1": "part1", "full_story_part2": "part2",
    "point_one": "point_one_body", "point_two": "point_two_body",
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_b1_segment(text: str, out_path: str, seg_name: str) -> dict:
    if seg_name in ("point_one", "point_two"):
        sc.assert_no_point_number_label(text, seg_name)
    return news_tail_fix.generate_news_narration_wide_margin(
        tts_gen.tts_safe_news_en(text), out_path)


def generate_a2_segment(text: str, out_path: str, seg_name: str) -> dict:
    if seg_name in ("point_one", "point_two"):
        sc.assert_no_point_number_label(text, seg_name)
    sub = tts_gen.first_words(text)
    return c.generate_english_segment_with_fallback(tts_gen.tts_safe_news_en(text), out_path, sub)


def run_topic(short_key: str) -> dict:
    out_dir = THEME_CONFIG[short_key]
    results = {}
    for level_dir in ("b1b", "a2"):
        parts = load_json(f"{out_dir}/{level_dir}/parts.json")
        overrides = B_SCRIPTS[short_key][level_dir]
        b_narration_dir = f"{B_OUT_ROOT}/{short_key}/{level_dir}"
        os.makedirs(b_narration_dir, exist_ok=True)
        level_results = {}
        for seg_name, part_key in SEGMENT_TO_PARTKEY.items():
            override_text = overrides.get(part_key)
            if override_text is None:
                level_results[seg_name] = {"status": "SKIPPED_UNCHANGED"}
                continue
            out_path = f"{b_narration_dir}/{seg_name}.wav"
            print(f"[{short_key}/{level_dir}] {seg_name} B版TTS生成開始...")
            with cl.segment_context(f"{seg_name}_B"):
                if level_dir == "b1b":
                    r = generate_b1_segment(override_text, out_path, seg_name)
                else:
                    r = generate_a2_segment(override_text, out_path, seg_name)
            r["canonical_text"] = override_text
            level_results[seg_name] = r
            print(f"  status={r.get('status')}")
        results[level_dir] = level_results
        with open(f"{b_narration_dir}/tts_generation_results_B.json", "w", encoding="utf-8") as f:
            json.dump(level_results, f, ensure_ascii=False, indent=2, default=str)
    return results


if __name__ == "__main__":
    import sys
    targets = sys.argv[1:] or list(THEME_CONFIG.keys())
    for t in targets:
        print(f"===== {t} =====")
        run_topic(t)
    print("ALL_TTS_B_DONE")
