# JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07B ②B-light prototype v1 (research/DEV only; NOT imported by Production; API 0; LLM 0).
# 目的: 『Primaryの読み一致』と『Secondary(Azure)の値一致』を atom 単位で組み合わせ、原稿全体を被覆できたときだけ
#       PASS_WITH_WARNING にする純関数 `composite_judge(canonical, primary_text, secondary_text, ...)`。
# 設計の要点 (B_LIGHT_DESIGN_01.md):
#   (i)   Secondaryの値一致だけではPASSしない: 値(Secondary EQUAL) ∧ Primary側の値が矛盾しない ∧ Primary読み(値atomを除いた残り)が
#         原稿と一致、の3つが揃うことを要求する。Secondary側の読みは一切使わない(2026-10-11『Secondary側PHONETIC/助詞差を採用しない』と整合)。
#   (ii)  数値以外の読みは v2 と同じ規則(normalize_ja 完全一致、または助詞は→わ/へ→えのみの発音一致。A7登録読み・C2同形異音・否定差は止める)。
#   (iii) 不規則読み値(Production `is_irregular_sig`)を含む原稿は対象外(NG維持)。
#   (iv)  Primary値とSecondary値の矛盾は NG_PROTECTED: Primary の数値表記が (a)原稿値と等しい か (b)『位取り断片の連結崩れ』で原稿値に説明できる
#         ときだけ矛盾とみなさない。説明できない値違い(8,800・89,000・千九百等)は矛盾=救済しない。
#   (v)   Candidate E(漢字候補総当たり)は使わない。(vii) 最終ANDゲートは呼出側が常に通す(本関数はPASS候補を返すだけ)。
# `allow_explained_garble=False` が案α(Primary値EQUALのみ=v2とほぼ同値の被覆確認)、True が案β(推奨候補)。
# Production関数は import して使い、複製しない(v2 helper `proto_reading_compare_02` も import)。
from __future__ import annotations
import os, re, sys, unicodedata
from dataclasses import dataclass, field
from fractions import Fraction

sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as sec
import er078_asr_value_guard_01 as vg
from er078_asr_unified_judge_01 import negation_diff
import proto_reading_compare_02 as P2

COMPOSITE_LABEL = "JA_SECONDARY_VALUE_PRIMARY_READING_COMPOSITE"
W_FROM_SECONDARY = "JA_COMPOSITE_VALUE_FROM_SECONDARY"            # 非ブロッキング警告: 値の根拠はSecondary(事後試聴対象)
W_GARBLE_EXPLAINED = "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED"  # Primaryの数値崩れを位取り断片で説明した場合
TOKEN = "【値】"

# Primaryの数値run: ASCII数字(カンマ含む)と漢数字。NFKC後の文字列に対して使う。
_RUN_CHARS = "0-9,〇零一二三四五六七八九十百千万億兆"


@dataclass
class AtomStatus:
    surface: str
    value: int
    unit_surface: str
    primary_run: str | None
    status: str            # EQUAL | EXPLAINED | CONTRADICTION | MISSING
    detail: str = ""
    span: tuple | None = None   # Primary側 (start, end) = run+unit


@dataclass
class BResult:
    equal: bool
    why: str
    blocked_by: str | None = None
    label: str | None = None
    warnings: tuple = ()
    atoms: list = field(default_factory=list)
    protected: bool = False     # True = 矛盾/値違いで NG_PROTECTED 相当(Secondaryが値を支持しても救済しない)


def _nfkc(t: str) -> str:
    return unicodedata.normalize("NFKC", t or "")


def _unit_surface(atom_surface: str) -> str:
    return re.sub(r"^[0-9,.〇零一二三四五六七八九十百千万億兆]+", "", atom_surface)


def _segments(run: str):
    """run を (kind, text) の連続断片へ。kind = 'digit'(ASCII数字) | 'kanji'(漢数字)。カンマ等が含まれれば None。"""
    if "," in run:
        return None
    segs, cur, kind = [], "", None
    for ch in run:
        k = "digit" if ch.isdigit() and ch.isascii() else "kanji"
        if k != kind and cur:
            segs.append((kind, cur)); cur = ""
        kind = k
        cur += ch
    if cur:
        segs.append((kind, cur))
    return segs


def _place_ok(frags: list[int]) -> bool:
    """断片の位取りが重ならない: 前の断片 f_i は、後続の断片 f_j の桁数ぶんの末尾0を持つ(8000 と 900 → 8000%1000==0)。"""
    for i, fi in enumerate(frags):
        for fj in frags[i + 1:]:
            if fj <= 0 or fi % (10 ** len(str(fj))) != 0:
                return False
    return True


