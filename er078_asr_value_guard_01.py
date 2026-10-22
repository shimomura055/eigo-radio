# ============================================================
# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_02b
# 値ガード(数値と単位の比較)。原稿側文と転写側文から「値atom」を位置順に抽出し、位置対応させて
# 5値 {NO_VALUES, EQUAL, DIFF, AMBIGUOUS, UNKNOWN} を返す唯一の数値比較実装。
#
# 状態: 作業branch feat/auw-unified-asr-01 上の新規moduleのみ。Production配線なし(委任_03/04)。
#       既存Production関数(er006_*/er007_*/runner群)は一切変更しない(importして使うだけ)。
#
# 意味論の正本: er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md §1
#   NO_VALUES : 両側とも値atomなし
#   EQUAL     : 全atomが値+単位で一致(表層違い可)、または表層同一
#   DIFF      : (a) 対応atomの値/単位が違う (b) 片側atomに対応する相手側spanに数字/数詞/かな数詞が無い(脱落/挿入)
#   AMBIGUOUS : 位置単位で表層が違い、値か普通語か確定できない(十分=10分/充分、for=4)
#   UNKNOWN   : 構文解析不能/片側のみ値化できた/補正(下記)。既存protected_check・読み一致へ委譲(新規に厳格化も緩和もしない)
#   集約優先順位 DIFF > UNKNOWN > AMBIGUOUS > EQUAL > NO_VALUES
# Fable補正(委任文): EN "one" の脱落/挿入は DIFF(b) ではなく UNKNOWN。"one"が数詞として相手側の別の数詞と対応する場合のみ DIFF(a)。
#
# 再利用元(コピペ重複を避ける方針の実装):
#   EN : er021_en_asr_semantic_equivalence_production_01._tier1_atoms / _atom_key (Tier1 atom抽出。number/time atomのみ使用。
#        percent/%/通貨/序数/英数詞/小数/分数/時刻はTier1が既に吸収済み)。normalize_numericは本module内では
#        再実装せず、Tier1が持つ同等の閉じた正規化に委ねる(Tier1はnormalize_numericと同じ契約を持つ)。
#   JA : er011_ja_asr_variant_layer_01.kanji_numeral_run_to_int (漢数字位取り変換)を関数importで再利用。
#        er066_ja_asr_orthographic_equivalence_01_trial の Stage 1 (find_spans/_to_value/COUNTERS/AMBIGUOUS_RE/is_irregular_sig) は
#        「Production→Trial import禁止」(DESIGN_01 §5-4、er066ヘッダ)のため移設(拡張込み)。Trialファイルは無変更。
#        移設分の一致はtestでer066をimportして突合(parity test。test側のみがTrialをimport)。
#   否定ガード(negation_diff)は本moduleでは扱わない(unified_judge側がer006 _NEGATION_WORDS/er003 safety._has_negation_ja を使用)。
# ============================================================
from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass, field
from fractions import Fraction
from decimal import Decimal, InvalidOperation

import er011_ja_asr_variant_layer_01 as _variant
import er021_en_asr_semantic_equivalence_production_01 as _tier1

NO_VALUES = "NO_VALUES"
EQUAL = "EQUAL"
DIFF = "DIFF"
AMBIGUOUS = "AMBIGUOUS"
UNKNOWN = "UNKNOWN"
KINDS = (NO_VALUES, EQUAL, DIFF, AMBIGUOUS, UNKNOWN)
_PRIORITY = {DIFF: 4, UNKNOWN: 3, AMBIGUOUS: 2, EQUAL: 1, NO_VALUES: 0}

WARN_IRREGULAR_READING = "JA_NUMERIC_IRREGULAR_READING"


@dataclass(frozen=True)
class PairResult:
    src: str | None
    hyp: str | None
    verdict: str
    reason: str


@dataclass(frozen=True)
class ValueGuardResult:
    kind: str
    pairs: tuple = ()
    reasons: tuple = ()
    warnings: tuple = ()  # 値は同じだが不規則読みを含む等(PASS系でも試聴対象)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "pairs": [{"src": p.src, "hyp": p.hyp, "verdict": p.verdict, "reason": p.reason} for p in self.pairs],
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
        }


