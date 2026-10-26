# -*- coding: utf-8 -*-
"""KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_01: Key Phrase全文選定(Prompt 2・GPT-6 Luna・最大3件)の
**未配線module**(設計: docs/research/KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01/IMPLEMENTATION_DESIGN_01.md)。

Status: 委任_02(2026-10-22)でX/Z Productionへ配線(`sc.run_key_phrase_selection(kp_backend="fulltext_p2")`が委譲)。
Status表記はWIRED_CODE_PENDING_RUNTIME_EVIDENCE(runtime evidenceは翌JST日。PRODUCTION_WIREDとは呼ばない)。
Opus条件Aレビュー(OF-KPFT-P-01〜14)反映済み。API呼出0(本moduleのimport時・test時とも。実API呼出は
`make_selector_fn()`が返す関数を呼んだときだけ)。

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
import time
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
                # OF-KPFT-P-10: strictモードでminItems/maxItemsが拒否されると全呼出が400で止まるため、schemaには件数制約を置かず、
                # 件数(1〜KP_COUNT_MAX)はローカル検証(validate_and_resolve)だけで保証する。
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


def _crosses_sentence_boundary(units: list, phrase: str) -> bool:
    """単一文内には一致しないが、隣接する2文をまたぐと(文末記号を挟んで)語が連続する語句か(OF-KPFT-P-10: 理由の区別用。受理はしない)。"""
    toks = [t for t in _normalize_phrase(phrase).split(" ") if t]
    if len(toks) < 2 or len(units) < 2:
        return False
    gap = r"[^" + _WORD_CH + r"]+"
    pat = re.compile(r"(?<![" + _WORD_CH + r"])" + gap.join(re.escape(t) for t in toks) + r"(?![" + _WORD_CH + r"])", re.IGNORECASE)
    for i in range(len(units) - 1):
        first = units[i]["raw_text"]
        joined = first + " " + units[i + 1]["raw_text"]
        for m in pat.finditer(joined):
            if m.start() < len(first) < m.end():
                return True
    return False


def _legacy_form_reasons(phrase: str) -> list:
    """下流互換precheck: 既存canonicalizationが必ず拒否する形(1〜5語・有限助動詞)を、API費用を使う前に検出する。
    既存validatorの値を再利用(再実装しない)。Prompt 2が許容する形でも、既存承認済み構造Validatorが拒否するなら
    その後段(canonicalization)は必ずINVALIDになるため、選定段でretryに回す(設計書§3-4)。"""
    import er003_key_words_canonicalization as kc   # 遅延import(test時に重いmodule群を不要に読まない)
    reasons = []
    if contains_finite_aux_role_based(phrase):   # 委任_03 区分1(2): have/has/hadは役割判定(fulltext経路。法助動詞・be系は従来どおり拒否)
        reasons.append("有限助動詞を含む(既存canonicalization Validatorが拒否する形)")
    reasons.extend(numeric_placeholder_reasons(phrase))   # P-13: 数値placeholder型の回避(CURRENT_SPEC:470-472)
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
            if _crosses_sentence_boundary(units, phrase):
                r.append("文の境界をまたいでいる(1文の中の連続した語句だけを選ぶ)")
            else:
                r.append("本文に連続一致しない(変更・言い換え・創作)")
        r.extend(_legacy_form_reasons(phrase))
        rec = {"index": idx, "phrase": phrase, "word_count": wc, "declared_word_count": s.get("declared_word_count"),
               "declared_word_count_mismatch": (s.get("declared_word_count") is not None and s.get("declared_word_count") != wc),
               "reasons": r}
        if hits:
            first = hits[0]
            rec.update(source_span=first["span"], source_sentence=first["sentence"], source_sentence_id=first["sentence_id"],
                       occurrence_count=len(hits), occurrence_sentence_ids=sorted({h["sentence_id"] for h in hits}),
                       # OF-KPFT-P-06: Z D1 gateが同名`resolution_method`を`exact`で上書きするため、別名で保持する。
                       selection_resolution_method="fulltext_exact_unique" if len(hits) == 1 else "fulltext_exact_first_of_N")
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
            "selection_resolution_method": r["selection_resolution_method"],
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
        try:
            response = client.responses.create(
                model=model,
                text={"format": {"type": "json_schema", **SELECTOR_JSON_SCHEMA}},
                input=[{"role": "user", "content": user_message}],
            )
        except Exception as e:   # OF-KPFT-P-10: schema拒否(HTTP 400)等はretryで直らない設定不備=即停止(技術的失敗として再試行しない)
            if type(e).__name__ == "BadRequestError" or getattr(e, "status_code", None) == 400:
                raise FulltextSelectionError(f"selector APIが要求を拒否しました(HTTP 400、設定/schema不備。retryしません): {e}") from e
            raise
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
def phrase_key(phrase: str) -> str:
    """KP-OUTER-RETRY-SAME-PHRASE-FIX: 同一句判定用の正規化キー(NFKC・空白正規化・小文字化)。"""
    return _normalize_phrase(phrase or "").lower()


def build_machine_note(attempt_record: dict, history: Optional[list] = None) -> str:
    """P-07: 直前attemptの機械診断(不適合だった語句と理由)を2回目の選定noteにする。Prompt 2本文は変更せず、本文の後ろに置く。
    history(KP-OUTER-RETRY-SAME-PHRASE-FIX): それ以前のattemptで不適合だった語句[{"phrase","reasons"}]を累積して併記する(同一句の再選択を防ぐ)。"""
    lines = []
    if attempt_record.get("status") == STATUS_PARSE_FAILED:
        lines.append("- 前回の出力は所定のJSON形式として解釈できませんでした。")
    for r in attempt_record.get("validation_reasons") or []:
        lines.append(f"- {r}")
    cur = set()
    for ir in attempt_record.get("item_reasons") or []:
        cur.add(phrase_key(ir["phrase"]))
        lines.append(f"- 「{ir['phrase']}」: " + " / ".join(ir["reasons"]))
    prior = [h for h in (history or []) if phrase_key(h["phrase"]) not in cur]
    if not lines and not prior:
        return ""
    out = ""
    if lines:
        out = ("前回の選定結果のうち、次の点が機械検証で不適合でした。該当する語句を、条件を満たす別の語句に置き換えて選び直してください"
               "(不適合でなかった語句は、そのまま使ってかまいません)。\n" + "\n".join(lines))
    if prior:
        out += ("\n\n" if out else "") + build_exclusion_note(prior)
    return out


def build_exclusion_note(excluded: list) -> str:
    """KP-OUTER-RETRY-SAME-PHRASE-FIX: 『次の語句は選ばない(理由付き)』のnote(本文後置・Prompt 2本文は不変)。excluded=[{"phrase","reasons":[...]}]。"""
    if not excluded:
        return ""
    lines = [f"- 「{e['phrase']}」: " + " / ".join(e.get("reasons") or ["不適合"]) for e in excluded]
    return ("次の語句は、これまでの検証で不適合と確定しています。同じ語句、または同じ理由で不適合になる語句は選ばないでください"
            "(条件を満たす別の語句がなければ、無理に3件に揃えず、適切な語句だけを選んでください)。\n" + "\n".join(lines))


def apply_exclusions(v: dict, excluded: Optional[list], *, final_attempt: bool, min_keep: int = KP_COUNT_MIN) -> dict:
    """KP-OUTER-RETRY-SAME-PHRASE-FIX: 外側retryで不適合確定済みの語句(excluded、正規化後一致)が選定に再び含まれたら、
    Luna(canonicalization)呼出前に機械検証で不適合とする。通常attemptはitem_reasonsへ理由追加(=再選定へ)。最終attemptは、残るitemが
    min_keep件以上なら除外句だけを落としてshortfall確定(数合わせ/条件緩和なし)、残らなければ不適合のまま。入力dictは変更しない。
    除外した語句は v["exclusion_dropped"] / 不適合化は v["exclusion_hits"] に残す。"""
    out = {k: (list(val) if isinstance(val, list) else val) for k, val in v.items()}
    out.setdefault("exclusion_hits", [])
    out.setdefault("exclusion_dropped", [])
    if not excluded:
        return out
    ex = {phrase_key(e["phrase"]): e for e in excluded}
    resolved = [dict(r) for r in v.get("resolved", [])]
    item_reasons = [dict(ir, reasons=list(ir["reasons"])) for ir in v.get("item_reasons", [])]
    hit_idx = {r["index"] for r in resolved if phrase_key(r["phrase"]) in ex}
    if not hit_idx:
        return out
    hits = [{"index": r["index"], "phrase": r["phrase"], "prior_reasons": list(ex[phrase_key(r["phrase"])].get("reasons") or [])}
            for r in resolved if r["index"] in hit_idx]
    keep = [r for r in resolved if r["index"] not in hit_idx]
    if final_attempt and len(keep) >= min_keep:
        item_reasons = [ir for ir in item_reasons if ir["index"] not in hit_idx]
        reasons = [x for x in out.get("reasons", []) if not x.startswith("件数が")]
        if not (KP_COUNT_MIN <= len(keep) <= KP_COUNT_MAX):
            reasons.append(f"件数が{KP_COUNT_MIN}〜{KP_COUNT_MAX}の範囲外(実際: {len(keep)})")
        out.update(resolved=keep, item_reasons=item_reasons, reasons=reasons, exclusion_dropped=hits,
                   ok=(not reasons and not item_reasons))
        return out
    by_idx = {ir["index"]: ir for ir in item_reasons}
    for h in hits:
        msg = "外側retryで不適合と確定済みの語句の再選択(前回の理由: " + (" / ".join(h["prior_reasons"]) or "不適合") + ")"
        if h["index"] in by_idx:
            by_idx[h["index"]]["reasons"].append(msg)
        else:
            item_reasons.append({"index": h["index"], "phrase": h["phrase"], "reasons": [msg]})
        for r in resolved:
            if r["index"] == h["index"]:
                r["reasons"] = list(r.get("reasons", [])) + [msg]
    out.update(resolved=resolved, item_reasons=item_reasons, exclusion_hits=hits, ok=False)
    return out


def merge_notes(*notes) -> Optional[str]:
    parts = [n for n in notes if n]
    return "\n\n".join(parts) if parts else None


def _cmu_gate_meta(cmu, lexicon: dict, attempts: list) -> dict:
    """選定metadataに記録するCMU条件の適用結果(OF-KPQ-P-05/P-08(a))。CMU未登録が原因のretry回と、最終attemptでの除外を残す。"""
    cmu_attempts = [a["attempt"] for a in attempts if any("CMU発音辞書" in r for ir in (a.get("item_reasons") or []) for r in ir.get("reasons", []))
                    or a.get("cmu_excluded")]
    excluded = [x for a in attempts for x in (a.get("cmu_excluded") or [])]
    return {"version": cmu.CHECK_VERSION, "applied": True, "lexicon": lexicon, "attempts_with_cmu_reason": cmu_attempts,
            "excluded": excluded}


def run_selection_gate(article_text: str, make_call_fn: Callable[[str], Callable], *, diagnostic_note: Optional[str] = None,
                       max_attempts: int = MAX_ATTEMPTS, units: Optional[list] = None,
                       sleep_fn: Optional[Callable[[float], None]] = None, excluded_phrases: Optional[list] = None) -> dict:
    """returns {"status", "items"(original_items形式), "attempts_detail", "model_id", "response_id", "shortfall",
    "user_message_sha256", "messages"}。attempt失敗(技術/parse/検証)は最大max_attempts回。
    OF-KPFT-P-07: 2回目以降は直前の機械診断noteを本文の後ろに後置して再選定する(Prompt 2本文は不変)。技術失敗の再試行前は待機する
    (canonicalizationのsleep_fn(2)と同じ思想)。内容品質を理由とした再選定はしない(hard requirementのみ)。"""
    if units is None:
        import er030_key_phrase_db_hybrid_core_01 as core   # 遅延import
        units = core.build_sentence_units(article_text)
    # KP-QUALITY-2ITEMS(2026-10-22、OF-KPQ-P-05): 『構成する全英単語がCMU発音辞書に登録済み』条件の辞書をAPI支出の前にpreflight(不備=fail-closedで例外)。
    import er108_kp_cmu_lexicon_gate_01 as cmu
    cmu_lexicon = cmu.preflight()
    sleep_fn = sleep_fn if sleep_fn is not None else time.sleep
    attempts, messages = [], []
    last_status, last_model, last_resp = STATUS_TECHNICAL_FAILED, None, None
    machine_note = None
    history = []   # KP-OUTER-RETRY-SAME-PHRASE-FIX: 以前のattemptで不適合だった語句(累積。次のmachine_noteへ併記)
    excluded_phrases = list(excluded_phrases or [])

    def _acc(rec):
        seen = {phrase_key(h["phrase"]) for h in history}
        for ir in rec.get("item_reasons") or []:
            if phrase_key(ir["phrase"]) not in seen:
                history.append({"phrase": ir["phrase"], "reasons": list(ir["reasons"])})
                seen.add(phrase_key(ir["phrase"]))
    for attempt in range(1, max_attempts + 1):
        user_message = build_user_message(article_text, merge_notes(diagnostic_note, machine_note))
        assert prompt_prefix_intact(user_message), "Prompt 2が改変されている"
        messages.append(user_message)
        msg_sha = hashlib.sha256(user_message.encode("utf-8")).hexdigest()
        fn = make_call_fn(user_message)
        try:
            raw, model_id, response_id = fn()
        except FulltextSelectionError as e:
            if isinstance(e, ModelMismatchError):
                attempts.append({"attempt": attempt, "status": STATUS_TECHNICAL_FAILED, "error": str(e), "raw_text": None,
                                 "user_message_sha256": msg_sha})
                last_status = STATUS_TECHNICAL_FAILED
                if attempt < max_attempts:
                    sleep_fn(2)
                continue
            raise
        except Exception as e:   # 通信等の技術的失敗(retry対象)
            attempts.append({"attempt": attempt, "status": STATUS_TECHNICAL_FAILED, "error": f"{type(e).__name__}: {e}", "raw_text": None,
                             "user_message_sha256": msg_sha})
            last_status = STATUS_TECHNICAL_FAILED
            if attempt < max_attempts:
                sleep_fn(2)
            continue
        last_model, last_resp = model_id, response_id
        try:
            selected = parse_selection(raw)
        except ParseError as e:
            rec = {"attempt": attempt, "status": STATUS_PARSE_FAILED, "error": str(e), "raw_text": raw,
                   "model": model_id, "response_id": response_id, "user_message_sha256": msg_sha}
            attempts.append(rec)
            machine_note = build_machine_note(rec, history)
            last_status = STATUS_PARSE_FAILED
            continue
        v = validate_and_resolve(selected, units)
        # KP-QUALITY-2ITEMS M1: 構成する全英単語のCMU登録確認(語単位)。未登録語itemは機械診断noteで再選定、最終attemptはCMU未登録のみが原因なら除外してshortfall確定。
        v = apply_exclusions(v, excluded_phrases, final_attempt=(attempt == max_attempts))
        v = cmu.apply_cmu_to_validation(v, final_attempt=(attempt == max_attempts))
        rec = {"attempt": attempt, "status": STATUS_PASS if v["ok"] else STATUS_INVALID, "validation_reasons": v["reasons"],
               "item_reasons": v["item_reasons"], "resolved": v["resolved"], "cmu_excluded": v.get("cmu_excluded") or [],
               "exclusion_hits": v.get("exclusion_hits") or [], "exclusion_dropped": v.get("exclusion_dropped") or [], "raw_text": raw, "model": model_id,
               "response_id": response_id, "user_message_sha256": msg_sha}
        attempts.append(rec)
        if v["ok"]:
            items = build_original_items(v["resolved"])
            return {"status": STATUS_PASS, "items": items, "attempts_detail": attempts, "model_id": model_id,
                    "response_id": response_id, "shortfall": len(items) < KP_COUNT_MAX, "user_message_sha256": msg_sha,
                    "messages": messages, "cmu_gate": _cmu_gate_meta(cmu, cmu_lexicon, attempts)}
        machine_note = build_machine_note(rec, history)
        _acc(rec)
        last_status = STATUS_INVALID
    return {"status": last_status, "items": None, "attempts_detail": attempts, "model_id": last_model, "response_id": last_resp,
            "shortfall": None, "user_message_sha256": attempts[-1].get("user_message_sha256") if attempts else None,
            "messages": messages, "cmu_gate": _cmu_gate_meta(cmu, cmu_lexicon, attempts)}


def run_fulltext_selection(article_text: str, out_dir: str, article_id: str, source_level: str, process: Optional[str] = None,
                           diagnostic_note: Optional[str] = None, *, make_call_fn: Optional[Callable[[str], Callable]] = None,
                           sleep_fn: Optional[Callable[[float], None]] = None, excluded_phrases: Optional[list] = None) -> dict:
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
    gate = run_selection_gate(article_text, make_call_fn, diagnostic_note=diagnostic_note, sleep_fn=sleep_fn,
                              excluded_phrases=excluded_phrases)
    for n, msg in enumerate(gate["messages"], start=1):
        with open(f"{out_dir}/keywords_selector_prompt.txt" if n == 1 else f"{out_dir}/keywords_selector_prompt_attempt{n}.txt",
                  "w", encoding="utf-8") as f:
            f.write(msg)
    # OF-KPFT-P-10: attemptごとの生出力を監査用に保存する(metadata本体はraw_textを含めない)。
    with open(f"{out_dir}/keywords_selector_raw_attempts.json", "w", encoding="utf-8") as f:
        json.dump([{"attempt": a["attempt"], "status": a["status"], "raw_text": a.get("raw_text"), "error": a.get("error")}
                   for a in gate["attempts_detail"]], f, ensure_ascii=False, indent=2)
    meta = {
        "article_id": article_id, "source_level": source_level, "kp_backend": BACKEND_ID, "prompt_id": "kp_prompt_2",
        "prompt_sha256": PROMPT_2_SHA256, "user_message_sha256": gate["user_message_sha256"], "record_status": "PRODUCTION",
        "model_requested": SELECTION_MODEL_ID, "model_id": gate["model_id"], "response_id": gate["response_id"],
        "final_status": gate["status"], "shortfall": gate["shortfall"], "kp_count_max": KP_COUNT_MAX,
        "kp_backend_used": BACKEND_ID,
        "attempts": len(gate["attempts_detail"]), "has_diagnostic_note": bool(diagnostic_note),
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in gate["attempts_detail"]],
        "cmu_gate": gate.get("cmu_gate"),
        "outer_excluded_phrases": [{"phrase": e["phrase"], "reasons": list(e.get("reasons") or [])} for e in (excluded_phrases or [])],
    }
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    result = {"status": gate["status"], "parsed": ({"items": gate["items"]} if gate["items"] else None), "model_id": gate["model_id"],
              "kp_backend_used": BACKEND_ID, "kp_attempts": len(gate["attempts_detail"]), "shortfall": gate["shortfall"]}
    if gate["status"] == STATUS_PASS:
        result["original_items"] = gate["items"]
    return result


# ============================================================
# 原形化(語形の基本形化)の決定論validator(設計書§4-2、Opus条件A Q1/OF-KPFT-P-02/P-04)
# 背景: 旧経路は「選定Prompt」が基本形への整形を担い(display_phrase=基本形)、canonicalizationのRule7は
#   「display_phrase一致 / source_span内の連続部分文字列 / 人称一般化」以外を拒否する。全文選定ではdisplay_phrase=本文の
#   表層形(pushed prices up)になるため、基本形化(push prices up)は現行Rule7で拒否される。
# 方式: 人称一般化(`kc._is_valid_person_generalization`が閉じた語彙表による1対1トークン置換のみ許す)と同じ思想で、
#   「display_phraseの連続したトークン範囲(語数=key_phraseの語数)」に対する1対1トークン置換だけを許す。
#   語の追加・削除・並べ替え・別語への置換(raw beans->raw materials等)は許さない。
# 誤受理防止(OF-KPFT-P-04): (1)動詞の活用形変換は、key_phrase内の先頭トークンかtoの直後に限り、かつ直後が限定詞/代名詞/不変化詞/前置詞
#   (または句末が不変化詞)の句動詞・他動詞句に限る(heated debate->heat debate等の形容詞化分詞を通さない)。過去形専用の不規則形
#   (gave/took等)は曖昧さが無いため直後条件を課さない。(2)複数->単数は句末トークンに限り、閉じた除外表(news/goods/means/sales等)を拒否。
#   (3)is/are/was/were/been->be、has/had->have、does/did->doは不規則表で扱う。
# 範囲(開示): 旧経路の選定Promptが担っていた「語順の整理」(took off players->take a player off)は含まない(安全側への縮小)。
#   V+名詞(raised concerns等)は形容詞/名詞修飾との区別がつかないため基本形化せず、表層形のまま(=Rule7の無変更)とする。
# ============================================================
_PAST_ONLY_IRREGULAR = {   # 過去形専用(形容詞/名詞の用法が実質無い)。位置制約のみ・直後条件なし
    "gave": "give", "took": "take", "went": "go", "came": "come", "made": "make", "got": "get", "ran": "run",
    "kept": "keep", "brought": "bring", "thought": "think", "began": "begin", "broke": "break", "fell": "fall",
    "paid": "pay", "told": "tell", "stood": "stand", "understood": "understand", "wrote": "write", "drew": "draw",
    "grew": "grow", "knew": "know", "sent": "send", "caught": "catch", "chose": "choose", "rose": "rise",
    "said": "say", "met": "meet", "sold": "sell", "led": "lead",
}
_AMBIGUOUS_IRREGULAR = {   # 過去分詞/形容詞・名詞用法がありうる不規則形(直後条件を課す)
    "given": "give", "taken": "take", "gone": "go", "gotten": "get", "seen": "see", "saw": "see", "held": "hold",
    "begun": "begin", "broken": "break", "fallen": "fall", "felt": "feel", "found": "find", "left": "leave",
    "lost": "lose", "spent": "spend", "written": "write", "drawn": "draw", "grown": "grow", "known": "know",
    "built": "build", "chosen": "choose", "risen": "rise",
}
_FUNCTION_VERB_FORMS = {   # be/have/do系(語彙的な曖昧さが無い)。位置制約のみ
    "is": "be", "are": "be", "was": "be", "were": "be", "been": "be", "being": "be", "am": "be",
    "has": "have", "had": "have", "having": "have", "does": "do", "did": "do", "done": "do", "doing": "do",
}
_IRREGULAR_PLURAL = {"men": "man", "women": "woman", "children": "child", "feet": "foot", "teeth": "tooth", "mice": "mouse"}
_PLURAL_EXCLUDE = frozenset({   # 単数化すると意味が変わる/単数形が別義の語(閉じた除外表。OF-KPFT-P-04)
    "news", "goods", "means", "arms", "glasses", "savings", "earnings", "odds", "terms", "clothes", "series", "species",
    "headquarters", "belongings", "sales", "customs", "premises", "outskirts", "remains", "thanks", "wages", "riches",
    "politics", "economics", "physics", "mathematics", "athletics", "statistics", "ethics", "dynamics", "electronics",
    "jeans", "pants", "trousers", "shorts", "scissors", "surroundings", "stairs", "proceeds", "feelings", "people",
    "bus", "gas", "lens", "focus", "status", "bonus", "campus", "virus", "census", "chaos", "access", "success", "business",
    "progress", "process", "class", "mass", "press", "stress", "loss", "boss", "glass", "grass", "pass", "dress",
})
_PARTICIPIAL_ADJ_EXCLUDE = frozenset({   # 形容詞化した分詞(動詞の基本形化の対象にしない)
    "heated", "mixed", "limited", "advanced", "skilled", "experienced", "tired", "aged", "married", "damaged", "detailed",
    "seasoned", "charged", "wounded", "closed", "united", "related", "involved", "interested", "excited", "worried",
    "concerned", "surprised", "talented", "gifted", "determined", "dedicated", "complicated", "sophisticated",
    "established", "estimated", "expected", "unexpected", "unlimited", "committed", "retired", "unmarked", "named",
    "rising", "growing", "leading", "living", "working", "missing", "existing", "aging", "ongoing", "lasting",
    "surprising", "mounting", "striking", "booming", "emerging", "declining", "increasing", "decreasing", "remaining",
    "challenging", "interesting", "exciting", "boring", "amazing", "shocking", "puzzling", "pressing", "binding",
    "outgoing", "upcoming", "incoming", "following", "preceding", "opening", "closing", "building", "meeting",
    "setting", "spending", "housing", "banking", "training", "marketing", "shipping", "sitting", "standing",
})
_GUARD_DET = frozenset({
    "a", "an", "the", "some", "any", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their",
    "one's", "someone's", "somebody's", "one", "someone", "somebody", "oneself", "it", "them", "him", "me", "us", "you",
})
_GUARD_PARTICLE = frozenset({
    "up", "down", "off", "out", "over", "back", "away", "in", "on", "along", "through", "by", "apart", "aside",
    "together", "forward", "around", "about", "across", "after", "ahead", "into", "onto", "for", "with", "at", "to",
    "from", "of", "under", "behind", "past", "against", "between", "toward", "towards", "upon", "without", "within",
})
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")


def _verb_base_candidates(w: str) -> set:
    """regular活用(-s/-es/-ies/-ed/-ied/-ing)の基本形候補。w=小文字。irregularは別表。"""
    c = set()
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


def _plural_base_candidates(w: str) -> set:
    if w in _IRREGULAR_PLURAL:
        return {_IRREGULAR_PLURAL[w]}
    c = set()
    if len(w) > 3 and w.endswith("ies"):
        c.add(w[:-3] + "y")
    if len(w) > 4 and w.endswith(("ches", "shes", "sses", "xes", "zes")):
        c.add(w[:-2])
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        c.add(w[:-1])
    c.discard(w)
    return c


def _guard_ok(key_tokens: list, idx: int) -> bool:
    """動詞活用の変換を許す文脈: 直後が限定詞/代名詞/不変化詞/前置詞、または句末が不変化詞(句動詞: pushed prices up)。"""
    nxt = key_tokens[idx + 1].lower() if idx + 1 < len(key_tokens) else None
    if nxt is not None and (nxt in _GUARD_DET or nxt in _GUARD_PARTICLE):
        return True
    return len(key_tokens) > idx + 1 and key_tokens[-1].lower() in _GUARD_PARTICLE


def _token_pair_ok(kt: str, dt: str, idx: int, key_tokens: list) -> bool:
    """key側トークンkt(idx番目)が、display側トークンdtからの許可された1対1置換か。"""
    kl, dl = kt.lower(), dt.lower()
    if kl == dl:
        return True
    import er003_key_words_canonicalization as kc   # 閉じた人称表を再利用(再実装しない)
    if kl in (kc._PERSON_DEPENDENT_TO_GENERIC.get(dl) or ()):
        return True
    verb_pos = idx == 0 or key_tokens[idx - 1].lower() == "to"
    if verb_pos:
        if dl in _FUNCTION_VERB_FORMS and kl == _FUNCTION_VERB_FORMS[dl]:
            return True
        if dl in _PAST_ONLY_IRREGULAR and kl == _PAST_ONLY_IRREGULAR[dl]:
            return True
        if dl in _AMBIGUOUS_IRREGULAR and kl == _AMBIGUOUS_IRREGULAR[dl] and _guard_ok(key_tokens, idx):
            return True
        if (dl not in _IRREGULAR_PLURAL and dl not in _PARTICIPIAL_ADJ_EXCLUDE and dl not in _PLURAL_EXCLUDE
                and kl in _verb_base_candidates(dl) and len(key_tokens) >= 2 and _guard_ok(key_tokens, idx)):
            return True
        if _adverb_follow_ok(kl, dl, idx, key_tokens):    # 委任_03 区分1(1): 副詞前の原形化(既存条件で不受理のときだけ追加判定=単調)
            return True
    if idx == len(key_tokens) - 1 and dl not in _PLURAL_EXCLUDE and kl in _plural_base_candidates(dl):
        return True
    return False


# ============================================================
# KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_03(2026-10-26、区分1=承認済み規則への準拠修正のProduction適用。fulltext経路限定)
# 正本: docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/DESIGN_02.md §3-1、OPUS_REVIEW_02.md Q1(b)/Q2(b)/M1/M2/R3、PROD_APPLY_01.md。
# 移植元: er123_kp_rescue_dev_01.py(DEV。判定をDEV/Prodで完全一致させるためデータ表・関数本体を逐語移植。parity=parity_01.json)。
# 適用範囲(3点のみ): (1)副詞前の原形化(承認文「先頭またはto直後の動詞」へ戻すguard是正。-ly名詞/動詞除外表+語幹CMU実在+前方活用一致+句末/前置詞等の前)
#   (2)有限助動詞have/has/hadの役割判定(`contains_finite_aux_role_based`。fulltext経路の_legacy_form_reasons・canonicalizationのallow_inflection_normalization=True時のみ)
#   (3)過去形表の補完(他動詞原形と同形のbound/lay/wound/ground/boreは追加しない)。
# 非適用(区分2): 量化詞限定詞guard・慣用句の閉表・辞書裏付けguard・救済フロー・A1短縮・再アンカー・A2・縮約形是正。A/B/C経路(allow_inflection_normalization=False)は不変。
# ============================================================
# lemma: (過去形, 過去分詞)。標準的な不規則動詞(be/have/doは_FUNCTION_VERB_FORMSで別管理)。
IRR = {
    "arise": ("arose", "arisen"), "awake": ("awoke", "awoken"), "bear": ("bore", "borne"), "beat": ("beat", "beaten"),
    "become": ("became", "become"), "begin": ("began", "begun"), "bend": ("bent", "bent"), "bind": ("bound", "bound"),
    "bite": ("bit", "bitten"), "bleed": ("bled", "bled"), "blow": ("blew", "blown"), "break": ("broke", "broken"),
    "breed": ("bred", "bred"), "bring": ("brought", "brought"), "build": ("built", "built"), "buy": ("bought", "bought"),
    "catch": ("caught", "caught"), "choose": ("chose", "chosen"), "cling": ("clung", "clung"), "come": ("came", "come"),
    "creep": ("crept", "crept"), "deal": ("dealt", "dealt"), "dig": ("dug", "dug"), "draw": ("drew", "drawn"),
    "drink": ("drank", "drunk"), "drive": ("drove", "driven"), "eat": ("ate", "eaten"), "fall": ("fell", "fallen"),
    "feed": ("fed", "fed"), "feel": ("felt", "felt"), "fight": ("fought", "fought"), "find": ("found", "found"),
    "flee": ("fled", "fled"), "fling": ("flung", "flung"), "fly": ("flew", "flown"), "forbid": ("forbade", "forbidden"),
    "forget": ("forgot", "forgotten"), "forgive": ("forgave", "forgiven"), "freeze": ("froze", "frozen"),
    "get": ("got", "gotten"), "give": ("gave", "given"), "go": ("went", "gone"), "grind": ("ground", "ground"),
    "grow": ("grew", "grown"), "hang": ("hung", "hung"), "hear": ("heard", "heard"), "hide": ("hid", "hidden"),
    "hold": ("held", "held"), "keep": ("kept", "kept"), "kneel": ("knelt", "knelt"), "know": ("knew", "known"),
    "lay": ("laid", "laid"), "lead": ("led", "led"), "leave": ("left", "left"), "lend": ("lent", "lent"),
    "lie": ("lay", "lain"), "light": ("lit", "lit"), "lose": ("lost", "lost"), "make": ("made", "made"),
    "mean": ("meant", "meant"), "meet": ("met", "met"), "overcome": ("overcame", "overcome"), "pay": ("paid", "paid"),
    "ride": ("rode", "ridden"), "ring": ("rang", "rung"), "rise": ("rose", "risen"), "run": ("ran", "run"),
    "say": ("said", "said"), "see": ("saw", "seen"), "seek": ("sought", "sought"), "sell": ("sold", "sold"),
    "send": ("sent", "sent"), "shake": ("shook", "shaken"), "shine": ("shone", "shone"), "shoot": ("shot", "shot"),
    "show": ("showed", "shown"), "shrink": ("shrank", "shrunk"), "sing": ("sang", "sung"), "sink": ("sank", "sunk"),
    "sit": ("sat", "sat"), "sleep": ("slept", "slept"), "slide": ("slid", "slid"), "speak": ("spoke", "spoken"),
    "spend": ("spent", "spent"), "spin": ("spun", "spun"), "spring": ("sprang", "sprung"), "stand": ("stood", "stood"),
    "steal": ("stole", "stolen"), "stick": ("stuck", "stuck"), "sting": ("stung", "stung"), "strike": ("struck", "struck"),
    "swear": ("swore", "sworn"), "sweep": ("swept", "swept"), "swim": ("swam", "swum"), "swing": ("swung", "swung"),
    "take": ("took", "taken"), "teach": ("taught", "taught"), "tear": ("tore", "torn"), "tell": ("told", "told"),
    "think": ("thought", "thought"), "throw": ("threw", "thrown"), "understand": ("understood", "understood"),
    "undertake": ("undertook", "undertaken"), "wake": ("woke", "woken"), "wear": ("wore", "worn"), "weave": ("wove", "woven"),
    "weep": ("wept", "wept"), "win": ("won", "won"), "wind": ("wound", "wound"), "withdraw": ("withdrew", "withdrawn"),
    "write": ("wrote", "written"),
}
# 過去形が名詞・形容詞・別語としても通用する語(過去形専用表には入れず、直後条件つきのAMBIGUOUS表へ)
# OPEN-476=DEFERRED(er105 is_valid_inflection_normalization docstring: bound to->bind to は拒否のまま)。補完の対象から除外する。
# R3(Opus): 他の動詞の原形/名詞と同形になる新規追加語は補完しない(bound/lay/wound/ground/bore。`bound`を外したのと同じ理由)。
COMPLETION_EXCLUDE = frozenset({"bound", "lay", "wound", "ground", "bore"})
PAST_ALSO_OTHER_WORD = frozenset({
    "saw", "left", "found", "bound", "wound", "lay", "bore", "rose", "felt", "spoke", "stole", "bit", "shot", "won",
    "stuck", "struck", "hung", "bent", "spent", "ground", "lit", "fell", "led", "sat", "bled", "fed", "laid", "dug", "lent",
})
# M2(Opus): 形が変わらない/不規則な過去分詞で表に無かった語(has spread/quit/cast/cost/burst/shed/split/upset/bet/forecast/broadcast/bid/fit/rid/wed、
#   dwelt/leapt/wrung/strode/stunk ほか)。2語の句は nxt2=None になり倒置ルールにも掛からないため、nxt自身を分詞として認識する。迷えばaux側。
IRR_PARTICIPLES_EXTRA = frozenset({
    "spread", "quit", "cast", "cost", "burst", "shed", "split", "upset", "bet", "forecast", "broadcast", "bid", "fit", "rid", "wed",
    "dwelt", "leapt", "wrung", "strode", "stunk", "bust", "slit", "thrust", "sublet", "typeset", "offset", "reset", "outbid", "overcast",
    "recast", "underbid", "unwound", "spat", "slung", "slunk", "snuck", "strung", "leant", "dived", "dove", "spoilt", "wound", "ground",
    "bore", "laid", "lain", "bled", "fled", "sped", "stove", "clad", "shod", "woven", "hewn", "mown", "rent", "bereft", "dealt", "meant",
    "overrun", "outrun", "overthrown", "withstood", "forborne", "foregone", "foresaw", "foreseen", "overseen", "outdone", "overtaken",
    "retaken", "remade", "regrown", "reborn", "reheard", "rebound", "unbound", "unbent", "underlain", "underwritten", "unfrozen"})
IRR_PARTICIPLES = frozenset(p for _, p in IRR.values()) | IRR_PARTICIPLES_EXTRA | frozenset({
    "got", "been", "done", "had", "put", "cut", "set", "let", "hit", "hurt", "read", "shut",
    # IRRマスタ外の過去分詞(完了形のauxを語彙haveと誤認しないための追加。迷えばaux側=現行どおり拒否)
    "proven", "learnt", "burnt", "dreamt", "spelt", "spilt", "smelt", "sped", "knit", "forsaken", "mistaken", "overtaken", "undergone",
    "outgrown", "slain", "striven", "trodden", "sewn", "sown", "shorn", "swollen", "stricken", "begotten", "beheld", "upheld", "withheld",
    "misled", "overdone", "undone", "redone", "rebuilt", "retold", "rewritten", "bidden", "wrought", "come", "become", "run", "gone"})

_VOWELS = "aeiou"


def _cvc(w: str) -> bool:
    return len(w) >= 3 and w[-1] not in _VOWELS + "wxy" and w[-2] in _VOWELS and w[-3] not in _VOWELS


def _doubling_options(l: str) -> tuple:
    """CVC語の重子音化: (重子音形を許す?, 非重子音形を許す?)。単音節/語末強勢→重子音(hop->hopped, plan->planned, prefer->preferred)、
    語末が無強勢→非重子音(visit->visited, open->opened)。CMUに無ければ両方許す。hoped->hop のような誤受理を前方生成一致で拒否するための判定。"""
    try:
        import pronouncing
        prons = pronouncing.phones_for_word(l)
    except Exception:   # noqa: BLE001
        prons = []
    if not prons:
        return True, True
    dbl = plain = False
    for pr in prons:
        vs = [x for x in pr.split() if x[-1].isdigit()]
        if not vs:
            continue
        if len(vs) == 1 or vs[-1].endswith("1"):
            dbl = True
        else:
            plain = True
    return (dbl or not plain), (plain or not dbl)


def regular_forms(lemma: str) -> set:
    """規則活用の前方生成(-s/-es/-ies, -ed/-d/-ied, -ing)。CVC語は重子音あり/なし両方(強勢未判定のため緩め=受理側の誤り防止ではなく『一致確認』用)。"""
    l = lemma.lower()
    out = set()
    # 3sg
    if re.search(r"(s|x|z|ch|sh|o)$", l):
        out.add(l + "es")
    elif re.search(r"[^aeiou]y$", l):
        out.add(l[:-1] + "ies")
    else:
        out.add(l + "s")
    # past / participle
    if l.endswith("e"):
        out.add(l + "d")
    elif re.search(r"[^aeiou]y$", l):
        out.add(l[:-1] + "ied")
    elif _cvc(l):
        dbl, plain = _doubling_options(l)
        if dbl:
            out.add(l + l[-1] + "ed")
        if plain:
            out.add(l + "ed")
    else:
        out.add(l + "ed")
    # gerund
    if l.endswith("ie"):
        out.add(l[:-2] + "ying")
    elif l.endswith("e") and not l.endswith(("ee", "ye", "oe")):
        out.add(l[:-1] + "ing")
    elif _cvc(l):
        dbl, plain = _doubling_options(l)
        if dbl:
            out.add(l + l[-1] + "ing")
        if plain:
            out.add(l + "ing")
    else:
        out.add(l + "ing")
    return out


def forms(lemma: str) -> set:
    """lemmaの活用形全体(前方生成)。不規則動詞は過去形・過去分詞をIRRから、3sg/gerundは規則形。"""
    l = lemma.lower()
    rf = regular_forms(l)
    if l in IRR:
        past, pp = IRR[l]
        rf = {f for f in rf if not f.endswith(("ed", "ied"))} | {past, pp}
    if l in ("be", "have", "do"):
        rf |= {"be": {"is", "are", "was", "were", "been", "being", "am"}, "have": {"has", "had", "having"},
               "do": {"does", "did", "done", "doing"}}[l]
    return rf


def inflects_to(lemma: str, surface: str) -> bool:
    """前方生成一致: surfaceがlemmaの活用形か(`hoped`->`hop`は偽、`hoped`->`hope`は真)。"""
    return surface.lower() in forms(lemma)




def _kc():
    import er003_key_words_canonicalization as kc   # 遅延import(循環回避)
    return kc


def _cmu_reasons(word: str) -> list:
    import er108_kp_cmu_lexicon_gate_01 as cmu   # 遅延import(Production既存の同一CMU辞書)
    return cmu.reasons_for_phrase(word)


_HAVE = frozenset({"has", "have", "had"})
_NOM_PRONOUN = frozenset({"i", "you", "he", "she", "it", "we", "they", "there", "who"})   # have + 主格代名詞=倒置の助動詞(You/Itは保守的にaux側)
_AUX_FOLLOW = frozenset({"been", "being", "to", "not", "t", "n't", "never", "already", "just", "ever", "better", "rather", "best", "got"})


_NOT_PARTICIPLE_ED = frozenset({"hundred", "kindred", "sacred", "naked", "wicked", "rugged", "crooked", "beloved", "wretched", "hatred", "infrared"})   # -edで終わるが分詞でない語


def _is_participle(w: str) -> bool:
    return w in IRR_PARTICIPLES or (w.endswith("ed") and len(w) > 3 and w not in _PARTICIPIAL_ADJ_EXCLUDE and w not in _NOT_PARTICIPLE_ED)


_HAVE_ADV = frozenset({"also", "often", "only", "finally", "just", "already", "ever", "never", "always", "still", "quite", "really", "soon",
                       "recently", "previously", "yet", "long", "so"})
_LEXICAL_START = frozenset(set(_GUARD_DET) | {"no", "each", "every", "all", "both", "another", "either", "neither", "several", "few", "many",
                                                 "much", "more", "less", "enough", "what", "something", "nothing", "anything", "everything"})


# M2(Opus): 助動詞と分詞の間に入りうる量化詞・副詞(have all gone / have both agreed / has more than doubled / have just been)。
_HAVE_SKIP = frozenset({"all", "both", "each", "either", "neither", "more", "less", "than", "much", "many", "few", "several", "most", "half",
                        "just", "already", "also", "never", "ever", "only", "still", "always", "often", "finally", "recently", "previously",
                        "yet", "really", "quite", "so", "long", "now", "then", "once", "twice", "nearly", "almost", "barely", "hardly", "all"})
_HAVE_DET_SET = frozenset(_GUARD_DET) | {"the", "a", "an"}


def have_role(toks: list, i: int, capitalized_first: bool = False) -> str:
    """have/has/had(toks[i])が『aux』(完了・倒置・慣用の助動詞用法)か『lexical』(所有・経験・実行の語彙動詞)か。
    保守的: 判定に迷えばaux(=現行どおり拒否)。lexicalと判定するのは、直後が限定詞/所有格/数量詞/名詞句の始まりで、かつ
    (1)文頭の大文字Have/Has/Had(倒置・疑問)でない (2)直後に副詞+過去分詞が続かない (3)『have+主語+been/過去分詞』の倒置でない
    (4)[M2] 量化詞/副詞を挟んだ『have all gone』『has more than doubled』でない (5)[M2] 形が変わらない過去分詞(has spread/quit/cast/cost…)でない
    (6)[M2] 限定詞(+形容詞)+名詞+過去分詞(had the board known / had the house painted は形が同じで区別不能→aux)でない 場合のみ。"""
    nxt = toks[i + 1] if i + 1 < len(toks) else None
    nxt2 = toks[i + 2] if i + 2 < len(toks) else None
    if capitalized_first and i == 0 and nxt is not None:
        return "aux"
    if nxt is None:
        return "aux"
    if nxt in _AUX_FOLLOW or nxt in _NOM_PRONOUN or nxt in _HAVE_ADV:
        return "aux"
    if _is_participle(nxt):
        return "aux"
    if nxt in _PARTICIPIAL_ADJ_EXCLUDE:
        # 形容詞化もしうる分詞(limited/interested/expected等): 直後が限定詞/前置詞(=目的語を取る完了形)・句末ならaux、名詞が続くときだけ形容詞=語彙have
        if nxt2 is None or nxt2 in _GUARD_DET or nxt2 in _GUARD_PARTICLE:
            return "aux"
        return "lexical"
    # (4) 量化詞/副詞を読み飛ばして、その先が分詞/been/beingならaux(have all gone / has more than doubled)
    j = i + 1
    skipped = False
    while j < len(toks) and toks[j] in _HAVE_SKIP:
        j += 1
        skipped = True
    if skipped and j < len(toks):
        w = toks[j]
        if w in ("been", "being") or _is_participle(w) or w in _PARTICIPIAL_ADJ_EXCLUDE or (w.endswith("ed") and len(w) > 3):
            return "aux"
    if skipped and j >= len(toks) and toks[-1] in _HAVE_SKIP and toks[-1] not in ("all", "both", "each", "either", "neither", "most", "half",
                                                                                     "many", "few", "several", "much", "more", "less", "than"):
        return "aux"      # have just / have already 等の副詞止まり(分詞が切れている)
    # (6) 限定詞(+形容詞)+名詞+過去分詞: had the board known / had the house painted → aux(倒置/使役の区別不能)
    if nxt in _HAVE_DET_SET:
        for k in (i + 3, i + 4):
            if k < len(toks) and (toks[k] in ("been", "being") or _is_participle(toks[k])):
                return "aux"
    if nxt not in _LEXICAL_START and nxt2 is not None and (nxt2 in ("been", "being") or _is_participle(nxt2)):
        return "aux"       # have + 主語(名詞) + been/過去分詞 = 倒置の助動詞(Had users been / Has Vera been)
    return "lexical"


def finite_aux_roles(text: str) -> list:
    orig = _kc()._WORD_TOKEN_RE.findall(text or "")
    toks = [t.lower() for t in orig]
    out = []
    for i, t in enumerate(toks):
        if t in _kc()._FINITE_AUX_WORDS:
            out.append((t, have_role(toks, i, capitalized_first=orig[i][:1].isupper()) if t in _HAVE else "aux"))
    return out


def contains_finite_aux_role_based(text: str) -> bool:
    return any(role == "aux" for _, role in finite_aux_roles(text))


LY_ADJ = frozenset({"friendly", "lovely", "lonely", "elderly", "costly", "likely", "unlikely", "silly", "early", "daily", "weekly", "monthly",
                    "yearly", "only", "family", "holy", "ugly", "lively", "deadly", "orderly", "lowly", "bubbly", "chilly", "curly",
                    # M1(c): -ly形容詞の追加(Opus指摘: timely/scholarly/cowardly/leisurely/manly/hourly/nightly/sickly/burly/unruly 他)
                    "timely", "scholarly", "cowardly", "leisurely", "manly", "womanly", "hourly", "nightly", "sickly", "burly", "unruly", "motherly",
                    "fatherly", "brotherly", "sisterly", "heavenly", "earthly", "ghostly", "kingly", "queenly", "masterly", "saintly", "worldly",
                    "homely", "kindly", "lordly", "neighborly", "neighbourly", "princely", "slovenly", "surly", "wily", "stately", "sprightly",
                    "gentlemanly", "ladylike", "cleanly", "comely", "courtly", "fortnightly", "quarterly", "northerly", "southerly", "easterly",
                    "westerly", "wobbly", "gnarly", "scraggly", "squiggly", "wriggly", "crumbly", "prickly", "bristly", "knobbly", "lumpy"})
# M1(a): -ly で終わる名詞/動詞(副詞ではない)の除外表。語幹検査をすり抜ける語(supply→supple, reply→rep)も明示的に除く。
LY_NOUN_VERB = frozenset({"supply", "reply", "rally", "assembly", "jelly", "belly", "bully", "folly", "monopoly", "anomaly", "tally", "ally",
                          "apply", "comply", "imply", "multiply", "rely", "fly", "ply", "july", "italy", "lily", "dolly", "holly", "molly", "polly",
                          "sally", "wally", "dally", "bully", "melancholy", "homily", "casualty", "butterfly", "firefly", "dragonfly", "gadfly",
                          "underlay", "overlay", "doily", "dilly", "filly", "hillbilly", "billy", "willy", "silly", "chilly", "cobbly", "gully", "bally",
                          "ghastly", "grisly", "grizzly", "bubbly", "dumbly", "unfriendly", "overly", "reapply", "resupply", "outfly", "nelly", "sully"})
_MANNER_ADV_EXTRA = frozenset({"again", "alone", "hard", "fast", "often", "always", "never"})    # well/stillは名詞用法(a well/a still)があるため除外(M1)


def _ly_stems(w: str) -> set:
    """-ly副詞の語幹候補(綴り規則: -ily→-y happily→happy / -ally→-ic basically→basic / -bly,-ply,-tly等→-ble,-ple,-tle simply→simple /
    -ully,-lly→-l fully→full / -uly→-ue truly→true / それ以外は-ly除去 quietly→quiet)。"""
    st = set()
    base = w[:-2]
    st.add(base)
    if w.endswith("ily"):
        st.add(w[:-3] + "y")
    if w.endswith("ally"):
        st.add(w[:-4])      # basically -> basic
    if re.search(r"[bpdgktz]ly$", w):
        st.add(w[:-1] + "e")
    if w.endswith("lly"):
        st.add(w[:-1])
    if w.endswith("uly"):
        st.add(w[:-2] + "e")
    if w.endswith("ably") or w.endswith("ibly"):
        st.add(w[:-1] + "e")
    return {x for x in st if len(x) >= 3}


def is_manner_adverb(w: str) -> bool:
    """[M1] -ly副詞か。-ly名詞/動詞/形容詞の除外表に無く、かつ語幹(綴り規則で復元)がCMU実在の語であること。
    (CMU実在だけでは rep(reply)/supple(supply)のように語幹検査をすり抜けるため、除外表と併用する。)"""
    w = w.lower()
    if w in _MANNER_ADV_EXTRA:
        return True
    if not (w.endswith("ly") and len(w) > 4) or w in LY_ADJ or w in LY_NOUN_VERB:
        return False
    return any(not _cmu_reasons(x) for x in _ly_stems(w))


def _adverb_tail_ok(key_tokens: list, adv_idx: int) -> bool:
    """副詞が句末、または直後が前置詞/不変化詞/限定詞/等位接続詞(= 副詞が動詞を修飾していて、後続名詞を修飾する形容詞化分詞ではない)。"""
    if adv_idx >= len(key_tokens) - 1:
        return True
    f = key_tokens[adv_idx + 1].lower()
    return f in _GUARD_PARTICLE or f in _GUARD_DET or f in ("and", "or", "but")



def _adverb_follow_ok(kl: str, dl: str, idx: int, key_tokens: list) -> bool:
    """[区分1(1)] 副詞前の原形化(承認文『先頭またはto直後の動詞』の目的に沿う是正)。DEV `RulePatch(adverb=True)`のpair_okと同一判定。
    P-04の目的(heated debate型=V+名詞を原形化しない)は、(a)形容詞化分詞表 (b)-ly名詞/動詞/形容詞の除外表+語幹CMU実在 (c)副詞が句末/前置詞等の直前 (d)前方活用一致 で維持する。"""
    if not (len(key_tokens) >= 2 and idx + 1 < len(key_tokens)):
        return False
    if dl in _IRREGULAR_PLURAL or dl in _PARTICIPIAL_ADJ_EXCLUDE or dl in _PLURAL_EXCLUDE:
        return False
    lemma_ok = ((dl in _AMBIGUOUS_IRREGULAR and kl == _AMBIGUOUS_IRREGULAR[dl])
                or (kl in _verb_base_candidates(dl) and inflects_to(kl, dl)))
    if not lemma_ok:
        return False
    nxt = key_tokens[idx + 1].lower()
    return is_manner_adverb(nxt) and _adverb_tail_ok(key_tokens, idx + 1)


def _complete_past_tables() -> None:
    """[区分1(3)] 過去形専用表/曖昧表の補完(import時に1回、冪等)。他動詞原形と同形の語(R3: bound/lay/wound/ground/bore等)は追加しない。"""
    for lemma, (past, pp) in IRR.items():
        if past in COMPLETION_EXCLUDE or pp in COMPLETION_EXCLUDE:
            continue
        if (past in IRR and past != lemma) or (pp in IRR and pp != lemma):
            continue
        if past != lemma and past not in _PAST_ONLY_IRREGULAR and past not in _AMBIGUOUS_IRREGULAR                 and past not in _FUNCTION_VERB_FORMS:
            (_AMBIGUOUS_IRREGULAR if past in PAST_ALSO_OTHER_WORD else _PAST_ONLY_IRREGULAR)[past] = lemma
        if pp not in (past, lemma) and pp not in _AMBIGUOUS_IRREGULAR and pp not in _PAST_ONLY_IRREGULAR:
            _AMBIGUOUS_IRREGULAR[pp] = lemma


_complete_past_tables()



# ============================================================
# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20 (2026-10-24, APPROVED_FOR_PRODUCTION: UDR #169[A-1]・#173[課題②])
# 課題② 見出し語の所有格一般化(possessor_roles + role条件付き受理 + revertのみの決定論後処理) + A-1(参照語の不定化)の統合。
# 設計正本: docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/WIRING_DESIGN_05.md
# 窓特定は本関数群に一本化する(validator[kc経由]と後処理が同じ`find_inflection_window`を使う。二重実装を作らない)。
# 共有許可表kc._PERSON_DEPENDENT_TO_GENERIC・A/B/Cの受理範囲は不変(role_ok_possは既定空=従来とバイト同一)。
# ============================================================
# A-1: 参照語の不定化の置換条件(this/that->a/an、目的格him/me/us/her->someone)
_DEM_FOLLOW_BLOCK = frozenset({
    "much", "many", "is", "was", "are", "were", "said", "will", "would", "can", "could", "has", "had", "does", "did", "off", "up", "out", "over",
    "down", "in", "on", "at", "to", "for", "with", "by", "from", "and", "or", "but", "if", "as", "than", "so", "time", "point", "case", "way", "day",
    "moment", "reason", "night", "morning", "long", "far", "big", "little", "one", "kind", "sort", "of",
    # 接続詞のthat(直後に主語・限定詞が来る): so that nobody noticed / said that the team won
    "nobody", "everyone", "everybody", "someone", "somebody", "anyone", "anybody", "he", "she", "they", "it", "we", "i", "you", "there",
    "the", "a", "an", "his", "her", "their", "our", "my", "your", "its", "people", "this", "that", "these", "those",
})
_UNCOUNTABLE = frozenset({
    "advice", "information", "news", "equipment", "furniture", "luggage", "baggage", "money", "music", "traffic", "weather", "progress", "research",
    "knowledge", "evidence", "help", "behavior", "behaviour", "attention", "trust", "work", "homework", "software", "feedback", "damage", "noise",
    "luck", "fun", "water", "air", "time", "energy", "love", "hope", "courage", "pressure", "silence", "sound",
})
# W-03(Opus条件C): 時間名詞・same/other/very等(this year / that same X)、直前語の除外(not that bad)、me系固定表現(between you and me / excuse me)
_TIME_NOUNS = frozenset({
    "year", "years", "week", "weeks", "weekend", "weekends", "month", "months", "evening", "afternoon", "season", "decade", "century", "minute",
    "hour", "second", "today", "tonight", "summer", "winter", "spring", "autumn", "fall", "semester", "quarter", "morning", "moment", "time",
})
_DEM_NEXT_BLOCK2 = frozenset({"same", "other", "very", "exact", "whole", "only", "first", "last", "next", "previous"})
_DEM_PREV_BLOCK = frozenset({"not", "all", "quite", "just", "only", "like", "at", "with", "than", "that", "so"})
_REF_OBJ_PREV_BLOCK = frozenset({"between", "excuse", "beats", "beat", "trust", "lucky", "poor", "pardon", "bless", "dear", "believe", "and", "or", "than",
                                 "like", "as", "except", "but", "me", "us"})
_OBJ_HER_FOLLOW = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "some", "any", "my", "your", "his", "our", "their", "to", "for", "with", "up", "down", "off", "out",
    "over", "away", "back", "in", "on", "at", "from", "into", "about", "around", "through", "by", "and", "or", "but", "so", "along", "aside", "apart",
})
POSSESSIVE_TOKENS = ("my", "your", "his", "her", "its", "their", "our")
GENERIC_POSSESSIVES = ("one's", "someone's", "somebody's")
POSSESSOR_ROLES = ("self", "other_person", "non_person", "none")
ROLE_OK_DISPLAY_TOKENS = ("my", "our")            # role=other_personのときだけ->someone's/somebody'sを受理するdisplay側の語
ROLE_OK_KEY_TOKENS = ("someone's", "somebody's")
REASON_REFERENCE_WORD = "generalize_reference_word"


def _first_phone_classes(word: str):
    """語頭音の分類集合(CMU辞書`pronouncing`=cmudict 1.1.3、er108と同一)。{"vowel"}/{"consonant"}/両方。辞書に無い語・辞書例外は空集合(=判定不能)。
    W-02(Opus条件C): 簡易綴り規則へのフォールバックは行わない(M2のcmu_post_canonがKP全語のCMU登録を要求するため本番では効かず安全でもない)。"""
    w = (word or "").lower().strip("'")
    if not w:
        return set()
    try:
        import pronouncing
        prons = pronouncing.phones_for_word(w)
    except Exception:   # noqa: BLE001  辞書が使えない=判定不能(例外は送出せず安全側=不許可)
        return set()
    out = set()
    for pr in prons or []:
        ph = pr.split()
        if not ph:
            return set()
        out.add("vowel" if any(ch.isdigit() for ch in ph[0]) else "consonant")
    return out


def starts_with_vowel_sound(word: str) -> bool:
    """全ての発音が母音始まりのときのみTrue(保守的)。辞書に無い語・例外・複数発音で母音/子音が混在する語はFalse。"""
    return _first_phone_classes(word) == {"vowel"}


def starts_with_consonant_sound(word: str) -> bool:
    """全ての発音が子音始まりのときのみTrue(保守的)。判定不能・混在はFalse。"""
    return _first_phone_classes(word) == {"consonant"}


def _looks_plural(w: str) -> bool:
    return len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is"))


def reference_pair_ok(kt: str, dt: str, idx: int, key_tokens: list, window: list, prev_d=None) -> bool:
    """A-1: 参照語の1対1置換が許されるか。指示語this/that->a/an(単数可算名詞の限定詞のときのみ。theは許可しない)、
    目的格him/me/us->someone/somebody、her->someone/somebody(直後語が_OBJ_HER_FOLLOWのときのみ=所有格herと区別)。
    prev_d: windowの直前のdisplay語(窓の外。idx>0なら窓内のwindow[idx-1]を使う)。W-03で追加した除外はいずれも受理範囲を狭めるだけ。"""
    kl, dl = kt.lower(), dt.lower()
    nxt_d = window[idx + 1].lower() if idx + 1 < len(window) else None
    prev = window[idx - 1].lower() if idx > 0 else (prev_d.lower() if prev_d else None)
    if dl in ("that", "this"):
        if kl not in ("a", "an"):
            return False
        if nxt_d is None or nxt_d in _DEM_FOLLOW_BLOCK or nxt_d in _UNCOUNTABLE or _looks_plural(nxt_d):
            return False
        if nxt_d in _TIME_NOUNS or nxt_d in _DEM_NEXT_BLOCK2:
            return False
        if prev is not None and (prev in _DEM_PREV_BLOCK or prev.endswith("n't")):
            return False
        # 不可算名詞は直後語だけでなくthat以降のいずれの語でも却下(take that good advice)。時間名詞もthat以降のいずれでは却下しない(直後のみ)
        if any(w.lower() in _UNCOUNTABLE for w in window[idx + 1:]):
            return False
        nxt_k = key_tokens[idx + 1].lower() if idx + 1 < len(key_tokens) else None
        if nxt_k is None:
            return False
        if kl == "a" and not starts_with_consonant_sound(nxt_k):
            return False
        if kl == "an" and not starts_with_vowel_sound(nxt_k):
            return False
        return True
    if dl in ("him", "me", "us"):
        if prev is not None and prev in _REF_OBJ_PREV_BLOCK:
            return False
        return kl in ("someone", "somebody")
    if dl == "her":
        if prev is not None and prev in _REF_OBJ_PREV_BLOCK:
            return False
        return kl in ("someone", "somebody") and (nxt_d is None or nxt_d in _OBJ_HER_FOLLOW)
    return False


def _norm_tokens(s: str) -> list:
    return _TOKEN_RE.findall(unicodedata.normalize("NFKC", s or "").replace("’", "'"))


def find_inflection_window(key_phrase: str, display_phrase: str, role_ok_poss=frozenset()):
    """key_phraseがdisplay_phrase内の連続トークン範囲の1対1置換(活用形->基本形・人称一般化[共有表]・A-1参照語・role条件付きmy/our->someone's)で
    得られるとき、その開始token indexを返す(最初に見つかった窓、変化トークン1つ以上)。無ければNone。
    role_ok_poss: displayのtoken index(絶対index)の集合。そのindexのmy/ourに限り->someone's/somebody'sを受理する(既定空=従来と同一)。"""
    k, d = _norm_tokens(key_phrase), _norm_tokens(display_phrase)
    if not k or len(k) > len(d):
        return None
    ok_idx = frozenset(role_ok_poss or ())
    for start in range(0, len(d) - len(k) + 1):
        window = d[start:start + len(k)]
        if all(_token_pair_ok(kt, dt, i, k) or reference_pair_ok(kt, dt, i, k, window, d[start - 1] if start > 0 else None)
               or ((start + i) in ok_idx and dt.lower() in ROLE_OK_DISPLAY_TOKENS and kt.lower() in ROLE_OK_KEY_TOKENS)
               for i, (kt, dt) in enumerate(zip(k, window))) \
                and any(kt.lower() != dt.lower() for kt, dt in zip(k, window)):
            return start
    return None


def is_valid_inflection_normalization(key_phrase: str, display_phrase: str, role_ok_poss=frozenset()) -> bool:
    """key_phraseがdisplay_phrase内の**連続したトークン範囲**(語数=key_phraseの語数)の『活用形->基本形(動詞の原形・名詞の単数)』
    および/または人称一般化・参照語不定化(A-1)の1対1トークン置換だけで得られるか(語数不変・変化トークン1つ以上・語の追加/削除/並べ替えなし)。
    例: pushed prices up->push prices up / gave back some gains->give back / pumps its fist->pump one's fist / draw that line->draw a line。
    拒否: mixed feelings->mix feelings / heated debate->heat debate / news->new / goods->good / means->mean /
    raw beans->raw materials(別語) / bound to->bind to(OPEN-476=DEFERRED)。
    role_ok_poss: find_inflection_windowを参照(既定空=従来と同一の受理範囲)。"""
    return find_inflection_window(key_phrase, display_phrase, role_ok_poss) is not None


# ------------------------------------------------------------ 課題② 後処理(決定論・API 0・revertのみ)
def possessive_slots(display_phrase: str) -> list:
    """display内の所有格(POSSESSIVE_TOKENS)の位置。[(token_index, token_lower)]。"""
    return [(i, t.lower()) for i, t in enumerate(_norm_tokens(display_phrase)) if t.lower() in POSSESSIVE_TOKENS]


def validate_possessor_roles(roles, display_phrase: str) -> tuple:
    """(ok, reason)。要素数=display内の所有格数、tokenが出現順に一致、roleがenum内。"""
    slots = possessive_slots(display_phrase)
    if not isinstance(roles, list):
        return False, "roles_not_list"
    if len(roles) != len(slots):
        return False, f"count_mismatch(expected={len(slots)},got={len(roles)})"
    for n, (r, (_, tok)) in enumerate(zip(roles, slots)):
        if not isinstance(r, dict) or str(r.get("token", "")).strip().lower() != tok:
            return False, f"token_mismatch@{n}(expected={tok},got={r.get('token') if isinstance(r, dict) else r})"
        if r.get("role") not in POSSESSOR_ROLES:
            return False, f"role_not_in_enum@{n}({r.get('role')})"
    return True, ""


def _allowed_generic_for_role(role: str) -> frozenset:
    """role -> 置換してよい一般形。置換しない(displayの語のまま)ことはどのroleでも常に許可。"""
    if role == "self":
        return frozenset({"one's"})
    if role == "other_person":
        return frozenset({"someone's", "somebody's"})
    return frozenset()   # non_person / none: 一般形は不可(displayの語へrevert)


def _replace_token_in_key(key: str, idx: int, new: str) -> str:
    """key文字列のidx番目のtokenをnewへ置換(周囲の文字列は保持。先頭大文字は引き継ぐ)。"""
    s = unicodedata.normalize("NFKC", key or "").replace("’", "'")
    for n, m in enumerate(_TOKEN_RE.finditer(s)):
        if n == idx:
            old = m.group(0)
            repl = (new[:1].upper() + new[1:]) if old[:1].isupper() else new
            return s[:m.start()] + repl + s[m.end():]
    return key


# 不定人称語(gloss側`_GENERIC_TOKENS`相当。A-1の`him->someone`を含む)
_PERSON_SUB_TOKENS = frozenset({"one's", "someone's", "somebody's", "one", "someone", "somebody", "oneself"})


def _recompute_item_fields(item: dict, display: str, new_key: str, role_ok: frozenset) -> None:
    """revert後のchanged_from_display_phrase / normalization_reasonを決定論で再計算する。
    LLMのreasonが新keyで整合するなら変更しない(A-1の`generalize_reference_word`記録を消さない)。"""
    import er003_key_words_canonicalization as kc
    kn, dn = _norm_tokens(new_key), _norm_tokens(display)
    same = [t.lower() for t in kn] == [t.lower() for t in dn]
    item["changed_from_display_phrase"] = not same
    if same:
        item["normalization_reason"] = "none"
        if item.get("qa_traceable_contiguous_span") == "FAIL":
            item["qa_traceable_contiguous_span"] = "PASS"   # QA定義(a): key_phraseがdisplay_phraseと完全一致
        return
    start = find_inflection_window(new_key, display, role_ok)
    dwin = dn[start:start + len(kn)] if start is not None else []
    person_sub = any(k.lower() in _PERSON_SUB_TOKENS and k.lower() != d.lower() for k, d in zip(kn, dwin))
    reason = item.get("normalization_reason")
    if reason == "generalize_person_dependent_reference" and not person_sub:
        if kc._is_valid_fulltext_normalization(new_key, display, "lemma_normalization", role_ok_poss=role_ok):
            item["normalization_reason"] = "lemma_normalization"
    elif reason == "lemma_normalization" and person_sub:
        item["normalization_reason"] = "generalize_person_dependent_reference"


def postprocess_possessor_roles(parsed: dict, original_items: list) -> dict:
    """canonicalization応答(parsed)に対する決定論後処理(fulltext専用。run_canonicalization_gateのpostprocess hookから呼ばれる)。API 0。

    各itemについて、possessor_roles(出現順の所有格ごとのrole)を検証し、keyの一般形(one's/someone's/somebody's)がroleと食い違う場合に
    **displayの語へ戻す(revertのみ)**。role modeでの書換え(one's<->someone's)・表外への置換はしない(WRONGを作らない)。
    roles検証不能/窓なし/revert後にvalidatorを通らない場合はkey無変更(現行どおり=新しいINVALID/retry消費を作らない)。
    parsed itemへ`person_role_repair`={status, roles_ok, roles_reason, repairs[], key_before, role_ok_poss[]}を残す(validator・mergeが参照)。
    入力parsedは破壊しない(deepcopyを返す)。"""
    import copy
    import er003_key_words_canonicalization as kc
    out = copy.deepcopy(parsed)
    items = out.get("items") if isinstance(out, dict) else None
    if not isinstance(items, list):
        return out
    by_rank = {it.get("rank"): it for it in (original_items or []) if isinstance(it, dict)}
    span_by_rank = {it["rank"]: it.get("source_span", "") for it in kc.canonicalization_view_items(list(original_items or []))}
    for item in items:
        if not isinstance(item, dict):
            continue
        orig = by_rank.get(item.get("rank"))
        if orig is None:
            continue
        display = orig.get("display_phrase") or orig.get("canonical_english") or ""
        key = item.get("key_phrase") or ""
        roles = item.get("possessor_roles")
        rec = {"status": "NO_POSSESSIVE", "roles_ok": None, "roles_reason": "", "repairs": [], "key_before": key, "role_ok_poss": []}
        item["person_role_repair"] = rec
        slots = possessive_slots(display)
        if not slots or not isinstance(key, str) or not key.strip():
            continue
        ok, why = validate_possessor_roles(roles, display)
        rec["roles_ok"], rec["roles_reason"] = ok, why
        if not ok:
            rec["status"] = "UNVERIFIED_ROLES"      # 迷えば触らない(現行どおり)。件数を記録して測る
            continue
        if [t.lower() for t in _norm_tokens(key)] == [t.lower() for t in _norm_tokens(display)]:
            rec["status"] = "NO_CHANGE"      # keyがdisplayと同一(置換していない)=常に許可
            continue
        # 窓特定: my/ourは全slotを許容して窓だけ特定し(受理の可否はrole照合後に決める)、食い違いはrevertで解消する。
        permissive = frozenset(i for i, t in slots if t in ROLE_OK_DISPLAY_TOKENS)
        start = find_inflection_window(key, display, permissive)
        if start is None:
            rec["status"] = "NO_WINDOW"
            continue
        kt = _norm_tokens(key)
        new_key = key
        repairs = []
        role_ok = set()
        for n, ((di, dtok), r) in enumerate(zip(slots, roles)):
            ki = di - start
            if ki < 0 or ki >= len(kt):
                continue            # 所有格が窓の外(keyに含まれない)
            cur = kt[ki].lower()
            if cur not in GENERIC_POSSESSIVES:
                continue            # 置換していない(displayの語のまま等)=常に許可
            if cur in _allowed_generic_for_role(r["role"]):
                if dtok in ROLE_OK_DISPLAY_TOKENS and r["role"] == "other_person" and cur in ROLE_OK_KEY_TOKENS:
                    role_ok.add(di)
                continue
            new_key = _replace_token_in_key(new_key, ki, dtok)    # revert(displayの語へ戻す)
            repairs.append({"ordinal": n, "display_token": dtok, "role": r["role"], "before": cur, "after": dtok,
                            "rule": "revert_%s" % r["role"]})
        rec["role_ok_poss"] = sorted(role_ok)
        if not repairs:
            rec["status"] = "NO_CHANGE"
            continue
        # revert後のkeyがvalidatorを通ることを確認できなければ、revertを中止してkey無変更(INVALID->retry消費を新たに作らない)。
        same_as_display = [t.lower() for t in _norm_tokens(new_key)] == [t.lower() for t in _norm_tokens(display)]
        valid = same_as_display or kc.validate_canonicalization_item(
            new_key, display, span_by_rank.get(item.get("rank"), ""), normalization_reason="lemma_normalization",
            original_span=orig.get("source_span"), allow_inflection_normalization=True, role_ok_poss=frozenset(role_ok))["ok"]
        rec["repairs"] = repairs
        if not valid:
            rec["status"] = "REVERT_SKIPPED"
            continue
        item["key_phrase"] = new_key
        rec["status"] = "REPAIRED"
        _recompute_item_fields(item, display, new_key, frozenset(role_ok))
        # revert後は全所有格slotがroleと整合する(上のループで食い違いを全てrevertした)ため、人称一般化QAをPASSにする。
        # 無条件のPASS上書きではなく、repairsがありvalidatorを通ったitemに限る。
        item["qa_person_reference_generalized"] = "PASS"
    return out


# ============================================================
# P-13(Fable決定、旧selection template:15 = CURRENT_SPEC:470-472「(2) 数値placeholder型の回避」の維持)
# Prompt 2は逐語固定で変更しない。選定後の決定論precheckで、数値・％・placeholder記号を含む、または数値を補わないと成立しない形
# のspanを拒否し、retry noteに理由を載せる(既存placeholder gate[音声化禁止記号検出]は現状維持)。
# ============================================================
_PLACEHOLDER_CHARS = "～〜~…"
_NUMBER_WORDS = frozenset({
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty", "thirty",
    "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million", "billion", "half",
    "quarter", "double", "triple",
})


def numeric_placeholder_reasons(phrase: str) -> list:
    """数値placeholder型の回避(CURRENT_SPEC:470-472)の決定論precheck。理由のlist(空=問題なし)。"""
    reasons = []
    p = phrase or ""
    if re.search(r"[0-9０-９]", p):
        reasons.append("数字を含む(数値placeholder型の回避: 数値を補わないと成立しない形/音声化で不安定になる形は選ばない)")
    if "%" in p or "％" in p:
        reasons.append("％記号を含む(数値placeholder型の回避)")
    if any(ch in p for ch in _PLACEHOLDER_CHARS) or "..." in p or "___" in p:
        reasons.append("placeholder記号(～,〜,…等)を含む")
    toks = [t.lower() for t in _TOKEN_RE.findall(p)]
    if ("percent" in toks or ("per" in toks and "cent" in toks)) and not any(t in _NUMBER_WORDS for t in toks):
        reasons.append("数値を補わないと成立しない形(percentのみで数値語が無い。数値placeholder型の回避)")
    return reasons
