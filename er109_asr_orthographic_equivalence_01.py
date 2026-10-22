# ============================================================
# er109_asr_orthographic_equivalence_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01 (2026-10-22) 未配線プロトタイプ。
# Status: INVESTIGATION_DESIGN_PENDING_OPUS(未承認・既定OFF。Production既存ファイルから参照されない=er109_*_test.pyで固定)。
#
# 目的: 『発音が同一なのに転写の表記が違うだけ』(one<->1, one's<->1's, 30 percent<->30%, Mr.<->mister ...)の偽NGを、
#       全英語ASR経路で共通に解消する「表記正規化+発音同値化」層の純関数(API 0・副作用なし)。
# 位置(設計): val.classify_asr_match()ラッパーの末尾(既存baseline・標準contraction展開の後)で、既存が不合格のときだけ1回呼ぶ想定。
#       全票(OpenAI/Azure/Whisper)・Store再利用・X引継ぎが同じclassify_asr_matchを通るため、判定原則が自動的に揃う。
# 判定: canonical/ASR両文を「unit列」へ分割し(語・数・記号・略語)、difflibで整列。表層が同じunitは同値。
#       差のあるspanごとに、各unitの『読みの候補(CMU音素列の集合)』を連結した音素列集合が両側で交わる場合のみ同値。
#       どれか1つでもspanが交わらない/CMU未登録(判定不能)/長すぎる場合は全体を非同値(fail-closed)。
# 禁止(安全): 欠落・付加(片側が空のspan)は同値にしない。音素が1つでも違えば同値にしない(2<->3, take part<->take tart)。
#       否定語(not/no/n't等)の有無差は音素が異なるため自然にNG。固有名詞(canonical側大文字始まり)は代表発音のみ(G9方針)。
# 再利用: 標準contraction展開=val.expand_standard_contractions(承認済み)、CMU取得=homophone_en._phone_variants(承認済み)、
#       entity判定=val.capitalized_flags/loanword_flags。新規の許容辞書は閉じた記号・略語表(下記)のみ。
# ============================================================
from __future__ import annotations

import difflib
import itertools
import re
import unicodedata
from dataclasses import dataclass, field

import er008_asr_variant_hardening_15_homophone_en as _hp

# ---- 単一flag(未承認・既定OFF。配線されるまで読取側は存在しない。env/引数/設定dictから変えられない) ----
ORTHOGRAPHIC_EQUIVALENCE_ENABLED = False
LAYER_VERSION = "er109_orthographic_equivalence_v0_proto"


def is_enabled() -> bool:
    """配線時の単一読取関数(現状は誰も呼ばない)。"""
    return bool(ORTHOGRAPHIC_EQUIVALENCE_ENABLED)


MAX_UNITS_PER_SIDE = 6      # 1つの差span内の最大unit数
MAX_JOINT = 64              # 音素列variant直積の上限(超過は代表発音へ縮退、それでも超過は判定不能)

# ---------------------------------------------------------------- 数 -> 英語読み
_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
         "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
_ORD_ONES = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth", "nine": "ninth",
             "twelve": "twelfth"}
_SCALES = [(10 ** 12, "trillion"), (10 ** 9, "billion"), (10 ** 6, "million"), (10 ** 3, "thousand")]


