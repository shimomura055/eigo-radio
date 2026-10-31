# -*- coding: utf-8 -*-
"""選定フォームv3: 学習項目(Phrase/Word)の記事内出現回数の決定論的集計 occ-v1(純関数・API 0・環境変数/flagを読まない)。

SELECTION-UI-OCCURRENCE-COUNT-01 委任_02(OPEN-632)。委任_01の試作 `docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/tools/occurrence_count_01.py` を正式位置へ昇格し、
Opus条件Aレビュー必須6件(M1-M3の集計規則側)と推奨を反映した。規則表の正本=`docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/RULES_01.md`(ユーザー確認用1ページ表)。
活用形・除外表は承認済みProductionの er105_kp_fulltext_selector_01(forms/IRR/_IRREGULAR_PLURAL/_PLURAL_EXCLUDE/_PARTICIPIAL_ADJ_EXCLUDE/PAST_ALSO_OTHER_WORD/COMPLETION_EXCLUDE)を
読み取り専用で再利用する(再実装・改変しない。表の内容が変わったら snapshot test が落ちる=再確認の合図)。

規則(occ-v1)
  確定(counted)      : exact(選定表層S/一般化形Uと一致) / lemma(活用形) / slot_pron(人称スロットを閉じた代名詞集合で充足) / sep_pron(句動詞の間に代名詞1語。直後が句読点・文末)
  判定保留(uncertain): slot_np(名詞句で埋まるスロット) / slot_name(人名で埋まる人称スロット) / sep_np(句動詞の間に名詞句) / sep_pron でも不変化詞が前置詞兼用で直後に語が続く /
                       excl(1語項目の活用形が er105 の除外表に該当: build->building, lie->lay, good->goods 等) / revlemma(活用済み語の他活用形) -> 加算しない(件数だけ別枠記録)
  対象外             : 日本語訳・説明文(入力に含めない) / 文境界・句読点・改行をまたぐ一致 / 部分文字列一致(トークン単位のみ) / 縮約 's(let's, it's)
"""
from __future__ import annotations

import re
import unicodedata

SECTIONS = ("story", "comment", "preview", "oneline", "title")
RULE_VERSION = "occ-v1"

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*")
_GAP_OK = re.compile(r"^[ \t ]+$")

_CLOSED = frozenset(
    "a an the this that these those my your his her its our their one's someone's somebody's some any each every no "
    "i you he she it we they me him us them who whom whose which what when where why how "
    "in on at by for from of off out over to up with into onto upon about above across after against along among around as before behind below "
    "beneath beside between beyond down during except inside near outside past since through throughout toward towards under until within without "
    "and or but nor so yet if than because while although though "
    "is are was were be been being am do does did have has had will would can could shall should may might must not never always just also still even only then now really simply".split())
_PRE_VERB_ADV = frozenset("never always just also still even only then now really simply often already almost".split())
_PARTICLES = frozenset("away out up down off on in over back around apart through aside along together forward".split())
# 前置詞兼用の不変化詞(M2): put it in boxes / put it on the table のように直後に名詞が続くと前置詞の用法かもしれない
_PREP_PARTICLES = frozenset("in on over through around along down up off by about across past".split())
_PRON_INSERT = frozenset("it them him her me you us this that these those everything something anything one".split())
_DET = frozenset("a an the this that these those my your his her its our their some any each every no".split())
_FUNC_VERBS = frozenset({"be", "have", "do"})       # M3: 先頭の be/have/do は活用対象(was in the way <- be in the way)
_FUNC_VERB_FORMS = {"be": frozenset({"be", "is", "are", "was", "were", "been", "being", "am"}),
                    "have": frozenset({"have", "has", "had", "having"}),
                    "do": frozenset({"do", "does", "did", "done", "doing"})}
# 's が所有格ではなく縮約(is/has/us)になりうる語。これらへ 's を付けた形は同一語として数えない(let's / it's / that's ...)
_CONTRACTION_BASES = frozenset(_CLOSED | {"let", "here", "there"})

