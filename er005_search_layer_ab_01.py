# ER-005-SEARCH-LAYER-AB-01
# Search Layer分離型Architecture成立性検証。
# Stage A1: Luna Query Planning (built-in web_search不使用、1回のみ)
# Stage A2: 外部Search API(Brave/Perplexity/Tavily)へ同一Query群を投入
# Stage A3: 各providerのCandidate PoolをLunaへ渡してTopic Selection
from __future__ import annotations

import json
import os
import time
from urllib.parse import urlparse

import requests

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


# ============================================================
# Stage A2: 外部Search API(今回はTavilyのみ、Brave/Perplexityは
# CREDENTIAL_REQUIREDのため未実行)
# ============================================================
MAX_CANDIDATE_POOL = 20

# 一次Source likelihoodの機械的な粗い分類(編集的判断ではなく、ドメインパターンのみに基づく)。
PRIMARY_SOURCE_DOMAIN_HINTS_HIGH = (
    "pubmed.ncbi.nlm.nih.gov", "doi.org", "nature.com", "nih.gov", ".gov",
    "sciencedirect.com", "springer.com", "apa.org", "jamanetwork.com",
    "thelancet.com", "cell.com", "pnas.org", "mdpi.com", "wiley.com",
    "tandfonline.com", "sagepub.com", "frontiersin.org", "bmj.com",
)
PRIMARY_SOURCE_DOMAIN_HINTS_MID = (
    "eurekalert.org", "phys.org", "newswise.com", "sciencedaily.com",
    ".edu", "apnews.com", "reuters.com",
)


def _classify_primary_source_likelihood(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if any(h in domain for h in PRIMARY_SOURCE_DOMAIN_HINTS_HIGH):
        return "高"
    if any(h in domain for h in PRIMARY_SOURCE_DOMAIN_HINTS_MID):
        return "中"
    return "低"


def _normalize_url(url: str) -> str:
    p = urlparse(url)
    path = p.path.rstrip("/")
    return f"{p.scheme}://{p.netloc.lower()}{path}"


def run_stage_a2_tavily_search(queries: list[str]) -> dict:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"provider": "tavily", "status": "CREDENTIAL_REQUIRED"}

    raw_results_by_query = {}
    all_candidates = []
    for q in queries:
        t0 = time.time()
        with cl.logging_context("parenting_search_layer", "tavily_search"):
            resp = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": q,
                    "search_depth": "basic",
                    "max_results": 10,
                },
                timeout=30,
            )
            elapsed = round(time.time() - t0, 3)
            success = resp.status_code == 200
            data = resp.json() if success else {}
            cl.record({
                "provider": "tavily", "api": "search", "attempt_number": 1,
                "success": success, "elapsed_seconds": elapsed,
                "usage_source": "OFFICIAL_API_RESPONSE" if success else "N/A_FAILED_CALL",
                "http_status": resp.status_code,
                "billed_requests": 1 if success else 0,
                "results_returned": len(data.get("results", [])) if success else 0,
                "query": q,
            })
        raw_results_by_query[q] = data.get("results", []) if success else []
        for r in raw_results_by_query[q]:
            all_candidates.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "source": urlparse(r.get("url", "")).netloc,
                "published_date": r.get("published_date"),
                "snippet": (r.get("content") or "")[:500],
                "query_that_found_it": q,
                "provider": "tavily",
                "relevance_score": r.get("score"),
                "primary_source_likelihood": _classify_primary_source_likelihood(r.get("url", "")),
            })

    with open(f"{OUT_DIR}/tavily/stage_a2_raw_results.json", "w", encoding="utf-8") as f:
        json.dump(raw_results_by_query, f, ensure_ascii=False, indent=2, default=str)

    # --- Dedup(機械的のみ: URL完全一致のみを対象。内容の面白さでの除外は行わない) ---
    seen: dict[str, int] = {}
    deduped = []
    for c in all_candidates:
        key = _normalize_url(c["url"])
        if key in seen:
            deduped[seen[key]]["also_found_by_queries"] = deduped[seen[key]].get(
                "also_found_by_queries", []) + [c["query_that_found_it"]]
            continue
        seen[key] = len(deduped)
        c["duplicate_group"] = key
        deduped.append(c)

    raw_count = len(all_candidates)
    deduped_count = len(deduped)

    # --- 20件上限(relevance/freshness/source qualityのみで機械的に削減) ---
    source_rank = {"高": 2, "中": 1, "低": 0}
    capped = sorted(
        deduped,
        key=lambda c: (source_rank.get(c["primary_source_likelihood"], 0),
                        c.get("relevance_score") or 0.0),
        reverse=True,
    )
    truncated_for_pool_cap = len(capped) > MAX_CANDIDATE_POOL
    capped = capped[:MAX_CANDIDATE_POOL]
    for i, c in enumerate(capped, start=1):
        c["candidate_id"] = f"TAV-{i:03d}"

    result = {
        "provider": "tavily",
        "status": "OK",
        "queries_used": queries,
        "raw_candidate_count": raw_count,
        "deduped_candidate_count": deduped_count,
        "pool_capped_at": MAX_CANDIDATE_POOL,
        "truncated_for_pool_cap": truncated_for_pool_cap,
        "candidate_pool": capped,
    }
    with open(f"{OUT_DIR}/tavily/stage_a2_candidate_pool.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Stage A2/Tavily] raw={raw_count} deduped={deduped_count} "
          f"pool={len(capped)} truncated_for_cap={truncated_for_pool_cap}")
    return result


