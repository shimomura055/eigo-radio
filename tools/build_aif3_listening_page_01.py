# -*- coding: utf-8 -*-
"""[薄いwrapper] AI-ISLAND-FORM-PRODUCTION-01 委任_03で作成したAI島最終試聴ページbuilderは、SLOT-23 委任_04Cで
標準builder `er019_family_x_listening_page_01.py`(本文ハイライト・Std Part 1・check_page/G3必須・AI島固有文言なし)へ昇格した。
本ファイルは互換のためのwrapper(AI島の既定引数を渡して標準builderを呼ぶだけ)。新規処理はここへ追加しない。
注意: 標準builderは音声ファイル名を `<slug>_<level名>.mp3` に統一した(旧: ai_island_Standard.mp3 等)。AI島の再ビルドはHR承認後の別委任。
使い方: .venv\Scripts\python.exe tools/build_aif3_listening_page_01.py [--run-name run_form_prod_01] [--web user_test/family_x_ai_island_form_01]"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er019_family_x_listening_page_01 as std  # noqa: E402

SLUG = "ai_island_temple"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-name", default="run_form_prod_01")
    ap.add_argument("--web", default="user_test/family_x_ai_island_form_01")
    a = ap.parse_args()
    return std.main(["--slug", SLUG, "--run-name", a.run_name, "--web", a.web])


if __name__ == "__main__":
    sys.exit(main())