_SLOT_SOMEONE = frozenset("me you him her us them someone somebody one i he she we they".split())
_SLOT_POSS = frozenset("my your his her its our their one's someone's somebody's".split())
_SLOT_SELF = frozenset("myself yourself himself herself itself ourselves themselves oneself yourselves".split())
_SLOT_SOMETHING = frozenset("it this that them these those everything something anything".split())
_SLOT_MAP = {"someone": _SLOT_SOMEONE, "somebody": _SLOT_SOMEONE, "one's": _SLOT_POSS, "someone's": _SLOT_POSS, "somebody's": _SLOT_POSS,
             "oneself": _SLOT_SELF, "something": _SLOT_SOMETHING,
             "sb": _SLOT_SOMEONE, "sth": _SLOT_SOMETHING, "sb's": _SLOT_POSS}      # sb/sth は someone/something の別名(辞書表記)
_NP_SLOTS = frozenset({"someone", "somebody", "something", "one's", "someone's", "somebody's", "sb", "sth", "sb's"})
_PERSON_SLOTS = frozenset({"someone", "somebody", "sb"})


def _er():
    """承認済みProduction helperを読み取り専用で遅延import。"""
    import er105_kp_fulltext_selector_01 as sel
    return sel


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text or "")
    return t.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "‐": "-", "‑": "-"}))


def tokenize(text: str) -> list:
    """[(lower, start, end)] (正規化後の文字位置)。ハイフン連結語・語中アポストロフィは1トークン。en/em dashは区切り。"""
    return [(m.group(0).lower(), m.start(), m.end()) for m in _TOKEN_RE.finditer(text)]


def term_tokens(term: str) -> list:
    return [t[0] for t in tokenize(normalize(term))]


# ---------------------------------------------------------------- 活用
def inflect_forms(lemma: str) -> set:
    """lemmaの活用形(動詞: -s/-ed/-ing/不規則、名詞複数)+lemma自身。承認済みer105.forms/_IRREGULAR_PLURALを再利用。be/have/doは閉じた表(junk形 bed/haved を作らない)。"""
    sel = _er()
    l = lemma.lower()
    if l in _FUNC_VERB_FORMS:
        return set(_FUNC_VERB_FORMS[l])
    out = {l} | set(sel.forms(l))
    if l in sel._IRREGULAR_PLURAL.values():
        out |= {k for k, v in sel._IRREGULAR_PLURAL.items() if v == l}
    if re.search(r"[^aeiou]y$", l):
        out.add(l[:-1] + "ies")
    elif re.search(r"(s|x|z|ch|sh)$", l):
        out.add(l + "es")
    else:
        out.add(l + "s")
    return out


def risky_forms(lemma: str, n_words: int) -> set:
    """lemmaの活用形のうち er105 の除外表に該当し、別語・別義と取り違えるおそれがある形(M1)。
    1語項目(Word)=複数形側(_PLURAL_EXCLUDE: good->goods)・形容詞化分詞(_PARTICIPIAL_ADJ_EXCLUDE: build->building)・過去形が別語(PAST_ALSO_OTHER_WORD: see->saw)・
    COMPLETION_EXCLUDE(lie->lay)の全て。複数語項目(Phrase)=複数形側と COMPLETION_EXCLUDE のみ(`leave out`<-`left out` のように句動詞の不変化詞が用法を決める形は確定のまま)。"""
    sel = _er()
    l = lemma.lower()
    forms = inflect_forms(l) - {l}
    bad = {f for f in forms if f in sel._PLURAL_EXCLUDE or f in sel.COMPLETION_EXCLUDE}
    if n_words == 1:
        bad |= {f for f in forms if f in sel._PARTICIPIAL_ADJ_EXCLUDE or f in sel.PAST_ALSO_OTHER_WORD}
    return bad


def lemmas_of(surface: str) -> set:
    """活用済みの表層(bothered / urging / predictions)から、前方生成で再現できる基本形候補を返す(承認済みer105の逆引き候補を前方生成で検証)。
    名詞化した分詞形容詞(_PARTICIPIAL_ADJ_EXCLUDE)・単数化で別義になる複数形(_PLURAL_EXCLUDE)は対象外。"""
    sel = _er()
    s = surface.lower()
    if s in sel._PLURAL_EXCLUDE or s in sel._PARTICIPIAL_ADJ_EXCLUDE:
        return set()
    cands = set(sel._verb_base_candidates(s)) | set(sel._plural_base_candidates(s))
    for base, (past, pp) in sel.IRR.items():
        if s in (past, pp):
            cands.add(base)
    return {l for l in cands if len(l) >= 3 and s in inflect_forms(l) and l != s}


