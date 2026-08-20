# ER-005-SUPPORT-COST-QUALITY-01
# Support Content(Preview/Key Phrases/Comment 1-4)のClean Cost/Quality計測。
# Full Story/Point One/Two/In One Lineは ER-005-WRITER-COST-QUALITY-01 で
# 既に生成済みのため再生成しない。Support生成にはproduction既存機構
# (er003_v1_n3_01_scaffold_generate.py / er003_v1_b1_scaffold_01_generate.py /
# er003_v1_iran01_a2_generate.py / er003_key_words_production.py /
# er003_key_words_canonicalization.py / er003_b1_p2_keywords.py)を無変更で
# importし、モデルのみLuna("gpt-5.6-luna")へ明示的に差し替えて再利用する。
from __future__ import annotations

import json
import os

import er005_cost_logger as cl
import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_production as prod
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_en_direct_vfl_01_generate as vfl01

OUT_DIR = "er005_output/support_cost_quality_01"
os.makedirs(f"{OUT_DIR}/b1/key_phrases", exist_ok=True)
os.makedirs(f"{OUT_DIR}/a2/key_phrases", exist_ok=True)

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

USD_TO_JPY = 160
LUNA_MODEL = "gpt-5.6-luna"

WRITER_DIR = "er005_output/writer_cost_quality_01"

# run_support_text(b1s/a2gen)はモデルを関数呼び出し時にモジュール変数MODEL経由で
# 解決するため、ここでLunaへ差し替える(production側ファイルは一切変更していない)。
b1s.MODEL = LUNA_MODEL
a2gen.MODEL = LUNA_MODEL


# ============================================================
# Key Phrase選定(Strategy L + Canonicalization)をLunaで実行する
# thin wrapper。prod.make_production_selector_fn / kc.make_canonicalization_fn
# はどちらもmodel引数を明示的に受け取れる設計のため、それぞれへ
# model="gpt-5.6-luna"を渡すだけで済む(production側コード自体は無変更)。
# ============================================================
def run_key_phrase_selection_luna(client, article_text: str, out_dir: str, article_id: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(article_text, template=template)
    with open(f"{out_dir}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_selector_factory():
        with cl.logging_context("support_cost_quality", "key_phrase_selection"):
            return prod.make_production_selector_fn(user_message, client=client, model=LUNA_MODEL)

    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, make_selector_factory, article_text,
        strategy_id=prod.STANDARD_STRATEGY_ID, max_attempts=1,
    )
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "article_id": article_id, "model": LUNA_MODEL, "final_status": status,
            "model_id": model_id, "response_id": response_id,
            "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        }, f, ensure_ascii=False, indent=2, default=str)

    result = {"status": status, "parsed": parsed}
    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result
    result["original_items"] = parsed["items"]
    return result


def run_key_phrase_canonicalization_luna(client, article_text: str, original_items: list,
                                          out_dir: str, article_id: str) -> dict:
    template = kc.load_prompt_template()
    user_message = kc.build_user_message(original_items, article_text, template=template)
    with open(f"{out_dir}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        with cl.logging_context("support_cost_quality", "key_phrase_canonicalization"):
            return kc.make_canonicalization_fn(user_message, client=client, model=LUNA_MODEL)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(make_factory, original_items)
    with open(f"{out_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "article_id": article_id, "model": LUNA_MODEL, "final_status": status,
            "model_id": model_id, "response_id": response_id,
            "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        }, f, ensure_ascii=False, indent=2, default=str)

    result = {"status": status}
    if status not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return result
    merged = kc.merge_canonicalization_result(original_items, parsed["items"])
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    result["merged"] = merged
    return result


def run_key_phrases_luna(client, article_text: str, out_dir: str, article_id: str) -> dict:
    sel = run_key_phrase_selection_luna(client, article_text, out_dir, article_id)
    if sel["status"] != "KEY_WORDS_STRUCTURE_PASS":
        return {"selection": sel, "canonicalization": None}
    canon = run_key_phrase_canonicalization_luna(client, article_text, sel["original_items"], out_dir, article_id)
    return {"selection": sel, "canonicalization": canon}


# ============================================================
# Support Fact Check(Luna、web_search不使用、新規実装。
# Support ↔ Article/VFL/Evidence Packの照合)
# ============================================================
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


def run_support_fact_check(client, label: str, support: dict, article_text: str, ledger_text: str) -> dict:
    support_texts = {k: v.get("text") for k, v in support.items()}
    prompt = SUPPORT_FACT_CHECK_PROMPT_TEMPLATE.format(
        support_json=json.dumps(support_texts, ensure_ascii=False, indent=2),
        article_text=article_text, ledger_text=ledger_text,
    )
    with cl.logging_context("support_cost_quality", f"support_fact_check_{label}"):
        resp = client.responses.create(
            model=LUNA_MODEL, reasoning={"effort": "medium"},
            text={"format": {"type": "json_schema", **support_fact_check_schema()}},
            input=[{"role": "developer", "content": SUPPORT_FACT_CHECK_DEVELOPER_MESSAGE},
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
def run_level(client, label: str, run_scaffold_fn, article_text: str, ledger_text: str) -> dict:
    out_dir = f"{OUT_DIR}/{label.lower()}"
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    parts = sc.split_article_text(article_text)
    with open(f"{out_dir}/parts.json", "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)

    print(f"[{label}] Support(Preview/Comment1-4)生成開始...")
    with cl.logging_context("support_cost_quality", f"support_text_{label.lower()}"):
        support = run_scaffold_fn(client, parts, out_dir, article_text)
    print(f"[{label}] Support生成完了。 statuses="
          f"{ {k: v.get('status') for k, v in support.items()} }")

    print(f"[{label}] Key Phrases生成開始...")
    kp_dir = f"{out_dir}/key_phrases"
    kp = run_key_phrases_luna(client, article_text, kp_dir, f"SUPPORT_CQ01_{label}")
    kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
    print(f"[{label}] Key Phrases完了。 status={kp_status}")

    print(f"[{label}] Support Fact Check開始...")
    fc = run_support_fact_check(client, label, support, article_text, ledger_text)
    with open(f"{out_dir}/support_fact_check.json", "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{label}] Support Fact Check完了。 verdict={fc['parsed']['verdict']} "
          f"issues={len(fc['parsed']['issues'])}")

    return {
        "label": label, "parts": parts,
        "support_statuses": {k: v.get("status") for k, v in support.items()},
        "key_phrases_status": kp_status,
        "key_phrases_count": len((kp.get("canonicalization") or {}).get("merged", {}).get("items", []))
                             if kp.get("canonicalization") else 0,
        "fact_check_verdict": fc["parsed"]["verdict"],
        "fact_check_issue_count": len(fc["parsed"]["issues"]),
    }


if __name__ == "__main__":
    client = vfl01.get_client()

    with open(f"{WRITER_DIR}/b1/article.md", encoding="utf-8") as f:
        b1_article_text = f.read()
    with open(f"{WRITER_DIR}/a2/article.md", encoding="utf-8") as f:
        a2_article_text = f.read()
    with open("er005_output/writer_cost_quality_01/ledger_text.txt", encoding="utf-8") as f:
        ledger_text = f.read()

    results = {}
    results["B1"] = run_level(client, "B1", sc.run_b1_scaffold, b1_article_text, ledger_text)
    results["A2"] = run_level(client, "A2", sc.run_a2_scaffold, a2_article_text, ledger_text)

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("完了。")
