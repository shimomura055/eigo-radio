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
# 委任_13(A3是正): ctx.max_len指定時のみ、Primary NG+length NGもP3へ回し、Primary PASS+length NGはP3へ降格する。Secondary受理時は採用転写(Secondary)の
#   長さで再評価(超過=NG_BOTH `secondary_length_ng`)。呼出元の最終ANDは `final_length_ok`(fail-closed)。ロールバック=module定数 A3_SECONDARY_LENGTH_REEVAL。
# KP3V(2026-10-22、ユーザー承認APPROVED_FOR_PRODUCTION): KP英語phrase専用の`vote_required`モード = OpenAI(Primary)・Azure(Secondary)・Whisper(local)の
#   3-ASR多数決(2/3 PASS)。P/Sが割れたときだけWhisperを呼ぶ。集計は純関数`er104_kp_three_asr_vote_01.tally()`(done()出口が1回呼ぶ)。
#   旧`dual_required`(両方PASS必須)と`NG_DUAL_PRIMARY_NOT_PASS`は撤去。既定False=現行コードパスを1行も変えない。
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
# KP3V(2026-10-22): `vote_required`モード(KP英語phrase)でのみ発生。Whisper(local)の例外/import失敗/timeout/circuit open = 技術STOP(PASS不可・HRに入れない)。
# 空転写はNG票(通常の再生成)でありこの状態にはならない。
NG_WHISPER_UNAVAILABLE = "NG_WHISPER_UNAVAILABLE"
STATES = (PASS, PASS_WITH_WARNING, NG_PROTECTED, NG_EXCLUDED, NG_BOTH, NG_SECONDARY_UNAVAILABLE, NG_PRIMARY_ASR_FAILURE,
          NG_WHISPER_UNAVAILABLE)
PASSING_STATES = (PASS, PASS_WITH_WARNING)
TECHNICAL_STOP_STATES = (NG_SECONDARY_UNAVAILABLE, NG_WHISPER_UNAVAILABLE)   # HR Lock/queueへ投入せず再実行で再開する状態

# ---- warningラベル ----
W_SECONDARY_CONFIRMED = "SECONDARY_CONFIRMED"
W_NUMERIC_AMBIGUOUS_SURFACE = "NUMERIC_AMBIGUOUS_SURFACE"
W_LR_REWRITTEN = "LR_REWRITTEN"
W_PRIMARY_LENGTH_EXCESS = "PRIMARY_LENGTH_EXCESS"  # 委任_13(A3R-07): Primary転写がmax_lenを超えたがSecondary転写(採用転写)で長さOKだった=事後試聴対象(受理条件は不変)
W_JA_NUMERIC_IRREGULAR_READING = vg.WARN_IRREGULAR_READING

# ---- 最終ANDゲートが再否定しない承認済みequivalence根拠(ctx/primary_resultの`equivalence_basis`で受け取る) ----
# 2026-10-25 JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A(OPEN-517 F1、承認済み安全条件の不具合是正): `READING_MATCH`(er007 読み一致[JA]。PHONETIC_MATCH/READING_RESOLVED_MATCH由来)を
#   この集合から**除外**した。旧実装(OF-AUW-01、追補§1-3「読み一致を再否定しない」)は承認済み仕様 CURRENT_SPEC.md:2855・ユーザー原文L97
#   (『承認済み根拠にも値・否定の最終ANDゲートを適用』)と矛盾し、数値を含む文の読み一致が値ガードを受けず誤PASSしていた(8,900↔89,000・しわ↔すわ等)。
#   READING_MATCHのPrimary PASSは最終ANDゲートを受ける(値DIFF/否定差=NG_PROTECTED、AMBIGUOUS=P3降格)。正しいかな書き数詞は F2(`kana_unify`)で値同一として維持する。
#   rollback = 下の `READING_MATCH_FINAL_GATE = False`(1行。READING_MATCHを再び承認基底へ戻し、F2も無効=旧挙動を完全復元)。
APPROVED_EQUIVALENCE_BASES = frozenset({
    "HOMOPHONE_MATCH_NUMBER_EXCEPTION",   # er006_preprod_hardening_01_validation.py:905/1066
    "TIER1_DIFF_ANCHORED",                # er021 Tier1(strict版、2026-09-28承認)
    "TIER1_NUMERIC_EQUIVALENCE",
})
READING_MATCH_BASIS = "READING_MATCH"
# OPEN-517 F1+F2のrollback用module定数(env/flag/起動scriptでは変更不可。承認済み不具合是正のためflag化しない)。True=READING_MATCH PASSにも最終ANDゲート+F2。False=旧挙動。
READING_MATCH_FINAL_GATE = True

