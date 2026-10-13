# ============================================================
# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01 Trial module (DEV/Trial専用)
# Production (er007_ja_asr_validator_01 / er011_ja_asr_variant_layer_01 / er003_*) からは
# 一切importされない。新自動PASS条件の候補であり、ユーザー承認(APPROVED_FOR_PRODUCTION)
# までProductionへ入れてはならない(USER_DECISION_REQUIRED)。
#
# 構成: (i)表記正規化層(数値+助数詞/単位 -> 「値」と「読み」) +
#       (ii)読み等価判定(読み展開後に既存Production判定=pykakasi/fugashi系へ委譲) +
#       (iii)安全条件(値不一致/助数詞違い/否定/別語/曖昧語は不許容、追加型=既存PASSは変更しない)
# 費用: ¥0(ASR再呼出なし、API不使用)
# ============================================================
from __future__ import annotations

import itertools
import re
import unicodedata
from dataclasses import dataclass, field

import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as variant

# ---------------- (i) 数値スパン抽出 ----------------
_KD = "〇零一二三四五六七八九十百千万"
# 02: 桁区切りは3桁区切り(1,000 / 12,345,678)のみ受理する。NFKCで全角「，」が半角「,」になるため
# 「3，4日」(列挙)を「34日」と読む誤PASS経路を塞ぐ(Opus推奨)。
_NUM_RE = r"(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?[万千百]?|\d+(?:\.\d+)?[万千百]?|[" + _KD + r"]+)"

# counter_id -> surfaces。ここに無い助数詞は一切変換しない(fail-safe)。
COUNTERS = {
    "day_span": ["日間"], "day": ["日"], "person": ["人"],
    "hour_span": ["時間"], "hour": ["時"], "minute": ["分"], "second": ["秒"],
    "month": ["月"], "month_span": ["か月", "ヶ月", "ヵ月", "カ月", "ケ月"],
    "year_span": ["年間"], "year": ["年"], "age": ["歳", "才"],
    "kai": ["回"], "ken": ["件"], "tsu": ["つ"], "haku": ["泊"], "week": ["週間", "週"],
    "yen": ["円"], "percent": ["%", "パーセント"], "ko": ["個"], "hon": ["本"],
    "gen": ["代"], "floor": ["階"], "ban": ["番"], "go": ["号"], "mai": ["枚"], "dai": ["台"], "bai": ["倍"], "do": ["度"], "km": ["キロ", "km"],
}
_SURF2ID = {s: cid for cid, ss in COUNTERS.items() for s in ss}
_COUNTER_RE = "|".join(re.escape(s) for s in sorted(_SURF2ID, key=len, reverse=True))
SPAN_RE = re.compile(r"(?<![A-Za-z\d,.万])(" + _NUM_RE + r")(" + _COUNTER_RE + r")")

# 語彙として別義を持つ/読みが分岐する表層。該当する文は自動救済しない(Cascade/HR温存)。
# 「三十分」等は数値表記なので除外対象外(直前が漢数字なら曖昧語ではない)。
# 02追加: 一時(いちじ/いっとき)・一月(いちがつ/ひとつき)・一分(いっぷん/いちぶ)・N分の/N分厘/N分割(ぶ読み)。
AMBIGUOUS_RE = re.compile(
    r"(?<![二三四五六七八九〇])十分|三日月"
    r"|(?<![二三四五六七八九〇十百千万])一時(?!間)"
    r"|(?<![二三四五六七八九〇十百千万])一月"
    r"|(?<![二三四五六七八九〇十百千万])一分(?!間)"
    r"|[\d〇一二三四五六七八九十百千万]分(?:の|厘|割)")


@dataclass
class Span:
    start: int
    end: int
    value: str
    counter: str
    surface: str


_KBLOCK = r"(?:[一二三四五六七八九]?千)?(?:[一二三四五六七八九]?百)?(?:[一二三四五六七八九]?十)?[一二三四五六七八九]?"
_KGRAMMAR = re.compile(r"^(?=.)(?:(?:" + _KBLOCK + r")万)?(?:" + _KBLOCK + r")$")


