# ============================================================
# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_02b
# 共通判定(統一ASR判定の状態機械)。role・言語共通。1音声=1 attemptごとに1回呼ぶ。
#
# 状態: 作業branch feat/auw-unified-asr-01 上の新規moduleのみ。**Production未配線**(既存2関数のadapter化は委任_03/04)。
#       既存Production関数(er006_secondary_asr_01 / er007_* / runner群)は変更しない。API呼出は一切持たない
#       (Secondary呼出は呼出側が注入するcallable `secondary_fn`のみ。本moduleはmock engineで検証可能)。
# 仕様の正本: DESIGN_01.md §4-3(状態機械) + DESIGN_02_ADDENDUM_01.md §1-3(AMBIGUOUS=P3)・§4(障害処理)・§7(費用)。
#
# 状態機械(Primary NGの場合のみSecondary):
#   Primary ASR取得失敗(text=None)                      -> NG_PRIMARY_ASR_FAILURE
#   Primary PASS -> 最終ANDゲート(値DIFF/否定差を再確認。承認済みequivalence根拠はskip) -> PASS / PASS_WITH_WARNING
#        (最終ゲートでAMBIGUOUS[根拠なし]は「10分のまま通さない」ためP3へ降格)
#   Primary NG:
#     P1 保護差(値DIFF / 否定差)                          -> NG_PROTECTED       [Secondary不呼出]
#     P2 除外表(SCG_EXCLUSIONS)に該当                      -> NG_EXCLUDED        [Secondary不呼出]
#     P3 それ以外(値AMBIGUOUS含む)                          -> Secondary 1回(SecondaryCacheで同一wavは1回)
#          取得不能(None/空/例外/circuit open)              -> NG_SECONDARY_UNAVAILABLE [PASS不可。技術STOP記録、Lock状態は増やさない]
#          Secondary転写に保護差(値DIFF/否定)                -> NG_BOTH
#          許容集合PASS かつ 最終ANDゲートOK                 -> PASS_WITH_WARNING(SECONDARY_CONFIRMED。値AMBIGUOUS時は
#                                                              Secondary転写が原稿と同一表層の場合のみNUMERIC_AMBIGUOUS_SURFACE)
#          それ以外                                          -> NG_BOTH
# 言語別Secondary許容集合は本module内に再実装しない。`secondary_fn`の戻り値(accepted)または`secondary_accept_fn`(注入callable)で受ける。
# ============================================================
from __future__ import annotations

import hashlib
import math
import re
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

import er003_audio_tts_asr_safety as _safety
import er006_preprod_hardening_01_validation as _val
import er078_asr_value_guard_01 as vg

# ---- 状態 ----
PASS = "PASS"
PASS_WITH_WARNING = "PASS_WITH_WARNING"
NG_PROTECTED = "NG_PROTECTED"
NG_EXCLUDED = "NG_EXCLUDED"
NG_BOTH = "NG_BOTH"
NG_SECONDARY_UNAVAILABLE = "NG_SECONDARY_UNAVAILABLE"
NG_PRIMARY_ASR_FAILURE = "NG_PRIMARY_ASR_FAILURE"
STATES = (PASS, PASS_WITH_WARNING, NG_PROTECTED, NG_EXCLUDED, NG_BOTH, NG_SECONDARY_UNAVAILABLE, NG_PRIMARY_ASR_FAILURE)
PASSING_STATES = (PASS, PASS_WITH_WARNING)

# ---- warningラベル ----
W_SECONDARY_CONFIRMED = "SECONDARY_CONFIRMED"
W_NUMERIC_AMBIGUOUS_SURFACE = "NUMERIC_AMBIGUOUS_SURFACE"
W_LR_REWRITTEN = "LR_REWRITTEN"
W_JA_NUMERIC_IRREGULAR_READING = vg.WARN_IRREGULAR_READING

# ---- 最終ANDゲートが再否定しない承認済みequivalence根拠(ctx/primary_resultの`equivalence_basis`で受け取る) ----
APPROVED_EQUIVALENCE_BASES = frozenset({
    "HOMOPHONE_MATCH_NUMBER_EXCEPTION",   # er006_preprod_hardening_01_validation.py:905/1066
    "TIER1_DIFF_ANCHORED",                # er021 Tier1(strict版、2026-09-28承認)
    "TIER1_NUMERIC_EQUIVALENCE",
    "READING_MATCH",                      # er007 読み一致(JA)
})

