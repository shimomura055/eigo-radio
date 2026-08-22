# ============================================================
# er006_batch_tts_wiring_01.py
# ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Gemini TTS Batch API配線
# ============================================================
# 目的: ER-006-AUDIO-COST-SPEC-FIX-01で「採用方針としては確定済みだが
# 未配線」と記録したGemini TTS Batch API(client.batches.create())を、
# 実際のProduction TTS生成6経路(er003_v1_crosslevel_audio_02_common.py/
# er003_v1_repro01_main_generate.py/er003_v1_sing01_news_tail_fix.py/
# er003_v1_sing01_point_headings_aoede.py/er003_v1_sing01_voice01_
# generate.py/er003_v1_n3_01_tts_generate.py)へ実際に配線する。
#
# 設計方針: 変更するのはStandard同期API(client.models.generate_content)
# →Gemini Batch API(client.batches.create)という「実行方式」のみ。
# TTS model・voice・style instruction・Structured Separation・spoken
# text・pacing・audio format・downstream processingは一切変更しない。
#
# 実装形状: er002_gemini_client.make_tts_call_fn(voice)や
# er003_b1_p7a_audio.make_tts_call_fn_for_model(model, voice)と**同一の
# 呼び出し形状**(tts_call_fn(prompt: str) -> bytes)を持つBatch版factory
# を提供する。既存のcommon._call_tts_with_retry(技術的retry機構)・
# ASR-first Retry Cascade・Validator・Master Audio Storeは一切変更せず、
# 「1回のTTS呼び出し」の中身だけをStandardからBatchへ差し替える
# drop-in replacementとして設計した。
#
# 各呼び出しは、1 Batch job = 1 item(text一括の複数segment同時投入では
# なく、既存の1segmentずつのretry loop構造をそのまま保つ設計)。
# Gemini Batch APIの料金割引(50%オフ)は1 jobのitem数に関わらずper-
# request単位で適用されるため、この形でも実コスト効果は完全に得られる
# (client.batches.create()を必ず経由するため、擬似Batch化ではない)。
# item数を増やしたグループ投入は、run_batch_multi()として同一モジュール
# 内に用意しているが、既存6ファイルの制御フロー(1segmentずつの検証・
# retry)を書き換える大規模リファクタリングを伴うため、今回は使用しない
# (ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01完了報告に設計判断として明記)。
#
# Fail-closed: Batch呼び出しが失敗した場合、Standardへの暗黙fallbackは
# 一切行わない(フォールバックのコードパス自体が存在しない)。失敗は
# 例外として送出し、既存のcommon._call_tts_with_retryが規定回数まで
# 「新しいBatch jobの再投入」として技術的retryを行う。
from __future__ import annotations

import json
import time
from typing import Optional

from google.genai import types

import er002_gemini_client as gclient

try:
    import er005_cost_logger as cost_logger
except Exception:  # pragma: no cover - cost_loggerが無いテスト環境向け防御
    cost_logger = None

DEFAULT_POLL_INTERVAL_SECONDS = 5.0
DEFAULT_TIMEOUT_SECONDS = 600.0
USD_TO_JPY = 160  # ER-005系cost scriptと同一の固定レート(プロジェクト既存慣習)

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
_PRICING_CACHE: Optional[list] = None


def _load_pricing() -> list:
    global _PRICING_CACHE
    if _PRICING_CACHE is None:
        with open(PRICING_PATH, encoding="utf-8") as f:
            _PRICING_CACHE = json.load(f)["prices"]
    return _PRICING_CACHE


def _batch_price(model_name: str, meter: str) -> Optional[float]:
    for p in _load_pricing():
        if p["provider"] == "gemini" and p["tier"] == "Batch" and p["model"] == model_name and p["meter"] == meter:
            return p["price"]
    return None


def estimate_cost_usd(model_name: str, usage_metadata) -> Optional[float]:
    """Batch tier単価(pricing_snapshot.json)を使い、1 itemのUSDコストを
    見積もる。price entryが無い/usageが取得できない場合はNoneを返す
    (無理に0円扱いにしない)。"""
    if usage_metadata is None:
        return None
    in_price = _batch_price(model_name, "input_tokens")
    out_price = _batch_price(model_name, "output_tokens")
    if in_price is None or out_price is None:
        return None
    in_tokens = getattr(usage_metadata, "prompt_token_count", None) or 0
    out_tokens = getattr(usage_metadata, "candidates_token_count", None) or 0
    return (in_tokens / 1_000_000) * in_price + (out_tokens / 1_000_000) * out_price


