# ============================================================
# er002_ja_master_imitation.py
# ER-002-v1.2M-JA: 阪神日本語マスター模倣方式(最小指示型)
# ============================================================
# ER-002-v1.1A/v1.1B(編集アングル生成→採点→Editorial Brief→編集品質QA
# ゲート)のようなルール・スコア中心の編集工程を一切使わない、別方式。
#
# 方針: Master-first / Minimal instruction / Guardrail-later。
# 面白さ・勢い・アングル・Pointの価値は人間が最終評価する。このモジュールが
# 機械的に検出するのは「明確な事故」(事実矛盾・必須構造欠落・API応答破損)
# だけであり、narrative qualityの自動合否や内容不満による再生成は行わない。
#
# このモジュールは以下を一切importしない(ER-002-v1.2M-P0の指示どおり、
# 旧ルール中心編集工程と明確に分離する):
#   - er002_editorial_common.py
#   - er002_editorial_angle_adapter.py
#   - er002_editorial_runner.py
# 編集判断を含まない基盤機能(共通API呼び出し・ハッシュ・QA通信リトライ等)は
# er002_common.py / er002_script_adapter.py(モデル名定数のみ)から再利用する。
#
# このモジュール自体は実APIを一切呼び出さない(呼び出し関数は引数として
# 注入される。ER-002-v1.2M-P0ではモックのみで検証する)。

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from dotenv import load_dotenv

import er002_common as common
import er002_script_adapter as script_adapter  # MODEL_WRITE定数の再利用のみ(台本生成ロジックは使わない)

EXPERIMENT_VERSION = "ER-002-v1.2M-JA"
BASE_EXPERIMENT_VERSION = "ER-002-v1.1B"  # 比較対象。旧ルール中心工程はv1.1B-CLOSEで終了

MASTERS_DIR = "er002_v1_2m_masters"
HANSHIN_MASTER_PATH = f"{MASTERS_DIR}/hanshin_ja_master.txt"
ORIGINAL_REQUEST_PATH = f"{MASTERS_DIR}/original_request.txt"
MASTERS_SHA256_PATH = f"{MASTERS_DIR}/masters_sha256.json"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ============================================================
# ブロック1: 事実ID(er002_editorial_common.assign_fact_idsとは独立実装。
# 新方式は編集系モジュールを一切importしない方針のため、小さな関数を
# ここで再定義する)
# ============================================================
def assign_fact_ids(verified_facts: list[str]) -> dict[str, str]:
    return {f"F{i + 1:02d}": fact for i, fact in enumerate(verified_facts)}


def build_facts_block(fact_id_map: dict) -> str:
    return "\n".join(f"{fid}: {text}" for fid, text in fact_id_map.items())


# ============================================================
# ブロック2: マスター・依頼文の読み込みとsha256照合(fail-closed)
# ============================================================
class MasterIntegrityError(RuntimeError):
    """マスター・依頼文のsha256が凍結値と一致しない場合に送出する。
    呼び出し側はこの例外を捕捉したら実APIを一切呼ばずに停止すること。"""


def load_and_verify_masters(masters_sha256_path: str = MASTERS_SHA256_PATH) -> dict:
    with open(masters_sha256_path, encoding="utf-8") as f:
        frozen = json.load(f)

    with open(frozen["hanshin_ja_master_path"], "rb") as f:
        master_bytes = f.read()
    actual_master_sha256 = sha256_bytes(master_bytes)
    if actual_master_sha256 != frozen["hanshin_ja_master_sha256"]:
        raise MasterIntegrityError(
            "阪神マスターのsha256が凍結値と一致しません"
            f"(actual={actual_master_sha256}, expected={frozen['hanshin_ja_master_sha256']})。"
            "APIを呼ばずに停止してください。"
        )

    with open(frozen["original_request_path"], "rb") as f:
        request_bytes = f.read()
    actual_request_sha256 = sha256_bytes(request_bytes)
    if actual_request_sha256 != frozen["original_request_sha256"]:
        raise MasterIntegrityError(
            "依頼文のsha256が凍結値と一致しません"
            f"(actual={actual_request_sha256}, expected={frozen['original_request_sha256']})。"
            "APIを呼ばずに停止してください。"
        )

    return {
        "master_full_text": master_bytes.decode("utf-8"),
        "master_sha256": actual_master_sha256,
        # 証跡としてのみ保持する。プロンプトへは使わない(過去6トピック一覧の混入防止)。
        "original_request_full_text": request_bytes.decode("utf-8"),
        "original_request_sha256": actual_request_sha256,
    }


