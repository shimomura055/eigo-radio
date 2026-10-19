# AUW 委任_06c: Opus条件Cレビュー所見(OF-AUW-C-01〜C-14)のFable採用分のtest。全てmock・API呼出0・費用JPY0。
# (a)非ラテンKP救済の最終ANDゲート対象 (b)Secondary障害の網羅 (c)再利用経路の値ガード (d)技術STOP≠HR (e)試聴リスト導出失敗
# (g)flag OFFロールバック経路 (h)Dialogue/Voices A2外側ループ
import hashlib
import json
import os
import re
import sys
import types
import wave

import pytest

import er003_v1_n3_01_tts_generate as n3_tts
import er006_master_audio_store_01 as store
import er006_secondary_asr_01 as sec
import er007_ja_secondary_asr_01 as ja
import er013_family_c_production_runner_01 as c_runner
import er019_family_x_audio_production_runner_01 as x_runner
import er019_family_x_validation_inheritance_01 as vi
import er063_family_z_audio_01 as z_audio
import er078_asr_unified_judge_01 as uj
import er078_pass_with_warning_registry_01 as reg
import er078_reuse_value_guard_01 as rvg
import er078_secondary_run_scope_01 as scope


class Az:
    def __init__(self, result=(None, "no result"), raises=None):
        self.result, self.raises, self.calls = result, raises, 0

    def __call__(self, wav_path, language="en-US", phrases=None, **kw):
        self.calls += 1
        if self.raises:
            raise self.raises
        return self.result


@pytest.fixture(autouse=True)
def _iso(monkeypatch):
    sec.reset_secondary_cache()
    sec._reset_m1_freeze_cache()
    monkeypatch.setattr(sec, "_RUN_STATE", None)
    monkeypatch.setattr(sec, "_RUN_CACHE", None)
    yield
    sec.reset_secondary_cache()


def _wav(tmp_path, name="a.wav", seconds=1, rate=8000):
    p = tmp_path / name
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(rate)
        w.writeframes(b"\x00" * (rate * seconds))
    return str(p)


def run(canon, asr, wav, az, monkeypatch, **kw):
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    kw.setdefault("cascade_enabled", True)
    return sec.evaluate_attempt_with_cascade_detail(canon, asr, [], wav, **kw)


NL_PRIMARY = "待ちきれない三日間"   # 非ラテン主体のPrimary転写(英語Key Phraseを日本語に誤認識した典型)


# ============================================================
# (a) BLOCKER 非ラテン救済の最終ANDゲートは採用転写(Azure転写)に対して行う
# ============================================================
@pytest.mark.parametrize("canon", ["I can't wait for 3 days.", "It is not at all clear.", "We cannot wait 2 days."])
def test_a_non_latin_rescue_with_negation_or_number_is_pass_with_warning(tmp_path, monkeypatch, canon):
    az = Az((canon, None))
    d = run(canon, NL_PRIMARY, _wav(tmp_path), az, monkeypatch, enable_non_latin_cascade=True)
    j = d["asr_judgement"]
    assert d["verified"] is True, (j["state"], j["reason_code"])           # 退行(NG_PROTECTED)していない
    assert j["state"] == uj.PASS_WITH_WARNING and uj.W_SECONDARY_CONFIRMED in j["warnings"]
    assert j["primary"]["text"] == NL_PRIMARY and j["primary"]["adopted_text"] == canon   # 採用転写で最終ゲート
    assert j["final_gate"]["applied"] is True and j["final_gate"]["negation_diff"] is False
    assert j["value_guard"]["gate_target"] == "adopted_text"
    assert az.calls == 1                                                     # Azureは1回(共有cache)


def test_a_primary_non_latin_text_is_never_checked_against_english_negation_or_numbers():
    # 退行の直接再現: adopted_textを持たないPrimaryの非ラテン転写を英語否定と照合するとNG_PROTECTED(旧挙動=退行の原因)。
    canon = "I can't wait for 3 days."
    pr = uj.PrimaryResult(passed=True, text=NL_PRIMARY, label="X")
    old = uj.unified_judge(uj.AttemptCtx(canonical_text=canon, wav_sha256="s1"), pr, lambda c: "never", lang="en", role=None)
    assert old.state == uj.NG_PROTECTED
    pr2 = uj.PrimaryResult(passed=True, text=NL_PRIMARY, label="X", adopted_text=canon)
    new = uj.unified_judge(uj.AttemptCtx(canonical_text=canon, wav_sha256="s2"), pr2, lambda c: "never", lang="en", role=None)
    assert new.state in (uj.PASS, uj.PASS_WITH_WARNING) and new.verified


