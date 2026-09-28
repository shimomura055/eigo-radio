# ============================================================
# er021_en_asr_semantic_equivalence_production_01.py
# 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Phase A+B)
# ============================================================
# 性質: Production module(ユーザー正式採用済み、APPROVED_FOR_PRODUCTION、
# 2026-09-27)。Trial(er021_en_asr_semantic_equivalence_trial_01.py、無変更
# のまま併存)で検証したTier 1(数値/通貨/%/年/時刻/分数/ローマ数字/略語の
# 値等価)+Tier 3(規則的複数形・固有名詞ASR表記差のcorroboration付き救済)
# のロジックを、実際のProduction呼び出し元(er006_preprod_hardening_01_
# validation.py::classify_asr_matchラッパー、er006_secondary_asr_01.py::
# evaluate_attempt_with_cascade_detail)から呼び出せる形へ昇格したもの。
# Phase C(wanna/gonna等Tier2)は対象外、実装しない。
#
# 循環import回避のための設計方針(重要):
#   このファイルはer006_preprod_hardening_01_validation.py(val)や
#   er006_secondary_asr_01.pyを一切importしない。tokenize済みのtoken列や
#   ProtectedCheckResult由来の値(content_word_diffs等)は、呼び出し側が
#   既に保持している値をそのまま引数で渡す設計にすることで、val側からも
#   このmoduleへ安全にimportできるようにしている(val -> このmodule の
#   一方向のみ、このmodule -> val は存在しない)。role gating判定
#   (resolve_narrative_role/connected_speech_enabled_for)は
#   er020_tts_retry_local_rewrite_01の同一関数を呼び出し元(val側)が
#   遅延importして使う(このmodule自体はrole名の集合[FIVE_ROLES]のみを
#   参照用に持つ、ロジックの重複実装はしない)。
#
# 書き込み範囲: 本ファイル(root)+
# er021_output/en_asr_semantic_equivalence_production_wiring_01/ 配下のみ。

from __future__ import annotations

import difflib
import json
import os
import re
from decimal import Decimal
from fractions import Fraction

# ------------------------------------------------------------
# Role gating(er020_tts_retry_local_rewrite_01.resolve_narrative_role()の
# 戻り値と同じ5値。ロジックそのものはer020側のみが保持するSSOTであり、
# ここでは「どの値が適用対象か」という参照用の集合のみを持つ)。
# ------------------------------------------------------------
FIVE_ROLES_APPLICABLE = frozenset({
    "FULL_STORY", "COMMENT", "PREVIEW", "TOPIC_INTRO", "IN_ONE_LINE",
})

NEW_CLASSIFICATION_LABELS = ("NUMERIC_EQUIVALENCE_MATCH", "SECONDARY_ASR_CORROBORATED_MATCH")

OUT_DIR = "er021_output/en_asr_semantic_equivalence_production_wiring_01"
TELEMETRY_LOG_PATH = f"{OUT_DIR}/telemetry.jsonl"


# ============================================================
# Part 1: Tier 1 数値/通貨/%/年/時刻/分数/ローマ数字/略語 値パーサ
# ============================================================
# 安全設計の核心(Fable最終レビュー準拠、Trial実装からの無変更移植):
# 両側を同一の意味値へ「パース」し、値が完全一致した場合のみ等価とする
# (文字列正規化の拡張ではない)。パース失敗・非対応構文は「等価でない」
# 扱い(best-effort禁止、常に安全側)。
_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
         "eighty": 80, "ninety": 90}
_MULTI_SCALE_WORDS = {"thousand": 1000, "million": 10 ** 6, "billion": 10 ** 9, "trillion": 10 ** 12}
_SCALE_WORDS = {"hundred": 100, **_MULTI_SCALE_WORDS}
_NUMBER_VOCAB = set(_ONES) | set(_TENS) | set(_SCALE_WORDS) | {"and"}

