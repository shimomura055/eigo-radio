# ============================================================
# er104_kp_three_asr_vote_01.py
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 (ユーザー正式承認 2026-10-22 APPROVED_FOR_PRODUCTION。委任_02でOpus条件A(OF-KP3V-P-01〜12)を反映)
#
# Key Phrase英語フレーズの「OpenAI(Primary)・Azure(Secondary)・Whisper(local)の3-ASR多数決(2/3 PASSで最終PASS)」の判定核。
# 置換対象 = 旧「両方PASS必須」(er096_kp_dual_pass_01、OPEN-440)。本moduleは **純粋な集計関数 tally()/whisper_needed()** を持つ
# (P-09: er078 judgeの`done()`出口と`decide()`が同じ関数を呼ぶ=実装二重化なし)。
#
# 【2026-10-22 KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01(OPEN-458、ユーザー承認)】KP英語の票・短絡から『数値・否定の保護(値DIFF/否定差)』を撤去した。
#   票のPASS/NGは本文一致判定(classify_asr_match+同音救済)だけで決め、値DIFF/否定差は監査(observed_protected_diff)に記録するだけで判定に使わない
#   (撤去: Primary保護差短絡の状態・反対票側保護差ブロックの状態/引数・Voterの保護差の判定用途。いずれも2026-10-22以前のKP3V v1の規則)。非KP音声の統一judgeの保護(er078側のNG_PROTECTED)は不変。
#   audit/証跡には `guard_lifted:true` / `guard_lifted_version` を加算(version `kp_vote_check_v1`は据え置き)。AMBIGUOUS(根拠のない曖昧表層)は票の分類として維持(保護解除の対象外)。
# 真理値表(ユーザー§2):  P=Primary(OpenAI自身のPASS。Azure転写に依存した救済PASSはPASSと数えない) S=Secondary(Azure) W=Whisper
#   行1 P PASS S PASS -> PASS(W不要)         行2 P PASS S NG -> W PASS で PASS(PASS_VOTE_2OF3,row=P+W) / W NG で NG
#   行4 P NG S PASS -> W PASS で PASS_WITH_WARNING+SECONDARY_CONFIRMED(row=S+W、事後試聴リスト対象。P-03) / W NG で NG
#   行6 P NG S NG -> NG(W不要・呼ばない)
# fail-closed(P-08): Secondary取得不能=NG_SECONDARY_UNAVAILABLE(技術STOP。Whisperで救済しない=2/3に降格しない、P-07a) /
#   Whisper例外・import失敗・timeout・circuit open=NG_WHISPER_UNAVAILABLE(技術STOP。HRに入れない) /
#   Whisper空転写=NG票(通常の再生成。技術障害ではない)。
# rollback(P-04): KP_WHISPER_TIEBREAK_ENABLED=False = 旧「両方PASS必須」(Whisperを呼ばず割れ=通常NG)。Primary単独へ落とすスイッチは置かない。
#   KP_THREE_ASR_VOTE_ENABLED=False は呼出点が vote_pass_required を渡さない経路(=KP専用規則なし)で、緊急用の単一flag。
# ============================================================
from __future__ import annotations

import concurrent.futures
import hashlib
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

CHECK_VERSION = "kp_vote_check_v1"
GUARD_LIFTED_VERSION = "kp_vote_guard_lifted_v1"   # 2026-10-22: 数値・否定の保護解除(加算フィールド。reader互換のためCHECK_VERSIONは据え置き)
KP_THREE_ASR_VOTE_ENABLED = True   # 単一flag(module定数。env/引数/設定dictからは変えられない)。読取は vote_enabled() のみ
KP_WHISPER_TIEBREAK_ENABLED = True  # 戻しスイッチ(P-04): False = 旧「両方PASS必須」。読取は tiebreak_enabled() のみ
WHISPER_MODEL_SIZE = "small"        # Production既存(er008 disfluency QA / er006 CS-equivalence)と同一: faster-whisper small cpu int8
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_TIMEOUT_SEC = 60.0
WHISPER_CIRCUIT_THRESHOLD = 3       # 例外の連続失敗でcircuit open(timeoutは閾値1=即open、P-08)

