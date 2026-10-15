# ============================================================
# er003_key_words_gloss_alignment.py
# KP-GLOSS-ALIGNMENT-01 (FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04, 2026-10-14)
# ============================================================
# 根本原因: 日本語gloss(japanese_gloss)は「選定段」(DB Hybrid / Strategy Lの選定LLM、
# 承認済みPromptの『選ぶ表現は本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付ける』)
# が**候補span/display_phraseに対して**生成する。一方、最終Key Phrase(key_phrase)は選定の後段
# canonicalization(別LLM呼出、入力にglossを含まない)が確定する。canonicalizationがKPを候補より
# 長く(補語・目的語を復元して)確定すると、glossは候補基準のまま残り、最終英語KPとglossが不整合になる
# (例: KP『based on interviews』/gloss『～をもとにした』/TTS『なになにをもとにした』)。
# 候補ID方式の案A'(原文窓の右拡張)でKPが候補より伸びる機会が増えたが、構造上の欠落は元々存在した
# (restore_semantic_complement等)。canonicalization→gloss再整合の工程が存在しないことが原因。
#
# 是正(Prompt/Rule7/Validator/Gate無変更): canonicalization確定後、最終KPが表示候補(display_phrase)
# に無い語を含むitemだけを対象に、同一モデルルーティング(SUPPORT_MODEL)で日本語glossを最終KP基準で
# 再整合する工程を1回(バッチ)追加する。gloss生成規則は承認済み選定Prompt(b1_p2_keywords_l_prompt_template.txt)
# の「日本語グロス…」の段落を実行時に抽出して再利用する(複製しない)。検証は既存の
# detect_prohibited_symbolsの規則+括弧禁止+算用数字禁止+自己検証項目。
# retry上限2。それでも整合できない場合(OF-227/228、KP-GLOSS-ALIGNMENT-PRODUCTION-01、2026-10-14): 既定は
# (ii)『最終KPを維持し、gloss_alignment_status=FAILEDで記録+run summary/通知(m2_fallbackと同形)へ必ず載せる』。
# 例外として(i)『KPを表示候補へ戻す』はconfig(GLOSS_ALIGNMENT_FALLBACK_MODE)で選んだ場合のみ、かつ戻し先が
# 末尾機能語で終わらずsource_span内に決定論的に含まれる場合に限り許可。全経路(初回/redundancy retry/Strategy L fallback/regeneration)は
# run_key_phrase_canonicalization経由のため同じ工程を通る。
from __future__ import annotations

import copy
import datetime
import difflib
import hashlib
import json
import os
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_audio_tts_asr_safety as safety
import er003_key_words_canonicalization as kc

GLOSS_ALIGNMENT_VERSION = "ER-003-KP-GLOSS-ALIGN-01"
MAX_GLOSS_ALIGNMENT_ATTEMPTS = 2
APPROVED_GLOSS_RULES_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt"
# OF-235 / 2026-10-15 ユーザー承認(KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_02、案a): 未承認のgloss再整合工程が通常Production経路で
# 意図せず実行されないよう、flagの既定値をOFFへ変更した(安全措置のみ。工程自体のProduction採用ではない)。
# 明示ON: 環境変数EIGO_KP_GLOSS_ALIGNMENT=1(true/on/yes可)、または align_glosses(enabled=True)/preflight(True)の明示引数(DEV/Trial)。
GLOSS_ALIGNMENT_ENABLED = os.environ.get("EIGO_KP_GLOSS_ALIGNMENT", "0").strip().lower() in ("1", "true", "on", "yes")


def flag_enabled() -> bool:
    """唯一のkill switch(KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_03、2026-10-15): EIGO_KP_GLOSS_ALIGNMENT明示ONの判定。
    gloss_alignment_mode="corrected"の指定だけでは再整合は実行されない(flag OFFならmode無関係にDISABLED・API 0)。"""
    return bool(GLOSS_ALIGNMENT_ENABLED)
# OF-227/228: fallback方式。"KEEP_KP_FLAG_FAILED"=(ii)既定 / "REVERT_TO_CANDIDATE_IF_SAFE"=(i)(条件付き)。Q2判断後に確定。
FALLBACK_KEEP_KP = "KEEP_KP_FLAG_FAILED"
FALLBACK_REVERT_IF_SAFE = "REVERT_TO_CANDIDATE_IF_SAFE"
GLOSS_ALIGNMENT_FALLBACK_MODE = FALLBACK_KEEP_KP
# OF-230: KP側にスロット語がある場合に限り、glossの「～」「〜」を許可する(無ければFAIL)。
SLOT_TOKENS = frozenset({"someone", "somebody", "something", "one's", "someone's", "somebody's", "oneself"})
_TILDE_RE = re.compile(r"[～〜~]")
DEVELOPER_MESSAGE = ("英語学習教材のKey Phraseに付ける日本語グロスを、最終的な英語Key Phrase全体の意味に"
                     "過不足なく一致させてください。")

GLOSS_ALIGNMENT_JSON_SCHEMA = {
    "name": "key_phrase_gloss_alignment",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rank": {"type": "integer"},
                        "current_gloss_consistent": {"type": "boolean"},
                        "japanese_gloss": {"type": "string"},
                        "qa_reflects_all_key_phrase_words": {"type": "string", "enum": ["PASS", "FAIL"]},
                        "reasoning": {"type": "string"},
                    },
                    "required": ["rank", "current_gloss_consistent", "japanese_gloss",
                                 "qa_reflects_all_key_phrase_words", "reasoning"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}

_PAREN_RE = re.compile(r"[()（）\[\]［］【】]")
_ARABIC_DIGIT_RE = re.compile(r"[0-9]")
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
_GENERIC_TOKENS = {"one's", "someone's", "somebody's", "one", "someone", "somebody", "oneself"}


def _stem(t: str) -> str:
    return re.sub(r"(ing|ed|es|s|d)$", "", t) if len(t) > 3 else t


def _extra_tokens(display_phrase: str, key_phrase: str) -> list:
    """最終KPが表示候補(display_phrase)に対して追加した語(トークン)のリスト(順序保持・重複あり得る)。
    kp_adds_words_beyond_display(legacy、挙動不変)とcorrectedモードの追加内容語算出が共有する(委任_02で関数抽出のみ)。"""
    d = kc._normalize_for_match(display_phrase or "").replace("’", "'")
    k = kc._normalize_for_match(key_phrase or "").replace("’", "'")
    if not k or d == k:
        return []
    articles = {"a", "an", "the"}
    dset = {_stem(t) for t in _TOKEN_RE.findall(d)}
    kset = [t for t in _TOKEN_RE.findall(k) if t not in articles]
    def _near(t):
        return any(difflib.SequenceMatcher(None, _stem(t), x).ratio() >= 0.7 for x in dset)
    return [t for t in kset if t not in _GENERIC_TOKENS and _stem(t) not in dset and not _near(t)]


def kp_adds_words_beyond_display(display_phrase: str, key_phrase: str) -> bool:
    """最終KPが表示候補(display_phrase)に無い語を含むか。活用形の違い(gave/give)・
    人称代名詞の一般化(their->one's)・冠詞の増減は『語の追加』に数えない。"""
    return bool(_extra_tokens(display_phrase, key_phrase))


def select_alignment_targets(merged_items: list) -> list:
    return [it for it in merged_items
            if it.get("kp_extends_beyond_candidate")
            or kp_adds_words_beyond_display(it.get("display_phrase"), it.get("key_phrase"))]


class GlossRulesExtractionError(RuntimeError):
    pass


_RULES_CACHE: dict = {}


