# ============================================================
# er002_ja_web_research_r3.py
# ER-002-v1.2M-R3: Web検索付きChatGPT自己取材・記事生成パイロット
# ============================================================
# R1/R2(concise brief方式)とは別の実験として分離する。writerモデルへ
# テーマ名だけを渡し、必要なWeb検索・調査・執筆判断をすべてwriterモデル
# 自身に一つのResponses API実行内で行わせる。Claude Codeや別モデルが
# 事前に検索・要約してwriterへ再投入する処理は一切実装しない。
#
# 生成後、R2の構造ゲート(validate_point_structure)をそのまま再利用する。
# 構造合格後、writerとは別の新規・独立したAPI実行で、Web検索ツールを
# 有効にしたfact checkerが事実確認を行う(writerの会話状態を引き継がない)。
#
# 以下は一切importしない・再利用しない:
#   - er002_editorial_common.py / er002_editorial_angle_adapter.py /
#     er002_editorial_runner.py(Editorial Brief系)
#   - er002_ja_master_imitation.pyのbuild_prompt/JA_ARTICLE_JSON_SCHEMA等
#     (Structured Output本文生成経路)
#   - concise brief関連の処理(R1/R2のbuild_writer_user_message系)
# 以下は再利用する:
#   - er002_ja_free_markdown_restore.WRITER_MODEL/WRITER_REASONING_EFFORT/
#     NEUTRAL_DEVELOPER_MESSAGE/GenerationEmptyOrBrokenError(R2から維持)
#   - er002_ja_free_markdown_restore_r2.validate_point_structure(構造ゲート)

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from dotenv import load_dotenv

import er002_ja_free_markdown_restore as restore
import er002_ja_free_markdown_restore_r2 as restore_r2

EXPERIMENT_VERSION = "ER-002-v1.2M-R3"
BASE_EXPERIMENT_VERSION = "ER-002-v1.2M-R2"

# R2から維持(変更しない)
WRITER_MODEL = restore.WRITER_MODEL  # "gpt-5.6-sol"
WRITER_REASONING_EFFORT = restore.WRITER_REASONING_EFFORT  # "high"
NEUTRAL_DEVELOPER_MESSAGE = restore.NEUTRAL_DEVELOPER_MESSAGE  # "日本語の記事を作成してください。"

R3_WRITER_PROMPT_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template_r3.txt"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_r3_writer_prompt_template(path: str = R3_WRITER_PROMPT_PATH) -> str:
    return restore.load_text_file(path)


def build_writer_user_message_r3(master_full_text: str, topic: str, template: Optional[str] = None) -> str:
    """concise briefを一切使わない。マスター全文とテーマ名だけを差し込む。"""
    template = template if template is not None else load_r3_writer_prompt_template()
    return template.format(hanshin_master_full_text=master_full_text, topic=topic)


# ============================================================
# ブロック1: writer応答からのWeb検索利用状況・参照ソースの抽出
# ============================================================
def extract_web_search_usage(response: Any) -> dict:
    """response.outputの中からweb_search_callアイテムを数え、writerモデル
    自身が生成した検索クエリを取り出す(アプリ側で検索語を指定していない
    ことの裏付けにもなる)。"""
    web_search_calls = [item for item in response.output if getattr(item, "type", None) == "web_search_call"]
    queries = []
    for call in web_search_calls:
        action = getattr(call, "action", None)
        if action is not None:
            qs = getattr(action, "queries", None)
            if qs:
                queries.extend(qs)
            else:
                q = getattr(action, "query", None)
                if q:
                    queries.append(q)
    return {"web_search_call_count": len(web_search_calls), "queries": queries}


def extract_sources(response: Any) -> list:
    """message出力内のurl_citation annotationから、参照ソースのタイトル・
    URLだけを抽出する(本文全体は保存しない)。"""
    sources = []
    seen = set()
    for item in response.output:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", None) or []:
            for ann in getattr(content, "annotations", None) or []:
                if getattr(ann, "type", None) == "url_citation":
                    url = getattr(ann, "url", None)
                    title = getattr(ann, "title", None)
                    if url and url not in seen:
                        seen.add(url)
                        sources.append({"title": title, "url": url})
    return sources