def explain_garble(run: str, target: int) -> str | None:
    """Primaryの数値run が『位取り断片の連結』として target(原稿値)に説明できるか。説明できれば理由文字列、できなければ None。
    許す形(狭い): F-A=ASCII数字のみのrun を2〜3断片へ分割 / F-B=ASCII数字断片+漢数字断片(万・億・兆を含まない)の2断片。
    いずれも 断片の総和==target ∧ 位取りが重ならない ∧ 先頭0の断片なし。カンマ付きrun(通常の桁区切り表記)は対象外。"""
    segs = _segments(run)
    if not segs:
        return None
    # F-A
    if len(segs) == 1 and segs[0][0] == "digit":
        d = segs[0][1]
        L = len(d)
        for i in range(1, L):
            parts2 = [d[:i], d[i:]]
            for parts in (parts2,) + tuple([[d[:i], d[i:j], d[j:]] for j in range(i + 1, L)]):
                if any(p.startswith("0") for p in parts):      # 先頭0の断片は不可
                    continue
                vals = [int(p) for p in parts]
                if sum(vals) == target and _place_ok(vals) and len(vals) >= 2:
                    return "digit_split:" + "+".join(parts)
        return None
    # F-B
    if len(segs) == 2 and segs[0][0] == "digit" and segs[1][0] == "kanji":
        k = segs[1][1]
        if any(c in k for c in "万億兆"):
            return None
        kv = vg.parse_ja_number(k)
        if kv is None or Fraction(kv).denominator != 1:
            return None
        vals = [int(segs[0][1]), int(kv)]
        if segs[0][1].startswith("0"):
            return None
        if sum(vals) == target and _place_ok(vals):
            return f"digit+kanji:{segs[0][1]}+{k}"
    return None


def analyze_primary_values(canonical_n: str, primary_n: str, allow_explained: bool):
    """原稿の値atomごとに Primary側の数値run を位置合わせして状態を決める。戻り: (atoms_status, c_atoms)。"""
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


def _mask(text: str, spans: list[tuple]) -> str:
    out, pos = [], 0
    for s, e in sorted(spans):
        out.append(text[pos:s]); out.append(TOKEN); pos = e
    out.append(text[pos:])
    return "".join(out)


def composite_judge(canonical_text: str, primary_text: str | None, secondary_text: str | None,
                    expected_readings: dict | None = None, allow_explained_garble: bool = True) -> BResult:
    """純関数。呼出側(adapter)がPrimary NGかつSecondary取得成功のときだけ呼ぶ想定。最終ANDゲートは呼出側が常に通す。"""
    if primary_text is None or not str(primary_text).strip():
        return BResult(False, "primary_none", "primary_unavailable")
    if secondary_text is None or not str(secondary_text).strip():
        return BResult(False, "secondary_none_or_empty", "secondary_unavailable")
    Cn, Pn, Sn = _nfkc(canonical_text), _nfkc(primary_text), _nfkc(secondary_text)
    # --- 否定(P/Sとも。値の根拠より前に止める) ---
    for tag, t in (("primary", primary_text), ("secondary", secondary_text)):
        if negation_diff(canonical_text, t, "ja") or sec._scg_negation_marker_diff(canonical_text, t):
            return BResult(False, f"negation_diff:{tag}", "negation", protected=True)
    # --- 値atom: 原稿 ---
    c_atoms = [a for a in vg.extract_atoms_ja(Cn) if a.kind in ("num", "frac")]
    if not c_atoms:
        return BResult(False, "no_value_atoms_in_canonical", "not_applicable")
    irr = [a.surface for a in c_atoms if a.kind == "num" and vg.is_irregular_sig(a.value, a.unit)]
    if irr:                                                    # (iii) 不規則読み
        return BResult(False, f"irregular_reading_value:{','.join(irr)}", "A4a_irregular_reading")
    # --- Secondary: 値が全atomで一致 ---
    gs = vg.value_guard(canonical_text, secondary_text, "ja")
    if gs.kind != vg.EQUAL:
        return BResult(False, f"secondary_value_guard={gs.kind}", "secondary_value", protected=(gs.kind == vg.DIFF))
    # --- Primary: 値が原稿値と等しい or 位取り断片崩れとして説明できる ---
    st, _ = analyze_primary_values(Cn, Pn, allow_explained_garble)
    bad = [s for s in st if s.status in ("CONTRADICTION", "MISSING")]
    if bad:
        contra = any(s.status == "CONTRADICTION" for s in bad)
        return BResult(False, "primary_value:" + ";".join(f"{s.surface}:{s.status}:{s.detail}" for s in bad),
                       "primary_secondary_value_contradiction" if contra else "primary_value_missing",
                       atoms=st, protected=contra)
    # --- Primary読み: 値atomを除いた残りが原稿と一致 (v2と同じ規則) ---
    cls = javal.classify_ja_asr_match(canonical_text, primary_text, expected_readings=expected_readings, allow_reading_resolver=False)
    rd = sec._scg_reading_dict_reason(cls)
    if rd:
        return BResult(False, rd, "A7_reading_dictionary", atoms=st)
    c_m = _mask(Cn, [(a.start, a.end) for a in c_atoms])
    p_m = _mask(Pn, [s.span for s in st])
    c, p = javal.normalize_ja(c_m), javal.normalize_ja(p_m)
    warnings = [W_FROM_SECONDARY]
    if any(s.status == "EXPLAINED" for s in st):
        warnings.append(W_GARBLE_EXPLAINED)
    if c != p:
        if P2.pron_hira(c) != P2.pron_hira(p):
            return BResult(False, "primary_reading_differs", "primary_reading", atoms=st)
        blk = P2.c2_blocked(cls, c, p)
        if blk:
            return BResult(False, blk, "C2_heterophone", atoms=st)
        warnings.append(P2.W_PRON)
    if sec._has_negation_ja_text(c_m) != sec._has_negation_ja_text(p_m):
        return BResult(False, "negation_after_mask", "negation", atoms=st, protected=True)
    return BResult(True, "composite_value_secondary_reading_primary", None, COMPOSITE_LABEL, tuple(warnings), st)
