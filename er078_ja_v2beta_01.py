# -*- coding: utf-8 -*-
# JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A: 日本語ASR判定の「v2読み規則 + B-light β」(R-1 OFF)のProduction module。
#
# 正式採用: ユーザー決定2026-10-29(APPROVED_FOR_PRODUCTION。`docs/pm/delegation_log/2026-10-29_JA-ASR-V2-BETA-PRODUCTION-WIRING-01_USER.md` §1A・§3)。
# 技術根拠(凍結proto。本moduleは複製ではなく再配置+境界整理): docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/{EVAL_UNIFIED_03.md, proto_unified_03.py},
#   docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{proto_reading_compare_02.py, b_light_proto_02.py}。設計=docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/。
#
# 有効範囲: X/Y/Z run scope内のみ(`er109_xz_scope_01.current_scope()`)。scope外(A/B/C・単体)は呼ばれず、er007の従来コードパス=出力byte同一(27-7)。
# 配線点: er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail の seam(S0/S1P/S1S/S2/S3)のみ。unified_judge本体は無改変。
# 新層で救済した判定は必ずPASS_WITH_WARNING(PASS_W)。PASS_Wは試聴待ちにしない(非ブロッキング。最終制作報告に載せるだけ)。
#   本moduleのどの分岐も verdict/rescue_basis/listen_advised を読んでretry・停止・HR投入・Assembly停止を行わない(静的testで固定)。
#
# 不移植(明示): R-1(複数読み漢字の事後検査)/別表L3(送り仮名省略形の訓読み救済)/ASR再試行・合意再試行・best-of-N/veto/frame検査/monkeypatch差替え。
#
# 重いlib(jaconv/fugashi系/pykakasi系)は関数内の遅延importのみ。scope外ではこのmodule自体がimportされない(er007側の分岐)。
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional

import er078_asr_unified_judge_01 as uj

# ============================================================
# 既定ON・緊急OFF(単一定数+単一読取関数)。env/引数/設定dict/起動scriptからON/OFFにできない。値の変更はソース編集+commitのみ。
# 前例: er078_asr_unified_judge_01.READING_MATCH_FINAL_GATE / er007_ja_secondary_asr_01.JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED。
# ============================================================
JA_V2_BETA_ENABLED = True
SCOPES = ("X", "Y", "Z")
JUDGE_RULE_VERSION = "ja_v2beta_r1off_01"   # 判定核を変えたら必ず上げる(判定核ソースhashとの対応をtestで固定)
OUT_OF_SCOPE_BLOCK_REASON = "JA_V2BETA_AUDIO_OUT_OF_SCOPE_OR_FLAG_OFF"

# ---- ラベル・警告 ----
PRON_LABEL = "JA_PRON_VALUE_EQUIVALENT_MATCH"        # READING_MATCH根拠にしない(最終ANDゲートを維持)
# 値のみ一致のラベルは、adapter(er007)が引数 value_label で渡す既存の値のみ一致ラベルを使う。定義/使用はJA adapter側のみ(下流allowlistに載せない既存規約)=本moduleはリテラルを持たない。
COMPOSITE_LABEL = "JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE"
W_PRON = "JA_PRON_EQUIVALENT"
W_NEWLAYER_PRON = "JA_NEWLAYER_PRON_EQUIVALENT"
W_NEWLAYER_VALUE_BEYOND = "JA_NEWLAYER_VALUE_ONLY_BEYOND_PROD"
W_NEWLAYER_BETA = "JA_NEWLAYER_BETA_COMPOSITE"
NEWLAYER_WARNINGS = (W_NEWLAYER_PRON, W_NEWLAYER_VALUE_BEYOND, W_NEWLAYER_BETA)
NEWLAYER_PREFIX = "JA_NEWLAYER_"
W_FROM_SECONDARY = "JA_COMPOSITE_VALUE_FROM_SECONDARY"
W_GARBLE_EXPLAINED = "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED"
W_SECONDARY_READING_CONFLICT = "JA_COMPOSITE_SECONDARY_READING_CONFLICT"
W_LISTEN_ADVISED = "JA_COMPOSITE_LISTEN_ADVISED"      # 試聴推奨(必須ではない)。いかなる分岐もこの値で制御フローを変えない
# 承認済みequivalence根拠(最終ANDゲートを素通りさせる集合)へ新ラベルを入れない(import時assert。er007側の READING_MATCH 系はtestで確認)
assert not ({PRON_LABEL, COMPOSITE_LABEL, *NEWLAYER_WARNINGS} & set(uj.APPROVED_EQUIVALENCE_BASES))
assert uj.READING_MATCH_BASIS not in (PRON_LABEL, COMPOSITE_LABEL)

ELIG = ("p1_value_diff", "final_gate_value_diff", "p1_protected_diff:number_mismatch", "secondary_not_accepted")   # βの発火理由(前方一致)
BETA_REASON_CODE = "ja_beta_composite"
BETA_SECONDARY_LABEL = "JA_BETA_SECONDARY_VALUE"
_PARTICLE_PRON = {"は": "ワ", "へ": "エ"}
_NUM_CHARS = "0-9,.〇零一二三四五六七八九十百千万億兆"
_RUN_CHARS = "0-9,〇零一二三四五六七八九十百千万億兆"
TOKEN = "【値】"


def is_active_for_run() -> bool:
    """唯一の読取関数: 定数 ∧ X/Y/Z run scope内。`current_scope()`だけを読む(ortho flag等と連動する er109_xz_scope_01.is_active_for_run は流用しない)。"""
    import er109_xz_scope_01 as xz
    return bool(JA_V2_BETA_ENABLED is True) and xz.current_scope() in SCOPES


# ============================================================
# 遅延import(依存libが無い環境でもモジュール自体はimportできる。使用時の例外はseam側でL0へ戻る=fail-closed)
# ============================================================
_DEPS = None


