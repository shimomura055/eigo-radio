# ============================================================
# er003_v1_en_direct_ab_01_generate.py
# ER-003-EN-DIRECT-AB-01: A02英語直接生成(B版)実験
# ============================================================
# 目的: 最終採用R4「条件L」のwriter方式を極力維持したまま、
# developer messageのみ「日本語の記事を作成してください。」→
# 「英語の記事を作成してください。」へ変更し、出力言語だけを変えた
# 場合の影響を見る。既存R4 Production候補コード(er002_ja_article_
# generation.py / er002_ja_web_research_r3.py)は一切変更せず、
# この独立スクリプトから関数を読み取り専用で再利用するだけ。
#
# 変更点(R4からの差分はこれだけ):
#   1. developer_message: "日本語の記事を作成してください。"
#      → "英語の記事を作成してください。"
#   2. user prompt末尾の長さ指示: R4の日本語文字数指示(阪神マスター
#      697字基準)は英語には機械的に転用できないため、A02の既存
#      Natural English Source語数(418語)を基準にした英語の語数指示へ
#      差し替え(このスクリプト内でのみ定義、production側は無変更)
# それ以外(阪神マスター全文投入・user instruction本文・Web検索有無・
# 構造ゲート・独立fact checker)はR4のロジックをそのまま呼び出す。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_en_direct_ab_01_generate.py

from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er002_ja_free_markdown_restore_r2 as restore_r2

load_dotenv()

TOPIC_ID = "A02"
TOPIC = "英国の未成年向け夜間SNS設定"
MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"
OUT_DIR = "er003_output/en_direct_ab_01/A02"

# A版(既存Natural English Source)の実測語数を基準にしたsoft target。
# R4の日本語文字数制約(阪神マスター基準)をそのまま転用しない
# (ER-003-EN-DIRECT-AB-01の指示どおり)。
A_VERSION_WORD_COUNT = 418
LENGTH_LOWER_BOUND = round(A_VERSION_WORD_COUNT * 0.85)  # 355
LENGTH_UPPER_BOUND = round(A_VERSION_WORD_COUNT * 1.15)  # 481

# developer message: R4から「日本語」→「英語」の1語だけ変更。他は追加しない。
EN_DEVELOPER_MESSAGE = "英語の記事を作成してください。"

# user prompt: R3/R4のuser instruction本文(日本語のまま)は完全に維持し、
# 末尾の長さ指示だけを英語の語数基準へ差し替える。それ以外の文言は
# writer_prompt_template_r3.txtと一字一句同一。
EN_LENGTH_INSTRUCTION_SUFFIX = (
    "記事本文の分量は、阪神マスターの日本語文字数をそのまま基準にせず、"
    f"英語の語数で目安{A_VERSION_WORD_COUNT}語程度、"
    f"許容範囲は{LENGTH_LOWER_BOUND}語から{LENGTH_UPPER_BOUND}語としてください"
    "(目安であり、厳密な制約ではありません)。\n"
    "調べた情報をすべて盛り込まず、記事の面白さに必要な情報だけを選んでください。"
)


def build_b_version_template() -> str:
    r3_template = r3.load_r3_writer_prompt_template()
    # r3_templateは末尾に改行のみで終わる。長さ指示だけをEN版へ差し替えて追加する。
    return r3_template.rstrip("\n") + "\n\n" + EN_LENGTH_INSTRUCTION_SUFFIX


def load_master_full_text() -> str:
    with open(MASTER_PATH, encoding="utf-8") as f:
        return f.read()


