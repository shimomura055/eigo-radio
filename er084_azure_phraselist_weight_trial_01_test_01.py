# -*- coding: utf-8 -*-
"""FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 harness test(API 0。SDKはmock)。"""
import json
import os
import types

import pytest

import er084_azure_phraselist_weight_trial_01_lib as L
import er084_azure_phraselist_weight_trial_01_run as R
import er084_azure_phraselist_weight_trial_01_eval as E

DESIGN = os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01", "design_matrix_01.json")
REC2 = os.path.join(L.ROOT, "er026_output", "family_z_production_e2e_01", "melos", "run_e2e_04", "a2", "narration",
                    "attempts", "full_story_part3_c1_attempt2_customa3c4625e.wav")


class _Ev:
    def __init__(self):
        self._h = []

    def connect(self, f):
        self._h.append(f)

    def fire(self, *a):
        for f in self._h:
            f(*a)


def make_fake_sdk(calls, text="He drank Mellows drank"):
    class Grammar:
        @classmethod
        def from_recognizer(cls, rec):
            g = cls()
            calls["grammar"] = g
            g.phrases, g.weight = [], "UNSET"
            return g

        def addPhrase(self, p):
            self.phrases.append(p)

        def setWeight(self, w):
            self.weight = w

    class Rec:
        def __init__(self, speech_config, audio_config):
            self.recognized, self.session_stopped, self.canceled = _Ev(), _Ev(), _Ev()

        def start_continuous_recognition(self):
            res = types.SimpleNamespace(reason="RS", text=text, json=json.dumps({"DisplayText": text}))
            self.recognized.fire(types.SimpleNamespace(result=res))
            self.session_stopped.fire(types.SimpleNamespace())

        def stop_continuous_recognition(self):
            pass

    class Cfg:
        def __init__(self, subscription, region):
            self.props = {}

        def set_property(self, k, v):
            self.props[k] = v

    sdk = types.SimpleNamespace(
        SpeechConfig=Cfg, SpeechRecognizer=Rec, PhraseListGrammar=Grammar,
        PropertyId=types.SimpleNamespace(Speech_LogFilename="LOGF"),
        audio=types.SimpleNamespace(AudioConfig=lambda filename: filename),
        ResultReason=types.SimpleNamespace(RecognizedSpeech="RS"),
        CancellationReason=types.SimpleNamespace(Error="ERR"))
    return sdk


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("SPEECH_KEY", "dummy")
    monkeypatch.setenv("SPEECH_REGION", "dummy")


def test_weight_passed_to_sdk_and_unspecified_not_called():
    for w, expect in [(None, "UNSET"), (1.0, 1.0), (1.5, 1.5), (2.0, 2.0)]:
        calls = {}
        r = L.azure_transcribe("x.wav", ["Melos"], w, speechsdk=make_fake_sdk(calls))
        assert calls["grammar"].phrases == ["Melos"]
        assert calls["grammar"].weight == expect
        assert r["weight_call"] == (None if w is None else float(w))


def test_no_pl_creates_no_grammar():
    calls = {}
    L.azure_transcribe("x.wav", None, None, speechsdk=make_fake_sdk(calls))
    assert "grammar" not in calls


def test_condition_table_is_fixed():
    assert [L.cond_spec(c) for c in L.COND_NAMES] == [
        {"use_pl": False, "weight": None}, {"use_pl": True, "weight": None},
        {"use_pl": True, "weight": 1.0}, {"use_pl": True, "weight": 1.5}, {"use_pl": True, "weight": 2.0}]


def test_classify_melos():
    assert L.classify_melos("Melos drank")["melos"] is True
    c = L.classify_melos("Mellows drank")
    assert c["melos"] is False and c["wrong"] == ["mellows"]
    assert L.classify_melos("The mellow sound")["wrong"] == ["mellow"]
    assert L.classify_melos(None) == {"melos": False, "wrong": []}


def test_extract_weight_evidence(tmp_path):
    p = tmp_path / "s.log"
    p.write_text("a\nname='SPEECH-PhraseListWeight'; value='2.000000'\n"
                 "speech.context='{\"dgi\":{\"Groups\":[],\"bias\":2.000000}}'\n", encoding="utf-8")
    ev = L.extract_weight_evidence(str(p))
    assert ev["prop_weight"] == ["2.000000"] and ev["wire_bias"] == ["2.000000"] and ev["wire_has_dgi"] is True
    assert L.extract_weight_evidence(str(tmp_path / "none.log")) == {"log_exists": False}


