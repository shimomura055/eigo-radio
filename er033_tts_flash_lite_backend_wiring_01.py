# ============================================================
# er033_tts_flash_lite_backend_wiring_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 1
# ============================================================
# 性質: opt-inのTTS backend抽象。既定(BACKEND_STRUCTURED_SEPARATION)では
# 既存呼び出しと完全に同一のcall_fn/promptを返す(byte-identical、Family
# A/B/C[legacy]の挙動へ一切影響しない)。Family X runnerのみが明示的に
# tts_backend="speech_metadata_flash_lite"を渡した場合のみ、Gemini 3.8
# Flash-Lite(speech_metadata方式)の経路を使う。
#
# 設計根拠: docs/pm/design_flash_lite_family_x_wiring_01.md §(a-3)(b)(g)。
# 実際のAPI呼び出し(client.models.generate_content)はこのモジュール内の
# 1箇所(make_speech_metadata_call_fn内のtts_call_fn)にのみ存在する。
# SF-3是正(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02
# 修正3回目、2026-09-28、Opus L2所見): 「Phase 1では一度も呼ばれない」は
# Phase 1時点の記述で、Phase 2でSDK 2.25.0導入・Production `.venv`での
# 実API呼び出し(Family X runnerがtts_backend="speech_metadata_flash_lite"
# を明示的に渡す経路)が既に実施済みのため、現状と矛盾する。
from __future__ import annotations

import io
import time
import wave
from math import gcd
from typing import Callable, Optional

import numpy as np

import er002_common as common
import er006_model_routing_contract_01 as routing_contract

BACKEND_STRUCTURED_SEPARATION = "structured_separation"
BACKEND_SPEECH_METADATA_FLASH_LITE = "speech_metadata_flash_lite"
SUPPORTED_TTS_BACKENDS = (BACKEND_STRUCTURED_SEPARATION, BACKEND_SPEECH_METADATA_FLASH_LITE)
DEFAULT_TTS_BACKEND = BACKEND_STRUCTURED_SEPARATION

# google-genai SDKの最小要求バージョン(Trial実行環境
# `.venv_trial_genai225`で検証済みのバージョン)。
# SF-3是正(修正3回目、2026-09-28、Opus L2所見): 「Production `.venv`は
# 2026-09-27時点2.11.0のままであり、speech_metadata方式は未対応」は
# Phase 1時点の記述。Phase 2(D-2、2026-09-28)でProduction `.venv`へ
# google-genai==2.25.0を導入済み(`requirements-production-genai-pin.txt`
# にexact pin、`assert_sdk_supports_speech_metadata()`実行時に実測値
# 2.25.0であることを確認済み)であり、speech_metadata方式は実API呼び出し
# 済み。
MIN_SUPPORTED_GENAI_VERSION = (2, 25, 0)

# 設計書§(g): TTS routing contractへ新規processとして登録する
# (require_modelのfail-closedチェックを経由させる)。既存TTS_MODEL/
# PROCESS_PROVIDER_MAPの汎用単一値契約は変更しない(Family別モデルを
# 許容する構造変更はせず、専用processキーを1件追加するのみ)。
FAMILY_X_FLASH_LITE_TTS_PROCESS = "FAMILY_X_FLASH_LITE_TTS"


class TTSBackendSDKUnsupportedError(RuntimeError):
    """speech_metadata_flash_liteバックエンドが要求するSDK versionを
    満たさない場合にfail-closedで送出する(黙って旧方式へfallbackしない、
    委任文で明示された`TTS_BACKEND_SDK_UNSUPPORTED`防御)。"""