# ============================================================
# ブロック3: 最小生成プロンプト
# ============================================================
# 依頼文全文から動的に抽出しない。過去6トピック一覧・過去記事本文の混入を
# 防ぐため、プロンプトで使う評価理由は固定文言としてここへ書き出す
# (依頼文の該当部分の引き写しであり、依頼文自体を解析するロジックは
# 実装しない)。
EVALUATION_REASONS = [
    "全体の概要を面白く展開",
    "今日の虎ポイントで、別切口でも解説",
    "一言で表すなら、でサマリー",
    "聞き手があきない設計",
]


def build_evaluation_reasons_block() -> str:
    return "\n".join(f"- {r}" for r in EVALUATION_REASONS)


PROMPT_VERSION = "er002-ja-master-imitation-v1"

MINIMAL_JA_GENERATION_PROMPT_TEMPLATE = """以下は、承認済みの記事(マスター)です。この記事の文体・語り口・構成の作り方を参考にして、新しい記事を1本書いてください。マスターの題材(阪神・野球)やマスター内の具体的な比喩・表現をそのまま使い回さないでください(今回は別のトピックです)。

【マスター記事】
{master_full_text}

【マスターが評価された理由】
{evaluation_reasons_block}

【今回の対象記事の確認済み事実】
{facts_block}

【今回のトピック】
{target_topic}

【指示】
阪神固有の表現や野球の比喩をコピーするのではなく、記事全体の編集センスを今回の題材へ応用してください。全体の概要を面白く展開し、二つのポイントでは本文とは別の切り口を加え、一言で印象的にまとめてください。確認済み事実にない具体的内容を推測で加えないでください。"""


def build_prompt(master_full_text: str, target_topic: str, fact_id_map: dict) -> str:
    return MINIMAL_JA_GENERATION_PROMPT_TEMPLATE.format(
        master_full_text=master_full_text,
        evaluation_reasons_block=build_evaluation_reasons_block(),
        facts_block=build_facts_block(fact_id_map),
        target_topic=target_topic,
    )


# structured outputが使えない場合にのみ追加する、JSON形状の指定だけの
# 最小指示(編集上の指示とは分離し、創作プロンプト本文には含めない)。
MINIMAL_JSON_SHAPE_FALLBACK_INSTRUCTION = """Return ONLY valid JSON, no other text, in exactly this shape:
{"title": "...", "body": ["...", "..."], "point_one": {"heading": "...", "paragraphs": ["...", "..."]}, "point_two": {"heading": "...", "paragraphs": ["...", "..."]}, "one_line_summary": "..."}"""


# ============================================================
# ブロック4: structured output スキーマ
# ============================================================
JA_ARTICLE_JSON_SCHEMA = {
    "name": "ja_master_imitation_article",
    "schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "body": {"type": "array", "items": {"type": "string"}},
            "point_one": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "paragraphs": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["heading", "paragraphs"],
                "additionalProperties": False,
            },
            "point_two": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "paragraphs": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["heading", "paragraphs"],
                "additionalProperties": False,
            },
            "one_line_summary": {"type": "string"},
        },
        "required": ["title", "body", "point_one", "point_two", "one_line_summary"],
        "additionalProperties": False,
    },
    "strict": True,
}


class GenerationParseError(ValueError):
    pass


def parse_ja_article_json(raw_text: Optional[str]) -> dict:
    if not raw_text:
        raise GenerationParseError("生成応答が空です")
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        raise GenerationParseError(f"生成応答のJSON解析に失敗しました: {e}")