# ---- U1(委任_10、2026-10-16ユーザー指示A-2/A-3「承認済み仕様への実装修正」。解放実装・Regression済み。既定は条件付きSTOP s1により暫定True) ----
# 既定の経緯: live負例対照でPrimary PASS 3件(Secondary不呼出=U1と無関係)が出たためs1に従いTrueのままcommit。Fableが採否判断し1行でFalse化する。
# False=JAの類似度<0.4(A5)・C1固有名詞差(A6: entity_like・辞書未登録Latin語)のP2事前除外を撤廃し、Primary NGなら原則Secondaryへ回す。
# True=旧挙動(A5/A6をP2除外のまま。ロールバック用。unit testでmonkeypatchして固定)。
# 例外として残す除外: A1/A2(P1 数値DIFF・否定差)、A3(length NG。Primary転写由来で「独立QA」ではない→OPEN起票済み)、
#   A4(C2同形異音候補、2026-10-11ユーザー逐語採用)、A7(登録読み辞書不一致=登録読み保護。Secondaryの表層一致は読みの正しさを
#   証明しないため、2026-10-11安全条件[読みでの受理禁止]に従い事前除外のまま。U1フラグの対象外)。
# U2(force_secondary)の死定数U2_FORCE_SECONDARY_SCOPEは委任_10で撤去(どこからも参照されていなかった。実体は呼出側の
#   er003_v1_crosslevel_audio_02_common.py `_run_a2_minimal_fallback_attempt` の force_secondary=True 1箇所のみ。静的testで固定)。
U1_KEEP_C1_SIMILARITY_EXCLUSIONS = True   # 委任_10 s1条件付きSTOPにより暫定True(実装・Regressionは完了。Fableの採否判断で1行False化)

# ---- 費用(秒数ベース。SCGと同じ式: er007_ja_secondary_asr_01.py:309-311、単価 SCG_AZURE_USD_PER_HOUR/SCG_JPY_PER_USD と同値。parity testで突合) ----
AZURE_USD_PER_HOUR = 1.0
JPY_PER_USD = 160.0
# COST_GUARD($0.05/segment, er006_secondary_asr_01.COST_GUARD_MAX_USD_PER_SEGMENT)の結論(委任_03確定、IMPLEMENTATION_03.md §4):
#   旧Cascadeの累積は固定概算定数(0.000002+0.00001x2)で最大でも約$0.000022のため、$0.05には構造上到達しない「実質無効」だった。
#   統一判定ではSecondaryがwav(sha256)あたり最大1回(SecondaryCache)かつcircuit breakerで有界。そこで**実費(秒数ベース、本module
#   の`AZURE_USD_PER_HOUR`)で等価に適用**する: adapter(er006_secondary_asr_01)のsecondary_fnが、Secondary呼出前に
#   「1回分の見積費用 > COST_GUARD_MAX_USD_PER_SEGMENT(= $0.05 = 音声180秒超)」を検査し、超過ならSecondaryを呼ばずfail-closed
#   (NG_SECONDARY_UNAVAILABLE相当、cost_guard_triggered=True)にする。judge本体は純粋(API/費用判断を持たない)ため適用点はadapter。
COST_GUARD_IN_UNIFIED_JUDGE = "APPLIED_AT_ADAPTER_SECONDARY_FN_ACTUAL_SECONDS_03"

CIRCUIT_BREAKER_THRESHOLD = 3  # run単位。連続Secondary障害がこの回数でそのrunのSecondary呼出を止める


def is_config_stop_error(exc: BaseException) -> bool:
    """委任_06c(OF-AUW-C-02): 設定不備として握りつぶしてはならない例外(er005_cost_loggerの「init_logger未呼出」・
    「[STOP] 単価未登録」RuntimeError)。Secondary障害(NG_SECONDARY_UNAVAILABLE)に変換せず再送出する。
    既存方針: er003_v1_n3_01_tts_generate.py `_post_slowdown_unified_judge`(init_logger/[STOP]は伝播)。"""
    if not isinstance(exc, RuntimeError):
        return False
    msg = str(exc)
    return ("init_logger" in msg) or msg.startswith("[STOP]") or "[STOP]" in msg


def est_jpy_for_seconds(audio_seconds) -> float | None:
    if audio_seconds is None:
        return None
    return round(math.ceil(audio_seconds) * AZURE_USD_PER_HOUR / 3600.0 * JPY_PER_USD, 4)


