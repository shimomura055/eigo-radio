# ============================================================
# er003_b1_p4b_audio.py
# ER-003-B1-P4B: 短文分割＋単一「合図」マーカーでListening Preview完成版
# ============================================================
# P4Aで、Preview全文を1回のTTS callで生成したところ、マーカー以外の
# 日本語(「最後の数分」)が崩れて聞こえる問題が生じた。本ステージでは
# Preview全文の一括生成をやめ、短い日本語chunk(原則1文)へ分割して
# 個別に生成する。Key Phraseを含むchunkでは、英語used formだけを
# 汎用の一時マーカー「合図」(番号なし、各marker chunkに1件だけ)へ
# 置換する。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p4_audio.load_pattern_a_text/JAPANESE_STYLE_PREFIX/
#     ENGLISH_STYLE_PREFIX/VOICE_NAME/MAX_TTS_TECHNICAL_RETRY/
#     PATTERN_A_SOURCE_PATH/build_tts_prompt/check_ja_content/
#     get_full_text_via_azure_stt_continuous/find_all_marker_spans/
#     spans_are_monotonic_non_overlapping/GAP_BEFORE_TARGET_SECONDS/
#     GAP_AFTER_TARGET_SECONDS/GAP_TOLERANCE_SECONDS/
#     EN_TRIM_SAFETY_MARGIN_SECONDS/EXISTING_SHOT_ON_TARGET_PATH
#   - er003_b1_p3u_audio.find_speech_bounds/trim_english_keyword_silence
#   - er003_b1_p3w_audio.MFA_*/run_mfa_align/parse_textgrid_words_tier
#   - er003_b1_p3z_audio.adjust_trailing_silence/adjust_leading_silence
#
# 新規に追加するのは、(1) Pattern Aを6つの短文chunkへ分割する
# build_chunk_plan(既存の分割ロジックがないため)、(2) 単一マーカー
# 「合図」への置換ロジック、の2つのみ。MFA・無音調整・診断ASR等は
# 全て既存実装を再利用する。

from __future__ import annotations

import re

import er003_b1_p4_audio as p4

ARTICLE_ID = "A01"
VOICE_NAME = p4.VOICE_NAME
JAPANESE_STYLE_PREFIX = p4.JAPANESE_STYLE_PREFIX
ENGLISH_STYLE_PREFIX = p4.ENGLISH_STYLE_PREFIX
MAX_TTS_TECHNICAL_RETRY = p4.MAX_TTS_TECHNICAL_RETRY
PATTERN_A_SOURCE_PATH = p4.PATTERN_A_SOURCE_PATH

GAP_BEFORE_TARGET_SECONDS = p4.GAP_BEFORE_TARGET_SECONDS  # 0.40
GAP_AFTER_TARGET_SECONDS = p4.GAP_AFTER_TARGET_SECONDS    # 0.30
GAP_TOLERANCE_SECONDS = p4.GAP_TOLERANCE_SECONDS          # 0.03
EN_TRIM_SAFETY_MARGIN_SECONDS = p4.EN_TRIM_SAFETY_MARGIN_SECONDS  # 0.08
EXISTING_SHOT_ON_TARGET_PATH = p4.EXISTING_SHOT_ON_TARGET_PATH

MARKER_TOKEN = "合図"
MARKER_TOKEN_SEQUENCE = (MARKER_TOKEN,)

_ASCII_LETTER_PATTERN = re.compile(r"[A-Za-z]")

_LAST_FEW_MINUTES_PHRASE = "最後の数分"

# Pattern A本文を6chunkへ分割するための、各chunk終端の目印文字列
# (既存の句読点位置での分割のみ。文字の追加・削除は行わない)。
_CHUNK_END_ANCHORS = [
    "静かな均衡が保たれます。",
    "守備を固め、",
    "を守ろうとします。",
    "その時、",
    "stoppage timeへ。",
]


