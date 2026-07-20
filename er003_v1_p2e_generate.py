# ============================================================
# er003_v1_p2e_generate.py
# ER-003-P2E: L/P/U 3方式の実API選定・比較QA
# ============================================================
# er003_key_words_strategy_compare.py(凍結済み)の関数をそのまま使う。
# API呼び出しパラメータは一切変更せず、生の応答オブジェクトを記録する
# プロキシクライアントを被せるだけ。
#
# 成功・失敗にかかわらず全attemptを保存する。3方式は独立1 callずつ
# (合計3 call)、Lの結果を見てP/Uの条件を変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2e_generate.py

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

import er003_key_words_strategy_compare as sc
import er003_ja_to_en_translation as er003

OUTPUT_ROOT = "er003_output/p2e"
TOPIC_ID = sc.TARGET_TOPIC_ID  # "A01"


class _RecordedResponses:
    def __init__(self, real_responses, captured):
        self._real = real_responses
        self._captured = captured

    def create(self, **kwargs):
        response = self._real.create(**kwargs)
        self._captured.append(response)
        return response


class RecordingClient:
    def __init__(self, real_client):
        self.captured = []
        self.responses = _RecordedResponses(real_client.responses, self.captured)


def response_to_dict(response) -> dict:
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    if hasattr(response, "to_dict"):
        return response.to_dict()
    return json.loads(str(response))


def make_real_client():
    load_dotenv()
    from openai import OpenAI
    return OpenAI()


