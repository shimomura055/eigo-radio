# ============================================================
# er007_ja_asr_validator_01.py
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01 Part A:
# 日本語ASR全文Validator(旧prefix+length方式を置き換える)。
# ============================================================
# 設計方針(English Validator er006_preprod_hardening_01_validation.py
# のprotected_check()と同じ思想を、日本語の特性へ適応させたもの):
#   1. canonical/ASR両テキストを軽く正規化(句読点除去、数字表記統一)
#   2. difflib.SequenceMatcherで文字単位の全文sequence diffを取る
#      (文頭2文字だけを見る旧方式を廃止し、全文の並びを評価する)
#   3. 各diff opcode(replace/delete/insert)ごとに、数字・否定・
#      固有名詞らしさ(カタカナ列・英大文字列)・読み(pykakasi)の
#      一致を個別に判定する(英語のProtected Checkと同じ「opcode単位で
#      保護要素を見る」設計)
#   4. 読みが完全一致するopcode差(漢字/ひらがな表記ゆれ等)は許容差、
#      固有名詞らしいopcode差はentity_like(Cascade対象候補)、
#      それ以外の実質的な差はTRUE_CONTENT_MISMATCHとして保護する
from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass, field

# 既存の短いsegment用検証(er003_audio_tts_asr_safety.py)が持つ
# 読み変換・数字抽出・否定マーカー判定をそのまま再利用する(重複実装しない)。
import er003_audio_tts_asr_safety as safety

VALID_CLASSIFICATIONS_JA = (
    "EXACT_MATCH", "NORMALIZED_MATCH", "PHONETIC_MATCH",
    "ASR_VALIDATION_UNCERTAIN", "TRUE_CONTENT_MISMATCH",
)

_PUNCT_RE = re.compile(r"[、。・「」『』（）()\s！？!?…—―‥～〜/／]")
_KATAKANA_RE = re.compile(r"[゠-ヿ]+")
_LATIN_ACRONYM_RE = re.compile(r"[A-Za-z]{2,}")
_DIGIT_RE = re.compile(r"\d+")


@dataclass
class ProtectedCheckResultJA:
    passed: bool
    number_mismatches: list[tuple[str, str]] = field(default_factory=list)
    negation_mismatches: list[tuple[str, str]] = field(default_factory=list)
    content_diffs: list[dict] = field(default_factory=list)  # {"type","canonical","asr","entity_like","reading_equal"}


@dataclass
class ClassificationResultJA:
    classification: str
    similarity_ratio: float
    protected: ProtectedCheckResultJA
    should_pass: bool
    should_retry: bool
    reason: str
    canonical_reading: str = ""
    asr_reading: str = ""


def normalize_ja(text: str) -> str:
    """句読点・空白等の非発話記号のみを除去する(内容語は一切変更しない)。
    カーリー引用符はストレートへ、全角/半角の数字は正規化する。英字の
    大文字/小文字は発話上の意味を持たないため吸収する(例:"INE"/"ine")。"""
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)  # 全角英数字->半角、全角記号統一
    t = _PUNCT_RE.sub("", t)
    t = re.sub(r"[A-Za-z]+", lambda m: m.group(0).lower(), t)
    return t


def _is_katakana_or_acronym(s: str) -> bool:
    """カタカナ列、または英大文字を含む語(FTC/PTP等のacronym)を、
    固有名詞・専門略語らしい語として扱う(英語Validatorの『文中で
    大文字始まりだった語』ヒューリスティックの日本語版)。"""
    if not s:
        return False
    stripped = s.replace(" ", "")
    katakana_chars = sum(1 for run in _KATAKANA_RE.findall(stripped) for _ in run)
    has_acronym = bool(_LATIN_ACRONYM_RE.search(s))
    total_len = len(stripped)
    return has_acronym or (total_len > 0 and katakana_chars / total_len >= 0.5)


def _reading_equal(a: str, b: str) -> bool:
    if a == b:
        return True
    if not a or not b:
        return False
    try:
        ra = safety._kakasi_reading(a)
        rb = safety._kakasi_reading(b)
    except Exception:
        return False
    return ra == rb


_READING_CONTEXT_CHARS = 4  # 単独の漢字1文字は文脈なしでは正しい読みが
                             # 決まらない(例:「居」単独と「居る」の「居」
                             # は読みが変わる、「速」単独[そく]と「速い」
                             # の「速」[はや]も同様)。diff span前後の
                             # 「equal」領域から同じ文字数だけ文脈を足して
                             # から読みを比較する(前後の文脈はcanonical/ASR
                             # 両側で文字として同一なため、比較の公平性は
                             # 崩れない)。


