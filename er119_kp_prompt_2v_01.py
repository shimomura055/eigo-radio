# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02: Prompt 2-V(追加候補選定、R-1/I-2のFable確定判断)。

構成(R-1): Prompt 2(承認済み・一字一句固定・sha不変)は無変更のまま1 call目で上位3件を取る(=現行の承認済み挙動そのもの)。
本module のPrompt 2-Vは2 call目で「前記3件を除き、学習価値の高い順に最大5件+理由1文」を取る。
Prompt 2-Vは Prompt 2 の条件1〜5と最終確認文を1字も変えず、冒頭の件数文と条件6だけを置換する(testで差分を固定)。
sha256はこのfileで固定(PROMPT_2V_SHA256)。変更はユーザー承認が必要な品質基準の変更に当たりうるためtestで固定する。
Production導入: X/Zの候補生成(er119_kp_candidates_01)からのみ呼ばれる。A/B/C・Y Trialの共有関数は呼ばない。
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Optional

import er105_kp_fulltext_selector_01 as ft

PROMPT_2V_ID = "kp_prompt_2v"
SELECTOR_2V_MAX_ITEMS = 5

_P2_HEAD = "以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを**3つ**選んでください。\n"
_P2V_HEAD = ("以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを、"
             "**すでに選ばれた表現を除いて、学習価値の高い順に最大5つ**選んでください"
             "(すでに選ばれた表現は、記事本文の後ろに示します)。\n")
_P2_COND6 = "6. **3件選定**：条件を満たす候補から3件選ぶ。適切な候補が不足する場合のみ3件未満とし、数合わせはしない。\n"
_P2V_COND6 = ("6. **最大5件・順位付け**：すでに選ばれた表現と同一、または一方がもう一方を含む表現は選ばない。"
              "条件を満たす候補から、学習価値の高い順に最大5件を選び、1位から順に並べる。"
              "適切な候補が不足する場合のみ5件未満とし、数合わせはしない。"
              "各候補に、選んだ理由を日本語で1文(40字以内)添える。\n")

assert _P2_HEAD in ft.PROMPT_2_TEXT and _P2_COND6 in ft.PROMPT_2_TEXT, "Prompt 2の想定文言が変わっています(2-Vの差分基準が崩れた)"
PROMPT_2V_TEXT = ft.PROMPT_2_TEXT.replace(_P2_HEAD, _P2V_HEAD, 1).replace(_P2_COND6, _P2V_COND6, 1)
PROMPT_2V_SHA256 = hashlib.sha256(PROMPT_2V_TEXT.encode("utf-8")).hexdigest()
# 固定sha(testで照合)。Promptを変えるときはユーザー承認のうえここと用途testを更新する。
PROMPT_2V_SHA256_PINNED = "e1d5349ce2fda897b74f0350817ced0d7385842c170d066721eb3917f012f5ec"
assert PROMPT_2V_SHA256 == PROMPT_2V_SHA256_PINNED, "Prompt 2-Vが固定shaと一致しません(変更にはユーザー承認が必要)"

ALREADY_DELIMITER = "\n\n---\n\n【すでに選ばれた表現(これらは選ばない)】\n"

SELECTOR_2V_JSON_SCHEMA = {
    "name": "kp_fulltext_selection_p2v",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    # reason_jaはphrase直後(Opus R-1)。件数制約はschemaに置かずローカル検査(strict JSONのminItems/maxItems拒否を避ける、er105 OF-KPFT-P-10と同じ)
                    "properties": {"phrase": {"type": "string"}, "reason_ja": {"type": "string"}, "word_count": {"type": "integer"}},
                    "required": ["phrase", "reason_ja", "word_count"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_user_message(article_text: str, already_phrases: list, diagnostic_note: Optional[str] = None) -> str:
    msg = PROMPT_2V_TEXT + ft.BODY_DELIMITER + article_text + ALREADY_DELIMITER + "\n".join(f"- {p}" for p in already_phrases)
    if diagnostic_note:
        msg += ft.NOTE_DELIMITER + diagnostic_note
    return msg


def prompt_prefix_intact(user_message: str) -> bool:
    return user_message.startswith(PROMPT_2V_TEXT + ft.BODY_DELIMITER)


def parse_selection(raw_text: str) -> list:
    """returns [{"phrase","reason_ja","declared_word_count"}]。形式不正はft.ParseError。"""
    try:
        doc = json.loads(raw_text)
    except (TypeError, ValueError) as e:
        raise ft.ParseError(f"JSON解析失敗: {e}") from e
    if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
        raise ft.ParseError("トップレベルが{'items': [...]}でない")
    out = []
    for i, it in enumerate(doc["items"]):
        if not isinstance(it, dict) or not isinstance(it.get("phrase"), str) or not it["phrase"].strip():
            raise ft.ParseError(f"items[{i}].phraseが空/文字列でない")
        wc = it.get("word_count")
        rj = it.get("reason_ja")
        out.append({"phrase": it["phrase"].strip(), "reason_ja": rj.strip() if isinstance(rj, str) else "",
                    "declared_word_count": wc if isinstance(wc, int) and not isinstance(wc, bool) else None})
    return out


def make_vocab_selector_fn(user_message: str, *, client: Any = None, model: Optional[str] = None) -> Callable:
    """returns fn() -> (raw_text, model_id, response_id)。er105.make_selector_fnと同じ条件(reasoningはprovider default・developer messageなし)
    でschemaだけ2-V用。API呼出は実運用時のみ(testはこの関数をmock.patchする)。"""
    model = model or ft.SELECTION_MODEL_ID
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fn():
        try:
            response = client.responses.create(
                model=model,
                text={"format": {"type": "json_schema", **SELECTOR_2V_JSON_SCHEMA}},
                input=[{"role": "user", "content": user_message}],
            )
        except Exception as e:
            if type(e).__name__ == "BadRequestError" or getattr(e, "status_code", None) == 400:
                raise ft.FulltextSelectionError(f"2-V selector APIが要求を拒否しました(HTTP 400、設定/schema不備。retryしません): {e}") from e
            raise
        if response.model != model:
            raise ft.ModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise ft.FulltextSelectionError("2-V selector応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn
