# ============================================================
# er064_kp_idiom_trial_01_extractor.py
# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase B4 (b1)
# LLM補助抽出(非透明複数語表現)。Trial専用。DB候補とは別ラベル(evidence=llm_noncompositional)。
# Pythonで決定論検証: 生本文の部分文字列一致ではなく、build_sentence_units のtoken列と照合する。
# Production(DB Hybrid)の「本文全文をLLMへ送らない」原則(CURRENT_SPEC:1847)に対する
# Trial限定の例外(Production採用時は別途ユーザー判断)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata

import er023_key_phrase_db_extraction as ext
import er030_key_phrase_db_hybrid_core_01 as core
import er003_key_words_production as prod

PROMPT_PATH = "er064_output/kp_idiom_trial_01/prompts/extractor_prompt_v1.txt"
MIN_WORDS, MAX_WORDS, ITEM_CAP = 2, 5, 5
LEVEL_DESC = {
    "std": "A2(英検3〜準2級相当。日常の基本語彙・高頻度の定型句は既知とみなす)",
    "adv": "B1(英検2級相当。基本的な句動詞・高頻度コロケーションは既知とみなすが、慣用句・比喩は未知の可能性が高い)",
}
KINDS = ["idiom_or_fixed_expression", "figurative_or_metaphorical_use", "nontransparent_collocation_or_phrasal"]
SCHEMA = {
    "name": "noncompositional_extraction",
    "schema": {
        "type": "object",
        "properties": {"items": {"type": "array", "items": {
            "type": "object",
            "properties": {"span": {"type": "string"}, "kind": {"type": "string", "enum": KINDS},
                           "reason_en": {"type": "string"}},
            "required": ["span", "kind", "reason_en"], "additionalProperties": False}}},
        "required": ["items"], "additionalProperties": False},
    "strict": True,
}
_NORM = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def prompt_template() -> str:
    return open(PROMPT_PATH, encoding="utf-8").read()


def prompt_sha() -> str:
    return hashlib.sha256(prompt_template().encode("utf-8")).hexdigest()


def build_prompt(article_text: str, level: str) -> str:
    return prompt_template().replace("{level_desc}", LEVEL_DESC[level]).replace("{article_text}", article_text)


def call_extractor(article_text: str, level: str, model: str, client=None) -> dict:
    """1回のAPI呼出(有料)。戻り値: raw_text/parsed/usage/response_id/model/elapsed_sec/prompt_sha256。"""
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()
    msg = build_prompt(article_text, level)
    t0 = time.time()
    resp = client.responses.create(
        model=model, reasoning={"effort": prod.SELECTOR_REASONING_EFFORT},
        text={"format": {"type": "json_schema", **SCHEMA}},
        input=[{"role": "developer", "content": prod.SELECTOR_DEVELOPER_MESSAGE},
               {"role": "user", "content": msg}])
    if resp.model != model:
        raise RuntimeError(f"model mismatch expected={model} actual={resp.model}")
    text = getattr(resp, "output_text", None)
    u = getattr(resp, "usage", None)
    usage = {}
    if u is not None:
        usage = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                 "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
    return {"raw_text": text, "parsed": json.loads(text), "usage": usage, "response_id": resp.id,
            "model": resp.model, "elapsed_sec": round(time.time() - t0, 3), "prompt_sha256": prompt_sha()}


def _norm_text(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").translate(_NORM)


def verify_span(span: str, sentence_units: list) -> dict:
    """決定論検証。OKなら candidate dict (shortlist互換) を返す。
    拒否理由: token_count_out_of_range / not_in_article_tokens / crosses_punctuation_or_format /
    all_closed_class / excluded_by_existing_gate。"""
    toks = ext._WORD_TOKEN_RE.findall(_norm_text(span))
    if len(toks) < MIN_WORDS or len(toks) > MAX_WORDS:
        return {"ok": False, "reason": "token_count_out_of_range", "span": span}
    low = [t.lower() for t in toks]
    if all(t in core._CLOSED for t in low):
        return {"ok": False, "reason": "all_closed_class", "span": span}
    token_hit = False
    for ui, u in enumerate(sentence_units):
        ut = [t.lower() for t in u["tokens"]]
        for i in range(0, len(ut) - len(low) + 1):
            if ut[i:i + len(low)] != low:
                continue
            token_hit = True
            real = u["tokens"][i:i + len(low)]
            surface = " ".join(real)
            # 句読点・書式をまたいでいないこと(shortlistのcontext_sentence_id付与と同じ \b 検索が成立)
            if not re.search(r"\b" + re.escape(surface.lower()) + r"\b", u["raw_text"].lower()):
                continue
            cand = {
                "surface_form": surface, "canonical_form": ext._normalize_key(surface), "n": len(real),
                "matched_dbs": [], "db_match_count": 0, "db_categories": ["llm_noncompositional"],
                "unit_type": ext.UNIT_TYPE_IDIOM, "cefr_level": None, "source_span": surface,
                "context_mismatch_rule": None, "important_noun_phrase_candidate": False,
                "repetition_count_in_article": None, "observed_surface_variants": [surface],
                "evidence": "llm_noncompositional",
            }
            gate = ext.apply_exclusion_gate(cand, [], {})
            if ((gate["too_easy_or_common"]["rule_determined"] and gate["too_easy_or_common"]["value"]) or
                    (gate["unnatural_out_of_context"]["rule_determined"] and
                     gate["unnatural_out_of_context"]["value"])):
                return {"ok": False, "reason": "excluded_by_existing_gate", "span": span}
            return {"ok": True, "candidate": cand, "sentence_index": ui, "span": span}
    return {"ok": False, "reason": "crosses_punctuation_or_format" if token_hit else "not_in_article_tokens",
            "span": span}


def build_llm_candidates(parsed: dict, sentence_units: list, existing_canonicals: set,
                         cap: int = ITEM_CAP) -> dict:
    """LLM出力 -> 検証済み候補。既存DB候補と同一canonicalは『重複』として除外(追加のみ)。
    capは検証通過後のitem数に対する上限(LLMの並び順=重要度順を保つ)。"""
    accepted, rejected, dup, seen = [], [], [], set()
    for it in (parsed.get("items") or []):
        v = verify_span(it.get("span", ""), sentence_units)
        v["kind"], v["reason_en"] = it.get("kind"), it.get("reason_en")
        if not v["ok"]:
            rejected.append(v)
            continue
        c = v["candidate"]
        if c["canonical_form"] in existing_canonicals or c["canonical_form"] in seen:
            dup.append({"span": it.get("span"), "canonical_form": c["canonical_form"]})
            continue
        if len(accepted) >= cap:
            rejected.append({"ok": False, "reason": "over_cap", "span": it.get("span")})
            continue
        seen.add(c["canonical_form"])
        c["llm_kind"], c["llm_reason_en"] = it.get("kind"), it.get("reason_en")
        accepted.append(c)
    return {"accepted": accepted, "rejected": rejected, "duplicate_of_existing": dup,
            "raw_item_count": len(parsed.get("items") or [])}
