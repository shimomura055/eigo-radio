#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-009-N1-POINT-RETRY-ROUTING-GOVERNANCE-10 (No.9 A2 Point Overlap Retry)

No.9 A2(Storytelling First + No Jargon)のPoint overlap NG(Trial-08実測:
Point One 0.409 / Point Two 0.542)に対し、Production正式仕様
(er003_v1_n3_01_articles_generate.py::run_one_pattern()の
POINT_OVERLAP_ARTICLE_RETRY_MAX=2ループ)と同じ挙動をDEVスクリプトとして
再現し、実際にLuna(Routing SSOT経由、fail-closed)でRetryする。

Writer instruction(Storytelling First + No Jargon + Hook許容)は
Trial-08(er009_n1_full_writer_ledger_integration_08.py)のprompt定数を
そのままimportして再利用する(同一条件での比較のため、文言を複製しない)。

Production Prompt本体への配線・Ledger局所RewriteのProduction配線・
Hook-aware Checker・Audio再生成は行わない(観察・検証のみ)。
Point-only regenerationは使用しない(Production同様、NGなら全文Retry)。
"""
from __future__ import annotations

import json
import os

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_point_overlap_qa_18 as overlap_qa
import er009_n1_full_writer_ledger_integration_08 as trial08
import er009_n1_routing_governance_10_actual_model_cost as cost_calc

OUT_DIR = "er009_output/point_retry_luna_10"
COST_LOG_PATH = f"{OUT_DIR}/cost_log.jsonl"
RESULTS_PATH = f"{OUT_DIR}/results.json"

os.makedirs(OUT_DIR, exist_ok=True)
cl.install(COST_LOG_PATH)  # global _LOG_PATHをこのRunの専用ログへ切り替える(SDK patchはtrial08 import時に既に適用済み)

client = OpenAI()

# ER-006-MODEL-ROUTING-CONTRACT-01のSSOTをfail-closedで直接呼ぶ。Trial-08の
# 根本原因(model=MODELという迂回変数の直接使用)を繰り返さない。
WRITER_MODEL = routing.require_model("A2_WRITER", routing.WRITER_MODEL)

# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22で確定したProduction仕様と
# 完全に同じ値(er003_v1_n3_01_articles_generate.POINT_OVERLAP_ARTICLE_RETRY_MAX)。
POINT_OVERLAP_ARTICLE_RETRY_MAX = 2


def generate_full_article_a2(attempt_label: str) -> dict:
    prompt = trial08.FULL_ARTICLE_PROMPT_TEMPLATE.format(
        level="A2", topic_ja=trial08.TOPIC_JA, title_en=trial08.TITLE_EN,
        register_note=trial08.REGISTER_NOTE["A2"], storytelling_first=trial08.STORYTELLING_FIRST,
        no_jargon=trial08.NO_JARGON, hook_guidance=trial08.HOOK_GUIDANCE,
        point_role_spec=trial08.POINT_ROLE_SPEC, ledger_text=trial08.VERIFIED_LEDGER_TEXT,
    )
    with cl.logging_context("point_retry_luna_10", f"writer_full_article_a2_{attempt_label}"):
        response = client.responses.create(
            model=WRITER_MODEL,
            reasoning={"effort": trial08.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **trial08.full_article_schema()}},
            input=[
                {"role": "developer", "content": trial08.FULL_ARTICLE_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    return json.loads(response.output_text)


def check_point_overlap(article_clean: dict, full_story_clean: str) -> dict:
    o1 = overlap_qa.flag_possible_paraphrase(article_clean["point_one_body"], full_story_clean)
    o2 = overlap_qa.flag_possible_paraphrase(article_clean["point_two_body"], full_story_clean)
    return {"point_one": o1, "point_two": o2, "flagged": bool(o1["flagged"] or o2["flagged"])}


def run_ledger_check_final(article_text: str) -> dict:
    with cl.logging_context("point_retry_luna_10", "ledger_check_final"):
        result = vfl01.run_deviation_check(client, trial08.VERIFIED_LEDGER_TEXT, article_text,
                                            model=WRITER_MODEL)
    parsed = result["parsed"]
    major = [d for d in parsed["deviations"] if d["severity"] == "MAJOR"]
    minor = [d for d in parsed["deviations"] if d["severity"] == "MINOR"]
    return {"overall_status": parsed["overall_status"], "major": major, "minor": minor}


def run_local_rewrite_if_major(article_text: str, ledger_result: dict):
    """Ledger MAJORが出た場合のみ、Trial-08で検証済みの局所Rewrite Rule
    (trial08.rewrite_ng_item、無変更で再利用)を適用する。Production配線
    ではなくDEV検証としての適用(タスク仕様item 9/15参照)。"""
    if not ledger_result["major"]:
        return None
    sentences = trial08.split_sentences(article_text)
    rewrite_results = []
    for idx, deviation in enumerate(ledger_result["major"], start=1):
        target, location_method = trial08.locate_target_sentence(
            deviation["claim_in_article"], article_text)
        if target is None:
            rewrite_results.append({
                "item_idx": idx, "resolved": False, "human_review_required": True,
                "location_method": "not_found",
            })
            continue
        try:
            sidx = sentences.index(target)
        except ValueError:
            sidx = -1
        before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
        after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
        with cl.logging_context("point_retry_luna_10", f"local_rewrite_item{idx}"):
            r = trial08.rewrite_ng_item("A2", idx, target, deviation, before_ctx, after_ctx)
        r["location_method"] = location_method
        rewrite_results.append(r)
    patched_text = trial08.apply_rewrites(article_text, rewrite_results)
    with cl.logging_context("point_retry_luna_10", "ledger_check_after_local_rewrite"):
        recheck = run_ledger_check_final(patched_text)
    return {"rewrite_results": rewrite_results, "patched_article_text": patched_text,
            "ledger_recheck": recheck}


def main():
    attempts_log = []
    final_article_clean = None
    final_full_story_clean = None
    status = None

    for attempt in range(0, POINT_OVERLAP_ARTICLE_RETRY_MAX + 1):
        label = "initial" if attempt == 0 else f"retry{attempt}"
        print(f"\n{'='*70}\nAttempt {attempt} ({label}): A2 Full Article生成(model={WRITER_MODEL})\n{'='*70}")
        article = generate_full_article_a2(label)
        hooks = trial08.extract_hooks(article["full_story"])
        full_story_clean = trial08.strip_hook_markers(article["full_story"])
        article_clean = dict(article)
        article_clean["full_story"] = full_story_clean

        overlap = check_point_overlap(article_clean, full_story_clean)
        jargon_found = trial08.detect_jargon(" ".join([
            full_story_clean, article["point_one_body"], article["point_two_body"], article["in_one_line"]]))

        print(f"[Attempt {attempt}] Point One overlap={overlap['point_one']['overlap_ratio']} "
              f"Point Two overlap={overlap['point_two']['overlap_ratio']} flagged={overlap['flagged']} "
              f"Hooks={len(hooks)} Jargon={jargon_found}")

        attempts_log.append({
            "attempt": attempt, "label": label, "model": WRITER_MODEL,
            "article_raw": article, "hooks_count": len(hooks), "jargon_found": jargon_found,
            "point_overlap": {
                "point_one_ratio": overlap["point_one"]["overlap_ratio"],
                "point_one_shared_words": overlap["point_one"]["shared_words"],
                "point_two_ratio": overlap["point_two"]["overlap_ratio"],
                "point_two_shared_words": overlap["point_two"]["shared_words"],
                "flagged": overlap["flagged"],
            },
        })

        final_article_clean = article_clean
        final_full_story_clean = full_story_clean

        if not overlap["flagged"]:
            status = "PASS"
            break
        if attempt >= POINT_OVERLAP_ARTICLE_RETRY_MAX:
            status = "NG_REVIEW_REQUIRED"
            break
        print(f"[Attempt {attempt}] Point overlap NG。記事全体をWriterから再生成します"
              f"(Production仕様と同じくPoint-only regenerationは使用しない)。")

    article_text_final = trial08.build_article_md("A2", final_article_clean, final_full_story_clean)

    print(f"\n{'='*70}\nRetry Loop終了: status={status}\n{'='*70}")

    ledger_result = None
    local_rewrite = None
    if status == "PASS":
        print("最終Ledger Deviation Check(全文、1回のみ、Production仕様通り)...")
        ledger_result = run_ledger_check_final(article_text_final)
        print(f"Ledger結果: {ledger_result['overall_status']} "
              f"MAJOR={len(ledger_result['major'])} MINOR={len(ledger_result['minor'])}")
        local_rewrite = run_local_rewrite_if_major(article_text_final, ledger_result)
        if local_rewrite:
            print(f"Ledger MAJOR検出。局所Rewrite適用後: "
                  f"{local_rewrite['ledger_recheck']['overall_status']}")
            article_text_final = local_rewrite["patched_article_text"]
    else:
        print("status=NG_REVIEW_REQUIRED のため、Production仕様通りFact Checker/"
              "Ledger Deviation Checkは実行しません。")

    cost_summary = cost_calc.summarize_cost_log(COST_LOG_PATH)

    output = {
        "status": status,
        "writer_model_used": WRITER_MODEL,
        "point_overlap_article_retry_max": POINT_OVERLAP_ARTICLE_RETRY_MAX,
        "attempts": attempts_log,
        "final_article_text": article_text_final,
        "final_ledger_check": ledger_result,
        "local_rewrite": local_rewrite,
        "cost_summary": cost_summary,
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n結果を保存しました: {RESULTS_PATH}")
    print(f"総Cost: {cost_summary['total_cost_jpy']}円 ({cost_summary['total_calls']} calls)")
    print(f"使用modelの内訳: "
          f"{sorted(set(c['model_id'] for c in cost_summary['per_call']))}")


if __name__ == "__main__":
    main()
