# ============================================================
# er011_tts_execution_mode_switch_wiring_01_test.py
# ER-011-TTS-EXECUTION-MODE-SWITCH-PRODUCTION-WIRING-01: Unit test
# ============================================================
# 実際のGemini API(client.batches.create/get、client.models.
# generate_content)は一切呼ばない。er006_batch_tts_wiring_01.
# make_batch_tts_call_fn()の環境変数TTS_EXECUTION_MODEによる分岐
# (既定BATCH/STANDARD/大文字小文字非依存/不正値ValueError)と、
# 返却されるtts_call_fnの呼び出し形状がBatch/Standard両モードで
# 同一であることを検証する。cost logger(er005_cost_logger)側の
# tts_execution_mode追加タグ付けも検証する。
from __future__ import annotations

import json
import os
import sys
import tempfile
from types import SimpleNamespace

import er002_gemini_client as gclient
import er003_b1_p7a_audio as p7a
import er005_cost_logger as cost_logger
import er006_batch_tts_wiring_01 as batch_wiring

MODEL = "gemini-2.5-pro-preview-tts"
VOICE = "Aoede"

ENV_VAR = batch_wiring.TTS_EXECUTION_MODE_ENV_VAR


def _clear_env():
    os.environ.pop(ENV_VAR, None)


# ------------------------------------------------------------
# resolve_tts_execution_mode()
# ------------------------------------------------------------
def test_default_env_unset_resolves_to_batch():
    _clear_env()
    try:
        assert batch_wiring.resolve_tts_execution_mode() == "BATCH"
    finally:
        _clear_env()
    print("[OK] test_default_env_unset_resolves_to_batch")


def test_standard_env_resolves_to_standard():
    os.environ[ENV_VAR] = "STANDARD"
    try:
        assert batch_wiring.resolve_tts_execution_mode() == "STANDARD"
    finally:
        _clear_env()
    print("[OK] test_standard_env_resolves_to_standard")


def test_lowercase_standard_env_also_resolves():
    os.environ[ENV_VAR] = "standard"
    try:
        assert batch_wiring.resolve_tts_execution_mode() == "STANDARD"
    finally:
        _clear_env()
    print("[OK] test_lowercase_standard_env_also_resolves")


def test_mixed_case_batch_env_also_resolves():
    os.environ[ENV_VAR] = "Batch"
    try:
        assert batch_wiring.resolve_tts_execution_mode() == "BATCH"
    finally:
        _clear_env()
    print("[OK] test_mixed_case_batch_env_also_resolves")


def test_invalid_env_raises_value_error():
    os.environ[ENV_VAR] = "SOMETHING_ELSE"
    try:
        try:
            batch_wiring.resolve_tts_execution_mode()
            raise AssertionError("不正値なのにValueErrorが送出されなかった")
        except ValueError as e:
            assert "SOMETHING_ELSE" in str(e)
    finally:
        _clear_env()
    print("[OK] test_invalid_env_raises_value_error")


# ------------------------------------------------------------
# make_batch_tts_call_fn(): 既定(未設定)でBatch経路
# ------------------------------------------------------------
class _FakeBatches:
    def __init__(self, job):
        self._job = job
        self.create_call_count = 0

    def create(self, model, src):
        self.create_call_count += 1
        return SimpleNamespace(name="job_1", state="JOB_STATE_PENDING")

    def get(self, name):
        return self._job


def _fake_success_job(pcm=b"BATCH_PCM"):
    resp = SimpleNamespace(
        error=None,
        response=SimpleNamespace(
            candidates=[SimpleNamespace(content=SimpleNamespace(
                parts=[SimpleNamespace(inline_data=SimpleNamespace(data=pcm))]))],
            usage_metadata=SimpleNamespace(prompt_token_count=1, candidates_token_count=1, total_token_count=2),
        ),
    )
    return SimpleNamespace(name="job_1", state="JOB_STATE_SUCCEEDED", dest=SimpleNamespace(inlined_responses=[resp]))


def test_default_unset_uses_batch_path():
    _clear_env()
    try:
        fake_batches = _FakeBatches(_fake_success_job(pcm=b"DEFAULT_BATCH_PCM"))
        client = SimpleNamespace(batches=fake_batches)
        call_fn = batch_wiring.make_batch_tts_call_fn(MODEL, VOICE, client=client,
                                                       poll_interval_seconds=0.001, timeout_seconds=0.5)
        pcm = call_fn("prompt")
        assert pcm == b"DEFAULT_BATCH_PCM"
        assert fake_batches.create_call_count == 1, "既定(未設定)なのにBatch job作成が行われなかった"
    finally:
        _clear_env()
    print("[OK] test_default_unset_uses_batch_path")