def _is_head_candidate(tok: str) -> bool:
    return tok not in _CLOSED and len(tok) > 1 and "'" not in tok and "-" not in tok


class Pattern:
    """pos[i] = 許容トークン集合(frozenset)。slots[i] = 人称スロット語(someone等)またはNone。sep=句動詞の分離形用。"""

    def __init__(self, pos: list, rule: str, slots: list | None = None, sep: bool = False, base: list | None = None):
        self.pos, self.rule, self.slots, self.sep, self.base = pos, rule, slots or [None] * len(pos), sep, base

    def sig(self) -> tuple:
        return (tuple(self.pos), self.rule, tuple(self.slots), self.sep, tuple(self.base) if self.base else None)


def _lemma_patterns(U: list, ref: list | None, n_words: int) -> list:
    """トークン列Uの各位置を活用/スロット展開した 'lemma'(確定)・'excl'(除外表に該当する形=保留)・'sep'(分離句動詞) の各パターンを作る。
    ref=対応する別表現(S)。同位置で ref[i] が U[i] の活用形なら、その位置を活用対象にする。"""
    pats: list = []
    n = len(U)
    pos, slots, changed = [], [], False
    xpos, xchanged = [], False
    for i, t in enumerate(U):
        allowed = {t}
        xallowed = {t}
        slot = None
        if t in _SLOT_MAP:
            allowed |= _SLOT_MAP[t]
            slot = t
        else:
            verb_pos = (i == 0 or U[i - 1] in _PRE_VERB_ADV or U[i - 1] == "to") and (_is_head_candidate(t) or t in _FUNC_VERBS)
            last_pos = i == n - 1 and _is_head_candidate(t)
            aligned = ref is not None and len(ref) == n and ref[i] != t and ref[i] in inflect_forms(t)
            if verb_pos or last_pos or aligned:
                fs = inflect_forms(t)
                bad = risky_forms(t, n_words) if t not in _FUNC_VERBS else set()
                allowed |= (fs - bad)
                xallowed |= (fs & bad)
            if t in ("a", "an") and i > 0:
                allowed |= {"this", "that", "a", "an"}      # 参照語の一般化(draw that line <-> draw a line)。theは加えない
        if len(allowed) > 1:
            changed = True
        if len(xallowed) > 1:
            xchanged = True
        pos.append(frozenset(allowed))
        xpos.append(frozenset(xallowed))
        slots.append(slot)
    if changed:
        pats.append(Pattern(pos, "lemma", slots))
    if xchanged:           # 除外表に該当する活用形(1語項目: build->building, lie->lay, good->goods)。他の位置は通常形のままにして、該当形を含む一致だけを保留に回す
        for i in range(n):
            if len(xpos[i]) > 1:
                pp = list(pos)
                pp[i] = frozenset(xpos[i] - {U[i]})
                pats.append(Pattern(pp, "excl", slots))
    if n >= 2 and _is_head_candidate(U[0]) and U[1] in _PARTICLES:
        head = inflect_forms(U[0]) - risky_forms(U[0], n_words) if n_words == 1 else inflect_forms(U[0])
        pats.append(Pattern([frozenset(head)] + pos[1:], "sep", slots, sep=True))
    return pats


def build_patterns(term: str, selection_phrase: str | None = None) -> list:
    """term=学習項目の表示形(N5一般化形=used_form。無変換ならselectionと同一)、selection_phrase=本文実表現(あれば)。
    活用・スロット展開パターンは一般化形Uと実表現Sの両方から生成して和集合にする(Opus推奨)。"""
    U = term_tokens(term)
    S = term_tokens(selection_phrase) if selection_phrase else U
    pats: list = []
    if not U:
        return pats
    pats.append(Pattern([frozenset([t]) for t in S], "exact"))
    if U != S:
        pats.append(Pattern([frozenset([t]) for t in U], "exact"))
    pats += _lemma_patterns(U, S, len(U))
    if S != U and S:
        pats += _lemma_patterns(S, U, len(S))
    # 活用済みの表示形(N5が基本形化していない語)の他活用形 = 判定保留(uncertain)。bothered -> bother/bothers
    n = len(U)
    slots = [t if t in _SLOT_MAP else None for t in U]
    rpos, rchanged = [], False
    for i, t in enumerate(U):
        allowed = {t}
        if t not in _SLOT_MAP and ((i == 0 or U[i - 1] in _PRE_VERB_ADV or U[i - 1] == "to") or i == n - 1) and _is_head_candidate(t):
            for l in lemmas_of(t):
                allowed |= inflect_forms(l)
        if len(allowed) > 1:
            rchanged = True
        rpos.append(frozenset(allowed))
    if rchanged:
        pats.append(Pattern(rpos, "revlemma", slots, base=U))
    seen, out = set(), []
    for p in pats:
        k = p.sig()
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


