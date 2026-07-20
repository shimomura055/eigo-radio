# ============================================================
# er003_v1_p2d_generate.py
# ER-003-P2D: A01/A02/ADD03のKey Words実API選定
# ============================================================
# er003_b2_key_words.py(凍結済み)の関数をそのまま使う。API呼び出し
# パラメータは一切変更せず、生の応答オブジェクトを記録するプロキシ
# クライアントを被せるだけ。
#
# 成功・失敗にかかわらず全attemptを保存する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2d_generate.py A01
#   .venv/Scripts/python.exe er003_v1_p2d_generate.py A02
#   .venv/Scripts/python.exe er003_v1_p2d_generate.py ADD03

from __future__ import annotations

import json
import os
import sys
import time

from dotenv import load_dotenv

import er003_b2_key_words as kw
import er003_ja_to_en_translation as er003

OUTPUT_ROOT = "er003_output/p2d"


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


def select_key_words(topic_id: str) -> dict:
    approved_summary = kw.load_approved_summary(topic_id)
    approved_summary_sha256 = er003.sha256_text(approved_summary)
    b2_article = kw.load_approved_b2_article(topic_id)
    b2_article_sha256 = er003.sha256_text(b2_article)
    user_message = kw.build_selector_user_message(approved_summary, b2_article)

    out_dir = f"{OUTPUT_ROOT}/{topic_id}"
    os.makedirs(out_dir, exist_ok=True)

    with open(f"{out_dir}/selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    result = {"topic_id": topic_id, "topic": kw.ARTICLE_TOPICS[topic_id]}

    recorder = RecordingClient(make_real_client())

    def make_selector_factory():
        return kw.make_selector_fn(user_message, client=recorder)

    parsed, status, attempts, model_id, response_id = kw.run_key_words_selection_gate(
        make_selector_factory, b2_article, sleep_fn=time.sleep)

    save_all_attempts(out_dir, attempts, recorder.captured)

    structure_retry_count = sum(1 for a in attempts if a["status"] == "KEY_WORDS_STRUCTURE_INVALID")
    technical_retry_count = sum(1 for a in attempts if a["status"] in ("TECHNICAL_GENERATION_FAILED", "PARSE_FAILED"))

    with open(f"{out_dir}/selector_request_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "topic_id": topic_id, "model": kw.SELECTOR_MODEL, "reasoning_effort": kw.SELECTOR_REASONING_EFFORT,
            "developer_message": kw.SELECTOR_DEVELOPER_MESSAGE, "api_endpoint": "responses.create",
            "approved_summary_sha256": approved_summary_sha256, "b2_article_sha256": b2_article_sha256,
            "actual_response_model_field": model_id, "model_field_matches_expected": model_id == kw.SELECTOR_MODEL,
            "response_id": response_id, "response_format_used": True, "web_search_tool_used": False,
            "technical_retry_count": technical_retry_count, "structure_retry_count": structure_retry_count,
            "content_attempt_count": len(attempts), "final_status": status,
        }, f, ensure_ascii=False, indent=2)

    result["selector_status"] = status
    result["content_attempt_count"] = len(attempts)
    result["structure_retry_count"] = structure_retry_count
    if attempts:
        result["first_attempt_status"] = attempts[0].get("status")

    execution_log = {"topic_id": topic_id, "selector_final_status": status,
                      "selector_attempts": [{k: v for k, v in a.items() if k not in ("raw_text", "parsed")}
                                             for a in attempts]}

    if status != "KEY_WORDS_STRUCTURE_PASS":
        with open(f"{out_dir}/execution_log.json", "w", encoding="utf-8") as f:
            json.dump(execution_log, f, ensure_ascii=False, indent=2)
        result["included_in_review"] = False
        result["exclusion_reason"] = status
        return result

    with open(f"{out_dir}/key_words_selection.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    reading_copy = kw.build_key_words_reading_copy(parsed["items"])
    with open(f"{out_dir}/key_words_reading_copy.md", "w", encoding="utf-8") as f:
        f.write(reading_copy)

    metrics = kw.compute_key_words_metrics(parsed["items"], reading_copy)
    with open(f"{out_dir}/key_words_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    result["key_words_metrics"] = metrics

    # --- 独立Key Words QA(selectorとは独立した新規API実行) ---
    key_words_json_text = json.dumps(parsed, ensure_ascii=False, indent=2)
    qa_prompt = kw.build_qa_prompt(approved_summary, b2_article, key_words_json_text)
    qa_recorder = RecordingClient(make_real_client())

    def make_qa_factory():
        def factory():
            return kw.make_qa_fn(qa_prompt, client=qa_recorder)
        return factory

    qa_parsed, qa_status, qa_attempts, qa_model_id, qa_response_id = kw.run_json_response_gate(
        make_qa_factory(), kw.parse_and_validate_key_words_qa_output, sleep_fn=time.sleep)

    if qa_recorder.captured:
        with open(f"{out_dir}/key_words_qa_raw_response.json", "w", encoding="utf-8") as f:
            json.dump(response_to_dict(qa_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    qa_result = {
        "status": qa_status, "model": qa_model_id, "reasoning_effort": kw.SELECTOR_REASONING_EFFORT,
        "response_id": qa_response_id, "parsed_result": qa_parsed,
    }
    with open(f"{out_dir}/key_words_qa.json", "w", encoding="utf-8") as f:
        json.dump(qa_result, f, ensure_ascii=False, indent=2)

    execution_log["key_words_qa_final_status"] = qa_status
    execution_log["key_words_qa_attempts"] = [{k: v for k, v in a.items() if k != "raw_text"} for a in qa_attempts]
    with open(f"{out_dir}/execution_log.json", "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)

    result["key_words_qa_status"] = qa_status
    result["key_words_qa_verdict"] = qa_parsed["verdict"] if qa_parsed else None
    result["included_in_review"] = True

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in kw.B2_INPUT_PATHS:
        print(f"使用法: python er003_v1_p2d_generate.py <{'|'.join(kw.B2_INPUT_PATHS)}>")
        sys.exit(1)
    topic_id = sys.argv[1]
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    result = select_key_words(topic_id)
    summary_path = f"{OUTPUT_ROOT}/{topic_id}_run_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"done. summary saved to {summary_path}")
