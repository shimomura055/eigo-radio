# ============================================================
# er003_v1_n3_01_tts_generate.py
# ER-003-A2-B1-N3-01: 3テーマ×2レベル 全segment TTS/ASR生成
# ============================================================
# 既存の確立済み生成関数をそのまま再利用する(新しいTTS instructionは
# 設計しない):
#   B1 Charon英語: voice01.generate_charon_english
#   B1/共通 Aoede英語(News本文・Point見出し): news_tail_fix.
#     generate_news_narration_wide_margin / point_headings.generate
#   Key Phrase英語Component: repro01.generate_key_phrase_component_verified
#   Charon日本語+reading-safety: to_tts_safe_japanese_fraction_reading()
#     を通したうえでvoice01.generate_charon_japanese
#   A2英語(単一Aoede): crosslevel_audio_02_common.
#     generate_english_segment_with_fallback
#   A2日本語(単一Aoede、reading-safety経由): repro01.
#     generate_narration_snippet_verified_strict(language="ja")相当を
#     reading-safety wrapperでラップ
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_tts_generate.py <theme_id>
#   (theme_idを省略すると3テーマ全部を実行)

from __future__ import annotations

import json
import os
import sys

import er003_audio_tts_asr_safety as safety
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_articles_generate as gen
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01

JAPANESE_TITLES = {
    "hanshin": "早い先制、そして危なげない勝利。阪神が広島に8対1で完勝",
    "health": "小さな習慣の積み重ねは、健康にどう関係するのか",
    "household": "冷蔵庫の野菜室、2つの設定を使い分けると食品が長持ちする",
}


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def generate_charon_japanese_with_reading_safety(text: str, out_path: str, expected_substring: str,
                                                   max_attempts: int = 6) -> dict:
    placeholder_safe = tts_safe_ja(text)
    tts_input = safety.to_tts_safe_japanese_fraction_reading(placeholder_safe)
    r = voice01.generate_charon_japanese(tts_input, out_path, expected_substring, max_attempts=max_attempts)
    r["canonical_text"] = text
    r["tts_input_text_after_reading_safety"] = tts_input
    r["reading_safety_changed_text"] = (tts_input != text)
    return r


# ER-003-N3-ROOT-FIX-01(2026-08-17): A2の短い日本語Key Phrase訳
# (meaning_N)も、B1のkp_ja_charonと同じ「短いフレーズ+長いJAPANESE_
# STYLE_PREFIX」の組み合わせで、voice01.generate_charon_japaneseと同種
# のinstruction leakageに晒されうる(標準経路はvoice=Aoede、
# c.generate_narration_snippet_verified_strict=repro01の同名関数の
# エイリアス)。voice01側に追加したのと同じ考え方のfallbackを、A2の
# Aoede経路にも用意する。
_A2_JA_MINIMAL_INSTRUCTION_PREFIX = (
    "次の文章だけを、翻訳・言い換え・追加をせず、自然で温かいpodcastの"
    "ナレーターの声でそのまま読み上げてください。\n\n"
)


def _generate_a2_japanese_minimal_instruction(text: str, out_path: str) -> dict:
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er003_b1_p9a_audio as p9a
    prompt = _A2_JA_MINIMAL_INSTRUCTION_PREFIX + text
    call_fn = p9a._make_japanese_call_fn()
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"minimal instructionでもTTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {"status": "OK", "text": text, "path": out_path, "trim_info": trim_info,
            "clipping_detected": metrics["clipping_detected"], "instruction": "minimal (not JAPANESE_STYLE_PREFIX)"}


