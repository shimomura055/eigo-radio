# ============================================================
# er011_open112_kp_validator_fix_trial_17_en.py
# 管理ID: OPEN-112-TREND-THEME2-B-KEYPHRASE-VALIDATOR-FIX-TRIAL-17
# Track B: EN厳密同音の正規化(隔離Trial、Production配線禁止)
# ============================================================
# 背景(Opus診断-15の結論): kp4_en canonical "point to" / ASR "Point two."で、
# er006_preprod_hardening_01_validation._convert_cardinal_words()がASR側
# "two"だけを"2"へ変換し、protected_check()の数字保護ゲートが
# 「canonicalに無い数字」として即TRUE_CONTENT_MISMATCHにする。canonical側
# "to"は_STOPWORDSで除外されるため、既存のhomophone_candidate機構
# (wait/weight等、1語対1語のcontent word置換にのみ適用)にも到達しない。
#
# ユーザー正式決定(2026-09-06): 完全同音(CMU辞書ARPAbet完全一致)のみを
# 同一とみなしPASSしてよい。近似音・別発音はPASSさせない。新辞書は作らず
# 既存er008_asr_variant_hardening_15_homophone_en.homophone_arpabet_
# equivalent()を再利用する。
#
# 実装方針: Production関数(classify_asr_match/protected_check等)は一切
# 変更しない。本モジュールは、Production関数の結果を受け取った後に、
# 「1トークン対1トークンの数字不一致opcodeが原因の唯一の不合格理由であり、
# かつ変換前の生語同士がARPAbet完全同音の場合のみ」という狭い例外を
# 後付けで適用する(Approach 2、数字ゲート例外案)。Approach 1(順序変更案)
# は、同じ判定材料をより早い段階(数字変換より前)で評価する変種として
# 別途実装し、2案の挙動・リスクを比較する。
# ============================================================
from __future__ import annotations

import dataclasses
import difflib

import er006_preprod_hardening_01_validation as validation
import er008_asr_variant_hardening_15_homophone_en as homophone_en

HOMOPHONE_NUMBER_EXCEPTION_CLASSIFICATION = "HOMOPHONE_MATCH_NUMBER_EXCEPTION"


def _raw_tokens_no_cardinal_conversion(text: str) -> list[str]:
    """Production関数validation.tokenize()の内部ステップ
    _convert_cardinal_words()だけを一時的に無効化して得る「変換前の生語」
    token列(その他の正規化[序数・通貨・小数点・BR/AM綴り等]は通常通り
    適用したまま)。Production関数自体は変更しない(呼び出しの間だけ
    モジュール属性を退避・復元する、単体testでもよく使われる一時的な
    monkeypatch)。"""
    original = validation._convert_cardinal_words
    validation._convert_cardinal_words = lambda t: t
    try:
        return validation.tokenize(text)
    finally:
        validation._convert_cardinal_words = original


def _alignment_safe(canonical_text: str, asr_text: str) -> tuple[list[str], list[str], list[str], list[str], bool]:
    """canon_raw/asr_raw(変換前)とcanon_tokens/asr_tokens(Production通常
    経路、変換後)を返す。alignment_safe=Trueは「このテキスト全体で、
    cardinal語変換によってtoken数が一切変わっていない」ことを意味し、
    その場合に限り、変換後token列のindex iが変換前token列の同じindex i
    に対応する(=生語を安全に逆引きできる)ことを保証する。複合基数
    (例: "twenty eight"->"28"のような2:1の圧縮)がテキスト中のどこかに
    1箇所でもあれば、それ以降のindexはズレるため安全側でFalseにする。"""
    canon_tokens = validation.tokenize(canonical_text)
    asr_tokens = validation.tokenize(asr_text)
    canon_raw = _raw_tokens_no_cardinal_conversion(canonical_text)
    asr_raw = _raw_tokens_no_cardinal_conversion(asr_text)
    safe = (len(canon_tokens) == len(canon_raw)) and (len(asr_tokens) == len(asr_raw))
    return canon_raw, asr_raw, canon_tokens, asr_tokens, safe


def _locate_number_mismatch_opcodes(canon_tokens: list[str], asr_tokens: list[str]) -> list[dict]:
    """Production protected_check()と全く同じSequenceMatcherを独立に
    走らせ(読み取り専用、Production関数は呼ばず・変更しない)、数字
    不一致を引き起こしているopcodeの位置を特定するためだけに使う。"""
    sm = difflib.SequenceMatcher(None, canon_tokens, asr_tokens, autojunk=False)
    located = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        canon_span = canon_tokens[i1:i2]
        asr_span = asr_tokens[j1:j2]
        canon_numbers = [t for t in canon_span if validation._is_number(t)]
        asr_numbers = [t for t in asr_span if validation._is_number(t)]
        if canon_numbers != asr_numbers and (canon_numbers or asr_numbers):
            located.append({"tag": tag, "canon_span": canon_span, "asr_span": asr_span,
                             "i1": i1, "i2": i2, "j1": j1, "j2": j2})
    return located


