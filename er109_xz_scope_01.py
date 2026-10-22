# ============================================================
# er109_xz_scope_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04 (2026-10-23)
# er109 v1(表記違い同音の同値判定層)の Production 配線: Family X / Z の run scope 内でのみ有効にする薄い module。
# Status: APPROVED_FOR_PRODUCTION(Family X/Zのみ、ユーザー正式決定2026-10-23。A/B/C対象外)。WIRED_PENDING_FABLE(Fable受入前)。
#
# 構造(WIRING_DESIGN_03 機構(b)=PNAP `er103_proper_noun_alarm_policy_01` と同型の run scope + 単一flag):
#   - flag: `er109_asr_orthographic_equivalence_01.ORTHOGRAPHIC_EQUIVALENCE_ENABLED`(rollbackスイッチ。env/引数/設定dictから変えられない)。
#   - scope: process内状態。公開は `run_scope(family)`(context manager)と `family_scope(family)`(decorator)のみ(M3: enter/leaveは非公開)。
#     familyはリテラル "X" / "Z" だけ(AST testでリポジトリ全体の呼出点を固定)。
#   - 読取は `is_active_for_run()` 1関数のみ(flag有効 ∧ scope∈{X,Z})。共有経路(adapter/judge/KP voter/再評価/Store guard)は
#     `is_active_for_run()` が False の間は従来コードパスのまま(scope未設定=A/B/C・単体呼出は完全に従来どおり)。
#   - er109本体(`evaluate`)は純関数のまま。本moduleは scope/flag確認(メモ外, M4)と `evaluate` のLRUメモ(純関数のみ)を持つ。
#   - 例外: er109/判定の例外は『同値ではない』(従来の厳しい判定)として扱い、呼出元のauditへ記録する(runは止めない)。
# ============================================================
from __future__ import annotations

import functools
import re
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional

APPROVED_SCOPES = frozenset({"X", "Z"})
_RUN_SCOPE: Optional[str] = None

ORTHO_LABEL = "ORTHOGRAPHIC_EQUIVALENT_MATCH"
ORTHO_BASIS = "ORTHOGRAPHIC_EQUIVALENT_MATCH"   # APPROVED_EQUIVALENCE_BASES には入れない(最終ANDゲートを丸ごとskipさせない。P-06)
W_ORTHO_NEGATION = "ORTHO_NEGATION_WORD_HOMOPHONE"
W_ORTHO_NONREP = "ORTHO_NON_REPRESENTATIVE_VARIANT"
ORTHO_WARNING_LABELS = frozenset({W_ORTHO_NEGATION, W_ORTHO_NONREP})
_WARNING_MAP = {"negation_word_homophone": W_ORTHO_NEGATION, "non_representative_variant_match": W_ORTHO_NONREP}
AUDIT_KEY = "orthographic_equivalence"
OUT_OF_SCOPE_BLOCK_REASON = "ORTHOGRAPHIC_EQUIVALENT_AUDIO_OUT_OF_SCOPE"


# ---------------------------------------------------------------- scope
def _enter_scope(family: str) -> None:
    global _RUN_SCOPE
    if family not in APPROVED_SCOPES:
        raise ValueError(f"unsupported scope: {family!r} (approved: {sorted(APPROVED_SCOPES)})")
    _RUN_SCOPE = family


@contextmanager
def run_scope(family: str):
    """X/Z runnerのTTS段・X専用toolの入口で `with run_scope("X"):`。例外・STOP・途中失敗でも必ずfinallyで復元する(scope残留防止)。
    入れ子: すでにscope内なら外側のscopeを維持する(内側の宣言は無視。外側がZでX関数を呼んでもZのまま)。"""
    global _RUN_SCOPE
    if family not in APPROVED_SCOPES:
        raise ValueError(f"unsupported scope: {family!r} (approved: {sorted(APPROVED_SCOPES)})")
    prev = _RUN_SCOPE
    if prev is None:
        _enter_scope(family)
    try:
        yield
    finally:
        _RUN_SCOPE = prev


