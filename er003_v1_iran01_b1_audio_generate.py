# ============================================================
# er003_v1_iran01_b1_audio_generate.py
# ER-003-IRAN-A2-B1-01: IRAN01 B1 Full Audio(全segment TTS+ASR検証)
# ============================================================
# VOICE-03時点の最終Voice Allocation(Charon=Navigator/Explanation、
# Aoede=Listening対象本文)を最初から適用する。既存の確立済み関数を
# そのまま再利用し、新しいTTS/ASR安全処理ロジックは作らない:
#   - er003_v1_sing01_voice01_generate.generate_charon_english
#     (Charon、ENGLISH_STYLE_PREFIX+MINIMAL_INSTRUCTION fallback、
#     trim安全マージン0.35秒、ASR+長さ検証)
#   - er003_v1_sing01_voice01_generate.generate_charon_japanese
#     (Charon、日本語、同上)
#   - er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin
#     (Aoede、News本文向け、同じ0.35秒マージンを最初から適用しtail切れ
#     バグを未然に回避する)
#   - er003_v1_sing01_point_headings_aoede.generate
#     (Aoede、"First point."/"Second point."見出し用)
#   - er003_v1_repro01_main_generate.generate_key_phrase_component_verified
#     (Aoede、Key Phrase英語Component)
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_b1_audio_generate.py

from __future__ import annotations

import json
import os

import er003_v1_iran01_articles_generate as gen
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = f"{gen.OUT_DIR}/b1"
NARRATION_DIR = f"{OUT_DIR}/narration"

with open(f"{OUT_DIR}/fixed_news_parts.json", encoding="utf-8") as f:
    PARTS = json.load(f)

ENGLISH_TITLE_TEXT = PARTS["title"]
TOPIC_INTRO_TEXT = f"Today's topic is {ENGLISH_TITLE_TEXT}."
WELCOME_TEXT = "Welcome to English Your Way."
PREVIEW_INTRO_TEXT = "Here's a quick preview."
KEY_PHRASES_INTRO_TEXT = "Here are today's key phrases."
FULL_STORY_INTRO_TEXT = "Now, the full story."
NUMBER_WORDS = ("One.", "Two.", "Three.", "Four.", "Five.")


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    with open(f"{OUT_DIR}/support_texts.json", encoding="utf-8") as f:
        support_texts = json.load(f)
    with open(f"{OUT_DIR}/key_phrases/keywords_canonicalized.json", encoding="utf-8") as f:
        kp_canon = json.load(f)

    results = {}

    # --- Shell(Charon、固定文言、記事非依存だが音源はarticle別に生成) ---
    charon_shell_jobs = {
        "welcome": WELCOME_TEXT,
        "topic_intro": TOPIC_INTRO_TEXT,
        "preview_intro": PREVIEW_INTRO_TEXT,
        "key_phrases_intro": KEY_PHRASES_INTRO_TEXT,
        "full_story_intro": FULL_STORY_INTRO_TEXT,
    }
    for i, num_text in enumerate(NUMBER_WORDS, start=1):
        names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
        charon_shell_jobs[names[i - 1]] = num_text

    for name, text in charon_shell_jobs.items():
        print(f"[IRAN01-B1-AUDIO] {name}生成(Charon)...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = voice01.generate_charon_english(text, out_path)
        results[name] = r
        print(f"[IRAN01-B1-AUDIO] {name}: status={r.get('status')}")

    # --- Support(Charon、Preview/Comment1-4/In One Line) ---
    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        print(f"[IRAN01-B1-AUDIO] {name}生成(Charon)...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = voice01.generate_charon_english(support_texts[name], out_path)
        results[name] = r
        print(f"[IRAN01-B1-AUDIO] {name}: status={r.get('status')}")

    print("[IRAN01-B1-AUDIO] in_one_line生成(Charon)...")
    in_one_line_path = f"{NARRATION_DIR}/in_one_line_charon.wav"
    r = voice01.generate_charon_english(PARTS["in_one_line"], in_one_line_path)
    results["in_one_line"] = r
    print(f"[IRAN01-B1-AUDIO] in_one_line: status={r.get('status')}")

    # --- Point見出し(Aoede、"First point."/"Second point.") ---
    for name, text in (("point_one_heading", "First point."), ("point_two_heading", "Second point.")):
        print(f"[IRAN01-B1-AUDIO] {name}生成(Aoede): {text!r}...")
        out_path = f"{NARRATION_DIR}/{name}_aoede.wav"
        r = point_headings.generate(text, out_path)
        results[name] = r
        print(f"[IRAN01-B1-AUDIO] {name}: status={r.get('status')}")

    # --- News本文(Aoede、tail安全マージン0.35秒を最初から適用) ---
    news_jobs = [
        ("full_story_part1", PARTS["part1"]),
        ("full_story_part2", PARTS["part2"]),
        ("point_one", PARTS["point_one_body"]),
        ("point_two", PARTS["point_two_body"]),
    ]
    for name, text in news_jobs:
        print(f"[IRAN01-B1-AUDIO] {name}生成(Aoede、News本文)...")
        out_path = f"{NARRATION_DIR}/{name}.wav"
        r = news_tail_fix.generate_news_narration_wide_margin(text, out_path)
        results[name] = r
        print(f"[IRAN01-B1-AUDIO] {name}: status={r.get('status')}")

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    with open(f"{OUT_DIR}/audit/segment_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    if failed:
        print(f"[IRAN01-B1-AUDIO] 生成失敗segmentあり、中断します: {failed}")
        return

    # --- Key Phrase Components(English, Aoede) + Japanese meaning(Charon) ---
    kp_items = sorted(kp_canon["items"], key=lambda it: it["rank"])
    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[IRAN01-B1-AUDIO] Key Phrase {rank} 英語Component生成(Aoede): {used_form!r}...")
        en_path = f"{NARRATION_DIR}/kp{rank}_en.wav"
        en_result = repro01.generate_key_phrase_component_verified(used_form, en_path)
        print(f"[IRAN01-B1-AUDIO] Key Phrase {rank} 日本語meaning生成(Charon): {ja_gloss!r}...")
        ja_path = f"{NARRATION_DIR}/kp{rank}_ja_charon.wav"
        ja_result = voice01.generate_charon_japanese(ja_gloss, ja_path, ja_gloss[:4])
        kp_results[rank] = {"english": en_result, "japanese": ja_result}
        print(f"[IRAN01-B1-AUDIO] Key Phrase {rank}: en={en_result.get('status')} ja={ja_result.get('status')}")

    with open(f"{OUT_DIR}/audit/key_phrase_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(kp_results, f, ensure_ascii=False, indent=2, default=str)

    kp_failed = [r for r, v in kp_results.items()
                 if v["english"].get("status") != "OK" or v["japanese"].get("status") != "OK"]
    if kp_failed:
        print(f"[IRAN01-B1-AUDIO] Key Phrase生成失敗あり、中断します: {kp_failed}")
        return

    summary = {
        "status": "OK", "article_id": "IRAN01_B1",
        "segment_status": {k: v.get("status") for k, v in results.items()},
        "key_phrase_status": {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                               for r, v in kp_results.items()},
    }
    with open(f"{OUT_DIR}/run_summary_audio.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[IRAN01-B1-AUDIO] 全content生成完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
