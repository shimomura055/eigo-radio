# ============================================================
# er011_open112_theme2_b1_numeric_minimal_fix_rerun_04.py
# 管理ID: OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04
# ============================================================
# ユーザー決定(2026-09-08、正式、選択肢A・決定的置換)に基づき、
# Theme 2 B1完成音声(rerun_03)のpoint_one_body/point_two_bodyのみ、
# 25.2%→about 25%、44.7%→about 45%を機械的な文字列置換で修正する。
# Evidence Compression Editorは再実行しない(ユーザー承認の例外、
# OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01_REPORT.md
# 選択肢A参照)。
#
# 本スクリプトの役割:
#   1. rerun_03/b1bの全生成物をrerun_04/b1bへコピーする(narration wav・
#      article.md・parts.json・audit/*・key_phrases/*等)。
#   2. article.md・parts.jsonのみ、対象2箇所を置換する前に「本文中に
#      ちょうど1回ずつ」であることを確認する(不一致ならAssertionErrorで
#      即停止、無音のまま処理を進めない)。
#   3. Preview/Comment/Key Phrase等、本文以外の場所に同じ数値が現れるか
#      どうかをリポジトリ全体(rerun_04コピー後のツリー)に対してgrepし、
#      結果を列挙する(STOPが必要な新規事実が見つかった場合のみ停止、
#      既知の「Key Phrase生成時プロンプトログへの転記」は事前調査済みの
#      非STOP事由として扱う)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_open112_theme2_b1_numeric_minimal_fix_rerun_04.py
from __future__ import annotations

import json
import os
import re
import shutil
import sys

SRC_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_03/b1b"
DST_ROOT = "er011_output/open112_trend_theme2_b_final_audio_rerun_04"
DST_DIR = f"{DST_ROOT}/b1b"

REPLACEMENTS = [
    {"old": "25.2%", "new": "about 25%", "field": "point_one_body"},
    {"old": "44.7%", "new": "about 45%", "field": "point_two_body"},
]


def assert_exactly_one(text: str, needle: str, where: str) -> None:
    n = text.count(needle)
    assert n == 1, (
        f"{where}に{needle!r}が{n}箇所見つかりました(想定は1箇所)。"
        "置換対象が一意でないため処理を停止します。"
    )


def replace_in_article(diff_log: list) -> None:
    path = f"{DST_DIR}/article.md"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for r in REPLACEMENTS:
        assert_exactly_one(text, r["old"], "article.md")
    new_text = text
    for r in REPLACEMENTS:
        # 該当行を抜き出してdiff記録
        for line in new_text.split("\n"):
            if r["old"] in line:
                before_line = line
                after_line = line.replace(r["old"], r["new"])
                diff_log.append({"file": "article.md", "old_line": before_line, "new_line": after_line})
        new_text = new_text.replace(r["old"], r["new"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)


def replace_in_parts_json(diff_log: list) -> None:
    path = f"{DST_DIR}/parts.json"
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    parts = json.loads(raw)
    for r in REPLACEMENTS:
        assert_exactly_one(raw, r["old"], "parts.json(raw)")
        field_val = parts[r["field"]]
        assert field_val.count(r["old"]) == 1, (
            f"parts.json[{r['field']!r}]に{r['old']!r}が"
            f"{field_val.count(r['old'])}箇所見つかりました(想定は1箇所)。"
        )
        diff_log.append({
            "file": "parts.json", "field": r["field"],
            "old_text": field_val, "new_text": field_val.replace(r["old"], r["new"]),
        })
    new_raw = raw
    for r in REPLACEMENTS:
        new_raw = new_raw.replace(r["old"], r["new"])
    # 直接文字列置換のみ(JSONの再シリアライズはしない、既存の改行・
    # エスケープ・キー順序をそのまま維持するため)。
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_raw)
    # 妥当なJSONのままであることを確認。
    with open(path, encoding="utf-8") as f:
        json.load(f)


def scan_other_occurrences() -> dict:
    """置換後のrerun_04/b1bツリー全体で、対象数値がpoint_one_body/
    point_two_body以外(Preview/Comment/Key Phrase実出力等)に現存するか
    列挙する。事前調査(タスク実行時)で判明した「Key Phrase生成時に使った
    promptログ(*.txt、article.md全文を引用しているだけの入力記録)」は
    許容済みの非STOP事由として明記し、実際のKey Phrase出力JSON
    (keywords_canonicalized.json等)・Preview・Comment本文には存在しない
    ことを機械確認する。"""
    findings = {"25.2%": [], "44.7%": []}
    for root, _dirs, files in os.walk(DST_DIR):
        for fn in files:
            if not fn.endswith((".md", ".json", ".txt")):
                continue
            full = os.path.join(root, fn)
            with open(full, encoding="utf-8", errors="replace") as f:
                content = f.read()
            for needle in findings:
                if needle in content:
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
    out_path = f"{DST_ROOT}/numeric_minimal_fix_diff.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n[numeric_minimal_fix_rerun_04] diff -> {out_path}")


if __name__ == "__main__":
    main()