def make_ja_article_generation_fn(
    target_topic: str,
    fact_id_map: dict,
    master_full_text: str,
    client: Optional[Any] = None,
    use_structured_output: bool = True,
):
    """generation_fn(config: dict) -> dict を返す。既存の台本生成アダプター
    (er002_script_adapter)と同じ責務分離(呼び出し関数へprompt_text/
    prompt_sha256を属性として付与)を踏襲するが、Editorial Brief等は一切
    受け取らない(編集判断を含まない、記事1件分の最小入力のみ)。"""
    if client is None:
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    prompt = build_prompt(master_full_text, target_topic, fact_id_map)
    prompt_sha256 = sha256_text(prompt)
    effective_prompt = prompt if use_structured_output else (
        prompt + "\n\n" + MINIMAL_JSON_SHAPE_FALLBACK_INSTRUCTION
    )

    def generation_fn(config: dict) -> dict:
        if use_structured_output:
            response = client.chat.completions.create(
                model=script_adapter.MODEL_WRITE,
                messages=[{"role": "user", "content": effective_prompt}],
                response_format={"type": "json_schema", "json_schema": JA_ARTICLE_JSON_SCHEMA},
            )
        else:
            response = client.chat.completions.create(
                model=script_adapter.MODEL_WRITE,
                messages=[{"role": "user", "content": effective_prompt}],
                response_format={"type": "json_object"},
            )
        return parse_ja_article_json(response.choices[0].message.content)

    generation_fn.prompt_text = effective_prompt
    generation_fn.prompt_sha256 = sha256_text(effective_prompt)
    generation_fn.prompt_version = PROMPT_VERSION
    generation_fn.model = script_adapter.MODEL_WRITE
    generation_fn.experiment_version = EXPERIMENT_VERSION
    generation_fn.use_structured_output = use_structured_output
    return generation_fn


# ============================================================
# ブロック5: 最小構造検証(コードのみ、LLM不要。面白さは一切判定しない)
# ============================================================
REQUIRED_ARTICLE_FIELDS = ["title", "body", "point_one", "point_two", "one_line_summary"]


class StructuralValidationError(ValueError):
    pass


def validate_structure(result: Any) -> dict:
    if not isinstance(result, dict):
        raise StructuralValidationError("応答がJSONオブジェクトではありません")

    missing = [f for f in REQUIRED_ARTICLE_FIELDS if f not in result]
    if missing:
        raise StructuralValidationError(f"必須フィールドが欠落しています: {missing}")

    if not result.get("title"):
        raise StructuralValidationError("titleが空です")
    if not result.get("body"):
        raise StructuralValidationError("bodyが空です")

    for key in ("point_one", "point_two"):
        point = result.get(key)
        if not isinstance(point, dict) or not point.get("heading") or not point.get("paragraphs"):
            raise StructuralValidationError(f"{key}が空、または構造が不正です")

    # Pointが正確に2件であること(3件目以降のPoint相当キーがあれば構造不合格)
    point_like_keys = [k for k in result.keys() if k.startswith("point_") and k not in ("point_one", "point_two")]
    if point_like_keys:
        raise StructuralValidationError(f"Pointに相当するキーが2件を超えています: {point_like_keys}")

    if not result.get("one_line_summary"):
        raise StructuralValidationError("one_line_summaryが空です")

    return result


# ============================================================
# ブロック6: 日本語文字数の記録(合否には使わない)
# ============================================================
def _article_full_text(result: dict) -> str:
    return "\n".join([
        result["title"],
        *result["body"],
        result["point_one"]["heading"], *result["point_one"]["paragraphs"],
        result["point_two"]["heading"], *result["point_two"]["paragraphs"],
        result["one_line_summary"],
    ])


def _strip_markdown_and_whitespace(text: str) -> str:
    stripped = re.sub(r"[#*_`>\-]", "", text)
    stripped = re.sub(r"\s", "", stripped)
    return stripped


def compute_character_metrics(result: dict, master_full_text: str) -> dict:
    full_text = _article_full_text(result)
    total_characters = len(full_text)
    characters_excluding_whitespace_and_markdown = len(_strip_markdown_and_whitespace(full_text))
    master_characters = len(_strip_markdown_and_whitespace(master_full_text))
    ratio_to_master = (
        round(characters_excluding_whitespace_and_markdown / master_characters, 3)
        if master_characters else None
    )
    return {
        "total_characters": total_characters,
        "characters_excluding_whitespace_and_markdown": characters_excluding_whitespace_and_markdown,
        "ratio_to_master": ratio_to_master,
    }


# ============================================================
# ブロック7: 最小事実QA(明確な事実事故の検出だけ。面白さは判定しない)
# ============================================================
MINIMAL_FACT_QA_PROMPT_VERSION = "er002-ja-master-imitation-fact-qa-v1"

