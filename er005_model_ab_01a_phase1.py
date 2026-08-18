# ER-005-MODEL-AB-01A Phase 1: Parenting theme, Luna vs Gemini 3.5 Flash-Lite
# Research -> Verified Fact Ledger draft -> Verification相当のみ。
# Sol再実行なし。各model 1回のみ(best-of禁止、技術的失敗のみretry許容)。
from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01

OUT_DIR = "er005_output/model_ab_01a/parenting"
os.makedirs(f"{OUT_DIR}/luna", exist_ok=True)
os.makedirs(f"{OUT_DIR}/gemini", exist_ok=True)

PARENTING_TOPIC = (
    "2026年3-4月号のChild Development誌(Vol.97 Issue 2、DOI 10.1093/chidev/"
    "aacaf050)に掲載された、ニュージーランドDunedin Studyのコホート追跡研究"
    "(Islam, Jaffee, Belsky, Hancox, Poulton, Ramrakha, Wertz)。出生から"
    "追跡された参加者のうち719人が親になった時点(平均32.7歳)で、3歳の"
    "子どもに対する養育行動(sensitivity・cognitive stimulation)を測定し、"
    "親自身の社会階層の世代間変化(上昇移動/安定低位/安定高位)との関連を検証した。"
    "上昇移動した親は、安定して低いSESの親より養育の質が高かったが、"
    "一貫して高いSESの親より低かった。"
)

cl.install("er005_output/model_ab_01a/raw_usage_log.jsonl")


# ============================================================
# Candidate A: GPT-5.6 Luna(既存vfl01の関数をそのまま再利用、modelのみ差替え)
# ============================================================
def run_luna():
    client = vfl01.get_client()
    prompt = vfl01.build_researcher_prompt(PARENTING_TOPIC)

    with cl.logging_context("parenting", "model_ab_luna_research"):
        t0 = time.time()
        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": vfl01.REASONING_EFFORT},
            tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": vfl01.RESEARCHER_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
        elapsed_research = time.time() - t0
    draft = {
        "prompt": prompt, "raw_text": response.output_text, "parsed": json.loads(response.output_text),
        "model": response.model, "response_id": response.id,
        "search_usage": vfl01.r3.extract_web_search_usage(response),
        "sources": vfl01.r3.extract_sources(response),
        "elapsed_seconds": round(elapsed_research, 2),
    }
    with open(f"{OUT_DIR}/luna/ledger_draft_raw.json", "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Luna] Research done. facts={len(draft['parsed'].get('facts', []))} elapsed={elapsed_research:.1f}s")

    v_prompt = vfl01.build_verification_prompt(PARENTING_TOPIC, draft["parsed"])
    with cl.logging_context("parenting", "model_ab_luna_verification"):
        t0 = time.time()
        v_response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": vfl01.REASONING_EFFORT},
            tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
                {"role": "user", "content": v_prompt},
            ],
        )
        elapsed_verif = time.time() - t0
    verification = {
        "prompt": v_prompt, "raw_text": v_response.output_text, "parsed": json.loads(v_response.output_text),
        "model": v_response.model, "response_id": v_response.id,
        "search_usage": vfl01.r3.extract_web_search_usage(v_response),
        "sources": vfl01.r3.extract_sources(v_response),
        "elapsed_seconds": round(elapsed_verif, 2),
    }
    with open(f"{OUT_DIR}/luna/ledger_verification_raw.json", "w", encoding="utf-8") as f:
        json.dump(verification, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Luna] Verification done. elapsed={elapsed_verif:.1f}s")
    return draft, verification


