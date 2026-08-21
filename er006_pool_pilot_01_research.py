# ============================================================
# er006_pool_pilot_01_research.py
# ER-006-POOL-PILOT-01: Evidence Pack -> VFL -> Verification
# ============================================================
# ER-005-RESEARCH-LAYER-REDESIGN-01で検証済みの設計(Luna、web_search不使用、
# 既知Sourceの直接取得テキストのみを根拠にする)を、複数Source対応へ一般化
# したもの。個々のprompt/schema/モデル設定はredesign-01から意図的に変更して
# いない(値の再検証はしない、複数件のsourcesリストを受け取れるようにする
# 変更のみ)。

from __future__ import annotations

import json
import os
import time

import requests

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01

SERVICE_POLICY = (
    "eigo-radioの記事候補として、最新性・ニュース価値・信頼性に加え、エンターテインメント性、"
    "意外性、具体性、人が続きを聞きたくなる興味喚起力を重視する。事実の正確性をエンターテインメント"
    "性のために曲げない。"
)


# ============================================================
# Stage B2: Evidence Pack化(Luna、web_search不使用、複数Source対応)
# ============================================================
EVIDENCE_PACK_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのEvidence Pack作成担当です。与えられた複数の一次/参考Sourceの抽出"
    "テキストのみを根拠に、後続のVFL生成・Verificationが再度Web検索しなくても使えるSource付き"
    "の証拠集合(Evidence Pack)を構造化してください。あなたにはWeb検索ツールは与えられていま"
    "せん。与えられたテキストに実際に書かれていない数値・事実を追加で生成しないでください。"
    "各SourceのAccess statusがpaywalled/summary-onlyの場合、そのSourceから拾えるEvidenceは"
    "「二次要約からの引用」であることが分かる形にしてください(ambiguityフィールド等へ明記)。"
    "各Evidenceは、それが支える具体的なFact categoryが分かる形にし、可能な限りsource_location"
    "(section/paragraph等)を残してください。\n\n"
    "【ER-006-RESEARCH-GATE-01: Source Quality Gate】\n"
    "各Sourceについて、source_tierを以下から選んでください: PRIMARY(当事者一次資料・公式"
    "発表)、GOVERNMENT_OR_INSTITUTIONAL(政府・公的機関)、ACADEMIC(査読付き学術論文)、"
    "NEWS_REPORTING(信頼性の高い一次報道)、TERTIARY_AGGREGATOR(Wikipedia等の三次情報・"
    "まとめサイト)、OTHER。\n"
    "具体的な日付・who/when/where・因果関係の断定・個別事例(Critical Fact)を含むEvidenceの"
    "source_tierがTERTIARY_AGGREGATORの場合、そのEvidenceのambiguityフィールドに必ず"
    "「三次情報源のみに基づく個別事実であり、一次情報での裏付けが未確認」と明記してください。"
    "一般的な背景説明・定義・広く知られた概念の紹介であれば、TERTIARY_AGGREGATORでも"
    "ambiguityへの明記は不要です(個別の日付・因果・具体的事例に限定した措置です)。\n\n"
    "【ER-006-FRESHNESS-GATE-01: Conditional Freshness Gate】\n"
    "このTopicが法律・規制・政府制度・policy・訴訟・現行ルール(現時点で有効かどうかがFactの"
    "意味を左右する制度)を含む場合のみ、該当するSourceのpublication_dateが取得可能な最新の"
    "ものかどうかを確認し、該当Evidenceのambiguityフィールドに「制度・規則の現行性は"
    "publication_date時点のものであり、その後の改廃は別途確認が必要」等、現行性に関する"
    "留保を明記してください。それ以外の一般的なEvergreen Topicでは、この留保の記載は"
    "不要です。"
)

EVIDENCE_PACK_PROMPT_TEMPLATE = """【対象Topic】
{title}

【複数のSource(Claude Codeが既知URLへ直接アクセスして取得、またはWeb検索結果の要約として
取得したもの。それぞれのaccess_status/retrieval_methodを参照)】
{sources_json}

【あなたのタスク】
上記の複数Sourceのみを根拠に、Evidence Packを構造化してください。各Sourceについて、以下の
観点をEvidenceとして拾ってください(該当情報がテキスト中にある場合のみ):
- 研究・データの目的・対象
- サンプルサイズ・対象・調査期間(該当する場合)
- 主な結果・数値・方向性
- 制度・ルール・基準(政府/規制Sourceの場合)
- 因果関係の強さ・限界
- publication metadata(著者/組織、日付、DOI等)

テキストに書かれていない情報は追加しないでください。paywalled/summary-onlyのSourceから
拾った内容は、Evidenceのambiguityフィールドに「二次要約由来、原文未確認」等と明記してください。"""


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
            "journal_or_venue": {"type": ["string", "null"]},
            "doi": {"type": ["string", "null"]},
            "primary_or_corroborating": {"type": "string"},
            "access_status": {"type": "string"},
            # ER-006-RESEARCH-GATE-01(Source Quality Gate)で追加。
            "source_tier": {
                "type": "string",
                "enum": ["PRIMARY", "GOVERNMENT_OR_INSTITUTIONAL", "ACADEMIC",
                          "NEWS_REPORTING", "TERTIARY_AGGREGATOR", "OTHER"],
            },
        },
        "required": ["source_id", "title", "url", "source_type", "publication_date",
                      "authors_or_organization", "journal_or_venue", "doi",
                      "primary_or_corroborating", "access_status", "source_tier"],
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


