# ============================================================
# er109_asr_orthographic_equivalence_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01 (2026-10-22) 未配線プロトタイプ。
# Status: APPROVED_FOR_PRODUCTION(ユーザー正式決定2026-10-23、Family X/Zのみ・A/B/C対象外)。Production配線=er109_xz_scope_01(X/Z run scope内でのみ有効)。
#         WIRED_PENDING_FABLE(委任_04、Fable受入前)。本moduleは純関数のまま(scope/stateを持たない)。
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

# ---- 単一flag(正式採用後の戻しスイッチ。読取は er109_xz_scope_01.is_active_for_run() 経由のみ=X/Z run scope内でのみ有効。env/引数/設定dictから変えられない) ----
# rollback: Falseにすると X/Zでも従来判定へ戻る(注意: X/Z内でer109受理されたStore entryは再利用ブロックされ再生成費用が出る)。
ORTHOGRAPHIC_EQUIVALENCE_ENABLED = True
# ②英米綴り層(UKUS、APPROVED_FOR_PRODUCTION 2026-10-23 UDR #168)のrollbackスイッチ。親flag(上)がFalseなら本層も不活性。
# 読取は er109_xz_scope_01.is_ukus_active_for_run() 経由のみ(X/Z run scope内)。env/引数/設定dictから変えられない。evaluate(ukus=...)は _evaluate_cached だけが渡す(AST test)。
# rollback: Falseにすると X/Zでも従来(v1)判定へ戻る(UKUSで受理済みStore entryは再利用ブロック→再生成費用が出る)。
UKUS_SPELLING_EQUIVALENCE_ENABLED = True
LAYER_VERSION = "er109_orthographic_equivalence_v2_ukus01"
STRESS_MODE = "binary_stressed_vs_unstressed"   # P-01: 強勢は有/無の2値で比較(1,2->1, 0->0)。除去しない


def is_enabled() -> bool:
    """単一flag読取関数(er109_xz_scope_01.is_active_for_run()だけが呼ぶ)。"""
    return bool(ORTHOGRAPHIC_EQUIVALENCE_ENABLED)


def ukus_is_enabled() -> bool:
    """UKUS層のflag読取関数(er109_xz_scope_01.is_ukus_active_for_run()だけが呼ぶ)。親flagがFalseなら常にFalse。"""
    return bool(UKUS_SPELLING_EQUIVALENCE_ENABLED) and is_enabled()


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
    "°": [["degrees"], ["degree"]],
}
# P-04: 複数の別語へ展開される記号・略語はfail-closed(同じ語の活用違い[degree/degrees, minute/minutes, foot/feet]だけ許す)
AMBIGUOUS_SYMBOLS = {"#"}            # number / hash / pound
AMBIGUOUS_ABBREVIATIONS = {"st", "dr", "mt"}   # saint/street, doctor/drive, mount/mountain
CURRENCY_SYMBOLS = {"$": ("dollar", "dollars", "cent", "cents"), "£": ("pound", "pounds", "penny", "pence"),
                    "€": ("euro", "euros", "cent", "cents")}