# ============================================================
# 除外表(データ化)
# ============================================================
@dataclass(frozen=True)
class ExclusionRule:
    rule_id: str
    description: str
    stage: str          # "P1"(保護差) / "P2"(除外)
    langs: tuple
    signal: str         # primary_result.signals / ctx のキー
    u1_gated: bool = False   # U1_KEEP_C1_SIMILARITY_EXCLUSIONSがTrueの間のみ有効(旧挙動ロールバック用)


SCG_EXCLUSIONS = (
    ExclusionRule("A1_NUMBER_DIFF", "数字差は『値DIFF』のみ除外(表記差は除外しない=旧過剰制限の撤廃)", "P1", ("en", "ja"), "value_guard=DIFF"),
    ExclusionRule("A2_NEGATION_DIFF", "否定差/JA否定マーカー差(既存保護の維持)", "P1", ("en", "ja"), "negation_diff"),
    ExclusionRule("A3_LENGTH_NG", "length NG(Secondaryで救えてもlength ANDで不合格)", "P2", ("en", "ja"), "length_ok=False"),
    ExclusionRule("A4_C2_HOMOGRAPH", "C2同形異音候補(Azureが原稿の漢字表記と一致しても読み違いを区別できない)", "P2", ("ja",), "c2_homophone_candidate"),
    ExclusionRule("A5_SIMILARITY_LT_0_4", "類似度<0.4(U1フラグがTrueの間のみ有効)", "P2", ("ja",), "similarity<0.4", u1_gated=True),
    ExclusionRule("A6_C1_PROPER_NOUN_DIFF", "C1固有名詞差(U1フラグがTrueの間のみ有効)", "P2", ("ja",), "c1_proper_noun_diff", u1_gated=True),
    ExclusionRule("A7_READING_DICT_MISMATCH", "登録読み保護: Primaryが登録読み辞書expected_readingsとの不一致を具体的に示した(Secondaryの表層一致は読みの正しさを証明しない。2026-10-11安全条件)", "P2", ("ja",), "reading_dictionary_mismatch"),
)
SCG_MIN_SIMILARITY = 0.4  # er007_ja_secondary_asr_01.SCG_MIN_SIMILARITY と同値(parity testで突合)


def _exclusion_hit(ctx: "AttemptCtx", primary: "PrimaryResult", lang: str):
    """P2除外表の該当ルールidを返す(なければNone)。P1相当(A1/A2)は別途判定。"""
    sig = primary.signals or {}
    for rule in SCG_EXCLUSIONS:
        if rule.stage != "P2" or lang not in rule.langs:
            continue
        if rule.u1_gated and not U1_KEEP_C1_SIMILARITY_EXCLUSIONS:
            continue
        if rule.rule_id == "A3_LENGTH_NG" and not ctx.length_ok:
            return rule.rule_id
        if rule.rule_id == "A4_C2_HOMOGRAPH" and sig.get("c2_homophone_candidate"):
            return rule.rule_id
        if rule.rule_id == "A5_SIMILARITY_LT_0_4":
            sim = sig.get("similarity")
            if sim is not None and sim < SCG_MIN_SIMILARITY:
                return rule.rule_id
        if rule.rule_id == "A6_C1_PROPER_NOUN_DIFF" and sig.get("c1_proper_noun_diff"):
            return rule.rule_id
        if rule.rule_id == "A7_READING_DICT_MISMATCH" and sig.get("reading_dictionary_mismatch"):
            return rule.rule_id
    return None


# ============================================================
# 入出力
# ============================================================
@dataclass
class RunState:
    """run単位の状態(circuit breaker・技術STOP記録・Secondary呼出集計)。Lock状態(HR)は持たない。"""
    circuit_breaker_threshold: int = CIRCUIT_BREAKER_THRESHOLD
    secondary_consecutive_failures: int = 0
    secondary_failures_total: int = 0
    secondary_calls: int = 0
    circuit_open: bool = False
    technical_stop_events: list = field(default_factory=list)
    est_jpy_total: float = 0.0


