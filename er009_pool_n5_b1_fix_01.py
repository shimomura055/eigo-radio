# -*- coding: utf-8 -*-
# ============================================================
# er009_pool_n5_b1_fix_01.py
# ============================================================
# No.5(pool_n5_cafes) B1の既存2件の問題を、既存の確立済み関数を
# そのまま再利用して解消する薄いラッパー:
#   (1) comment_4: 「customers who work there may offer the café more
#       than their payment」という、B1自身のIn One Line・A2 Point Two
#       (いずれも「方針の明確さ」テーマ)と整合しない要約文を、
#       ユーザー指示により「方針の明確さ」テーマへ言い換え済み
#       (b1_support_texts.json、内容はユーザー承認済み)。ここでは
#       修正後テキストを、既存のvoice01.generate_charon_english経路で
#       再生成するのみ(新規instructionは作らない)。
#   (2) full_story_part1/full_story_part2: 現行tts_generation_results.
#       jsonでstatus=STOPPED(旧試行ログ)。現行Production経路
#       (news_tail_fix.generate_news_narration_wide_margin、Secondary
#       ASR Cascade込み)で新規に取り直す。
from __future__ import annotations

import json
import sys

import er005_cost_logger as cl

cl.install("er006_output/pool_pilot_01/pool_n5_cafes/b1b/audit/pool_n5_b1_fix_raw_usage_log.jsonl")

import er003_v1_n3_01_tts_generate as tg
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR_B1 = "er006_output/pool_pilot_01/pool_n5_cafes/b1b"
NARRATION_DIR = f"{OUT_DIR_B1}/narration"
RESULTS_PATH = f"{OUT_DIR_B1}/audit/tts_generation_results.json"


def run_comment4(results, support):
    text = support["comment_4"]
    print(f"[N5-B1-FIX] comment_4 再生成(修正後の内容): {text!r}")
    with cl.logging_context("pool_n5_cafes", "b1_fix"), cl.segment_context("comment_4"):
        r = voice01.generate_charon_english(
            tg.tts_safe_number_words_en(tg.tts_safe_en(text)), f"{NARRATION_DIR}/comment_4.wav")
    r["canonical_text"] = text
    results["segments"]["comment_4"] = r
    print(f"[N5-B1-FIX] comment_4 status={r.get('status')}")


def run_full_story(results, parts, name, key):
    text = parts[key]
    print(f"[N5-B1-FIX] {name} 再生成(現行Production Cascade経路)...")
    with cl.logging_context("pool_n5_cafes", "b1_fix"), cl.segment_context(name):
        r = news_tail_fix.generate_news_narration_wide_margin(
            tg.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav")
    r["canonical_text"] = text
    results["segments"][name] = r
    print(f"[N5-B1-FIX] {name} status={r.get('status')}")
    if r.get("status") != "OK":
        print(f"[N5-B1-FIX] {name} reason={r.get('reason')}")
    for a in r.get("attempts_log", []):
        print(f"    attempt {a.get('attempt')}: {a.get('audio_classification')} "
              f"verified={a.get('verified')} asr={str(a.get('asr_text'))[:160]!r}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    parts = tg.load_json(f"{OUT_DIR_B1}/parts.json")
    support = tg.load_json(f"{OUT_DIR_B1}/b1_support_texts.json")
    results = tg.load_json(RESULTS_PATH)

    if target in ("comment_4", "all"):
        run_comment4(results, support)
    if target in ("full_story_part1", "all"):
        run_full_story(results, parts, "full_story_part1", "part1")
    if target in ("full_story_part2", "all"):
        run_full_story(results, parts, "full_story_part2", "part2")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_status = {k: v.get("status") for k, v in results["segments"].items()}
    print("[N5-B1-FIX] segment_status:", json.dumps(all_status, ensure_ascii=False))


if __name__ == "__main__":
    main()
