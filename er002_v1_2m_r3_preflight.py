# ============================================================
# er002_v1_2m_r3_preflight.py
# ER-002-v1.2M-R3: 実API呼び出し前のプリフライト検証
# ============================================================
# 仕様(ユーザー指示 section 13)の全項目を実API呼び出し無しで検証する。
# いずれか1項目でも不一致であれば、APIを一切呼ばずoverall_status=
# "R3_PREFLIGHT_FAILED"として停止する。
#
# 実行方法:
#   .venv/Scripts/python.exe er002_v1_2m_r3_preflight.py

from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import sys

import er002_ja_web_research_r3 as r3

R3_TOPICS = {
    "A01": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
    "A02": "英国の未成年向け夜間SNS設定",
    "ADD03": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
}

FROZEN_FILES = [
    "er002_v1_2m_masters/hanshin_ja_master.txt",
    "er002_v1_2m_restore_briefs/writer_prompt_template_r3.txt",
    "er002_v1_2m_restore_briefs/fact_checker_prompt_template_r3.txt",
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
    actual = run(["git", "rev-parse", "HEAD"]).strip()
    return {"head": actual}


def check_tracked_files_clean() -> dict:
    unstaged = run(["git", "diff", "--name-only"]).strip()
    staged = run(["git", "diff", "--cached", "--name-only"]).strip()
    unstaged_lines = [l for l in unstaged.splitlines() if l]
    staged_lines = [l for l in staged.splitlines() if l]
    return {
        "unstaged_modified_tracked_files": unstaged_lines,
        "staged_uncommitted_files": staged_lines,
        "clean": not unstaged_lines and not staged_lines,
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
        result[path] = {
            "committed_sha256": committed_hash,
            "working_tree_sha256": working_hash,
            "match": match,
        }
    result["all_match"] = all_match
    return result


def check_model_and_reasoning() -> dict:
    writer_ok = r3.WRITER_MODEL == "gpt-5.6-sol" and r3.WRITER_REASONING_EFFORT == "high"
    checker_ok = r3.FACT_CHECKER_MODEL == "gpt-5.6-sol" and r3.FACT_CHECKER_REASONING_EFFORT == "high"
    return {
        "writer_model": r3.WRITER_MODEL,
        "writer_reasoning_effort": r3.WRITER_REASONING_EFFORT,
        "fact_checker_model": r3.FACT_CHECKER_MODEL,
        "fact_checker_reasoning_effort": r3.FACT_CHECKER_REASONING_EFFORT,
        "writer_ok": writer_ok,
        "fact_checker_ok": checker_ok,
        "ok": writer_ok and checker_ok,
    }


def check_responses_api_and_web_search() -> dict:
    writer_src = inspect.getsource(r3.make_writer_research_fn)
    checker_src = inspect.getsource(r3.make_fact_checker_fn)
    writer_uses_responses_api = "client.responses.create" in writer_src
    checker_uses_responses_api = "client.responses.create" in checker_src
    writer_has_web_search = '{"type": "web_search"}' in writer_src
    checker_has_web_search = '{"type": "web_search"}' in checker_src
    writer_no_fixed_query = '"query":' not in writer_src and '"queries":' not in writer_src
    checker_no_fixed_query = '"query":' not in checker_src and '"queries":' not in checker_src
    return {
        "writer_uses_responses_api": writer_uses_responses_api,
        "checker_uses_responses_api": checker_uses_responses_api,
        "writer_has_web_search_tool": writer_has_web_search,
        "checker_has_web_search_tool": checker_has_web_search,
        "writer_search_query_not_fixed_by_app": writer_no_fixed_query,
        "checker_search_query_not_fixed_by_app": checker_no_fixed_query,
        "ok": all([
            writer_uses_responses_api, checker_uses_responses_api,
            writer_has_web_search, checker_has_web_search,
            writer_no_fixed_query, checker_no_fixed_query,
        ]),
    }


def check_no_pre_summarization_step() -> dict:
    with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
        src = f.read().lower()
    forbidden = ["summarize", "summarise", "要約する関数"]
    found = [term for term in forbidden if term in src]
    return {"forbidden_terms_found": found, "ok": not found}


def check_no_structured_output_for_writer() -> dict:
    writer_src = inspect.getsource(r3.make_writer_research_fn)
    ok = '"text":' not in writer_src and "text={" not in writer_src
    return {"writer_response_format_absent": ok, "ok": ok}


def check_structure_gate_active() -> dict:
    gate_src = inspect.getsource(r3.run_writer_with_gates)
    ok = "restore_r2.validate_point_structure" in gate_src
    return {"uses_r2_validator": ok, "ok": ok}


def check_writer_input_composition() -> dict:
    sample = r3.build_writer_user_message_r3("MASTER_PLACEHOLDER_TEXT", "TOPIC_PLACEHOLDER")
    forbidden_markers = [
        "concise_brief", "fact_registry", "source_url", "verification_status",
        "recommended_angle", "editorial_brief", "past_article", "prior_article",
    ]
    found = [m for m in forbidden_markers if m in sample.lower()]
    params = list(inspect.signature(r3.build_writer_user_message_r3).parameters)
    forbidden_params = [p for p in params if p not in ("master_full_text", "topic", "template")]
    return {
        "forbidden_markers_found": found,
        "forbidden_params_found": forbidden_params,
        "ok": not found and not forbidden_params,
    }


def check_editorial_pipeline_not_imported() -> dict:
    with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
        import_lines = [l for l in f.readlines() if l.strip().startswith(("import", "from"))]
    found = []
    for line in import_lines:
        for forbidden in FORBIDDEN_EDITORIAL_MODULES:
            if forbidden in line:
                found.append(line.strip())
    return {"forbidden_imports_found": found, "ok": not found}


def check_tts_not_referenced() -> dict:
    with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
        src = f.read().lower()
    ok = "tts" not in src
    return {"tts_referenced": not ok, "ok": ok}


def check_target_scope() -> dict:
    ok = len(R3_TOPICS) == 3
    return {"topics": R3_TOPICS, "topic_count": len(R3_TOPICS), "ok": ok}


def run_preflight() -> dict:
    result = {
        "experiment_version": r3.EXPERIMENT_VERSION,
        "git_head": check_git_head(),
        "tracked_files_clean": check_tracked_files_clean(),
        "frozen_file_integrity": check_frozen_file_integrity(),
        "model_and_reasoning": check_model_and_reasoning(),
        "responses_api_and_web_search": check_responses_api_and_web_search(),
        "no_pre_summarization_step": check_no_pre_summarization_step(),
        "no_structured_output_for_writer": check_no_structured_output_for_writer(),
        "structure_gate_active": check_structure_gate_active(),
        "writer_input_composition": check_writer_input_composition(),
        "editorial_pipeline_not_imported": check_editorial_pipeline_not_imported(),
        "tts_not_referenced": check_tts_not_referenced(),
        "target_scope": check_target_scope(),
        "planned_tts_call_count": 0,
        "planned_old_editorial_brief_pipeline_call_count": 0,
    }

    checks_ok = [
        result["tracked_files_clean"]["clean"],
        result["frozen_file_integrity"]["all_match"],
        result["model_and_reasoning"]["ok"],
        result["responses_api_and_web_search"]["ok"],
        result["no_pre_summarization_step"]["ok"],
        result["no_structured_output_for_writer"]["ok"],
        result["structure_gate_active"]["ok"],
        result["writer_input_composition"]["ok"],
        result["editorial_pipeline_not_imported"]["ok"],
        result["tts_not_referenced"]["ok"],
        result["target_scope"]["ok"],
    ]
    result["overall_status"] = "R3_PREFLIGHT_PASSED" if all(checks_ok) else "R3_PREFLIGHT_FAILED"
    return result


if __name__ == "__main__":
    import os
    result = run_preflight()
    os.makedirs("er002_output/v1_2m_r3", exist_ok=True)
    with open("er002_output/v1_2m_r3/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result["overall_status"])
    if result["overall_status"] != "R3_PREFLIGHT_PASSED":
        sys.exit(1)
