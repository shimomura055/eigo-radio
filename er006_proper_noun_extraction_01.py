# ============================================================
# er006_proper_noun_extraction_01.py
# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01: 固有名詞抽出
# ============================================================
# Writer完成後の記事本文・Support・Key Phraseから、通常の英語綴り規則
# だけでは読みが不確実、またはASR誤認識リスクが高い固有名詞のみを抽出
# する(全単語を対象にしない)。抽出はLuna(Model Routing Contract SSOT)
# を使う。

from __future__ import annotations

import json
from typing import Any, Optional

import er006_model_routing_contract_01 as routing

DEVELOPER_MESSAGE = (
    "英語ポッドキャスト記事から、発音が音声合成・音声認識で問題になりうる"
    "固有名詞だけを抽出してください。"
)

EXTRACTION_JSON_SCHEMA = {
    "name": "proper_noun_extraction",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "surface": {"type": "string"},
                        "entity_type": {
                            "type": "string",
                            "enum": ["person", "place", "organization", "product", "loanword", "abbreviation", "other"],
                        },
                        "risk_reason": {"type": "string"},
                    },
                    "required": ["surface", "entity_type", "risk_reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}

PROMPT_TEMPLATE = """以下はB1/A2レベルの英語学習ポッドキャスト用に完成した記事本文・Support・Key Phraseです。

この中から、次の条件を**両方**満たす固有名詞だけを抽出してください:
1. 人名・地名・組織名・製品名・外国語由来語・発音が自明でない略称のいずれかである
2. 通常の英語綴り規則だけでは読みが不確実、または音声認識(ASR)が誤認識しやすい

普通の英単語、一般的で発音が明白な固有名詞(例: "United States"、"New York"のような
広く知られた地名で発音に曖昧さがないもの)は対象外です。全単語を機械的に走査するのでは
なく、実際にTTS/ASRで問題が起きそうなものだけに絞ってください。

各項目について、なぜリスクがあると判断したか(risk_reason)を簡潔に一言で記してください。

---
記事本文:
{article_text}

Support:
{support_text}

Key Phrases:
{key_phrases_text}
---
"""


def build_user_message(article_text: str, support_text: str, key_phrases_text: str) -> str:
    return PROMPT_TEMPLATE.format(
        article_text=article_text, support_text=support_text, key_phrases_text=key_phrases_text)


def make_extraction_fn(user_message: str, client: Optional[Any] = None,
                        model: Optional[str] = None) -> Any:
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()
    model = routing.require_model("PROPER_NOUN_EXTRACTION", model or routing.PROCESS_MODEL_MAP["PROPER_NOUN_EXTRACTION"])

    def fn():
        response = client.responses.create(
            model=model,
            text={"format": {"type": "json_schema", **EXTRACTION_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": DEVELOPER_MESSAGE},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise routing.ModelContractViolation(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = response.output_text
        return json.loads(text), response.model, response.id

    fn.model = model
    return fn


def extract_proper_nouns(article_text: str, support_text: str, key_phrases_text: str,
                          client: Optional[Any] = None) -> dict:
    user_message = build_user_message(article_text, support_text, key_phrases_text)
    fn = make_extraction_fn(user_message, client=client)
    parsed, model, response_id = fn()
    return {"items": parsed["items"], "model": model, "response_id": response_id}