def aggregate(verdicts) -> str:
    verdicts = list(verdicts)
    if not verdicts:
        return NO_VALUES
    return max(verdicts, key=lambda v: _PRIORITY[v])


# ============================================================
# 共通atom
# ============================================================
@dataclass
class Atom:
    surface: str
    kind: str                     # num / frac / approx / amb / unparsed / time(EN)
    value: object = None          # Fraction | str | None
    unit: str = ""                # JA: counter id / EN: 単位語(singular)や通貨等
    start: int = 0
    end: int = 0
    alt: tuple | None = None      # amb: (value, unit) 読み候補
    soft_one: bool = False        # EN: 代名詞/冠詞的用法がありうる"one"
    extra: tuple = ()             # EN: (percent, currency, ordinal, meridiem) 等

    def key(self):
        if self.kind in ("amb", "unparsed"):
            return (self.kind, self.surface)
        return (self.kind, self.value, self.unit, self.extra)

    def desc(self) -> str:
        return self.surface


# ============================================================
# JA
# ============================================================
# --- 移設元: er066_ja_asr_orthographic_equivalence_01_trial.py (COUNTERS, L29-37。拡張: 割/円等は元から、"割"を追加) ---
COUNTERS = {
    "day_span": ["日間"], "day": ["日"], "person": ["人"],
    "hour_span": ["時間"], "hour": ["時"], "minute": ["分"], "second": ["秒"],
    "month": ["月"], "month_span": ["か月", "ヶ月", "ヵ月", "カ月", "ケ月"],
    "year_span": ["年間"], "year": ["年"], "age": ["歳", "才"],
    "kai": ["回"], "ken": ["件"], "tsu": ["つ"], "haku": ["泊"], "week": ["週間", "週"],
    "yen": ["円"], "percent": ["%", "パーセント"], "ko": ["個"], "hon": ["本"],
    "gen": ["代"], "floor": ["階"], "ban": ["番"], "go": ["号"], "mai": ["枚"], "dai": ["台"], "bai": ["倍"], "do": ["度"],
    "km": ["キロ", "km"],
    "wari": ["割"],  # 本module拡張(割合)
}
_SURF2ID = {s: cid for cid, ss in COUNTERS.items() for s in ss}
_COUNTER_RE = "|".join(re.escape(s) for s in sorted(_SURF2ID, key=len, reverse=True))

_KD = "〇零一二三四五六七八九十百千万億兆"
_NUMRUN = r"(?:\d[\d,]*(?:\.\d+)?[万億兆千百]?(?:\d[\d,]*)?|[" + _KD + r"]+)"
_SPAN_RE = re.compile(r"(?<![A-Za-z\d,.])(" + _NUMRUN + r")(" + _COUNTER_RE + r")")
_BARE_RE = re.compile(r"(?<![A-Za-z\d,.])\d[\d,]*(?:\.\d+)?(?![A-Za-z\d])")
_APPROX_RE = re.compile(r"(十数|数十|数百|数千|数万|何十|何百|何千|何万|数|何|幾|両)(" + _COUNTER_RE + r")")

# 分数「N分のM」(M/N)
_FRAC_RE = re.compile(r"(?<![A-Za-z\d,.])(" + _NUMRUN + r")分の(" + _NUMRUN + r")")

# 曖昧表層(er066 AMBIGUOUS_RE を移設): 十分/三日月/一時/一月/一分/N分の厘割
_AMB_RE = re.compile(
    r"(?<![二三四五六七八九〇])十分(?:間|後|前|ほど|ぐらい|くらい|程度|おき|ごと)?"
    r"|三日月"
    r"|(?<![二三四五六七八九〇十百千万])一時(?!間)"
    r"|(?<![二三四五六七八九〇十百千万])一月"
    r"|(?<![二三四五六七八九〇十百千万])一分(?!間)"
    r"|[\d〇一二三四五六七八九十百千万]分(?:厘|割)")
