# -*- coding: utf-8 -*-
"""End User sync gate の一括dry sync(API 0・ローカルfaster-whisperのみ・enduser/は書かない)。

全行を同期し、gateに落ちる行を全列挙する(1行ずつSTOPを繰り返さない)。閾値は変更しない。
使い方: python tools/er135_enduser_sync_dry_01.py --dev-dir <pages_dir> --family z --run-dir <run> --cache-dir <cache> --out <json> [--no-proper-nouns]
rc=0: 全行PASS / rc=3: 落ち行あり(--out に列挙)
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import er135_enduser_page_01 as P  # noqa: E402
import er135_enduser_sync_01 as S  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-dir", required=True)
    ap.add_argument("--family", required=True)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="medium")
    ap.add_argument("--no-proper-nouns", action="store_true", help="修正前の測定(initial_prompt・正規化なし)")
    a = ap.parse_args(argv)
    dev = Path(a.dev_dir).resolve()
    raw = (dev / "index.html").read_bytes()
    rows_by_level, _st, meta = P.build_rows_from_dev_html(raw.decode("utf-8"), {"family": a.family, "dev_dir": dev, "dev_index_sha256": P.sha256_text_bytes(raw)})
    pn = None if a.no_proper_nouns else P.proper_nouns_for_run(a.run_dir, a.family, rows_by_level, meta)
    os.makedirs(a.cache_dir, exist_ok=True)
    res = {"proper_nouns": pn, "levels": {}}
    bad = 0
    for lv, rows in rows_by_level.items():
        r = S.sync_level(str(dev), P.rows_for_sync(rows), cache_dir=a.cache_dir, model=a.model, align_mode="direct", proper_nouns=pn, collect_failures=True)
        res["levels"][lv] = {"gate": r["gate"]["status"], "dry_failures": r["dry_failures"], "warnings": r["gate"]["warnings"],
                             "min_row_ratio": r["gate"]["token_match"]["min_row_ratio"], "cost": r["cost"]}
        bad += len(r["dry_failures"])
    res["failed_rows_total"] = bad
    Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("failed_rows", bad, {lv: (v["gate"], v["min_row_ratio"]) for lv, v in res["levels"].items()})
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
