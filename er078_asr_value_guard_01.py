# ============================================================
# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_02b
# 値ガード(数値と単位の比較)。原稿側文と転写側文から「値atom」を位置順に抽出し、位置対応させて
# 5値 {NO_VALUES, EQUAL, DIFF, AMBIGUOUS, UNKNOWN} を返す唯一の数値比較実装。
#
# 状態: 作業branch feat/auw-unified-asr-01 上の新規moduleのみ。Production配線なし(委任_03/04)。
#       既存Production関数(er006_*/er007_*/runner群)は一切変更しない(importして使うだけ)。
#
# 2026-10-25 JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A(OPEN-517 F1+F2 / OPEN-523 / OPEN-524 のProduction適用。承認済み安全条件[値・単位の最終確認]を機能させる不具合是正。
#   合格範囲は狭まる方向のみ。DEV正本: docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_DESIGN_02.md・proto_value_gate_fix_04.py):
#   F2 = `value_guard_kana_unified`(READING_MATCH PASSの最終ゲートにだけ judge が `kana_unify=True` で使う。かな書き数詞の表記統一)。
#   OPEN-524 = かな数詞が『より大きいかな数詞の一部』(にじゅうよっか内のよっか)のとき atom を『部分一致』印にして値一致扱いしない(KANA_WORD_BOUNDARY_CHECK)。
#   OPEN-523 = 弱いかな数詞(なのか/ようか/とお)は、脱落atomの値と一致しうる場合だけ数詞の証拠とする(WEAK_KANA_REGION_COMPAT)。
#   rollback: 上記2定数を False(各1行)。F1(READING_MATCH最終ゲート)は judge の READING_MATCH_FINAL_GATE。
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

import dataclasses
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
# OPEN-523(2026-10-25): 弱いかな数詞が表せる(値, 助数詞)。脱落atomがこの値でないとき、弱い語は『数詞の証拠』にしない(一般語[何なのか/しようか/通り]と区別できないため、
# 『脱落atomの値と一致しうる場合だけ』UNKNOWN=委譲、それ以外は従来のDIFF(b)判定へ進む=合格範囲は狭まるのみ)。False=従来挙動(rollback用module定数。env/flagではない)。
WEAK_KANA_REGION_COMPAT = True
_WEAK_KANA_VALUES = {"なのか": ((7, "day"), (7, "day_span")), "ようか": ((8, "day"), (8, "day_span")), "とお": ((10, "tsu"),)}
# OPEN-524(2026-10-25): かな数詞の一致が『同じ助数詞のより大きいかな数詞の一部』(にじゅうよっか内のよっか)のとき、atomに部分一致印(extra)を付け、
# 他atomと値が一致しても同一視しない(従来はEQUAL=誤PASS)。False=従来挙動(rollback用module定数)。
KANA_WORD_BOUNDARY_CHECK = True
_EMBEDDED_TAG = "embedded"
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
            extra = ()
            if KANA_WORD_BOUNDARY_CHECK:
                big = embedded_in_larger_reading(t, s, e, m.group(0), v, unit)
                if big:
                    extra = (_EMBEDDED_TAG, big)   # 部分一致印: keyにbig(より大きい読み)を含むため、24日(にじゅうよっか)と34日(さんじゅうよっか)も区別される
            atoms.append(Atom(m.group(0), "num", Fraction(v), unit, s, e, extra=extra))
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


def _weak_kana_compatible(atom, weak: str) -> bool:
    """弱いかな数詞(weak)が、脱落したatomの値を表しうるか。値を持たない種別(frac/approx/unparsed)は従来どおり『表しうる』扱い(=変更しない)。"""
    if atom is None or not WEAK_KANA_REGION_COMPAT:
        return True
    if atom.kind == "num":
        return (atom.value, atom.unit) in _WEAK_KANA_VALUES[weak]
    if atom.kind == "amb" and atom.alt is not None:
        return tuple(atom.alt) in _WEAK_KANA_VALUES[weak]
    return True


def _region_has_numeral_ja(text: str, atom=None) -> bool:
    return (bool(re.search(r"[0-9〇零一二三四五六七八九十百千万億兆]", text))
            or any(w in text and _weak_kana_compatible(atom, w) for w in WEAK_KANA_NUMERALS)
            or bool(_KANA_RE.search(text)))


