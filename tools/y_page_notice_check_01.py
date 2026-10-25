# -*- coding: utf-8 -*-
"""Family Y 試聴ページの注意書き検査CLI(API呼出なし)。FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B。
実体は er121_family_y_structure_01.check_y_page_notice / page_has_notice。
  - Yページ(--expect y, 既定): 注意書きが本文外の冒頭に1回・noindex が揃っていること。
  - X/Zページ(--expect none): 注意書きが出ていないこと(Y専用の注意書きがX/Zへ漏れていない確認)。
使い方: python -I tools/y_page_notice_check_01.py --page <index.html> [--expect y|none] [--out <json>]
exit: 0=適合 / 1=不適合 / 2=引数・読込エラー"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import er121_family_y_structure_01 as ys  # noqa: E402


def check_file(path: str, expect: str = "y") -> dict:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if expect == "none":
        has = ys.page_has_notice(text)
        res = {"ok": not has, "violations": ["Y_NOTICE_PRESENT_ON_NON_Y_PAGE"] if has else []}
    else:
        res = ys.check_y_page_notice(text)
    return {"page": path, "expect": expect, **res}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True)
    ap.add_argument("--expect", default="y", choices=("y", "none"))
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        r = check_file(a.page, a.expect)
    except OSError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
