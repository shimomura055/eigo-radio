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
# retry上限2。それでも整合できない場合は、人間確認へ送らず、自動で『KPを表示候補display_phraseへ戻す』
# (候補とglossは元々整合)。全経路(初回/redundancy retry/Strategy L fallback/regeneration)は
# run_key_phrase_canonicalization経由のため同じ工程を通る。
from __future__ import annotations

import difflib
import json
import re
from typing import Any, Callable, Optional

import er003_audio_tts_asr_safety as safety
import er003_key_words_canonicalization as kc

GLOSS_ALIGNMENT_VERSION = "ER-003-KP-GLOSS-ALIGN-01"
MAX_GLOSS_ALIGNMENT_ATTEMPTS = 2
APPROVED_GLOSS_RULES_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt"
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


def load_approved_gloss_rules(path: str = APPROVED_GLOSS_RULES_TEMPLATE_PATH) -> str:
    """承認済み選定Promptの『日本語グロス』規則の段落を実行時に抽出する(複製・改変しない)。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    paras = [p.strip() for p in text.split("\n\n") if p.strip().startswith("日本語グロス")]
    if len(paras) < 3:
        raise RuntimeError("承認済みgloss規則の抽出に失敗(段落数不足)")
    return "\n\n".join(paras)


def build_user_message(targets: list, article_text: str, rules: Optional[str] = None) -> str:
    rules = rules if rules is not None else load_approved_gloss_rules()
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
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise RuntimeError("gloss alignment応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    return fn


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
        if safety.symbol_gate_requires_stop(
                [{**f, "rank": r} for f in safety.detect_prohibited_symbols(kc.convert_display_gloss_to_tts_text(g), language="ja")]):
            reasons.append(f"rank{r}: 音声化禁止記号")
    return {"ok": not reasons, "reasons": reasons, "by_rank": by_rank}


def run_alignment_gate(make_factory: Callable[[], Callable], targets: list,
                       max_attempts: int = MAX_GLOSS_ALIGNMENT_ATTEMPTS):
    attempts = []
    for attempt in range(1, max_attempts + 1):
        fn = make_factory()
        try:
            raw, model_id, response_id = fn()
        except Exception as e:  # 技術的失敗も同じ上限の中でretry
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            continue
        try:
            parsed = json.loads(raw)
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "PARSE_FAILED", "error": str(e), "model": model_id})
            continue
        v = validate_alignment_response(parsed, targets)
        attempts.append({"attempt": attempt, "status": "ALIGN_PASS" if v["ok"] else "ALIGN_INVALID",
                         "reasons": v["reasons"], "parsed": parsed, "model": model_id, "response_id": response_id})
        if v["ok"]:
            return v["by_rank"], "ALIGN_PASS", attempts, model_id, response_id
    return None, "ALIGN_FAILED", attempts, None, None


def apply_alignment(merged: dict, by_rank: Optional[dict], targets: list) -> dict:
    """merged(merge_canonicalization_result出力)へ結果を適用する(新しいdictを返す)。
    by_rank=Noneはretry上限でも整合できなかった場合: KPを表示候補へ自動で戻す(候補とglossは元々整合)。"""
    target_ranks = {t["rank"] for t in targets}
    items = []
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
        else:
            reverted = it.get("display_phrase")
            new["gloss_alignment"] = {
                "version": GLOSS_ALIGNMENT_VERSION, "status": "FALLBACK_KP_REVERTED_TO_DISPLAY_PHRASE",
                "original_japanese_gloss": orig_gloss, "key_phrase_before_revert": it["key_phrase"],
            }
            new["key_phrase"] = reverted
            new["used_form"] = reverted
            new["changed_from_display_phrase"] = False
            new["kp_extends_beyond_candidate"] = False
        new["gloss_review_hint"] = False
        items.append(new)
    out = dict(merged)
    out["items"] = items
    return out


def align_glosses(merged: dict, article_text: str, make_factory_for: Callable[[str], Callable],
                  out_dir: Optional[str] = None, article_id: str = "") -> dict:
    """戻り値: {"merged": 更新後merged, "status": ..., "targets": [ranks], "attempts": [...]}。
    対象0件のときはAPI呼出なし・mergedは無変更(同一object)。"""
    targets = select_alignment_targets(merged["items"])
    if not targets:
        return {"merged": merged, "status": "NO_TARGETS", "targets": [], "attempts": []}
    user_message = build_user_message(targets, article_text)
    by_rank, status, attempts, model_id, response_id = run_alignment_gate(
        lambda: make_factory_for(user_message), targets)
    new_merged = apply_alignment(merged, by_rank, targets)
    if out_dir:
        with open(f"{out_dir}/gloss_alignment_prompt.txt", "w", encoding="utf-8") as f:
            f.write(user_message)
        with open(f"{out_dir}/gloss_alignment_runtime_metadata.json", "w", encoding="utf-8") as f:
            json.dump({"article_id": article_id, "version": GLOSS_ALIGNMENT_VERSION, "final_status": status,
                       "model_id": model_id, "response_id": response_id, "targets": [t["rank"] for t in targets],
                       "attempts_detail": attempts}, f, ensure_ascii=False, indent=2)
    return {"merged": new_merged, "status": status, "targets": [t["rank"] for t in targets],
            "attempts": attempts, "model_id": model_id}