# ローマ数字: 安全のため単独の"I"(代名詞"I"と衝突するため)は意図的に
# 対象から除外する(閉じた集合をII〜Xに限定)。
_ROMAN_SAFE = {"II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正、ユーザー
# 承認2026-09-28): "V"・"X"は英語の一般的な語(ブランド名・型番の末尾等、
# 例:"Model X")としても高頻度に出現するため、_ROMAN_SAFEに含まれていても
# 無条件にローマ数字として数値化しない(単独では締める方向の安全化)。
# 直前の語が閉じたラベル語(Act/Part/Chapter等の番号ラベル文脈)である
# 場合のみローマ数字として扱う。II/III/IV/VI/VII/VIII/IXは通常の英単語と
# 衝突しないため従来通り無条件のまま(このgateの対象外)。
_ROMAN_AMBIGUOUS_SINGLE = {"V", "X"}
_ROMAN_LABEL_CONTEXT_WORDS = {
    "act", "part", "chapter", "section", "phase", "version", "book", "volume",
    "episode", "step", "movie", "season",
}

# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正、
# er006_preprod_hardening_01_validation.py::_MONTHS/_DATE_ORDINAL_REから
# 移設。er006は本moduleを既にimportしている[一方向import]ため、器006側は
# semantic_equivalence._MONTHS/_DATE_ORDINAL_REを参照するだけに変更し、
# 定義自体はこちらのみに置く[複製ではなく共通化・参照化]): 日付文脈
# (月名直後)限定の裸digit序数接尾辞吸収。月名に隣接しない裸digitの序数
# 接尾辞(例:"28th"単独)は対象外のまま(基数/序数の意味差を壊さないため、
# 分類Bで不採用と整理済み)。
_MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august",
           "september", "october", "november", "december")
_DATE_ORDINAL_RE = re.compile(r"\b(" + "|".join(_MONTHS) + r")\s+(\d{1,2})(st|nd|rd|th)\b", re.IGNORECASE)

# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正、
# er006_preprod_hardening_01_validation.py::_ORDINAL_WORDSから移設・
# 共通化。"first"/"second"は副詞的用法[discourse connector・"may first
# run"等]との曖昧さのため意図的に除外する既存方針を維持): 序数語(third等)
# をTier1でも認識できるようにする(基数atomとは"ordinal"フラグで区別し、
# "28 articles"vs"28th articles"のような基数/序数の意味差は壊さない)。
_ORDINAL_WORDS = {
    "third": "3rd", "fourth": "4th", "fifth": "5th",
    "sixth": "6th", "seventh": "7th", "eighth": "8th", "ninth": "9th", "tenth": "10th",
    "eleventh": "11th", "twelfth": "12th", "thirteenth": "13th", "fourteenth": "14th",
    "fifteenth": "15th", "sixteenth": "16th", "seventeenth": "17th", "eighteenth": "18th",
    "nineteenth": "19th", "twentieth": "20th", "thirtieth": "30th",
}
_ORDINAL_WORD_VALUES = {w: int(re.match(r"\d+", s).group()) for w, s in _ORDINAL_WORDS.items()}
# 裸digit+序数接尾辞(13th/28th等)を1トークンとして認識するための正規表現
# (_TOKEN_REの専用alternativeと対で使う)。
_ORDINAL_DIGIT_RE = re.compile(r"(\d[\d,]*)(st|nd|rd|th)")

_CURRENCY_SYMBOLS = {"$": "USD", "£": "GBP", "€": "EUR"}
_CURRENCY_WORDS = {"dollar": "USD", "dollars": "USD", "pound": "GBP", "pounds": "GBP",
                    "euro": "EUR", "euros": "EUR"}

_FRACTION_PHRASES = {
    ("a", "half"): Fraction(1, 2), ("one", "half"): Fraction(1, 2),
    ("a", "third"): Fraction(1, 3), ("one", "third"): Fraction(1, 3),
    ("two", "thirds"): Fraction(2, 3),
    ("a", "quarter"): Fraction(1, 4), ("one", "quarter"): Fraction(1, 4),
    ("three", "quarters"): Fraction(3, 4),
}

_NUMSTR_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")
_FRACTION_DIGIT_RE = re.compile(r"(\d+)/(\d+)")
_TOKEN_RE = re.compile(
    r"[$£€]\d[\d,]*(?:\.\d+)?"
    r"|\d{1,2}:\d{2}"
    r"|\d+/\d+"
    r"|\d[\d,]*(?:\.\d+)?%"
    # EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02: 裸digit+序数接尾辞
    # (13th/28th等)を1トークンとして拾う(下記の桁のみパターンより先に
    # 置くことで、"13th"が"13"+"th"の2トークンへ分裂しないようにする)。
    r"|\d[\d,]*(?:st|nd|rd|th)\b"
    r"|\d[\d,]*(?:\.\d+)?"
    r"|[A-Za-z']+"
    # ER021-SAFETY: 上記いずれにも一致しない文字(上付き指数記号
    # ¹⁶・数式記号×÷等、空白でない1文字)を、黙って消える(=情報が
    # 消失し値が変わって見えてしまう)のではなく、必ず1文字ずつの
    # literal atomとして残す(Trialで実測発見・修正した回帰バグ対策)。
    r"|[^\s]"
)