def _under_1000(n: int, with_and: bool = False) -> list[str]:
    out: list[str] = []
    if n >= 100:
        out += [_ONES[n // 100], "hundred"]
        n %= 100
        if n and with_and:
            out.append("and")
    if n >= 20:
        out.append(_TENS[n // 10])
        if n % 10:
            out.append(_ONES[n % 10])
    elif n or not out:
        out.append(_ONES[n])
    return out


def int_to_words(n: int, with_and: bool = False) -> list[str] | None:
    if n < 0 or n >= 10 ** 15:
        return None
    if n == 0:
        return ["zero"]
    out: list[str] = []
    for scale, name in _SCALES:
        if n >= scale:
            out += _under_1000(n // scale, with_and) + [name]
            n %= scale
    if n:
        # 100未満の端数だけが残り、かつ上位があるときの"and"(英式)
        if with_and and out and n < 100:
            out.append("and")
        out += _under_1000(n, with_and)
    return out


def _ordinal_of_words(words: list[str]) -> list[str]:
    last = words[-1]
    if last in _ORD_ONES:
        o = _ORD_ONES[last]
    elif last.endswith("y"):
        o = last[:-1] + "ieth"
    elif last in ("hundred", "thousand", "million", "billion", "trillion"):
        o = last + "th"
    else:
        o = last + "th"
    return words[:-1] + [o]


def cardinal_variants(n: int) -> list[list[str]]:
    """整数nの読みの候補(米式/英式and有無、4桁年の読み)。"""
    base = int_to_words(n)
    if base is None:
        return []
    outs = [base]
    if n >= 101:
        wa = int_to_words(n, True)
        if wa and wa != base:
            outs.append(wa)
    if 1100 <= n <= 2099 and n % 1000 != 0 or (n == 2000):
        hi, lo = divmod(n, 100)
        if n % 100 == 0 and n != 2000:
            yr = int_to_words(hi) + ["hundred"]
        elif lo == 0:
            yr = None
        elif lo < 10:
            yr = int_to_words(hi) + ["oh", _ONES[lo]]
        else:
            yr = int_to_words(hi) + int_to_words(lo)
        if yr and yr not in outs:
            outs.append(yr)
    return outs


# ---------------------------------------------------------------- 閉じた記号・略語表(新規許容はこれだけ)
SYMBOL_READINGS = {
    "%": [["percent"]], "&": [["and"]], "+": [["plus"]], "=": [["equals"], ["equal"]], "@": [["at"]],
    "°": [["degrees"], ["degree"]], "#": [["number"], ["hash"], ["pound"]],
}
CURRENCY_SYMBOLS = {"$": ("dollar", "dollars", "cent", "cents"), "£": ("pound", "pounds", "penny", "pence"),
                    "€": ("euro", "euros", "cent", "cents")}
# 略語(語単位)。ambiguous語(dr=doctor/drive, st=saint/street)は候補を複数持つ(どれか1つが相手と一致すれば同値)。
ABBREVIATIONS = {
    "mr": [["mister"]], "mrs": [["missus"], ["misses"]], "ms": [["miz"], ["mizz"]], "dr": [["doctor"], ["drive"]],
    "st": [["saint"], ["street"]], "jr": [["junior"]], "sr": [["senior"]], "vs": [["versus"]], "v": [["versus"]],
    "inc": [["incorporated"]], "co": [["company"]], "ltd": [["limited"]], "corp": [["corporation"]],
    "ok": [["okay"]], "approx": [["approximately"]], "dept": [["department"]], "govt": [["government"]],
    "etc": [["et", "cetera"], ["etcetera"]], "ave": [["avenue"]], "blvd": [["boulevard"]], "rd": [["road"]],
    "mt": [["mount"], ["mountain"]], "ft": [["feet"], ["foot"]], "lb": [["pounds"], ["pound"]], "lbs": [["pounds"]],
    "oz": [["ounces"], ["ounce"]], "min": [["minutes"], ["minute"]], "sec": [["seconds"], ["second"]],
    "hr": [["hour"], ["hours"]], "hrs": [["hours"]], "km": [["kilometers"], ["kilometres"]],
    "kg": [["kilograms"], ["kilogram"]], "mph": [["miles", "per", "hour"]]
}
# 句読点付きだけ略語とみなす語(通常語と衝突する): min/sec/hr/v/co/ft/mt/ok 等は『ピリオド付き』か『大文字のみ』のとき限定
_ABBR_NEEDS_DOT_OR_CAPS = {"min", "sec", "hr", "v", "co", "ft", "mt", "lb", "oz", "st", "dr", "ms", "ave", "rd", "sr", "jr", "inc"}
_LETTER_NAMES = {
    "a": "EY", "b": "B IY", "c": "S IY", "d": "D IY", "e": "IY", "f": "EH F", "g": "JH IY", "h": "EY CH", "i": "AY",
    "j": "JH EY", "k": "K EY", "l": "EH L", "m": "EH M", "n": "EH N", "o": "OW", "p": "P IY", "q": "K Y UW",
    "r": "AA R", "s": "EH S", "t": "T IY", "u": "Y UW", "v": "V IY", "w": "D AH B AH L Y UW", "x": "EH K S",
    "y": "W AY", "z": "Z IY",
}
_FRACTIONS = {(1, 2): [["one", "half"], ["a", "half"]], (1, 3): [["one", "third"]], (2, 3): [["two", "thirds"]],
              (1, 4): [["one", "quarter"], ["one", "fourth"]], (3, 4): [["three", "quarters"], ["three", "fourths"]]}

# ---------------------------------------------------------------- unit
@dataclass
class Unit:
    surface: str
    key: str
    kind: str                       # word | number | symbol | abbrev | acronym | unknown
    prons: set | None               # set[tuple[str,...]] 音素列(stress無視)。None=判定不能
    rep_prons: set | None = None    # 代表発音のみ(固有名詞・variant爆発時の縮退用)
    rule: str = ""
    why: str = ""


def _strip_stress(ph: str) -> tuple:
    return tuple(re.sub(r"\d", "", ph).split())


def _word_prons(w: str, representative: bool = False) -> set | None:
    """英単語(小文字)のCMU音素列集合。未登録は規則的な'sのみ補完、他はNone。"""
    w = (w or "").lower().strip("'\".,;:!?")
    if not w:
        return None
    ps = _hp._phone_variants(w)
    out: set = set()
    if ps:
        ps = ps[:1] if representative else ps
        out |= {_strip_stress(p) for p in ps}
    if "-" in w:
        parts = [p for p in w.split("-") if p]
        sets = [_word_prons(p, representative) for p in parts]
        if parts and all(sets):
            out |= {tuple(x for part in combo for x in part) for combo in itertools.product(*sets)}
    if out:
        return out
    m = re.match(r"^(.+?)'s$", w)
    if m:
        base = _word_prons(m.group(1), representative)
        if base:
            return {b + _s_suffix(b) for b in base}
    return None


def _s_suffix(ph: tuple) -> tuple:
    """規則的な複数・所有の-s(直前音素で S / Z / IH Z)。"""
    if not ph:
        return ("Z",)
    last = ph[-1]
    if last in ("S", "Z", "SH", "ZH", "CH", "JH"):
        return ("IH", "Z")
    if last in ("P", "T", "K", "F", "TH"):
        return ("S",)
    return ("Z",)


def _concat_words(word_lists: list[list[str]], representative: bool = False) -> set | None:
    """読み候補(語リストの候補群)をCMU音素列集合へ。1つでも未登録語を含む候補は捨て、全滅ならNone。"""
    out: set = set()
    for words in word_lists:
        sets = []
        ok = True
        for w in words:
            s = _word_prons(w, representative)
            if not s:
                ok = False
                break
            sets.append(s)
        if not ok:
            continue
        n = 1
        for s in sets:
            n *= len(s)
        if n > MAX_JOINT * 4:
            continue
        for combo in itertools.product(*sets):
            out.add(tuple(x for part in combo for x in part))
    return out or None


def _letters_prons(letters: str) -> set | None:
    try:
        return {tuple(x for ch in letters.lower() for x in _LETTER_NAMES[ch].split())}
    except KeyError:
        return None


def _surface_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKC", s).lower())


_TOKEN_RE = re.compile(
    r"""(?P<money>[$£€]\s?\d+(?:,\d{3})*(?:\.\d+)?)"""
    r"""|(?P<time>\d{1,2}:\d{2}(?:\s?[ap]\.?m\.?)?)"""
    r"""|(?P<ord>\d+(?:,\d{3})*(?:st|nd|rd|th)\b)"""
    r"""|(?P<frac>\d+/\d+)"""
    r"""|(?P<num>(?<![\w.])-?\d+(?:,\d{3})*(?:\.\d+)?(?:'?s)?%?|\d+(?:,\d{3})*(?:\.\d+)?(?:'?s)?%?)"""
    r"""|(?P<dotted>(?:[A-Za-z]\.){2,})"""
    r"""|(?P<word>[A-Za-z]+(?:['’][A-Za-z]+)*(?:-[A-Za-z]+)*'?\.?)"""
    r"""|(?P<sym>[&+=@#°%])""")


def _num_units(m_text: str, group: str, entity: bool) -> Unit:
    """数・通貨・%・序数・時刻・分数のunit化。"""
    s = m_text
    key = _surface_key(s)
    if group in ("num", "money"):
        # 小数点・桁区切りを含めて値を区別する(3.5と35、1,000と1.000を同一keyにしない)。通貨/%は印を付けて語unit(dollars/percent)と整列させる
        key = re.sub(r"[^0-9.\-]", "", s.replace(",", "")) + ("s" if re.search(r"'?s$", s) and group == "num" else "")
        if group == "money":
            key = s[0] + key
        if s.endswith("%"):
            key += "pct"
    if group == "ord":
        n = int(re.sub(r"\D", "", s[:-2]))
        vs = [_ordinal_of_words(w) for w in cardinal_variants(n)]
        return Unit(s, key, "number", _concat_words(vs), rule="number_ordinal")
    if group == "frac":
        a, b = (int(x) for x in s.split("/"))
        vs = _FRACTIONS.get((a, b))
        return Unit(s, key, "number" if vs else "unknown", _concat_words(vs) if vs else None, rule="number_fraction",
                    why="" if vs else "fraction_unsupported")
    if group == "time":
        mm = re.match(r"(\d{1,2}):(\d{2})\s?([ap])?\.?m?\.?", s, re.I)
        h, mi = int(mm.group(1)), int(mm.group(2))
        mer = (mm.group(3) or "").lower()
        if h > 24 or mi > 59:
            return Unit(s, key, "unknown", None, why="time_out_of_range")
        hw = int_to_words(h) if h else ["zero"]
        if mi == 0:
            cands = [hw + ["o'clock"], hw] if not mer else [hw]
        elif mi < 10:
            cands = [hw + ["oh", _ONES[mi]], hw + ["zero", _ONES[mi]]]
        else:
            cands = [hw + int_to_words(mi)]
        if mer:
            ps_h = _concat_words(cands)
            lt = _letters_prons(mer + "m")
            if ps_h and lt:
                return Unit(s, key, "number", {x + y for x in ps_h for y in lt}, rule="number_time")
            return Unit(s, key, "unknown", None, why="time_meridiem")
        return Unit(s, key, "number", _concat_words(cands), rule="number_time")
    if group == "money":
        cur = s[0]
        body = s[1:].strip().replace(",", "")
        d_sing, d_plur, c_sing, c_plur = CURRENCY_SYMBOLS[cur]
        if "." in body:
            whole, frac = body.split(".", 1)
            if len(frac) != 2:
                return Unit(s, key, "unknown", None, why="currency_decimal_unsupported")
            w, f = int(whole or 0), int(frac)
            cands = []
            for wv in cardinal_variants(w):
                unit_w = d_sing if w == 1 else d_plur
                for fv in cardinal_variants(f) if f else [[]]:
                    if f:
                        cands.append(wv + [unit_w, "and"] + fv + [c_sing if f == 1 else c_plur])
                        cands.append(wv + [unit_w] + fv)
                    else:
                        cands.append(wv + [unit_w])
            return Unit(s, key, "number", _concat_words(cands), rule="number_currency")
        n = int(body)
        cands = [wv + [d_sing if n == 1 else d_plur] for wv in cardinal_variants(n)]
        return Unit(s, key, "number", _concat_words(cands), rule="number_currency")
    # num
    t = s
    pct = t.endswith("%")
    if pct:
        t = t[:-1]
    poss = False
    plural_s = False
    mm = re.match(r"^(.*?)('s|s)$", t)
    if mm and re.search(r"\d", mm.group(1)):
        poss = mm.group(2) == "'s"
        plural_s = mm.group(2) == "s"
        t = mm.group(1)
    neg = t.startswith("-")
    if neg:
        t = t[1:]
    body = t.replace(",", "")
    if not re.fullmatch(r"\d+(?:\.\d+)?", body):
        return Unit(s, key, "unknown", None, why="number_unparsed")
    if "," in t and not re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", t):
        return Unit(s, key, "unknown", None, why="number_bad_grouping")
    if len(body.split(".")[0]) > 1 and body.startswith("0") and "." not in body:
        return Unit(s, key, "unknown", None, why="number_leading_zero")
    if "." in body:
        ip, fp = body.split(".")
        ivs = cardinal_variants(int(ip)) if ip != "0" else [["zero"], []]
        digits = [_ONES[int(d)] for d in fp]
        cands = [iv + ["point"] + digits for iv in ivs]
        cands = [c if c[0] != "point" else c for c in cands]
        if ip == "0":
            cands = [["zero", "point"] + digits, ["point"] + digits, ["oh", "point"] + digits]
    else:
        n = int(body)
        cands = cardinal_variants(n)
        if len(body) >= 5 and "," not in t and n >= 10 ** 5:
            return Unit(s, key, "unknown", None, why="long_digit_string_ambiguous")
    if not cands:
        return Unit(s, key, "unknown", None, why="number_out_of_range")
    if neg:
        cands = [["minus"] + c for c in cands] + [["negative"] + c for c in cands]
    if pct:
        cands = [c + ["percent"] for c in cands]
    if plural_s and not pct:
        # 10年代: 90s -> nineties / 1990s -> nineteen nineties
        new = []
        for c in cands:
            if c and c[-1] in _TENS[2:]:
                new.append(c[:-1] + [c[-1][:-1] + "ies"])
        cands = new
        if not cands:
            return Unit(s, key, "unknown", None, why="plural_digits_unsupported")
    prons = _concat_words(cands)
    if prons and poss:
        prons = {p + _s_suffix(p) for p in prons}
    return Unit(s, key, "number", prons, rule="number_cardinal" if not pct else "number_percent")


def _val_contractions() -> dict:
    import er006_preprod_hardening_01_validation as val   # 遅延import(循環回避)
    return val._ALL_STANDARD_CONTRACTIONS


def _units(text: str, entity_tokens: set) -> list[Unit]:
    t = unicodedata.normalize("NFKC", text or "").replace("’", "'").replace("‘", "'")
    t = t.replace("—", " ").replace("–", " ").replace("−", "-")
    out: list[Unit] = []
    for m in _TOKEN_RE.finditer(t):
        g = m.lastgroup
        s = m.group(0)
        if g in ("money", "time", "ord", "frac", "num"):
            out.append(_num_units(s, g, False))
        elif g == "sym":
            reads = SYMBOL_READINGS.get(s)
            out.append(Unit(s, "", "symbol", _concat_words(reads) if reads else None, rule="symbol_reading",
                            why="" if reads else "symbol_unsupported"))
        elif g == "dotted":
            letters = re.sub(r"[^A-Za-z]", "", s)
            out.append(Unit(s, letters.lower(), "acronym", _letters_prons(letters), rule="acronym_letters"))
        else:
            w = s
            has_dot = w.endswith(".")
            core = w.rstrip(".")
            low = core.lower()
            if low.endswith("'") and len(low) > 1 and low[-2] != "s":
                low = low.rstrip("'")
            is_caps = core.isupper() and len(core) >= 2 and core.isalpha()
            if low in ABBREVIATIONS and (low not in _ABBR_NEEDS_DOT_OR_CAPS or has_dot or is_caps):
                out.append(Unit(core, _surface_key(core), "abbrev", _concat_words(ABBREVIATIONS[low]),
                                 rep_prons=None, rule="abbreviation"))
                continue
            if is_caps and core.isalpha() and not _hp._phone_variants(low):
                # 大文字のみ・辞書に語として無い(AI/FBI/SQL等)= 文字読み
                out.append(Unit(core, low, "acronym", _letters_prons(core), rule="acronym_letters"))
                continue
            if is_caps and len(core) <= 5:
                lp = _letters_prons(core)
                wp = _word_prons(low)
                ps = (lp or set()) | (wp or set())
                out.append(Unit(core, low, "acronym", ps or None, rule="acronym_letters_or_word"))
                continue
            ent = low in entity_tokens
            prons = _word_prons(low, representative=ent)
            rule = "cmu_word"
            exp = _val_contractions().get(low)
            if exp:
                # 承認済み標準contraction(否定保持/非否定。val.expand_standard_contractionsと同一表)の展開形も読みの候補にする
                alt = _concat_words([exp.split()], representative=ent)
                if alt:
                    prons = (prons or set()) | alt
                    rule = "contraction_expand"
            out.append(Unit(core, _surface_key(core), "word", prons, rep_prons=_word_prons(low, True), rule=rule,
                            why="" if prons else "cmu_unregistered"))
    return out


# ---------------------------------------------------------------- 比較
@dataclass
class SpanRecord:
    canon_span: list
    asr_span: list
    equivalent: bool
    rule: str
    why: str = ""


@dataclass
class EquivalenceResult:
    equivalent: bool
    reason: str
    spans: list = field(default_factory=list)       # list[SpanRecord](監査: 適用した同音ルール)
    rules: list = field(default_factory=list)       # 適用ルール名(重複除去)
    canon_units: list = field(default_factory=list)
    asr_units: list = field(default_factory=list)
    contraction_expanded: bool = False
    version: str = LAYER_VERSION

    def audit(self) -> dict:
        return {"version": self.version, "equivalent": self.equivalent, "reason": self.reason,
                "rules": list(self.rules), "contraction_expanded": self.contraction_expanded,
                "spans": [{"canon": r.canon_span, "asr": r.asr_span, "equivalent": r.equivalent, "rule": r.rule,
                           "why": r.why} for r in self.spans]}


def _joint(units: list[Unit], representative: bool) -> set | None:
    sets = []
    for u in units:
        s = (u.rep_prons if representative and u.rep_prons else u.prons)
        if representative and u.kind in ("number", "symbol", "abbrev", "acronym"):
            s = u.prons      # 記号・数・略語は固定の閉じた候補(代表縮退しない)
        if not s:
            return None
        sets.append(s)
    n = 1
    for s in sets:
        n *= len(s)
    if n > MAX_JOINT:
        return None
    return {tuple(x for part in combo for x in part) for combo in itertools.product(*sets)}


def _span_rule(cu: list[Unit], au: list[Unit]) -> str:
    kinds = {u.kind for u in cu + au}
    for k, name in (("number", "number_spoken_form"), ("symbol", "symbol_reading"), ("abbrev", "abbreviation"),
                    ("acronym", "acronym_letters")):
        if k in kinds:
            return name
    if len(cu) != len(au):
        return "word_boundary_cmu_equal"
    return "cmu_homophone"


def _letters(units: list[Unit]) -> str:
    return "".join(re.sub(r"[^a-z]", "", u.surface.lower()) for u in units)


def _judge_span(c_span: list[Unit], a_span: list[Unit], representative_only: bool, entity_tokens: set):
    """1つの差spanの判定 -> (同値?, rule, why)。
    語だけのspanは承認済みの既存条件を超えない: 同数(n:n)は『位置ごとのCMU同音』(既存1:1同音救済と同じ単位)、
    個数が違うとき(1:n)は ①綴り連結が一致(複合語の分かち書き差=承認済みdespaced規則) または ②er094(PNMH-01承認済み多語同音条件)の純関数。
    数・記号・略語・頭字語を含むspanは、閉じた読み表から作った音素列集合の交差で判定する。"""
    all_words = all(u.kind == "word" and u.rule != "contraction_expand" for u in c_span + a_span)
    if all_words:
        if len(c_span) == len(a_span):
            for cu_, au_ in zip(c_span, a_span):
                vc = _joint([cu_], representative_only) or _joint([cu_], True)
                va = _joint([au_], representative_only) or _joint([au_], True)
                if vc is None or va is None:
                    return False, "incomparable", "incomparable(variant過多)"
                if not (vc & va):
                    return False, "cmu_homophone", "phoneme_differs"
            return True, "cmu_homophone", "phoneme_equal"
        if _letters(c_span) == _letters(a_span):
            # 複合語の分かち書き・ハイフン位置の差のみ(綴り連結が同一)。承認済みdespaced規則と同じ基準
            vc, va = _joint(c_span, False), _joint(a_span, False)
            if vc is not None and va is not None and not (vc & va):
                return False, "compound_spacing", "phoneme_differs"
            return True, "compound_spacing", "letters_equal_and_phoneme_compatible"
        import er094_multiword_homophone_01 as _mw   # 承認済み多語同音条件をそのまま再利用(再実装しない)
        toks_c = [u.surface.lower() for u in c_span]
        toks_a = [u.surface.lower() for u in a_span]
        ent = all(u.surface.lower() in entity_tokens or u.surface in entity_tokens for u in c_span)
        if _mw.multiword_span_equivalent_v3(toks_c, toks_a, ent):
            return True, "multiword_homophone_er094", "er094_conditions_and_phoneme_equal"
        return False, "multiword", "outside_approved_multiword_conditions_or_phoneme_differs"
    vc = _joint(c_span, representative_only) or _joint(c_span, True)
    va = _joint(a_span, representative_only) or _joint(a_span, True)
    if vc is None or va is None:
        return False, "incomparable", "incomparable(variant過多)"
    rule = _span_rule(c_span, a_span)
    ok = bool(vc & va)
    return ok, rule, "phoneme_equal" if ok else "phoneme_differs"


def evaluate(canonical: str, asr: str, *, representative_only: bool = False) -> EquivalenceResult:
    """canonical(期待文)とasr(転写)が『発音として同値』かを判定する純関数。
    representative_only=True: 全wordを代表発音(CMU先頭variant)のみで比較(より厳格。設計比較用)。"""
    if asr is None or canonical is None:
        return EquivalenceResult(False, "none_input")
    import er006_preprod_hardening_01_validation as val   # 遅延import(循環回避。純関数のみ使用)
    c_text, a_text = canonical, asr
    expanded = False
    entity_tokens = set()
    try:
        entity_tokens = set(val.capitalized_flags(canonical)) | set(val.loanword_flags(canonical))
    except Exception:
        pass
    cu, au = _units(c_text, entity_tokens), _units(a_text, entity_tokens)
    if not cu or not au:
        return EquivalenceResult(False, "empty_units", canon_units=cu, asr_units=au)
    ck = [u.key or u.surface for u in cu]
    ak = [u.key or u.surface for u in au]
    sm = difflib.SequenceMatcher(None, ck, ak, autojunk=False)
    res = EquivalenceResult(False, "", contraction_expanded=expanded, canon_units=cu, asr_units=au)
    n_diff = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        n_diff += 1
        c_span, a_span = cu[i1:i2], au[j1:j2]
        cs, as_ = [u.surface for u in c_span], [u.surface for u in a_span]
        if not c_span or not a_span:
            res.spans.append(SpanRecord(cs, as_, False, "insert_or_delete", "one_side_empty"))
            res.reason = "one_side_empty(欠落・付加は同値にしない)"
            return res
        if len(c_span) > MAX_UNITS_PER_SIDE or len(a_span) > MAX_UNITS_PER_SIDE:
            res.spans.append(SpanRecord(cs, as_, False, "too_long", "span_too_long"))
            res.reason = "span_too_long"
            return res
        bad = [u for u in c_span + a_span if not u.prons]
        if bad:
            res.spans.append(SpanRecord(cs, as_, False, "incomparable", ",".join(sorted({u.why or u.kind for u in bad}))))
            res.reason = "incomparable(CMU未登録/解析不能のため同値化しない)"
            return res
        ok, rule, why = _judge_span(c_span, a_span, representative_only, entity_tokens)
        res.spans.append(SpanRecord(cs, as_, ok, rule, why))
        if not ok:
            res.reason = why
            return res
        if rule not in res.rules:
            res.rules.append(rule)
    if n_diff == 0:
        res.equivalent = True
        res.reason = "surface_equal_after_normalization"
        return res
    res.equivalent = True
    res.reason = "all_diff_spans_phoneme_equal"
    return res