# ---------------------------------------------------------------- 照合
def _gap_ok(text: str, a_end: int, b_start: int) -> bool:
    return bool(_GAP_OK.match(text[a_end:b_start]))


def _poss_ok(tok: str, allowed: frozenset) -> bool:
    """末尾位置のみ所有格('s)付きも同一語として数える(campaign's)。縮約になりうる語(let's/it's/that's)は数えない。"""
    return tok.endswith("'s") and tok[:-2] in allowed and tok[:-2] not in _CONTRACTION_BASES


def _capitalized_name(text: str, tok_span: tuple, tok: str) -> bool:
    raw = text[tok_span[0]:tok_span[1]]
    return len(raw) > 1 and raw[0].isupper() and raw[1:].islower() and tok not in _CLOSED


def _match_plain(text: str, toks: list, i: int, pat: Pattern) -> list:
    """toks[i]から始まる通常照合。returns [(used_token_indexes, rule, uncertain)]"""
    results = []
    m = len(pat.pos)

    def rec(k: int, j: int, used: list, unc: bool, rule: str):
        if k == m:
            results.append((list(used), rule, unc))
            return
        if j >= len(toks):
            return
        if used and not _gap_ok(text, toks[used[-1]][2], toks[j][1]):
            return
        tok = toks[j][0]
        if tok in pat.pos[k] or (k == m - 1 and _poss_ok(tok, pat.pos[k])):
            r = rule
            if pat.slots[k] and tok != pat.slots[k] and pat.rule == "lemma":
                r = "slot_pron"
            u = unc or pat.rule == "excl" or (pat.rule == "revlemma" and tok not in (pat.base[k], pat.base[k] + "'s"))
            rec(k + 1, j + 1, used + [j], u, r)
        elif pat.slots[k] in _NP_SLOTS and tok in _DET and pat.rule == "lemma":
            for ln in (2, 3):      # 限定詞+名詞(1-2語) = 名詞句で埋まるスロット -> 判定保留
                if j + ln <= len(toks) and all(_gap_ok(text, toks[x][2], toks[x + 1][1]) for x in range(j, j + ln - 1)):
                    rec(k + 1, j + ln, used + list(range(j, j + ln)), True, "slot_np")
        elif k > 0 and pat.slots[k] in _PERSON_SLOTS and pat.rule == "lemma" and _capitalized_name(text, (toks[j][1], toks[j][2]), tok):
            rec(k + 1, j + 1, used + [j], True, "slot_name")      # pulled Tom under = 人名スロット -> 保留

    rec(0, i, [], False, pat.rule)
    return results


_TAIL_PUNCT = ".,;:!?)\"'-–—…"


def _followed_by_word(text: str, end: int) -> bool:
    """end以降の最初の非空白文字が句読点でも文末でもない=直後に語が続く。"""
    rest = text[end:].lstrip(" \t ")
    return bool(rest) and rest[0] not in _TAIL_PUNCT


def _match_sep(text: str, toks: list, i: int, pat: Pattern) -> list:
    """動詞 + [間1-3語] + particle(+残り)。間なしは通常照合が拾う。"""
    results = []
    if toks[i][0] not in pat.pos[0]:
        return results
    for ins in (1, 2, 3):
        jpart = i + 1 + ins
        if jpart >= len(toks):
            break
        if not all(_gap_ok(text, toks[x][2], toks[x + 1][1]) for x in range(i, jpart)):
            break
        if toks[jpart][0] not in pat.pos[1]:
            continue
        used, j, ok = [jpart], jpart, True
        for k in range(2, len(pat.pos)):
            j += 1
            if j >= len(toks) or toks[j][0] not in pat.pos[k] or not _gap_ok(text, toks[j - 1][2], toks[j][1]):
                ok = False
                break
            used.append(j)
        if not ok:
            continue
        mid = [toks[x][0] for x in range(i + 1, jpart)]
        seq = [i] + used            # 表示用span(間の語を含む外枠)
        nxt = toks[used[-1] + 1][0] if used[-1] + 1 < len(toks) and _gap_ok(text, toks[used[-1]][2], toks[used[-1] + 1][1]) else None
        if ins == 1 and mid[0] in _PRON_INSERT:
            particle_final = len(pat.pos) == 2 and toks[jpart][0] in _PREP_PARTICLES
            prep_like = particle_final and _followed_by_word(text, toks[used[-1]][2])      # M2: put it in boxes / put it on the table = 前置詞の用法かもしれない
            results.append((seq, "sep_pron", prep_like or nxt in _DET))
        else:
            results.append((seq, "sep_np", True))
    return results


