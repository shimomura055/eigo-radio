# -*- coding: utf-8 -*-
"""FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 runner(Trial専用)。

使い方:
  --prepare-sources                 sources_raw -> sources/ と manifest(API 0)
  --variant E0 [A B ...|ALL] --topic mey --samples 2 --out <dir> --budget-jpy 30 [--dry-run]
--dry-run: StubClient(API 0、合成応答)。出力は <out>/_dryrun/ 配下、callログは calls_dryrun.jsonl
           (cost_log*.jsonl/raw_usage_log.jsonlの名前を使わない=日次費用集計に混入させない)。
実run: cost loggerを<out>/raw_usage_log.jsonlへ install(THEME_TAG=XRFR_TRIAL_01、web_search toolは渡さない)。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import er085_research_fact_retention_trial_01_lib as lib


def load_design(path: str) -> dict:
    return lib.read_json(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", default=os.path.join(lib.DOC_DIR, "design_matrix_01.json"))
    ap.add_argument("--variant", nargs="*", default=None, help="E0 A B C D E | ALL")
    ap.add_argument("--topic", nargs="*", default=None)
    ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--out", default=lib.OUT_ROOT)
    ap.add_argument("--budget-jpy", type=float, default=30.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prepare-sources", action="store_true")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    lib.assert_under_out_root(out)
    spec = lib.load_sources_spec()

    if a.prepare_sources:
        m = lib.prepare_sources(spec, out)
        print(json.dumps({t: [(s["id"], s["body_chars"]) for s in d["sources"]] for t, d in m["topics"].items()}, ensure_ascii=False))
        return 0

    design = load_design(a.design)
    variants = list(lib.VARIANTS) if (a.variant is None or a.variant == ["ALL"]) else a.variant
    for v in variants:
        if v not in lib.VARIANTS or v not in design["variants"]:
            raise SystemExit(f"unknown variant {v}")
    topics = a.topic or list(spec["topics"])
    cells = [(v, t, s) for t in topics for s in range(1, a.samples + 1) for v in variants]

    if a.dry_run:
        client = lib.StubClient()
        guard = None
    else:
        import er005_cost_logger as cl
        from dotenv import load_dotenv
        load_dotenv()
        cl.install(os.path.join(out, "raw_usage_log.jsonl"))
        client = lib._vfl01().get_client()
        guard = lib.BudgetGuard(os.path.join(out, "calls_real.jsonl"), a.budget_jpy)

    results = []
    for v, t, s in cells:
        if a.dry_run:
            summ = lib.run_variant(client, v, t, s, spec, out, guard=None, dry_run=True)
        else:
            import er005_cost_logger as cl
            with cl.logging_context(lib.THEME_TAG, f"{v}_{t}_s{s}"):
                summ = lib.run_variant(client, v, t, s, spec, out, guard=guard, dry_run=False)
        results.append(summ)
        print(f"[XRFR][{'DRY' if a.dry_run else 'REAL'}] {v}/{t}/s{s}: facts={summ['n_facts_draft']} kept={summ['n_kept']} calls={summ['n_llm_calls']} "
              f"jpy={summ['cost_jpy']} schema_errs={len(summ['schema_errors'])}")
    spent = guard.spent() if guard else 0.0
    print(f"[XRFR] done cells={len(results)} total_jpy_this_session_log={spent:.3f} dry_run={a.dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