def build_chunk_plan(pattern_a_text: str, used_forms: list[dict], marker_token: str = MARKER_TOKEN) -> list[dict]:
    """Pattern A本文を、既存の句読点位置で6つのchunkへ分割する。
    語句・順序・句読点は一切変更しない(既存アンカー文字列での単純な
    スライスのみ)。各chunkについて、含まれるused_form(0または1件)を
    特定し、marker chunkの場合はTTS用テキスト(used_formをmarker_token
    へ置換したもの)を構築する。marker_tokenを省略した場合は、この
    ステージ(P4B)のデフォルト「合図」を使う(後続ステージが別の
    marker語で同じ分割ロジックを再利用できるようにするための引数)。"""
    pos = 0
    raw_chunks = []
    for anchor in _CHUNK_END_ANCHORS:
        idx = pattern_a_text.index(anchor, pos)
        end = idx + len(anchor)
        raw_chunks.append(pattern_a_text[pos:end])
        pos = end
    raw_chunks.append(pattern_a_text[pos:])

    reconstructed = "".join(raw_chunks)
    if reconstructed != pattern_a_text:
        raise ValueError("chunk分割の復元がPattern A原文と一致しません")

    used_form_by_text = {uf["used_form"]: uf for uf in used_forms}

    plan = []
    for i, source_text in enumerate(raw_chunks, start=1):
        matched = [uf for uf_text, uf in used_form_by_text.items() if uf_text in source_text]
        if len(matched) > 1:
            raise ValueError(f"chunk{i}に複数のused formが含まれています(分割不足): {[m['used_form'] for m in matched]}")

        contains_last_few_minutes = _LAST_FEW_MINUTES_PHRASE in source_text

        if matched:
            uf = matched[0]
            if source_text.count(uf["used_form"]) != 1:
                raise ValueError(f"chunk{i}内でused_form{uf['used_form']!r}の出現数が1ではありません")
            tts_text = source_text.replace(uf["used_form"], marker_token, 1)
            plan.append({
                "chunk_id": f"{i:02d}",
                "chunk_type": "marker",
                "source_text": source_text,
                "tts_text": tts_text,
                "canonical_english": uf["canonical_english"],
                "used_form": uf["used_form"],
                "marker_count_in_tts_text": tts_text.count(marker_token),
                "order": i,
                "contains_last_few_minutes": contains_last_few_minutes,
            })
        else:
            plan.append({
                "chunk_id": f"{i:02d}",
                "chunk_type": "normal",
                "source_text": source_text,
                "tts_text": source_text,
                "canonical_english": None,
                "used_form": None,
                "marker_count_in_tts_text": source_text.count(marker_token),
                "order": i,
                "contains_last_few_minutes": contains_last_few_minutes,
            })

    return plan


def verify_chunk_plan_static(chunk_plan: list[dict], pattern_a_text: str, marker_token: str = MARKER_TOKEN) -> dict:
    """TTS呼び出し前の静的検証(section7)。1つでも満たさない場合は
    呼び出し側でTTSを呼ばず停止する。marker_tokenを省略した場合は、
    このステージ(P4B)のデフォルト「合図」を使う。"""
    reconstructed_source = "".join(c["source_text"] for c in chunk_plan)
    reconstruction_matches = reconstructed_source == pattern_a_text

    marker_chunks = [c for c in chunk_plan if c["chunk_type"] == "marker"]
    normal_chunks = [c for c in chunk_plan if c["chunk_type"] == "normal"]

    per_chunk_checks = []
    all_ok = True
    for c in chunk_plan:
        ascii_count = len(_ASCII_LETTER_PATTERN.findall(c["tts_text"]))
        if c["chunk_type"] == "marker":
            used_form_in_source_count = c["source_text"].count(c["used_form"])
            used_form_in_tts_count = c["tts_text"].count(c["used_form"])
            marker_count = c["tts_text"].count(marker_token)
            ok = (used_form_in_source_count == 1 and used_form_in_tts_count == 0
                  and marker_count == 1 and ascii_count == 0)
        else:
            used_form_in_source_count = None
            used_form_in_tts_count = None
            marker_count = c["tts_text"].count(marker_token)
            ok = (marker_count == 0 and ascii_count == 0)
        if not ok:
            all_ok = False
        per_chunk_checks.append({
            "chunk_id": c["chunk_id"], "chunk_type": c["chunk_type"],
            "used_form_in_source_count": used_form_in_source_count,
            "used_form_in_tts_count": used_form_in_tts_count,
            "marker_count": marker_count, "ascii_letter_count": ascii_count, "ok": ok,
        })

    marker_chunk_count_is_five = len(marker_chunks) == 5
    total_marker_count = sum(c["tts_text"].count(marker_token) for c in marker_chunks)
    total_marker_count_is_five = total_marker_count == 5

    all_used_forms = [c["used_form"] for c in marker_chunks]
    used_form_residue_in_any_tts_text = {
        uf: sum(c["tts_text"].count(uf) for c in chunk_plan) for uf in all_used_forms
    }
    all_used_forms_absent_in_tts = all(v == 0 for v in used_form_residue_in_any_tts_text.values())

    all_passed = (
        reconstruction_matches and all_ok and marker_chunk_count_is_five
        and total_marker_count_is_five and all_used_forms_absent_in_tts
    )

    return {
        "reconstruction_matches": reconstruction_matches,
        "per_chunk_checks": per_chunk_checks,
        "marker_chunk_count": len(marker_chunks),
        "normal_chunk_count": len(normal_chunks),
        "marker_chunk_count_is_five": marker_chunk_count_is_five,
        "total_marker_count": total_marker_count,
        "total_marker_count_is_five": total_marker_count_is_five,
        "used_form_residue_in_any_tts_text": used_form_residue_in_any_tts_text,
        "all_used_forms_absent_in_tts": all_used_forms_absent_in_tts,
        "all_passed": all_passed,
    }


def build_tts_prompt(text: str, style_prefix: str) -> str:
    return style_prefix + text
