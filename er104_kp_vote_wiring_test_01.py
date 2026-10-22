# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02: KP英語phrase「3-ASR多数決(OpenAI・Azure・Whisper、2/3 PASS)」のFamily X/Z Production配線test(API 0・費用JPY0)。
# 実行: .venv/Scripts/python.exe -m pytest er104_kp_vote_wiring_test_01.py -q
# 全てmock(Primary=routing.transcribe / Secondary=get_full_text_via_azure_stt_with_phrase_list / Whisper=kp3v.whisper_transcribe / TTS=p9a)。
# HR queue・Lock・Storeの書込先は全てtmp_pathへ退避。旧er096_kp_dual_pass_01_wiring_test_01(両方PASS必須)の後継(旧testは履歴として残置・Production importなしをAST固定)。
# 構成: A 判定層(unified_judge vote_required) / B adapter層(本番adapter経路) / C strict+KP 4回構成 / D 6呼出点(AST)・旧識別子撤去・Production import境界 /
#       E 再利用6点・Store gate・本番adapter再判定(P-01) / F P-08(Whisper障害・circuit・preflight) / G take part型 / H 組立監査
import ast
import itertools
import json
import os
import re
import subprocess
import wave

import numpy as np
import pytest

import er006_asr_provider_routing_01 as routing  # noqa: F401
import er006_master_audio_store_01 as store
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er011_human_review_lock_01 as review_lock
import er078_asr_unified_attempt_ctx_01 as actx_mod
import er078_asr_unified_judge_01 as uj
import er104_kp_three_asr_vote_01 as kp3v
import er104_kp_vote_reuse_01 as kv

ROOT = os.path.dirname(os.path.abspath(__file__))
CANON = "take part"


class Az:
    """Secondary(Azure)のmock。callsは実呼出回数。"""

    def __init__(self, result=("Take part.", None), raises=None, seq=None):
        self.result, self.raises, self.calls, self.seq = result, raises, 0, seq

    def __call__(self, wav_path, language="en-US", phrases=None, **kw):
        self.calls += 1
        if self.raises:
            raise self.raises
        if self.seq:
            return self.seq[min(self.calls - 1, len(self.seq) - 1)]
        return self.result


class Wh:
    """Whisper票のmock(judge層/adapter層用callable)。textを分類してVoterを返す。callsは呼出回数。exc指定で例外。"""

    def __init__(self, text="Take part.", exc=None, canon=CANON, max_len=None):
        self.text, self.exc, self.calls, self.canon, self.max_len = text, exc, 0, canon, max_len

    def __call__(self):
        self.calls += 1
        if self.exc:
            raise self.exc
        return kp3v.make_voter("whisper", self.canon, self.text, max_len=self.max_len, ambiguous_blocks=True)


