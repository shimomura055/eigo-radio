# ============================================================
# er011_key_phrase_set_redundancy_qa_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Key Phrase 5件相互の意味重複QA
# ============================================================
# 背景: No.18 B1で「catch their attention」「a piece of your attention」という、
# 文字列は異なるが「注意を引く/注意の一部を奪う」という近い意味・学習目的
# の表現が両方選ばれた。既存QA(er003_key_words_canonicalization.py)は
# 各候補を個別にsource_span/display_phraseとの関係でのみ検証しており、
# 5件相互の重複は一度も評価されていなかった(選定プロンプトの優先順位
# 「汎用性」は最後の基準であり、候補同士の比較は行わない)。
#
# 本モジュールは、canonicalization完了後の5件(最終的な学習教材としての
# key_phrase・japanese_gloss・元文脈)を対象に、以下4観点での相互重複を
# LLMで判定する新規QA工程を追加する:
#   - 意味 (meaning)
#   - 使用場面 (usage_context)
#   - 文法・構文上の学習価値 (grammatical_teaching_value)
#   - 記事内で担う概念 (conceptual_role)
#
# 単なる言い換え・同じ内容を別の比喩で表しただけの候補ペアがあればNGとし、
# 呼び出し側(er003_v1_n3_01_scaffold_generate.py::run_key_phrases)が
# Key Phrase選定(方式L)からやり直す。記事本文はこの工程の対象外であり、
# 記事全体の再生成は行わない(Point Overlap QAとは異なる独立した後段
# 工程のため)。

from __future__ import annotations

import itertools
import json
from typing import Any, Callable, Optional

REDUNDANCY_QA_VERSION = "ER-011-KP-REDUNDANCY-01"

DEVELOPER_MESSAGE = (
    "英語学習ポッドキャストのKey Phrase 5件が、互いに意味・使用場面・"
    "文法/構文上の学習価値・記事内で担う概念のいずれかの観点で、実質的に"
    "同じ内容の言い換えになっていないかを判定してください。"
)

