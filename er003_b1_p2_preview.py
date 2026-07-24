# ============================================================
# er003_b1_p2_preview.py
# ER-003-B1-P2 Part B: 統合Listening Preview 3案生成
# ============================================================
# Part A(er003_b1_p2_keywords.py)で固定したA01 B1 Key Words 5件を、
# 承認済みA01 B1本文へ日本語中心で織り込んだListening Previewを、
# 役割の異なる3パターン(A/B/C)、1回のAPI呼び出しで生成する。
#
# B2本文・日本語マスター・Natural English Sourceは入力へ一切含めない。
# B1本文だけを内容のsource of truthとする。自動再生成・人手修正は行わ
# ない。形式違反があっても再生成せず、結果を記録してユーザーへ提示する。

from __future__ import annotations

import json
import re
from typing import Any, Optional

import er003_key_words_min_unit as p2g
import er003_key_words_production as prod
import er003_ja_to_en_translation as er003

PREVIEW_MODEL = prod.SELECTOR_MODEL  # "gpt-5.6-sol"(既存production selectorと同一)
PREVIEW_REASONING_EFFORT = prod.SELECTOR_REASONING_EFFORT  # "high"
PREVIEW_DEVELOPER_MESSAGE = "日本語中心のListening Previewを3案作成してください。"

PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_listening_preview_prompt_template.txt"

PATTERN_IDS = ("A", "B", "C")
MIN_SENTENCE_COUNT = 3
MAX_SENTENCE_COUNT = 4

# 本文にない事実の判断・自然さ・スポイラー有無の最終確認は、既存の
# hard requirement判定と同じ原則で機械チェックが不十分な部分のみ
# Claude Codeが目視で行う(追加API呼び出しはしない、B1-P1の忠実性
# レビューと同じ扱い)。ここではA01の実スコアに限定した具体的な
# 数字パターンだけを機械的に検出する。
_SCORE_PATTERNS = ("1–2", "1-2", "2–1", "2-1", "final score")
_WINNER_WORDS = ("won", "winner", "victory", "beat ")

_JAPANESE_CHAR_RE = p2g._JAPANESE_CHAR_RE

# Previewは日本語主体の文章のため、英語専用のer003.split_sentences
# (ピリオド等ASCII終端記号のみ対応)は使わず、日本語・英語双方の文末
# 記号をまとめて数える軽量な文数カウンタをここだけで使う(新しい文分割
# 基盤は作らない、あくまで件数を数えるだけの最小限の実装)。
_SENTENCE_BOUNDARY_RE = re.compile(r"[。！？.!?]+")


def _count_sentences_ja_en(text: str) -> int:
    return len(_SENTENCE_BOUNDARY_RE.findall(text))

# ============================================================
# ブロック1: prompt構築
# ============================================================
def load_prompt_template(path: str = PROMPT_TEMPLATE_PATH) -> str:
    return er003.restore.load_text_file(path)


def build_keywords_block(selected_json: dict) -> str:
    lines = []
    for item in sorted(selected_json["items"], key=lambda it: it["rank"]):
        lines.append(
            f"{item['rank']}. {item['canonical_english']} ({item['japanese_gloss']}) "
            f"— source: {item['source_evidence']}"
        )
    return "\n".join(lines)


def build_preview_user_message(selected_json: dict, approved_b1_article: str,
                                template: Optional[str] = None) -> str:
    template = template if template is not None else load_prompt_template()
    keywords_block = build_keywords_block(selected_json)
    return template.replace("{keywords_block}", keywords_block).replace(
        "{approved_b1_article}", approved_b1_article)


