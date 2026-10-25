# OPEN-517 是正案プロトタイプ v4(DEV/proto。Production fileは一切変更しない。Production関数はimportして使い、複製しない)。
# v3(proto_value_gate_fix_03.py、凍結・変更なし)からの差分 = Opus条件Cレビュー(OPUS_REVIEW_01_OPEN517.md)の必須M-2/M-3/M-4(+R-6の意図差分):
#   V4-1(M-2a): 期待読み候補から vg.WEAK_KANA_NUMERALS の読み(なのか/ようか/とお。一般語と衝突しProductionが辞書から外した読み)を除外。
#   V4-2(M-2b 単調性ガード): かな統一は『相手側atomがF2前に未対応(drop)だった、または既に別かな数詞atomと誤対応(単位違い等)だった』ものだけを対象にし、
#         統一後の guard で『F2前の非EQUAL pair(置換に対応するpairを除く)』が同じ(src,hyp,verdict)で全て残ることを検証。残らなければF2前の結果を採用(whole fallback)。
#   V4-3(M-3 語境界): 一致したかな列が、同一助数詞のより大きい数詞の一部(前: さん|じゅうにん / 後: にじ|ゅうじ)である場合は置換しない。
#         期待読みの逆引き表(unit別 read->値集合, n=1..20000)で『直前/直後k文字(k<=8)を連結した列が別の値の読みか』を判定する(最長一致の等価)。
#         逆引きで値が一意でない読みは候補から除外。吸収される既存atom(候補が内包するもの)は許可(みっか->みっかかん/よっか->にじゅうよっか)。
#   V4-5(系統スイープで発見した修正): 吸収できる既存atomに曖昧かな数詞(kind=amb: いつか<->いつかかん)を含める(v3は許容していた。v4初版で5日間<->いつかかんが誤NG化)。
#   V4-4(M-4): F2の適用は明示引数 kana_unify=True のときだけ(呼出回数ではない)。negation_diffは常に置換前の元テキストで判定。
#         in-process harness(apply_in_process)だけが『judge内でPrimary PASS(根拠READING_MATCH)の最初の_protected呼出』にkana_unify=Trueを渡す(Production適用時は呼出側引数)。
# 期待読み表=er066 Trial `_cands`(Production vgの『移設元』。Production適用時は移設+parity testが必要=本proto外)。
import contextlib, dataclasses, sys, unicodedata
sys.path.insert(0, ".")
import er078_asr_value_guard_01 as vg
import er078_asr_unified_judge_01 as uj
import er066_ja_asr_orthographic_equivalence_01_trial as tr
from dataclasses import dataclass

_WEAK = frozenset(vg.WEAK_KANA_NUMERALS)
_REV = {}          # unit -> {read: set(values)}
_REV_MAX = 20000
_EXT_K = 8


def _rev(unit):
    if unit not in _REV:
        m = {}
        for n in range(1, _REV_MAX + 1):
            try:
                for r in tr._cands(n, unit):
                    if r:
                        m.setdefault(r, set()).add(n)
            except Exception:
                pass
        _REV[unit] = m
    return _REV[unit]


def _cand_reads(value, unit):
    """atom(value, unit)の期待読み。弱い読み(V4-1)と、同unit内で値が一意でない読みを除く。"""
    try:
        if value is None or vg.Fraction(value).denominator != 1 or unit == "":
            return []
        n = int(value)
        rv = _rev(unit) if 1 <= n <= _REV_MAX else {}
        out = []
        for x in tr._cands(n, unit):
            if not x or x in _WEAK:
                continue
            if rv and rv.get(x, {n}) != {n}:
                continue
            out.append(x)
        return out
    except Exception:
        return []


def _part_of_larger_numeral(text, i, j, r, value, unit):
    """text[i:j]==r(値valueの読み)が、同unitのより大きい(別値の)数詞読みの一部か(V4-3)。"""
    if not (1 <= int(value) <= _REV_MAX):
        return False
    rv = _rev(unit)
    for k in range(1, _EXT_K + 1):
        if i - k >= 0:
            s = text[i - k:i] + r
            if rv.get(s) and rv[s] != {int(value)}:
                return True
        if j + k <= len(text):
            s = r + text[j:j + k]
            if rv.get(s) and rv[s] != {int(value)}:
                return True
    if j < len(text) and text[j] in "ゃゅょ":
        return True
    return False