def _parse_genai_version() -> tuple:
    import google.genai as genai_pkg
    version_str = getattr(genai_pkg, "__version__", None)
    if not version_str:
        try:
            import importlib.metadata as importlib_metadata
            version_str = importlib_metadata.version("google-genai")
        except Exception:
            version_str = None
    if not version_str:
        raise TTSBackendSDKUnsupportedError(
            "TTS_BACKEND_SDK_UNSUPPORTED: google-genai SDKのバージョンを取得できませんでした"
            "(__version__欠落かつimportlib.metadataでも取得不可)。speech_metadata_flash_lite"
            "バックエンドはfail-closedで停止します。")
    parts = []
    for p in version_str.split(".")[:3]:
        digits = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def assert_sdk_supports_speech_metadata() -> tuple:
    """speech_metadata_flash_liteバックエンドを使う直前に必ず呼ぶ。
    SF-3是正(修正3回目、2026-09-28、Opus L2所見): 旧docstring「Production
    `.venv`(2.11.0)ではここで確実に例外を送出する(Phase 1はAPI呼び出し
    0件であり、この関数はunit testからのみ実行される)」はPhase 1時点の
    記述。Phase 2以降、Production `.venv`はgoogle-genai==2.25.0
    (`requirements-production-genai-pin.txt`)であり、本関数は例外を
    送出せずversionを返して実API呼び出し経路へ進む(Family X runnerの
    実行を実際に確認済み)。"""
    version = _parse_genai_version()
    if version < MIN_SUPPORTED_GENAI_VERSION:
        raise TTSBackendSDKUnsupportedError(
            f"TTS_BACKEND_SDK_UNSUPPORTED: google-genai=={'.'.join(map(str, version))} は"
            f"speech_metadata_flash_liteバックエンドの要求"
            f"({'.'.join(map(str, MIN_SUPPORTED_GENAI_VERSION))}以上)を満たしません。"
            "Production .venvへのSDK 2.25.0導入(Phase 3)まで、このバックエンドは"
            "使用できません(設計書§(f))。")
    return version


# ------------------------------------------------------------
# WAV/PCM防御(Gemini 3.8系はデフォルトでWAVヘッダ付き音声を返す、
# Trial実測: 24000Hz/mono/16bit。ヘッダが無い場合は生PCMとして扱う)
# ------------------------------------------------------------
def _decode_audio_defensive(raw: bytes) -> tuple:
    if raw[:4] == b"RIFF" and raw[8:12] == b"WAVE":
        with wave.open(io.BytesIO(raw), "rb") as w:
            channels = w.getnchannels()
            sampwidth = w.getsampwidth()
            framerate = w.getframerate()
            nframes = w.getnframes()
            frames = w.readframes(nframes)
        if sampwidth != 2:
            raise RuntimeError(f"想定外のsample width: {sampwidth}(speech_metadata_flash_lite backend)")
        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
        if channels > 1:
            samples = samples.reshape(-1, channels).mean(axis=1)
        return samples, framerate
    samples = common.pcm_bytes_to_float_mono(raw)
    return samples, common.SAMPLE_RATE


def _resample_to_common_rate(samples: "np.ndarray", framerate: int) -> "np.ndarray":
    """既存Production下流コード(pcm_bytes_to_float_mono/write_wav_float等)は
    すべてcommon.SAMPLE_RATE(24000Hz)を暗黙の前提とするため、モデルの
    返却framerateがこれと異なる場合のみ、内容・速度・ピッチを変えない
    rational resampling(scipy.signal.resample_poly、p9a.py既存パターンと
    同一手法)で24000Hzへ変換する(Trial実測ではframerate==24000で一致
    しており通常は素通りするが、将来のモデル仕様変更への防御として残す)。"""
    if framerate == common.SAMPLE_RATE:
        return samples
    from scipy.signal import resample_poly
    g = gcd(framerate, common.SAMPLE_RATE)
    up, down = common.SAMPLE_RATE // g, framerate // g
    return resample_poly(samples, up, down)


def _float_to_pcm16_bytes(samples: "np.ndarray") -> bytes:
    peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
    if peak > 1.0:
        samples = samples / peak
    clipped = np.clip(samples, -1.0, 1.0)
    return (clipped * 32767.0).astype(np.int16).tobytes()


