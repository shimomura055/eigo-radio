# ============================================================
# er003_v1_p2_generate.py
# ER-003-P2 Part B: A01/A02/ADD03のB2実API調整
# ============================================================
# er003_b2_adapter.py(凍結済み)の関数をそのまま使う。API呼び出し
# パラメータは一切変更せず、生の応答オブジェクトを記録するプロキシ
# クライアントを被せるだけ。
#
# ER-003-P2 Part Aで指示された保存改善に従い、構造再試行が発生した
# 場合は全attempt(失敗分を含む)のraw_response/article/structure_check
# を保存する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2_generate.py A01
#   .venv/Scripts/python.exe er003_v1_p2_generate.py A02
#   .venv/Scripts/python.exe er003_v1_p2_generate.py ADD03

from __future__ import annotations

import json
import os
import sys
import time

from dotenv import load_dotenv

import er003_b2_adapter as b2
import er003_ja_to_en_translation as er003

OUTPUT_ROOT = "er003_output/p2"


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
    """全attempt(構造不適合等で破棄された分も含む)のraw_response・
    article・structure_checkを保存する(ER-003-P2 Part Aで指示された
    保存改善)。captured応答とattemptsの対応は基本的に呼び出し順の
    位置対応で行う(技術的失敗のうち、API呼び出し自体が例外を送出した
    場合はcaptured応答が存在しないことがある)。"""
    for i, attempt in enumerate(attempts_detail, start=1):
        if i - 1 < len(recorder_captured):
            with open(os.path.join(out_dir, f"attempt_{i}_raw_response.json"), "w", encoding="utf-8") as f:
                json.dump(response_to_dict(recorder_captured[i - 1]), f, ensure_ascii=False, indent=2)
        raw_text = attempt.get("raw_text")
        if raw_text is not None:
            with open(os.path.join(out_dir, f"attempt_{i}_article.md"), "w", encoding="utf-8") as f:
                f.write(raw_text)
            structure = b2.validate_b2_structure(raw_text)
            with open(os.path.join(out_dir, f"attempt_{i}_structure_check.json"), "w", encoding="utf-8") as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)


