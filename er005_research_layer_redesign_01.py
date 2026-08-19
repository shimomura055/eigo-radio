# ER-005-RESEARCH-LAYER-REDESIGN-01
# Evidence Pack型 Research / VFL / Verification 成立性検証。
# Stage B1: Primary Source取得(既知URLの直接取得。新規Searchではない)
# Stage B2: Evidence Pack化(Luna、web_search不使用)
# Stage B3: VFL生成(Luna、Evidence Packのみを根拠、web_search不使用)
# Stage B4: Verification(Luna、VFL+Evidence Packのみ、web_search不使用)
# Stage B5: Exception Search(NEEDS_EXTERNAL_CHECK/重大AMBIGUOUSのみ、Perplexity最大2 request)
from __future__ import annotations

import json
import os
import time

import requests

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01

OUT_DIR = "er005_output/research_layer_redesign_01"
os.makedirs(OUT_DIR, exist_ok=True)

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

# ER-005-SEARCH-LAYER-OPT-01のPerplexity multi-query経路でLunaが最終選定したTopic
# (Topic Selectionはやり直さない。PPXM-002の候補metadataをそのまま引き継ぐ)
SELECTED_TOPIC = {
    "candidate_id": "PPXM-002",
    "title": "A longitudinal study of parent–child relationship and behavioral "
              "problems in children aged 3 to 6: the mediating role of screen time",
    "url": "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1794353/full",
    "date": "2026-05-25",
}

SERVICE_POLICY = (
    "eigo-radioの記事候補として、最新性・ニュース価値・信頼性に加え、エンターテインメント性、"
    "意外性、具体性、人が続きを聞きたくなる興味喚起力を重視する。事実の正確性をエンターテインメント"
    "性のために曲げない。"
)


# ============================================================
# Stage B1: Primary Source取得(直接取得。既知URLのため新規Searchではない)
# ============================================================
def save_primary_source_raw_text(fetched_text: str) -> dict:
    """WebFetch(Claude Code側の直接取得ツール)で取得した本文抽出結果を保存する。
    これはSearchではなく、Stage A(Topic Selection)で既に判明しているURLへの
    直接アクセスであり、仕様6章の「一次Source URLがすでに明確なら直接取得を優先する」
    に基づく。取得作業自体にLLM API課金は発生しない(WebFetchはこのプロセスの外側で
    実行され、コストロガーの対象であるOpenAI/Perplexity API呼び出しではない)。
    """
    record = {
        "source_id": "SRC-001",
        "title": SELECTED_TOPIC["title"],
        "url": SELECTED_TOPIC["url"],
        "source_type": "PRIMARY_JOURNAL_ARTICLE",
        "primary_or_corroborating": "primary",
        "access_status": "FULL_TEXT_ACCESSIBLE",
        "retrieval_method": "DIRECT_FETCH_KNOWN_URL_NOT_SEARCH",
        "fetched_extraction": fetched_text,
    }
    with open(f"{OUT_DIR}/stage_b1_primary_source.json", "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, default=str)
    return record


# ============================================================
# Stage B2: Evidence Pack化(Luna、web_search不使用)
# ============================================================
EVIDENCE_PACK_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのEvidence Pack作成担当です。与えられた一次Sourceの抽出テキストのみを"
    "根拠に、後続のVFL生成・Verificationが再度Web検索しなくても使えるSource付きの証拠集合"
    "(Evidence Pack)を構造化してください。あなたにはWeb検索ツールは与えられていません。"
    "与えられたテキストに実際に書かれていない数値・事実を追加で生成しないでください。"
    "各Evidenceは、それが支える具体的なFact categoryが分かる形にし、可能な限り"
    "section/paragraph/table等の参照位置(source_location)を残してください。"
)

EVIDENCE_PACK_PROMPT_TEMPLATE = """【対象Topic】
{title}
URL: {url}

【一次Sourceの抽出テキスト(Claude Codeがこの既知URLへ直接アクセスして取得したもの、
Web検索結果ではない)】
{fetched_text}

【あなたのタスク】
上記の抽出テキストのみを根拠に、Evidence Packを構造化してください。少なくとも以下の
観点をEvidenceとして拾ってください(該当情報がテキスト中にある場合のみ):
- 研究の目的・対象
- サンプルサイズ・年齢・対象地域
- 調査期間・時点(longitudinal design等)
- 親子関係(conflict/closeness)の測定方法
- screen timeの測定方法
- 主な統計結果(係数・p値・信頼区間・方向性)
- causal interpretationの限界
- limitations / generalizability
- publication metadata(journal, DOI, 掲載日, 著者)

テキストに書かれていない情報は追加しないでください。"""