def _record(status: str, model_name: str, voice_name: str, job_name: Optional[str], item_id: str,
            elapsed_seconds: float, output_path: Optional[str], usage_metadata=None,
            cost_usd: Optional[float] = None, extra: Optional[dict] = None) -> None:
    """既存er005_cost_logger.record()へ、Batch特有のフィールド
    (batch_job_id/item_id/result status/output_path/cost)を追加して記録
    する。theme/stage/segment(topic/level/segment_idに相当)は、既存の
    cl.logging_context()/cl.segment_context()で設定済みの周辺文脈を
    そのまま自動的に拾う(このモジュール側で明示的に引き回さない、
    既存の全API call loggingと同じ設計)。cost_logger未installの通常
    実行(cl.install()が呼ばれていない場合)や、logger自体が無い環境
    では静かに何もしない(TTS生成そのものを壊さない)。"""
    if cost_logger is None or getattr(cost_logger, "_LOG_PATH", None) is None:
        return
    entry = {
        "provider": "gemini_batch", "api": "batches.create", "model_id": model_name,
        "voice": voice_name, "batch_job_id": job_name, "item_id": item_id,
        "result_status": status, "success": status == "SUCCESS",
        "elapsed_seconds": round(elapsed_seconds, 3), "output_path": output_path,
        "usage_source": "OFFICIAL_API_RESPONSE" if usage_metadata is not None else "N/A",
    }
    if usage_metadata is not None:
        entry["input_tokens"] = getattr(usage_metadata, "prompt_token_count", None)
        entry["output_tokens"] = getattr(usage_metadata, "candidates_token_count", None)
        entry["total_tokens"] = getattr(usage_metadata, "total_token_count", None)
    if cost_usd is not None:
        entry["cost_usd"] = round(cost_usd, 6)
        entry["cost_jpy"] = round(cost_usd * USD_TO_JPY, 3)
    if extra:
        entry.update(extra)
    try:
        cost_logger.record(entry)
    except Exception:
        pass  # cost telemetryの失敗でTTS生成自体を止めない


class BatchItemStatus:
    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    JOB_FAILED = "JOB_FAILED"
    MISSING_RESPONSE = "MISSING_RESPONSE"
    API_ERROR = "API_ERROR"
    INVALID_AUDIO = "INVALID_AUDIO"
    EMPTY_RESULT = "EMPTY_RESULT"


def _build_inlined_request(prompt: str, model_name: str, speech_config: "types.SpeechConfig") -> "types.InlinedRequest":
    return types.InlinedRequest(
        model=model_name,
        contents=[types.Content(parts=[types.Part(text=prompt)], role="user")],
        config=types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=speech_config),
    )


def _wait_for_job(client, job_name: str, poll_interval_seconds: float, timeout_seconds: float, t0: float):
    while True:
        job = client.batches.get(name=job_name)
        state = str(job.state)
        if state.endswith("SUCCEEDED") or state.endswith("FAILED") or state.endswith("CANCELLED"):
            return job, state
        if time.time() - t0 > timeout_seconds:
            return job, "TIMEOUT_EXCEEDED"
        time.sleep(poll_interval_seconds)


def _resolve_single_item(job, job_name: str, model_name: str, voice_name: str, output_path: Optional[str],
                          elapsed: float):
    """job(SUCCEEDED状態)からitem 0の結果を取り出し、pcm bytesを返す。
    (a)success (b)API error (c)empty result (d)invalid audio
    (e)missing responseの5分類で判定し、success以外は例外を送出する
    (fail-closed、Standardへの暗黙fallbackなし)。"""
    responses = getattr(job.dest, "inlined_responses", None) if job.dest else None
    if not responses:
        _record(BatchItemStatus.MISSING_RESPONSE, model_name, voice_name, job_name, "item_0", elapsed, output_path)
        raise RuntimeError(f"Gemini Batch job {job_name}: inlined_responsesが空でした(missing response)")

    resp = responses[0]
    if getattr(resp, "error", None):
        _record(BatchItemStatus.API_ERROR, model_name, voice_name, job_name, "item_0", elapsed, output_path,
                extra={"error": str(resp.error)[:500]})
        raise RuntimeError(f"Gemini Batch job {job_name} item 0: API error: {resp.error}")

    try:
        parts = resp.response.candidates[0].content.parts
        pcm = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
    except Exception as e:
        _record(BatchItemStatus.INVALID_AUDIO, model_name, voice_name, job_name, "item_0", elapsed, output_path,
                extra={"parse_error": str(e)[:500]})
        raise RuntimeError(f"Gemini Batch job {job_name} item 0: 応答の解析に失敗(invalid audio): {e}")

    if not pcm:
        _record(BatchItemStatus.EMPTY_RESULT, model_name, voice_name, job_name, "item_0", elapsed, output_path)
        raise RuntimeError(f"Gemini Batch job {job_name} item 0: 音声パーツが空でした(empty result)")

    usage = getattr(resp.response, "usage_metadata", None)
    cost_usd = estimate_cost_usd(model_name, usage)
    _record(BatchItemStatus.SUCCESS, model_name, voice_name, job_name, "item_0", elapsed, output_path,
            usage_metadata=usage, cost_usd=cost_usd)
    return pcm