def run_stage_b2_evidence_pack(theme_id: str, out_dir: str, title: str, sources: list) -> dict:
    client = vfl01.get_client()
    prompt = EVIDENCE_PACK_PROMPT_TEMPLATE.format(
        title=title, sources_json=json.dumps(sources, ensure_ascii=False, indent=2))
    with cl.logging_context(theme_id, "research_evidence_pack"):
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
    with open(f"{out_dir}/stage_b2_evidence_pack.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{theme_id}][Stage B2] sources={len(result['parsed']['sources'])} "
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


def run_stage_b3_vfl(theme_id: str, out_dir: str, title: str, evidence_pack: dict) -> dict:
    client = vfl01.get_client()
    prompt = VFL_PROMPT_TEMPLATE.format(
        title=title,
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    with cl.logging_context(theme_id, "research_vfl"):
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
    with open(f"{out_dir}/stage_b3_vfl.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{theme_id}][Stage B3] facts={len(result['parsed']['facts'])}")
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


def run_stage_b4_verification(theme_id: str, out_dir: str, vfl: dict, evidence_pack: dict) -> dict:
    client = vfl01.get_client()
    prompt = VERIFICATION_PROMPT_TEMPLATE.format(
        vfl_json=json.dumps({"facts": vfl["parsed"]["facts"]}, ensure_ascii=False, indent=2),
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    with cl.logging_context(theme_id, "research_verification"):
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
    with open(f"{out_dir}/stage_b4_verification.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    verdict_counts = {}
    for v in result["parsed"]["verifications"]:
        verdict_counts[v["verdict"]] = verdict_counts.get(v["verdict"], 0) + 1
    print(f"[{theme_id}][Stage B4] verdicts={verdict_counts}")
    return result


# ============================================================
# Stage B5: Exception Search(NEEDS_EXTERNAL_CHECK/重大AMBIGUOUSのみ、Perplexity最大2 request)
# ============================================================
def run_exception_search(theme_id: str, out_dir: str, queries: list) -> dict:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"status": "CREDENTIAL_REQUIRED"}
    if len(queries) > 2:
        raise ValueError("Exception Searchは最大2 requestまで(仕様15章)")

    all_results = []
    for q_batch in queries:
        t0 = time.time()
        with cl.logging_context(theme_id, "research_exception_search"):
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
    with open(f"{out_dir}/stage_b5_exception_search.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    return {"status": "OK", "results": all_results}


# ============================================================
# メイン: 1テーマ分のResearchを通しで実行
# ============================================================
def run_research_for_theme(theme_id: str, out_dir: str, title: str, sources: list) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    evidence_pack = run_stage_b2_evidence_pack(theme_id, out_dir, title, sources)
    t1 = time.time()
    vfl = run_stage_b3_vfl(theme_id, out_dir, title, evidence_pack)
    t2 = time.time()
    verification = run_stage_b4_verification(theme_id, out_dir, vfl, evidence_pack)
    t3 = time.time()

    verdict_by_fact = {v["fact_id"]: v["verdict"] for v in verification["parsed"]["verifications"]}
    needs_check = [fid for fid, v in verdict_by_fact.items() if v == "NEEDS_EXTERNAL_CHECK"]
    rejected = [fid for fid, v in verdict_by_fact.items() if v == "REJECTED"]

    timing = {
        "evidence_pack_seconds": round(t1 - t0, 2),
        "vfl_seconds": round(t2 - t1, 2),
        "verification_seconds": round(t3 - t2, 2),
        "research_total_seconds": round(t3 - t0, 2),
    }
    with open(f"{out_dir}/research_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)

    print(f"[{theme_id}] Research完了。needs_external_check={len(needs_check)} rejected={len(rejected)} "
          f"timing={timing}")
    return {
        "theme_id": theme_id, "evidence_pack": evidence_pack, "vfl": vfl, "verification": verification,
        "verdict_by_fact": verdict_by_fact, "needs_external_check_fact_ids": needs_check,
        "rejected_fact_ids": rejected, "timing": timing,
    }


if __name__ == "__main__":
    print("This module is imported by er006_pool_pilot_01_run.py; not run directly.")
