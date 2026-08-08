# ============================================================
# er003_v1_kp01_canonicalize_generate.py
# ER-003-KP-01: Key Phrase境界正規化の実行(A01回帰・A02本番・Negative fixture)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_kp01_canonicalize_generate.py

from __future__ import annotations

import json
import os

import er003_key_words_canonicalization as kc
import er003_natural_source as natural_source

sha256_text = natural_source.sha256_text


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_for_article(article_id: str, b1_article_path: str, runtime_metadata_path: str, out_dir: str) -> dict:
    """既存の方式L選定結果(runtime_metadata_pathのattempts_detail最終試行)
    を読み込み、canonicalization(この工程)だけを新規に実行する。
    keywords_selected.json・keywords_runtime_metadata.json(方式L選定の
    成果物)は一切変更しない。"""
    article_text = _load_text(b1_article_path)
    runtime_metadata = _load_json(runtime_metadata_path)
    original_items = runtime_metadata["attempts_detail"][-1]["parsed"]["items"]

    template = kc.load_prompt_template()
    user_message = kc.build_user_message(original_items, article_text, template=template)
    os.makedirs(out_dir, exist_ok=True)
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
            "b1_article_path": b1_article_path,
            "b1_article_sha256": sha256_text(article_text),
            "source_selection_path": runtime_metadata_path,
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
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    result["merged"] = merged
    return result


NEGATIVE_FIXTURE_ARTICLE_TEXT = (
    "There are a lot of small changes in this plan, and a number of families "
    "already follow similar routines at the same time each night. On the other "
    "hand, some experts describe the new rule as the same as an existing "
    "voluntary guideline."
)

NEGATIVE_FIXTURE_ITEMS = [
    {"rank": 1, "display_phrase": "a lot of",
     "source_span": "a lot of", "source_sentence": "There are a lot of small changes in this plan."},
    {"rank": 2, "display_phrase": "a number of",
     "source_span": "a number of",
     "source_sentence": "and a number of families already follow similar routines at the same time each night."},
    {"rank": 3, "display_phrase": "at the same time",
     "source_span": "at the same time",
     "source_sentence": "and a number of families already follow similar routines at the same time each night."},
    {"rank": 4, "display_phrase": "on the other hand",
     "source_span": "On the other hand",
     "source_sentence": "On the other hand, some experts describe the new rule as the same as an "
                         "existing voluntary guideline."},
    {"rank": 5, "display_phrase": "the same as",
     "source_span": "the same as",
     "source_sentence": "On the other hand, some experts describe the new rule as the same as an "
                         "existing voluntary guideline."},
]


