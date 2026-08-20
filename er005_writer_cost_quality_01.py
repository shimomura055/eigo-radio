# ER-005-WRITER-COST-QUALITY-01
# Writer工程(B1/A2)のClean Cost/Quality Baseline計測。
# ER-005-RESEARCH-MODEL-AB-01のLuna版VFL/Evidence Packを唯一の事実源として使い、
# 現行production Writer prompt(COMMON_BLOCK_TEMPLATE、B1_B_DIRECT_INSTRUCTION、
# A2_KAI1_INSTRUCTION、いずれもer003_v1_n3_01_articles_generate.pyより無変更で再利用)を
# Lunaで実行する。Fact Checkのみ、Web Search不使用・VFL/Evidence Pack主体の新規実装。
from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cl
import er003_v1_en_direct_ab_01_generate as ab01
import er002_ja_free_markdown_restore_r2 as restore_r2
import er003_v1_n3_01_articles_generate as gen
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_spoken_first_01_r1_generate as sf1r1

OUT_DIR = "er005_output/writer_cost_quality_01"
os.makedirs(f"{OUT_DIR}/b1", exist_ok=True)
os.makedirs(f"{OUT_DIR}/a2", exist_ok=True)

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

USD_TO_JPY = 160
LUNA_MODEL = "gpt-5.6-luna"
LUNA_REASONING_EFFORT = "high"  # 現行production Writer(r3.WRITER_REASONING_EFFORT)と同一設定

RESEARCH_DIR = "er005_output/research_model_ab_01/luna"

TOPIC_JA = (
    "3〜6歳の未就学児を対象に、親子関係(親密さ・葛藤)と子どものスクリーンタイム、"
    "行動上の問題(内在化・外在化)の関連を調べた2026年のFrontiers in Psychology掲載の"
    "縦断研究(532人、3時点、4か月間隔)。葛藤的な親子関係は、後の行動問題を予測し、"
    "その関連の一部はスクリーンタイムの増加によって媒介されていた。"
)


# ============================================================
# Luna版VFL(JSON)を、production Writerが読める形式のVerified Fact Ledgerテキストへ
# 変換する。新しいFactは一切追加しない、純粋な機械的な再フォーマット。
# ============================================================
def build_ledger_text_from_vfl(vfl_parsed: dict, evidence_parsed: dict) -> str:
    evidence_by_id = {e["evidence_id"]: e for e in evidence_parsed["evidence_items"]}
    lines = [
        "ER-005-WRITER-COST-QUALITY-01 Verified Fact Ledger",
        "(ER-005-RESEARCH-MODEL-AB-01のLuna版Evidence Pack/VFLをそのまま再フォーマットしたもの。",
        " 新しいFactの追加・削除は行っていない)",
        "",
        "注記: 本Ledgerは、number_classification(ANCHOR/SUPPORTING/DISPENSABLE)および",
        "exactness_requirement(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)の個別タグを",
        "含まない(Evidence Pack型Research Layerの標準schemaにこの分類が含まれないため)。",
        "Spoken-first原則(数字の扱い、A〜E)は編集判断として適用し、タグ参照前提のF/Gは",
        "該当なしとして扱うこと。",
        "",
        "=== Fact一覧 ===",
        "",
    ]
    for f in vfl_parsed["facts"]:
        ev = evidence_by_id.get(f["evidence_id"], {})
        lines.append(f"[{f['fact_id']}] {f['claim']}")
        if f.get("numeric_value"):
            lines.append(f"  numeric_value: {f['numeric_value']}")
        if f.get("numeric_scope"):
            lines.append(f"  numeric_scope: {f['numeric_scope']}")
        lines.append(f"  causal_strength: {f.get('causal_strength')}")
        if f.get("ambiguity"):
            lines.append(f"  ambiguity: {f['ambiguity']}")
        if f.get("scope"):
            lines.append(f"  scope: {f['scope']}")
        source_loc = ev.get("source_location")
        lines.append(f"  source: {f['source_id']}/{f['evidence_id']}"
                      + (f"({source_loc})" if source_loc else ""))
        lines.append("")
    return "\n".join(lines)


# ============================================================
# Writer(Luna、web_search不使用、production同一prompt構造)
# ============================================================
def run_writer_no_search(client, user_message: str) -> dict:
    with cl.logging_context("writer_cost_quality", "writer_call"):
        response = client.responses.create(
            model=LUNA_MODEL,
            reasoning={"effort": LUNA_REASONING_EFFORT},
            input=[
                {"role": "developer", "content": vfl01.WRITER_DEVELOPER_MESSAGE},
                {"role": "user", "content": user_message},
            ],
        )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("writer応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id,
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}


def run_writer_with_technical_retry(client, user_message: str, max_attempts: int = 2) -> dict:
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            result = run_writer_no_search(client, user_message)
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                time.sleep(2)
                continue
            return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}
        structure = restore_r2.validate_point_structure(result["raw_text"])
        attempts.append({
            "attempt": attempt, "status": structure.status, "model": result["model"],
            "response_id": result["response_id"], "h3_count": structure.h3_count,
            "headings": structure.headings,
            "input_tokens": result["input_tokens"], "output_tokens": result["output_tokens"],
        })
        if structure.status == "STRUCTURE_PASS":
            return {"status": "STRUCTURE_PASS", "attempts": attempts, **result}
        if attempt < max_attempts:
            continue
        return {"status": "STRUCTURE_INVALID", "attempts": attempts, **result}
    return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}


