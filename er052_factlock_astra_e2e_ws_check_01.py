# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_05 (g): 予算ガードのweb_search課金計上の再確認(API 0、読取専用)。

既存の実run(既定: er052_output/gpt6_wiring_e2e_01/run_02)の raw_usage_log.jsonl から、
(1) 予算ガード efam.compute_cost_jpy_so_far(web_search_call_usd込み、OPEN-242是正済み)、
(2) er019 の cost.json 集計 compute_stage_cost_breakdown、
(3) 保存済み cost.json
の3値を並べ、許容差(±0.01円)内で一致することを確認する。web_search課金行(web_search_call_count>0)の件数と加算額も出す。
使い方: .venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_ws_check_01.py [--run-dir <dir>] [--out <json>]
終了コード: 一致=0 / 不一致=1
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_entertainment_production_runner_01 as e19


def check(run_dir: str, tol: float = 0.01) -> dict:
    log = f"{run_dir}/raw_usage_log.jsonl"
    guard_jpy, _ = efam.compute_cost_jpy_so_far(log)
    cost19 = e19.compute_stage_cost_breakdown(log)["total_jpy"]
    saved = json.load(open(f"{run_dir}/cost.json", encoding="utf-8"))["total_jpy"] if os.path.exists(f"{run_dir}/cost.json") else None
    price = efam._load_pricing()
    rows = [json.loads(l) for l in open(log, encoding="utf-8") if l.strip()]
    ws = [r for r in rows if (r.get("web_search_call_count") or 0) > 0]
    ws_jpy = sum(efam.web_search_call_usd(r, price) for r in ws) * efam.USD_JPY
    ok = saved is not None and abs(guard_jpy - saved) <= tol and abs(cost19 - saved) <= tol
    return {"run_dir": run_dir, "guard_total_jpy": round(guard_jpy, 4), "er019_cost_total_jpy": cost19, "saved_cost_json_jpy": saved,
            "web_search_rows": len(ws), "web_search_calls": sum(r["web_search_call_count"] for r in ws), "web_search_jpy": round(ws_jpy, 4),
            "tolerance": tol, "match": ok}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default="er052_output/gpt6_wiring_e2e_01/run_02")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    r = check(a.run_dir)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        json.dump(r, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return 0 if r["match"] else 1


if __name__ == "__main__":
    sys.exit(main())