# ---- U1(委任_10、2026-10-16ユーザー指示A-2/A-3「承認済み仕様への実装修正」。解放実装・Regression済み。既定は条件付きSTOP s1により暫定True) ----
# 既定の経緯: live負例対照でPrimary PASS 3件(Secondary不呼出=U1と無関係)が出たためs1に従いTrueのままcommit。Fableが採否判断し1行でFalse化する。
# False=JAの類似度<0.4(A5)・C1固有名詞差(A6: entity_like・辞書未登録Latin語)のP2事前除外を撤廃し、Primary NGなら原則Secondaryへ回す。
# True=旧挙動(A5/A6をP2除外のまま。ロールバック用。unit testでmonkeypatchして固定)。
# 例外として残す除外: A1/A2(P1 数値DIFF・否定差)、A3(length NG。委任_13で是正済み: max_len指定の呼出元はP2除外から外れSecondary転写で再評価。max_len未指定=旧挙動のP2除外)、
#   A4(C2同形異音候補、2026-10-11ユーザー逐語採用)、A7(登録読み辞書不一致=登録読み保護。Secondaryの表層一致は読みの正しさを
#   証明しないため、2026-10-11安全条件[読みでの受理禁止]に従い事前除外のまま。U1フラグの対象外)。
# U2(force_secondary)の死定数U2_FORCE_SECONDARY_SCOPEは委任_10で撤去(どこからも参照されていなかった。実体は呼出側の
#   er003_v1_crosslevel_audio_02_common.py `_run_a2_minimal_fallback_attempt` の force_secondary=True 1箇所のみ。静的testで固定)。
U1_KEEP_C1_SIMILARITY_EXCLUSIONS = False  # 委任_11(2026-10-16): Fable判断でs1非該当→発効。True=旧挙動ロールバック用。A7(登録読み保護)・A1/A2/A3/A4は対象外で維持

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

# ---- A3是正(委任_13、2026-10-16、ユーザー指示A-2「Primaryの差が大きいという理由だけでSecondaryを省略したり、Secondaryの正当なPASSを拒否したりしない」の実装修正) ----
# True : 呼出元がattempt_ctxで`max_len`を渡したとき(ctx.max_len is not None)に限り、length判定をPrimary転写由来のP2事前除外(A3)から外し、
#        (1) Primary NGでもSecondaryへ回す (2) Primary PASSでもPrimary転写がmax_lenを超えていればP3へ降格しSecondaryへ回す
#        (3) Secondary受理時は採用転写(Secondary)の長さで再評価(超過ならNG_BOTH `secondary_length_ng`) (4) 最終ANDは呼出元が`final_length_ok`で行う。
#        max_len未指定の呼出元(安全ラッチ)は従来挙動(JA=A3事前除外/EN=従来)。
# False: ロールバック用(module定数。env/flagではない)。A3を従来どおり表に残し、max_lenがあっても旧挙動に戻す。
A3_SECONDARY_LENGTH_REEVAL = True

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
    ExclusionRule("A3_LENGTH_NG", "length NG(Secondaryで救えてもlength ANDで不合格)。委任_13: ctx.max_len指定時(かつA3_SECONDARY_LENGTH_REEVAL=True)は無効化し、Secondary転写で再評価", "P2", ("en", "ja"), "length_ok=False"),
    ExclusionRule("A4_C2_HOMOGRAPH", "C2同形異音候補(Azureが原稿の漢字表記と一致しても読み違いを区別できない)", "P2", ("ja",), "c2_homophone_candidate"),
    ExclusionRule("A5_SIMILARITY_LT_0_4", "類似度<0.4(U1フラグがTrueの間のみ有効)", "P2", ("ja",), "similarity<0.4", u1_gated=True),
    ExclusionRule("A6_C1_PROPER_NOUN_DIFF", "C1固有名詞差(U1フラグがTrueの間のみ有効)", "P2", ("ja",), "c1_proper_noun_diff", u1_gated=True),
    ExclusionRule("A7_READING_DICT_MISMATCH", "登録読み保護: Primaryが登録読み辞書expected_readingsとの不一致を具体的に示した(Secondaryの表層一致は読みの正しさを証明しない。2026-10-11安全条件)", "P2", ("ja",), "reading_dictionary_mismatch"),
)
SCG_MIN_SIMILARITY = 0.4  # er007_ja_secondary_asr_01.SCG_MIN_SIMILARITY と同値(parity testで突合)


def _a3_reeval_active(ctx: "AttemptCtx") -> bool:
    """委任_13(A3R-03 安全ラッチ): max_lenを渡した呼出元だけがA3是正の対象。max_len未指定は従来挙動。"""
    return bool(A3_SECONDARY_LENGTH_REEVAL) and getattr(ctx, "max_len", None) is not None


