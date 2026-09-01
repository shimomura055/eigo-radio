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
#      固有名詞らしいopcode差(entity_like)・濁点/半濁点の有無だけが
#      異なる読みゆれ(phonetic_uncertain、ER-007-JA-ASR-TTS-RETRY-
#      PATH-FIX-01で追加)はいずれもCascade対象候補、それ以外の実質的な
#      差はTRUE_CONTENT_MISMATCHとして保護する
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
    大文字/小文字は発話上の意味を持たないため吸収する(例:"INE"/"ine")。
    助数詞「つ」直前の単独漢数字(一〜九)だけは算用数字へ揃える(例:
    "二つ"->"2つ")。「つ」という助数詞の直前という文脈があるため、
    意味・読み・数量が完全に同じ表記ゆれとして安全に判別できる限定的な
    正規化であり、「二十」「二回」等の一般の漢数字は対象外のまま変更
    しない(ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07、
    safety.normalize_kanji_counter_numerals_ja()を再利用)。"""
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)  # 全角英数字->半角、全角記号統一
    t = _PUNCT_RE.sub("", t)
    t = re.sub(r"[A-Za-z]+", lambda m: m.group(0).lower(), t)
    t = safety.normalize_kanji_counter_numerals_ja(t)
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


def _hira_reading(text: str) -> str:
    """ひらがな読みへ変換する(pykakasi、遅延import)。濁点/半濁点の
    有無だけを比較したい場合(_reading_equal_allowing_voicing)に使う。
    ローマ字(hepburn)は濁音行によって文字数が変わる(例: し->じは
    'shi'[3文字]->'ji'[2文字])ため、1文字=1モーラで長さが揃う
    ひらがなのほうが濁点差の比較に適する。"""
    import pykakasi
    kks = pykakasi.kakasi()
    return "".join(item["hira"] for item in kks.convert(text))


def _strip_voicing_marks(s: str) -> str:
    """濁点(゛)・半濁点(゜)を取り除いた「清音化」文字列を返す。Unicodeの
    濁音/半濁音かな(例: が)はNFD正規化で基底文字(か)+結合文字(濁点)へ
    分解できるため、結合文字だけを取り除けば清音化できる。"""
    nfd = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nfd if not unicodedata.combining(ch))


def _reading_equal_allowing_voicing(a: str, b: str) -> bool:
    """濁点/半濁点(いわゆる連濁)の有無だけが異なる読みを許容した比較。
    実例: canonical「聞き終わるころには」/ASR「聞き終わる頃には」で、
    kakasiが文脈なしで「頃」を(本来「ころ」と読むべき箇所でも)連濁形の
    「ごろ」と読んでしまうケース(_reading_equalでは検知できない)。
    「頃」を清音化すると「ころ」となり、canonical側の「ころ」の清音化
    結果と一致するため、ここで拾える。無関係な語同士の読みが清音化後に
    偶然一致することは、通常の日本語語彙では極めて稀(数字・否定・
    固有名詞ヒューリスティックによる保護は本チェックより先に評価される
    ため、ここへ到達する時点でその種の差ではないことは確認済み)。"""
    if not a or not b:
        return False
    try:
        ra = _hira_reading(a)
        rb = _hira_reading(b)
    except Exception:
        return False
    return _strip_voicing_marks(ra) == _strip_voicing_marks(rb)


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
        # ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part B: 読みが完全一致は
        # しないが、濁点/半濁点(連濁)の有無だけが異なる場合は、TTSの
        # 内容誤りではなくkakasiの文脈依存読み判定の限界である可能性が
        # 高い(「頃」を「ごろ」と読む等)。この場合はTRUE_CONTENT_MISMATCH
        # として即TTS再生成させず、ASR_VALIDATION_UNCERTAINとしてCascade
        # (追加ASR再確認)へ回す(entity_likeと同じ扱いだが、判定根拠は
        # 別物として区別して記録する)。
        phonetic_uncertain = _reading_equal_allowing_voicing(c_padded, a_padded)
        # 脱落(delete)・追加(insert)は、除去後に空になる側があるため
        # entity_like/phonetic_uncertain判定の対象外(固有名詞やphonetic
        # ambiguityの脱落/追加はCascade対象にしない、英語Validatorの
        # content_word_diffsと同じ扱い)。
        if tag != "replace":
            entity_like = False
            phonetic_uncertain = False

        result.content_diffs.append({
            "type": tag, "canonical": c_span, "asr": a_span,
            "entity_like": entity_like, "phonetic_uncertain": phonetic_uncertain,
            "cascade_eligible": entity_like or phonetic_uncertain,
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

    # ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part B: Cascade(追加ASR再確認)
    # へ回してよい差は、固有名詞・略語らしき表記ゆれ(entity_like)に加え、
    # 濁点/半濁点の有無だけが異なる読みゆれ(phonetic_uncertain、「頃」の
    # kakasi読み判定限界等)も含める。いずれも「TTSの意味内容は正しい
    # 可能性が高いが、ASR側の表記・読み判定が不確実」というentity_likeと
    # 同種の不確実性であり、即TTS再生成の対象にはしない。
    non_cascade_diffs = [d for d in protected.content_diffs if not d["cascade_eligible"]]
    cascade_eligible_diffs = [d for d in protected.content_diffs if d["cascade_eligible"]]

    # 注意: 文字単位diffのため、読みが同じでも生の文字重複率(ratio)が
    # 低くなることがある(例:「後半」と「公判」は同じ「こうはん」だが
    # 共通する文字は1つもない)。したがってratioは「読みで説明できない
    # 差が実際に残っている場合」のhallucination検知にのみ使い、
    # content_diffsが空(=全ての差が読みで説明できた)の場合はratioに
    # 関わらずPHONETIC_MATCHとする。
    if non_cascade_diffs:
        # ER-010-NO9-A2-KEYPHRASE-AUDIO-ISSUES-103-104-17: protected_check_ja()の
        # 文字単位SequenceMatcherは、canonicalが漢字混じり・ASRが全文ひらがな
        # 書き起こしのケース(例: canonical「落とし穴、ただし書き」/ASR
        # 「おとしあなただしがき」)で、両者に偶然共通するひらがな1〜数文字
        # (と/し/た/だ/き等)だけが"equal"として拾われ、opcodeが不自然に
        # 細かく分断される。この結果、各opcodeへ渡す前後4文字のpadding窓が
        # canonical側とASR側で対応しない範囲を切り出してしまい(語境界が
        # 全く別の位置にずれる)、本来は語末の連濁(例:「書き」の「かき」→
        # 「がき」)だけの差でしかない箇所まで`_reading_equal`/
        # `_reading_equal_allowing_voicing`の局所比較が偽陰性で失敗し、
        # TRUE_CONTENT_MISMATCHへ落ちていた(No.9 A2 Key Phrase 4「a catch」
        # 日本語meaningで実際に6回連続再現、DECISION_LOG.md参照)。
        #
        # 局所opcodeの分断に頼らず、正規化後の**全文**の読み(pykakasi)を
        # 直接比較することで、この window不整合を回避する。数字・否定は
        # このifへ到達する時点で既にprotected_check_ja()側でチェック済み
        # (保護は一切弱めない)。全文読みが完全一致するケースは、既存の
        # 「content_diffsが空ならPHONETIC_MATCH」ルール(下記)と同じ確信度
        # のため即PASSとする。濁点/半濁点の有無だけが異なるケースは、単発の
        # 局所phonetic_uncertain判定と同じ慎重さを保ち、即PASSにはせず
        # 既存のCascade(追加ASR再確認)対象として扱う(「頃/ごろ」と同じ
        # 設計方針の一般化であり、新しい許容基準ではない)。
        whole_text_reading_equal = _reading_equal(c_norm, a_norm)
        whole_text_voicing_equal = (not whole_text_reading_equal) and _reading_equal_allowing_voicing(c_norm, a_norm)
        if whole_text_reading_equal or whole_text_voicing_equal:
            c_reading = safety._kakasi_reading(c_norm)
            a_reading = safety._kakasi_reading(a_norm)
            whole_text_diff = {
                "type": "whole_text_reading", "canonical": c_norm, "asr": a_norm,
                "entity_like": False, "phonetic_uncertain": True, "cascade_eligible": True,
            }
            rescued = ProtectedCheckResultJA(passed=True, content_diffs=[whole_text_diff])
            if whole_text_reading_equal:
                return ClassificationResultJA(
                    "PHONETIC_MATCH", ratio, rescued, should_pass=True, should_retry=False,
                    reason="局所diffはcanonical(漢字)とASR(全ひらがな)の script差で分断されたが、"
                           "正規化後の全文の読みは完全一致",
                    canonical_reading=c_reading, asr_reading=a_reading)
            return ClassificationResultJA(
                "ASR_VALIDATION_UNCERTAIN", ratio, rescued, should_pass=False, should_retry=False,
                reason="局所diffはscript差で分断されたが、正規化後の全文の読みは濁点/半濁点の有無を"
                       "除き一致(retryでは解決しない可能性が高い、Cascadeで追加確認)",
                canonical_reading=c_reading, asr_reading=a_reading)
        if ratio < tts_failure_threshold:
            return ClassificationResultJA(
                "TRUE_CONTENT_MISMATCH", ratio, protected, should_pass=False, should_retry=True,
                reason="全体類似度が著しく低く、TTS生成自体の異常(hallucination等)が疑われる")
        return ClassificationResultJA(
            "TRUE_CONTENT_MISMATCH", ratio, protected, should_pass=False, should_retry=True,
            reason=f"固有名詞・略語・濁点ゆれ以外の内容に差がある(内容誤りの可能性): {non_cascade_diffs}")

    if cascade_eligible_diffs:
        c_reading = safety._kakasi_reading(c_norm)
        a_reading = safety._kakasi_reading(a_norm)
        return ClassificationResultJA(
            "ASR_VALIDATION_UNCERTAIN", ratio, protected, should_pass=False, should_retry=False,
            reason=f"固有名詞・略語、または濁点/半濁点の有無だけが異なる読みゆれにのみ表記差がある"
                   f"(retryでは解決しない可能性が高い): {cascade_eligible_diffs}",
            canonical_reading=c_reading, asr_reading=a_reading)

    # content_diffsが空 = 全ての差が読み一致(漢字/ひらがな/同音別表記等)
    # で説明できた。生の文字重複率に関わらずPHONETIC_MATCHとする。
    return ClassificationResultJA("PHONETIC_MATCH", ratio, protected,
                                   should_pass=True, should_retry=False,
                                   reason="表記(漢字/ひらがな/同音異字等)は異なるが、読みが完全一致")


def is_entity_like_mismatch_ja(result: ClassificationResultJA) -> bool:
    """classify_ja_asr_matchの結果が、Cascade(追加ASR再確認)対象に
    してよいASR_VALIDATION_UNCERTAINかどうかを判定する(英語版
    is_entity_like_mismatch()と同じ役割)。ER-007-JA-ASR-TTS-RETRY-
    PATH-FIX-01時点で、固有名詞・略語らしき表記ゆれ(entity_like)だけで
    なく、濁点/半濁点の有無だけが異なる読みゆれ(phonetic_uncertain)も
    対象に含む(関数名は既存呼び出し元との互換のため変更していない)。"""
    if result.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = result.protected.content_diffs
    return bool(diffs) and all(d["cascade_eligible"] for d in diffs)