def family_scope(family: str):
    """TTS段関数用decorator。`@er109_scope.family_scope("X")`(リテラルのみ)。functools.wrapsで署名・名前を保つ。"""
    if family not in APPROVED_SCOPES:
        raise ValueError(f"unsupported scope: {family!r} (approved: {sorted(APPROVED_SCOPES)})")

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with run_scope(family):
                return fn(*args, **kwargs)
        wrapper.__er109_scoped__ = family
        return wrapper
    return deco


def layer_version() -> str:
    """監査記録用のer109層version(呼出元がer109純関数moduleを直接importしないための窓口)。"""
    import er109_asr_orthographic_equivalence_01 as e109
    return e109.LAYER_VERSION


def current_scope() -> Optional[str]:
    """診断・test用(判定には使わない)。"""
    return _RUN_SCOPE


def is_active_for_run() -> bool:
    """共有経路が参照する唯一の読取関数: flag有効 ∧ X/Z run scope内。(M4: scope/flagの確認はメモの外で毎回行う)"""
    if _RUN_SCOPE not in APPROVED_SCOPES:
        return False
    import er109_asr_orthographic_equivalence_01 as e109
    return e109.is_enabled()


# ---------------------------------------------------------------- 判定(純関数のメモ + 例外時fail-closed)
@functools.lru_cache(maxsize=8192)
def _evaluate_cached(canonical: str, text: str):
    """er109.evaluate のみをメモ化(M4。scope/flagはメモ外)。純関数・API 0。"""
    import er109_asr_orthographic_equivalence_01 as e109
    return e109.evaluate(canonical, text)


@dataclass(frozen=True)
class OrthoDecision:
    canonical: str
    text: str
    eq: object                     # er109.EquivalenceResult
    warning_labels: tuple = ()     # ORTHO_* 警告ラベル(空=決定的規則=警告なし)
    scope: Optional[str] = None

    @property
    def verdict(self) -> str:
        return "PASS_WITH_WARNING" if self.warning_labels else "PASS"

    def site_audit(self, site: str) -> dict:
        eq = self.eq
        return {"site": site, "text": self.text, "verdict": self.verdict, "warnings": list(self.warning_labels), "er109": eq.audit()}


def decision(canonical, text, *, lang: str = "en", sink: Optional[dict] = None) -> Optional[OrthoDecision]:
    """(canonical, text) が発音同値(表記違いのみ)なら OrthoDecision、そうでなければ None(従来の厳しい判定を維持)。
    inactive(flag OFF/scope外)・lang!=en・None/空 は常に None。er109/本module内の例外は None + sink['orthographic_equivalence_error']へ記録(runを止めない)。"""
    if lang != "en" or not is_active_for_run():
        return None
    if not canonical or text is None or not str(text).strip():
        return None
    try:
        import er109_asr_orthographic_equivalence_01 as e109
        eq = _evaluate_cached(canonical, text)
        if (not eq.equivalent) or eq.version != e109.LAYER_VERSION:
            return None
        labels = tuple(dict.fromkeys(_WARNING_MAP.get(w, "ORTHO_" + str(w).upper()) for w in (eq.warnings or [])))
        return OrthoDecision(canonical, text, eq, labels, _RUN_SCOPE)
    except Exception as exc:  # noqa: BLE001  fail-closed: 『同値ではない』として従来判定に委ね、auditへ記録する
        if sink is not None:
            sink.setdefault("orthographic_equivalence_errors", []).append(f"{type(exc).__name__}: {exc}")
        return None


