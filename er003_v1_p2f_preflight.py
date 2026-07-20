# ============================================================
# er003_v1_p2f_preflight.py
# ER-003-P2F: 実API呼び出し前のプリフライト検証
# ============================================================
# 仕様(ユーザー指示 section 22)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "ER003_P2F_PREFLIGHT_FAILED"として停止する。

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest

import er003_key_words_research10 as r10
import er003_key_words_strategy_compare as p2e
import er003_ja_to_en_translation as er003

FROZEN_FILES = [
    "er003_v1_translator_briefs/b2_key_words_research10_l_prompt_template.txt",
    "er003_v1_translator_briefs/b2_key_words_research10_p_prompt_template.txt",
    "er003_v1_translator_briefs/b2_key_words_research10_u_prompt_template.txt",
    "er003_v1_translator_briefs/b2_key_words_research10_comparison_qa_prompt_template.txt",
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
    for article_id in r10.ARTICLE_IDS:
        summary_path = r10.APPROVED_SUMMARY_PATHS[article_id]
        summary_sha_path = f"er003_output/p2b/{article_id}/summary_approved_sha256.txt"
        with open(summary_path, encoding="utf-8") as f:
            summary_text = f.read()
        with open(summary_sha_path, encoding="utf-8") as f:
            saved_summary_hash = f.read().strip()
        current_summary_hash = er003.sha256_text(summary_text)
        summary_ok = current_summary_hash == saved_summary_hash

        b2_path = r10.B2_INPUT_PATHS[article_id]
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
    """selector入力にA01具体例・P2D/P2E結果が混入していないことを
    確認する。"""
    forbidden_examples = list(p2e.USER_HELPFUL_REFERENCE) + list(p2e.USER_UNHELPFUL_REFERENCE)
    found_in_templates = {}
    all_ok = True
    for strategy_id in r10.STRATEGY_IDS:
        template = r10.load_strategy_prompt_template(strategy_id)
        found = [phrase for phrase in forbidden_examples if phrase in template]
        if found:
            all_ok = False
        found_in_templates[strategy_id] = found

    params = list(inspect.signature(r10.build_strategy_user_message).parameters)
    forbidden_params = [p for p in params if p not in ("strategy_id", "approved_summary",
                                                        "approved_b2_article", "template")]
    if forbidden_params:
        all_ok = False

    return {"forbidden_examples_found_in_templates": found_in_templates,
            "forbidden_params_found": forbidden_params, "ok": all_ok}


def check_no_batch_calls_and_distinct_prompts() -> dict:
    templates = {sid: r10.load_strategy_prompt_template(sid) for sid in r10.STRATEGY_IDS}
    all_distinct = len(set(templates.values())) == 3
    has_batch_fn = (hasattr(r10, "select_all_strategies_in_one_call")
                     or hasattr(r10, "select_all_articles_in_one_call"))
    ok = all_distinct and not has_batch_fn
    return {"all_distinct": all_distinct, "no_batch_function": not has_batch_fn, "ok": ok}


def check_model_and_reasoning() -> dict:
    ok = r10.SELECTOR_MODEL == "gpt-5.6-sol" and r10.SELECTOR_REASONING_EFFORT == "high"
    return {"model": r10.SELECTOR_MODEL, "reasoning_effort": r10.SELECTOR_REASONING_EFFORT, "ok": ok}


def check_no_web_search_no_external_dictionary() -> dict:
    no_web_search = True
    for strategy_id in r10.STRATEGY_IDS:
        fn = r10.make_strategy_selector_fn(strategy_id, "dummy", client=object())
        no_web_search = no_web_search and fn.uses_web_search_tool is False
    src = inspect.getsource(r10).lower()
    no_external_dict = "wordnet" not in src and "dictionary_api" not in src
    ok = no_web_search and no_external_dict
    return {"no_web_search": no_web_search, "no_external_dictionary": no_external_dict, "ok": ok}


def check_schema_guarantees_exactly_10_and_fixed_counts() -> dict:
    result = {}
    all_ok = True
    for strategy_id in r10.STRATEGY_IDS:
        schema_props = r10.RESEARCH10_JSON_SCHEMAS[strategy_id]["schema"]["properties"]
        items_schema = schema_props["items"]
        ok = (items_schema.get("minItems") == 10 and items_schema.get("maxItems") == 10
              and schema_props["research_item_count"]["enum"] == [10]
              and schema_props["production_item_count_unchanged"]["enum"] == [5])
        all_ok = all_ok and ok
        result[strategy_id] = {"minItems": items_schema.get("minItems"), "maxItems": items_schema.get("maxItems"),
                                "research_item_count_enum": schema_props["research_item_count"]["enum"],
                                "production_item_count_unchanged_enum":
                                    schema_props["production_item_count_unchanged"]["enum"], "ok": ok}
    result["ok"] = all_ok
    return result


def check_production_manifest_untouched() -> dict:
    """製品仕様の正式参照manifest(ER-003-P2C)をP2Fが変更しないことを
    ソースから確認する。"""
    src = inspect.getsource(r10)
    ok = "ER-003-P2C_reference_manifest" not in src
    return {"ok": ok}


def check_regression_tests() -> dict:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in ["er003_test_key_words_research10", "er003_test_key_words_strategy_compare",
                         "er003_test_b2_key_words", "er003_test_b2_summary", "er003_test_ja_to_en_translation"]:
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    with open(os.devnull, "w") as devnull:
        runner = unittest.TextTestRunner(verbosity=0, stream=devnull)
        result = runner.run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "ok": result.wasSuccessful()}


def run_preflight() -> dict:
    result = {
        "experiment_version": r10.EXPERIMENT_VERSION,
        "target_article_ids": list(r10.ARTICLE_IDS),
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_prompt_integrity": check_frozen_prompt_integrity(),
        "input_sha256": check_input_sha256(),
        "selector_input_isolation": check_selector_input_isolation(),
        "no_batch_calls_and_distinct_prompts": check_no_batch_calls_and_distinct_prompts(),
        "model_and_reasoning": check_model_and_reasoning(),
        "no_web_search_no_external_dictionary": check_no_web_search_no_external_dictionary(),
        "schema_guarantees_exactly_10_and_fixed_counts": check_schema_guarantees_exactly_10_and_fixed_counts(),
        "production_manifest_untouched": check_production_manifest_untouched(),
        "regression_tests": check_regression_tests(),
        "planned_tts_call_count": 0,
        "planned_selector_call_count": len(r10.ARTICLE_IDS) * len(r10.STRATEGY_IDS),
        "planned_comparison_qa_call_count": len(r10.ARTICLE_IDS),
    }
    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_prompt_integrity"]["all_match"],
        result["input_sha256"]["ok"],
        result["selector_input_isolation"]["ok"],
        result["no_batch_calls_and_distinct_prompts"]["ok"],
        result["model_and_reasoning"]["ok"],
        result["no_web_search_no_external_dictionary"]["ok"],
        result["schema_guarantees_exactly_10_and_fixed_counts"]["ok"],
        result["production_manifest_untouched"]["ok"],
        result["regression_tests"]["ok"],
    ]
    result["overall_status"] = "ER003_P2F_PREFLIGHT_PASSED" if all(checks_ok) else "ER003_P2F_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    result = run_preflight()
    os.makedirs("er003_output/p2f", exist_ok=True)
    with open("er003_output/p2f/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "ER003_P2F_PREFLIGHT_PASSED":
        sys.exit(1)