MINIMAL_FACT_QA_PROMPT_TEMPLATE = """あなたは、生成済みの日本語記事を、確認済み事実だけと突き合わせて検証する担当です。記事の面白さ・勢い・アングルの良し悪し・Pointの価値・narrativeのまとまり・In One Lineの印象・聞き手が続きを聞きたいかは一切判定しないでください。判定するのは、事実面の事故の有無だけです。

【確認済み事実】
{facts_block}

【検証対象の記事】
{article_text}

以下の2点だけを判定してください:
1. contradicts_verified_facts: 記事が確認済み事実と明確に矛盾する記述を含むか(true/false)。
2. unsupported_specific_claims: 確認済み事実に存在しない具体的な主張のリスト(空リストなら該当なし)。対象には少なくとも、数字・日付・固有名詞・具体的な出来事・発言・心理や意図・因果関係・政策効果・戦術評価・確認済み事実に存在しない具体的場面・確認済み事実に存在しない具体的反応を含めること。

Return ONLY valid JSON, no other text, in exactly this shape:
{{"contradicts_verified_facts": false, "unsupported_specific_claims": [], "evidence": "brief explanation"}}"""


def build_minimal_fact_qa_prompt(article_text: str, fact_id_map: dict) -> str:
    return MINIMAL_FACT_QA_PROMPT_TEMPLATE.format(
        facts_block=build_facts_block(fact_id_map), article_text=article_text,
    )


MINIMAL_FACT_QA_REQUIRED_FIELDS = ["contradicts_verified_facts", "unsupported_specific_claims", "evidence"]


class FactQaParseError(Exception):
    pass


def classify_fact_qa(raw_result: dict) -> dict:
    if not isinstance(raw_result, dict):
        raise FactQaParseError("事実QA応答がJSONオブジェクトではありません")
    missing = [f for f in MINIMAL_FACT_QA_REQUIRED_FIELDS if f not in raw_result]
    if missing:
        raise FactQaParseError(f"事実QA応答に必須フィールドが欠落: {missing}")
    if not raw_result.get("evidence"):
        raise FactQaParseError("事実QA応答にevidenceがありません")

    contradicts = raw_result.get("contradicts_verified_facts")
    unsupported = raw_result.get("unsupported_specific_claims")
    if not isinstance(contradicts, bool):
        raise FactQaParseError("contradicts_verified_factsが真偽値ではありません")
    if not isinstance(unsupported, list):
        raise FactQaParseError("unsupported_specific_claimsがリストではありません")

    if contradicts:
        verdict = "FAIL"
    elif unsupported:
        verdict = "REVIEW_REQUIRED"
    else:
        verdict = "PASS"

    return {"verdict": verdict, "raw": raw_result}


MAX_FACT_QA_EVAL_ATTEMPTS = 2  # 解析不能時のみ、同じ記事内容で最大2回まで評価をやり直す


