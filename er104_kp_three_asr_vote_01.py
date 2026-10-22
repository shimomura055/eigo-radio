# ============================================================
# er104_kp_three_asr_vote_01.py  (未配線 / API 0 / Production既存ファイル未編集)
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_01 (ユーザー正式承認 2026-10-22 APPROVED_FOR_PRODUCTION、到達Status=設計+未配線module)
#
# Key Phrase英語フレーズの「OpenAI(Primary)・Azure(Secondary)・Whisper(local)の3-ASR多数決(2/3 PASSで最終PASS)」の判定核。
# 置換対象 = er096_kp_dual_pass_01(両方PASS必須、OPEN-440)。本moduleはまだどのProduction経路からもimportされない
# (配線は次委任。`import er104_*`するProduction .pyが0であることはtestで固定)。
#
# 真理値表(ユーザー§2):  P=Primary(OpenAI自身のPASS。Azure転写に依存した救済PASSはPASSと数えない=er096踏襲) S=Secondary(Azure) W=Whisper
#   P PASS S PASS -> PASS(W不要)      P PASS S NG -> W PASS で PASS / W NG で NG
#   P NG   S PASS -> W PASS で PASS / W NG で NG      P NG S NG -> NG(W不要・呼ばない)
# fail-closed: Secondary取得不能=NG_SECONDARY_UNAVAILABLE(Whisperで救済しない=2/3に降格しない) / Whisper不能(例外・空・timeout・未導入)=NG_WHISPER_UNAVAILABLE。
# 呼出順: Primary(既に取得済) -> Secondary(callable) -> Whisper(callable、PとSが割れたときのみ)。callableは遅延呼出で、呼出回数をtestで固定する。
# ============================================================
from __future__ import annotations

import concurrent.futures
import hashlib
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

CHECK_VERSION = "kp_vote_check_v1"
KP_THREE_ASR_VOTE_ENABLED = True   # rollback定数(配線時に単一flag読取関数`vote_enabled()`経由。env/flagではない)。Falseなら呼出側はer096両方PASSへ戻す
WHISPER_MODEL_SIZE = "small"       # 既存Production(er008 disfluency QA / er006 CS-equivalence local ASR)と同一: faster-whisper small cpu int8
WHISPER_TIMEOUT_SEC = 60.0

# ---- 最終状態 ----
PASS_DUAL = "PASS_DUAL"                         # P PASS かつ S PASS (Whisper不呼出)
PASS_VOTE_2OF3 = "PASS_VOTE_2OF3"               # P/Sが割れ、Whisperが多数派を作ってPASS
NG_BOTH = "NG_BOTH"                             # P NG かつ S NG (Whisper不呼出)
NG_VOTE_WHISPER_NG = "NG_VOTE_WHISPER_NG"       # 割れてWhisperもNG(1/3 PASS)
NG_PROTECTED = "NG_PROTECTED"                   # Primaryの保護差(値DIFF/否定差)。既存P1どおりSecondary/Whisper不呼出
NG_PROTECTED_DISSENT = "NG_PROTECTED_DISSENT"   # 反対票側に保護差(値DIFF/否定差)があり、2/3 PASSを成立させない(保守側。Opus確認観点)
NG_PRIMARY_ASR_FAILURE = "NG_PRIMARY_ASR_FAILURE"
NG_SECONDARY_UNAVAILABLE = "NG_SECONDARY_UNAVAILABLE"   # 技術STOP(従来どおり。Primary+Whisperの2/3へ降格しない)
NG_WHISPER_UNAVAILABLE = "NG_WHISPER_UNAVAILABLE"       # fail-closed
NG_SPLIT_TIEBREAK_OFF = "NG_SPLIT_TIEBREAK_OFF"         # tie-break無効(段階rollback定数)時の割れ = 旧「両方PASS必須」と同じ通常NG
PASSING = (PASS_DUAL, PASS_VOTE_2OF3)
STATES = (PASS_DUAL, PASS_VOTE_2OF3, NG_BOTH, NG_VOTE_WHISPER_NG, NG_PROTECTED, NG_PROTECTED_DISSENT, NG_PRIMARY_ASR_FAILURE,
          NG_SECONDARY_UNAVAILABLE, NG_WHISPER_UNAVAILABLE, NG_SPLIT_TIEBREAK_OFF)
KP_WHISPER_TIEBREAK_ENABLED = True   # 段階rollback定数: False = Whisperを呼ばず、割れ(P/S不一致)は旧「両方PASS必須」と同じ通常NG(コード撤去不要でdual挙動へ戻せる)


def vote_enabled() -> bool:
    """単一のflag読取関数(配線時に全呼出点がこれだけを見る)。"""
    return bool(KP_THREE_ASR_VOTE_ENABLED)


