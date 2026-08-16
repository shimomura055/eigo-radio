# ============================================================
# er003_v1_b1redesign_audio_generate.py
# ER-003-B1-REDESIGN-AUDIO-01: B1-B Full Audio生成(全segment TTS+ASR)
# ============================================================
# VOICE-03時点のVoice Allocation(Charon=Navigator/Explanation、
# Aoede=本文)を無変更で適用する。既存の確立済み関数を再利用し、
# tail安全マージン0.35秒を最初から適用する(IRAN01 B1と同一方針)。
#
# 今回必須: 日本語Key Phrase meaning生成では、ER-003-AUDIO-
# JP-READING-SAFETY-01で追加した共通関数
# safety.to_tts_safe_japanese_fraction_reading() を必ず経由する
# (記事固有のreplacementを再実装しない)。経路を通った証拠として、
# canonical textとTTS input双方をログ・監査ファイルへ記録する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1redesign_audio_generate.py

from __future__ import annotations

import json
import os

import er003_audio_tts_asr_safety as safety
import er003_v1_b1redesign_audio_scaffold_generate as scaf
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = scaf.OUT_DIR
NARRATION_DIR = f"{OUT_DIR}/narration"

with open(f"{OUT_DIR}/audit/text_identity.json", encoding="utf-8") as f:
    PARTS = json.load(f)["parts"]

ENGLISH_TITLE_TEXT = PARTS["title"]
TOPIC_INTRO_TEXT = f"Today's topic is {ENGLISH_TITLE_TEXT}."
WELCOME_TEXT = "Welcome to English Your Way."
PREVIEW_INTRO_TEXT = "Here's a quick preview."
KEY_PHRASES_INTRO_TEXT = "Here are today's key phrases."
FULL_STORY_INTRO_TEXT = "Now, the full story."
NUMBER_WORDS = ("One.", "Two.", "Three.", "Four.", "Five.")


def generate_charon_japanese_with_reading_safety(text: str, out_path: str, expected_substring: str,
                                                   max_attempts: int = 6) -> dict:
    """日本語Charon生成の前段に、共通の分数reading-safe正規化を必ず通す。
    canonical textはそのまま、TTS inputのみ変換したコピーを使う。
    経路を通過した証拠としてcanonical/tts_input両方を戻り値へ含める。"""
    tts_input = safety.to_tts_safe_japanese_fraction_reading(text)
    print(f"    [JP-READING-SAFETY] canonical={text!r} -> tts_input={tts_input!r} "
          f"(changed={tts_input != text})")
    r = voice01.generate_charon_japanese(tts_input, out_path, expected_substring, max_attempts=max_attempts)
    r["canonical_text"] = text
    r["tts_input_text_after_reading_safety"] = tts_input
    r["reading_safety_changed_text"] = (tts_input != text)
    return r


def main():
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    with open(f"{OUT_DIR}/support_texts.json", encoding="utf-8") as f:
        support_texts = json.load(f)
    with open(f"{OUT_DIR}/key_phrases/keywords_canonicalized.json", encoding="utf-8") as f:
        kp_canon = json.load(f)

    results = {}

    # --- Shell(Charon) ---
    charon_shell_jobs = {
        "welcome": WELCOME_TEXT,
        "topic_intro": TOPIC_INTRO_TEXT,
        "preview_intro": PREVIEW_INTRO_TEXT,
        "key_phrases_intro": KEY_PHRASES_INTRO_TEXT,
        "full_story_intro": FULL_STORY_INTRO_TEXT,
    }
    names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    for i, num_text in enumerate(NUMBER_WORDS):
        charon_shell_jobs[names[i]] = num_text

    for name, text in charon_shell_jobs.items():
        print(f"[B1REDESIGN-AUDIO] {name}生成(Charon)...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = voice01.generate_charon_english(text, out_path)
        results[name] = r
        print(f"[B1REDESIGN-AUDIO] {name}: status={r.get('status')}")

    # --- Support(Charon) ---
    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        print(f"[B1REDESIGN-AUDIO] {name}生成(Charon)...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = voice01.generate_charon_english(support_texts[name], out_path)
        results[name] = r
        print(f"[B1REDESIGN-AUDIO] {name}: status={r.get('status')}")

    print("[B1REDESIGN-AUDIO] in_one_line生成(Charon)...")
    r = voice01.generate_charon_english(PARTS["in_one_line"], f"{NARRATION_DIR}/in_one_line_charon.wav")
    results["in_one_line"] = r
    print(f"[B1REDESIGN-AUDIO] in_one_line: status={r.get('status')}")

    # --- Point見出し(Aoede) ---
    for name, text in (("point_one_heading", "First point."), ("point_two_heading", "Second point.")):
        print(f"[B1REDESIGN-AUDIO] {name}生成(Aoede): {text!r}...")
        r = point_headings.generate(text, f"{NARRATION_DIR}/{name}_aoede.wav")
        results[name] = r
        print(f"[B1REDESIGN-AUDIO] {name}: status={r.get('status')}")

    # --- News本文(Aoede、B1-B本文を無変更で使用) ---
    news_jobs = [
        ("full_story_part1", PARTS["part1"]),
        ("full_story_part2", PARTS["part2"]),
        ("point_one", PARTS["point_one_body"]),
        ("point_two", PARTS["point_two_body"]),
    ]
    for name, text in news_jobs:
        print(f"[B1REDESIGN-AUDIO] {name}生成(Aoede、News本文=B1-B無変更)...")
        r = news_tail_fix.generate_news_narration_wide_margin(text, f"{NARRATION_DIR}/{name}.wav")
        results[name] = r
        print(f"[B1REDESIGN-AUDIO] {name}: status={r.get('status')}")

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    with open(f"{OUT_DIR}/audit/segment_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    if failed:
        print(f"[B1REDESIGN-AUDIO] 生成失敗segmentあり、中断します: {failed}")
        return

    # --- Key Phrase Components(English, Aoede) + Japanese meaning(Charon、reading-safety経由) ---
    kp_items = sorted(kp_canon["items"], key=lambda it: it["rank"])
    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[B1REDESIGN-AUDIO] Key Phrase {rank} 英語Component生成(Aoede): {used_form!r}...")
        en_result = repro01.generate_key_phrase_component_verified(used_form, f"{NARRATION_DIR}/kp{rank}_en.wav")
        print(f"[B1REDESIGN-AUDIO] Key Phrase {rank} 日本語meaning生成(Charon、reading-safety経由): {ja_gloss!r}...")
        ja_result = generate_charon_japanese_with_reading_safety(
            ja_gloss, f"{NARRATION_DIR}/kp{rank}_ja_charon.wav", ja_gloss[:4])
        kp_results[rank] = {"english": en_result, "japanese": ja_result}
        print(f"[B1REDESIGN-AUDIO] Key Phrase {rank}: en={en_result.get('status')} ja={ja_result.get('status')}")

    with open(f"{OUT_DIR}/audit/key_phrase_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(kp_results, f, ensure_ascii=False, indent=2, default=str)

    kp_failed = [r for r, v in kp_results.items()
                 if v["english"].get("status") != "OK" or v["japanese"].get("status") != "OK"]

    summary = {
        "status": "OK" if not kp_failed else "PARTIAL",
        "segment_status": {k: v.get("status") for k, v in results.items()},
        "key_phrase_status": {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status"),
                                    "ja_reading_safety_changed": v["japanese"].get("reading_safety_changed_text")}
                               for r, v in kp_results.items()},
    }
    with open(f"{OUT_DIR}/run_summary_audio.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[B1REDESIGN-AUDIO] 全content生成完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
