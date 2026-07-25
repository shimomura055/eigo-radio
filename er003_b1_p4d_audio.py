# ============================================================
# er003_b1_p4d_audio.py
# ER-003-B1-P4D: 全文ひらがな読み正規化・日本語Preview検証
# ============================================================
# P4B/P4Cでは、`最後の数分`の誤読・`守備を固め`が`守備を固める`へ変化・
# 短文分割による声色の不連続などが確認された。本ステージは、特定語の
# 個別修正ではなく、承認済み日本語原稿全体を形態素解析(SudachiPy)の
# reading formに基づき機械的に全文ひらがなへ変換し、1回のTTS callで
# 音声化する方式を検証する(語句別の例外辞書・人手修正は一切使わない)。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p4_audio.load_pattern_a_text/PATTERN_A_SOURCE_PATH/
#     build_marker_map/get_full_text_via_azure_stt_continuous/
#     _strip_punctuation
#   - er003_b1_p4b_audio.JAPANESE_STYLE_PREFIX/VOICE_NAME/
#     MAX_TTS_TECHNICAL_RETRY/build_tts_prompt
#   - er003_b1_p3w_audio.MFA_MICROMAMBA_EXE/MFA_ENV_PREFIX(SudachiPyが
#     インストール済みの隔離環境を、tokenize専用サブプロセスとして再利用。
#     アプリ本体.venvにはsudachipyを追加しない)
#
# 新規に追加するのは、(1) 5 used formの「目印」への一括置換、(2) 隔離
# 環境でSudachiPyを実行するサブプロセス呼び出し、(3) reading formの
# カタカナ→ひらがな機械変換とreading map構築、(4) 変換後scriptの静的
# 検証、の4つのみ。

from __future__ import annotations

import difflib
import json
import os
import re
import subprocess

import er003_b1_p4_audio as p4
import er003_b1_p4b_audio as p4b
import er003_b1_p3w_audio as p3w

ARTICLE_ID = "A01"
VOICE_NAME = p4b.VOICE_NAME
JAPANESE_STYLE_PREFIX = p4b.JAPANESE_STYLE_PREFIX
MAX_TTS_TECHNICAL_RETRY = p4b.MAX_TTS_TECHNICAL_RETRY
PATTERN_A_SOURCE_PATH = p4b.PATTERN_A_SOURCE_PATH
build_tts_prompt = p4b.build_tts_prompt

MARKER_TOKEN = "目印"
MARKER_HIRAGANA = "めじるし"  # 目印のreading form(メジルシ)をひらがな化した期待値

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_SUDACHI_HELPER_SCRIPT = os.path.join(_REPO_ROOT, "er003_b1_p4d_sudachi_tokenize_helper.py")

_ASCII_LETTER_PATTERN = re.compile(r"[A-Za-z]")
_ARABIC_NUMERAL_PATTERN = re.compile(r"[0-9]")
_KANJI_PATTERN = re.compile(r"[一-鿿]")
# 変換対象の「カタカナ」は、実際に変換アルゴリズムがひらがな化する範囲
# (U+30A1〜U+30F6、標準的なカタカナ文字)に限定する。長音記号「ー」
# (U+30FC)はひらがな表記でも通常使われるため、残存チェックの対象外
# とする(例: 「わずかなりーど」は正しい変換結果であり不合格ではない)。
_KATAKANA_LETTER_PATTERN = re.compile(r"[ァ-ヶ]")

# SudachiPyが実際の読みを持たない記号類(句読点・ダッシュ・括弧等)に
# 割り当てる品詞大分類。この分類のtokenは、reading_form(「キゴウ」等、
# 実際の読みではない汎用ラベル)を使わず、surfaceをそのまま保持する
# (指示section6の「保持対象: 日本語の句読点・括弧」に対応する一般規則。
# 個々の記号ごとの例外ではなく、品詞分類による一括ルール)。
_SYMBOL_POS_MAJOR = "補助記号"


def sudachi_tokenize(text: str, work_dir: str) -> list[dict]:
    """隔離MFA環境(mfa_tool/envs/mfa、SudachiPy導入済み)でtokenizeを実行し、
    [{'surface','dictionary_form','reading_form','part_of_speech'}, ...]を
    返す。アプリ本体.venvにはsudachipyを追加しないため、既存のMFA隔離環境
    をmicromamba経由のサブプロセスとして再利用する(er003_b1_p3w_audio.
    run_mfa_alignと同じ隔離方式)。"""
    os.makedirs(work_dir, exist_ok=True)
    input_path = os.path.join(work_dir, "sudachi_input.txt")
    output_path = os.path.join(work_dir, "sudachi_output.json")
    with open(input_path, "w", encoding="utf-8") as f:
        f.write(text)

    cmd = [p3w.MFA_MICROMAMBA_EXE, "run", "-p", p3w.MFA_ENV_PREFIX, "python", _SUDACHI_HELPER_SCRIPT, input_path, output_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"SudachiPy tokenizeが失敗しました: {result.stderr}")

    with open(output_path, encoding="utf-8") as f:
        return json.load(f)