def _d():
    global _DEPS
    if _DEPS is None:
        import types
        import jaconv
        import er007_ja_asr_validator_01 as javal
        import er007_ja_secondary_asr_01 as sec
        import er008_asr_variant_hardening_15_ja_kanji_readings as kr
        import er011_ja_asr_variant_layer_01 as vl
        import er078_asr_value_guard_01 as vg
        _DEPS = types.SimpleNamespace(jaconv=jaconv, javal=javal, sec=sec, kr=kr, vl=vl, vg=vg)
    return _DEPS


# ============================================================
# 実行時状態(1 attempt = 1 state)
# ============================================================
@dataclass
class V2bState:
    active: bool
    scope: Optional[str] = None
    canonical_text: str = ""
    primary_text: Optional[str] = None
    expected_readings: Optional[dict] = None
    blocked_by: Optional[str] = None           # M-6: "M6_E3" | "M6_E4"(全新層不適用=従来判定のまま)
    disabled_by: Optional[str] = None          # scope内でflag定数がFalse: "constant"
    layers: list = field(default_factory=list)  # [{"layer","side","cause","effective"}]
    errors: list = field(default_factory=list)
    beta: Optional[dict] = None                # β寄与/不成立の記録
    beta_skipped: Optional[str] = None
    value_label: str = "VALUE_ONLY"            # 値のみ一致の分類ラベル(er007が既存ラベルを渡す。本moduleはリテラルを持たない)
    secondary_layer_accepted: bool = False     # S1S: Secondary受理が新層(v2)によるか
    secondary_called_by_beta: bool = False

    @property
    def usable(self) -> bool:
        return bool(self.active and not self.blocked_by)

    def primary_layers(self) -> list:
        return [x for x in self.layers if x.get("side") == "primary" and x.get("layer") in ("v2_pron", "v2_value_only")]

    def primary_warning_labels(self) -> tuple:
        """PrimaryResult.warning_labelsへ渡す新層警告(Primary側でv2が救済したときだけ)。寄与なし=空(従来と同一)。"""
        out = []
        for x in self.primary_layers():
            w = W_NEWLAYER_PRON if x["layer"] == "v2_pron" else W_NEWLAYER_VALUE_BEYOND
            if w not in out:
                out.append(w)
        return tuple(out)


def begin(canonical_text: str, primary_text: Optional[str], *, e3=None, e4=None, expected_readings=None, value_label: str = "VALUE_ONLY") -> V2bState:
    """S0。scope外/flag OFFなら active=False(何も記録しない[scope外]/disabled_by記録[scope内OFF])。M-6: E3/E4が非空なら全新層不適用。"""
    import er109_xz_scope_01 as xz
    scope = xz.current_scope()
    if scope not in SCOPES:
        return V2bState(active=False, scope=scope)
    if not is_active_for_run():
        return V2bState(active=False, scope=scope, disabled_by="constant")
    st = V2bState(active=True, scope=scope, canonical_text=canonical_text, primary_text=primary_text, expected_readings=expected_readings,
                  value_label=value_label)
    if e3:
        st.blocked_by = "M6_E3"
    elif e4:
        st.blocked_by = "M6_E4"
    return st


# ============================================================
# v2読み規則(proto_reading_compare_02 の再配置。R-1なし)
# ============================================================
@dataclass
class V1Result:
    equal: bool
    kind: Optional[str]                 # "VALUE_ONLY" | "PRON" | None
    why: str
    label: Optional[str] = None
    warnings: tuple = ()
    cause: Optional[str] = None
    blocked_by: Optional[str] = None


def _tag_pron(t: str, particle: bool) -> str:
    D = _d()
    out = []
    for w in D.vl._get_tagger()(t):
        f = w.feature
        if particle and getattr(f, "pos1", "") == "助詞" and w.surface in _PARTICLE_PRON:
            out.append(_PARTICLE_PRON[w.surface])
            continue
        k = getattr(f, "kana", None) or getattr(f, "pron", None) or w.surface
        out.append(k)
    return D.jaconv.kata2hira("".join(out))


def pron_hira(t: str) -> str:
    """助詞 は->わ / へ->え のみ発音形を使う読み(他はunidic kana)。"""
    return _tag_pron(t, True)


