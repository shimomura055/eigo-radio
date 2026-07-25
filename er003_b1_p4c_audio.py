# ============================================================
# er003_b1_p4c_audio.py
# ER-003-B1-P4C: 「目印」マーカーでListening Preview完成版を再生成
# ============================================================
# P4Bでは、marker語「合図」自体は正しく発話されていたが、ASRの表記が
# 「合図」「会津」「アイズ」のように揺れ、文字列完全一致のQAが誤って
# chunk05を停止させた。今回はmarkerを「目印」へ統一し、ASRは言語・
# 内容の診断にとどめ(表記完全一致を合否条件にしない)、marker区間の
# 正式な特定はMFAで行う。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p4b_audio.build_chunk_plan/verify_chunk_plan_static
#     (marker_token引数を追加済み。デフォルトは「合図」のまま、
#     P4B時点の挙動・テストに影響しない)
#   - er003_b1_p4b_audio.JAPANESE_STYLE_PREFIX/ENGLISH_STYLE_PREFIX/
#     VOICE_NAME/MAX_TTS_TECHNICAL_RETRY/PATTERN_A_SOURCE_PATH/
#     GAP_BEFORE_TARGET_SECONDS/GAP_AFTER_TARGET_SECONDS/
#     GAP_TOLERANCE_SECONDS/EN_TRIM_SAFETY_MARGIN_SECONDS/
#     EXISTING_SHOT_ON_TARGET_PATH/_LAST_FEW_MINUTES_PHRASE/
#     _ASCII_LETTER_PATTERN/build_tts_prompt
#   - er003_b1_p4_audio.get_full_text_via_azure_stt_continuous/
#     _strip_punctuation/find_all_marker_spans/
#     spans_are_monotonic_non_overlapping
#   - er003_b1_p3u_audio.find_speech_bounds/trim_english_keyword_silence
#   - er003_b1_p3w_audio.MFA_*/run_mfa_align/parse_textgrid_words_tier
#   - er003_b1_p3z_audio.adjust_trailing_silence/adjust_leading_silence
#
# 新規に追加するのは、(1) marker語「目印」の定数・token列、(2) ASRの
# 表記揺れを許容する内容確認ロジック(check_chunk_content)、の2つのみ。

from __future__ import annotations

import difflib

import er003_b1_p4_audio as p4
import er003_b1_p4b_audio as p4b

ARTICLE_ID = "A01"
VOICE_NAME = p4b.VOICE_NAME
JAPANESE_STYLE_PREFIX = p4b.JAPANESE_STYLE_PREFIX
ENGLISH_STYLE_PREFIX = p4b.ENGLISH_STYLE_PREFIX
MAX_TTS_TECHNICAL_RETRY = p4b.MAX_TTS_TECHNICAL_RETRY
PATTERN_A_SOURCE_PATH = p4b.PATTERN_A_SOURCE_PATH

GAP_BEFORE_TARGET_SECONDS = p4b.GAP_BEFORE_TARGET_SECONDS  # 0.40
GAP_AFTER_TARGET_SECONDS = p4b.GAP_AFTER_TARGET_SECONDS    # 0.30
GAP_TOLERANCE_SECONDS = p4b.GAP_TOLERANCE_SECONDS          # 0.03
EN_TRIM_SAFETY_MARGIN_SECONDS = p4b.EN_TRIM_SAFETY_MARGIN_SECONDS  # 0.08
EXISTING_SHOT_ON_TARGET_PATH = p4b.EXISTING_SHOT_ON_TARGET_PATH

# 採用: 「目印」。不採用: 「合図」「キーワード挿入位置」「合図1/2…」
# 「キーワード挿入位置1/2…」・英語表現のカタカナ読み(指示section3)。
MARKER_TOKEN = "目印"

# sudachipy(MFAの日本語tokenizerが内部で使用)による実機トークン化を、
# 実際の5 marker chunkの文脈で個別に確認済み(「目印」は常に単一token)。
# 例: 「…道を閉ざすこと目印が現実になりそうな…」→ […, "こと", "目印",
# "が", …]。3語以上に分かれる既存markerとは異なり、単一token列。
MARKER_TOKEN_SEQUENCE = (MARKER_TOKEN,)