def _wav(path, seconds=1, rate=8000):
    os.makedirs(os.path.dirname(str(path)) or ".", exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(b"\x00" * (rate * seconds))
    return str(path)


@pytest.fixture(autouse=True)
def _iso(monkeypatch, tmp_path):
    sec.reset_secondary_cache()
    sec._reset_m1_freeze_cache()
    kp3v.reset_whisper_state()
    kv.reset_preflight()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda *a, **k: {})
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda *a, **k: None)
    monkeypatch.setattr(sec.semantic_equivalence, "append_telemetry_log", lambda *a, **k: None)
    monkeypatch.setattr(sec, "HUMAN_REVIEW_LOG_PATH", str(tmp_path / "hrq_en.jsonl"))
    monkeypatch.setattr(review_lock, "save_tts_attempt_audio", lambda *a, **k: "saved.wav")
    monkeypatch.setattr(review_lock, "append_attempt_history_event", lambda *a, **k: None)
    monkeypatch.setattr(review_lock, "ATTEMPT_HISTORY_PATH", str(tmp_path / "attempt_history.jsonl"))
    import er003_v1_repro01_main_generate as r1
    monkeypatch.setattr(r1.pronun_ledger, "get_hint_for_text", lambda *a, **k: [])
    monkeypatch.setattr(store, "STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setattr(store, "AUDIO_DIR", str(tmp_path / "store" / "audio"))
    monkeypatch.setattr(store, "MANIFEST_PATH", str(tmp_path / "store" / "manifest.json"))
    monkeypatch.setattr(store, "TELEMETRY_PATH", str(tmp_path / "store" / "telemetry.jsonl"))
    # 事前確認は実モデルをロードしない(unit): ok固定。F章で個別に上書きする
    monkeypatch.setattr(kp3v, "whisper_preflight", lambda **k: {"model": "small", "compute_type": "int8", "device": "cpu", "ok": True,
                                                                "error": None, "model_cache_present": True, "load_sec": 0.0})
    yield
    sec.reset_secondary_cache()
    kp3v.reset_whisper_state()
    kv.reset_preflight()


# ============================================================
# A. 判定層(unified_judge, vote_required)
# ============================================================
def _accept(canon, stext):
    r = val.classify_asr_match(canon, stext)
    return bool(r.should_pass), r.classification


def _judge(primary_text, primary_pass, sec_text, *, canon=CANON, vote=True, sec_exc=None, signals=None, lang="en", whisper=None, **ctxkw):
    calls = {"n": 0}

    def sec_fn(_c):
        calls["n"] += 1
        if sec_exc:
            raise sec_exc
        return sec_text

    ctx = uj.AttemptCtx(canonical_text=canon, wav_sha256=f"sha-{primary_text}-{sec_text}-{vote}-{id(whisper)}", audio_seconds=1.7,
                        segment_key="kp1_en", vote_required=vote, whisper_fn=whisper, **ctxkw)
    jr = uj.unified_judge(ctx, uj.PrimaryResult(passed=primary_pass, text=primary_text, signals=signals or {}), sec_fn,
                          lang=lang, role="KP_EN", secondary_accept_fn=_accept)
    return jr, calls["n"]


def test_dual_identifiers_are_gone_from_judge():
    assert not hasattr(uj, "NG_DUAL_PRIMARY_NOT_PASS")
    assert "dual_required" not in {f for f in uj.AttemptCtx.__dataclass_fields__}
    assert "vote_required" in uj.AttemptCtx.__dataclass_fields__
    assert uj.NG_WHISPER_UNAVAILABLE in uj.STATES and uj.NG_WHISPER_UNAVAILABLE not in uj.PASSING_STATES
    assert set(uj.TECHNICAL_STOP_STATES) == {uj.NG_SECONDARY_UNAVAILABLE, uj.NG_WHISPER_UNAVAILABLE}


def test_row1_both_pass_is_PASS_no_whisper_and_audit_complete():
    wh = Wh()
    jr, n = _judge("Take part.", True, "Take part.", whisper=wh)
    assert jr.state == uj.PASS and n == 1 and jr.reason_code == "dual_agreed" and wh.calls == 0
    v = jr.audit_record["vote"]
    assert v["required"] and v["state"] == kp3v.PASS_DUAL and v["row"] == "P+S" and v["pass_count"] == 2
    assert v["primary"]["pass"] and v["secondary"]["pass"] and v["whisper"] is None and v["whisper_called"] is False


def test_row2_primary_pass_secondary_ng_whisper_pass_is_PASS_think_up_type():
    wh = Wh("Take part.")
    jr, n = _judge("Take part.", True, "Take Tart.", whisper=wh)
    assert jr.state == uj.PASS and jr.verified and wh.calls == 1 and n == 1       # 警告なしのPASS(P-03: 行2はPASS)
    v = jr.audit_record["vote"]
    assert v["state"] == kp3v.PASS_VOTE_2OF3 and v["row"] == "P+W" and v["whisper_called"] and v["pass_count"] == 2
    assert uj.W_SECONDARY_CONFIRMED not in jr.warning_labels
    assert v["whisper_model"] == {"model": "small", "compute_type": "int8", "device": "cpu", "library": "faster_whisper"}


def test_row3_primary_pass_secondary_ng_whisper_ng_is_NG():
    wh = Wh("Take Tarte.")
    jr, n = _judge("Take part.", True, "Take Tart.", whisper=wh)
    assert (jr.state, wh.calls) == (uj.NG_BOTH, 1) and not jr.verified
    assert jr.audit_record["vote"]["state"] == kp3v.NG_VOTE_WHISPER_NG and jr.reason_code == "whisper_ng_1of3"


def test_row4_primary_ng_secondary_pass_whisper_pass_is_PASS_WITH_WARNING_secondary_confirmed_blurt_type():
    wh = Wh("Take part.")
    jr, n = _judge("Take tart.", False, "Take part.", whisper=wh)
    assert jr.state == uj.PASS_WITH_WARNING and jr.verified and wh.calls == 1       # P-03: 事後試聴リスト対象
    assert uj.W_SECONDARY_CONFIRMED in jr.warning_labels
    v = jr.audit_record["vote"]
    assert v["state"] == kp3v.PASS_VOTE_2OF3 and v["row"] == "S+W" and v["primary"]["pass"] is False


def test_row5_primary_ng_secondary_pass_whisper_ng_is_NG_no_NG_DUAL_PRIMARY_NOT_PASS():
    wh = Wh("Take Tarte.")
    jr, n = _judge("Take tart.", False, "Take part.", whisper=wh)
    assert (jr.state, wh.calls) == (uj.NG_BOTH, 1) and not jr.verified


def test_row6_both_ng_no_whisper_call():
    wh = Wh("Take part.")
    jr, n = _judge("Take tart.", False, "Take Tart.", whisper=wh)
    assert (jr.state, n, wh.calls) == (uj.NG_BOTH, 1, 0) and jr.reason_code == "secondary_not_accepted"


def test_P05_lifted_primary_ng_with_protected_diff_no_short_circuit_calls_secondary_and_whisper():
    """2026-10-22保護解除(OF-KPQ): KPではPrimary NG+保護差でもP1短絡せずSecondaryを呼び、S PASS+W PASSなら行4(S+W、PASS_WITH_WARNING)。"""
    wh = Wh("I have 5 cats.", canon="I have 5 cats")
    jr, n = _judge("I have 3 cats", False, "I have 5 cats", canon="I have 5 cats", whisper=wh)
    assert n == 1 and wh.calls == 1 and jr.state == uj.PASS_WITH_WARNING and uj.W_SECONDARY_CONFIRMED in jr.warning_labels
    v = jr.audit_record["vote"]
    assert v["row"] == "S+W" and v["guard_lifted"] is True and v["observed_protected_diff"]["primary"] is True


def test_P05_non_kp_keeps_p1_short_circuit_no_azure_no_whisper():
    """非KP(vote_required=False)のP1短絡(NG_PROTECTED)は不変。"""
    jr, n = _judge("I have 3 cats", False, "I have 5 cats", canon="I have 5 cats", vote=False)
    assert jr.state == uj.NG_PROTECTED and n == 0


def test_lifted_primary_pass_with_value_diff_final_gate_skipped_but_recorded():
    """Primary PASS(分類器PASS扱い)+観測保護差: 最終ANDゲートでNG_PROTECTEDにせず票として扱う(記録のみ)。非KPは従来どおりNG_PROTECTED。"""
    wh = Wh("I have 5 cats.", canon="I have 5 cats")
    jr, n = _judge("I have 3 cats.", True, "I have 5 cats.", canon="I have 5 cats", whisper=wh)
    assert jr.state == uj.PASS and wh.calls == 0 and jr.audit_record["vote"]["observed_protected_diff"]["primary"] is True
    jr2, _ = _judge("I have 3 cats.", True, "I have 5 cats.", canon="I have 5 cats", vote=False)
    assert jr2.state == uj.NG_PROTECTED


def test_dissent_secondary_protected_diff_no_longer_blocks_2of3_lifted():
    """2026-10-22保護解除(P-07(b)置換): 反対票側(Secondary)が別の数を言っていてもWhisperを呼び、P PASS+W PASSなら2/3でPASS(行2、P+W)。"""
    wh = Wh("I have 5 cats.", canon="I have 5 cats")
    jr, n = _judge("I have 5 cats.", True, "I have 3 cats.", canon="I have 5 cats", whisper=wh)
    assert jr.verified and wh.calls == 1 and jr.audit_record["vote"]["row"] == "P+W"
    assert jr.audit_record["vote"]["observed_protected_diff"]["secondary"] is True


def test_lifted_dissent_with_whisper_ng_is_ng():
    wh = Wh("I have 3 cats.", canon="I have 5 cats")
    jr, n = _judge("I have 5 cats.", True, "I have 3 cats.", canon="I have 5 cats", whisper=wh)
    assert (not jr.verified) and wh.calls == 1 and jr.audit_record["vote"]["state"] == kp3v.NG_VOTE_WHISPER_NG


def test_lifted_both_ng_with_protected_diff_no_whisper():
    wh = Wh("I have 5 cats.", canon="I have 5 cats")
    jr, n = _judge("I have 3 cats.", False, "I have 3 cats.", canon="I have 5 cats", whisper=wh)
    assert (not jr.verified) and wh.calls == 0 and jr.audit_record["vote"]["state"] == kp3v.NG_BOTH


def test_P06_lifted_p1_skip_now_evaluates_p2_exclusion():
    """OF-KPQ-P-06: P1を外すとP2除外(A3 length NGなど)が評価される。除外は数値・否定の保護ではないため維持される。"""
    wh = Wh("I have 5 cats.", canon="I have 5 cats")
    jr, n = _judge("I have 3 cats.", False, "I have 5 cats.", canon="I have 5 cats", whisper=wh,
                   length_ok=False)
    assert jr.state == uj.NG_EXCLUDED and n == 0 and wh.calls == 0 and jr.reason_code.startswith("p2_exclusion:")


@pytest.mark.parametrize("exc,text", [(RuntimeError("timeout"), "x"), (None, ""), (None, None)])
def test_azure_failure_or_empty_is_technical_stop_no_2of3_downgrade_P07a(exc, text):
    wh = Wh("Take part.")
    jr, n = _judge("Take part.", True, text, sec_exc=exc, whisper=wh)
    assert not jr.verified and jr.state == uj.NG_SECONDARY_UNAVAILABLE and jr.secondary_unavailable
    assert wh.calls == 0                                                       # Whisperで救済しない(Primary+Whisperの2/3へ降格しない)


def test_circuit_open_is_not_primary_only_pass_and_azure_not_called():
    rs = uj.RunState()
    rs.circuit_open = True
    wh = Wh()
    jr, n = _judge("Take part.", True, "Take part.", run_state=rs, whisper=wh)
    assert (jr.state, n, wh.calls) == (uj.NG_SECONDARY_UNAVAILABLE, 0, 0)


@pytest.mark.parametrize("layers", [["non_latin"], ["tier3"], ["cs_equivalence"]])
def test_P06_rescued_primary_counts_as_NG_vote_whisper_decides(layers):
    pr_signals = {"primary_rescued_by_secondary": True, "primary_rescue_layers": layers}
    for w_text, expect in (("Take part.", uj.PASS_WITH_WARNING), ("Take Tarte.", uj.NG_BOTH)):
        wh = Wh(w_text)
        ctx = uj.AttemptCtx(canonical_text=CANON, wav_sha256="sha-r-" + layers[0] + w_text, audio_seconds=1.7, vote_required=True, whisper_fn=wh)
        pr = uj.PrimaryResult(passed=True, text="テイクパート", adopted_text="Take part.", signals=pr_signals)
        jr = uj.unified_judge(ctx, pr, lambda c: "Take part.", lang="en", role="KP_EN", secondary_accept_fn=_accept)
        assert jr.state == expect and wh.calls == 1
        v = jr.audit_record["vote"]
        assert v["primary_rescued_by_secondary"] is True and v["primary"]["rescue_layers"] == layers and v["primary"]["pass"] is False


def test_rescue_flag_is_ignored_without_vote_required():
    ctx = uj.AttemptCtx(canonical_text=CANON, wav_sha256="sha-r-novote", audio_seconds=1.7)
    pr = uj.PrimaryResult(passed=True, text="テイクパート", adopted_text="Take part.", signals={"primary_rescued_by_secondary": True})
    jr = uj.unified_judge(ctx, pr, lambda c: (_ for _ in ()).throw(AssertionError("no secondary")), lang="en", role="KP_EN",
                          secondary_accept_fn=_accept)
    assert jr.state == uj.PASS and "vote" not in jr.audit_record


def test_P12_primary_length_demotion_is_NG_vote_and_whisper_length_also_applies_P02():
    # Primaryが長すぎ(降格) -> P NG票。Secondary PASS -> Whisper決定。Whisperの転写も長ければNG票(max_lenはctxと同じ値)
    ml = len(CANON) + 10
    wh_ok = Wh("Take part.", max_len=ml)
    jr, n = _judge("Take part with extra long chatter here.", True, "Take part.", max_len=ml, whisper=wh_ok)
    assert jr.state == uj.PASS_WITH_WARNING and uj.W_SECONDARY_CONFIRMED in jr.warning_labels and wh_ok.calls == 1
    wh_long = Wh("Take part with extra long chatter here.", max_len=ml)
    jr2, n2 = _judge("Take part with extra long chatter here.", True, "Take part.", max_len=ml, whisper=wh_long)
    assert jr2.state == uj.NG_BOTH and wh_long.calls == 1 and jr2.audit_record["vote"]["whisper"]["pass"] is False


def test_P12_ambiguous_value_demotion_is_NG_vote():
    wh = Wh("十分待ってください", canon="十分待ってください")
    jr, n = _judge("10分待ってください", True, "十分待ってください", canon="十分待ってください", lang="ja", whisper=wh)
    assert jr.audit_record["vote"]["primary"]["pass"] is False


def test_vote_false_is_byte_identical_flow():
    for p_text, p_pass, s_text in [("Take part.", True, "x"), ("Take tart.", False, "Take part."), ("Take tart.", False, "Take Tart.")]:
        jr, _ = _judge(p_text, p_pass, s_text, vote=False)
        assert "vote" not in jr.audit_record and "dual" not in jr.audit_record


def test_u2_force_secondary_unchanged_with_vote_false():
    jr, n = _judge("Take tart.", False, "Take part.", vote=False, force_secondary=True)
    assert jr.verified and jr.state == uj.PASS_WITH_WARNING


def test_whisper_not_configured_on_split_is_technical_stop_not_pass():
    jr, n = _judge("Take part.", True, "Take Tart.", whisper=None)
    assert jr.state == uj.NG_WHISPER_UNAVAILABLE and not jr.verified
    assert jr.audit_record["technical_stop"]["type"] == "WHISPER_UNAVAILABLE"


def test_whisper_exception_is_technical_stop_and_recorded_in_run_state():
    rs = uj.RunState()
    wh = Wh(exc=RuntimeError("model load failed"))
    jr, n = _judge("Take part.", True, "Take Tart.", whisper=wh, run_state=rs)
    assert jr.state == uj.NG_WHISPER_UNAVAILABLE and not jr.verified
    assert rs.technical_stop_events and rs.technical_stop_events[-1]["type"] == "WHISPER_UNAVAILABLE"
    assert jr.audit_record["vote"]["state"] == kp3v.NG_WHISPER_UNAVAILABLE


def test_whisper_empty_transcript_is_ng_vote_not_technical_stop():
    wh = Wh("")
    jr, n = _judge("Take part.", True, "Take Tart.", whisper=wh)
    assert jr.state == uj.NG_BOTH and jr.reason_code == "whisper_empty_transcript_ng_vote" and "technical_stop" not in jr.audit_record or \
        not jr.audit_record.get("technical_stop")


def test_tiebreak_off_equals_old_dual_rule_and_never_calls_whisper(monkeypatch):
    monkeypatch.setattr(kp3v, "KP_WHISPER_TIEBREAK_ENABLED", False)
    for p_text, p_pass, s_text, expect in [("Take part.", True, "Take part.", True), ("Take part.", True, "Take Tart.", False),
                                           ("Take tart.", False, "Take part.", False), ("Take tart.", False, "Take Tart.", False)]:
        wh = Wh("Take part.")
        jr, _ = _judge(p_text, p_pass, s_text, whisper=wh)
        assert jr.verified is expect and wh.calls == 0, (p_text, s_text)
    jr, _ = _judge("Take part.", True, "Take Tart.", whisper=Wh())
    assert jr.audit_record["vote"]["state"] == kp3v.NG_SPLIT_TIEBREAK_OFF and jr.state == uj.NG_BOTH


@pytest.mark.parametrize("tiebreak", [True, False])
def test_P09_judge_and_decide_agree_on_all_combinations(monkeypatch, tiebreak):
    """判定ロジックの二重実装なし: judge(done出口)とdecide()が同じtally()で、全組合せの結果・Whisper呼出回数が一致する。"""
    monkeypatch.setattr(kp3v, "KP_WHISPER_TIEBREAK_ENABLED", tiebreak)
    canon = "I have 5 cats"
    P = {"pass": ("I have 5 cats.", True), "ng": ("I have 5 hats.", False), "p1": ("I have 3 cats.", False)}
    S = {"pass": "I have 5 cats.", "ng": "I have 5 hats.", "prot": "I have 3 cats.", "none": ""}
    W = {"pass": "I have 5 cats.", "ng": "I have 5 hats.", "empty": "", "boom": None}
    n_checked = 0
    for (pk, (pt, pp)), (sk, st), (wk, wt) in itertools.product(P.items(), S.items(), W.items()):
        wh = Wh(wt, exc=(RuntimeError("x") if wk == "boom" else None), canon=canon)
        jr, _ = _judge(pt, pp, st, canon=canon, whisper=wh)
        # decide()側は同じ分類器でVoterを作る(judgeのPrimary passedは呼出側の入力pp、Secondaryは_accept+保護ガード)
        pv = kp3v.make_voter("openai", canon, pt)
        pv.passed = bool(pp)
        sv = kp3v.make_voter("azure", canon, st) if st else kp3v.Voter("azure", st, False, available=False)
        wh2 = Wh(wt, exc=(RuntimeError("x") if wk == "boom" else None), canon=canon)
        d = kp3v.decide(pv, lambda sv=sv: sv, wh2)
        assert jr.audit_record["vote"]["state"] == d.state or jr.state == uj.NG_SECONDARY_UNAVAILABLE \
            and d.state == kp3v.NG_SECONDARY_UNAVAILABLE, (pk, sk, wk, jr.state, jr.audit_record["vote"], d.state)
        assert jr.verified == d.verified, (pk, sk, wk)
        assert wh.calls == wh2.calls, (pk, sk, wk, wh.calls, wh2.calls)
        n_checked += 1
    assert n_checked == 3 * 4 * 4


# ============================================================
# B. adapter層(evaluate_attempt_with_cascade_detail = 本番adapter経路)
# ============================================================
def _adapter(tmp_path, canon, primary_text, az, monkeypatch, *, vote=True, is_last=False, rs=None, cascade=True, whisper_text=None,
             whisper_fn=None, **kw):
    wav = _wav(tmp_path / f"w_{abs(hash((canon, primary_text, str(az.result), whisper_text)))}.wav")
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    ctx = {"slot": 4 if is_last else 1, "is_last_slot": is_last, "script_version": "v0", "max_len": len(canon) + 10}
    if vote:
        ctx["vote_required"] = True
        if whisper_fn is not None:
            ctx["vote_whisper_fn"] = whisper_fn
        elif whisper_text is not None:
            ctx["vote_whisper_fn"] = lambda: kp3v.whisper_vote(canon, wav, sha=sec._wav_sha256(wav), max_len=len(canon) + 10,
                                                               stored_text=whisper_text)
    if rs is not None:
        ctx["run_state"] = rs
    return sec.evaluate_attempt_with_cascade_detail(
        canon, primary_text, [], wav, language="en-US", ledger_phrases=[], cascade_enabled=cascade,
        enable_non_latin_cascade=True, attempt_ctx=ctx, **kw)


def test_adapter_both_pass(tmp_path, monkeypatch):
    az = Az(("Take part.", None))
    d = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch)
    aj = d["asr_judgement"]
    assert d["verified"] and az.calls == 1 and aj["state"] == uj.PASS and aj["vote"]["required"] is True
    assert [s["step"] for s in d["steps"]] == ["primary_1", "secondary_vote"] and d["steps"][1]["vote_required"] is True
    assert d["classification"].classification == "NORMALIZED_MATCH"       # 行1: classificationをSecondary側で上書きしない
    assert aj["adapter"]["azure_real_calls"] == 1 and d["vote_state"] == uj.PASS