# 略語(語単位)。ambiguous語(dr=doctor/drive, st=saint/street)は候補を複数持つ(どれか1つが相手と一致すれば同値)。
ABBREVIATIONS = {
    "mr": [["mister"]], "mrs": [["missus"], ["misses"]], "ms": [["miz"], ["mizz"]], 
    "jr": [["junior"]], "sr": [["senior"]], "vs": [["versus"]], "v": [["versus"]],
    "inc": [["incorporated"]], "co": [["company"]], "ltd": [["limited"]], "corp": [["corporation"]],
    "ok": [["okay"]], "approx": [["approximately"]], "dept": [["department"]], "govt": [["government"]],
    "etc": [["et", "cetera"], ["etcetera"]], "ave": [["avenue"]], "blvd": [["boulevard"]], "rd": [["road"]],
    "ft": [["feet"], ["foot"]], "lb": [["pounds"], ["pound"]], "lbs": [["pounds"]],
    "oz": [["ounces"], ["ounce"]], "min": [["minutes"], ["minute"]], "sec": [["seconds"], ["second"]],
    "hr": [["hour"], ["hours"]], "hrs": [["hours"]], "km": [["kilometers"], ["kilometres"]],
    "kg": [["kilograms"], ["kilogram"]], "mph": [["miles", "per", "hour"]]
}
# 句読点付きだけ略語とみなす語(通常語と衝突する): min/sec/hr/v/co/ft/mt/ok 等は『ピリオド付き』か『大文字のみ』のとき限定
_ABBR_NEEDS_DOT_OR_CAPS = {"min", "sec", "hr", "v", "co", "ft", "lb", "oz", "ms", "ave", "rd", "sr", "jr", "inc"}
_LETTER_NAMES = {   # CMUの文字名(2値強勢)。aのみ強勢読み(EY1)を明示
    "a": "EY1", "b": "B IY1", "c": "S IY1", "d": "D IY1", "e": "IY1", "f": "EH1 F", "g": "JH IY1", "h": "EY1 CH", "i": "AY1",
    "j": "JH EY1", "k": "K EY1", "l": "EH1 L", "m": "EH1 M", "n": "EH1 N", "o": "OW1", "p": "P IY1", "q": "K Y UW1",
    "r": "AA1 R", "s": "EH1 S", "t": "T IY1", "u": "Y UW1", "v": "V IY1", "w": "D AH1 B AH0 L Y UW0", "x": "EH1 K S",
    "y": "W AY1", "z": "Z IY1",
}
_FRACTIONS = {(1, 2): [["one", "half"], ["a", "half"]], (1, 3): [["one", "third"]], (2, 3): [["two", "thirds"]],
              (1, 4): [["one", "quarter"], ["one", "fourth"]], (3, 4): [["three", "quarters"], ["three", "fourths"]]}

# ---------------------------------------------------------------- unit
@dataclass
class Unit:
    surface: str
    key: str
    kind: str                       # word | number | symbol | abbrev | acronym | unknown
    prons: set | None               # set[tuple[str,...]] 音素列(強勢2値)。None=判定不能。語unitは『強勢読みのみ』
    rep_prons: set | None = None    # 代表発音のみ(固有名詞・variant爆発時の縮退用)
    rule: str = ""
    why: str = ""
    own_strong: set | None = None   # 語unitの『自分自身のCMU強勢読み』(contraction展開を含まない)
    rep_strong: tuple | None = None # 語unitの代表(先頭)強勢読み
    exp_strong: set | None = None   # contraction展開(承認済み標準表)の強勢読み
    all_prons: set | None = None    # 語unitの全読み(弱形含む。承認済みdespaced規則[綴り連結一致]の判定専用)


def _strip_stress(ph: str) -> tuple:
    """P-01: 強勢を除去せず2値化(AH1/AH2->AH1, AH0->AH0)。billow(B IH1 L OW0)とbelow(B IH0 L OW1)は別物のまま。"""
    return _hp._stress2_tokens(ph)


def _is_stressed_reading(r: tuple) -> bool:
    return _hp._has_stressed_vowel(r)


def _strong(ps):
    """P-02: 強勢母音を含む読みだけ(弱形のみの読み[are=ER0等]での一致を許さない)。"""
    return {r for r in (ps or ()) if _is_stressed_reading(r)}


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
            s = _strong(_word_prons(w, representative))
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