def evaluate_fact_qa(
    prompt: str,
    fact_qa_call_fn: Callable[[str], str],
    max_eval_attempts: int = MAX_FACT_QA_EVAL_ATTEMPTS,
    max_api_retry: int = common.MAX_QA_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> dict:
    total_api_retry = 0
    for attempt in range(1, max_eval_attempts + 1):
        outcome = common.call_qa_with_retry(
            lambda p, _wav: fact_qa_call_fn(p), prompt, b"", max_retry=max_api_retry, sleep_fn=sleep_fn)
        total_api_retry += outcome.api_retry_count

        if outcome.parse_failed or outcome.raw_result is None:
            if attempt < max_eval_attempts:
                continue
            return {"status": "inconclusive", "verdict": None, "eval_attempts": attempt,
                    "total_api_retry_count": total_api_retry}

        try:
            classified = classify_fact_qa(outcome.raw_result)
        except FactQaParseError:
            if attempt < max_eval_attempts:
                continue
            return {"status": "inconclusive", "verdict": None, "eval_attempts": attempt,
                    "total_api_retry_count": total_api_retry}

        return {"status": "ok", "verdict": classified["verdict"], "raw": classified["raw"],
                "eval_attempts": attempt, "total_api_retry_count": total_api_retry}

    return {"status": "inconclusive", "verdict": None, "total_api_retry_count": total_api_retry}


# ============================================================
# ブロック8: 生成の技術的再試行(内容不満での再生成は禁止。解析不能時のみ
# 同一内容生成を1回だけ再試行し、技術再試行として別カウントする)
# ============================================================
MAX_GENERATION_API_RETRY = common.MAX_TTS_API_RETRY
MAX_GENERATION_PARSE_RETRY = 1  # 解析不能時のみ、同一内容生成を1回だけ再試行する


def _run_generation_with_retries(
    generation_fn: Callable[[dict], dict],
    max_api_retry: int = MAX_GENERATION_API_RETRY,
    max_parse_retry: int = MAX_GENERATION_PARSE_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    api_retry_count = 0
    parse_retry_count = 0
    last_error = None
    while True:
        try:
            result = generation_fn({})
            return result, api_retry_count, parse_retry_count, True, None
        except GenerationParseError as e:
            parse_retry_count += 1
            last_error = str(e)
            if parse_retry_count > max_parse_retry:
                return None, api_retry_count, parse_retry_count, False, f"parse_failed_after_retry: {last_error}"
            continue
        except Exception as e:
            api_retry_count += 1
            last_error = str(e)
            if sleep_fn:
                sleep_fn(2)
            if api_retry_count > max_api_retry:
                return None, api_retry_count, parse_retry_count, False, f"api_failed_after_retry: {last_error}"
            continue


# ============================================================
# ブロック9: 記事1件分のパイプライン(内容生成は1回のみ。事実QAの結果
# (REVIEW_REQUIRED/FAIL)による再生成は行わない)
# ============================================================
@dataclass
class JaMasterImitationOutcome:
    status: str  # "OK" / "FAILED_STRUCTURAL" / "FAILED_TECHNICAL" / "MASTER_INTEGRITY_FAILED"
    article: Optional[dict] = None
    fact_qa: Optional[dict] = None
    character_metrics: Optional[dict] = None
    reasons: list = field(default_factory=list)
    generation_api_retry_count: int = 0
    generation_parse_retry_count: int = 0
    fact_qa_api_retry_count: int = 0
    fact_qa_eval_attempts: int = 0


def run_ja_master_imitation_pipeline(
    generation_fn: Callable[[dict], dict],
    fact_qa_call_fn: Callable[[str], str],
    fact_id_map: dict,
    master_full_text: str,
    max_generation_api_retry: int = MAX_GENERATION_API_RETRY,
    max_generation_parse_retry: int = MAX_GENERATION_PARSE_RETRY,
    max_fact_qa_eval_attempts: int = MAX_FACT_QA_EVAL_ATTEMPTS,
    max_fact_qa_api_retry: int = common.MAX_QA_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> JaMasterImitationOutcome:
    article, gen_api_retries, gen_parse_retries, gen_ok, gen_err = _run_generation_with_retries(
        generation_fn, max_generation_api_retry, max_generation_parse_retry, sleep_fn)
    if not gen_ok:
        return JaMasterImitationOutcome(
            status="FAILED_TECHNICAL", reasons=[gen_err],
            generation_api_retry_count=gen_api_retries, generation_parse_retry_count=gen_parse_retries,
        )

    try:
        validate_structure(article)
    except StructuralValidationError as e:
        return JaMasterImitationOutcome(
            status="FAILED_STRUCTURAL", article=article, reasons=[str(e)],
            generation_api_retry_count=gen_api_retries, generation_parse_retry_count=gen_parse_retries,
        )

    character_metrics = compute_character_metrics(article, master_full_text)

    fact_qa_prompt = build_minimal_fact_qa_prompt(_article_full_text(article), fact_id_map)
    fact_qa_result = evaluate_fact_qa(
        fact_qa_prompt, fact_qa_call_fn,
        max_eval_attempts=max_fact_qa_eval_attempts, max_api_retry=max_fact_qa_api_retry, sleep_fn=sleep_fn,
    )

    return JaMasterImitationOutcome(
        status="OK", article=article, fact_qa=fact_qa_result, character_metrics=character_metrics,
        generation_api_retry_count=gen_api_retries, generation_parse_retry_count=gen_parse_retries,
        fact_qa_api_retry_count=fact_qa_result.get("total_api_retry_count", 0),
        fact_qa_eval_attempts=fact_qa_result.get("eval_attempts", 0),
    )
