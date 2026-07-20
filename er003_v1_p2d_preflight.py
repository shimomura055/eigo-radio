# ============================================================
# er003_v1_p2d_preflight.py
# ER-003-P2D: 実API呼び出し前のプリフライト検証
# ============================================================
# 仕様(ユーザー指示 section 24)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "ER003_P2D_PREFLIGHT_FAILED"として停止する。

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest

import er003_b2_key_words as kw
import er003_ja_to_en_translation as er003

FROZEN_FILES = [
    "er003_v1_translator_briefs/b2_key_words_selector_prompt_template.txt",
    "er003_v1_translator_briefs/b2_key_words_qa_prompt_template.txt",
]

FORBIDDEN_SELECTOR_TERMS = [
    "natural english source", "natural_english_source", "japanese_article",
    "approved_japanese_article", "fact_registry", "fact registry", "dictionary_api", "wordnet",
    "阪神", "hanshin", "tts", "text-to-speech",
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


def check_approved_summary_is_official_reference() -> dict:
    """approved概要(summary_en_approved.md)が正式参照先であり、3記事とも
    sha256が保存済みの値と一致することを確認する。"""
    result = {}
    all_ok = True
    for topic_id, path in kw.APPROVED_SUMMARY_PATHS.items():
        sha_path = f"er003_output/p2b/{topic_id}/summary_approved_sha256.txt"
        if not (os.path.exists(path) and os.path.exists(sha_path)):
            all_ok = False
            result[topic_id] = {"ok": False, "reason": "ファイルが見つかりません"}
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(sha_path, encoding="utf-8") as f:
            saved_hash = f.read().strip()
        current_hash = er003.sha256_text(text)
        match = current_hash == saved_hash
        all_ok = all_ok and match
        result[topic_id] = {"current_sha256": current_hash, "saved_sha256": saved_hash, "ok": match}
    result["ok"] = all_ok
    return result


def check_b2_body_sha256_unchanged() -> dict:
    result = {}
    all_ok = True
    for topic_id, path in kw.B2_INPUT_PATHS.items():
        segments_path = f"er003_output/p2/{topic_id}/sentence_segments.json"
        if not (os.path.exists(path) and os.path.exists(segments_path)):
            all_ok = False
            result[topic_id] = {"ok": False, "reason": "B2本文またはsentence_segments.jsonが見つかりません"}
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(segments_path, encoding="utf-8") as f:
            segments = json.load(f)
        current_hash = er003.sha256_text(text)
        match = current_hash == segments["source_sha256"]
        all_ok = all_ok and match
        result[topic_id] = {"current_sha256": current_hash, "expected_sha256": segments["source_sha256"], "ok": match}
    result["ok"] = all_ok
    return result


def check_selector_input_composition() -> dict:
    """selector入力に日本語原稿・Natural English Source等が含まれない
    ことを確認する。"""
    params = list(inspect.signature(kw.build_selector_user_message).parameters)
    forbidden_params = [p for p in params if p not in ("approved_summary", "approved_b2_article", "template")]
    template = kw.load_selector_prompt_template().lower()
    forbidden_terms_found = [term for term in FORBIDDEN_SELECTOR_TERMS if term in template]
    ok = not forbidden_params and not forbidden_terms_found
    return {"forbidden_params_found": forbidden_params, "forbidden_terms_found": forbidden_terms_found, "ok": ok}


def check_selector_no_web_search() -> dict:
    fn = kw.make_selector_fn("dummy", client=object())
    no_web_search = fn.uses_web_search_tool is False
    return {"no_web_search_tool": no_web_search, "ok": no_web_search}


def check_schema_guarantees_exactly_5() -> dict:
    items_schema = kw.KEY_WORDS_JSON_SCHEMA["schema"]["properties"]["items"]
    ok = items_schema.get("minItems") == 5 and items_schema.get("maxItems") == 5
    return {"minItems": items_schema.get("minItems"), "maxItems": items_schema.get("maxItems"), "ok": ok}


def check_model_and_reasoning() -> dict:
    ok = kw.SELECTOR_MODEL == "gpt-5.6-sol" and kw.SELECTOR_REASONING_EFFORT == "high"
    return {"model": kw.SELECTOR_MODEL, "reasoning_effort": kw.SELECTOR_REASONING_EFFORT, "ok": ok}


def check_single_execution_per_article() -> dict:
    has_batch_fn = any("batch" in name.lower() for name in dir(kw))
    return {"no_batch_function": not has_batch_fn, "ok": not has_batch_fn}


def check_regression_tests() -> dict:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in ["er003_test_b2_key_words", "er003_test_b2_summary", "er003_test_b2_summary_p2c",
                         "er003_test_ja_to_en_translation", "er003_test_b2_adapter"]:
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    with open(os.devnull, "w") as devnull:
        runner = unittest.TextTestRunner(verbosity=0, stream=devnull)
        result = runner.run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "ok": result.wasSuccessful()}


def run_preflight() -> dict:
    result = {
        "experiment_version": kw.EXPERIMENT_VERSION,
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_prompt_integrity": check_frozen_prompt_integrity(),
        "approved_summary_is_official_reference": check_approved_summary_is_official_reference(),
        "b2_body_sha256_unchanged": check_b2_body_sha256_unchanged(),
        "selector_input_composition": check_selector_input_composition(),
        "selector_no_web_search": check_selector_no_web_search(),
        "schema_guarantees_exactly_5": check_schema_guarantees_exactly_5(),
        "model_and_reasoning": check_model_and_reasoning(),
        "single_execution_per_article": check_single_execution_per_article(),
        "regression_tests": check_regression_tests(),
        "planned_tts_call_count": 0,
    }
    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_prompt_integrity"]["all_match"],
        result["approved_summary_is_official_reference"]["ok"],
        result["b2_body_sha256_unchanged"]["ok"],
        result["selector_input_composition"]["ok"],
        result["selector_no_web_search"]["ok"],
        result["schema_guarantees_exactly_5"]["ok"],
        result["model_and_reasoning"]["ok"],
        result["single_execution_per_article"]["ok"],
        result["regression_tests"]["ok"],
    ]
    result["overall_status"] = "ER003_P2D_PREFLIGHT_PASSED" if all(checks_ok) else "ER003_P2D_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    result = run_preflight()
    os.makedirs("er003_output/p2d", exist_ok=True)
    with open("er003_output/p2d/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "ER003_P2D_PREFLIGHT_PASSED":
        sys.exit(1)