# ------------------------------------------------------------
# make_batch_tts_call_fn(): STANDARD時はp7a.make_tts_call_fn_for_modelへ委譲
# ------------------------------------------------------------
def test_standard_mode_delegates_to_p7a_make_tts_call_fn_for_model():
    os.environ[ENV_VAR] = "STANDARD"
    captured = {}
    original = p7a.make_tts_call_fn_for_model
    sentinel_client = SimpleNamespace(marker="sentinel")

    def fake_for_model(model_name, voice_name, client=None):
        captured["args"] = (model_name, voice_name, client)
        return lambda prompt: b"STANDARD_PCM_VIA_P7A"

    p7a.make_tts_call_fn_for_model = fake_for_model
    try:
        call_fn = batch_wiring.make_batch_tts_call_fn(MODEL, VOICE, client=sentinel_client)
        assert callable(call_fn)
        assert call_fn("some prompt") == b"STANDARD_PCM_VIA_P7A"
        assert captured["args"] == (MODEL, VOICE, sentinel_client)
    finally:
        p7a.make_tts_call_fn_for_model = original
        _clear_env()
    print("[OK] test_standard_mode_delegates_to_p7a_make_tts_call_fn_for_model")


def test_standard_mode_falls_back_to_gclient_when_p7a_unavailable():
    """er003_b1_p7a_audioがimportできない実行環境向けの防御経路
    (通常の本番実行では到達しない)を、sys.modulesを一時的にNoneへ
    差し替えてImportErrorを強制することで検証する。"""
    os.environ[ENV_VAR] = "STANDARD"
    had_module = "er003_b1_p7a_audio" in sys.modules
    original_module = sys.modules.get("er003_b1_p7a_audio")
    sys.modules["er003_b1_p7a_audio"] = None  # importするとImportErrorになる

    captured = {}
    original_gclient_fn = gclient.make_tts_call_fn
    sentinel_client = SimpleNamespace(marker="sentinel2")

    def fake_gclient_fn(voice_name, client=None):
        captured["args"] = (voice_name, client)
        return lambda prompt: b"STANDARD_PCM_VIA_GCLIENT"

    gclient.make_tts_call_fn = fake_gclient_fn
    try:
        call_fn = batch_wiring.make_batch_tts_call_fn(MODEL, VOICE, client=sentinel_client)
        assert call_fn("prompt") == b"STANDARD_PCM_VIA_GCLIENT"
        assert captured["args"] == (VOICE, sentinel_client)
    finally:
        gclient.make_tts_call_fn = original_gclient_fn
        if had_module:
            sys.modules["er003_b1_p7a_audio"] = original_module
        else:
            del sys.modules["er003_b1_p7a_audio"]
        _clear_env()
    print("[OK] test_standard_mode_falls_back_to_gclient_when_p7a_unavailable")


# ------------------------------------------------------------
# 呼び出し形状(tts_call_fn(prompt: str) -> bytes)がBatch/Standardで同一
# ------------------------------------------------------------
def test_call_shape_identical_across_modes():
    import inspect

    _clear_env()
    fake_batches = _FakeBatches(_fake_success_job())
    client = SimpleNamespace(batches=fake_batches)
    batch_fn = batch_wiring.make_batch_tts_call_fn(MODEL, VOICE, client=client,
                                                    poll_interval_seconds=0.001, timeout_seconds=0.5)

    os.environ[ENV_VAR] = "STANDARD"
    original = p7a.make_tts_call_fn_for_model
    p7a.make_tts_call_fn_for_model = lambda model_name, voice_name, client=None: (lambda prompt: b"X")
    try:
        standard_fn = batch_wiring.make_batch_tts_call_fn(MODEL, VOICE, client=SimpleNamespace())
        for fn in (batch_fn, standard_fn):
            params = list(inspect.signature(fn).parameters.values())
            assert len(params) == 1, f"tts_call_fnは単一引数(prompt)のはず: {params}"
            result = fn("some prompt text")
            assert isinstance(result, (bytes, bytearray)), "tts_call_fnはbytesを返すはず"
    finally:
        p7a.make_tts_call_fn_for_model = original
        _clear_env()
    print("[OK] test_call_shape_identical_across_modes")


