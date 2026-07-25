# ============================================================
# er003_b1_p3y_audio.py
# ER-003-B1-P3Y: 日本語用instruction＋カタカナマーカー置換検証
# ============================================================
# ER-003-B1-P3Xで、マーカー入り日本語原稿へ既存(英語記事読み上げ用)の
# TTS instructionをそのまま使うと、Gemini TTSが英語音声を返すことを
# 確認した。本ステージでは、instructionの「言語指定」1行だけを日本語
# 読み上げ用の文言へ差し替え、それ以外(演技指示・POINT_LABEL_FIDELITY
# ・Voice/Level等)は一切変更しない。また、意味的にTTSへの指示のように
# 読めてしまう恐れのあった一時マーカー「キーワード挿入位置」をやめ、
# 文脈上自然なカタカナ語「ショット・オン・ターゲット」を一時マーカーと
# して使う。
#
# 再利用するもの(再実装しない):
#   - er002_common.COMMON_BASE_INSTRUCTION/LEVEL2_INSTRUCTION/
#     POINT_LABEL_FIDELITY_RULE(言語指定1行以外は無変更のまま再利用)
#   - er002_common.SAMPLE_RATE/read_wav_float/write_wav_float/
#     pcm_bytes_to_float_mono/measure_metrics/apply_dynamics3_once/
#     _call_tts_with_retry/MODEL_NAME
#   - er002_gemini_client.make_tts_call_fn(voice_name)
#   - er003_b1_p3r_audio.VOICE_NAME
#   - er003_b1_p3t_audio.SOURCE_INTEGRATED_SENTENCE/
#     SOURCE_JAPANESE_FULL_SENTENCE/SOURCE_ENGLISH_KEYWORD
#   - er003_b1_p3u_audio.BOUNDARY_PAUSE_SECONDS(0.12秒)/
#     join_with_boundary_pauses
#   - er003_b1_p3w_audio.MFA_*(隔離環境設定)/mfa_environment_available/
#     run_mfa_align/parse_textgrid_words_tier/find_marker_span/
#     remove_marker_span/EXISTING_EN_TRIMMED_PATH
#     (find_marker_spanはmarker_tokensを引数化済みのため、カタカナ
#     マーカーにもそのまま使える。再実装しない)

from __future__ import annotations

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p3t_audio as p3t
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w

ARTICLE_ID = "A01"
VOICE_NAME = p3r.VOICE_NAME  # "Aoede"(既存採用済み仕様と同一)

SOURCE_INTEGRATED_SENTENCE = p3t.SOURCE_INTEGRATED_SENTENCE
SOURCE_JAPANESE_FULL_SENTENCE = p3t.SOURCE_JAPANESE_FULL_SENTENCE
SOURCE_ENGLISH_KEYWORD = p3t.SOURCE_ENGLISH_KEYWORD  # "shot on target"

# 承認済み原稿の語句・意味は変更しない。挿入位置を作るための一時的な
# カタカナマーカーのみを追加する(編集用であり完成音声には残さない)。
KATAKANA_MARKER = "ショット・オン・ターゲット"
_INSERTION_MARKER = "枠内シュートを記録できないまま"
_INSERTION_REPLACEMENT = f"枠内シュート、{KATAKANA_MARKER}を記録できないまま"

# MFAの日本語tokenizerは、KATAKANA_MARKERを「・」区切りで3つの実在語へ
# 分割して認識する(実機確認済み: "ショット"/"オン"/"ターゲット")。
MARKER_TOKEN_SEQUENCE = ("ショット", "オン", "ターゲット")

# 既存のtrim済み英語音声を再利用する(再TTS生成しない)。P3Wと同一。
EXISTING_EN_TRIMMED_PATH = p3w.EXISTING_EN_TRIMMED_PATH

BOUNDARY_PAUSE_SECONDS = p3u.BOUNDARY_PAUSE_SECONDS  # 0.12秒(P3U/P3Wと同一)
MAX_TTS_TECHNICAL_RETRY = 1

# ------------------------------------------------------------
# instruction: 言語指定1行だけを日本語読み上げ用へ差し替える
# ------------------------------------------------------------
_ORIGINAL_LANGUAGE_LINE = "TTS the following complete story in natural, engaging English."
_JAPANESE_LANGUAGE_LINE = "次の文章を、翻訳・言い換えせず、日本語のまま読み上げてください。"


def build_japanese_style_prefix() -> str:
    """採用済みの共通instruction(er002_common.COMMON_BASE_INSTRUCTION+
    LEVEL2_INSTRUCTION+POINT_LABEL_FIDELITY_RULE)のうち、言語指定の
    先頭1行だけを日本語読み上げ用の文言へ差し替える。それ以外の行は
    一切変更しない(LEVEL2_INSTRUCTION/POINT_LABEL_FIDELITY_RULEは
    無変更のまま再利用)。"""
    base = common.COMMON_BASE_INSTRUCTION
    if not base.startswith(_ORIGINAL_LANGUAGE_LINE):
        raise ValueError("COMMON_BASE_INSTRUCTIONの先頭行が想定と異なります(言語指定行の置換対象を特定できません)")
    ja_base = _JAPANESE_LANGUAGE_LINE + base[len(_ORIGINAL_LANGUAGE_LINE):]
    prefix = ja_base + common.LEVEL2_INSTRUCTION + common.POINT_LABEL_FIDELITY_RULE
    common.assert_no_wpm_specification(prefix)
    common.assert_no_genre_leakage(prefix)
    return prefix


def build_instruction_diff() -> dict:
    """変更前(英語用)instructionと変更後(日本語用)instructionの行単位
    diffを返す。言語指定1行以外に差分がないことの検証に使う。"""
    before = common.build_style_prefix()
    after = build_japanese_style_prefix()
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    diff_lines = [
        {"line_index": i, "before": b, "after": a}
        for i, (b, a) in enumerate(zip(before_lines, after_lines))
        if b != a
    ]
    return {
        "before": before,
        "after": after,
        "before_line_count": len(before_lines),
        "after_line_count": len(after_lines),
        "line_count_equal": len(before_lines) == len(after_lines),
        "changed_line_indices": [d["line_index"] for d in diff_lines],
        "changed_lines": diff_lines,
        "only_one_line_changed": len(diff_lines) == 1,
    }


def build_tts_prompt(text: str, style_prefix: str = None) -> str:
    if style_prefix is None:
        style_prefix = build_japanese_style_prefix()
    return style_prefix + text


def build_tts_katakana_marker_script(source_japanese_full_sentence: str = SOURCE_JAPANESE_FULL_SENTENCE) -> str:
    """承認済み日本語原稿の英語Key Phrase挿入位置へ、カタカナの一時
    マーカー(KATAKANA_MARKER)を追加する。語彙・語順・助詞は一切変更
    せず、挿入位置(「枠内シュート」と「を記録できないまま」の間)へ
    マーカーのみを追加する。"""
    if _INSERTION_MARKER not in source_japanese_full_sentence:
        raise ValueError("挿入位置のマーカーが日本語通し原稿内に見つかりません")
    return source_japanese_full_sentence.replace(_INSERTION_MARKER, _INSERTION_REPLACEMENT, 1)
