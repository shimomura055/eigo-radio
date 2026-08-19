# ER-005-E2E-RESEARCH-AB-01-P1
# Zero-base: User Input -> Stage A(Topic Selection) -> Stage B(Research Brief)
# -> Stage C(Research/VFL)。Luna / Gemini 3.5 Flash-Lite、Parentingのみ、各1run。
from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01
# NOTE: er005_model_ab_01a_phase1をここで先にimportしておくことで、
# 同モジュール冒頭のcl.install(別ログpath)を先に発火させ、下のcl.install()
# (このE2E用ログpath)で確実に上書きさせる。run_gemini()内で遅延import
# すると、Stage C実行中にログ出力先が model_ab_01a 側へ無断で切り替わる
# バグがあったため(ER-005-E2E-RESEARCH-AB-01-P1実行時に発見・修正)。
from er005_model_ab_01a_phase1 import GEMINI_FACT_SCHEMA, GEMINI_VERIFICATION_SCHEMA

USER_INPUT = "最近の子育て研究"

SERVICE_POLICY = (
    "eigo-radioの記事候補として、最新性・ニュース価値・信頼性に加え、エンターテインメント性、"
    "意外性、具体性、人が続きを聞きたくなる興味喚起力を重視する。ユーザーのお題に対して候補を"
    "広く探索し、単に最初に見つかった無難な話題を選ばず、複数候補を比較したうえで、一般の"
    "リスナーが「面白い」「知らなかった」「聞いてみたい」と感じやすく、約5分の記事として十分な"
    "内容の厚みがあるTopicを選定する。選定後は一次Sourceを優先してResearchし、Verified Fact "
    "Ledgerを作成する。事実の正確性をエンターテインメント性のために曲げない。"
)

TOPIC_SELECTION_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのTopic Selection担当です。ユーザーの短い入力から、Web検索を使って"
    "記事候補を幅広く探索し、Service Policyに基づいて最も適した1件を選定してください。"
    "記事本文は書きません。"
)

TOPIC_SELECTION_PROMPT_TEMPLATE = """【ユーザー入力】
{user_input}

【eigo-radio Service Policy】
{service_policy}

【あなたのタスク】
1. ユーザー入力に関連する記事候補を、Web検索を使って幅広く探索してください。単に最初に見つかった無難な話題を選ばないでください。
2. 探索した中から、最大10件をCandidate Poolとして構造化してください。各候補について、実際に検索・参照したSourceに基づいて記録してください(検索で確認していない候補を後付けで作らないでください)。
3. Candidate Poolの中から、本気で検討した上位3〜5件をShortlistとして残し、それぞれについてService Policyの各観点で簡潔に評価してください。
4. Shortlistから最終的に1件をFinal Selectionとして選び、他のShortlist候補よりeigo-radioに適していると判断した理由を簡潔に記載してください。
5. Shortlistから落とした主要候補についても、簡潔な理由を残してください。"""

RESEARCH_BRIEF_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのResearch Brief作成担当です。選定されたTopicについて、後続の"
    "Researcherが何を調べるべきかを示す方針書(Research Brief)を作成してください。Brief自体は"
    "「答え」ではなく、Researchの方向づけです。Stage Aで確認していないFactを、確定Factとして"
    "新たに追加しないでください。"
)

RESEARCH_BRIEF_PROMPT_TEMPLATE = """【選定されたTopic】
{topic}

【選定理由】
{rationale}

【参考: Topic Selection時に参照した主なSource】
{source_ref}

【あなたのタスク】
上記のTopicについて、後続のResearcherへ向けたResearch Briefを自然な文章で作成してください。以下を含めてください:
- Research Objective(何を明らかにするための調査か)
- 調べるべき主要論点
- 確認が必要なFact categories(人数・日付・scope等)
- Primary Source方針
- 数字・scopeの精度についての注意点
- causal vs correlational区別についての注意点
- 想定されるlimitations/ambiguity
- 後続のWriterが記事を書く上で必要になりそうなcontext"""