# ============================================================
# Candidate B: Gemini 3.5 Flash-Lite(google_search grounding + response_schema
# を同一request内で使用。developer message/prompt/JSON schemaの中身はOpenAI版と
# 同一内容をGemini形式へ変換しただけで、Research Architectureは変更しない)
# ============================================================
GEMINI_FACT_SCHEMA = {
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact_id": {"type": "string"},
                    "claim": {"type": "string"},
                    "subject": {"type": "string"},
                    "date_or_period": {"type": "string", "nullable": True},
                    "scope": {"type": "string", "nullable": True},
                    "conditions": {"type": "string", "nullable": True},
                    "numeric_value": {"type": "string", "nullable": True},
                    "numeric_scope": {"type": "string", "nullable": True},
                    "causal_strength": {
                        "type": "string",
                        "enum": ["OBSERVED_REPORTED", "CORRELATIONAL", "CAUSAL_STATED_BY_SOURCE", "NOT_APPLICABLE"],
                    },
                    "source_title": {"type": "string"},
                    "source_url": {"type": "string"},
                    "source_type": {
                        "type": "string",
                        "enum": ["PRIMARY_GOVERNMENT_OR_REGULATOR", "OFFICIAL_REPORT_OR_STUDY",
                                 "RELIABLE_SECONDARY_NEWS", "OTHER"],
                    },
                    "support_level": {
                        "type": "string",
                        "enum": ["DIRECTLY_STATED", "INFERRED_FROM_SOURCE", "PARTIALLY_STATED"],
                    },
                    "ambiguity": {"type": "string", "nullable": True},
                    "notes_for_writer": {"type": "string", "nullable": True},
                },
                "required": ["fact_id", "claim", "subject", "causal_strength", "source_title",
                             "source_url", "source_type", "support_level"],
            },
        },
    },
    "required": ["facts"],
}

GEMINI_VERIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "verifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact_id": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["VERIFIED", "AMBIGUOUS", "REJECTED"]},
                    "verification_notes": {"type": "string"},
                },
                "required": ["fact_id", "verdict", "verification_notes"],
            },
        },
    },
    "required": ["verifications"],
}


def run_gemini():
    from dotenv import load_dotenv
    load_dotenv()
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = vfl01.build_researcher_prompt(PARENTING_TOPIC)

    with cl.logging_context("parenting", "model_ab_gemini_research"):
        t0 = time.time()
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=vfl01.RESEARCHER_DEVELOPER_MESSAGE + "\n\n" + prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json",
                response_schema=GEMINI_FACT_SCHEMA,
            ),
        )
        elapsed_research = time.time() - t0
    gm = response.candidates[0].grounding_metadata
    draft_parsed = json.loads(response.text)
    draft = {
        "prompt": prompt, "raw_text": response.text, "parsed": draft_parsed,
        "model": response.model_version,
        "web_search_queries": list(gm.web_search_queries) if gm and gm.web_search_queries else [],
        "grounding_chunks_count": len(gm.grounding_chunks) if gm and gm.grounding_chunks else 0,
        "usage_metadata": {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "thoughts_token_count": getattr(response.usage_metadata, "thoughts_token_count", None),
            "total_token_count": response.usage_metadata.total_token_count,
        },
        "elapsed_seconds": round(elapsed_research, 2),
    }
    with open(f"{OUT_DIR}/gemini/ledger_draft_raw.json", "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Gemini] Research done. facts={len(draft_parsed.get('facts', []))} "
          f"grounding_queries={len(draft['web_search_queries'])} elapsed={elapsed_research:.1f}s")

    v_prompt = vfl01.build_verification_prompt(PARENTING_TOPIC, draft_parsed)
    with cl.logging_context("parenting", "model_ab_gemini_verification"):
        t0 = time.time()
        v_response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=vfl01.VERIFICATION_DEVELOPER_MESSAGE + "\n\n" + v_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json",
                response_schema=GEMINI_VERIFICATION_SCHEMA,
            ),
        )
        elapsed_verif = time.time() - t0
    v_gm = v_response.candidates[0].grounding_metadata
    verif_parsed = json.loads(v_response.text)
    verification = {
        "prompt": v_prompt, "raw_text": v_response.text, "parsed": verif_parsed,
        "model": v_response.model_version,
        "web_search_queries": list(v_gm.web_search_queries) if v_gm and v_gm.web_search_queries else [],
        "grounding_chunks_count": len(v_gm.grounding_chunks) if v_gm and v_gm.grounding_chunks else 0,
        "usage_metadata": {
            "prompt_token_count": v_response.usage_metadata.prompt_token_count,
            "candidates_token_count": v_response.usage_metadata.candidates_token_count,
            "thoughts_token_count": getattr(v_response.usage_metadata, "thoughts_token_count", None),
            "total_token_count": v_response.usage_metadata.total_token_count,
        },
        "elapsed_seconds": round(elapsed_verif, 2),
    }
    with open(f"{OUT_DIR}/gemini/ledger_verification_raw.json", "w", encoding="utf-8") as f:
        json.dump(verification, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Gemini] Verification done. grounding_queries={len(verification['web_search_queries'])} "
          f"elapsed={elapsed_verif:.1f}s")
    return draft, verification


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "both"
    if target in ("luna", "both"):
        run_luna()
    if target in ("gemini", "both"):
        run_gemini()