def final_length_ok(length_ok_primary, detail) -> bool:
    """委任_13(A3R-03): 呼出元の最終AND用helper(fail-closed)。`detail`はcascade/adapterのdetail dict(`asr_judgement`キー)または
    asr_judgement自体。Primaryのlength_okを置換するのは次の全条件を満たすときだけ:
      asr_judgementが存在 ∧ state∈PASSING ∧ audit["length"]["adopted_from"]=="secondary" ∧ audit["length"]["adopted_ok"] is True。
    それ以外(キー欠落・型不正・NG・Primary採用・例外)は常にPrimary由来のlength_okを返す(=従来と同じ)。"""
    primary = bool(length_ok_primary)
    try:
        aj = detail.get("asr_judgement", detail) if isinstance(detail, dict) else None
        if not isinstance(aj, dict) or aj.get("state") not in PASSING_STATES:
            return primary
        ln = aj.get("length")
        if isinstance(ln, dict) and ln.get("adopted_from") == "secondary" and ln.get("adopted_ok") is True:
            return True
    except Exception:
        return primary
    return primary


def _exclusion_hit(ctx: "AttemptCtx", primary: "PrimaryResult", lang: str):
    """P2除外表の該当ルールidを返す(なければNone)。P1相当(A1/A2)は別途判定。"""
    sig = primary.signals or {}
    for rule in SCG_EXCLUSIONS:
        if rule.stage != "P2" or lang not in rule.langs:
            continue
        if rule.u1_gated and not U1_KEEP_C1_SIMILARITY_EXCLUSIONS:
            continue
        if rule.rule_id == "A3_LENGTH_NG" and not ctx.length_ok and not _a3_reeval_active(ctx):
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
    # 委任_13(A3R-01/03): 呼出元のmax_len(余裕文字数は呼出元ごとに異なる。judge内で固定再計算しない)。None=従来挙動(安全ラッチ)。
    max_len: int | None = None
    force_secondary: bool = False
    # KP3V: True=KP英語phrase専用の「3-ASR多数決(2/3 PASS)」判定。既定False=現行コードパスを1行も変えない。
    # Trueを渡す呼出元は`generate_narration_snippet_verified_strict(vote_pass_required=True)`経由のKP英語phrase 6箇所のみ(静的testで固定)。
    vote_required: bool = False
    whisper_fn: object = None   # vote_required時のみ: callable() -> er104.Voter(Whisper票)。None=Whisper未設定(割れたら技術STOP)
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
    return _neg_count_impl(canonical) != _neg_count_impl(text)


def _neg_count_impl(t: str) -> Counter:
    # 委任_03(統合で判明した偽否定の是正): 承認済みの標準contraction展開(TRANSCRIPT_STYLE_NORMALIZED_MATCH: do not/don't,
    # will not/won't, is not/isn't, cannot/can't)と「can not」=cannotを、否定語の数える前に正規化する。展開しないと
    # 『否定語の語形が違う』だけで承認済み等価(否定保持)をNG_PROTECTEDにしてしまう。否定の有無が反転する差
    # (can/can't, is/isn't)は展開後も差として残る(安全側は不変)。
    # ASR-HOMOPHONE 委任_04: negation_diffの内部関数を module-level へ移しただけ(本体は1文字も変えない。negation_counterが公開入口)。
    t = _val.expand_standard_contractions(t or "")
    t = re.sub(r"\bcan\s+not\b", "cannot", unicodedata.normalize("NFKC", t).lower().replace("’", "'"))
    toks = [w.replace("'", "") for w in re.findall(r"[a-z']+", t)]
    return Counter(w for w in toks if w in _val._NEGATION_WORDS)


def negation_counter(t: str) -> Counter:
    """EN: 否定語の出現数(Counter)。`negation_diff`と同じ数え方の公開入口(ASR-HOMOPHONE 委任_04: er109のspan解除が『judgeと同じneg_count』を
    使うため。実装は`negation_diff`の`neg_count`を呼ぶだけ=数え方は二重化しない)。"""
    return _neg_count_impl(t)


def _surface_key(t: str) -> str:
    t = unicodedata.normalize("NFKC", t or "").casefold()
    return re.sub(r"[\s\W_]+", "", t)


def same_surface(a: str, b: str) -> bool:
    """句読点・空白・大小文字・全半角のみ違う同一表層(ASR転写が原稿と同一表層か)。"""
    return _surface_key(a) == _surface_key(b)