def run_negative_fixtures(out_dir: str = "er003_output/kp01_negative_fixtures") -> dict:
    """Rule3(固定表現を破壊しない)の検証専用データ。実記事本文由来では
    ないため、production承認済みKey Phraseとしては扱わない(アルゴリズム
    単体テスト用データであることをmetadataに明記する)。"""
    os.makedirs(out_dir, exist_ok=True)

    template = kc.load_prompt_template()
    user_message = kc.build_user_message(NEGATIVE_FIXTURE_ITEMS, NEGATIVE_FIXTURE_ARTICLE_TEXT, template=template)
    with open(f"{out_dir}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        return kc.make_canonicalization_fn(user_message)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
        make_factory, NEGATIVE_FIXTURE_ITEMS)

    with open(f"{out_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "data_kind": "ALGORITHM_TEST_ONLY_NOT_PRODUCTION",
            "note": "本文由来ではない、Rule3(固定表現保持)検証専用の合成fixture。"
                    "承認済みKey Phraseとして製品成果物には使用しない。",
            "canonicalization_version": kc.CANONICALIZATION_VERSION,
            "model": kc.SELECTOR_MODEL,
            "reasoning_effort": kc.SELECTOR_REASONING_EFFORT,
            "final_status": status,
            "model_id": model_id,
            "response_id": response_id,
            "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        }, f, ensure_ascii=False, indent=2)

    result = {"status": status}
    if status != "CANONICALIZATION_PASS":
        return result

    merged = kc.merge_canonicalization_result(NEGATIVE_FIXTURE_ITEMS, parsed["items"])
    merged["data_kind"] = "ALGORITHM_TEST_ONLY_NOT_PRODUCTION"
    merged["canonicalization_version"] = kc.CANONICALIZATION_VERSION
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    result["merged"] = merged
    return result


# ============================================================
# ER-003-KP-02: Over-minimization(削りすぎ)検証専用fixture
# ============================================================
# 実記事本文由来ではない、アルゴリズムテスト専用データ。「the urge to
# watch」のように、display_phraseが既に文脈限定語を落とした後でも、
# 単独で聞くと意味が欠けた断片になる可能性があるケースを、複数の異なる
# 構文(不定詞to/前置詞of/目的語なし等)で検証する。
OVER_MINIMIZATION_ARTICLE_TEXT = (
    "She felt the urge to watch just one more episode before bed. For many "
    "families, rent has become a struggle to pay each month. Workers worried "
    "about the risk of losing jobs during the transition. The minister faced "
    "growing pressure to resign after the scandal."
)

OVER_MINIMIZATION_FIXTURE_ITEMS = [
    {"rank": 1, "display_phrase": "the urge to",
     "source_span": "the urge to watch",
     "source_sentence": "She felt the urge to watch just one more episode before bed."},
    {"rank": 2, "display_phrase": "a struggle to pay",
     "source_span": "a struggle to pay",
     "source_sentence": "For many families, rent has become a struggle to pay each month."},
    {"rank": 3, "display_phrase": "the risk of losing jobs",
     "source_span": "the risk of losing jobs",
     "source_sentence": "Workers worried about the risk of losing jobs during the transition."},
    {"rank": 4, "display_phrase": "pressure to resign",
     "source_span": "pressure to resign",
     "source_sentence": "The minister faced growing pressure to resign after the scandal."},
]


def run_over_minimization_fixtures(out_dir: str = "er003_output/kp02_over_minimization_fixtures") -> dict:
    """Rule3/4(意味理解に必要な補語・目的語は保持する、ただし記事固有
    情報まで抱え込まない)の検証専用データ。実記事本文由来ではない
    ため、production承認済みKey Phraseとしては扱わない。"""
    os.makedirs(out_dir, exist_ok=True)

    template = kc.load_prompt_template()
    user_message = kc.build_user_message(
        OVER_MINIMIZATION_FIXTURE_ITEMS, OVER_MINIMIZATION_ARTICLE_TEXT, template=template)
    with open(f"{out_dir}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        return kc.make_canonicalization_fn(user_message)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
        make_factory, OVER_MINIMIZATION_FIXTURE_ITEMS)

    with open(f"{out_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "data_kind": "ALGORITHM_TEST_ONLY_NOT_PRODUCTION",
            "note": "本文由来ではない、Rule3/4(over-minimization検証)専用の合成fixture。"
                    "承認済みKey Phraseとして製品成果物には使用しない。",
            "canonicalization_version": kc.CANONICALIZATION_VERSION,
            "model": kc.SELECTOR_MODEL,
            "reasoning_effort": kc.SELECTOR_REASONING_EFFORT,
            "final_status": status,
            "model_id": model_id,
            "response_id": response_id,
            "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        }, f, ensure_ascii=False, indent=2)

    result = {"status": status}
    if status not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return result

    merged = kc.merge_canonicalization_result(OVER_MINIMIZATION_FIXTURE_ITEMS, parsed["items"])
    merged["data_kind"] = "ALGORITHM_TEST_ONLY_NOT_PRODUCTION"
    merged["canonicalization_version"] = kc.CANONICALIZATION_VERSION
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    result["merged"] = merged
    return result


if __name__ == "__main__":
    print("=== A01 (regression check, existing approved 5 items) ===")
    r_a01 = run_for_article(
        "A01",
        "er003_output/b1_p1/A01/b1_article_raw.md",
        "er003_output/b1_p2/A01/keywords_runtime_metadata.json",
        "er003_output/b1_p2/A01",
    )
    print(f"status: {r_a01['status']}")
    if "merged" in r_a01:
        for item in r_a01["merged"]["items"]:
            print(f"  rank {item['rank']}: display={item['display_phrase']!r} -> key_phrase={item['key_phrase']!r} "
                  f"(changed={item['changed_from_display_phrase']})")

    print("\n=== A02 (production, includes 'the urge to') ===")
    r_a02 = run_for_article(
        "A02",
        "er003_output/b1_p1/A02/b1_article_raw.md",
        "er003_output/b1_p2/A02/keywords_runtime_metadata.json",
        "er003_output/b1_p2/A02",
    )
    print(f"status: {r_a02['status']}")
    if "merged" in r_a02:
        for item in r_a02["merged"]["items"]:
            print(f"  rank {item['rank']}: display={item['display_phrase']!r} -> key_phrase={item['key_phrase']!r} "
                  f"(changed={item['changed_from_display_phrase']})")

    print("\n=== Negative fixtures (fixed expressions, must stay unchanged) ===")
    r_neg = run_negative_fixtures()
    print(f"status: {r_neg['status']}")
    if "merged" in r_neg:
        for item in r_neg["merged"]["items"]:
            print(f"  rank {item['rank']}: display={item['display_phrase']!r} -> key_phrase={item['key_phrase']!r} "
                  f"(changed={item['changed_from_display_phrase']})")

    print("\n=== Over-minimization fixtures (ER-003-KP-02) ===")
    r_over = run_over_minimization_fixtures()
    print(f"status: {r_over['status']}")
    if "merged" in r_over:
        for item in r_over["merged"]["items"]:
            print(f"  rank {item['rank']}: display={item['display_phrase']!r} -> key_phrase={item['key_phrase']!r} "
                  f"(changed={item['changed_from_display_phrase']})")
