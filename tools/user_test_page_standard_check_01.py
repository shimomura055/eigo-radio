# -*- coding: utf-8 -*-
"""ユーザー試聴ページ標準適合check CLI(X/Z/Y共通、API呼出なし)。実体は er_user_listening_page_common_01.check_page。
使い方: python -I tools/user_test_page_standard_check_01.py --page <index.html> --out <json> [--levels Standard,Advanced]"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import er_user_listening_page_common_01 as c  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--page", required=True)
ap.add_argument("--out")
ap.add_argument("--levels", default="Standard,Advanced")
a = ap.parse_args()
r = c.check_file(a.page, levels=tuple(a.levels.split(",")), out=a.out)
print(json.dumps({k: (v if k != "checks" else {n: x["ok"] for n, x in v.items()}) for k, v in r.items()}, ensure_ascii=False))
sys.exit(0 if r["overall"] == "PASS" else 1)