def compute_word_count(text: str) -> int:
    body = re.sub(r"^#{1,6}\s*.*$", "", text, flags=re.MULTILINE)
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", body)
    return len(words)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    master_full_text = load_master_full_text()
    template = build_b_version_template()
    user_message = r3.build_writer_user_message_r3(master_full_text, TOPIC, template=template)

    prompt_record = {
        "topic_id": TOPIC_ID,
        "topic": TOPIC,
        "developer_message": EN_DEVELOPER_MESSAGE,
        "user_message_sha256": r3.sha256_text(user_message),
        "user_message_full_text": user_message,
        "length_lower_bound_words": LENGTH_LOWER_BOUND,
        "length_upper_bound_words": LENGTH_UPPER_BOUND,
        "a_version_word_count_basis": A_VERSION_WORD_COUNT,
    }
    with open(f"{OUT_DIR}/audit/prompt_record.json", "w", encoding="utf-8") as f:
        json.dump(prompt_record, f, ensure_ascii=False, indent=2)

    def make_writer_fn():
        return r3.make_writer_research_fn(user_message, developer_message=EN_DEVELOPER_MESSAGE)

    print(f"[{TOPIC_ID}] writer呼び出し開始(developer_message={EN_DEVELOPER_MESSAGE!r})...")
    raw_text, final_status, attempts_detail, model_id, response_id, search_usage, sources = r3.run_writer_with_gates(
        make_writer_fn, sleep_fn=time.sleep,
    )
    print(f"[{TOPIC_ID}] writer final_status={final_status} model={model_id} "
          f"web_search_call_count={search_usage['web_search_call_count'] if search_usage else None} "
          f"attempts={len(attempts_detail)}")

    writer_metadata = {
        "topic_id": TOPIC_ID,
        "topic": TOPIC,
        "model": model_id,
        "reasoning_effort": r3.WRITER_REASONING_EFFORT,
        "developer_message": EN_DEVELOPER_MESSAGE,
        "api_endpoint": "responses.create",
        "response_id": response_id,
        "final_status": final_status,
        "content_attempt_count": len(attempts_detail),
        "web_search_call_count": search_usage["web_search_call_count"] if search_usage else None,
        "web_search_queries": search_usage["queries"] if search_usage else None,
        "concise_brief_passed_to_writer": False,
        "full_fact_registry_passed_to_writer": False,
        "length_lower_bound_words": LENGTH_LOWER_BOUND,
        "length_upper_bound_words": LENGTH_UPPER_BOUND,
    }
    with open(f"{OUT_DIR}/writer_request_metadata.json", "w", encoding="utf-8") as f:
        json.dump(writer_metadata, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/writer_attempts_detail.json", "w", encoding="utf-8") as f:
        json.dump(attempts_detail, f, ensure_ascii=False, indent=2, default=str)
    if sources is not None:
        with open(f"{OUT_DIR}/writer_sources.json", "w", encoding="utf-8") as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)

    if final_status != "STRUCTURE_PASS" or raw_text is None:
        print(f"[{TOPIC_ID}] writerが技術的失敗または構造不適合で終了しました: {final_status}")
        return

    with open(f"{OUT_DIR}/raw_article.md", "w", encoding="utf-8") as f:
        f.write(raw_text)

    structure = restore_r2.validate_point_structure(raw_text)
    word_count = compute_word_count(raw_text)
    length_status = "LENGTH_WITHIN_SOFT_TARGET" if LENGTH_LOWER_BOUND <= word_count <= LENGTH_UPPER_BOUND else "LENGTH_OUTSIDE_SOFT_TARGET"
    diagnostics = {
        "structure_status": structure.status,
        "h3_count": structure.h3_count,
        "headings": structure.headings,
        "word_count": word_count,
        "length_lower_bound_words": LENGTH_LOWER_BOUND,
        "length_upper_bound_words": LENGTH_UPPER_BOUND,
        "length_status": length_status,
    }
    with open(f"{OUT_DIR}/diagnostics.json", "w", encoding="utf-8") as f:
        json.dump(diagnostics, f, ensure_ascii=False, indent=2)
    print(f"[{TOPIC_ID}] structure={structure.status} h3_count={structure.h3_count} "
          f"word_count={word_count} length_status={length_status}")

    # 独立fact checker(writerとは別の新規API呼び出し、R3のロジックをそのまま再利用)
    fact_check_prompt = r3.build_fact_check_prompt(TOPIC, raw_text, sources or [])
    with open(f"{OUT_DIR}/audit/fact_check_prompt.txt", "w", encoding="utf-8") as f:
        f.write(fact_check_prompt)

    def make_fc_fn():
        return r3.make_fact_checker_fn(fact_check_prompt)

    print(f"[{TOPIC_ID}] 独立fact checker呼び出し開始...")
    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep,
    )
    print(f"[{TOPIC_ID}] fact_check final_status={fc_status} "
          f"verdict={fc_result.get('verdict') if fc_result else None}")

    fact_qa_record = {
        "topic_id": TOPIC_ID,
        "final_status": fc_status,
        "model": fc_model,
        "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts),
        "result": fc_result,
    }
    with open(f"{OUT_DIR}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/fact_check_attempts_detail.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    print(f"[{TOPIC_ID}] 完了。出力: {OUT_DIR}/raw_article.md")


if __name__ == "__main__":
    main()