def _preprocess_raw(text: str) -> str:
    """記号レベルの閉じた対応(&⇔and、No.⇔number、minus⇔-)を、大文字小文字
    情報(ローマ数字判定に必要)を保ったまま適用する。"""
    text = text.replace("’", "'").replace("‘", "'")
    # EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正):
    # 月名直後限定の裸digit序数接尾辞吸収(er006の_DATE_ORDINAL_REと同一
    # スコープ、両側へ対称に適用するため呼び出し側がどちらの表記でも
    # 結果的に同じ形へ揃う。月名に隣接しない裸digitの序数接尾辞は対象外の
    # ままで、"28 articles"vs"28th articles"のような基数/序数の意味差は
    # 壊さない)。
    text = _DATE_ORDINAL_RE.sub(r"\1 \2", text)
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"\bNo\.\s*(?=\d)", "number ", text)
    # 語と語の間のハイフン(twenty-eight/ninety-nine等)は、語を分かつ
    # 空白と同じ扱いにする(production側_convert_cardinal_words()と同型の
    # 対策)。EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術
    # 修正)で「文字-文字」に加え「文字-数字」(COVID-19)・「数字-文字」
    # (15-minute)の組へ拡張する(番号付き固有表現・hyphenated numeric、
    # 新しい数値の意味等価ではなく閉じた表記差の吸収)。文字が直前に
    # 隣接するハイフンは、以降のマイナス記号判定より必ず先に空白化する
    # ことで、"COVID-19"が誤って"COVID minus 19"へならないようにする。
    text = re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z0-9])", " ", text)
    text = re.sub(r"(?<=[0-9])-(?=[A-Za-z])", " ", text)
    # マイナス記号(数字の直前、直前の文字が数字・アルファベットいずれでも
    # ない場合のみ。文字直前のハイフンは上記で既に空白化済みのため対象外)。
    text = re.sub(r"(?<![\dA-Za-z])-(?=\d)", " minus ", text)
    return text


def _to_fraction(numstr: str) -> Fraction:
    return Fraction(Decimal(numstr.replace(",", "")))


def _mk_number(value: Fraction, currency: str | None = None, percent: bool = False,
                ordinal: bool = False) -> dict:
    # ordinal: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02で追加。
    # 序数(3rd/third)か基数(3)かを区別するフラグ(_atoms_equal()で比較する
    # ことで、"28"[基数]と"28th"[序数]の意味差[negative #23]を壊さない)。
    return {"kind": "number", "value": value, "currency": currency, "percent": percent, "ordinal": ordinal}


def _split_into_two_digit_groups(words: list[str]) -> list[int] | None:
    """"nineteen ninety-nine"(年のペア読み)のような、桁を連結する2桁
    グループへ分割できるかを判定する。単独の一桁数字語の連続("one two
    three"のような桁ごとの読み上げ)は1つの数へ合成しない(安全側)。"""
    groups = []
    i, n = 0, len(words)
    while i < n:
        w = words[i]
        if w in _TENS:
            if i + 1 < n and words[i + 1] in _ONES and 1 <= _ONES[words[i + 1]] <= 9:
                groups.append(_TENS[w] + _ONES[words[i + 1]])
                i += 2
            else:
                groups.append(_TENS[w])
                i += 1
        elif w in _ONES:
            v = _ONES[w]
            if v >= 10:
                groups.append(v)
                i += 1
            else:
                if n == 1:
                    groups.append(v)
                    i += 1
                else:
                    return None  # 単独一桁数字語の連続 -> 合成しない(安全側)
        else:
            return None
    return groups


def _words_to_number_scale(words: list[str]) -> int | None:
    total, current, seen = 0, 0, False
    for w in words:
        if w == "and":
            continue
        if w in _ONES:
            current += _ONES[w]
            seen = True
        elif w in _TENS:
            current += _TENS[w]
            seen = True
        elif w == "hundred":
            current = (current if current else 1) * 100
            seen = True
        elif w in _MULTI_SCALE_WORDS:
            scale = _MULTI_SCALE_WORDS[w]
            total += (current if current else 1) * scale
            current = 0
            seen = True
        else:
            return None
    if not seen:
        return None
    return total + current


