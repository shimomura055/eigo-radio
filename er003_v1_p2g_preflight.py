# ============================================================
# er003_v1_p2g_preflight.py
# ER-003-P2G: 実API呼び出し前のプリフライト検証
# ============================================================
# 仕様(ユーザー指示 section 23)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "ER003_P2G_PREFLIGHT_FAILED"として停止する。

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest

import er003_key_words_min_unit as mu
import er003_key_words_strategy_compare as p2e
import er003_ja_to_en_translation as er003

FROZEN_FILES = [
    "er003_v1_translator_briefs/b2_key_words_min_unit_l_prompt_template.txt",
    "er003_v1_translator_briefs/b2_key_words_min_unit_p_prompt_template.txt",
    "er003_v1_translator_briefs/b2_key_words_min_unit_u_prompt_template.txt",
    "er003_v1_translator_briefs/b2_key_words_min_unit_form_qa_prompt_template.txt",
]


def run(cmd: list) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def run_bytes(cmd: list) -> bytes:
    return subprocess.run(cmd, capture_output=True, check=True).stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_git_head() -> dict:
    return {"head": run(["git", "rev-parse", "HEAD"]).strip()}


def check_tracked_files_clean() -> dict:
    unstaged = [l for l in run(["git", "diff", "--name-only"]).strip().splitlines() if l]
    staged = [l for l in run(["git", "diff", "--cached", "--name-only"]).strip().splitlines() if l]
    return {
        "unstaged_modified_tracked_files": unstaged,
        "staged_uncommitted_files": staged,
        "clean": not unstaged and not staged,
    }


def check_frozen_prompt_integrity() -> dict:
    result = {}
    all_match = True
    for path in FROZEN_FILES:
        committed = run_bytes(["git", "show", f"HEAD:{path}"])
        with open(path, "rb") as f:
            working = f.read()
        committed_hash = sha256_bytes(committed)
        working_hash = sha256_bytes(working)
        match = committed_hash == working_hash
        all_match = all_match and match
        result[path] = {"committed_sha256": committed_hash, "working_tree_sha256": working_hash, "match": match}
    result["all_match"] = all_match
    return result


def check_input_sha256() -> dict:
    result = {}
    all_ok = True
    for article_id in mu.ARTICLE_IDS:
        summary_path = mu.APPROVED_SUMMARY_PATHS[article_id]
        summary_sha_path = f"er003_output/p2b/{article_id}/summary_approved_sha256.txt"
        with open(summary_path, encoding="utf-8") as f:
            summary_text = f.read()
        with open(summary_sha_path, encoding="utf-8") as f:
            saved_summary_hash = f.read().strip()
        current_summary_hash = er003.sha256_text(summary_text)
        summary_ok = current_summary_hash == saved_summary_hash

        b2_path = mu.B2_INPUT_PATHS[article_id]
        segments_path = f"er003_output/p2/{article_id}/sentence_segments.json"
        with open(b2_path, encoding="utf-8") as f:
            b2_text = f.read()
        with open(segments_path, encoding="utf-8") as f:
            segments = json.load(f)
        current_b2_hash = er003.sha256_text(b2_text)
        b2_ok = current_b2_hash == segments["source_sha256"]

        ok = summary_ok and b2_ok
        all_ok = all_ok and ok
        result[article_id] = {
            "approved_summary": {"current_sha256": current_summary_hash, "saved_sha256": saved_summary_hash,
                                  "ok": summary_ok},
            "b2_article": {"current_sha256": current_b2_hash, "expected_sha256": segments["source_sha256"],
                           "ok": b2_ok},
            "ok": ok,
        }
    result["ok"] = all_ok
    return result


def check_selector_input_isolation() -> dict:
    forbidden_examples = list(p2e.USER_HELPFUL_REFERENCE) + list(p2e.USER_UNHELPFUL_REFERENCE)
    forbidden_examples += ["shook global energy supply routes", "the bigger question was whether"]
    found_in_templates = {}
    all_ok = True
    for strategy_id in mu.STRATEGY_IDS:
        template = mu.load_strategy_prompt_template(strategy_id)
        found = [phrase for phrase in forbidden_examples if phrase in template]
        if found:
            all_ok = False
        found_in_templates[strategy_id] = found

    params = list(inspect.signature(mu.build_strategy_user_message).parameters)
    forbidden_params = [p for p in params if p not in ("strategy_id", "approved_summary",
                                                        "approved_b2_article", "template")]
    if forbidden_params:
        all_ok = False

    return {"forbidden_examples_found_in_templates": found_in_templates,
            "forbidden_params_found": forbidden_params, "ok": all_ok}


def check_no_model_self_reported_identifiers() -> dict:
    """article_id/strategy_id/counts/research_bandがmodel schemaに
    一切含まれず、runtimeが決定的に付与することを確認する。"""
    schema_props = mu.SELECTOR_JSON_SCHEMA["schema"]["properties"]
    item_props = schema_props["items"]["items"]["properties"]
    forbidden_top = [f for f in ("article_id", "strategy_id", "research_item_count",
                                  "production_item_count_unchanged") if f in schema_props]
    forbidden_item = [f for f in ("research_band",) if f in item_props]
    ok = not forbidden_top and not forbidden_item
    return {"forbidden_top_level_fields": forbidden_top, "forbidden_item_fields": forbidden_item, "ok": ok}


