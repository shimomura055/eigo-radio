# ============================================================
# er003_v1_p1_generate.py
# ER-003-P1: A01/A02/ADD03の実API英訳(制約なし自然英訳ベースライン)
# ============================================================
# er003_ja_to_en_translation.py(凍結済み)の関数をそのまま使う。API
# 呼び出しパラメータは一切変更せず、生の応答オブジェクトを記録する
# プロキシクライアントを被せるだけ。1テーマにつき: translator1回 →
# (成功時)構造チェック → fidelity QA1回 → 難易度評価1回。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p1_generate.py A01
#   .venv/Scripts/python.exe er003_v1_p1_generate.py A02
#   .venv/Scripts/python.exe er003_v1_p1_generate.py ADD03

from __future__ import annotations

import json
import os
import sys
import time

from dotenv import load_dotenv

import er003_ja_to_en_translation as er003

OUTPUT_ROOT = "er003_output/p1"


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


def translate_article(topic_id: str) -> dict:
    ja_text = er003.load_approved_japanese_article(topic_id)
    ja_sha256 = er003.sha256_text(ja_text)
    user_message = er003.build_translator_user_message(ja_text)

    out_dir = os.path.join(OUTPUT_ROOT, topic_id)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "source_ja.md"), "w", encoding="utf-8") as f:
        f.write(ja_text)
    with open(os.path.join(out_dir, "source_ja_metadata.json"), "w", encoding="utf-8") as f:
        json.dump({
            "topic_id": topic_id, "topic": er003.ARTICLE_TOPICS[topic_id],
            "source_path": er003.APPROVED_ARTICLE_SOURCE_PATHS[topic_id], "sha256": ja_sha256,
        }, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "translator_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(user_message)

    result = {"topic_id": topic_id, "topic": er003.ARTICLE_TOPICS[topic_id]}

    writer_recorder = RecordingClient(make_real_client())

    def make_translator_factory():
        def factory():
            return er003.make_translator_fn(user_message, client=writer_recorder)
        return factory

    raw_text, status, attempts, model_id, response_id, search_usage, sources = er003.run_translator_technical_gate(
        make_translator_factory(), sleep_fn=time.sleep)

    if writer_recorder.captured:
        with open(os.path.join(out_dir, "raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(writer_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "translator_request_metadata.json"), "w", encoding="utf-8") as f:
        json.dump({
            "topic_id": topic_id, "model": er003.TRANSLATOR_MODEL,
            "reasoning_effort": er003.TRANSLATOR_REASONING_EFFORT,
            "developer_message": er003.TRANSLATOR_DEVELOPER_MESSAGE,
            "api_endpoint": "responses.create", "source_ja_sha256": ja_sha256,
            "actual_response_model_field": model_id, "model_field_matches_expected": model_id == er003.TRANSLATOR_MODEL,
            "response_id": response_id, "response_format_used": False, "web_search_tool_used": False,
            "technical_retry_count": sum(1 for a in attempts if a["status"] == "TECHNICAL_GENERATION_FAILED"),
            "content_attempt_count": len(attempts), "final_status": status,
        }, f, ensure_ascii=False, indent=2)

    result["writer_status"] = status
    execution_log = {"topic_id": topic_id, "translator_final_status": status,
                      "translator_attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts]}

    if status != "WRITER_CALL_SUCCEEDED":
        with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
            json.dump(execution_log, f, ensure_ascii=False, indent=2)
        result["included_in_review"] = False
        result["exclusion_reason"] = status
        return result

    with open(os.path.join(out_dir, "translated_en_raw.md"), "w", encoding="utf-8") as f:
        f.write(raw_text)
    # translatorにcitation annotationはそもそも存在しない(Web検索を
    # 与えていないため)。reading copyはraw本文と同一とする。
    with open(os.path.join(out_dir, "translated_en_reading_copy.md"), "w", encoding="utf-8") as f:
        f.write(raw_text)

    structure = er003.check_english_structure(raw_text)
    with open(os.path.join(out_dir, "structure_check.json"), "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    result["structure_check"] = structure

    difficulty_metrics = er003.compute_difficulty_metrics(raw_text)

    # --- 翻訳整合性QA(translatorとは独立した新規API実行) ---
    qa_prompt = er003.build_fidelity_qa_prompt(ja_text, raw_text)
    qa_recorder = RecordingClient(make_real_client())

    def make_qa_factory():
        def factory():
            return er003.make_fidelity_qa_fn(qa_prompt, client=qa_recorder)
        return factory

    qa_parsed, qa_status, qa_attempts, qa_model_id, qa_response_id = er003.run_json_response_gate(
        make_qa_factory(), er003.parse_and_validate_fidelity_qa_output, sleep_fn=time.sleep)

    if qa_recorder.captured:
        with open(os.path.join(out_dir, "fidelity_qa_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(qa_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    fidelity_qa_result = {
        "status": qa_status, "model": qa_model_id, "reasoning_effort": er003.FIDELITY_QA_REASONING_EFFORT,
        "response_id": qa_response_id, "parsed_result": qa_parsed,
    }
    with open(os.path.join(out_dir, "fidelity_qa.json"), "w", encoding="utf-8") as f:
        json.dump(fidelity_qa_result, f, ensure_ascii=False, indent=2)

    # --- 難易度評価(translator・QAとは独立した新規API実行) ---
    difficulty_prompt = er003.build_difficulty_prompt(raw_text)
    diff_recorder = RecordingClient(make_real_client())

    def make_difficulty_factory():
        def factory():
            return er003.make_difficulty_assessment_fn(difficulty_prompt, client=diff_recorder)
        return factory

    diff_parsed, diff_status, diff_attempts, diff_model_id, diff_response_id = er003.run_json_response_gate(
        make_difficulty_factory(), er003.parse_and_validate_difficulty_output, sleep_fn=time.sleep)

    if diff_recorder.captured:
        with open(os.path.join(out_dir, "difficulty_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(diff_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    difficulty_assessment_result = {
        "status": diff_status, "model": diff_model_id, "reasoning_effort": er003.DIFFICULTY_REASONING_EFFORT,
        "response_id": diff_response_id, "llm_assessment": diff_parsed, "deterministic_metrics": difficulty_metrics,
    }
    with open(os.path.join(out_dir, "difficulty_assessment.json"), "w", encoding="utf-8") as f:
        json.dump(difficulty_assessment_result, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "translation_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(difficulty_metrics, f, ensure_ascii=False, indent=2)

    execution_log["fidelity_qa_final_status"] = qa_status
    execution_log["fidelity_qa_attempts"] = [{k: v for k, v in a.items() if k != "raw_text"} for a in qa_attempts]
    execution_log["difficulty_final_status"] = diff_status
    execution_log["difficulty_attempts"] = [{k: v for k, v in a.items() if k != "raw_text"} for a in diff_attempts]
    with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)

    result["fidelity_qa_status"] = qa_status
    result["fidelity_qa_verdict"] = qa_parsed["verdict"] if qa_parsed else None
    result["difficulty_status"] = diff_status
    result["estimated_cefr"] = diff_parsed["estimated_cefr"] if diff_parsed else None
    result["deterministic_metrics"] = difficulty_metrics
    result["included_in_review"] = (
        qa_status == "COMPLETED" and qa_parsed["verdict"] in ("PASS", "REVIEW_REQUIRED")
    )
    if not result["included_in_review"]:
        result["exclusion_reason"] = qa_status if qa_status != "COMPLETED" else qa_parsed["verdict"]

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in er003.APPROVED_ARTICLE_SOURCE_PATHS:
        print(f"使用法: python er003_v1_p1_generate.py <{'|'.join(er003.APPROVED_ARTICLE_SOURCE_PATHS)}>")
        sys.exit(1)
    topic_id = sys.argv[1]
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    result = translate_article(topic_id)
    summary_path = os.path.join(OUTPUT_ROOT, f"{topic_id}_run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"done. summary saved to {summary_path}")