def _diff_spans(c: str, a: str):
    import difflib
    sm = difflib.SequenceMatcher(None, c, a, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            yield c[i1:i2], a[j1:j2]


def c2_blocked(cls, cf_norm: str, af_norm: str) -> Optional[str]:
    """同形異音(C2)。順方向=Production `_scg_c2_candidate`、逆方向=ASR側の漢字spanが複数読みを持ち原稿の読みがその1つ。"""
    D = _d()
    if D.sec._scg_c2_candidate(cls):
        return "c2_forward(production _scg_c2_candidate)"
    for c_span, a_span in _diff_spans(cf_norm, af_norm):
        if not a_span or not c_span:
            continue
        try:
            if D.sec._scg_heterophone_candidate({"canonical": c_span, "asr": a_span}):
                return f"c2_forward_span:{c_span}->{a_span}"
            cands = D.kr.reading_candidates_for_span(a_span)
            if cands and len(set(cands)) >= 2:
                if D.javal._hira_reading(c_span) in cands:
                    return f"c2_reverse_span:{c_span}->{a_span}"
        except Exception:
            continue
    return None


def irregular_atoms(canon: str) -> list:
    """M-1: 原稿中の不規則読み数詞(一日・三日・二十歳等)。ASRの漢数字/算用数字表記から読みの正誤は判別できない。"""
    vg = _d().vg
    return [a.surface for a in vg.extract_atoms_ja(canon) if a.kind == "num" and vg.is_irregular_sig(a.value, a.unit)]


def pron_value_equivalence(canonical_text: str, asr_text: Optional[str], cls, side: str = "primary", value_label: str = "VALUE_ONLY") -> V1Result:
    """v2: Primary/Secondary共通の判定(純関数、API 0。cls=呼出側が持つ分類結果)。"""
    D = _d()
    javal, sec, vg = D.javal, D.sec, D.vg
    if asr_text is None:
        return V1Result(False, None, "asr_none")
    if cls.classification != "TRUE_CONTENT_MISMATCH":
        return V1Result(False, None, "not_tcm")
    if cls.protected.negation_mismatches:
        return V1Result(False, None, "negation_mismatch", blocked_by="negation")
    if uj.negation_diff(canonical_text, asr_text, "ja"):
        return V1Result(False, None, "negation_diff", blocked_by="negation")
    if sec._scg_negation_marker_diff(canonical_text, asr_text):
        return V1Result(False, None, "negation_marker_diff", blocked_by="negation")
    rd = sec._scg_reading_dict_reason(cls)
    if rd:                                                   # A7 登録読み保護
        return V1Result(False, None, rd, blocked_by="A7_reading_dictionary")
    g = vg.value_guard(canonical_text, asr_text, "ja")
    has_num_diff = bool(cls.protected.number_mismatches)
    if g.kind == vg.EQUAL:
        pass
    elif g.kind == vg.NO_VALUES and not has_num_diff:
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
        if side == "secondary" and has_atoms:           # A4(a) 不規則読み数詞の値のみ一致は救済しない
            irr = [x.surface for x in vg.extract_atoms_ja(canonical_text) if x.kind == "num" and vg.is_irregular_sig(x.value, x.unit)]
            if irr:
                return V1Result(False, None, f"a4a_irregular_reading_value:{','.join(irr)}", blocked_by="A4a_irregular_reading")
        cause = "A1_value_notation" if has_atoms else "unexpected_surface_equal"
        return V1Result(True, "VALUE_ONLY", "surface_equal_after_value_form", value_label, warnings, cause)
    p_with, p_plain = pron_hira(c), _tag_pron(c, False)
    a_with, a_plain = pron_hira(a), _tag_pron(a, False)
    if p_with != a_with:
        return V1Result(False, None, "pron_differs")
    blk = c2_blocked(cls, c, a)                              # C2 (発音救済のときだけ意味を持つ)
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
        cause = "ENGINE_reading_difference"                 # 助詞も値も要らない読み一致=エンジン差。Production化の範囲外
    return V1Result(True, "PRON", "pron_equal_after_value_form", PRON_LABEL, warnings + (W_PRON,), cause)


def to_classification(r: V1Result, base_cls):
    """Primary/Secondary adapter用のClassificationResultJA(`_numeric_value_equivalence`と同位置)。READING_MATCHにしない。"""
    assert r.equal
    javal = _d().javal
    return javal.ClassificationResultJA(
        r.label, base_cls.similarity_ratio, javal.ProtectedCheckResultJA(passed=True),
        should_pass=True, should_retry=False, reason=f"v2 {r.kind}: {r.why}")


def value_layer(canon: str, asr: Optional[str], cls, side: str, st: V2bState, orig_fn):
    """S1P/S1S: `_numeric_value_equivalence`位置の新層。orig_fn=従来関数(フォールバック=L1 ⊇ L0)。呼出側が例外をL0へ戻す。
    寄与(Productionの値等価層が受理しない救済)のときだけ st.layers へ記録する。"""
    if not st.usable:
        return orig_fn(canon, asr, cls)
    irr = irregular_atoms(canon)
    if irr:                                                  # M-1: side・kindに関わらずProduction判定へ戻す
        return orig_fn(canon, asr, cls)
    r = pron_value_equivalence(canon, asr, cls, side, st.value_label)
    if not r.equal:
        return orig_fn(canon, asr, cls)
    if r.kind == "PRON":
        if r.cause == "ENGINE_reading_difference":
            return orig_fn(canon, asr, cls)
        st.layers.append({"layer": "v2_pron", "side": side, "cause": r.cause, "effective": None})
        return to_classification(r, cls)
    o = orig_fn(canon, asr, cls)                             # VALUE_ONLY: Production既存の値等価層が受理するなら同一(寄与なし・警告なし)
    if getattr(o, "should_pass", False):
        return o
    st.layers.append({"layer": "v2_value_only", "side": side, "cause": r.cause, "effective": None})
    return to_classification(r, cls)


# ============================================================
# B-light β(b_light_proto_02 の再配置。reading_rule="v2"固定・secondary_reading_conflict="warn"固定)
# ============================================================
@dataclass
class AtomStatus:
    surface: str
    value: int
    unit_surface: str
    primary_run: Optional[str]
    status: str            # EQUAL | EXPLAINED | CONTRADICTION | MISSING
    detail: str = ""
    span: Optional[tuple] = None


@dataclass
class BResult:
    equal: bool
    why: str
    blocked_by: Optional[str] = None
    label: Optional[str] = None
    warnings: tuple = ()
    atoms: list = field(default_factory=list)
    protected: bool = False
    listen_advised: bool = False
    listen_reasons: tuple = ()
    audit: dict = field(default_factory=dict)


@dataclass
class PrecheckResult:
    """フック①の事前判定(S:=原稿)専用の戻り型。`.equal`/`.label`/`.warnings`を持たない=最終判定として流用できない。"""
    may_call_secondary: bool
    why: str
    blocked_by: Optional[str] = None


def _nfkc(t: str) -> str:
    return unicodedata.normalize("NFKC", t or "")


def _unit_surface(atom_surface: str) -> str:
    return re.sub(r"^[0-9,.〇零一二三四五六七八九十百千万億兆]+", "", atom_surface)


def _numeric_notation_ok(a) -> bool:
    """値atomが『数字・漢数字表記 + 助数詞』であること(かな数詞・あいまい語・分数は不可)。"""
    if a.kind != "num":
        return False
    us = _unit_surface(a.surface)
    pre = a.surface[: len(a.surface) - len(us)] if us else a.surface
    return bool(us) and bool(pre) and re.fullmatch("[" + _NUM_CHARS + "]+", pre) is not None


def _segments(run: str):
    if "," in run:
        return None
    segs, cur, kind = [], "", None
    for ch in run:
        k = "digit" if ch.isdigit() and ch.isascii() else "kanji"
        if k != kind and cur:
            segs.append((kind, cur))
            cur = ""
        kind = k
        cur += ch
    if cur:
        segs.append((kind, cur))
    return segs


def _place_ok(frags: list) -> bool:
    for i, fi in enumerate(frags):
        for fj in frags[i + 1:]:
            if fj <= 0 or fi % (10 ** len(str(fj))) != 0:
                return False
    return True


_FRONT_RE = re.compile(r"[1-9]0+")      # 前断片は『1桁 + 0の並び』(d x 10^k, k>=1)。観測形=8000


def explain_garble(run: str, target: int) -> Optional[str]:
    """観測形に限定。F-A=数字のみrunの2断片(前断片 d*10^k)。F-B=数字(d*10^k)+漢数字(万億兆なし)。いずれも断片の総和==target ∧ 位取りが重ならない。"""
    vg = _d().vg
    segs = _segments(run)
    if not segs:
        return None
    if len(segs) == 1 and segs[0][0] == "digit":
        d = segs[0][1]
        for i in range(1, len(d)):
            a, b = d[:i], d[i:]
            if not _FRONT_RE.fullmatch(a) or b.startswith("0"):
                continue
            vals = [int(a), int(b)]
            if sum(vals) == target and _place_ok(vals):
                return f"digit_split:{a}+{b}"
        return None
    if len(segs) == 2 and segs[0][0] == "digit" and segs[1][0] == "kanji":
        if not _FRONT_RE.fullmatch(segs[0][1]):
            return None
        k = segs[1][1]
        if any(c in k for c in "万億兆"):
            return None
        kv = vg.parse_ja_number(k)
        if kv is None or Fraction(kv).denominator != 1:
            return None
        vals = [int(segs[0][1]), int(kv)]
        if sum(vals) == target and _place_ok(vals):
            return f"digit+kanji:{segs[0][1]}+{k}"
    return None


def analyze_primary_values(canonical_n: str, primary_n: str, allow_explained: bool):
    vg = _d().vg
    c_atoms = [a for a in vg.extract_atoms_ja(canonical_n) if a.kind in ("num", "frac")]
    out, cursor = [], 0
    for a in c_atoms:
        us = _unit_surface(a.surface)
        val = int(a.value) if (a.kind == "num" and Fraction(a.value).denominator == 1) else None
        if a.kind != "num" or val is None or not us:
            out.append(AtomStatus(a.surface, -1, us, None, "CONTRADICTION", "unsupported_atom(kind/unit/non-integer)"))
            continue
        pat = re.compile(r"(?<![A-Za-z0-9,.])([" + _RUN_CHARS + r"]+)" + re.escape(us))
        found = None
        for m in pat.finditer(primary_n, cursor):
            found = m
            break
        if found is None:
            out.append(AtomStatus(a.surface, val, us, None, "MISSING", "no_numeric_run_before_unit_in_primary"))
            continue
        run = found.group(1)
        span = (found.start(), found.end())
        cursor = found.end()
        pv = vg.parse_ja_number(run)
        if pv is not None and Fraction(pv).denominator == 1 and int(pv) == val:
            out.append(AtomStatus(a.surface, val, us, run, "EQUAL", "primary_run_value_equals_canonical", span))
            continue
        why = explain_garble(run, val) if allow_explained else None
        if why:
            out.append(AtomStatus(a.surface, val, us, run, "EXPLAINED", why, span))
        else:
            out.append(AtomStatus(a.surface, val, us, run, "CONTRADICTION",
                                  f"primary_run_value={pv}" + ("" if allow_explained else "(explain disabled)"), span))
    return out, c_atoms


def _mask(text: str, spans: list) -> str:
    out, pos = [], 0
    for s, e in sorted(spans):
        out.append(text[pos:s])
        out.append(TOKEN)
        pos = e
    out.append(text[pos:])
    return "".join(out)


def _atom_seq(atoms):
    return [(int(a.value), a.unit) for a in atoms if a.kind == "num" and Fraction(a.value).denominator == 1]


def composite_core(canonical_text, primary_text, secondary_text, expected_readings) -> BResult:
    D = _d()
    javal, sec, vg = D.javal, D.sec, D.vg
    if primary_text is None or not str(primary_text).strip():
        return BResult(False, "primary_none", "primary_unavailable")
    if secondary_text is None or not str(secondary_text).strip():
        return BResult(False, "secondary_none_or_empty", "secondary_unavailable")
    Cn, Pn, Sn = _nfkc(canonical_text), _nfkc(primary_text), _nfkc(secondary_text)
    for tag, t in (("primary", primary_text), ("secondary", secondary_text)):
        if uj.negation_diff(canonical_text, t, "ja") or sec._scg_negation_marker_diff(canonical_text, t):
            return BResult(False, f"negation_diff:{tag}", "negation", protected=True)
    c_all = vg.extract_atoms_ja(Cn)
    c_atoms = [a for a in c_all if a.kind in ("num", "frac")]
    if not c_atoms:
        return BResult(False, "no_value_atoms_in_canonical", "not_applicable")
    if any(a.kind == "amb" for a in c_all):
        return BResult(False, "canonical_has_ambiguous_atom", "R4_atom_notation")
    if not all(_numeric_notation_ok(a) for a in c_atoms):
        return BResult(False, "canonical_atom_notation_unsupported", "R4_atom_notation")
    irr = [a.surface for a in c_atoms if a.kind == "num" and vg.is_irregular_sig(a.value, a.unit)]
    if irr:
        return BResult(False, f"irregular_reading_value:{','.join(irr)}", "A4a_irregular_reading")
    s_all = vg.extract_atoms_ja(Sn)
    if any(a.kind != "num" for a in s_all) or not all(_numeric_notation_ok(a) for a in s_all):
        return BResult(False, "secondary_atom_notation_unsupported", "R4_atom_notation", protected=True)
    if _atom_seq(c_atoms) != _atom_seq(s_all):               # 値atom列を位置・個数・順序で照合(value_guardの二重化)
        return BResult(False, "secondary_atom_sequence_mismatch", "secondary_value", protected=True)
    gs = vg.value_guard(canonical_text, secondary_text, "ja")
    if gs.kind != vg.EQUAL:
        return BResult(False, f"secondary_value_guard={gs.kind}", "secondary_value", protected=(gs.kind == vg.DIFF))
    st, _ = analyze_primary_values(Cn, Pn, True)
    bad = [s for s in st if s.status in ("CONTRADICTION", "MISSING")]
    if bad:
        contra = any(s.status == "CONTRADICTION" for s in bad)
        return BResult(False, "primary_value:" + ";".join(f"{s.surface}:{s.status}:{s.detail}" for s in bad),
                       "primary_secondary_value_contradiction" if contra else "primary_value_missing", atoms=st, protected=contra)
    cls = javal.classify_ja_asr_match(canonical_text, primary_text, expected_readings=expected_readings, allow_reading_resolver=False)
    rd = sec._scg_reading_dict_reason(cls)
    if rd:
        return BResult(False, rd, "A7_reading_dictionary", atoms=st)
    c_m = _mask(Cn, [(a.start, a.end) for a in c_atoms])
    p_m = _mask(Pn, [s.span for s in st])
    s_m = _mask(Sn, [(a.start, a.end) for a in s_all])
    c, p, s = javal.normalize_ja(c_m), javal.normalize_ja(p_m), javal.normalize_ja(s_m)
    warnings = [W_FROM_SECONDARY]
    listen: list = []
    if any(x.status == "EXPLAINED" for x in st):
        warnings.append(W_GARBLE_EXPLAINED)
        listen.append("garble_explained(TTS不自然な間の可能性)")
    if c != p:
        if pron_hira(c) != pron_hira(p):
            return BResult(False, "primary_reading_differs", "primary_reading", atoms=st)
        blk = c2_blocked(cls, c, p)
        if blk:
            return BResult(False, blk, "C2_heterophone", atoms=st)
        warnings.append(W_PRON)
        listen.append("pron_equivalent(v2読み規則)")
    if sec._has_negation_ja_text(c_m) != sec._has_negation_ja_text(p_m):
        return BResult(False, "negation_after_mask", "negation", atoms=st, protected=True)
    conflict = False
    if s != c and pron_hira(s) != pron_hira(c):              # Secondaryの残りの読みが原稿(=Primaryが保証した読み)と食い違う=警告(vetoにしない)
        conflict = True
        warnings.append(W_SECONDARY_READING_CONFLICT)
        listen.append("secondary_reading_conflict(Primary読みを正とする)")
    if listen:
        warnings.append(W_LISTEN_ADVISED)
    audit = {"composite_contributed": True, "reading_source": "primary", "value_source": "secondary",
             "reading_rule": "v2:normalize_ja_exact_or_particle_pron+c2_blocked+A7",
             "explained_spans": [{"canon": x.surface, "primary_run": x.primary_run, "detail": x.detail} for x in st if x.status == "EXPLAINED"],
             "secondary_reading_conflict": conflict, "atom_count": len(c_atoms)}
    return BResult(True, "composite_value_secondary_reading_primary", None, COMPOSITE_LABEL, tuple(warnings), st,
                   listen_advised=bool(listen), listen_reasons=tuple(listen), audit=audit)


def composite_judge(canonical_text: str, primary_text: Optional[str], secondary_text: Optional[str],
                    secondary_meta: Optional[dict] = None, expected_readings: Optional[dict] = None) -> BResult:
    """純関数。呼出側がPrimary NGかつSecondary取得成功のときだけ呼ぶ。最終ANDゲートは呼出側が常に通す。
    secondary_meta = {'engine','wav_sha256','model_id','phrase_list_hash'} が無ければ fail-closed(保存を配線前提にする)。"""
    meta = secondary_meta or {}
    if meta.get("precheck"):
        return BResult(False, "precheck_meta_not_final", "precheck_not_final")
    if not (meta.get("engine") and meta.get("wav_sha256")) or str(meta.get("wav_sha256")).startswith("nosha:"):
        return BResult(False, "secondary_provenance_missing", "secondary_provenance_missing")
    if "phrase_list_hash" not in meta or meta.get("phrase_list_hash") not in ("", None):   # M-7: Azureへ原稿を渡していないことを確認できなければfail-closed
        return BResult(False, "phrase_list_hash_not_empty_or_unknown", "M7_witness_independence")
    r = composite_core(canonical_text, primary_text, secondary_text, expected_readings)
    if r.equal:
        r.audit.update(secondary_engine=meta["engine"], secondary_wav_sha256=meta["wav_sha256"], secondary_model_id=meta.get("model_id"),
                       phrase_list_hash=meta.get("phrase_list_hash") or "",
                       secondary_transcript=secondary_text, primary_transcript=primary_text, canonical_text=canonical_text)
    return r


def precheck_composite(canonical_text: str, primary_text: Optional[str], expected_readings=None) -> PrecheckResult:
    """S:=原稿として『Secondaryが台本通りの値を返したら composite が成立し得るか』だけを返す。最終判定へ流用しない。"""
    r = composite_core(canonical_text, primary_text, canonical_text, expected_readings)
    return PrecheckResult(bool(r.equal), r.why, r.blocked_by)


# ============================================================
# S2: β救済(JA adapter内。unified_judge無改変)
# ============================================================
def _secondary_failure_bookkeeping(rs, ctx, err: str) -> None:
    """R-2: βのSecondary追加呼出の失敗も、unified_judgeと同じ規約でrun状態へ計上する(判定は元のNGのまま。circuit到達で他segmentを技術STOPへ)。"""
    if rs is None:
        return
    rs.secondary_calls += 1
    rs.secondary_consecutive_failures += 1
    rs.secondary_failures_total += 1
    rs.technical_stop_events.append({"type": "SECONDARY_UNAVAILABLE", "segment_key": ctx.segment_key, "slot": ctx.slot, "error": err,
                                     "restartable": True, "approval_required": False, "source": "ja_v2beta_beta_call"})
    if rs.secondary_consecutive_failures >= rs.circuit_breaker_threshold and not rs.circuit_open:
        rs.circuit_open = True
        rs.technical_stop_events.append({"type": "SECONDARY_CIRCUIT_OPEN", "after_failures": rs.secondary_consecutive_failures,
                                         "restartable": True, "approval_required": False, "source": "ja_v2beta_beta_call"})


def maybe_beta_rescue(st: V2bState, jr, *, ctx, canonical_text: str, primary_text: Optional[str], length_ok: bool,
                      secondary_fn, no_speech_sentinel: str, expected_readings=None):
    """S2: unified_judgeが返した直後の判定`jr`がNGで、βの発火理由(ELIG)かつ全前提を満たすときだけ、PASS_WITH_WARNINGの新`JudgeResult`を返す。
    それ以外は元の`jr`をそのまま返す(fail-closed)。例外は呼出側(er007)がL0へ戻す(is_config_stop_errorは再送出)。"""
    if not st.usable or jr.verified or jr.secondary_unavailable:
        return jr
    rc = jr.reason_code or ""
    if not any(rc.startswith(e) for e in ELIG):
        return jr
    audit = jr.audit_record
    if primary_text is None or not str(primary_text).strip():
        return jr
    if getattr(ctx, "phrase_list_hash", "") != "":                      # M-7
        st.beta_skipped = "M7_phrase_list_hash_not_empty"
        return jr
    ln = audit.get("length") or {}
    if length_ok is not True or ln.get("primary_ok") is False:         # M-3: 長さ判定はPrimary由来(fail-closed)。長さNGのattemptをβが救済しない
        st.beta_skipped = "M3_primary_length_ng"
        return jr
    rs = getattr(ctx, "run_state", None)
    if rs is not None and rs.circuit_open:                              # M-1: circuit open時は追加Secondary呼出をしない
        st.beta_skipped = "circuit_open"
        return jr
    sha = ctx.sha()
    if not sha or str(sha).startswith("nosha:"):
        st.beta_skipped = "provenance_sha_missing"
        return jr
    sec_a = audit["secondary"]
    stext = sec_a.get("text")
    if stext is not None and (sec_a.get("label") == "NO_SPEECH" or stext == no_speech_sentinel or sec_a.get("error")):
        st.beta_skipped = "secondary_no_speech_or_error"            # R-1: NO_SPEECH転写はβの入力にしない
        return jr
    if not stext:
        pc = precheck_composite(canonical_text, primary_text, expected_readings)
        if not pc.may_call_secondary:
            st.beta_skipped = f"precheck:{pc.blocked_by or pc.why}"
            return jr                                                   # 費用0: 事前判定が成立し得ないときAzureを呼ばない
        import time as _time
        cache_ = ctx.cache if ctx.cache is not None else uj.SecondaryCache()
        key = (sha, ctx.engine, "ja", ctx.phrase_list_hash)             # unified_judge(:663)と同一key=同一shaのSecondaryは重複0円
        ts = _time.time()
        exc, outcome, was_cached = None, None, False
        try:
            outcome, was_cached = cache_.get_or_call(key, lambda: secondary_fn(ctx))
        except Exception as e:  # noqa: BLE001  障害は元のNGのまま(PASS不可)
            if uj.is_config_stop_error(e):
                raise
            exc = f"{type(e).__name__}: {e}"
        st.secondary_called_by_beta = True
        sec_a["called"] = not was_cached
        sec_a["cached"] = was_cached
        audit["timing"]["secondary_ms"] = int((_time.time() - ts) * 1000)
        if not was_cached:                                              # M-2: unified_judge(:684-689)と同じ費用・呼出回数の計上
            jpy = uj.est_jpy_for_seconds(ctx.audio_seconds)
            audit["cost"] = {"azure_calls": 1, "azure_seconds": ctx.audio_seconds, "est_jpy": jpy if jpy is not None else 0.0,
                             "est_jpy_known": jpy is not None, "source": "ja_v2beta_beta_call"}
            if rs is not None and jpy:
                rs.est_jpy_total += jpy
        if exc is not None or outcome is None or not outcome.ok:
            err = exc or (outcome.error if outcome is not None else None) or "secondary_empty"
            sec_a["error"] = err
            _secondary_failure_bookkeeping(rs, ctx, err)               # M-2/R-2
            st.beta_skipped = "secondary_unavailable"
            return jr
        if rs is not None and not was_cached:
            rs.secondary_calls += 1
            rs.secondary_consecutive_failures = 0
        stext = outcome.text
        sec_a.update(text=stext, label=getattr(outcome, "label", "") or "")
        if stext == no_speech_sentinel or getattr(outcome, "label", "") == "NO_SPEECH":
            st.beta_skipped = "secondary_no_speech"
            return jr
        svg0 = _d().vg.value_guard(canonical_text, stext, "ja")       # 取得転写の保護情報を記録(ガード判定自体は composite_judge が全て行う)
        audit.setdefault("value_guard", {})["secondary"] = svg0.to_dict()
        audit.setdefault("negation_guard", {})["secondary"] = bool(uj.negation_diff(canonical_text, stext, "ja"))
    b = composite_judge(canonical_text, primary_text, stext,
                        {"engine": "azure", "wav_sha256": sha, "model_id": "azure-speech-stt", "phrase_list_hash": ctx.phrase_list_hash},
                        expected_readings)
    if not b.equal:
        st.beta = {"composite_contributed": False, "blocked_by": b.blocked_by, "why": b.why}
        return jr
    # ---- 成立: PASS_WITH_WARNING の新JudgeResult ----
    original = {"state": jr.state, "reason_code": jr.reason_code}
    warnings = list(jr.warning_labels) + list(b.warnings) + [W_NEWLAYER_BETA]
    if getattr(ctx, "script_version", "v0") == "v1":
        warnings.append(uj.W_LR_REWRITTEN)
    warnings = list(dict.fromkeys(warnings))
    audit["state"], audit["reason_code"], audit["warnings"] = uj.PASS_WITH_WARNING, BETA_REASON_CODE, warnings
    svg = (audit.get("value_guard") or {}).get("secondary") or {}
    audit["final_gate"] = {"applied": True, "target": "secondary", "value_guard": svg.get("kind"),
                           "negation_diff": (audit.get("negation_guard") or {}).get("secondary"), "source": "ja_v2beta_beta"}
    sec_a["accepted"] = True
    sec_a["label"] = BETA_SECONDARY_LABEL
    sec_a["unavailable"] = False
    sec_a["provenance_complete"] = bool(stext) and bool(sec_a.get("engine")) and bool(sha) and not str(sha).startswith("nosha:")
    audit["technical_stop"] = None
    beta_rec = dict(b.audit)
    beta_rec.update(original=original, listen_advised=bool(b.listen_advised), listen_reasons=list(b.listen_reasons),
                    expected_readings=expected_readings if expected_readings else None)
    st.beta = beta_rec
    st.layers.append({"layer": "beta", "side": "primary+secondary", "cause": "value=secondary/reading=primary", "effective": True})
    return uj.JudgeResult(uj.PASS_WITH_WARNING, warnings, audit, BETA_REASON_CODE, False)


# ============================================================
# S2後半/S3: 実効判定(R-3)・警告付与・PASS->PASS_W格上げ(M-6)・監査記録
# ============================================================
_SECONDARY_PATH_REASONS = ("secondary_confirmed", "secondary_confirmed_primary_length_ng", "force_secondary_agreed")


def resolve_effectiveness(st: V2bState, jr) -> None:
    """R-3: 救済の実体は『確定した通過経路』から決める。Primary側v2は Primary通過(P3へ降格しない)のとき、Secondary側v2は Secondary受理で通ったときだけ effective。"""
    passing = jr.state in uj.PASSING_STATES
    audit = jr.audit_record
    rc = jr.reason_code or ""
    p3 = audit.get("p3_entry")
    for x in st.layers:
        if x["layer"] == "beta":
            x["effective"] = bool(passing and rc == BETA_REASON_CODE)
        elif x["side"] == "primary":
            x["effective"] = bool(passing and p3 is None and rc.startswith("primary_pass"))
        elif x["side"] == "secondary":
            x["effective"] = bool(passing and st.secondary_layer_accepted and rc in _SECONDARY_PATH_REASONS)


def apply_secondary_layer_contribution(st: V2bState, jr):
    """M-6: Secondary側v2が合否に寄与(effective)したとき、(1) 新層警告を追記 (2) state=PASSならPASS_WITH_WARNINGへ格上げ。JudgeResultを再構築し audit も更新。"""
    resolve_effectiveness(st, jr)
    eff_sec = [x for x in st.layers if x["side"] == "secondary" and x.get("effective")]
    if not eff_sec:
        return jr
    audit = jr.audit_record
    add = []
    for x in eff_sec:
        w = W_NEWLAYER_PRON if x["layer"] == "v2_pron" else W_NEWLAYER_VALUE_BEYOND
        if w not in add:
            add.append(w)
    warnings = list(dict.fromkeys(list(jr.warning_labels) + add))
    state = jr.state
    if state == uj.PASS:
        state = uj.PASS_WITH_WARNING
    audit["state"], audit["warnings"] = state, warnings
    return uj.JudgeResult(state, warnings, audit, jr.reason_code, jr.secondary_unavailable)


def rescue_basis_of(st: V2bState, jr) -> Optional[str]:
    resolve_effectiveness(st, jr)
    eff = [x for x in st.layers if x.get("effective")]
    if any(x["layer"] == "beta" for x in eff):
        return "beta"
    if eff:
        return "v2"
    return None


def weak_rank(rec: dict) -> int:
    """R-6: 証拠の弱い順(小さいほど弱い=先頭表示)。0=Secondary読み相違あり / 1=garble説明 / 2=発音同一 / 3=その他の新方式。"""
    labels = set(rec.get("warnings") or []) if isinstance(rec, dict) else set()
    if W_SECONDARY_READING_CONFLICT in labels:
        return 0
    if W_GARBLE_EXPLAINED in labels:
        return 1
    if W_PRON in labels or W_NEWLAYER_PRON in labels:
        return 2
    return 3


def _reason_ja(st: V2bState, jr, basis: Optional[str]) -> Optional[str]:
    if basis is None:
        return None
    if basis == "beta":
        b = st.beta or {}
        parts = ["数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。"]
        spans = b.get("explained_spans") or []
        if spans:
            parts.append("Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: "
                         + "、".join(f"{s.get('canon')}←{s.get('primary_run')}({s.get('detail')})" for s in spans) + "。")
        if W_PRON in (jr.warning_labels or []):
            parts.append("Primaryの読みは助詞は→わ等の発音形でのみ一致。")
        if b.get("secondary_reading_conflict"):
            parts.append("Secondaryの残りの読みが原稿と食い違う(Secondaryが別内容を聞いた可能性。Primaryの読みを正とした)。")
        return "".join(parts)
    causes = [x.get("cause") for x in st.layers if x.get("layer") in ("v2_pron", "v2_value_only") and x.get("effective")]
    kinds = {x.get("layer") for x in st.layers if x.get("effective")}
    txt = "v2読み規則: " + ("値の表記差(三十人=30人、桁区切りの有無等)と発音形の一致のみ" if "v2_pron" in kinds else "受理済み範囲を上回る値表記差のみ")
    return txt + f"(原因={'/'.join(str(c) for c in causes if c)})。読み・値は原稿と同等と判定。"


def finalize_audit(st: V2bState, audit: dict, jr, *, human_review_required: bool, error: Optional[str] = None) -> None:
    """S3。auditへ additive に verdict/rescue_basis/judge_rule_version/ja_v2beta を追加。scope外(active=Falseかつdisabled_by無し)は呼出側が呼ばない=キー自体を作らない。"""
    block: dict = {"active": bool(st.active), "scope": st.scope}
    if st.disabled_by:
        block["disabled_by"] = st.disabled_by
    if st.blocked_by:
        block["blocked_by"] = st.blocked_by
    if error:
        block["error"] = error
    if not st.active:
        audit["ja_v2beta"] = block
        return
    basis = rescue_basis_of(st, jr)
    state = jr.state
    if state == uj.PASS:
        verdict = "PASS"
    elif state == uj.PASS_WITH_WARNING:
        verdict = "PASS_W"
    elif human_review_required:
        verdict = "HR"
    else:
        verdict = "NG"
    audit["verdict"] = verdict
    audit["rescue_basis"] = basis
    audit["judge_rule_version"] = JUDGE_RULE_VERSION
    block["layers"] = [dict(x) for x in st.layers]
    if st.beta_skipped:
        block["beta_skipped"] = st.beta_skipped
    if st.errors:
        block["error"] = "; ".join(st.errors)
    if st.beta is not None:
        block["beta"] = st.beta
    if basis:
        block["rescue_basis"] = basis
        block["rescue_reason_ja"] = _reason_ja(st, jr, basis)
        audit["rescue_reason_ja"] = block["rescue_reason_ja"]
        block["weak_rank"] = weak_rank({"warnings": list(jr.warning_labels or [])})
        if st.expected_readings:
            block["expected_readings"] = st.expected_readings
    audit["ja_v2beta"] = block


# ============================================================
# 再利用(Master Audio Store・継承・resume)用: 寄与検出と API 0 再判定
# ============================================================
def contributed(aj) -> bool:
    """この判定recordで新方式が**確定した通過経路**として寄与したか(R-3。NG recordに警告が残っても真にならない)。fail-closed: 壊れた/旧形式でも警告が残る場合は真。"""
    if not isinstance(aj, dict) or aj.get("state") not in uj.PASSING_STATES:
        return False
    v = aj.get("ja_v2beta")
    if isinstance(v, dict) and isinstance(v.get("layers"), list):
        return any(isinstance(x, dict) and x.get("effective", True) for x in v["layers"])
    if aj.get("rescue_basis"):
        return True
    return any(str(w).startswith(NEWLAYER_PREFIX) for w in (aj.get("warnings") or []))


def rejudge_contributed(aj: dict, orig_fn=None) -> tuple:
    """版不一致の寄与recordを**API 0**(Reading Resolver=LLMなし・Secondary新規呼出なし)で現行規則により再判定する。
    戻り=(ok, reason)。保存データが欠けていれば (False, 'provenance_missing:...')。"""
    try:
        D = _d()
        v = aj.get("ja_v2beta") or {}
        canon = aj.get("canonical_text") or (v.get("beta") or {}).get("canonical_text")
        ptext = (aj.get("primary") or {}).get("text")
        stext = (aj.get("secondary") or {}).get("text")
        if not canon:
            return False, "provenance_missing:canonical_text"
        eff = [x for x in (v.get("layers") or []) if isinstance(x, dict) and x.get("effective", True)]
        if not eff:
            return False, "provenance_missing:layers"
        er = v.get("expected_readings") or (v.get("beta") or {}).get("expected_readings")
        sec = D.sec
        for x in eff:
            if x["layer"] == "beta":
                bm = v.get("beta") or {}
                if not (stext and ptext and bm.get("secondary_wav_sha256") and bm.get("secondary_engine")):
                    return False, "provenance_missing:beta_transcripts_or_sha"
                r = composite_judge(canon, ptext, stext, {"engine": bm["secondary_engine"], "wav_sha256": bm["secondary_wav_sha256"],
                                                        "model_id": bm.get("secondary_model_id"), "phrase_list_hash": bm.get("phrase_list_hash", "")}, er)
                if not r.equal:
                    return False, f"beta_rejudge_ng:{r.blocked_by}"
                continue
            text = ptext if x.get("side") == "primary" else stext
            if not text:
                return False, f"provenance_missing:{x.get('side')}_transcript"
            cls = D.javal.classify_ja_asr_match(canon, text, expected_readings=er, allow_reading_resolver=False)
            cls = sec._apply_variant_layer_voicing_upgrade(canon, text, cls)
            if getattr(cls.protected, "candidate_e_rejections", None) or getattr(cls.protected, "candidate_e_cascade_diffs", None):
                return False, "m6_e3_e4"
            if cls.should_pass:
                continue     # 現行のProduction規則だけで受理される(新層に依存しない)
            r = pron_value_equivalence(canon, text, cls, x.get("side") or "primary")
            if irregular_atoms(canon) or not r.equal or (r.kind == "PRON" and r.cause == "ENGINE_reading_difference"):
                return False, f"v2_rejudge_ng:{r.why}"
        return True, "REJUDGE_OK"
    except Exception as e:  # noqa: BLE001  判定不能は fail-closed(再利用しない)
        return False, f"rejudge_error:{type(e).__name__}"