# ============================================================
# 期待読み表(OPEN-517 F2 / OPEN-524) — 移設元: er066_ja_asr_orthographic_equivalence_01_trial.py `_cands` と周辺(L114-280)。
# 「Production→Trial import禁止」(DESIGN_01 §5-4)のため移設。**移設後の表とTrialの`_cands`の差分はparity testで固定**
# (er078_asr_value_guard_kana_unify_test_01.py: n=1..20000×全unit。意図差分は『弱い読み除外』『同unitで値が一意でない読み除外』のみ=`expected_reads`側で適用)。
# ============================================================
_ER_D = {1: "いち", 2: "に", 3: "さん", 4: "よん", 5: "ご", 6: "ろく", 7: "なな", 8: "はち", 9: "きゅう"}


def _er_under10000(n: int) -> str:
    out = ""
    th, rest = divmod(n, 1000)
    if th:
        out += {1: "せん", 3: "さんぜん", 8: "はっせん"}.get(th, _ER_D[th] + "せん")
    hu, rest = divmod(rest, 100)
    if hu:
        out += {1: "ひゃく", 3: "さんびゃく", 6: "ろっぴゃく", 8: "はっぴゃく"}.get(hu, _ER_D[hu] + "ひゃく")
    te, on = divmod(rest, 10)
    if te:
        out += "じゅう" if te == 1 else _ER_D[te] + "じゅう"
    if on:
        out += _ER_D[on]
    return out


def _er_kana_int(n: int) -> str:
    if n == 0:
        return "ぜろ"
    out = ""
    oku, rest = divmod(n, 10 ** 8)
    man, rest = divmod(rest, 10000)
    if oku:
        out += _er_under10000(oku) + "おく"
    if man:
        out += ("いち" if man == 1 else _er_under10000(man)) + "まん"
    if rest:
        out += _er_under10000(rest)
    return out


def _er_sok(k: str, six: bool = True) -> str:
    """促音化。six=Falseなら6(ろく)は促音化しない(6歳ろくさい・6週間ろくしゅうかん)。"""
    for a, b in (("いち", "いっ"), ("ろく", "ろっ"), ("はち", "はっ"), ("じゅう", "じゅっ"), ("ひゃく", "ひゃっ")):
        if a == "ろく" and not six:
            continue
        if k.endswith(a):
            return k[: -len(a)] + b
    return k


def _er_swap_last(n: int, sub: dict) -> str | None:
    """末尾桁の慣用読み(4->よ, 7->しち, 9->く)へ差し替えた数詞読み。"""
    k = _er_kana_int(n)
    d = n % 10
    dflt = {4: "よん", 7: "なな", 9: "きゅう"}
    if d in sub and k.endswith(dflt[d]):
        return k[: -len(dflt[d])] + sub[d]
    return None


def _er_cls(n: int) -> int:
    """促音化クラス: 末尾桁。10/100の倍数は0、1000の倍数は-1(促音化なし)。"""
    if n % 1000 == 0:
        return -1
    return n % 10


_ER_DAY = {1: ["ついたち", "いちにち"], 2: ["ふつか"], 3: ["みっか"], 4: ["よっか"], 5: ["いつか"], 6: ["むいか"],
        7: ["なのか"], 8: ["ようか"], 9: ["ここのか"], 10: ["とおか"], 14: ["じゅうよっか"], 20: ["はつか"],
        24: ["にじゅうよっか"]}
_ER_TSU = {1: "ひとつ", 2: "ふたつ", 3: "みっつ", 4: "よっつ", 5: "いつつ", 6: "むっつ", 7: "ななつ", 8: "やっつ", 9: "ここのつ", 10: "とお"}
_ER_MONTH = {1: "いち", 2: "に", 3: "さん", 4: "し", 5: "ご", 6: "ろく", 7: "しち", 8: "はち", 9: "く", 10: "じゅう", 11: "じゅういち", 12: "じゅうに"}


def _er_uniq(xs):
    return list(dict.fromkeys(xs))