def test_adapter_think_up_type_row2_keeps_primary_classification_and_logs_whisper_step(tmp_path, monkeypatch):
    az = Az(("Take Tart.", None))
    d = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch, whisper_text="Take part.")
    aj = d["asr_judgement"]
    assert d["verified"] and aj["state"] == uj.PASS and aj["vote"]["row"] == "P+W"
    assert [s["step"] for s in d["steps"]] == ["primary_1", "secondary_vote", "whisper_vote"]
    assert d["steps"][2]["provider"] == "faster_whisper" and d["steps"][2]["pass"] is True and d["steps"][2]["model"] == "small"
    assert d["classification"].classification == "NORMALIZED_MATCH"       # P-03: 行2はPrimaryの根拠を保持


def test_adapter_blurt_type_row4_uses_secondary_classification_with_confirmed_warning(tmp_path, monkeypatch):
    az = Az(("Take part.", None))
    d = _adapter(tmp_path, CANON, "Take Tart.", az, monkeypatch, whisper_text="Take part.")
    aj = d["asr_judgement"]
    assert d["verified"] and aj["state"] == uj.PASS_WITH_WARNING and aj["vote"]["row"] == "S+W"
    assert uj.W_SECONDARY_CONFIRMED in aj["warnings"]
    assert d["classification"].classification != "TRUE_CONTENT_MISMATCH"   # P-03: 行4はSecondaryの分類(合格根拠)を採る


def test_adapter_take_part_type_primary_pass_azure_ng_whisper_ng_rejected(tmp_path, monkeypatch):
    az = Az(("Take Tart.", None))
    d = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch, whisper_text="Take Tarte.")
    assert not d["verified"] and az.calls == 1 and d["asr_judgement"]["state"] == uj.NG_BOTH
    assert d["asr_judgement"]["vote"]["state"] == kp3v.NG_VOTE_WHISPER_NG


def test_adapter_default_whisper_fn_uses_local_whisper_with_wav_sha_memo(tmp_path, monkeypatch):
    n = []
    monkeypatch.setattr(kp3v, "whisper_transcribe", lambda p, **k: n.append(p) or "Take part.")
    az = Az(("Take Tart.", None))
    d = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch)             # vote_whisper_fn未指定 = 既定の本番Whisper経路
    assert d["verified"] and len(n) == 1 and d["asr_judgement"]["vote"]["whisper"]["memo_hit"] is False
    d2 = sec.evaluate_attempt_with_cascade_detail(CANON, "Take part.", [], d["wav_path"], language="en-US", ledger_phrases=[],
                                                  cascade_enabled=True, enable_non_latin_cascade=True,
                                                  attempt_ctx={"slot": 1, "vote_required": True, "max_len": len(CANON) + 10})
    assert d2["verified"] and len(n) == 1 and d2["asr_judgement"]["vote"]["whisper"]["memo_hit"] is True   # 同一wavは再転写しない


def test_adapter_non_latin_rescue_is_NG_vote_whisper_can_decide_other_roles_unchanged(tmp_path, monkeypatch):
    az = Az(("Take part.", None))
    d = _adapter(tmp_path, CANON, "テイクパート", az, monkeypatch, whisper_text="Take Tarte.")
    aj = d["asr_judgement"]
    assert not d["verified"] and aj["vote"]["primary_rescued_by_secondary"] is True and aj["vote"]["primary"]["rescue_layers"] == ["non_latin"]
    assert az.calls == 1
    az2 = Az(("Take part.", None))
    d2 = _adapter(tmp_path, CANON, "テイクパート", az2, monkeypatch, vote=False)
    assert d2["verified"] and d2["asr_judgement"]["state"] == uj.PASS_WITH_WARNING and "vote" not in d2["asr_judgement"]


def test_adapter_azure_failure_is_technical_stop_not_primary_only_pass(tmp_path, monkeypatch):
    for az in (Az(raises=RuntimeError("timeout")), Az((None, "no result")), Az(("", None))):
        d = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch, is_last=True, whisper_text="Take part.")
        assert not d["verified"] and d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE
        assert d["technical_stop_status"] == "TECHNICAL_STOP_SECONDARY_UNAVAILABLE" and d["human_review_required"] is False


def test_adapter_whisper_failure_is_technical_stop_hr_not_entered(tmp_path, monkeypatch):
    az = Az(("Take Tart.", None))
    d = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch, is_last=True, whisper_fn=Wh(exc=ImportError("no faster_whisper")))
    assert not d["verified"] and d["asr_judgement"]["state"] == uj.NG_WHISPER_UNAVAILABLE
    assert d["technical_stop_status"] == "TECHNICAL_STOP_WHISPER_UNAVAILABLE" and d["human_review_required"] is False
    assert d["technical_stop"]["type"] == "WHISPER_UNAVAILABLE"


def test_adapter_circuit_breaker_opens_after_three_failures_and_stops_calling_azure(tmp_path, monkeypatch):
    rs = uj.RunState()
    az = Az(raises=RuntimeError("down"))
    for i in range(4):
        d = _adapter(tmp_path, f"take part {i}", f"Take part {i}.", az, monkeypatch, rs=rs)
        assert not d["verified"]
    assert rs.circuit_open and az.calls == 3


def test_adapter_cascade_disabled_with_vote_is_fail_closed(tmp_path, monkeypatch):
    az = Az(("Take part.", None))
    d = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch, cascade=False)
    assert d["verified"] is False and az.calls == 0 and d["technical_stop"]["type"] == "VOTE_REQUIRED_BUT_CASCADE_DISABLED"
    d2 = _adapter(tmp_path, CANON, "Take part.", az, monkeypatch, cascade=False, vote=False)
    assert d2["verified"] is True


def test_adapter_last_slot_vote_ng_goes_to_hr_queue_technical_stops_do_not(tmp_path, monkeypatch):
    d = _adapter(tmp_path, CANON, "Take Tart.", Az(("Take part.", None)), monkeypatch, is_last=True, whisper_text="Take Tarte.")
    assert d["human_review_required"] is True and d["asr_judgement"]["state"] == uj.NG_BOTH
    d2 = _adapter(tmp_path, CANON, "Take part.", Az(raises=RuntimeError("down")), monkeypatch, is_last=True)
    assert d2["human_review_required"] is False
    d3 = _adapter(tmp_path, CANON, "Take part.", Az(("Take part.", None)), monkeypatch, is_last=True)
    assert d3["verified"] and d3["human_review_required"] is False


def test_adapter_homophone_rescue_applies_to_each_provider_separately(tmp_path, monkeypatch):
    canon = "Try byUs now."
    d = _adapter(tmp_path, canon, "Try buy us now.", Az(("Try buy us now.", None)), monkeypatch)
    assert d["verified"] and d["asr_judgement"]["state"] in (uj.PASS, uj.PASS_WITH_WARNING)
    assert d["asr_judgement"]["vote"]["secondary"]["pass"] and d["asr_judgement"]["vote"]["primary"]["pass"]
    d2 = _adapter(tmp_path, canon, "Try buy us now.", Az(("Try cat now.", None)), monkeypatch, whisper_text="Try cat now.")
    assert not d2["verified"] and d2["asr_judgement"]["vote"]["primary"]["pass"] and not d2["asr_judgement"]["vote"]["secondary"]["pass"]
    d3 = _adapter(tmp_path, canon, "Try cat now.", Az(("Try buy us now.", None)), monkeypatch, whisper_text="Try cat now.")
    assert not d3["verified"]


def test_adapter_non_vote_default_paths_have_no_new_keys(tmp_path, monkeypatch):
    d = _adapter(tmp_path, CANON, "Take part.", Az(("Take Tart.", None)), monkeypatch, vote=False)
    assert d["verified"] and "vote_state" not in d and "vote" not in d["asr_judgement"]
    assert all("vote_required" not in s for s in d["steps"])


def test_attempt_ctx_adds_key_only_when_vote():
    assert "vote_required" not in actx_mod.build_attempt_ctx(1, 2, slot_offset=0, total_slots=4)
    assert actx_mod.build_attempt_ctx(1, 2, slot_offset=0, total_slots=4, vote_required=True)["vote_required"] is True


# ============================================================
# C. strict + KP 4回構成(mock TTS/Primary/Azure/Whisper)
# ============================================================
def _patch_leaf(monkeypatch, *, primary_seq, az, tts_counter, whisper_text="Take part."):
    import er003_v1_repro01_main_generate as r1
    import er002_common as common

    def fake_tts(text, language, out_path, **kw):
        tts_counter.append(1)
        common.write_wav_float(out_path, np.zeros(8000, dtype=np.float32), common.SAMPLE_RATE, 1)
        return {"status": "OK", "duration_seconds": 1.0, "path": out_path, "sha256": "x"}

    def fake_transcribe(*a, **k):
        i = min(len(tts_counter) - 1, len(primary_seq) - 1)
        return primary_seq[i], None

    monkeypatch.setattr(r1.p9a, "generate_narration_snippet", fake_tts)
    monkeypatch.setattr(r1.batch_wiring, "make_batch_tts_call_fn", lambda *a, **k: None)
    monkeypatch.setattr(r1.routing, "transcribe", fake_transcribe)
    monkeypatch.setattr(r1.pron_resolver_core, "resolve_and_augment_en_style_prefix", lambda base, text: (base, {"hints_applied": False}))
    monkeypatch.setattr(r1.dq18, "apply_disfluency_gate", lambda v, p, language="en", enabled=False: {"verified": v, "disfluency_checked": False, "disfluency_evidence": None})
    monkeypatch.setattr(r1.repetition_qa, "apply_repetition_qa_gate", lambda v, *a, **k: {"verified": v, "repetition_qa_checked": False})
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    wcalls = []

    def fake_whisper(p, **k):
        wcalls.append(p)
        if isinstance(whisper_text, Exception):
            raise whisper_text
        return whisper_text
    monkeypatch.setattr(kp3v, "whisper_transcribe", fake_whisper)
    r1._wcalls = wcalls
    return r1