def _replace_kana(text, own_atoms, other_atoms, budget):
    """NFKC text中の『かな書き数詞』を相手側atom表層へ置換。budget={surface: 許可回数}(F2前に未対応だった相手atomだけ)。
    戻り: (新text, 置換したatomのlist)"""
    out = unicodedata.normalize("NFKC", text or "")
    spans = [(a.start, a.end, a) for a in own_atoms]
    replaced = []
    for a in other_atoms:
        if a.kind != "num" or budget.get(a.surface, 0) <= 0:
            continue
        done = False
        for r in sorted(_cand_reads(a.value, a.unit), key=len, reverse=True):
            i = out.find(r)
            while i >= 0:
                j = i + len(r)
                ok = True
                for s, e, x in spans:
                    if not (i < e and j > s):
                        continue
                    # 重なる既存atom: 候補(=相手atomの値の完全な期待読み)が既存atomを内包する(完全一致でない)場合のみ吸収を許可
                    # (みっか->みっかかん、よっか->にじゅうよっか。部分的な重なりは触らない)。語境界は_part_of_larger_numeralで別途判定
                    if not ((i <= s and e <= j) and (s, e) != (i, j) and x.kind in ("num", "amb")):
                        ok = False
                        break
                if ok and not _part_of_larger_numeral(out, i, j, r, a.value, a.unit):
                    out = out[:i] + a.surface + out[j:]
                    replaced.append(a)
                    budget[a.surface] -= 1
                    spans = [(x.start, x.end, x) for x in vg.extract_atoms_ja(out)]
                    done = True
                    break
                i = out.find(r, i + 1)
            if done:
                break
    return out, replaced


def _eligible_budget(pairs0, side):
    """F2前のpair列から『相手atomが未対応(None)または別のかな数詞atomと対応していた』非EQUALを集計。
    side='hyp': 置換対象=転写側 -> 原稿側atom(src)が対象。side='src': 逆。"""
    b = {}
    for p in pairs0:
        if p.verdict == vg.EQUAL:
            continue
        mine, other = (p.src, p.hyp) if side == "hyp" else (p.hyp, p.src)
        if mine is None:
            continue
        if other is None or other in vg.KANA_NUMERALS:
            b[mine] = b.get(mine, 0) + 1
    return b


@dataclass(frozen=True)
class F2Info:
    fired: bool
    replaced: tuple = ()          # ((side, partner_surface), ...)
    fallback: str = ""            # '' / 'monotonic_guard' / 'no_replacement'
    canon2: str = ""
    text2: str = ""


def _replace_both(canon, text, g0):
    nc, na = unicodedata.normalize("NFKC", canon or ""), unicodedata.normalize("NFKC", text or "")
    ac, aa = vg.extract_atoms_ja(nc), vg.extract_atoms_ja(na)
    bh = _eligible_budget(g0.pairs, "hyp")   # 原稿側atomを相手にして転写をかな->数字へ
    bs = _eligible_budget(g0.pairs, "src")   # 転写側atomを相手にして原稿をかな->数字へ
    c2, rc = _replace_kana(nc, ac, aa, bs)
    a2, ra = _replace_kana(na, aa, ac, bh)
    return c2, a2, [("src", a) for a in rc], [("hyp", a) for a in ra]


def unify_kana_numerals(canon, asr, g0=None):
    """(canon', asr', 置換atoms)。g0=F2前のvalue_guard結果(省略時は計算)。"""
    g0 = g0 or vg.value_guard(canon, asr, "ja")
    c2, a2, rc, ra = _replace_both(canon, asr, g0)
    return c2, a2, [a for _, a in rc + ra]


def _nonequal(g):
    return [(p.src, p.hyp, p.verdict) for p in g.pairs if p.verdict != vg.EQUAL]


