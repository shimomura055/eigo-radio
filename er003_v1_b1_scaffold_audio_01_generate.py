# ============================================================
# er003_v1_b1_scaffold_audio_01_generate.py
# ER-003-B1-SCAFFOLD-AUDIO-01: A02 B1 Supported Natural English Audio Prototype
# ============================================================
# ER-003-B1-SCAFFOLD-01のB1 Supported Natural English(A02)を音声化する。
# ニュース本文(Full Story Part1/2、Point One/Two、In One Line)はB2 V2
# 版(ER-003-CEFR-DIRECT-02)と一字一句共通のテキストをそのまま読み上げる
# (別原稿を作らない)。Preview/Comment1-4は易しいSupport英語のテキストを
# 読み上げる(Comment 4はLedger deviation修正版、Previewは"is planning"
# 修正版)。Key Phrasesは5件、English->Japanese->English。
#
# 音声生成・組み立て・ASR検証は、既存Production機構(er002_common.py/
# er002_gemini_client.py/er003_b1_p9a_audio.py/er003_b1_p4_audio.py/
# er003_v1_repro01_main_generate.pyのgenerate_narration_snippet_
# verified_strict/generate_key_phrase_component_verified/
# MINIMAL_INSTRUCTION_PREFIX等)を読み取り専用でimportし、そのまま再利用
# する。新しいTTS style/instructionは、Preview/Comment用の短い単独発話
# にのみ、既存のMINIMAL_INSTRUCTION_PREFIX経路をASR strict検証付きで
# 適用する形で使う(新規style文言は作らない)。
#
# Production本体(CURRENT_SPEC.md、er002_ja_article_generation.py、
# 上記の各audio/TTSモジュール本体)は一切変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_scaffold_audio_01_generate.py

from __future__ import annotations

import json
import os
import re
import time

import numpy as np
import soundfile as sf
from dotenv import load_dotenv

import er002_common as common
import er003_b1_p4_audio as p4
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er003_v1_b1_scaffold_01_generate as scaffold
import er003_v1_en_direct_vfl_01_generate as vfl01
import er002_ja_web_research_r3 as r3

load_dotenv()

ARTICLE_ID = "A02"
OUT_DIR = "er003_output/b1_scaffold_audio_01/A02"
NARRATION_DIR = f"{OUT_DIR}/narration"
NUM_WORD_SOURCE_DIR = "er003_output/b1_p9a/A01/narration"  # service-level、article非依存

TARGET_SR = p9a.TARGET_SAMPLE_RATE  # 48000
PAUSE_SECONDS = 0.5  # 英語Comment<->英語本文間の暫定既定値(新territory、報告する)

KEY_PHRASES = [
    {"rank": 1, "used_form": "by default", "japanese_gloss": "初期設定で", "ja_expected": "初期設定"},
    {"rank": 2, "used_form": "curfew", "japanese_gloss": "利用禁止時間", "ja_expected": "利用禁止"},
    {"rank": 3, "used_form": "cross the finish line", "japanese_gloss": "完了する、成立に至る", "ja_expected": "完了する"},
    {"rank": 4, "used_form": "pilot", "japanese_gloss": "試験的な調査", "ja_expected": "試験的な調査"},
    # used_formは記事本文と同じ英国綴り"personalised feeds"を表示・記録用に保持する。
    # tts_textだけAmerican綴り"personalized feeds"を使う理由: 発音は完全に同一
    # (s/zはどちらも同じ音)で、Azure STT(en-US)がAmerican綴りへ正規化して
    # 書き起こすため、英国綴りのままではASR文字列検証(H節参照)が綴り差だけで
    # 毎回不合格になっていた。音声内容自体は変更していない。
    {"rank": 5, "used_form": "personalised feeds", "tts_text": "personalized feeds",
     "japanese_gloss": "個人向けに選ばれた投稿欄", "ja_expected": "投稿欄"},
]
NUM_WORDS = ["num_one", "num_two", "num_three", "num_four", "num_five"]


def get_client():
    return vfl01.get_client()


