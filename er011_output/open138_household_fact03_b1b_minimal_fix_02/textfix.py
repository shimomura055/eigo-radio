# ============================================================
# textfix.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(OPEN-138)
# ============================================================
# ユーザー決定(2026-09-09)に基づき、Numeric Precision修正(Theme 2
# rerun_04、OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04)と
# 同じ「既存承認済みArtifactへの最小修正例外」方式で、Household公開B1記事
# (2026-08-17承認、er003_output/n3_01/household/b1b/)のpoint_one_bodyのみ
# 差し替える。FACT-03 v4(usable: no、イチゴ・柑橘類=高湿度という家庭用
# 設定の断定を家電メーカー間の見解不一致により削除)に基づく。
#
# A2(er003_output/n3_01/household/a2/)は、article.md・parts.json・
# a2_support_texts.json・key_phrases/keywords_canonicalized.json全てに
# strawberr*/citrus/orangeの一致がゼロ件であることを事前grepで確認済み
# (元々FACT-03の問題箇所を含んでいない)。よってA2は変更対象外、コピー
# すら行わない(元のer003_output/n3_01/household/a2/がそのまま最終成果物)。
#
# 本スクリプトの役割:
#   1. b1b/の全生成物をfact03_fix_02/b1bへコピーする。
#   2. article.md・parts.jsonのみ、対象文が本文中ちょうど1回ずつで
#      あることを確認したうえで置換する(不一致ならAssertionErrorで
#      即停止)。
#   3. Preview/Comment/Key Phrase等、本文以外の場所に旧文言の断片が
#      残っていないかをリポジトリ全体(コピー後のツリー)に対してgrepし、
#      結果を列挙する。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_output/open138_household_fact03_b1b_minimal_fix_02/textfix.py
from __future__ import annotations

import json
import os
import shutil

SRC_DIR = "er003_output/n3_01/household/b1b"
DST_ROOT = "er003_output/n3_01/household/fact03_fix_02"
DST_DIR = f"{DST_ROOT}/b1b"
DIFF_OUT_PATH = "er011_output/open138_household_fact03_b1b_minimal_fix_02/textfix_diff.json"

OLD_POINT_ONE_BODY = (
    "The common shortcut—fruit in low humidity and vegetables in high humidity"
    "—has important exceptions. Strawberries and citrus fruits, including oranges, "
    "prefer high humidity. UC Davis lists an ideal humidity of 90 to 95 percent for both. "
    "The food’s behavior matters more than its category."
)
NEW_POINT_ONE_BODY = (
    "The common shortcut—fruit in low humidity and vegetables in high humidity"
    "—has important exceptions. Strawberries and citrus fruits, including oranges, "
    "are one case. Refrigerator makers do not even agree on which drawer suits them best. "
    "The food’s behavior matters more than its category."
)


def assert_exactly_one(text: str, needle: str, where: str) -> None:
    n = text.count(needle)
    assert n == 1, (
        f"{where}に対象文が{n}箇所見つかりました(想定は1箇所)。"
        "置換対象が一意でないため処理を停止します。"
    )


def replace_in_article(diff_log: list) -> None:
    path = f"{DST_DIR}/article.md"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert_exactly_one(text, OLD_POINT_ONE_BODY, "article.md")
    new_text = text.replace(OLD_POINT_ONE_BODY, NEW_POINT_ONE_BODY)
    diff_log.append({"file": "article.md", "old_text": OLD_POINT_ONE_BODY, "new_text": NEW_POINT_ONE_BODY})
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)


def replace_in_parts_json(diff_log: list) -> None:
    path = f"{DST_DIR}/parts.json"
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    parts = json.loads(raw)
    assert_exactly_one(raw, OLD_POINT_ONE_BODY, "parts.json(raw)")
    assert parts["point_one_body"] == OLD_POINT_ONE_BODY, (
        "parts.json[point_one_body]が想定していた旧文言と一致しません。"
        f"実際: {parts['point_one_body']!r}"
    )
    diff_log.append({
        "file": "parts.json", "field": "point_one_body",
        "old_text": OLD_POINT_ONE_BODY, "new_text": NEW_POINT_ONE_BODY,
    })
    new_raw = raw.replace(OLD_POINT_ONE_BODY, NEW_POINT_ONE_BODY)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_raw)
    with open(path, encoding="utf-8") as f:
        json.load(f)


def scan_other_occurrences() -> dict:
    """置換後のfact03_fix_02/b1bツリー全体で、旧文言の断片(削除対象の
    「prefer high humidity」文脈につながる"90 to 95 percent"・
    strawberries/citrus/orangesの並び)が、point_one_body以外(Preview/
    Comment/Key Phrase実出力等)に現存するか列挙する。過去の生成過程ログ
    (audit/prompt.txt・audit/deviation_full_record.json等、当時のLedger
    v2/v3を引用したprompt記録)は事前調査で確認済みの非STOP事由として扱う
    (実際に読み上げられる/表示されるcontent自体への混入のみが問題)。"""
    findings = {"90 to 95 percent": [], "strawberries and citrus": []}
    for root, _dirs, files in os.walk(DST_DIR):
        for fn in files:
            if not fn.endswith((".md", ".json", ".txt")):
                continue
            full = os.path.join(root, fn)
            with open(full, encoding="utf-8", errors="replace") as f:
                content = f.read()
            for needle in findings:
                if needle.lower() in content.lower():
                    findings[needle].append(os.path.relpath(full, DST_DIR).replace("\\", "/"))
    return findings


def main():
    assert not os.path.exists(DST_DIR), f"{DST_DIR} は既に存在します(重複実行防止のため停止)。"
    os.makedirs(DST_ROOT, exist_ok=True)
    shutil.copytree(SRC_DIR, DST_DIR)
    print(f"[COPY] {SRC_DIR} -> {DST_DIR}")

    diff_log = []
    replace_in_article(diff_log)
    replace_in_parts_json(diff_log)

    findings = scan_other_occurrences()

    out = {"diff": diff_log, "other_occurrences_after_replace": findings}
    with open(DIFF_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out, ensure_ascii=True, indent=2))
    print(f"\n[textfix] diff -> {DIFF_OUT_PATH}")


if __name__ == "__main__":
    main()