# ============================================================
# ブロック2: Structured Output schema・単発API呼び出し(gateなし)
# ============================================================
PREVIEW_JSON_SCHEMA = {
    "name": "b1_listening_preview_three_patterns",
    "schema": {
        "type": "object",
        "properties": {
            "patterns": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "pattern_id": {"type": "string", "enum": list(PATTERN_IDS)},
                        "text": {"type": "string"},
                        "used_forms": {
                            "type": "array",
                            "minItems": 5,
                            "maxItems": 5,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "rank": {"type": "integer"},
                                    "canonical_english": {"type": "string"},
                                    "used_form": {"type": "string"},
                                    "japanese_gloss_used": {"type": "string"},
                                },
                                "required": ["rank", "canonical_english", "used_form", "japanese_gloss_used"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["pattern_id", "text", "used_forms"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["patterns"],
        "additionalProperties": False,
    },
    "strict": True,
}


class PreviewModelMismatchError(RuntimeError):
    """API応答のmodelフィールドが指定モデルと一致しない場合。"""


def make_preview_fn(
    user_message: str,
    client: Optional[Any] = None,
    model: str = PREVIEW_MODEL,
    reasoning_effort: str = PREVIEW_REASONING_EFFORT,
    developer_message: str = PREVIEW_DEVELOPER_MESSAGE,
):
    """単発呼び出し(gateに包まない)。自動再生成しないため。"""
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **PREVIEW_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise PreviewModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise er003.restore.GenerationEmptyOrBrokenError("Preview応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    fn.uses_web_search_tool = False
    fn.uses_structured_output = True
    return fn


def parse_preview_json(raw_text: str) -> dict:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise er003.QaSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict) or "patterns" not in parsed:
        raise er003.QaSchemaError("'patterns'フィールドがありません")
    if len(parsed["patterns"]) != 3:
        raise er003.QaSchemaError(f"patternsが3件でありません(実際: {len(parsed['patterns'])}件)")
    return parsed


# ============================================================
# ブロック3: 最小限の機械確認(自動再生成のトリガーにはしない)
# ============================================================
def _count_occurrences(needle: str, haystack: str) -> int:
    if not needle:
        return 0
    return len(re.findall(re.escape(needle), haystack, flags=re.IGNORECASE))


def check_pattern_machine(pattern: dict, selected_ranks: list, b1_article_text: str) -> dict:
    text = pattern.get("text", "") or ""
    used_forms = pattern.get("used_forms", []) or []

    checks = {}
    checks["pattern_id_valid"] = pattern.get("pattern_id") in PATTERN_IDS

    plain = er003.article_gen.strip_markdown_symbols(text)
    sentence_count = _count_sentences_ja_en(plain)
    checks["sentence_count"] = sentence_count
    checks["sentence_count_in_3_to_4"] = MIN_SENTENCE_COUNT <= sentence_count <= MAX_SENTENCE_COUNT

    checks["exactly_5_used_forms"] = len(used_forms) == 5
    checks["all_5_ranks_present"] = sorted(uf.get("rank") for uf in used_forms) == sorted(selected_ranks)

    per_item = []
    for uf in used_forms:
        used_form = uf.get("used_form", "") or ""
        gloss = uf.get("japanese_gloss_used", "") or ""
        occurrence_count = _count_occurrences(used_form, text)
        used_form_idx = text.lower().find(used_form.lower()) if used_form else -1
        gloss_idx = text.find(gloss) if gloss else -1
        if gloss_idx == -1 or used_form_idx == -1:
            ja_before_en = "UNVERIFIABLE"
        elif gloss_idx < used_form_idx:
            ja_before_en = "PASS"
        else:
            ja_before_en = "FAIL"
        per_item.append({
            "rank": uf.get("rank"),
            "canonical_english": uf.get("canonical_english"),
            "used_form": used_form,
            "japanese_gloss_used": gloss,
            "used_form_occurrence_count": occurrence_count,
            "used_form_occurs_exactly_once": occurrence_count == 1,
            "japanese_before_english": ja_before_en,
        })
    checks["per_item"] = per_item
    checks["all_used_forms_occur_exactly_once"] = all(it["used_form_occurs_exactly_once"] for it in per_item)
    checks["all_japanese_before_english_pass_or_unverifiable"] = all(
        it["japanese_before_english"] != "FAIL" for it in per_item)

    lowered = text.lower()
    checks["no_explicit_score_pattern"] = not any(p in lowered or p in text for p in _SCORE_PATTERNS)
    checks["no_winner_language_detected"] = not any(w in lowered for w in _WINNER_WORDS)

    checks["has_japanese_content"] = bool(_JAPANESE_CHAR_RE.search(text))

    status = "ALL_CHECKS_PASS" if (
        checks["pattern_id_valid"] and checks["sentence_count_in_3_to_4"] and checks["exactly_5_used_forms"]
        and checks["all_5_ranks_present"] and checks["all_used_forms_occur_exactly_once"]
        and checks["all_japanese_before_english_pass_or_unverifiable"] and checks["no_explicit_score_pattern"]
        and checks["no_winner_language_detected"] and checks["has_japanese_content"]
    ) else "SOME_CHECKS_FAILED"

    return {"status": status, "checks": checks}


def run_preview_machine_checks(parsed: dict, selected_ranks: list, b1_article_text: str) -> dict:
    patterns = parsed["patterns"]
    per_pattern = {
        p["pattern_id"]: check_pattern_machine(p, selected_ranks, b1_article_text) for p in patterns
    }
    overall = "ALL_CHECKS_PASS" if all(r["status"] == "ALL_CHECKS_PASS" for r in per_pattern.values()) \
        else "SOME_CHECKS_FAILED"
    return {
        "status": overall,
        "pattern_count": len(patterns),
        "pattern_ids_present": sorted(p["pattern_id"] for p in patterns),
        "per_pattern": per_pattern,
    }


# ============================================================
# ブロック4: ユーザー比較用markdown(section 12の形式をそのまま使う)
# ============================================================
_PATTERN_LABELS = {
    "A": "Pattern A — Story / Drama",
    "B": "Pattern B — Comprehension / Structure",
    "C": "Pattern C — Keyword Salience",
}


def build_candidates_markdown(parsed: dict) -> str:
    by_id = {p["pattern_id"]: p for p in parsed["patterns"]}
    lines = []
    for pattern_id in PATTERN_IDS:
        lines.append(f"## {_PATTERN_LABELS[pattern_id]}")
        lines.append("")
        lines.append(by_id[pattern_id]["text"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
