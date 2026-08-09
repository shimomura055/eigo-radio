# ============================================================
# er003_v1_a2_kp_select_generate.py
# ER-003-CROSSLEVEL-AUDIO-02: A01・ADD03 A2版Key Phrase正式選定
# ============================================================
# 新しい選定ロジックは設計しない。既存の方式L選定
# (er003_b1_p2_keywords.py/er003_key_words_production.py)+
# Canonicalization(er003_key_words_canonicalization.py、ER-003-KP-02-R1
# 「最小十分」版)を、入力だけB1本文からA2最終英語本文
# (er003_output/a2_p1_r3/{article}/a2_article_raw.md、STRUCT-04/05で
# 確定した英語Full Story/Points/In One Lineの原本)へ差し替えて適用する。
# B1で選定済みのKey Phraseをそのまま流用しない(A2本文の語彙で実際に
# 支援価値が高い表現を、同じ方式で選び直す)。
#
# プロンプトテンプレート文言は「B1英語記事本文から」という既存の固定文言
# のまま変更しない(大規模な方式変更をしないため)。入力テキスト自体が
# A2本文であるため、実際の選定はA2本文の難所を対象に行われる。

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_production as prod
import er003_natural_source as natural_source

sha256_text = natural_source.sha256_text

STRATEGY_ID = prod.STANDARD_STRATEGY_ID  # "L"
SOURCE_LEVEL = "A2"
MAX_SELECTOR_ATTEMPTS = 1


def _a2_source_path(article_id: str) -> str:
    return f"er003_output/a2_p1_r3/{article_id}/a2_article_raw.md"


def _out_dir(article_id: str) -> str:
    return f"er003_output/a2_p2_keywords/{article_id}"


def load_a2_article(article_id: str) -> str:
    with open(_a2_source_path(article_id), encoding="utf-8") as f:
        return f.read()


def run_selection(article_id: str) -> dict:
    """方式L選定(Part A)をA2本文へ適用する。B1版
    (er003_v1_repro01/02_b1_p2_keywords_generate.py)と同一パターン、
    入力パス・出力先だけがA2用。"""
    out_dir = _out_dir(article_id)
    os.makedirs(out_dir, exist_ok=True)

    a2_article = load_a2_article(article_id)
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(a2_article, template=template)
    with open(f"{out_dir}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_selector_factory():
        return bk.make_selector_fn(user_message)

    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, make_selector_factory, a2_article,
        strategy_id=STRATEGY_ID, max_attempts=MAX_SELECTOR_ATTEMPTS,
    )

    last_attempt = attempts[-1] if attempts else None
    raw_text = last_attempt.get("raw_text") if last_attempt else None
    if raw_text:
        with open(f"{out_dir}/keywords_selector_raw.md", "w", encoding="utf-8") as f:
            f.write(raw_text)

    runtime_metadata = {
        "article_id": article_id,
        "strategy_id": STRATEGY_ID,
        "source_level": SOURCE_LEVEL,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "model": bk.SELECTOR_MODEL,
        "reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "developer_message": bk.SELECTOR_DEVELOPER_MESSAGE,
        "a2_article_path": _a2_source_path(article_id),
        "a2_article_sha256": sha256_text(a2_article),
        "max_attempts": MAX_SELECTOR_ATTEMPTS,
        "api_call_count": len(attempts),
        "auto_regeneration_count": 0,
        "final_status": status,
        "model_id": model_id,
        "response_id": response_id,
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    result = {"status": status, "parsed": parsed, "runtime_metadata": runtime_metadata}
    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result

    selected_json = bk.build_selected_keywords_json(parsed)
    selected_json["source_level"] = SOURCE_LEVEL
    with open(f"{out_dir}/keywords_selected.json", "w", encoding="utf-8") as f:
        json.dump(selected_json, f, ensure_ascii=False, indent=2)

    reading_copy = bk.build_selected_keywords_reading_copy(selected_json)
    with open(f"{out_dir}/keywords_selected_for_review.md", "w", encoding="utf-8") as f:
        f.write(reading_copy)

    result["selected_json"] = selected_json
    return result


def run_canonicalization(article_id: str) -> dict:
    """Canonicalization(最小十分単位への正規化)をA2選定結果へ適用する。
    er003_v1_kp01_canonicalize_generate.run_for_articleと同一パターン。"""
    out_dir = _out_dir(article_id)
    article_text = load_a2_article(article_id)
    with open(f"{out_dir}/keywords_runtime_metadata.json", encoding="utf-8") as f:
        runtime_metadata = json.load(f)
    original_items = runtime_metadata["attempts_detail"][-1]["parsed"]["items"]

    template = kc.load_prompt_template()
    user_message = kc.build_user_message(original_items, article_text, template=template)
    with open(f"{out_dir}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        return kc.make_canonicalization_fn(user_message)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(make_factory, original_items)

    result = {"article_id": article_id, "status": status}
    with open(f"{out_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "article_id": article_id,
            "canonicalization_version": kc.CANONICALIZATION_VERSION,
            "record_status": "PROTOTYPE",
            "approval_status": "NOT_APPROVED",
            "model": kc.SELECTOR_MODEL,
            "reasoning_effort": kc.SELECTOR_REASONING_EFFORT,
            "a2_article_path": _a2_source_path(article_id),
            "a2_article_sha256": sha256_text(article_text),
            "source_selection_path": f"{out_dir}/keywords_runtime_metadata.json",
            "final_status": status,
            "model_id": model_id,
            "response_id": response_id,
            "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        }, f, ensure_ascii=False, indent=2)

    if status not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return result

    merged = kc.merge_canonicalization_result(original_items, parsed["items"])
    merged["article_id"] = article_id
    merged["canonicalization_version"] = kc.CANONICALIZATION_VERSION
    merged["source_level"] = SOURCE_LEVEL
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    result["merged"] = merged
    return result


def run_for_article(article_id: str) -> dict:
    sel = run_selection(article_id)
    if sel["status"] != "KEY_WORDS_STRUCTURE_PASS":
        return {"article_id": article_id, "selection": sel, "canonicalization": None}
    can = run_canonicalization(article_id)
    return {"article_id": article_id, "selection": sel, "canonicalization": can}


if __name__ == "__main__":
    for aid in ("A01", "ADD03"):
        print(f"=== {aid} ===")
        r = run_for_article(aid)
        print(f"  selection status: {r['selection']['status']}")
        if r["canonicalization"]:
            print(f"  canonicalization status: {r['canonicalization']['status']}")
            if "merged" in r["canonicalization"]:
                for item in r["canonicalization"]["merged"]["items"]:
                    print(f"    rank {item['rank']}: display={item['display_phrase']!r} -> "
                          f"key_phrase={item['key_phrase']!r} (changed={item['changed_from_display_phrase']})")