def _er_cands(n: int, c: str) -> list[str]:
    k = _er_kana_int(n)
    d = n % 10
    if c in ("day", "day_span"):
        suf = "かん" if c == "day_span" else ""
        if n in _ER_DAY:
            return [x + suf for x in (_ER_DAY[n] if c == "day" else _ER_DAY[n][:1] if n != 1 else ["いちにち"])]
        if d == 4:
            return [k[:-2] + "よっか" + suf]
        outs = [k + "にち" + suf]
        for dd, key in ((7, "しち"), (9, "く")):
            if d == dd:
                s = _er_swap_last(n, {dd: key})
                if s:
                    outs.append(s + "にち" + suf)
        return outs
    if c == "person":
        if n == 1:
            return ["ひとり"]
        if n == 2:
            return ["ふたり"]
        if d == 4:
            return [_er_swap_last(n, {4: "よ"}) + "にん"]
        outs = [k + "にん"]
        if d == 7:
            outs.append(_er_swap_last(n, {7: "しち"}) + "にん")
        return outs
    if c in ("hour", "hour_span"):
        suf = "じ" if c == "hour" else "じかん"
        if d == 4:
            return [_er_swap_last(n, {4: "よ"}) + suf]
        if d == 7:
            return [k + suf, _er_swap_last(n, {7: "しち"}) + suf]
        if d == 9:
            return [_er_swap_last(n, {9: "く"}) + suf]
        return [k + suf]
    if c in ("minute", "hon", "haku"):
        h, p = {"minute": ("ふん", "ぷん"), "hon": ("ほん", "ぽん"), "haku": ("はく", "ぱく")}[c]
        cl = _er_cls(n)
        if cl == -1:
            return [k + {"minute": "ぷん", "hon": "ぼん", "haku": "ぱく"}[c]]
        if cl in (1, 6, 8, 0):
            outs = [_er_sok(k) + p]
            if c == "minute" and cl in (8, 0):
                outs.append(k + h)
            return outs
        if c == "minute" and cl in (3, 4):
            return [k + p]
        if c == "hon" and cl == 3:
            return [k + "ぼん"]
        if c == "haku" and cl == 3:
            return [k + p]
        return [k + h]
    if c == "second":
        return [k + "びょう"]
    if c == "month":
        return [_ER_MONTH[n] + "がつ"] if n in _ER_MONTH else []
    if c == "month_span":
        return [(_er_sok(k) if _er_cls(n) in (1, 6, 8, 0) else k) + "かげつ"]
    if c in ("year", "year_span"):
        suf = "ねん" + ("かん" if c == "year_span" else "")
        if d == 4:
            return [_er_swap_last(n, {4: "よ"}) + suf]
        if d == 7:
            return [k + suf, _er_swap_last(n, {7: "しち"}) + suf]
        if d == 9:
            return [k + suf, _er_swap_last(n, {9: "く"}) + suf]
        return [k + suf]
    if c in ("age", "kai", "ken", "ko", "week"):
        base = {"age": "さい", "kai": "かい", "ken": "けん", "ko": "こ", "week": "しゅうかん"}[c]
        if c == "age" and n == 20:
            return ["はたち"]
        # 02: 歳(さい)・週間(しゅうかん)は6でも促音化しない(ろくさい/ろくしゅうかん)。1/8/10/100は促音化。
        six = c not in ("age", "week")
        outs = [(_er_sok(k, six) if _er_cls(n) in (1, 6, 8, 0) else k) + base]
        if c in ("age", "week") and _er_cls(n) == 0:
            outs.append(k + base)  # さんじゅうさい / さんじゅっさい の両方が標準
        return outs
    if c == "tsu":
        return [_ER_TSU[n]] if n in _ER_TSU else []
    if c == "yen":
        if d == 4:
            return [_er_swap_last(n, {4: "よ"}) + "えん", k + "えん"]
        return [k + "えん"]
    if c == "percent":
        return [k + "ぱーせんと", k + "ぱあせんと"]
    if c == "floor":
        if _er_cls(n) == 3:
            return [k + "がい"]
        return [(_er_sok(k) if _er_cls(n) in (1, 6, 8, 0) else k) + "かい"]
    simple = {"gen": "だい", "ban": "ばん", "go": "ごう", "mai": "まい", "dai": "だい", "bai": "ばい", "do": "ど", "km": "きろ"}
    if c in simple:
        return [k + simple[c]]
    return []



