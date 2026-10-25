# JA-ASR-FALSE-NG-ROOT-CAUSE-01 Phase 3 prototype v1 (research/DEV only; NOT imported by Production; API 0).
# v0 (sha256 c3e61412c7adaada..., 凍結; 退避=proto_reading_compare_01_v0_frozen.py.txt) からの差分 = Opus条件Aレビュー必須修正 M1/M2/M3/M7:
#   M1: 救済しない条件を追加 = A7 登録読み不一致(expected_readings) / C2 同形異音候補(順方向=Production `_scg_c2_candidate`、
#       逆方向=ASR側の漢字spanが複数読みを持ち原稿の読みがその1つ)。Primary・Secondaryとも同じ関数を使う。
#   M2: 新分類名 JA_PRON_VALUE_EQUIVALENT_MATCH (READING_MATCH根拠にしない。最終ANDゲートを維持)。値のみ一致は既存
#       NUMERIC_VALUE_EQUIVALENT_MATCH。
#   M3: number_mismatches があるときは値ガード EQUAL のみ許可。NO_VALUES は数字差が無いTCMのときだけ許可。UNKNOWN/DIFF/AMBIGUOUS不可。
#       JAのP1保護差(否定差・否定マーカー差)も救済しない。
#   M7: 配線候補コードと同一にするため、Production関数を直接importして使う(`_ja_value_form`は「atomが無ければNone」を含め
#       Productionそのもの、複製しない)。parityは proto_reading_compare_01_test_01.py。
#   R3: A1(桁区切りstrip)は廃止。`extract_atoms_ja`が `8,900` を1 atomにするため。Productionが落とす原因は
#       `_numeric_value_equivalence` の「number_mismatches非空」ゲート(桁区切りの`,`は content_diff であって number_mismatch ではない)。
#       v1はこのゲートを外し、値atomトークン化後の残りで比較する。
# 厳格: 濁点許容なし、漢字候補総当たりなし、LLMなし、残りの読みが1つでも違えば救済しない。
from __future__ import annotations
import difflib, sys
from dataclasses import dataclass
sys.path.insert(0, ".")
import jaconv
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er008_asr_variant_hardening_15_ja_kanji_readings as kr
import er011_ja_asr_variant_layer_01 as vl
import er078_asr_value_guard_01 as vg
from er078_asr_unified_judge_01 import negation_diff

PRON_LABEL = "JA_PRON_VALUE_EQUIVALENT_MATCH"          # M2: 新分類名 (_READING_MATCH_CLASSIFICATIONS に入れない)
VALUE_LABEL = sec.NUMERIC_VALUE_EQUIVALENT_MATCH        # 既存ラベル(値のみ一致)
W_PRON = "JA_PRON_EQUIVALENT"                           # R2: 事後試聴対象の非ブロッキングwarning
_PARTICLE_PRON = {"は": "ワ", "へ": "エ"}


@dataclass
class V1Result:
    equal: bool
    kind: str | None            # "VALUE_ONLY" | "PRON" | None
    why: str
    label: str | None = None
    warnings: tuple = ()
    cause: str | None = None    # R4: flip原因分類
    blocked_by: str | None = None  # M1/M3 で救済を止めた理由


def _tag_pron(t: str, particle: bool) -> str:
    out = []
    for w in vl._get_tagger()(t):
        f = w.feature
        if particle and getattr(f, "pos1", "") == "助詞" and w.surface in _PARTICLE_PRON:
            out.append(_PARTICLE_PRON[w.surface]); continue
        k = getattr(f, "kana", None) or getattr(f, "pron", None) or w.surface
        out.append(k)
    return jaconv.kata2hira("".join(out))


def pron_hira(t: str) -> str:
    """A2: 助詞 は->わ / へ->え のみ発音形を使う読み(他はunidic kana)。"""
    return _tag_pron(t, True)


