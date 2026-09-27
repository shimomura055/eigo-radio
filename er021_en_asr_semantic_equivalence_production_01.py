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
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"\bNo\.\s*(?=\d)", "number ", text)
    # 語と語の間のハイフン(twenty-eight/ninety-nine等)は、語を分かつ
    # 空白と同じ扱いにする(production側_convert_cardinal_words()と同型の
    # 対策)。
    text = re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " ", text)
    # マイナス記号(数字の直前、直前の文字が数字でない場合のみ)。
    text = re.sub(r"(?<![\d])-(?=\d)", " minus ", text)
    return text


def _to_fraction(numstr: str) -> Fraction:
    return Fraction(Decimal(numstr.replace(",", "")))


def _mk_number(value: Fraction, currency: str | None = None, percent: bool = False) -> dict:
    return {"kind": "number", "value": value, "currency": currency, "percent": percent}


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
    n = len(words)
    j = i
    while j < n and words[j].lower() in _NUMBER_VOCAB:
        j += 1
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
    if j < n and words[j].lower() in ("am", "pm"):
        meridiem = words[j].lower()
        j += 1
    else:
        return None  # am/pmが無い場合は時刻として確定させない(安全側)
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
            meridiem, consumed = None, 1
            if i + 1 < n and words[i + 1].lower() in ("am", "pm"):
                meridiem = words[i + 1].lower()
                consumed = 2
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
        return a["value"] == b["value"] and a["currency"] == b["currency"] and a["percent"] == b["percent"]
    if a["kind"] == "time":
        return a["value"] == b["value"] and a["meridiem"] == b["meridiem"]
    return False


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
    ラッパー)がこの関数の戻り値からClassificationResultを組み立てる。"""
    if canonical is None or asr is None:
        return None
    try:
        ca = _tier1_atoms(canonical)
        aa = _tier1_atoms(asr)
    except Exception:
        return None  # パース例外は非等価扱い(安全側、best-effort禁止)
    if len(ca) != len(aa):
        return None
    if not any(a["kind"] != "literal" for a in ca):
        return None  # 数値的内容が無い(Tier1の対象外)
    for a, b in zip(ca, aa):
        if not _atoms_equal(a, b):
            return None
    return {"canonical_atoms": atoms_public(ca), "asr_atoms": atoms_public(aa)}


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
