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

import difflib
import hashlib
import json
import os
import re
from typing import Any, Callable, Optional

import er003_audio_tts_asr_safety as safety
import er003_key_words_canonicalization as kc

GLOSS_ALIGNMENT_VERSION = "ER-003-KP-GLOSS-ALIGN-01"
MAX_GLOSS_ALIGNMENT_ATTEMPTS = 2
APPROVED_GLOSS_RULES_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt"
# OF-235: 明示flag(既定ON)。環境変数EIGO_KP_GLOSS_ALIGNMENT=0でOFF。align_glosses(enabled=...)で上書き可。
# 運用: ユーザー判断(Q1)までは新規量産runでこの段を通さない=運用側でOFFを指定する(OPEN-356)。
GLOSS_ALIGNMENT_ENABLED = os.environ.get("EIGO_KP_GLOSS_ALIGNMENT", "1") not in ("0", "false", "False", "off", "OFF")
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


def kp_adds_words_beyond_display(display_phrase: str, key_phrase: str) -> bool:
    """最終KPが表示候補(display_phrase)に無い語を含むか。活用形の違い(gave/give)・
    人称代名詞の一般化(their->one's)・冠詞の増減は『語の追加』に数えない。"""
    d = kc._normalize_for_match(display_phrase or "").replace("’", "'")
    k = kc._normalize_for_match(key_phrase or "").replace("’", "'")
    if not k or d == k:
        return False
    articles = {"a", "an", "the"}
    dset = {_stem(t) for t in _TOKEN_RE.findall(d)}
    kset = [t for t in _TOKEN_RE.findall(k) if t not in articles]
    def _near(t):
        return any(difflib.SequenceMatcher(None, _stem(t), x).ratio() >= 0.7 for x in dset)
    extra = [t for t in kset if t not in _GENERIC_TOKENS and _stem(t) not in dset and not _near(t)]
    return bool(extra)


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
                      reasoning_effort: str = "high", developer_message: str = DEVELOPER_MESSAGE):
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
            text={"format": {"type": "json_schema", **GLOSS_ALIGNMENT_JSON_SCHEMA}},
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
                  fallback_mode: Optional[str] = None) -> dict:
    """戻り値: {"merged": 更新後merged, "status": ..., "targets": [ranks], "attempts": [...]}。
    対象0件のときはAPI呼出なし・mergedは無変更(同一object)。enabled=False(flag OFF)なら status=DISABLED で無変更。"""
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
