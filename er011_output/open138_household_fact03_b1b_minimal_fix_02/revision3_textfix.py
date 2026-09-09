# ============================================================
# revision3_textfix.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続)
# ============================================================
# revision3_qa.pyでFact Checker PASS・Ledger Deviation COMPLIANTを確認した
# revision3a("...low-humidity drawer instead."、"the low-humidity one"の
# 省略されやすい反復パターンを解消)を、fact03_fix_02/b1b/article.mdと
# parts.json[point_one_body](revision2文言)へ上書き適用する。
from __future__ import annotations

import json
import os

DST_DIR = "er003_output/n3_01/household/fact03_fix_02/b1b"
DIFF_OUT_PATH = "er011_output/open138_household_fact03_b1b_minimal_fix_02/textfix_diff_revision3.json"

REVISION2_BODY = (
    "The common shortcut—fruit in low humidity and vegetables in high humidity"
    "—has important exceptions. Strawberries are one case: some refrigerator "
    "makers place them in the high-humidity drawer, others in the low-humidity one. "
    "The food’s behavior matters more than its category."
)
REVISION3A_BODY = (
    "The common shortcut—fruit in low humidity and vegetables in high humidity"
    "—has important exceptions. Strawberries are one case: some refrigerator "
    "makers put them in the high-humidity drawer, while others put them in the "
    "low-humidity drawer instead. The food’s behavior matters more than its "
    "category."
)


def assert_exactly_one(text: str, needle: str, where: str) -> None:
    n = text.count(needle)
    assert n == 1, f"{where}に対象文が{n}箇所見つかりました(想定は1箇所)。"


def replace_in_article(diff_log: list) -> None:
    path = f"{DST_DIR}/article.md"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert_exactly_one(text, REVISION2_BODY, "article.md")
    new_text = text.replace(REVISION2_BODY, REVISION3A_BODY)
    diff_log.append({"file": "article.md", "old_text": REVISION2_BODY, "new_text": REVISION3A_BODY})
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)


def replace_in_parts_json(diff_log: list) -> None:
    path = f"{DST_DIR}/parts.json"
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    parts = json.loads(raw)
    assert_exactly_one(raw, REVISION2_BODY, "parts.json(raw)")
    assert parts["point_one_body"] == REVISION2_BODY, (
        "parts.json[point_one_body]がrevision2文言と一致しません。"
        f"実際: {parts['point_one_body']!r}"
    )
    diff_log.append({"file": "parts.json", "field": "point_one_body",
                      "old_text": REVISION2_BODY, "new_text": REVISION3A_BODY})
    new_raw = raw.replace(REVISION2_BODY, REVISION3A_BODY)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_raw)
    with open(path, encoding="utf-8") as f:
        json.load(f)


def main():
    assert os.path.isdir(DST_DIR), f"{DST_DIR} が存在しません。"
    diff_log = []
    replace_in_article(diff_log)
    replace_in_parts_json(diff_log)
    with open(DIFF_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"diff": diff_log}, f, ensure_ascii=False, indent=2)
    print(json.dumps({"diff": diff_log}, ensure_ascii=True, indent=2))
    print(f"\n[revision3_textfix] diff -> {DIFF_OUT_PATH}")


if __name__ == "__main__":
    main()
