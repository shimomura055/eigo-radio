# ============================================================
# er002_v1_2m_generate_article.py
# ER-002-v1.2M-R4-FINALIZE: 正式採用された記事生成の実行スクリプト
# ============================================================
# 1テーマにつきwriterを1回実行する(正式仕様)。複数テーマを1回の
# writer実行で同時生成するモード(条件LB、不採用)は、このスクリプトには
# 一切存在しない。実験的な条件LBの再現が必要な場合は、実験記録として
# 保持している er002_v1_2m_r4_generate.py (lbサブコマンド)を使うこと
# (通常の運用では使用しないこと)。
#
# 使うロジック:
#   - er002_ja_article_generation.py(正式採用: 読み上げ文字数正規化、
#     長さ指示付きプロンプト構築、技術的失敗のみの再試行ゲート、診断分類)
#   - er002_ja_web_research_r3.py(R3から不変: writer本体呼び出し・
#     独立fact checker)
#
# 文字数超過・構造不適合・fact-QA不合格を理由とした自動再生成は行わない
# (ER-002-v1.2M-R4-FINALIZEの正式決定)。
#
# 実行方法:
#   .venv/Scripts/python.exe er002_v1_2m_generate_article.py A01 "2026年ワールドカップ準決勝のイングランド対アルゼンチン"

from __future__ import annotations

import json
import os
import sys
import time

from dotenv import load_dotenv

import er002_ja_article_generation as article_gen
import er002_ja_web_research_r3 as r3

MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"
OUTPUT_ROOT = "er002_output/v1_2m_article_generation"


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


def run_fact_check(topic: str, article_text: str, writer_sources: list, out_dir: str) -> dict:
    """R3のfact checkerロジックを一切変更せずに使う。PASS/REVIEW_REQUIRED/
    FAILの3値を維持し、REVIEW_REQUIREDをPASSへ読み替えることはしない。"""
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
        "status": status, "model": model_id, "reasoning_effort": r3.FACT_CHECKER_REASONING_EFFORT,
        "response_id": response_id, "parsed_result": parsed_result,
    }
    with open(os.path.join(out_dir, "fact_qa.json"), "w", encoding="utf-8") as f:
        json.dump(fact_qa, f, ensure_ascii=False, indent=2)
    return fact_qa


def generate_article(topic_id: str, topic: str, out_root: str = OUTPUT_ROOT) -> dict:
    """1テーマにつきwriterを1回実行する正式パイプライン。"""
    with open(MASTER_PATH, encoding="utf-8") as f:
        master_text = f.read()

    user_message = article_gen.build_writer_user_message(master_text, topic)
    out_dir = os.path.join(out_root, topic_id)
    os.makedirs(out_dir, exist_ok=True)

    recorder = RecordingClient(make_real_client())

    def make_writer_factory():
        def factory():
            return r3.make_writer_research_fn(user_message, client=recorder)
        return factory

    raw_text, status, attempts, model_id, response_id, search_usage, sources = article_gen.run_writer_technical_gate(
        make_writer_factory(), sleep_fn=time.sleep)

    result = {"topic_id": topic_id, "topic": topic, "writer_status": status}

    if recorder.captured:
        with open(os.path.join(out_dir, "raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    if status != "WRITER_CALL_SUCCEEDED":
        result["included_in_output"] = False
        result["exclusion_reason"] = status
        return result

    annotations = article_gen.extract_citation_annotations(recorder.captured[-1])
    count_result = article_gen.compute_spoken_text_char_count(raw_text, annotations)
    diagnostics = article_gen.classify_writer_diagnostics(raw_text, search_usage, count_result)

    with open(os.path.join(out_dir, "raw_article.md"), "w", encoding="utf-8") as f:
        f.write(raw_text)
    with open(os.path.join(out_dir, "reading_copy.md"), "w", encoding="utf-8") as f:
        f.write(count_result.get("reading_copy") or raw_text)
    with open(os.path.join(out_dir, "writer_sources.json"), "w", encoding="utf-8") as f:
        json.dump(sources or [], f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "length_validation.json"), "w", encoding="utf-8") as f:
        json.dump({
            "status": diagnostics["length_status"],
            "spoken_text_char_count": count_result.get("spoken_text_char_count"),
            "lower_bound": article_gen.LENGTH_LOWER_BOUND, "upper_bound": article_gen.LENGTH_UPPER_BOUND,
        }, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "structure_validation.json"), "w", encoding="utf-8") as f:
        json.dump({
            "status": diagnostics["structure_status"], "h3_headings": diagnostics["structure_headings"],
            "reasons": diagnostics["structure_reasons"],
        }, f, ensure_ascii=False, indent=2)

    result["diagnostics"] = diagnostics
    result["spoken_text_char_count"] = count_result.get("spoken_text_char_count")

    if diagnostics["eligible_for_fact_check"]:
        fact_qa = run_fact_check(topic, raw_text, sources, out_dir)
        result["fact_qa_status"] = fact_qa["status"]
        result["fact_qa_verdict"] = fact_qa["parsed_result"]["verdict"] if fact_qa["parsed_result"] else None
        result["included_in_output"] = (
            fact_qa["status"] == "FACT_CHECK_COMPLETED"
            and fact_qa["parsed_result"]["verdict"] in article_gen.FACT_CHECK_INCLUDE_VERDICTS
        )
        if not result["included_in_output"]:
            result["exclusion_reason"] = (
                fact_qa["status"] if fact_qa["status"] != "FACT_CHECK_COMPLETED" else fact_qa["parsed_result"]["verdict"]
            )
    else:
        result["included_in_output"] = False
        result["exclusion_reason"] = (
            diagnostics["web_search_status"] if diagnostics["web_search_status"] != "WEB_SEARCH_USED"
            else diagnostics["structure_status"]
        )

    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用法: python er002_v1_2m_generate_article.py <topic_id> <topic>")
        sys.exit(1)
    topic_id, topic = sys.argv[1], sys.argv[2]
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    result = generate_article(topic_id, topic)
    summary_path = os.path.join(OUTPUT_ROOT, f"{topic_id}_run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"done. summary saved to {summary_path}")