@pytest.mark.parametrize("adopted,reason", [("I can wait for 3 days.", "final_gate_negation_diff"),
                                             ("I can't wait for 4 days.", "final_gate_value_diff")])
def test_a_negation_or_value_diff_on_adopted_transcript_stays_ng_protected(adopted, reason):
    canon = "I can't wait for 3 days."
    pr = uj.PrimaryResult(passed=True, text=NL_PRIMARY, label="X", adopted_text=adopted)
    r = uj.unified_judge(uj.AttemptCtx(canonical_text=canon, wav_sha256="s3"), pr, lambda c: "never", lang="en", role=None)
    assert r.state == uj.NG_PROTECTED and r.reason_code == reason


def test_a_adapter_non_latin_rescue_with_diff_in_azure_transcript_is_not_verified(tmp_path, monkeypatch):
    az = Az(("I can wait for 3 days.", None))
    d = run("I can't wait for 3 days.", NL_PRIMARY, _wav(tmp_path), az, monkeypatch, enable_non_latin_cascade=True)
    assert d["verified"] is False and d["asr_judgement"]["state"] != uj.PASS_WITH_WARNING


def test_a_j11_rejudge_non_latin_rescue_uses_stored_azure_transcript():
    canon = "I can't wait for 3 days."
    aj = {"state": "PASS_WITH_WARNING", "warnings": [uj.W_SECONDARY_CONFIRMED], "adapter": {"layers": ["non_latin"]},
          "primary": {"text": NL_PRIMARY, "passed": True}, "secondary": {"text": canon}}
    e = {"asr_text": NL_PRIMARY, "text": canon, "sha256": "abc", "asr_judgement": aj}
    rj = vi.rejudge_with_current_judge(e, "b1b", "kp1_english")
    assert rj["ok"] is True and rj["secondary_new_calls"] == 0


# ============================================================
# (b) Secondary障害の網羅
# ============================================================
CANON_B = "Ottoni and colleagues published a study."
PRIMARY_NG_B = "A Tony and colleagues published a study."


@pytest.mark.parametrize("mode,az", [
    ("err", Az((None, "azure error"))),
    ("exception", Az(raises=ValueError("sdk boom"))),
    ("timeout", Az((None, "連続認識がtimeout(90.0秒)内に完了しませんでした"))),
    ("empty", Az(("", None))),
    ("canceled", Az((None, "CancellationReason.Error: auth"))),
])
def test_b_every_failure_mode_is_ng_secondary_unavailable(tmp_path, monkeypatch, mode, az):
    d = run(CANON_B, PRIMARY_NG_B, _wav(tmp_path), az, monkeypatch)
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE, mode
    assert d.get("technical_stop")


@pytest.mark.parametrize("layer", ["non_latin", "tier3"])
def test_b_exception_in_each_layer_does_not_propagate_and_is_unavailable(tmp_path, monkeypatch, layer):
    az = Az(raises=OSError("network down"))
    if layer == "non_latin":
        d = run("Roasting beans.", NL_PRIMARY, _wav(tmp_path), az, monkeypatch, enable_non_latin_cascade=True)
    else:
        d = run(CANON_B, PRIMARY_NG_B, _wav(tmp_path), az, monkeypatch, segment_id="full_story_part1")
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_SECONDARY_UNAVAILABLE


def test_b_azure_shared_call_converts_exception_to_outcome(tmp_path, monkeypatch):
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(raises=KeyError("x")))
    az = sec._AzureShared(_wav(tmp_path), "en-US", None, "shaX", uj.SecondaryCache())
    out = az.outcome()
    assert out.text is None and "KeyError" in out.error