def save_all_attempts(out_dir: str, attempts_detail: list, recorder_captured: list) -> None:
    for i, attempt in enumerate(attempts_detail, start=1):
        if i - 1 < len(recorder_captured):
            with open(f"{out_dir}/attempt_{i}_raw_response.json", "w", encoding="utf-8") as f:
                json.dump(response_to_dict(recorder_captured[i - 1]), f, ensure_ascii=False, indent=2)
        parsed = attempt.get("parsed")
        if parsed is not None:
            with open(f"{out_dir}/attempt_{i}_selection.json", "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
        validation = {
            "status": attempt.get("status"),
            "reasons": attempt.get("validation_reasons", []),
            "item_reasons": attempt.get("item_reasons", []),
        }
        with open(f"{out_dir}/attempt_{i}_validation.json", "w", encoding="utf-8") as f:
            json.dump(validation, f, ensure_ascii=False, indent=2)


def select_strategy(strategy_id: str, approved_summary: str, b2_article: str) -> dict:
    user_message = sc.build_strategy_user_message(strategy_id, approved_summary, b2_article)

    out_dir = f"{OUTPUT_ROOT}/{strategy_id}"
    os.makedirs(out_dir, exist_ok=True)

    with open(f"{out_dir}/selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    result = {"strategy_id": strategy_id}

    recorder = RecordingClient(make_real_client())

    def make_selector_factory():
        return sc.make_strategy_selector_fn(strategy_id, user_message, client=recorder)

    parsed, status, attempts, model_id, response_id = sc.run_strategy_selection_gate(
        strategy_id, make_selector_factory, b2_article, sleep_fn=time.sleep)

    save_all_attempts(out_dir, attempts, recorder.captured)

    structure_retry_count = sum(1 for a in attempts if a["status"] == "KEY_WORDS_STRUCTURE_INVALID")
    technical_retry_count = sum(1 for a in attempts if a["status"] in ("TECHNICAL_GENERATION_FAILED", "PARSE_FAILED"))

    with open(f"{out_dir}/selector_request_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "strategy_id": strategy_id, "model": sc.SELECTOR_MODEL, "reasoning_effort": sc.SELECTOR_REASONING_EFFORT,
            "developer_message": sc.SELECTOR_DEVELOPER_MESSAGE, "api_endpoint": "responses.create",
            "actual_response_model_field": model_id, "model_field_matches_expected": model_id == sc.SELECTOR_MODEL,
            "response_id": response_id, "response_format_used": True, "web_search_tool_used": False,
            "technical_retry_count": technical_retry_count, "structure_retry_count": structure_retry_count,
            "content_attempt_count": len(attempts), "final_status": status,
        }, f, ensure_ascii=False, indent=2)

    result["selector_status"] = status
    result["content_attempt_count"] = len(attempts)
    result["structure_retry_count"] = structure_retry_count

    execution_log = {"strategy_id": strategy_id, "selector_final_status": status,
                      "selector_attempts": [{k: v for k, v in a.items() if k not in ("raw_text", "parsed")}
                                             for a in attempts]}

    if status != "KEY_WORDS_STRUCTURE_PASS":
        with open(f"{out_dir}/execution_log.json", "w", encoding="utf-8") as f:
            json.dump(execution_log, f, ensure_ascii=False, indent=2)
        result["included_in_comparison"] = False
        result["exclusion_reason"] = status
        return result

    with open(f"{out_dir}/key_words_selection.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    reading_copy = sc.build_key_words_reading_copy(parsed["items"])
    with open(f"{out_dir}/key_words_reading_copy.md", "w", encoding="utf-8") as f:
        f.write(reading_copy)

    metrics = sc.compute_strategy_metrics(parsed["items"], reading_copy)
    with open(f"{out_dir}/key_words_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    result["key_words_metrics"] = metrics

    with open(f"{out_dir}/execution_log.json", "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)

    result["included_in_comparison"] = True
    result["selection"] = parsed
    return result


def run_comparison_qa(approved_summary: str, b2_article: str, strategy_selections: dict) -> dict:
    strategy_results_json = json.dumps(
        {sid: strategy_selections[sid]["selection"] for sid in sc.STRATEGY_IDS
         if strategy_selections[sid].get("included_in_comparison")},
        ensure_ascii=False, indent=2,
    )
    qa_prompt = sc.build_comparison_qa_prompt(approved_summary, b2_article, strategy_results_json)

    with open(f"{OUTPUT_ROOT}/comparison_qa_prompt.txt", "w", encoding="utf-8") as f:
        f.write(qa_prompt)

    recorder = RecordingClient(make_real_client())

    def make_qa_factory():
        def factory():
            return sc.make_comparison_qa_fn(qa_prompt, client=recorder)
        return factory

    qa_parsed, qa_status, qa_attempts, qa_model_id, qa_response_id = sc.run_json_response_gate(
        make_qa_factory(), sc.parse_and_validate_comparison_qa_output, sleep_fn=time.sleep)

    if recorder.captured:
        with open(f"{OUTPUT_ROOT}/comparison_qa_raw_response.json", "w", encoding="utf-8") as f:
            json.dump(response_to_dict(recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    qa_result = {
        "status": qa_status, "model": qa_model_id, "reasoning_effort": sc.SELECTOR_REASONING_EFFORT,
        "response_id": qa_response_id, "parsed_result": qa_parsed,
    }
    with open(f"{OUTPUT_ROOT}/comparison_qa.json", "w", encoding="utf-8") as f:
        json.dump(qa_result, f, ensure_ascii=False, indent=2)

    return qa_result


if __name__ == "__main__":
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    approved_summary = sc.load_approved_summary(TOPIC_ID)
    b2_article = sc.load_approved_b2_article(TOPIC_ID)

    approved_summary_sha256 = er003.sha256_text(approved_summary)
    b2_article_sha256 = er003.sha256_text(b2_article)
    with open(f"{OUTPUT_ROOT}/input_manifest.json", "w", encoding="utf-8") as f:
        json.dump({
            "topic_id": TOPIC_ID,
            "approved_summary_path": sc.APPROVED_SUMMARY_PATHS[TOPIC_ID],
            "approved_summary_sha256": approved_summary_sha256,
            "b2_article_path": sc.B2_INPUT_PATHS[TOPIC_ID],
            "b2_article_sha256": b2_article_sha256,
        }, f, ensure_ascii=False, indent=2)

    strategy_selections = {}
    for strategy_id in sc.STRATEGY_IDS:
        print(f"selecting strategy {strategy_id}...")
        strategy_selections[strategy_id] = select_strategy(strategy_id, approved_summary, b2_article)

    with open(f"{OUTPUT_ROOT}/strategy_run_summary.json", "w", encoding="utf-8") as f:
        json.dump(strategy_selections, f, ensure_ascii=False, indent=2)

    if all(strategy_selections[sid].get("included_in_comparison") for sid in sc.STRATEGY_IDS):
        print("running comparison QA...")
        run_comparison_qa(approved_summary, b2_article, strategy_selections)
    else:
        print("skipping comparison QA: not all strategies passed structure gate")

    blind_mapping = sc.build_blind_mapping()
    with open(f"{OUTPUT_ROOT}/ER-003-P2E_blind_mapping.json", "w", encoding="utf-8") as f:
        json.dump(blind_mapping, f, ensure_ascii=False, indent=2)

    print("done.")