def build_marker_replaced_source(pattern_a_text: str, used_forms: list[dict]) -> dict:
    """5つの英語used formを、出現順に「目印」へ置換する(指示section5)。
    承認済み原稿の語句・順序・句読点はmarker置換以外一切変更しない。"""
    marker_map = p4.build_marker_map(pattern_a_text, used_forms)

    marked_text = pattern_a_text
    for e in marker_map:
        used_form = e["used_form"]
        if marked_text.count(used_form) != 1:
            raise ValueError(f"used_form{used_form!r}の出現数が1ではありません")
        marked_text = marked_text.replace(used_form, MARKER_TOKEN, 1)

    used_form_residue = {e["used_form"]: marked_text.count(e["used_form"]) for e in marker_map}
    marker_count = marked_text.count(MARKER_TOKEN)

    return {
        "marked_text": marked_text,
        "marker_map": marker_map,
        "used_form_residue_all_zero": all(v == 0 for v in used_form_residue.values()),
        "used_form_residue": used_form_residue,
        "marker_count": marker_count,
        "marker_count_is_five": marker_count == 5,
    }


def katakana_to_hiragana(s: str) -> str:
    """カタカナ文字(U+30A1〜U+30F6)だけを対応するひらがなへ機械変換する
    (Unicodeオフセット-0x60)。長音記号「ー」・中黒「・」等、この範囲外の
    文字はそのまま保持する。"""
    return "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in s)


def build_reading_map(morphemes: list[dict], marker_token: str = MARKER_TOKEN) -> list[dict]:
    """tokenごとに、記号類(補助記号)はsurfaceをそのまま、それ以外は
    reading_form(カタカナ)をひらがな化したものをhiragana_formとして
    記録する。個々の単語ごとの例外辞書は使わない(品詞分類による
    一般規則のみ)。"""
    reading_map = []
    pos = 0
    for m in morphemes:
        surface = m["surface"]
        reading_form = m["reading_form"]
        is_symbol = m["part_of_speech"][0] == _SYMBOL_POS_MAJOR

        if is_symbol:
            hiragana_form = surface
        else:
            hiragana_form = katakana_to_hiragana(reading_form) if reading_form else None

        reading_map.append({
            "surface": surface,
            "dictionary_form": m["dictionary_form"],
            "reading_form": reading_form,
            "hiragana_form": hiragana_form,
            "part_of_speech": m["part_of_speech"],
            "source_position": pos,
            "is_marker": surface == marker_token,
            "is_symbol": is_symbol,
        })
        pos += len(surface)

    return reading_map


def build_full_hiragana_script(reading_map: list[dict]) -> str:
    """token間に新しい空白を挿入せず、hiragana_formをそのまま連結する。"""
    return "".join(e["hiragana_form"] or "" for e in reading_map)


_LAST_FEW_MINUTES_EXPECTED = "さいごのすうふん"
_DEFEND_EXPECTED = "しゅびをかため"
_DEFEND_FORBIDDEN = "しゅびをかためる"
_NARROW_LEAD_EXPECTED = "わずかなりーど"


