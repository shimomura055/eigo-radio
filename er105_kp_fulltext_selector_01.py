# -*- coding: utf-8 -*-
"""KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_01: Key Phrase全文選定(Prompt 2・GPT-6 Luna・最大3件)の
**未配線module**(設計: docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/IMPLEMENTATION_DESIGN_01.md)。

Status: APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS。Production既存ファイルは一切import元から変更していない。
どのProduction経路からもimportされていない(配線は次委任・Opus条件Aレビュー後)。API呼出0(本moduleのimport時・
test時とも。実API呼出は`make_selector_fn()`が返す関数を呼んだときだけ)。

責務(本module=選定段のみ):
  記事全文 + 正式Prompt 2(一字一句固定)をLunaへ1回 -> 構造化出力(phrase, word_count)の厳密parse ->
  機械検証(本文連続一致[表記ゆれのみ吸収]・5語以内・3件以内・重複なし)+旧Production形式check(downstream互換)->
  原文spanと文IDを決定論的に確定 -> 既存canonicalizationが読むoriginal_items(旧Strategy L/DB Hybridと同形)へ変換。
  解析失敗・検証不適合はretry(上限2、旧Strategy Lと同じMAX_PRODUCTION_RETRY_ATTEMPTS)-> 上限でKEY_WORDS_STRUCTURE_INVALID等を
  返す(呼出側がstage失敗=fail-closed。手動override・黙示的補完・旧経路へのfallbackはしない)。

後段(canonicalization / gloss再整合 / Redundancy QA / Z SRC D1 gate / 音声 / 組立)は変更しない。
Family A/B/C(旧Strategy L・5件・4+1)は本moduleを使わない(開発対象外、27-7)。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from typing import Any, Callable, Optional

# ============================================================
# 定数(KP件数の単一の置き場。X/Z経路はここをimportする。旧共有定数prod.PRODUCTION_ITEM_COUNT=5はA/B/C用に不変)
# ============================================================
KP_COUNT_MAX = 3                 # ユーザー正式決定(2026-10-22): 各レベル最大3件
KP_COUNT_MIN = 1                 # 0件は選定失敗(fail-closed)。1〜2件は「適切な候補が不足」として許容(数合わせ禁止)
KP_WORDS_MAX = 5                 # Prompt 2「5語以内(絶対条件)」(スペース区切り)
SELECTION_MODEL_ID = "gpt-6-luna"          # ユーザー正式決定。actual model IDはresponse.modelで照合する
ALLOWED_PROCESSES = ("B1_SUPPORT", "A2_SUPPORT")   # er006_model_routing_contract_01でSUPPORT_MODEL(=gpt-6-luna)に束ねられるprocess
MAX_ATTEMPTS = 2                 # 旧Strategy Lの既存上限(prod.MAX_PRODUCTION_RETRY_ATTEMPTS)と同じ。独自に増減しない
BACKEND_ID = "fulltext_p2"       # sc.run_key_phrase_selection(kp_backend=...)に渡す値
FULLTEXT_SOURCE_REF_ID = "fulltext_exact_v1"   # 注意: 旧`source_reference_contract`キーは使わない(下記)

STATUS_PASS = "KEY_WORDS_STRUCTURE_PASS"       # 既存呼出側(`sel["status"] != "KEY_WORDS_STRUCTURE_PASS"`)と同値
STATUS_INVALID = "KEY_WORDS_STRUCTURE_INVALID"
STATUS_PARSE_FAILED = "PARSE_FAILED"
STATUS_TECHNICAL_FAILED = "TECHNICAL_GENERATION_FAILED"

# ============================================================
# 正式Prompt 2(ユーザー逐語、docs/pm/delegation_log/2026-10-22_KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01_USER.md §2の
# 2本の`---`の間の本文)。一字一句固定。変更はユーザーの明示承認が必要。sha256をtestで固定する。
# ============================================================
PROMPT_2_TEXT = (
    "以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを**3つ**選んでください。\n"
    "\n"
    "以下の順序で処理し、上位条件を優先してください。\n"
    "\n"
    "1. **本文一致（絶対条件）**：本文中の連続した語句だけを抜き出す。変更・言い換え・追加・創作は禁止。\n"
    "2. **5語以内（絶対条件）**：スペース区切りで正確に数える。6語以上は出力禁止。\n"
    "3. **学習ポイントの明確化と最小化（必須）**：学ぶべき語彙・熟語・表現を明確にし、意味と自然さを保てる最短の形で抽出する。"
    "不要な目的語・修飾語・文脈は除く。5語は上限であり、目標ではない。短縮によって学習価値が失われる場合のみ、必要な語を残す。\n"
    "4. **上級者向けの学習価値**：上級者でも学ぶ価値のある語彙・イディオム・慣用表現を優先する。\n"
    "5. **易しい表現の除外**：基本語だけで構成され、字面どおりに意味が分かる表現や、上級者なら知っている易しい表現は除外する。\n"
    "6. **3件選定**：条件を満たす候補から3件選ぶ。適切な候補が不足する場合のみ3件未満とし、数合わせはしない。\n"
    "\n"
    "**出力直前に各候補を本文と照合し、改変がないこと、5語以内であることを再確認してください。語数も併記してください。**"
)
# 本文受け渡し区切り(Trial KP6M/TRIAL-02/03と同一。Prompt本文は1字も変えず末尾に後置するだけ。TRIAL_RESULT_02 §8-2)
BODY_DELIMITER = "\n\n---\n\n【記事本文】\n"
# 再選定時のみ後置する補足(Redundancy QA NG等の機械診断。Prompt 2本文より後ろ=本文の後ろに置き、Prompt本文は不変)
NOTE_DELIMITER = "\n\n---\n\n【前回の選定結果に関する指摘(機械診断)】\n"

PROMPT_2_SHA256 = hashlib.sha256(PROMPT_2_TEXT.encode("utf-8")).hexdigest()

# 構造化出力schema(API側のtext.format。Prompt本文は変更しない。語数併記の指示にそのまま対応する)
SELECTOR_JSON_SCHEMA = {
    "name": "kp_fulltext_selection_p2",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "minItems": KP_COUNT_MIN,
                "maxItems": KP_COUNT_MAX,
                "items": {
                    "type": "object",
                    "properties": {"phrase": {"type": "string"}, "word_count": {"type": "integer"}},
                    "required": ["phrase", "word_count"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}


class FulltextSelectionError(RuntimeError):
    """選定段の異常(モデルrouting違反等。retryで直らない設定不備はfail-closedで即停止)。"""


class ModelMismatchError(FulltextSelectionError):
    """response.model != 要求model(actual model ID不一致。技術的失敗として扱う)。"""


# ============================================================
# Prompt組立
# ============================================================
def build_user_message(article_text: str, diagnostic_note: Optional[str] = None) -> str:
    """Prompt 2(固定)+区切り+記事全文。diagnostic_noteは再選定時のみ、本文の後ろに後置する(Prompt本文は不変)。"""
    msg = PROMPT_2_TEXT + BODY_DELIMITER + article_text
    if diagnostic_note:
        msg += NOTE_DELIMITER + diagnostic_note
    return msg


def prompt_prefix_intact(user_message: str) -> bool:
    """送信messageの先頭がPrompt 2と完全一致し、直後が区切りであること(Prompt改変の機械的検出)。"""
    return user_message.startswith(PROMPT_2_TEXT + BODY_DELIMITER)


# ============================================================
# 出力解析(厳密。構造化出力のJSONのみ受理。自由文からの手動補正・heuristic抽出はしない)
# ============================================================
class ParseError(ValueError):
    pass


def parse_selection(raw_text: str) -> list:
    """returns [{"phrase": str, "declared_word_count": int|None}, ...]。形式不正はParseError(retry対象)。"""
    try:
        doc = json.loads(raw_text)
    except (TypeError, ValueError) as e:
        raise ParseError(f"JSON解析失敗: {e}") from e
    if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
        raise ParseError("トップレベルが{'items': [...]}でない")
    out = []
    for i, it in enumerate(doc["items"]):
        if not isinstance(it, dict) or not isinstance(it.get("phrase"), str) or not it["phrase"].strip():
            raise ParseError(f"items[{i}].phraseが空/文字列でない")
        wc = it.get("word_count")
        out.append({"phrase": it["phrase"].strip(), "declared_word_count": wc if isinstance(wc, int) and not isinstance(wc, bool) else None})
    return out


# ============================================================
# 本文照合(Prompt 2「本文一致(絶対条件)」の機械検証)と原文span/文IDの決定論的確定
# 吸収する表記ゆれ=大文字小文字・アポストロフィ/引用符の種類・ダッシュの種類・連続空白のみ。語の変更は一切吸収しない。
# 文単位は既存の`er030_key_phrase_db_hybrid_core_01.build_sentence_units`(Family Z SRC D1と同一の文分割)を使う。
# ============================================================
_APOS = "'’‘ʼ`´"
_DASH = "-‐‑‒–—―"
_WORD_CH = r"A-Za-z0-9"


def _normalize_phrase(phrase: str) -> str:
    p = unicodedata.normalize("NFKC", phrase)
    p = p.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    return re.sub(r"\s+", " ", p).strip()


def _phrase_pattern(phrase: str) -> "re.Pattern":
    toks = _normalize_phrase(phrase).split(" ")
    parts = []
    for t in toks:
        buf = ""
        for ch in t:
            if ch in _APOS:
                buf += "[" + re.escape(_APOS) + "]"
            elif ch in _DASH:
                buf += "[" + re.escape(_DASH) + "]"
            else:
                buf += re.escape(ch)
        parts.append(buf)
    body = r"\s+".join(parts)
    # 語境界: 英数字の途中に一致しない("in the"が"within the"内に誤一致しない)
    return re.compile(r"(?<![" + _WORD_CH + r"])" + body + r"(?![" + _WORD_CH + r"])", re.IGNORECASE)


def count_words(phrase: str) -> int:
    """Prompt 2「スペース区切りで正確に数える」。"""
    return len([t for t in phrase.strip().split() if t])


def locate_phrase(units: list, phrase: str) -> list:
    """全文の文単位(units=build_sentence_units結果)から、phraseの連続一致を全て返す。
    returns [{"unit_index": i, "sentence_id": "S{i+1}", "span": 原文どおりのスライス, "sentence": unit raw_text}, ...](出現順)。
    文境界をまたぐ語句は一致しない(=本文一致不成立として扱う)。"""
    pat = _phrase_pattern(phrase)
    hits = []
    for i, u in enumerate(units):
        for m in pat.finditer(u["raw_text"]):
            hits.append({"unit_index": i, "sentence_id": f"S{i + 1}", "span": m.group(0), "sentence": u["raw_text"]})
    return hits


def _legacy_form_reasons(phrase: str) -> list:
    """下流互換precheck: 既存canonicalizationが必ず拒否する形(1〜5語・有限助動詞)を、API費用を使う前に検出する。
    既存validatorの値を再利用(再実装しない)。Prompt 2が許容する形でも、既存承認済み構造Validatorが拒否するなら
    その後段(canonicalization)は必ずINVALIDになるため、選定段でretryに回す(設計書§3-4)。"""
    import er003_key_words_canonicalization as kc   # 遅延import(test時に重いmodule群を不要に読まない)
    reasons = []
    if kc._contains_finite_auxiliary(phrase):
        reasons.append("有限助動詞を含む(既存canonicalization Validatorが拒否する形)")
    return reasons


def validate_and_resolve(selected: list, units: list) -> dict:
    """機械検証+原文span/文ID確定。returns {"ok": bool, "reasons": [...], "item_reasons": [...], "resolved": [...]}。
    blocking: 本文連続一致 / 実語数1〜5 / 件数1〜3 / 重複なし / 旧形式precheck。
    non-blocking記録: LLM申告語数と実語数の不一致、複数文に出現(first_of_N)。"""
    reasons, item_reasons, resolved = [], [], []
    if not (KP_COUNT_MIN <= len(selected) <= KP_COUNT_MAX):
        reasons.append(f"件数が{KP_COUNT_MIN}〜{KP_COUNT_MAX}の範囲外(実際: {len(selected)})")
    seen = set()
    for idx, s in enumerate(selected):
        phrase = s["phrase"]
        r = []
        wc = count_words(phrase)
        if not (1 <= wc <= KP_WORDS_MAX):
            r.append(f"語数が1〜{KP_WORDS_MAX}語でない(実際: {wc}語)")
        key = _normalize_phrase(phrase).lower()
        if key in seen:
            r.append("重複")
        seen.add(key)
        hits = locate_phrase(units, phrase) if wc >= 1 else []
        if not hits:
            r.append("本文に連続一致しない(変更・言い換え・創作、または文をまたぐ語句)")
        r.extend(_legacy_form_reasons(phrase))
        rec = {"index": idx, "phrase": phrase, "word_count": wc, "declared_word_count": s.get("declared_word_count"),
               "declared_word_count_mismatch": (s.get("declared_word_count") is not None and s.get("declared_word_count") != wc),
               "reasons": r}
        if hits:
            first = hits[0]
            rec.update(source_span=first["span"], source_sentence=first["sentence"], source_sentence_id=first["sentence_id"],
                       occurrence_count=len(hits), occurrence_sentence_ids=sorted({h["sentence_id"] for h in hits}),
                       resolution_method="fulltext_exact_unique" if len(hits) == 1 else "fulltext_exact_first_of_N")
        if r:
            item_reasons.append({"index": idx, "phrase": phrase, "reasons": r})
        resolved.append(rec)
    ok = not reasons and not item_reasons
    return {"ok": ok, "reasons": reasons, "item_reasons": item_reasons, "resolved": resolved}


def build_original_items(resolved: list) -> list:
    """既存canonicalizationが読むoriginal_items(旧Strategy L/DB Hybridと同形のキー)へ変換する。rankは選定順(1..n)。
    重要(契約調整): `source_reference_contract`キーは付けない。このキーが真だと既存canonicalizationの案A'窓拡張
    (`expand_dangling_source_span`)・`kp_extends_beyond_candidate`が候補ID方式前提で発火するため。全文選定では
    source_span=LLMが選んだ語句そのもの(原文スライス)であり、窓拡張は不要・不適切。代わりに`fulltext_source_ref`を付ける。
    japanese_glossは選定段では生成しない(Prompt 2は意味を出力しない)。None=gloss再整合工程の生成対象(設計書§4-3)。"""
    items = []
    for n, r in enumerate(resolved, start=1):
        items.append({
            "rank": n,
            "display_phrase": r["source_span"],          # 選定語句そのまま(原形化は後段canonicalizationの責務、設計書§4-2)
            "source_span": r["source_span"],
            "source_sentence": r["source_sentence"],
            "source_sentence_id": r["source_sentence_id"],
            "ja_gloss": None,
            "japanese_gloss": None,
            "fulltext_source_ref": FULLTEXT_SOURCE_REF_ID,
            "resolution_method": r["resolution_method"],
            "occurrence_count": r["occurrence_count"],
            "occurrence_sentence_ids": r["occurrence_sentence_ids"],
            "declared_word_count_mismatch": r["declared_word_count_mismatch"],
        })
    return items


# ============================================================
# 実API呼出(Luna)。routing contract経由でmodelを確定し、response.modelを照合する。このmoduleのimport時・test時は呼ばれない。
# ============================================================
def make_selector_fn(user_message: str, *, client: Any = None, model: Optional[str] = None) -> Callable:
    """returns fn() -> (raw_text, model_id, response_id)。reasoningはprovider default(Trial KP6M/TRIAL-02と同条件)。
    developer messageは付けない(Trialと同条件)。構造化出力schemaのみ追加(Prompt本文は変更しない)。"""
    model = model or SELECTION_MODEL_ID
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fn():
        response = client.responses.create(
            model=model,
            text={"format": {"type": "json_schema", **SELECTOR_JSON_SCHEMA}},
            input=[{"role": "user", "content": user_message}],
        )
        if response.model != model:
            raise ModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise FulltextSelectionError("selector応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


def resolve_model(process: Optional[str]) -> str:
    """routing contractでLuna(SUPPORT_MODEL)を確定する。processがB1_SUPPORT/A2_SUPPORT以外、または解決結果が
    gpt-6-lunaでなければ即停止(fail-closed、独自model指定を許さない)。"""
    if process not in ALLOWED_PROCESSES:
        raise FulltextSelectionError(f"processはB1_SUPPORT/A2_SUPPORTのみ(実際: {process!r})。全文選定はLuna固定")
    import er006_model_routing_contract_01 as routing   # 遅延import
    model = routing.require_model(process, routing.SUPPORT_MODEL)
    if model != SELECTION_MODEL_ID:
        raise FulltextSelectionError(f"routing解決モデルが{SELECTION_MODEL_ID}でない(実際: {model})")
    return model


# ============================================================
# 選定gate(retry込み)と、run_key_phrase_selection互換の入口
# ============================================================
def run_selection_gate(article_text: str, make_call_fn: Callable[[str], Callable], *, diagnostic_note: Optional[str] = None,
                       max_attempts: int = MAX_ATTEMPTS, units: Optional[list] = None) -> dict:
    """returns {"status", "items"(original_items形式), "attempts_detail", "model_id", "response_id", "shortfall", "user_message_sha256"}。
    attempt失敗(技術/parse/検証)は同一messageで最大max_attempts回。内容品質を理由とした再選定はしない(hard requirementのみ)。"""
    if units is None:
        import er030_key_phrase_db_hybrid_core_01 as core   # 遅延import
        units = core.build_sentence_units(article_text)
    user_message = build_user_message(article_text, diagnostic_note)
    assert prompt_prefix_intact(user_message), "Prompt 2が改変されている"
    msg_sha = hashlib.sha256(user_message.encode("utf-8")).hexdigest()
    attempts, last_status, last_model, last_resp = [], STATUS_TECHNICAL_FAILED, None, None
    for attempt in range(1, max_attempts + 1):
        fn = make_call_fn(user_message)
        try:
            raw, model_id, response_id = fn()
        except FulltextSelectionError as e:
            if isinstance(e, ModelMismatchError):
                attempts.append({"attempt": attempt, "status": STATUS_TECHNICAL_FAILED, "error": str(e), "raw_text": None})
                last_status = STATUS_TECHNICAL_FAILED
                continue
            raise
        except Exception as e:   # 通信等の技術的失敗(retry対象)
            attempts.append({"attempt": attempt, "status": STATUS_TECHNICAL_FAILED, "error": f"{type(e).__name__}: {e}", "raw_text": None})
            last_status = STATUS_TECHNICAL_FAILED
            continue
        last_model, last_resp = model_id, response_id
        try:
            selected = parse_selection(raw)
        except ParseError as e:
            attempts.append({"attempt": attempt, "status": STATUS_PARSE_FAILED, "error": str(e), "raw_text": raw,
                             "model": model_id, "response_id": response_id})
            last_status = STATUS_PARSE_FAILED
            continue
        v = validate_and_resolve(selected, units)
        attempts.append({"attempt": attempt, "status": STATUS_PASS if v["ok"] else STATUS_INVALID, "validation_reasons": v["reasons"],
                         "item_reasons": v["item_reasons"], "resolved": v["resolved"], "raw_text": raw, "model": model_id,
                         "response_id": response_id})
        if v["ok"]:
            items = build_original_items(v["resolved"])
            return {"status": STATUS_PASS, "items": items, "attempts_detail": attempts, "model_id": model_id,
                    "response_id": response_id, "shortfall": len(items) < KP_COUNT_MAX, "user_message_sha256": msg_sha}
        last_status = STATUS_INVALID
    return {"status": last_status, "items": None, "attempts_detail": attempts, "model_id": last_model, "response_id": last_resp,
            "shortfall": None, "user_message_sha256": msg_sha}


def run_fulltext_selection(article_text: str, out_dir: str, article_id: str, source_level: str, process: Optional[str] = None,
                           diagnostic_note: Optional[str] = None, *, make_call_fn: Optional[Callable[[str], Callable]] = None) -> dict:
    """`sc.run_key_phrase_selection(..., kp_backend="fulltext_p2")`が委譲する入口(配線は次委任)。
    戻り値は旧`_run_key_phrase_selection_strategy_l`と同じキー構成(status/parsed/model_id/original_items/kp_backend_used)に
    加え、Zの外側retryが参照する`parsed={"items": [...]}`を持つ。成果物: keywords_selector_prompt.txt / keywords_runtime_metadata.json。
    make_call_fn省略時のみ実API(Luna)を使う(test/mockは注入)。"""
    os.makedirs(out_dir, exist_ok=True)
    if make_call_fn is None:
        model = resolve_model(process)
        make_call_fn = lambda msg: make_selector_fn(msg, model=model)   # noqa: E731
    else:
        if process is not None and process not in ALLOWED_PROCESSES:
            raise FulltextSelectionError(f"processはB1_SUPPORT/A2_SUPPORTのみ(実際: {process!r})")
    gate = run_selection_gate(article_text, make_call_fn, diagnostic_note=diagnostic_note)
    user_message = build_user_message(article_text, diagnostic_note)
    with open(f"{out_dir}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)
    meta = {
        "article_id": article_id, "source_level": source_level, "kp_backend": BACKEND_ID, "prompt_id": "kp_prompt_2",
        "prompt_sha256": PROMPT_2_SHA256, "user_message_sha256": gate["user_message_sha256"], "record_status": "PRODUCTION",
        "model_requested": SELECTION_MODEL_ID, "model_id": gate["model_id"], "response_id": gate["response_id"],
        "final_status": gate["status"], "shortfall": gate["shortfall"], "kp_count_max": KP_COUNT_MAX,
        "attempts": len(gate["attempts_detail"]), "has_diagnostic_note": bool(diagnostic_note),
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in gate["attempts_detail"]],
    }
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    result = {"status": gate["status"], "parsed": ({"items": gate["items"]} if gate["items"] else None), "model_id": gate["model_id"],
              "kp_backend_used": BACKEND_ID, "kp_attempts": len(gate["attempts_detail"]), "shortfall": gate["shortfall"]}
    if gate["status"] == STATUS_PASS:
        result["original_items"] = gate["items"]
    return result


# ============================================================
# 原形化(語形の基本形化)の決定論validator【プロトタイプ・未配線】(設計書§4-2、Opus確認事項Q1)
# 背景: 旧経路は「選定Prompt」が基本形への整形を担い(display_phrase=基本形)、canonicalizationのRule7は
#   「display_phrase一致 / source_span内の連続部分文字列 / 人称一般化」以外を拒否する。全文選定ではdisplay_phrase=本文の
#   表層形(pushed prices up)になるため、基本形化(push prices up)は現行Rule7で拒否される。
# 方式: 人称一般化(`kc._is_valid_person_generalization`が閉じた語彙表による1対1トークン置換のみ許す)と同じ思想で、
#   「活用形→基本形の1対1トークン置換(語数不変)」だけを許す。語の追加・削除・別語への置換(raw beans->raw materials等)は許さない。
# 配線時はcanonicalizationのvalidator(`validate_canonicalization_item`)へ、fulltext由来itemに限って(`fulltext_source_ref`)
# 追加判定として組み込む(A/B/Cの旧経路は無変更)。
# ============================================================
_IRREGULAR_TO_BASE = {   # 閉じた不規則活用表(過去形/過去分詞/三単現以外)。拡張はここだけで行う
    "gave": "give", "given": "give", "took": "take", "taken": "take", "went": "go", "gone": "go", "came": "come",
    "made": "make", "got": "get", "gotten": "get", "ran": "run", "saw": "see", "seen": "see", "said": "say",
    "kept": "keep", "held": "hold", "brought": "bring", "thought": "think", "began": "begin", "begun": "begin",
    "broke": "break", "broken": "break", "fell": "fall", "fallen": "fall", "felt": "feel", "found": "find",
    "left": "leave", "lost": "lose", "met": "meet", "paid": "pay", "sold": "sell", "told": "tell", "stood": "stand",
    "understood": "understand", "wrote": "write", "written": "write", "drew": "draw", "drawn": "draw",
    "grew": "grow", "grown": "grow", "knew": "know", "known": "know", "led": "lead", "sent": "send", "spent": "spend",
    "built": "build", "caught": "catch", "chose": "choose", "chosen": "choose", "rose": "rise", "risen": "rise",
    "hit": "hit", "cut": "cut", "put": "put", "set": "set", "let": "let", "men": "man", "women": "woman",
    "people": "person", "children": "child",
}
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")


def _base_candidates(w: str) -> set:
    w = w.lower()
    c = set()
    if w in _IRREGULAR_TO_BASE:
        c.add(_IRREGULAR_TO_BASE[w])
    if len(w) > 3 and w.endswith("ies"):
        c.add(w[:-3] + "y")
    if len(w) > 3 and w.endswith("es"):
        c.add(w[:-2])
    if len(w) > 2 and w.endswith("s") and not w.endswith("ss"):
        c.add(w[:-1])
    if len(w) > 4 and w.endswith("ied"):
        c.add(w[:-3] + "y")
    for suf in ("ed", "ing"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            stem = w[: -len(suf)]
            c.add(stem)
            c.add(stem + "e")
            if len(stem) > 2 and stem[-1] == stem[-2]:
                c.add(stem[:-1])
    c.discard(w)
    return c


def is_valid_inflection_normalization(key_phrase: str, display_phrase: str) -> bool:
    """key_phraseがdisplay_phraseの『活用形->基本形(動詞の原形・名詞の単数等)』の1対1トークン置換のみで得られるか。
    語数不変・変化トークンが1つ以上・各変化トークンが基本形候補に一致すること。人称一般化との併用は
    人称代名詞->一般形(closed table)も同じ1対1置換として許す。"""
    import er003_key_words_canonicalization as kc   # 閉じた人称表を再利用(再実装しない)
    k = _TOKEN_RE.findall(unicodedata.normalize("NFKC", key_phrase or "").replace("’", "'"))
    d = _TOKEN_RE.findall(unicodedata.normalize("NFKC", display_phrase or "").replace("’", "'"))
    if not k or len(k) != len(d):
        return False
    changed = False
    for kt, dt in zip(k, d):
        kl, dl = kt.lower(), dt.lower()
        if kl == dl:
            continue
        changed = True
        if kl in _base_candidates(dl):
            continue
        if kl in (kc._PERSON_DEPENDENT_TO_GENERIC.get(dl) or ()):
            continue
        return False
    return changed
