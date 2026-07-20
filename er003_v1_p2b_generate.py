# ============================================================
# er003_v1_p2b_generate.py
# ER-003-P2B: A01/A02/ADD03の「Before You Listen」概要実API生成
# ============================================================
# er003_b2_summary.py(凍結済み)の関数をそのまま使う。API呼び出し
# パラメータは一切変更せず、生の応答オブジェクトを記録するプロキシ
# クライアントを被せるだけ。
#
# 成功・失敗にかかわらず全attemptを保存する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2b_generate.py A01
#   .venv/Scripts/python.exe er003_v1_p2b_generate.py A02
#   .venv/Scripts/python.exe er003_v1_p2b_generate.py ADD03

from __future__ import annotations

import json
import os
import sys
import time

from dotenv import load_dotenv

import er003_b2_summary as s
import er003_ja_to_en_translation as er003

OUTPUT_ROOT = "er003_output/p2b"


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
            with open(os.path.join(out_dir, f"attempt_{i}_raw_response.json"), "w", encoding="utf-8") as f:
                json.dump(response_to_dict(recorder_captured[i - 1]), f, ensure_ascii=False, indent=2)
        raw_text = attempt.get("raw_text")
        if raw_text is not None:
            with open(os.path.join(out_dir, f"attempt_{i}_summary.md"), "w", encoding="utf-8") as f:
                f.write(raw_text)
            structure = s.validate_summary_structure(raw_text)
            with open(os.path.join(out_dir, f"attempt_{i}_structure_check.json"), "w", encoding="utf-8") as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)


def generate_summary(topic_id: str) -> dict:
    b2_article = s.load_approved_b2_article(topic_id)
    b2_article_sha256 = er003.sha256_text(b2_article)
    user_message = s.build_summary_user_message(b2_article)

    out_dir = os.path.join(OUTPUT_ROOT, topic_id)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "b2_article_input.md"), "w", encoding="utf-8") as f:
        f.write(b2_article)
    with open(os.path.join(out_dir, "summary_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(user_message)

    result = {"topic_id": topic_id, "topic": s.ARTICLE_TOPICS[topic_id]}

    recorder = RecordingClient(make_real_client())

    def make_generator_factory():
        return s.make_summary_generator_fn(user_message, client=recorder)

    raw_text, status, attempts, model_id, response_id = s.run_summary_structure_gate(
        make_generator_factory, sleep_fn=time.sleep)

    save_all_attempts(out_dir, attempts, recorder.captured)

    structure_retry_count = sum(1 for a in attempts if a["status"] == "B2_SUMMARY_STRUCTURE_INVALID")
    technical_retry_count = sum(1 for a in attempts if a["status"] == "TECHNICAL_GENERATION_FAILED")

    with open(os.path.join(out_dir, "summary_request_metadata.json"), "w", encoding="utf-8") as f:
        json.dump({
            "topic_id": topic_id, "model": s.SUMMARY_MODEL, "reasoning_effort": s.SUMMARY_REASONING_EFFORT,
            "developer_message": s.SUMMARY_DEVELOPER_MESSAGE, "api_endpoint": "responses.create",
            "b2_article_sha256": b2_article_sha256, "actual_response_model_field": model_id,
            "model_field_matches_expected": model_id == s.SUMMARY_MODEL, "response_id": response_id,
            "response_format_used": False, "web_search_tool_used": False,
            "technical_retry_count": technical_retry_count, "structure_retry_count": structure_retry_count,
            "content_attempt_count": len(attempts), "final_status": status,
        }, f, ensure_ascii=False, indent=2)

    result["generator_status"] = status
    result["content_attempt_count"] = len(attempts)
    result["structure_retry_count"] = structure_retry_count
    if attempts:
        result["first_attempt_status"] = attempts[0].get("status")
        result["first_attempt_structure_reasons"] = attempts[0].get("structure_reasons")

    execution_log = {"topic_id": topic_id, "generator_final_status": status,
                      "generator_attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts]}

    if status != "B2_SUMMARY_STRUCTURE_PASS":
        with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
            json.dump(execution_log, f, ensure_ascii=False, indent=2)
        result["included_in_review"] = False
        result["exclusion_reason"] = status
        return result

    with open(os.path.join(out_dir, "summary_en_reading_copy.md"), "w", encoding="utf-8") as f:
        f.write(raw_text)

    metrics = s.compute_summary_metrics(raw_text)
    with open(os.path.join(out_dir, "summary_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    result["summary_metrics"] = metrics

    # --- 概要QA(generatorとは独立した新規API実行) ---
    qa_prompt = s.build_summary_qa_prompt(b2_article, raw_text)
    qa_recorder = RecordingClient(make_real_client())

    def make_qa_factory():
        def factory():
            return s.make_summary_qa_fn(qa_prompt, client=qa_recorder)
        return factory

    qa_parsed, qa_status, qa_attempts, qa_model_id, qa_response_id = s.run_json_response_gate(
        make_qa_factory(), s.parse_and_validate_summary_qa_output, sleep_fn=time.sleep)

    if qa_recorder.captured:
        with open(os.path.join(out_dir, "summary_qa_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(qa_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    qa_result = {
        "status": qa_status, "model": qa_model_id, "reasoning_effort": s.SUMMARY_REASONING_EFFORT,
        "response_id": qa_response_id, "parsed_result": qa_parsed,
    }
    with open(os.path.join(out_dir, "summary_qa.json"), "w", encoding="utf-8") as f:
        json.dump(qa_result, f, ensure_ascii=False, indent=2)

    execution_log["summary_qa_final_status"] = qa_status
    execution_log["summary_qa_attempts"] = [{k: v for k, v in a.items() if k != "raw_text"} for a in qa_attempts]
    with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)

    result["summary_qa_status"] = qa_status
    result["summary_qa_verdict"] = qa_parsed["verdict"] if qa_parsed else None
    result["included_in_review"] = True

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in s.B2_INPUT_PATHS:
        print(f"使用法: python er003_v1_p2b_generate.py <{'|'.join(s.B2_INPUT_PATHS)}>")
        sys.exit(1)
    topic_id = sys.argv[1]
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    result = generate_summary(topic_id)
    summary_path = os.path.join(OUTPUT_ROOT, f"{topic_id}_run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"done. summary saved to {summary_path}")