def topic_selection_schema_openai():
    item = {
        "type": "object",
        "properties": {
            "candidate_id": {"type": "string"},
            "title": {"type": "string"},
            "topic_summary": {"type": "string"},
            "source_title": {"type": "string"},
            "source_url": {"type": "string"},
            "source_date": {"type": ["string", "null"]},
            "user_input_relevance": {"type": "string"},
            "service_policy_appeal": {"type": "string"},
            "five_minute_depth": {"type": "string"},
            "primary_source_likelihood": {"type": "string"},
        },
        "required": ["candidate_id", "title", "topic_summary", "source_title", "source_url",
                     "source_date", "user_input_relevance", "service_policy_appeal",
                     "five_minute_depth", "primary_source_likelihood"],
        "additionalProperties": False,
    }
    shortlist_item = {
        "type": "object",
        "properties": {
            "candidate_id": {"type": "string"},
            "freshness": {"type": "string"},
            "news_value": {"type": "string"},
            "entertainment_value": {"type": "string"},
            "surprise_novelty": {"type": "string"},
            "curiosity_pull": {"type": "string"},
            "five_minute_fit": {"type": "string"},
            "source_strength": {"type": "string"},
        },
        "required": ["candidate_id", "freshness", "news_value", "entertainment_value",
                     "surprise_novelty", "curiosity_pull", "five_minute_fit", "source_strength"],
        "additionalProperties": False,
    }
    return {
        "name": "topic_selection_result",
        "schema": {
            "type": "object",
            "properties": {
                "candidate_pool": {"type": "array", "items": item},
                "shortlist": {"type": "array", "items": shortlist_item},
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
            "required": ["candidate_pool", "shortlist", "final_selection", "rejected_shortlist"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def topic_selection_schema_gemini():
    item = {
        "type": "object",
        "properties": {
            "candidate_id": {"type": "string"},
            "title": {"type": "string"},
            "topic_summary": {"type": "string"},
            "source_title": {"type": "string"},
            "source_url": {"type": "string"},
            "source_date": {"type": "string", "nullable": True},
            "user_input_relevance": {"type": "string"},
            "service_policy_appeal": {"type": "string"},
            "five_minute_depth": {"type": "string"},
            "primary_source_likelihood": {"type": "string"},
        },
        "required": ["candidate_id", "title", "topic_summary", "source_title", "source_url",
                     "user_input_relevance", "service_policy_appeal", "five_minute_depth",
                     "primary_source_likelihood"],
    }
    shortlist_item = {
        "type": "object",
        "properties": {
            "candidate_id": {"type": "string"},
            "freshness": {"type": "string"},
            "news_value": {"type": "string"},
            "entertainment_value": {"type": "string"},
            "surprise_novelty": {"type": "string"},
            "curiosity_pull": {"type": "string"},
            "five_minute_fit": {"type": "string"},
            "source_strength": {"type": "string"},
        },
        "required": ["candidate_id", "freshness", "news_value", "entertainment_value",
                     "surprise_novelty", "curiosity_pull", "five_minute_fit", "source_strength"],
    }
    return {
        "type": "object",
        "properties": {
            "candidate_pool": {"type": "array", "items": item},
            "shortlist": {"type": "array", "items": shortlist_item},
            "final_selection": {
                "type": "object",
                "properties": {
                    "candidate_id": {"type": "string"},
                    "topic": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["candidate_id", "topic", "rationale"],
            },
            "rejected_shortlist": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"candidate_id": {"type": "string"}, "reason": {"type": "string"}},
                    "required": ["candidate_id", "reason"],
                },
            },
        },
        "required": ["candidate_pool", "shortlist", "final_selection", "rejected_shortlist"],
    }


cl.install("er005_output/e2e_research_ab_01_p1/raw_usage_log.jsonl")


# ============================================================
# Luna(OpenAI Responses API)
# ============================================================
def run_luna():
    out_dir = "er005_output/e2e_research_ab_01_p1/luna"
    os.makedirs(out_dir, exist_ok=True)
    client = vfl01.get_client()

    # Stage A
    prompt_a = TOPIC_SELECTION_PROMPT_TEMPLATE.format(user_input=USER_INPUT, service_policy=SERVICE_POLICY)
    with cl.logging_context("parenting_e2e", "luna_stage_a_topic_selection"):
        resp_a = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "high"},
            tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **topic_selection_schema_openai()}},
            input=[
                {"role": "developer", "content": TOPIC_SELECTION_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt_a},
            ],
        )
    stage_a = {
        "prompt": prompt_a, "raw_text": resp_a.output_text, "parsed": json.loads(resp_a.output_text),
        "model": resp_a.model, "response_id": resp_a.id,
        "search_usage": vfl01.r3.extract_web_search_usage(resp_a),
        "sources": vfl01.r3.extract_sources(resp_a),
    }
    with open(f"{out_dir}/stage_a_topic_selection.json", "w", encoding="utf-8") as f:
        json.dump(stage_a, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Luna] Stage A done. candidates={len(stage_a['parsed']['candidate_pool'])} "
          f"search_calls={stage_a['search_usage']['web_search_call_count']}")

    final = stage_a["parsed"]["final_selection"]
    cand = next((c for c in stage_a["parsed"]["candidate_pool"] if c["candidate_id"] == final["candidate_id"]), None)
    source_ref = f"{cand['source_title']} ({cand['source_url']})" if cand else "(参照Source不明)"

    # Stage B
    prompt_b = RESEARCH_BRIEF_PROMPT_TEMPLATE.format(topic=final["topic"], rationale=final["rationale"],
                                                       source_ref=source_ref)
    with cl.logging_context("parenting_e2e", "luna_stage_b_research_brief"):
        resp_b = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "high"},
            input=[
                {"role": "developer", "content": RESEARCH_BRIEF_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt_b},
            ],
        )
    stage_b = {"prompt": prompt_b, "brief_text": resp_b.output_text, "model": resp_b.model,
               "response_id": resp_b.id}
    with open(f"{out_dir}/stage_b_research_brief.json", "w", encoding="utf-8") as f:
        json.dump(stage_b, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Luna] Stage B done. brief_length={len(resp_b.output_text)}")

    # Stage C(既存vfl01関数を再利用、topic=Stage Bのbrief全文)
    brief_text = resp_b.output_text
    prompt_c1 = vfl01.build_researcher_prompt(brief_text)
    with cl.logging_context("parenting_e2e", "luna_stage_c_research"):
        resp_c1 = client.responses.create(
            model="gpt-5.6-luna", reasoning={"effort": "high"}, tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}},
            input=[{"role": "developer", "content": vfl01.RESEARCHER_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt_c1}],
        )
    draft = {"prompt": prompt_c1, "raw_text": resp_c1.output_text, "parsed": json.loads(resp_c1.output_text),
             "model": resp_c1.model, "response_id": resp_c1.id,
             "search_usage": vfl01.r3.extract_web_search_usage(resp_c1),
             "sources": vfl01.r3.extract_sources(resp_c1)}
    with open(f"{out_dir}/stage_c_ledger_draft.json", "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Luna] Stage C draft done. facts={len(draft['parsed'].get('facts', []))}")

    prompt_c2 = vfl01.build_verification_prompt(brief_text, draft["parsed"])
    with cl.logging_context("parenting_e2e", "luna_stage_c_verification"):
        resp_c2 = client.responses.create(
            model="gpt-5.6-luna", reasoning={"effort": "high"}, tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
            input=[{"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt_c2}],
        )
    verif = {"prompt": prompt_c2, "raw_text": resp_c2.output_text, "parsed": json.loads(resp_c2.output_text),
             "model": resp_c2.model, "response_id": resp_c2.id,
             "search_usage": vfl01.r3.extract_web_search_usage(resp_c2),
             "sources": vfl01.r3.extract_sources(resp_c2)}
    with open(f"{out_dir}/stage_c_verification.json", "w", encoding="utf-8") as f:
        json.dump(verif, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Luna] Stage C verification done.")


# ============================================================
# Gemini 3.5 Flash-Lite
# ============================================================
def run_gemini():
    from dotenv import load_dotenv
    load_dotenv()
    from google import genai
    from google.genai import types

    out_dir = "er005_output/e2e_research_ab_01_p1/gemini"
    os.makedirs(out_dir, exist_ok=True)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def usage_of(resp):
        return {
            "prompt_token_count": resp.usage_metadata.prompt_token_count,
            "candidates_token_count": resp.usage_metadata.candidates_token_count,
            "thoughts_token_count": getattr(resp.usage_metadata, "thoughts_token_count", None),
            "total_token_count": resp.usage_metadata.total_token_count,
        }

    def grounding_of(resp):
        gm = resp.candidates[0].grounding_metadata
        return {
            "web_search_queries": list(gm.web_search_queries) if gm and gm.web_search_queries else [],
            "grounding_chunks_count": len(gm.grounding_chunks) if gm and gm.grounding_chunks else 0,
        }

    # Stage A
    prompt_a = TOPIC_SELECTION_PROMPT_TEMPLATE.format(user_input=USER_INPUT, service_policy=SERVICE_POLICY)
    with cl.logging_context("parenting_e2e", "gemini_stage_a_topic_selection"):
        resp_a = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=TOPIC_SELECTION_DEVELOPER_MESSAGE + "\n\n" + prompt_a,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json",
                response_schema=topic_selection_schema_gemini(),
            ),
        )
    stage_a = {"prompt": prompt_a, "raw_text": resp_a.text, "parsed": json.loads(resp_a.text),
               "model": resp_a.model_version, "usage_metadata": usage_of(resp_a), **grounding_of(resp_a)}
    with open(f"{out_dir}/stage_a_topic_selection.json", "w", encoding="utf-8") as f:
        json.dump(stage_a, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Gemini] Stage A done. candidates={len(stage_a['parsed']['candidate_pool'])} "
          f"search_queries={len(stage_a['web_search_queries'])}")

    final = stage_a["parsed"]["final_selection"]
    cand = next((c for c in stage_a["parsed"]["candidate_pool"] if c["candidate_id"] == final["candidate_id"]), None)
    source_ref = f"{cand['source_title']} ({cand['source_url']})" if cand else "(参照Source不明)"

    # Stage B(検索なし、純粋な統合・執筆)
    prompt_b = RESEARCH_BRIEF_PROMPT_TEMPLATE.format(topic=final["topic"], rationale=final["rationale"],
                                                       source_ref=source_ref)
    with cl.logging_context("parenting_e2e", "gemini_stage_b_research_brief"):
        resp_b = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=RESEARCH_BRIEF_DEVELOPER_MESSAGE + "\n\n" + prompt_b,
        )
    stage_b = {"prompt": prompt_b, "brief_text": resp_b.text, "model": resp_b.model_version,
               "usage_metadata": usage_of(resp_b)}
    with open(f"{out_dir}/stage_b_research_brief.json", "w", encoding="utf-8") as f:
        json.dump(stage_b, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Gemini] Stage B done. brief_length={len(resp_b.text)}")

    # Stage C
    brief_text = resp_b.text
    prompt_c1 = vfl01.build_researcher_prompt(brief_text)
    with cl.logging_context("parenting_e2e", "gemini_stage_c_research"):
        resp_c1 = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=vfl01.RESEARCHER_DEVELOPER_MESSAGE + "\n\n" + prompt_c1,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json",
                response_schema=GEMINI_FACT_SCHEMA,
            ),
        )
    draft = {"prompt": prompt_c1, "raw_text": resp_c1.text, "parsed": json.loads(resp_c1.text),
             "model": resp_c1.model_version, "usage_metadata": usage_of(resp_c1), **grounding_of(resp_c1)}
    with open(f"{out_dir}/stage_c_ledger_draft.json", "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Gemini] Stage C draft done. facts={len(draft['parsed'].get('facts', []))} "
          f"search_queries={len(draft['web_search_queries'])}")

    prompt_c2 = vfl01.build_verification_prompt(brief_text, draft["parsed"])
    with cl.logging_context("parenting_e2e", "gemini_stage_c_verification"):
        resp_c2 = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=vfl01.VERIFICATION_DEVELOPER_MESSAGE + "\n\n" + prompt_c2,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json",
                response_schema=GEMINI_VERIFICATION_SCHEMA,
            ),
        )
    verif = {"prompt": prompt_c2, "raw_text": resp_c2.text, "parsed": json.loads(resp_c2.text),
             "model": resp_c2.model_version, "usage_metadata": usage_of(resp_c2), **grounding_of(resp_c2)}
    with open(f"{out_dir}/stage_c_verification.json", "w", encoding="utf-8") as f:
        json.dump(verif, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Gemini] Stage C verification done. search_queries={len(verif['web_search_queries'])}")


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "both"
    if target in ("luna", "both"):
        run_luna()
    if target in ("gemini", "both"):
        run_gemini()
