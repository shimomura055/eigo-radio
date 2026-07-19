# ============================================================
# er002_v1_2m_r4_generate.py
# ER-002-v1.2M-R4: 条件L(個別生成)・条件LB(3記事同時生成)の実API生成
# 【実験記録・通常運用では使用しないこと】
# ============================================================
# ★★★ ER-002-v1.2M-R4-FINALIZEにより、条件Lは正式採用、条件LBは不採用と
# ★★★ 決定した。正式な記事生成には er002_v1_2m_generate_article.py
# ★★★ (1テーマ1writer実行のみ、LBモードなし)を使うこと。このスクリプト
# ★★★ はR4比較実験の再現性のためだけに保持しており、"lb"サブコマンドを
# ★★★ 含め、通常の記事生成フローからは呼び出さないこと。
#
# er002_ja_web_research_r3.py / er002_ja_web_research_r4.py(いずれも
# 凍結済み)の関数をそのまま使う。このスクリプトはAPI呼び出しパラメータ
# を一切変更せず、生の応答オブジェクトを記録するプロキシクライアントを
# 被せるだけ。
#
# 実行方法(実験再現のみ):
#   .venv/Scripts/python.exe er002_v1_2m_r4_generate.py l
#   .venv/Scripts/python.exe er002_v1_2m_r4_generate.py lb

from __future__ import annotations

import json
import os
import sys
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er002_ja_web_research_r4 as r4

R4_TOPICS = {
    "A01": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
    "A02": "英国の未成年向け夜間SNS設定",
    "ADD03": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
}
TOPIC_ORDER = ["A01", "A02", "ADD03"]

MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"
OUTPUT_ROOT = "er002_output/v1_2m_r4"


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


def load_master_and_bounds():
    with open(MASTER_PATH, encoding="utf-8") as f:
        master_text = f.read()
    count_result = r4.compute_master_char_count_result(master_text)
    lower, upper = r4.compute_length_bounds(count_result["spoken_text_char_count"])
    return master_text, count_result["spoken_text_char_count"], lower, upper


def run_fact_check(topic: str, article_text: str, writer_sources: list, out_dir: str) -> dict:
    fact_check_prompt = r3.build_fact_check_prompt(topic, article_text, writer_sources or [])
    recorder = RecordingClient(make_real_client())

    def make_fact_checker_factory():
        def factory():
            return r3.make_fact_checker_fn(fact_check_prompt, client=recorder)
        return factory

    parsed_result, status, attempts, model_id, response_id, search_usage, sources = r3.run_fact_checker_with_gates(
        make_fact_checker_factory(), sleep_fn=time.sleep)

    if recorder.captured:
        with open(os.path.join(out_dir, "fact_check_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    fact_qa = {
        "status": status,
        "model": model_id,
        "reasoning_effort": r3.FACT_CHECKER_REASONING_EFFORT,
        "response_id": response_id,
        "parsed_result": parsed_result,
    }
    with open(os.path.join(out_dir, "fact_qa.json"), "w", encoding="utf-8") as f:
        json.dump(fact_qa, f, ensure_ascii=False, indent=2)
    return fact_qa


def save_common_article_artifacts(out_dir: str, raw_text: str, count_result: dict,
                                   writer_sources: list, search_usage: dict,
                                   diagnostics: dict, writer_request_metadata: dict,
                                   execution_log: dict):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "raw_article.md"), "w", encoding="utf-8") as f:
        f.write(raw_text)
    reading_copy = count_result.get("reading_copy")
    with open(os.path.join(out_dir, "reading_copy.md"), "w", encoding="utf-8") as f:
        f.write(reading_copy if reading_copy is not None else raw_text)
    with open(os.path.join(out_dir, "writer_sources.json"), "w", encoding="utf-8") as f:
        json.dump(writer_sources or [], f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "writer_tool_usage.json"), "w", encoding="utf-8") as f:
        json.dump(search_usage or {"web_search_call_count": 0, "queries": []}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "writer_request_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(writer_request_metadata, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "structure_validation.json"), "w", encoding="utf-8") as f:
        json.dump({
            "status": diagnostics["structure_status"],
            "h3_headings": diagnostics["structure_headings"],
            "reasons": diagnostics["structure_reasons"],
        }, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "length_validation.json"), "w", encoding="utf-8") as f:
        json.dump({
            "status": diagnostics["length_status"],
            "raw_char_count": len(raw_text),
            "spoken_text_char_count": count_result.get("spoken_text_char_count"),
            "count_extraction_status": count_result.get("status"),
        }, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)


