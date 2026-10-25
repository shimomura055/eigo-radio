# OPEN-517 是正案プロトタイプ(DEV/proto。Production fileは一切変更しない。Production関数はimportして使い、複製しない)。
# 是正の2点:
#   (F1) READING_MATCH(PHONETIC_MATCH/READING_RESOLVED_MATCH)のPrimary PASSにも、最終ANDゲート(値ガード+否定差)を適用する。
#        = er078_asr_unified_judge_01.APPROVED_EQUIVALENCE_BASES から "READING_MATCH" を外した場合と同じ判定。他の承認根拠は触らない。
#   (F2) 副作用の除去: 『かな書きの 数詞+規則読み助数詞(番・度)』は 『漢数字/算用数字+助数詞』と同じ値の別表記として正規化してから値ガードへ渡す。
#        (例: いちばん<->一番。数詞ではなく慣用語/序数の『一番』が脱落DIFFで誤NGになるのを防ぐ。値は変えない=等価表記の統一のみ)
#        不規則/促音/連濁を伴う助数詞(日・人・つ・回・本・分…)は対象外(現行どおり保守的=脱落DIFF)。是正前より弱くなることはない
#        (F2は『NGを減らす』方向のみ。F1適用後の判定は 是正前PASS(=スキップ) 以下の厳しさで、かつ F2なしのF1以上に緩い)。
# 使い方: reading_match_final_gate(canon, gate_text) -> GateVerdict。統合再現は apply_in_process() (in-process差替え。Production file無変更)。
import contextlib, re, sys
sys.path.insert(0, ".")
import er078_asr_value_guard_01 as vg
import er078_asr_unified_judge_01 as uj
from dataclasses import dataclass

# --- F2: 規則読み助数詞(読みが数詞に依らず固定: ばん/ど)の かな数詞表。1〜10のみ。複数読みは全て列挙 ---
_NUM_KANA = {  # 数詞 -> かな読み候補(長い順に照合するため後でソート)
    "一": ["いち"], "二": ["に"], "三": ["さん"], "四": ["よん", "し", "よ"], "五": ["ご"],
    "六": ["ろく"], "七": ["なな", "しち"], "八": ["はち"], "九": ["きゅう", "く"], "十": ["じゅう"],
}
REGULAR_COUNTERS = {"番": "ばん", "度": "ど"}   # 閉集合(拡張は証拠付きで)。促音/連濁/不規則(is_irregular_sig)を持つ助数詞は入れない。

_KANA2KANJI = {}
for _k, _rs in _NUM_KANA.items():
    for _c, _cr in REGULAR_COUNTERS.items():
        for _r in _rs:
            _KANA2KANJI[_r + _cr] = _k + _c
_KANA_PAT = re.compile("|".join(re.escape(s) for s in sorted(_KANA2KANJI, key=len, reverse=True)))


def canonicalize_kana_counter(text: str) -> str:
    """かな書きの『数詞+番/度』を漢数字表記へ統一(値は同一)。例: 活動がいちばん低い -> 活動が一番低い。"""
    return _KANA_PAT.sub(lambda m: _KANA2KANJI[m.group(0)], text or "")


def value_guard_fixed(canon: str, text: str, lang: str = "ja"):
    """Production value_guardに F2 の表記統一を前置したもの(JA以外は素通し)。"""
    if lang == "ja":
        return vg.value_guard(canonicalize_kana_counter(canon), canonicalize_kana_counter(text), lang)
    return vg.value_guard(canon, text, lang)


@dataclass(frozen=True)
class GateVerdict:
    state: str          # PASS / NG_PROTECTED(DIFFまたは否定差) / DEMOTE_P3(AMBIGUOUS=Secondaryへ降格)
    value_kind: str
    negation_diff: bool
    reason: str


def reading_match_final_gate(canon: str, gate_text: str, lang: str = "ja", fix_f2: bool = True) -> GateVerdict:
    """Productionの最終ANDゲート(er078_asr_unified_judge_01.py:538-553)と同じ分岐をREADING_MATCH PASSへ適用した判定。
    ortho span解除は(basis!=ORTHO_BASISなので)適用されない=NG_PROTECTED。"""
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
    """judgeを in-process で是正後の挙動にする(統合再現用。Production fileは変更しない)。
    f1: APPROVED_EQUIVALENCE_BASESから READING_MATCH を外す / f2: judgeの値ガード呼出(_protected)にかな統一を前置。"""
    orig_bases, orig_prot = uj.APPROVED_EQUIVALENCE_BASES, uj._protected
    try:
        if f1:
            uj.APPROVED_EQUIVALENCE_BASES = frozenset(orig_bases - {"READING_MATCH"})
        if f2:
            def _prot(c, t, lang):
                if lang == "ja":
                    c, t = canonicalize_kana_counter(c), canonicalize_kana_counter(t)
                return orig_prot(c, t, lang)
            uj._protected = _prot
        yield
    finally:
        uj.APPROVED_EQUIVALENCE_BASES, uj._protected = orig_bases, orig_prot
