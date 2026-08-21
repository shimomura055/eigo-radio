# ============================================================
# er005_cost_logger.py
# ER-005-COST-BASELINE-01: 全有料API callのraw usage計測
# ============================================================
# 目的: Production生成ロジック(prompt/リトライ回数/モデル選択)を一切
# 変更せず、実際に発生する全API callのusage metadataを記録する。
#
# 方式: 各SDKのクラスメソッド(openai.resources.responses.Responses.create /
# google.genai.models.Models.generate_content)をprocess単位でmonkeypatchし、
# 呼び出し箇所のコード(各Writer/TTSモジュール)は一切変更しない。
# Azure Speech(ASRの2エントリ関数)は、SDKがusageを返さないため、
# 関数そのものをwrapし、送信WAVの尺をローカルで計算して記録する
# (ASRのAPI呼び出し自体は一切変更しない)。
#
# 1 API call = 1 JSONL record。API key/secret/個人情報は記録しない。
from __future__ import annotations

import json
import os
import time
import wave
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Optional

_LOG_PATH: Optional[str] = None
_CONTEXT = {"theme": None, "stage": None, "segment": None}
_ATTEMPT_COUNTERS: dict[tuple, int] = {}
_INSTALLED = False


def init_logger(log_path: str) -> None:
    """記録先JSONLファイルを設定する(実行ごとに1回呼ぶ)。"""
    global _LOG_PATH
    _LOG_PATH = log_path
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        open(log_path, "w", encoding="utf-8").close()


@contextmanager
def logging_context(theme: str, stage: str):
    """このwith블록内の全API callに theme/stage タグを付与する。"""
    prev = dict(_CONTEXT)
    _CONTEXT["theme"] = theme
    _CONTEXT["stage"] = stage
    try:
        yield
    finally:
        _CONTEXT["theme"] = prev["theme"]
        _CONTEXT["stage"] = prev["stage"]


# ER-006-POOL-PREPROD-HARDENING-01: segment単位のCost Telemetry。
# logging_context()の内側で使うことを想定した追加タグ(theme/stageは変更しない)。
# cl.install()が呼ばれていない通常の本番実行(このcontext managerを呼び出す
# コード自体が無ければ何もしない)には一切影響しない、純粋加算的な変更。
@contextmanager
def segment_context(segment: str):
    """このwith블록内の全API callにsegmentタグを追加で付与する。
    logging_context()と併用する(themeやstageは変更しない)。"""
    prev = _CONTEXT["segment"]
    _CONTEXT["segment"] = segment
    try:
        yield
    finally:
        _CONTEXT["segment"] = prev


def _next_attempt(provider: str, api: str) -> int:
    key = (_CONTEXT["theme"], _CONTEXT["stage"], _CONTEXT["segment"], provider, api)
    _ATTEMPT_COUNTERS[key] = _ATTEMPT_COUNTERS.get(key, 0) + 1
    return _ATTEMPT_COUNTERS[key]


