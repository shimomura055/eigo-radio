# ============================================================
# er003_b1_p6b_audio.py
# ER-003-B1-P6B: 2-Macrochunk生成およびmarker境界改善検証
# ============================================================
# P6A(4chunk方式)はユーザー試聴で不合格となった。
#   1. shot on targetの挿入位置で助詞「を」が不自然に分断された
#   2. chunk01とchunk02の声質が異なり、接続が不自然だった
# 本ステージでは、(1) TTS call数を2回(Macrochunk A/B)へ減らして声質
# 不連続を抑えられるか、(2) marker置換の除去範囲をMFA区間そのものへ
# 一本化し、RMSベースのspeech boundsを除去範囲決定に使わないことで
# 隣接助詞の欠落を防げるか、の2点を分離して検証する。
#
# Stage1(日本語raw接続の自然さ)が合格した場合のみStage2(marker境界
# 改善による英語置換)へ進む(指示section2の明記通り)。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p6a_audio.build_chunk_plan(chunk_end_anchorsを渡して
#     2-Macrochunk用に再利用)/verify_chunk_plan_static/
#     check_kanji_target_phrases/JAPANESE_STYLE_PREFIX/VOICE_NAME/
#     MAX_TTS_TECHNICAL_RETRY/GAP_BEFORE_TARGET_SECONDS/
#     GAP_AFTER_TARGET_SECONDS/GAP_TOLERANCE_SECONDS/
#     EN_TRIM_SAFETY_MARGIN_SECONDS/EXISTING_SHOT_ON_TARGET_PATH/
#     MARKER_TOKEN/MARKER_TOKEN_SEQUENCE/JA_CHUNK_JOIN_PAUSE_SECONDS/
#     build_tts_prompt
#   - er003_b1_p4_audio.load_pattern_a_text/PATTERN_A_SOURCE_PATH/
#     find_all_marker_spans/spans_are_monotonic_non_overlapping/
#     get_full_text_via_azure_stt_continuous/_strip_punctuation
#   - er003_b1_p3z_audio.adjust_trailing_silence/adjust_leading_silence
#     (RMS検出結果ではなく、MFAのtoken境界をspeech_end/speech_start
#     として直接渡す。両関数ともspeech_end/speech_startを外部から
#     受け取る設計であり、値の出所(RMS/MFA)を関数自身は問わないため、
#     関数を変更せず呼び出し方だけを変える)
#   - er003_b1_p3w_audio.MFA_*/run_mfa_align/parse_textgrid_words_tier

from __future__ import annotations

import er003_b1_p4_audio as p4
import er003_b1_p6a_audio as p6a

ARTICLE_ID = "A01"
VOICE_NAME = p6a.VOICE_NAME
JAPANESE_STYLE_PREFIX = p6a.JAPANESE_STYLE_PREFIX
MAX_TTS_TECHNICAL_RETRY = p6a.MAX_TTS_TECHNICAL_RETRY
PATTERN_A_SOURCE_PATH = p6a.PATTERN_A_SOURCE_PATH
build_tts_prompt = p6a.build_tts_prompt

GAP_BEFORE_TARGET_SECONDS = p6a.GAP_BEFORE_TARGET_SECONDS
GAP_AFTER_TARGET_SECONDS = p6a.GAP_AFTER_TARGET_SECONDS
GAP_TOLERANCE_SECONDS = p6a.GAP_TOLERANCE_SECONDS
EN_TRIM_SAFETY_MARGIN_SECONDS = p6a.EN_TRIM_SAFETY_MARGIN_SECONDS
EXISTING_SHOT_ON_TARGET_PATH = p6a.EXISTING_SHOT_ON_TARGET_PATH

MARKER_TOKEN = p6a.MARKER_TOKEN
MARKER_TOKEN_SEQUENCE = p6a.MARKER_TOKEN_SEQUENCE
KANJI_TARGET_PHRASES = p6a.KANJI_TARGET_PHRASES
check_kanji_target_phrases = p6a.check_kanji_target_phrases

# 本編共通仕様の0.8秒(必須)。指示section6: 比較用の短い接続版は、新規
# TTS callなしで同じraw音声から作ってよい(最大2件まで)。
MACROCHUNK_JOIN_PAUSE_SECONDS = p6a.JA_CHUNK_JOIN_PAUSE_SECONDS  # 0.8
MACROCHUNK_JOIN_PAUSE_COMPARISON_CANDIDATES = (0.4, 0.6)

# Pattern A原文を2つのMacrochunkへ分割するアンカー(P6Aの4chunk用
# アンカーのうち、文2の終端のみを使う→文1+文2 / 文3+文4の2分割)。
MACROCHUNK_END_ANCHORS = ["を守ろうとします。"]


def build_macrochunk_plan(pattern_a_text: str, used_forms: list[dict]) -> list[dict]:
    """P6Aのbuild_chunk_planを2-Macrochunk用アンカーで呼び出すだけの
    薄いラッパー(分割ロジック自体は再実装しない)。"""
    return p6a.build_chunk_plan(pattern_a_text, used_forms, chunk_end_anchors=MACROCHUNK_END_ANCHORS)


def verify_macrochunk_plan_static(chunk_plan: list[dict], pattern_a_text: str) -> dict:
    return p6a.verify_chunk_plan_static(chunk_plan, pattern_a_text)


# ============================================================
# Stage2: MFA区間そのものを除去範囲とするmarker境界処理(新規)
# ============================================================
def verify_spans_no_overlap_with_adjacent_tokens(spans: list[dict]) -> dict:
    """MFA区間が、直前・直後token区間と重ならないことを機械確認する
    (指示section9: 「MFA区間に不確実性がある場合は、隣接する日本語
    tokenの区間と重ならないことを機械確認する」)。RMSは一切使わない。"""
    per_span_checks = []
    all_ok = True
    for span in spans:
        no_overlap_before = span["preceding_end_seconds"] <= span["start_seconds"]
        no_overlap_after = span["end_seconds"] <= span["following_start_seconds"]
        ok = no_overlap_before and no_overlap_after
        if not ok:
            all_ok = False
        per_span_checks.append({
            "marker_id": span["marker_id"],
            "preceding_token": span["preceding_token"], "preceding_end_seconds": span["preceding_end_seconds"],
            "marker_start_seconds": span["start_seconds"], "marker_end_seconds": span["end_seconds"],
            "following_token": span["following_token"], "following_start_seconds": span["following_start_seconds"],
            "no_overlap_before": no_overlap_before, "no_overlap_after": no_overlap_after, "ok": ok,
        })
    return {"per_span_checks": per_span_checks, "all_passed": all_ok}


def mfa_anchor_sample(seconds: float, segment_start_seconds: float, sr: int) -> int:
    """chunk絶対時刻(MFAが返す秒数)を、segment先頭を0とした相対サンプル
    番号へ変換する(RMSでの再検出は行わない)。"""
    return int(round((seconds - segment_start_seconds) * sr))