_ER_REV: dict = {}       # unit -> {read: set(values)}  (n=1..ER_REV_MAX、遅延生成・プロセス内キャッシュ)
ER_REV_MAX = 20000
_ER_EXT_K = 8            # 前後k文字(<=8)を連結して『より大きいかな数詞の読みか』を調べる範囲(最長一致の等価)
_WEAK_SET = frozenset(WEAK_KANA_NUMERALS)


def _er_rev(unit: str) -> dict:
    if unit not in _ER_REV:
        m: dict = {}
        for n in range(1, ER_REV_MAX + 1):
            try:
                for r in _er_cands(n, unit):
                    if r:
                        m.setdefault(r, set()).add(n)
            except Exception:  # noqa: BLE001  表生成の失敗はその値を表に載せないだけ(fail-safe=置換しない)
                pass
        _ER_REV[unit] = m
    return _ER_REV[unit]


def expected_reads(value, unit) -> list:
    """atom(value, unit)の期待読み(かな)。Trial `_cands` との意図差分: (1)弱い読み(なのか/ようか/とお。一般語と衝突しProductionが辞書から外した)を除外
    (2)同unit内で値が一意でない読みを除外。整数以外・助数詞なし・範囲外は空。"""
    try:
        if value is None or Fraction(value).denominator != 1 or unit == "":
            return []
        n = int(value)
        rv = _er_rev(unit) if 1 <= n <= ER_REV_MAX else {}
        out = []
        for x in _er_cands(n, unit):
            if not x or x in _WEAK_SET:
                continue
            if rv and rv.get(x, {n}) != {n}:
                continue
            out.append(x)
        return out
    except Exception:  # noqa: BLE001
        return []


def _part_of_larger_numeral(text: str, i: int, j: int, r: str, value, unit: str) -> bool:
    """text[i:j]==r(値valueの読み)が、同unitのより大きい(別値の)数詞読みの一部か。F2の置換可否判定(最長一致)。"""
    if not (1 <= int(value) <= ER_REV_MAX):
        return False
    rv = _er_rev(unit)
    for k in range(1, _ER_EXT_K + 1):
        if i - k >= 0:
            sx = text[i - k:i] + r
            if rv.get(sx) and rv[sx] != {int(value)}:
                return True
        if j + k <= len(text):
            sx = r + text[j:j + k]
            if rv.get(sx) and rv[sx] != {int(value)}:
                return True
    if j < len(text) and text[j] in "ゃゅょ":
        return True
    return False


def embedded_in_larger_reading(text: str, i: int, j: int, r: str, value, unit: str) -> str:
    """OPEN-524: かな数詞の一致text[i:j]==r(registered, 値value/助数詞unit)が、より大きいかな数詞の読みの一部なら、その(最長の)読み文字列を返す。無ければ ''。
    判定: (a)同unitの別値の読みになる (b)unit=dayのとき日数(day_span)の読みになる(みっか+かん=3日間。値が同じでも助数詞が違うので『部分一致』)
    (c)直後が拗音(ゃゅょ)。表に無い(非標準の)連結は『部分一致』にしない=従来どおり。"""
    try:
        if not (1 <= int(value) <= ER_REV_MAX):
            return ""
        best = ""
        tables = [(unit, False)] + ([("day_span", True)] if unit == "day" else [])
        for u, any_value in tables:
            rv = _er_rev(u)
            for k in range(1, _ER_EXT_K + 1):
                cands = []
                if i - k >= 0:
                    cands.append(text[i - k:i] + r)
                if j + k <= len(text):
                    cands.append(r + text[j:j + k])
                for sx in cands:
                    hit = rv.get(sx)
                    if hit and (any_value or hit != {int(value)}) and len(sx) > len(best):
                        best = sx
        if not best and j < len(text) and text[j] in "ゃゅょ":
            best = r + text[j]
        return best
    except Exception:  # noqa: BLE001  fail-safe: 判定不能は従来どおり(印を付けない)
        return ""


