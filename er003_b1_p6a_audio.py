# ============================================================
# er003_b1_p6a_audio.py
# ER-003-B1-P6A: 本編分割・接続方式のPreview適用検証
# ============================================================
# 本編(ER-002以来の記事ナレーション基盤、er002_common.build_narration_plan/
# assemble_audio/run_tts_content_attempts/apply_dynamics3_once)を実機
# コード監査した結果、以下が「自然さを維持している要因」と特定できた
# (推測ではない、er002_common.pyの実装から直接確認)。
#
#   1. 分割は文/段落単位ではなく、記事の「構造境界」(タイトル+本文,
#      Points見出し+Point One+Point Two, In One Line)の3chunkのみ。
#      P4B/P4Cのように英語Key Phraseの位置を理由に文中(読点)で追加
#      分割することはしていない。
#   2. 各chunkは、共通style_prefix(COMMON_BASE_INSTRUCTION+
#      LEVEL2_INSTRUCTION+POINT_LABEL_FIDELITY_RULE)+そのchunkの
#      テキストだけをプロンプトとして独立にTTS呼び出しする
#      (er002_common.run_tts_content_attempts内、chunkごとに
#      _call_tts_with_retryを個別呼び出し)。前後文脈の追加共有・
#      session/seed/temperature制御は一切ない。
#   3. COMMON_BASE_INSTRUCTION自身に
#      "Treat the narration as one continuous program, even when it is
#      generated in separate sections." という一文が含まれており、
#      これが複数回に分けて生成しても声を一貫させる直接の指示になって
#      いる(この行はJAPANESE_STYLE_PREFIX(P3Y/P4B/P4C/P4Dで既に採用
#      済み)にもそのまま含まれている。言語指定行以外は無変更のため)。
#   4. 各chunkのPCMはcommon.normalize_pcm(ピーク基準)で個別正規化した
#      うえで、chunk間にcommon.SECTION_JOIN_PAUSE_SECONDS(0.8秒)の
#      無音を機械的に挿入するだけ(crossfadeなし、chunk先頭・末尾の
#      trimなし)。
#   5. Dynamics3は、結合後の全体波形へ1回だけ適用する
#      (common.apply_dynamics3_once、tts_result.accepted_audioに対して)。
#
# 本ステージでは、この5点をPattern Aの日本語Previewへそのまま適用する。
# Pattern Aは記事構造(タイトル/見出し)を持たないため、本編のbuild_
# narration_planをそのまま流用はできない。その代わり、本編と同じ設計
# 思想(英語Key Phraseの位置ではなく、原稿本来の文境界で最小限に分割)
# に基づき、Pattern A原文の4つの文(「。」区切り)をそのままchunkとする
# (P4B/P4Cの6chunkのように読点で追加分割しない)。文2・文3は元々2つの
# used_formを含むため、1chunkに複数markerが入ることを許容する
# (P4/P4Aで既に実証済みのfind_all_marker_spansによる順序ベース対応
# づけをそのまま再利用できるため、新たな技術的課題ではない)。
#
# 再利用するもの(再実装しない):
#   - er002_common.SAMPLE_RATE/SECTION_JOIN_PAUSE_SECONDS/
#     _call_tts_with_retry/normalize_pcm/assemble_audio/
#     pcm_to_wav_bytes/pcm_bytes_to_float_mono/read_wav_float/
#     write_wav_float/measure_metrics/apply_dynamics3_once
#   - er003_b1_p4_audio.load_pattern_a_text/PATTERN_A_SOURCE_PATH/
#     build_marker_map/get_full_text_via_azure_stt_continuous/
#     find_all_marker_spans/_strip_punctuation
#   - er003_b1_p4b_audio.JAPANESE_STYLE_PREFIX/VOICE_NAME/
#     MAX_TTS_TECHNICAL_RETRY/GAP_BEFORE_TARGET_SECONDS/
#     GAP_AFTER_TARGET_SECONDS/GAP_TOLERANCE_SECONDS/
#     EN_TRIM_SAFETY_MARGIN_SECONDS/EXISTING_SHOT_ON_TARGET_PATH/
#     build_tts_prompt
#   - er003_b1_p3w_audio.MFA_*/run_mfa_align/parse_textgrid_words_tier
#   - er003_b1_p3z_audio.adjust_trailing_silence/adjust_leading_silence
#   - er003_b1_p3u_audio.find_speech_bounds/trim_english_keyword_silence
#
# 新規に追加するのは、(1) Pattern Aを4文へ分割し1chunkに0〜2markerを
# 許容するbuild_chunk_plan、(2) その静的検証、(3) 漢字かな表記のままの
# 対象句チェック、の3つのみ。

from __future__ import annotations

import re

import er002_common as common
import er003_b1_p4_audio as p4
import er003_b1_p4b_audio as p4b

ARTICLE_ID = "A01"
VOICE_NAME = p4b.VOICE_NAME
JAPANESE_STYLE_PREFIX = p4b.JAPANESE_STYLE_PREFIX
MAX_TTS_TECHNICAL_RETRY = p4b.MAX_TTS_TECHNICAL_RETRY
PATTERN_A_SOURCE_PATH = p4b.PATTERN_A_SOURCE_PATH
build_tts_prompt = p4b.build_tts_prompt

GAP_BEFORE_TARGET_SECONDS = p4b.GAP_BEFORE_TARGET_SECONDS  # 0.40
GAP_AFTER_TARGET_SECONDS = p4b.GAP_AFTER_TARGET_SECONDS    # 0.30
GAP_TOLERANCE_SECONDS = p4b.GAP_TOLERANCE_SECONDS          # 0.03
EN_TRIM_SAFETY_MARGIN_SECONDS = p4b.EN_TRIM_SAFETY_MARGIN_SECONDS  # 0.08
EXISTING_SHOT_ON_TARGET_PATH = p4b.EXISTING_SHOT_ON_TARGET_PATH

