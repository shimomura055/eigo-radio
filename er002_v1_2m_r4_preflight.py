# ============================================================
# er002_v1_2m_r4_preflight.py
# ER-002-v1.2M-R4: 実API呼び出し前のプリフライト検証
# 【実験記録・通常運用では使用しないこと】
# ============================================================
# ★★★ ER-002-v1.2M-R4-FINALIZEにより、条件Lは正式採用、条件LBは不採用と
# ★★★ 決定した。このスクリプトはR4比較実験(条件L・条件LB双方)の
# ★★★ プリフライトとして使ったものであり、実験記録として保持している。
# ★★★ 正式な記事生成の前提条件確認は、正式仕様の一部として別途整理する。
#
# 仕様(ユーザー指示 section 18)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "R4_PREFLIGHT_FAILED"として停止する。阪神マスターの読み上げ文字数・
# 許容下限/上限もここで計算・凍結する。
#
# 実行方法(実験再現のみ):
#   .venv/Scripts/python.exe er002_v1_2m_r4_preflight.py

from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import unittest

import er002_ja_web_research_r3 as r3
import er002_ja_web_research_r4 as r4

R4_TOPICS = {
    "A01": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
    "A02": "英国の未成年向け夜間SNS設定",
    "ADD03": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
}

FROZEN_FILES = [
    "er002_v1_2m_masters/hanshin_ja_master.txt",
    "er002_v1_2m_restore_briefs/writer_prompt_template_r3.txt",
    "er002_v1_2m_restore_briefs/length_instruction_suffix_r4.txt",
    "er002_v1_2m_restore_briefs/writer_prompt_template_r4_lb.txt",
]

FORBIDDEN_EDITORIAL_MODULES = [
    "er002_editorial_common", "er002_editorial_angle_adapter", "er002_editorial_runner",
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


def check_frozen_file_integrity() -> dict:
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


def check_master_length_and_bounds() -> dict:
    with open("er002_v1_2m_masters/hanshin_ja_master.txt", encoding="utf-8") as f:
        master_text = f.read()
    count_result = r4.compute_master_char_count_result(master_text)
    lower_bound, upper_bound = r4.compute_length_bounds(count_result["spoken_text_char_count"])
    ok = count_result["status"] == "COUNT_OK" and lower_bound < upper_bound
    return {
        "master_spoken_text_char_count": count_result["spoken_text_char_count"],
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "count_status": count_result["status"],
        "user_reported_master_char_count": 915,
        "measurement_difference_note_ja": (
            "ユーザー報告値(915字)と自動計測値は測定対象・方法が異なる可能性がある"
            "(自動計測はcitation annotation除去+Markdown記号除去+NFKC正規化+空白除去後の"
            "文字数)。差異がある場合はR4完了報告で明示する。"
        ),
        "ok": ok,
    }


def check_condition_l_diff_from_r3(master_count: int, lower_bound: int, upper_bound: int) -> dict:
    with open("er002_v1_2m_masters/hanshin_ja_master.txt", encoding="utf-8") as f:
        master_text = f.read()
    sample_topic = "PREFLIGHT_SAMPLE_TOPIC"
    r3_msg = r3.build_writer_user_message_r3(master_text, sample_topic)
    l_msg = r4.build_writer_user_message_r4_l(master_text, sample_topic, master_count, lower_bound, upper_bound)
    suffix = r4.build_length_instruction_suffix(master_count, lower_bound, upper_bound)
    starts_with_r3 = l_msg.startswith(r3_msg)
    diff_is_exactly_suffix = l_msg == r3_msg + "\n\n" + suffix
    return {
        "starts_with_r3_message": starts_with_r3,
        "diff_is_exactly_length_suffix": diff_is_exactly_suffix,
        "ok": starts_with_r3 and diff_is_exactly_suffix,
    }


def check_condition_lb_length_matches_l(master_count: int, lower_bound: int, upper_bound: int) -> dict:
    with open("er002_v1_2m_masters/hanshin_ja_master.txt", encoding="utf-8") as f:
        master_text = f.read()
    l_suffix = r4.build_length_instruction_suffix(master_count, lower_bound, upper_bound)
    lb_msg = r4.build_writer_user_message_r4_lb(master_text, master_count, lower_bound, upper_bound)
    ok = l_suffix in lb_msg and str(lower_bound) in lb_msg and str(upper_bound) in lb_msg
    return {"length_suffix_present_in_lb": l_suffix in lb_msg, "bounds_present_in_lb": True, "ok": ok}


def check_model_and_reasoning() -> dict:
    writer_ok = r4.WRITER_MODEL == "gpt-5.6-sol" and r4.WRITER_REASONING_EFFORT == "high"
    checker_ok = r3.FACT_CHECKER_MODEL == "gpt-5.6-sol" and r3.FACT_CHECKER_REASONING_EFFORT == "high"
    return {
        "writer_model": r4.WRITER_MODEL, "writer_reasoning_effort": r4.WRITER_REASONING_EFFORT,
        "fact_checker_model": r3.FACT_CHECKER_MODEL, "fact_checker_reasoning_effort": r3.FACT_CHECKER_REASONING_EFFORT,
        "writer_ok": writer_ok, "fact_checker_ok": checker_ok, "ok": writer_ok and checker_ok,
    }


def check_responses_api_and_web_search() -> dict:
    writer_src = inspect.getsource(r3.make_writer_research_fn)
    checker_src = inspect.getsource(r3.make_fact_checker_fn)
    checks = {
        "writer_uses_responses_api": "client.responses.create" in writer_src,
        "checker_uses_responses_api": "client.responses.create" in checker_src,
        "writer_has_web_search_tool": '{"type": "web_search"}' in writer_src,
        "checker_has_web_search_tool": '{"type": "web_search"}' in checker_src,
        "writer_search_query_not_fixed_by_app": '"query":' not in writer_src and '"queries":' not in writer_src,
        "checker_search_query_not_fixed_by_app": '"query":' not in checker_src and '"queries":' not in checker_src,
    }
    checks["ok"] = all(checks.values())
    return checks


def check_no_structured_output_for_writer() -> dict:
    writer_src = inspect.getsource(r3.make_writer_research_fn)
    ok = '"text":' not in writer_src and "text={" not in writer_src
    return {"writer_response_format_absent": ok, "ok": ok}


def check_structure_gate_reused() -> dict:
    tech_gate_src = inspect.getsource(r4.run_writer_technical_gate)
    classify_src = inspect.getsource(r4.classify_writer_diagnostics)
    tech_gate_has_no_structure_check = "validate_point_structure" not in tech_gate_src
    classify_uses_r2_validator = "restore_r2.validate_point_structure" in classify_src
    return {
        "technical_gate_does_not_check_structure": tech_gate_has_no_structure_check,
        "diagnostics_uses_r2_validator": classify_uses_r2_validator,
        "ok": tech_gate_has_no_structure_check and classify_uses_r2_validator,
    }


def check_no_retry_on_length_or_structure() -> dict:
    tech_gate_src = inspect.getsource(r4.run_writer_technical_gate)
    ok = "validate_length" not in tech_gate_src and "web_search_call_count" not in tech_gate_src
    return {"technical_gate_only_checks_technical_failure": ok, "ok": ok}


def check_writer_input_composition() -> dict:
    sample = r3.build_writer_user_message_r3("MASTER_PLACEHOLDER_TEXT", "TOPIC_PLACEHOLDER")
    forbidden_markers = [
        "concise_brief", "fact_registry", "source_url", "verification_status",
        "recommended_angle", "editorial_brief", "past_article", "prior_article",
    ]
    found = [m for m in forbidden_markers if m in sample.lower()]
    return {"forbidden_markers_found": found, "ok": not found}


def check_editorial_pipeline_not_imported() -> dict:
    with open("er002_ja_web_research_r4.py", encoding="utf-8") as f:
        import_lines = [l for l in f.readlines() if l.strip().startswith(("import", "from"))]
    found = [line.strip() for line in import_lines for forbidden in FORBIDDEN_EDITORIAL_MODULES if forbidden in line]
    return {"forbidden_imports_found": found, "ok": not found}


def check_tts_not_referenced() -> dict:
    with open("er002_ja_web_research_r4.py", encoding="utf-8") as f:
        ok = "tts" not in f.read().lower()
    return {"ok": ok}


def check_target_scope() -> dict:
    ok = set(R4_TOPICS.keys()) == {"A01", "A02", "ADD03"}
    return {"topics": R4_TOPICS, "topic_count": len(R4_TOPICS), "ok": ok}


def check_regression_tests() -> dict:
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in [
        "er002_test_ja_web_research_r3",
        "er002_test_ja_web_research_r4",
        "er002_test_ja_free_markdown_restore_r2",
    ]:
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    with open(os.devnull, "w") as devnull:
        runner = unittest.TextTestRunner(verbosity=0, stream=devnull)
        result = runner.run(suite)
    ok = result.wasSuccessful()
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "ok": ok,
    }


