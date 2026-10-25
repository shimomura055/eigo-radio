# OPEN-517 是正案プロトタイプ v2(DEV/proto。Production fileは一切変更しない。Production関数はimportして使い、複製しない)。
# v1(proto_value_gate_fix_01.py、凍結・変更なし)からの差分 = F2のみ(OPEN517_PREREGISTERED_01.md §5):
#   v1のF2(かな数詞+番/度の閉集合書換え)は正例対照6件(みっかかん/しがつ/さんにん/ひゃくえん/しちがつ/じゅうだい)を誤NG化し基準1不合格。
#   v2のF2 = 『かな書きの数詞』を、相手側テキストの数値atom(値,助数詞)の**期待読み表**で認識して表記統一する汎用規則:
#       相手側にatom(value=n, unit=c)があり、こちら側に c,n の期待読み(_cands(n,c))と一致するかな列があれば、そのかな列をatomの表層に置換。
#       期待読み表に無い読み(例: 三日<->さんにち、一分<->いちふん)は置換されない=脱落DIFFのまま=NG(不規則読みの保護は維持)。
#   期待読み表 = er066 Trialの `_cands`(Production vgが『移設元』としているmodule)。Production適用時は移設+parity testが必要(未実施・本proto外)。
# F1は v1 と同一: READING_MATCH PASSにも最終ANDゲート(値ガードDIFF・否定差。AMBIGUOUS=P3降格)を適用。
import contextlib, sys
sys.path.insert(0, ".")
import er078_asr_value_guard_01 as vg
import er078_asr_unified_judge_01 as uj
import er066_ja_asr_orthographic_equivalence_01_trial as tr
from dataclasses import dataclass


def _cand_reads(value, unit):
    try:
        if value is None or vg.Fraction(value).denominator != 1 or unit == "":
            return []
        n = int(value)
        return [x for x in tr._cands(n, unit) if x]
    except Exception:
        return []


def _replace_kana(text: str, other_atoms) -> str:
    """text中の『かな書き数詞』を、相手側atomの表層へ置換(期待読みに完全一致する場合のみ。長い読み優先、各atomにつき1回)。"""
    out = text
    for a in other_atoms:
        if a.kind != "num":
            continue
        for r in sorted(_cand_reads(a.value, a.unit), key=len, reverse=True):
            # かな列が既にatomとして取れているテキストには触らない(漢字/数字表記側が自分で持っている場合は置換不要)
            i = out.find(r)
            if i >= 0:
                out = out[:i] + a.surface + out[i + len(r):]
                break
    return out


def unify_kana_numerals(canon: str, asr: str):
    """(canon', asr')。両方向に適用(canonがかな書きでもASRがかな書きでも)。atomが元から対応している位置は変えない。"""
    ac, aa = vg.extract_atoms_ja(canon), vg.extract_atoms_ja(asr)
    return _replace_kana(canon, aa), _replace_kana(asr, ac)


def value_guard_fixed(canon: str, text: str, lang: str = "ja"):
    if lang == "ja":
        c2, t2 = unify_kana_numerals(canon, text)
        return vg.value_guard(c2, t2, lang)
    return vg.value_guard(canon, text, lang)


@dataclass(frozen=True)
class GateVerdict:
    state: str          # PASS / NG_PROTECTED(DIFFまたは否定差) / DEMOTE_P3(AMBIGUOUS=Secondaryへ降格)
    value_kind: str
    negation_diff: bool
    reason: str


def reading_match_final_gate(canon: str, gate_text: str, lang: str = "ja", fix_f2: bool = True) -> GateVerdict:
    """Productionの最終ANDゲート(er078_asr_unified_judge_01.py:538-553)と同じ分岐をREADING_MATCH PASSへ適用。ortho span解除は(basis!=ORTHO_BASIS)適用されない。"""
    g = value_guard_fixed(canon, gate_text, lang) if fix_f2 else vg.value_guard(canon, gate_text, lang)
    neg = uj.negation_diff(canon, gate_text, lang)
    if g.kind == vg.DIFF:
        return GateVerdict("NG_PROTECTED", g.kind, neg, "final_gate_value_diff")
    if neg:
        return GateVerdict("NG_PROTECTED", g.kind, neg, "final_gate_negation_diff")
    if g.kind == vg.AMBIGUOUS:
        return GateVerdict("DEMOTE_P3", g.kind, neg, "primary_pass_demoted_ambiguous_value")
    return GateVerdict("PASS", g.kind, neg, "ok")


@contextlib.contextmanager
def apply_in_process(f1=True, f2=True):
    """judgeを in-process で是正後の挙動にする(統合再現用)。f1: APPROVED基底からREADING_MATCHを外す / f2: judgeの値ガード呼出(_protected)にかな統一を前置。"""
    orig_bases, orig_prot = uj.APPROVED_EQUIVALENCE_BASES, uj._protected
    try:
        if f1:
            uj.APPROVED_EQUIVALENCE_BASES = frozenset(orig_bases - {"READING_MATCH"})
        if f2:
            def _prot(c, t, lang):
                if lang == "ja":
                    c, t = unify_kana_numerals(c, t)
                return orig_prot(c, t, lang)
            uj._protected = _prot
        yield
    finally:
        uj.APPROVED_EQUIVALENCE_BASES, uj._protected = orig_bases, orig_prot