_LAST_FEW_MINUTES_PHRASE = p4b._LAST_FEW_MINUTES_PHRASE
_ASCII_LETTER_PATTERN = p4b._ASCII_LETTER_PATTERN

# ASRの表記揺れを許容する(指示section9の明記例)。この3表記のいずれかが
# 含まれていれば、marker相当の発話が存在すると診断する(合否の最終判断
# ではなく、MFAへ進む前の粗いフィルタに過ぎない)。
ALLOWED_MARKER_SPELLINGS = ("目印", "めじるし", "目じるし")

# 「文の大部分が欠落」「語順が大きく崩壊」を大づかみに検知するための
# 目安値。ASRの同音異義語程度の揺れでは十分高い値になり、逆に文の
# 大部分が欠落・語順崩壊するような重大な失敗では大きく下がることを、
# 実データで確認したうえでの選定(0.5=diffの過半が一致)。この値単独で
# 「自然さ」を判定するものではない(指示section9: MFAが正式な位置・
# 存在確認、ユーザー試聴が最終判断)。
CONTENT_SIMILARITY_THRESHOLD = 0.5


def build_tts_prompt(text: str, style_prefix: str) -> str:
    return style_prefix + text


def _reference_text_for_chunk(chunk: dict) -> str:
    """chunkのtts_text(marker語を含む、実際にTTSへ渡した文字列)を
    診断用の比較対象とする。marker_tokenをALLOWED_MARKER_SPELLINGSの
    代表表記(「目印」)のまま扱う(tts_text自体が既にその表記)。"""
    return chunk["tts_text"]


def check_chunk_content(recognized_text_ja: str, chunk: dict) -> dict:
    """P4Bのcheck_chunk_content(er003_v1_b1_p4b_generate.py)と同じ設計
    思想(句読点除去後に照合、無音長は使わない)だが、marker表記の完全
    一致を要求しない点が異なる(指示section9)。ASRは以下の診断にのみ
    使う: 日本語かどうか・意図しない英語混入がないか・大部分欠落や
    語順崩壊がないか・marker相当の発話が存在するか。markerの正式な
    位置・存在確認はMFA(別関数)で行う。"""
    stripped = p4._strip_punctuation(recognized_text_ja)
    ja_char_count = sum(
        1 for ch in recognized_text_ja
        if ("぀" <= ch <= "ゟ") or ("゠" <= ch <= "ヿ") or ("一" <= ch <= "鿿")
    )
    ja_char_ratio = ja_char_count / len(recognized_text_ja) if recognized_text_ja else 0.0
    is_japanese = ja_char_ratio >= 0.5

    ascii_letter_count = len(_ASCII_LETTER_PATTERN.findall(recognized_text_ja))
    no_unintended_english = ascii_letter_count == 0

    marker_spellings_found = [s for s in ALLOWED_MARKER_SPELLINGS if s in stripped]
    marker_plausible = len(marker_spellings_found) > 0

    reference_stripped = p4._strip_punctuation(_reference_text_for_chunk(chunk))
    similarity_ratio = difflib.SequenceMatcher(None, reference_stripped, stripped).ratio()
    similarity_ok = similarity_ratio >= CONTENT_SIMILARITY_THRESHOLD

    last_few_minutes_check = None
    if chunk["contains_last_few_minutes"]:
        last_few_minutes_check = {
            "expected_phrase": _LAST_FEW_MINUTES_PHRASE,
            "present_in_recognized": _LAST_FEW_MINUTES_PHRASE in stripped,
        }

    passed = (
        is_japanese and no_unintended_english and similarity_ok
        and (marker_plausible if chunk["chunk_type"] == "marker" else True)
        and (last_few_minutes_check is None or last_few_minutes_check["present_in_recognized"])
    )

    return {
        "recognized_text_ja_JP": recognized_text_ja,
        "ja_char_ratio": round(ja_char_ratio, 4),
        "is_japanese": is_japanese,
        "ascii_letter_count": ascii_letter_count,
        "no_unintended_english": no_unintended_english,
        "marker_spellings_found": marker_spellings_found,
        "marker_plausible": marker_plausible,
        "content_similarity_ratio": round(similarity_ratio, 4),
        "similarity_ok": similarity_ok,
        "last_few_minutes_check": last_few_minutes_check,
        "passed": passed,
    }
