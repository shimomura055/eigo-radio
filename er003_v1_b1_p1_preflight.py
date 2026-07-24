# ============================================================
# er003_v1_b1_p1_preflight.py
# ER-003-B1-P1: 実API実行前の最小限の確認(APIは呼ばない)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p1_preflight.py

from __future__ import annotations

import json

import er003_b1_article as b1

if __name__ == "__main__":
    ja = b1.load_japanese_master()
    en = b1.load_natural_english_source()

    template = b1.load_b1_prompt_template()
    user_message = b1.build_b1_user_message(en, template=template)

    result = {
        "topic_id": b1.TOPIC_ID,
        "japanese_master_path": b1.JAPANESE_MASTER_PATH,
        "japanese_master_sha256": b1.sha256_text(ja),
        "japanese_master_word_count_chars": len(ja),
        "natural_english_source_path": b1.NATURAL_ENGLISH_SOURCE_PATH,
        "natural_english_source_sha256": b1.sha256_text(en),
        "natural_english_source_word_count_chars": len(en),
        "prompt_template_path": b1.B1_PROMPT_TEMPLATE_PATH,
        "prompt_template_sha256": b1.sha256_text(template),
        "user_message_contains_source": en[:40] in user_message,
        "user_message_length_chars": len(user_message),
        "model": b1.B1_MODEL,
        "reasoning_effort": b1.B1_REASONING_EFFORT,
        "developer_message": b1.B1_DEVELOPER_MESSAGE,
        "api_calls_made": 0,
    }

    with open("er003_output/b1_p1/A01/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
