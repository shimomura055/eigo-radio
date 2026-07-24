# ============================================================
# er003_v1_b1_p2_preflight.py
# ER-003-B1-P2: 実API実行前の最小限の確認(APIは呼ばない)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p2_preflight.py

from __future__ import annotations

import json

import er003_b1_p2_keywords as bk
import er003_b1_p2_preview as bp
import er003_natural_source as natural_source

sha256_text = natural_source.sha256_text

if __name__ == "__main__":
    b1_article = bk.load_b1_article()

    kw_template = bk.load_prompt_template()
    kw_user_message = bk.build_user_message(b1_article, template=kw_template)

    preview_template = bp.load_prompt_template()

    result = {
        "article_id": bk.ARTICLE_ID,
        "strategy_id": bk.STRATEGY_ID,
        "b1_article_path": bk.B1_ARTICLE_PATH,
        "b1_article_sha256": sha256_text(b1_article),
        "keywords_prompt_template_path": bk.PROMPT_TEMPLATE_PATH,
        "keywords_prompt_template_sha256": sha256_text(kw_template),
        "keywords_user_message_contains_b1_article": b1_article[:40] in kw_user_message,
        "keywords_selector_model": bk.SELECTOR_MODEL,
        "keywords_selector_reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "keywords_max_attempts": bk.MAX_SELECTOR_ATTEMPTS,
        "preview_prompt_template_path": bp.PROMPT_TEMPLATE_PATH,
        "preview_prompt_template_sha256": sha256_text(preview_template),
        "preview_model": bp.PREVIEW_MODEL,
        "preview_reasoning_effort": bp.PREVIEW_REASONING_EFFORT,
        "api_calls_made": 0,
    }

    with open("er003_output/b1_p2/A01/preflight.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