def _try_homophone_number_rescue(canonical_text: str, asr_text: str, baseline: "validation.ClassificationResult"):
    """baselineがTRUE_CONTENT_MISMATCH(数字不一致のみが原因、否定不一致は
    無い)の場合に、1トークン対1トークンの置換opcode全てが変換前の生語
    同士でARPAbet厳密同音である場合のみ、rescue結果を返す(該当しなければ
    Noneを返し、呼び出し側はbaselineをそのまま使う)。"""
    if baseline.classification != "TRUE_CONTENT_MISMATCH":
        return None, []
    if not baseline.protected.number_mismatches or baseline.protected.negation_mismatches:
        return None, []

    canon_raw, asr_raw, canon_tokens, asr_tokens, safe = _alignment_safe(canonical_text, asr_text)
    if not safe:
        return None, []

    located = _locate_number_mismatch_opcodes(canon_tokens, asr_tokens)
    if not located or len(located) != len(baseline.protected.number_mismatches):
        return None, []

    rescues = []
    for loc in located:
        if loc["tag"] != "replace" or len(loc["canon_span"]) != 1 or len(loc["asr_span"]) != 1:
            return None, []
        raw_c = canon_raw[loc["i1"]]
        raw_a = asr_raw[loc["j1"]]
        is_homophone = homophone_en.homophone_arpabet_equivalent(raw_c, raw_a)
        if is_homophone is not True:
            return None, []
        rescues.append({"canonical_raw": raw_c, "asr_raw": raw_a,
                         "canonical_converted": loc["canon_span"][0], "asr_converted": loc["asr_span"][0]})

    # 数字ゲート以外の保護(否定・非同音の内容語差)が無いことを、Production
    # protected_check()自体を素直に呼んで再確認する(number_mismatchesが
    # 出ること自体は織り込み済みなので、それ以外の観点だけを見る)。
    entity_tokens = validation.capitalized_flags(canonical_text)
    protected_full = validation.protected_check(canon_tokens, asr_tokens, entity_tokens=entity_tokens)
    if protected_full.negation_mismatches:
        return None, []
    non_entity_non_homophone_diffs = [
        d for d in protected_full.content_word_diffs if not d["entity_like"] and not d["homophone_candidate"]
    ]
    if non_entity_non_homophone_diffs:
        return None, []

    rescued = dataclasses.replace(
        baseline,
        classification=HOMOPHONE_NUMBER_EXCEPTION_CLASSIFICATION,
        should_pass=True, should_retry=False,
        reason=f"数字ゲート例外(Track B): ASR側の数字と、変換前のcanonical側の語が"
               f"CMU辞書ARPAbet完全同音(厳密一致のみ許容): rescues={rescues}",
    )
    return rescued, rescues


def classify_asr_match_track_b_approach2(canonical_text: str, asr_text: str, **kwargs):
    """Approach 2(数字ゲート例外案、推奨)。Production関数
    validation.classify_asr_match()をそのまま呼び、その結果に対して
    狭いrescueだけを後付けする(数字ゲートの例外はグローバルに
    token数が変化していない[alignment_safe]場合のみ有効、複合基数を
    含む長文では安全側でrescueしない)。"""
    baseline = validation.classify_asr_match(canonical_text, asr_text, **kwargs)
    rescued, rescues = _try_homophone_number_rescue(canonical_text, asr_text, baseline)
    if rescued is not None:
        return rescued, rescues
    return baseline, []


def classify_asr_match_track_b_approach1(canonical_text: str, asr_text: str, **kwargs):
    """Approach 1(順序変更案)。Approach 2と同じ判定材料(CMU辞書ARPAbet
    厳密同音)を使うが、「テキスト全体でtoken数が変化していないこと」
    (alignment_safe)というグローバルな前提を課さず、rescue対象の
    opcode自身がlocalに1トークン対1トークンの置換であれば足りるとする、
    より緩い(=適用範囲は広いがリスクも高い)変種。他の複合基数
    (例: "twenty eight")が同じテキストの別の場所に存在していても、
    その部分のindexズレを気にせずrescueを試みる。"""
    baseline = validation.classify_asr_match(canonical_text, asr_text, **kwargs)
    if baseline.classification != "TRUE_CONTENT_MISMATCH":
        return baseline, []
    if not baseline.protected.number_mismatches or baseline.protected.negation_mismatches:
        return baseline, []

    canon_tokens = validation.tokenize(canonical_text)
    asr_tokens = validation.tokenize(asr_text)
    canon_raw = _raw_tokens_no_cardinal_conversion(canonical_text)
    asr_raw = _raw_tokens_no_cardinal_conversion(asr_text)
    located = _locate_number_mismatch_opcodes(canon_tokens, asr_tokens)
    if not located or len(located) != len(baseline.protected.number_mismatches):
        return baseline, []

    rescues = []
    for loc in located:
        if loc["tag"] != "replace" or len(loc["canon_span"]) != 1 or len(loc["asr_span"]) != 1:
            return baseline, []
        i1, j1 = loc["i1"], loc["j1"]
        # Approach 1: グローバルなalignment_safeを要求せず、このopcode位置が
        # 生語token列の範囲内であることだけ確認する(ローカルな安全確認のみ)。
        if i1 >= len(canon_raw) or j1 >= len(asr_raw):
            return baseline, []
        raw_c = canon_raw[i1]
        raw_a = asr_raw[j1]
        is_homophone = homophone_en.homophone_arpabet_equivalent(raw_c, raw_a)
        if is_homophone is not True:
            return baseline, []
        rescues.append({"canonical_raw": raw_c, "asr_raw": raw_a,
                         "canonical_converted": loc["canon_span"][0], "asr_converted": loc["asr_span"][0]})

    entity_tokens = validation.capitalized_flags(canonical_text)
    protected_full = validation.protected_check(canon_tokens, asr_tokens, entity_tokens=entity_tokens)
    if protected_full.negation_mismatches:
        return baseline, []
    non_entity_non_homophone_diffs = [
        d for d in protected_full.content_word_diffs if not d["entity_like"] and not d["homophone_candidate"]
    ]
    if non_entity_non_homophone_diffs:
        return baseline, []

    rescued = dataclasses.replace(
        baseline, classification=HOMOPHONE_NUMBER_EXCEPTION_CLASSIFICATION,
        should_pass=True, should_retry=False,
        reason=f"数字ゲート例外(Track B Approach1、緩いローカル判定): rescues={rescues}",
    )
    return rescued, rescues