def record(entry: dict) -> None:
    if _LOG_PATH is None:
        raise RuntimeError("init_logger()が呼ばれていません")
    base = {
        "theme": _CONTEXT["theme"],
        "stage": _CONTEXT["stage"],
        "segment": _CONTEXT["segment"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    base.update(entry)
    with open(_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(base, ensure_ascii=False) + "\n")


# ============================================================
# OpenAI Responses API (Researcher/Verification/Writer/Fact Checker等)
# ============================================================
def _usage_to_dict(usage: Any) -> dict:
    if usage is None:
        return {}
    d = {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
    in_details = getattr(usage, "input_tokens_details", None)
    if in_details is not None:
        d["cached_input_tokens"] = getattr(in_details, "cached_tokens", None)
    out_details = getattr(usage, "output_tokens_details", None)
    if out_details is not None:
        d["reasoning_tokens"] = getattr(out_details, "reasoning_tokens", None)
    return d


def _patch_openai() -> None:
    from openai.resources.responses import responses as responses_module

    original_create = responses_module.Responses.create

    def patched_create(self, *args, **kwargs):
        attempt = _next_attempt("openai", "responses.create")
        t0 = time.time()
        try:
            response = original_create(self, *args, **kwargs)
        except Exception as exc:
            record({
                "provider": "openai", "api": "responses.create",
                "model_id": kwargs.get("model"), "attempt_number": attempt,
                "success": False, "error": str(exc)[:500],
                "elapsed_seconds": round(time.time() - t0, 3),
                "usage_source": "N/A_FAILED_CALL",
            })
            raise
        usage = _usage_to_dict(getattr(response, "usage", None))
        web_search_call_count = sum(
            1 for item in getattr(response, "output", []) or []
            if getattr(item, "type", None) == "web_search_call"
        )
        record({
            "provider": "openai", "api": "responses.create",
            "model_id": getattr(response, "model", kwargs.get("model")),
            "response_id": getattr(response, "id", None),
            "attempt_number": attempt, "success": True,
            "elapsed_seconds": round(time.time() - t0, 3),
            "usage_source": "OFFICIAL_API_RESPONSE",
            "web_search_call_count": web_search_call_count,
            **usage,
        })
        return response

    responses_module.Responses.create = patched_create


# ============================================================
# Gemini generate_content (TTS音声生成・QA)
# ============================================================
def _gemini_usage_to_dict(usage_metadata: Any) -> dict:
    if usage_metadata is None:
        return {}
    return {
        "input_tokens": getattr(usage_metadata, "prompt_token_count", None),
        "output_tokens": getattr(usage_metadata, "candidates_token_count", None),
        "total_tokens": getattr(usage_metadata, "total_token_count", None),
    }


def _patch_gemini() -> None:
    from google.genai import models as genai_models

    original_generate_content = genai_models.Models.generate_content

    def patched_generate_content(self, *args, **kwargs):
        model_id = kwargs.get("model")
        config = kwargs.get("config")
        response_modalities = getattr(config, "response_modalities", None) if config else None
        is_audio = bool(response_modalities and "AUDIO" in response_modalities)
        api = "models.generate_content(TTS)" if is_audio else "models.generate_content(text)"
        attempt = _next_attempt("gemini", api)
        t0 = time.time()
        try:
            response = original_generate_content(self, *args, **kwargs)
        except Exception as exc:
            record({
                "provider": "gemini", "api": api, "model_id": model_id,
                "attempt_number": attempt, "success": False,
                "error": str(exc)[:500],
                "elapsed_seconds": round(time.time() - t0, 3),
                "usage_source": "N/A_FAILED_CALL",
            })
            raise
        usage = _gemini_usage_to_dict(getattr(response, "usage_metadata", None))
        audio_seconds = None
        if is_audio:
            try:
                parts = response.candidates[0].content.parts
                pcm = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
                # 24kHz/16bit/mono固定(er002_common.SAMPLE_RATE)。生PCMバイト長から
                # 直接算出する厳密値であり、tokenのESTIMATEDとは区別する。
                audio_seconds = round(len(pcm) / (24000 * 2), 3)
            except Exception:
                audio_seconds = None
        record({
            "provider": "gemini", "api": api, "model_id": model_id,
            "attempt_number": attempt, "success": True,
            "elapsed_seconds": round(time.time() - t0, 3),
            "usage_source": "OFFICIAL_API_RESPONSE",
            "output_audio_seconds_computed_from_pcm": audio_seconds,
            **usage,
        })
        return response

    genai_models.Models.generate_content = patched_generate_content


# ============================================================
# Azure Speech ASR(SDKがusageを返さないため、送信WAV尺をローカル計算)
# ============================================================
def _wav_duration_seconds(wav_path: str) -> Optional[float]:
    try:
        with wave.open(wav_path, "rb") as wf:
            return round(wf.getnframes() / float(wf.getframerate()), 3)
    except Exception:
        return None


def _wrap_asr_function(module, func_name: str):
    original = getattr(module, func_name)

    def wrapped(wav_path, *args, **kwargs):
        duration = _wav_duration_seconds(wav_path)
        language = kwargs.get("language", args[0] if args else "ja-JP")
        attempt = _next_attempt("azure", func_name)
        t0 = time.time()
        result = original(wav_path, *args, **kwargs)
        success = isinstance(result, tuple) and result[0] is not None
        record({
            "provider": "azure", "api": func_name, "model_id": "azure-speech-stt",
            "locale": language, "attempt_number": attempt, "success": success,
            "elapsed_seconds": round(time.time() - t0, 3),
            "usage_source": "LOCAL_WAV_HEADER_EXACT",
            "audio_duration_submitted_seconds": duration,
        })
        return result

    setattr(module, func_name, wrapped)


def _patch_azure() -> None:
    import er003_b1_p3u_audio as p3u
    import er003_b1_p4_audio as p4

    _wrap_asr_function(p3u, "get_word_timestamps_via_azure_stt")
    _wrap_asr_function(p4, "get_full_text_via_azure_stt_continuous")


def install(log_path: str) -> None:
    """3プロバイダ全てにpatchを適用する。プロセス内で1回だけ実行する。"""
    global _INSTALLED
    init_logger(log_path)
    if _INSTALLED:
        return
    _patch_openai()
    _patch_gemini()
    _patch_azure()
    _INSTALLED = True