# 「十分」を時間(10分)と確定する閉集合マーカー(DESIGN_01 §5-2)。「十分な/に/だ/で」「以上/以内」は含めない=機械的同値化をしない。
JUUBUN_TIME_MARKERS = ("十分間", "十分後", "十分前", "十分ほど", "十分ぐらい", "十分くらい", "十分程度", "十分おき", "十分ごと")
_AMB_ALT = {"十分": (Fraction(10), "minute"), "一時": (Fraction(1), "hour"), "一月": (Fraction(1), "month"),
            "一分": (Fraction(1), "minute")}

# 同読み数詞変種辞書(かな数詞。読みは er066 _DAY/_TSU/特殊読み と一致することをtestで突合)
# (value, counter_id, ambiguous_word)。「なのか」「ようか」「とお」は一般語(何なのか/しようか/通)と衝突するため辞書に入れず、
# 脱落判定の「数詞が相手側にある」確認(WEAK_KANA_NUMERALS)にのみ使う。
KANA_NUMERALS = {
    "ひとり": (1, "person", False), "ふたり": (2, "person", False),
    "ひとつ": (1, "tsu", False), "ふたつ": (2, "tsu", False), "みっつ": (3, "tsu", False), "よっつ": (4, "tsu", False),
    "いつつ": (5, "tsu", False), "むっつ": (6, "tsu", False), "ななつ": (7, "tsu", False), "やっつ": (8, "tsu", False),
    "ここのつ": (9, "tsu", False),
    "はたち": (20, "age", False),
    "ついたち": (1, "day", False), "ふつか": (2, "day", False), "みっか": (3, "day", False), "よっか": (4, "day", False),
    "むいか": (6, "day", False), "ここのか": (9, "day", False), "とおか": (10, "day", False), "はつか": (20, "day", False),
    "いつか": (5, "day", True),  # 「いつか(someday)」と衝突 -> 曖昧語atom扱い
}
WEAK_KANA_NUMERALS = ("なのか", "ようか", "とお")
_KANA_RE = re.compile("|".join(sorted((re.escape(k) for k in KANA_NUMERALS), key=len, reverse=True)))

_KBLOCK = r"(?:[一二三四五六七八九]?千)?(?:[一二三四五六七八九]?百)?(?:[一二三四五六七八九]?十)?[一二三四五六七八九]?"
_KGRAMMAR = re.compile(r"^(?=.)(?:(?:" + _KBLOCK + r")万)?(?:" + _KBLOCK + r")$")
_KDIGIT_ONLY = re.compile(r"^[〇零一二三四五六七八九]+$")
_KD_VAL = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_BIG = {"万": 10000, "億": 10 ** 8, "兆": 10 ** 12, "千": 1000, "百": 100}
_ARABIC_RE = re.compile(r"^\d[\d,]*(?:\.\d+)?$")


def _arabic_to_fraction(s: str):
    if "," in s and not re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", s):
        return None
    try:
        return Fraction(Decimal(s.replace(",", "")))
    except InvalidOperation:
        return None


def parse_ja_number(run: str):
    """数値run(算用/漢数字/混在)をFractionへ。解釈不能はNone(fail-safe=atomはunparsed→UNKNOWN)。
    移設元 er066._to_value(漢数字は厳格文法のみ。位取り〇は本moduleで追加)+混在('1万2000')対応。"""
    if _ARABIC_RE.match(run):
        return _arabic_to_fraction(run)
    m = re.fullmatch(r"(\d[\d,]*(?:\.\d+)?)([万億兆千百])", run)
    if m:
        base = _arabic_to_fraction(m.group(1))
        return None if base is None else base * _BIG[m.group(2)]
    m = re.fullmatch(r"(\d[\d,]*(?:\.\d+)?)([万億兆])(\d[\d,]*)", run)
    if m:
        base, tail = _arabic_to_fraction(m.group(1)), _arabic_to_fraction(m.group(3))
        if base is None or tail is None or tail >= _BIG[m.group(2)] or "." in m.group(3):
            return None
        return base * _BIG[m.group(2)] + tail
    if re.search(r"\d", run):
        return None
    # 純漢数字
    if run in ("〇", "零"):
        return None
    if _KDIGIT_ONLY.match(run) and len(run) >= 2 and run[0] not in "〇零" and any(c in "〇零" for c in run):
        return Fraction(int("".join(str(_KD_VAL[c]) for c in run)))  # 位取り表記: 二〇二六 -> 2026
    # 「一二」等(〇を含まない桁並び)は下の厳格文法で弾かれてNone(救済しない)
    if any(c in run for c in "億兆") or not _KGRAMMAR.fullmatch(run) or run.startswith("万"):
        return None
    v = _variant.kanji_numeral_run_to_int(run)
    return None if (v is None or v <= 0) else Fraction(v)


