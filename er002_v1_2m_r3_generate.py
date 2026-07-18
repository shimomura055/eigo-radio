# ============================================================
# er002_v1_2m_r3_generate.py
# ER-002-v1.2M-R3: A01/A02/ADD03の実API生成(writer自己取材+独立fact checker)
# ============================================================
# er002_ja_web_research_r3.py(凍結済みモジュール)が持つwriter/fact checker
# の呼び出し関数・ゲートロジックをそのまま使う。このスクリープではAPI呼び出し
# パラメータ(モデル・reasoning effort・tools・プロンプト)を一切変更せず、
# 生の応答オブジェクトを記録するためのプロキシクライアントを被せるだけ。
#
# 実行方法:
#   .venv/Scripts/python.exe er002_v1_2m_r3_generate.py A01
#   .venv/Scripts/python.exe er002_v1_2m_r3_generate.py A02
#   .venv/Scripts/python.exe er002_v1_2m_r3_generate.py ADD03

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3

R3_TOPICS = {
    "A01": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
    "A02": "英国の未成年向け夜間SNS設定",
    "ADD03": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
}

EXISTING_FACT_REGISTRY_PATHS = {
    "A01": "er002_v1_2m_fact_registry/A01.json",
    "A02": "er002_v1_2m_fact_registry/A02.json",
    "ADD03": "er002_v1_2m_fact_registry/ADD03_hormuz.json",
}

MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"
OUTPUT_ROOT = "er002_output/v1_2m_r3"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================
# 生の応答オブジェクトを記録するだけのプロキシクライアント
# (r3.make_writer_research_fn/make_fact_checker_fnの呼び出しパラメータには
# 一切関与しない。responses.create()の戻り値を横取りして保存するだけ)
# ============================================================
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