REDUNDANCY_QA_JSON_SCHEMA = {
    "name": "key_phrase_set_redundancy_qa",
    "schema": {
        "type": "object",
        "properties": {
            "pairs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rank_a": {"type": "integer"},
                        "rank_b": {"type": "integer"},
                        "meaning_overlap": {"type": "string", "enum": ["PASS", "FAIL"]},
                        "usage_context_overlap": {"type": "string", "enum": ["PASS", "FAIL"]},
                        "grammatical_teaching_value_overlap": {"type": "string", "enum": ["PASS", "FAIL"]},
                        "conceptual_role_overlap": {"type": "string", "enum": ["PASS", "FAIL"]},
                        "is_near_duplicate": {"type": "boolean"},
                        "reasoning": {"type": "string"},
                    },
                    "required": [
                        "rank_a", "rank_b", "meaning_overlap", "usage_context_overlap",
                        "grammatical_teaching_value_overlap", "conceptual_role_overlap",
                        "is_near_duplicate", "reasoning",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["pairs"],
        "additionalProperties": False,
    },
    "strict": True,
}

PROMPT_TEMPLATE = """以下は、同じ記事から選ばれた{num_items}件のKey Phrase(英語学習ポッドキャストの
リスニング教材)です。{num_items}件から作れる全てのペア({num_pairs}組)について、
それぞれ以下4つの観点で意味重複を判定してください(それぞれPASS=重複なし/
FAIL=重複あり)。

- meaning_overlap: 2つのkey_phraseが表す意味内容が、実質的に同じか(例:
  「注意を引く」と「注意の一部を奪う」は表現は違っても同じ「注意を奪われる」
  という概念を指しており、meaning_overlap=FAILとすべきです)
- usage_context_overlap: 2つの表現が使われる典型的な場面・文脈が、実質的に
  同じか
- grammatical_teaching_value_overlap: 2つの表現が学習者に教える文法・構文上の
  価値(例: 句動詞の型、比喩の型、コロケーションの型)が、実質的に同じか
- conceptual_role_overlap: 記事の中でこの2つの表現が担っている概念・役割が、
  実質的に同じか

is_near_duplicateは、上記4観点のうち2つ以上がFAILの場合、または1つでも
明確にFAILで「単なる言い換え、または同じ内容を別の比喩・表現で表しただけ」
と判断できる場合にtrueにしてください。reasoningには判定理由を1〜2文の
日本語で書いてください。

単に同じ記事・同じ話題について書かれているために表面的な語彙(記事固有の
固有名詞やトピック語)が共通することは、重複とはみなさないでください。
判定対象はあくまで、Key Phraseそのものが教える意味・用法・学習価値です。

pairsには、必ず{num_pairs}組全ての組み合わせを含めてください(rank_a < rank_b)。

【記事本文(参考、文脈確認用)】
{article_text}

【Key Phrase {num_items}件(JSON)】
{items_json}
"""


def _expected_pairs(ranks: list) -> set:
    return {(a, b) for a, b in itertools.combinations(sorted(ranks), 2)}


def build_user_message(merged_items: list, article_text: str, template: Optional[str] = None) -> str:
    template = template if template is not None else PROMPT_TEMPLATE
    items_for_prompt = [
        {"rank": it["rank"], "key_phrase": it["key_phrase"], "japanese_gloss": it.get("japanese_gloss"),
         "source_sentence": it.get("source_sentence", "")}
        for it in merged_items
    ]
    ranks = sorted(it["rank"] for it in merged_items)
    num_items = len(ranks)
    num_pairs = num_items * (num_items - 1) // 2
    return template.format(
        num_items=num_items, num_pairs=num_pairs, article_text=article_text,
        items_json=json.dumps(items_for_prompt, ensure_ascii=False, indent=2),
    )


class RedundancyQaModelMismatchError(RuntimeError):
    """API応答のmodelフィールドが指定モデルと一致しない場合。技術的失敗として扱う。"""


def make_redundancy_qa_fn(user_message: str, client: Optional[Any] = None, model: str = None,
                           reasoning_effort: str = "high", developer_message: str = DEVELOPER_MESSAGE):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()
    if model is None:
        raise ValueError("modelは明示的に指定してください(SSOT経由のrouting.require_model())")

    def fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **REDUNDANCY_QA_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        if response.model != model:
            raise RedundancyQaModelMismatchError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise RuntimeError("redundancy QA応答が空です")
        return text, response.model, response.id

    fn.model = model
    fn.reasoning_effort = reasoning_effort
    return fn


def validate_redundancy_response(parsed: dict, ranks: list) -> dict:
    """全ペアが揃っているか(構造)と、is_near_duplicate=trueのペアが
    あるかどうか(内容)を検査する。戻り値のstatusは3状態:
      - REDUNDANCY_INVALID: 構造不適合(ペア不足・重複・不正な値)
      - REDUNDANCY_NG: 構造は正しいが、is_near_duplicate=trueのペアが1件以上ある
      - REDUNDANCY_PASS: 構造正しく、near_duplicateなし
    """
    if not isinstance(parsed, dict) or not isinstance(parsed.get("pairs"), list):
        return {"status": "REDUNDANCY_INVALID", "reasons": ["'pairs'が配列でない"], "duplicate_pairs": []}

    expected = _expected_pairs(ranks)
    seen = set()
    reasons = []
    duplicate_pairs = []
    for i, pair in enumerate(parsed["pairs"]):
        if not isinstance(pair, dict):
            reasons.append(f"pairs[{i}]がオブジェクトでない")
            continue
        key = (pair.get("rank_a"), pair.get("rank_b"))
        normalized_key = tuple(sorted(k for k in key if k is not None)) if None not in key else key
        if key not in expected and normalized_key not in expected:
            reasons.append(f"pairs[{i}]のrank_a/rank_b({key})が期待される組み合わせにない")
            continue
        canonical_key = key if key in expected else normalized_key
        if canonical_key in seen:
            reasons.append(f"pairs[{i}]のrank_a/rank_b({key})が重複している")
            continue
        seen.add(canonical_key)
        for field in ("meaning_overlap", "usage_context_overlap",
                      "grammatical_teaching_value_overlap", "conceptual_role_overlap"):
            if pair.get(field) not in ("PASS", "FAIL"):
                reasons.append(f"pairs[{i}].{field}が不正(実際: {pair.get(field)!r})")
        if not isinstance(pair.get("is_near_duplicate"), bool):
            reasons.append(f"pairs[{i}].is_near_duplicateがbooleanでない")
        elif pair["is_near_duplicate"]:
            duplicate_pairs.append({
                "rank_a": key[0], "rank_b": key[1],
                "meaning_overlap": pair.get("meaning_overlap"),
                "usage_context_overlap": pair.get("usage_context_overlap"),
                "grammatical_teaching_value_overlap": pair.get("grammatical_teaching_value_overlap"),
                "conceptual_role_overlap": pair.get("conceptual_role_overlap"),
                "reasoning": pair.get("reasoning"),
            })

    missing = expected - seen
    if missing:
        reasons.append(f"評価されていない組み合わせがある: {sorted(missing)}")

    if reasons:
        return {"status": "REDUNDANCY_INVALID", "reasons": reasons, "duplicate_pairs": duplicate_pairs}
    if duplicate_pairs:
        return {"status": "REDUNDANCY_NG", "reasons": [], "duplicate_pairs": duplicate_pairs}
    return {"status": "REDUNDANCY_PASS", "reasons": [], "duplicate_pairs": []}


MAX_REDUNDANCY_QA_TECHNICAL_RETRY_ATTEMPTS = 2  # 初回 + 技術的失敗/構造不適合時の再試行1回のみ


def run_redundancy_qa_gate(make_factory: Callable[[], Callable], ranks: list,
                            max_attempts: int = MAX_REDUNDANCY_QA_TECHNICAL_RETRY_ATTEMPTS,
                            sleep_fn: Optional[Callable[[float], None]] = None):
    """技術的失敗・構造不適合時のみ同一条件で最大1回再試行する
    (is_near_duplicate=trueという内容判断自体はそのまま採用し、
    再試行しない。呼び出し側がKey Phrase選定からのやり直しを判断する)。"""
    attempts_detail = []
    for attempt in range(1, max_attempts + 1):
        fn = make_factory()
        try:
            raw_text, model_id, response_id = fn()
        except Exception as e:
            attempts_detail.append({
                "attempt": attempt, "status": "TECHNICAL_GENERATION_FAILED",
                "error": f"{type(e).__name__}: {e}",
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None

        try:
            parsed = json.loads(raw_text)
        except (json.JSONDecodeError, TypeError) as e:
            attempts_detail.append({
                "attempt": attempt, "status": "PARSE_FAILED", "error": str(e),
                "model": model_id, "response_id": response_id,
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "PARSE_FAILED", attempts_detail, model_id, response_id

        validation = validate_redundancy_response(parsed, ranks)
        attempts_detail.append({
            "attempt": attempt, "status": validation["status"], "reasons": validation["reasons"],
            "duplicate_pairs": validation["duplicate_pairs"], "raw_text": raw_text, "parsed": parsed,
            "model": model_id, "response_id": response_id,
        })
        if validation["status"] in ("REDUNDANCY_PASS", "REDUNDANCY_NG"):
            return parsed, validation["status"], attempts_detail, model_id, response_id
        if attempt < max_attempts:
            continue
        return parsed, "REDUNDANCY_INVALID", attempts_detail, model_id, response_id

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None


def build_redundancy_diagnostic_note(duplicate_pairs: list, items_by_rank: dict) -> str:
    """Key Phrase選定retry時にprompt末尾へ追加する診断メモ(日本語)。
    どの概念が重複と判定されたかを名指しし、同じ概念の候補を再選定しない
    よう選定モデルへ伝える(記事固有のハードコードではなく、直前の
    判定結果をそのまま渡すだけの一般的な仕組み)。"""
    lines = ["【前回の選定で、以下のペアが意味・用法上の重複と判定されました。今回は同じ概念を"
             "指す表現を2件以上選ばないでください】"]
    for dup in duplicate_pairs:
        a = items_by_rank.get(dup["rank_a"], {})
        b = items_by_rank.get(dup["rank_b"], {})
        lines.append(
            f"- {a.get('key_phrase', a.get('display_phrase', '?'))!r} と "
            f"{b.get('key_phrase', b.get('display_phrase', '?'))!r}: {dup.get('reasoning', '')}")
    return "\n".join(lines)