@dataclass
class PrimaryResult:
    passed: bool
    text: str | None
    label: str = ""                       # 既存P-chainの分類ラベル
    equivalence_basis: str | None = None  # 承認済みequivalenceでPASSした根拠(最終ANDゲートが再否定しない)
    warning_labels: tuple = ()            # Primary側のwarning(CONNECTED_SPEECH/CS_EQUIVALENCE/M1_MULTI_CANDIDATE/SECONDARY_CORROBORATED等)
    signals: dict = field(default_factory=dict)  # c2_homophone_candidate / c1_proper_noun_diff / similarity など(除外表用)
    # 委任_06c(OF-AUW-C-01): Primary層の救済(非ラテンKP層のAzure転写採用等)で**採用根拠が別転写**のとき、その転写。
    # Primary PASSの最終ANDゲート(値ガード・否定)はこの転写(無ければtext)に対して行う(Primary非ラテン転写に英語否定語・数値を
    # 照合しない。JA J11 `_j11_adopted_judgement`と同じ考え方)。textは監査・Primary取得失敗判定に引き続き使う。
    adopted_text: str | None = None


@dataclass
class SecondaryOutcome:
    text: str | None
    accepted: bool | None = None   # 注入側の許容集合判定(None=未判定。secondary_accept_fnまたはEXACT一致で決める)
    label: str = ""
    error: str | None = None

    @property
    def ok(self) -> bool:
        return bool(self.text and str(self.text).strip()) and not self.error


@dataclass
class SecondaryCache:
    """key=(sha256(wav), engine, lang, phrase_hash)。**成功結果のみ**キャッシュ(失敗は非キャッシュ)。"""
    _store: dict = field(default_factory=dict)
    calls: int = 0
    hits: int = 0

    def get_or_call(self, key: tuple, fn):
        if key in self._store:
            self.hits += 1
            return self._store[key], True
        self.calls += 1
        out = _normalize_outcome(fn())
        if out.ok:
            self._store[key] = out
        return out, False


