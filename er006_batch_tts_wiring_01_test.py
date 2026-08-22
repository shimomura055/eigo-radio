# ============================================================
# er006_batch_tts_wiring_01_test.py
# ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Unit/Regression test
# ============================================================
# 実際のGemini API(client.batches.create/get)は一切呼ばない。
# client.batches相当をFakeで差し替え、item-level成功/失敗5分類・
# job失敗・timeout・cost telemetry・technical retryとの統合・
# 複数item投入時のmodel統一制約を検証する。
from __future__ import annotations

import json
import os
import tempfile
import time
from types import SimpleNamespace

import er002_common as common
import er005_cost_logger as cost_logger
import er006_batch_tts_wiring_01 as batch_wiring

MODEL = "gemini-2.5-pro-preview-tts"
VOICE = "Aoede"


def _fake_part(data: bytes | None):
    return SimpleNamespace(inline_data=SimpleNamespace(data=data) if data is not None else None)


def _fake_usage(in_tok=10, out_tok=20, total=30):
    return SimpleNamespace(prompt_token_count=in_tok, candidates_token_count=out_tok, total_token_count=total)


def _fake_success_job(job_name="job_ok", pcm=b"PCMDATA", usage=None):
    resp = SimpleNamespace(
        error=None,
        response=SimpleNamespace(
            candidates=[SimpleNamespace(content=SimpleNamespace(parts=[_fake_part(pcm)]))],
            usage_metadata=usage or _fake_usage(),
        ),
    )
    return SimpleNamespace(name=job_name, state="JOB_STATE_SUCCEEDED", dest=SimpleNamespace(inlined_responses=[resp]))


class FakeBatches:
    """create()/get()を差し替えるFake。jobs_by_scriptでcreate呼び出し
    順に返すjob列を指定する(1テストにつき複数回create()される
    retryケースに対応するため)。"""

    def __init__(self, jobs_by_script: list):
        self._jobs_by_script = jobs_by_script
        self.create_call_count = 0
        self.get_call_log = []

    def create(self, model, src):
        script = self._jobs_by_script[self.create_call_count]
        self.create_call_count += 1
        script["_get_calls"] = iter(script["get_sequence"])
        script["_job_name"] = f"job_{self.create_call_count}"
        return SimpleNamespace(name=script["_job_name"], state="JOB_STATE_PENDING")

    def get(self, name):
        self.get_call_log.append(name)
        idx = self.create_call_count - 1
        script = self._jobs_by_script[idx]
        job = next(script["_get_calls"])
        return job


class FakeClient:
    def __init__(self, jobs_by_script):
        self.batches = FakeBatches(jobs_by_script)


def _make_call_fn(jobs_by_script, output_path=None, poll_interval_seconds=0.001, timeout_seconds=0.05):
    client = FakeClient(jobs_by_script)
    return batch_wiring.make_batch_tts_call_fn(
        MODEL, VOICE, client=client, output_path=output_path,
        poll_interval_seconds=poll_interval_seconds, timeout_seconds=timeout_seconds), client


def test_success_single_item():
    job = _fake_success_job(pcm=b"HELLO_PCM")
    call_fn, client = _make_call_fn([{"get_sequence": [job]}])
    pcm = call_fn("some prompt")
    assert pcm == b"HELLO_PCM"
    assert client.batches.create_call_count == 1
    print("[OK] test_success_single_item")


def test_api_error_raises():
    resp = SimpleNamespace(error="RESOURCE_EXHAUSTED", response=None)
    job = SimpleNamespace(name="job_err", state="JOB_STATE_SUCCEEDED", dest=SimpleNamespace(inlined_responses=[resp]))
    call_fn, _ = _make_call_fn([{"get_sequence": [job]}])
    try:
        call_fn("prompt")
        raise AssertionError("API errorなのに例外が送出されなかった")
    except RuntimeError as e:
        assert "API error" in str(e)
    print("[OK] test_api_error_raises")


def test_empty_result_raises():
    job = _fake_success_job(pcm=b"")
    call_fn, _ = _make_call_fn([{"get_sequence": [job]}])
    try:
        call_fn("prompt")
        raise AssertionError("空音声なのに例外が送出されなかった")
    except RuntimeError as e:
        assert "empty result" in str(e) or "空でした" in str(e)
    print("[OK] test_empty_result_raises")