# ============================================================
# F2: かな書き数詞の表記統一(OPEN-517、DESIGN_02 §F2 / proto_value_gate_fix_04.py v4 の移設)
# READING_MATCH PASSの最終ゲートでだけ使う(judgeが明示引数 kana_unify=True で呼ぶ)。Primary NG・Secondary・KP等では使わない。
# 原稿(または転写)の『かな書き数詞』を、相手側が同じ値を数字で書いた表層へ置換してから値ガードを再計算する。
# 単調性ガード: F2前の非EQUAL pair(置換に対応するものを除く)がF2後も同じ(src,hyp,verdict)で全て残らなければF2前の結果を採用する
# =F2は『誤NG防止』の側にだけ働き、F1が検出した値違い・否定差を隠さない(合格範囲は広がらない)。
# ============================================================
def _replace_kana(text, own_atoms, other_atoms, budget):
    """NFKC text中の『かな書き数詞』を相手側atom表層へ置換。budget={surface: 許可回数}(F2前に未対応だった相手atomだけ)。戻り: (新text, 置換したatomのlist)"""
    out = unicodedata.normalize("NFKC", text or "")
    spans = [(a.start, a.end, a) for a in own_atoms]
    replaced = []
    for a in other_atoms:
        if a.kind != "num" or budget.get(a.surface, 0) <= 0:
            continue
        done = False
        for r in sorted(expected_reads(a.value, a.unit), key=len, reverse=True):
            i = out.find(r)
            while i >= 0:
                j = i + len(r)
                ok = True
                for st, en, x in spans:
                    if not (i < en and j > st):
                        continue
                    # 重なる既存atom: 候補(=相手atomの値の完全な期待読み)が既存atomを内包する(完全一致でない)場合のみ吸収を許可
                    if not ((i <= st and en <= j) and (st, en) != (i, j) and x.kind in ("num", "amb")):
                        ok = False
                        break
                if ok and not _part_of_larger_numeral(out, i, j, r, a.value, a.unit):
                    out = out[:i] + a.surface + out[j:]
                    replaced.append(a)
                    budget[a.surface] -= 1
                    spans = [(x.start, x.end, x) for x in extract_atoms_ja(out)]
                    done = True
                    break
                i = out.find(r, i + 1)
            if done:
                break
    return out, replaced


def _eligible_budget(pairs0, side):
    """F2前のpair列から『相手atomが未対応(None)または別のかな数詞atomと対応していた』非EQUALを集計。
    side='hyp': 置換対象=転写側 -> 原稿側atom(src)が対象。side='src': 逆。"""
    b: dict = {}
    for p in pairs0:
        if p.verdict == EQUAL:
            continue
        mine, other = (p.src, p.hyp) if side == "hyp" else (p.hyp, p.src)
        if mine is None:
            continue
        if other is None or other in KANA_NUMERALS:
            b[mine] = b.get(mine, 0) + 1
    return b


@dataclass(frozen=True)
class KanaUnifyInfo:
    fired: bool
    replaced: tuple = ()          # ((side, partner_surface), ...)
    fallback: str = ""            # '' / 'monotonic_guard' / 'no_replacement'
    canon2: str = ""
    text2: str = ""

    def to_dict(self) -> dict:
        return {"fired": self.fired, "replaced": [list(x) for x in self.replaced], "fallback": self.fallback,
                "canon2": self.canon2, "text2": self.text2}


def _replace_both(canon, text, g0):
    nc, na = unicodedata.normalize("NFKC", canon or ""), unicodedata.normalize("NFKC", text or "")
    ac, aa = extract_atoms_ja(nc), extract_atoms_ja(na)
    bh = _eligible_budget(g0.pairs, "hyp")   # 原稿側atomを相手にして転写をかな->数字へ
    bs = _eligible_budget(g0.pairs, "src")   # 転写側atomを相手にして原稿をかな->数字へ
    c2, rc = _replace_kana(nc, ac, aa, bs)
    a2, ra = _replace_kana(na, aa, ac, bh)
    return c2, a2, [("src", a) for a in rc], [("hyp", a) for a in ra]


def unify_kana_numerals(canon, asr, g0=None):
    """(canon', asr', 置換atoms)。g0=F2前のvalue_guard結果(省略時は計算)。"""
    g0 = g0 or _guard_ja(canon, asr)
    c2, a2, rc, ra = _replace_both(canon, asr, g0)
    return c2, a2, [a for _, a in rc + ra]