def make_speech_metadata_call_fn(model_name: str, voice_name: str, client=None,
                                  output_path: Optional[str] = None) -> Callable:
    """speech_metadata方式のtts_call_fn factory。既存call_fn
    (er002_gemini_client.make_tts_call_fn/er006_batch_tts_wiring_01.
    make_batch_tts_call_fn)とは異なり、戻り値のtts_call_fnは
    `tts_call_fn(payload: tuple[str, str | None]) -> bytes`という形状を
    持つ(payload=(text, style))。common._call_tts_with_retry(call_fn,
    prompt, ...)はpromptをそのままcall_fnへ渡すだけのduck-typed実装
    (`tts_call_fn(prompt)`という呼び出し1箇所のみ)のため、promptに
    tupleを渡しても既存の技術的retry機構(_call_tts_with_retry自体)は
    無変更のまま動作する。

    戻り値の生PCMは既存呼び出し元が期待する形式(24000Hz/mono/16bit
    int16 raw PCM、WAVヘッダ無し)に統一する(WAV/PCM防御込み)。

    Batch API経由が必要な場合はmake_speech_metadata_batch_call_fn()を使う
    (resolve_tts_call_and_prompt()がresolve_tts_execution_mode()を見て
    自動的に切り替える、B-1参照)。このfactory自身はStandard同期呼び出し
    のみを行う。

    output_path: **N-1是正(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-
    FAMILY-X-02、Opus L2所見、2026-09-28)**: FAMILY-X-01 Phase 1時点では
    この引数は仮引数として存在するのみでtts_call_fn内部から一切参照
    されておらず(cost_logger側はer005_cost_logger._patch_gemini()が
    client.models.generate_content自体をmonkeypatchして自動記録するため、
    Standard経路は元々output_pathをtelemetryへ渡す設計を必要としない)、
    dead paramだった。呼び出し元(make_batch_tts_call_fnと同一シグネチャに
    揃えるためのAPI対称性)としては引き続き受け取るが、実際にエラー
    メッセージへ含めることで診断用途の実利用を持たせる(cost記録自体は
    引き続き_patch_gemini()に一任、二重記録はしない)。"""
    assert_sdk_supports_speech_metadata()
    resolved_model_name = routing_contract.require_model(FAMILY_X_FLASH_LITE_TTS_PROCESS, model_name)

    import er002_gemini_client as gclient
    from google.genai import types

    client = client or gclient.make_client()

    def tts_call_fn(payload) -> bytes:
        text, style = payload
        parts_kwargs = {"text": text}
        if style:
            parts_kwargs["speech_metadata"] = types.SpeechMetadata(style=style)
        content = types.Content(parts=[types.Part(**parts_kwargs)], role="user")
        response = client.models.generate_content(
            model=resolved_model_name,
            contents=content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    language_code=common.LANGUAGE_CODE,
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                    )
                ),
                http_options=types.HttpOptions(timeout=gclient.TTS_TIMEOUT_MS),
            ),
        )
        parts = response.candidates[0].content.parts
        raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
        if not raw:
            raise RuntimeError(f"音声パーツが空でした(parts数: {len(parts)}, speech_metadata_flash_lite backend"
                               f"{f', output_path={output_path}' if output_path else ''})")
        samples, framerate = _decode_audio_defensive(raw)
        samples = _resample_to_common_rate(samples, framerate)
        return _float_to_pcm16_bytes(samples)

    return tts_call_fn