def check_hard_gates_present() -> dict:
    """1〜5語hard gate・完全文/節禁止gate・基本形正規化要件が存在する
    ことを、既知の受入例で確認する。"""
    accept_case = mu.validate_display_phrase_form("take a different form")
    reject_word_count = mu.validate_display_phrase_form("take the lead in the match today")
    reject_clause = mu.validate_display_phrase_form("the bigger question was whether")
    reject_aux = mu.validate_display_phrase_form("had taken a different form")
    ok = accept_case["ok"] and not reject_word_count["ok"] and not reject_clause["ok"] and not reject_aux["ok"]
    return {
        "accept_case_ok": accept_case["ok"],
        "reject_word_count_ok": not reject_word_count["ok"],
        "reject_clause_ok": not reject_clause["ok"],
        "reject_finite_auxiliary_ok": not reject_aux["ok"],
        "ok": ok,
    }


def check_no_batch_calls_and_distinct_prompts() -> dict:
    templates = {sid: mu.load_strategy_prompt_template(sid) for sid in mu.STRATEGY_IDS}
    all_distinct = len(set(templates.values())) == 3
    has_batch_fn = hasattr(mu, "select_all_in_one_call")
    ok = all_distinct and not has_batch_fn
    return {"all_distinct": all_distinct, "no_batch_function": not has_batch_fn, "ok": ok}


def check_model_and_reasoning() -> dict:
    ok = mu.SELECTOR_MODEL == "gpt-5.6-sol" and mu.SELECTOR_REASONING_EFFORT == "high"
    return {"model": mu.SELECTOR_MODEL, "reasoning_effort": mu.SELECTOR_REASONING_EFFORT, "ok": ok}


def check_no_web_search_no_external_dictionary() -> dict:
    fn = mu.make_strategy_selector_fn("dummy", client=object())
    no_web_search = fn.uses_web_search_tool is False
    src = inspect.getsource(mu).lower()
    no_external_dict = "wordnet" not in src and "dictionary_api" not in src
    ok = no_web_search and no_external_dict
    return {"no_web_search": no_web_search, "no_external_dictionary": no_external_dict, "ok": ok}


def check_blind_mapping_not_exposed_in_module() -> dict:
    """blind mapping自体は保存する仕組みだが、モジュールが方式分析や
    比較ロジックを持たないことを確認する(開示防止の構造的保証)。"""
    ok = not hasattr(mu, "build_strategy_analysis") and not hasattr(mu, "compute_provisional_best_fit")
    return {"ok": ok}


def check_regression_tests() -> dict:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in ["er003_test_key_words_min_unit", "er003_test_key_words_research10",
                         "er003_test_key_words_strategy_compare", "er003_test_b2_key_words",
                         "er003_test_ja_to_en_translation"]:
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    with open(os.devnull, "w") as devnull:
        runner = unittest.TextTestRunner(verbosity=0, stream=devnull)
        result = runner.run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "ok": result.wasSuccessful()}


def run_preflight() -> dict:
    result = {
        "experiment_version": mu.EXPERIMENT_VERSION,
        "target_article_ids": list(mu.ARTICLE_IDS),
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_prompt_integrity": check_frozen_prompt_integrity(),
        "input_sha256": check_input_sha256(),
        "selector_input_isolation": check_selector_input_isolation(),
        "no_model_self_reported_identifiers": check_no_model_self_reported_identifiers(),
        "hard_gates_present": check_hard_gates_present(),
        "no_batch_calls_and_distinct_prompts": check_no_batch_calls_and_distinct_prompts(),
        "model_and_reasoning": check_model_and_reasoning(),
        "no_web_search_no_external_dictionary": check_no_web_search_no_external_dictionary(),
        "blind_mapping_not_exposed_in_module": check_blind_mapping_not_exposed_in_module(),
        "regression_tests": check_regression_tests(),
        "planned_tts_call_count": 0,
        "planned_selector_call_count": len(mu.ARTICLE_IDS) * len(mu.STRATEGY_IDS),
        "planned_form_qa_call_count": len(mu.ARTICLE_IDS),
    }
    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_prompt_integrity"]["all_match"],
        result["input_sha256"]["ok"],
        result["selector_input_isolation"]["ok"],
        result["no_model_self_reported_identifiers"]["ok"],
        result["hard_gates_present"]["ok"],
        result["no_batch_calls_and_distinct_prompts"]["ok"],
        result["model_and_reasoning"]["ok"],
        result["no_web_search_no_external_dictionary"]["ok"],
        result["blind_mapping_not_exposed_in_module"]["ok"],
        result["regression_tests"]["ok"],
    ]
    result["overall_status"] = "ER003_P2G_PREFLIGHT_PASSED" if all(checks_ok) else "ER003_P2G_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    result = run_preflight()
    os.makedirs("er003_output/p2g", exist_ok=True)
    with open("er003_output/p2g/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "ER003_P2G_PREFLIGHT_PASSED":
        sys.exit(1)