def record_site(audit: dict, site: str, dec: OrthoDecision, *, span_unlock: Optional[dict] = None) -> None:
    """asr_judgement(audit)へ additive に記録する。ortho不使用ならこの関数は呼ばれない=キー自体が存在しない(A/B/C署名不変)。"""
    import er109_asr_orthographic_equivalence_01 as e109
    rec = audit.get(AUDIT_KEY)
    if not isinstance(rec, dict):
        rec = {"applied": True, "version": e109.LAYER_VERSION, "scope": dec.scope, "label": ORTHO_LABEL, "sites": []}
        audit[AUDIT_KEY] = rec
    rec["applied"] = True
    rec["sites"] = [s for s in rec["sites"] if s.get("site") != site] + [dec.site_audit(site)]
    warns = list(rec.get("warnings") or [])
    for w in dec.warning_labels:
        if w not in warns:
            warns.append(w)
    rec["warnings"] = warns
    if span_unlock is not None:
        rec.setdefault("span_unlock", {})[site] = span_unlock


def ortho_contributed(aj) -> bool:
    """M1: この判定record(asr_judgement / asr_judgement_inherited)でer109が合否に寄与したか(層・印の種類ごと)。
      (1) orthographic_equivalence.applied  (2) primary/secondary の label == ORTHO_LABEL
      (3) vote内いずれかの票 label == ORTHO_LABEL  (4) warnings に ORTHO_* のいずれか"""
    if not isinstance(aj, dict):
        return False
    oe = aj.get(AUDIT_KEY)
    if isinstance(oe, dict) and oe.get("applied"):
        return True
    for side in ("primary", "secondary"):
        sub = aj.get(side)
        if isinstance(sub, dict) and sub.get("label") == ORTHO_LABEL:
            return True
    vote = aj.get("vote")
    if isinstance(vote, dict):
        for side in ("primary", "secondary", "whisper"):
            sub = vote.get(side)
            if isinstance(sub, dict) and sub.get("label") == ORTHO_LABEL:
                return True
    return any(w in ORTHO_WARNING_LABELS for w in (aj.get("warnings") or []))


# ---------------------------------------------------------------- P-06: 最終保護Gateのspan単位解除(M7〜M10)
@dataclass(frozen=True)
class ProtectedExplanation:
    explained: bool
    reason: str
    detail: dict = field(default_factory=dict)
    value_unlocked: bool = False
    negation_unlocked: bool = False
    warning_labels: tuple = ()



def _token_regex(tok: str):
    """token境界一致: `1` が `21's` / `1.5` / `1,000` / `3:15` に一致しない(M8b)。"""
    return re.compile(r"(?<![0-9A-Za-z])(?<!\d[.,:/])" + re.escape(str(tok).lower()) + r"(?![0-9A-Za-z])(?![.,:/]\d)")


def _occurrences(token, surfaces: list) -> list:
    rx = _token_regex(token)
    return [i for i, s in enumerate(surfaces) if rx.search(str(s).lower())]