def strip_markdown_emphasis(text: str) -> str:
    """TTS入力直前のみで使う。固定B2本文中の`**強調**`記号(Markdown)と
    カーブ引用符(smart quotes “ ”)を除去・正規化する(単語自体は変更
    しない)。2026-08-14の生成試行で、"**“default”**"を含む
    Full Story Part 1が、`**`除去後もカーブ引用符が残っていたために
    引き続きGemini TTSから'Model tried to generate text, but it should
    only be used for TTS'という400エラーを返し続けていたことが判明した
    ため、カーブ引用符の除去も追加した(発見の経緯はレポートH節)。
    fixed_news_parts.json等、他の用途のテキストはこの関数を通さず元の
    Markdown/引用符を保持する。"""
    text = text.replace("**", "")
    text = text.replace("“", "").replace("”", "")
    return text


def _extract_words(text: str) -> list:
    return re.findall(r"[A-Za-z0-9']+", (text or "").lower())


def expected_words_present(expected_text: str, asr_text: str, n: int = 6) -> bool:
    """expected_textの先頭n語(句読点・改行・ハイフンを無視した単語列)が、
    asr_textの単語列の中に連続部分列として現れるかを判定する。
    単純な`text[:40] in asr_text`方式(改行を含む/単語途中で切れる/
    ハイフン付き複合語がASR側で空白区切りに正規化される/コンマの
    有無で文字列一致が崩れる、等)による偽陰性(実際は正しい音声なのに
    ASR検証が不合格になる)を避けるため、文字列包含ではなく単語列の
    連続部分列一致で判定する。"""
    expected_words = _extract_words(expected_text)[:n]
    if not expected_words:
        return False
    asr_words = _extract_words(asr_text)
    span = len(expected_words)
    for i in range(len(asr_words) - span + 1):
        if asr_words[i:i + span] == expected_words:
            return True
    return False


# ============================================================
# Step 0: Support textの最小修正(Comment 4 scope修正、Preview語彙修正)
# ============================================================
def build_fixed_support_texts() -> dict:
    with open(f"{scaffold.OUT_DIR}/support_texts.json", encoding="utf-8") as f:
        support_texts = json.load(f)

    support_texts["preview"] = support_texts["preview"].replace("Britain is considering", "Britain is planning")

    support_texts["comment_4"] = (
        "So, the night-curfew group found this easier to manage, and reported better sleep. "
        "But many just changed when they used social media, not how much. "
        "With that in mind, here is the story in one line."
    )
    return support_texts