def make_batch_tts_call_fn(model_name: str, voice_name: str, client=None, output_path: Optional[str] = None,
                            poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
                            timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS):
    """er002_gemini_client.make_tts_call_fn(voice)・er003_b1_p7a_audio.
    make_tts_call_fn_for_model(model, voice)と**同一の呼び出し形状**
    (tts_call_fn(prompt: str) -> bytes)を持つ、Gemini Batch API版
    factory。既存の呼び出し元(common._call_tts_with_retry経由)は
    一切変更せず、この関数が返すcall_fnを差し込むだけでBatchへ切り替わる。

    output_pathはtraceability記録用(§6)。省略可(呼び出し元がまだ
    out_pathを持たない場合はNoneのまま記録される)。
    """
    client = client or gclient.make_client()
    speech_config = gclient.build_speech_config(voice_name)

    def tts_call_fn(prompt: str) -> bytes:
        req = _build_inlined_request(prompt, model_name, speech_config)
        t0 = time.time()
        job = client.batches.create(model=model_name, src=[req])
        job_name = job.name
        job, state = _wait_for_job(client, job_name, poll_interval_seconds, timeout_seconds, t0)
        elapsed = time.time() - t0

        if state == "TIMEOUT_EXCEEDED":
            _record(BatchItemStatus.TIMEOUT, model_name, voice_name, job_name, "item_0", elapsed, output_path,
                    extra={"timeout_seconds": timeout_seconds})
            raise TimeoutError(f"Gemini Batch job {job_name} が{timeout_seconds}秒以内に完了しませんでした")
        if not state.endswith("SUCCEEDED"):
            _record(BatchItemStatus.JOB_FAILED, model_name, voice_name, job_name, "item_0", elapsed, output_path,
                    extra={"job_state": state})
            raise RuntimeError(f"Gemini Batch job {job_name} がSUCCEEDEDになりませんでした(state={state})")

        return _resolve_single_item(job, job_name, model_name, voice_name, output_path, elapsed)

    return tts_call_fn


# ------------------------------------------------------------
# 複数segment一括投入(将来の最適化余地として用意。現時点では既存6
# ファイルのいずれからも呼ばれていない。§8「実装方法は過度に指定
# しない」を踏まえ、1 job=1 itemのmake_batch_tts_call_fn()を今回の
# 主たる配線方式として採用し、こちらは同一APIサーフェスの拡張余地と
# して残す設計判断とした。詳細はER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01
# 完了報告参照)。
# ------------------------------------------------------------
def submit_batch_multi(requests: list, client=None) -> "types.BatchJob":
    """requests: [(prompt, model_name, voice_name), ...]。**全item同一
    modelであること**(Gemini Batch APIのjobはmodel単位のため、English/
    Japanese混在時は呼び出し側でmodelごとにgroupingしてから渡すこと)。
    1つのbatch jobとして投入し、job(未完了状態)を返す(呼び出し側で
    wait_for_batch_multi()を使って完了を待つ)。"""
    if not requests:
        raise ValueError("requestsが空です")
    models = {m for _, m, _ in requests}
    if len(models) != 1:
        raise ValueError(f"submit_batch_multi()は単一model限定です(渡されたmodel集合: {models})")
    model_name = next(iter(models))
    reqs = []
    for prompt, _model, voice_name in requests:
        speech_config = gclient.build_speech_config(voice_name)
        reqs.append(_build_inlined_request(prompt, model_name, speech_config))
    client = client or gclient.make_client()
    return client.batches.create(model=model_name, src=reqs)


def wait_for_batch_multi(client, job_name: str, poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
                          timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS):
    t0 = time.time()
    return _wait_for_job(client, job_name, poll_interval_seconds, timeout_seconds, t0)