def evidence_pack_schema():
    source_item = {
        "type": "object",
        "properties": {
            "source_id": {"type": "string"},
            "title": {"type": "string"},
            "url": {"type": "string"},
            "source_type": {"type": "string"},
            "publication_date": {"type": ["string", "null"]},
            "authors_or_organization": {"type": ["string", "null"]},
            "doi": {"type": ["string", "null"]},
            "primary_or_corroborating": {"type": "string"},
            "access_status": {"type": "string"},
        },
        "required": ["source_id", "title", "url", "source_type", "publication_date",
                      "authors_or_organization", "doi", "primary_or_corroborating", "access_status"],
        "additionalProperties": False,
    }
    evidence_item = {
        "type": "object",
        "properties": {
            "evidence_id": {"type": "string"},
            "source_id": {"type": "string"},
            "evidence_summary": {"type": "string"},
            "supported_fact_category": {"type": "string"},
            "numeric_value": {"type": ["string", "null"]},
            "numeric_scope": {"type": ["string", "null"]},
            "population": {"type": ["string", "null"]},
            "date_or_period": {"type": ["string", "null"]},
            "causal_strength": {"type": "string"},
            "limitation": {"type": ["string", "null"]},
            "ambiguity": {"type": ["string", "null"]},
            "source_location": {"type": ["string", "null"]},
            "support_level": {"type": "string", "enum": ["direct_support", "partial_support"]},
        },
        "required": ["evidence_id", "source_id", "evidence_summary", "supported_fact_category",
                      "numeric_value", "numeric_scope", "population", "date_or_period",
                      "causal_strength", "limitation", "ambiguity", "source_location", "support_level"],
        "additionalProperties": False,
    }
    return {
        "name": "evidence_pack",
        "schema": {
            "type": "object",
            "properties": {
                "sources": {"type": "array", "items": source_item},
                "evidence_items": {"type": "array", "items": evidence_item},
            },
            "required": ["sources", "evidence_items"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def run_stage_b2_evidence_pack(primary_source: dict) -> dict:
    client = vfl01.get_client()
    prompt = EVIDENCE_PACK_PROMPT_TEMPLATE.format(
        title=SELECTED_TOPIC["title"], url=SELECTED_TOPIC["url"],
        fetched_text=primary_source["fetched_extraction"],
    )
    with cl.logging_context("parenting_research_redesign", "luna_stage_b2_evidence_pack"):
        resp = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **evidence_pack_schema()}},
            input=[
                {"role": "developer", "content": EVIDENCE_PACK_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    result = {
        "prompt": prompt, "raw_text": resp.output_text, "parsed": json.loads(resp.output_text),
        "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }
    with open(f"{OUT_DIR}/stage_b2_evidence_pack.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Stage B2] sources={len(result['parsed']['sources'])} "
          f"evidence_items={len(result['parsed']['evidence_items'])}")
    return result


# ============================================================
# Stage B3: VFL生成(Luna、Evidence Packのみを根拠、web_search不使用)
# ============================================================
VFL_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのVerified Fact Ledger作成担当です。与えられたEvidence Packのみを"
    "根拠にFactを生成してください。あなたにはWeb検索ツールは与えられていません。"
    "Evidence Packに存在しないFactを、あなたの一般知識や記憶から追加しないでください。"
    "各FactはEvidence Packのsource_idとevidence_idへ必ず逆参照できる形にしてください。"
    "対応するEvidenceが無いFactはLedgerに含めないでください。"
)

VFL_PROMPT_TEMPLATE = """【対象Topic】
{title}

【Evidence Pack(このみを根拠にしてください、Web検索はしないでください)】
{evidence_pack_json}

【あなたのタスク】
上記のEvidence Packのみを根拠に、Verified Fact LedgerのFactを生成してください。
各Factについて、fact_id・claim・subject・date_or_period・scope・conditions・
numeric_value・numeric_scope・causal_strength・source_id・evidence_id・
support_level・ambiguity・notes_for_writerを埋めてください(該当しない項目はnullで可)。
必ずsource_id/evidence_idで元のEvidence Packの項目へ逆参照できるようにしてください。"""


def vfl_schema():
    fact_item = {
        "type": "object",
        "properties": {
            "fact_id": {"type": "string"},
            "claim": {"type": "string"},
            "subject": {"type": "string"},
            "date_or_period": {"type": ["string", "null"]},
            "scope": {"type": ["string", "null"]},
            "conditions": {"type": ["string", "null"]},
            "numeric_value": {"type": ["string", "null"]},
            "numeric_scope": {"type": ["string", "null"]},
            "causal_strength": {"type": "string"},
            "source_id": {"type": "string"},
            "evidence_id": {"type": "string"},
            "support_level": {"type": "string"},
            "ambiguity": {"type": ["string", "null"]},
            "notes_for_writer": {"type": ["string", "null"]},
        },
        "required": ["fact_id", "claim", "subject", "date_or_period", "scope", "conditions",
                      "numeric_value", "numeric_scope", "causal_strength", "source_id",
                      "evidence_id", "support_level", "ambiguity", "notes_for_writer"],
        "additionalProperties": False,
    }
    return {
        "name": "verified_fact_ledger",
        "schema": {
            "type": "object",
            "properties": {"facts": {"type": "array", "items": fact_item}},
            "required": ["facts"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def run_stage_b3_vfl(evidence_pack: dict) -> dict:
    client = vfl01.get_client()
    prompt = VFL_PROMPT_TEMPLATE.format(
        title=SELECTED_TOPIC["title"],
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    with cl.logging_context("parenting_research_redesign", "luna_stage_b3_vfl"):
        resp = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **vfl_schema()}},
            input=[
                {"role": "developer", "content": VFL_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    result = {
        "prompt": prompt, "raw_text": resp.output_text, "parsed": json.loads(resp.output_text),
        "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }
    with open(f"{OUT_DIR}/stage_b3_vfl.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Stage B3] facts={len(result['parsed']['facts'])}")
    return result


# ============================================================
# Stage B4: Verification(Luna、VFL+Evidence Packのみ、web_search不使用)
# ============================================================
VERIFICATION_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのVerification担当です。目的は、VFLに書かれたFactがEvidence Pack"
    "と一致しているかを確認することであり、Web検索をもう一度全面的にやり直すことでは"
    "ありません。あなたにはVFLとEvidence Packだけが渡されます。Web検索ツールは"
    "与えられていません。各Factについて、VERIFIED(Evidenceが直接支える)/"
    "PARTIALLY_SUPPORTED(一部は支えるがClaimが広すぎる)/AMBIGUOUS(Evidenceだけでは"
    "断定できない)/REJECTED(EvidenceとClaimが矛盾)/NEEDS_EXTERNAL_CHECK(Evidence Pack"
    "だけでは確認不能)のいずれかで判定し、理由をverification_notesへ記載してください。"
)

VERIFICATION_PROMPT_TEMPLATE = """【検証対象VFL】
{vfl_json}

【Evidence Pack】
{evidence_pack_json}

【あなたのタスク】
各fact_idについて、VERIFIED / PARTIALLY_SUPPORTED / AMBIGUOUS / REJECTED /
NEEDS_EXTERNAL_CHECKのいずれかで判定し、理由をverification_notesへ記載してください。"""


def verification_schema():
    v_item = {
        "type": "object",
        "properties": {
            "fact_id": {"type": "string"},
            "verdict": {"type": "string", "enum": ["VERIFIED", "PARTIALLY_SUPPORTED",
                                                     "AMBIGUOUS", "REJECTED", "NEEDS_EXTERNAL_CHECK"]},
            "verification_notes": {"type": "string"},
        },
        "required": ["fact_id", "verdict", "verification_notes"],
        "additionalProperties": False,
    }
    return {
        "name": "verification_result",
        "schema": {
            "type": "object",
            "properties": {"verifications": {"type": "array", "items": v_item}},
            "required": ["verifications"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def run_stage_b4_verification(vfl: dict, evidence_pack: dict, stage_name: str = "luna_stage_b4_verification",
                                vfl_subset: list = None) -> dict:
    client = vfl01.get_client()
    facts_for_prompt = vfl_subset if vfl_subset is not None else vfl["parsed"]["facts"]
    prompt = VERIFICATION_PROMPT_TEMPLATE.format(
        vfl_json=json.dumps({"facts": facts_for_prompt}, ensure_ascii=False, indent=2),
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    with cl.logging_context("parenting_research_redesign", stage_name):
        resp = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **verification_schema()}},
            input=[
                {"role": "developer", "content": VERIFICATION_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    result = {
        "prompt": prompt, "raw_text": resp.output_text, "parsed": json.loads(resp.output_text),
        "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }
    return result


# ============================================================
# Stage B5: Exception Search(NEEDS_EXTERNAL_CHECK/重大AMBIGUOUSのみ、Perplexity最大2 request)
# ============================================================
def run_exception_search(queries: list[str]) -> dict:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"status": "CREDENTIAL_REQUIRED"}
    if len(queries) > 2:
        raise ValueError("Exception Searchは最大2 requestまで(仕様15章)")

    all_results = []
    for q_batch in queries:
        t0 = time.time()
        with cl.logging_context("parenting_research_redesign", "perplexity_exception_search"):
            resp = requests.post(
                "https://api.perplexity.ai/search",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"query": q_batch, "max_results": 10},
                timeout=30,
            )
            elapsed = round(time.time() - t0, 3)
            success = resp.status_code == 200
            data = resp.json() if success else {}
            cl.record({
                "provider": "perplexity", "api": "exception_search", "attempt_number": 1,
                "success": success, "elapsed_seconds": elapsed,
                "usage_source": "OFFICIAL_API_RESPONSE" if success else "N/A_FAILED_CALL",
                "http_status": resp.status_code,
                "billed_requests": 1 if success else 0,
                "query_batch": q_batch,
            })
        all_results.append({"query_batch": q_batch, "results": data.get("results", []) if success else []})
    with open(f"{OUT_DIR}/stage_b5_exception_search.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    return {"status": "OK", "results": all_results}


if __name__ == "__main__":
    print("This script is driven interactively/stepwise; see report for the executed sequence.")