def _hr_slots(monkeypatch):
    slots = []

    def spy(detail):
        slots.append((detail["asr_judgement"]["slot"], detail["asr_judgement"]["state"]))
    monkeypatch.setattr(sec, "_log_human_review", spy)
    return slots


def test_kp_default_vote_flow_both_pass_one_tts_one_azure_no_whisper(tmp_path, monkeypatch):
    n = []
    az = Az(("Take part.", None))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n)
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"), vote_pass_required=True)
    assert r["status"] == "OK" and len(n) == 1 and az.calls == 1 and r["asr_judgement"]["vote"]["required"] and r1._wcalls == []


def test_kp_think_up_type_split_passes_on_first_slot_with_one_whisper_call(tmp_path, monkeypatch):
    n = []
    az = Az(("Take Tart.", None))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n, whisper_text="Take part.")
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"), vote_pass_required=True)
    assert r["status"] == "OK" and len(n) == 1 and az.calls == 1 and len(r1._wcalls) == 1          # 再生成なし(旧方式は4回)
    assert r["asr_judgement"]["vote"]["row"] == "P+W"


def test_kp_default_without_vote_is_unchanged_primary_pass_no_azure(tmp_path, monkeypatch):
    n = []
    az = Az(("Take Tart.", None))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n)
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"))
    assert r["status"] == "OK" and az.calls == 0 and "vote" not in r["asr_judgement"] and r1._wcalls == []


def test_kp_take_part_type_all_four_slots_stopped_hr_only_slot4(tmp_path, monkeypatch):
    n = []
    az = Az(("Take Tart.", None))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n, whisper_text="Take Tarte.")
    slots = _hr_slots(monkeypatch)
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"), vote_pass_required=True)
    assert r["status"] == "STOPPED" and len(n) == 4 and az.calls == 4 and len(r1._wcalls) == 1      # MINIMAL 2 + ENGLISH_LOCK 2(不変)。mock TTSは同一wav(同sha)のためWhisperはmemoで1回
    assert slots == [(4, uj.NG_BOTH)]                                                                  # HR queueは最終slotのみ


def test_kp_fails_over_to_next_slot_then_passes(tmp_path, monkeypatch):
    n = []
    az = Az(seq=[("Take Tart.", None), ("Take part.", None)])
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n, whisper_text="Take Tarte.")
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"), vote_pass_required=True)
    assert r["status"] == "OK" and len(n) == 2 and az.calls == 2


def test_kp_primary_ng_secondary_pass_whisper_ng_all_slots_hr_slot4(tmp_path, monkeypatch):
    n = []
    az = Az(("Take part.", None))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take tart."], az=az, tts_counter=n, whisper_text="Take Tarte.")
    slots = _hr_slots(monkeypatch)
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"), vote_pass_required=True)
    assert r["status"] == "STOPPED" and len(n) == 4 and slots == [(4, uj.NG_BOTH)]


def test_kp_azure_down_circuit_open_skips_english_lock_tts(tmp_path, monkeypatch):
    n = []
    az = Az(raises=RuntimeError("down"))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n)
    rs = sec.begin_secondary_run(circuit_breaker_threshold=2)
    try:
        r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"), vote_pass_required=True)
    finally:
        sec.end_secondary_run()
    assert r["status"] == "STOPPED" and rs.circuit_open and len(n) == 2 and az.calls == 2
    assert r.get("english_lock_skipped_secondary_circuit_open") is True and r1._wcalls == []     # Azure障害ではWhisperを呼ばない
    n2 = []
    az2 = Az(raises=RuntimeError("down"))
    r1b = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az2, tts_counter=n2)
    sec.begin_secondary_run()
    try:
        r2 = r1b.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp2_en.wav"), vote_pass_required=True)
    finally:
        sec.end_secondary_run()
    assert r2["status"] == "STOPPED" and len(n2) == 4 and az2.calls == 3


def test_kp_whisper_timeout_opens_circuit_and_skips_english_lock_tts_P08(tmp_path, monkeypatch):
    n = []
    az = Az(("Take Tart.", None))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n, whisper_text=kp3v.WhisperTimeout("t"))
    r = r1.generate_key_phrase_component_verified(CANON, str(tmp_path / "kp1_en.wav"), vote_pass_required=True)
    assert r["status"] == "STOPPED" and kp3v.whisper_circuit_open()
    assert len(n) == 2 and len(r1._wcalls) == 1                                  # MINIMAL 2回で停止(Whisper転写はtimeoutした1回のみ、ENGLISH_LOCKへ進まない)
    assert r.get("english_lock_skipped_secondary_circuit_open") is True


def test_P08_final_slot_whisper_unavailable_hr_queue_not_entered_but_hr_lock_as_today_recorded(tmp_path, monkeypatch):
    """P-08/OPEN-371: Whisper障害で最終STOPPEDになるとHR Lock(HUMAN_REVIEW_REQUIRED)に入る現行挙動は変更しない(Azure障害時と同じ)。
    HR queue(人間レビューの問題)には入らない(technical_stop)。露出が増える点はOPEN-371へ追記。"""
    seg = tmp_path / "theme" / "a2" / "narration"
    seg.mkdir(parents=True)
    out = str(seg / "kp1_en.wav").replace("\\", "/")
    n = []
    az = Az(("Take Tart.", None))
    r1 = _patch_leaf(monkeypatch, primary_seq=["Take part."], az=az, tts_counter=n, whisper_text=RuntimeError("model broken"))
    slots = _hr_slots(monkeypatch)
    r = r1.generate_key_phrase_component_verified(CANON, out, vote_pass_required=True)
    assert r["status"] == "STOPPED" and slots == []
    st = review_lock._load_store(review_lock._level_out_dir_from_out_path(out))
    assert st["kp1_en"]["state"] == "HUMAN_REVIEW_REQUIRED"


# ============================================================
# D. 6呼出点(AST)・旧識別子撤去・Production import境界
# ============================================================
def _production_py_files():
    out = []
    for f in sorted(os.listdir(ROOT)):
        if not f.endswith(".py"):
            continue
        if "_test" in f or f.startswith("test_") or "audit" in f or "_trial_" in f or "_trial." in f:
            continue
        if f.startswith(("er088_", "er091_", "er092_", "er093_", "er096_", "er099_", "er106_", "er107_", "er108_kp_cmu_census",
                         "er108_kp_noguard", "er108_kp_guard_exposure", "er108_kp_guard_lifted_runtime",
                         "er109_pattern_probe_01", "er109_stored_census_01")):    # 履歴script/Trial/研究script(Productionではない)
            continue
        out.append(f)
    return out


class _V(ast.NodeVisitor):
    def __init__(self, kwname):
        self.kwname, self.stack, self.res = kwname, [], []

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        for k in node.keywords:
            if k.arg == self.kwname:
                self.res.append((self.stack[-1] if self.stack else "<module>", node, k))
        self.generic_visit(node)