def test_build_calls_phase_a_is_15_and_interleaved():
    design = json.load(open(DESIGN, encoding="utf-8"))
    calls = R.build_calls(design, "A")
    assert len(calls) == 15
    assert [c["cond"] for c in calls[:5]] == list(L.COND_NAMES) and calls[0]["rep"] == 1 and calls[5]["rep"] == 2
    with pytest.raises(SystemExit):
        R.build_calls(design, "B")


def test_dry_run_estimates_and_writes_nothing(tmp_path, capsys):
    if not os.path.exists(REC2):
        pytest.skip("録音2 wav無(ローカルのみ)")
    rc = R.main(["--design", DESIGN, "--phase", "A", "--out", str(tmp_path), "--budget-jpy", "30", "--dry-run"])
    out = capsys.readouterr().out
    assert rc == 0 and '"n_calls": 15' in out
    assert not (tmp_path / "raw").exists()
    assert R.main(["--design", DESIGN, "--phase", "A", "--out", str(tmp_path), "--budget-jpy", "1", "--dry-run"]) == 2


def _row(aid, cond, rep, text):
    return {"audio_id": aid, "cond": cond, "rep": rep, "text": text, "err": None, "wav_path": "x.wav",
            "cls": L.classify_melos(text), "wire_evidence": {"wire_bias": ["1.000000"], "wire_has_dgi": True}}


def test_aggregate_positive_negative_and_no_exclusion():
    rows = [_row("P", "pl_w2.0", 1, "Melos drank"), _row("P", "pl_w2.0", 2, "Mellows drank"),
            _row("N", "pl_w2.0", 1, "Melos walked"), _row("N", "pl_w2.0", 2, "Mellow walked"),
            _row("P", "no_pl", 1, "Mello drank")]
    meta = {"P": {"label": "positive", "expected_melos": 1}, "N": {"label": "negative", "expected_melos": 0}}
    agg = E.aggregate(rows, meta)
    assert agg["n_rows"] == 5
    cell = {(c["audio_id"], c["cond"]): c for c in agg["cells"]}
    assert cell[("P", "pl_w2.0")]["correct"] == 1 and cell[("P", "pl_w2.0")]["distinct_transcripts"] == 2
    assert cell[("N", "pl_w2.0")]["false_melos"] == 1 and cell[("N", "pl_w2.0")]["correct"] == 1
    rates = E.rates_by_condition(agg)
    assert rates["pl_w2.0"]["positive_rate"] == 0.5 and rates["pl_w2.0"]["negative_false_rate"] == 0.5
    assert rates["no_pl"]["positive_rate"] == 0.0
    assert sum(c["n_calls"] for c in agg["cells"]) == 5  # 除外なし


def test_judge_offline_matches_production_and_no_side_effects():
    import er006_secondary_asr_01 as sec
    import er084_azure_phraselist_weight_trial_01_judge as J
    canon = ("He remembered the hands held out for the chains. Water came slowly through a crack in the rock. "
             "Melos drank, got onto his knees, and stood up.")
    prim = canon.replace("Melos", "Mello")
    hr = getattr(sec, "HUMAN_REVIEW_LOG_PATH", None)
    before = os.path.getsize(hr) if hr and os.path.exists(hr) else None
    orig = sec.get_full_text_via_azure_stt_with_phrase_list
    ng = J.judge_offline(canon, prim, canon.replace("Melos", "Mellows"), "x.wav")
    ok = J.judge_offline(canon, prim, canon, "x.wav")
    assert ng["state"] == "NG_BOTH" and ng["verified"] is False and ng["fake_azure_calls"] == 1
    assert ok["state"] == "PASS_WITH_WARNING" and ok["verified"] is True
    assert sec.get_full_text_via_azure_stt_with_phrase_list is orig  # 差替えは復元される
    after = os.path.getsize(hr) if hr and os.path.exists(hr) else None
    assert before == after


def test_cost_estimate_formula():
    assert abs(L.est_jpy(3600) - 160.0) < 1e-9