def test_missing_response_raises():
    job = SimpleNamespace(name="job_missing", state="JOB_STATE_SUCCEEDED", dest=SimpleNamespace(inlined_responses=[]))
    call_fn, _ = _make_call_fn([{"get_sequence": [job]}])
    try:
        call_fn("prompt")
        raise AssertionError("missing responseなのに例外が送出されなかった")
    except RuntimeError as e:
        assert "missing response" in str(e)
    print("[OK] test_missing_response_raises")


def test_invalid_audio_raises():
    resp = SimpleNamespace(error=None, response=SimpleNamespace(candidates=[], usage_metadata=None))
    job = SimpleNamespace(name="job_invalid", state="JOB_STATE_SUCCEEDED", dest=SimpleNamespace(inlined_responses=[resp]))
    call_fn, _ = _make_call_fn([{"get_sequence": [job]}])
    try:
        call_fn("prompt")
        raise AssertionError("invalid audioなのに例外が送出されなかった")
    except RuntimeError as e:
        assert "invalid audio" in str(e)
    print("[OK] test_invalid_audio_raises")


def test_job_failed_raises():
    job = SimpleNamespace(name="job_failed", state="JOB_STATE_FAILED", dest=None)
    call_fn, _ = _make_call_fn([{"get_sequence": [job]}])
    try:
        call_fn("prompt")
        raise AssertionError("job failedなのに例外が送出されなかった")
    except RuntimeError as e:
        assert "SUCCEEDEDになりません" in str(e)
    print("[OK] test_job_failed_raises")


def test_timeout_raises():
    pending_forever = SimpleNamespace(name="job_pending", state="JOB_STATE_PENDING", dest=None)
    call_fn, _ = _make_call_fn(
        [{"get_sequence": [pending_forever] * 1000}],  # timeoutに達するまでずっとPENDING
        poll_interval_seconds=0.001, timeout_seconds=0.01)
    try:
        call_fn("prompt")
        raise AssertionError("timeoutなのに例外が送出されなかった")
    except TimeoutError as e:
        assert "完了しませんでした" in str(e)
    print("[OK] test_timeout_raises")


def test_no_implicit_standard_fallback():
    """fail-closed確認: 失敗時のcall_fn内にStandard(client.models.
    generate_content)を呼ぶコードパスが存在しないことをモジュールソース
    レベルで確認する(実行時にFakeClientがmodels属性すら持たないため、
    もし暗黙fallbackが実装されていればAttributeErrorとして即座に検出
    できる設計だが、念のためソース上でも確認する)。"""
    import inspect
    src = inspect.getsource(batch_wiring.make_batch_tts_call_fn)
    code_only = "\n".join(line for line in src.splitlines() if not line.strip().startswith("#"))
    assert "generate_content" not in code_only, (
        "make_batch_tts_call_fn内にStandard API直接呼び出しが見つかった(fail-closed違反)")
    print("[OK] test_no_implicit_standard_fallback")


def test_retry_only_resubmits_failed_item_as_new_job():
    """common._call_tts_with_retry(既存の技術的retry機構)経由で、1回目の
    Batch job失敗後、2回目で新しいjobが投入されて成功することを確認する
    (Batch全体の無条件再投入=同じ失敗内容の使い回しではなく、失敗した
    item分だけ新規jobとして再投入されることを確認)。"""
    failed_job = SimpleNamespace(name="job_1st", state="JOB_STATE_FAILED", dest=None)
    ok_job = _fake_success_job(job_name="job_2nd", pcm=b"RETRY_OK_PCM")
    call_fn, client = _make_call_fn([
        {"get_sequence": [failed_job]},
        {"get_sequence": [ok_job]},
    ])
    pcm, retries, ok, err = common._call_tts_with_retry(call_fn, "prompt", max_retry=1, sleep_fn=None)
    assert ok is True
    assert retries == 1
    assert client.batches.create_call_count == 2, "失敗後に新しいbatch jobが投入されていない"
    print("[OK] test_retry_only_resubmits_failed_item_as_new_job")


