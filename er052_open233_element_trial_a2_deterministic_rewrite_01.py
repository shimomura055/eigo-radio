# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_element_trial_a2_deterministic_rewrite_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_27 Part2、Trial A-2)
# ============================================================
# 目的: §1-2「用語の範囲違い→名詞句だけ置換」の初期単位を、決定論
# (文字列置換、LLM Rewrite callを使わない)で実施し、文全体の語順・
# ストーリーが保持されることをdiffで示す。段落Rewriteへは進まない。
# 対象1件(原文②、JA/EN対、"Oil prices"→"Brent futures"/
# 「原油価格」→「Brent先物」)についてのみ、既存Production資産
# (er003_ja_to_en_translation.pyの翻訳忠実性QA)を借用した局所QA 1 call
# で、Rewrite後の記事全文がLedger整合・周辺影響・JA/EN等価の観点で
# 問題ないかを確認する(既存run_ja_en_equivalence_checkと同一原則、
# 本ファイル自身のbudget stateで完結させ他委任の証跡を汚染しない)。
# NG群のうち"gasoline prices"/"world energy prices"の2件はEN単体
# 構成claim(JA対訳が無い)のため、決定論diffのみで確認する(API call
# 不要、¥0)。
#
# 重要な設計制約:
# - Production code(er003/er006/er009/er010/er012/er019)は一切変更しない。
# - API keyは環境変数のみ。保存jsonにはprompt本体ではなくsha256のみ記録。
from __future__ import annotations

import difflib
import hashlib
import json
import os
import time

import er003_ja_to_en_translation as jtr
import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_element_trial_hormuz_terms_01 as elem
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_element_trial_hormuz_terms_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233ad_a2.json"
TOTAL_BUDGET_JPY = 4.0  # 委任_27 Part2 Trial A-2 Guardrail(小修正1回分の枠内)


def load_budget_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def save_budget_state(state: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_STATE_PATH), exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def word_diff(before: str, after: str) -> list:
    """決定論(¥0)のword-level diff。置換が対象名詞句のみで、文の語順・
    ストーリーの他部分が保持されていることを示す。"""
    sm = difflib.SequenceMatcher(None, before.split(), after.split())
    return [{"op": op, "before": before.split()[i1:i2], "after": after.split()[j1:j2]}
            for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]


def main():
    hormuz, _claims = elem.build_claims()
    en_full = hormuz["article_text"]
    ja_full = hormuz["source_article_text"]

    results = {}

    # ---- (1) ng-1: gasoline prices(EN単体、決定論diffのみ、¥0) ----
    ng1_before = "Gasoline prices did not fall across the whole market after the plan was withdrawn."
    ng1_after = ng1_before.replace("Gasoline prices", "Brent futures")
    results["ng1_gasoline_to_brent"] = {
        "before": ng1_before, "after": ng1_after, "word_diff": word_diff(ng1_before, ng1_after),
    }

    # ---- (2) ng-2: world energy prices(EN単体、決定論diffのみ、¥0) ----
    ng2_before = ("World energy prices did not fall after the plan was withdrawn, and stayed high "
                  "across all energy markets.")
    ng2_after = ng2_before.replace("World energy prices", "Brent futures")
    results["ng2_world_energy_to_brent"] = {
        "before": ng2_before, "after": ng2_after, "word_diff": word_diff(ng2_before, ng2_after),
    }

    # ---- (3) 原文②(JA/EN対、決定論置換+局所QA1call) ----
    en_target = "Political statements changed greatly. Oil prices moved briefly, then returned to a high level."
    ja_target = "政治の発言が大きく変わっても、原油価格は一度揺れたあと、高い水準へ戻った。"
    assert en_target in en_full, "EN target not found verbatim in real article(捏造防止チェック)"
    assert ja_target in ja_full, "JA target not found verbatim in real article(捏造防止チェック)"

    en_after_sentence = en_target.replace("Oil prices", "Brent futures")
    ja_after_sentence = ja_target.replace("原油価格", "Brent先物")
    en_full_after = en_full.replace(en_target, en_after_sentence, 1)
    ja_full_after = ja_full.replace(ja_target, ja_after_sentence, 1)

    results["el2_oilprices_to_brent"] = {
        "before_sentence": en_target, "after_sentence": en_after_sentence,
        "before_sentence_ja": ja_target, "after_sentence_ja": ja_after_sentence,
        "word_diff_en": word_diff(en_target, en_after_sentence),
        "word_diff_ja_char_level": [
            {"op": op, "before": ja_target[i1:i2], "after": ja_after_sentence[j1:j2]}
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(
                None, ja_target, ja_after_sentence).get_opcodes() if op != "equal"
        ],
        "full_article_unchanged_elsewhere": (
            en_full.replace(en_target, "") == en_full_after.replace(en_after_sentence, "")
            and ja_full.replace(ja_target, "") == ja_full_after.replace(ja_after_sentence, "")
        ),
    }

    # ---- 局所QA 1 call(既存Production翻訳忠実性QA資産をread-onlyで借用、
    # 本ファイル自身のbudget stateで完結) ----
    state = load_budget_state()
    if state["cumulative_jpy"] < TOTAL_BUDGET_JPY:
        client = vfl01.get_client()
        prompt = jtr.build_fidelity_qa_prompt(ja_full_after, en_full_after)
        t0 = time.time()
        response = client.responses.create(
            model=s2p.MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
            text={"format": {"type": "json_schema", **jtr.FIDELITY_QA_JSON_SCHEMA}},
            input=prompt,
        )
        elapsed = round(time.time() - t0, 3)
        parsed = jtr.parse_and_validate_fidelity_qa_output(response.output_text)
        usage = s2p._extract_usage(response)
        cost = round(s2p.official_cost_jpy(usage), 4)
        state["cumulative_jpy"] += cost
        state["cumulative_calls"] += 1
        state["history"].append({"label": "el2_oilprices_to_brent_local_qa", "cost_jpy": cost, "usage": usage})
        save_budget_state(state)
        results["el2_local_qa"] = {
            "verdict": parsed.get("verdict"), "notes": parsed.get("notes"),
            "meaning_changes": parsed.get("meaning_changes"),
            "unsupported_additions": parsed.get("unsupported_additions"),
            "number_name_negation_issues": parsed.get("number_name_negation_issues"),
            "cost_jpy": cost, "elapsed_seconds": elapsed,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        }

    summary = {
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
    }
    save_json(f"{OUT_DIR}/trial_a2_deterministic_rewrite.json", {"summary": summary, "results": results})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in results.items() if k == "el2_local_qa"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