@dataclass
class Voter:
    provider: str                     # openai | azure | whisper
    text: Optional[str] = None
    passed: bool = False              # 現行分類器(classify_asr_match + 同音救済 + 値/否定ガード)でのPASS。Primaryは「OpenAI自身のPASS」(救済でない)
    available: bool = True            # False = 取得不能(例外/空転写/circuit open/timeout/未導入)
    label: str = ""
    protected_diff: bool = False      # 値DIFFまたは否定差(転写自体が別の数/否定を言っている)
    rescued: bool = False             # (Primaryのみ) Azure転写等に依存した救済PASS。passed=Falseとして渡す
    error: Optional[str] = None

    def audit(self) -> dict:
        return {"provider": self.provider, "text": self.text, "pass": bool(self.passed), "available": bool(self.available),
                "label": self.label, "protected_diff": bool(self.protected_diff), "rescued": bool(self.rescued), "error": self.error}


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
    audit: dict = field(default_factory=dict)

    @property
    def verified(self) -> bool:
        return self.state in PASSING

    @property
    def technical_stop(self) -> bool:
        return self.state == NG_SECONDARY_UNAVAILABLE


def _unavailable(provider: str, err: str) -> Voter:
    return Voter(provider=provider, text=None, passed=False, available=False, error=err)


def decide(primary: Voter, secondary_fn: Callable[[], Voter], whisper_fn: Optional[Callable[[], Voter]], *,
           protected_dissent_blocks: bool = True, tiebreak_enabled: Optional[bool] = None) -> VoteDecision:
    """3-ASR多数決。secondary_fn/whisper_fnは遅延callable(Voter返却。例外はfail-closedに変換)。"""
    def done(state, reason, sec=None, wh=None, sc=False, wc=False) -> VoteDecision:
        n = int(bool(primary.passed)) + int(bool(sec and sec.passed)) + int(bool(wh and wh.passed))
        d = VoteDecision(state, reason, primary, sec, wh, whisper_called=wc, secondary_called=sc, pass_count=n)
        d.audit = {"version": CHECK_VERSION, "state": state, "reason": reason, "pass_count": n, "primary": primary.audit(),
                   "secondary": sec.audit() if sec else None, "secondary_called": sc,
                   "whisper": wh.audit() if wh else None, "whisper_called": wc, "whisper_model": WHISPER_MODEL_SIZE if wc else None}
        return d

    if not primary.available or primary.text is None:
        return done(NG_PRIMARY_ASR_FAILURE, "primary_asr_failure")
    if primary.protected_diff:
        return done(NG_PROTECTED, "primary_protected_diff")      # 既存P1と同じ短絡(Secondary/Whisper不呼出)

    try:
        sec = secondary_fn()
    except Exception as e:                                          # 設定不備の再送出は呼出側adapter(is_config_stop_error)が担う
        sec = _unavailable("azure", f"{type(e).__name__}: {e}")
    if sec is None or not sec.available or not (sec.text and str(sec.text).strip()):
        return done(NG_SECONDARY_UNAVAILABLE, "secondary_unavailable", sec=sec, sc=True)

    if primary.passed and sec.passed:
        return done(PASS_DUAL, "dual_agreed", sec=sec, sc=True)
    if (not primary.passed) and (not sec.passed):
        return done(NG_BOTH, "primary_and_secondary_ng", sec=sec, sc=True)

    # ---- P/Sが割れた: Whisperのみ呼ぶ ----
    dissent = sec if primary.passed else primary
    if protected_dissent_blocks and dissent.protected_diff:
        return done(NG_PROTECTED_DISSENT, f"dissent_protected_diff:{dissent.provider}", sec=sec, sc=True)
    if not (KP_WHISPER_TIEBREAK_ENABLED if tiebreak_enabled is None else tiebreak_enabled):
        return done(NG_SPLIT_TIEBREAK_OFF, "split_tiebreak_disabled_dual_rule", sec=sec, sc=True)
    if whisper_fn is None:
        return done(NG_WHISPER_UNAVAILABLE, "whisper_not_configured", sec=sec, sc=True)
    try:
        wh = whisper_fn()
    except Exception as e:
        wh = _unavailable("whisper", f"{type(e).__name__}: {e}")
    if wh is None or not wh.available or not (wh.text and str(wh.text).strip()):
        return done(NG_WHISPER_UNAVAILABLE, "whisper_unavailable", sec=sec, wh=wh, sc=True, wc=True)
    if wh.passed:
        return done(PASS_VOTE_2OF3, "vote_2of3:" + ("primary+whisper" if primary.passed else "secondary+whisper"),
                    sec=sec, wh=wh, sc=True, wc=True)
    return done(NG_VOTE_WHISPER_NG, "whisper_ng_1of3", sec=sec, wh=wh, sc=True, wc=True)


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