# ============================================================
# 判定本体
# ============================================================
def _protected(canonical: str, text: str, lang: str, *, kana_unify: bool = False, info_out: dict | None = None):
    """(value_guard結果, 否定差bool)。

    kana_unify(OPEN-517 F2): 明示引数。Trueのときだけ値ガードの前に『かな書き数詞の表記統一』を行う(呼出回数や副作用では決めない)。
      Trueにしてよいのは READING_MATCH PASS の Primary 最終ゲートだけ(呼出元で限定)。Primary NG・Secondary・KP等は既定False。
      否定差は**常に置換前の元テキスト**で判定する(F2の置換後テキストでは判定しない)。info_out(dict)を渡すとF2の発動情報を書き込む。"""
    if kana_unify and lang == "ja":
        g, info = vg.value_guard_kana_unified_detail(canonical, text, lang)
        if info_out is not None:
            info_out.update(info.to_dict())
        return g, negation_diff(canonical, text, lang)
    return vg.value_guard(canonical, text, lang), negation_diff(canonical, text, lang)


# ---- ASR-HOMOPHONE 委任_04: er109(表記違い同音)のX/Z限定配線。scope外・ortho根拠でない呼出では下の関数群は何もしない(従来コードパスのまま) ----
def _ortho_record_primary(pr, lang: str, audit: dict) -> None:
    """adapterがer109でPrimaryをPASSさせたとき(signals['er109_decision']あり)だけ、asr_judgementへ`orthographic_equivalence`を加算記録する。"""
    dec = (pr.signals or {}).get("er109_decision") if lang == "en" else None
    if dec is None:
        return
    import er109_xz_scope_01 as xz
    xz.record_site(audit, "primary", dec)


def _ortho_unlock_primary(pr, canon: str, gate_text: str, pvg, pneg: bool, lang: str, audit: dict):
    """Primary PASS最終ゲート(非KP)のspan単位解除(P-06)。解除対象は『ortho根拠のPrimary』かつ『gate_text==er109判定対象』のときだけ(M9)。
    戻り値: ProtectedExplanation(解除可否) / None(対象外=従来どおり)。"""
    if lang != "en" or (pr.signals or {}).get("er109_decision") is None:
        return None
    import er109_xz_scope_01 as xz
    if (not xz.is_active_for_run()) or pr.equivalence_basis != xz.ORTHO_BASIS:
        return None
    try:
        ex = xz.explain_protected(pr.signals["er109_decision"], pvg, pneg, canon, gate_text)
    except Exception as exc:  # noqa: BLE001  fail-closed: 説明不能=解除しない(従来のNG_PROTECTED)
        audit.setdefault("orthographic_equivalence_errors", []).append(f"{type(exc).__name__}: {exc}")
        return None
    xz.record_site(audit, "primary", pr.signals["er109_decision"],
                   span_unlock={"explained": ex.explained, "reason": ex.reason, "detail": ex.detail, "negation_unlocked": ex.negation_unlocked,
                                "value_unlocked": ex.value_unlocked})
    return ex


def _ortho_secondary_precheck(outcome, canon: str, stext: str, svg, sneg: bool, lang: str, audit: dict, has_accept_fn: bool):
    """Secondary転写に値DIFF/否定差があるとき(非KP)、er109の同値spanで説明できるなら『判定を許容集合判定まで保留』する(M10)。
    条件: lang=en ∧ scope内 ∧ `outcome.accepted is None`(providerが事前に受理を決めていない) ∧ accept関数が注入されている ∧ Secondary転写のspan説明が成立。
    保留した場合は呼出元が、許容集合判定が`ORTHO_LABEL`受理でなければ従来どおり`NG_BOTH(secondary_value_diff/negation_diff)`へ戻す。
    判定対象は必ずSecondary転写(stext)=Primaryのガード結果・decisionを流用しない(M9)。"""
    if lang != "en" or outcome.accepted is not None or not has_accept_fn:
        return None
    import er109_xz_scope_01 as xz
    if not xz.is_active_for_run():
        return None
    dec = xz.decision(canon, stext, sink=audit)
    if dec is None:
        return None
    try:
        ex = xz.explain_protected(dec, svg, sneg, canon, stext)
    except Exception as exc:  # noqa: BLE001
        audit.setdefault("orthographic_equivalence_errors", []).append(f"{type(exc).__name__}: {exc}")
        return None
    if not ex.explained:
        return None
    return dec, ex