@pytest.mark.parametrize("msg", ["init_logger()が呼ばれていません", "[STOP] Azure STT単価未登録(pricing_snapshot.json)"])
def test_b_cost_logger_config_errors_are_reraised_not_swallowed(tmp_path, monkeypatch, msg):
    # adapter経由(_AzureShared._call)
    with pytest.raises(RuntimeError):
        run(CANON_B, PRIMARY_NG_B, _wav(tmp_path), Az(raises=RuntimeError(msg)), monkeypatch)
    # judge直(secondary_fnが設定不備を投げた場合)
    pr = uj.PrimaryResult(passed=False, text=PRIMARY_NG_B, label="UNCERTAIN")

    def boom(_c):
        raise RuntimeError(msg)
    with pytest.raises(RuntimeError):
        uj.unified_judge(uj.AttemptCtx(canonical_text=CANON_B, wav_sha256="s9"), pr, boom, lang="en", role=None)

    # 通常のRuntimeErrorは障害扱い(再送出しない)
    def other(_c):
        raise RuntimeError("some runtime failure")
    r = uj.unified_judge(uj.AttemptCtx(canonical_text=CANON_B, wav_sha256="s10"), pr, other, lang="en", role=None)
    assert r.state == uj.NG_SECONDARY_UNAVAILABLE


