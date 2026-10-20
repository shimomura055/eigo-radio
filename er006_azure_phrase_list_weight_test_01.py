# -*- coding: utf-8 -*-
"""Azure Phrase List重み2.0 Production配線test(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01)。API 0。
2026-10-20ユーザー APPROVED_FOR_PRODUCTION。SDK(azure.cognitiveservices.speech)はmock、Azure呼出なし。"""
import os
import sys
import wave

import pytest

sys.path.insert(0, os.getcwd())
import azure.cognitiveservices.speech as speechsdk  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402


class _Evt:
    def __init__(self):
        self.cbs = []

    def connect(self, f):
        self.cbs.append(f)


class FakeRec:
    last = None

    def __init__(self, speech_config=None, audio_config=None):
        self.recognized, self.session_stopped, self.canceled = _Evt(), _Evt(), _Evt()
        FakeRec.last = self

    def start_continuous_recognition(self):
        for f in self.session_stopped.cbs:
            f("stopped")

    def stop_continuous_recognition(self):
        pass


class FakeGrammar:
    instances = []

    def __init__(self):
        self.phrases, self.weights = [], []
        FakeGrammar.instances.append(self)

    @classmethod
    def from_recognizer(cls, rec):
        return cls()

    def addPhrase(self, p):
        self.phrases.append(p)

    def setWeight(self, w):
        self.weights.append(w)


@pytest.fixture()
def wav(tmp_path):
    p = tmp_path / "a.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 1600)
    return str(p)


@pytest.fixture(autouse=True)
def _sdk(monkeypatch):
    FakeGrammar.instances = []
    monkeypatch.setenv("SPEECH_KEY", "k")
    monkeypatch.setenv("SPEECH_REGION", "r")
    monkeypatch.setattr(speechsdk, "SpeechRecognizer", FakeRec)
    monkeypatch.setattr(speechsdk, "PhraseListGrammar", FakeGrammar)
    monkeypatch.setattr(speechsdk.audio, "AudioConfig", lambda filename=None: object())
    monkeypatch.setattr(sec.cl, "record", lambda *a, **k: None)
    import dotenv
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **k: False)


def test_const_is_2_0():
    assert sec.AZURE_PHRASE_LIST_WEIGHT == 2.0
    assert sec.CASCADE_CONFIG["phrase_list_weight"] == 2.0


def test_set_weight_called_with_phrases(wav):
    sec.get_full_text_via_azure_stt_with_phrase_list(wav, phrases=["Melos", "Selinuntius"])
    g = FakeGrammar.instances[0]
    assert g.phrases == ["Melos", "Selinuntius"] and g.weights == [2.0]


@pytest.mark.parametrize("ph", [None, []])
def test_no_phrase_list_when_empty(wav, ph):
    sec.get_full_text_via_azure_stt_with_phrase_list(wav, phrases=ph)
    assert FakeGrammar.instances == []  # PL未作成=bias送信なし(従来どおり)


def test_weight_independent_of_env_and_flags(wav, monkeypatch):
    for k in ("AZURE_PHRASE_LIST_WEIGHT", "PHRASE_LIST_WEIGHT", "AZURE_PL_WEIGHT"):
        monkeypatch.setenv(k, "0.5")
    sec.get_full_text_via_azure_stt_with_phrase_list(wav, phrases=["Melos"])
    assert FakeGrammar.instances[0].weights == [2.0]
    import inspect
    sig = inspect.signature(sec.get_full_text_via_azure_stt_with_phrase_list)
    assert not any("weight" in n for n in sig.parameters)  # 関数引数で迂回不可


def test_audit_keys_additive(monkeypatch):
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", lambda wav, language="en-US", phrases=None: ("Marcus said.", None))
    d = sec.evaluate_attempt_with_cascade_detail("Melos said.", "Marcus said.", [], "dummy.wav", cascade_enabled=True,
                                                 ledger_phrases=["Melos"])
    az = [s for s in d["steps"] if s.get("provider") == "azure"]
    assert az, d["steps"]
    for s in az:
        assert s["azure_phrase_list_weight"] == 2.0 and s["azure_phrase_list"] == ["Melos"]
        # 既存キー不変
        for k in ("step", "provider", "text", "classification", "phrase_list_used"):
            assert k in s
        assert s["phrase_list_used"] is True


def test_audit_none_weight_without_phrases(monkeypatch):
    monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", lambda wav, language="en-US", phrases=None: ("Marcus said.", None))
    d = sec.evaluate_attempt_with_cascade_detail("Melos said.", "Marcus said.", [], "dummy.wav", cascade_enabled=True,
                                                 ledger_phrases=None)
    for s in [s for s in d["steps"] if s.get("provider") == "azure"]:
        assert s["azure_phrase_list_weight"] is None and s["azure_phrase_list"] == [] and s["phrase_list_used"] is False
