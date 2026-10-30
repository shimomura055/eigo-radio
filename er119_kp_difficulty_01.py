# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_01: 学習項目(Key Phrase/Key Word)候補の難易度4段階(易/中/難/激難(レア))判定。

ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-30、原文=docs/pm/delegation_log/2026-10-30_KP-DIFFICULTY-4LEVEL-DISPLAY-01_USER.md §4)。
新規flagなしの既定ON正規実装(選定Prompt P7/W5'・Gate・件数・順位には一切触れない。追加するのは候補への参考情報fieldのみ)。

設計(DESIGN_01.md): 候補生成の最終段(補完・Redundancy QA後)に**1 generate = 1 call**の軽量判定(gpt-6-luna、routing.SUPPORT_MODEL)を置く。
- 難易度は**Gateではない**(4.3): 候補を除外・並べ替え・件数変更しない。判定失敗・欠落は`unknown`(未判定)でfail-open(候補は全件そのまま提示)。
- 付与位置が候補生成の最終段1か所のため、初回/外側retry/補完(backfill)/再選定(reselect round)のいずれの候補にも同じ経路で付く。
  resumeはkp_candidates.jsonに保存済みの値を読む。
- 技術失敗(API例外・parse不能・構造不適合)はattempt 2回まで(他の段と同じ上限)→それでも失敗なら該当候補をunknownにして続行。
  routing違反/モデル不一致(FulltextSelectionError系)とSTOPは握らず伝播(他の段と同じ。bf.is_propagating_exception)。
- 保存形: candidate["difficulty"] = {"level": easy|medium|hard|rare|unknown, "label_ja": 易|中|難|激難(レア)|未判定, "reason_ja", "source": llm|fail_open}。
  doc["difficulty_grading"] = 監査record(version/prompt_id/prompt_sha256/model_id/response_id/status/件数/attempts)。
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Optional

DIFFICULTY_VERSION = "kp_difficulty_v1"
PROMPT_ID = "kp_difficulty_prompt_v1"
LEVELS = ("easy", "medium", "hard", "rare")
UNKNOWN = "unknown"
LABEL_JA = {"easy": "易", "medium": "中", "hard": "難", "rare": "激難(レア)", UNKNOWN: "未判定"}
MAX_ATTEMPTS = 2
LEVEL_CONTEXT = {"a2": "Standard", "b1b": "Advanced"}

PROMPT_TEXT = (
    "あなたは日本人の英語学習者向けの教材編集者です。以下に示す学習項目(英語の単語・フレーズ)それぞれについて、"
    "学習者にとっての**難易度を4段階**で判定してください。難易度は選定の合否を決めるものではなく、利用者が選ぶときの目安として表示されます。\n"
    "\n"
    "4段階の定義:\n"
    "- easy(易): 比較的基本的で習得しやすい表現。中学〜高校初級で習う語・熟語、日常会話で頻出する表現。\n"
    "- medium(中): 一般的な英語学習で一定の習熟が必要な表現。ニュースや読み物に普通に出てくるが、意味・用法の理解に練習が要るもの。\n"
    "- hard(難): 高度な語彙・熟語・用法の理解が必要な表現。抽象的・文語的・比喩的な用法、複数の意味を使い分ける句動詞・イディオムなど。\n"
    "- rare(激難・レア): 特に高度、または使用頻度が低く特殊性の強い表現。専門的・文学的・古風・地域限定の語、ほとんど辞書でしか見ない表現。\n"
    "\n"
    "判定の方針:\n"
    "1. 単語数や文字数だけで判定しない。短くても難しい語(例: 多義の句動詞)や、長くても易しい表現がある。\n"
    "2. 次を総合して直感的に判定する: 表現の使用頻度 / 語彙・熟語としての難しさ / 意味・用法の習得難易度 / 特殊性・希少性。\n"
    "3. 「この記事の学習レベル」(Standard/Advanced)は境界例の参考にとどめ、表現そのものの難しさを基準にする。\n"
    "4. 基準の目安(例): easy=look for, weather / medium=come up with, reliable / hard=stave off, disparity / rare=doff, perspicacious。\n"
    "5. 迷ったときは極端な段階を避け、より近い段階を選ぶ。全項目に必ず1つの段階を付ける。\n"
    "6. 各項目に、判定理由を日本語で1文(30字以内)添える。\n"
    "\n"
    "出力: 入力された全項目のidを1回ずつ、入力と同じ順で返す。"
)
PROMPT_SHA256 = hashlib.sha256(PROMPT_TEXT.encode("utf-8")).hexdigest()
ITEMS_DELIMITER = "\n\n【この記事の学習レベル】\n"
LIST_DELIMITER = "\n\n【判定する学習項目】\n"

JSON_SCHEMA = {
    "name": "kp_difficulty_grading",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {"items": {"type": "array", "items": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "level": {"type": "string", "enum": list(LEVELS)},
                           "reason_ja": {"type": "string"}},
            "required": ["id", "level", "reason_ja"], "additionalProperties": False}}},
        "required": ["items"], "additionalProperties": False,
    },
}