def generate_article(topic_id: str, sleep_fn=None) -> dict:
    if topic_id not in R3_TOPICS:
        raise ValueError(f"未知のtopic_id: {topic_id}")
    topic = R3_TOPICS[topic_id]

    with open(MASTER_PATH, encoding="utf-8") as f:
        master_full_text = f.read()

    user_message = r3.build_writer_user_message_r3(master_full_text, topic)
    template_sha256 = sha256_text(r3.load_r3_writer_prompt_template())
    master_sha256 = sha256_text(master_full_text)
    user_message_sha256 = sha256_text(user_message)

    out_dir = os.path.join(OUTPUT_ROOT, topic_id)
    os.makedirs(out_dir, exist_ok=True)

    real_client = make_real_client()
    writer_recorder = RecordingClient(real_client)

    def make_writer_factory():
        def factory():
            return r3.make_writer_research_fn(user_message, client=writer_recorder)
        return factory

    raw_text, writer_status, writer_attempts, writer_model_id, writer_response_id, \
        writer_search_usage, writer_sources = r3.run_writer_with_gates(
            make_writer_factory(), sleep_fn=sleep_fn)

    # --- writer側artifact保存 ---
    if writer_recorder.captured:
        with open(os.path.join(out_dir, "raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(writer_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    if raw_text is not None:
        with open(os.path.join(out_dir, "raw_article.md"), "w", encoding="utf-8") as f:
            f.write(raw_text)
        # citationマーカーの分離が必要な場合のみ表示用に加工する。今回のR3
        # writerの応答にannotationsとして分離済みのcitationがあり、
        # output_text本文自体に改変を要する破壊的マーカーは含まれないため、
        # raw_article.mdをそのままrendered_article.mdとしてコピーする。
        with open(os.path.join(out_dir, "rendered_article.md"), "w", encoding="utf-8") as f:
            f.write(raw_text)

    writer_retry_counts = {
        "technical_generation_failed_count": sum(
            1 for a in writer_attempts if a["status"] == "TECHNICAL_GENERATION_FAILED"),
        "web_search_not_used_count": sum(
            1 for a in writer_attempts if a["status"] == "WRITER_WEB_SEARCH_NOT_USED"),
        "structure_invalid_count": sum(
            1 for a in writer_attempts if a["status"] == "STRUCTURE_INVALID_POINT_COUNT_OR_BODY"),
        "content_attempt_count": len(writer_attempts),
    }

    writer_request_metadata = {
        "topic_id": topic_id,
        "topic": topic,
        "model": r3.WRITER_MODEL,
        "reasoning_effort": r3.WRITER_REASONING_EFFORT,
        "developer_message": r3.NEUTRAL_DEVELOPER_MESSAGE,
        "api_endpoint": "responses.create",
        "writer_prompt_template_sha256": template_sha256,
        "master_full_text_sha256": master_sha256,
        "rendered_user_message_sha256": user_message_sha256,
        "actual_response_model_field": writer_model_id,
        "model_field_matches_expected": writer_model_id == r3.WRITER_MODEL,
        "response_id": writer_response_id,
        "response_format_used": False,
        "full_fact_registry_passed_to_writer": False,
        "concise_brief_passed_to_writer": False,
        **writer_retry_counts,
        "final_writer_status": writer_status,
    }
    with open(os.path.join(out_dir, "writer_request_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(writer_request_metadata, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "writer_tool_usage.json"), "w", encoding="utf-8") as f:
        json.dump(writer_search_usage or {"web_search_call_count": 0, "queries": []}, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "writer_sources.json"), "w", encoding="utf-8") as f:
        json.dump(writer_sources or [], f, ensure_ascii=False, indent=2)

    last_attempt = writer_attempts[-1] if writer_attempts else {}
    structure_validation = {
        "status": writer_status,
        "h3_headings": last_attempt.get("structure_headings"),
        "reasons": last_attempt.get("structure_reasons"),
    }
    with open(os.path.join(out_dir, "structure_validation.json"), "w", encoding="utf-8") as f:
        json.dump(structure_validation, f, ensure_ascii=False, indent=2)

    execution_log = {
        "topic_id": topic_id,
        "writer_final_status": writer_status,
        "writer_attempts": [
            {k: v for k, v in a.items() if k != "raw_text"} for a in writer_attempts
        ],
    }

    result = {
        "topic_id": topic_id,
        "topic": topic,
        "writer_status": writer_status,
        "fact_check_status": None,
        "fact_check_verdict": None,
        "included_in_user_evaluation": False,
    }

    if writer_status != "STRUCTURE_PASS":
        with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
            json.dump(execution_log, f, ensure_ascii=False, indent=2)
        result["exclusion_reason"] = writer_status
        return result

    # --- ここから独立fact checker(writerとは完全に別の新規API実行) ---
    fact_check_prompt = r3.build_fact_check_prompt(topic, raw_text, writer_sources or [])
    fact_checker_recorder = RecordingClient(make_real_client())

    def make_fact_checker_factory():
        def factory():
            return r3.make_fact_checker_fn(fact_check_prompt, client=fact_checker_recorder)
        return factory

    parsed_result, fact_check_status, fact_check_attempts, checker_model_id, \
        checker_response_id, checker_search_usage, checker_sources = r3.run_fact_checker_with_gates(
            make_fact_checker_factory(), sleep_fn=sleep_fn)

    if fact_checker_recorder.captured:
        with open(os.path.join(out_dir, "fact_check_raw_response.json"), "w", encoding="utf-8") as f:
            json.dump(response_to_dict(fact_checker_recorder.captured[-1]), f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "fact_check_result.json"), "w", encoding="utf-8") as f:
        json.dump({
            "status": fact_check_status,
            "model": checker_model_id,
            "reasoning_effort": r3.FACT_CHECKER_REASONING_EFFORT,
            "response_id": checker_response_id,
            "parsed_result": parsed_result,
        }, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "fact_check_sources.json"), "w", encoding="utf-8") as f:
        json.dump(checker_sources or [], f, ensure_ascii=False, indent=2)

    execution_log["fact_check_final_status"] = fact_check_status
    execution_log["fact_check_attempts"] = [
        {k: v for k, v in a.items() if k != "raw_text"} for a in fact_check_attempts
    ]
    with open(os.path.join(out_dir, "execution_log.json"), "w", encoding="utf-8") as f:
        json.dump(execution_log, f, ensure_ascii=False, indent=2)

    # --- 既存fact registryとの単純な監査証跡照合(自動矛盾検出はしない) ---
    registry_path = EXISTING_FACT_REGISTRY_PATHS.get(topic_id)
    registry_exists = bool(registry_path) and os.path.exists(registry_path)
    source_conflict_audit = {
        "existing_registry_path": registry_path,
        "existing_registry_exists": registry_exists,
        "fact_check_verdict": parsed_result["verdict"] if parsed_result else None,
        "manual_review_recommended": registry_exists and (
            parsed_result is None or parsed_result["verdict"] != "PASS"
        ),
        "note": "自動矛盾検出は行っていない。fact checkerの判定がPASS以外、"
                "かつ既存registryが存在する場合のみ、人間による突き合わせを推奨する。",
    }
    with open(os.path.join(out_dir, "source_conflict_audit.json"), "w", encoding="utf-8") as f:
        json.dump(source_conflict_audit, f, ensure_ascii=False, indent=2)

    result["fact_check_status"] = fact_check_status
    result["fact_check_verdict"] = parsed_result["verdict"] if parsed_result else None
    if fact_check_status == "FACT_CHECK_COMPLETED" and parsed_result["verdict"] in ("PASS", "REVIEW_REQUIRED"):
        result["included_in_user_evaluation"] = True
    else:
        result["exclusion_reason"] = (
            fact_check_status if fact_check_status != "FACT_CHECK_COMPLETED"
            else parsed_result["verdict"]
        )

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in R3_TOPICS:
        print(f"使用法: python er002_v1_2m_r3_generate.py <{'|'.join(R3_TOPICS)}>")
        sys.exit(1)
    topic_id = sys.argv[1]
    result = generate_article(topic_id, sleep_fn=time.sleep)
    print(json.dumps(result, ensure_ascii=False, indent=2))