def _calls_with_kw(kwname):
    res = []
    for f in _production_py_files():
        try:
            tree = ast.parse(open(os.path.join(ROOT, f), encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError):
            continue
        v = _V(kwname)
        v.visit(tree)
        res.extend((f, fn, c, k) for fn, c, k in v.res)
    return res


def test_AST_vote_pass_required_is_passed_only_at_the_six_kp_phrase_sites():
    sites = _calls_with_kw("vote_pass_required")
    summary = sorted({(f, fn) for f, fn, _c, _k in sites})
    assert summary == [
        ("er003_v1_repro01_main_generate.py", "generate_key_phrase_component_verified"),
        ("er019_family_x_kp_en_k2_store_01.py", "_gen_lock"),
        ("er019_family_x_kp_en_k2_store_01.py", "_styled_two_stage"),
        ("er063_family_z_audio_01.py", "_kp_en_two_stage"),
        ("er104_kp_vote_reuse_01.py", "ensure_key_phrase_english_component_x_vote"),
    ], summary
    from collections import Counter
    cnt = Counter(f for f, _fn, _c, _k in sites)
    assert cnt == {"er003_v1_repro01_main_generate.py": 2, "er019_family_x_kp_en_k2_store_01.py": 2, "er063_family_z_audio_01.py": 2,
                   "er104_kp_vote_reuse_01.py": 1}, cnt
    for f, fn, _c, k in sites:
        v = k.value
        ok = (isinstance(v, ast.Name) and v.id == "vote_pass_required") or (
            isinstance(v, ast.Call) and ((isinstance(v.func, ast.Attribute) and v.func.attr == "vote_enabled")
                                          or (isinstance(v.func, ast.Name) and v.func.id == "vote_enabled")))
        assert ok, (f, fn, ast.dump(v))


def test_AST_total_slots_keyphrase_total_calls_iff_vote_kwarg():
    for f in _production_py_files():
        try:
            tree = ast.parse(open(os.path.join(ROOT, f), encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError):
            continue
        for c in [n for n in ast.walk(tree) if isinstance(n, ast.Call)]:
            fname = c.func.attr if isinstance(c.func, ast.Attribute) else (c.func.id if isinstance(c.func, ast.Name) else "")
            if fname != "generate_narration_snippet_verified_strict":
                continue
            kws = {k.arg: k.value for k in c.keywords}
            ts = kws.get("total_slots")
            is_kp4 = ts is not None and ast.unparse(ts).endswith("KEY_PHRASE_TOTAL_MAX_ATTEMPTS")
            assert is_kp4 == ("vote_pass_required" in kws), (f, c.lineno)


def test_AST_no_literal_true_for_vote_anywhere_in_production():
    for f, fn, c, k in _calls_with_kw("vote_pass_required"):
        assert not (isinstance(k.value, ast.Constant) and k.value.value is True), (f, fn)
    for f in _production_py_files():
        tree = ast.parse(open(os.path.join(ROOT, f), encoding="utf-8").read())
        for n in ast.walk(tree):
            if isinstance(n, ast.keyword) and n.arg == "vote_required" and isinstance(n.value, ast.Constant) and n.value.value is True:
                raise AssertionError(f"literal vote_required=True in {f}")


def test_AST_attempt_ctx_vote_flag_is_forwarded_from_strict_only():
    sites = _calls_with_kw("vote_required")
    where = sorted({(f, fn) for f, fn, _c, _k in sites})
    assert ("er003_v1_repro01_main_generate.py", "generate_narration_snippet_verified_strict") in where, where
    for f, fn, _c, k in sites:
        if isinstance(k.value, ast.Constant) and k.value.value is False:
            continue   # PNAP gate呼出(KP除外のため常にFalse)は転送ではなくKPでないことの明示
        assert f in ("er003_v1_repro01_main_generate.py", "er006_secondary_asr_01.py", "er103_proper_noun_alarm_policy_01.py"), (f, fn)


def test_flag_is_only_read_via_vote_enabled_and_cannot_be_forced_on_by_mode_arg_or_dict():
    """flag(KP_THREE_ASR_VOTE_ENABLED)を読むのは単一関数のみ。env/引数/設定dictから変更する経路が無い。"""
    pat = re.compile(r"KP_THREE_ASR_VOTE_ENABLED")
    for f in _production_py_files():
        txt = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
        hits = [m.start() for m in pat.finditer(txt)]
        if f == "er104_kp_three_asr_vote_01.py":
            continue
        assert not hits or f in ("er104_kp_vote_reuse_01.py", "er019_family_x_audio_production_runner_01.py"), (f, len(hits))
    src = open(os.path.join(ROOT, "er104_kp_three_asr_vote_01.py"), encoding="utf-8").read()
    assert src.count("KP_THREE_ASR_VOTE_ENABLED") >= 2 and "os.environ" not in src and "getenv" not in src


def test_old_dual_identifiers_removed_from_production_semantic_names():
    """P-05(混合方式): flag/kwarg/ctx/state/step名の意味名は vote へ。容器名(kp_dual_check, kp_dual_reuse_gate*, kp_dual_gate telemetry)は維持。"""
    banned = re.compile(r"dual_pass_required|dual_required|NG_DUAL_PRIMARY_NOT_PASS|KP_EN_PHRASE_DUAL_REQUIRED|secondary_dual|\bdual_enabled\b|"
                        r"KpDualReuseGate|kp_dual_reuse_ok|\+dual1|_dual_circuit_open|kp_dual_canonical|kp_dual_required|_attach_kp_dual_audit")
    hits = []
    for f in _production_py_files():
        for i, line in enumerate(open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read().splitlines(), 1):
            if banned.search(line):
                hits.append((f, i, line.strip()[:100]))
    # 許容: 撤去の経緯を述べるコメントのみ(コード識別子としての残存は0)
    code_hits = [h for h in hits if not h[2].lstrip().startswith("#") and "撤去" not in h[2] and "旧" not in h[2]]
    assert code_hits == [], code_hits


def test_containers_kept_for_store_and_telemetry_P05():
    src = open(os.path.join(ROOT, "er006_master_audio_store_01.py"), encoding="utf-8").read()
    for name in ("kp_dual_check", "reuse_blocked_by_kp_dual_gate", "kp_dual_gate", "kp_dual_reuse_gate"):
        assert name in src
    assert kp3v.CHECK_VERSION == "kp_vote_check_v1"


def test_er096_is_history_only_production_never_imports_it():
    pat = re.compile(r"^\s*(?:import|from)\s+er096_", re.M)
    for f in sorted(os.listdir(ROOT)):
        if not f.endswith(".py") or f.startswith("er096_"):
            continue
        txt = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
        if pat.search(txt):
            # 許容: 履歴script・test・Trial(Productionの量産経路ではない)
            assert ("_test" in f or f.startswith(("er099_", "er104_stored_audio_reeval")) or "audit" in f or "_trial" in f), f


def test_er104_core_is_imported_only_from_the_approved_production_set():
    pat = re.compile(r"^\s*(?:import|from)\s+er104_", re.M)
    allowed = {"er003_v1_repro01_main_generate.py", "er006_secondary_asr_01.py", "er078_asr_unified_judge_01.py",
               "er019_family_x_audio_production_runner_01.py", "er019_family_x_kp_en_k2_store_01.py",
               "er019_family_x_validation_inheritance_01.py", "er063_family_z_audio_01.py"}
    for f in _production_py_files():
        if f.startswith("er104_"):
            continue
        txt = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
        if pat.search(txt):
            assert f in allowed, f


def test_dangling_reference_production_py_does_not_import_trial_modules():
    pat = re.compile(r"^\s*(?:import|from)\s+(er08[89]|er09[123])_", re.M)
    for f in _production_py_files():
        txt = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
        m = pat.search(txt)
        assert m is None, (f, m.group(0) if m else None)


def test_rollback_flag_false_restores_site_flags_and_x_default_delegates_to_shared(tmp_path, monkeypatch):
    monkeypatch.setattr(kp3v, "KP_THREE_ASR_VOTE_ENABLED", False)
    assert kv.vote_enabled() is False
    import er006_audio_cost_pilot_02_shared_narration as shared
    seen = {}
    monkeypatch.setattr(shared.store, "get_or_generate", lambda key, out, fn, *a, **k: seen.update(i=key.master_audio_id()) or {"status": "OK"})
    shared.ensure_key_phrase_english_component("take part", str(tmp_path / "x.wav"), tts_backend="speech_metadata_flash_lite")
    shared_id = seen["i"]
    kv.ensure_key_phrase_english_component_x_vote("take part", str(tmp_path / "x.wav"), tts_backend="speech_metadata_flash_lite")
    assert seen["i"] == shared_id                                                     # rollback = 共有関数 = 同一key


def test_FamilyA_shared_module_has_no_diff_and_legacy_key_unchanged():
    out = subprocess.run(["git", "status", "--porcelain", "--", "er006_audio_cost_pilot_02_shared_narration.py"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip()
    assert out == "", out
    import er006_audio_cost_pilot_02_shared_narration as shared
    k_legacy = store.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id=shared._resolve_shared_narration_model("en", "speech_metadata_flash_lite"),
                                    canonical_text="take part", level=None, style_instruction_id="key_phrase_english_component",
                                    style_instruction_version=shared.KEY_PHRASE_TRIM_POLICY_VERSION)
    kx = kv.vote_store_key("take part", "speech_metadata_flash_lite")
    assert k_legacy.master_audio_id() != kx.master_audio_id()
    assert kx.as_dict()["style_instruction_version"] == shared.KEY_PHRASE_TRIM_POLICY_VERSION + "+vote1"
    d1, d2 = dict(k_legacy.as_dict()), dict(kx.as_dict())
    d2["style_instruction_version"] = d1["style_instruction_version"]
    assert d1 == d2


def test_P04_vote_calls_with_flag_and_gate(tmp_path, monkeypatch):
    import er003_v1_repro01_main_generate as r1
    seen = {}
    called = {}
    monkeypatch.setattr(r1, "generate_key_phrase_component_verified", lambda t, p, **kw: called.update(kw=kw) or {"status": "OK"})
    monkeypatch.setattr(store, "get_or_generate", lambda key, out, fn, reuse_gate=None: (fn(out), seen.update(id=key.master_audio_id(), gate=reuse_gate))[0])
    kv.ensure_key_phrase_english_component_x_vote("take part", str(tmp_path / "x.wav"), tts_backend="speech_metadata_flash_lite")
    assert called["kw"]["vote_pass_required"] is True and called["kw"]["tts_backend"] == "speech_metadata_flash_lite"
    assert isinstance(seen["gate"], kv.KpVoteReuseGate)


def test_x_k2_and_z_sites_forward_vote_flag(tmp_path, monkeypatch):
    import er003_v1_repro01_main_generate as r1
    import er019_family_x_kp_en_k2_store_01 as k2
    kws = []
    monkeypatch.setattr(r1, "generate_narration_snippet_verified_strict", lambda *a, **k: kws.append(k) or {"status": "STOPPED"})
    monkeypatch.setattr(k2.store, "get_or_generate", lambda key, out, fn, reuse_gate=None: fn(out))
    out = str(tmp_path / "kp.wav")
    k2.ensure_key_phrase_english_component_styled("take part", out, style_text="K2", style_id="k2id", tts_backend="speech_metadata_flash_lite")
    assert len(kws) == 2 and all(k["vote_pass_required"] is True for k in kws)
    kws.clear()
    monkeypatch.setattr(kp3v, "KP_THREE_ASR_VOTE_ENABLED", False)
    k2.ensure_key_phrase_english_component_styled("take part", out, style_text="K2", style_id="k2id", tts_backend="speech_metadata_flash_lite")
    assert all(k["vote_pass_required"] is False for k in kws)
    monkeypatch.setattr(kp3v, "KP_THREE_ASR_VOTE_ENABLED", True)
    import er063_family_z_audio_01 as z
    kws.clear()
    gens = z.real_generators()
    spec = z.ClipSpec("kp1_en", "b1b", "kp_en", "take part", voice="Aoede", role_key="KP_EN", rank=1, language="en")
    gens["kp_en"](spec, out)
    assert len(kws) == 2 and all(k["vote_pass_required"] is True for k in kws)
    kws.clear()
    import er019_family_x_audio_production_runner_01 as x
    monkeypatch.setattr(x.repro01 if hasattr(x, "repro01") else r1, "generate_narration_snippet_verified_strict", lambda *a, **k: kws.append(k) or {"status": "OK"})
    x.generate_key_phrase_explanation_en_verified("Explain.", out, style_prefix_override="S", tts_backend="speech_metadata_flash_lite")
    assert kws and all("vote_pass_required" not in k for k in kws)                          # KP英語解説に投票なし


def test_x_default_branch_uses_x_vote_function_and_k2_branch_unchanged(monkeypatch):
    import er019_family_x_audio_production_runner_01 as x
    called = {}
    monkeypatch.setattr(x.kp_vote, "ensure_key_phrase_english_component_x_vote",
                        lambda safe, wav, tts_backend: called.update(safe=safe, tb=tts_backend) or {"status": "OK"})
    fn, k2 = x._kp_english_generate_fn("default", "a2", "speech_metadata_flash_lite", "take part", "w.wav")
    assert k2 is None and fn()["status"] == "OK" and called["tb"] == "speech_metadata_flash_lite"
    fn2, k2b = x._kp_english_generate_fn("fx_20261017", "a2", "speech_metadata_flash_lite", "take part", "w.wav")
    assert k2b is not None


# ============================================================
# E. 再利用6点・Store gate・本番adapter再判定(P-01)
# ============================================================
def _stored_entry(tmp_path, name, primary="Take part.", azure="Take part.", with_check=True, canonical=CANON, whisper_text=None):
    """生成時相当のentry(asr_judgement.vote + kp_dual_check)を本番adapter(evaluate_vote)で作る。Azure/Whisperはmock(API 0)。"""
    wav = _wav(tmp_path / f"{name}.wav")
    import unittest.mock as mock
    az = Az((azure, None))
    with mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", az):
        ev = kv.evaluate_vote(canonical, primary, wav, whisper_text=whisper_text)
    chk = kp3v.vote_check_from_audit(ev["vote"], wav, canonical, source="generation", judge_state=ev["state"], verified=ev["verified"])
    entry = {"status": "OK", "asr_verified": ev["verified"], "asr_text": primary, "sha256": kp3v.sha256_file(wav), "canonical_text": canonical,
             "asr_judgement": ev["asr_judgement"], "path": wav}
    if with_check:
        entry["kp_dual_check"] = chk
    return wav, entry, ev, chk


def test_reuse_ok_with_stored_evidence_is_api0_and_goes_through_production_adapter(tmp_path, monkeypatch):
    wav, entry, ev, chk = _stored_entry(tmp_path, "e1")
    assert chk["ok"] and chk["version"] == "kp_vote_check_v1" and chk["primary"]["text"] == "Take part." and chk["secondary"]["text"] == "Take part."
    az = Az(raises=AssertionError("Azure must not be called"))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    calls = []
    orig = sec.evaluate_attempt_with_cascade_detail
    monkeypatch.setattr(sec, "evaluate_attempt_with_cascade_detail", lambda *a, **k: calls.append(k.get("attempt_ctx")) or orig(*a, **k))
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert d["ok"] and d["action"] == "reuse" and d["azure_real_calls"] == 0 and az.calls == 0 and d["source"] == "stored_evidence_rejudged"
    assert calls and calls[0]["vote_required"] is True                                 # P-01: 手書き再判定ではなく本番adapter(vote_required)経由


def test_reuse_think_up_type_old_dual_ng_becomes_reuse_with_whisper_only(tmp_path, monkeypatch):
    """旧kp_dual_check_v1(読取専用)でP PASS/S NGだったentryは、Whisper(保存転写 or ローカル)だけでPASS・再利用に変わる(Primary/Azure再呼出0)。"""
    wav = _wav(tmp_path / "tu.wav")
    entry = {"status": "OK", "asr_text": "Take part.", "kp_dual_check": {
        "version": "kp_dual_check_v1", "ok": False, "canonical_text": CANON, "wav_sha256": kp3v.sha256_file(wav),
        "primary": {"text": "Take part.", "pass": True}, "secondary": {"text": "Take Tart.", "pass": False}}}
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    wcalls = []
    monkeypatch.setattr(kp3v, "whisper_transcribe", lambda p, **k: wcalls.append(p) or "Take part.")
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=False)
    assert d["ok"] and d["action"] == "reuse" and d["azure_real_calls"] == 0 and len(wcalls) == 1
    new_chk = d["kp_dual_check"]
    assert new_chk["version"] == "kp_vote_check_v1" and new_chk["row"] == "P+W" and new_chk["whisper"]["text"] == "Take part."
    # 保存済みWhisper転写(同sha)が残っていれば再転写しない
    entry["kp_dual_check"] = new_chk
    d2 = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=False)
    assert d2["ok"] and len(wcalls) == 1


def test_reuse_evidence_derived_from_asr_judgement_vote_alone(tmp_path, monkeypatch):
    wav, entry, ev, chk = _stored_entry(tmp_path, "e2", with_check=False)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=False)
    assert d["ok"] and d["azure_real_calls"] == 0