def test_b_ja_legacy_scg_path_reraises_config_stop(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("[STOP] Azure STT単価未登録")
    monkeypatch.setattr(ja, "_azure_stt_strict", boom)
    with pytest.raises(RuntimeError):
        ja._run_scg_secondary_confirm("テストです。", "dummy.wav", None)


class _Sig:
    def __init__(self):
        self.handlers = []

    def connect(self, h):
        self.handlers.append(h)

    def fire(self, evt):
        for h in self.handlers:
            h(evt)


def _install_fake_speechsdk(monkeypatch, events):
    """events: [("recognized", text) | ("canceled", reason_name) | ("stopped",)] を start時に順に発火するfake SDK。"""
    class ResultReason:
        RecognizedSpeech = "RecognizedSpeech"

    class CancellationReason:
        Error = "Error"
        EndOfStream = "EndOfStream"

    class Recognizer:
        def __init__(self, speech_config=None, audio_config=None):
            self.recognized, self.session_stopped, self.canceled = _Sig(), _Sig(), _Sig()

        def start_continuous_recognition(self):
            for ev in events:
                if ev[0] == "recognized":
                    self.recognized.fire(types.SimpleNamespace(result=types.SimpleNamespace(reason="RecognizedSpeech", text=ev[1])))
                elif ev[0] == "canceled":
                    self.canceled.fire(types.SimpleNamespace(cancellation_details=types.SimpleNamespace(
                        reason=ev[1], error_details="auth failure")))
                else:
                    self.session_stopped.fire(types.SimpleNamespace())

        def stop_continuous_recognition(self):
            pass

    speech = types.ModuleType("azure.cognitiveservices.speech")
    speech.SpeechConfig = lambda **k: types.SimpleNamespace()
    speech.audio = types.SimpleNamespace(AudioConfig=lambda **k: None)
    speech.SpeechRecognizer = Recognizer
    speech.PhraseListGrammar = types.SimpleNamespace(from_recognizer=lambda r: types.SimpleNamespace(addPhrase=lambda p: None))
    speech.ResultReason, speech.CancellationReason = ResultReason, CancellationReason
    pkg_c = types.ModuleType("azure.cognitiveservices")
    pkg_c.speech = speech
    pkg_a = sys.modules.get("azure") or types.ModuleType("azure")
    monkeypatch.setitem(sys.modules, "azure", pkg_a)
    monkeypatch.setattr(pkg_a, "cognitiveservices", pkg_c, raising=False)   # `import a.b.c as m`は属性連鎖で解決される
    monkeypatch.setitem(sys.modules, "azure.cognitiveservices", pkg_c)
    monkeypatch.setitem(sys.modules, "azure.cognitiveservices.speech", speech)
    monkeypatch.setenv("SPEECH_KEY", "k")
    monkeypatch.setenv("SPEECH_REGION", "r")
    monkeypatch.setattr(sec.cl, "record", lambda rec: None)


def test_b_en_azure_canceled_error_with_partial_transcript_is_error_not_pass_basis(tmp_path, monkeypatch):
    _install_fake_speechsdk(monkeypatch, [("recognized", "partial text only"), ("canceled", "Error")])
    text, err = sec.get_full_text_via_azure_stt_with_phrase_list(_wav(tmp_path), language="en-US", timeout_seconds=5)
    assert text is None and err and err.startswith("CancellationReason.Error")        # 部分転写をerr=Noneで返さない(SDK読込失敗等ではない)


def test_b_en_azure_canceled_end_of_stream_is_normal(tmp_path, monkeypatch):
    _install_fake_speechsdk(monkeypatch, [("recognized", "full text"), ("canceled", "EndOfStream")])
    text, err = sec.get_full_text_via_azure_stt_with_phrase_list(_wav(tmp_path), language="en-US", timeout_seconds=5)
    assert text == "full text" and err is None


def test_b_en_azure_session_stopped_is_normal(tmp_path, monkeypatch):
    _install_fake_speechsdk(monkeypatch, [("recognized", "ok text"), ("stopped",)])
    text, err = sec.get_full_text_via_azure_stt_with_phrase_list(_wav(tmp_path), language="en-US", timeout_seconds=5)
    assert text == "ok text" and err is None


# ============================================================
# (c) 再利用経路の値ガード
# ============================================================
TXT = "The study followed 2 groups of participants."
TXT_BAD = "The study followed 3 groups of participants."
E_OK = {"status": "OK", "asr_verified": True, "text": TXT, "canonical_text": TXT, "asr_text": TXT}
E_VAL = dict(E_OK, asr_text=TXT_BAD)
E_NEG = {"status": "OK", "asr_verified": True, "text": "We do not go there today.", "canonical_text": "We do not go there today.",
         "asr_text": "We go there today."}


def test_c_guard_entry_blocks_value_diff_and_negation_diff_allows_ok_and_untranscribed():
    assert rvg.guard_entry(E_VAL, label="point_one")["blocked"] is True
    g = rvg.guard_entry(E_NEG, label="comment_1")
    assert g["blocked"] is True and "negation" in g["reason"]
    ok = rvg.guard_entry(E_OK, label="point_one")
    assert ok["blocked"] is False and ok["reason"] == "REJUDGE_OK" and ok["api_calls"] == 0 and ok["secondary_new_calls"] == 0
    assert rvg.guard_entry({"status": "OK", "text": TXT}, label="x")["blocked"] is False    # 転写なし=判定不能=従来どおり
    assert rvg.guard_entry(dict(E_OK, reuse_blocked={"by": "bulk"}), label="x")["blocked"] is True


def test_c_try_inherit_from_cached_refuses_diff_and_inherits_ok(tmp_path):
    wav = _wav(tmp_path)
    sha = hashlib.sha256(open(wav, "rb").read()).hexdigest()
    for entry, expect_none in ((dict(E_OK, sha256=sha), False), (dict(E_VAL, sha256=sha), True)):
        got = vi.try_inherit_from_cached(entry, wav, TXT, "v1", "v1", {"kind": "t", "label": "point_one"})
        assert (got is None) == expect_none


def test_c_x_runner_generate_or_reuse_regenerates_on_diff_and_reuses_ok(tmp_path, monkeypatch):
    wav = _wav(tmp_path)
    monkeypatch.setattr(x_runner, "_only_segments_skip", lambda name: None)
    calls = []

    def gen():
        calls.append(1)
        return {"status": "OK", "regenerated": True}
    ver = x_runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION
    cached_ok = {"style_version": ver, "segments": {"point_one": dict(E_OK)}}
    cached_bad = {"style_version": ver, "segments": {"point_one": dict(E_VAL)}}
    r1 = x_runner._generate_or_reuse(cached_ok, "point_one", wav, gen, expected_text=TXT)
    assert r1.get("reused_from_previous_run") is True and calls == []
    r2 = x_runner._generate_or_reuse(cached_bad, "point_one", wav, gen, expected_text=TXT)
    assert r2.get("regenerated") is True and calls == [1] and r2["reuse_value_guard_blocked_previous"]["reason"].startswith("PROTECTED_DIFF")


def test_c_x_runner_kp_reuse_guard(tmp_path, monkeypatch):
    wav = _wav(tmp_path)
    monkeypatch.setattr(x_runner, "_only_segments_skip", lambda name: None)
    calls = []

    def gen():
        calls.append(1)
        return {"status": "OK", "regenerated": True}
    cached = {"key_phrases": {"1": {"english": dict(E_VAL)}}}
    r = x_runner._generate_or_reuse_kp(cached, 1, "english", wav, gen, expected_text=TXT)
    assert r.get("regenerated") is True and calls == [1]


def _patch_store(monkeypatch, tmp_path):
    d = tmp_path / "store"
    monkeypatch.setattr(store, "STORE_DIR", str(d))
    monkeypatch.setattr(store, "AUDIO_DIR", str(d / "audio"))
    monkeypatch.setattr(store, "MANIFEST_PATH", str(d / "manifest.json"))
    monkeypatch.setattr(store, "TELEMETRY_PATH", str(d / "reuse_telemetry.jsonl"))


def test_c_master_audio_store_reuse_guard(tmp_path, monkeypatch):
    _patch_store(monkeypatch, tmp_path)
    key = store.MasterAudioKey("en", "Charon", "m", TXT, style_instruction_id="s")
    for asr, expect_reused in ((TXT, True), (TXT_BAD, False)):
        os.makedirs(store.AUDIO_DIR, exist_ok=True)
        mid = key.master_audio_id()
        stored = f"{store.AUDIO_DIR}/{mid}.wav"
        open(stored, "wb").write(b"RIFFold")
        json.dump({mid: {"audio_path": stored, "key": key.as_dict(), "qa_evidence": {"asr_text": asr, "sha256": "x"}}},
                  open(store.MANIFEST_PATH, "w", encoding="utf-8"))
        calls = []

        def gen(out):
            calls.append(1)
            open(out, "wb").write(b"RIFFnew")
            return {"status": "OK", "sha256": "n", "asr_verified": True, "asr_text": TXT}
        r = store.get_or_generate(key, str(tmp_path / f"out_{expect_reused}.wav"), gen)
        assert r["reused"] is expect_reused and bool(calls) is (not expect_reused)
        if not expect_reused:
            assert any(f.startswith(mid) for f in os.listdir(f"{store.AUDIO_DIR}/_reuse_blocked"))   # 旧音声は削除せず退避


def test_c_master_audio_store_honours_reuse_blocked_mark(tmp_path, monkeypatch):
    _patch_store(monkeypatch, tmp_path)
    key = store.MasterAudioKey("en", "Charon", "m", TXT, style_instruction_id="s2")
    os.makedirs(store.AUDIO_DIR, exist_ok=True)
    mid = key.master_audio_id()
    stored = f"{store.AUDIO_DIR}/{mid}.wav"
    open(stored, "wb").write(b"RIFFold")
    json.dump({mid: {"audio_path": stored, "key": key.as_dict(), "qa_evidence": {"asr_text": TXT}, "reuse_blocked": {"by": "bulk"}}},
              open(store.MANIFEST_PATH, "w", encoding="utf-8"))
    calls = []

    def gen(out):
        calls.append(1)
        open(out, "wb").write(b"x")
        return {"status": "OK"}
    r = store.get_or_generate(key, str(tmp_path / "o.wav"), gen)
    assert r["reused"] is False and calls == [1]


def test_c_z_generate_or_reuse_z_guard(tmp_path):
    spec = z_audio.ClipSpec(clip_id="point_one", level="a2", kind="narrator", text=TXT, voice="Charon", role_key="NARRATOR_FULL_STORY_STD")
    wav = _wav(tmp_path)
    key = z_audio.build_reuse_key(spec)
    gen_calls = []

    def gen():
        gen_calls.append(1)
        return {"status": "OK", "regenerated": True}
    ok = dict(E_OK, reuse_key=key)
    bad = dict(E_VAL, reuse_key=key)
    assert z_audio.generate_or_reuse_z(ok, spec, wav, gen).get("reused_from_previous_run") is True and gen_calls == []
    r = z_audio.generate_or_reuse_z(bad, spec, wav, gen)
    assert r.get("regenerated") is True and gen_calls == [1]


def test_c_c_runner_resumable_reuse_guard(tmp_path):
    out = str(tmp_path / "seg.wav")
    open(out, "wb").write(b"RIFFdata")
    sha_text = c_runner._sha256_text(TXT)
    open(out + ".ok", "w").write("ok")
    wsha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    for asr, expect in ((TXT, True), (TXT_BAD, False)):
        aj = {"state": "PASS", "primary": {"text": asr, "passed": True}, "warnings": []}
        json.dump({"tts_text_sha256": sha_text, "wav_sha256": wsha, "asr_judgement": aj}, open(out + ".ok.meta.json", "w"))
        got = c_runner.resumable_reuse(out, sha_text, TXT)
        assert (got is not None) is expect


def test_c_bulk_script_find_entries():
    import er078_auw_reuse_bulk_rejudge_06c as bulk
    data = {"segments": {"a": dict(E_OK), "b": dict(E_VAL, status="STOPPED")}, "key_phrases": {"1": {"english": dict(E_VAL)}}}
    found = list(bulk.find_entries(data))
    assert [p for p, _ in found] == ["/segments/a", "/key_phrases/1/english"]       # STOPPEDは対象外


# ============================================================
# (d) Secondary障害は技術STOP、HR Lockにしない
# ============================================================
def test_d_en_last_slot_secondary_only_failure_is_technical_stop_not_hr(tmp_path, monkeypatch):
    logged = []
    monkeypatch.setattr(sec, "_log_human_review", lambda d: logged.append(d))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az((None, "azure down")))
    d = sec.evaluate_attempt_with_cascade_detail(CANON_B, PRIMARY_NG_B, [], _wav(tmp_path), cascade_enabled=True,
                                                 attempt_ctx={"slot": 3, "is_last_slot": True})
    assert d["verified"] is False and d["human_review_required"] is False
    assert d["technical_stop"] and d["technical_stop_status"] == "TECHNICAL_STOP_SECONDARY_UNAVAILABLE"
    assert d["technical_stop"].get("restartable") is True and d["technical_stop"].get("approval_required") is False
    sec.evaluate_attempt_with_cascade(CANON_B, PRIMARY_NG_B, [], _wav(tmp_path, "b.wav"), cascade_enabled=True,
                                      attempt_ctx={"slot": 3, "is_last_slot": True})
    assert logged == []                                                      # wrapperもHR queueへ投入しない


