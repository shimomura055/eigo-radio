# ============================================================
# er003_b1_p4a_audio.py
# ER-003-B1-P4A: Preview TTS入力監査と5マーカー再生成
# ============================================================
# P4で生成したListening Preview音声のうち、`close the door to`の
# used form(`close the door to the final`)に対応する箇所だけが英語で
# 発話された。本ステージでは、まずP4で実際にTTSへ渡した入力原稿を
# 静的に確認し、Case A(used formの置換漏れ)かCase B(カタカナへの
# 置換は正しく行われていたがTTSが英語で発話した)かを機械的に確定する。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p4_audio.load_pattern_a_text/build_tts_script_with_markers/
#     check_ja_content/get_full_text_via_azure_stt_continuous/
#     JAPANESE_STYLE_PREFIX/VOICE_NAME/MAX_TTS_TECHNICAL_RETRY/
#     PATTERN_A_SOURCE_PATH

from __future__ import annotations

import re

import er003_b1_p4_audio as p4

ARTICLE_ID = "A01"
VOICE_NAME = p4.VOICE_NAME
JAPANESE_STYLE_PREFIX = p4.JAPANESE_STYLE_PREFIX
MAX_TTS_TECHNICAL_RETRY = p4.MAX_TTS_TECHNICAL_RETRY

PATTERN_A_SOURCE_PATH = p4.PATTERN_A_SOURCE_PATH
P4_TTS_INPUT_PATH = "er003_output/b1_p4/A01/source/pattern_a_tts_with_katakana_markers.txt"

# P4で英語発話が確認された箇所のみ、日本語のみで構成された固有マーカー
# へ変更する(Case B対応)。他の4件は、P4で正常に日本語発話されたことを
# 確認済みのカタカナのまま維持する。
_FIXED_MARKER_OVERRIDE_BY_USED_FORM = {
    "close the door to the final": "第四の合図",
}

_USED_FORMS = ["shot on target", "take players off", "a narrow lead",
               "close the door to the final", "stoppage time"]

_ASCII_LETTER_PATTERN = re.compile(r"[A-Za-z]")


def audit_tts_input(text: str, used_forms: list, marker_map: list) -> dict:
    """P4で実際にTTSへ渡した入力原稿に対する静的監査。新しいTTS呼び出し
    は一切行わない。"""
    used_form_counts = {uf: text.count(uf) for uf in used_forms}
    marker_counts = {e["katakana_marker"]: text.count(e["katakana_marker"]) for e in marker_map}
    ascii_matches = _ASCII_LETTER_PATTERN.findall(text)

    all_used_forms_absent = all(c == 0 for c in used_form_counts.values())
    all_markers_present_once = all(c == 1 for c in marker_counts.values())
    no_ascii_letters = len(ascii_matches) == 0
    marker_total = len(marker_map)

    if all_used_forms_absent and all_markers_present_once and no_ascii_letters and marker_total == 5:
        case = "B"
        case_reason = (
            "TTS入力原稿に英語used formの残存はなく、5マーカーは全てカタカナで"
            "1回ずつ正しく置換済み。ASCII英字の残存も0。よって、入力原稿自体は"
            "正しく、TTSモデル自身が該当マーカーを英語で発話したと判定する。"
        )
    elif not all_used_forms_absent or not no_ascii_letters:
        case = "A"
        case_reason = "TTS入力原稿に英語used form、またはASCII英字が残存しており、置換処理に不一致がある。"
    else:
        case = "UNCLASSIFIED"
        case_reason = "used form残存・ASCII残存は0だが、マーカー出現数または総数の条件を満たさない(欠落・重複の可能性)。"

    return {
        "used_form_counts": used_form_counts,
        "marker_counts": marker_counts,
        "ascii_letters_found": ascii_matches,
        "ascii_letter_count": len(ascii_matches),
        "all_used_forms_absent": all_used_forms_absent,
        "all_markers_present_once": all_markers_present_once,
        "no_ascii_letters": no_ascii_letters,
        "marker_total": marker_total,
        "case": case,
        "case_reason": case_reason,
    }


def build_marker_map_fixed(pattern_a_text: str, used_forms: list) -> list:
    """p4.build_marker_mapと同じ構築ロジックだが、_FIXED_MARKER_OVERRIDE_
    BY_USED_FORMに該当するused formだけカタカナを日本語固有表現へ差し替える。"""
    base_map = p4.build_marker_map(pattern_a_text, used_forms)
    for e in base_map:
        override = _FIXED_MARKER_OVERRIDE_BY_USED_FORM.get(e["used_form"])
        if override is not None:
            e["katakana_marker"] = override
            e["marker_type"] = "japanese_unique_phrase"
        else:
            e["marker_type"] = "katakana"
    return base_map


def build_tts_script_with_markers_fixed(pattern_a_text: str, marker_map: list) -> str:
    return p4.build_tts_script_with_markers(pattern_a_text, marker_map)


def build_tts_prompt(text: str, style_prefix: str = None) -> str:
    if style_prefix is None:
        style_prefix = JAPANESE_STYLE_PREFIX
    return style_prefix + text


def verify_pre_call_checks(script: str, marker_map: list, pattern_a_text: str) -> dict:
    """API call前に必ず通す確定チェック(section7)。1つでも満たさない
    場合はcaller側でTTSを呼ばず停止する。"""
    used_form_counts = {e["used_form"]: script.count(e["used_form"]) for e in marker_map}
    marker_counts = {e["katakana_marker"]: script.count(e["katakana_marker"]) for e in marker_map}
    ascii_matches = _ASCII_LETTER_PATTERN.findall(script)

    # Pattern Aの日本語部分の変更0(マーカーを元のused formへ戻すと完全一致することで確認)
    reconstructed = script
    for e in marker_map:
        reconstructed = reconstructed.replace(e["katakana_marker"], e["used_form"], 1)
    japanese_part_unchanged = reconstructed == pattern_a_text

    checks = {
        "used_form_counts_all_zero": all(c == 0 for c in used_form_counts.values()),
        "marker_counts_all_one": all(c == 1 for c in marker_counts.values()),
        "marker_total_is_five": len(marker_map) == 5,
        "ascii_letter_count_zero": len(ascii_matches) == 0,
        "japanese_part_unchanged": japanese_part_unchanged,
    }
    checks["all_passed"] = all(checks.values())
    checks["used_form_counts"] = used_form_counts
    checks["marker_counts"] = marker_counts
    checks["ascii_letters_found"] = ascii_matches
    return checks