def run_support_safety_recheck(client, support_texts: dict, ledger_text: str, topic: str) -> dict:
    support_concat = "\n\n".join(t for t in support_texts.values() if t)
    print("[AUDIO-PROTO] 修正後Support Ledger Deviation Check開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, support_concat)
    print(f"[AUDIO-PROTO] deviation={deviation_result['parsed']['overall_status']} "
          f"count={len(deviation_result['parsed']['deviations'])}")

    print("[AUDIO-PROTO] 修正後Support Fact Check開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, support_concat, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[AUDIO-PROTO] fact_check status={fc_status} verdict={verdict}")

    return {
        "ledger_deviation": deviation_result["parsed"],
        "fact_check": {"final_status": fc_status, "result": fc_result},
    }


# ============================================================
# Step 1: Support(Preview/Comment)音声 — MINIMAL_INSTRUCTION経路+ASR strict検証
# ============================================================
def generate_support_narration_verified(text: str, out_path: str, max_attempts: int = 6,
                                         max_extra_chars: int = 15) -> dict:
    """ENGLISH_STYLE_PREFIX(『complete story』読み上げ前提の長い指示)は
    短い単独のnavigationコメントには不適合と判断し、既存のKey Phrase
    Component fallback経路(MINIMAL_INSTRUCTION_PREFIX、warm podcast
    announcer voice)をPreview/Comment全件の主経路として使う。新しい
    instruction文言は作らない(既存文言をそのまま流用)。ASR検証は
    expected_words_present(単語列の連続部分列一致)で行う(H節参照)。"""
    max_len = len(text) + max_extra_chars
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        r = repro01.generate_english_component_minimal_instruction(text, out_path)
        if r.get("status") != "OK":
            attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        substring_ok = expected_words_present(text, asr_text)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = substring_ok and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "substring_ok": substring_ok, "length_ok": length_ok, "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["attempts_log"] = attempts_log
            r["instruction_type"] = "minimal"
            return r
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


# ============================================================
# Step 2: News本文音声(Full Story/Point/In One Line)
# ============================================================
def generate_news_narration_verified(text: str, out_path: str, max_attempts: int = 6,
                                      max_extra_chars: int = 15) -> dict:
    """まずENGLISH_STYLE_PREFIX(complete story読み上げ前提、Full Story
    本文の既存経路)を試みる。2026-08-14の生成試行で、"The word default
    matters."という自己言及的な一文を含むFull Story Part 1が、
    MarkdownやSmart Quoteを除去した後も毎回'Model tried to generate
    text, but it should only be used for TTS'という400エラーを返す
    ことが判明した(H節)。この場合、Key Phrase Componentの既存fallback
    経路と同じMINIMAL_INSTRUCTION_PREFIXへ切り替える(新しいinstruction
    文言は作らない、テキスト自体も変更しない)。ASR検証はexpected_
    words_present(単語列の連続部分列一致)で行う。"""
    max_len = len(text) + max_extra_chars
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        r = p9a.generate_narration_snippet(text, "en", out_path)
        instruction_type = "english_style_prefix"
        if r.get("status") != "OK":
            attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                  "instruction_type": instruction_type})
            r = repro01.generate_english_component_minimal_instruction(text, out_path)
            instruction_type = "minimal_fallback"
            if r.get("status") != "OK":
                attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                      "instruction_type": instruction_type})
                continue
        asr_text, err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        substring_ok = expected_words_present(text, asr_text)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = substring_ok and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "substring_ok": substring_ok,
                              "length_ok": length_ok, "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["attempts_log"] = attempts_log
            r["instruction_type"] = instruction_type
            return r
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