def _ortho_mark_votes(canon: str, lang: str, audit: dict, voters) -> list:
    """KP3V票(P/S/W)のうち、er109(ORTHO_LABEL)でPASSした票に`ortho_applied`/`ortho_warnings`を付け、PASS票由来のORTHO警告を返す(M11)。
    S/W票の警告は『その票の転写文字列』で再計算(P票と同じ判定入力。tallyの勝ち組はPASS票なのでPASS票から合成)。scope外は何もしない=空リスト。"""
    if lang != "en":
        return []
    import er109_xz_scope_01 as xz
    if not xz.is_active_for_run():
        return []
    out: list = []
    for site, v in voters:
        if v is None or not v.passed or v.label != xz.ORTHO_LABEL:
            continue
        d = xz.decision(canon, v.text, sink=audit)
        v.ortho_applied = True
        if d is not None:
            v.ortho_warnings = tuple(d.warning_labels)
            xz.record_site(audit, site, d)
            out += list(d.warning_labels)
    return list(dict.fromkeys(out))


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
        # 委任_13(A3R-06): length監査。applied=A3是正が有効(max_len指定∧定数True)か。
        "length": {"applied": _a3_reeval_active(ctx), "primary_len": None, "secondary_len": None, "max_len": ctx.max_len,
                   "adopted_from": "primary", "adopted_ok": None, "surface_len": None, "primary_ok": None},
    }
    a3 = _a3_reeval_active(ctx)
    vote = None
    if ctx.vote_required:
        # KP3V: 3 Providerの票を並べて残すための監査キー(additive、vote_required時のみ存在)。確定時に`build_vote_audit`の完全形で置換する。
        vote = {"required": True, "version": "kp_vote_check_v1", "primary_pass": False, "primary_text": pr.text,
                "primary_rescued_by_secondary": False, "primary_rescue_layers": [], "primary_not_pass_reason": None,
                "state": None, "row": None}
        audit["vote"] = vote
    if ctx.wav_sha256:
        audit["audio_sha256"] = ctx.wav_sha256  # 委任_03: Primary PASS(Secondary不呼出)でも採用音声のsha256を記録(registryが突合に使う)
    _ortho_record_primary(pr, lang, audit)   # ASR-HOMOPHONE 委任_04: ortho根拠のPrimaryのみ加算記録(それ以外は何もしない)

    def done(state, reason, warnings=(), unavailable=False) -> JudgeResult:
        if vote is not None and audit.get("vote") is vote:
            # 票の集計(finish_vote)を経由せずに確定した出口(Primary失敗/P1保護差/P2除外/Secondary障害): 状態だけ記録する。
            vote["state"] = state
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
    # OPEN-517(F1+F2): READING_MATCHのPrimary PASSは最終ANDゲートを受け、そのゲートの値ガードにだけF2(かな数詞の表記統一)を許す。Primary NG・Secondaryは対象外。
    kana_unify = bool(READING_MATCH_FINAL_GATE and pr.passed and pr.equivalence_basis == READING_MATCH_BASIS)
    f2_info: dict = {}
    pvg, pneg = _protected(canon, gate_text, lang, kana_unify=kana_unify, info_out=f2_info)
    audit["value_guard"] = {"primary": pvg.to_dict()}
    if kana_unify and f2_info.get("replaced"):
        audit["value_guard"]["kana_unify"] = f2_info   # 監査(R-3集計用): F2が置換を試みた(発動/単調性ガードで巻戻し)場合のみ
    audit["negation_guard"] = {"primary": pneg}
    if gate_text is not pr.text:
        audit["primary"]["adopted_text"] = gate_text
        audit["value_guard"]["gate_target"] = "adopted_text"
    warnings = list(pr.warning_labels) + list(pvg.warnings)
    primary_ng_reason = None
    # 委任_13(A3R-02): Primary length計測はgate_text(採用転写)基準。ctx.length_ok(呼出元がPrimary転写で計算)もANDし、fail-closedにする。
    plen_ok = True
    if a3:
        plen = len(gate_text)
        plen_ok = (plen <= int(ctx.max_len)) and bool(ctx.length_ok)
        audit["length"].update(primary_len=plen, primary_ok=plen_ok, adopted_ok=plen_ok)

    # ---- Primary PASS -> 最終ANDゲート ----
    if pr.passed:
        approved = (pr.equivalence_basis in APPROVED_EQUIVALENCE_BASES
                    or (not READING_MATCH_FINAL_GATE and pr.equivalence_basis == READING_MATCH_BASIS))   # False=旧挙動へのrollback
        if not final_and_gate:
            audit["final_gate"] = {"applied": False, "skipped": "final_and_gate=False"}
        elif approved:
            audit["final_gate"] = {"applied": False, "skipped": f"approved_equivalence:{pr.equivalence_basis}"}
        elif vote is not None:
            # 2026-10-22(KP-QUALITY-2ITEMS、ユーザー承認): KP英語(vote_required)は数値・否定の保護を解除。値DIFF/否定差は監査に記録するだけでNGにしない。
            # AMBIGUOUS(根拠のない曖昧表層)は票の分類として維持(P3へ降格)。
            audit["final_gate"] = {"applied": False, "skipped": "vote_guard_lifted",
                                   "observed": {"value_guard": pvg.kind, "negation_diff": pneg}}
            if pvg.kind == vg.AMBIGUOUS:
                primary_ng_reason = "primary_pass_demoted_ambiguous_value"
        else:
            audit["final_gate"] = {"applied": True, "value_guard": pvg.kind, "negation_diff": pneg}
            if pvg.kind == vg.DIFF or pneg:
                # ASR-HOMOPHONE 委任_04(P-06、M7/M9): er109(表記違い同音)でPASSしたPrimaryに限り、値DIFF/否定差を『er109の同値spanで説明できる場合のみ』解除する。
                # X/Z run scope外・ortho根拠でないPrimaryは_ortho_unlock_primaryがNoneを返す=従来どおりNG_PROTECTED。説明不能・AMBIGUOUSは解除しない。
                _ex = _ortho_unlock_primary(pr, canon, gate_text, pvg, pneg, lang, audit)
                if _ex is None or not _ex.explained:
                    return done(NG_PROTECTED, "final_gate_value_diff" if pvg.kind == vg.DIFF else "final_gate_negation_diff")
                audit["final_gate"]["span_unlock"] = {"explained": True, "reason": _ex.reason, "detail": _ex.detail}
                warnings = warnings + [w for w in _ex.warning_labels if w not in warnings]   # 否定差を解除した場合は必ず警告付き=PASS_WITH_WARNING(M7)
            if pvg.kind == vg.AMBIGUOUS:
                # 根拠のない曖昧表層(10分/十分)はPrimary転写のままPASSさせない -> P3(Secondary)へ降格
                primary_ng_reason = "primary_pass_demoted_ambiguous_value"
        if primary_ng_reason is None and not plen_ok:
            # 委任_13(A3R-02): Primary内容PASS+length NGはAMBIGUOUS降格と同形でP3(Secondary)へ降格する。
            primary_ng_reason = "primary_length_ng"
        if primary_ng_reason is None and vote is not None and (pr.signals or {}).get("primary_rescued_by_secondary"):
            # KP3V(OF-KPD-P-06踏襲): Azure転写でPrimaryをPASSさせた救済(非ラテンKP層/Tier3/CS equivalence)はOpenAI自身のPASS(票)ではない。
            primary_ng_reason = "primary_rescued_by_secondary"
            vote["primary_rescued_by_secondary"] = True
        if primary_ng_reason is None and not ctx.force_secondary and vote is None:
            return done(PASS, "primary_pass" if not approved else f"primary_pass_approved_equivalence:{pr.equivalence_basis}", warnings)
        if primary_ng_reason is None:
            if vote is not None:
                vote["primary_pass"] = True   # OpenAI自身のPASS(救済・降格なし)。以降Secondaryを必ず呼ぶ
            primary_ng_reason = "force_secondary" if vote is None else "vote_required"
    else:
        # ---- Primary NG: P1 / P2 ----
        # 2026-10-22: vote_required(KP英語)ではP1(値DIFF/否定差の短絡)をskipしてP3(Secondary)へ進む。P2除外は維持(数値・否定の保護ではない)。
        if vote is None and pvg.kind == vg.DIFF:
            return done(NG_PROTECTED, "p1_value_diff")
        if vote is None and pneg:
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
    if vote is not None:
        vote["primary_rescue_layers"] = list((pr.signals or {}).get("primary_rescue_layers") or [])
        if not vote["primary_pass"]:
            vote["primary_not_pass_reason"] = primary_ng_reason

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

    def finish_vote(s_pass: bool, s_reason: str, extra_warnings=()):
        """KP3V: 票(P/S[/W])を純関数tally()で集計して確定する唯一の出口。状態変換(PASS/PASS_WITH_WARNING/NG)はdone()の
        PASS_WITH_WARNING変換・LR_REWRITTEN付与より前にここで済ませる(P-09)。Whisperは割れたときだけ呼ぶ。"""
        import er104_kp_three_asr_vote_01 as kp3v
        pv = kp3v.Voter("openai", text=pr.text, passed=bool(vote["primary_pass"]), label=pr.label,
                        observed_protected_diff=bool(pvg.kind == vg.DIFF or pneg),
                        rescued=bool(vote["primary_rescued_by_secondary"]), rescue_layers=tuple(vote["primary_rescue_layers"]),
                        reason_note=vote.get("primary_not_pass_reason"))
        sv = kp3v.Voter("azure", text=stext, passed=bool(s_pass), label=(audit["secondary"].get("label") or ""),
                        observed_protected_diff=bool(svg.kind == vg.DIFF or sneg), reason_note=s_reason)
        wv, wcalled = None, False
        if kp3v.whisper_needed(pv, sv):
            wcalled = True
            if ctx.whisper_fn is not None:
                try:
                    wv = ctx.whisper_fn()
                except Exception as _we:  # noqa: BLE001  Whisper障害は必ず技術STOP(PASS不可)
                    wv = kp3v.Voter("whisper", None, False, available=False, error=f"{type(_we).__name__}: {_we}", technical_failure=True)
        _ow = _ortho_mark_votes(canon, lang, audit, (("primary", pv), ("secondary", sv), ("whisper", wv)))   # ASR-HOMOPHONE 委任_04(M11): ortho票の印+警告
        tr = kp3v.tally(pv, sv, wv)
        va = kp3v.build_vote_audit(pv, sv, wv, tr, secondary_called=bool(audit["secondary"].get("called") or audit["secondary"].get("cached")),
                                   whisper_called=wcalled,
                                   extra={"primary_not_pass_reason": vote.get("primary_not_pass_reason"),
                                          "primary_rescued_by_secondary": vote["primary_rescued_by_secondary"]})
        audit["vote"] = va
        w2 = list(warnings) + list(extra_warnings) + list(_ow)
        if tr.verified:
            if tr.secondary_confirmed_warning:
                w2 = w2 + [W_SECONDARY_CONFIRMED]   # 行4(P NG/S PASS/W PASS)= 事後試聴リスト対象(P-03)
            return done(PASS, tr.reason, w2)
        if tr.state == kp3v.NG_WHISPER_UNAVAILABLE:
            ev = {"type": "WHISPER_UNAVAILABLE", "error": (wv.error if wv is not None else tr.reason), "segment_key": ctx.segment_key,
                  "slot": ctx.slot, "restartable": True, "approval_required": False}
            audit["technical_stop"] = ev
            if rs is not None:
                rs.technical_stop_events.append(ev)
            return done(NG_WHISPER_UNAVAILABLE, tr.reason, w2)
        # NG: P/Sとも不合格は従来の具体的な理由(secondary_not_accepted等)を維持。割れ(Whisper NG/保護差/rollback)はvote理由。
        both_ng = (not pv.passed) and (not sv.passed)
        return done(NG_BOTH, s_reason if both_ng else tr.reason, w2)

    _s_ortho_hold = None   # ASR-HOMOPHONE 委任_04(M10): (OrthoDecision, ProtectedExplanation, 従来のNG理由)。許容集合判定がORTHO_LABEL受理のときだけ解除を確定する
    if vote is None and (svg.kind == vg.DIFF or sneg):
        # 2026-10-22: vote_required(KP英語)ではS票の値DIFF/否定差を票に影響させない(下の許容集合判定で決める)。非KPは従来どおり。
        _r = "secondary_value_diff" if svg.kind == vg.DIFF else "secondary_negation_diff"
        _hold = _ortho_secondary_precheck(outcome, canon, stext, svg, sneg, lang, audit, secondary_accept_fn is not None)
        if _hold is None:
            return done(NG_BOTH, _r, warnings)
        _s_ortho_hold = (_hold[0], _hold[1], _r)

    # 許容集合判定(注入)
    accepted, label = outcome.accepted, outcome.label
    if accepted is None and secondary_accept_fn is not None:
        r = secondary_accept_fn(canon, stext)
        accepted, label = (r if isinstance(r, tuple) else (bool(r), ""))
    if accepted is None:
        accepted = same_surface(canon, stext)  # 注入が無い場合はEXACT(同一表層)のみ
        label = label or "EXACT_SURFACE"
    audit["secondary"].update(accepted=bool(accepted), label=label)
    if _s_ortho_hold is not None:
        # M10: ORTHO_LABEL受理でなければ(M1/homophone等のORTHO以外の受理・不受理)、従来どおり値DIFF/否定差のNG_BOTH。
        import er109_xz_scope_01 as _xz
        if not (accepted and label == _xz.ORTHO_LABEL):
            return done(NG_BOTH, _s_ortho_hold[2], warnings)
        audit["final_gate"] = {"applied": True, "target": "secondary", "value_guard": svg.kind, "negation_diff": sneg,
                               "span_unlock": {"explained": True, "reason": _s_ortho_hold[1].reason, "detail": _s_ortho_hold[1].detail}}
    # ASR-HOMOPHONE 委任_04: Secondary転写がer109(ORTHO_LABEL)で受理されたとき、ORTHO警告(+否定差解除時のORTHO_NEGATION_WORD_HOMOPHONE)を付与し、記録を加算する。
    _s_ortho_w: list = []
    if accepted and lang == "en" and label == "ORTHOGRAPHIC_EQUIVALENT_MATCH":
        import er109_xz_scope_01 as _xz
        _sd = _s_ortho_hold[0] if _s_ortho_hold is not None else _xz.decision(canon, stext, sink=audit)
        if _sd is not None:
            _xz.record_site(audit, "secondary", _sd,
                            span_unlock=({"explained": True, "reason": _s_ortho_hold[1].reason, "detail": _s_ortho_hold[1].detail}
                                         if _s_ortho_hold is not None else None))
            _s_ortho_w = list(_sd.warning_labels) + (list(_s_ortho_hold[1].warning_labels) if _s_ortho_hold is not None else [])
            _s_ortho_w = list(dict.fromkeys(_s_ortho_w))

    if a3:
        # 委任_13(A3R-01/02/06): Secondary受理時は採用転写(Secondary)の長さで再評価する(max_lenは呼出元の値)。
        slen = len(stext)
        sok = slen <= int(ctx.max_len)
        audit["length"].update(secondary_len=slen, surface_len=len(_surface_key(stext)))
        if accepted and not sok:
            audit["length"].update(adopted_from="secondary", adopted_ok=False)
            if vote is not None:
                return finish_vote(False, "secondary_length_ng")
            return done(NG_BOTH, "secondary_length_ng", warnings)
        if accepted:
            audit["length"].update(adopted_from="secondary", adopted_ok=True)
            if not plen_ok:
                warnings = warnings + [W_PRIMARY_LENGTH_EXCESS]  # A3R-07: additive(受理条件は不変)
    ambiguous_primary = pvg.kind == vg.AMBIGUOUS
    if svg.kind == vg.AMBIGUOUS and not same_surface(canon, stext):
        if vote is not None:
            return finish_vote(False, "secondary_ambiguous_value_not_same_surface")
        return done(NG_BOTH, "secondary_ambiguous_value_not_same_surface", warnings)
    if ambiguous_primary:
        if same_surface(canon, stext):
            if vote is not None:
                return finish_vote(True, "secondary_exact_resolves_ambiguous", [W_NUMERIC_AMBIGUOUS_SURFACE])
            return done(PASS_WITH_WARNING, "secondary_exact_resolves_ambiguous", warnings + [W_NUMERIC_AMBIGUOUS_SURFACE])
        if vote is not None:
            return finish_vote(False, "ambiguous_value_secondary_not_same_surface")
        return done(NG_BOTH, "ambiguous_value_secondary_not_same_surface", warnings)
    if not accepted:
        if vote is not None:
            return finish_vote(False, "secondary_not_accepted")
        return done(NG_BOTH, "secondary_not_accepted", warnings)
    if final_and_gate:
        _fg_prev = audit.get("final_gate") if isinstance(audit.get("final_gate"), dict) else {}
        audit["final_gate"] = {"applied": True, "target": "secondary", "value_guard": svg.kind, "negation_diff": sneg}
        if _fg_prev.get("span_unlock") is not None and _s_ortho_hold is not None:
            audit["final_gate"]["span_unlock"] = _fg_prev["span_unlock"]   # ASR-HOMOPHONE 委任_04: Secondary転写のspan解除記録を残す(ortho不使用ならキー無し)
    if vote is not None:
        # KP3V: Secondary(Azure)許容集合PASS ∧ 値/否定ガードOK = S票PASS。最終は3票の集計(finish_vote)。classificationはadapter側で行ごとに整理(P-03)。
        return finish_vote(True, "secondary_accepted", list(svg.warnings))
    if primary_ng_reason == "force_secondary":
        # 委任_03: Primary PASS + force_secondary(minimal fallback/LR後v1)でSecondaryも許容集合PASS = 両エンジン合意。
        # 従来(er006 force_secondary)もPASS扱い(警告なし)だったため、SECONDARY_CONFIRMED警告は付けない(LR後v1はdone()がLR_REWRITTENを付与)。
        return done(PASS, "force_secondary_agreed", warnings + list(svg.warnings) + _s_ortho_w)
    return done(PASS_WITH_WARNING, "secondary_confirmed" if primary_ng_reason != "primary_length_ng" else "secondary_confirmed_primary_length_ng",
                warnings + [W_SECONDARY_CONFIRMED] + list(svg.warnings) + _s_ortho_w)