# 本編で採用されているchunk間無音(er002_common.SECTION_JOIN_PAUSE_SECONDS)
# をそのまま再利用する。P4Cは意図的にこれを使わなかった(固定無音を
# 足さない方式)が、本ステージは「本編で自然な接続に実際に寄与している
# 処理を適用する」(指示section8)ため、あえて本編と同じ0.8秒を使う。
JA_CHUNK_JOIN_PAUSE_SECONDS = common.SECTION_JOIN_PAUSE_SECONDS  # 0.8

MARKER_TOKEN = "目印"
MARKER_TOKEN_SEQUENCE = (MARKER_TOKEN,)

_ASCII_LETTER_PATTERN = re.compile(r"[A-Za-z]")

# Pattern A原文の「。」区切り(4文)。P4B/P4Cのように読点でのさらなる
# 分割は行わない(指示section5: 文中の不自然な場所でchunkを終了させない)。
_CHUNK_END_ANCHORS = [
    "静かな均衡が保たれます。",
    "を守ろうとします。",
    "stoppage timeへ。",
]

# 指示section6・10で明示された、省略・言い換えしてはいけない原稿要素
# (漢字かな交じり表記のまま照合、読み正規化はしない)。
KANJI_TARGET_PHRASES = (
    "選手を交代で下げる",
    "という決断で",
    "守備を固め",
    "わずかなリード",
    "最後の数分",
    "何が起きるのでしょうか",
)


def build_chunk_plan(pattern_a_text: str, used_forms: list[dict]) -> list[dict]:
    """Pattern A原文を、既存の文境界(「。」)で4つのchunkへ分割する。
    語句・順序・句読点は一切変更しない(既存アンカー文字列での単純な
    スライスのみ、P4B/P4Cと同じ検証済みアンカーの一部を再利用)。
    1chunkに0〜2件のused_formを許容する(P4B/P4Cは1chunk=1markerに
    限定していたが、本ステージは文境界を優先するためこの制約を外す)。"""
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

    plan = []
    for i, source_text in enumerate(raw_chunks, start=1):
        matched = sorted(
            (uf for uf in used_forms if uf["used_form"] in source_text),
            key=lambda uf: source_text.index(uf["used_form"]),
        )

        tts_text = source_text
        for uf in matched:
            if tts_text.count(uf["used_form"]) != 1:
                raise ValueError(f"chunk{i}内でused_form{uf['used_form']!r}の出現数が1ではありません")
            tts_text = tts_text.replace(uf["used_form"], MARKER_TOKEN, 1)

        plan.append({
            "chunk_id": f"{i:02d}",
            "chunk_type": "marker" if matched else "normal",
            "source_text": source_text,
            "tts_text": tts_text,
            "used_forms": [uf["used_form"] for uf in matched],
            "canonical_english": [uf["canonical_english"] for uf in matched],
            "marker_count_in_tts_text": tts_text.count(MARKER_TOKEN),
            "order": i,
        })

    return plan


def verify_chunk_plan_static(chunk_plan: list[dict], pattern_a_text: str) -> dict:
    """TTS呼び出し前の静的検証。1つでも満たさない場合は呼び出し側で
    TTSを呼ばず停止する。"""
    reconstructed_source = "".join(c["source_text"] for c in chunk_plan)
    reconstruction_matches = reconstructed_source == pattern_a_text

    per_chunk_checks = []
    all_ok = True
    for c in chunk_plan:
        ascii_count = len(_ASCII_LETTER_PATTERN.findall(c["tts_text"]))
        used_form_residue = sum(c["tts_text"].count(uf) for uf in c["used_forms"])
        marker_count = c["tts_text"].count(MARKER_TOKEN)
        expected_marker_count = len(c["used_forms"])
        ok = (used_form_residue == 0 and marker_count == expected_marker_count and ascii_count == 0)
        if not ok:
            all_ok = False
        per_chunk_checks.append({
            "chunk_id": c["chunk_id"], "chunk_type": c["chunk_type"],
            "used_form_residue": used_form_residue, "marker_count": marker_count,
            "expected_marker_count": expected_marker_count, "ascii_letter_count": ascii_count, "ok": ok,
        })

    total_marker_count = sum(c["tts_text"].count(MARKER_TOKEN) for c in chunk_plan)
    total_marker_count_is_five = total_marker_count == 5

    all_used_forms = [uf for c in chunk_plan for uf in c["used_forms"]]
    used_form_count_is_five = len(all_used_forms) == 5

    kanji_target_phrase_presence = {phrase: (phrase in pattern_a_text) for phrase in KANJI_TARGET_PHRASES}

    all_passed = (
        reconstruction_matches and all_ok and total_marker_count_is_five
        and used_form_count_is_five and all(kanji_target_phrase_presence.values())
    )

    return {
        "reconstruction_matches": reconstruction_matches,
        "per_chunk_checks": per_chunk_checks,
        "chunk_count": len(chunk_plan),
        "total_marker_count": total_marker_count,
        "total_marker_count_is_five": total_marker_count_is_five,
        "used_form_count_is_five": used_form_count_is_five,
        "kanji_target_phrase_presence": kanji_target_phrase_presence,
        "all_passed": all_passed,
    }


def check_kanji_target_phrases(recognized_text: str) -> dict:
    """漢字かな交じりのASR認識結果に対し、対象句を読み正規化せず
    そのまま照合する(診断情報、ASR結果のみで合否を判断しない)。"""
    result = {phrase: (phrase in recognized_text) for phrase in KANJI_TARGET_PHRASES}
    result["目印_count"] = recognized_text.count(MARKER_TOKEN)
    return result