def test_d_en_last_slot_real_ng_still_goes_to_hr(tmp_path, monkeypatch):
    monkeypatch.setattr(sec, "_log_human_review", lambda d: None)
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", Az(("Completely unrelated sentence here.", None)))
    d = sec.evaluate_attempt_with_cascade_detail(CANON_B, PRIMARY_NG_B, [], _wav(tmp_path), cascade_enabled=True,
                                                 attempt_ctx={"slot": 3, "is_last_slot": True})
    assert d["verified"] is False and d["asr_judgement"]["state"] == uj.NG_BOTH
    assert d["human_review_required"] is True and "technical_stop_status" not in d


def test_d_ja_last_slot_secondary_only_failure_is_technical_stop_not_hr(tmp_path, monkeypatch):
    import er007_ja_asr_validator_01 as javal
    monkeypatch.setattr(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False)
    monkeypatch.setattr(ja, "_azure_stt_strict", lambda *a, **k: (None, "azure down"))
    canon = "AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした"
    d = ja.evaluate_attempt_ja_with_cascade_detail(canon, "AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。", _wav(tmp_path),
                                                   cascade_enabled=True, attempt_ctx={"slot": 3, "is_last_slot": True})
    assert d["verified"] is False and d["human_review_required"] is False
    assert d["technical_stop_status"] == "TECHNICAL_STOP_SECONDARY_UNAVAILABLE"


