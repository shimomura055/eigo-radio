# ER-005-SEARCH-LAYER-AB-01
# Search Layer分離型Architecture成立性検証。
# Stage A1: Luna Query Planning (built-in web_search不使用、1回のみ)
# Stage A2: 外部Search API(Brave/Perplexity/Tavily)へ同一Query群を投入
# Stage A3: 各providerのCandidate PoolをLunaへ渡してTopic Selection
from __future__ import annotations

import json
import os

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01

USER_INPUT = "最近の子育て研究"

SERVICE_POLICY = (
    "eigo-radioの記事候補として、最新性・ニュース価値・信頼性に加え、エンターテインメント性、"
    "意外性、具体性、人が続きを聞きたくなる興味喚起力を重視する。ユーザーのお題に対して候補を"
    "広く探索し、単に最初に見つかった無難な話題を選ばず、複数候補を比較したうえで、一般の"
    "リスナーが「面白い」「知らなかった」「聞いてみたい」と感じやすく、約5分の記事として十分な"
    "内容の厚みがあるTopicを選定する。選定後は一次Sourceを優先してResearchし、Verified Fact "
    "Ledgerを作成する。事実の正確性をエンターテインメント性のために曲げない。"
)

MAX_QUERIES = 6

OUT_DIR = "er005_output/search_layer_ab_01"
os.makedirs(OUT_DIR, exist_ok=True)

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")


# ============================================================
# Stage A1: Query Planner (Luna, web_search不使用)
# ============================================================
QUERY_PLANNER_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのQuery Plannerです。あなたの役割は、ユーザー入力とService Policyから、"
    "後続の外部Search APIへ投げるための検索query群を設計することだけです。"
    "あなたは以下を行いません: "
    "特定研究を最終Topicとして決定すること、特定分野(睡眠・遺伝等)へ勝手に絞り込むこと、"
    "Research結果を捏造すること、Search前にCandidate Topicを確定すること、"
    "DOIや人数等のFactを生成すること、Candidate rankingを完成させること。"
    "あなたにはWeb検索ツールは与えられていません。あなた自身の知識で検索queryを考案してください。"
    "queryは複数の方向(異なる切り口・異なる情報源タイプ)から探索できるよう設計し、"
    "早期に1つのTopicへ収束しないようにしてください。"
)

QUERY_PLANNER_PROMPT = f"""【ユーザー入力】
{USER_INPUT}

【eigo-radio Service Policy(Topic Selectionに関わる部分)】
{SERVICE_POLICY}

【あなたのタスク】
上記のユーザー入力とService Policyに基づいて、外部Search APIへ投入するための検索query群を
設計してください。最大{MAX_QUERIES}件まで。特定の研究・分野へ早期に絞り込まず、
複数の方向から広く探索できるquery群にしてください。"""

QUERY_PLAN_SCHEMA = {
    "name": "query_plan",
    "schema": {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
        },
        "required": ["queries"],
        "additionalProperties": False,
    },
    "strict": True,
}


def run_stage_a1_query_planning() -> dict:
    client = vfl01.get_client()
    with cl.logging_context("parenting_search_layer", "luna_stage_a1_query_planning"):
        resp = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **QUERY_PLAN_SCHEMA}},
            input=[
                {"role": "developer", "content": QUERY_PLANNER_DEVELOPER_MESSAGE},
                {"role": "user", "content": QUERY_PLANNER_PROMPT},
            ],
        )
    parsed = json.loads(resp.output_text)
    raw_queries = parsed["queries"]
    truncated = len(raw_queries) > MAX_QUERIES
    used_queries = raw_queries[:MAX_QUERIES]
    dropped_queries = raw_queries[MAX_QUERIES:]

    result = {
        "prompt": QUERY_PLANNER_PROMPT,
        "raw_text": resp.output_text,
        "raw_queries_from_model": raw_queries,
        "used_queries": used_queries,
        "dropped_queries_due_to_cap": dropped_queries,
        "truncated": truncated,
        "model": resp.model,
        "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }
    with open(f"{OUT_DIR}/stage_a1_query_plan.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Stage A1] queries_from_model={len(raw_queries)} used={len(used_queries)} "
          f"truncated={truncated}")
    return result


if __name__ == "__main__":
    run_stage_a1_query_planning()