# ============================================================
# Fact Check(Luna、web_search不使用、VFL/Evidence Packのみ根拠。新規実装)
# ============================================================
FACT_CHECK_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのWriter後Fact Checkerです。生成された記事を、Verified Fact "
    "LedgerとEvidence Packのみと突き合わせて検証してください。あなた自身はWeb検索を"
    "行いません(検索ツールは与えられていません)。原論文本文には直接アクセスできません。"
    "以下の観点で問題を探してください: "
    "unsupported claim(Ledgerにない主張)、number drift(数値の変化・誤転記)、"
    "causal overstatement(相関を因果として書いている等)、scope expansion"
    "(対象範囲の逸脱・過度な一般化)、source interpretation error(Sourceの誤読)、"
    "omitted critical limitation(重要な限界の欠落)。"
)

FACT_CHECK_PROMPT_TEMPLATE = """【検証対象記事】
{article_text}

【Verified Fact Ledger】
{ledger_text}

【Evidence Pack(参考)】
{evidence_pack_json}

【あなたのタスク】
上記の記事を、Ledger・Evidence Packとのみ突き合わせて検証してください。発見した問題を
issuesとして列挙し(問題が無ければ空配列)、各issueにcategory
(unsupported_claim/number_drift/causal_overstatement/scope_expansion/
source_interpretation_error/omitted_critical_limitation)、severity(MINOR/MAJOR)、
description、article上の該当箇所(quote)を記載してください。
最終的にverdictを PASS / MINOR_FIX / MAJOR_FIX / REGENERATE のいずれかで判定してください。"""


def fact_check_schema():
    issue_item = {
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": [
                "unsupported_claim", "number_drift", "causal_overstatement",
                "scope_expansion", "source_interpretation_error", "omitted_critical_limitation",
            ]},
            "severity": {"type": "string", "enum": ["MINOR", "MAJOR"]},
            "description": {"type": "string"},
            "quote": {"type": "string"},
        },
        "required": ["category", "severity", "description", "quote"],
        "additionalProperties": False,
    }
    return {
        "name": "fact_check_result",
        "schema": {
            "type": "object",
            "properties": {
                "issues": {"type": "array", "items": issue_item},
                "verdict": {"type": "string", "enum": ["PASS", "MINOR_FIX", "MAJOR_FIX", "REGENERATE"]},
                "summary": {"type": "string"},
            },
            "required": ["issues", "verdict", "summary"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def run_fact_check(client, label: str, article_text: str, ledger_text: str, evidence_parsed: dict) -> dict:
    prompt = FACT_CHECK_PROMPT_TEMPLATE.format(
        article_text=article_text, ledger_text=ledger_text,
        evidence_pack_json=json.dumps(evidence_parsed, ensure_ascii=False, indent=2),
    )
    with cl.logging_context("writer_cost_quality", f"fact_check_{label}"):
        resp = client.responses.create(
            model=LUNA_MODEL, reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **fact_check_schema()}},
            input=[{"role": "developer", "content": FACT_CHECK_DEVELOPER_MESSAGE},
                   {"role": "user", "content": prompt}],
        )
    return {
        "prompt": prompt, "raw_text": resp.output_text, "parsed": json.loads(resp.output_text),
        "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }


# ============================================================
# メイン
# ============================================================
def run_level(client, label: str, instruction: str, common_block: str, ledger_text: str,
              evidence_parsed: dict) -> dict:
    out_dir = f"{OUT_DIR}/{label.lower()}"
    prompt = gen.build_prompt(common_block, instruction)
    with open(f"{out_dir}/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"[{label}] Writer呼び出し開始...")
    writer_result = run_writer_with_technical_retry(client, prompt)
    with open(f"{out_dir}/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[{label}] Writer失敗 status={writer_result['status']}")
        return {"label": label, "status": writer_result["status"]}

    article_text = writer_result["raw_text"].strip()
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    metrics = gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    print(f"[{label}] Writer完了。 metrics={metrics} sections={section_wc} "
          f"attempts={len(writer_result['attempts'])}")

    print(f"[{label}] Fact Check呼び出し開始...")
    fc = run_fact_check(client, label, article_text, ledger_text, evidence_parsed)
    with open(f"{out_dir}/fact_check.json", "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{label}] Fact Check完了。 verdict={fc['parsed']['verdict']} "
          f"issues={len(fc['parsed']['issues'])}")

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc,
        "writer_attempts": len(writer_result["attempts"]),
        "writer_input_tokens": writer_result["input_tokens"],
        "writer_output_tokens": writer_result["output_tokens"],
        "fact_check_verdict": fc["parsed"]["verdict"],
        "fact_check_issue_count": len(fc["parsed"]["issues"]),
        "fact_check_input_tokens": fc["input_tokens"],
        "fact_check_output_tokens": fc["output_tokens"],
    }


if __name__ == "__main__":
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()

    with open(f"{RESEARCH_DIR}/vfl.json", encoding="utf-8") as f:
        vfl_data = json.load(f)
    with open(f"{RESEARCH_DIR}/evidence_pack.json", encoding="utf-8") as f:
        evidence_data = json.load(f)

    ledger_text = build_ledger_text_from_vfl(vfl_data["parsed"], evidence_data["parsed"])
    with open(f"{OUT_DIR}/ledger_text.txt", "w", encoding="utf-8") as f:
        f.write(ledger_text)

    common_block = gen.build_common_block(master_full_text, TOPIC_JA, ledger_text)

    results = {}
    for label, instruction in [("B1", gen.B1_B_DIRECT_INSTRUCTION), ("A2", gen.A2_KAI1_INSTRUCTION)]:
        results[label] = run_level(client, label, instruction, common_block, ledger_text,
                                    evidence_data["parsed"])

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    print("完了。")