def test_reuse_legacy_asr_judgement_dual_is_read_only_evidence(tmp_path, monkeypatch):
    wav = _wav(tmp_path / "ld.wav")
    entry = {"status": "OK", "asr_text": "Take part.", "asr_judgement": {"state": "PASS", "dual": {
        "required": True, "primary_pass": True, "secondary_pass": True, "primary_text": "Take part.", "secondary_text": "Take part."}}}
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=False)
    assert d["ok"] and d["kp_dual_check"]["version"] == "kp_vote_check_v1" and d["azure_real_calls"] == 0


def test_reuse_fail_closed_cases(tmp_path, monkeypatch):
    wav, entry, ev, chk = _stored_entry(tmp_path, "e3")
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    bad = json.loads(json.dumps(entry))
    bad["kp_dual_check"]["wav_sha256"] = "0" * 64
    bad.pop("asr_judgement")
    d = kv.kp_vote_reuse_ok(bad, wav_path=wav, canonical_text=CANON, allow_s1=False)
    assert not d["ok"] and d["reason"] == "no_vote_evidence_api0_context"
    d = kv.kp_vote_reuse_ok({"status": "OK", "asr_text": "Take part."}, wav_path=wav, canonical_text=CANON, allow_s1=False)
    assert not d["ok"]
    d = kv.kp_vote_reuse_ok({"status": "OK"}, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert not d["ok"] and d["reason"] == "no_primary_transcript" and d["action"] == "regenerate"
    assert not kv.kp_vote_reuse_ok(entry, wav_path=str(tmp_path / "none.wav"), canonical_text=CANON, allow_s1=True)["ok"]
    d = kv.kp_vote_reuse_ok(dict(entry), wav_path=wav, canonical_text="different phrase", allow_s1=False)
    assert not d["ok"]


def test_reuse_rejudge_rejects_stored_pass_when_current_vote_is_ng(tmp_path, monkeypatch):
    wav = _wav(tmp_path / "e4.wav")
    entry = {"status": "OK", "asr_text": "Take Tart.", "sha256": kp3v.sha256_file(wav), "kp_dual_check": {
        "version": kp3v.CHECK_VERSION, "ok": True, "canonical_text": CANON, "wav_sha256": kp3v.sha256_file(wav),
        "primary": {"text": "Take Tart.", "pass": True}, "secondary": {"text": "Take Tart."}}}
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert not d["ok"] and d["action"] == "regenerate" and "NG_BOTH" in d["reason"]            # 保存証跡を信用せず現行の判定で再評価
    entry["kp_dual_check"]["primary"]["text"] = "Take part."
    entry["kp_dual_check"]["secondary"]["text"] = "Take Tart."
    entry["kp_dual_check"]["whisper"] = {"text": "Take Tarte."}
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert not d["ok"] and d["action"] == "regenerate"


def test_reuse_whisper_failure_is_technical_stop_not_regenerate(tmp_path, monkeypatch):
    wav = _wav(tmp_path / "wf.wav")
    entry = {"status": "OK", "asr_text": "Take part.", "kp_dual_check": {
        "version": "kp_dual_check_v1", "canonical_text": CANON, "wav_sha256": kp3v.sha256_file(wav),
        "primary": {"text": "Take part."}, "secondary": {"text": "Take Tart."}}}

    def boom(p, **k):
        raise RuntimeError("model broken")
    monkeypatch.setattr(kp3v, "whisper_transcribe", boom)
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=False)
    assert d["action"] == "technical_stop" and not d["ok"] and d["reason"] == "whisper_unavailable"
    assert kv.technical_stop_entry("kp1_english", d)["status"] == "TECHNICAL_STOP_WHISPER_UNAVAILABLE"


def test_S1_azure_once_pass_persists_evidence_and_second_time_is_api0(tmp_path, monkeypatch):
    wav = _wav(tmp_path / "s1.wav")
    entry = {"status": "OK", "asr_text": "Take part.", "qa_evidence": {"asr_text": "Take part."}}
    az = Az(("Take part.", None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert d["ok"] and d["action"] == "reuse" and az.calls == 1 and d["azure_real_calls"] == 1 and d["source"] == "s1_confirm"
    assert d["kp_dual_check"]["secondary"]["provider"] == "azure" and d["kp_dual_check"]["secondary"]["text"] == "Take part."
    entry["kp_dual_check"] = d["kp_dual_check"]
    d2 = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert d2["ok"] and az.calls == 1


def test_S1_azure_ng_regenerates_and_azure_outage_is_technical_stop(tmp_path, monkeypatch):
    wav = _wav(tmp_path / "s1b.wav")
    entry = {"status": "OK", "asr_text": "Take part."}
    monkeypatch.setattr(kp3v, "whisper_transcribe", lambda p, **k: "Take Tarte.")
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(("Take Tart.", None)))
    d = kv.kp_vote_reuse_ok(entry, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert not d["ok"] and d["action"] == "regenerate"
    for i, az in enumerate((Az(raises=RuntimeError("down")), Az(("", None)), Az((None, "err")))):
        monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
        d = kv.kp_vote_reuse_ok({"status": "OK", "asr_text": "Take part."}, wav_path=_wav(tmp_path / f"o{i}.wav"), canonical_text=CANON, allow_s1=True)
        assert d["action"] == "technical_stop" and not d["ok"]
    rs = uj.RunState()
    rs.circuit_open = True
    monkeypatch.setattr(sec, "_RUN_STATE", rs)
    d = kv.kp_vote_reuse_ok({"status": "OK", "asr_text": "Take part."}, wav_path=wav, canonical_text=CANON, allow_s1=True)
    assert d["action"] == "technical_stop" and d["reason"] == "secondary_circuit_open"


def _seed_store(key, tmp_path, *, primary="Take part.", with_check=None):
    wav = _wav(tmp_path / "seed.wav")
    os.makedirs(store.AUDIO_DIR, exist_ok=True)
    stored = f"{store.AUDIO_DIR}/{key.master_audio_id()}.wav"
    import shutil
    shutil.copyfile(wav, stored)
    entry = {"audio_path": stored, "key": key.as_dict(), "created_at": "2026-10-01T00:00:00",
             "qa_evidence": {"sha256": kp3v.sha256_file(stored), "asr_verified": True, "asr_text": primary},
             "asr_judgement": None, "audio_classification": "NORMALIZED_MATCH"}
    if with_check is not None:
        entry["kp_dual_check"] = with_check
    store._save_manifest({key.master_audio_id(): entry})
    return stored


def _key():
    return kv.vote_store_key(CANON, "speech_metadata_flash_lite")


def test_store_gate_s1_pass_reuses_and_persists_check(tmp_path, monkeypatch):
    key = _key()
    _seed_store(key, tmp_path)
    az = Az(("Take part.", None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    gen = []
    r = store.get_or_generate(key, str(tmp_path / "out.wav"), lambda p: gen.append(1) or {"status": "OK"}, reuse_gate=kv.KpVoteReuseGate())
    assert r["reused"] and not gen and az.calls == 1 and r["kp_dual_check"]["source"] == "s1_confirm"
    assert store._load_manifest()[key.master_audio_id()]["kp_dual_check"]["ok"] is True
    r2 = store.get_or_generate(key, str(tmp_path / "out2.wav"), lambda p: gen.append(1) or {"status": "OK"}, reuse_gate=kv.KpVoteReuseGate())
    assert r2["reused"] and az.calls == 1 and r2["kp_dual_check"]["ok"]


def test_store_gate_split_with_whisper_pass_reuses_without_regeneration_think_up_type(tmp_path, monkeypatch):
    key = _key()
    wav = None
    stored = _seed_store(key, tmp_path)
    chk = {"version": "kp_dual_check_v1", "ok": False, "canonical_text": CANON, "wav_sha256": kp3v.sha256_file(stored),
           "primary": {"text": "Take part."}, "secondary": {"text": "Take Tart."}}
    m = store._load_manifest()
    m[key.master_audio_id()]["kp_dual_check"] = chk
    store._save_manifest(m)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    monkeypatch.setattr(kp3v, "whisper_transcribe", lambda p, **k: "Take part.")
    gen = []
    r = store.get_or_generate(key, str(tmp_path / "out.wav"), lambda p: gen.append(1) or {"status": "OK"}, reuse_gate=kv.KpVoteReuseGate())
    assert r["reused"] is True and not gen                       # 旧方式ならNGで再生成。新方式はWhisperのみ(Primary/Azure/TTS 0)で再利用
    assert store._load_manifest()[key.master_audio_id()]["kp_dual_check"]["version"] == "kp_vote_check_v1"


def test_store_gate_vote_ng_regenerates_and_backs_up_old_audio(tmp_path, monkeypatch):
    key = _key()
    _seed_store(key, tmp_path)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(("Take Tart.", None)))
    monkeypatch.setattr(kp3v, "whisper_transcribe", lambda p, **k: "Take Tarte.")
    gen = []

    def gen_fn(p):
        gen.append(1)
        _wav(p)
        return {"status": "OK", "asr_verified": True, "asr_text": "Take part.", "asr_judgement": {
            "state": "PASS", "vote": {"required": True, "state": "PASS_DUAL", "row": "P+S", "pass_count": 2,
                                      "primary": {"text": "Take part.", "pass": True}, "secondary": {"text": "Take part.", "pass": True},
                                      "secondary_called": True, "whisper": None, "whisper_called": False}}}
    r = store.get_or_generate(key, str(tmp_path / "out.wav"), gen_fn, reuse_gate=kv.KpVoteReuseGate())
    assert gen == [1] and r["reused"] is False and r["cache_miss_reason"] == "kp_dual_gate_blocked"
    assert os.listdir(f"{store.AUDIO_DIR}/_reuse_blocked")
    assert store._load_manifest()[key.master_audio_id()]["kp_dual_check"]["ok"] is True


def test_store_gate_azure_outage_is_technical_stop_no_regen_no_reuse(tmp_path, monkeypatch):
    key = _key()
    _seed_store(key, tmp_path)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=RuntimeError("down")))
    gen = []
    r = store.get_or_generate(key, str(tmp_path / "out.wav"), lambda p: gen.append(1) or {"status": "OK"}, reuse_gate=kv.KpVoteReuseGate())
    assert r["status"] == "TECHNICAL_STOP_SECONDARY_UNAVAILABLE" and r["technical_stop"] and not gen and not os.path.exists(tmp_path / "out.wav")
    assert not os.path.exists(f"{store.AUDIO_DIR}/_reuse_blocked")
    assert "kp_dual_check" not in store._load_manifest()[key.master_audio_id()]


def test_store_without_gate_is_unchanged_for_family_ABC(tmp_path, monkeypatch):
    key = _key()
    _seed_store(key, tmp_path)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    before = json.dumps(store._load_manifest(), sort_keys=True)
    r = store.get_or_generate(key, str(tmp_path / "out.wav"), lambda p: (_ for _ in ()).throw(AssertionError("no gen")))
    assert r["reused"] and "kp_dual_check" not in r and json.dumps(store._load_manifest(), sort_keys=True) == before
    k2 = store.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id="m", canonical_text="other", style_instruction_id="other")
    store.get_or_generate(k2, str(tmp_path / "o2.wav"), lambda p: (_wav(p), {"status": "OK"})[1])
    assert "kp_dual_check" not in store._load_manifest()[k2.master_audio_id()]


