# ============================================================
# er003_b1_p3s_audio.py
# ER-003-B1-P3S: 日英分離TTS・短尺結合サンプル検証
# ============================================================
# ER-003-B1-P3Rで、日本語・英語が混在するListening Preview全文の単発
# TTS生成がAoedeで技術的に失敗した(モデルが音声ではなくテキスト応答を
# 試みた)ことを受け、Pattern A原稿から1箇所だけ「日本語span→英語Key
# Phrase→日本語span」を切り出し、3つを別々にTTS生成してから短尺結合
# した場合に技術的に成立するかを検証する。Pattern A全文・B1本文の生成
# は行わない。
#
# 新しいTTS instruction・別voiceは一切導入しない。B2までに採用済みの
# 同一instruction(er002_common.build_style_prefix、無変更)を3span
# すべてに使う。
#
# 再利用するもの(再実装しない):
#   - er002_common.build_style_prefix/SAMPLE_RATE/_call_tts_with_retry/
#     assemble_audio/pcm_to_wav_bytes/pcm_bytes_to_float_mono/
#     write_wav_float/measure_metrics/apply_dynamics3_once/MODEL_NAME
#   - er002_gemini_client.make_tts_call_fn(voice_name)
#   - er003_b1_p3r_audio.load_pattern_a_text/sha256_text/
#     PATTERN_A_SOURCE_PATH/VOICE_NAME(ER-003-B1-P3Rと同一source・
#     同一voice)
#
# 新規に追加するのは、Pattern A原稿から3spanを決定的に切り出す
# select_excerpt()のみ(この用途の既存実装がないため)。

from __future__ import annotations

import re
from typing import Optional

import er003_b1_p3r_audio as p3r

ARTICLE_ID = "A01"
VOICE_NAME = p3r.VOICE_NAME  # "Aoede"(P3Rと同一)

PATTERN_A_SOURCE_PATH = p3r.PATTERN_A_SOURCE_PATH
sha256_text = p3r.sha256_text
load_pattern_a_text = p3r.load_pattern_a_text
build_style_prefix = p3r.build_style_prefix
build_tts_prompt = p3r.build_tts_prompt

DEFAULT_KEY_PHRASE = "shot on target"

# 境界の無音は、本ステージ限定の初回技術値(正式仕様ではない)。
JOIN_PAUSE_SECONDS = 0.2

# 技術的失敗時のみ、同一payloadでspanごとに最大1回まで再試行する
# (品質目的の再生成は行わない)。
MAX_TTS_TECHNICAL_RETRY = 1

_TERMINAL_PUNCT_RE = re.compile(r"[。！？]")


def select_excerpt(pattern_a_text: str, key_phrase: str = DEFAULT_KEY_PHRASE) -> dict:
    """Pattern A原稿から、指定Key Phraseを含む「日本語span→英語Key
    Phrase→日本語span」を、文頭側は直前の文末記号の直後から、文末側は
    直後の文末記号までの範囲で、決定的に切り出す。語句の変更・要約・
    接続語の追加は一切行わない(Markdown/句読点の変更もしない)。"""
    idx = pattern_a_text.find(key_phrase)
    if idx == -1:
        raise ValueError(f"Key Phrase {key_phrase!r}がPattern A原稿内に見つかりません")

    preceding_terminal = pattern_a_text.rfind("。", 0, idx)
    ja_before_start = preceding_terminal + 1 if preceding_terminal != -1 else 0
    ja_before = pattern_a_text[ja_before_start:idx]

    after_start = idx + len(key_phrase)
    m = _TERMINAL_PUNCT_RE.search(pattern_a_text, after_start)
    if m is None:
        raise ValueError("Key Phrase直後に文末記号が見つかりません")
    ja_after = pattern_a_text[after_start:m.end()]

    if not ja_before.strip():
        raise ValueError("日本語前spanが空です(このKey Phraseは冒頭に前置spanを持ちません)")
    if not ja_after.strip():
        raise ValueError("日本語後spanが空です")

    reconstructed = ja_before + key_phrase + ja_after
    original_span = pattern_a_text[ja_before_start:m.end()]
    if reconstructed != original_span:
        raise ValueError("3spanを結合した結果が原文の該当範囲と一致しません(切り出しロジックの不整合)")

    return {
        "key_phrase": key_phrase,
        "ja_before": ja_before,
        "en_keyword": key_phrase,
        "ja_after": ja_after,
        "reconstructed": reconstructed,
        "punctuation_adjusted": False,
    }
