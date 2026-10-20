# -*- coding: utf-8 -*-
"""当日費用の内訳突合(read-only、API 0)。daily_dev_cost_01の価格関数を再利用し、
(a)run dir別 (b)theme tag別 (c)同一response_idの重複(二重計上) (d)ledger行別 を出す。
管理ID: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_01 W6。"""
from __future__ import annotations
import argparse, collections, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "pm", "tools"))
import daily_dev_cost_01 as dd


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-10-20")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--json-out", required=True)
    a = ap.parse_args(argv)
    prices = dd.load_prices(a.repo_root)
    by_dir = collections.defaultdict(float)
    by_theme = collections.defaultdict(float)
    by_file = collections.defaultdict(float)
    seen = collections.defaultdict(list)  # response_id -> [(file, jpy)]
    total = 0.0
    nrec = 0
    for path in dd.iter_log_files(a.repo_root):
        rel = os.path.relpath(path, a.repo_root).replace("\\", "/")
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(rec, dict) or dd.to_jst_date(rec.get("timestamp")) != a.date:
                continue
            usd, why = dd.price_record(rec, prices)
            if usd is None:
                continue
            jpy = usd * dd.USD_JPY
            nrec += 1
            total += jpy
            parts = rel.split("/")
            by_dir["/".join(parts[:2])] += jpy
            by_file[rel] += jpy
            by_theme[f"{rec.get('theme')}|{rec.get('stage')}"] += jpy
            rid = rec.get("response_id")
            if rid:
                seen[rid].append((rel, jpy))
    dup_total = 0.0
    dup_pairs = collections.defaultdict(float)
    for rid, lst in seen.items():
        if len(lst) > 1:
            extra = sum(j for _, j in lst[1:])  # 1件目を正とし、2件目以降を二重計上分
            dup_total += extra
            dup_pairs[" + ".join(sorted({f.split('/')[0] + '/' + f.split('/')[1] for f, _ in lst}))] += extra
    ledger = dd.aggregate_ledger(os.path.join(a.repo_root, "docs/pm/REPORT_LEDGER.md"), a.date)
    out = {
        "date": a.date, "records": nrec, "total_jpy_log": round(total, 2),
        "duplicate_response_id_extra_jpy": round(dup_total, 2),
        "total_jpy_dedup": round(total - dup_total, 2),
        "dup_by_file_pair": {k: round(v, 2) for k, v in sorted(dup_pairs.items(), key=lambda x: -x[1])},
        "by_dir2_jpy": {k: round(v, 2) for k, v in sorted(by_dir.items(), key=lambda x: -x[1])},
        "by_theme_stage_jpy": {k: round(v, 2) for k, v in sorted(by_theme.items(), key=lambda x: -x[1])},
        "by_file_jpy_top15": {k: round(v, 2) for k, v in sorted(by_file.items(), key=lambda x: -x[1])[:15]},
        "ledger": ledger,
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.json_out)), exist_ok=True)
    json.dump(out, open(a.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