def _to_value(num: str):
    n = num.replace(",", "")
    if "," in num and not re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?[万千百]?", num):
        return None
    if re.fullmatch(r"\d+(\.\d+)?[万千百]?", n):
        mult = {"万": 10000, "千": 1000, "百": 100}.get(n[-1], 1)
        base = n[:-1] if n[-1] in "万千百" else n
        if "." in base:
            return base if mult == 1 else None
        return str(int(base) * mult)
    if n in ("〇", "零"):
        return None
    # 02: 漢数字は厳密な文法(千百十の順・万の前に数字)のみ受理。「万」単独(=0扱い)や「万千」等は救済対象外。
    if not _KGRAMMAR.fullmatch(n) or n.startswith("万"):
        return None
    v = variant.kanji_numeral_run_to_int(n)
    return None if (v is None or v <= 0) else str(v)


def find_spans(text: str) -> list[Span]:
    t = unicodedata.normalize("NFKC", text)
    out = []
    for m in SPAN_RE.finditer(t):
        val = _to_value(m.group(1))
        if val is None:
            continue
        out.append(Span(m.start(), m.end(), val, _SURF2ID[m.group(2)], m.group(0)))
    return out


def has_ambiguous(text: str) -> bool:
    t = unicodedata.normalize("NFKC", text)
    return bool(AMBIGUOUS_RE.search(t))


def value_form(text: str) -> str:
    """数値+助数詞スパンを <値:助数詞ID> に置換した文字列(表記差の吸収)。"""
    t = unicodedata.normalize("NFKC", text)
    res, pos = [], 0
    for s in find_spans(text):
        res.append(t[pos:s.start])
        res.append(f"<{s.value}:{s.counter}>")
        pos = s.end
    res.append(t[pos:])
    return "".join(res)


# ---------------- (ii) 読み展開 ----------------
_D = {1: "いち", 2: "に", 3: "さん", 4: "よん", 5: "ご", 6: "ろく", 7: "なな", 8: "はち", 9: "きゅう"}


def _under10000(n: int) -> str:
    out = ""
    th, rest = divmod(n, 1000)
    if th:
        out += {1: "せん", 3: "さんぜん", 8: "はっせん"}.get(th, _D[th] + "せん")
    hu, rest = divmod(rest, 100)
    if hu:
        out += {1: "ひゃく", 3: "さんびゃく", 6: "ろっぴゃく", 8: "はっぴゃく"}.get(hu, _D[hu] + "ひゃく")
    te, on = divmod(rest, 10)
    if te:
        out += "じゅう" if te == 1 else _D[te] + "じゅう"
    if on:
        out += _D[on]
    return out


def kana_int(n: int) -> str:
    if n == 0:
        return "ぜろ"
    out = ""
    oku, rest = divmod(n, 10 ** 8)
    man, rest = divmod(rest, 10000)
    if oku:
        out += _under10000(oku) + "おく"
    if man:
        out += ("いち" if man == 1 else _under10000(man)) + "まん"
    if rest:
        out += _under10000(rest)
    return out


def _sok(k: str, six: bool = True) -> str:
    """促音化。six=Falseなら6(ろく)は促音化しない(6歳ろくさい・6週間ろくしゅうかん)。"""
    for a, b in (("いち", "いっ"), ("ろく", "ろっ"), ("はち", "はっ"), ("じゅう", "じゅっ"), ("ひゃく", "ひゃっ")):
        if a == "ろく" and not six:
            continue
        if k.endswith(a):
            return k[: -len(a)] + b
    return k


def _swap_last(n: int, sub: dict) -> str | None:
    """末尾桁の慣用読み(4->よ, 7->しち, 9->く)へ差し替えた数詞読み。"""
    k = kana_int(n)
    d = n % 10
    dflt = {4: "よん", 7: "なな", 9: "きゅう"}
    if d in sub and k.endswith(dflt[d]):
        return k[: -len(dflt[d])] + sub[d]
    return None


