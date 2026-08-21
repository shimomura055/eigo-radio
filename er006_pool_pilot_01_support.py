# ============================================================
# er006_pool_pilot_01_support.py
# ER-006-POOL-PILOT-01: Support(Preview/Comment1-4/KeyPhrase)+Support FactCheck
# ============================================================
# er003_v1_n3_01_scaffold_generate.py の本番run_b1_scaffold/run_a2_scaffold/
# run_key_phrasesをそのまま呼び出す(prompt/model設定は無変更、production
# デフォルトのまま)。Support Fact Checkは、er005_support_cost_quality_01.py
# で検証済みの実装(Web Search不使用、Article/Ledgerとの突き合わせのみ)を
# そのまま再利用する。B1/A2それぞれ個別にcl.logging_context()で囲む。

from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cl
import er003_v1_n3_01_scaffold_generate as sc
import er006_model_routing_contract_01 as routing

SUPPORT_FACT_CHECK_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのSupport Content Fact Checkerです。生成されたSupport"
    "(Preview・Comment1〜4)を、記事本文(Article)およびVerified Fact Ledgerと"
    "突き合わせて検証してください。あなた自身はWeb検索を行いません。"
    "以下の観点で問題を探してください: unsupported claim(記事・Ledgerにない主張)、"
    "number drift(数値の変化・誤転記)、causal overstatement、"
    "articleと異なる因果表現、新しいFactの追加、英日間の意味ズレ"
    "(該当する場合のみ)、Level不適合(Supportが本文と同等以上に難しい、"
    "Point/結論の先出し等)。"
)

SUPPORT_FACT_CHECK_PROMPT_TEMPLATE = """【検証対象Support(このLevelのPreview/Comment1-4全体)】
{support_json}

【元記事(Article)】
{article_text}

【Verified Fact Ledger(参考)】
{ledger_text}

【あなたのタスク】
上記のSupportを、Article・Ledgerとのみ突き合わせて検証してください。発見した問題を
issuesとして列挙し(問題が無ければ空配列)、各issueにcomponent(preview/comment_1/
comment_2/comment_3/comment_4のいずれか)、category(unsupported_claim/number_drift/
causal_overstatement/new_fact_added/meaning_shift/level_mismatch)、severity(MINOR/MAJOR)、
description、該当箇所(quote)を記載してください。
最終的にverdictを PASS / MINOR_FIX / MAJOR_FIX / REGENERATE のいずれかで判定してください。"""


def support_fact_check_schema():
    issue_item = {
        "type": "object",
        "properties": {
            "component": {"type": "string", "enum": [
                "preview", "comment_1", "comment_2", "comment_3", "comment_4"]},
            "category": {"type": "string", "enum": [
                "unsupported_claim", "number_drift", "causal_overstatement",
                "new_fact_added", "meaning_shift", "level_mismatch"]},
            "severity": {"type": "string", "enum": ["MINOR", "MAJOR"]},
            "description": {"type": "string"},
            "quote": {"type": "string"},
        },
        "required": ["component", "category", "severity", "description", "quote"],
        "additionalProperties": False,
    }
    return {
        "name": "support_fact_check_result",
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


def run_support_fact_check(client, support: dict, article_text: str, ledger_text: str) -> dict:
    support_texts = {k: v.get("text") for k, v in support.items()}
    prompt = SUPPORT_FACT_CHECK_PROMPT_TEMPLATE.format(
        support_json=json.dumps(support_texts, ensure_ascii=False, indent=2),
        article_text=article_text, ledger_text=ledger_text,
    )
    resp = client.responses.create(
        model=routing.require_model("SUPPORT_FACT_CHECK", routing.SUPPORT_FACT_CHECK_MODEL),
        reasoning={"effort": "medium"},
        text={"format": {"type": "json_schema", **support_fact_check_schema()}},
        input=[{"role": "developer", "content": SUPPORT_FACT_CHECK_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    return {
        "prompt": prompt, "raw_text": resp.output_text, "parsed": json.loads(resp.output_text),
        "model": resp.model, "response_id": resp.id,
        "input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
    }


def run_support_for_theme(client, theme_id: str, out_dir: str, ledger_text: str) -> dict:
    result = {}
    timing = {}
    for label, run_fn, source_level, stage_tag in [
        ("b1b", sc.run_b1_scaffold, "B1-B(N3-01, direct generation)", "support_b1"),
        ("a2", sc.run_a2_scaffold, "A2(V2改1, N3-01)", "support_a2"),
    ]:
        level_out_dir = f"{out_dir}/{label}"
        os.makedirs(f"{level_out_dir}/audit", exist_ok=True)
        with open(f"{level_out_dir}/article.md", encoding="utf-8") as f:
            article_text = f.read()
        parts = sc.split_article_text(article_text)
        with open(f"{level_out_dir}/parts.json", "w", encoding="utf-8") as f:
            json.dump(parts, f, ensure_ascii=False, indent=2)

        t0 = time.time()
        with cl.logging_context(theme_id, stage_tag):
            support = run_fn(client, parts, level_out_dir, article_text)

            kp_dir = f"{level_out_dir}/key_phrases"
            article_id = f"ER006_{theme_id}_{label}"
            kp_process = "B1_SUPPORT" if label == "b1b" else "A2_SUPPORT"
            kp = sc.run_key_phrases(article_text, kp_dir, article_id, source_level, process=kp_process)
            kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]

            fc = run_support_fact_check(client, support, article_text, ledger_text)
        timing[stage_tag] = round(time.time() - t0, 2)

        with open(f"{level_out_dir}/support_fact_check.json", "w", encoding="utf-8") as f:
            json.dump(fc, f, ensure_ascii=False, indent=2, default=str)

        print(f"[{theme_id}] {label}: support={ {k: v.get('status') for k, v in support.items()} } "
              f"kp_status={kp_status} support_fc_verdict={fc['parsed']['verdict']} "
              f"issues={len(fc['parsed']['issues'])}")

        result[label] = {
            "parts": parts, "support_statuses": {k: v.get("status") for k, v in support.items()},
            "key_phrases_status": kp_status,
            "key_phrases_count": len((kp.get("canonicalization") or {}).get("merged", {}).get("items", []))
                                 if kp.get("canonicalization") else 0,
            "support_fact_check_verdict": fc["parsed"]["verdict"],
            "support_fact_check_issue_count": len(fc["parsed"]["issues"]),
        }

    with open(f"{out_dir}/scaffold_run_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/support_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{theme_id}] Support完了。timing={timing}")
    return {"results": result, "timing": timing}


if __name__ == "__main__":
    print("This module is imported by er006_pool_pilot_01_run.py; not run directly.")
