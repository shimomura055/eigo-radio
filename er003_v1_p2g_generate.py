# ============================================================
# er003_v1_p2g_generate.py
# ER-003-P2G: 3記事×3方式(9 jobs)の実API選定・記事別Extraction Form QA
# ============================================================
# er003_key_words_min_unit.py(凍結済み)の関数をそのまま使う。API
# 呼び出しパラメータは一切変更せず、生の応答オブジェクトを記録する
# プロキシクライアントを被せるだけ。
#
# 成功・失敗にかかわらず全attemptを保存する。3記事×3方式=独立9 job。
# 先行結果を見て後続prompt・条件を変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2g_generate.py

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

import er003_key_words_min_unit as mu
import er003_ja_to_en_translation as er003

OUTPUT_ROOT = "er003_output/p2g"


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


def select_strategy(article_id: str, strategy_id: str, approved_summary: str, b2_article: str) -> dict:
    user_message = mu.build_strategy_user_message(strategy_id, approved_summary, b2_article)

    out_dir = f"{OUTPUT_ROOT}/{article_id}/{strategy_id}"
    os.makedirs(out_dir, exist_ok=True)

    with open(f"{out_dir}/selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    result = {"article_id": article_id, "strategy_id": strategy_id}

    recorder = RecordingClient(make_real_client())

    def make_selector_factory():
        return mu.make_strategy_selector_fn(user_message, client=recorder)

    parsed, status, attempts, model_id, response_id = mu.run_min_unit_selection_gate(
        article_id, strategy_id, make_selector_factory, b2_article, sleep_fn=time.sleep)

    save_all_attempts(out_dir, attempts, recorder.captured)

    hard_retry_count = sum(1 for a in attempts if a["status"] == "KEY_WORDS_STRUCTURE_INVALID")
    technical_retry_count = sum(1 for a in attempts if a["status"] in ("TECHNICAL_GENERATION_FAILED", "PARSE_FAILED"))

    with open(f"{out_dir}/selector_request_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "article_id": article_id, "strategy_id": strategy_id, "model": mu.SELECTOR_MODEL,
            "reasoning_effort": mu.SELECTOR_REASONING_EFFORT, "developer_message": mu.SELECTOR_DEVELOPER_MESSAGE,
            "api_endpoint": "responses.create", "actual_response_model_field": model_id,
            "model_field_matches_expected": model_id == mu.SELECTOR_MODEL, "response_id": response_id,
            "response_format_used": True, "web_search_tool_used": False,
            "technical_retry_count": technical_retry_count, "hard_form_retry_count": hard_retry_count,
            "content_attempt_count": len(attempts), "final_status": status,
        }, f, ensure_ascii=False, indent=2)

    result["selector_status"] = status
    result["content_attempt_count"] = len(attempts)
    result["hard_form_retry_count"] = hard_retry_count

    execution_log = {"article_id": article_id, "strategy_id": strategy_id, "selector_final_status": status,
                      "selector_attempts": [{k: v for k, v in a.items() if k not in ("raw_text", "parsed")}
                                             for a in attempts]}
    with open(f"{out_dir}/execution_log.json", "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)

    if status != "KEY_WORDS_STRUCTURE_PASS":
        result["included_in_review"] = False
        result["exclusion_reason"] = status
        return result

    with open(f"{out_dir}/key_words_selection.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    reading_copy = mu.build_research_reading_copy(parsed["items"])
    with open(f"{out_dir}/key_words_reading_copy_top5.md", "w", encoding="utf-8") as f:
        f.write(reading_copy)
    with open(f"{out_dir}/reading_copy_metadata.json", "w", encoding="utf-8") as f:
        json.dump(mu.READING_COPY_METADATA, f, ensure_ascii=False, indent=2)

    metrics = mu.compute_min_unit_metrics(parsed["items"])
    with open(f"{out_dir}/key_words_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    result["key_words_metrics"] = metrics

    result["included_in_review"] = True
    result["selection"] = parsed
    return result


def run_form_qa(article_id: str, b2_article: str, strategy_selections: dict) -> dict:
    sets_json = json.dumps(
        [{"runtime_strategy_id": sid, "items": strategy_selections[sid]["selection"]["items"]}
         for sid in mu.STRATEGY_IDS],
        ensure_ascii=False, indent=2,
    )
    qa_prompt = mu.build_form_qa_prompt(b2_article, sets_json)

    out_dir = f"{OUTPUT_ROOT}/{article_id}"
    with open(f"{out_dir}/form_qa_prompt.txt", "w", encoding="utf-8") as f:
        f.write(qa_prompt)

    recorder = RecordingClient(make_real_client())

    def make_qa_factory():
        def factory():
            return mu.make_form_qa_fn(qa_prompt, client=recorder)
        return factory

    qa_parsed, qa_status, qa_attempts, qa_model_id, qa_response_id = mu.run_json_response_gate(
        make_qa_factory(), mu.parse_and_validate_form_qa_output, sleep_fn=time.sleep)

    if recorder.captured:
        with open(f"{out_dir}/form_qa_raw_response.json", "w", encoding="utf-8") as f:
            json.dump(response_to_dict(recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    qa_result = {
        "status": qa_status, "model": qa_model_id, "reasoning_effort": mu.SELECTOR_REASONING_EFFORT,
        "response_id": qa_response_id, "parsed_result": qa_parsed,
    }
    with open(f"{out_dir}/form_qa.json", "w", encoding="utf-8") as f:
        json.dump(qa_result, f, ensure_ascii=False, indent=2)

    return qa_result


if __name__ == "__main__":
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    all_input_manifest = {}
    all_strategy_selections = {}

    for article_id in mu.ARTICLE_IDS:
        approved_summary = mu.load_approved_summary(article_id)
        b2_article = mu.load_approved_b2_article(article_id)
        all_input_manifest[article_id] = {
            "approved_summary_path": mu.APPROVED_SUMMARY_PATHS[article_id],
            "approved_summary_sha256": er003.sha256_text(approved_summary),
            "b2_article_path": mu.B2_INPUT_PATHS[article_id],
            "b2_article_sha256": er003.sha256_text(b2_article),
        }

        strategy_selections = {}
        for strategy_id in mu.STRATEGY_IDS:
            print(f"selecting {article_id}-{strategy_id}...")
            strategy_selections[strategy_id] = select_strategy(article_id, strategy_id, approved_summary, b2_article)
        all_strategy_selections[article_id] = strategy_selections

        with open(f"{OUTPUT_ROOT}/{article_id}/strategy_run_summary.json", "w", encoding="utf-8") as f:
            json.dump(strategy_selections, f, ensure_ascii=False, indent=2)

        if all(strategy_selections[sid].get("included_in_review") for sid in mu.STRATEGY_IDS):
            print(f"running Extraction Form QA for {article_id}...")
            run_form_qa(article_id, b2_article, strategy_selections)
        else:
            print(f"skipping Extraction Form QA for {article_id}: not all 3 jobs passed")

        blind_mapping = mu.build_blind_mapping(article_id)
        with open(f"{OUTPUT_ROOT}/{article_id}/blind_mapping.json", "w", encoding="utf-8") as f:
            json.dump(blind_mapping, f, ensure_ascii=False, indent=2)

    with open(f"{OUTPUT_ROOT}/input_manifest.json", "w", encoding="utf-8") as f:
        json.dump(all_input_manifest, f, ensure_ascii=False, indent=2)

    print("done.")
