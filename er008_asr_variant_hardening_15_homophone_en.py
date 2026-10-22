# ============================================================
# er008_asr_variant_hardening_15_homophone_en.py
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part I/J:
# 英語の同音異義語(homophone)をローカル判定するための最小実装。
# ============================================================
# No.8 point_one_heading("wait"/ASR"weight")監査で判明した通り、英語
# Validatorには同音異義語を扱う仕組みが存在せず、wait/weightのような
# 一般語の差はentity_like判定に該当しないため、Secondary ASR(Azure)へ
# 一度も回らずに即blind TTS retryされていた。
#
# QCD比較(ユーザー指示、実装前に実施)の結論として、閉じたペアテーブル
# 単独ではなく、CMU Pronouncing Dictionary(ARPAbet音素列、ローカル
# データ・ネットワーク不要・新規依存はpykakasiと同種の軽量な言語データ
# 辞書のみ)を主経路とするハイブリッド方式を採用する。詳細はDECISION_LOG
# のER-008-ASR-VARIANT-HARDENING-AND-RETRY-15エントリを参照。
#
# 重要な設計上の区別(このファイル内で2つの比較関数を分ける理由):
#   - homophone_arpabet_equivalent(): 一般の英単語(wait/weight等)向け。
#     「いずれかの発音バリアント同士が完全一致すればOK」といういる
#     やや緩い基準を使う(CMU辞書内の一般語は、バリアントが複数あって
#     もいずれも実在の発音のため、この緩さで実害は無い)。
#   - entity_word_arpabet_primary_match(): 固有名詞(人名等)向け。
#     実際に`Tse`という3文字がCMU辞書に(無関係な理由で)偶然登録されて
#     おり、その一部バリアント(`S IY1`)が`Sea`/`C`という無関係な語と
#     一致してしまう事例を実装中に確認した。固有名詞では「辞書に載って
#     いる」こと自体が発音の正しさを保証しないため、より厳しく「代表
#     (先頭)発音同士の完全一致」のみを許可する(ER-008-15 D-2'参照)。
from __future__ import annotations

from dataclasses import dataclass

try:
    import pronouncing
    _PRONOUNCING_AVAILABLE = True
except ImportError:
    _PRONOUNCING_AVAILABLE = False


# ------------------------------------------------------------
# CMU辞書に存在しない語(縮約形の一部等)向けの、小さな閉じた補完テーブル。
# 2026-08-28時点、Part J-2必須fixture(wait/weight, their/there,
# hear/here, week/weak)はいずれもCMU辞書内で解決できることを確認済み
# ("they're"もCMU辞書に登録されていた)のため、初期状態では空。実際に
# CMU辞書で解決できない同音語ペアが量産時に見つかった場合のみ、ここへ
# 追記する(OPEN_ITEMS.md参照、個別whitelistを主方式にはしない)。
_HOMOPHONE_OVERRIDE_GROUPS: tuple[frozenset[str], ...] = ()


def _normalize_word(word: str) -> str:
    return (word or "").strip().lower().strip("'\".,;:!?")


def _phone_variants(word: str) -> list[str] | None:
    """CMU辞書から発音バリアント一覧(ARPAbet文字列、ストレス記号含む)を
    取得する。辞書に存在しない場合はNone(=辞書では判定不能)。"""
    if not _PRONOUNCING_AVAILABLE:
        return None
    w = _normalize_word(word)
    if not w:
        return None
    phones = pronouncing.phones_for_word(w)
    return phones or None


def _override_group_for(word: str) -> frozenset[str] | None:
    w = _normalize_word(word)
    for group in _HOMOPHONE_OVERRIDE_GROUPS:
        if w in group:
            return group
    return None


def homophone_arpabet_equivalent(word_a: str, word_b: str) -> bool | None:
    """一般の英単語2語が同音異義語(発音が完全一致)かどうかを判定する。

    戻り値:
      True  -> 発音が完全一致する同音語(いずれかのバリアント同士が一致)
      False -> 両語ともCMU辞書で解決できたが、発音が一致しない
      None  -> 少なくとも一方がCMU辞書・補完テーブルのいずれにも
               存在せず、判定不能(呼び出し側は「同音語として扱わない」
               安全側で処理すること)
    """
    wa, wb = _normalize_word(word_a), _normalize_word(word_b)
    if not wa or not wb:
        return None
    if wa == wb:
        return True

    variants_a = _phone_variants(wa)
    variants_b = _phone_variants(wb)
    if variants_a is not None and variants_b is not None:
        return bool(set(variants_a) & set(variants_b))

    group_a = _override_group_for(wa)
    group_b = _override_group_for(wb)
    if group_a is not None and group_b is not None and group_a == group_b:
        return True
    if (variants_a is None and group_a is None) or (variants_b is None and group_b is None):
        return None
    return False