def test_cost_telemetry_logged():
    tmp_dir = tempfile.mkdtemp()
    log_path = os.path.join(tmp_dir, "raw_usage_log.jsonl")
    cost_logger._INSTALLED = False
    cost_logger._LOG_PATH = None
    cost_logger.init_logger(log_path)
    try:
        job = _fake_success_job(pcm=b"PCM", usage=_fake_usage(in_tok=100, out_tok=200, total=300))
        call_fn, _ = _make_call_fn([{"get_sequence": [job]}], output_path="er003_output/dummy/seg.wav")
        call_fn("prompt")
        with open(log_path, encoding="utf-8") as f:
            lines = [json.loads(l) for l in f]
        assert len(lines) == 1
        entry = lines[0]
        assert entry["provider"] == "gemini_batch"
        assert entry["api"] == "batches.create"
        assert entry["model_id"] == MODEL
        assert entry["voice"] == VOICE
        assert entry["batch_job_id"] == "job_1"
        assert entry["item_id"] == "item_0"
        assert entry["result_status"] == "SUCCESS"
        assert entry["success"] is True
        assert entry["output_path"] == "er003_output/dummy/seg.wav"
        assert entry["input_tokens"] == 100
        assert entry["output_tokens"] == 200
        assert "cost_usd" in entry and entry["cost_usd"] > 0
        assert "cost_jpy" in entry and entry["cost_jpy"] > 0
        # Batch tierは50%オフなので、Standard単価(input$1.00/output$20.00)
        # の半額(input$0.50/output$20.00は違う、Batchは20.00の半額=10.00)
        # で計算されているはずであることを確認する。
        expected_usd = (100 / 1_000_000) * 0.50 + (200 / 1_000_000) * 10.00
        assert abs(entry["cost_usd"] - round(expected_usd, 6)) < 1e-9
    finally:
        cost_logger._INSTALLED = False
        cost_logger._LOG_PATH = None
    print("[OK] test_cost_telemetry_logged")


def test_cost_telemetry_not_installed_does_not_crash():
    cost_logger._INSTALLED = False
    cost_logger._LOG_PATH = None
    job = _fake_success_job(pcm=b"PCM")
    call_fn, _ = _make_call_fn([{"get_sequence": [job]}])
    pcm = call_fn("prompt")  # cost_logger未installでも例外を出さない
    assert pcm == b"PCM"
    print("[OK] test_cost_telemetry_not_installed_does_not_crash")


def test_submit_batch_multi_single_model_ok():
    class FakeMultiBatches:
        def create(self, model, src):
            assert model == MODEL
            assert len(src) == 2
            return SimpleNamespace(name="multi_job", state="JOB_STATE_PENDING")

    client = SimpleNamespace(batches=FakeMultiBatches())
    job = batch_wiring.submit_batch_multi(
        [("prompt1", MODEL, "Aoede"), ("prompt2", MODEL, "Charon")], client=client)
    assert job.name == "multi_job"
    print("[OK] test_submit_batch_multi_single_model_ok")


def test_submit_batch_multi_mixed_model_raises():
    try:
        batch_wiring.submit_batch_multi(
            [("prompt1", "gemini-2.5-pro-preview-tts", "Aoede"),
             ("prompt2", "gemini-3.1-flash-tts-preview", "Charon")],
            client=SimpleNamespace(batches=None))
        raise AssertionError("model混在なのに例外が送出されなかった")
    except ValueError as e:
        assert "単一model限定" in str(e)
    print("[OK] test_submit_batch_multi_mixed_model_raises")


def test_price_matches_50_percent_of_standard():
    pricing = batch_wiring._load_pricing()
    standard_in = next(p["price"] for p in pricing if p["provider"] == "gemini" and p["tier"] == "Standard"
                        and p["model"] == MODEL and p["meter"] == "input_tokens")
    standard_out = next(p["price"] for p in pricing if p["provider"] == "gemini" and p["tier"] == "Standard"
                         and p["model"] == MODEL and p["meter"] == "output_tokens")
    batch_in = batch_wiring._batch_price(MODEL, "input_tokens")
    batch_out = batch_wiring._batch_price(MODEL, "output_tokens")
    assert batch_in == standard_in * 0.5
    assert batch_out == standard_out * 0.5
    print("[OK] test_price_matches_50_percent_of_standard")


def run():
    test_success_single_item()
    test_api_error_raises()
    test_empty_result_raises()
    test_missing_response_raises()
    test_invalid_audio_raises()
    test_job_failed_raises()
    test_timeout_raises()
    test_no_implicit_standard_fallback()
    test_retry_only_resubmits_failed_item_as_new_job()
    test_cost_telemetry_logged()
    test_cost_telemetry_not_installed_does_not_crash()
    test_submit_batch_multi_single_model_ok()
    test_submit_batch_multi_mixed_model_raises()
    test_price_matches_50_percent_of_standard()
    print("\nOK: 全テストPASS")


if __name__ == "__main__":
    run()