# ------------------------------------------------------------
# er006_batch_tts_wiring_01._record(): BATCH経路のruntime evidence記録
# ------------------------------------------------------------
def test_batch_record_tags_tts_execution_mode_batch():
    tmp_dir = tempfile.mkdtemp()
    log_path = os.path.join(tmp_dir, "raw_usage_log.jsonl")
    cost_logger._INSTALLED = False
    cost_logger._LOG_PATH = None
    cost_logger.init_logger(log_path)
    _clear_env()
    try:
        fake_batches = _FakeBatches(_fake_success_job(pcm=b"TAGGED_PCM"))
        client = SimpleNamespace(batches=fake_batches)
        call_fn = batch_wiring.make_batch_tts_call_fn(MODEL, VOICE, client=client,
                                                       poll_interval_seconds=0.001, timeout_seconds=0.5)
        call_fn("prompt")
        with open(log_path, encoding="utf-8") as f:
            lines = [json.loads(l) for l in f]
        assert len(lines) == 1
        assert lines[0]["tts_execution_mode"] == "BATCH"
        assert lines[0]["provider"] == "gemini_batch"  # 既存キーは変えていないことを確認
    finally:
        cost_logger._INSTALLED = False
        cost_logger._LOG_PATH = None
        _clear_env()
    print("[OK] test_batch_record_tags_tts_execution_mode_batch")


# ------------------------------------------------------------
# er005_cost_logger._patch_gemini(): STANDARD経路のruntime evidence記録
# ------------------------------------------------------------
def test_cost_logger_tags_standard_tts_calls_only():
    from google.genai import models as genai_models

    tmp_dir = tempfile.mkdtemp()
    log_path = os.path.join(tmp_dir, "raw_usage_log.jsonl")
    cost_logger._INSTALLED = False
    cost_logger._LOG_PATH = None
    original_generate_content = genai_models.Models.generate_content

    def fake_generate_content(self, *args, **kwargs):
        return SimpleNamespace(
            candidates=[SimpleNamespace(content=SimpleNamespace(
                parts=[SimpleNamespace(inline_data=SimpleNamespace(data=b"PCM"))]))],
            usage_metadata=SimpleNamespace(prompt_token_count=5, candidates_token_count=6, total_token_count=11),
        )

    genai_models.Models.generate_content = fake_generate_content
    try:
        cost_logger.install(log_path)
        client_stub = SimpleNamespace()
        # TTS呼び出し(response_modalities=["AUDIO"])
        genai_models.Models.generate_content(
            client_stub, model="fake-tts-model",
            config=SimpleNamespace(response_modalities=["AUDIO"]))
        # text呼び出し(QA/Writer相当、AUDIOではない)
        genai_models.Models.generate_content(
            client_stub, model="fake-text-model",
            config=SimpleNamespace(response_modalities=["TEXT"]))
        with open(log_path, encoding="utf-8") as f:
            lines = [json.loads(l) for l in f]
        tts_entries = [l for l in lines if l["api"] == "models.generate_content(TTS)"]
        text_entries = [l for l in lines if l["api"] == "models.generate_content(text)"]
        assert len(tts_entries) == 1 and len(text_entries) == 1
        assert tts_entries[0]["tts_execution_mode"] == "STANDARD"
        assert "tts_execution_mode" not in text_entries[0], "text呼び出しにtts_execution_modeを付与してはいけない"
    finally:
        genai_models.Models.generate_content = original_generate_content
        cost_logger._INSTALLED = False
        cost_logger._LOG_PATH = None
    print("[OK] test_cost_logger_tags_standard_tts_calls_only")


def run():
    test_default_env_unset_resolves_to_batch()
    test_standard_env_resolves_to_standard()
    test_lowercase_standard_env_also_resolves()
    test_mixed_case_batch_env_also_resolves()
    test_invalid_env_raises_value_error()
    test_default_unset_uses_batch_path()
    test_standard_mode_delegates_to_p7a_make_tts_call_fn_for_model()
    test_standard_mode_falls_back_to_gclient_when_p7a_unavailable()
    test_call_shape_identical_across_modes()
    test_batch_record_tags_tts_execution_mode_batch()
    test_cost_logger_tags_standard_tts_calls_only()
    print("\nOK: 全テストPASS")


if __name__ == "__main__":
    run()