# ---- 最終状態 ----
PASS_DUAL = "PASS_DUAL"                         # P PASS かつ S PASS (Whisper不呼出)
PASS_VOTE_2OF3 = "PASS_VOTE_2OF3"               # P/Sが割れ、Whisperが多数派を作ってPASS
NG_BOTH = "NG_BOTH"                             # P NG かつ S NG (Whisper不呼出)
NG_VOTE_WHISPER_NG = "NG_VOTE_WHISPER_NG"       # 割れてWhisperもNG/空転写(1/3 PASS)。通常の再生成
NG_PRIMARY_ASR_FAILURE = "NG_PRIMARY_ASR_FAILURE"
NG_SECONDARY_UNAVAILABLE = "NG_SECONDARY_UNAVAILABLE"   # 技術STOP(Primary+Whisperの2/3へ降格しない)
NG_WHISPER_UNAVAILABLE = "NG_WHISPER_UNAVAILABLE"       # 技術STOP(例外/import失敗/timeout/circuit open/未設定)
NG_SPLIT_TIEBREAK_OFF = "NG_SPLIT_TIEBREAK_OFF"         # tie-break無効(戻しスイッチ)時の割れ = 旧「両方PASS必須」と同じ通常NG
PASSING = (PASS_DUAL, PASS_VOTE_2OF3)
TECHNICAL_STOPS = (NG_SECONDARY_UNAVAILABLE, NG_WHISPER_UNAVAILABLE)
HARD_STATES = (NG_PRIMARY_ASR_FAILURE, NG_SECONDARY_UNAVAILABLE)   # 票を集計する前に確定する状態(除外NG_EXCLUDEDはjudge側P2)
STATES = (PASS_DUAL, PASS_VOTE_2OF3, NG_BOTH, NG_VOTE_WHISPER_NG, NG_PRIMARY_ASR_FAILURE,
          NG_SECONDARY_UNAVAILABLE, NG_WHISPER_UNAVAILABLE, NG_SPLIT_TIEBREAK_OFF)
ROW_DUAL, ROW_P_W, ROW_S_W = "P+S", "P+W", "S+W"   # どの行で合格したか(P-10)


def vote_enabled() -> bool:
    """単一のflag読取関数(全呼出点がこれだけを見る)。"""
    return bool(KP_THREE_ASR_VOTE_ENABLED)


def tiebreak_enabled() -> bool:
    """戻しスイッチの単一読取関数(P-04)。"""
    return bool(KP_WHISPER_TIEBREAK_ENABLED)


@dataclass
class Voter:
    provider: str                     # openai | azure | whisper
    text: Optional[str] = None
    passed: bool = False              # 現行分類器(classify_asr_match + 同音救済 + 値/否定ガード)でのPASS。Primaryは「OpenAI自身のPASS」
    available: bool = True            # False = 票を投じられない(空転写/例外/circuit open/timeout/未導入)
    label: str = ""
    observed_protected_diff: bool = False   # 観測した値DIFF/否定差(監査のみ。票・短絡には使わない=2026-10-22保護解除)
    rescued: bool = False             # (Primaryのみ) Azure転写等に依存した救済PASS。passed=Falseとして渡す
    error: Optional[str] = None
    technical_failure: bool = False   # True = 環境障害(例外/import失敗/timeout/circuit open)。空転写はFalse(NG票)
    reason_note: Optional[str] = None  # NG票の理由(length_ng / ambiguous_value / not_accepted ...)
    ms: Optional[int] = None
    memo_hit: bool = False
    rescue_layers: tuple = ()

    def audit(self) -> dict:
        return {"provider": self.provider, "text": self.text, "pass": bool(self.passed), "available": bool(self.available),
                "label": self.label, "observed_protected_diff": bool(self.observed_protected_diff), "rescued": bool(self.rescued), "error": self.error,
                "technical_failure": bool(self.technical_failure), "note": self.reason_note, "rescue_layers": list(self.rescue_layers)}


@dataclass
class TallyResult:
    state: str
    reason: str
    pass_count: int
    row: Optional[str] = None          # 合格時のみ: ROW_DUAL / ROW_P_W / ROW_S_W
    secondary_confirmed_warning: bool = False   # ROW_S_W(Primary NGでAzure+Whisperが合格)= SECONDARY_CONFIRMED警告+事後試聴リスト(P-03)

    @property
    def verified(self) -> bool:
        return self.state in PASSING

    @property
    def technical_stop(self) -> bool:
        return self.state in TECHNICAL_STOPS