def adapt_article(topic_id: str) -> dict:
    natural_source = b2.load_natural_english_source(topic_id)
    natural_source_sha256 = er003.sha256_text(natural_source)
    ja_text = er003.load_approved_japanese_article(topic_id)
    user_message = b2.build_b2_adapter_user_message(natural_source)

    out_dir = os.path.join(OUTPUT_ROOT, topic_id)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "natural_source_input.md"), "w", encoding="utf-8") as f:
        f.write(natural_source)
    with open(os.path.join(out_dir, "adapter_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(user_message)

    result = {"topic_id": topic_id, "topic": b2.ARTICLE_TOPICS[topic_id]}

    recorder = RecordingClient(make_real_client())

    def make_adapter_factory():
        return b2.make_b2_adapter_fn(user_message, client=recorder)

    raw_text, status, attempts, model_id, response_id, search_usage, sources = b2.run_b2_adapter_structure_gate(
        make_adapter_factory, sleep_fn=time.sleep)

    save_all_attempts(out_dir, attempts, recorder.captured)

    structure_retry_count = sum(1 for a in attempts if a["status"] == "TRANSLATION_STRUCTURE_INVALID")
    technical_retry_count = sum(1 for a in attempts if a["status"] == "TECHNICAL_GENERATION_FAILED")

    with open(os.path.join(out_dir, "adapter_request_metadata.json"), "w", encoding="utf-8") as f:
        json.dump({
            "topic_id": topic_id, "model": b2.B2_ADAPTER_MODEL, "reasoning_effort": b2.B2_ADAPTER_REASONING_EFFORT,
            "developer_message": b2.B2_ADAPTER_DEVELOPER_MESSAGE, "api_endpoint": "responses.create",
            "natural_source_sha256": natural_source_sha256, "actual_response_model_field": model_id,
            "model_field_matches_expected": model_id == b2.B2_ADAPTER_MODEL, "response_id": response_id,
            "response_format_used": False, "web_search_tool_used": False,
            "technical_retry_count": technical_retry_count, "structure_retry_count": structure_retry_count,
            "content_attempt_count": len(attempts), "final_status": status,
        }, f, ensure_ascii=False, indent=2)

    result["adapter_status"] = status
    result["content_attempt_count"] = len(attempts)
    result["structure_retry_count"] = structure_retry_count
    if attempts:
        result["first_attempt_status"] = attempts[0].get("status")
        result["first_attempt_structure_reasons"] = attempts[0].get("structure_reasons")

    execution_log = {"topic_id": topic_id, "adapter_final_status": status,
                      "adapter_attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts]}

    if status != "TRANSLATION_STRUCTURE_PASS":
        with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
            json.dump(execution_log, f, ensure_ascii=False, indent=2)
        result["included_in_review"] = False
        result["exclusion_reason"] = status
        return result

    with open(os.path.join(out_dir, "b2_version_raw.md"), "w", encoding="utf-8") as f:
        f.write(raw_text)

    final_structure = b2.validate_b2_structure(raw_text)
    with open(os.path.join(out_dir, "structure_check.json"), "w", encoding="utf-8") as f:
        json.dump(final_structure, f, ensure_ascii=False, indent=2)
    result["structure_check"] = final_structure

    sentence_metrics = b2.compute_b2_sentence_metrics(raw_text)
    with open(os.path.join(out_dir, "sentence_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(sentence_metrics, f, ensure_ascii=False, indent=2)
    result["sentence_metrics"] = sentence_metrics

    # --- B2整合性QA(adapterとは独立した新規API実行) ---
    fidelity_prompt = b2.build_b2_fidelity_qa_prompt(ja_text, natural_source, raw_text)
    fidelity_recorder = RecordingClient(make_real_client())

    def make_fidelity_factory():
        def factory():
            return b2.make_b2_fidelity_qa_fn(fidelity_prompt, client=fidelity_recorder)
        return factory

    fidelity_parsed, fidelity_status, fidelity_attempts, fidelity_model_id, fidelity_response_id = b2.run_json_response_gate(
        make_fidelity_factory(), b2.parse_and_validate_b2_fidelity_qa_output, sleep_fn=time.sleep)

    if fidelity_recorder.captured:
        with open(os.path.join(out_dir, "fidelity_qa_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(fidelity_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    fidelity_qa_result = {
        "status": fidelity_status, "model": fidelity_model_id, "reasoning_effort": b2.B2_ADAPTER_REASONING_EFFORT,
        "response_id": fidelity_response_id, "parsed_result": fidelity_parsed,
    }
    with open(os.path.join(out_dir, "fidelity_qa.json"), "w", encoding="utf-8") as f:
        json.dump(fidelity_qa_result, f, ensure_ascii=False, indent=2)

    # --- B2難易度QA(adapter・fidelity QAとは独立した新規API実行) ---
    difficulty_prompt = b2.build_b2_difficulty_qa_prompt(raw_text)
    difficulty_recorder = RecordingClient(make_real_client())

    def make_difficulty_factory():
        def factory():
            return b2.make_b2_difficulty_qa_fn(difficulty_prompt, client=difficulty_recorder)
        return factory

    difficulty_parsed, difficulty_status, difficulty_attempts, difficulty_model_id, difficulty_response_id = b2.run_json_response_gate(
        make_difficulty_factory(), b2.parse_and_validate_b2_difficulty_output, sleep_fn=time.sleep)

    if difficulty_recorder.captured:
        with open(os.path.join(out_dir, "difficulty_qa_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(difficulty_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    difficulty_qa_result = {
        "status": difficulty_status, "model": difficulty_model_id, "reasoning_effort": b2.B2_ADAPTER_REASONING_EFFORT,
        "response_id": difficulty_response_id, "parsed_result": difficulty_parsed,
    }
    with open(os.path.join(out_dir, "difficulty_qa.json"), "w", encoding="utf-8") as f:
        json.dump(difficulty_qa_result, f, ensure_ascii=False, indent=2)

    execution_log["fidelity_qa_final_status"] = fidelity_status
    execution_log["fidelity_qa_attempts"] = [{k: v for k, v in a.items() if k != "raw_text"} for a in fidelity_attempts]
    execution_log["difficulty_qa_final_status"] = difficulty_status
    execution_log["difficulty_qa_attempts"] = [{k: v for k, v in a.items() if k != "raw_text"} for a in difficulty_attempts]
    with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)

    result["fidelity_qa_status"] = fidelity_status
    result["fidelity_qa_verdict"] = fidelity_parsed["verdict"] if fidelity_parsed else None
    result["difficulty_qa_status"] = difficulty_status
    result["difficulty_qa_verdict"] = difficulty_parsed["verdict"] if difficulty_parsed else None
    result["estimated_cefr"] = difficulty_parsed["estimated_cefr"] if difficulty_parsed else None

    fidelity_ok = fidelity_status == "COMPLETED" and fidelity_parsed["verdict"] in ("PASS", "REVIEW_REQUIRED")
    difficulty_ok = difficulty_status == "COMPLETED" and difficulty_parsed["verdict"] in ("PASS", "REVIEW_REQUIRED")
    result["included_in_review"] = fidelity_ok and difficulty_ok
    if not result["included_in_review"]:
        reasons = []
        if not fidelity_ok:
            reasons.append(fidelity_status if fidelity_status != "COMPLETED" else fidelity_parsed["verdict"])
        if not difficulty_ok:
            reasons.append(difficulty_status if difficulty_status != "COMPLETED" else difficulty_parsed["verdict"])
        result["exclusion_reason"] = reasons

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in b2.NATURAL_SOURCE_PATHS:
        print(f"使用法: python er003_v1_p2_generate.py <{'|'.join(b2.NATURAL_SOURCE_PATHS)}>")
        sys.exit(1)
    topic_id = sys.argv[1]
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    result = adapt_article(topic_id)
    summary_path = os.path.join(OUTPUT_ROOT, f"{topic_id}_run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"done. summary saved to {summary_path}")