# 移設元: er066.is_irregular_sig と _DAY の閉集合
_IRREG_DAYS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 20, 24}


def is_irregular_sig(value, counter: str) -> bool:
    """不規則読み(音読みの素直な連結と異なる)を持つ署名か。移設元 er066.is_irregular_sig(parity testで突合)。"""
    if value is None or Fraction(value).denominator != 1:
        return False
    n = int(value)
    if counter in ("day", "day_span"):
        return n in _IRREG_DAYS or n % 10 in (4, 7, 9)
    if counter == "person":
        return n in (1, 2) or n % 10 == 4
    if counter == "age":
        return n == 20
    if counter == "tsu":
        return True
    if counter in ("month", "hour"):
        return n % 10 in (4, 7, 9)
    return False


def extract_atoms_ja(text: str) -> list:
    t = unicodedata.normalize("NFKC", text or "")
    taken = [False] * len(t)
    atoms: list[Atom] = []

    def free(s, e):
        return not any(taken[s:e])

    def take(s, e):
        for i in range(s, e):
            taken[i] = True

    # 1) 曖昧表層(十分...)。閉集合マーカーが付けば時間と確定(num化)
    for m in _AMB_RE.finditer(t):
        s, e = m.span()
        surf = m.group(0)
        if not free(s, e):
            continue
        if surf in JUUBUN_TIME_MARKERS:
            # 時間確定: 「十分」部分のみをnum atom(10,minute)へ。マーカー後続部は普通語として残す
            atoms.append(Atom("十分", "num", Fraction(10), "minute", s, s + 2))
            take(s, s + 2)
            continue
        base = "十分" if surf.startswith("十分") else surf[:2]
        atoms.append(Atom(surf, "amb", None, "", s, e, alt=_AMB_ALT.get(base)))
        take(s, e)
    # 2) 分数
    for m in _FRAC_RE.finditer(t):
        s, e = m.span()
        if not free(s, e):
            continue
        den, num = parse_ja_number(m.group(1)), parse_ja_number(m.group(2))
        if den is None or num is None or den == 0:
            atoms.append(Atom(m.group(0), "unparsed", None, "", s, e))
        else:
            atoms.append(Atom(m.group(0), "frac", num / den, "", s, e))
        take(s, e)
    # 3) 概数(数十人/十数人...)
    for m in _APPROX_RE.finditer(t):
        s, e = m.span()
        if not free(s, e):
            continue
        atoms.append(Atom(m.group(0), "approx", m.group(1), _SURF2ID[m.group(2)], s, e))
        take(s, e)
    # 4) 数値+助数詞
    for m in _SPAN_RE.finditer(t):
        s, e = m.span()
        if not free(s, e):
            continue
        val = parse_ja_number(m.group(1))
        unit = _SURF2ID[m.group(2)]
        if val is None:
            atoms.append(Atom(m.group(0), "unparsed", None, unit, s, e))
        else:
            atoms.append(Atom(m.group(0), "num", val, unit, s, e))
        take(s, e)
    # 5) かな数詞
    for m in _KANA_RE.finditer(t):
        s, e = m.span()
        if not free(s, e):
            continue
        v, unit, amb = KANA_NUMERALS[m.group(0)]
        if amb:
            atoms.append(Atom(m.group(0), "amb", None, "", s, e, alt=(Fraction(v), unit)))
        else:
            atoms.append(Atom(m.group(0), "num", Fraction(v), unit, s, e))
        take(s, e)
    # 6) 助数詞なしの算用数字(単位 '')
    for m in _BARE_RE.finditer(t):
        s, e = m.span()
        if not free(s, e):
            continue
        val = _arabic_to_fraction(m.group(0))
        atoms.append(Atom(m.group(0), "unparsed" if val is None else "num", val, "", s, e))
        take(s, e)
    atoms.sort(key=lambda a: a.start)
    return atoms


