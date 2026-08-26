# -*- coding: utf-8 -*-
# ============================================================
# er008_pool_n4_audio_qa_sync_01.py
# ============================================================
# 目的: Pool Topic No.4「The Supermarket Shuffle」
# (er006_output/pool_pilot_01/pool_n4_supermarket/)は、台本・Factが
# 既にDIRECTLY_REUSABLE判定済みで完成しているが、生成当時のTTS/Audio QA
# 仕様が、その後Production標準になった以下2点を含んでいない:
#   (1) ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11: A2英語7segment
#       (point_one_heading/point_two_heading/full_story_part1/
#       full_story_part2/point_one/point_two/in_one_line)への6%
#       FFmpeg time-stretch(post-process slowdown)
#   (2) ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05:
#       Audio Validation Gate監査で、pool_n4_supermarket/a2は
#       comment_2がSTOPPED状態のまま(標準/fallback各6回不合格)
#       であることが判明している。
#
# 本スクリプトは、台本・Fact(article.md/parts.json/*_support_texts.json)
# を一切書き換えず、既存の確立済み関数(generate_a2_segment_with_
# slowdown/generate_a2_japanese_with_reading_safety、いずれも
# er003_v1_n3_01_tts_generate.pyで他テーマ向けに実装済み)をそのまま
# import して、上記2つの未適用箇所だけを薄く再生成する。
#
# 対象外(意図的に触らない):
#   - A2のtopic_intro/japanese_title/preview/comment_1・3・4/Key Phrase
#     英日5件 → 既にAudio Validation Gate上VALIDATED、内容変更不要
#   - B1(b1b) → 監査で既にGateクリーンと判明済み、音声は一切変更しない
#     (本スクリプトはGate再確認のみ行う)
#   - Evidence Compression・Directional Fact Precheck → 台本自体を
#     書き換える工程であり、OPEN-68(遡及適用は個別対応のみ、一括不要)
#     の方針および「台本は書き換えない」というタスク指示に従い、
#     今回は適用しない
from __future__ import annotations

import json

import er005_cost_logger as cl

cl.install("er006_output/pool_pilot_01/pool_n4_supermarket/a2/audit/pool_n4_qa_sync_raw_usage_log.jsonl")

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as tg

THEME = {"theme_id": "pool_n4_supermarket", "out_dir": "er006_output/pool_pilot_01/pool_n4_supermarket"}
OUT_DIR_A2 = f"{THEME['out_dir']}/a2"
OUT_DIR_B1 = f"{THEME['out_dir']}/b1b"
NARRATION_DIR = f"{OUT_DIR_A2}/narration"
RESULTS_PATH = f"{OUT_DIR_A2}/audit/tts_generation_results.json"

# ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05実データ監査で
# 判明したSTOPPED segment(内容は変えず取り直しのみ)。
STOPPED_JAPANESE_SEGMENTS = ("comment_2",)


def regenerate_stopped_japanese_segments(results: dict, support: dict) -> None:
    for name in STOPPED_JAPANESE_SEGMENTS:
        text = support[name]
        print(f"[QA-SYNC][a2] {name} 再生成(日本語、STOPPED解消、内容不変)...")
        with cl.segment_context(name):
            r = tg.generate_a2_japanese_with_reading_safety(
                text, f"{NARRATION_DIR}/{name}.wav", tg.expected_substring_ja(text))
        results["segments"][name] = r
        print(f"[QA-SYNC][a2] {name} status={r.get('status')}")


def regenerate_a2_slowdown_segments(results: dict, parts: dict) -> None:
    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        tg.sc.assert_no_point_number_label(text, name)
        tts_input = tg.tts_safe_number_words_en(tg.tts_safe_en(text))
        print(f"[QA-SYNC][a2] {name} 再生成(英語見出し、6% slowdown経路)...")
        with cl.segment_context(name):
            r = tg.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", tg.first_words(text, 3), max_extra_chars=20,
                style_prefix_override=tg.A2_ENGLISH_STYLE_PREFIX_SLOWER)
        r["canonical_text"] = text
        results["segments"][name] = r
        print(f"[QA-SYNC][a2] {name} status={r.get('status')}")

    for name, text in (
        ("full_story_part1", parts["part1"]),
        ("full_story_part2", parts["part2"]),
        ("point_one", parts["point_one_body"]),
        ("point_two", parts["point_two_body"]),
        ("in_one_line", parts["in_one_line"]),
    ):
        if name in ("point_one", "point_two"):
            tg.sc.assert_no_point_number_label(text, name)
        sub = tg.first_words(text)
        tts_input = tg.tts_safe_news_en(text)
        print(f"[QA-SYNC][a2] {name} 再生成(英語News本文、6% slowdown経路)...")
        with cl.segment_context(name):
            r = tg.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", sub,
                style_prefix_override=tg.A2_ENGLISH_STYLE_PREFIX_SLOWER)
        r["canonical_text"] = text
        results["segments"][name] = r
        print(f"[QA-SYNC][a2] {name} status={r.get('status')}")


def main():
    parts = tg.load_json(f"{OUT_DIR_A2}/parts.json")
    support = tg.load_json(f"{OUT_DIR_A2}/a2_support_texts.json")
    results = tg.load_json(RESULTS_PATH)

    with cl.logging_context(THEME["theme_id"], "qa_sync_a2"):
        regenerate_stopped_japanese_segments(results, support)
        regenerate_a2_slowdown_segments(results, parts)

    all_status = {k: v.get("status") for k, v in results["segments"].items()}
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("[QA-SYNC][a2] segment_status:", json.dumps(all_status, ensure_ascii=False))

    blocked = [f"{k}={v}" for k, v in all_status.items() if v != "OK"]
    if blocked:
        print("[QA-SYNC][a2] BLOCKED_SEGMENTS_REMAIN:", blocked)
        print("[QA-SYNC] 停止: gateがまだ通らないため、reassembleは実行しません。")
        return

    # B1は無変更。Gateが実際にPASSすることだけ確認する(壊れていないことの
    # 確認のみ、音声・assembled wavは一切書き換えない)。
    asm.verify_episode_audio_validation_gate(OUT_DIR_B1, "B1")
    print("[QA-SYNC][b1b] Audio Validation Gate: PASS(無変更のまま確認のみ)")

    with cl.logging_context(THEME["theme_id"], "qa_sync_assemble_a2"):
        a2_summary = asm.stage_assemble_a2(THEME)
    print("[QA-SYNC][a2] reassemble完了:", json.dumps(a2_summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