@dataclass
class VoteDecision:
    state: str
    reason: str
    primary: Voter
    secondary: Optional[Voter] = None
    whisper: Optional[Voter] = None
    whisper_called: bool = False
    secondary_called: bool = False
    pass_count: int = 0
    row: Optional[str] = None
    secondary_confirmed_warning: bool = False
    audit: dict = field(default_factory=dict)

    @property
    def verified(self) -> bool:
        return self.state in PASSING

    @property
    def technical_stop(self) -> bool:
        return self.state in TECHNICAL_STOPS


def _unavailable(provider: str, err: str, *, technical: bool = True) -> Voter:
    return Voter(provider=provider, text=None, passed=False, available=False, error=err, technical_failure=technical)


def _secondary_ok(sec: Optional[Voter]) -> bool:
    return bool(sec is not None and sec.available and sec.text and str(sec.text).strip())


def _is_split(primary: Voter, secondary: Voter) -> bool:
    return bool(primary.passed) != bool(secondary.passed)


def whisper_needed(primary: Voter, secondary: Optional[Voter], *, tiebreak: Optional[bool] = None) -> bool:
    """純関数: PとSが割れていて、Whisperの票で結論が変わりうるときだけTrue(呼出側はTrueのときだけWhisperを呼ぶ)。"""
    if not primary.available or primary.text is None or not _secondary_ok(secondary):
        return False
    if not _is_split(primary, secondary):
        return False
    return bool(tiebreak_enabled() if tiebreak is None else tiebreak)


def tally(primary: Voter, secondary: Optional[Voter], whisper: Optional[Voter], *, tiebreak: Optional[bool] = None) -> TallyResult:
    """純粋な集計関数(I/Oなし)。judgeの`done()`出口と`decide()`が共に呼ぶ(P-09)。`whisper`はwhisper_needed()がTrueのときだけ渡す。"""
    n = int(bool(primary.passed)) + int(bool(secondary and secondary.passed)) + int(bool(whisper and whisper.passed))

    def R(state, reason, row=None, warn=False, count=None):
        return TallyResult(state, reason, n if count is None else count, row, warn)

    if not primary.available or primary.text is None:
        return R(NG_PRIMARY_ASR_FAILURE, "primary_asr_failure", count=0)
    if not _secondary_ok(secondary):
        return R(NG_SECONDARY_UNAVAILABLE, "secondary_unavailable")
    if primary.passed and secondary.passed:
        return R(PASS_DUAL, "dual_agreed", ROW_DUAL)
    if (not primary.passed) and (not secondary.passed):
        return R(NG_BOTH, "primary_and_secondary_ng")
    if not (tiebreak_enabled() if tiebreak is None else tiebreak):
        return R(NG_SPLIT_TIEBREAK_OFF, "split_tiebreak_disabled_dual_rule")
    if whisper is None:
        return R(NG_WHISPER_UNAVAILABLE, "whisper_not_called")
    if whisper.technical_failure:
        return R(NG_WHISPER_UNAVAILABLE, "whisper_unavailable")
    if not whisper.available or not (whisper.text and str(whisper.text).strip()):
        return R(NG_VOTE_WHISPER_NG, "whisper_empty_transcript_ng_vote")   # 空転写 = NG票(通常の再生成)
    if whisper.passed:
        if primary.passed:
            return R(PASS_VOTE_2OF3, "vote_2of3:primary+whisper", ROW_P_W)
        return R(PASS_VOTE_2OF3, "vote_2of3:secondary+whisper", ROW_S_W, warn=True)
    return R(NG_VOTE_WHISPER_NG, "whisper_ng_1of3")