# ============================================================
# Step 3: 音声読み込み・stereo変換
# ============================================================
def load_mono_as_stereo(path: str) -> "np.ndarray":
    samples, framerate, channels, nframes = common.read_wav_float(path)
    if channels != 1:
        raise RuntimeError(f"想定外のchannels={channels}: {path}")
    if framerate != common.SAMPLE_RATE:
        raise RuntimeError(f"想定外のframerate={framerate}: {path}")
    return p9a.mono_24k_to_stereo_target(samples, TARGET_SR)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = get_client()

    b2_text = scaffold.load_text(scaffold.B2_ARTICLE_PATH)
    ledger_text = scaffold.load_text(scaffold.LEDGER_TEXT_PATH)
    parts = scaffold.split_fixed_news_text(b2_text)

    # --- Step 0 ---
    support_texts = build_fixed_support_texts()
    with open(f"{OUT_DIR}/support_texts_fixed.json", "w", encoding="utf-8") as f:
        json.dump(support_texts, f, ensure_ascii=False, indent=2)
    safety = run_support_safety_recheck(client, support_texts, ledger_text, scaffold.TOPIC)
    with open(f"{OUT_DIR}/support_safety_recheck.json", "w", encoding="utf-8") as f:
        json.dump(safety, f, ensure_ascii=False, indent=2)
    if safety["ledger_deviation"]["overall_status"] != "LEDGER_COMPLIANT":
        print("[AUDIO-PROTO] LEDGER_COMPLIANTではないため中断します。")
        return

    # --- Step 1: Support音声(Preview + Comment1-4) ---
    support_jobs = [
        ("preview", support_texts["preview"]),
        ("comment_1", support_texts["comment_1"]),
        ("comment_2", support_texts["comment_2"]),
        ("comment_3", support_texts["comment_3"]),
        ("comment_4", support_texts["comment_4"]),
    ]
    audio_results = {}
    for name, text in support_jobs:
        print(f"[AUDIO-PROTO] Support音声生成: {name}...")
        out_path = f"{NARRATION_DIR}/{name}.wav"
        r = generate_support_narration_verified(text, out_path)
        audio_results[name] = r
        print(f"[AUDIO-PROTO] {name}: status={r.get('status')}")

    # --- Step 2: News本文音声(TTS入力直前でMarkdown強調記号・カーブ引用符のみ除去、H節参照) ---
    _part1_tts = strip_markdown_emphasis(parts["part1"])
    _part2_tts = strip_markdown_emphasis(parts["part2"])
    _point_one_tts = strip_markdown_emphasis(f"{parts['point_one_heading']}. {parts['point_one_body']}")
    _point_two_tts = strip_markdown_emphasis(f"{parts['point_two_heading']}. {parts['point_two_body']}")
    _in_one_line_tts = strip_markdown_emphasis(parts["in_one_line"])
    news_jobs = [
        ("full_story_part1", _part1_tts),
        ("full_story_part2", _part2_tts),
        ("point_one", _point_one_tts),
        ("point_two", _point_two_tts),
        ("in_one_line", _in_one_line_tts),
    ]
    for name, text in news_jobs:
        print(f"[AUDIO-PROTO] News音声生成: {name}...")
        out_path = f"{NARRATION_DIR}/{name}.wav"
        r = generate_news_narration_verified(text, out_path)
        audio_results[name] = r
        print(f"[AUDIO-PROTO] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/segment_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(audio_results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in audio_results.items() if v.get("status") != "OK"]
    if failed:
        print(f"[AUDIO-PROTO] 生成失敗segmentあり、中断します: {failed}")
        return

    # --- Step 4: Key Phrase Components(English + Japanese meaning) ---
    kp_results = {}
    for kp in KEY_PHRASES:
        rank = kp["rank"]
        tts_text = kp.get("tts_text", kp["used_form"])
        print(f"[AUDIO-PROTO] Key Phrase {rank} 英語Component生成: {tts_text!r}...")
        en_path = f"{NARRATION_DIR}/kp{rank}_en.wav"
        en_result = repro01.generate_key_phrase_component_verified(tts_text, en_path)
        print(f"[AUDIO-PROTO] Key Phrase {rank} 日本語meaning生成: {kp['japanese_gloss']!r}...")
        ja_path = f"{NARRATION_DIR}/kp{rank}_ja.wav"
        ja_result = repro01.generate_narration_snippet_verified_strict(
            kp["japanese_gloss"], "ja", ja_path, kp["ja_expected"])
        kp_results[rank] = {"english": en_result, "japanese": ja_result}
        print(f"[AUDIO-PROTO] Key Phrase {rank}: en={en_result.get('status')} ja={ja_result.get('status')}")

    with open(f"{OUT_DIR}/audit/key_phrase_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(kp_results, f, ensure_ascii=False, indent=2, default=str)

    kp_failed = [r for r, v in kp_results.items()
                 if v["english"].get("status") != "OK" or v["japanese"].get("status") != "OK"]
    if kp_failed:
        print(f"[AUDIO-PROTO] Key Phrase生成失敗あり、中断します: {kp_failed}")
        return

    # --- Step 5: 組み立て ---
    print("[AUDIO-PROTO] 音声組み立て開始...")
    news_stereo = {name: load_mono_as_stereo(f"{NARRATION_DIR}/{name}.wav")
                   for name, _ in news_jobs}
    support_stereo = {name: load_mono_as_stereo(f"{NARRATION_DIR}/{name}.wav")
                      for name, _ in support_jobs}

    # gain基準: News本文(Full Story/Point/In One Line)のRMS平均をアンカーにする
    news_rms_values = [p9a.rms(news_stereo[n]) for n, _ in news_jobs]
    target_rms = float(np.mean(news_rms_values))

    def gain_matched(samples):
        gain = p9a.compute_gain_for_target_rms(samples, target_rms)
        return samples * gain, gain

    gain_report = {}
    for name in news_stereo:
        news_stereo[name], gain = gain_matched(news_stereo[name])
        gain_report[name] = gain
    for name in support_stereo:
        support_stereo[name], gain = gain_matched(support_stereo[name])
        gain_report[name] = gain

    num_word_stereo = []
    for num_name in NUM_WORDS:
        arr = load_mono_as_stereo(f"{NUM_WORD_SOURCE_DIR}/{num_name}.wav")
        arr, gain = gain_matched(arr)
        num_word_stereo.append(arr)
        gain_report[num_name] = gain

    kp_en_stereo, kp_ja_stereo = {}, {}
    for kp in KEY_PHRASES:
        rank = kp["rank"]
        en_arr = load_mono_as_stereo(f"{NARRATION_DIR}/kp{rank}_en.wav")
        ja_arr = load_mono_as_stereo(f"{NARRATION_DIR}/kp{rank}_ja.wav")
        en_arr, gain_en = gain_matched(en_arr)
        ja_arr, gain_ja = gain_matched(ja_arr)
        kp_en_stereo[rank] = en_arr
        kp_ja_stereo[rank] = ja_arr
        gain_report[f"kp{rank}_en"] = gain_en
        gain_report[f"kp{rank}_ja"] = gain_ja

    pause = p9a.silence_stereo(PAUSE_SECONDS, TARGET_SR)

    key_phrase_blocks = [
        p9a.build_key_phrase_block(num_word_stereo[kp["rank"] - 1], kp_en_stereo[kp["rank"]],
                                    kp_ja_stereo[kp["rank"]], TARGET_SR)
        for kp in KEY_PHRASES
    ]
    key_phrases_section = np.concatenate(key_phrase_blocks)

    timeline = [
        ("Preview", support_stereo["preview"]),
        ("pause", pause),
        ("Key Phrases (5 items)", key_phrases_section),
        ("pause", pause),
        ("Comment 1", support_stereo["comment_1"]),
        ("pause", pause),
        ("Full Story Part 1", news_stereo["full_story_part1"]),
        ("pause", pause),
        ("Comment 2", support_stereo["comment_2"]),
        ("pause", pause),
        ("Full Story Part 2", news_stereo["full_story_part2"]),
        ("pause", pause),
        ("Comment 3", support_stereo["comment_3"]),
        ("pause", pause),
        ("Point One", news_stereo["point_one"]),
        ("pause", pause),
        ("Point Two", news_stereo["point_two"]),
        ("pause", pause),
        ("Comment 4", support_stereo["comment_4"]),
        ("pause", pause),
        ("In One Line", news_stereo["in_one_line"]),
    ]
    final_audio = np.concatenate([piece for _, piece in timeline])

    final_wav_path = f"{OUT_DIR}/b1_scaffold_final.wav"
    common.write_wav_float(final_wav_path, final_audio, TARGET_SR, 2)
    print(f"[AUDIO-PROTO] final wav書き出し完了: {final_wav_path} "
          f"({len(final_audio) / TARGET_SR:.1f}秒)")

    final_mp3_path = f"{OUT_DIR}/b1_scaffold_final.mp3"
    sf.write(final_mp3_path, final_audio, TARGET_SR, format="MP3")
    print(f"[AUDIO-PROTO] final mp3書き出し完了: {final_mp3_path}")

    timeline_log = [{"part": name, "duration_seconds": round(len(piece) / TARGET_SR, 3)}
                     for name, piece in timeline]
    with open(f"{OUT_DIR}/timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline_log, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(gain_report, f, ensure_ascii=False, indent=2)

    summary = {
        "article_id": ARTICLE_ID,
        "total_duration_seconds": round(len(final_audio) / TARGET_SR, 2),
        "final_wav_path": final_wav_path, "final_mp3_path": final_mp3_path,
        "target_rms_anchor": target_rms,
        "pause_seconds_between_parts": PAUSE_SECONDS,
        "segment_status": {k: v.get("status") for k, v in audio_results.items()},
        "key_phrase_status": {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                               for r, v in kp_results.items()},
        "support_ledger_status": safety["ledger_deviation"]["overall_status"],
        "support_fact_status": safety["fact_check"]["final_status"],
        "support_fact_verdict": (safety["fact_check"]["result"] or {}).get("verdict"),
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[AUDIO-PROTO] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
