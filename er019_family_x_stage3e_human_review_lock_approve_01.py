# ============================================================
# er019_family_x_stage3e_human_review_lock_approve_01.py
# NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 Stage 3e
# ============================================================
# ユーザー既決(2026-09-27、PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-
# WIRING-AND-JA-VALIDATOR-PUNCT-01修正2回目の委任文): 根本原因修正済みの
# 9 segment(Hormuz A2/B1B full_story_part2、Hormuz B1B kp2_ja_charon、
# small_bag A2 comment_2/full_story_part2/full_story_part3、small_bag
# B1B full_story_part2/full_story_part3、Meta A2 japanese_title)の
# Human Review Lockを、既存Production機構(er011_human_review_lock_01.
# approve_regenerate → REGENERATE_APPROVED)で解除する。**新しいGate/
# 閾値/retry仕様は追加しない**。承認外のsegment(small_bag A2 meaning_5
# 等)には一切触れない。
#
# N8(Opus L2所見、正規化揃え): approve_regenerate()へ渡すtextは、
# 実際にHuman Review Lockの対象になる関数(guarded_generateでラップ
# された最も内側の関数)が受け取るのと同じ正規化後テキストに揃える
# (前例: er011_discovery_generalization_towels_trial_11_audio_04_b1b_
# fullstory_resume_human_review.py L61)。
#   - full_story_part2/3(EN、A2/B1B、Hormuz/small_bag): news_tail_fix.
#     generate_news_narration_wide_margin/n3_tts.generate_a2_segment_
#     with_slowdown経由crosslevel_common.generate_english_segment_
#     with_fallbackはいずれも、呼び出し元(runner)が計算した
#     n3_tts.tts_safe_news_en(body_text)をそのままtext引数として受け取る
#     (guarded decoratorは最外周の関数定義に直接ついているため、追加の
#     内部正規化は無い)。
#   - comment_2(A2、JA)/japanese_title(A2、JA)/kp2_ja_charon(B1B、JA):
#     実際にguardedなのはgenerate_a2_japanese_with_fallback/voice01.
#     generate_charon_japaneseであり、呼び出し元のgenerate_a2_japanese_
#     with_reading_safety/generate_charon_japanese_with_reading_safety
#     が内部でtts_safe_ja()→safety.to_tts_safe_japanese_fraction_reading()
#     を適用した後のtts_input文字列を渡す。したがってapprove_regenerate
#     にはこのtts_input(素のraw textではない)を渡す。
#
# 実行方法(root直下から、TTS/ASR API呼び出しは無し、¥0):
#   .venv/Scripts/python.exe er019_family_x_stage3e_human_review_lock_approve_01.py [--level a2|b1b|both]
from __future__ import annotations

import argparse
import json

import er003_audio_tts_asr_safety as safety
import er003_v1_n3_01_tts_generate as n3_tts
import er011_human_review_lock_01 as review_lock

APPROVED_BY = ("operator(Sonnet, per user 2026-09-27 decision "
               "'Human Review Lock解除承認(根本原因修正済みの9 segment)', "
               "管理ID: PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01"
               "(修正2回目) / NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 Stage 3e)")

BASE = "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01"
META_BASE = "er019_output/family_x_b3_production_wiring_01/run_01"
META_OUT = "er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _en_body_tts_input(parts_path: str, body_key: str) -> str:
    parts = load_json(parts_path)
    return n3_tts.tts_safe_news_en(parts[body_key])


def _ja_tts_input(raw_text: str) -> str:
    placeholder_safe = n3_tts.tts_safe_ja(raw_text)
    return safety.to_tts_safe_japanese_fraction_reading(placeholder_safe)