def build_vote_audit(primary: Voter, secondary: Optional[Voter], whisper: Optional[Voter], tr: TallyResult, *, secondary_called: bool,
                     whisper_called: bool, tiebreak: Optional[bool] = None, extra: Optional[dict] = None) -> dict:
    """judgeの`audit["vote"]`と`decide()`の`VoteDecision.audit`が同じ形になる唯一の組立関数。"""
    obs = {"primary": bool(primary.observed_protected_diff), "secondary": bool(secondary.observed_protected_diff) if secondary else False,
           "whisper": bool(whisper.observed_protected_diff) if whisper else False}
    a = {"version": CHECK_VERSION, "guard_lifted": True, "guard_lifted_version": GUARD_LIFTED_VERSION, "observed_protected_diff": obs,
         "required": True, "state": tr.state, "reason": tr.reason, "row": tr.row, "pass_count": tr.pass_count,
         "tiebreak_enabled": bool(tiebreak_enabled() if tiebreak is None else tiebreak),
         "primary": primary.audit(), "secondary": (secondary.audit() if secondary else None), "secondary_called": bool(secondary_called),
         "whisper": (whisper.audit() if whisper else None), "whisper_called": bool(whisper_called),
         "whisper_model": ({"model": WHISPER_MODEL_SIZE, "compute_type": WHISPER_COMPUTE_TYPE, "device": "cpu",
                            "library": "faster_whisper"} if whisper_called else None)}
    if whisper is not None:
        a["whisper"].update(ms=whisper.ms, memo_hit=whisper.memo_hit)
    if extra:
        a.update(extra)
    return a


def decide(primary: Voter, secondary_fn: Callable[[], Voter], whisper_fn: Optional[Callable[[], Voter]], *,
           tiebreak: Optional[bool] = None) -> VoteDecision:
    """純関数+遅延callable。judgeと同じ`whisper_needed()`/`tally()`だけを使う(判定ロジックの二重実装なし)。
    secondary_fn/whisper_fnの例外はfail-closed(Secondary=技術STOP、Whisper=技術STOP)に変換する。"""
    def finish(sec, wh, sc, wc):
        tr = tally(primary, sec, wh, tiebreak=tiebreak)
        return VoteDecision(tr.state, tr.reason, primary, sec, wh, whisper_called=wc, secondary_called=sc, pass_count=tr.pass_count,
                            row=tr.row, secondary_confirmed_warning=tr.secondary_confirmed_warning,
                            audit=build_vote_audit(primary, sec, wh, tr, secondary_called=sc, whisper_called=wc, tiebreak=tiebreak))

    if not primary.available or primary.text is None:
        return finish(None, None, False, False)
    try:
        sec = secondary_fn()
    except Exception as e:                                          # 設定不備の再送出は呼出側adapter(is_config_stop_error)が担う
        sec = _unavailable("azure", f"{type(e).__name__}: {e}")
    if not _secondary_ok(sec):
        return finish(sec, None, True, False)
    if not whisper_needed(primary, sec, tiebreak=tiebreak):
        return finish(sec, None, True, False)
    if whisper_fn is None:
        wh = None
    else:
        try:
            wh = whisper_fn()
        except Exception as e:
            wh = _unavailable("whisper", f"{type(e).__name__}: {e}")
    return finish(sec, wh, True, whisper_fn is not None)


# ============================================================
# Voter構築: Production既存の分類器をそのまま使う(新しい判定基準は作らない)
# ============================================================
def _classify(canonical: str, text: str):
    import er006_preprod_hardening_01_validation as val
    import er006_secondary_asr_01 as S
    cls = val.classify_asr_match(canonical, text)
    if cls.should_pass:
        return True, cls.classification
    alt = S._step_alternate_pass(cls)
    if alt:
        return True, str(alt)
    return False, cls.classification


def make_voter(provider: str, canonical: str, text: Optional[str], *, rescued: bool = False, lang: str = "en",
               max_len: Optional[int] = None, ambiguous_blocks: bool = False) -> Voter:
    """転写文字列 -> Voter。classify_asr_match + 同音救済(_step_alternate_pass) + 値/否定ガード(er078 _protected)。
    票は本文一致判定のみで決める(値DIFF/否定差=pdiffは`observed_protected_diff`として記録するだけ。2026-10-22保護解除)。
    M1(multi-candidate)は含めない(P-07c: Whisperには適用しない=保守側)。`max_len`(P-02)=呼出元と同じ長さ判定(超過はNG票)、
    `ambiguous_blocks`=値ガードAMBIGUOUS(根拠のない曖昧表層)はPASS票にしない(P-02)。空転写は技術障害ではなくNG票(available=False)。"""
    if text is None or not str(text).strip():
        return Voter(provider=provider, text=text, passed=False, available=False, error="empty_transcript", technical_failure=False)
    import er078_asr_unified_judge_01 as uj
    vgr, neg = uj._protected(canonical, text, lang)
    pdiff = bool(vgr.kind == uj.vg.DIFF or neg)
    ok, label = _classify(canonical, text)
    note = None
    if ok and max_len is not None and len(text) > int(max_len):
        ok, note = False, "length_ng"
    if ok and ambiguous_blocks and vgr.kind == uj.vg.AMBIGUOUS:
        ok, note = False, "ambiguous_value"
    return Voter(provider=provider, text=text, passed=bool(ok and not rescued), label=label, observed_protected_diff=pdiff,
                 rescued=rescued, reason_note=note)