def make_voter(provider: str, canonical: str, text: Optional[str], *, rescued: bool = False, lang: str = "en") -> Voter:
    """転写文字列 -> Voter。classify_asr_match + 同音救済(_step_alternate_pass、er006 `_secondary_accept`の前2段と同一) + 値/否定ガード(er078 _protected)。
    M1(multi-candidate)は含めない(より保守側。ProductionのSecondary側のみM1経路があるが、Whisperには適用しない)。"""
    if text is None or not str(text).strip():
        return Voter(provider=provider, text=text, passed=False, available=False, error="empty_transcript")
    import er078_asr_unified_judge_01 as uj
    vgr, neg = uj._protected(canonical, text, lang)
    pdiff = bool(vgr.kind == uj.vg.DIFF or neg)
    ok, label = _classify(canonical, text)
    return Voter(provider=provider, text=text, passed=bool(ok and not pdiff and not rescued), label=label, protected_diff=pdiff, rescued=rescued)


# ============================================================
# ローカルWhisper(faster-whisper small int8、Production既存loaderを共有。API 0 / 費用0)
# ============================================================
def whisper_transcribe(wav_path: str, *, model_size: str = WHISPER_MODEL_SIZE, timeout: float = WHISPER_TIMEOUT_SEC) -> str:
    """既存`er008_disfluency_qa_18.transcribe_verbatim`(word timestamps付きverbatim)と同一設定で転写する。timeout/例外は呼出側で
    NG_WHISPER_UNAVAILABLEへ変換される(ここでは握りつぶさず送出)。"""
    import er008_disfluency_qa_18 as dq

    def _run():
        words = dq.transcribe_verbatim(wav_path, language="en", model_size=model_size)
        return " ".join("".join(w["text"] for w in words).split())

    ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        return ex.submit(_run).result(timeout=timeout)
    finally:
        ex.shutdown(wait=False, cancel_futures=True)


def make_whisper_fn(canonical: str, wav_path: str, *, transcribe_fn: Callable[[str], str] = whisper_transcribe) -> Callable[[], Voter]:
    def _fn() -> Voter:
        text = transcribe_fn(wav_path)
        return make_voter("whisper", canonical, text)
    return _fn


# ============================================================
# 証跡 kp_vote_check(Store entry / results entryに保存。旧kp_dual_check_v1の後継)
# ============================================================
def _sha256_file(path: str) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def vote_check_from_decision(d: VoteDecision, wav_path: str, canonical_text: str, *, source: str) -> dict:
    return {"version": CHECK_VERSION, "ok": bool(d.verified), "source": source, "canonical_text": canonical_text,
            "wav_sha256": _sha256_file(wav_path), "judge_state": d.state, "reason_code": d.reason, "pass_count": d.pass_count,
            "primary": {"provider": "openai", "text": d.primary.text, "pass": d.primary.passed, "rescued": d.primary.rescued},
            "secondary": ({"provider": "azure", "text": d.secondary.text, "pass": d.secondary.passed, "called": d.secondary_called}
                          if d.secondary else None),
            "whisper": ({"provider": "faster_whisper", "model": WHISPER_MODEL_SIZE, "text": d.whisper.text, "pass": d.whisper.passed,
                         "called": d.whisper_called, "error": d.whisper.error} if d.whisper else {"called": False}),
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S")}


def rejudge_stored(check: dict, wav_path: str, canonical_text: str, *,
                   whisper_fn: Optional[Callable[[], Voter]]) -> Optional[VoteDecision]:
    """Store/results再利用時の再判定(Azure再呼出なし・API 0)。`check`は旧`kp_dual_check_v1`でも新`kp_vote_check_v1`でもよい
    (primary.text / secondary.text を読むだけ)。canonical/wav sha256が現物と一致しない・転写が欠けるなら None(呼出側はS1/再生成=fail-closed)。
    Whisper転写が保存済み(同sha)ならそれを再利用、無ければwhisper_fn(ローカル)を呼ぶ。"""
    if not isinstance(check, dict) or check.get("canonical_text") != canonical_text:
        return None
    if check.get("wav_sha256") != _sha256_file(wav_path):
        return None
    pri = check.get("primary") or {}
    pri_t = pri.get("text")
    sec_t = (check.get("secondary") or {}).get("text")
    if not pri_t or not (sec_t and str(sec_t).strip()):
        return None
    primary = make_voter("openai", canonical_text, pri_t, rescued=bool(pri.get("rescued") or pri.get("rescued_by_secondary")))
    stored_w = (check.get("whisper") or {}).get("text") if check.get("version") == CHECK_VERSION else None
    wfn = (lambda: make_voter("whisper", canonical_text, stored_w)) if stored_w else whisper_fn
    return decide(primary, lambda: make_voter("azure", canonical_text, sec_t), wfn)
