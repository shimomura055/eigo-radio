# ============================================================
# er011_open112_theme2_a2_numeric_minimal_fix_rerun_04.py
# 管理ID: OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01
# ============================================================
# Theme 2 B1で承認済みの方式(OPEN-112-THEME2-B1-NUMERIC-PRECISION-
# MINIMAL-FIX-RERUN-04、選択肢A・決定的置換)と同一手順を、Theme 2 A2
# 完成音声(rerun_02/a2)へ適用する。Part 1(本タスクの仕様確認)で、
# 「24.1%」を現行Production Evidence Compression Editor(無変更)へ通すと
# "about 24%"へ丸められることを実データで確認済み(er011_output/
# open112_trend_theme2_a2_numeric_check_01/editor_output.md)。Editor自体は
# 再実行せず(選択肢A、B1と同一の例外的手順)、article.md/parts.jsonの
# "24.1%"を"about 24%"へ機械的な決定的文字列置換のみで修正する。
#
# 出力先: er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2/
# (B1のrerun_04と同じ親ディレクトリ。既存のrerun_04/b1bとplayer.htmlには
# 一切触れない)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_open112_theme2_a2_numeric_minimal_fix_rerun_04.py
from __future__ import annotations

import json
import os
import shutil

SRC_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_02/a2"
DST_ROOT = "er011_output/open112_trend_theme2_b_final_audio_rerun_04"
DST_DIR = f"{DST_ROOT}/a2"

REPLACEMENTS = [
    {"old": "24.1%", "new": "about 24%", "field": "part1"},
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
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_raw)
    with open(path, encoding="utf-8") as f:
        json.load(f)


def scan_other_occurrences() -> dict:
    """置換後のrerun_04/a2ツリー全体で、対象数値がpart1本文以外
    (Preview/Comment/Key Phrase実出力等)に現存するか列挙する。B1の
    minimal-fixと同じ非STOP事由(Key Phrase生成時プロンプトログへの
    転記等)以外に新規のものが見つかった場合は目視で判断できるよう
    列挙のみ行う(自動停止はしない、置換前チェックのassert_exactly_one
    が本質的な安全装置)。"""
    findings = {"24.1%": []}
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
    out_path = f"{DST_ROOT}/numeric_minimal_fix_diff_a2.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n[numeric_minimal_fix_rerun_04_a2] diff -> {out_path}")


if __name__ == "__main__":
    main()
