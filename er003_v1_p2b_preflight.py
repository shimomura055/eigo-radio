# ============================================================
# er003_v1_p2b_preflight.py
# ER-003-P2B: 実API呼び出し前のプリフライト検証
# ============================================================
# 仕様(ユーザー指示 section 20)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "ER003_P2B_PREFLIGHT_FAILED"として停止する。

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest

import er003_b2_summary as s

FROZEN_FILES = [
    "er003_v1_translator_briefs/b2_summary_prompt_template.txt",
    "er003_v1_translator_briefs/b2_summary_qa_prompt_template.txt",
]

FORBIDDEN_GENERATOR_TERMS = [
    "natural english source", "natural_english_source", "key words", "key_words",
    "tts", "text-to-speech", "阪神", "hanshin", "fact_registry", "fact registry",
    "japanese_article", "approved_japanese_article",
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


def check_p2a_finalized_as_pass() -> dict:
    """P2Aの正式判定(sentence_metrics_recalculated.json経由)が3記事とも
    PASSであること。run_summary.jsonのsentence_metrics欄が正式指標を
    参照していることも確認する。"""
    result = {}
    all_ok = True
    for topic_id in ("A01", "A02", "ADD03"):
        recalculated_path = f"er003_output/p2/{topic_id}/sentence_metrics_recalculated.json"
        run_summary_path = f"er003_output/p2/{topic_id}_run_summary.json"
        if not (os.path.exists(recalculated_path) and os.path.exists(run_summary_path)):
            all_ok = False
            result[topic_id] = {"ok": False, "reason": "ファイルが見つかりません"}
            continue
        with open(recalculated_path, encoding="utf-8") as f:
            recalculated = json.load(f)
        with open(run_summary_path, encoding="utf-8") as f:
            run_summary = json.load(f)
        official_pass = recalculated["overall_status"] == "B2_SENTENCE_METRICS_PASS"
        run_summary_references_official = (
            run_summary.get("sentence_metrics", {}).get("overall_status") == "B2_SENTENCE_METRICS_PASS"
            and "sentence_metrics_pre_p2a_superseded" in run_summary
        )
        ok = official_pass and run_summary_references_official
        all_ok = all_ok and ok
        result[topic_id] = {"official_metrics_pass": official_pass,
                             "run_summary_references_official_metrics": run_summary_references_official, "ok": ok}
    result["all_finalized_as_pass"] = all_ok
    return result


def check_b2_reading_copy_sha256_unchanged() -> dict:
    result = {}
    all_ok = True
    for topic_id, path in s.B2_INPUT_PATHS.items():
        segments_path = f"er003_output/p2/{topic_id}/sentence_segments.json"
        if not (os.path.exists(path) and os.path.exists(segments_path)):
            all_ok = False
            result[topic_id] = {"ok": False, "reason": "B2 reading copyまたはsentence_segments.jsonが見つかりません"}
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(segments_path, encoding="utf-8") as f:
            segments = json.load(f)
        import er003_ja_to_en_translation as er003
        current_hash = er003.sha256_text(text)
        match = current_hash == segments["source_sha256"]
        all_ok = all_ok and match
        result[topic_id] = {"current_sha256": current_hash, "expected_sha256": segments["source_sha256"], "ok": match}
    result["ok"] = all_ok
    return result


def check_generator_input_composition() -> dict:
    """generator入力にB2本文以外の原稿(日本語原稿・Natural English
    Source・Key Words・TTS指示等)が含まれないことを確認する。"""
    params = list(inspect.signature(s.build_summary_user_message).parameters)
    forbidden_params = [p for p in params if p not in ("approved_b2_article", "template")]
    template = s.load_summary_prompt_template().lower()
    forbidden_terms_found = [term for term in FORBIDDEN_GENERATOR_TERMS if term in template]
    ok = not forbidden_params and not forbidden_terms_found
    return {"forbidden_params_found": forbidden_params, "forbidden_terms_found": forbidden_terms_found, "ok": ok}


def check_generator_no_web_search_no_structured_output() -> dict:
    fn = s.make_summary_generator_fn("dummy", client=object())
    no_web_search = fn.uses_web_search_tool is False
    no_structured_output = fn.response_format_used is False
    return {"no_web_search_tool": no_web_search, "no_structured_output": no_structured_output,
            "ok": no_web_search and no_structured_output}


def check_model_and_reasoning() -> dict:
    ok = s.SUMMARY_MODEL == "gpt-5.6-sol" and s.SUMMARY_REASONING_EFFORT == "high"
    return {"model": s.SUMMARY_MODEL, "reasoning_effort": s.SUMMARY_REASONING_EFFORT, "ok": ok}


def check_single_execution_per_article() -> dict:
    has_batch_fn = any("batch" in name.lower() for name in dir(s))
    return {"no_batch_function": not has_batch_fn, "ok": not has_batch_fn}


def check_regression_tests() -> dict:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in ["er003_test_b2_summary", "er003_test_ja_to_en_translation",
                         "er003_test_ja_to_en_translation_p1b", "er003_test_b2_adapter"]:
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    with open(os.devnull, "w") as devnull:
        runner = unittest.TextTestRunner(verbosity=0, stream=devnull)
        result = runner.run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "ok": result.wasSuccessful()}


def run_preflight() -> dict:
    result = {
        "experiment_version": s.EXPERIMENT_VERSION,
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_prompt_integrity": check_frozen_prompt_integrity(),
        "p2a_finalized_as_pass": check_p2a_finalized_as_pass(),
        "b2_reading_copy_sha256_unchanged": check_b2_reading_copy_sha256_unchanged(),
        "generator_input_composition": check_generator_input_composition(),
        "generator_no_web_search_no_structured_output": check_generator_no_web_search_no_structured_output(),
        "model_and_reasoning": check_model_and_reasoning(),
        "single_execution_per_article": check_single_execution_per_article(),
        "regression_tests": check_regression_tests(),
        "planned_tts_call_count": 0,
        "planned_key_words_call_count": 0,
    }
    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_prompt_integrity"]["all_match"],
        result["p2a_finalized_as_pass"]["all_finalized_as_pass"],
        result["b2_reading_copy_sha256_unchanged"]["ok"],
        result["generator_input_composition"]["ok"],
        result["generator_no_web_search_no_structured_output"]["ok"],
        result["model_and_reasoning"]["ok"],
        result["single_execution_per_article"]["ok"],
        result["regression_tests"]["ok"],
    ]
    result["overall_status"] = "ER003_P2B_PREFLIGHT_PASSED" if all(checks_ok) else "ER003_P2B_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    result = run_preflight()
    os.makedirs("er003_output/p2b", exist_ok=True)
    with open("er003_output/p2b/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "ER003_P2B_PREFLIGHT_PASSED":
        sys.exit(1)
