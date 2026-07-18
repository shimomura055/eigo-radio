# ============================================================
# er002_gemini_client.py
# ER-002-S2: TTS/QA用の実Gemini API接続アダプター
# ============================================================
# er002_common.run_tts_content_attempts / evaluate_qa_for_audio が要求する
#   tts_call_fn(prompt) -> bytes(生PCM)
#   qa_call_fn(prompt, wav_bytes) -> str(QAモデルの生レスポンステキスト)
# インターフェースの実装。モデル名・言語コード・サンプルレートは
# er002_common(ER-001B-6以降で確定した値)からそのまま参照し、ここでは
# 定義し直さない。呼び出し方(response_modalities=["AUDIO"]、タイムアウト
# 150秒、QA側はresponse_mime_type="application/json")はER-001B-9/10の
# call_tts()/technical_check_*()と同一。
#
# PCMの正規化(ピーク基準)はer002_common._call_tts_with_retry側で
# 一律に行うため、ここでは生のPCMをそのまま返す。

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

import er002_common as common

TTS_TIMEOUT_MS = 150_000


def make_client() -> genai.Client:
    load_dotenv()
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_speech_config(voice_name: str) -> types.SpeechConfig:
    return types.SpeechConfig(
        language_code=common.LANGUAGE_CODE,
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
        ),
    )


def make_tts_call_fn(voice_name: str, client: genai.Client = None):
    """指定話者(voice_name)固定のtts_call_fn(prompt)->bytesを返す。"""
    client = client or make_client()
    speech_config = build_speech_config(voice_name)

    def tts_call_fn(prompt: str) -> bytes:
        response = client.models.generate_content(
            model=common.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config,
                http_options=types.HttpOptions(timeout=TTS_TIMEOUT_MS),
            ),
        )
        parts = response.candidates[0].content.parts
        pcm = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
        if not pcm:
            raise RuntimeError(f"音声パーツが空でした(parts数: {len(parts)})")
        return pcm

    return tts_call_fn


def make_qa_call_fn(client: genai.Client = None):
    """qa_call_fn(prompt, wav_bytes)->strを返す(embedded/grounded共通)。"""
    client = client or make_client()

    def qa_call_fn(prompt: str, wav_bytes: bytes) -> str:
        resp = client.models.generate_content(
            model=common.QA_MODEL_NAME,
            contents=[types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"), prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return resp.text

    return qa_call_fn