def make_speech_metadata_batch_call_fn(model_name: str, voice_name: str, client=None,
                                        output_path: Optional[str] = None,
                                        poll_interval_seconds: Optional[float] = None,
                                        timeout_seconds: Optional[float] = None) -> Callable:
    """B-1(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02、
    ユーザー確定仕様): speech_metadata方式をGemini Batch API
    (client.batches.create)経由で実行するcall_fn factory。

    既存Batch wiring(er006_batch_tts_wiring_01)と**同じ分岐点**
    (resolve_tts_call_and_prompt内でresolve_tts_execution_mode()を見て
    このfactoryへ切り替える、下記resolve_tts_call_and_prompt参照)・
    同じpolling/timeout実装(wait_for_batch_multi)・同じtelemetry schema
    (provider="gemini_batch"、_record()経由でtts_execution_mode="BATCH"
    が自動記録される)を再利用する。「Batch未対応」を前提にfail-closedへ
    倒す設計にはしていない(speech_metadataがInlinedRequestで実際に
    受理されることを2026-09-28に1 item probeで実測確認済み: job
    SUCCEEDED、170.7秒、pcm 175024 bytes、usage prompt_tokens=12/
    candidates_tokens=113。詳細はFAMILY-X-02 REPORT参照)。

    Standard版(make_speech_metadata_call_fn)と同じWAV/PCM防御
    (_decode_audio_defensive/_resample_to_common_rate/
    _float_to_pcm16_bytes)を適用してから24000Hz/mono/16bit rawとして
    返す(Batch応答もGemini 3.8系である以上、同じWAVヘッダ付き形式で
    返る前提のため)。"""
    assert_sdk_supports_speech_metadata()
    resolved_model_name = routing_contract.require_model(FAMILY_X_FLASH_LITE_TTS_PROCESS, model_name)

    import er002_gemini_client as gclient
    import er006_batch_tts_wiring_01 as batch_wiring
    from google.genai import types

    client = client or gclient.make_client()
    _poll = poll_interval_seconds if poll_interval_seconds is not None else batch_wiring.DEFAULT_POLL_INTERVAL_SECONDS
    _timeout = timeout_seconds if timeout_seconds is not None else batch_wiring.DEFAULT_TIMEOUT_SECONDS

    def tts_call_fn(payload) -> bytes:
        text, style = payload
        parts_kwargs = {"text": text}
        if style:
            parts_kwargs["speech_metadata"] = types.SpeechMetadata(style=style)
        content = types.Content(parts=[types.Part(**parts_kwargs)], role="user")
        speech_config = types.SpeechConfig(
            language_code=common.LANGUAGE_CODE,
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            ),
        )
        req = types.InlinedRequest(
            model=resolved_model_name,
            contents=[content],
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config,
                http_options=types.HttpOptions(timeout=gclient.TTS_TIMEOUT_MS),
            ),
        )
        t0 = time.time()
        job = client.batches.create(model=resolved_model_name, src=[req])
        job_name = job.name
        job, state = batch_wiring.wait_for_batch_multi(
            client, job_name, poll_interval_seconds=_poll, timeout_seconds=_timeout)
        elapsed = time.time() - t0
        # N-4是正(修正3回目、2026-09-28、Opus L2所見): shell/legacy prefix
        # 経路ではstyleが約2,000字(p9a.ENGLISH_STYLE_PREFIX等)になり得るため、
        # 無加工でraw_usage_log.jsonlへ書くと毎callで肥大化する。telemetry
        # 用途(どのstyleが使われたかの識別)には先頭200文字で十分なため
        # truncateする(実際のTTS呼び出しに渡すstyle本体[speech_metadata]は
        # 無変更、telemetry記録のみの変更)。
        _style_for_telemetry = style[:200] if isinstance(style, str) else style
        _extra = {"tts_backend": BACKEND_SPEECH_METADATA_FLASH_LITE, "style": _style_for_telemetry}

        if state == "TIMEOUT_EXCEEDED":
            batch_wiring._record(batch_wiring.BatchItemStatus.TIMEOUT, resolved_model_name, voice_name, job_name,
                                  "item_0", elapsed, output_path,
                                  extra={**_extra, "timeout_seconds": _timeout})
            raise TimeoutError(
                f"Gemini Batch job {job_name}(speech_metadata_flash_lite)が{_timeout}秒以内に完了しませんでした")
        if not state.endswith("SUCCEEDED"):
            batch_wiring._record(batch_wiring.BatchItemStatus.JOB_FAILED, resolved_model_name, voice_name, job_name,
                                  "item_0", elapsed, output_path, extra={**_extra, "job_state": state})
            raise RuntimeError(
                f"Gemini Batch job {job_name}(speech_metadata_flash_lite)がSUCCEEDEDになりませんでした"
                f"(state={state})")

        responses = getattr(job.dest, "inlined_responses", None) if job.dest else None
        if not responses:
            batch_wiring._record(batch_wiring.BatchItemStatus.MISSING_RESPONSE, resolved_model_name, voice_name,
                                  job_name, "item_0", elapsed, output_path, extra=_extra)
            raise RuntimeError(f"Gemini Batch job {job_name}(speech_metadata_flash_lite): "
                               f"inlined_responsesが空でした(missing response)")

        resp = responses[0]
        if getattr(resp, "error", None):
            batch_wiring._record(batch_wiring.BatchItemStatus.API_ERROR, resolved_model_name, voice_name, job_name,
                                  "item_0", elapsed, output_path,
                                  extra={**_extra, "error": str(resp.error)[:500]})
            raise RuntimeError(f"Gemini Batch job {job_name}(speech_metadata_flash_lite) item 0: "
                               f"API error: {resp.error}")

        try:
            parts = resp.response.candidates[0].content.parts
            raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
        except Exception as e:
            batch_wiring._record(batch_wiring.BatchItemStatus.INVALID_AUDIO, resolved_model_name, voice_name,
                                  job_name, "item_0", elapsed, output_path,
                                  extra={**_extra, "parse_error": str(e)[:500]})
            raise RuntimeError(f"Gemini Batch job {job_name}(speech_metadata_flash_lite) item 0: "
                               f"応答の解析に失敗(invalid audio): {e}")

        if not raw:
            batch_wiring._record(batch_wiring.BatchItemStatus.EMPTY_RESULT, resolved_model_name, voice_name,
                                  job_name, "item_0", elapsed, output_path, extra=_extra)
            raise RuntimeError(f"Gemini Batch job {job_name}(speech_metadata_flash_lite) item 0: "
                               f"音声パーツが空でした(empty result)")

        samples, framerate = _decode_audio_defensive(raw)
        samples = _resample_to_common_rate(samples, framerate)
        pcm16 = _float_to_pcm16_bytes(samples)

        usage = getattr(resp.response, "usage_metadata", None)
        cost_usd = batch_wiring.estimate_cost_usd(resolved_model_name, usage)
        batch_wiring._record(batch_wiring.BatchItemStatus.SUCCESS, resolved_model_name, voice_name, job_name,
                              "item_0", elapsed, output_path, usage_metadata=usage, cost_usd=cost_usd, extra=_extra)
        return pcm16

    return tts_call_fn