def _nonequal(g):
    return [(p.src, p.hyp, p.verdict) for p in g.pairs if p.verdict != EQUAL]


def value_guard_kana_unified_detail(canon: str, text: str, lang: str = "ja"):
    """value_guardにF2を前置。戻り (ValueGuardResult, KanaUnifyInfo)。lang!='ja'は通常のvalue_guardでF2なし。純関数(API 0・副作用なし)。"""
    if lang != "ja":
        return value_guard(canon, text, lang), KanaUnifyInfo(False)
    g0 = _guard_ja(canon, text)
    c2, t2, rc, ra = _replace_both(canon, text, g0)
    reps = rc + ra
    if not reps:
        return g0, KanaUnifyInfo(False, fallback="no_replacement")
    g = _guard_ja(c2, t2)
    # 単調性ガード: F2前の非EQUAL pairから『置換に対応するpair』を除いたものが、F2後も同じ(src,hyp,verdict)で全て残ること
    pre = _nonequal(g0)
    for side, a in reps:
        for k, (sv, hv, v) in enumerate(pre):
            if (side == "hyp" and sv == a.surface and (hv is None or hv in KANA_NUMERALS)) or \
               (side == "src" and hv == a.surface and (sv is None or sv in KANA_NUMERALS)):
                pre.pop(k)
                break
    post = _nonequal(g)
    rep_t = tuple((sd, a.surface) for sd, a in reps)
    for t in pre:
        if t in post:
            post.remove(t)
        else:
            return g0, KanaUnifyInfo(False, rep_t, "monotonic_guard", c2, t2)
    warns = list(dict.fromkeys(list(g0.warnings) + list(g.warnings)))
    if any(is_irregular_sig(a.value, a.unit) for _, a in reps) and WARN_IRREGULAR_READING not in warns:
        warns.append(WARN_IRREGULAR_READING)
    return dataclasses.replace(g, warnings=tuple(warns)), KanaUnifyInfo(True, rep_t, "", c2, t2)


def value_guard_kana_unified(canon: str, text: str, lang: str = "ja") -> ValueGuardResult:
    return value_guard_kana_unified_detail(canon, text, lang)[0]


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
    if a.kind == "num" and (a.extra[:1] == (_EMBEDDED_TAG,) or b.extra[:1] == (_EMBEDDED_TAG,)) and a.extra != b.extra:
        return DIFF, "kana_numeral_part_of_larger_reading", False   # OPEN-524: 『にじゅうよっか』のよっか等は4日と同一視しない
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
    if _region_has_numeral_ja(region_text, atom):
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
        # 2026-10-23(OPEN-482 第2層、FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_04、承認済み規則の不具合是正): 原稿の「時 分」2数値atom
        # (TTS入力の数字化後の`10 thirty` -> num10,num30)と、反対側の1つの時刻atom(`10:30` -> time1030)は、隣接する2数値の
        # hour*100+minute(時0-24・分10-59・単位/%/通貨/序数なし)が時刻atomと一致し、時刻atomにam/pmが無いときだけ同一とみなす。
        # 値が違えば(10:13/11:30/2:03/10 vs 10:30等)従来どおりDIFF/UNKNOWN。単独数値・桁連結には適用しない。
        def _clock_pair(blk2, blk1):
            n2 = [(k, t) for k, t in enumerate(blk2) if isnum(t)]
            n1 = [t for t in blk1 if isnum(t)]
            if len(n2) != 2 or len(n1) != 1 or n2[1][0] - n2[0][0] != 1:
                return False
            (_, h), (_, mi), one = n2[0], n2[1], n1[0]
            return (one.kind == "time" and one.extra == (None,)
                    and all(t.kind == "num" and t.unit == "" and t.extra == (False, None, False) and t.value == int(t.value) for t in (h, mi))
                    and 0 <= h.value <= 24 and 10 <= mi.value <= 59 and h.value * 100 + mi.value == one.value)
        if _clock_pair(a_blk, b_blk) or _clock_pair(b_blk, a_blk):
            pairs.append(PairResult(" ".join(a.surface for a in an), " ".join(b.surface for b in bn), EQUAL, "clock_time_words_vs_digits"))
            continue
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