def value_guard_fixed_detail(canon, text, lang="ja"):
    """Production value_guardにF2(v4)を前置。戻り (ValueGuardResult, F2Info)。"""
    if lang != "ja":
        return vg.value_guard(canon, text, lang), F2Info(False)
    g0 = vg.value_guard(canon, text, lang)
    c2, t2, rc, ra = _replace_both(canon, text, g0)
    reps = rc + ra
    if not reps:
        return g0, F2Info(False, fallback="no_replacement")
    g = vg.value_guard(c2, t2, lang)
    # 単調性ガード(V4-2): F2前の非EQUAL pairから『置換に対応するpair』を除いたものが、F2後も同じ(src,hyp,verdict)で全て残ること
    pre = _nonequal(g0)
    for side, a in reps:
        for k, (s, h, v) in enumerate(pre):
            if (side == "hyp" and s == a.surface and (h is None or h in vg.KANA_NUMERALS)) or \
               (side == "src" and h == a.surface and (s is None or s in vg.KANA_NUMERALS)):
                pre.pop(k)
                break
    post = _nonequal(g)
    rep_t = tuple((s, a.surface) for s, a in reps)
    for t in pre:
        if t in post:
            post.remove(t)
        else:
            return g0, F2Info(False, rep_t, "monotonic_guard", c2, t2)
    warns = list(dict.fromkeys(list(g0.warnings) + list(g.warnings)))
    if any(vg.is_irregular_sig(a.value, a.unit) for _, a in reps) and vg.WARN_IRREGULAR_READING not in warns:
        warns.append(vg.WARN_IRREGULAR_READING)
    return dataclasses.replace(g, warnings=tuple(warns)), F2Info(True, rep_t, "", c2, t2)


def value_guard_fixed(canon, text, lang="ja"):
    return value_guard_fixed_detail(canon, text, lang)[0]


def protected(canon, text, lang, kana_unify=False):
    """uj._protected 相当。F2は kana_unify=True のときだけ(V4-4)。否定差は常に元テキスト。"""
    if kana_unify and lang == "ja":
        return value_guard_fixed(canon, text, lang), uj.negation_diff(canon, text, lang)
    return vg.value_guard(canon, text, lang), uj.negation_diff(canon, text, lang)


@dataclass(frozen=True)
class GateVerdict:
    state: str          # PASS / NG_PROTECTED(DIFFまたは否定差) / DEMOTE_P3(AMBIGUOUS=Secondaryへ降格)
    value_kind: str
    negation_diff: bool
    reason: str
    warnings: tuple = ()


def reading_match_final_gate(canon, gate_text, lang="ja", kana_unify=True) -> GateVerdict:
    """Productionの最終ANDゲート(er078_asr_unified_judge_01.py:538-553)と同じ分岐をREADING_MATCH PASSへ適用(F1)。kana_unify=F2。"""
    g, neg = protected(canon, gate_text, lang, kana_unify=kana_unify)
    if g.kind == vg.DIFF:
        return GateVerdict("NG_PROTECTED", g.kind, neg, "final_gate_value_diff", g.warnings)
    if neg:
        return GateVerdict("NG_PROTECTED", g.kind, neg, "final_gate_negation_diff", g.warnings)
    if g.kind == vg.AMBIGUOUS:
        return GateVerdict("DEMOTE_P3", g.kind, neg, "primary_pass_demoted_ambiguous_value", g.warnings)
    return GateVerdict("PASS", g.kind, neg, "ok", g.warnings)


@contextlib.contextmanager
def apply_in_process(f1=True, f2=True, log=None):
    """judgeを in-process で是正後の挙動にする(統合再現用)。
    f1: APPROVED基底からREADING_MATCHを外す。 f2: Primary PASS(根拠READING_MATCH)の最終ゲート(=judge内の最初の_protected呼出)にのみ kana_unify=True を渡す。
    log(list)を渡すとF2発動件(canon, text, F2Info)を追記する。"""
    orig_bases, orig_prot, orig_judge = uj.APPROVED_EQUIVALENCE_BASES, uj._protected, uj.unified_judge
    state = {"read": False, "n": 0}
    try:
        if f1:
            uj.APPROVED_EQUIVALENCE_BASES = frozenset(orig_bases - {"READING_MATCH"})
        if f2:
            def _judge(ctx, primary_result, *a, **k):
                pr = uj._mk_primary(primary_result)
                state["read"] = bool(pr.passed and pr.equivalence_basis == "READING_MATCH")
                state["n"] = 0
                return orig_judge(ctx, primary_result, *a, **k)

            def _prot(c, t, lang, **kw):   # 2026-10-25(07A): Production _protected が kana_unify/info_out を受けるため**kwを許容(protoは明示F2を自前で行う)
                state["n"] += 1
                if lang == "ja" and state["read"] and state["n"] == 1:
                    g, info = value_guard_fixed_detail(c, t, lang)
                    if log is not None and info.fired:
                        log.append((c, t, info))
                    return g, uj.negation_diff(c, t, lang)
                return orig_prot(c, t, lang)
            uj.unified_judge, uj._protected = _judge, _prot
        yield
    finally:
        uj.APPROVED_EQUIVALENCE_BASES, uj._protected, uj.unified_judge = orig_bases, orig_prot, orig_judge