def _word_key(s: str) -> str:
    """語unitの整列key。アポストロフィを残す(we're/were, I'll/ill, he'll/hell, we'd/wed を『表層が同じ』と誤認しない)。"""
    return re.sub(r"[^a-z0-9']+", "", unicodedata.normalize("NFKC", s).lower().replace("’", "'")).strip("'")


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
            # 委任_05 是正: 裸の数詞(three)は「3:00」と同値にしない(発音が異なる=three o'clockと三。fail-closed)。
            # 時刻表記は o'clock を伴う読みのみ。meridiem付きは「hour + a m/p m」(meridiem文字を伴うので裸ではない)
            cands = [hw + ["o'clock"]] if not mer else [hw]
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
            why = "" if reads else ("ambiguous_symbol(#)" if s in AMBIGUOUS_SYMBOLS else "symbol_unsupported")
            out.append(Unit(s, "", "symbol", _concat_words(reads) if reads else None, rule="symbol_reading", why=why))
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
            if low in AMBIGUOUS_ABBREVIATIONS and (has_dot or is_caps):
                out.append(Unit(core, _surface_key(core), "abbrev", None, rule="abbreviation", why="ambiguous_abbreviation(St/Dr/Mt)"))
                continue
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
                wp = _strong(_word_prons(low, True))     # P-04: 文字読み+代表発音のみ(CMUの展開variantは除外)
                ps = (lp or set()) | (wp or set())
                out.append(Unit(core, low, "acronym", ps or None, rule="acronym_letters_or_word"))
                continue
            ent = low in entity_tokens
            if len(low) >= 2 and not re.search(r"[aeiouy]", low):
                # P-04: 母音字の無い綴り(tv/st/dr/mt/ft等)は略語であり、CMUが誤って付ける展開variant(tv->television)を使わない
                out.append(Unit(core, _surface_key(core), "word", None, rule="cmu_word", why="vowelless_token_abbreviation_like"))
                continue
            all_p = _word_prons(low, representative=False)
            own = _strong(_word_prons(low, representative=ent))
            rep_p = _strong(_word_prons(low, representative=True))
            rule = "cmu_word"
            exp = _val_contractions().get(low)
            exp_set = set()
            if exp:
                # 承認済み標準contraction(否定保持/非否定。val.expand_standard_contractionsと同一表)の展開形(閉じた表なのでentityでも使う)
                alt = _concat_words([exp.split()], representative=ent)
                if alt:
                    exp_set = set(alt)
                    rule = "contraction_expand"
            out.append(Unit(core, _word_key(core), "word", None, rep_prons=rep_p or None, rule=rule,
                            why="" if (own or exp_set) else "cmu_unregistered_or_no_strong_reading",
                            own_strong=own, rep_strong=_hp.representative_strong_reading(low), exp_strong=exp_set,
                            all_prons=all_p))
            out[-1].prons = (own | exp_set) or None
    return out


# ---------------------------------------------------------------- 比較
NEGATION_WORDS = {"not", "no", "never", "none", "nobody", "nothing", "neither", "nor", "cannot", "without", "nowhere"}


def _build_number_vocab() -> frozenset:
    """P-07: 数・記号を含むspanに混ざってよい『数の読み語彙』(基数・序数・位取り・and/point/oh/percent/通貨・時刻・分数・記号/略語の展開語・文字名)。"""
    v: set = set(_ONES) | {t for t in _TENS if t} | {"hundred", "thousand", "million", "billion", "trillion", "and", "point", "oh",
        "zero", "minus", "negative", "percent", "o'clock", "half", "quarter", "quarters", "thirds", "third", "fourth", "fourths",
        "a", "am", "pm", "plus", "equals", "equal", "at", "per", "hour", "dollar", "dollars", "cent", "cents", "pound", "pounds",
        "penny", "pence", "euro", "euros", "degree", "degrees"}
    for n in list(range(0, 1001)) + [1100, 2000, 10 ** 6]:
        for w in cardinal_variants(n):
            v.update(w)
            v.update(_ordinal_of_words(w))
    for exps in ABBREVIATIONS.values():
        for e in exps:
            v.update(e)
    v.update(_LETTER_NAMES.keys())
    for rs in SYMBOL_READINGS.values():
        for e in rs:
            v.update(e)
    return frozenset(v)