def _parse_bare_number_run(words: list[str]) -> int | None:
    if any(w in _SCALE_WORDS for w in words):
        return _words_to_number_scale(words)
    groups = _split_into_two_digit_groups([w for w in words if w != "and"])
    if groups is None:
        return None
    if len(groups) == 1:
        return groups[0]
    if len(groups) == 2:
        # 年のペア読み(nineteen ninety-nine=1999、twenty twenty-six=2026等)。
        return groups[0] * 100 + groups[1]
    return None


def _consume_number_word_run(words: list[str], i: int):
    # EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正):
    # 数値語runが前後の"and"を飲み込むparser bugの修正。"and"は数値語run
    # の先頭には来ない(単なる接続詞の"and"が後続の裸digit語1つと誤って
    # 結合されるのを防ぐ)。
    n = len(words)
    if words[i].lower() == "and":
        return None
    j = i
    while j < n and words[j].lower() in _NUMBER_VOCAB:
        j += 1
    # runの末尾の"and"も含めない(直後が数値語で終わらない場合、"and"だけが
    # 取り残されて誤って数値へ合成されるのを防ぐ)。"one hundred and five"
    # のようなscale語を含む正規のケースは_words_to_number_scale()側で
    # "and"を明示的にskipして処理するため、この末尾除去の影響を受けない。
    while j > i and words[j - 1].lower() == "and":
        j -= 1
    integer_words = [w.lower() for w in words[i:j]]
    if not integer_words:
        return None
    int_value = _parse_bare_number_run(integer_words)
    if int_value is None:
        return None
    value = Fraction(int_value)
    k = j
    if k < n and words[k].lower() == "point":
        k2 = k + 1
        frac_digits = []
        while k2 < n and words[k2].lower() in _ONES and _ONES[words[k2].lower()] < 10:
            frac_digits.append(_ONES[words[k2].lower()])
            k2 += 1
        if frac_digits:
            frac_str = "0." + "".join(str(d) for d in frac_digits)
            value = value + Fraction(Decimal(frac_str))
            k = k2
    return value, k


def _try_fraction_phrase(words: list[str], i: int):
    if i + 1 >= len(words):
        return None
    key = (words[i].lower(), words[i + 1].lower())
    if key in _FRACTION_PHRASES:
        return _FRACTION_PHRASES[key], 2
    return None


def _try_minute(words: list[str], j: int):
    """時刻の分部分(2桁グループ)。ちょうど1つの2桁グループとして解釈でき、
    値が0〜59の範囲に収まる場合のみ返す(それ以外はNone、安全側)。"""
    n = len(words)
    for length in (2, 1):
        if j + length <= n:
            candidate = [w.lower() for w in words[j:j + length]]
            if all(w in _ONES or w in _TENS for w in candidate):
                groups = _split_into_two_digit_groups(candidate)
                if groups and len(groups) == 1 and 0 <= groups[0] <= 59:
                    return groups[0], j + length
    return None


def _peek_meridiem(words: list[str], j: int):
    """EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正、
    meridiem略記のatom結合): "am"/"pm"に加え、打点表記"a.m."/"p.m."
    (_TOKEN_REのcatch-all設計により"a"/"."/"m"/"."の4 atomへ分裂した状態)
    も同じmeridiem値として認識する。時刻atom自体の閉じたスコープ(数字の
    直後限定)は変えない。戻り値: (meridiem, consumed_token_count)または
    None。"""
    n = len(words)
    if j < n and words[j].lower() in ("am", "pm"):
        return words[j].lower(), 1
    if (j + 3 < n and words[j].lower() in ("a", "p")
            and words[j + 1] == "." and words[j + 2].lower() == "m" and words[j + 3] == "."):
        return words[j].lower() + "m", 4
    return None


def _try_spoken_time(words: list[str], i: int):
    """"three thirty pm"のような話し言葉の時刻表現。am/pmが直後に続く
    場合のみ時刻として認識する(時刻はh:mm⇔語+am/pmの閉じた対応のみ)。"""
    n = len(words)
    hour_word = words[i].lower()
    if hour_word not in _ONES or not (1 <= _ONES[hour_word] <= 12):
        return None
    hour = _ONES[hour_word]
    j = i + 1
    minute = None
    if (j < n and words[j].lower() == "oh" and j + 1 < n
            and words[j + 1].lower() in _ONES and _ONES[words[j + 1].lower()] < 10):
        minute = _ONES[words[j + 1].lower()]
        j += 2
    else:
        m = _try_minute(words, j)
        if m is not None:
            minute, j = m
    if minute is None:
        return None
    meridiem_info = _peek_meridiem(words, j)
    if meridiem_info is None:
        return None  # am/pmが無い場合は時刻として確定させない(安全側)
    meridiem, mconsumed = meridiem_info
    j += mconsumed
    return {"kind": "time", "value": Fraction(hour * 100 + minute), "meridiem": meridiem}, j