def approve_a2(dry_run: bool) -> dict:
    results = {}

    # Hormuz A2 full_story_part2
    hz_a2_fsp2 = _en_body_tts_input(f"{BASE}/hormuz__run_02/a2/parts.json", "body2")
    out_path = f"{BASE}/hormuz__run_02/a2/narration/full_story_part2.wav"
    if not dry_run:
        results["hormuz_a2_full_story_part2"] = review_lock.approve_regenerate(
            out_path, hz_a2_fsp2, approved_by=APPROVED_BY)
    else:
        results["hormuz_a2_full_story_part2"] = {"out_path": out_path, "text_preview": hz_a2_fsp2[:60]}

    # small_bag A2 comment_2
    sb_a2_support = load_json(f"{BASE}/small_bag__run_02/a2/a2_support_texts.json")
    comment2_tts = _ja_tts_input(sb_a2_support["comment_2"])
    out_path = f"{BASE}/small_bag__run_02/a2/narration/comment_2.wav"
    if not dry_run:
        results["small_bag_a2_comment_2"] = review_lock.approve_regenerate(
            out_path, comment2_tts, approved_by=APPROVED_BY)
    else:
        results["small_bag_a2_comment_2"] = {"out_path": out_path, "text_preview": comment2_tts[:60]}

    # small_bag A2 full_story_part2/part3
    sb_a2_fsp2 = _en_body_tts_input(f"{BASE}/small_bag__run_02/a2/parts.json", "body2")
    out_path = f"{BASE}/small_bag__run_02/a2/narration/full_story_part2.wav"
    if not dry_run:
        results["small_bag_a2_full_story_part2"] = review_lock.approve_regenerate(
            out_path, sb_a2_fsp2, approved_by=APPROVED_BY)
    else:
        results["small_bag_a2_full_story_part2"] = {"out_path": out_path, "text_preview": sb_a2_fsp2[:60]}

    sb_a2_fsp3 = _en_body_tts_input(f"{BASE}/small_bag__run_02/a2/parts.json", "body3")
    out_path = f"{BASE}/small_bag__run_02/a2/narration/full_story_part3.wav"
    if not dry_run:
        results["small_bag_a2_full_story_part3"] = review_lock.approve_regenerate(
            out_path, sb_a2_fsp3, approved_by=APPROVED_BY)
    else:
        results["small_bag_a2_full_story_part3"] = {"out_path": out_path, "text_preview": sb_a2_fsp3[:60]}

    # Meta A2 japanese_title
    meta_evidence = load_json(f"{META_BASE}/ja_writer/runtime_evidence.json")
    meta_title_tts = _ja_tts_input(meta_evidence["title"])
    out_path = f"{META_OUT}/a2/narration/japanese_title.wav"
    if not dry_run:
        results["meta_a2_japanese_title"] = review_lock.approve_regenerate(
            out_path, meta_title_tts, approved_by=APPROVED_BY)
    else:
        results["meta_a2_japanese_title"] = {"out_path": out_path, "text_preview": meta_title_tts[:60]}

    return results


def approve_b1b(dry_run: bool) -> dict:
    results = {}

    # Hormuz B1B full_story_part2
    hz_b1b_fsp2 = _en_body_tts_input(f"{BASE}/hormuz__run_02/b1b/parts.json", "body2")
    out_path = f"{BASE}/hormuz__run_02/b1b/narration/full_story_part2.wav"
    if not dry_run:
        results["hormuz_b1b_full_story_part2"] = review_lock.approve_regenerate(
            out_path, hz_b1b_fsp2, approved_by=APPROVED_BY)
    else:
        results["hormuz_b1b_full_story_part2"] = {"out_path": out_path, "text_preview": hz_b1b_fsp2[:60]}

    # Hormuz B1B kp2_ja_charon
    hz_b1b_kp = load_json(f"{BASE}/hormuz__run_02/b1b/key_phrases/keywords_canonicalized.json")
    kp2_item = next(it for it in hz_b1b_kp["items"] if it["rank"] == 2)
    ja_gloss_tts, _fallback = n3_tts.resolve_key_phrase_ja_gloss_tts(kp2_item)
    kp2_tts = _ja_tts_input(ja_gloss_tts)
    out_path = f"{BASE}/hormuz__run_02/b1b/narration/kp2_ja_charon.wav"
    if not dry_run:
        results["hormuz_b1b_kp2_ja_charon"] = review_lock.approve_regenerate(
            out_path, kp2_tts, approved_by=APPROVED_BY)
    else:
        results["hormuz_b1b_kp2_ja_charon"] = {"out_path": out_path, "text_preview": kp2_tts[:60]}

    # small_bag B1B full_story_part2/part3
    sb_b1b_fsp2 = _en_body_tts_input(f"{BASE}/small_bag__run_02/b1b/parts.json", "body2")
    out_path = f"{BASE}/small_bag__run_02/b1b/narration/full_story_part2.wav"
    if not dry_run:
        results["small_bag_b1b_full_story_part2"] = review_lock.approve_regenerate(
            out_path, sb_b1b_fsp2, approved_by=APPROVED_BY)
    else:
        results["small_bag_b1b_full_story_part2"] = {"out_path": out_path, "text_preview": sb_b1b_fsp2[:60]}

    sb_b1b_fsp3 = _en_body_tts_input(f"{BASE}/small_bag__run_02/b1b/parts.json", "body3")
    out_path = f"{BASE}/small_bag__run_02/b1b/narration/full_story_part3.wav"
    if not dry_run:
        results["small_bag_b1b_full_story_part3"] = review_lock.approve_regenerate(
            out_path, sb_b1b_fsp3, approved_by=APPROVED_BY)
    else:
        results["small_bag_b1b_full_story_part3"] = {"out_path": out_path, "text_preview": sb_b1b_fsp3[:60]}

    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", default="both", choices=("a2", "b1b", "both"))
    parser.add_argument("--dry-run", action="store_true",
                         help="approve_regenerate()を実際には呼ばず、対象out_path/textだけ表示する")
    args = parser.parse_args()

    results = {}
    if args.level in ("a2", "both"):
        results["a2"] = approve_a2(args.dry_run)
    if args.level in ("b1b", "both"):
        results["b1b"] = approve_b1b(args.dry_run)

    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
