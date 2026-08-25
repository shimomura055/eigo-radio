# ============================================================
# er006_asr_provider_routing_01.py
# ER-006-AUDIO-COST-PILOT-02: ASR Provider Routing SSOT
# ============================================================
# 言語ごとのPrimary ASR providerを一箇所で確定させる(er006_model_
# routing_contract_01.pyのWriter/Support向けrequire_model()と同じ
# 設計思想: Fail-closed、暗黙fallbackなし、呼び出し直前に必ずこの
# モジュールを経由させる)。
#
# 構成(ユーザー確定、2026-08-22時点):
#   English  -> OpenAI gpt-4o-mini-transcribe (Primary)
#   Japanese -> Azure Speech STT
# Secondary ASR(Azure併用によるambiguous時の二重確認)は今回
# Production採用しない(評価のみ、ER-006-AUDIO-COST-OPTIMIZATION-01
# 完了報告 §5参照)。
#
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(2026-08-25)で
# Japanese Primaryも OpenAI gpt-4o-mini-transcribe へ変更(English側と
# 同一構成へ統一)。Secondary(ambiguous時のAzure確認)は
# er007_ja_secondary_asr_01.FEATURE_FLAG_JA_PRIMARY_OPENAIで別途制御。

from __future__ import annotations

import os
import time
from typing import Optional

import er003_b1_p4_audio as p4

ASR_ROUTING = {
    "en": {"provider": "openai_asr", "model": "gpt-4o-mini-transcribe"},
    "ja": {"provider": "openai_asr", "model": "gpt-4o-mini-transcribe"},
}


class UnroutedLanguageError(ValueError):
    """未知の言語がASR routingへ渡された。Fail-closed: Azureへの暗黙
    fallbackは行わない。ASR_ROUTINGへ明示的にエントリを追加すること。"""


def _lang_key(language: str) -> str:
    return (language or "").split("-")[0].lower()


def require_asr_route(language: str) -> dict:
    """languageに対応するPrimary ASR routeをSSOTから取得する。
    ASR_ROUTINGに存在しない言語はここで例外を送出し、API呼び出しへは
    絶対に進ませない(Fail-closed契約、Model Routing Contractと同じ設計)。"""
    key = _lang_key(language)
    if key not in ASR_ROUTING:
        raise UnroutedLanguageError(
            f"ASR_ROUTINGに未登録の言語です: language={language!r} (key={key!r})。"
            f"暗黙にAzureへfallbackしません。ASR_ROUTINGへ明示的に追加してください。")
    return dict(ASR_ROUTING[key])


_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


def _transcribe_openai_mini(wav_path: str, language: str, model: str) -> tuple[Optional[str], Optional[str]]:
    client = _get_openai_client()
    try:
        with open(wav_path, "rb") as f:
            resp = client.audio.transcriptions.create(model=model, file=f, language=_lang_key(language))
        return resp.text, None
    except Exception as exc:
        return None, str(exc)[:500]


def transcribe(wav_path: str, language: str, timeout_seconds: float = 90.0) -> tuple[Optional[str], Optional[str]]:
    """Production ASR dispatch。戻り値は既存のget_full_text_via_azure_stt_
    continuous()と同じ(asr_text, error)形式で、既存の呼び出し側コードを
    そのまま差し替えられる。

    Fail-closed: 未登録言語はrequire_asr_route()が例外を送出し、この
    関数はどのASR APIも呼ばない。OpenAI呼び出しが失敗しても、Azureへ
    黙って切り替えることはしない(エラーをそのまま返し、既存のretry/
    guardrail機構に判断を委ねる)。"""
    route = require_asr_route(language)
    if route["provider"] == "openai_asr":
        return _transcribe_openai_mini(wav_path, language, route["model"])
    elif route["provider"] == "azure":
        return p4.get_full_text_via_azure_stt_continuous(wav_path, language=language, timeout_seconds=timeout_seconds)
    raise UnroutedLanguageError(f"ASR_ROUTINGに未対応のprovider種別です: {route}")