def _apply_suffixes(atom: dict, words: list[str], idx: int) -> int:
    """数値atom生成直後に、続く語がscale語・"percent"・通貨語であれば併合する。"""
    if atom["kind"] != "number":
        return idx
    n = len(words)
    if idx < n and words[idx].lower() in _SCALE_WORDS:
        atom["value"] = atom["value"] * _SCALE_WORDS[words[idx].lower()]
        idx += 1
    if idx < n:
        w = words[idx].lower()
        if w == "percent" and not atom["percent"]:
            atom["percent"] = True
            idx += 1
        # EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正):
        # "per cent"(2語表記、er006のnormalize_numeric()と同じ閉じた
        # 対応)も"percent"と同じ意味atomへ正規化する。
        elif (w == "per" and idx + 1 < n and words[idx + 1].lower() == "cent"
              and not atom["percent"]):
            atom["percent"] = True
            idx += 2
        elif w in _CURRENCY_WORDS and atom["currency"] is None:
            atom["currency"] = _CURRENCY_WORDS[w]
            idx += 1
    return idx


def _tier1_atoms(text: str) -> list[dict]:
    if not text:
        return []
    raw = _preprocess_raw(text)
    words = _TOKEN_RE.findall(raw)
    atoms: list[dict] = []
    i, n = 0, len(words)
    while i < n:
        w = words[i]
        if w and w[0] in _CURRENCY_SYMBOLS and _NUMSTR_RE.fullmatch(w[1:]):
            atoms.append(_mk_number(_to_fraction(w[1:]), currency=_CURRENCY_SYMBOLS[w[0]]))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        m = _TIME_RE.fullmatch(w)
        if m:
            hour, minute = int(m.group(1)), int(m.group(2))
            meridiem_info = _peek_meridiem(words, i + 1)
            if meridiem_info is not None:
                meridiem, mconsumed = meridiem_info
                consumed = 1 + mconsumed
            else:
                meridiem, consumed = None, 1
            atoms.append({"kind": "time", "value": Fraction(hour * 100 + minute), "meridiem": meridiem})
            i += consumed
            continue
        m = _FRACTION_DIGIT_RE.fullmatch(w)
        if m:
            num, den = int(m.group(1)), int(m.group(2))
            if den != 0:
                atoms.append(_mk_number(Fraction(num, den)))
                i += 1
                i = _apply_suffixes(atoms[-1], words, i)
                continue
        if w.endswith("%") and _NUMSTR_RE.fullmatch(w[:-1]):
            atoms.append(_mk_number(_to_fraction(w[:-1]), percent=True))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        # EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02: 裸digit+序数接尾辞
        # (13th/28th等、_TOKEN_REが1トークンとして拾い済み)。基数atomとは
        # ordinal=Trueで区別する(negative #23の基数/序数の意味差は壊さない)。
        m_ord = _ORDINAL_DIGIT_RE.fullmatch(w)
        if m_ord:
            atoms.append(_mk_number(_to_fraction(m_ord.group(1)), ordinal=True))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        if _NUMSTR_RE.fullmatch(w):
            bare = w.replace(",", "")
            if "," not in w and "." not in w and len(bare) >= 7:
                # 7桁以上の生の数字列(電話番号・ID等) -> 値化せず桁完全一致のみ
                atoms.append({"kind": "literal", "word": w})
                i += 1
                continue
            atoms.append(_mk_number(_to_fraction(w)))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        if w in _ROMAN_SAFE:
            # EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(分類A技術修正、
            # 締める方向の安全化): "V"/"X"は直前が閉じたラベル語文脈の場合
            # のみローマ数字として扱う(それ以外はfall throughしてliteral
            # atomとして扱われる、"Model X"のような衝突を防ぐ)。
            roman_allowed = True
            if w in _ROMAN_AMBIGUOUS_SINGLE:
                prev_word = words[i - 1].lower() if i > 0 else ""
                roman_allowed = prev_word in _ROMAN_LABEL_CONTEXT_WORDS
            if roman_allowed:
                atoms.append(_mk_number(Fraction(_ROMAN_SAFE[w])))
                i += 1
                i = _apply_suffixes(atoms[-1], words, i)
                continue
        frac = _try_fraction_phrase(words, i)
        if frac is not None:
            value, consumed = frac
            atoms.append(_mk_number(value))
            i += consumed
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        spoken_time = _try_spoken_time(words, i)
        if spoken_time is not None:
            atom, next_i = spoken_time
            atoms.append(atom)
            i = next_i
            continue
        lw = w.lower()
        # EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02: 序数語(third等、
        # er006の_ORDINAL_WORDSと同じ閉じた集合、first/secondは除外)。
        if lw in _ORDINAL_WORD_VALUES:
            atoms.append(_mk_number(Fraction(_ORDINAL_WORD_VALUES[lw]), ordinal=True))
            i += 1
            i = _apply_suffixes(atoms[-1], words, i)
            continue
        if lw in _NUMBER_VOCAB:
            parsed = _consume_number_word_run(words, i)
            if parsed is not None:
                value, next_i = parsed
                atoms.append(_mk_number(value))
                i = next_i
                i = _apply_suffixes(atoms[-1], words, i)
                continue
        atoms.append({"kind": "literal", "word": lw.strip("'")})
        i += 1
    return atoms


