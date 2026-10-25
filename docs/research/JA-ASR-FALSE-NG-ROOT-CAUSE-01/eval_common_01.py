# API 0 評価の共通部。Productionの adapter (`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`) を
# そのまま呼び、Primary層 `_numeric_value_equivalence` だけを in-process で v1 に差し替える(Production fileは変更しない)。
# Secondary(Azure)は stub (呼出0)。socket接続はAPI0違反として例外にする。
import os, socket, sys, tempfile, wave
sys.path.insert(0, ".")
sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import er007_ja_asr_validator_01 as javal
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False   # LLM(Resolver)を呼ばない = API 0
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import proto_reading_compare_01 as P

_real_connect = socket.socket.connect


def _no_net(self, *a, **k):
    raise RuntimeError("API0 violation: network connect attempted")


def api0_guard_on():
    socket.socket.connect = _no_net


def api0_guard_off():
    socket.socket.connect = _real_connect


_WAV = None


def dummy_wav():
    global _WAV
    if _WAV is None:
        _WAV = os.path.join(tempfile.gettempdir(), "ja_asr_v1_eval_dummy.wav")
        w = wave.open(_WAV, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 16000 * 3); w.close()
    return _WAV


_ORIG_NUM = sec._numeric_value_equivalence
_CTX = {"er": None, "last": None}


def _v1_layer(canonical_text, asr_text, cls):
    r = P.pron_value_equivalence(canonical_text, asr_text, cls=cls, expected_readings=_CTX["er"])
    _CTX["last"] = r
    if r.equal:
        return P.to_classification(r, cls)
    return None


def primary_stage(canon, asr, candidate, expected_readings=None):
    """Primary転写1本をProduction adapterに通す(Secondaryは呼ばない stub)。candidate=Trueで v1 層に差替。
    戻り: dict(state, reason, label, warnings, primary_pass)"""
    _CTX["er"], _CTX["last"] = expected_readings, None
    orig_az = sec._azure_stt_strict
    sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_call")
    sec._numeric_value_equivalence = _v1_layer if candidate else _ORIG_NUM
    try:
        r = sec.evaluate_attempt_ja_with_cascade_detail(
            canon, asr, dummy_wav(), cascade_enabled=True, expected_readings=expected_readings,
            attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig_az
        sec._numeric_value_equivalence = _ORIG_NUM
    j = r["asr_judgement"]
    state = j.get("state")
    steps = r.get("steps") or []
    label = r["classification"].classification if r.get("classification") is not None else None
    v1 = _CTX["last"] if candidate else None
    warns = list(j.get("warnings") or [])
    if candidate and v1 is not None and v1.equal and state in uj.PASSING_STATES:
        warns = list(dict.fromkeys(warns + list(v1.warnings)))   # 配線時はadapterが付与する想定のwarning(R2)
    return {"state": state, "reason": j.get("reason_code"), "label": label, "warnings": warns,
            "primary_pass": state in uj.PASSING_STATES and not any(s.get("provider") == "azure" for s in steps),
            "v1": v1}


def secondary_accept_kind(canon, stext, expected_readings=None):
    """Secondary(Azure)転写に対する受理。現行=EXACT/NORMALIZED。A4(a)=値のみ一致、A4(b)=発音一致(新仕様候補)。
    戻り: (baseline_accept: bool, a4a: bool, a4b: bool, v1result)"""
    cls_s = javal.classify_ja_asr_match(canon, stext, expected_readings=expected_readings, allow_reading_resolver=False)
    base = cls_s.classification in sec.SCG_PASS_CLASSIFICATIONS
    if base or stext is None:
        return base, False, False, None
    r = P.pron_value_equivalence(canon, stext, cls=cls_s, expected_readings=expected_readings)
    return base, bool(r.equal and r.kind == "VALUE_ONLY"), bool(r.equal and r.kind == "PRON"), r