def test_store_legacy_shared_entry_is_not_touched_by_x_vote_key(tmp_path, monkeypatch):
    import er006_audio_cost_pilot_02_shared_narration as shared
    legacy = store.MasterAudioKey(language="en", speaker_voice="Aoede", tts_model_id=shared._resolve_shared_narration_model("en", "speech_metadata_flash_lite"),
                                  canonical_text=CANON, level=None, style_instruction_id="key_phrase_english_component",
                                  style_instruction_version=shared.KEY_PHRASE_TRIM_POLICY_VERSION)
    _seed_store(legacy, tmp_path)
    before = store._load_manifest()[legacy.master_audio_id()]
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(("Take part.", None)))
    import er003_v1_repro01_main_generate as r1
    monkeypatch.setattr(r1, "generate_key_phrase_component_verified", lambda t, p, **kw: (_wav(p), {"status": "OK", "asr_verified": True, "asr_text": "Take part."})[1])
    r = kv.ensure_key_phrase_english_component_x_vote(CANON, str(tmp_path / "o.wav"), tts_backend="speech_metadata_flash_lite")
    assert r["reused"] is False and r["cache_miss_reason"] == "no_existing_master"
    assert store._load_manifest()[legacy.master_audio_id()] == before


def test_reuse_point1_runner_previous_results_gate(tmp_path, monkeypatch):
    import er019_family_x_audio_production_runner_01 as x
    wav, entry, ev, chk = _stored_entry(tmp_path, "r1", canonical=CANON)
    cached = {"style_version": x.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "key_phrases": {"1": {"english": dict(entry, canonical_text=CANON)}}}
    gen = []
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    r = x._generate_or_reuse_kp(cached, 1, "english", wav, lambda: gen.append(1) or {"status": "OK"}, expected_text=CANON)
    assert r["reused_from_previous_run"] and not gen and r["kp_dual_check"]["ok"]
    cached2 = {"style_version": x.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "key_phrases": {"1": {"english": {"status": "OK", "canonical_text": CANON}}}}
    r2 = x._generate_or_reuse_kp(cached2, 1, "english", wav, lambda: gen.append(1) or {"status": "OK"}, expected_text=CANON)
    assert gen == [1] and r2.get("kp_dual_reuse_gate_previous", {}).get("reason") == "no_primary_transcript"
    gen.clear()
    cached3 = {"style_version": x.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "key_phrases": {"1": {"english": {"status": "OK", "canonical_text": CANON, "asr_text": "Take part."}}}}
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=RuntimeError("down")))
    r3 = x._generate_or_reuse_kp(cached3, 1, "english", wav, lambda: gen.append(1) or {"status": "OK"}, expected_text=CANON)
    assert r3["status"] == "TECHNICAL_STOP_SECONDARY_UNAVAILABLE" and not gen
    r4 = x._generate_or_reuse_kp({"style_version": x.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "key_phrases": {"1": {"explanation": {"status": "OK", "canonical_text": "E"}}}},
                                 1, "explanation", wav, lambda: gen.append(1) or {"status": "OK"}, expected_text="E")
    assert r4["reused_from_previous_run"] and not gen


def test_reuse_point2_inheritance_gate_api0(tmp_path, monkeypatch):
    import er019_family_x_validation_inheritance_01 as inh
    wav, entry, ev, chk = _stored_entry(tmp_path, "r2")
    entry = dict(entry, asr_verified=True, text=CANON, canonical_text=CANON)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    got = inh.try_inherit_from_cached(entry, wav, CANON, "v1", "v1", {"kind": "t", "label": "kp1_english"},
                                      kp_vote_required=True, kp_vote_canonical=CANON)
    assert got is not None and got["validation_inheritance"]["label"] == inh.REUSED_VALIDATED
    e2 = {k: v for k, v in entry.items() if k not in ("kp_dual_check", "asr_judgement")}
    assert inh.try_inherit_from_cached(e2, wav, CANON, "v1", "v1", {"kind": "t", "label": "kp1_english"},
                                       kp_vote_required=True, kp_vote_canonical=CANON) is None
    assert inh.try_inherit_from_cached(e2, wav, CANON, "v1", "v1", {"kind": "t", "label": "kp1_explanation"}) is not None
    e3 = dict(e2, status="STOPPED")
    assert inh.try_inherit_from_cached(e3, wav, CANON, "v1", "v1", {"kind": "t", "label": "kp1_english"},
                                       kp_vote_required=True, kp_vote_canonical=CANON) == inh.try_inherit_from_cached(
        e3, wav, CANON, "v1", "v1", {"kind": "t", "label": "kp1_english"})
    assert "TECHNICAL_STOP_WHISPER_UNAVAILABLE" in inh._OVERWRITABLE_STATUSES


def test_reuse_point6_z_generate_or_reuse_gate(tmp_path, monkeypatch):
    import er063_family_z_audio_01 as z
    spec = z.ClipSpec("kp1_en", "b1b", "kp_en", "take part", voice="Aoede", role_key="KP_EN", rank=1, language="en")
    norm = z._norm_for_tts(spec)
    wav, entry, ev, chk = _stored_entry(tmp_path, "z1", canonical=norm)
    entry = dict(entry, reuse_key=z.build_reuse_key(spec), sha256=z._sha_file(wav))
    gen = []
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    r = z.generate_or_reuse_z(entry, spec, wav, lambda: gen.append(1) or {"status": "OK"})
    assert r["reused_from_previous_run"] and not gen and r["kp_dual_check"]["ok"]
    e2 = {k: v for k, v in entry.items() if k not in ("kp_dual_check", "asr_judgement")}
    e2["asr_text"] = "Take part."
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(("Take Tart.", None)))
    monkeypatch.setattr(kp3v, "whisper_transcribe", lambda p, **k: "Take Tarte.")
    r2 = z.generate_or_reuse_z(e2, spec, wav, lambda: gen.append(1) or {"status": "OK"})
    assert gen == [1] and r2["kp_dual_reuse_gate_previous"]["action"] == "regenerate"
    spec_x = z.ClipSpec("kp1_explanation_en", "b1b", "kp_expl_en", "Explain.", voice="Aoede", role_key="KP_EXPL_EN")
    ex = {"status": "OK", "reuse_key": z.build_reuse_key(spec_x), "sha256": z._sha_file(wav), "canonical_text": "Explain."}
    gen.clear()
    r3 = z.generate_or_reuse_z(ex, spec_x, wav, lambda: gen.append(1) or {"status": "OK"})
    assert r3["reused_from_previous_run"] and not gen


def test_z_split_clip_uses_same_adapter_and_records_vote_check(tmp_path, monkeypatch):
    """P-06: Zが同じ本番adapterを通ること、Zの再利用でkp_vote_check_v1が記録されることをtestで固定(Xと同じhelper)。"""
    import er063_family_z_audio_01 as z
    spec = z.ClipSpec("kp1_en", "b1b", "kp_en", "take part", voice="Aoede", role_key="KP_EN", rank=1, language="en")
    norm = z._norm_for_tts(spec)
    wav = _wav(tmp_path / "zsplit.wav")
    entry = {"status": "OK", "reuse_key": z.build_reuse_key(spec), "sha256": z._sha_file(wav), "canonical_text": norm, "asr_text": "Take part.",
             "kp_dual_check": {"version": "kp_dual_check_v1", "canonical_text": norm, "wav_sha256": kp3v.sha256_file(wav),
                               "primary": {"text": "Take part."}, "secondary": {"text": "Take Tart."}}}
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    monkeypatch.setattr(kp3v, "whisper_transcribe", lambda p, **k: "Take part.")
    r = z.generate_or_reuse_z(entry, spec, wav, lambda: (_ for _ in ()).throw(AssertionError("no regen")))
    assert r["reused_from_previous_run"] and r["kp_dual_check"]["version"] == "kp_vote_check_v1" and r["kp_dual_check"]["row"] == "P+W"


def test_z_build_entry_carries_kp_dual_check_container(tmp_path, monkeypatch):
    import er063_family_z_audio_01 as z
    spec = z.ClipSpec("kp1_en", "b1b", "kp_en", "take part", voice="Aoede", role_key="KP_EN", rank=1, language="en")
    out = str(tmp_path / "theme" / "b1b" / "narration" / "kp1_en.wav")
    _wav(out)
    e = z.build_entry(spec, out, {"status": "OK", "kp_dual_check": {"ok": True, "version": kp3v.CHECK_VERSION}})
    assert e["kp_dual_check"]["ok"] is True
    e2 = z.build_entry(spec, out, {"status": "OK"})
    assert "kp_dual_check" not in e2


# ============================================================
# F. P-08: Whisper障害・preflight・circuit guard
# ============================================================
def test_guard_whisper_blocks_generation_when_preflight_fails(monkeypatch):
    kp3v.reset_whisper_state()
    kv.reset_preflight()

    def bad_pf(**k):
        kp3v.WHISPER_STATE.circuit_open = True
        return {"model": "small", "compute_type": "int8", "device": "cpu", "ok": False, "error": "ImportError: no module", "model_cache_present": False, "load_sec": None}
    monkeypatch.setattr(kp3v, "whisper_preflight", bad_pf)
    gen = []
    g = kv.guard_whisper(lambda: gen.append(1) or {"status": "OK"}, "kp1_english")
    r = g()
    assert r["status"] == "TECHNICAL_STOP_WHISPER_UNAVAILABLE" and r["technical_stop"] and not gen and r["human_review_required"] is False
    assert r["whisper_preflight"]["error"].startswith("ImportError")


