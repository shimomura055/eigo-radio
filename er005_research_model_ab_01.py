# ER-005-RESEARCH-MODEL-AB-01
# Research Layer(Evidence Pack -> VFL -> Verification)のモデル比較: Luna vs DeepSeek V4 Flash。
# 両モデルへ完全に同一のPrimary Source本文(ER-005-SOURCE-RETRIEVER-01のSimple Retriever
# 取得結果)を渡す。Topic Selection・Search APIは今回対象外。
from __future__ import annotations

import json
import os

from openai import OpenAI

import er005_cost_logger as cl
# NOTE: import後にこちらのcl.install()を呼ぶことで、このモジュール冒頭のcl.installで
# ログ出力先が確実にこのタスク用のログpathになるようにする
# (ER-005-E2E-RESEARCH-AB-01-P1で発見・修正した、遅延importによるログ先誤爆バグと同じ
# 回避策)。
import er005_research_layer_redesign_01 as redesign01
import er003_v1_en_direct_vfl_01_generate as vfl01

OUT_DIR = "er005_output/research_model_ab_01"
os.makedirs(f"{OUT_DIR}/luna", exist_ok=True)
os.makedirs(f"{OUT_DIR}/deepseek", exist_ok=True)

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

USD_TO_JPY = 160

# ER-005-SOURCE-RETRIEVER-01が取得したPrimary Source本文(両モデルへ完全同一入力)
with open("er005_output/source_retriever_01/retrieval_result.json", encoding="utf-8") as f:
    _retrieval = json.load(f)
PRIMARY_SOURCE_TEXT = _retrieval["extracted_text"]
SELECTED_TOPIC = redesign01.SELECTED_TOPIC


# ============================================================
# Luna(GPT-5.6 Luna、Responses API、json_schema strict mode)
# ============================================================
def run_luna_pipeline() -> dict:
    client = vfl01.get_client()
    out = {}

    prompt_ep = redesign01.EVIDENCE_PACK_PROMPT_TEMPLATE.format(
        title=SELECTED_TOPIC["title"], url=SELECTED_TOPIC["url"],
        fetched_text=PRIMARY_SOURCE_TEXT,
    )
    with cl.logging_context("research_model_ab", "luna_r1_evidence_pack"):
        resp = client.responses.create(
            model="gpt-5.6-luna", reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **redesign01.evidence_pack_schema()}},
            input=[{"role": "developer", "content": redesign01.EVIDENCE_PACK_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt_ep}],
        )
    evidence_pack = {"parsed": json.loads(resp.output_text), "raw_text": resp.output_text,
                      "model": resp.model, "response_id": resp.id,
                      "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
    out["evidence_pack"] = evidence_pack
    print(f"[Luna R1] evidence_items={len(evidence_pack['parsed']['evidence_items'])}")

    prompt_vfl = redesign01.VFL_PROMPT_TEMPLATE.format(
        title=SELECTED_TOPIC["title"],
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    with cl.logging_context("research_model_ab", "luna_r2_vfl"):
        resp = client.responses.create(
            model="gpt-5.6-luna", reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **redesign01.vfl_schema()}},
            input=[{"role": "developer", "content": redesign01.VFL_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt_vfl}],
        )
    vfl = {"parsed": json.loads(resp.output_text), "raw_text": resp.output_text,
           "model": resp.model, "response_id": resp.id,
           "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
    out["vfl"] = vfl
    print(f"[Luna R2] facts={len(vfl['parsed']['facts'])}")

    prompt_v = redesign01.VERIFICATION_PROMPT_TEMPLATE.format(
        vfl_json=json.dumps({"facts": vfl["parsed"]["facts"]}, ensure_ascii=False, indent=2),
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    with cl.logging_context("research_model_ab", "luna_r3_verification"):
        resp = client.responses.create(
            model="gpt-5.6-luna", reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **redesign01.verification_schema()}},
            input=[{"role": "developer", "content": redesign01.VERIFICATION_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt_v}],
        )
    verification = {"parsed": json.loads(resp.output_text), "raw_text": resp.output_text,
                     "model": resp.model, "response_id": resp.id,
                     "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
    out["verification"] = verification
    print(f"[Luna R3] verifications={len(verification['parsed']['verifications'])}")

    for name, data in out.items():
        with open(f"{OUT_DIR}/luna/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return out


# ============================================================
# DeepSeek V4 Flash(OpenAI互換Chat Completions API、json_object mode)
# DeepSeekはOpenAIのjson_schema strict modeを持たないため(2026-08-19公式ドキュメント
# 確認済み)、response_format={"type":"json_object"}のみを使用し、プロンプト内へ目的の
# JSON構造を明示する。developer/userの本文内容自体はLunaと完全に同一のものを使う。
DEEPSEEK_MODEL = "deepseek-v4-flash"


def get_deepseek_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def _json_mode_suffix(schema_description: str) -> str:
    return (f"\n\n【出力形式(json_object mode)】\n"
            f"必ず有効なJSONのみを出力してください(コードフェンスや説明文を含めない)。\n"
            f"次の構造に従ってください:\n{schema_description}")


EVIDENCE_PACK_SCHEMA_DESC = """{
  "sources": [ {"source_id","title","url","source_type","publication_date","authors_or_organization","doi","primary_or_corroborating","access_status"} ],
  "evidence_items": [ {"evidence_id","source_id","evidence_summary","supported_fact_category","numeric_value","numeric_scope","population","date_or_period","causal_strength","limitation","ambiguity","source_location","support_level":"direct_support"|"partial_support"} ]
}"""

VFL_SCHEMA_DESC = """{
  "facts": [ {"fact_id","claim","subject","date_or_period","scope","conditions","numeric_value","numeric_scope","causal_strength","source_id","evidence_id","support_level","ambiguity","notes_for_writer"} ]
}"""

VERIFICATION_SCHEMA_DESC = """{
  "verifications": [ {"fact_id","verdict":"VERIFIED"|"PARTIALLY_SUPPORTED"|"AMBIGUOUS"|"REJECTED"|"NEEDS_EXTERNAL_CHECK","verification_notes"} ]
}"""


def _deepseek_call(client: OpenAI, stage_name: str, developer_message: str, prompt: str, schema_desc: str) -> dict:
    full_user_content = prompt + _json_mode_suffix(schema_desc)
    # NOTE(API仕様上必要な最小差分): DeepSeekはreasoning_tokensをcompletion_tokens/
    # max_tokensの同一予算内でカウントする(Lunaのreasoning effortとは異なり、可視output
    # とは別枠にならない)。実測で、この課題の入力サイズ(約7万字/2万token)ではreasoning
    # だけで6,000超token消費し、max_tokens=8000では可視JSON出力が全て切り詰められ
    # json.loads不能になった(finish_reason="length")。そのためmax_tokensを32000へ
    # 引き上げている。これはLuna側には存在しない、DeepSeek固有の制約に対する必須調整で
    # あり、プロンプト内容自体は変更していない。
    with cl.logging_context("research_model_ab", stage_name):
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "system", "content": developer_message},
                      {"role": "user", "content": full_user_content}],
            response_format={"type": "json_object"},
            max_tokens=32000,
        )
        usage = resp.usage
        cl.record({
            "provider": "deepseek", "api": "chat.completions.create",
            "model_id": resp.model, "attempt_number": 1, "success": True,
            "usage_source": "OFFICIAL_API_RESPONSE",
            "input_tokens": usage.prompt_tokens, "output_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "prompt_cache_hit_tokens": getattr(usage, "prompt_cache_hit_tokens", None),
            "prompt_cache_miss_tokens": getattr(usage, "prompt_cache_miss_tokens", None),
        })
    content = resp.choices[0].message.content
    return {
        "prompt": full_user_content, "raw_text": content, "parsed": json.loads(content),
        "model": resp.model, "response_id": resp.id,
        "input_tokens": usage.prompt_tokens, "output_tokens": usage.completion_tokens,
        "prompt_cache_hit_tokens": getattr(usage, "prompt_cache_hit_tokens", None),
        "prompt_cache_miss_tokens": getattr(usage, "prompt_cache_miss_tokens", None),
    }