def _cls(n: int) -> int:
    """促音化クラス: 末尾桁。10/100の倍数は0、1000の倍数は-1(促音化なし)。"""
    if n % 1000 == 0:
        return -1
    return n % 10


_DAY = {1: ["ついたち", "いちにち"], 2: ["ふつか"], 3: ["みっか"], 4: ["よっか"], 5: ["いつか"], 6: ["むいか"],
        7: ["なのか"], 8: ["ようか"], 9: ["ここのか"], 10: ["とおか"], 14: ["じゅうよっか"], 20: ["はつか"],
        24: ["にじゅうよっか"]}
_TSU = {1: "ひとつ", 2: "ふたつ", 3: "みっつ", 4: "よっつ", 5: "いつつ", 6: "むっつ", 7: "ななつ", 8: "やっつ", 9: "ここのつ", 10: "とお"}
_MONTH = {1: "いち", 2: "に", 3: "さん", 4: "し", 5: "ご", 6: "ろく", 7: "しち", 8: "はち", 9: "く", 10: "じゅう", 11: "じゅういち", 12: "じゅうに"}


def _uniq(xs):
    return list(dict.fromkeys(xs))


def _cands(n: int, c: str) -> list[str]:
    k = kana_int(n)
    d = n % 10
    if c in ("day", "day_span"):
        suf = "かん" if c == "day_span" else ""
        if n in _DAY:
            return [x + suf for x in (_DAY[n] if c == "day" else _DAY[n][:1] if n != 1 else ["いちにち"])]
        if d == 4:
            return [k[:-2] + "よっか" + suf]
        outs = [k + "にち" + suf]
        for dd, key in ((7, "しち"), (9, "く")):
            if d == dd:
                s = _swap_last(n, {dd: key})
                if s:
                    outs.append(s + "にち" + suf)
        return outs
    if c == "person":
        if n == 1:
            return ["ひとり"]
        if n == 2:
            return ["ふたり"]
        if d == 4:
            return [_swap_last(n, {4: "よ"}) + "にん"]
        outs = [k + "にん"]
        if d == 7:
            outs.append(_swap_last(n, {7: "しち"}) + "にん")
        return outs
    if c in ("hour", "hour_span"):
        suf = "じ" if c == "hour" else "じかん"
        if d == 4:
            return [_swap_last(n, {4: "よ"}) + suf]
        if d == 7:
            return [k + suf, _swap_last(n, {7: "しち"}) + suf]
        if d == 9:
            return [_swap_last(n, {9: "く"}) + suf]
        return [k + suf]
    if c in ("minute", "hon", "haku"):
        h, p = {"minute": ("ふん", "ぷん"), "hon": ("ほん", "ぽん"), "haku": ("はく", "ぱく")}[c]
        cl = _cls(n)
        if cl == -1:
            return [k + {"minute": "ぷん", "hon": "ぼん", "haku": "ぱく"}[c]]
        if cl in (1, 6, 8, 0):
            outs = [_sok(k) + p]
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
        return [_MONTH[n] + "がつ"] if n in _MONTH else []
    if c == "month_span":
        return [(_sok(k) if _cls(n) in (1, 6, 8, 0) else k) + "かげつ"]
    if c in ("year", "year_span"):
        suf = "ねん" + ("かん" if c == "year_span" else "")
        if d == 4:
            return [_swap_last(n, {4: "よ"}) + suf]
        if d == 7:
            return [k + suf, _swap_last(n, {7: "しち"}) + suf]
        if d == 9:
            return [k + suf, _swap_last(n, {9: "く"}) + suf]
        return [k + suf]
    if c in ("age", "kai", "ken", "ko", "week"):
        base = {"age": "さい", "kai": "かい", "ken": "けん", "ko": "こ", "week": "しゅうかん"}[c]
        if c == "age" and n == 20:
            return ["はたち"]
        # 02: 歳(さい)・週間(しゅうかん)は6でも促音化しない(ろくさい/ろくしゅうかん)。1/8/10/100は促音化。
        six = c not in ("age", "week")
        outs = [(_sok(k, six) if _cls(n) in (1, 6, 8, 0) else k) + base]
        if c in ("age", "week") and _cls(n) == 0:
            outs.append(k + base)  # さんじゅうさい / さんじゅっさい の両方が標準
        return outs
    if c == "tsu":
        return [_TSU[n]] if n in _TSU else []
    if c == "yen":
        if d == 4:
            return [_swap_last(n, {4: "よ"}) + "えん", k + "えん"]
        return [k + "えん"]
    if c == "percent":
        return [k + "ぱーせんと", k + "ぱあせんと"]
    if c == "floor":
        if _cls(n) == 3:
            return [k + "がい"]
        return [(_sok(k) if _cls(n) in (1, 6, 8, 0) else k) + "かい"]
    simple = {"gen": "だい", "ban": "ばん", "go": "ごう", "mai": "まい", "dai": "だい", "bai": "ばい", "do": "ど", "km": "きろ"}
    if c in simple:
        return [k + simple[c]]
    return []