def generate_a2_japanese_with_fallback(text: str, out_path: str, expected_substring: str,
                                        max_extra_chars: int = 40, max_attempts: int = 6) -> dict:
    """標準経路(JAPANESE_STYLE_PREFIX)が合格しない場合、minimal
    instructionへフォールバックする(声・モデルは変えない)。
    ER-003-N3-ROOT-FIX-01: 短いA2日本語フレーズのinstruction
    leakage対策。"""
    import er003_b1_p4_audio as p4
    standard = c.generate_narration_snippet_verified_strict(
        text, "ja", out_path, expected_substring, max_attempts=max_attempts, max_extra_chars=max_extra_chars)
    if standard.get("status") == "OK":
        standard["fallback_used"] = False
        return standard

    max_len = len(text) + max_extra_chars
    fallback_attempts = []
    for attempt in range(1, max_attempts + 1):
        r = _generate_a2_japanese_minimal_instruction(text, out_path)
        if r.get("status") != "OK":
            fallback_attempts.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err = p4.get_full_text_via_azure_stt_continuous(out_path, language="ja-JP")
        substring_ok = asr_text is not None and expected_substring.lower() in asr_text.lower()
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = substring_ok and length_ok
        fallback_attempts.append({"attempt": attempt, "status": "OK", "asr_text": asr_text, "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = standard.get("attempts_log")
            r["fallback_attempts_log"] = fallback_attempts
            return r
    return {"status": "STOPPED", "reason": f"標準経路・minimal instruction経路とも{max_attempts}回で不合格",
            "standard_attempts_log": standard.get("attempts_log"), "fallback_attempts_log": fallback_attempts}


def generate_a2_japanese_with_reading_safety(text: str, out_path: str, expected_substring: str,
                                              max_extra_chars: int = 40, max_attempts: int = 6) -> dict:
    placeholder_safe = tts_safe_ja(text)
    tts_input = safety.to_tts_safe_japanese_fraction_reading(placeholder_safe)
    r = generate_a2_japanese_with_fallback(
        tts_input, out_path, expected_substring, max_attempts=max_attempts, max_extra_chars=max_extra_chars)
    r["canonical_text"] = text
    r["tts_input_text_after_reading_safety"] = tts_input
    r["reading_safety_changed_text"] = (tts_input != text)
    return r


_EN_STRIP_PUNCT = ",.;:!?“”\"()[]"


def first_words(text: str, n: int = 4) -> str:
    # ASRは引用符・句読点を書き起こしに再現しないことが多いため、
    # 期待文字列側の各語からも同じ記号を取り除く(Health themeの
    # topic_intro/point_one_headingで実際に発生した偽陰性への対応)。
    # 綴られた小さな数もTTS入力側と同じく算用数字へ変換する(Household
    # themeのa2 topic_introで実際に発生した偽陰性: "Two"のままだと
    # TTS入力側で変換済みの"2"というASR書き起こしと一致しなかった)。
    safe = tts_safe_number_words_en(tts_safe_en(text))
    words = safe.strip().split()
    cleaned = [w.strip(_EN_STRIP_PUNCT) for w in words[:n]]
    return " ".join(w for w in cleaned if w)


# 既に確立済みの2件のTTS入力専用normalization(canonical textは変更しない):
#   (1) カーリーアポストロフィ(U+2019)→ストレートアポストロフィ
#       (ASRの書き起こしはストレートのみを認識するため、curly混在時に
#       単語トークン化がずれてASR一致検証が失敗する。ER-003-B1-
#       REDESIGN-AUDIO-01のpreview音切れ調査で確立済みのTTS入力限定の
#       置換をここでも再利用する)
#   (2) 先頭の「～」placeholder除去(ER-003-B1-REDESIGN-AUDIO-01系の
#       SING01 kp5で確立済み。「～」は発音されない記号であり、ASR側の
#       書き起こしにも現れないため、期待文字列側からも同じ規則で除去する)
def tts_safe_en(text: str) -> str:
    # カーリーシングル/ダブルクォートはASRの書き起こしに現れない
    # (発音されない記号のため)、期待文字列側からも取り除く。
    return text.replace("’", "'").replace("‘", "'").replace("“", "").replace("”", "")


# 追加で確立した2件のTTS入力専用normalization(Health themeで発見):
#   (3) 綴られた小さな数(two〜twelve)→算用数字。ASRは口頭の小さな数を
#       算用数字へ正規化して書き起こすことが多く(例: "two"→"2")、
#       canonical textが綴りのままだと単語トークンが一致せずASR一致
#       検証が失敗する。TTSは算用数字を渡しても綴りと同じ発音になる
#       ため、読み上げ内容には影響しない
#   (4) 段落区切り(空行)を単一の空白へ統合。空行の直後にcolon付きの
#       短いフレーズが続く構造(例: 数値の列挙)で、TTSが不自然な間を
#       置き、ASRが書き起こし上に余計な文区切りを挿入する事例が
#       Hanshin/Healthの両テーマで確認された。地の文として自然に
#       読める形にする(語は一切変更しない)
_EN_NUMBER_WORDS = {
    "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
}
_EN_NUMBER_WORD_RE = __import__("re").compile(
    r"\b(" + "|".join(_EN_NUMBER_WORDS.keys()) + r")\b", flags=__import__("re").IGNORECASE)


def tts_safe_number_words_en(text: str) -> str:
    def _sub(m):
        return _EN_NUMBER_WORDS[m.group(1).lower()]
    return _EN_NUMBER_WORD_RE.sub(_sub, text)


def tts_safe_paragraphs_en(text: str) -> str:
    return " ".join(p.strip() for p in text.split("\n\n") if p.strip())


def tts_safe_news_en(text: str) -> str:
    return tts_safe_number_words_en(tts_safe_paragraphs_en(tts_safe_en(text)))


# Key Phrase英語Componentの既知の失敗パターン(Health themeで発見):
# "healthspan"のような複合語はASRが"Health Span"と2語に分けて書き起こす
# ことが多く、"moderate-to-vigorous"のようなハイフン複合語はASRが
# ハイフンをスペースに正規化して書き起こす。generate_key_phrase_
# component_verified()は与えたtextそのものを比較対象に使うため、
# ハイフン→スペース・既知の複合語→分割語のnormalizationをTTS入力
# (かつ比較対象)として適用する。実際の発音はほぼ変わらない
_KP_COMPOUND_OVERRIDES = {"healthspan": "health span", "lifespan": "life span"}


def tts_safe_kp_en(text: str) -> str:
    safe = tts_safe_en(text).replace("-", " ")
    for compound, split in _KP_COMPOUND_OVERRIDES.items():
        safe = __import__("re").sub(compound, split, safe, flags=__import__("re").IGNORECASE)
    return safe


def tts_safe_ja(text: str) -> str:
    return text.lstrip("～").replace("’", "'")


_JA_KANJI_NUMERALS = set("一二三四五六七八九十百千万億〇")
_JA_PUNCTUATION = set("、。！？「」『』・…—―‥～")


def expected_substring_ja(text: str, n: int = 2) -> str:
    """先頭N文字を機械的に使うと、句読点(ASRが書き起こしで再現しない
    ことが多い)や漢数字(ASRが算用数字へ正規化することが多い)を含む
    ことがあり、実際には内容が正しいのに部分一致検証が偽陰性になる
    (このN3-01タスクのHanshin previewで実際に発生: 期待文字列
    "今回は、"の読点がASR書き起こしに現れず不一致になった)。句読点・
    漢数字・算用数字を含まない、最初の安全な連続N文字を探して使う。
    Health themeでは、2つの2文字語が連結した4文字語(例:「観察研究」)
    の自然な語境界にASRが読点を挿入する例が見つかったため、既定のNは
    その語境界をまたがない2文字とする(元は4→3で試したが、いずれも
    「観察」「研究」の境界をまたぐ3文字窓が選ばれ解決しなかった)。"""
    safe = tts_safe_ja(text)
    for i in range(len(safe) - n + 1):
        window = safe[i:i + n]
        if any(ch in _JA_PUNCTUATION or ch in _JA_KANJI_NUMERALS or ch.isdigit() for ch in window):
            continue
        return window
    return safe[:n]


# ============================================================
# B1 segment生成
# ============================================================
def generate_b1_segments(theme: dict) -> dict:
    theme_id = theme["theme_id"]
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")

    results = {}

    topic_intro_text = f"Today's topic is {parts['title']}."
    print(f"[N3-TTS][{theme_id}/b1b] topic_intro生成(Charon)...")
    results["topic_intro"] = voice01.generate_charon_english(
        tts_safe_number_words_en(tts_safe_en(topic_intro_text)), f"{narration_dir}/topic_intro.wav")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        print(f"[N3-TTS][{theme_id}/b1b] {name}生成(Charon)...")
        results[name] = voice01.generate_charon_english(
            tts_safe_number_words_en(tts_safe_en(text)), f"{narration_dir}/{name}.wav")
        results[name]["canonical_text"] = text

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        print(f"[N3-TTS][{theme_id}/b1b] {name}生成(Aoede、semantic heading)...")
        results[name] = point_headings.generate(
            tts_safe_number_words_en(tts_safe_en(text)), f"{narration_dir}/{name}.wav")
        results[name]["canonical_text"] = text

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        ("point_one", parts["point_one_body"]), ("point_two", parts["point_two_body"]),
        ("in_one_line", parts["in_one_line"]),
    ):
        print(f"[N3-TTS][{theme_id}/b1b] {name}生成(Aoede、News本文)...")
        results[name] = news_tail_fix.generate_news_narration_wide_margin(
            tts_safe_news_en(text), f"{narration_dir}/{name}.wav")
        results[name]["canonical_text"] = text

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[N3-TTS][{theme_id}/b1b] Key Phrase {rank} 英語Component生成(Aoede): {used_form!r}...")
        en_r = repro01.generate_key_phrase_component_verified(tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav")
        print(f"[N3-TTS][{theme_id}/b1b] Key Phrase {rank} 日本語meaning生成(Charon、reading-safety): {ja_gloss!r}...")
        ja_r = generate_charon_japanese_with_reading_safety(
            ja_gloss, f"{narration_dir}/kp{rank}_ja_charon.wav", expected_substring_ja(ja_gloss))
        kp_results[rank] = {"english": en_r, "japanese": ja_r}

    all_status = {k: v.get("status") for k, v in results.items()}
    kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                 for r, v in kp_results.items()}
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": results, "key_phrases": kp_results}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump({"segment_status": all_status, "key_phrase_status": kp_status}, f, ensure_ascii=False, indent=2)
    print(f"[N3-TTS][{theme_id}/b1b] 完了。segment_status={all_status} kp_status={kp_status}")
    return {"segment_status": all_status, "key_phrase_status": kp_status}


# ============================================================
# A2 segment生成
# ============================================================
def generate_a2_segments(theme: dict) -> dict:
    theme_id = theme["theme_id"]
    out_dir = f"{theme['out_dir']}/a2"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/a2_support_texts.json")
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")

    results = {}

    topic_intro_text = f"Today's topic is {parts['title']}."
    print(f"[N3-TTS][{theme_id}/a2] topic_intro生成(Aoede、A2既存単一Voice)...")
    results["topic_intro"] = c.generate_english_segment_with_fallback(
        tts_safe_number_words_en(tts_safe_en(topic_intro_text)), f"{narration_dir}/topic_intro.wav",
        first_words(parts["title"], 3), max_extra_chars=30)
    results["topic_intro"]["canonical_text"] = topic_intro_text

    ja_title = JAPANESE_TITLES[theme_id]
    print(f"[N3-TTS][{theme_id}/a2] japanese_title生成: {ja_title!r}...")
    results["japanese_title"] = generate_a2_japanese_with_reading_safety(
        ja_title, f"{narration_dir}/japanese_title.wav", expected_substring_ja(ja_title), max_extra_chars=30)

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        print(f"[N3-TTS][{theme_id}/a2] {name}生成(日本語)...")
        results[name] = generate_a2_japanese_with_reading_safety(
            text, f"{narration_dir}/{name}.wav", expected_substring_ja(text))

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        print(f"[N3-TTS][{theme_id}/a2] {name}生成(英語、semantic heading)...")
        results[name] = c.generate_english_segment_with_fallback(
            tts_safe_number_words_en(tts_safe_en(text)), f"{narration_dir}/{name}.wav",
            first_words(text, 3), max_extra_chars=20)
        results[name]["canonical_text"] = text

    for name, text, sub in (
        ("full_story_part1", parts["part1"], first_words(parts["part1"])),
        ("full_story_part2", parts["part2"], first_words(parts["part2"])),
        ("point_one", parts["point_one_body"], first_words(parts["point_one_body"])),
        ("point_two", parts["point_two_body"], first_words(parts["point_two_body"])),
        ("in_one_line", parts["in_one_line"], first_words(parts["in_one_line"])),
    ):
        print(f"[N3-TTS][{theme_id}/a2] {name}生成(英語News本文)...")
        results[name] = c.generate_english_segment_with_fallback(tts_safe_news_en(text), f"{narration_dir}/{name}.wav", sub)
        results[name]["canonical_text"] = text

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_results = {}
    for i, item in enumerate(kp_items, start=1):
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[N3-TTS][{theme_id}/a2] Key Phrase {rank} 英語Component生成(Aoede): {used_form!r}...")
        en_r = repro01.generate_key_phrase_component_verified(tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav")
        print(f"[N3-TTS][{theme_id}/a2] meaning_{i}生成(日本語): {ja_gloss!r}...")
        ja_r = generate_a2_japanese_with_reading_safety(
            ja_gloss, f"{narration_dir}/meaning_{i}.wav", expected_substring_ja(ja_gloss), max_extra_chars=30)
        kp_results[rank] = {"english": en_r, "japanese_meaning": ja_r}

    all_status = {k: v.get("status") for k, v in results.items()}
    kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")}
                 for r, v in kp_results.items()}
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": results, "key_phrases": kp_results}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump({"segment_status": all_status, "key_phrase_status": kp_status}, f, ensure_ascii=False, indent=2)
    print(f"[N3-TTS][{theme_id}/a2] 完了。segment_status={all_status} kp_status={kp_status}")
    return {"segment_status": all_status, "key_phrase_status": kp_status}


def run_theme(theme: dict) -> dict:
    b1_result = generate_b1_segments(theme)
    a2_result = generate_a2_segments(theme)
    return {"b1b": b1_result, "a2": a2_result}


def main():
    theme_ids = sys.argv[1:] or [t["theme_id"] for t in gen.THEMES]
    themes_by_id = {t["theme_id"]: t for t in gen.THEMES}
    for theme_id in theme_ids:
        run_theme(themes_by_id[theme_id])
    print("[N3-TTS] 完了。")


if __name__ == "__main__":
    main()