@dataclass
class AttemptCtx:
    canonical_text: str
    wav_path: str | None = None
    wav_sha256: str | None = None
    audio_seconds: float | None = None
    segment_key: str = ""
    script_version: str = "v0"
    slot: int = 1
    is_last_slot: bool = False
    length_ok: bool = True
    force_secondary: bool = False
    engine: str = "azure"
    phrase_list_hash: str = ""
    cache: SecondaryCache | None = None
    run_state: RunState | None = None

    def sha(self) -> str:
        if self.wav_sha256:
            return self.wav_sha256
        if self.wav_path:
            h = hashlib.sha256()
            with open(self.wav_path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest()
        return f"nosha:{self.segment_key}:{self.slot}"


@dataclass
class JudgeResult:
    state: str
    warning_labels: list
    audit_record: dict
    reason_code: str = ""
    secondary_unavailable: bool = False

    @property
    def verified(self) -> bool:
        return self.state in PASSING_STATES


def _normalize_outcome(raw) -> SecondaryOutcome:
    if isinstance(raw, SecondaryOutcome):
        return raw
    if raw is None:
        return SecondaryOutcome(None, error="secondary_returned_none")
    if isinstance(raw, str):
        return SecondaryOutcome(raw)
    if isinstance(raw, dict):
        return SecondaryOutcome(raw.get("text"), raw.get("accepted"), raw.get("label", ""), raw.get("error"))
    return SecondaryOutcome(None, error=f"unsupported_secondary_result:{type(raw).__name__}")


# ============================================================
# 否定ガード(既存の否定語集合を再利用。再実装しない)
# ============================================================
def negation_diff(canonical: str, text: str, lang: str) -> bool:
    """EN: er006 _NEGATION_WORDS の出現数が異なる / JA: er003 safety._has_negation_ja の有無が異なる。"""
    if lang == "ja":
        return bool(_safety._has_negation_ja(canonical or "")) != bool(_safety._has_negation_ja(text or ""))

    def neg_count(t: str) -> Counter:
        # 委任_03(統合で判明した偽否定の是正): 承認済みの標準contraction展開(TRANSCRIPT_STYLE_NORMALIZED_MATCH: do not/don't,
        # will not/won't, is not/isn't, cannot/can't)と「can not」=cannotを、否定語の数える前に正規化する。展開しないと
        # 『否定語の語形が違う』だけで承認済み等価(否定保持)をNG_PROTECTEDにしてしまう。否定の有無が反転する差
        # (can/can't, is/isn't)は展開後も差として残る(安全側は不変)。
        t = _val.expand_standard_contractions(t or "")
        t = re.sub(r"\bcan\s+not\b", "cannot", unicodedata.normalize("NFKC", t).lower().replace("’", "'"))
        toks = [w.replace("'", "") for w in re.findall(r"[a-z']+", t)]
        return Counter(w for w in toks if w in _val._NEGATION_WORDS)

    return neg_count(canonical) != neg_count(text)


def _surface_key(t: str) -> str:
    t = unicodedata.normalize("NFKC", t or "").casefold()
    return re.sub(r"[\s\W_]+", "", t)


def same_surface(a: str, b: str) -> bool:
    """句読点・空白・大小文字・全半角のみ違う同一表層(ASR転写が原稿と同一表層か)。"""
    return _surface_key(a) == _surface_key(b)


# ============================================================
# 判定本体
# ============================================================
def _protected(canonical: str, text: str, lang: str):
    """(value_guard結果, 否定差bool)。"""
    return vg.value_guard(canonical, text, lang), negation_diff(canonical, text, lang)


def _mk_primary(p) -> PrimaryResult:
    if isinstance(p, PrimaryResult):
        return p
    if isinstance(p, dict):
        return PrimaryResult(bool(p.get("passed")), p.get("text"), p.get("label", ""), p.get("equivalence_basis"),
                             tuple(p.get("warning_labels", ())), dict(p.get("signals", {})), p.get("adopted_text"))
    return PrimaryResult(bool(getattr(p, "passed")), getattr(p, "text", None), getattr(p, "label", ""),
                         getattr(p, "equivalence_basis", None), tuple(getattr(p, "warning_labels", ())),
                         dict(getattr(p, "signals", {}) or {}), getattr(p, "adopted_text", None))


def unified_judge(ctx: AttemptCtx, primary_result, secondary_fn, *, lang: str, role: str | None,
                  final_and_gate: bool = True, secondary_accept_fn=None) -> JudgeResult:
    """1音声=1 attemptの統一判定。純粋: API呼出は`secondary_fn`(注入)経由のみ。

    secondary_fn(ctx) -> str | None | SecondaryOutcome | dict   (例外は障害として扱う)
    secondary_accept_fn(canonical, secondary_text) -> bool | (bool, label)  言語別許容集合(既存分類器)の注入点
    """
    t0 = time.time()
    if lang not in ("en", "ja"):
        raise ValueError(f"unsupported lang: {lang!r}")
    pr = _mk_primary(primary_result)
    canon = ctx.canonical_text
    rs = ctx.run_state
    cache = ctx.cache if ctx.cache is not None else SecondaryCache()
    audit = {
        "state": None, "reason_code": "", "slot": ctx.slot, "script_version": ctx.script_version, "role": role, "lang": lang,
        "segment_key": ctx.segment_key, "audio_sha256": None,
        "primary": {"text": pr.text, "passed": pr.passed, "label": pr.label, "equivalence_basis": pr.equivalence_basis,
                    "warning_labels": list(pr.warning_labels)},
        "secondary": {"called": False, "cached": False, "engine": ctx.engine, "text": None, "label": "", "accepted": None,
                      "error": None, "unavailable": False},
        "value_guard": {}, "negation_guard": {}, "final_gate": {"applied": False},
        "warnings": [], "exclusion_rule": None,
        "cost": {"azure_calls": 0, "azure_seconds": None, "est_jpy": 0.0},
        "timing": {"total_ms": 0, "secondary_ms": 0},
        "technical_stop": None,
    }
    if ctx.wav_sha256:
        audit["audio_sha256"] = ctx.wav_sha256  # 委任_03: Primary PASS(Secondary不呼出)でも採用音声のsha256を記録(registryが突合に使う)

    def done(state, reason, warnings=(), unavailable=False) -> JudgeResult:
        audit["state"], audit["reason_code"] = state, reason
        wl = list(dict.fromkeys(warnings))
        if state in PASSING_STATES and ctx.script_version == "v1":
            wl.append(W_LR_REWRITTEN)
            wl = list(dict.fromkeys(wl))
        if state == PASS and wl:
            state = PASS_WITH_WARNING
            audit["state"] = state
        audit["warnings"] = wl
        audit["secondary"]["unavailable"] = unavailable
        audit["timing"]["total_ms"] = int((time.time() - t0) * 1000)
        return JudgeResult(state, wl, audit, reason, unavailable)

    # ---- Primary ASR取得失敗 ----
    if pr.text is None:
        return done(NG_PRIMARY_ASR_FAILURE, "primary_asr_failure")

    # 委任_06c(OF-AUW-C-01): Primary PASSの根拠が別転写(adopted_text)ならその転写で最終ANDゲートを行う。
    gate_text = pr.adopted_text if (pr.passed and pr.adopted_text is not None) else pr.text
    pvg, pneg = _protected(canon, gate_text, lang)
    audit["value_guard"] = {"primary": pvg.to_dict()}
    audit["negation_guard"] = {"primary": pneg}
    if gate_text is not pr.text:
        audit["primary"]["adopted_text"] = gate_text
        audit["value_guard"]["gate_target"] = "adopted_text"
    warnings = list(pr.warning_labels) + list(pvg.warnings)
    primary_ng_reason = None

    # ---- Primary PASS -> 最終ANDゲート ----
    if pr.passed:
        approved = pr.equivalence_basis in APPROVED_EQUIVALENCE_BASES
        if not final_and_gate:
            audit["final_gate"] = {"applied": False, "skipped": "final_and_gate=False"}
        elif approved:
            audit["final_gate"] = {"applied": False, "skipped": f"approved_equivalence:{pr.equivalence_basis}"}
        else:
            audit["final_gate"] = {"applied": True, "value_guard": pvg.kind, "negation_diff": pneg}
            if pvg.kind == vg.DIFF or pneg:
                return done(NG_PROTECTED, "final_gate_value_diff" if pvg.kind == vg.DIFF else "final_gate_negation_diff")
            if pvg.kind == vg.AMBIGUOUS:
                # 根拠のない曖昧表層(10分/十分)はPrimary転写のままPASSさせない -> P3(Secondary)へ降格
                primary_ng_reason = "primary_pass_demoted_ambiguous_value"
        if primary_ng_reason is None and not ctx.force_secondary:
            return done(PASS, "primary_pass" if not approved else f"primary_pass_approved_equivalence:{pr.equivalence_basis}", warnings)
        if primary_ng_reason is None:
            primary_ng_reason = "force_secondary"
    else:
        # ---- Primary NG: P1 / P2 ----
        if pvg.kind == vg.DIFF:
            return done(NG_PROTECTED, "p1_value_diff")
        if pneg:
            return done(NG_PROTECTED, "p1_negation_diff")
        # 委任_04(JA): 既存の保護差(JA SCGが従来から除外していた per-span 数字不一致[値ガードがUNKNOWN/NO_VALUESのとき]・
        # per-span 否定不一致・fugashi否定マーカー差)を、呼出側(adapter)が signals["protected_diff"]=<理由> で渡す。
        # DESIGN_01 §4-3 P1「JA否定マーカー差」/DESIGN_02_ADDENDUM_01 §1-5。値ガードDIFF/否定差と同じくSecondary不呼出。
        _pd = (pr.signals or {}).get("protected_diff")
        if _pd:
            return done(NG_PROTECTED, f"p1_protected_diff:{_pd}")
        hit = _exclusion_hit(ctx, pr, lang)
        if hit:
            audit["exclusion_rule"] = hit
            return done(NG_EXCLUDED, f"p2_exclusion:{hit}")
        primary_ng_reason = "p3_primary_ng"
    audit["p3_entry"] = primary_ng_reason

    # ---- P3: Secondary 1回 ----
    key = (ctx.sha(), ctx.engine, lang, ctx.phrase_list_hash)
    audit["audio_sha256"] = key[0]
    if rs is not None and rs.circuit_open:
        err = "circuit_breaker_open"
        audit["secondary"].update(error=err)
        audit["technical_stop"] = {"type": "SECONDARY_CIRCUIT_OPEN", "restartable": True, "approval_required": False}
        return done(NG_SECONDARY_UNAVAILABLE, "secondary_circuit_open", warnings, unavailable=True)

    ts = time.time()
    outcome = None
    exc = None
    was_cached = False
    try:
        outcome, was_cached = cache.get_or_call(key, lambda: secondary_fn(ctx))
    except Exception as e:  # 障害は例外でも必ずNG_SECONDARY_UNAVAILABLEへ(PASS不可)
        if is_config_stop_error(e):
            raise  # 委任_06c(OF-AUW-C-02): 設定不備(init_logger未呼出/[STOP]単価未登録)は握りつぶさず再送出
        exc = f"{type(e).__name__}: {e}"
    audit["timing"]["secondary_ms"] = int((time.time() - ts) * 1000)
    audit["secondary"]["called"] = not was_cached
    audit["secondary"]["cached"] = was_cached
    if not was_cached:
        jpy = est_jpy_for_seconds(ctx.audio_seconds)
        audit["cost"] = {"azure_calls": 1, "azure_seconds": ctx.audio_seconds, "est_jpy": jpy if jpy is not None else 0.0,
                         "est_jpy_known": jpy is not None}
        if rs is not None and jpy:
            rs.est_jpy_total += jpy

    if exc is not None or outcome is None or not outcome.ok:
        err = exc or (outcome.error if outcome is not None else None) or "secondary_empty"
        audit["secondary"]["error"] = err
        if rs is not None:
            rs.secondary_calls += 1
            rs.secondary_consecutive_failures += 1
            rs.secondary_failures_total += 1
            ev = {"type": "SECONDARY_UNAVAILABLE", "segment_key": ctx.segment_key, "slot": ctx.slot, "error": err,
                  "restartable": True, "approval_required": False}
            rs.technical_stop_events.append(ev)
            audit["technical_stop"] = ev
            if rs.secondary_consecutive_failures >= rs.circuit_breaker_threshold and not rs.circuit_open:
                rs.circuit_open = True
                rs.technical_stop_events.append({"type": "SECONDARY_CIRCUIT_OPEN", "after_failures": rs.secondary_consecutive_failures,
                                                 "restartable": True, "approval_required": False})
        else:
            audit["technical_stop"] = {"type": "SECONDARY_UNAVAILABLE", "error": err, "restartable": True, "approval_required": False}
        return done(NG_SECONDARY_UNAVAILABLE, "secondary_unavailable", warnings, unavailable=True)

    # 取得成功
    if rs is not None and not was_cached:
        rs.secondary_calls += 1
        rs.secondary_consecutive_failures = 0
    stext = outcome.text
    audit["secondary"].update(text=stext, label=outcome.label)
    svg, sneg = _protected(canon, stext, lang)
    audit["value_guard"]["secondary"] = svg.to_dict()
    audit["negation_guard"]["secondary"] = sneg
    if svg.kind == vg.DIFF or sneg:
        return done(NG_BOTH, "secondary_value_diff" if svg.kind == vg.DIFF else "secondary_negation_diff", warnings)

    # 許容集合判定(注入)
    accepted, label = outcome.accepted, outcome.label
    if accepted is None and secondary_accept_fn is not None:
        r = secondary_accept_fn(canon, stext)
        accepted, label = (r if isinstance(r, tuple) else (bool(r), ""))
    if accepted is None:
        accepted = same_surface(canon, stext)  # 注入が無い場合はEXACT(同一表層)のみ
        label = label or "EXACT_SURFACE"
    audit["secondary"].update(accepted=bool(accepted), label=label)

    ambiguous_primary = pvg.kind == vg.AMBIGUOUS
    if svg.kind == vg.AMBIGUOUS and not same_surface(canon, stext):
        return done(NG_BOTH, "secondary_ambiguous_value_not_same_surface", warnings)
    if ambiguous_primary:
        if same_surface(canon, stext):
            return done(PASS_WITH_WARNING, "secondary_exact_resolves_ambiguous", warnings + [W_NUMERIC_AMBIGUOUS_SURFACE])
        return done(NG_BOTH, "ambiguous_value_secondary_not_same_surface", warnings)
    if not accepted:
        return done(NG_BOTH, "secondary_not_accepted", warnings)
    if final_and_gate:
        audit["final_gate"] = {"applied": True, "target": "secondary", "value_guard": svg.kind, "negation_diff": sneg}
    if primary_ng_reason == "force_secondary":
        # 委任_03: Primary PASS + force_secondary(minimal fallback/LR後v1)でSecondaryも許容集合PASS = 両エンジン合意。
        # 従来(er006 force_secondary)もPASS扱い(警告なし)だったため、SECONDARY_CONFIRMED警告は付けない(LR後v1はdone()がLR_REWRITTENを付与)。
        return done(PASS, "force_secondary_agreed", warnings + list(svg.warnings))
    return done(PASS_WITH_WARNING, "secondary_confirmed", warnings + [W_SECONDARY_CONFIRMED] + list(svg.warnings))