# ============================================================
# ブロック2: writer(自己取材)呼び出し
# ============================================================
def make_writer_research_fn(
    user_message: str,
    client: Optional[Any] = None,
    model: str = WRITER_MODEL,
    reasoning_effort: str = WRITER_REASONING_EFFORT,
    developer_message: str = NEUTRAL_DEVELOPER_MESSAGE,
):
    """Web検索ツールを有効にしたwriter呼び出し関数を返す。検索語・検索回数・
    追加検索の要否はすべてモデル自身が同一のResponses API実行内で判断する。"""
    if client is None:
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def writer_fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            tools=[{"type": "web_search"}],
            input=[
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message},
            ],
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise restore.GenerationEmptyOrBrokenError("応答が空です")
        search_usage = extract_web_search_usage(response)
        sources = extract_sources(response)
        return text, response.model, response.id, search_usage, sources

    writer_fn.model = model
    writer_fn.reasoning_effort = reasoning_effort
    writer_fn.developer_message = developer_message
    writer_fn.uses_web_search_tool = True
    writer_fn.response_format_used = False
    return writer_fn


class WriterWebSearchNotUsedError(RuntimeError):
    """Web検索ツールが1回も呼ばれなかった場合に技術的失敗として扱うための印。"""


MAX_CONTENT_ATTEMPTS = 2  # 初回 + (Web検索未使用 または 構造不適合)時の再生成1回のみ


def run_writer_with_gates(
    make_writer_fn: Callable[[], Callable],
    max_content_attempts: int = MAX_CONTENT_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """内容不満での再生成ではない。(1) Web検索ツールが1回も呼ばれなかった場合、
    (2) 構造(Point数)が不適合な場合、のいずれかであれば、同一条件で最大1回
    だけ再生成する。2回目も不適合ならそれ以上再生成しない。

    戻り値: (raw_text, final_status, attempts_detail, model_id, response_id,
             search_usage, sources)
    final_status: "STRUCTURE_PASS" / "STRUCTURE_INVALID" /
                  "WRITER_WEB_SEARCH_NOT_USED" / "TECHNICAL_GENERATION_FAILED"
    """
    attempts_detail = []

    for attempt in range(1, max_content_attempts + 1):
        writer_fn = make_writer_fn()
        try:
            raw_text, model_id, response_id, search_usage, sources = writer_fn()
        except Exception as e:
            attempts_detail.append({
                "content_attempt": attempt, "status": "TECHNICAL_GENERATION_FAILED",
                "error": f"{type(e).__name__}: {e}", "raw_text": None,
            })
            if attempt < max_content_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None, None, None

        if search_usage["web_search_call_count"] == 0:
            attempts_detail.append({
                "content_attempt": attempt, "status": "WRITER_WEB_SEARCH_NOT_USED",
                "search_usage": search_usage, "sources": sources,
                "raw_text": raw_text, "model": model_id, "response_id": response_id,
            })
            if attempt < max_content_attempts:
                continue
            return raw_text, "WRITER_WEB_SEARCH_NOT_USED", attempts_detail, model_id, response_id, search_usage, sources

        structure = restore_r2.validate_point_structure(raw_text)
        attempts_detail.append({
            "content_attempt": attempt, "status": structure.status,
            "search_usage": search_usage, "sources": sources,
            "raw_text": raw_text, "model": model_id, "response_id": response_id,
            "structure_headings": structure.headings, "structure_reasons": structure.reasons,
        })
        if structure.status == "STRUCTURE_PASS":
            return raw_text, "STRUCTURE_PASS", attempts_detail, model_id, response_id, search_usage, sources
        if attempt < max_content_attempts:
            continue
        return raw_text, "STRUCTURE_INVALID", attempts_detail, model_id, response_id, search_usage, sources

    return None, "TECHNICAL_GENERATION_FAILED", attempts_detail, None, None, None, None


# ============================================================
# ブロック3: 独立したWeb fact checker(writerとは別の新規API実行)
# ============================================================
FACT_CHECKER_MODEL = WRITER_MODEL  # writerと同一モデルだが、会話状態は完全に独立した別呼び出し
FACT_CHECKER_REASONING_EFFORT = WRITER_REASONING_EFFORT

FACT_CHECK_PROMPT_TEMPLATE_PATH = "er002_v1_2m_restore_briefs/fact_checker_prompt_template_r3.txt"

FACT_CHECK_JSON_SCHEMA = {
    "name": "independent_fact_check",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["PASS", "REVIEW_REQUIRED", "FAIL"]},
            "contradictions": {"type": "array", "items": {"type": "string"}},
            "unsupported_specific_claims": {"type": "array", "items": {"type": "string"}},
            "verified_claims_summary": {"type": "array", "items": {"type": "string"}},
            "sources": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
        },
        "required": ["verdict", "contradictions", "unsupported_specific_claims",
                     "verified_claims_summary", "sources", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}


