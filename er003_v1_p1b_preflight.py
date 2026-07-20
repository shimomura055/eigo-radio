# ============================================================
# er003_v1_p1b_preflight.py
# ER-003-P1B: 実API呼び出し前のプリフライト検証
# ============================================================
# 仕様(ユーザー指示 section 19)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "ER003_P1B_PREFLIGHT_FAILED"として停止する。

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest

import er003_ja_to_en_translation as er003
import er003_ja_to_en_translation_p1b as p1b

FROZEN_FILES = [
    "er003_v1_translator_briefs/translator_prompt_template_p1b.txt",
    "er003_v1_translator_briefs/fidelity_qa_prompt_template.txt",
    "er003_v1_translator_briefs/difficulty_assessment_prompt_template.txt",
]

FORBIDDEN_NEW_CONSTRAINT_TERMS = [
    "cefr", "b2", "b1", "a2", "a1", "vocabulary", "word count", "sentence length",
    "english master", "hanshin", "阪神", "fact_registry", "fact registry",
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


def check_source_matches_p1() -> dict:
    """P1と完全に同一の日本語原稿(sha256一致)を使うこと。P1英訳を入力に
    していないこと。"""
    result = {}
    all_ok = True
    for topic_id in p1b.APPROVED_ARTICLE_SOURCE_PATHS:
        p1_text = er003.load_approved_japanese_article(topic_id)
        p1b_text = p1b.load_approved_japanese_article(topic_id)
        p1_sha = sha256_bytes(p1_text.encode("utf-8"))
        p1b_sha = sha256_bytes(p1b_text.encode("utf-8"))
        match = p1_sha == p1b_sha
        all_ok = all_ok and match
        result[topic_id] = {"p1_sha256": p1_sha, "p1b_sha256": p1b_sha, "match": match}
    result["all_match"] = all_ok

    p1b_builder_params = list(inspect.signature(p1b.build_translator_user_message_p1b).parameters)
    no_p1_translation_input = "english_translation" not in p1b_builder_params and "p1_translation" not in p1b_builder_params
    result["p1b_does_not_accept_p1_translation_as_input"] = no_p1_translation_input
    result["ok"] = all_ok and no_p1_translation_input
    return result


def check_translator_prompt_forbidden_terms() -> dict:
    template = p1b.load_translator_prompt_template_p1b().lower()
    found = [term for term in FORBIDDEN_NEW_CONSTRAINT_TERMS if term in template]
    return {"forbidden_terms_found": found, "ok": not found}


def check_translator_no_web_search_no_structured_output() -> dict:
    src = inspect.getsource(p1b.make_translator_fn)
    no_web_search = '"type": "web_search"' not in src and "tools=" not in src
    no_structured_output = "text={" not in src
    return {
        "no_web_search_tool": no_web_search, "no_structured_output": no_structured_output,
        "ok": no_web_search and no_structured_output,
    }


def check_model_and_reasoning_match_p1() -> dict:
    model_match = p1b.TRANSLATOR_MODEL == er003.TRANSLATOR_MODEL == "gpt-5.6-sol"
    reasoning_match = p1b.TRANSLATOR_REASONING_EFFORT == er003.TRANSLATOR_REASONING_EFFORT == "high"
    return {
        "p1b_model": p1b.TRANSLATOR_MODEL, "p1_model": er003.TRANSLATOR_MODEL,
        "p1b_reasoning_effort": p1b.TRANSLATOR_REASONING_EFFORT, "p1_reasoning_effort": er003.TRANSLATOR_REASONING_EFFORT,
        "ok": model_match and reasoning_match,
    }


def check_single_execution_per_article() -> dict:
    has_batch_fn = any("batch" in name.lower() for name in dir(p1b))
    return {"no_batch_function": not has_batch_fn, "ok": not has_batch_fn}


def check_fidelity_qa_unchanged_from_p1() -> dict:
    ok = (
        p1b.er003.make_fidelity_qa_fn is er003.make_fidelity_qa_fn
        and p1b.er003.run_json_response_gate is er003.run_json_response_gate
        and p1b.er003.parse_and_validate_fidelity_qa_output is er003.parse_and_validate_fidelity_qa_output
    )
    return {"fidelity_qa_functions_identical_to_p1": ok, "ok": ok}


def check_target_scope() -> dict:
    ok = set(p1b.APPROVED_ARTICLE_SOURCE_PATHS.keys()) == {"A01", "A02", "ADD03"}
    return {"topics": list(p1b.APPROVED_ARTICLE_SOURCE_PATHS.keys()), "ok": ok}


def check_regression_tests() -> dict:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in ["er003_test_ja_to_en_translation_p1b", "er003_test_ja_to_en_translation",
                         "er002_test_ja_article_generation"]:
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    with open(os.devnull, "w") as devnull:
        runner = unittest.TextTestRunner(verbosity=0, stream=devnull)
        result = runner.run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "ok": result.wasSuccessful()}


def run_preflight() -> dict:
    result = {
        "experiment_version": p1b.EXPERIMENT_VERSION,
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_prompt_integrity": check_frozen_prompt_integrity(),
        "source_matches_p1": check_source_matches_p1(),
        "translator_prompt_forbidden_terms": check_translator_prompt_forbidden_terms(),
        "translator_no_web_search_no_structured_output": check_translator_no_web_search_no_structured_output(),
        "model_and_reasoning_match_p1": check_model_and_reasoning_match_p1(),
        "single_execution_per_article": check_single_execution_per_article(),
        "fidelity_qa_unchanged_from_p1": check_fidelity_qa_unchanged_from_p1(),
        "target_scope": check_target_scope(),
        "regression_tests": check_regression_tests(),
        "planned_tts_call_count": 0,
    }
    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_prompt_integrity"]["all_match"],
        result["source_matches_p1"]["ok"],
        result["translator_prompt_forbidden_terms"]["ok"],
        result["translator_no_web_search_no_structured_output"]["ok"],
        result["model_and_reasoning_match_p1"]["ok"],
        result["single_execution_per_article"]["ok"],
        result["fidelity_qa_unchanged_from_p1"]["ok"],
        result["target_scope"]["ok"],
        result["regression_tests"]["ok"],
    ]
    result["overall_status"] = "ER003_P1B_PREFLIGHT_PASSED" if all(checks_ok) else "ER003_P1B_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    result = run_preflight()
    os.makedirs("er003_output/p1b", exist_ok=True)
    with open("er003_output/p1b/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "ER003_P1B_PREFLIGHT_PASSED":
        sys.exit(1)