_MAX_COMBOS = 24


def reading_expansions(text: str) -> list[str] | None:
    """数値スパンを全てかな読みへ展開した候補文字列(最大_MAX_COMBOS)。展開不能なスパンが
    1つでもあればNone(fail-safe=救済しない)。スパン無しなら[元の文字列]。"""
    t = unicodedata.normalize("NFKC", text)
    spans = find_spans(text)
    if not spans:
        return [t]
    lists = []
    for s in spans:
        if "." in s.value or int(s.value) > 99_999_999:
            return None
        c = _uniq(_cands(int(s.value), s.counter))
        if not c:
            return None
        lists.append(c)
    outs = []
    for combo in itertools.islice(itertools.product(*lists), _MAX_COMBOS):
        res, pos = [], 0
        for s, r in zip(spans, combo):
            res.append(t[pos:s.start])
            res.append(r)
            pos = s.end
        res.append(t[pos:])
        outs.append("".join(res))
    return outs


# ---------------- (iii) 判定(追加型) ----------------
STAGE_ORDER = {"S1": 1, "S1P": 2, "S2": 3}


@dataclass
class TrialResult:
    verdict: str  # PRODUCTION_PASS / TRIAL_NOTATION_MATCH / TRIAL_READING_MATCH / AMBIGUOUS_NO_RESCUE / NO_RESCUE / VETO_PROD_PASS
    prod_class: str
    detail: str = ""
    spans_c: list = field(default_factory=list)
    spans_a: list = field(default_factory=list)
    stage: str = ""  # 救済時のみ: S1(表記一致のみ) / S1P(署名スパン不透明置換+既存判定) / S2(読み展開)
    warning: bool = False  # 不規則読みを持つ署名を含む救済(PASS_WITH_WARNING候補)

    @property
    def would_pass(self) -> bool:
        return self.verdict in ("PRODUCTION_PASS", "TRIAL_NOTATION_MATCH", "TRIAL_READING_MATCH")

    @property
    def rescued(self) -> bool:
        return self.verdict in ("TRIAL_NOTATION_MATCH", "TRIAL_READING_MATCH")

    def rescued_at(self, max_stage: str) -> bool:
        """max_stage(S1/S1P/S2)までの段階を有効にした場合に救済として通るか(累積列の計算用)。"""
        return self.rescued and STAGE_ORDER[self.stage] <= STAGE_ORDER[max_stage]


def prod_effective(c: str, a: str):
    """現行Production相当(classify + Cascade側のD-2引き上げ)。Resolver(LLM)はOFF。"""
    r = javal.classify_ja_asr_match(c, a, allow_reading_resolver=False)
    if r.classification == "ASR_VALIDATION_UNCERTAIN":
        up = variant.try_upgrade_voicing_cascade(c, a, r)
        if up is not None:
            r = up
    return r


