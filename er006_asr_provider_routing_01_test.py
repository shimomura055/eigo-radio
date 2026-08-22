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


if __name__ == "__main__":
    test_english_routes_to_openai()
    test_japanese_routes_to_azure()
    test_unrouted_language_fails_closed_no_call()
    test_transcribe_dispatches_to_azure_for_japanese_no_openai_call()
    test_transcribe_openai_failure_does_not_fallback_to_azure()
    print("ALL TESTS PASSED")