_TENS_PLURALS = frozenset(t[:-1] + "ies" for t in _TENS if t)    # twenties..nineties(年代)
_NUMBER_VOCAB = _build_number_vocab()
_VOCAB_HOMOPHONE_CACHE: dict = {}


def _in_number_vocab(u: "Unit") -> bool:
    w = u.surface.lower().rstrip(".")
    if w.endswith("'s"):
        w = w[:-2]                       # one's / two's(数+'s)
    if w in _NUMBER_VOCAB or w in _TENS_PLURALS:
        return True
    if "-" in w and all(p in _NUMBER_VOCAB or p in _TENS_PLURALS for p in w.split("-") if p):
        return True                       # twenty-eight / thirty-first(複合数詞)
    # 数詞と同音の普通の語(to/too->two, for->four, won->one, ate->eight)。strict(canonical=語彙語, asr=その語)
    if w not in _VOCAB_HOMOPHONE_CACHE:
        _VOCAB_HOMOPHONE_CACHE[w] = any(
            _hp.strict_homophone_pair(v, w) for v in _NUMBER_VOCAB if len(v) > 1 and v.isalpha())
    return _VOCAB_HOMOPHONE_CACHE[w]


@dataclass
class SpanRecord:
    canon_span: list
    asr_span: list
    equivalent: bool
    rule: str
    why: str = ""
    matched: list = field(default_factory=list)         # 一致した読み(最大3、音素列文字列)
    representative_match: bool | None = None            # 代表発音同士でも一致したか(False=非代表variantのみ=警告)
    heteronym_guard: bool = False                       # 同形異音語ガード(P-03)を適用した語unitがあったか
    warnings: list = field(default_factory=list)


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
    warnings: list = field(default_factory=list)    # P-08: 空=警告なし。非空=PASS_WITH_WARNING+事後試聴の対象
    ukus_pairs: list = field(default_factory=list)  # UKUS層で同値化した位置の記録(空=UKUS寄与なし。warningsには入れない)
    ukus_error: str = ""                            # UKUS層の例外(fail-closed: v1判定へ戻る)。空=なし

    @property
    def verdict(self) -> str:
        if not self.equivalent:
            return "NOT_EQUIVALENT"
        return "PASS_WITH_WARNING" if self.warnings else "PASS"

    def audit(self) -> dict:
        d = self._audit_base()
        if self.ukus_pairs:                          # UKUS適用時のみ追加(非UKUS行のauditはversion文字列を除き不変)
            d["ukus_pairs"] = [dict(p) for p in self.ukus_pairs]
            d["ukus_pairs_n"] = len(self.ukus_pairs)
            d["pron_differs_n"] = sum(1 for p in self.ukus_pairs if p.get("pron_differs"))
            import er109_ukus_spelling_01 as _uk
            d["ukus_active"] = True
            d["ukus_table_sha256"] = _uk.PAIRS_CANONICAL_SHA256       # W-07: 適用時のみ(非UKUS行の署名は不変)
        if self.ukus_error:
            d["ukus_error"] = self.ukus_error
        return d

    def _audit_base(self) -> dict:
        return {"version": self.version, "flag_enabled": is_enabled(), "stress_mode": STRESS_MODE,
                "equivalent": self.equivalent, "verdict": self.verdict, "reason": self.reason,
                "rules": list(self.rules), "warnings": list(self.warnings), "contraction_expanded": self.contraction_expanded,
                "spans": [{"canon": r.canon_span, "asr": r.asr_span, "equivalent": r.equivalent, "rule": r.rule,
                           "why": r.why, "matched_variants": r.matched, "representative_match": r.representative_match,
                           "heteronym_guard": r.heteronym_guard, "warnings": r.warnings} for r in self.spans]}