def test_d_runner_stops_remaining_clips_when_circuit_open_and_reports(capsys):
    sec.begin_secondary_run()
    try:
        called = []

        def fn():
            called.append(1)
            return {"status": "OK"}
        g = scope.guard_generate(fn, "clip_a")
        assert g() == {"status": "OK"} and called == [1]                       # open前は通常
        rs = sec._RUN_STATE
        rs.circuit_open = True
        rs.technical_stop_events.append({"type": "SECONDARY_CIRCUIT_OPEN", "restartable": True, "approval_required": False})
        e = g()
        assert e["status"] == scope.TECHNICAL_STOP_STATUS and e["human_review_required"] is False
        assert e["restartable"] is True and e["approval_required"] is False and called == [1]   # TTS/ASRを呼ばない
        scope._report_technical_stop(sec)
        assert "[TECHNICAL_STOP]" in capsys.readouterr().out
    finally:
        sec.end_secondary_run()


def test_d_x_and_z_and_c_choke_points_stop_when_circuit_open(tmp_path, monkeypatch):
    monkeypatch.setattr(x_runner, "_only_segments_skip", lambda name: None)
    sec.begin_secondary_run()
    sec._RUN_STATE.circuit_open = True
    try:
        calls = []

        def gen():
            calls.append(1)
            return {"status": "OK"}
        assert x_runner._generate_or_reuse(None, "point_one", _wav(tmp_path), gen)["status"] == scope.TECHNICAL_STOP_STATUS
        assert x_runner._generate_or_reuse_kp(None, 1, "english", _wav(tmp_path), gen)["status"] == scope.TECHNICAL_STOP_STATUS
        spec = z_audio.ClipSpec(clip_id="p1", level="a2", kind="narrator", text=TXT, voice="Charon", role_key="NARRATOR_FULL_STORY_STD")
        assert z_audio.generate_or_reuse_z(None, spec, _wav(tmp_path), gen)["status"] == scope.TECHNICAL_STOP_STATUS

        class B:
            def check_before(self, *a):
                pass
        r = c_runner.tts_call_for_voice("narrator", TXT, str(tmp_path / "c.wav"), "lbl", B(), {})
        assert r["status"] == scope.TECHNICAL_STOP_STATUS
        assert calls == []
        assert vi._OVERWRITABLE_STATUSES.count(scope.TECHNICAL_STOP_STATUS) == 1   # 再実行で再生成
    finally:
        sec.end_secondary_run()