def run_preflight() -> dict:
    length_check = check_master_length_and_bounds()
    result = {
        "experiment_version": r4.EXPERIMENT_VERSION,
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_file_integrity": check_frozen_file_integrity(),
        "master_length_and_bounds": length_check,
        "condition_l_diff_from_r3": check_condition_l_diff_from_r3(
            length_check["master_spoken_text_char_count"], length_check["lower_bound"], length_check["upper_bound"]),
        "condition_lb_length_matches_l": check_condition_lb_length_matches_l(
            length_check["master_spoken_text_char_count"], length_check["lower_bound"], length_check["upper_bound"]),
        "model_and_reasoning": check_model_and_reasoning(),
        "responses_api_and_web_search": check_responses_api_and_web_search(),
        "no_structured_output_for_writer": check_no_structured_output_for_writer(),
        "structure_gate_reused": check_structure_gate_reused(),
        "no_retry_on_length_or_structure": check_no_retry_on_length_or_structure(),
        "writer_input_composition": check_writer_input_composition(),
        "editorial_pipeline_not_imported": check_editorial_pipeline_not_imported(),
        "tts_not_referenced": check_tts_not_referenced(),
        "target_scope": check_target_scope(),
        "regression_tests": check_regression_tests(),
        "planned_tts_call_count": 0,
        "planned_old_editorial_brief_pipeline_call_count": 0,
        "planned_structure_or_length_regeneration_count": 0,
    }

    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_file_integrity"]["all_match"],
        result["master_length_and_bounds"]["ok"],
        result["condition_l_diff_from_r3"]["ok"],
        result["condition_lb_length_matches_l"]["ok"],
        result["model_and_reasoning"]["ok"],
        result["responses_api_and_web_search"]["ok"],
        result["no_structured_output_for_writer"]["ok"],
        result["structure_gate_reused"]["ok"],
        result["no_retry_on_length_or_structure"]["ok"],
        result["writer_input_composition"]["ok"],
        result["editorial_pipeline_not_imported"]["ok"],
        result["tts_not_referenced"]["ok"],
        result["target_scope"]["ok"],
        result["regression_tests"]["ok"],
    ]
    result["overall_status"] = "R4_PREFLIGHT_PASSED" if all(checks_ok) else "R4_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    import os
    result = run_preflight()
    os.makedirs("er002_output/v1_2m_r4", exist_ok=True)
    with open("er002_output/v1_2m_r4/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "R4_PREFLIGHT_PASSED":
        sys.exit(1)