def load_fact_check_prompt_template(path: str = FACT_CHECK_PROMPT_TEMPLATE_PATH) -> str:
    return restore.load_text_file(path)


def build_fact_check_prompt(topic: str, article_text: str, writer_sources: list, template: Optional[str] = None) -> str:
    template = template if template is not None else load_fact_check_prompt_template()
    sources_block = "\n".join(f"- {s.get('title') or '(タイトル不明)'}: {s.get('url')}" for s in writer_sources) or "(参照ソースなし)"
    return template.format(topic=topic, article_text=article_text, writer_sources_block=sources_block)


def make_fact_checker_fn(
    prompt: str,
    client: Optional[Any] = None,
    model: str = FACT_CHECKER_MODEL,
    reasoning_effort: str = FACT_CHECKER_REASONING_EFFORT,
):
    """writerの会話状態を一切引き継がない、新規・独立したResponses API呼び出し。
    Web検索ツールとStructured Outputの両方を有効にする。"""
    if client is None:
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    def fact_checker_fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **FACT_CHECK_JSON_SCHEMA}},
            input=prompt,
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise restore.GenerationEmptyOrBrokenError("fact checker応答が空です")
        search_usage = extract_web_search_usage(response)
        sources = extract_sources(response)
        return text, response.model, response.id, search_usage, sources

    fact_checker_fn.model = model
    fact_checker_fn.reasoning_effort = reasoning_effort
    fact_checker_fn.uses_web_search_tool = True
    fact_checker_fn.uses_structured_output = True
    return fact_checker_fn


# ============================================================
# ブロック4: fact checker出力のスキーマ検証 + Web検索必須ゲート
# ============================================================
# writerの本文(記事)は、fact checkerがどのような結果であっても一切
# 再生成しない。ここで行う再試行は、fact checker自身の技術的な失敗
# (検索未使用・JSON解析/スキーマ不適合)に対する再試行であり、記事の
# 内容不満による再生成ではない。

class FactCheckSchemaError(ValueError):
    """fact checkerの出力がJSONとして解析できない、またはスキーマ要件
    (必須フィールド・型・verdictの3値制約)を満たさない場合。"""


FACT_CHECK_VERDICTS = ("PASS", "REVIEW_REQUIRED", "FAIL")

_FACT_CHECK_REQUIRED_FIELD_TYPES = {
    "verdict": str,
    "contradictions": list,
    "unsupported_specific_claims": list,
    "verified_claims_summary": list,
    "sources": list,
    "notes": str,
}
_FACT_CHECK_STRING_LIST_FIELDS = (
    "contradictions", "unsupported_specific_claims", "verified_claims_summary", "sources",
)


def parse_and_validate_fact_check_output(raw_text: str) -> dict:
    """fact checkerの出力テキストをJSONとして解析し、必須フィールド・型・
    verdictの3値制約を検証する。解析不能・スキーマ不適合の場合は例外を
    送出するのみで、PASS等の結果として扱うことは一切ない。"""
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise FactCheckSchemaError(f"JSON解析に失敗しました: {e}") from e

    if not isinstance(parsed, dict):
        raise FactCheckSchemaError("トップレベルがJSONオブジェクトではありません")

    for field_name, expected_type in _FACT_CHECK_REQUIRED_FIELD_TYPES.items():
        if field_name not in parsed:
            raise FactCheckSchemaError(f"必須フィールド'{field_name}'がありません")
        if not isinstance(parsed[field_name], expected_type):
            raise FactCheckSchemaError(
                f"'{field_name}'の型が不正です(期待: {expected_type.__name__})")

    for list_field in _FACT_CHECK_STRING_LIST_FIELDS:
        if not all(isinstance(item, str) for item in parsed[list_field]):
            raise FactCheckSchemaError(f"'{list_field}'の要素は全て文字列である必要があります")

    if parsed["verdict"] not in FACT_CHECK_VERDICTS:
        raise FactCheckSchemaError(
            f"verdictは{FACT_CHECK_VERDICTS}のいずれかである必要があります(実際: {parsed['verdict']!r})")

    return parsed