def find_hits(text: str, patterns: list) -> list:
    """1 unit(段落/1行)内の一致。重なりは(確定優先・長い順)で先勝ち。returns [{start,end,surface,rule,uncertain}]"""
    t = normalize(text)
    toks = tokenize(t)
    cands = []
    for i in range(len(toks)):
        for p in patterns:
            found = _match_sep(t, toks, i, p) if p.sep else _match_plain(t, toks, i, p)
            for used, rule, unc in found:
                st, en = toks[used[0]][1], toks[used[-1]][2]
                cands.append({"start": st, "end": en, "surface": t[st:en], "rule": rule, "uncertain": unc})
    out, taken = [], []
    for h in sorted(cands, key=lambda h: (h["uncertain"], -(h["end"] - h["start"]), h["start"])):
        if any(not (h["end"] <= a or b <= h["start"]) for a, b in taken):
            continue
        taken.append((h["start"], h["end"]))
        out.append(h)
    out.sort(key=lambda h: h["start"])
    return out


_SENT_B = re.compile(r"(?<=[.!?])\s+|\n")


def _sentence_of(t: str, a: int, b: int) -> str:
    s = 0
    for m in _SENT_B.finditer(t):
        if m.end() <= a:
            s = m.end()
        else:
            break
    m2 = _SENT_B.search(t, b)
    e = m2.start() if m2 else len(t)
    return t[s:e].strip()


def count_entry(sections: dict, term: str, selection_phrase: str | None = None, with_hits: bool = False) -> dict:
    """sections = {"story":[段落...], "comment":[...], "preview":[...], "oneline":[...], "title":[...]} (値None=本文未取得=unavailable)。
    returns occurrence dict(フォームdata JSONの各entryの`occurrence`キー本体)。"""
    pats = build_patterns(term, selection_phrase)
    counts, unc, forms, unc_forms, unavailable, hits = {}, {}, {}, {}, [], []
    for sec in SECTIONS:
        paras = sections.get(sec)
        if paras is None:
            if sec != "title":
                unavailable.append(sec)
            continue
        c = u = 0
        for ui, para in enumerate(paras):
            nt = normalize(para)
            for h in find_hits(para, pats):
                if with_hits:
                    hits.append({"section": sec, "unit": ui, **h, "sentence": _sentence_of(nt, h["start"], h["end"])})
                k = h["surface"].lower()
                if h["uncertain"]:
                    u += 1
                    unc_forms[k] = unc_forms.get(k, 0) + 1
                else:
                    c += 1
                    forms[k] = forms.get(k, 0) + 1
        counts[sec] = c
        if u:
            unc[sec] = u
    out = {"v": RULE_VERSION, "counts": counts, "total": sum(v for k, v in counts.items() if k != "title"), "forms": forms}
    if unc:
        out["uncertain"] = unc
        out["uncertain_forms"] = unc_forms
    if unavailable:
        out["unavailable"] = unavailable
    if with_hits:
        out["hits"] = hits
    return out


def exact_selection_count(sections: dict, selection_phrase: str, secs=("story", "oneline", "title")) -> int | None:
    """選定時の厳密一致件数(er105の `item.occurrence_count` と同じ定義: 実表現Sの完全一致、所有格 's 付きも含む)。export時自己検査用。
    対象区分のいずれかが未取得なら None(比較不能)。"""
    toks = term_tokens(selection_phrase)
    if not toks:
        return 0
    pat = [Pattern([frozenset([t]) for t in toks], "exact")]
    n = 0
    for sec in secs:
        paras = sections.get(sec)
        if paras is None:
            return None
        for para in paras:
            n += sum(1 for h in find_hits(para, pat) if not h["uncertain"])
    return n
