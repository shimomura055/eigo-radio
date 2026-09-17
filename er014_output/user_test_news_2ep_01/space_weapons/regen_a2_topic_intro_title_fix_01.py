# ============================================================
# er014_output/user_test_news_2ep_01/space_weapons/regen_a2_topic_intro_title_fix_01.py
# 管理ID: USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06
#
# 目的: ユーザー試聴Feedback(2026-09-17、A2タイトル読み上げの区切りが
# 不自然)への対応。Space Weapons A2の`topic_intro`segmentのみを、
# `parts.json`の新設フィールド`title_tts`(TTS入力専用、canonicalな
# `title`はcolon付きのまま無変更)を使って再生成し、Assembly/Audio
# Validation Gate/player.html/web mp3のみ更新する。
#
# 対象外(意図的に一切呼ばない): 記事本文再生成、Fact/Ledger再実行、
# Key Phrase変更、Comment内容変更、他segmentのTTS再生成
# (comment_1-4/preview/key_phrases/full_story_part1-2/point_one/two/
# in_one_line/japanese_titleは一切呼ばない。generate_a2_segments()を
# 丸ごと呼ぶと全segmentが再生成されてしまうため、意図的にtopic_intro
# 単体の生成呼び出しのみをここに複製する)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er014_output/user_test_news_2ep_01/space_weapons/regen_a2_topic_intro_title_fix_01.py
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_crosslevel_audio_02_common as c
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as ttsgen
import er005_cost_logger as cl

sys.path.insert(0, "er014_output/user_test_news_2ep_01")
import build_web_player_common as bwpc  # noqa: E402  (読み取り専用の既存共通module、無変更で呼ぶだけ)

THEME_ID = "user_test_news_2ep_01_space_weapons"
BASE_DIR = "er014_output/user_test_news_2ep_01/space_weapons"
OUT_DIR = f"{BASE_DIR}/a2"
NARRATION_DIR = f"{OUT_DIR}/narration"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def regen_topic_intro() -> dict:
    parts = load_json(f"{OUT_DIR}/parts.json")
    canonical_title = parts["title"]
    tts_title = parts.get("title_tts", canonical_title)
    canonical_text = f"Today's topic is {canonical_title}."
    tts_text = f"Today's topic is {tts_title}."
    tts_input = ttsgen.tts_safe_number_words_en(ttsgen.tts_safe_en(tts_text))

    print(f"[REGEN][a2/topic_intro] canonical={canonical_text!r}")
    print(f"[REGEN][a2/topic_intro] tts_input ={tts_input!r}")

    with cl.segment_context("topic_intro"):
        result = c.generate_english_segment_with_fallback(
            tts_input, f"{NARRATION_DIR}/topic_intro.wav",
            ttsgen.first_words(canonical_title, 3), max_extra_chars=30)
    result["canonical_text"] = canonical_text
    result["tts_input_text"] = tts_input

    tts_results = load_json(f"{OUT_DIR}/audit/tts_generation_results.json")
    tts_results["segments"]["topic_intro"] = result
    save_json(f"{OUT_DIR}/audit/tts_generation_results.json", tts_results)

    run_summary_tts = load_json(f"{OUT_DIR}/run_summary_tts.json")
    run_summary_tts["segment_status"]["topic_intro"] = result.get("status")
    save_json(f"{OUT_DIR}/run_summary_tts.json", run_summary_tts)

    print(f"[REGEN][a2/topic_intro] status={result.get('status')} "
          f"audio_classification={result.get('audio_classification')} "
          f"asr_text={result.get('asr_text')!r}")
    return result


def reassemble_and_gate() -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": BASE_DIR}
    result = asm.stage_assemble_a2(theme)
    print(f"[REGEN][a2] Assembly status={result.get('status')} "
          f"duration={result.get('duration_seconds')} peak={result.get('peak')} "
          f"clipping={result.get('clipping_detected')}")
    rs = asm.derive_a_family_required_structure("A2")
    asm.verify_episode_audio_validation_gate(OUT_DIR, "A2", required_structure=rs)
    print("[REGEN][a2] Audio Validation Gate: PASS")
    return result


def rebuild_web_and_player(assemble_result: dict) -> str:
    import html as html_mod

    seg_names = [
        "topic_intro", "japanese_title", "preview", "kp1_en", "meaning_1", "kp2_en", "meaning_2",
        "kp3_en", "meaning_3", "kp4_en", "meaning_4", "kp5_en", "meaning_5",
        "comment_1", "full_story_part1", "comment_2", "full_story_part2", "comment_3",
        "point_one_heading", "point_one", "point_two_heading", "point_two", "comment_4", "in_one_line",
    ]
    web_delivery = bwpc.build_web_delivery(
        OUT_DIR, OUT_DIR, NARRATION_DIR, assemble_result["out_path"], seg_names)
    rows, kp_table_html, parts = bwpc.build_a2_rows(OUT_DIR, "web/segments")

    # USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06: bwpc.build_a2_rows()は
    # topic_introの表示script欄にtts_generation_results.json["text"]
    # (=実際にTTSへ渡した入力、本タスクではcolon->periodのTTS専用整形後の
    # 文字列)をそのまま使うため、無変更のままだと表示・記事本文・canonical
    # であるべきtitle文字列(colon付き)が壊れてしまう。build_web_player_
    # common.py自体は共有module(並行タスクが使用中)のため変更せず、この
    # 呼び出し側でTopic introの行(rows[2]、build_a2_rows()内でIntro→
    # Welcome→Topic introの順に3番目に追加される固定順序)のみ、TTS入力
    # 表記からcanonical表記へ文字列置換して戻す(表示・canonical不変の
    # 要件を満たすための、このdriver script内で完結する後処理)。
    canonical_title = parts["title"]
    tts_title = parts.get("title_tts", canonical_title)
    if tts_title != canonical_title:
        tts_text = f"Today's topic is {tts_title}."
        canonical_text = f"Today's topic is {canonical_title}."
        tts_html = html_mod.escape(tts_text)
        canonical_html = html_mod.escape(canonical_text)
        if tts_html in rows[2]:
            rows[2] = rows[2].replace(tts_html, canonical_html)
            print("[REGEN][a2] player.html Topic introの表示textをcanonical(colon付き)へ復元")
        else:
            raise RuntimeError(
                "[REGEN][a2] Topic intro行のHTML内にTTS入力textが見つからず、"
                "canonical表示への復元ができませんでした。STOP。")

    note_html = (f"USER-TEST(Space Weapons)。A2タイトルTTS区切り修正"
                 f"(USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-06)。")
    out_path = bwpc.render_player_page(
        f"Space Weapons - A2 (Beginner)",
        note_html, web_delivery["episode_mp3"],
        assemble_result["duration_seconds"], assemble_result["peak"], assemble_result["clipping_detected"],
        rows, kp_table_html, f"{OUT_DIR}/player.html")
    print(f"[REGEN][a2] player.html再生成: {out_path}")
    return out_path


def main() -> None:
    cl.install(f"{BASE_DIR}/raw_usage_log.jsonl")
    with cl.logging_context(THEME_ID, "tts_a2_title_fix_resume06"):
        regen_result = regen_topic_intro()
    if regen_result.get("status") != "OK":
        raise RuntimeError(f"topic_intro regen失敗、STOP。status={regen_result.get('status')}")
    assemble_result = reassemble_and_gate()
    rebuild_web_and_player(assemble_result)
    print("[REGEN][a2] 完了。")


if __name__ == "__main__":
    main()
