# ============================================================
# er003_v1_p1_preflight.py
# ER-003-P1: 実API呼び出し前のプリフライト検証
# ============================================================
# 仕様(ユーザー指示 section 18)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "ER003_P1_PREFLIGHT_FAILED"として停止する。

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest

import er003_ja_to_en_translation as er003

FROZEN_FILES = [
    "er003_v1_translator_briefs/translator_prompt_template.txt",
    "er003_v1_translator_briefs/fidelity_qa_prompt_template.txt",
    "er003_v1_translator_briefs/difficulty_assessment_prompt_template.txt",
]

FORBIDDEN_TRANSLATOR_INPUT_TERMS = [
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


def check_source_articles() -> dict:
    """翻訳元が条件Lの承認済み日本語記事(reading_copy.md)であること、
    3記事すべてが揃っていること、sha256を記録する。"""
    result = {}
    all_ok = True
    for topic_id, path in er003.APPROVED_ARTICLE_SOURCE_PATHS.items():
        exists = os.path.exists(path)
        is_condition_l = "condition_l" in path and path.endswith("reading_copy.md")
        sha256 = None
        if exists:
            with open(path, "rb") as f:
                sha256 = sha256_bytes(f.read())
        ok = exists and is_condition_l
        all_ok = all_ok and ok
        result[topic_id] = {"path": path, "exists": exists, "is_condition_l_reading_copy": is_condition_l,
                             "sha256": sha256, "ok": ok}
    result["all_three_present"] = all_ok
    return result


def check_translator_prompt_forbidden_terms() -> dict:
    template = er003.load_translator_prompt_template().lower()
    found = [term for term in FORBIDDEN_TRANSLATOR_INPUT_TERMS if term in template]
    return {"forbidden_terms_found": found, "ok": not found}


def check_translator_no_web_search_no_structured_output() -> dict:
    src = inspect.getsource(er003.make_translator_fn)
    no_web_search = '"type": "web_search"' not in src and "tools=" not in src
    no_structured_output = "text={" not in src
    return {
        "no_web_search_tool": no_web_search, "no_structured_output": no_structured_output,
        "ok": no_web_search and no_structured_output,
    }


def check_qa_and_difficulty_no_web_search() -> dict:
    qa_src = inspect.getsource(er003.make_fidelity_qa_fn)
    diff_src = inspect.getsource(er003.make_difficulty_assessment_fn)
    qa_ok = '"type": "web_search"' not in qa_src and "tools=" not in qa_src
    diff_ok = '"type": "web_search"' not in diff_src and "tools=" not in diff_src
    return {"fidelity_qa_no_web_search": qa_ok, "difficulty_no_web_search": diff_ok, "ok": qa_ok and diff_ok}


def check_model_and_reasoning() -> dict:
    ok = er003.TRANSLATOR_MODEL == "gpt-5.6-sol" and er003.TRANSLATOR_REASONING_EFFORT == "high"
    return {
        "translator_model": er003.TRANSLATOR_MODEL, "translator_reasoning_effort": er003.TRANSLATOR_REASONING_EFFORT,
        "fidelity_qa_model": er003.FIDELITY_QA_MODEL, "difficulty_model": er003.DIFFICULTY_MODEL,
        "ok": ok,
    }


def check_single_execution_per_article() -> dict:
    # モジュール内にバッチ翻訳関数が存在しないこと(1記事1実行の構造的保証)
    has_batch_fn = any("batch" in name.lower() for name in dir(er003))
    uses_shared_technical_gate = er003.run_translator_technical_gate is er003.article_gen.run_writer_technical_gate
    ok = (not has_batch_fn) and uses_shared_technical_gate
    return {"no_batch_function": not has_batch_fn, "reuses_shared_technical_gate": uses_shared_technical_gate, "ok": ok}


def check_target_scope() -> dict:
    ok = set(er003.APPROVED_ARTICLE_SOURCE_PATHS.keys()) == {"A01", "A02", "ADD03"}
    return {"topics": list(er003.APPROVED_ARTICLE_SOURCE_PATHS.keys()), "ok": ok}


def check_regression_tests() -> dict:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in ["er003_test_ja_to_en_translation", "er002_test_ja_article_generation",
                         "er002_test_ja_web_research_r3"]:
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    with open(os.devnull, "w") as devnull:
        runner = unittest.TextTestRunner(verbosity=0, stream=devnull)
        result = runner.run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "ok": result.wasSuccessful()}


def run_preflight() -> dict:
    result = {
        "experiment_version": er003.EXPERIMENT_VERSION,
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_prompt_integrity": check_frozen_prompt_integrity(),
        "source_articles": check_source_articles(),
        "translator_prompt_forbidden_terms": check_translator_prompt_forbidden_terms(),
        "translator_no_web_search_no_structured_output": check_translator_no_web_search_no_structured_output(),
        "qa_and_difficulty_no_web_search": check_qa_and_difficulty_no_web_search(),
        "model_and_reasoning": check_model_and_reasoning(),
        "single_execution_per_article": check_single_execution_per_article(),
        "target_scope": check_target_scope(),
        "regression_tests": check_regression_tests(),
        "planned_tts_call_count": 0,
    }
    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_prompt_integrity"]["all_match"],
        result["source_articles"]["all_three_present"],
        result["translator_prompt_forbidden_terms"]["ok"],
        result["translator_no_web_search_no_structured_output"]["ok"],
        result["qa_and_difficulty_no_web_search"]["ok"],
        result["model_and_reasoning"]["ok"],
        result["single_execution_per_article"]["ok"],
        result["target_scope"]["ok"],
        result["regression_tests"]["ok"],
    ]
    result["overall_status"] = "ER003_P1_PREFLIGHT_PASSED" if all(checks_ok) else "ER003_P1_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    result = run_preflight()
    os.makedirs("er003_output/p1", exist_ok=True)
    with open("er003_output/p1/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "ER003_P1_PREFLIGHT_PASSED":
        sys.exit(1)