# ============================================================
# ローカルWhisper(faster-whisper small int8、Production既存loaderを共有。API 0 / 費用0)
# ============================================================
class WhisperTimeout(TimeoutError):
    pass


@dataclass
class WhisperRunState:
    """Whisper専用のrun単位circuit(P-08)。Azure RunStateとは独立(Whisperを使わない音声には影響しない)。"""
    failures: int = 0
    failures_total: int = 0
    calls: int = 0
    memo_hits: int = 0
    circuit_open: bool = False
    events: list = field(default_factory=list)
    memo: dict = field(default_factory=dict)       # (sha, model) -> text


WHISPER_STATE = WhisperRunState()


def reset_whisper_state() -> None:
    global WHISPER_STATE
    WHISPER_STATE = WhisperRunState()


def whisper_circuit_open() -> bool:
    return bool(WHISPER_STATE.circuit_open)


def _record_whisper_failure(err: str, *, timeout: bool) -> None:
    s = WHISPER_STATE
    s.failures += 1
    s.failures_total += 1
    s.events.append({"type": "WHISPER_TIMEOUT" if timeout else "WHISPER_UNAVAILABLE", "error": err, "restartable": True,
                     "approval_required": False})
    if (timeout or s.failures >= WHISPER_CIRCUIT_THRESHOLD) and not s.circuit_open:
        s.circuit_open = True
        s.events.append({"type": "WHISPER_CIRCUIT_OPEN", "after_failures": s.failures, "restartable": True, "approval_required": False})


def whisper_transcribe(wav_path: str, *, model_size: str = WHISPER_MODEL_SIZE, timeout: float = WHISPER_TIMEOUT_SEC) -> str:
    """既存`er008_disfluency_qa_18.transcribe_verbatim`と同一設定で転写する。timeoutはWhisperTimeout、例外は送出(呼出側で技術STOPへ変換)。"""
    import er008_disfluency_qa_18 as dq

    def _run():
        words = dq.transcribe_verbatim(wav_path, language="en", model_size=model_size)
        return " ".join("".join(w["text"] for w in words).split())

    ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        try:
            return ex.submit(_run).result(timeout=timeout)
        except concurrent.futures.TimeoutError as e:
            raise WhisperTimeout(f"whisper timeout {timeout}s") from e
    finally:
        ex.shutdown(wait=False, cancel_futures=True)


def whisper_vote(canonical: str, wav_path: str, *, sha: Optional[str] = None, max_len: Optional[int] = None, lang: str = "en",
                 transcribe_fn: Optional[Callable[[str], str]] = None, stored_text: Optional[str] = None) -> Voter:
    """Whisperの1票。例外/timeout/circuit open = 技術障害Voter(technical_failure=True)、空転写 = NG票。
    同一wav(sha)×modelはrun内memo。`stored_text`(保存済み転写)があればそれを使い再転写しない。
    transcribe_fnの既定は呼出時に`whisper_transcribe`を解決する(testでのmonkeypatch可)。"""
    s = WHISPER_STATE
    t0 = time.time()
    memo_key = ((sha or wav_path), WHISPER_MODEL_SIZE)
    text, memo_hit = None, False
    if stored_text is not None and str(stored_text).strip():
        text, memo_hit = stored_text, True
    elif memo_key in s.memo:
        text, memo_hit = s.memo[memo_key], True
        s.memo_hits += 1
    else:
        if s.circuit_open:
            return _unavailable("whisper", "whisper_circuit_open")
        fn = transcribe_fn or whisper_transcribe
        s.calls += 1
        try:
            text = fn(wav_path)
        except WhisperTimeout as e:
            _record_whisper_failure(f"{type(e).__name__}: {e}", timeout=True)
            return _unavailable("whisper", f"{type(e).__name__}: {e}")
        except Exception as e:  # noqa: BLE001  import失敗/モデル破損/OS error等はすべて技術障害
            _record_whisper_failure(f"{type(e).__name__}: {e}", timeout=False)
            return _unavailable("whisper", f"{type(e).__name__}: {e}")
        s.failures = 0
        s.memo[memo_key] = text
    v = make_voter("whisper", canonical, text, lang=lang, max_len=max_len, ambiguous_blocks=True)
    v.ms, v.memo_hit = int((time.time() - t0) * 1000), memo_hit
    return v


