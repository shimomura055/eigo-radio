# ============================================================
# er006_pronunciation_research_01.py
# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01: Perplexity発音調査
# ============================================================
# 抽出済みの固有名詞リストをまとめて1 topicにつき1 requestでPerplexityへ
# 問い合わせる。IPAだけでなく、TTSへ自然言語で渡せる説明形式(plain
# English-readable form)も取得する。

from __future__ import annotations

import json
import os
import time
from typing import Optional

import requests

import er005_cost_logger as cl

RESEARCH_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "surface": {"type": "string"},
                    "entity_type": {"type": "string"},
                    "language_origin": {"type": "string"},
                    "canonical_spelling": {"type": "string"},
                    "expected_pronunciation_ipa": {"type": "string"},
                    "pronunciation_hint": {
                        "type": "string",
                        "description": "Plain English-readable phonetic approximation a TTS style instruction can use directly, e.g. 'oh-TOH-nee'.",
                    },
                    "alternate_pronunciations": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "ambiguity_note": {"type": "string"},
                },
                "required": [
                    "surface", "entity_type", "language_origin", "canonical_spelling",
                    "expected_pronunciation_ipa", "pronunciation_hint",
                    "alternate_pronunciations", "confidence", "ambiguity_note",
                ],
            },
        },
    },
    "required": ["items"],
}

PROMPT_TEMPLATE = """次の固有名詞それぞれについて、英語ポッドキャストのTTS読み上げ・音声認識の
参考にするための発音情報を調べてください。

情報源は、本人・公式サイト・所属組織・公式イベント・信頼できるインタビュー等の
一次情報源(本人が話す音声・本人インタビュー・公式発表等)を最優先で探してください。
そのような一次情報源が見つからない場合のみ、辞書サイト・発音解説サイト等の
二次情報源を使ってください(その場合はambiguity_noteに一次情報源が
見つからなかった旨を明記してください)。

対象:
{entity_list}

各項目について次を含めてください:
- entity_type(person/place/organization/product/loanword/abbreviation等)
- language_origin(どの言語由来か)
- canonical_spelling(正しい綴り)
- expected_pronunciation_ipa(IPA表記)
- pronunciation_hint(TTSのstyle instructionへそのまま渡せる、平易な英語の
  カタカナ的近似表記。例: "oh-TOH-nee"のような形式)
- alternate_pronunciations(有力な別の読み方があれば)
- confidence(high/medium/low、情報源の一致度に基づく)
- ambiguity_note(読み方に曖昧さ・地域差がある場合の注記、無ければ空文字)
"""


def build_user_message(entities: list[dict]) -> str:
    entity_list = "\n".join(f"- {e['surface']} ({e['entity_type']}): {e.get('risk_reason', '')}" for e in entities)
    return PROMPT_TEMPLATE.format(entity_list=entity_list)


def research_pronunciations(entities: list[dict], model: str = "sonar", timeout: float = 60.0) -> dict:
    """entities: [{"surface": ..., "entity_type": ..., "risk_reason": ...}, ...]
    1 requestで全件まとめて問い合わせる(1 topicにつき1 request、per task spec)。"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"status": "CREDENTIAL_REQUIRED"}

    user_message = build_user_message(entities)
    t0 = time.time()
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": user_message}],
            "response_format": {"type": "json_schema", "json_schema": {"schema": RESEARCH_JSON_SCHEMA}},
        },
        timeout=timeout,
    )
    elapsed = round(time.time() - t0, 3)
    success = resp.status_code == 200
    if not success:
        cl.record({
            "provider": "perplexity", "api": "pronunciation_research", "model_id": model,
            "attempt_number": 1, "success": False, "elapsed_seconds": elapsed,
            "usage_source": "N/A_FAILED_CALL", "http_status": resp.status_code,
        })
        return {"status": "FAILED", "http_status": resp.status_code, "elapsed_seconds": elapsed, "body": resp.text[:500]}

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    usage = data.get("usage", {})
    cl.record({
        "provider": "perplexity", "api": "pronunciation_research", "model_id": data.get("model"),
        "attempt_number": 1, "success": True, "elapsed_seconds": elapsed,
        "usage_source": "OFFICIAL_API_RESPONSE", "http_status": resp.status_code,
        "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"), "items_returned": len(parsed.get("items", [])),
    })
    return {
        "status": "OK",
        "items": parsed["items"],
        "citations": data.get("citations", []),
        "model": data.get("model"),
        "response_id": data.get("id"),
        "elapsed_seconds": elapsed,
        "usage": usage,
    }