MAX_FACT_CHECK_ATTEMPTS = 2  # 初回 + (Web検索未使用 または JSON解析/スキーマ不適合)時の技術再試行1回のみ


def run_fact_checker_with_gates(
    make_fact_checker_fn: Callable[[], Callable],
    max_attempts: int = MAX_FACT_CHECK_ATTEMPTS,
    sleep_fn: Optional[Callable[[float], None]] = None,
):
    """writer本文の再生成には一切関与しない。(1) fact checker自身がWeb検索
    ツールを1回も呼ばなかった場合、(2) fact checkerの出力がJSONとして解析
    できない、またはスキーマ要件を満たさない場合、のいずれかであれば、
    同一条件で最大1回だけ技術再試行する。2回目も失敗すれば、それ以上は
    再試行しない。

    戻り値: (parsed_result, final_status, attempts_detail, model_id,
             response_id, search_usage, sources)
    final_status: "FACT_CHECK_COMPLETED" / "FACT_CHECK_WEB_SEARCH_NOT_USED" /
                  "FACT_CHECK_TECHNICAL_FAILED"
    parsed_resultはFACT_CHECK_COMPLETED時のみ辞書(verdict/contradictions/
    unsupported_specific_claims/verified_claims_summary/sources/notesを
    含む)、それ以外は必ずNone。

    FACT_CHECK_WEB_SEARCH_NOT_USEDおよびFACT_CHECK_TECHNICAL_FAILEDと
    なった記事は、STRUCTURE_INVALID等と同様にユーザー品質評価から除外
    する(呼び出し側のレビュー生成処理が担う)。
    """
    attempts_detail = []

    for attempt in range(1, max_attempts + 1):
        fact_checker_fn = make_fact_checker_fn()
        try:
            raw_text, model_id, response_id, search_usage, sources = fact_checker_fn()
        except Exception as e:
            attempts_detail.append({
                "fact_check_attempt": attempt, "status": "FACT_CHECK_TECHNICAL_FAILED",
                "error": f"{type(e).__name__}: {e}", "raw_text": None,
            })
            if attempt < max_attempts:
                if sleep_fn:
                    sleep_fn(2)
                continue
            return None, "FACT_CHECK_TECHNICAL_FAILED", attempts_detail, None, None, None, None

        if search_usage["web_search_call_count"] == 0:
            attempts_detail.append({
                "fact_check_attempt": attempt, "status": "FACT_CHECK_WEB_SEARCH_NOT_USED",
                "search_usage": search_usage, "sources": sources,
                "raw_text": raw_text, "model": model_id, "response_id": response_id,
            })
            if attempt < max_attempts:
                continue
            return None, "FACT_CHECK_WEB_SEARCH_NOT_USED", attempts_detail, model_id, response_id, search_usage, sources

        try:
            parsed_result = parse_and_validate_fact_check_output(raw_text)
        except FactCheckSchemaError as e:
            attempts_detail.append({
                "fact_check_attempt": attempt, "status": "FACT_CHECK_TECHNICAL_FAILED",
                "error": str(e), "search_usage": search_usage, "sources": sources,
                "raw_text": raw_text, "model": model_id, "response_id": response_id,
            })
            if attempt < max_attempts:
                continue
            return None, "FACT_CHECK_TECHNICAL_FAILED", attempts_detail, model_id, response_id, search_usage, sources

        attempts_detail.append({
            "fact_check_attempt": attempt, "status": "FACT_CHECK_COMPLETED",
            "verdict": parsed_result["verdict"], "search_usage": search_usage, "sources": sources,
            "raw_text": raw_text, "model": model_id, "response_id": response_id,
        })
        return parsed_result, "FACT_CHECK_COMPLETED", attempts_detail, model_id, response_id, search_usage, sources

    return None, "FACT_CHECK_TECHNICAL_FAILED", attempts_detail, None, None, None, None