def run_deepseek_pipeline() -> dict:
    client = get_deepseek_client()
    out = {}

    prompt_ep = redesign01.EVIDENCE_PACK_PROMPT_TEMPLATE.format(
        title=SELECTED_TOPIC["title"], url=SELECTED_TOPIC["url"],
        fetched_text=PRIMARY_SOURCE_TEXT,
    )
    evidence_pack = _deepseek_call(client, "deepseek_r1_evidence_pack",
                                    redesign01.EVIDENCE_PACK_DEVELOPER_MESSAGE, prompt_ep,
                                    EVIDENCE_PACK_SCHEMA_DESC)
    out["evidence_pack"] = evidence_pack
    print(f"[DeepSeek R1] evidence_items={len(evidence_pack['parsed'].get('evidence_items', []))}")

    prompt_vfl = redesign01.VFL_PROMPT_TEMPLATE.format(
        title=SELECTED_TOPIC["title"],
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    vfl = _deepseek_call(client, "deepseek_r2_vfl",
                          redesign01.VFL_DEVELOPER_MESSAGE, prompt_vfl, VFL_SCHEMA_DESC)
    out["vfl"] = vfl
    print(f"[DeepSeek R2] facts={len(vfl['parsed'].get('facts', []))}")

    prompt_v = redesign01.VERIFICATION_PROMPT_TEMPLATE.format(
        vfl_json=json.dumps({"facts": vfl["parsed"]["facts"]}, ensure_ascii=False, indent=2),
        evidence_pack_json=json.dumps(evidence_pack["parsed"], ensure_ascii=False, indent=2),
    )
    verification = _deepseek_call(client, "deepseek_r3_verification",
                                   redesign01.VERIFICATION_DEVELOPER_MESSAGE, prompt_v,
                                   VERIFICATION_SCHEMA_DESC)
    out["verification"] = verification
    print(f"[DeepSeek R3] verifications={len(verification['parsed'].get('verifications', []))}")

    for name, data in out.items():
        with open(f"{OUT_DIR}/deepseek/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return out


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "both"
    if target in ("luna", "both"):
        run_luna_pipeline()
    if target in ("deepseek", "both"):
        run_deepseek_pipeline()