def verify_reading_conversion(marked_text: str, reading_map: list[dict], hiragana_script: str) -> dict:
    """TTS呼び出し前の静的検証(指示section8)。1つでも不合格ならTTSを
    呼ばず停止する。"""
    reconstructed_surfaces = "".join(e["surface"] for e in reading_map)
    reconstruction_matches = reconstructed_surfaces == marked_text

    unconvertible_tokens = [
        {"surface": e["surface"], "reading_form": e["reading_form"], "part_of_speech": e["part_of_speech"]}
        for e in reading_map if not e["is_symbol"] and not e["hiragana_form"]
    ]

    ascii_letter_count = len(_ASCII_LETTER_PATTERN.findall(hiragana_script))
    arabic_numeral_count = len(_ARABIC_NUMERAL_PATTERN.findall(hiragana_script))
    kanji_count = len(_KANJI_PATTERN.findall(hiragana_script))
    katakana_letter_count = len(_KATAKANA_LETTER_PATTERN.findall(hiragana_script))

    marker_hiragana_count = hiragana_script.count(MARKER_HIRAGANA)

    source_sentence_count = marked_text.count("。")
    script_sentence_count = hiragana_script.count("。")

    source_punctuation_sequence = [ch for ch in marked_text if ch in "、。―"]
    script_punctuation_sequence = [ch for ch in hiragana_script if ch in "、。―"]

    checks = {
        "reconstruction_matches": reconstruction_matches,
        "unconvertible_tokens": unconvertible_tokens,
        "unconvertible_token_count_is_zero": len(unconvertible_tokens) == 0,
        "ascii_letter_count": ascii_letter_count,
        "ascii_letter_count_is_zero": ascii_letter_count == 0,
        "arabic_numeral_count": arabic_numeral_count,
        "arabic_numeral_count_is_zero": arabic_numeral_count == 0,
        "kanji_count": kanji_count,
        "kanji_count_is_zero": kanji_count == 0,
        "katakana_letter_count": katakana_letter_count,
        "katakana_letter_count_is_zero": katakana_letter_count == 0,
        "marker_hiragana_count": marker_hiragana_count,
        "marker_hiragana_count_is_five": marker_hiragana_count == 5,
        "source_sentence_count": source_sentence_count,
        "script_sentence_count": script_sentence_count,
        "sentence_count_matches": source_sentence_count == script_sentence_count,
        "punctuation_sequence_matches": source_punctuation_sequence == script_punctuation_sequence,
    }

    all_passed = (
        checks["reconstruction_matches"] and checks["unconvertible_token_count_is_zero"]
        and checks["ascii_letter_count_is_zero"] and checks["arabic_numeral_count_is_zero"]
        and checks["kanji_count_is_zero"] and checks["katakana_letter_count_is_zero"]
        and checks["marker_hiragana_count_is_five"] and checks["sentence_count_matches"]
        and checks["punctuation_sequence_matches"]
    )
    checks["all_passed"] = all_passed
    return checks


_ALLOWED_MARKER_SPELLINGS = (MARKER_TOKEN, MARKER_HIRAGANA, "目じるし")
_CONTENT_SIMILARITY_THRESHOLD = 0.5


def check_full_text_content(recognized_text_ja: str, marked_text: str) -> dict:
    """生成直後の全文ASR診断(指示section11)。境界決定・合否には使わず、
    日本語かどうか・意図しない英語混入・大幅な欠落や語順崩壊がないか・
    marker相当の発話が5回あるかを確認する。ASR出力(カタカナ・漢字表記)
    はhiragana化前のmarked_text(marker置換後・変換前)と比較する
    (全文ひらがな台本と比較すると、表記が違うだけで一致率が不当に
    下がるため)。"""
    stripped = p4._strip_punctuation(recognized_text_ja)
    ja_char_count = sum(
        1 for ch in recognized_text_ja
        if ("぀" <= ch <= "ゟ") or ("゠" <= ch <= "ヿ") or ("一" <= ch <= "鿿")
    )
    ja_char_ratio = ja_char_count / len(recognized_text_ja) if recognized_text_ja else 0.0
    is_japanese = ja_char_ratio >= 0.5

    ascii_letter_count = len(_ASCII_LETTER_PATTERN.findall(recognized_text_ja))
    no_unintended_english = ascii_letter_count == 0

    marker_occurrences_by_spelling = {s: stripped.count(s) for s in _ALLOWED_MARKER_SPELLINGS}
    marker_occurrence_total = sum(marker_occurrences_by_spelling.values())

    reference_stripped = p4._strip_punctuation(marked_text)
    similarity_ratio = difflib.SequenceMatcher(None, reference_stripped, stripped).ratio()
    similarity_ok = similarity_ratio >= _CONTENT_SIMILARITY_THRESHOLD

    return {
        "recognized_text_ja_JP": recognized_text_ja,
        "ja_char_ratio": round(ja_char_ratio, 4),
        "is_japanese": is_japanese,
        "ascii_letter_count": ascii_letter_count,
        "no_unintended_english": no_unintended_english,
        "marker_occurrences_by_spelling": marker_occurrences_by_spelling,
        "marker_occurrence_total": marker_occurrence_total,
        "marker_occurrence_total_is_five": marker_occurrence_total == 5,
        "content_similarity_ratio": round(similarity_ratio, 4),
        "similarity_ok": similarity_ok,
    }


def check_key_expressions(hiragana_script: str) -> dict:
    """重点表現の変換結果を確認する(指示section8/12/18)。個別の読み
    修正ではなく、全文変換アルゴリズムの結果を事後的に検証するだけ。"""
    return {
        "last_few_minutes": {
            "expected": _LAST_FEW_MINUTES_EXPECTED,
            "present": _LAST_FEW_MINUTES_EXPECTED in hiragana_script,
        },
        "defend": {
            "expected": _DEFEND_EXPECTED,
            "present": _DEFEND_EXPECTED in hiragana_script,
            "forbidden_form_present": _DEFEND_FORBIDDEN in hiragana_script,
        },
        "narrow_lead": {
            "expected": _NARROW_LEAD_EXPECTED,
            "present": _NARROW_LEAD_EXPECTED in hiragana_script,
        },
    }