def _region_has_numeral_ja(text: str) -> bool:
    return bool(re.search(r"[0-9〇零一二三四五六七八九十百千万億兆]", text)) or any(w in text for w in WEAK_KANA_NUMERALS) \
        or bool(_KANA_RE.search(text))


# ============================================================
# EN
# ============================================================
# 数詞と同音で、ASRが語/数字を取り違えうる閉集合のみ(for=four, to/too=two, won=one, ate=eight)。
_EN_HOMOPHONE_WORDS = {"for", "fore", "to", "too", "tu", "won", "ate"}
_EN_UNIT_WORDS = {"hour", "minute", "second", "day", "week", "month", "year", "people", "person", "dollar", "euro", "pound",
                  "yen", "kilometer", "kilometre", "km", "mile", "kg", "kilogram", "meter", "metre", "gram", "percent"}


def _en_unit(word: str):
    w = word.lower().strip("'")
    if w in _EN_UNIT_WORDS:
        return w
    if w.endswith("s") and w[:-1] in _EN_UNIT_WORDS:
        return w[:-1]
    if w == "people":
        return "people"
    return None


def extract_atoms_en(text: str) -> list:
    """Tier1 atom(number/time/literal)から値atomを作る。literalは単位語判定とalign用に別途保持(_en_sequence)。"""
    return [a for a in _en_sequence(text) if a.kind in ("num", "time")]


def _en_atom_text(text: str) -> str:
    """B-1/B-3(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02、既存承認仕様の不具合修正)。
    値atomを作る前に、分類側(val.normalize_numeric)が既に同値と扱っている2つの表記差を同じ関数で揃える:
      B-1 複合序数 `twenty first`/`sixty eighth` -> `21st`/`68th` (valの単一関数 _convert_compound_ordinal_words を再利用。再実装しない。
          未対応だとatomが20+literal`first`に分裂し、`21st`との値DIFFで最終ゲートがPASS済みの分類を再否定していた)
      B-3 数字と%の間の空白 `60 %` -> `60%` (`60 percent`/`60%`と同じatom形へ)
    値が異なるもの(twenty first と 22nd 等)は従来どおりDIFF。"""
    t = text or ""
    import er006_preprod_hardening_01_validation as _val   # 遅延import(循環回避。純関数のみ使用)
    t = _val._convert_compound_ordinal_words(t)
    return re.sub(r"(?<=\d) +%", "%", t)


def _en_sequence(text: str) -> list:
    raw = _tier1._tier1_atoms(_en_atom_text(text))
    has_one_word = bool(re.search(r"\bone\b", text or "", re.I))
    seq: list[Atom] = []
    for i, a in enumerate(raw):
        k = a["kind"]
        if k == "number":
            val = a["value"]
            extra = (bool(a.get("percent")), a.get("currency"), bool(a.get("ordinal")))
            unit = ""
            if i + 1 < len(raw) and raw[i + 1]["kind"] == "literal":
                unit = _en_unit(raw[i + 1]["word"]) or ""
            soft = (val == 1 and has_one_word and not extra[0] and extra[1] is None and not extra[2])
            seq.append(Atom(str(val), "num", val, unit, extra=extra, soft_one=soft))
        elif k == "time":
            seq.append(Atom(str(a["value"]), "time", a["value"], "", extra=(a.get("meridiem"),)))
        else:
            seq.append(Atom(a.get("word", ""), "literal", None, ""))
    return seq