def protected_check_ja(canonical_norm: str, asr_norm: str) -> ProtectedCheckResultJA:
    result = ProtectedCheckResultJA(passed=True)
    sm = difflib.SequenceMatcher(None, canonical_norm, asr_norm, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        c_span = canonical_norm[i1:i2]
        a_span = asr_norm[j1:j2]

        c_numbers = _DIGIT_RE.findall(c_span)
        a_numbers = _DIGIT_RE.findall(a_span)
        if c_numbers != a_numbers and (c_numbers or a_numbers):
            result.number_mismatches.append(("".join(c_numbers), "".join(a_numbers)))
            result.passed = False
            continue  # 数字差は独立して記録、content_diffsへは二重計上しない

        c_neg = safety._has_negation_ja(c_span)
        a_neg = safety._has_negation_ja(a_span)
        if c_neg != a_neg:
            result.negation_mismatches.append((c_span if c_neg else "", a_span if a_neg else ""))
            result.passed = False
            continue

        if not c_span and not a_span:
            continue

        c_pad_start = max(0, i1 - _READING_CONTEXT_CHARS)
        c_pad_end = min(len(canonical_norm), i2 + _READING_CONTEXT_CHARS)
        a_pad_start = max(0, j1 - _READING_CONTEXT_CHARS)
        a_pad_end = min(len(asr_norm), j2 + _READING_CONTEXT_CHARS)
        c_padded = canonical_norm[c_pad_start:c_pad_end]
        a_padded = asr_norm[a_pad_start:a_pad_end]

        reading_equal = _reading_equal(c_padded, a_padded)
        if reading_equal:
            # 漢字/ひらがな表記ゆれ等、読みが変わらない差は許容差
            continue

        entity_like = _is_katakana_or_acronym(c_span) and _is_katakana_or_acronym(a_span)
        # 脱落(delete)・追加(insert)は、除去後に空になる側があるため
        # entity_like判定の対象外(固有名詞の脱落/追加はentity_likeにしない、
        # 英語Validatorのcontent_word_diffsと同じ扱い)。
        if tag != "replace":
            entity_like = False

        result.content_diffs.append({
            "type": tag, "canonical": c_span, "asr": a_span, "entity_like": entity_like,
        })

    return result


def classify_ja_asr_match(canonical_text: str, asr_text: str | None,
                           tts_failure_threshold: float = 0.4) -> ClassificationResultJA:
    if asr_text is None:
        return ClassificationResultJA("TRUE_CONTENT_MISMATCH", 0.0, ProtectedCheckResultJA(passed=False),
                                       should_pass=False, should_retry=True,
                                       reason="ASR書き起こし自体が取得できなかった")

    if canonical_text.strip() == asr_text.strip():
        return ClassificationResultJA("EXACT_MATCH", 1.0, ProtectedCheckResultJA(passed=True),
                                       should_pass=True, should_retry=False, reason="完全一致")

    c_norm = normalize_ja(canonical_text)
    a_norm = normalize_ja(asr_text)

    if c_norm == a_norm:
        return ClassificationResultJA("NORMALIZED_MATCH", 1.0, ProtectedCheckResultJA(passed=True),
                                       should_pass=True, should_retry=False,
                                       reason="句読点・全角半角等の表記正規化後に一致")

    ratio = difflib.SequenceMatcher(None, c_norm, a_norm, autojunk=False).ratio()

    protected = protected_check_ja(c_norm, a_norm)

    if not protected.passed:
        return ClassificationResultJA(
            "TRUE_CONTENT_MISMATCH", ratio, protected, should_pass=False, should_retry=True,
            reason=f"数字/否定の不一致を検出: numbers={protected.number_mismatches} negation={protected.negation_mismatches}")

    non_entity_diffs = [d for d in protected.content_diffs if not d["entity_like"]]
    entity_only_diffs = [d for d in protected.content_diffs if d["entity_like"]]

    # 注意: 文字単位diffのため、読みが同じでも生の文字重複率(ratio)が
    # 低くなることがある(例:「後半」と「公判」は同じ「こうはん」だが
    # 共通する文字は1つもない)。したがってratioは「読みで説明できない
    # 差が実際に残っている場合」のhallucination検知にのみ使い、
    # content_diffsが空(=全ての差が読みで説明できた)の場合はratioに
    # 関わらずPHONETIC_MATCHとする。
    if non_entity_diffs:
        if ratio < tts_failure_threshold:
            return ClassificationResultJA(
                "TRUE_CONTENT_MISMATCH", ratio, protected, should_pass=False, should_retry=True,
                reason="全体類似度が著しく低く、TTS生成自体の異常(hallucination等)が疑われる")
        return ClassificationResultJA(
            "TRUE_CONTENT_MISMATCH", ratio, protected, should_pass=False, should_retry=True,
            reason=f"固有名詞・略語以外の内容に差がある(内容誤りの可能性): {non_entity_diffs}")

    if entity_only_diffs:
        c_reading = safety._kakasi_reading(c_norm)
        a_reading = safety._kakasi_reading(a_norm)
        return ClassificationResultJA(
            "ASR_VALIDATION_UNCERTAIN", ratio, protected, should_pass=False, should_retry=False,
            reason=f"固有名詞・略語らしき語にのみ表記差がある(retryでは解決しない可能性が高い): {entity_only_diffs}",
            canonical_reading=c_reading, asr_reading=a_reading)

    # content_diffsが空 = 全ての差が読み一致(漢字/ひらがな/同音別表記等)
    # で説明できた。生の文字重複率に関わらずPHONETIC_MATCHとする。
    return ClassificationResultJA("PHONETIC_MATCH", ratio, protected,
                                   should_pass=True, should_retry=False,
                                   reason="表記(漢字/ひらがな/同音異字等)は異なるが、読みが完全一致")


def is_entity_like_mismatch_ja(result: ClassificationResultJA) -> bool:
    """classify_ja_asr_matchの結果が、固有名詞・略語らしき語のみの表記差に
    よるASR_VALIDATION_UNCERTAINかどうかを判定する(英語版
    is_entity_like_mismatch()と同じ役割)。"""
    if result.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = result.protected.content_diffs
    return bool(diffs) and all(d["entity_like"] for d in diffs)