# ============================================================
# (e) 試聴リスト導出失敗の表示
# ============================================================
def test_e_listening_list_failure_is_not_reported_as_zero(tmp_path):
    run_dir = tmp_path / "run"
    (run_dir / "audit").mkdir(parents=True)
    (run_dir / "audit" / "tts_generation_results.json").write_text("{ broken json", encoding="utf-8")
    got = reg.load_listening_list(str(run_dir))
    assert got != [] and isinstance(got, reg.ListeningListDerivationFailed) and list(got) == [] and not got
    html = reg.render_html_section(got)
    assert "導出失敗(要確認)" in html and "0件(該当なし" not in html
    # 結果ファイル自体が無い=そのrunにWARNING対象なし=従来どおり0件
    empty = reg.load_listening_list(str(tmp_path / "norun"))
    assert empty == [] and "0件(該当なし" in reg.render_html_section(empty)
    # 単独HTML(legacy hook)も失敗を表示
    rep = reg.write_listening_list_safe(str(run_dir), standalone_html=True)
    assert rep["error"] and "導出失敗(要確認)" in open(rep["html"], encoding="utf-8").read()


# ============================================================
# (g) flag OFF(cascade_enabled=False)はロールバック経路として旧挙動に戻る
# ============================================================
def test_g_flag_off_returns_legacy_behaviour_and_stop_retrying_is_reachable(tmp_path, monkeypatch):
    az = Az(("never", None))
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", az)
    canon, asr = CANON_B, PRIMARY_NG_B
    prior = []
    last = None
    for _ in range(3):
        last = sec.evaluate_attempt_with_cascade_detail(canon, asr, prior, _wav(tmp_path), cascade_enabled=False)
    assert "asr_judgement" not in last and last["cascade_invoked"] is False and az.calls == 0      # 統一judge/Secondaryを通らない
    assert last["stop_retrying"] is True and last["verified"] is False                          # 旧: 同一signature連続で打切り(到達可能)
    on = sec.evaluate_attempt_with_cascade_detail(canon, asr, [], _wav(tmp_path, "c.wav"), cascade_enabled=True)
    assert on["stop_retrying"] is False and "asr_judgement" in on                               # flag ON(既定)はstop_retrying=False固定


def test_g_leaf_stop_retrying_branches_retained_as_flag_off_rollback_and_flag_default_on():
    leaves = ["er003_v1_sing01_voice01_generate.py", "er003_v1_sing01_news_tail_fix.py", "er003_v1_sing01_point_headings_aoede.py",
              "er012_b_family_voices_production_01.py", "er003_v1_repro01_main_generate.py", "er003_v1_n3_01_tts_generate.py"]
    n = sum(len(re.findall(r"^\s+if stop_retrying:", open(f, encoding="utf-8").read(), re.M)) for f in leaves)
    assert n == 8                                  # 委任_05記録どおり残置(flag OFF=ロールバック経路。削除しない)
    assert sec.FEATURE_FLAG_SECONDARY_ASR_ENABLED is True


def test_g_dead_rescue_function_removed():
    assert not hasattr(n3_tts, "_post_slowdown_cascade_rescue")
    assert hasattr(n3_tts, "_post_slowdown_unified_judge")