def _diff_spans(c: str, a: str):
    sm = difflib.SequenceMatcher(None, c, a, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            yield c[i1:i2], a[j1:j2]


def c2_blocked(cls, cf_norm: str, af_norm: str) -> str | None:
    """M1: C2同形異音。順方向=Production(`_scg_c2_candidate`、原稿漢字spanの正当な読み候補にASR側の読みが含まれる)。
    逆方向=ASRが書いた漢字spanが複数の読み(2つ以上)を持ち、原稿側の読みがその1つ(ASRの文字は、TTSが別の読みで読んだ
    可能性を排除しない: 例 原稿`きょう` / ASR`今日` / 実音声`こんにち`)。差分spanは値atomトークン化後の文字列から取る。"""
    if sec._scg_c2_candidate(cls):
        return "c2_forward(production _scg_c2_candidate)"
    for c_span, a_span in _diff_spans(cf_norm, af_norm):
        if not a_span or not c_span:
            continue
        try:
            if sec._scg_heterophone_candidate({"canonical": c_span, "asr": a_span}):
                return f"c2_forward_span:{c_span}->{a_span}"
            cands = kr.reading_candidates_for_span(a_span)
            if cands and len(set(cands)) >= 2:
                if javal._hira_reading(c_span) in cands:
                    return f"c2_reverse_span:{c_span}->{a_span}"
        except Exception:
            continue
    return None


def pron_value_equivalence(canonical_text: str, asr_text: str | None, cls=None,
                           expected_readings: dict | None = None, require_value_atoms: bool = False) -> V1Result:
    """案A v1: Primary/Secondary共通の判定(純関数、API 0)。clsはclassify結果(None=内部で計算、resolver=OFF)。"""
    if asr_text is None:
        return V1Result(False, None, "asr_none")
    if cls is None:
        cls = javal.classify_ja_asr_match(canonical_text, asr_text, expected_readings=expected_readings,
                                          allow_reading_resolver=False)
    if cls.classification != "TRUE_CONTENT_MISMATCH":
        return V1Result(False, None, "not_tcm")
    if cls.protected.negation_mismatches:
        return V1Result(False, None, "negation_mismatch", blocked_by="negation")
    if negation_diff(canonical_text, asr_text, "ja"):
        return V1Result(False, None, "negation_diff", blocked_by="negation")
    if sec._scg_negation_marker_diff(canonical_text, asr_text):
        return V1Result(False, None, "negation_marker_diff", blocked_by="negation")
    rd = sec._scg_reading_dict_reason(cls)
    if rd:                                                   # M1: A7 登録読み保護
        return V1Result(False, None, rd, blocked_by="A7_reading_dictionary")
    g = vg.value_guard(canonical_text, asr_text, "ja")
    has_num_diff = bool(cls.protected.number_mismatches)
    if g.kind == vg.EQUAL:
        pass
    elif g.kind == vg.NO_VALUES and not has_num_diff and not require_value_atoms:   # M3
        pass
    else:
        return V1Result(False, None, f"value_guard={g.kind}", blocked_by="value_guard")
    cf, af = sec._ja_value_form(canonical_text), sec._ja_value_form(asr_text)
    has_atoms = cf is not None and af is not None
    if (cf is None) != (af is None):
        return V1Result(False, None, "value_atoms_presence_differs", blocked_by="value_guard")
    if not has_atoms:
        cf, af = canonical_text, asr_text
    c, a = javal.normalize_ja(cf), javal.normalize_ja(af)
    warnings = tuple(g.warnings or ())
    if c == a:
        if sec._has_negation_ja_text(cf) != sec._has_negation_ja_text(af):
            return V1Result(False, None, "negation_after_value_form", blocked_by="negation")
        cause = "A1_value_notation" if has_atoms else "unexpected_surface_equal"
        return V1Result(True, "VALUE_ONLY", "surface_equal_after_value_form", VALUE_LABEL, warnings, cause)
    p_with, p_plain = pron_hira(c), _tag_pron(c, False)
    a_with, a_plain = pron_hira(a), _tag_pron(a, False)
    if p_with != a_with:
        return V1Result(False, None, "pron_differs")
    blk = c2_blocked(cls, c, a)                              # M1: C2 (発音救済のときだけ意味を持つ)
    if blk:
        return V1Result(False, None, blk, blocked_by="C2_heterophone")
    needs_particle = p_plain != a_plain
    if has_atoms and needs_particle:
        cause = "A3_value+A2_particle"
    elif has_atoms:
        cause = "A3_value+pron"
    elif needs_particle:
        cause = "A2_particle"
    else:
        cause = "ENGINE_reading_difference"                 # R4: 助詞も値も要らない読み一致=エンジン差。個別正当化が必要
    return V1Result(True, "PRON", "pron_equal_after_value_form", PRON_LABEL,
                    warnings + (W_PRON,), cause)


def to_classification(r: V1Result, base_cls):
    """Primary adapter用のClassificationResultJA(配線時は `_numeric_value_equivalence` と同位置)。M2: READING_MATCHにしない。"""
    assert r.equal
    return javal.ClassificationResultJA(
        r.label, base_cls.similarity_ratio, javal.ProtectedCheckResultJA(passed=True),
        should_pass=True, should_retry=False, reason=f"v1 {r.kind}: {r.why}")


def design_a(canon: str, asr: str):
    """v0互換の薄いラッパー(旧スクリプト用)。"""
    r = pron_value_equivalence(canon, asr)
    return r.equal, (r.why if r.equal else (r.blocked_by and f"{r.why}[{r.blocked_by}]") or r.why)
