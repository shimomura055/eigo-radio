# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C Track E: 既存の完了runを『copy-run』として複製し、evidence用の印(EVIDENCE_COPY_RUN.json)を書く。API 0。

  py docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/tools/copy_run_01.py --src <完了runのout dir> --dst <複製先> --by <名前> [--src-input <X: 入力dir> --dst-input <複製先>]

- 元run(公開済み・本番)は読むだけで書換えない。複製先は repo の ignored 領域(er0XX_output)に置く(git管理外)。
- 印 `EVIDENCE_COPY_RUN.json` が無いrunには `er119_kp_human_review_cli_01.py nuance-issue-spec` は使えない(実運用runへの遡及を構造的に防ぐ=Opus M-2)。
- 複製先が既に存在する場合は拒否(上書きしない)。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time

SCHEMA = "eigo_radio_evidence_copy_run_v1"


def copy_run(src: str, dst: str, by: str, purpose: str) -> dict:
    src, dst = os.path.abspath(src), os.path.abspath(dst)
    if not os.path.isdir(src):
        raise SystemExit(f"元runがありません: {src}")
    if os.path.exists(dst):
        raise SystemExit(f"複製先が既に存在します(上書きしません): {dst}")
    shutil.copytree(src, dst)
    marker = {"schema": SCHEMA, "copy_run": dst, "source_run": src, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "by": by, "purpose": purpose}
    with open(os.path.join(dst, "EVIDENCE_COPY_RUN.json"), "w", encoding="utf-8") as f:
        json.dump(marker, f, ensure_ascii=False, indent=2)
    return marker


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--by", required=True)
    ap.add_argument("--purpose", default="NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C runtime evidence(Track E)")
    ap.add_argument("--src-input", default=None, help="X: 入力dir(er019_output/<slug>/<run>)も複製する")
    ap.add_argument("--dst-input", default=None)
    a = ap.parse_args(argv)
    out = {"run": copy_run(a.src, a.dst, a.by, a.purpose)}
    if a.src_input or a.dst_input:
        if not (a.src_input and a.dst_input):
            raise SystemExit("--src-input と --dst-input は両方必要です")
        out["input"] = copy_run(a.src_input, a.dst_input, a.by, a.purpose)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