def test_guard_whisper_passes_through_when_preflight_ok_and_when_vote_disabled(monkeypatch):
    gen = []
    g = kv.guard_whisper(lambda: gen.append(1) or {"status": "OK"}, "kp1_english")
    assert g()["status"] == "OK" and gen == [1]
    monkeypatch.setattr(kp3v, "KP_THREE_ASR_VOTE_ENABLED", False)
    calls = []
    monkeypatch.setattr(kp3v, "whisper_preflight", lambda **k: calls.append(1) or {"ok": False})
    kv.reset_preflight()
    assert g()["status"] == "OK" and calls == []                       # rollback時はpreflightも行わない


def test_preflight_runs_once_per_process(monkeypatch):
    calls = []
    monkeypatch.setattr(kp3v, "whisper_preflight", lambda **k: calls.append(1) or {"model": "small", "compute_type": "int8", "device": "cpu",
                                                                                      "ok": True, "error": None, "model_cache_present": True, "load_sec": 0.1})
    kv.reset_preflight()
    kv.preflight_once()
    kv.preflight_once()
    assert len(calls) == 1 and kv.preflight_once()["model_cache_present"] is True


def test_x_and_z_generate_paths_are_wrapped_by_guard_whisper(tmp_path, monkeypatch):
    import er019_family_x_audio_production_runner_01 as x
    import er063_family_z_audio_01 as z
    monkeypatch.setattr(kp3v, "KP_THREE_ASR_VOTE_ENABLED", True)

    def bad_pf(**k):
        kp3v.WHISPER_STATE.circuit_open = True
        return {"model": "small", "compute_type": "int8", "device": "cpu", "ok": False, "error": "x", "model_cache_present": False, "load_sec": None}
    monkeypatch.setattr(kp3v, "whisper_preflight", bad_pf)
    kv.reset_preflight()
    gen = []
    r = x._generate_or_reuse_kp(None, 1, "english", str(tmp_path / "a.wav"), lambda: gen.append(1) or {"status": "OK"}, expected_text=CANON)
    assert r["status"] == "TECHNICAL_STOP_WHISPER_UNAVAILABLE" and not gen
    kv.reset_preflight()
    kp3v.reset_whisper_state()
    spec = z.ClipSpec("kp1_en", "b1b", "kp_en", "take part", voice="Aoede", role_key="KP_EN", rank=1, language="en")
    r2 = z.generate_or_reuse_z(None, spec, str(tmp_path / "b.wav"), lambda: gen.append(1) or {"status": "OK"})
    assert r2["status"] == "TECHNICAL_STOP_WHISPER_UNAVAILABLE" and not gen
    # 解説(role!=english)はWhisperを必要としないのでguardなし
    kv.reset_preflight()
    kp3v.reset_whisper_state()
    r3 = x._generate_or_reuse_kp(None, 1, "explanation", str(tmp_path / "c.wav"), lambda: gen.append(1) or {"status": "OK"}, expected_text="E")
    assert r3["status"] == "OK" and gen == [1]


# ============================================================
# G. take part型(Primary PASS/Azure NG)の保存転写差込み(Trial er088の実測10/10 + Whisper small保存転写『Take Tarte.』)
# ============================================================
def test_take_part_type_saved_transcripts_all_rejected_by_production_vote(tmp_path, monkeypatch):
    base = os.path.join(ROOT, "er088_output", "kp_asr_dual_pass_trial_01")
    rp = os.path.join(base, "results.jsonl")
    wav_src = os.path.join(base, "kp4_en.wav")
    if not (os.path.exists(rp) and os.path.exists(wav_src)):
        pytest.skip("er088 evidence data not present")
    rows = [json.loads(l) for l in open(rp, encoding="utf-8") if l.strip()]
    assert len(rows) == 10
    import shutil
    wav = str(tmp_path / "kp4_en.wav")
    shutil.copyfile(wav_src, wav)
    for r in rows:
        pt = r["primary_and_secondary"]["primary_call"]["text"]
        st = r["primary_and_secondary"]["judge"]["secondary_text"]
        assert st == "Take Tart."
        ev = kv.evaluate_vote("take part", pt, wav, secondary_text=st, whisper_text="Take Tarte.")
        assert ev["verified"] is False and ev["state"] == uj.NG_BOTH, (pt, ev["state"])


# ============================================================
# H. 組立時の非blocking監査
# ============================================================
def test_assembly_audit_is_nonblocking_and_reports_missing_evidence(tmp_path, capsys, monkeypatch):
    import er019_family_x_audio_production_runner_01 as x
    res = {"key_phrases": {
        "1": {"english": {"status": "OK", "kp_dual_check": {"ok": True, "version": "kp_vote_check_v1"}}},
        "2": {"english": {"status": "OK", "asr_judgement": {"state": "PASS", "vote": {"required": True, "state": "PASS_VOTE_2OF3"}}}},
        "3": {"english": {"status": "OK", "asr_judgement": {"state": "PASS"}}},
        "4": {"english": {"status": "STOPPED"}}}}
    a = kv.assembly_audit(res, "b1b")
    assert a["blocking"] is False and a["with_vote_evidence"] == ["1", "2"] and a["missing_vote_evidence"] == ["3"] and a["checked"] == 3
    assert "kp3_english" in capsys.readouterr().out
    summary = {}
    d = tmp_path / "audit"
    d.mkdir()
    (d / "tts_generation_results.json").write_text(json.dumps(res), encoding="utf-8")
    x._attach_kp_vote_audit(summary, str(tmp_path), "b1b")
    assert summary["kp_vote_audit"]["missing_vote_evidence"] == ["3"]
    monkeypatch.setattr(kp3v, "KP_THREE_ASR_VOTE_ENABLED", False)
    s2 = {}
    x._attach_kp_vote_audit(s2, str(tmp_path), "b1b")
    assert s2 == {} and kv.assembly_audit(res) == {"enabled": False}


# ============================================================
# I. KP-QUALITY-2ITEMS(2026-10-22): 再利用事前guard(guard_entry)の保護解除は『vote gateが後続する呼出』だけ(OF-KPQ-P-01)
# ============================================================
import er078_reuse_value_guard_01 as rvg  # noqa: E402

_E_DIFF = {"status": "OK", "asr_verified": True, "text": "two days", "canonical_text": "two days", "asr_text": "Three days."}


def test_P01_guard_entry_skip_only_with_explicit_arg_and_reuse_blocked_mark_still_wins():
    lab = "master:key_phrase_english_component"
    assert rvg.guard_entry(_E_DIFF, label=lab)["blocked"] is True                          # 既定(A/B/C・非KP・vote無効)= 保護維持
    assert rvg.guard_entry(_E_DIFF, label=lab, kp_vote_gate_follows=False)["blocked"] is True
    g = rvg.guard_entry(_E_DIFF, label=lab, kp_vote_gate_follows=True)
    assert g["blocked"] is False and g["reason"] == "KP_EN_VOTE_GATE_DECIDES" and g["api_calls"] == 0
    g2 = rvg.guard_entry(dict(_E_DIFF, reuse_blocked={"by": "bulk"}), label=lab, kp_vote_gate_follows=True)
    assert g2["blocked"] is True and g2["reason"] == "REUSE_BLOCKED_MARK"                  # 明示markは尊重


def test_P01_store_abc_default_still_blocks_value_diff_same_label_as_kp(tmp_path, monkeypatch):
    """A/B/CのKP英語再利用(reuse_gate=None, label同一)は保護維持: 値DIFFのentryは再利用せず再生成する。"""
    key = kv.vote_store_key("two days", "speech_metadata_flash_lite")
    _seed_store(key, tmp_path, primary="Three days.")
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=AssertionError("no azure")))
    gen = []
    r = store.get_or_generate(key, str(tmp_path / "out.wav"), lambda p: (gen.append(1), _wav(p), {"status": "OK"})[2])
    assert gen == [1] and r["reused"] is False


def test_P01_store_with_vote_gate_passes_true_and_without_gate_passes_false(tmp_path, monkeypatch):
    seen = []
    orig = rvg.guard_entry

    def spy(entry, **kw):
        seen.append(kw.get("kp_vote_gate_follows"))
        return orig(entry, **kw)
    monkeypatch.setattr(rvg, "guard_entry", spy)
    key = kv.vote_store_key("two days", "speech_metadata_flash_lite")
    _seed_store(key, tmp_path, primary="Two days.")
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(("Two days.", None)))
    store.get_or_generate(key, str(tmp_path / "o1.wav"), lambda p: {"status": "OK"})
    store.get_or_generate(key, str(tmp_path / "o2.wav"), lambda p: {"status": "OK"}, reuse_gate=kv.KpVoteReuseGate())
    assert seen == [False, True]


def test_P01_x_runner_and_inheritance_and_z_pass_explicit_arg(monkeypatch):
    import er019_family_x_audio_production_runner_01 as xr
    import er019_family_x_validation_inheritance_01 as vi
    seen = []
    orig = rvg.guard_entry

    def spy(entry, **kw):
        seen.append(("kp_vote_gate_follows", kw.get("kp_vote_gate_follows")))
        return orig(entry, **kw)
    monkeypatch.setattr(rvg, "guard_entry", spy)
    assert xr._reuse_guard_blocks(_E_DIFF, "kp1_english", kp_vote_gate_follows=True) is None
    assert xr._reuse_guard_blocks(_E_DIFF, "kp1_english") is not None
    # 引継ぎ: kp_vote_required がそのまま渡る
    seen.clear()
    vi.try_inherit_from_cached(dict(_E_DIFF), "no.wav", None, "v1", "v1", {"label": "x"}, kp_vote_required=True)
    vi.try_inherit_from_cached(dict(_E_DIFF), "no.wav", None, "v1", "v1", {"label": "x"}, kp_vote_required=False)
    # 上は証拠不足でguardに到達しない場合があるため、ソースでも固定する
    srcs = {f: open(os.path.join(ROOT, f), encoding="utf-8").read() for f in
            ("er019_family_x_validation_inheritance_01.py", "er019_family_x_audio_production_runner_01.py", "er063_family_z_audio_01.py",
             "er006_master_audio_store_01.py")}
    assert "kp_vote_gate_follows=bool(kp_vote_required)" in srcs["er019_family_x_validation_inheritance_01.py"]
    assert 'kp_vote_gate_follows=bool(role == "english" and kp_vote.vote_enabled())' in srcs["er019_family_x_audio_production_runner_01.py"]
    assert 'kp_vote_gate_follows=bool(spec.kind == "kp_en" and kp_vote.vote_enabled())' in srcs["er063_family_z_audio_01.py"]
    assert "kp_vote_gate_follows=(reuse_gate is not None)" in srcs["er006_master_audio_store_01.py"]


def test_P01_rollback_vote_disabled_keeps_protection_in_x_and_z(monkeypatch):
    """vote無効(rollback)ではKP英語でも保護再判定を維持する(呼出元がFalseを渡す)。"""
    import er019_family_x_audio_production_runner_01 as xr
    monkeypatch.setattr(kp3v, "KP_THREE_ASR_VOTE_ENABLED", False)
    follows = bool("english" == "english" and xr.kp_vote.vote_enabled())
    assert follows is False
    assert xr._reuse_guard_blocks(_E_DIFF, "kp1_english", kp_vote_gate_follows=follows) is not None