# ============================================================
# 共通: 比較
# ============================================================
def _compare_pair(a: Atom, b: Atom, lang: str):
    """対応するatom 2つの判定。(verdict, reason, warn_flag)"""
    if a.kind == b.kind and a.key() == b.key():
        # 値+単位が同一。表層が違い、不規則読みを含むならwarning
        warn = False
        if lang == "ja" and a.kind == "num" and a.surface != b.surface and is_irregular_sig(a.value, a.unit):
            warn = True
        if lang == "en" and a.kind == "num" and a.unit != b.unit:
            pass
        return EQUAL, "same_value_unit" if a.surface != b.surface else "same_surface", warn
    # --- 曖昧語atom ---
    if a.kind == "amb" or b.kind == "amb":
        amb, other = (a, b) if a.kind == "amb" else (b, a)
        if other.kind == "num" and amb.alt is not None:
            if (other.value, other.unit) == amb.alt:
                return AMBIGUOUS, "ambiguous_surface_same_alt_value", False
            return DIFF, "ambiguous_alt_value_differs", False
        return AMBIGUOUS, "ambiguous_surface", False
    if a.kind == "unparsed" or b.kind == "unparsed":
        return UNKNOWN, "unparsed_numeric_span", False
    if a.kind != b.kind:
        if {a.kind, b.kind} == {"num", "approx"} or {a.kind, b.kind} == {"approx", "frac"}:
            return DIFF, "approx_vs_exact", False
        return UNKNOWN, f"kind_mismatch:{a.kind}/{b.kind}", False
    if a.kind == "approx":
        return DIFF, "approx_differs", False
    if a.kind == "frac":
        return DIFF, "fraction_value_differs", False
    if a.kind in ("num", "time"):
        if lang == "en" and (a.soft_one or b.soft_one) and a.value == b.value:
            pass  # 値が同じ(1==1)で単位/形のみ違う -> 下で処理
        if a.value != b.value:
            return DIFF, "value_differs", False
        # 値は同じ。形(percent/通貨/序数/meridiem)や単位が違う
        if a.extra != b.extra:
            return DIFF, "form_differs(percent/currency/ordinal/meridiem)", False
        if a.unit != b.unit:
            if a.unit == "" or b.unit == "":
                return UNKNOWN, "unit_present_on_one_side_only", False
            return DIFF, "unit_differs", False
        return EQUAL, "same_value_unit", False
    return UNKNOWN, "unhandled", False


def _drop_verdict_ja(atom: Atom, region_text: str, side: str):
    if _region_has_numeral_ja(region_text):
        return UNKNOWN, f"{side}_drop_but_partner_region_has_numeral_like_text"
    if atom.kind == "amb":
        return AMBIGUOUS, f"{side}_ambiguous_surface_without_counterpart"
    if atom.kind == "unparsed":
        return UNKNOWN, f"{side}_unparsed_without_counterpart"
    return DIFF, f"{side}_drop(b)"


def _region(atoms: list, text: str, idx_before: int) -> str:
    s = atoms[idx_before - 1].end if idx_before > 0 else 0
    e = atoms[idx_before].start if idx_before < len(atoms) else len(text)
    return text[s:e] if e >= s else ""


def _guard_ja(src: str, hyp: str) -> ValueGuardResult:
    st = unicodedata.normalize("NFKC", src or "")
    ht = unicodedata.normalize("NFKC", hyp or "")
    A, B = extract_atoms_ja(src), extract_atoms_ja(hyp)
    if not A and not B:
        return ValueGuardResult(NO_VALUES)
    sm = difflib.SequenceMatcher(None, [a.key() for a in A], [b.key() for b in B], autojunk=False)
    pairs: list[PairResult] = []
    warns: list[str] = []

    def do_pair(a, b):
        v, r, w = _compare_pair(a, b, "ja")
        pairs.append(PairResult(a.surface, b.surface, v, r))
        if w and WARN_IRREGULAR_READING not in warns:
            warns.append(WARN_IRREGULAR_READING)

    def drop_src(a, j_idx):
        v, r = _drop_verdict_ja(a, _region(B, ht, j_idx), "src")
        pairs.append(PairResult(a.surface, None, v, r))

    def drop_hyp(b, i_idx):
        v, r = _drop_verdict_ja(b, _region(A, st, i_idx), "hyp")
        pairs.append(PairResult(None, b.surface, v, r))

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for a, b in zip(A[i1:i2], B[j1:j2]):
                do_pair(a, b)
        elif op == "delete":
            for a in A[i1:i2]:
                drop_src(a, j1)
        elif op == "insert":
            for b in B[j1:j2]:
                drop_hyp(b, i1)
        else:  # replace
            if any(x.kind == "frac" for x in A[i1:i2]) != any(x.kind == "frac" for x in B[j1:j2]):
                # 分数の構文が合わない(3分の1 vs 1/3 等): 値ガードでは結論を出さず既存判定へ委譲
                pairs.append(PairResult(" ".join(x.surface for x in A[i1:i2]), " ".join(x.surface for x in B[j1:j2]),
                                        UNKNOWN, "fraction_syntax_mismatch"))
                continue
            m = min(i2 - i1, j2 - j1)
            for k in range(m):
                do_pair(A[i1 + k], B[j1 + k])
            for a in A[i1 + m:i2]:
                drop_src(a, j2)
            for b in B[j1 + m:j2]:
                drop_hyp(b, i2)
    kind = aggregate(p.verdict for p in pairs)
    reasons = tuple(f"{p.verdict}:{p.reason}:{p.src!r}->{p.hyp!r}" for p in pairs if p.verdict != EQUAL)
    return ValueGuardResult(kind, tuple(pairs), reasons, tuple(warns))