def resolve_actual_model_name(model_name: str, tts_backend: str) -> str:
    """結果dictの"model"フィールドへ記録する実際のmodel_idを返す
    (設計書§(g): result["model"]既存フィールドへ実際に使われたmodel_idを
    そのまま記録する、追加スキーマ不要の方針)。"""
    if tts_backend == BACKEND_SPEECH_METADATA_FLASH_LITE:
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        return fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME
    return model_name


def resolve_tts_call_and_prompt(text: str, style_prefix: str, model_name: str, voice_name: str,
                                 out_path: Optional[str] = None,
                                 tts_backend: str = DEFAULT_TTS_BACKEND,
                                 build_tts_prompt: Optional[Callable] = None,
                                 make_batch_tts_call_fn: Optional[Callable] = None) -> tuple:
    """既存の「call_fn = batch_wiring.make_batch_tts_call_fn(model, voice,
    output_path=out_path); prompt = p4c.build_tts_prompt(text,
    style_prefix)」という3行パターンのopt-in版。

    tts_backend既定値(BACKEND_STRUCTURED_SEPARATION)では、既存呼び出しと
    完全に同一のcall_fn/promptを返す(byte-identical、Family A/B/C
    [legacy]・既存B1/A2呼び出し元への影響ゼロ)。

    build_tts_prompt/make_batch_tts_call_fn: 呼び出し元(voice01/repro01/
    news_tail_fix/point_headings/p9a/n3_01_tts_generate)が既にモジュール
    レベルでimport済みのp4c.build_tts_prompt/batch_wiring.
    make_batch_tts_call_fnをそのまま渡すための差し込み口。呼び出し元自身の
    `import ... as p4c`をmock.patch.object(caller_module, "p4c", ...)で
    まるごと差し替える既存テスト方式(OPEN-197/198 pronunciation resolver
    wiring test等)が、この関数へ委譲した後も引き続き有効であるために必須
    (このモジュール自身が独自にfresh importすると、呼び出し元モジュールの
    名前空間への差し替えが反映されない)。省略した場合のみこのモジュール
    自身がfresh importする(将来の新規呼び出し元向けのfallback)。

    tts_backend=BACKEND_SPEECH_METADATA_FLASH_LITEの場合のみ、
    speech_metadata方式のcall_fnを返し、promptは(text, style_prefix)の
    tupleとする(style_prefixは呼び出し側が既に組み立てている値を
    そのまま流用する — 設計書§(c-1)の推奨案「既存augment_style_prefix_
    with_pronunciation()の戻り値をそのままspeech_metadata.styleへ渡す」
    に従い、この関数自身は新しいstyle値を考案・変換しない)。"""
    if tts_backend not in SUPPORTED_TTS_BACKENDS:
        raise ValueError(f"unknown tts_backend: {tts_backend!r}(supported: {SUPPORTED_TTS_BACKENDS})")
    if tts_backend == BACKEND_SPEECH_METADATA_FLASH_LITE:
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        # B-1(TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02、
        # ユーザー確定仕様): 既存Production実行方式contract
        # (er006_batch_tts_wiring_01.resolve_tts_execution_mode)と同じ
        # 分岐点をFlash-Lite経路にも通す(legacy backendと共通の環境変数
        # TTS_EXECUTION_MODE、既定BATCH)。「Batch未対応」前提のfail-closed
        # にはしない(Batch APIでspeech_metadataが受理されることは実測
        # 済み、下記make_speech_metadata_batch_call_fn docstring参照)。
        import er006_batch_tts_wiring_01 as _batch_wiring_mod
        mode = _batch_wiring_mod.resolve_tts_execution_mode()
        if mode == _batch_wiring_mod.TTS_EXECUTION_MODE_BATCH:
            call_fn = make_speech_metadata_batch_call_fn(
                fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, voice_name, output_path=out_path)
        else:
            call_fn = make_speech_metadata_call_fn(
                fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, voice_name, output_path=out_path)
        prompt = (text, style_prefix)
        return call_fn, prompt

    _build_tts_prompt = build_tts_prompt
    if _build_tts_prompt is None:
        import er003_b1_p4c_audio as _p4c
        _build_tts_prompt = _p4c.build_tts_prompt
    _make_batch_tts_call_fn = make_batch_tts_call_fn
    if _make_batch_tts_call_fn is None:
        import er006_batch_tts_wiring_01 as _batch_wiring
        _make_batch_tts_call_fn = _batch_wiring.make_batch_tts_call_fn
    call_fn = _make_batch_tts_call_fn(model_name, voice_name, output_path=out_path)
    prompt = _build_tts_prompt(text, style_prefix)
    return call_fn, prompt