# ============================================================
# (h) Dialogue(Std)/Voices A2の外側ループ(通算TTS3回)
# ============================================================
def test_h_outer_loop_regenerates_after_slowdown_ng_within_total_budget_3(tmp_path, monkeypatch):
    seq = []

    def fake_post(name, nd, text, result, is_last_slot=True, **kw):
        seq.append(is_last_slot)
        return dict(result, status="OK" if len(seq) == 2 else "STOPPED")      # 1回目の減速後NG、2回目OK
    monkeypatch.setattr(n3_tts, "apply_a2_slowdown_postprocess", fake_post)
    monkeypatch.setattr(n3_tts.review_lock, "append_attempt_history_event", lambda *a, **k: None)
    budgets = []

    def gen(max_attempts):
        budgets.append(max_attempts)
        return {"status": "OK", "attempts_log": [{"a": 1}]}                    # 1回消費
    r = n3_tts.generate_with_a2_slowdown_outer_loop("p1", "text", str(tmp_path / "x.wav"), gen)
    assert r["status"] == "OK" and budgets == [3, 2] and seq == [False, False]
    assert r["tts_generations_used"] == 2 and len(r["slowdown_attempts_log"]) == 2


def test_h_outer_loop_caps_at_total_3_and_last_slot_flag(tmp_path, monkeypatch):
    seq = []

    def fake_post(name, nd, text, result, is_last_slot=True, **kw):
        seq.append(is_last_slot)
        return dict(result, status="STOPPED")
    monkeypatch.setattr(n3_tts, "apply_a2_slowdown_postprocess", fake_post)
    monkeypatch.setattr(n3_tts.review_lock, "append_attempt_history_event", lambda *a, **k: None)
    budgets = []

    def gen(max_attempts):
        budgets.append(max_attempts)
        return {"status": "OK", "attempts_log": [{"a": 1}]}
    r = n3_tts.generate_with_a2_slowdown_outer_loop("p1", "text", str(tmp_path / "x.wav"), gen)
    assert budgets == [3, 2, 1] and r["status"] == "STOPPED" and r["tts_generation_cap_reached"] is True   # 4回目は絶対に生成しない
    assert seq == [False, False, True]                                                                    # 通算3回目のみ最終slot(HR対象)


def test_h_outer_loop_stops_when_inner_fails(tmp_path, monkeypatch):
    def fail(*a, **k):
        pytest.fail("内側失敗なら減速後判定へ進まない")
    monkeypatch.setattr(n3_tts, "apply_a2_slowdown_postprocess", fail)
    monkeypatch.setattr(n3_tts.review_lock, "append_attempt_history_event", lambda *a, **k: None)
    r = n3_tts.generate_with_a2_slowdown_outer_loop("p1", "t", str(tmp_path / "x.wav"),
                                                    lambda m: {"status": "STOPPED", "attempts_log": [1, 2]})
    assert r["status"] == "STOPPED"


def test_h_dialogue_std_and_voices_a2_use_outer_loop_with_prompt_unchanged(tmp_path, monkeypatch):
    import er012_b_family_voices_a2_production_01 as a2prod
    import er012_b_family_voices_production_01 as bvoices
    seen = []

    def fake_body(text, out, voice, max_attempts=3, **kw):
        seen.append((voice, max_attempts, kw.get("style_prefix_override")))
        return {"status": "OK", "attempts_log": [{"a": 1}]}
    monkeypatch.setattr(bvoices, "generate_voice_body_wide_margin", fake_body)
    monkeypatch.setattr(n3_tts, "apply_a2_slowdown_postprocess",
                        lambda name, nd, text, result, is_last_slot=True, **kw: dict(result, status="OK"))
    monkeypatch.setattr(n3_tts.review_lock, "append_attempt_history_event", lambda *a, **k: None)
    a2prod.generate_voice_body_wide_margin_with_a2_slowdown("point_one", "t", str(tmp_path / "x.wav"), "Puck")
    gens = z_audio.real_generators()
    spec = z_audio.ClipSpec(clip_id="dlg1", level="a2", kind="dialogue", text="Hello there.", voice="Puck", speaker="A")
    gens["dialogue"](spec, str(tmp_path / "d.wav"))
    # [Voices A2=SLOWER維持, Z Std Dialogue=None(2026-10-19決定③: Adv同一の既定Style)]
    assert [s[2] for s in seen] == [n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER, None] and [s[0] for s in seen] == ["Puck", "Puck"]