def build_message(cands: list, level: str) -> str:
    """Prompt本文は不変。学習レベルと項目listを後置(他の段と同じ本文後置方式)。"""
    lines = []
    for c in cands:
        lines.append(json.dumps({"id": c["candidate_id"], "expression": c.get("used_form") or c.get("selection_phrase"),
                                 "kind": c.get("kind") or "phrase", "meaning_ja": c.get("japanese_gloss") or "",
                                 "example": c.get("source_sentence") or ""}, ensure_ascii=False))
    return PROMPT_TEXT + ITEMS_DELIMITER + LEVEL_CONTEXT.get(level, str(level)) + LIST_DELIMITER + "\n".join(lines)


def prefix_intact(msg: str) -> bool:
    return msg.startswith(PROMPT_TEXT + ITEMS_DELIMITER)


def make_difficulty_fn(user_message: str, *, client: Any = None, model: Optional[str] = None) -> Callable:
    """returns fn() -> (raw_text, model_id, response_id)。他の補助段と同じ条件(reasoningはprovider default)。API呼出は実運用時のみ(testはmock.patch)。
    cost loggerはer005のOpenAI patch(global)が自動で記録する。"""
    import er105_kp_fulltext_selector_01 as ft
    if not prefix_intact(user_message):
        raise ft.FulltextSelectionError("難易度判定のmessage先頭がPromptでない(取り違え)")
    model = model or ft.SELECTION_MODEL_ID
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fn():
        try:
            response = client.responses.create(model=model, text={"format": {"type": "json_schema", **JSON_SCHEMA}},
                                               input=[{"role": "user", "content": user_message}])
        except Exception as e:
            if type(e).__name__ == "BadRequestError" or getattr(e, "status_code", None) == 400:
                raise ft.FulltextSelectionError(f"難易度判定APIが要求を拒否しました(HTTP 400、設定/schema不備): {e}") from e
            raise
        if response.model != model:
            raise ft.ModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise RuntimeError("難易度判定の応答が空です")
        return text, response.model, response.id

    fn.model = model
    return fn


def parse_response(raw: str, ids: set) -> dict:
    """returns {id: {"level","reason_ja"}}。JSON不能・構造不適合は ValueError。idの欠落・未知idは個別に扱う(欠落=呼出側でunknown)。
    重複idは最初の1件を採る。levelが定義外の項目はその項目だけ欠落扱い。"""
    try:
        d = json.loads(raw)
    except Exception as e:   # noqa: BLE001
        raise ValueError(f"JSONとして解釈できません: {e}") from e
    items = d.get("items") if isinstance(d, dict) else None
    if not isinstance(items, list):
        raise ValueError("itemsがlistでない")
    out = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        i, lv = it.get("id"), it.get("level")
        if i in ids and i not in out and lv in LEVELS:
            out[i] = {"level": lv, "reason_ja": (it.get("reason_ja") or "").strip()}
    return out