def via_candidate_e(prod) -> bool:
    """注意: Trialでは`reason`文字列の一致でCandidate E経由を検出する。Production実装では
    文字列一致に依存せず、Variant Layerが返す構造化フィールド(例: rescue_candidate_id)を使うこと。"""
    return "Candidate E" in (prod.reason or "")


# 不規則読み(音読みの素直な連結と異なる)を持つ署名。同じ値でも読みが誤った音声をASRが算用数字で書けば
# 通る型(さんにちかん/いちがつ/ついたち等)の残余リスクが特に大きい。救済時はPASS_WITH_WARNING候補として
# 最終試聴リストへ回す(ユーザー判断事項(a))、または対象外にする(同(b))。
def is_irregular_sig(value: str, counter: str) -> bool:
    if "." in value:
        return False
    n = int(value)
    if counter in ("day", "day_span"):
        return n in _DAY or n % 10 in (4, 7, 9)
    if counter == "person":
        return n in (1, 2) or n % 10 == 4
    if counter == "age":
        return n == 20
    if counter == "tsu":
        return True
    if counter in ("month", "hour"):
        return n % 10 in (4, 7, 9)
    return False


def _signature_homophone(sig_c: list, sig_a: list) -> bool:
    """署名(値,助数詞ID)が異なる場合でも、不一致分が互いに同音(読み候補が交差)なら
    純粋な同音異表記(例: 一回/1階=いっかい、音声では区別不能)として扱う。"""
    from collections import Counter
    cc, ca = Counter(sig_c), Counter(sig_a)
    uc = sorted((cc - ca).elements())
    ua = sorted((ca - cc).elements())
    if len(uc) != len(ua) or not uc:
        return False
    for (vc, kc), (va, ka) in zip(uc, ua):
        if "." in vc or "." in va:
            return False
        rc = set(_cands(int(vc), kc))
        ra = set(_cands(int(va), ka))
        if not (rc & ra):
            return False
    return True


def candidate_e_veto(canonical: str, asr: str) -> bool:
    """Candidate E由来のPASSを取り消すべきか(02修正版)。
    - 両側に数値スパン: 署名(値,助数詞)が異なり、かつ読みも交差しない時のみ取消。
    - 片側のみスパン(他方はASRのかな書き等): 件数差ではなく『読み展開』で比較する。スパン側を
      かな展開した候補のいずれかが、もう一方と(Candidate Eを使わない)EXACT/NORMALIZED/PHONETICで
      一致するなら取消さない。展開不能/一致なしなら取消(Cascade/HRへ)。
    - 両側にスパンなし: 本層の対象外(非数値の同音過許容はOPEN-333)で取消さない。"""
    sc, sa = find_spans(canonical), find_spans(asr)
    gc = [(s.value, s.counter) for s in sc]
    ga = [(s.value, s.counter) for s in sa]
    if not sc and not sa:
        return False
    if sc and sa:
        return sorted(gc) != sorted(ga) and not _signature_homophone(gc, ga)
    if sc:
        exp, other, side = reading_expansions(canonical), asr, "c"
    else:
        exp, other, side = reading_expansions(asr), canonical, "a"
    if not exp:
        return True
    for e in exp:
        r2 = prod_effective(e, other) if side == "c" else prod_effective(other, e)
        if r2.classification in ("EXACT_MATCH", "NORMALIZED_MATCH", "PHONETIC_MATCH") and not via_candidate_e(r2):
            return False
    return True


_OPAQUE = "〓"


def opaque_form(text: str) -> str:
    """署名スパン(数値+助数詞)を同一の不透明記号へ置換(読み表は使わない)。"""
    t = unicodedata.normalize("NFKC", text)
    res, pos = [], 0
    for s in find_spans(text):
        res.append(t[pos:s.start])
        res.append(_OPAQUE)
        pos = s.end
    res.append(t[pos:])
    return "".join(res)


def _mk(verdict, prod, detail, info, stage="", sigs=()):
    warn = bool(stage) and any(is_irregular_sig(v, k) for v, k in sigs)
    return TrialResult(verdict, prod.classification, detail, stage=stage, warning=warn, **info)