def whisper_preflight(*, sample_wav: Optional[str] = None) -> dict:
    """KP stage開始時の事前確認(P-08): モデルロード可否・キャッシュ有無・model/compute type。失敗時はcircuitを開く(最初のTTSの前に技術STOP)。
    sample_wavがあれば1clip転写して動作確認する(任意)。"""
    import os
    rec = {"model": WHISPER_MODEL_SIZE, "compute_type": WHISPER_COMPUTE_TYPE, "device": "cpu", "ok": False, "error": None,
           "model_cache_present": None, "load_sec": None}
    try:
        hub = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub", f"models--Systran--faster-whisper-{WHISPER_MODEL_SIZE}")
        rec["model_cache_present"] = os.path.isdir(hub)
        t = time.time()
        import er008_disfluency_qa_18 as dq
        dq._get_model(WHISPER_MODEL_SIZE)
        rec["load_sec"] = round(time.time() - t, 3)
        if sample_wav:
            whisper_transcribe(sample_wav)
        rec["ok"] = True
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {e}"
        _record_whisper_failure(rec["error"], timeout=False)
        WHISPER_STATE.circuit_open = True
    return rec


# ============================================================
# 証跡 kp_vote_check(Store entry / results entryに保存。旧kp_dual_check_v1の後継。容器名kp_dual_checkは維持し、versionで区別 P-05)
# ============================================================
def sha256_file(path: str) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def vote_check_from_audit(vote_audit: dict, wav_path: str, canonical_text: str, *, source: str, judge_state: Optional[str] = None,
                          verified: Optional[bool] = None) -> dict:
    """judge audit["vote"] または VoteDecision.audit から保存用証跡を作る(1つの組立関数)。`row`=どの行で合格したか(P-10)。"""
    a = vote_audit or {}
    ok = bool(a.get("state") in PASSING) if verified is None else bool(verified)
    p, s, w = a.get("primary") or {}, a.get("secondary") or {}, a.get("whisper") or {}
    return {"version": CHECK_VERSION, "guard_lifted": bool(a.get("guard_lifted", False)), "guard_lifted_version": a.get("guard_lifted_version"),
            "observed_protected_diff": a.get("observed_protected_diff"), "ok": ok, "source": source, "canonical_text": canonical_text, "wav_sha256": sha256_file(wav_path),
            "vote_state": a.get("state"), "judge_state": judge_state or a.get("state"), "reason_code": a.get("reason"), "row": a.get("row"),
            "pass_count": a.get("pass_count"), "tiebreak_enabled": a.get("tiebreak_enabled"),
            "primary": {"provider": "openai", "text": p.get("text"), "pass": bool(p.get("pass")), "rescued": bool(p.get("rescued")),
                        "rescue_layers": list(p.get("rescue_layers") or [])},
            "secondary": ({"provider": "azure", "text": s.get("text"), "pass": bool(s.get("pass")), "called": bool(a.get("secondary_called")),
                           "observed_protected_diff": bool(s.get("observed_protected_diff"))} if s else None),
            "whisper": ({"provider": "faster_whisper", "model": WHISPER_MODEL_SIZE, "compute_type": WHISPER_COMPUTE_TYPE,
                         "text": w.get("text"), "pass": bool(w.get("pass")), "called": bool(a.get("whisper_called")),
                         "error": w.get("error"), "memo_hit": bool(w.get("memo_hit"))} if w else {"called": False}),
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
