# ============================================================
# er003_v1_repro01_b1_p2_keywords_generate.py
# ER-003-REPRO-01-KP: SNS規制記事(A02) B1 Key Words選定(方式L、Part Aのみ)
# ============================================================
# er003_b1_p2_keywords.py(A01専用、ARTICLE_ID/B1_ARTICLE_PATH固定)は
# 変更しない。同モジュール・er003_key_words_production.pyの汎用部品
# (load_prompt_template/build_user_message/make_selector_fn/
# build_selected_keywords_json/build_selected_keywords_reading_copy、
# および記事非依存のprod.run_production_selection_gate)をそのまま
# 再利用し、article_idだけをこのスクリプト側でA02として渡す。
#
# 新しい選定ロジックは一切設計していない。ER-003-P2Iで正式採用された
# 標準方式L(Listening Blocker Ranking)を、B2本文ではなくA02の承認済み
# B1本文(er003_output/b1_p1/A02/b1_article_raw.md、本日ER-003-REPRO-01
# Stage1-2で新規生成、まだユーザー未承認)へ適用する。
#
# Part B(Listening Preview 3案)は今回のユーザー指示の対象外のため
# 実行しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_repro01_b1_p2_keywords_generate.py

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er003_key_words_production as prod
import er003_natural_source as natural_source

ARTICLE_ID = "A02"
STRATEGY_ID = prod.STANDARD_STRATEGY_ID  # "L"
SOURCE_LEVEL = "B1"
MAX_SELECTOR_ATTEMPTS = 1  # P2と同じく自動再選定・自動再実行は行わない

B1_ARTICLE_PATH = f"er003_output/b1_p1/{ARTICLE_ID}/b1_article_raw.md"
OUT_DIR = f"er003_output/b1_p2/{ARTICLE_ID}"

sha256_text = natural_source.sha256_text


def load_b1_article() -> str:
    with open(B1_ARTICLE_PATH, encoding="utf-8") as f:
        return f.read()


def run_part_a(make_selector_factory=None) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)

    b1_article = load_b1_article()
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(b1_article, template=template)
    with open(f"{OUT_DIR}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    if make_selector_factory is None:
        def make_selector_factory():
            return bk.make_selector_fn(user_message)

    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        ARTICLE_ID, make_selector_factory, b1_article,
        strategy_id=STRATEGY_ID, max_attempts=MAX_SELECTOR_ATTEMPTS,
    )

    last_attempt = attempts[-1] if attempts else None
    raw_text = last_attempt.get("raw_text") if last_attempt else None
    if raw_text:
        with open(f"{OUT_DIR}/keywords_selector_raw.md", "w", encoding="utf-8") as f:
            f.write(raw_text)

    runtime_metadata = {
        "article_id": ARTICLE_ID,
        "strategy_id": STRATEGY_ID,
        "source_level": SOURCE_LEVEL,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "model": bk.SELECTOR_MODEL,
        "reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "developer_message": bk.SELECTOR_DEVELOPER_MESSAGE,
        "b1_article_path": B1_ARTICLE_PATH,
        "b1_article_sha256": sha256_text(b1_article),
        "max_attempts": MAX_SELECTOR_ATTEMPTS,
        "api_call_count": len(attempts),
        "auto_regeneration_count": 0,
        "final_status": status,
        "model_id": model_id,
        "response_id": response_id,
        "attempts_detail": [
            {k: v for k, v in a.items() if k != "raw_text"} for a in attempts
        ],
    }
    with open(f"{OUT_DIR}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    result = {"status": status, "parsed": parsed, "runtime_metadata": runtime_metadata}

    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result

    selected_json = bk.build_selected_keywords_json(parsed)
    with open(f"{OUT_DIR}/keywords_selected.json", "w", encoding="utf-8") as f:
        json.dump(selected_json, f, ensure_ascii=False, indent=2)

    reading_copy = bk.build_selected_keywords_reading_copy(selected_json)
    with open(f"{OUT_DIR}/keywords_selected_for_review.md", "w", encoding="utf-8") as f:
        f.write(reading_copy)

    result["selected_json"] = selected_json
    return result


if __name__ == "__main__":
    part_a = run_part_a()
    print(f"Part A status: {part_a['status']}")
    if part_a["status"] != "KEY_WORDS_STRUCTURE_PASS":
        print("Part A did not pass.")
    else:
        for item in part_a["selected_json"]["items"]:
            print(f"  rank {item['rank']}: {item['canonical_english']!r}")
