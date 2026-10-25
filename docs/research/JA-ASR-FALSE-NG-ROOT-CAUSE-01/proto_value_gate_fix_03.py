# OPEN-517 是正案プロトタイプ v3(DEV/proto。Production fileは一切変更しない。Production関数はimportして使い、複製しない)。
# v2(proto_value_gate_fix_02.py、凍結・変更なし)からの差分 = judge統合評価(open517_api0_eval_02.out.json)で判明した副作用2点のみ(OPEN517_PREREGISTERED_01.md §6):
#   V3-1: 警告の保全。v2のかな統一は、既にatom化されている位置(ふたり/はたち/みっか 等 KANA_NUMERALS)まで書換え、
#         JA_NUMERIC_IRREGULAR_READING警告(事後試聴対象)を消した(PASS_WITH_WARNING->PASS 8件)。v3は(a)自テキスト内で既にatomの位置は書換えない
#         (b)統一後のguard結果へ統一前のwarningsを必ず併合し、(c)統一で認識したかな数詞が不規則読み署名(is_irregular_sig)なら同じ警告を付ける。
#   V3-2: 適用範囲の限定。v2は_protected全呼出に統一を前置したためPrimary NGのP1(値DIFF短絡)まで解除した(NG_PROTECTED->Secondary呼出 6件=Production挙動の拡大)。
#         v3はF2を『Primary PASSの根拠がREADING_MATCHのときの最終ANDゲート』にだけ適用する(新規緩和なし。Primary NG/Secondary gateは現行どおり)。
# F1・期待読み表の考え方はv2と同一。期待読み表=er066 Trial `_cands`(Production vgの『移設元』。Production適用時は移設+parity testが必要=本proto外)。
import contextlib, dataclasses, sys, unicodedata
sys.path.insert(0, ".")
import er078_asr_value_guard_01 as vg
import er078_asr_unified_judge_01 as uj
import er066_ja_asr_orthographic_equivalence_01_trial as tr
from dataclasses import dataclass


def _cand_reads(value, unit):
    try:
        if value is None or vg.Fraction(value).denominator != 1 or unit == "":
            return []
        return [x for x in tr._cands(int(value), unit) if x]
    except Exception:
        return []


def _replace_kana(text: str, own_atoms, other_atoms):
    """NFKC text中の『かな書き数詞』を相手側atomの表層へ置換。自テキストで既にatom化されている位置は触らない。
    戻り: (新text, 置換したatomのlist)"""
    out = unicodedata.normalize("NFKC", text or "")
    spans = [(a.start, a.end) for a in own_atoms]
    replaced = []
    for a in other_atoms:
        if a.kind != "num":
            continue
        done = False
        for r in sorted(_cand_reads(a.value, a.unit), key=len, reverse=True):
            i = out.find(r)
            while i >= 0:
                j = i + len(r)
                # 既存atomと重なる場合: 完全一致(既に同じ語がatom化済み)や部分的な重なりは触らない。候補が既存atomを内包する(みっか->みっかかん)ときだけ置換
                if all((not (i < e and j > s)) or ((i <= s and e <= j) and (s, e) != (i, j)) for s, e in spans):
                    out = out[:i] + a.surface + out[i + len(r):]
                    replaced.append(a)
                    spans = [(x.start, x.end) for x in vg.extract_atoms_ja(out)]   # 置換後の位置で再計算(置換済みの表層も以後atom扱い)
                    done = True
                    break
                i = out.find(r, i + 1)
            if done:
                break
    return out, replaced


def unify_kana_numerals(canon: str, asr: str):
    """(canon', asr', 置換atoms)。"""
    nc, na = unicodedata.normalize("NFKC", canon or ""), unicodedata.normalize("NFKC", asr or "")
    ac, aa = vg.extract_atoms_ja(nc), vg.extract_atoms_ja(na)
    c2, rc = _replace_kana(nc, ac, aa)
    a2, ra = _replace_kana(na, aa, ac)
    return c2, a2, rc + ra


def value_guard_fixed(canon: str, text: str, lang: str = "ja", _orig=None):
    """Production value_guardにF2を前置。warningsは統一前のものを併合し、不規則読みのかな数詞なら警告を付ける(V3-1)。"""
    if lang != "ja":
        return vg.value_guard(canon, text, lang)
    f = _orig or vg.value_guard
    c2, t2, rep = unify_kana_numerals(canon, text)
    g, g0 = f(c2, t2, lang), f(canon, text, lang)
    warns = list(dict.fromkeys(list(g0.warnings) + list(g.warnings)))
    if any(vg.is_irregular_sig(a.value, a.unit) for a in rep) and vg.WARN_IRREGULAR_READING not in warns:
        warns.append(vg.WARN_IRREGULAR_READING)
    return dataclasses.replace(g, warnings=tuple(warns))


@dataclass(frozen=True)
class GateVerdict:
    state: str          # PASS / NG_PROTECTED(DIFFまたは否定差) / DEMOTE_P3(AMBIGUOUS=Secondaryへ降格)
    value_kind: str
    negation_diff: bool
    reason: str
    warnings: tuple = ()


def reading_match_final_gate(canon: str, gate_text: str, lang: str = "ja", fix_f2: bool = True) -> GateVerdict:
    """Productionの最終ANDゲート(er078_asr_unified_judge_01.py:538-553)と同じ分岐をREADING_MATCH PASSへ適用。ortho span解除は(basis!=ORTHO_BASIS)適用されない。"""
    g = value_guard_fixed(canon, gate_text, lang) if fix_f2 else vg.value_guard(canon, gate_text, lang)
    neg = uj.negation_diff(canon, gate_text, lang)
    if g.kind == vg.DIFF:
        return GateVerdict("NG_PROTECTED", g.kind, neg, "final_gate_value_diff", g.warnings)
    if neg:
        return GateVerdict("NG_PROTECTED", g.kind, neg, "final_gate_negation_diff", g.warnings)
    if g.kind == vg.AMBIGUOUS:
        return GateVerdict("DEMOTE_P3", g.kind, neg, "primary_pass_demoted_ambiguous_value", g.warnings)
    return GateVerdict("PASS", g.kind, neg, "ok", g.warnings)


@contextlib.contextmanager
def apply_in_process(f1=True, f2=True):
    """judgeを in-process で是正後の挙動にする(統合再現用)。
    f1: APPROVED基底からREADING_MATCHを外す。 f2: Primary PASS(根拠READING_MATCH)の最終ゲート(=judge内の最初の_protected呼出)にのみかな統一を前置(V3-2)。"""
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

            def _prot(c, t, lang):
                state["n"] += 1
                if lang == "ja" and state["read"] and state["n"] == 1:
                    return value_guard_fixed(c, t, lang), uj.negation_diff(c, t, lang)
                return orig_prot(c, t, lang)
            uj.unified_judge, uj._protected = _judge, _prot
        yield
    finally:
        uj.APPROVED_EQUIVALENCE_BASES, uj._protected, uj.unified_judge = orig_bases, orig_prot, orig_judge