def _unit_set(u: Unit, side: str, mode: str, representative_only: bool = False, numeric_ctx: bool = False,
              exp_only: bool = False) -> set | None:
    """unitの読み候補。mode='policy': 語unitにP-02/P-03を適用
         canonical側: 強勢読みが『ただ1つ』の語だけ(同形異音語は不可)。ASR側: 代表(先頭)強勢読みのみ。
         contraction unitは自身のCMU読み(同上)に承認済み展開の読みを加える。
       mode='loose': 強勢読みのすべて(承認済みdespaced規則=綴り連結一致の判定用)。
       mode='rep': 両側とも代表強勢読みのみ(警告判定=非代表variantでしか一致しないか)。
    数・記号・略語・頭字語は閉じた表から作った固定の読み(モードに依らない)。"""
    if u.kind != "word":
        return u.prons
    own = u.own_strong or set()
    exp = u.exp_strong or set()
    _sl = u.surface.lower().rstrip(".")
    if numeric_ctx and (_sl in _NUMBER_VOCAB or _sl in _TENS_PLURALS or (_sl.endswith("'s") and _sl[:-2] in _NUMBER_VOCAB)
                        or ("-" in _sl and all(p in _NUMBER_VOCAB for p in _sl.split("-") if p))):
        # 数の読み語彙そのもの(twenty/first/and/dollars等)は同形異音語ではなく弱化variantのみ=強勢読みすべてを使う
        return (own | exp) or None
    if mode == "loose":
        return ((u.all_prons or own) | exp) or None
    rep = {u.rep_strong} if u.rep_strong else set()
    if exp_only and exp:
        # 個数の違う語span(1:n/n:m)ではcontractionは承認済みの展開形としてのみ使う(自身のCMU読みで語境界をまたがない:
        # corbeil<->korb i'll 型の誤同値を防ぐ)
        return exp
    if mode == "rep":
        return ((rep & own) | exp) or None
    if side == "c":
        base = own if len(own) == 1 else set()
        if representative_only:
            base = base & rep
    else:
        base = rep & own
    return (base | exp) or None


def _joint(units: list[Unit], side: str, mode: str, representative_only: bool = False, numeric_ctx: bool = False,
           exp_only: bool = False) -> set | None:
    sets = []
    for u in units:
        s_ = _unit_set(u, side, mode, representative_only, numeric_ctx, exp_only)
        if not s_:
            return None
        sets.append(s_)
    n = 1
    for s_ in sets:
        n *= len(s_)
    if n > MAX_JOINT:
        return None
    return {tuple(x for part in combo for x in part) for combo in itertools.product(*sets)}


def _span_rule(cu: list[Unit], au: list[Unit]) -> str:
    kinds = {u.kind for u in cu + au}
    for k, name in (("number", "number_spoken_form"), ("symbol", "symbol_reading"), ("abbrev", "abbreviation"),
                    ("acronym", "acronym_letters")):
        if k in kinds:
            return name
    if any(u.rule == "contraction_expand" for u in cu + au):
        return "contraction_or_homophone"
    if len(cu) != len(au):
        return "word_boundary_cmu_equal"
    return "cmu_homophone"


def _letters(units: list[Unit]) -> str:
    return "".join(re.sub(r"[^a-z]", "", u.surface.lower()) for u in units)


def _span_warnings(c_span, a_span, rep_ok: bool | None) -> list:
    w = []
    surf = [u.surface.lower() for u in c_span + a_span]
    if any(x in NEGATION_WORDS or x.endswith("n't") for x in surf):
        w.append("negation_word_homophone")
    if rep_ok is False:
        w.append("non_representative_variant_match")
    return w


def _fmt(t: tuple) -> str:
    return " ".join(t)