# ============================================================
# 条件L: 個別生成
# ============================================================
def generate_condition_l_article(topic_id: str, master_text: str, master_count: int,
                                  lower_bound: int, upper_bound: int) -> dict:
    topic = R4_TOPICS[topic_id]
    user_message = r4.build_writer_user_message_r4_l(master_text, topic, master_count, lower_bound, upper_bound)
    out_dir = os.path.join(OUTPUT_ROOT, "condition_l", topic_id)
    os.makedirs(out_dir, exist_ok=True)

    recorder = RecordingClient(make_real_client())

    def make_writer_factory():
        def factory():
            return r3.make_writer_research_fn(user_message, client=recorder)
        return factory

    raw_text, status, attempts, model_id, response_id, search_usage, sources = r4.run_writer_technical_gate(
        make_writer_factory(), sleep_fn=time.sleep)

    result = {"condition": "L", "topic_id": topic_id, "topic": topic, "writer_status": status}

    if recorder.captured:
        with open(os.path.join(out_dir, "raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    if status != "WRITER_CALL_SUCCEEDED":
        with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
            json.dump({"topic_id": topic_id, "writer_final_status": status,
                       "attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts]},
                      f, ensure_ascii=False, indent=2)
        result["included_in_review"] = False
        result["exclusion_reason"] = status
        return result

    annotations = r4.extract_citation_annotations(recorder.captured[-1])
    count_result = r4.compute_spoken_text_char_count(raw_text, annotations)
    diagnostics = r4.classify_writer_diagnostics(raw_text, search_usage, count_result, lower_bound, upper_bound)

    writer_request_metadata = {
        "condition": "L", "topic_id": topic_id, "topic": topic,
        "model": r4.WRITER_MODEL, "reasoning_effort": r4.WRITER_REASONING_EFFORT,
        "developer_message": r4.NEUTRAL_DEVELOPER_MESSAGE,
        "api_endpoint": "responses.create",
        "actual_response_model_field": model_id,
        "model_field_matches_expected": model_id == r4.WRITER_MODEL,
        "response_id": response_id,
        "response_format_used": False,
        "concise_brief_passed_to_writer": False,
        "full_fact_registry_passed_to_writer": False,
        "master_count": master_count, "lower_bound": lower_bound, "upper_bound": upper_bound,
        "technical_retry_count": sum(1 for a in attempts if a["status"] == "TECHNICAL_GENERATION_FAILED"),
        "content_attempt_count": len(attempts),
    }
    execution_log = {
        "topic_id": topic_id, "writer_final_status": status,
        "attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        "diagnostics": diagnostics,
    }
    save_common_article_artifacts(out_dir, raw_text, count_result, sources, search_usage,
                                   diagnostics, writer_request_metadata, execution_log)

    result["diagnostics"] = diagnostics
    result["spoken_text_char_count"] = count_result.get("spoken_text_char_count")

    if diagnostics["eligible_for_fact_check"]:
        fact_qa = run_fact_check(topic, raw_text, sources, out_dir)
        result["fact_qa_status"] = fact_qa["status"]
        result["fact_qa_verdict"] = fact_qa["parsed_result"]["verdict"] if fact_qa["parsed_result"] else None
        result["included_in_review"] = (
            fact_qa["status"] == "FACT_CHECK_COMPLETED"
            and fact_qa["parsed_result"]["verdict"] in ("PASS", "REVIEW_REQUIRED")
        )
        if not result["included_in_review"]:
            result["exclusion_reason"] = (
                fact_qa["status"] if fact_qa["status"] != "FACT_CHECK_COMPLETED" else fact_qa["parsed_result"]["verdict"]
            )
    else:
        result["included_in_review"] = False
        result["exclusion_reason"] = (
            diagnostics["web_search_status"] if diagnostics["web_search_status"] != "WEB_SEARCH_USED"
            else diagnostics["structure_status"]
        )

    return result


# ============================================================
# 条件LB: 3記事同時生成
# ============================================================
def generate_condition_lb(master_text: str, master_count: int, lower_bound: int, upper_bound: int) -> dict:
    user_message = r4.build_writer_user_message_r4_lb(master_text, master_count, lower_bound, upper_bound)
    out_dir = os.path.join(OUTPUT_ROOT, "condition_lb")
    os.makedirs(out_dir, exist_ok=True)

    recorder = RecordingClient(make_real_client())

    def make_writer_factory():
        def factory():
            return r3.make_writer_research_fn(user_message, client=recorder)
        return factory

    raw_text, status, attempts, model_id, response_id, search_usage, sources = r4.run_writer_technical_gate(
        make_writer_factory(), sleep_fn=time.sleep)

    if recorder.captured:
        with open(os.path.join(out_dir, "batch_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    batch_result = {"condition": "LB", "writer_status": status, "topics": [], "included_in_review": {}}

    if status != "WRITER_CALL_SUCCEEDED":
        with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
            json.dump({"writer_final_status": status,
                       "attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts]},
                      f, ensure_ascii=False, indent=2)
        batch_result["exclusion_reason"] = status
        return batch_result

    with open(os.path.join(out_dir, "batch_raw_markdown.md"), "w", encoding="utf-8") as f:
        f.write(raw_text)

    parse_result = r4.parse_batch_articles(raw_text)
    with open(os.path.join(out_dir, "batch_parse_result.json"), "w", encoding="utf-8") as f:
        json.dump({"status": parse_result["status"], "reasons": parse_result["reasons"]}, f, ensure_ascii=False, indent=2)

    if parse_result["status"] != "BATCH_PARSE_OK":
        with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
            json.dump({"writer_final_status": status, "batch_parse_status": parse_result["status"],
                       "reasons": parse_result["reasons"]}, f, ensure_ascii=False, indent=2)
        batch_result["exclusion_reason"] = parse_result["status"]
        return batch_result

    batch_annotations = r4.extract_citation_annotations(recorder.captured[-1])
    attributed = r4.attribute_annotations_to_batch_articles(parse_result["articles"], batch_annotations)
    batch_web_search_status = "WEB_SEARCH_USED" if search_usage["web_search_call_count"] >= 1 else "WRITER_WEB_SEARCH_NOT_USED"

    source_attribution = {
        "batch_web_search_call_count": search_usage["web_search_call_count"],
        "batch_writer_generated_queries": search_usage.get("queries", []),
        "batch_referenced_sources": sources or [],
        "per_topic_citation_counts": {t: len(info["citation_annotations"]) if info["citation_annotations"] is not None else None
                                       for t, info in attributed.items()},
    }
    with open(os.path.join(out_dir, "article_source_attribution.json"), "w", encoding="utf-8") as f:
        json.dump(source_attribution, f, ensure_ascii=False, indent=2)

    for topic_id in TOPIC_ORDER:
        info = attributed[topic_id]
        article_text = info["raw_text"]
        count_result = r4.compute_spoken_text_char_count(article_text, info["citation_annotations"])
        diagnostics = r4.classify_batch_article_diagnostics(
            article_text, batch_web_search_status, info["citation_annotations"], count_result, lower_bound, upper_bound)

        article_out_dir = os.path.join(out_dir, topic_id)
        writer_request_metadata = {
            "condition": "LB", "topic_id": topic_id, "topic": R4_TOPICS[topic_id],
            "model": r4.WRITER_MODEL, "reasoning_effort": r4.WRITER_REASONING_EFFORT,
            "developer_message": r4.NEUTRAL_DEVELOPER_MESSAGE,
            "api_endpoint": "responses.create", "batch_writer_api_call_count": 1,
            "actual_response_model_field": model_id, "model_field_matches_expected": model_id == r4.WRITER_MODEL,
            "response_id": response_id, "response_format_used": False,
            "concise_brief_passed_to_writer": False, "full_fact_registry_passed_to_writer": False,
            "master_count": master_count, "lower_bound": lower_bound, "upper_bound": upper_bound,
        }
        article_sources = [{"title": c.get("title"), "url": c.get("url")} for c in (info["citation_annotations"] or [])]
        execution_log = {
            "topic_id": topic_id, "batch_writer_final_status": status,
            "batch_parse_status": parse_result["status"], "diagnostics": diagnostics,
        }
        save_common_article_artifacts(article_out_dir, article_text, count_result, article_sources,
                                       {"web_search_call_count": search_usage["web_search_call_count"],
                                        "queries": search_usage.get("queries", [])},
                                       diagnostics, writer_request_metadata, execution_log)

        topic_result = {
            "topic_id": topic_id, "diagnostics": diagnostics,
            "spoken_text_char_count": count_result.get("spoken_text_char_count"),
        }
        if diagnostics["eligible_for_fact_check"]:
            fact_qa = run_fact_check(R4_TOPICS[topic_id], article_text, article_sources, article_out_dir)
            topic_result["fact_qa_status"] = fact_qa["status"]
            topic_result["fact_qa_verdict"] = fact_qa["parsed_result"]["verdict"] if fact_qa["parsed_result"] else None
            included = (fact_qa["status"] == "FACT_CHECK_COMPLETED"
                        and fact_qa["parsed_result"]["verdict"] in ("PASS", "REVIEW_REQUIRED"))
            if not included:
                topic_result["exclusion_reason"] = (
                    fact_qa["status"] if fact_qa["status"] != "FACT_CHECK_COMPLETED" else fact_qa["parsed_result"]["verdict"]
                )
        else:
            included = False
            topic_result["exclusion_reason"] = diagnostics["topic_evidence_status"] if diagnostics["topic_evidence_status"] != "TOPIC_RESEARCH_CONFIRMED" else diagnostics["structure_status"]

        batch_result["included_in_review"][topic_id] = included
        batch_result["topics"].append(topic_result)

    with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
        json.dump({"writer_final_status": status, "batch_parse_status": parse_result["status"],
                   "source_attribution": source_attribution}, f, ensure_ascii=False, indent=2)

    return batch_result


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("l", "lb"):
        print("使用法: python er002_v1_2m_r4_generate.py <l|lb>")
        sys.exit(1)

    master_text, master_count, lower_bound, upper_bound = load_master_and_bounds()
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    if sys.argv[1] == "l":
        results = []
        for topic_id in TOPIC_ORDER:
            results.append(generate_condition_l_article(topic_id, master_text, master_count, lower_bound, upper_bound))
        summary_path = os.path.join(OUTPUT_ROOT, "condition_l_run_summary.json")
    else:
        results = generate_condition_lb(master_text, master_count, lower_bound, upper_bound)
        summary_path = os.path.join(OUTPUT_ROOT, "condition_lb_run_summary.json")

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"done. summary saved to {summary_path}")