def _atoms_equal(a: dict, b: dict) -> bool:
    if a["kind"] != b["kind"]:
        return False
    if a["kind"] == "literal":
        return a["word"] == b["word"]
    if a["kind"] == "number":
        return (a["value"] == b["value"] and a["currency"] == b["currency"]
                and a["percent"] == b["percent"] and a.get("ordinal", False) == b.get("ordinal", False))
    if a["kind"] == "time":
        return a["value"] == b["value"] and a["meridiem"] == b["meridiem"]
    return False


def _atom_key(atom: dict):
    """SequenceMatcher用のhashableキー。数値/時刻atomは値そのものを
    キーへ含めるため、表記が違っても値が一致するatomは最初から'equal'
    opcodeとして扱われる(diff-anchored化後も既存のTier1値等価判定基準
    そのものは一切変更しない)。"""
    if atom["kind"] == "literal":
        return ("literal", atom["word"])
    if atom["kind"] == "number":
        return ("number", atom["value"], atom["currency"], atom["percent"], atom.get("ordinal", False))
    if atom["kind"] == "time":
        return ("time", atom["value"], atom["meridiem"])
    return ("unknown", atom.get("word"))


# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(strict版Tier1合成規則、
# ユーザー承認2026-09-28): diff-anchored比較で局所的に許容できる差分op数・
# 対象atom比率の上限(定数化、防御的安全装置。既存の閉じたalnum完全一致
# 判定に加えた多重防御であり、この上限自体が新しいfalse acceptの余地を
# 広げるものではない)。
_TIER1_MAX_ABSORBED_PUNCT_OPS = 3
_TIER1_MAX_ABSORBED_PUNCT_ATOM_RATIO = 0.2


def _closed_punctuation_diff_ok(canon_slice: list[dict], asr_slice: list[dict]) -> bool:
    """strict版Tier1合成規則(ユーザー承認2026-09-28)。diff-anchored
    比較で非equalと判定された1つのop区間について、局所的に許容してよい
    「punctuation由来の差分」かどうかを判定する。1つでも満たさなければ
    False(best-effort禁止、opごと・全体非等価)。

    閉じた規則(すべて満たす場合のみTrue):
    (1) 差分区間の両側atomはliteralのみ(数字・時刻atomの差は絶対に
        吸収しない。ここでNoneを返す=このopは通常のTier1値比較[既存の
        _atoms_equal]に委ねられ、値が違えば非等価のまま)。
    (2) 両側の英数字内容(re.sub(r"[^a-z0-9]","",word)を連結したもの)が
        完全一致すること。literal atomの語は既に小文字化・前後アポスト
        ロフィ除去済みのため、この一致は大文字小文字や語順の並べ替えでは
        なく、句読点・空白によるtokenization差のみによって成立する
        (このopが既に'equal'でない=どちらかの側にatomが余る/種類が違う
        ことは確定しているため、alnum内容が一致するならその差は必ず
        punctuation由来である。単語脱落・否定語脱落・数量差・固有名詞差は
        alnum内容そのものが変わるため、この等式を満たせない)。
    (3) 両側とも少なくとも1 atom以上を含むこと(replaceのみを対象とし、
        insert/delete[片側が完全に空]は対象外とする)。理由: ハイフン付き
        数値・alphanumeric entity(15-minute/COVID-19等)は_preprocess_raw()
        側の前処理で既に空白化されるため、この関数へ到達する時点では
        atom差として現れない。逆に、この関数がinsert/deleteまで許容すると
        "12-34"(1 atomの記号)vs"12 34"(記号なし)のような、区切り記号が
        数値の意味的な単位[2つの独立した数/1つのコード全体]を左右し得る
        ケースまで安全側の判定を緩めてしまう回帰を実測で確認したため、
        意図的に対象外とする(既存の安全性を拡張しない)。
    """
    if not canon_slice or not asr_slice:
        return False
    if any(a["kind"] != "literal" for a in canon_slice) or any(a["kind"] != "literal" for a in asr_slice):
        return False
    canon_alnum = "".join(re.sub(r"[^a-z0-9]", "", a["word"]) for a in canon_slice)
    asr_alnum = "".join(re.sub(r"[^a-z0-9]", "", a["word"]) for a in asr_slice)
    ok = canon_alnum == asr_alnum
    # 安全装置(assertレベル): このopがPASSする範囲は「英数字内容完全一致」
    # に限定されることを実行時にも固定する(diff-anchored化後の実装バグ
    # 混入を防ぐ防御的アサーション、best-effort禁止の原則を機械的に保証)。
    if ok:
        assert canon_alnum == asr_alnum
    return ok