def unknown_entry(reason: str) -> dict:
    return {"level": UNKNOWN, "label_ja": LABEL_JA[UNKNOWN], "reason_ja": reason, "source": "fail_open"}


def grade(cands: list, level: str, *, process: Optional[str] = None, call_fn: Optional[Callable] = None) -> dict:
    """候補listを1 call(最大2 attempt)で判定。returns {"by_id": {candidate_id: difficulty dict}, "record": 監査record}。
    候補を増減・並べ替えしない。失敗時もby_idは全候補ぶん埋める(unknown=fail-open)。call_fn(msg)->fn() はtest差込み用。
    伝播例外: routing違反/モデル不一致/STOP(bf.is_propagating_exception)。"""
    import er119_kp_backfill_01 as bf
    rec = {"version": DIFFICULTY_VERSION, "prompt_id": PROMPT_ID, "prompt_sha256": PROMPT_SHA256, "status": "SKIPPED", "model_id": None,
           "response_id": None, "n_candidates": len(cands), "n_graded": 0, "n_unknown": 0, "attempts": [], "failure": None}
    if not cands:
        return {"by_id": {}, "record": rec}
    ids = [c["candidate_id"] for c in cands]
    by_id = {}
    msg = build_message(cands, level)
    if call_fn is None:
        import er105_kp_fulltext_selector_01 as ft
        import er006_model_routing_contract_01 as routing
        model = routing.require_model(process, routing.SUPPORT_MODEL) if process else routing.SUPPORT_MODEL
        if model != ft.SELECTION_MODEL_ID:
            raise ft.FulltextSelectionError(f"routing解決モデルが{ft.SELECTION_MODEL_ID}でない(実際: {model})")
        call_fn = lambda m: make_difficulty_fn(m, model=model)   # noqa: E731
    for attempt in range(1, MAX_ATTEMPTS + 1):
        a = {"attempt": attempt, "status": None}
        try:
            raw, model_id, response_id = call_fn(msg)()
            rec["model_id"], rec["response_id"] = model_id, response_id
            parsed = parse_response(raw, set(ids))
        except Exception as e:   # noqa: BLE001  技術失敗だけ握る(fail-open)。routing違反/STOPは伝播
            if bf.is_propagating_exception(e):
                raise
            a.update(status="FAILED", error=f"{type(e).__name__}: {e}")
            rec["attempts"].append(a)
            rec["failure"] = a["error"]
            continue
        a.update(status="OK", n_parsed=len(parsed))
        rec["attempts"].append(a)
        for i, v in parsed.items():
            by_id.setdefault(i, {"level": v["level"], "label_ja": LABEL_JA[v["level"]], "reason_ja": v["reason_ja"], "source": "llm"})
        if len(by_id) == len(ids):
            rec["failure"] = None
            break
        rec["failure"] = f"{len(ids) - len(by_id)}件の判定が欠落/不正"
    for i in ids:
        if i not in by_id:
            by_id[i] = unknown_entry("難易度を判定できませんでした(fail-open: 候補はそのまま提示)")
    rec["n_graded"] = sum(1 for v in by_id.values() if v["source"] == "llm")
    rec["n_unknown"] = len(ids) - rec["n_graded"]
    rec["status"] = "OK" if rec["n_unknown"] == 0 else ("PARTIAL" if rec["n_graded"] else "FAILED_OPEN")
    return {"by_id": by_id, "record": rec}


def apply_to_candidates(cands: list, level: str, *, process: Optional[str] = None, call_fn: Optional[Callable] = None) -> dict:
    """候補dictへ`difficulty`を**追加のみ**で付与し(既存fieldは無変更・件数/順序不変)、監査recordを返す。"""
    res = grade(cands, level, process=process, call_fn=call_fn)
    for c in cands:
        c["difficulty"] = res["by_id"][c["candidate_id"]]
    return res["record"]
