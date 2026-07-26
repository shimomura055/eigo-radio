# ============================================================
# er003_b1_p5c_audio.py
# ER-003-B1-P5C: GCP漢字かな交じり入力検証
# ============================================================
# P5B-GCPでは、全文ひらがな入力を使ったGoogle Cloud TTS(ja-JP-Neural2-B)
# の音声が、ユーザー試聴で「極めて機械的」「何が→なんが」と不合格に
# なった。本ステージでは、同一エンジン・同一voice・同一生成条件のまま、
# 入力表記だけを「英語used form5件を目印へ置換した直後の漢字かな交じり
# 原稿」(P4Dが実際に保存済みのpattern_a_with_markers.txt、全文ひらがな
# 化する一つ前の段階)へ変更し、不自然さの原因が入力方式(全文ひらがな
# 正規化)にあったのかを切り分ける。新しいTTSエンジンは追加しない。
#
# 再利用するもの(再実装しない):
#   - er003_b1_p4_audio.load_pattern_a_text/PATTERN_A_SOURCE_PATH/
#     build_marker_map/get_full_text_via_azure_stt_continuous
#   - er003_b1_p4d_audio._KANJI_PATTERN
#   - er003_b1_p5a_audio.MAX_TTS_TECHNICAL_RETRY
#   - er003_b1_p5b_audio.make_google_tts_call_fn/
#     check_google_cloud_tts_availability/GOOGLE_VOICE_NAME/
#     GOOGLE_LANGUAGE_CODE(P5B-GCPと完全同一の実装・voice・生成条件を
#     再利用し、入力表記だけを変える)

from __future__ import annotations

import hashlib
import json

import er003_b1_p4_audio as p4
import er003_b1_p4d_audio as p4d
import er003_b1_p5a_audio as p5a
import er003_b1_p5b_audio as p5b

ARTICLE_ID = "A01"

# P4Dが実際に保存済みの「英語used form5件を目印へ置換した直後」の
# 漢字かな交じり原稿(全文ひらがな化する一つ前の段階)。新規に作り直さず
# そのまま再利用する。
P4D_MARKED_TEXT_PATH = "er003_output/b1_p4d/A01/source/pattern_a_with_markers.txt"
# P4D完了時にreading_audit.md/source_hashes.jsonへ記録済みの値。
P4D_MARKED_TEXT_EXPECTED_SHA256 = "a28f3cf892fce482d27b5c512be1a260ca305c286c7f6625fd68aff9a4193cd8"

GOOGLE_VOICE_NAME = p5b.GOOGLE_VOICE_NAME
GOOGLE_LANGUAGE_CODE = p5b.GOOGLE_LANGUAGE_CODE
MAX_TTS_TECHNICAL_RETRY = p5a.MAX_TTS_TECHNICAL_RETRY

MARKER_TOKEN = "目印"

# 指示section7で明示された対象句(漢字かな交じり表記のまま、読み正規化
# しない)。P4D/P5A/P5Bのひらがな対象句とは別物。
KANJI_TARGET_PHRASES = (
    "何が起きる",
    "選手を交代で下げる",
    "目印という決断で",
    "守備を固め",
    "最後の数分",
    "わずかなリード",
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_marked_text_input(
    path: str = P4D_MARKED_TEXT_PATH,
    expected_sha256: str = P4D_MARKED_TEXT_EXPECTED_SHA256,
) -> dict:
    """P4Dが保存済みの、目印置換直後・ひらがな化前の原稿を変更せず
    読み込む。記録済みsha256と不一致なら例外を送出する(改変検知)。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    actual_sha256 = _sha256_text(text)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"入力ファイルのsha256が記録値と一致しません(改変の可能性): "
            f"expected={expected_sha256}, actual={actual_sha256}"
        )
    return {"text": text, "path": path, "sha256": actual_sha256}


def load_used_forms() -> list[dict]:
    with open(p4.PATTERN_A_SOURCE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return next(p for p in data["patterns"] if p["pattern_id"] == "A")["used_forms"]


def verify_marker_replacement(marked_text: str, pattern_a_text: str, used_forms: list[dict]) -> dict:
    """指示section7の静的QA: 元入力が承認済みPattern Aであること、
    5 used form残存0、目印5回、漢字が残存している(ひらがな化されて
    いない)ことを機械確認する。"""
    marker_map = p4.build_marker_map(pattern_a_text, used_forms)

    reconstructed = marked_text
    for e in marker_map:
        reconstructed = reconstructed.replace(MARKER_TOKEN, e["used_form"], 1)
    reconstruction_matches_pattern_a = reconstructed == pattern_a_text

    used_form_residue = {e["used_form"]: marked_text.count(e["used_form"]) for e in marker_map}
    used_form_residue_all_zero = all(v == 0 for v in used_form_residue.values())

    marker_count = marked_text.count(MARKER_TOKEN)
    kanji_count = len(p4d._KANJI_PATTERN.findall(marked_text))

    kanji_target_phrase_presence = {phrase: (phrase in marked_text) for phrase in KANJI_TARGET_PHRASES}

    all_passed = (
        reconstruction_matches_pattern_a and used_form_residue_all_zero
        and marker_count == 5 and kanji_count > 0
        and all(kanji_target_phrase_presence.values())
    )

    return {
        "reconstruction_matches_pattern_a": reconstruction_matches_pattern_a,
        "used_form_residue": used_form_residue,
        "used_form_residue_all_zero": used_form_residue_all_zero,
        "marker_count": marker_count,
        "marker_count_is_five": marker_count == 5,
        "kanji_count": kanji_count,
        "not_hiragana_converted": kanji_count > 0,
        "kanji_target_phrase_presence_in_source": kanji_target_phrase_presence,
        "all_passed": all_passed,
    }


def check_kanji_target_phrases(recognized_text: str) -> dict:
    """漢字かな交じりのASR認識結果に対し、対象句を読み正規化せず
    そのまま照合する(P4D/P5Bのひらがな正規化パイプラインとは別方式。
    ASR結果だけで合否を判断しない、指示section7の明記通り診断情報)。"""
    result = {phrase: (phrase in recognized_text) for phrase in KANJI_TARGET_PHRASES}
    result["目印_count"] = recognized_text.count(MARKER_TOKEN)
    return result