def atoms_public(atoms: list[dict]) -> list[dict]:
    out = []
    for a in atoms:
        pub = dict(a)
        if isinstance(pub.get("value"), Fraction):
            pub["value"] = str(pub["value"])
            pub["value_float"] = float(a["value"])
        out.append(pub)
    return out


def tier1_numeric_equivalence(canonical: str, asr: str) -> dict | None:
    """Tier 1 early-exit。両側の値パース列が完全一致した場合のみdictを
    返す(等価でなければNone、呼び出し側は既存の分類本体へフォールバック
    する)。このmoduleはval(er006_preprod_hardening_01_validation)を
    importしない(循環import回避)ため、呼び出し側(classify_asr_match
    ラッパー)がこの関数の戻り値からClassificationResultを組み立てる。

    EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(strict版Tier1合成
    規則、ユーザー承認2026-09-28): 従来はセグメント全体のatom列を
    「位置固定zip」で比較するall-or-nothing判定だったため、無関係な
    1箇所のpunctuation由来の表記差(打点略語のatom分裂・meridiem略記等)
    が、同一segment内の他の正しい数値等価判定までまとめて握りつぶして
    いた(Hormuz"Act One"⇔"Act 1"実例、design_en_asr_orthographic_
    equivalence_coverage_02.md §1参照)。この関数は(a)まず従来通りの
    全体一致を試み(既存の合格経路は無変更)、(b)一致しない場合のみ
    diff-anchored比較(SequenceMatcher(autojunk=False))へ進み、非equalな
    各opが_closed_punctuation_diff_ok()の閉じた規則に該当する場合のみ
    その差分を局所的に許容する。1つのopでもこの規則に該当しなければ
    即座に全体を非等価とする(best-effort禁止、既存のfalse accept 0の
    安全性は一切拡張しない)。"""
    if canonical is None or asr is None:
        return None
    try:
        ca = _tier1_atoms(canonical)
        aa = _tier1_atoms(asr)
    except Exception:
        return None  # パース例外は非等価扱い(安全側、best-effort禁止)
    if not any(a["kind"] != "literal" for a in ca):
        return None  # 数値的内容が無い(Tier1の対象外)

    if len(ca) == len(aa) and all(_atoms_equal(a, b) for a, b in zip(ca, aa)):
        # 既存の全体一致経路(従来のall-or-nothing判定と完全に同じ挙動、
        # 無回帰)。
        return {"canonical_atoms": atoms_public(ca), "asr_atoms": atoms_public(aa),
                "diff_anchored": False, "absorbed_ops": 0}

    ca_keys = [_atom_key(a) for a in ca]
    aa_keys = [_atom_key(a) for a in aa]
    sm = difflib.SequenceMatcher(None, ca_keys, aa_keys, autojunk=False)
    absorbed_ops = 0
    absorbed_atom_total = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if not _closed_punctuation_diff_ok(ca[i1:i2], aa[j1:j2]):
            return None  # best-effort禁止、1opでも該当しなければ全体非等価
        absorbed_ops += 1
        absorbed_atom_total += (i2 - i1) + (j2 - j1)
    if absorbed_ops == 0:
        return None  # 理論上到達しない(全equalならlen一致のはず)が安全側
    if absorbed_ops > _TIER1_MAX_ABSORBED_PUNCT_OPS:
        return None
    total_atoms = max(len(ca), len(aa), 1)
    if absorbed_atom_total / total_atoms > _TIER1_MAX_ABSORBED_PUNCT_ATOM_RATIO:
        return None
    return {"canonical_atoms": atoms_public(ca), "asr_atoms": atoms_public(aa),
            "diff_anchored": True, "absorbed_ops": absorbed_ops}