def explain_protected(dec, vgr, neg_diff: bool, canonical: str, text: str) -> ProtectedExplanation:
    """最終ANDゲート(値DIFF/否定差)を、er109の同値spanで説明できる場合に限って解除してよいか(WIRING_DESIGN_03 §C-3、Opus M7〜M10)。
    fail-closed: 1つでも説明できない差があれば explained=False(従来どおりNG)。AMBIGUOUSは解除しない(呼出元が従来どおりP3降格/Secondary NG)。
    M9: 判定対象一致(dec.canonical==canonical ∧ dec.text==text)のときのみ。Primaryは gate_text、Secondaryは stext を渡すこと。"""
    import er078_asr_unified_judge_01 as uj
    import er109_asr_orthographic_equivalence_01 as e109
    if dec is None:
        return ProtectedExplanation(False, "no_orthographic_decision")
    if dec.canonical != canonical or dec.text != text:
        return ProtectedExplanation(False, "decision_target_mismatch")
    eq = dec.eq
    if (not getattr(eq, "equivalent", False)) or getattr(eq, "version", None) != e109.LAYER_VERSION:
        return ProtectedExplanation(False, "decision_not_equivalent_or_version_mismatch")
    spans = [s for s in eq.spans if s.equivalent]
    detail: dict = {"layer_version": eq.version, "spans": [{"canon": list(s.canon_span), "asr": list(s.asr_span), "rule": s.rule,
                                                          "warnings": list(s.warnings)} for s in spans]}
    value_unlocked = False
    # ---- 値DIFF ----
    if any(p.verdict == uj.vg.AMBIGUOUS for p in (vgr.pairs if vgr is not None else ())):
        return ProtectedExplanation(False, "ambiguous_value_pair_present", detail)      # AMBIGUOUS(Point to / Point 2.)は解除しない(P3降格・SecondaryでもNG)
    diff_pairs = [p for p in (vgr.pairs if vgr is not None else ()) if p.verdict == uj.vg.DIFF]
    if diff_pairs:
        if not spans:
            return ProtectedExplanation(False, "value_diff_without_equivalent_span", detail)
        used: set = set()
        mapping = []
        for p in diff_pairs:
            if p.src is None and p.hyp is None:
                return ProtectedExplanation(False, "value_diff_pair_without_token", detail)
            placed = None
            for si, s in enumerate(spans):
                c_surf, a_surf = [str(x) for x in s.canon_span], [str(x) for x in s.asr_span]
                c_occ = [i for i in _occurrences(p.src, c_surf) if ("c", si, i) not in used] if p.src is not None else None
                a_occ = [i for i in _occurrences(p.hyp, a_surf) if ("a", si, i) not in used] if p.hyp is not None else None
                if (c_occ is not None and not c_occ) or (a_occ is not None and not a_occ):
                    continue            # src/hyp両方ありは同一span必須(M8c)。片側だけなら存在する側だけ要求
                placed = (si, c_occ[0] if c_occ else None, a_occ[0] if a_occ else None)
                break
            if placed is None:
                return ProtectedExplanation(False, "value_diff_not_explained_by_span", {**detail, "unexplained_pair": {"src": p.src, "hyp": p.hyp}})
            si, ci, ai = placed
            if ci is not None:
                used.add(("c", si, ci))
            if ai is not None:
                used.add(("a", si, ai))
            mapping.append({"pair": {"src": p.src, "hyp": p.hyp, "reason": p.reason}, "span_index": si,
                            "canon_unit": (str(spans[si].canon_span[ci]) if ci is not None else None),
                            "asr_unit": (str(spans[si].asr_span[ai]) if ai is not None else None)})
        detail["value_pairs"] = mapping            # M8d: 対応表を全記録
        value_unlocked = True
    # ---- 否定差(M7) ----
    negation_unlocked = False
    if neg_diff:
        if not spans:
            return ProtectedExplanation(False, "negation_diff_without_equivalent_span", detail)
        sum_c: Counter = Counter()
        sum_a: Counter = Counter()
        neg_spans = []
        for si, s in enumerate(spans):
            cc = uj.negation_counter(" ".join(str(x) for x in s.canon_span))
            ca = uj.negation_counter(" ".join(str(x) for x in s.asr_span))
            sum_c.update(cc)
            sum_a.update(ca)
            if cc != ca:
                if "negation_word_homophone" not in (s.warnings or []):
                    return ProtectedExplanation(False, "negation_span_without_homophone_warning", detail)
                neg_spans.append(si)
        tot_c, tot_a = uj.negation_counter(canonical), uj.negation_counter(text)
        res_c, res_a = tot_c - sum_c, tot_a - sum_a
        if (res_c + sum_c) != tot_c or (res_a + sum_a) != tot_a:
            return ProtectedExplanation(False, "negation_span_count_exceeds_total", detail)
        if res_c != res_a:
            return ProtectedExplanation(False, "negation_diff_outside_equivalent_spans", {**detail, "residual": {"canon": dict(res_c), "asr": dict(res_a)}})
        if not neg_spans:
            return ProtectedExplanation(False, "negation_diff_not_explained", detail)
        detail["negation_spans"] = neg_spans
        negation_unlocked = True
    if not (value_unlocked or negation_unlocked):
        return ProtectedExplanation(False, "nothing_to_unlock", detail)
    labels = (W_ORTHO_NEGATION,) if negation_unlocked else ()
    return ProtectedExplanation(True, "explained_by_equivalent_spans", detail, value_unlocked, negation_unlocked, labels)
