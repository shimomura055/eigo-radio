# ============================================================
# er006_asr_provider_routing_01_test.py
# ER-006-ASR-OPENAI-PILOT-01: ASR Provider Routing SSOTのcontract test
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_asr_provider_routing_01_test.py

from __future__ import annotations

import er006_asr_provider_routing_01 as routing
import er003_b1_p4_audio as p4


def test_english_routes_to_openai():
    route = routing.require_asr_route("en-US")
    assert route["provider"] == "openai_asr", route
    assert route["model"] == "gpt-4o-mini-transcribe", route
    print("PASS: test_english_routes_to_openai")


def test_japanese_routes_to_azure():
    route = routing.require_asr_route("ja-JP")
    assert route["provider"] == "azure", route
    print("PASS: test_japanese_routes_to_azure")


def test_unrouted_language_fails_closed_no_call():
    # 未登録言語は例外を送出し、どのASR APIも一切呼ばれないこと。
    try:
        routing.require_asr_route("fr-FR")
        raise AssertionError("UnroutedLanguageErrorが送出されるべき")
    except routing.UnroutedLanguageError:
        pass
    print("PASS: test_unrouted_language_fails_closed_no_call")


def test_transcribe_dispatches_to_azure_for_japanese_no_openai_call():
    # transcribe()がja-JPでAzure(p4)を呼び、OpenAIクライアントを一切
    # 生成しないことを確認する(実際のAzure呼び出し自体はモックする)。
    calls = {"azure": 0, "openai": 0}
    orig_azure = p4.get_full_text_via_azure_stt_continuous

    def fake_azure(*args, **kwargs):
        calls["azure"] += 1
        return "テスト", None

    def fake_get_openai_client():
        calls["openai"] += 1
        raise AssertionError("Japaneseルートでは呼ばれないはず")

    p4.get_full_text_via_azure_stt_continuous = fake_azure
    orig_get_client = routing._get_openai_client
    routing._get_openai_client = fake_get_openai_client
    try:
        text, err = routing.transcribe("dummy.wav", language="ja-JP")
        assert text == "テスト"
        assert calls["azure"] == 1
        assert calls["openai"] == 0
    finally:
        p4.get_full_text_via_azure_stt_continuous = orig_azure
        routing._get_openai_client = orig_get_client
    print("PASS: test_transcribe_dispatches_to_azure_for_japanese_no_openai_call")


def test_transcribe_openai_failure_does_not_fallback_to_azure():
    # English routeでOpenAI呼び出しが失敗した場合、Azureへ黙って
    #切り替わらないこと(fail-closed、暗黙fallback禁止)。
    calls = {"azure": 0}
    orig_azure = p4.get_full_text_via_azure_stt_continuous

    def fake_azure(*args, **kwargs):
        calls["azure"] += 1
        return "SHOULD NOT BE CALLED", None

    class FakeTranscriptions:
        def create(self, *args, **kwargs):
            raise RuntimeError("simulated OpenAI ASR failure")

    class FakeAudio:
        transcriptions = FakeTranscriptions()

    class FakeClient:
        audio = FakeAudio()

    real_wav = "er006_output/pool_pilot_01/pool_benches/h_onset_diagnostic/hostile_repeat1.wav"
    p4.get_full_text_via_azure_stt_continuous = fake_azure
    orig_get_client = routing._get_openai_client
    routing._get_openai_client = lambda: FakeClient()
    try:
        text, err = routing.transcribe(real_wav, language="en-US")
        assert text is None
        assert err is not None and "simulated OpenAI ASR failure" in err
        assert calls["azure"] == 0, "OpenAI失敗時にAzureへ暗黙fallbackしてはならない"
    finally:
        p4.get_full_text_via_azure_stt_continuous = orig_azure
        routing._get_openai_client = orig_get_client
    print("PASS: test_transcribe_openai_failure_does_not_fallback_to_azure")


# ============================================================
# KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01:
# prompt引数の既定None・呼び出し元限定の確認
# ============================================================
class _FakeTranscriptionsCapture:
    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        class _Resp:
            text = "captured"
        return _Resp()


def _install_fake_openai_client():
    class _FakeAudio:
        transcriptions = _FakeTranscriptionsCapture()

    class _FakeClient:
        audio = _FakeAudio()

    client = _FakeClient()
    orig_get_client = routing._get_openai_client
    routing._get_openai_client = lambda: client
    return client, orig_get_client


def test_transcribe_omits_prompt_kwarg_when_none():
    # promptを渡さない既存の全呼び出し元(本文segment等)は、OpenAI APIへ
    # prompt kwargが一切送られないこと(既存挙動の完全無変更を保証)。
    real_wav = "er006_output/pool_pilot_01/pool_benches/h_onset_diagnostic/hostile_repeat1.wav"
    client, orig_get_client = _install_fake_openai_client()
    try:
        text, err = routing.transcribe(real_wav, language="en-US")
        assert text == "captured"
        assert "prompt" not in client.audio.transcriptions.last_kwargs
    finally:
        routing._get_openai_client = orig_get_client
    print("PASS: test_transcribe_omits_prompt_kwarg_when_none")


def test_transcribe_forwards_prompt_kwarg_when_provided():
    # 呼び出し元が明示的にpromptを渡した場合のみ、OpenAI APIへ転送される
    # こと(英語Key Phrase Component経路が使う想定の引数)。
    real_wav = "er006_output/pool_pilot_01/pool_benches/h_onset_diagnostic/hostile_repeat1.wav"
    client, orig_get_client = _install_fake_openai_client()
    try:
        prompt_text = "The audio is spoken in English. Transcribe it verbatim."
        text, err = routing.transcribe(real_wav, language="en-US", prompt=prompt_text)
        assert text == "captured"
        assert client.audio.transcriptions.last_kwargs.get("prompt") == prompt_text
    finally:
        routing._get_openai_client = orig_get_client
    print("PASS: test_transcribe_forwards_prompt_kwarg_when_provided")


if __name__ == "__main__":
    test_english_routes_to_openai()
    test_japanese_routes_to_azure()
    test_unrouted_language_fails_closed_no_call()
    test_transcribe_dispatches_to_azure_for_japanese_no_openai_call()
    test_transcribe_openai_failure_does_not_fallback_to_azure()
    test_transcribe_omits_prompt_kwarg_when_none()
    test_transcribe_forwards_prompt_kwarg_when_provided()
    print("ALL TESTS PASSED")
