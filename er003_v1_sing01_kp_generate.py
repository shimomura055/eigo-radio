# ============================================================
# er003_v1_sing01_kp_generate.py
# ER-003-B1-NOVEL-AUDIO-01: SING01 Key Phrase選定(方式L)+ Canonicalization
# ============================================================
# 既存のStrategy L(Listening Blocker Ranking)selector・Canonicalization
# の仕組み(er003_b1_p2_keywords.py/er003_key_words_canonicalization.py)を
# そのまま再利用し、入力をSING01のB2記事本文へ差し替える。新しい選定
# ロジックは一切設計しない(CURRENT_SPEC.mdのKey Phrase節: 方式L+
# Canonicalization+minimum sufficient+semantic safeguardsをそのまま使用)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_kp_generate.py

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc

ARTICLE_ID = "SING01"
SOURCE_LEVEL = "B2"
ARTICLE_PATH = "er003_output/novel_audio_01/SING01/article/B2_article.md"
OUT_DIR = "er003_output/novel_audio_01/SING01/keyphrases"


def load_article() -> str:
    with open(ARTICLE_PATH, encoding="utf-8") as f:
        return f.read()


def run_selection(article_text: str) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(article_text, template=template)
    with open(f"{OUT_DIR}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_selector_factory():
        return bk.make_selector_fn(user_message)

    parsed, status, attempts, model_id, response_id = bk.run_selection_gate(
        make_selector_factory, article_text)

    with open(f"{OUT_DIR}/keywords_selection_result.json", "w", encoding="utf-8") as f:
        json.dump({"status": status, "parsed": parsed, "model": model_id, "response_id": response_id,
                    "attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts]},
                   f, ensure_ascii=False, indent=2, default=str)

    return {"status": status, "parsed": parsed}


def run_canonicalization(article_text: str, original_items: list) -> dict:
    template = kc.load_prompt_template()
    user_message = kc.build_user_message(original_items, article_text, template=template)
    with open(f"{OUT_DIR}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        return kc.make_canonicalization_fn(user_message)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(make_factory, original_items)

    with open(f"{OUT_DIR}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({"status": status, "model": model_id, "response_id": response_id,
                    "attempts": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts]},
                   f, ensure_ascii=False, indent=2, default=str)

    if status != "CANONICALIZATION_STRUCTURE_PASS" and parsed is None:
        return {"status": status, "merged": None}

    merged = kc.merge_canonicalization_result(original_items, parsed["items"])
    merged["article_id"] = ARTICLE_ID
    merged["canonicalization_version"] = kc.CANONICALIZATION_VERSION
    merged["source_level"] = SOURCE_LEVEL
    with open(f"{OUT_DIR}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    return {"status": status, "merged": merged}


def main():
    article_text = load_article()
    print("[SING01-KP] Strategy L selection開始...")
    sel = run_selection(article_text)
    print(f"[SING01-KP] selection status={sel['status']}")
    if sel["status"] != "KEY_WORDS_STRUCTURE_PASS":
        print("[SING01-KP] selectionが不合格のため中断します。")
        return

    items = sorted(sel["parsed"]["items"], key=lambda it: it["rank"])
    for it in items:
        print(f"  rank {it['rank']}: {it['display_phrase']!r} <- {it['source_span']!r}")

    print("[SING01-KP] Canonicalization開始...")
    canon = run_canonicalization(article_text, items)
    print(f"[SING01-KP] canonicalization status={canon['status']}")
    if canon["merged"]:
        for it in sorted(canon["merged"]["items"], key=lambda it: it["rank"]):
            print(f"  rank {it['rank']}: key_phrase={it['key_phrase']!r} "
                  f"used_form={it['used_form']!r} ja_gloss={it['ja_gloss']!r} "
                  f"qa={it.get('qa_overall_status')}")
        print("overall_status:", canon["merged"].get("overall_status"))


if __name__ == "__main__":
    main()