def trial_judge(canonical: str, asr: str, prod=None) -> TrialResult:
    prod = prod or prod_effective(canonical, asr)
    sc, sa = find_spans(canonical), find_spans(asr)
    gc = [(s.value, s.counter) for s in sc]
    ga = [(s.value, s.counter) for s in sa]
    info = dict(spans_c=gc, spans_a=ga)
    if prod.should_pass:
        # (iv) 数値署名ガード(Trial): 現行ProductionのCandidate E(漢字候補読み総当たり)由来のPASSが、
        # 数値+助数詞の署名が異なる文を通す型(三日間->三日目 等)を検出して取り消す(Cascadeへ)。
        # 副作用: 正しい音声をASRが『三日目』と誤記した場合も取り消すため不要な再生成を生みうる(OPEN-333)。
        if via_candidate_e(prod) and candidate_e_veto(canonical, asr):
            return TrialResult("VETO_PROD_PASS", prod.classification,
                               "Candidate E由来のPASSだが数値+助数詞の署名/読みが一致しない(値/助数詞違いの疑い)", **info)
        return TrialResult("PRODUCTION_PASS", prod.classification)
    if not sc and not sa:
        return TrialResult("NO_RESCUE", prod.classification, "数値+助数詞スパンなし(本層の対象外)", **info)
    if has_ambiguous(canonical) or has_ambiguous(asr):
        return TrialResult("AMBIGUOUS_NO_RESCUE", prod.classification, "曖昧語(十分/三日月/一時/一月/一分/N分の等)を含むため自動救済しない", **info)
    # Stage 1: 値の表記差のみ(値+助数詞を置換後、Production正規化で完全一致)
    if gc == ga:
        if javal.normalize_ja(value_form(canonical)) == javal.normalize_ja(value_form(asr)):
            return _mk("TRIAL_NOTATION_MATCH", prod, "Stage1: 数値+助数詞の表記差のみ(署名一致)", info, "S1", gc)
        # Stage 1': 署名スパンを同一の不透明記号へ置換し、残りの差は既存Production判定(読み表不使用)へ委ねる。
        # 数値以外の差(あと/後、つけ/付け等)が併発していても、既存判定が通すなら救済。
        try:
            r1 = prod_effective(opaque_form(canonical), opaque_form(asr))
        except Exception:  # 例外時は既存判定へフォールバック(=救済しない)
            r1 = None
        if r1 is not None and r1.classification in ("EXACT_MATCH", "NORMALIZED_MATCH", "PHONETIC_MATCH") and not via_candidate_e(r1):
            return _mk("TRIAL_NOTATION_MATCH", prod, f"Stage1': 署名一致+署名スパン不透明置換後に既存判定{r1.classification}", info, "S1P", gc)
    # Stage 2: 読み展開後に既存Production判定(Resolver LLM OFF)
    ec, ea = reading_expansions(canonical), reading_expansions(asr)
    if ec is None or ea is None:
        return TrialResult("NO_RESCUE", prod.classification, "読み展開不能スパンあり", **info)
    sig_ok = gc == ga or _signature_homophone(gc, ga)
    for c2, a2 in itertools.product(ec, ea):
        r2 = prod_effective(c2, a2)
        if r2.classification in ("EXACT_MATCH", "NORMALIZED_MATCH", "PHONETIC_MATCH"):
            # (c) Candidate E経由のPASSは、元の署名が一致/同音の場合のみ許可(展開で署名が消えるため)
            if via_candidate_e(r2) and not (sc and sa and sig_ok) and candidate_e_veto(canonical, asr):
                continue
            return _mk("TRIAL_READING_MATCH", prod, f"Stage2: 数値を読みへ展開後に{r2.classification}", info, "S2", gc + ga)
    return TrialResult("NO_RESCUE", prod.classification, "展開後も不一致(値差/助数詞差/別語等)", **info)