def _guard_en(src: str, hyp: str) -> ValueGuardResult:
    SA, SB = _en_sequence(src), _en_sequence(hyp)
    if not any(a.kind in ("num", "time") for a in SA + SB):
        return ValueGuardResult(NO_VALUES)

    def key(a: Atom):
        return ("lit", a.surface) if a.kind == "literal" else a.key()

    sm = difflib.SequenceMatcher(None, [key(a) for a in SA], [key(b) for b in SB], autojunk=False)
    pairs: list[PairResult] = []

    def isnum(a):
        return a.kind in ("num", "time")

    def drop(a: Atom, partner_lits: list, side: str):
        if a.kind == "num" and a.soft_one:
            pairs.append(PairResult(a.surface if side == "src" else None, a.surface if side == "hyp" else None,
                                    UNKNOWN, f"{side}_one_dropped_or_inserted(pronoun_article_use_possible)"))
            return
        if any(w.surface in _EN_HOMOPHONE_WORDS for w in partner_lits):
            pairs.append(PairResult(a.surface if side == "src" else None, a.surface if side == "hyp" else None,
                                    AMBIGUOUS, f"{side}_number_vs_homophone_word"))
            return
        pairs.append(PairResult(a.surface if side == "src" else None, a.surface if side == "hyp" else None,
                                DIFF, f"{side}_drop(b)"))

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        a_blk, b_blk = SA[i1:i2], SB[j1:j2]
        if op == "equal":
            for a, b in zip(a_blk, b_blk):
                if isnum(a):
                    v, r, _ = _compare_pair(a, b, "en")
                    pairs.append(PairResult(a.surface, b.surface, v, r))
            continue
        an = [a for a in a_blk if isnum(a)]
        bn = [b for b in b_blk if isnum(b)]
        al = [a for a in a_blk if not isnum(a)]
        bl = [b for b in b_blk if not isnum(b)]
        m = min(len(an), len(bn))
        for k in range(m):
            a, b = an[k], bn[k]
            v, r, _ = _compare_pair(a, b, "en")
            # "one"が明確な数量として相手側の別の数詞と対応 -> DIFF(a)(_compare_pairのvalue_differs)。値が同じなら通常比較。
            pairs.append(PairResult(a.surface, b.surface, v, r))
        for a in an[m:]:
            drop(a, bl, "src")
        for b in bn[m:]:
            drop(b, al, "hyp")
    kind = aggregate(p.verdict for p in pairs)
    reasons = tuple(f"{p.verdict}:{p.reason}:{p.src!r}->{p.hyp!r}" for p in pairs if p.verdict != EQUAL)
    return ValueGuardResult(kind, tuple(pairs), reasons)


def value_guard(src: str, hyp: str, lang: str) -> ValueGuardResult:
    """原稿側(src)と転写側(hyp)の値ガード。lang in {'en','ja'}。純関数(API 0・副作用なし)。"""
    if lang == "ja":
        return _guard_ja(src, hyp)
    if lang == "en":
        return _guard_en(src, hyp)
    raise ValueError(f"unsupported lang: {lang!r}")
