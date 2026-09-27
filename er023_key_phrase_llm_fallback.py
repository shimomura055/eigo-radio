# ============================================================
# er023_key_phrase_llm_fallback.py
# KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
# 設計doc F-2: DB照合+除外Gate後の候補が4件未満の場合のみ、不足数を
# 補うための1回のLLM呼び出しを行う(既存Support経路と同モデル設定=
# ER-006-MODEL-ROUTING-CONTRACT-01のSUPPORT_MODEL="gpt-5.6-luna"を
# 流用、独自モデルを新設しない)。
# ============================================================

from __future__ import annotations

import json
from typing import Optional

import er003_key_words_min_unit as mu
import er006_model_routing_contract_01 as routing

FALLBACK_MODEL = routing.SUPPORT_MODEL  # "gpt-5.6-luna"(既存Support経路と同一)
FALLBACK_REASONING_EFFORT = "high"

FALLBACK_DEVELOPER_MESSAGE = (
    "英語ニュース記事から、リスニング学習者が他の文脈でも再利用しやすい"
    "短い表現(1〜5語)を追加で選んでください。主観的な「重要な表現」"
    "判断ではなく、以下の客観的基準にすべて合致するものだけを選んでください。"
)

_FALLBACK_ITEM_PROPERTIES = {
    "source_span": {"type": "string"},
    "display_phrase": {"type": "string"},
    "unit_type": {"type": "string", "enum": [
        "word", "phrase", "phrasal_verb", "idiom", "collocation", "discourse_expression"]},
    "reason": {"type": "string"},
}


def build_fallback_schema(gap_count: int) -> dict:
    return {
        "name": "key_phrase_db_trial_llm_fallback",
        "schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": gap_count,
                    "maxItems": gap_count,
                    "items": {
                        "type": "object",
                        "properties": _FALLBACK_ITEM_PROPERTIES,
                        "required": list(_FALLBACK_ITEM_PROPERTIES.keys()),
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["items"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def build_fallback_user_message(article_text: str, existing_candidates: list, gap_count: int) -> str:
    existing_list = "\n".join(f"- {c}" for c in existing_candidates) if existing_candidates else "(なし)"
    return f"""以下は確定済みの英語記事本文です。

---
{article_text}
---

既に選定済みの候補(重複を避けてください):
{existing_list}

上記に加えて、新たに{gap_count}件の候補を選んでください。各候補は以下の
条件をすべて満たすこと(これはhard requirementであり、満たさない候補は
無効です):
- 1〜5語(display_phraseの語数)
- 完全な文・節ではない(有限助動詞[is/are/was/were/has/have/had/will/
  would/can/could/should/may/might/must]を含む完全な節ではない)
- 本文中に実在する表現(source_spanは本文からの逐語抜粋であること)
- 他の文脈でも再利用しやすい表現である(記事固有の専門語・固有名詞
  だけではない)
- chunkとして覚える価値がある(単独の意味だけでなく、組み合わせとして
  意味のある単位)
- 既存の選定済み候補と意味・機能が重複しない
- 学習者にとって意味のある表現である

「重要そうな表現を選べ」という主観的な指示ではなく、上記の客観的条件で
判断してください。他記事・他レベルの選定結果、DB側の内部スコアは
考慮しないでください(そのような情報は与えられていません)。
"""


def make_fallback_selector_fn(user_message: str, client=None, model: str = FALLBACK_MODEL,
                              reasoning_effort: str = FALLBACK_REASONING_EFFORT,
                              gap_count: int = 1):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    schema = build_fallback_schema(gap_count)

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **schema}},
            input=[
                {"role": "developer", "content": FALLBACK_DEVELOPER_MESSAGE},
                {"role": "user", "content": user_message},
            ],
        )
        text = getattr(response, "output_text", None)
        usage = getattr(response, "usage", None)
        return text, response.model, response.id, usage

    return fn


def validate_fallback_items(items: list, article_text: str) -> dict:
    """既存hard requirement(er003_key_words_min_unit)をそのまま流用して
    検証する。"""
    item_reasons = []
    ok = True
    normalized_article = mu._normalize_for_match(article_text)
    for i, item in enumerate(items):
        reasons = []
        display_phrase = item.get("display_phrase", "")
        form = mu.validate_display_phrase_form(display_phrase)
        reasons.extend(form["reasons"])
        source_span = item.get("source_span", "")
        if source_span and mu._normalize_for_match(source_span) not in normalized_article:
            reasons.append("source_spanが本文に存在しない")
        if reasons:
            ok = False
        item_reasons.append({"index": i, "reasons": reasons})
    return {"ok": ok, "item_reasons": item_reasons}


def run_fallback_gate(article_text: str, existing_candidates: list, gap_count: int,
                      client=None, max_attempts: int = 2) -> dict:
    """MAX_PRODUCTION_RETRY_ATTEMPTS相当(初回+技術的失敗/hard requirement
    不適合時の再試行1回のみ)を踏襲する。既存のretry上限を独自に緩めない。"""
    user_message = build_fallback_user_message(article_text, existing_candidates, gap_count)
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        selector_fn = make_fallback_selector_fn(user_message, client=client, gap_count=gap_count)
        try:
            raw_text, model_id, response_id, usage = selector_fn()
        except Exception as e:
            attempts_detail.append({"attempt": attempt, "status": "TECHNICAL_GENERATION_FAILED",
                                    "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                continue
            return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts_detail, "items": []}
        try:
            parsed = json.loads(raw_text)
            items = parsed["items"]
        except Exception as e:
            attempts_detail.append({"attempt": attempt, "status": "PARSE_FAILED", "error": str(e)})
            if attempt < max_attempts:
                continue
            return {"status": "PARSE_FAILED", "attempts": attempts_detail, "items": []}

        validation = validate_fallback_items(items, article_text)
        attempts_detail.append({
            "attempt": attempt, "status": "PASS" if validation["ok"] else "HARD_REQUIREMENT_FAILED",
            "item_reasons": validation["item_reasons"], "model": model_id, "response_id": response_id,
            "usage": {"input_tokens": getattr(usage, "input_tokens", None),
                      "output_tokens": getattr(usage, "output_tokens", None)} if usage else None,
        })
        if validation["ok"]:
            for item in items:
                item["matched_dbs"] = []
                item["db_match_count"] = 0
                item["final_selection_reason"] = "llm_fallback"
            return {"status": "PASS", "attempts": attempts_detail, "items": items,
                    "model": model_id, "response_id": response_id}
        if attempt < max_attempts:
            continue
        return {"status": "HARD_REQUIREMENT_FAILED", "attempts": attempts_detail, "items": []}
    return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts_detail, "items": []}