# ============================================================
# Part 2: Tier 3 (sub_reason判定 + corroboration救済) — 純粋関数のみ。
# tokenize済みのtoken列・content_word_diffs等は呼び出し側(val.tokenize
# 等を既にimport済みのProduction module)がその場で渡す。
# ============================================================
def singularize_simple(word: str) -> str | None:
    """`_is_benign_plural_pair`相当(er006本体、L514-522の同型実装。
    Production本体[protected_check]は変更しないため、observability用に
    このmodule内で独立に再実装する)。"""
    if len(word) > 4 and word.endswith("es") and word[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return word[:-2]
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return None


def is_benign_plural_pair(a: str, b: str) -> bool:
    if a == b:
        return True
    return singularize_simple(a) == b or singularize_simple(b) == a


def locate_single_token_diff(canon_tokens: list[str], asr_tokens: list[str]) -> dict | None:
    """非等価opcodeがちょうど1件、かつ1トークン対1トークンのreplaceの
    場合のみ位置情報を返す(それ以外はNone、救済対象を狭く限定する)。
    tokenize済みのtoken列を直接受け取る(このmodule自体はtokenize
    ロジックを持たない、valのtokenize()の重複実装を避けるため)。"""
    sm = difflib.SequenceMatcher(None, canon_tokens, asr_tokens, autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    if len(ops) != 1:
        return None
    tag, i1, i2, j1, j2 = ops[0]
    if tag != "replace" or i2 - i1 != 1 or j2 - j1 != 1:
        return None
    return {"index": i1, "canonical_word": canon_tokens[i1], "asr_word": asr_tokens[j1]}


def corroboration_supports(canon_tokens: list[str], idx: int, other_tokens: list[str] | None) -> bool | None:
    """OPEN-122の`_word_at_diff_matches_canonical`相当(同型実装、
    position-basedでcanonical語をother_tokens[Secondary/Local ASRを
    tokenize済みのtoken列]が支持しているかを判定する)。"""
    if not other_tokens:
        return None
    if idx >= len(other_tokens) or idx >= len(canon_tokens):
        return None
    return other_tokens[idx] == canon_tokens[idx]


def determine_sub_reason(*, classification: str, should_pass: bool,
                          content_word_diffs: list[dict], number_mismatches: list,
                          negation_mismatches: list,
                          canon_tokens: list[str], asr_tokens: list[str]) -> tuple[str, dict | None]:
    """ASR_VALIDATION_UNCERTAIN/TRUE_CONTENT_MISMATCHの内訳をobservability
    用に細分化する(既存ラベル自体は変更しない、新規フィールドのみ)。
    ClassificationResult自体は受け取らず、必要な値だけを個別に受け取る
    (このmoduleがvalをimportしなくて済むようにするための設計)。"""
    if should_pass:
        return "none", None
    if classification == "TTS_FAILURE":
        return "tts_failure", None
    if classification == "TRUE_CONTENT_MISMATCH":
        if number_mismatches:
            return "protected_number", None
        if negation_mismatches:
            return "protected_negation", None
        return "content_word", None
    if classification == "ASR_VALIDATION_UNCERTAIN":
        diffs = content_word_diffs
        if diffs and all(d["entity_like"] for d in diffs):
            loc = locate_single_token_diff(canon_tokens, asr_tokens)
            return "entity_only", loc
        if diffs and all(d["homophone_candidate"] and not d["entity_like"] for d in diffs):
            return "homophone_only", None
        if not diffs:
            loc = locate_single_token_diff(canon_tokens, asr_tokens)
            if loc and is_benign_plural_pair(loc["canonical_word"], loc["asr_word"]):
                return "plural_only", loc
            return "low_ratio", None
    return "content_word", None


# ============================================================
# Part 3: Telemetry(NG時のcanonical/ASR/diff_span/sub_reason観測ログ、
# Phase Aの観測性改善。挙動変更なし)
# ============================================================
def append_telemetry_log(record: dict, path: str = TELEMETRY_LOG_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