def load_approved_gloss_rules(path: str = APPROVED_GLOSS_RULES_TEMPLATE_PATH) -> str:
    """承認済み選定Promptの日本語グロス規則を実行時に抽出する(複製・改変しない)。
    対象: (1)『日本語グロス』で始まる段落すべて(3段落以上) + (2)『短く自然な日本語グロス』を含む選定指示の段落
    (OF-229: テンプレート17行『選ぶ表現は必ず本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付けて…』)。
    いずれかが欠けたらGlossRulesExtractionError(記事内容に依存しない即時失敗)。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    selection = [p for p in paras if "短く自然な日本語グロス" in p]
    gloss = [p for p in paras if p.startswith("日本語グロス")]
    if len(gloss) < 3:
        raise GlossRulesExtractionError(f"承認済みgloss規則の抽出に失敗(日本語グロス段落数不足: {len(gloss)})")
    if len(selection) != 1:
        raise GlossRulesExtractionError(f"承認済み選定指示『短く自然な日本語グロス』段落の抽出に失敗(件数: {len(selection)})")
    return "\n\n".join(selection + gloss)


def rules_sha256(rules: str) -> str:
    return hashlib.sha256(rules.encode("utf-8")).hexdigest()


def preflight(enabled: Optional[bool] = None) -> Optional[dict]:
    """run開始時に1回呼ぶ(OF-229)。抽出失敗は例外で全記事を即時停止させる。無効時は何もしない。
    成功時は{rules, sha256}をキャッシュし、以後のalign_glossesはキャッシュを使う。"""
    if enabled is None:
        enabled = GLOSS_ALIGNMENT_ENABLED
    if not enabled:
        return None
    if "v" not in _RULES_CACHE:
        rules = load_approved_gloss_rules()
        _RULES_CACHE["v"] = {"rules": rules, "sha256": rules_sha256(rules)}
    return _RULES_CACHE["v"]


def build_user_message(targets: list, article_text: str, rules: Optional[str] = None) -> str:
    rules = rules if rules is not None else (preflight(True) or {})["rules"]
    items = [{
        "rank": it["rank"],
        "key_phrase": it["key_phrase"],
        "display_phrase_before_canonicalization": it.get("display_phrase"),
        "current_japanese_gloss": it.get("japanese_gloss"),
        "source_sentence": it.get("source_sentence", ""),
    } for it in targets]
    return (
        "以下の各英語key_phraseは、教材として最終確定した英語表現です。current_japanese_glossは、確定前の候補表現"
        "(display_phrase_before_canonicalization)を基準に付けた日本語グロスで、確定したkey_phrase全体とは"
        "一致していない可能性があります。\n\n"
        "各項目について、current_japanese_glossが最終的なkey_phrase全体(目的語・補語・修飾語を含むすべての語)の"
        "意味と過不足なく一致しているかを判定し(current_gloss_consistent)、japanese_glossに、最終key_phrase全体に"
        "一致する日本語グロスを返してください。key_phraseに含まれる具体的な語(目的語・補語等)は、「～」のような"
        "スロットで済ませず、対応する日本語を具体的に含めてください。key_phrase自体が「someone's」「something」等の"
        "スロットを持つ場合に限り、「～」の使用を許可します。current_japanese_glossが既に最終key_phraseと一致して"
        "いる場合は、その文字列をそのまま返してください。key_phrase単体で他の文脈でも再利用できる自然な訳にし、"
        "本文固有の固有名詞・文脈の追加はしないでください。key_phrase全体の意味を反映できている場合のみ"
        "qa_reflects_all_key_phrase_wordsをPASSにしてください。\n\n"
        "【日本語グロスの規則(承認済み選定Promptと同一)】\n" + rules + "\n\n"
        "【対象項目】\n" + json.dumps(items, ensure_ascii=False, indent=2) + "\n\n【記事本文(参考)】\n" + article_text
    )


class GlossAlignmentModelMismatchError(RuntimeError):
    pass


def make_alignment_fn(user_message: str, client: Optional[Any] = None, model: str = None,
                      reasoning_effort: str = "high", developer_message: str = DEVELOPER_MESSAGE,
                      schema: Optional[dict] = None):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()
    if model is None:
        raise ValueError("modelは明示的に指定してください(routing.require_model()経由)")

    def fn():
        response = client.responses.create(
            model=model, reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **(schema if schema is not None else GLOSS_ALIGNMENT_JSON_SCHEMA)}},
            input=[{"role": "developer", "content": developer_message},
                   {"role": "user", "content": user_message}],
        )
        if response.model != model:
            raise GlossAlignmentModelMismatchError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        u = getattr(response, "usage", None)
        in_d = getattr(u, "input_tokens_details", None)
        fn.last_usage = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                         "cached_input_tokens": getattr(in_d, "cached_tokens", None) if in_d is not None else None}
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise RuntimeError("gloss alignment応答が空です")
        return text, response.model, response.id

    fn.last_usage = None
    fn.model = model
    fn.reasoning_effort = reasoning_effort
    return fn


def kp_has_slot_word(key_phrase: Optional[str]) -> bool:
    toks = _TOKEN_RE.findall(kc._normalize_for_match(key_phrase or "").replace("’", "'"))
    return any(t in SLOT_TOKENS for t in toks)


def gloss_has_unjustified_slot(key_phrase: Optional[str], gloss: Optional[str]) -> bool:
    """OF-230: KPにスロット語(someone/something/one's/oneself等)が無いのに、glossに「～」「〜」が残っていればTrue。
    LLM自己申告(qa_reflects_all_key_phrase_words)に依存しない決定論チェック。"""
    return bool(_TILDE_RE.search(gloss or "")) and not kp_has_slot_word(key_phrase)


def validate_alignment_response(parsed: Any, targets: list) -> dict:
    reasons = []
    if not isinstance(parsed, dict) or not isinstance(parsed.get("items"), list):
        return {"ok": False, "reasons": ["items欠落"], "by_rank": {}}
    by_rank = {}
    for it in parsed["items"]:
        if isinstance(it, dict) and isinstance(it.get("rank"), int):
            by_rank[it["rank"]] = it
    want = [t["rank"] for t in targets]
    if sorted(by_rank) != sorted(want) or len(parsed["items"]) != len(want):
        reasons.append(f"rank不一致 want={want} got={sorted(by_rank)}")
    for r in want:
        it = by_rank.get(r)
        if not it:
            continue
        g = it.get("japanese_gloss")
        if not isinstance(g, str) or not g.strip():
            reasons.append(f"rank{r}: gloss空")
            continue
        if it.get("qa_reflects_all_key_phrase_words") != "PASS":
            reasons.append(f"rank{r}: qa_reflects_all_key_phrase_words!=PASS")
        if _PAREN_RE.search(g):
            reasons.append(f"rank{r}: 括弧禁止違反")
        if _ARABIC_DIGIT_RE.search(g):
            reasons.append(f"rank{r}: 算用数字禁止違反")
        if "…" in g:
            reasons.append(f"rank{r}: …禁止違反")
        tgt = next((t for t in targets if t["rank"] == r), None)
        if tgt is not None and gloss_has_unjustified_slot(tgt.get("key_phrase"), g):
            reasons.append(f"rank{r}: KPにスロット語が無いのにglossに「～」が残っている(決定論チェックFAIL)")
        if safety.symbol_gate_requires_stop(
                [{**f, "rank": r} for f in safety.detect_prohibited_symbols(kc.convert_display_gloss_to_tts_text(g), language="ja")]):
            reasons.append(f"rank{r}: 音声化禁止記号")
    return {"ok": not reasons, "reasons": reasons, "by_rank": by_rank}


def _usage_cost(fn, model_id) -> dict:
    u = getattr(fn, "last_usage", None) or {}
    cost = None
    try:
        import er009_n1_routing_governance_10_actual_model_cost as pricing
        if u.get("input_tokens") is not None:
            cost = round(pricing.cost_jpy_for_call("openai", model_id or getattr(fn, "model", None), u.get("input_tokens"),
                                                   u.get("cached_input_tokens"), u.get("output_tokens")), 4)
    except Exception:
        cost = None
    return {"usage": u, "cost_jpy": cost}


def run_alignment_gate(make_factory: Callable[[], Callable], targets: list,
                       max_attempts: int = MAX_GLOSS_ALIGNMENT_ATTEMPTS):
    attempts = []
    for attempt in range(1, max_attempts + 1):
        fn = make_factory()
        try:
            raw, model_id, response_id = fn()
        except Exception as e:  # 技術的失敗も同じ上限の中でretry
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}",
                             **_usage_cost(fn, None)})
            continue
        uc = _usage_cost(fn, model_id)
        try:
            parsed = json.loads(raw)
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "PARSE_FAILED", "error": str(e), "model": model_id, **uc})
            continue
        v = validate_alignment_response(parsed, targets)
        attempts.append({"attempt": attempt, "status": "ALIGN_PASS" if v["ok"] else "ALIGN_INVALID",
                         "reasons": v["reasons"], "parsed": parsed, "model": model_id, "response_id": response_id, **uc})
        if v["ok"]:
            return v["by_rank"], "ALIGN_PASS", attempts, model_id, response_id
    return None, "ALIGN_FAILED", attempts, None, None


def revert_to_candidate_allowed(item: dict) -> tuple:
    """OF-227(i)の例外条件: 戻し先display_phraseが(1)末尾機能語で終わらず(2)source_span内に決定論的に含まれ、
    (3)Rule7(validate_canonicalization_item)を通る場合のみTrue。戻り値(許可, 理由)。"""
    disp = item.get("display_phrase") or ""
    toks = kc._SPAN_WORD_RE.findall(kc._normalize_for_match(disp).replace("’", "'"))
    if not toks:
        return False, "display_phrase空"
    if toks[-1] in kc._DANGLING_TAIL_WORDS:
        return False, f"display_phraseが末尾機能語({toks[-1]})で終わる"
    span = item.get("source_span") or ""
    if not span or not kc._is_contiguous_substring(disp, span):
        return False, "display_phraseがsource_span内の連続部分文字列でない"
    v = kc.validate_canonicalization_item(disp, disp, span)
    if not v["ok"]:
        return False, "Rule7再判定NG: " + "; ".join(v["reasons"])
    return True, "OK"


def apply_alignment(merged: dict, by_rank: Optional[dict], targets: list,
                    fallback_mode: Optional[str] = None) -> dict:
    """merged(merge_canonicalization_result出力)へ結果を適用する(新しいdictを返す)。
    by_rank=Noneはretry上限でも整合できなかった場合(OF-227/228):
      既定(ii) KEEP_KP_FLAG_FAILED: 最終KPを維持し、gloss_alignment.status=GLOSS_ALIGNMENT_FAILED_KP_KEPT、
        gloss_review_hint=True、merged['gloss_alignment_failed'](全件list)へ記録(通知用)。人間確認Queueへは送らない。
      (i) REVERT_TO_CANDIDATE_IF_SAFE: revert_to_candidate_allowedを満たすitemのみKPを表示候補へ戻す(qa/
        normalization_reason/reasoning/canonicalization_source_spanは無効化・再計算、gloss_review_hint維持)。
        満たさないitemは(ii)と同じ。"""
    fallback_mode = fallback_mode or GLOSS_ALIGNMENT_FALLBACK_MODE
    target_ranks = {t["rank"] for t in targets}
    items = []
    failed = []
    for it in merged["items"]:
        if it["rank"] not in target_ranks:
            items.append(it)
            continue
        new = dict(it)
        orig_gloss = it.get("japanese_gloss")
        if by_rank is not None:
            a = by_rank[it["rank"]]
            new["japanese_gloss"] = a["japanese_gloss"].strip()
            new["japanese_gloss_tts"] = kc.convert_display_gloss_to_tts_text(new["japanese_gloss"])
            changed = new["japanese_gloss"] != orig_gloss
            new["gloss_alignment"] = {
                "version": GLOSS_ALIGNMENT_VERSION,
                "status": "GLOSS_REALIGNED" if changed else "GLOSS_ALREADY_CONSISTENT",
                "original_japanese_gloss": orig_gloss,
                "current_gloss_consistent_verdict": a["current_gloss_consistent"],
                "reasoning": a["reasoning"],
            }
            new["gloss_review_hint"] = False
        else:
            ok, why = (False, "mode=keep_kp")
            if fallback_mode == FALLBACK_REVERT_IF_SAFE:
                ok, why = revert_to_candidate_allowed(it)
            if ok:
                reverted = it.get("display_phrase")
                new["gloss_alignment"] = {
                    "version": GLOSS_ALIGNMENT_VERSION, "status": "FALLBACK_KP_REVERTED_TO_DISPLAY_PHRASE",
                    "original_japanese_gloss": orig_gloss, "key_phrase_before_revert": it["key_phrase"],
                    "gloss_alignment_status": "FAILED"}
                new["key_phrase"] = reverted
                new["used_form"] = reverted
                new["changed_from_display_phrase"] = False
                new["kp_extends_beyond_candidate"] = False
                new["normalization_reason"] = "none"
                new["reasoning"] = "gloss再整合に失敗したためKPを表示候補へ戻した(canonicalization判断は無効化)"
                new["qa"] = {k: "INVALIDATED_BY_GLOSS_REVERT" for k in (it.get("qa") or {})}
                new.pop("canonicalization_source_span", None)
                new["gloss_review_hint"] = True
                new["gloss_alignment_status"] = "FAILED"
            else:
                new["gloss_alignment"] = {
                    "version": GLOSS_ALIGNMENT_VERSION, "status": "GLOSS_ALIGNMENT_FAILED_KP_KEPT",
                    "original_japanese_gloss": orig_gloss, "key_phrase_kept": it["key_phrase"],
                    "gloss_alignment_status": "FAILED", "revert_not_applied_reason": why}
                new["gloss_review_hint"] = True
                new["gloss_alignment_status"] = "FAILED"
            failed.append({"rank": it["rank"], "key_phrase": it["key_phrase"], "display_phrase": it.get("display_phrase"),
                           "japanese_gloss": orig_gloss, "action": new["gloss_alignment"]["status"],
                           "fallback_mode": fallback_mode, "gloss_alignment_status": "FAILED"})
        items.append(new)
    out = dict(merged)
    out["items"] = items
    if failed:
        out["gloss_alignment_failed"] = failed
    return out


def build_gloss_alignment_fallback_record(article_id: str, failed: list, fallback_mode: str) -> dict:
    """m2_fallback_eventsと同形(article/stage/reason_code/reason/fallback_result/note)のrun summary用record。"""
    return {"article": article_id, "stage": "kp_gloss_alignment", "reason_code": "GLOSS_ALIGNMENT_FAILED",
            "reason": f"gloss再整合が上限{MAX_GLOSS_ALIGNMENT_ATTEMPTS}回で成立しなかった(rank={[f['rank'] for f in failed]})",
            "fallback_result": f"mode={fallback_mode} actions={[f['action'] for f in failed]}",
            "items": failed,
            "note": "gloss_alignment_status=FAILED。人間確認Queueへは送らない。PM/Fableはユーザーへ必ず報告すること。"}


def align_glosses(merged: dict, article_text: str, make_factory_for: Callable[[str], Callable],
                  out_dir: Optional[str] = None, article_id: str = "", enabled: Optional[bool] = None,
                  fallback_mode: Optional[str] = None, mode: Optional[str] = None,
                  mapping_gate: bool = False) -> dict:
    """戻り値: {"merged": 更新後merged, "status": ..., "targets": [ranks], "attempts": [...]}。
    対象0件のときはAPI呼出なし・mergedは無変更(同一object)。enabled=False(flag OFF)なら status=DISABLED で無変更。
    mode(委任_02、KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01): 既定None=GLOSS_ALIGNMENT_MODE(=legacy、現行挙動そのまま)。
    "corrected"=Trial専用の新設計(明示引数のみ。envでは切替えない)。mapping_gateはcorrectedのみ有効。"""
    if resolve_mode(mode) == GLOSS_ALIGNMENT_MODE_CORRECTED:
        return _align_glosses_corrected(merged, article_text, make_factory_for, out_dir=out_dir, article_id=article_id,
                                        enabled=enabled, mapping_gate=mapping_gate)
    if enabled is None:
        enabled = GLOSS_ALIGNMENT_ENABLED
    if not enabled:
        return {"merged": merged, "status": "DISABLED", "targets": [], "attempts": []}
    targets = select_alignment_targets(merged["items"])
    if not targets:
        return {"merged": merged, "status": "NO_TARGETS", "targets": [], "attempts": []}
    pf = preflight(True)
    user_message = build_user_message(targets, article_text, rules=pf["rules"])
    by_rank, status, attempts, model_id, response_id = run_alignment_gate(
        lambda: make_factory_for(user_message), targets)
    new_merged = apply_alignment(merged, by_rank, targets, fallback_mode=fallback_mode)
    total_cost = round(sum(a.get("cost_jpy") or 0 for a in attempts), 4)
    fb = None
    if new_merged.get("gloss_alignment_failed"):
        fb = build_gloss_alignment_fallback_record(article_id, new_merged["gloss_alignment_failed"],
                                                   fallback_mode or GLOSS_ALIGNMENT_FALLBACK_MODE)
    if out_dir:
        with open(f"{out_dir}/gloss_alignment_prompt.txt", "w", encoding="utf-8") as f:
            f.write(user_message)
        with open(f"{out_dir}/gloss_alignment_runtime_metadata.json", "w", encoding="utf-8") as f:
            json.dump({"article_id": article_id, "version": GLOSS_ALIGNMENT_VERSION, "final_status": status,
                       "model_id": model_id, "response_id": response_id, "targets": [t["rank"] for t in targets],
                       "rules_sha256": pf["sha256"], "cost_jpy": total_cost,
                       "fallback_mode": fallback_mode or GLOSS_ALIGNMENT_FALLBACK_MODE,
                       "gloss_alignment_fallback": fb,
                       "attempts_detail": attempts}, f, ensure_ascii=False, indent=2)
    return {"merged": new_merged, "status": status, "targets": [t["rank"] for t in targets],
            "attempts": attempts, "model_id": model_id, "cost_jpy": total_cost, "fallback_event": fb,
            "rules_sha256": pf["sha256"]}


GLOSS_ALIGNMENT_NOTICE_FILENAME = "GLOSS_ALIGNMENT_FAILED_NOTICE.md"


def write_failed_notice(out_dir: str, events: list):
    """run dir直下へ人間可読notice(M2_FALLBACK_NOTICEと同パターン)。eventsが空なら何も書かずNoneを返す。"""
    if not events:
        return None
    path = os.path.join(out_dir, GLOSS_ALIGNMENT_NOTICE_FILENAME)
    lines = ["# GLOSS_ALIGNMENT_FAILED_NOTICE", "",
             "KP gloss再整合が上限回数で成立しませんでした(gloss_alignment_status=FAILED)。",
             "**PM/Fableはユーザーへ必ず報告してください。人間確認Queueへは自動で送っていません。**", ""]
    for i, ev in enumerate(events, 1):
        lines.append(f"## Event {i}")
        for k in ("article", "stage", "reason_code", "reason", "fallback_result", "note"):
            lines.append(f"- {k}: {ev.get(k)}")
        for f in ev.get("items", []):
            lines.append(f"- item rank={f['rank']} KP={f['key_phrase']!r} gloss={f['japanese_gloss']!r} action={f['action']}")
        lines.append("")
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def format_failed_stdout(events: list) -> str:
    if not events:
        return "[GLOSS-ALIGN] FAILEDなし"
    parts = [f"[GLOSS-ALIGN][NOTICE] gloss再整合FAILEDが{len(events)}記事で発生しました。ユーザーへ必ず報告してください"
             f"({GLOSS_ALIGNMENT_NOTICE_FILENAME}参照)。"]
    for ev in events:
        parts.append(f"  - article={ev.get('article')} {ev.get('reason')} result={ev.get('fallback_result')}")
    return "\n".join(parts)


# ============================================================
# KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02 (2026-10-15): mode="corrected"(DEV/Trial専用)
# ============================================================
# 本節は「gloss再整合の方針A/B/C/D」(ユーザー2026-10-15)をTrial専用modeで実装する。Production既定は変更しない:
#   * 既定mode=legacy(上記の現行挙動そのまま)。corrected は align_glosses(..., mode="corrected") /
#     run_key_phrases(..., gloss_alignment_mode="corrected") の**明示引数でのみ**有効(envでは切替えない)。
#   * correctedで不使用(legacyでは残す): SLOT_TOKENS / kp_has_slot_word / gloss_has_unjustified_slot / fallback(i)
#     (revert_to_candidate_allowed / FALLBACK_REVERT_IF_SAFE) / GLOSS_ALIGNMENT_FALLBACK_MODE / apply_alignment /
#     build_gloss_alignment_fallback_record / write_failed_notice / format_failed_stdout。
#   * 方針A: 「～」の有無は合否に使わない。追加内容語→日本語span対応は record-only(gate化は要ユーザー承認)。
#   * 方針B/C: 2回(item単位)失敗したitemは gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED としてartifactに永続化し、
#     消費側(Family X TTS関所/Family Z stage_kp)が参照して停止する。Human Review Lock・human_review_queue.jsonlは使わない。
#     KPを短い候補へ戻さない(参考情報としてHR報告書に載せるのみ)。
GLOSS_ALIGNMENT_MODE_LEGACY = "legacy"
GLOSS_ALIGNMENT_MODE_CORRECTED = "corrected"
GLOSS_ALIGNMENT_MODES = (GLOSS_ALIGNMENT_MODE_LEGACY, GLOSS_ALIGNMENT_MODE_CORRECTED)
# Production既定。ここを書換えない限りcorrectedはProduction経路で動かない(既定ON/OFFはユーザー判断=別UDR)。
GLOSS_ALIGNMENT_MODE = GLOSS_ALIGNMENT_MODE_LEGACY

STATUS_HR_REQUIRED = "FAILED_HUMAN_REVIEW_REQUIRED"      # itemのgloss_alignment_status(correctedのみが書く)
STATUS_HUMAN_RESOLVED = "HUMAN_RESOLVED"                 # resolve_glossが書く
STATUS_ALIGNED = "ALIGNED"                               # correctedで再整合が成立したitem
STOPPED_STATUS = "STOPPED_GLOSS_ALIGNMENT_FAILED"        # 消費側(TTS関所)が返す非OK status(Gateは非許可statusとしてblock)
HR_REPORT_JSON = "GLOSS_ALIGNMENT_HUMAN_REVIEW_01.json"
HR_REPORT_MD = "GLOSS_ALIGNMENT_HUMAN_REVIEW_01.md"
HR_REPORT_VERSION = "ER-003-KP-GLOSS-ALIGN-HR-01"
HR_REASON_CODE = "GLOSS_ALIGNMENT_HUMAN_REVIEW_REQUIRED"
HR_REFERENCE_CAUTION = "KPを短くすると意味が失われる、人間判断でのみ採用"


class GlossAlignmentNotificationError(RuntimeError):
    """HR報告の書込/再読検証に失敗(fail-closed: 呼出元は当該stageを止める。『通知失敗だが継続』は禁止)。"""


class GlossResolveRejected(ValueError):
    pass


def resolve_mode(mode: Optional[str] = None) -> str:
    m = mode if mode is not None else GLOSS_ALIGNMENT_MODE
    if m not in GLOSS_ALIGNMENT_MODES:
        raise ValueError(f"gloss_alignment_modeは{GLOSS_ALIGNMENT_MODES}のいずれか: {m!r}")
    return m


# ---- 追加内容語(機械算出) -------------------------------------------------
# 機能語(前置詞・不変化詞・助動詞・冠詞・接続/補助語)は日本語spanの必須対象外(Opus OF-KGDC-06)。
# 人称代名詞の一般化(their->one's等)は_extra_tokens側で既に追加語に数えない。
FUNCTION_WORDS = frozenset({
    "a", "an", "the",
    "in", "on", "at", "to", "of", "for", "with", "by", "from", "into", "onto", "about", "around", "through",
    "across", "after", "before", "between", "against", "among", "along", "as", "than", "per", "via", "over",
    "under", "above", "below", "behind", "beyond", "within", "without", "toward", "towards", "upon", "off",
    "up", "down", "out", "away", "back", "forth", "apart",
    "be", "is", "are", "am", "was", "were", "been", "being", "do", "does", "did", "have", "has", "had",
    "will", "would", "can", "could", "shall", "should", "may", "might", "must",
    "and", "or", "but", "if", "that", "so",
})


def added_content_words(display_phrase: str, key_phrase: str) -> list:
    """最終KPが候補に追加した内容語(機能語除く)。重複除去・出現順。correctedの機械検査対象。"""
    seen, out = set(), []
    for t in _extra_tokens(display_phrase, key_phrase):
        if t in FUNCTION_WORDS or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


_WS_RE = re.compile(r"\s+")


def _norm_tilde_space(s: Optional[str]) -> str:
    """OF-KGDC-10: 『真なら不変』比較の正規化(空白と～/〜/~のみ。それ以外の書換えは検知する)。"""
    return _WS_RE.sub("", s or "").replace("〜", "～").replace("~", "～")


def _norm_span(s: Optional[str]) -> str:
    """OF-KGDC-06: span一致の正規化(NFKC+空白除去+～/〜統一)。"""
    return _norm_tilde_space(unicodedata.normalize("NFKC", s or ""))


_SYMBOL_ONLY_RE = re.compile(r"[～~〜\s・、。,.!?！？「」『』\-ー_/…]*")


def _span_is_symbol_only(span_norm: str) -> bool:
    return _SYMBOL_ONLY_RE.fullmatch(span_norm or "") is not None


def _words_match(a: str, b: str) -> bool:
    """英単語の同一性(活用/単複を許容): 完全一致・語幹一致・長さ4以上の前方一致(price/prices, watch/watching)。"""
    if a == b or _stem(a) == _stem(b):
        return True
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    return len(short) >= 4 and long_.startswith(short)


def check_added_word_mappings(required_words: list, mappings: Any, gloss: str) -> dict:
    """追加内容語→日本語span対応の機械検査(record-only既定。gate化はユーザー承認事項)。
    判定=必須内容語すべてが、gloss内に実在する記号以外のspanのいずれかで覆われる。
    mappingは多対一・重複可、english_wordに句可(トークン/語幹一致)。戻り値のpassは『gateとして判定した場合』の合否。"""
    result = {"required_words": list(required_words), "covered": {}, "uncovered": [], "span_not_in_gloss": [],
              "symbol_only_spans": [], "malformed_mappings": 0, "pass": True}
    if not required_words:
        result["note"] = "必須内容語なし(機械検査対象外)"
        return result
    gnorm = _norm_span(gloss)
    valid = []   # (english_tokens, span_original)
    if not isinstance(mappings, list):
        result["malformed_mappings"] = 1
        mappings = []
    for m in mappings:
        if not (isinstance(m, dict) and isinstance(m.get("english_word"), str) and isinstance(m.get("japanese_span"), str)):
            result["malformed_mappings"] += 1
            continue
        span = m["japanese_span"]
        sn = _norm_span(span)
        if not sn or _span_is_symbol_only(sn):
            result["symbol_only_spans"].append(span)
            continue
        if sn not in gnorm:
            result["span_not_in_gloss"].append(span)
            continue
        toks = _TOKEN_RE.findall(m["english_word"].lower().replace("’", "'"))
        valid.append((toks, span))
    for w in required_words:
        hit = next((span for toks, span in valid if any(_words_match(t, w) for t in toks)), None)
        if hit is None:
            result["uncovered"].append(w)
        else:
            result["covered"][w] = hit
    result["pass"] = not result["uncovered"]
    return result


# ---- 課題指示文(DESIGN_DRAFT_01 3.3 + Opus OF-KGDC (b)) ----------------------
GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED = copy.deepcopy(GLOSS_ALIGNMENT_JSON_SCHEMA)
GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED["name"] = "key_phrase_gloss_alignment_corrected"
_item_schema = GLOSS_ALIGNMENT_JSON_SCHEMA_CORRECTED["schema"]["properties"]["items"]["items"]
_item_schema["properties"]["added_word_mappings"] = {
    "type": "array",
    "items": {"type": "object",
              "properties": {"english_word": {"type": "string"}, "japanese_span": {"type": "string"}},
              "required": ["english_word", "japanese_span"], "additionalProperties": False},
}
_item_schema["required"] = ["rank", "current_gloss_consistent", "japanese_gloss", "added_word_mappings",
                            "qa_reflects_all_key_phrase_words", "reasoning"]
del _item_schema


def build_user_message_corrected(targets: list, article_text: str, rules: Optional[str] = None) -> str:
    rules = rules if rules is not None else (preflight(True) or {})["rules"]
    items = [{
        "rank": it["rank"],
        "key_phrase": it["key_phrase"],
        "display_phrase_before_canonicalization": it.get("display_phrase"),
        "current_japanese_gloss": it.get("japanese_gloss"),
        "source_sentence": it.get("source_sentence", ""),
        "added_content_words": added_content_words(it.get("display_phrase"), it.get("key_phrase")),
    } for it in targets]
    return (
        "以下の各英語key_phraseは、教材として最終確定した英語表現です。current_japanese_glossは、確定前の候補表現"
        "(display_phrase_before_canonicalization)を基準に付けた日本語グロスで、確定したkey_phrase全体とは"
        "一致していない可能性があります。added_content_wordsは、確定時に候補表現へ新しく加わった内容語です"
        "(空の場合があります)。\n\n"
        "各項目について、次を行ってください。\n"
        "1. current_japanese_glossが、最終的なkey_phrase全体(目的語・補語・修飾語を含むすべての語)の意味と過不足なく"
        "一致しているかを判定し(current_gloss_consistent)てください。「～」「〜」を含むかどうかは判定の基準ではありません。"
        "key_phrase全体の意味が日本語に表れているかどうかだけで判定してください。\n"
        "2. 一致している場合は、japanese_glossにcurrent_japanese_glossをそのまま返してください。一致していない場合は、"
        "最終key_phrase全体に一致する日本語グロスを返してください。\n"
        "3. added_content_wordsの各語について、japanese_glossの中でその語の意味を表している部分を、japanese_glossから"
        "そのまま切り出してadded_word_mappingsに書いてください(english_wordには対応させる英語の語、複数語をまとめた句でも"
        "かまいません。japanese_spanにはjapanese_glossに含まれない文字列や、「～」などの記号だけを書かないでください)。"
        "複数の英語語が一つの日本語表現でまとめて表されている場合は、同じ部分を複数の語に対応させてかまいません。"
        "added_content_wordsが空の項目は、added_word_mappingsを空配列にしてください。\n"
        "判定の参考例:\n"
        "- key_phrase「based on」にcurrent「～をもとにした」: 辞書的に自然なので一致です。\n"
        "- key_phrase「based on interviews」にcurrent「～をもとにした」: interviewsの意味が欠けているので不一致です。"
        "「インタビューをもとにした」なら一致です。\n\n"
        "key_phrase単体で他の文脈でも再利用できる自然な訳にし、本文固有の固有名詞・文脈の追加はしないでください。"
        "key_phrase全体の意味を反映できている場合のみqa_reflects_all_key_phrase_wordsをPASSにしてください。\n\n"
        "【日本語グロスの規則(承認済み選定Promptと同一)】\n" + rules + "\n\n"
        "【対象項目】\n" + json.dumps(items, ensure_ascii=False, indent=2) + "\n\n【記事本文(参考)】\n" + article_text
    )


# ---- item単位検証(「～」条件なし) ---------------------------------------------
def validate_item_corrected(resp: Any, target: dict, mapping_gate: bool = False) -> dict:
    """1 itemの応答を検証する。合否=LLM判定(qa PASS・真偽とglossの整合)+承認規則由来の記号チェック。
    mappingの機械検査(machine_check)は常に記録し、mapping_gate=Trueの場合のみ合否にも使う(既定record-only)。"""
    rank = target["rank"]
    cur = target.get("japanese_gloss") or ""
    reasons: list = []
    out = {"rank": rank, "valid": False, "reasons": reasons, "machine_check": None, "adopt_gloss": None,
           "proposed_gloss": None, "current_gloss_consistent": None, "qa": None, "reasoning": None,
           "added_word_mappings": None}
    if not isinstance(resp, dict):
        reasons.append("応答にこのrankのitemが無い")
        return out
    g = resp.get("japanese_gloss")
    out["current_gloss_consistent"] = resp.get("current_gloss_consistent")
    out["qa"] = resp.get("qa_reflects_all_key_phrase_words")
    out["reasoning"] = resp.get("reasoning")
    out["added_word_mappings"] = resp.get("added_word_mappings")
    if not isinstance(g, str) or not g.strip():
        reasons.append("gloss空")
        return out
    g = g.strip()
    out["proposed_gloss"] = g
    consistent = resp.get("current_gloss_consistent")
    if not isinstance(consistent, bool):
        reasons.append("current_gloss_consistentが真偽値でない")
    if resp.get("qa_reflects_all_key_phrase_words") != "PASS":
        reasons.append("qa_reflects_all_key_phrase_words!=PASS")
    if _PAREN_RE.search(g):
        reasons.append("括弧禁止違反")
    if _ARABIC_DIGIT_RE.search(g):
        reasons.append("算用数字禁止違反")
    if "…" in g:
        reasons.append("…禁止違反")
    if safety.symbol_gate_requires_stop(
            [{**f, "rank": rank} for f in safety.detect_prohibited_symbols(kc.convert_display_gloss_to_tts_text(g), language="ja")]):
        reasons.append("音声化禁止記号")
    same = _norm_tilde_space(g) == _norm_tilde_space(cur)
    if consistent is True and not same:
        reasons.append("current_gloss_consistent=真なのにcurrentと異なるglossを返した(矛盾)")
    if consistent is False and same:
        reasons.append("current_gloss_consistent=偽なのにcurrentと同じglossを返した(矛盾)")
    adopt = cur if (consistent is True and same) else g
    out["adopt_gloss"] = adopt
    required = added_content_words(target.get("display_phrase"), target.get("key_phrase"))
    mc = check_added_word_mappings(required, resp.get("added_word_mappings"), adopt)
    out["machine_check"] = mc
    if mapping_gate and not mc["pass"]:
        reasons.append(f"追加内容語に対応するspanが無い/不正: {mc['uncovered']}(mapping gate)")
    out["valid"] = not reasons
    return out


def _item_log_entry(attempt: int, v: dict, batch: dict) -> dict:
    return {"attempt": attempt, "verdict": "VALID" if v["valid"] else "INVALID", "reasons": list(v["reasons"]),
            "proposed_gloss": v["proposed_gloss"], "current_gloss_consistent": v["current_gloss_consistent"],
            "qa": v["qa"], "reasoning": v["reasoning"], "added_word_mappings": v["added_word_mappings"],
            "machine_check": v["machine_check"], "batch_status": batch.get("status"),
            "batch_cost_jpy": batch.get("cost_jpy"), "model": batch.get("model")}


def run_alignment_gate_corrected(make_factory_for: Callable[[str], Callable], targets: list, article_text: str,
                                 rules: str, mapping_gate: bool = False,
                                 max_attempts: int = MAX_GLOSS_ALIGNMENT_ATTEMPTS) -> dict:
    """item単位retry(OF-KGDC-09): 各attemptは未解決itemのみで入力を再構築し、各itemは最初の有効出力を採用する。
    上限は既存と同じ2回(MAX_GLOSS_ALIGNMENT_ATTEMPTS)。技術失敗/JSON不正もattemptを消費する。"""
    adopted: dict = {}
    item_log = {t["rank"]: [] for t in targets}
    attempts: list = []
    messages: list = []
    pending = list(targets)
    for attempt in range(1, max_attempts + 1):
        if not pending:
            break
        msg = build_user_message_corrected(pending, article_text, rules)
        messages.append(msg)
        fn = make_factory_for(msg)
        rec = {"attempt": attempt, "target_ranks": [t["rank"] for t in pending]}
        try:
            raw, model_id, response_id = fn()
        except Exception as e:
            rec.update({"status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}", **_usage_cost(fn, None)})
            attempts.append(rec)
            for t in pending:
                item_log[t["rank"]].append({"attempt": attempt, "verdict": "TECHNICAL_FAILED", "reasons": [rec["error"]],
                                            "proposed_gloss": None, "batch_status": rec["status"],
                                            "batch_cost_jpy": rec.get("cost_jpy")})
            continue
        rec.update({"model": model_id, "response_id": response_id, **_usage_cost(fn, model_id)})
        try:
            parsed = json.loads(raw)
        except Exception as e:
            rec.update({"status": "PARSE_FAILED", "error": str(e)})
            attempts.append(rec)
            for t in pending:
                item_log[t["rank"]].append({"attempt": attempt, "verdict": "PARSE_FAILED", "reasons": [f"JSON不正: {e}"],
                                            "proposed_gloss": None, "batch_status": rec["status"],
                                            "batch_cost_jpy": rec.get("cost_jpy"), "model": model_id})
            continue
        resp_items = parsed.get("items") if isinstance(parsed, dict) else None
        if not isinstance(resp_items, list):
            resp_items = []
            rec["structure_note"] = "items欠落"
        by_rank: dict = {}
        for it in resp_items:
            if isinstance(it, dict) and isinstance(it.get("rank"), int) and it["rank"] not in by_rank:
                by_rank[it["rank"]] = it
        extra = sorted(set(by_rank) - {t["rank"] for t in pending})
        if extra:
            rec["extra_ranks_ignored"] = extra
        n_valid = 0
        for t in pending:
            v = validate_item_corrected(by_rank.get(t["rank"]), t, mapping_gate=mapping_gate)
            item_log[t["rank"]].append(_item_log_entry(attempt, v, {"status": None, "cost_jpy": rec.get("cost_jpy"),
                                                                    "model": model_id}))
            if v["valid"]:
                adopted[t["rank"]] = {**v, "attempt": attempt}
                n_valid += 1
        rec["status"] = "ALIGN_PASS" if n_valid == len(pending) else ("ALIGN_PARTIAL" if n_valid else "ALIGN_INVALID")
        rec["n_valid"] = n_valid
        rec["n_items"] = len(pending)
        rec["parsed"] = parsed
        attempts.append(rec)
        pending = [t for t in pending if t["rank"] not in adopted]
    return {"adopted": adopted, "unresolved_ranks": [t["rank"] for t in pending], "item_log": item_log,
            "attempts": attempts, "messages": messages}


def apply_alignment_corrected(merged: dict, targets: list, gate: dict) -> dict:
    """適用(新しいdictを返す)。成立item: gloss更新(真なら不変=currentの原文を保持)。未解決item: KP・旧glossは維持し
    gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED(KPを候補へ戻さない=方針C)。対象外itemは無変更。"""
    target_ranks = {t["rank"] for t in targets}
    unresolved = set(gate["unresolved_ranks"])
    items, unresolved_list = [], []
    for it in merged["items"]:
        r = it["rank"]
        if r not in target_ranks:
            items.append(it)
            continue
        new = dict(it)
        orig = it.get("japanese_gloss")
        log = gate["item_log"].get(r, [])
        if r in gate["adopted"]:
            a = gate["adopted"][r]
            adopt = a["adopt_gloss"]
            changed = _norm_tilde_space(adopt) != _norm_tilde_space(orig) or adopt != orig
            if changed:
                new["japanese_gloss"] = adopt
                new["japanese_gloss_tts"] = kc.convert_display_gloss_to_tts_text(adopt)
            new["gloss_alignment"] = {
                "version": GLOSS_ALIGNMENT_VERSION, "mode": GLOSS_ALIGNMENT_MODE_CORRECTED,
                "status": "GLOSS_REALIGNED" if changed else "GLOSS_ALREADY_CONSISTENT",
                "original_japanese_gloss": orig, "current_gloss_consistent_verdict": a["current_gloss_consistent"],
                "reasoning": a["reasoning"], "adopted_attempt": a["attempt"],
                "added_word_mappings": a["added_word_mappings"], "machine_check_record_only": a["machine_check"],
                "attempts_count": len(log)}
            new["gloss_review_hint"] = False
            new["gloss_alignment_status"] = STATUS_ALIGNED
        else:
            new["gloss_alignment"] = {
                "version": GLOSS_ALIGNMENT_VERSION, "mode": GLOSS_ALIGNMENT_MODE_CORRECTED,
                "status": "GLOSS_ALIGNMENT_FAILED_HUMAN_REVIEW_REQUIRED",
                "original_japanese_gloss": orig, "key_phrase_kept": it.get("key_phrase"),
                "failure": {"attempts": log, "attempts_count": len(log)}}
            new["gloss_review_hint"] = True
            new["gloss_alignment_status"] = STATUS_HR_REQUIRED
            unresolved_list.append({"rank": r, "key_phrase": it.get("key_phrase")})
        items.append(new)
    out = dict(merged)
    out["items"] = items
    if unresolved_list:
        out["gloss_alignment_unresolved"] = unresolved_list
    return out


def _align_glosses_corrected(merged: dict, article_text: str, make_factory_for: Callable[[str], Callable],
                             out_dir: Optional[str] = None, article_id: str = "", enabled: Optional[bool] = None,
                             mapping_gate: bool = False) -> dict:
    if enabled is None:
        enabled = GLOSS_ALIGNMENT_ENABLED
    base = {"mode": GLOSS_ALIGNMENT_MODE_CORRECTED}
    if not enabled:
        return {**base, "merged": merged, "status": "DISABLED", "targets": [], "attempts": []}
    targets = select_alignment_targets(merged["items"])
    if not targets:
        return {**base, "merged": merged, "status": "NO_TARGETS", "targets": [], "attempts": []}
    pf = preflight(True)
    gate = run_alignment_gate_corrected(make_factory_for, targets, article_text, pf["rules"], mapping_gate=mapping_gate)
    new_merged = apply_alignment_corrected(merged, targets, gate)
    n_unres = len(gate["unresolved_ranks"])
    status = "ALIGN_PASS" if n_unres == 0 else ("ALIGN_FAILED_HUMAN_REVIEW_REQUIRED" if n_unres == len(targets)
                                                else "ALIGN_PARTIAL_HUMAN_REVIEW_REQUIRED")
    total_cost = round(sum(a.get("cost_jpy") or 0 for a in gate["attempts"]), 4)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        for i, msg in enumerate(gate["messages"], 1):
            fn_ = "gloss_alignment_prompt.txt" if i == 1 else f"gloss_alignment_prompt_attempt{i}.txt"
            with open(f"{out_dir}/{fn_}", "w", encoding="utf-8") as f:
                f.write(msg)
        with open(f"{out_dir}/gloss_alignment_runtime_metadata.json", "w", encoding="utf-8") as f:
            json.dump({"article_id": article_id, "version": GLOSS_ALIGNMENT_VERSION, "mode": GLOSS_ALIGNMENT_MODE_CORRECTED,
                       "final_status": status, "targets": [t["rank"] for t in targets],
                       "unresolved_ranks": gate["unresolved_ranks"], "mapping_gate": mapping_gate,
                       "rules_sha256": pf["sha256"], "cost_jpy": total_cost,
                       "attempts_detail": [{k: v for k, v in a.items() if k != "parsed"} for a in gate["attempts"]],
                       "item_log": {str(k): v for k, v in gate["item_log"].items()}}, f, ensure_ascii=False, indent=2)
    return {**base, "merged": new_merged, "status": status, "targets": [t["rank"] for t in targets],
            "attempts": gate["attempts"], "item_log": gate["item_log"], "unresolved_ranks": gate["unresolved_ranks"],
            "cost_jpy": total_cost, "fallback_event": None, "rules_sha256": pf["sha256"],
            "model_id": next((a.get("model") for a in gate["attempts"] if a.get("model")), None)}


# ---- 最終artifactに対するHuman Review報告(Lock/queue不使用) ---------------------
def collect_unresolved(kp_json: Any) -> list:
    """永続化済みartifact(keywords_canonicalized.json相当)から、Human Review待ちのitemを返す。
    消費側(TTS関所/stage_kp/assemble前チェック/HR報告)が共通に参照する唯一の関数。legacy artifactは常に[]。"""
    if not isinstance(kp_json, dict):
        return []
    return [it for it in (kp_json.get("items") or [])
            if isinstance(it, dict) and it.get("gloss_alignment_status") == STATUS_HR_REQUIRED]


def build_hr_entries(article_id: str, level: str, unresolved_items: list) -> list:
    entries = []
    for it in unresolved_items:
        info = it.get("gloss_alignment") or {}
        attempts = (info.get("failure") or {}).get("attempts") or []
        reasons = []
        for a in attempts:
            for rs in (a.get("reasons") or []):
                tag = f"attempt{a.get('attempt')}: {rs}"
                if tag not in reasons:
                    reasons.append(tag)
        if not reasons:
            reasons = ["再整合が上限回数で成立しなかった(詳細reasonなし)"]
        proposed = [{"attempt": a.get("attempt"), "proposed_gloss": a.get("proposed_gloss"),
                     "violations": a.get("reasons") or []} for a in attempts if a.get("proposed_gloss")]
        required = added_content_words(it.get("display_phrase"), it.get("key_phrase"))
        missing = []
        for a in attempts:
            for w in ((a.get("machine_check") or {}).get("uncovered") or []):
                if w not in missing:
                    missing.append(w)
        if not missing and not proposed:
            missing = list(required)
        entries.append({
            "article": article_id, "level": level, "rank": it.get("rank"),
            "key_phrase_en": it.get("key_phrase"),
            "current_japanese_gloss": info.get("original_japanese_gloss") or it.get("japanese_gloss"),
            "added_content_words": required,
            "failure_reasons": reasons,
            "attempts": attempts,
            "regeneration_candidates": {
                "proposed_glosses": proposed,
                "missing_words": missing,
                "reference_candidate": {"display_phrase": it.get("display_phrase"),
                                        "old_gloss": it.get("japanese_gloss"),
                                        "caution": HR_REFERENCE_CAUTION},
                "kp_regeneration": "既存経路でKey Phraseを再生成する(1レベル1回の運用上限に注意)。人間判断のみ。",
            },
            "resolution_how_to": "resolve_gloss(kp_json_path, rank, gloss, resolved_by) を実行(HR_RESOLVE_PROCEDURE_01.md)",
        })
    return entries


_HR_ENTRY_REQUIRED_STR = ("article", "level", "key_phrase_en", "current_japanese_gloss")


def validate_hr_report(path: str) -> list:
    """HR報告書を**ディスクから再読**し、必須項目が非空であることを検証する。問題のリストを返す(空=OK)。"""
    problems = []
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        return [f"読込失敗: {type(e).__name__}: {e}"]
    if not isinstance(doc, dict) or not doc.get("entries"):
        return ["entriesが空/欠落"]
    for i, e in enumerate(doc["entries"]):
        for k in _HR_ENTRY_REQUIRED_STR:
            if not (isinstance(e.get(k), str) and e[k].strip()):
                problems.append(f"entry{i}.{k}が空")
        if not isinstance(e.get("rank"), int):
            problems.append(f"entry{i}.rankが整数でない")
        for k in ("failure_reasons", "attempts"):
            if not (isinstance(e.get(k), list) and e[k]):
                problems.append(f"entry{i}.{k}が空")
        rc = e.get("regeneration_candidates")
        if not isinstance(rc, dict):
            problems.append(f"entry{i}.regeneration_candidatesが無い")
        else:
            for k in ("proposed_glosses", "missing_words", "reference_candidate", "kp_regeneration"):
                if k not in rc:
                    problems.append(f"entry{i}.regeneration_candidates.{k}が無い")
            ref = rc.get("reference_candidate")
            if isinstance(ref, dict) and not ref.get("caution"):
                problems.append(f"entry{i}.reference_candidate.cautionが空")
    return problems


def _render_hr_md(doc: dict) -> str:
    lines = ["# GLOSS_ALIGNMENT_HUMAN_REVIEW", "",
             f"article: {doc['article']} / level: {doc['level']} / generated_at: {doc['generated_at']}", "",
             "KP日本語glossの再整合が上限回数(item単位2回)で成立しませんでした。**対象levelのKP segment(日本語意味・B1解説)は"
             "TTSに進みません(0 API call)。正常完成としても扱われません。** 最終KPは短い候補へ戻していません。",
             "対応: 下の再生成候補から人間が判断し、`resolve_gloss`で確定するか、KPを再生成してください"
             "(手順: HR_RESOLVE_PROCEDURE_01.md)。", ""]
    for e in doc["entries"]:
        lines += [f"## rank {e['rank']}: {e['key_phrase_en']}", f"- 現在gloss: {e['current_japanese_gloss']}",
                  f"- 追加内容語: {e.get('added_content_words')}", "- 失敗理由:"]
        lines += [f"  - {r}" for r in e["failure_reasons"]]
        lines.append("- 試行結果:")
        for a in e["attempts"]:
            lines.append(f"  - attempt{a.get('attempt')}: verdict={a.get('verdict')} 提案gloss={a.get('proposed_gloss')!r} "
                         f"理由={a.get('reasons')}")
        rc = e["regeneration_candidates"]
        lines.append("- 再生成候補:")
        lines.append(f"  - 提案gloss: {[p['proposed_gloss'] for p in rc['proposed_glosses']]}")
        lines.append(f"  - 欠落語一覧: {rc['missing_words']}")
        ref = rc["reference_candidate"]
        lines.append(f"  - 参考: 候補表現={ref['display_phrase']!r} / 旧gloss={ref['old_gloss']!r} "
                     f"({ref['caution']})")
        lines.append(f"  - KP再生成: {rc['kp_regeneration']}")
        lines.append("")
    return "\n".join(lines)


def emit_human_review_notice(out_dir: str, article_id: str, level: str, kp_json: Any, print_fn: Optional[Callable] = None) -> Optional[dict]:
    """KP段の**最終artifact**に対して1回だけ呼ぶ(OF-KGDC-04)。unresolvedが無ければ古い報告書を除去してNone。
    あれば: 報告書(json+md)を書く -> その場で再読してスキーマ検証 -> 失敗なら例外(fail-closed) -> event生成 -> 専用stdout行。
    戻り値のeventを、呼出元がrun summaryへ載せる(条件②)。条件③(非OKのrun終了status)・④(下流停止)は呼出元と消費側が担う。"""
    unresolved = collect_unresolved(kp_json)
    jpath, mpath = os.path.join(out_dir, HR_REPORT_JSON), os.path.join(out_dir, HR_REPORT_MD)
    if not unresolved:
        for p in (jpath, mpath):
            if os.path.exists(p):
                os.remove(p)   # 最終artifactにunresolvedが無い=過去attempt/過去runの報告書は孤児(OF-KGDC-04)
        return None
    doc = {"report_version": HR_REPORT_VERSION, "article": article_id, "level": level,
           "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "entries": build_hr_entries(article_id, level, unresolved)}
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(jpath, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(_render_hr_md(doc))
        problems = validate_hr_report(jpath)
        if not os.path.exists(mpath) or os.path.getsize(mpath) == 0:
            problems.append("md報告書が空/欠落")
    except GlossAlignmentNotificationError:
        raise
    except Exception as e:
        raise GlossAlignmentNotificationError(f"HR報告書の書込失敗(fail-closed): {type(e).__name__}: {e}") from e
    if problems:
        raise GlossAlignmentNotificationError(f"HR報告書の再読検証に失敗(fail-closed): {problems}")
    with open(jpath, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    event = {"article": article_id, "level": level, "stage": "kp_gloss_alignment", "reason_code": HR_REASON_CODE,
             "reason": f"gloss再整合がitem単位の上限{MAX_GLOSS_ALIGNMENT_ATTEMPTS}回で成立しなかった"
                       f"(rank={[e['rank'] for e in doc['entries']]})。KPは維持・短い候補へ戻していない",
             "ranks": [e["rank"] for e in doc["entries"]], "report_json": jpath, "report_md": mpath,
             "report_sha256": sha, "report_schema_validated": True,
             "downstream": "当該levelのKP segmentはTTS保留(0 API call、status=" + STOPPED_STATUS + ")。Gateはassemblyを拒否。"
                           "ZはFamilyZE2EStopでstage停止",
             "queue_used": False, "human_review_lock_used": False}
    (print_fn or print)(format_hr_stdout([event]))
    return event


def format_hr_stdout(events: list) -> str:
    if not events:
        return "[GLOSS-ALIGN] Human Review待ちなし"
    ev = events[0] if len(events) == 1 else None
    if ev is not None:
        return (f"[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED] article={ev['article']} level={ev['level']} ranks={ev['ranks']} "
                f"gloss再整合が成立せず対象KP segmentのTTS/完成を停止します。報告書={ev['report_md']} "
                f"(ユーザーへ必ず報告してください)")
    return "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED] " + "; ".join(
        f"article={e['article']} level={e['level']} ranks={e['ranks']} 報告書={e['report_md']}" for e in events)


def resolve_gloss(kp_json_path: str, rank: int, gloss: str, resolved_by: str, now: Optional[str] = None) -> dict:
    """Human Review解消の唯一の手段(OF-KGDC-03)。人間が確定したglossを書き、gloss_alignment_status=HUMAN_RESOLVEDにする。
    承認規則由来の記号チェックを再利用し、違反なら書かずにGlossResolveRejectedを送出する。対象はHR待ち/解消済みitemのみ。"""
    if not isinstance(gloss, str) or not gloss.strip():
        raise GlossResolveRejected("glossが空")
    if not resolved_by or not str(resolved_by).strip():
        raise GlossResolveRejected("resolved_byが空")
    g = gloss.strip()
    bad = []
    if _PAREN_RE.search(g):
        bad.append("括弧禁止違反")
    if _ARABIC_DIGIT_RE.search(g):
        bad.append("算用数字禁止違反")
    if "…" in g:
        bad.append("…禁止違反")
    if safety.symbol_gate_requires_stop(
            [{**f, "rank": rank} for f in safety.detect_prohibited_symbols(kc.convert_display_gloss_to_tts_text(g), language="ja")]):
        bad.append("音声化禁止記号")
    if bad:
        raise GlossResolveRejected(f"gloss不正(書込まない): {bad}")
    with open(kp_json_path, encoding="utf-8") as f:
        doc = json.load(f)
    item = next((it for it in doc.get("items", []) if it.get("rank") == rank), None)
    if item is None:
        raise GlossResolveRejected(f"rank={rank}のitemが無い")
    if item.get("gloss_alignment_status") not in (STATUS_HR_REQUIRED, STATUS_HUMAN_RESOLVED):
        raise GlossResolveRejected(f"rank={rank}はHR待ちではない(status={item.get('gloss_alignment_status')!r})。書き換えない")
    prev = item.get("japanese_gloss")
    ts = now or datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    item["japanese_gloss"] = g
    item["japanese_gloss_tts"] = kc.convert_display_gloss_to_tts_text(g)
    item["gloss_alignment_status"] = STATUS_HUMAN_RESOLVED
    item["gloss_review_hint"] = False
    item["gloss_alignment_human_resolution"] = {"resolved_by": str(resolved_by), "resolved_at": ts, "previous_gloss": prev}
    if isinstance(item.get("gloss_alignment"), dict):
        item["gloss_alignment"]["status"] = "GLOSS_HUMAN_RESOLVED"
    if "gloss_alignment_unresolved" in doc:
        remain = [u for u in doc["gloss_alignment_unresolved"] if u.get("rank") != rank]
        if remain:
            doc["gloss_alignment_unresolved"] = remain
        else:
            del doc["gloss_alignment_unresolved"]
    tmp = kp_json_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    os.replace(tmp, kp_json_path)
    log_path = os.path.join(os.path.dirname(kp_json_path), "GLOSS_ALIGNMENT_HUMAN_RESOLUTIONS_01.jsonl")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"rank": rank, "key_phrase": item.get("key_phrase"), "previous_gloss": prev, "gloss": g,
                            "resolved_by": str(resolved_by), "resolved_at": ts}, ensure_ascii=False) + "\n")
    return item