def _judge_span(c_span: list[Unit], a_span: list[Unit], representative_only: bool, entity_tokens: set) -> SpanRecord:
    cs, as_ = [u.surface for u in c_span], [u.surface for u in a_span]
    rec = SpanRecord(cs, as_, False, "", "")
    plain = [u for u in c_span + a_span if u.kind == "word"]
    non_word = [u for u in c_span + a_span if u.kind != "word"]
    rec.heteronym_guard = any(u.rule == "cmu_word" for u in plain)
    # P-07: 数・記号・略語・頭字語を含むspanに混ざる普通の語は数の読み語彙(とその同音語)に限る
    if non_word:
        stray = [u.surface for u in plain if not _in_number_vocab(u)]
        if stray:
            rec.rule, rec.why = _span_rule(c_span, a_span), "ordinary_word_in_numeric_span:" + ",".join(stray)
            return rec
    all_words = all(u.kind == "word" and u.rule != "contraction_expand" for u in c_span + a_span)
    if all_words and len(c_span) != len(a_span):
        if _letters(c_span) == _letters(a_span):
            # 複合語の分かち書き・ハイフン位置の差のみ(綴り連結が同一)。承認済みdespaced規則と同じ基準(variantは全強勢読み)
            vc, va = _joint(c_span, "c", "loose"), _joint(a_span, "a", "loose")
            rec.rule = "compound_spacing"
            if vc is not None and va is not None and not (vc & va):
                rec.why = "phoneme_differs"
                return rec
            rec.equivalent, rec.why = True, "letters_equal_and_phoneme_compatible"
            return rec
        import er006_preprod_hardening_01_validation as _val   # 承認済み多語同音条件(PNMH-01)を、valが保持する同一moduleからそのまま再利用(再実装しない。
        _mw = _val._mw_homophone                                # er094を直接importするのはvalだけ=er094 StaticChecksの『valのみimport』を保つ)
        toks_c = [u.surface.lower() for u in c_span]
        toks_a = [u.surface.lower() for u in a_span]
        ent = all(u.surface.lower() in entity_tokens or u.surface in entity_tokens for u in c_span)
        rec.rule = "multiword_homophone_er094"
        if _mw.multiword_span_equivalent_v3(toks_c, toks_a, ent):
            rec.equivalent, rec.why = True, "er094_conditions_and_phoneme_equal"
            rec.warnings = _span_warnings(c_span, a_span, None)
        else:
            rec.why = "outside_approved_multiword_conditions_or_phoneme_differs"
        return rec
    rec.rule = _span_rule(c_span, a_span)
    if len(c_span) == len(a_span) and all(u.kind == "word" for u in c_span + a_span):
        # 同数の語span: 位置ごとに判定(既存1:1同音救済と同じ単位。語境界をまたぐ連結をさせない)
        for cu_, au_ in zip(c_span, a_span):
            if len(cu_.surface.rstrip(".")) == 1 or len(au_.surface.rstrip(".")) == 1:
                rec.why = "single_letter_token_not_equalized"      # tea<->T 等。文字読みの同値は頭字語spanでのみ扱う
                return rec
            vc = _joint([cu_], "c", "policy", representative_only)
            va = _joint([au_], "a", "policy", representative_only)
            if vc is None or va is None:
                rec.why = "incomparable(同形異音語/強勢読み無し)"
                return rec
            if not (vc & va):
                rec.why = "phoneme_differs"
                return rec
            rec.matched.append(_fmt(sorted(vc & va)[0]))
        vcr = [_joint([x], "c", "rep") for x in c_span]
        var = [_joint([x], "a", "rep") for x in a_span]
        rec.representative_match = all(a1 and b1 and (a1 & b1) for a1, b1 in zip(vcr, var))
        rec.equivalent, rec.why = True, "phoneme_equal"
        rec.warnings = _span_warnings(c_span, a_span, rec.representative_match)
        return rec
    nctx = any(u.kind in ("number", "symbol") for u in non_word)   # 数読み語彙のloose化は数・記号spanだけ(略語/頭字語spanでは使わない)
    eo = (not non_word) and len(c_span) != len(a_span)             # 語だけで個数が違うspan: contractionは展開形のみ
    vc = _joint(c_span, "c", "policy", representative_only, nctx, eo)
    va = _joint(a_span, "a", "policy", representative_only, nctx, eo)
    if vc is None or va is None:
        rec.why = "incomparable(同形異音語/variant過多/強勢読み無し)"
        return rec
    common = vc & va
    if not common:
        rec.why = "phoneme_differs"
        return rec
    rec.matched = [_fmt(x) for x in sorted(common)[:3]]
    vcr, var = _joint(c_span, "c", "rep", numeric_ctx=nctx, exp_only=eo), _joint(a_span, "a", "rep", numeric_ctx=nctx, exp_only=eo)
    rec.representative_match = bool(vcr and var and (vcr & var))
    rec.equivalent, rec.why = True, "phoneme_equal"
    rec.warnings = _span_warnings(c_span, a_span, rec.representative_match)
    return rec