def entity_word_arpabet_primary_match(canonical_word: str, candidate_word: str) -> bool | None:
    """固有名詞1語同士の、代表(先頭)発音バリアントによる厳格な一致判定。

    homophone_arpabet_equivalent()と異なり「いずれかのバリアントが一致」
    ではなく「CMU辞書が最初に返す代表的な発音同士が完全一致」のみを許可
    する。固有名詞はCMU辞書に偶然・部分的に登録されているだけで、その
    登録が実際の人物・地名の発音を正しく反映している保証が無いため
    (`Tse`の実例を参照)、より保守的な基準にする。

    戻り値:
      True  -> 代表発音同士が完全一致
      False -> 両語ともCMU辞書で解決できたが、代表発音が一致しない
      None  -> 少なくとも一方がCMU辞書に存在せず、判定不能(呼び出し側は
               ER-008-15 D-2'の(B)経路[Pronunciation Ledger]へ進むこと)
    """
    wa, wb = _normalize_word(canonical_word), _normalize_word(candidate_word)
    if not wa or not wb:
        return None
    if wa == wb:
        return True

    variants_a = _phone_variants(wa)
    variants_b = _phone_variants(wb)
    if variants_a is None or variants_b is None:
        return None
    return variants_a[0] == variants_b[0]


@dataclass
class EntitySpanMatchResult:
    resolved: bool  # 全構成語がCMU辞書で解決できたか(Trueならmatchedの値が確定情報)
    matched: bool   # resolved=Trueの場合のみ意味を持つ: 全語が一致したか
    unresolved_words: list[str]  # CMU辞書で解決できなかった語(canonical側の語のうち)


def entity_span_arpabet_match(canonical_span: str, candidate_span: str) -> EntitySpanMatchResult:
    """複数語からなる固有名詞span(例: "Kristie Tse")を、語ごとに
    entity_word_arpabet_primary_match()で比較する。語数が一致しない
    場合は「解決不能」として扱う(既存の英語Validatorの語数不一致時の
    扱いと同じ、安全側)。"""
    canon_words = _normalize_word(canonical_span).split()
    cand_words = _normalize_word(candidate_span).split()
    if not canon_words or len(canon_words) != len(cand_words):
        return EntitySpanMatchResult(resolved=False, matched=False, unresolved_words=canon_words)

    unresolved = []
    all_match = True
    for cw, dw in zip(canon_words, cand_words):
        result = entity_word_arpabet_primary_match(cw, dw)
        if result is None:
            unresolved.append(cw)
            all_match = False
        elif not result:
            all_match = False
    resolved = not unresolved
    return EntitySpanMatchResult(resolved=resolved, matched=(resolved and all_match), unresolved_words=unresolved)


# ------------------------------------------------------------
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02 (2026-10-22, Opus P-01/P-02/P-03):
# 追加のみ(既存関数は無変更)。『強勢2値・弱形のみ一致不可・同形異音語保護』つきの厳格な1語同音判定。
# 用途: (1)B-2(1語/短文のratioゲートより先の承認済み同音救済、er006 validation)の安全条件
#       (2)er109(未配線の表記同値層)の語unit判定。既存homophone_arpabet_equivalent()の承認済み挙動は変えない。
import re as _re_strict


def _stress2_tokens(ph: str) -> tuple:
    """ARPAbet文字列 -> 強勢を2値(1=主/副強勢, 0=無強勢)にした音素tuple。"""
    return tuple(_re_strict.sub(r"([A-Z]+)[12]$", r"\g<1>1", t) for t in ph.split())


def _has_stressed_vowel(reading: tuple) -> bool:
    return any(len(t) > 1 and t[-1] == "1" and t[:-1].isalpha() for t in reading)


def representative_strong_reading(word: str):
    """語の代表発音(CMU先頭の強勢読み。2値強勢)。無ければNone。"""
    for v in _phone_variants(word) or []:
        r = _stress2_tokens(v)
        if _has_stressed_vowel(r):
            return r
    return None


def strong_readings(word: str) -> frozenset | None:
    """語の『強勢母音を含む読み』(2値強勢)の集合。弱形のみの読み(are=ER0等)は含めない。
    CMU未登録 または 強勢読みが無い場合はNone(判定不能=安全側)。"""
    vs = _phone_variants(word)
    if not vs:
        return None
    out = frozenset(r for r in (_stress2_tokens(v) for v in vs) if _has_stressed_vowel(r))
    return out or None


def strict_homophone_pair(canonical_word: str, asr_word: str) -> bool | None:
    """P-01/P-02/P-03を満たす1語同音判定(第1引数=canonical=TTSが読むべき語、第2引数=ASR転写語)。
    True : (1)canonicalの強勢読み(2値強勢・弱形のみの読みを除く)が『ただ1つ』で、
           (2)ASR語の代表(先頭)強勢読みがそれと一致する。
           (=canonicalが同形異音語[lead/desert/won/read/our等]なら不可。ASR語の少数派読みでしか一致しない場合
              [our<->are, we're<->were]も不可。弱形のみの一致[are<->or]・強勢差[billow<->below]も不可。
              canonicalが単一読みでASR語が複数読みを持つのは(2)を満たす限り可=綴りの違いだけ)
    False: 両語ともCMUで解決でき、上記を満たさない
    None : 判定不能(未登録/強勢読み無し)。呼出側は同音として扱わない。綴りが同じ場合はTrue。"""
    wa, wb = _normalize_word(canonical_word), _normalize_word(asr_word)
    if not wa or not wb:
        return None
    if wa == wb:
        return True
    rc, ra = strong_readings(wa), strong_readings(wb)
    if rc is None or ra is None:
        return None
    return len(rc) == 1 and representative_strong_reading(wb) in rc