# ============================================================
# Stage A3: Topic Selector (Luna, web_search不使用、providerごとに1回)
# ============================================================
TOPIC_SELECTOR_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのTopic Selectorです。外部Search APIが返したCandidate Poolのみを"
    "根拠として、Service Policyに基づきTopicを選定してください。あなた自身はWeb検索を行いません"
    "(検索ツールは与えられていません)。Candidate Poolにない情報を追加で捏造しないでください。"
    "内部の思考過程は出力せず、観測可能な評価結果とEditorial rationaleのみを出力してください。"
)

TOPIC_SELECTOR_PROMPT_TEMPLATE = """【ユーザー入力】
{user_input}

【eigo-radio Service Policy】
{service_policy}

【Candidate Pool(外部Search API: {provider}が返した候補、あなた自身は検索していません)】
{candidate_pool_json}

【あなたのタスク】
1. Candidate Poolの各候補について、user_intent_fit / freshness / news_value /
   entertainment_value / surprise / curiosity / five_minute_story_depth /
   source_quality / primary_source_reachability を簡潔に評価してください。
2. 本気で検討した上位3〜5件をShortlistとして選んでください。
3. Shortlistから最終的に1件をFinal Selectionとして選び、選定理由を記載してください。
4. Shortlistから落とした主要候補についても、簡潔な理由を残してください。"""


def topic_selector_schema():
    assessment_item = {
        "type": "object",
        "properties": {
            "candidate_id": {"type": "string"},
            "user_intent_fit": {"type": "string"},
            "freshness": {"type": "string"},
            "news_value": {"type": "string"},
            "entertainment_value": {"type": "string"},
            "surprise": {"type": "string"},
            "curiosity": {"type": "string"},
            "five_minute_story_depth": {"type": "string"},
            "source_quality": {"type": "string"},
            "primary_source_reachability": {"type": "string"},
        },
        "required": ["candidate_id", "user_intent_fit", "freshness", "news_value",
                      "entertainment_value", "surprise", "curiosity",
                      "five_minute_story_depth", "source_quality",
                      "primary_source_reachability"],
        "additionalProperties": False,
    }
    return {
        "name": "topic_selector_result",
        "schema": {
            "type": "object",
            "properties": {
                "candidate_assessment": {"type": "array", "items": assessment_item},
                "shortlist": {"type": "array", "items": {"type": "string"}},
                "final_selection": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "topic": {"type": "string"},
                        "rationale": {"type": "string"},
                    },
                    "required": ["candidate_id", "topic", "rationale"],
                    "additionalProperties": False,
                },
                "rejected_shortlist": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"candidate_id": {"type": "string"}, "reason": {"type": "string"}},
                        "required": ["candidate_id", "reason"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["candidate_assessment", "shortlist", "final_selection", "rejected_shortlist"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def run_stage_a3_topic_selection(provider: str, candidate_pool: list[dict]) -> dict:
    client = vfl01.get_client()
    pool_for_prompt = [
        {k: c[k] for k in ("candidate_id", "title", "url", "source", "published_date",
                            "snippet", "primary_source_likelihood") if k in c}
        for c in candidate_pool
    ]
    prompt = TOPIC_SELECTOR_PROMPT_TEMPLATE.format(
        user_input=USER_INPUT, service_policy=SERVICE_POLICY, provider=provider,
        candidate_pool_json=json.dumps(pool_for_prompt, ensure_ascii=False, indent=2),
    )
    with cl.logging_context("parenting_search_layer", f"luna_stage_a3_topic_selection_{provider}"):
        resp = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **topic_selector_schema()}},
            input=[
                {"role": "developer", "content": TOPIC_SELECTOR_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    result = {
        "provider": provider,
        "prompt": prompt,
        "raw_text": resp.output_text,
        "parsed": json.loads(resp.output_text),
        "model": resp.model,
        "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }
    with open(f"{OUT_DIR}/{provider}/stage_a3_topic_selection.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    final = result["parsed"]["final_selection"]
    print(f"[Stage A3/{provider}] shortlist={len(result['parsed']['shortlist'])} "
          f"final={final['candidate_id']}")
    return result


if __name__ == "__main__":
    import sys

    plan_path = f"{OUT_DIR}/stage_a1_query_plan.json"
    if os.path.exists(plan_path):
        # Query Planは1回だけ作る(section 23)。既存のplanを再利用し、再生成しない。
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
        print("[Stage A1] reusing existing query plan (not re-generated)")
    else:
        plan = run_stage_a1_query_planning()

    target = sys.argv[1] if len(sys.argv) > 1 else "tavily"
    if target == "tavily":
        tavily_pool = run_stage_a2_tavily_search(plan["used_queries"])
        if tavily_pool.get("status") == "OK":
            run_stage_a3_topic_selection("tavily", tavily_pool["candidate_pool"])