def evaluate(canonical: str, asr: str, *, representative_only: bool = False, ukus: bool = False) -> EquivalenceResult:
    """canonical(期待文)とasr(転写)が『発音として同値』かを判定する純関数。
    representative_only=True: canonical側も代表強勢読みのみで比較(より厳格。設計比較用)。
    ukus=True: 既存判定が不合格になった『同数・全unitがword』のspanだけ、固定対表(er109_ukus_spelling_01)で位置別に英米綴り差を救済する。
      既存判定が合格するspanには触れない(PASS->NG 0)。救済不成立なら ukus=False と同一のNG記録。既定False(従来)。呼出はer109_xz_scope_01._evaluate_cachedのみ(AST test)。"""
    if asr is None or canonical is None:
        return EquivalenceResult(False, "none_input")
    import er006_preprod_hardening_01_validation as val   # 遅延import(循環回避。純関数のみ使用)
    c_text, a_text = canonical, asr
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
    res = EquivalenceResult(False, "", canon_units=cu, asr_units=au)
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
        rec = None if bad else _judge_span(c_span, a_span, representative_only, entity_tokens)
        if ukus and (bad or not rec.equivalent):
            # UKUS救済(既存判定が不合格のspanだけ。合格spanには触れない)。例外はfail-closed(v1判定のNG記録へ戻る)。
            try:
                import er109_ukus_spelling_01 as _uk
                resc = _uk.rescue_span(canonical, len(cu), i1, c_span, a_span, representative_only, entity_tokens)
            except Exception as exc:  # noqa: BLE001
                resc = None
                res.ukus_error = f"{type(exc).__name__}: {exc}"
            if resc is not None:
                recs, pairs, wns = resc
                res.spans.extend(recs)
                if _uk.RULE_NAME not in res.rules:
                    res.rules.append(_uk.RULE_NAME)
                for r_ in recs:
                    if r_.rule not in res.rules:
                        res.rules.append(r_.rule)
                res.ukus_pairs.extend(pairs)
                for w in wns:
                    if w not in res.warnings:
                        res.warnings.append(w)
                continue
        if bad:
            res.spans.append(SpanRecord(cs, as_, False, "incomparable", ",".join(sorted({u.why or u.kind for u in bad}))))
            res.reason = "incomparable(CMU未登録/解析不能/曖昧略語のため同値化しない)"
            return res
        res.spans.append(rec)
        if not rec.equivalent:
            res.reason = rec.why
            return res
        if rec.rule not in res.rules:
            res.rules.append(rec.rule)
        for w in rec.warnings:
            if w not in res.warnings:
                res.warnings.append(w)
    if n_diff == 0:
        res.equivalent = True
        res.reason = "surface_equal_after_normalization"
        return res
    res.equivalent = True
    res.reason = "all_diff_spans_phoneme_equal_or_ukus_variant" if res.ukus_pairs else "all_diff_spans_phoneme_equal"
    return res
