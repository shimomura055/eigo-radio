# -*- coding: utf-8 -*-
"""er083_b3_background_fact_trial_01_run.py
B3背景Fact補完Trial の候補実行CLI(Trial専用。Production runnerは使わない・触らない)。1候補=B3 1 call(再評価は既存の下限2件ロジックに委ねる)。

  python er083_b3_background_fact_trial_01_run.py --article middle_east_yemen_saudi --ledger <path> --theme "<topic>" \
      --candidate baseline|C1|C2|C3 --out-root <dir> --budget-jpy N [--dry-run]

--dry-run: StubClient(API 0)。出力は <out-root>/_dryrun/ 配下。実runは <out-root>/<article>/<candidate>/s<N>/ (cost_log.jsonlも同dir)。
実runの前提: 委任文の承認済みScope・個別Cap内、stop_scope_check_01 rc=0。STOP/STOP_ALL が out-root にあれば開始しない。
有料run(--dry-runなし)のみ cost logger をinstallし cost_log.jsonl に全callを記録する。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import er083_b3_background_fact_trial_01_lib as lib


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--theme", required=True)
    ap.add_argument("--candidate", required=True, choices=lib.CANDIDATE_NAMES)
    ap.add_argument("--out-root", default=lib.OUT_ROOT)
    ap.add_argument("--sample", type=int, default=1, help="sample番号(M5)。出力先 <article>/<candidate>/s<N>")
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--baseline-run-dir", default=lib.PRODUCTION_MEY_RUN,
                    help="Baseline(現行Production選定)の読取元。読取のみ。")
    args = ap.parse_args(argv)

    out_root = os.path.abspath(args.out_root)
    for sentinel in ("STOP", "STOP_ALL"):
        if os.path.exists(os.path.join(out_root, sentinel)):
            print(f"[STOP] {sentinel} センチネルが {out_root} にあります。開始しません。")
            return 3
    if args.sample < 1:
        print("[STOP] --sample は1以上")
        return 4
    cand_dir = os.path.join(out_root, "_dryrun" if args.dry_run else "", args.article, args.candidate, f"s{args.sample}")
    # run単位のcost log(並列プロセスでもBudgetGuardが自分のrunの実費だけを数える。Trial全体はcost_summary_treeで合算=M1/F-1)
    cost_log = os.path.join(out_root, "cost_log_dryrun.jsonl") if args.dry_run else os.path.join(cand_dir, "cost_log.jsonl")
    ledger_text = lib.read_text(args.ledger)
    baseline_ids = lib.baseline_ids_from_production(args.baseline_run_dir)

    if args.dry_run:
        stored = json.loads(lib.read_text(os.path.join(args.baseline_run_dir, "storyline_b3", "fact_selection_evidence.json")))
        client = lib.StubB3Client(stored, cost_log, synthetic_supplement_id="F01")
    else:
        if args.budget_jpy < lib.EST_B3_CALL_JPY:
            print(f"[STOP] budget {args.budget_jpy} < 1call見込み {lib.EST_B3_CALL_JPY}")
            return 4
        lib.cl.install(cost_log)                      # 全実callをcost_log.jsonlへ(Production loggerをそのまま使用)
        client = lib.vfl01.get_client()

    meta = lib.run_candidate(
        client, candidate=args.candidate, topic=args.theme, ledger_text=ledger_text, cand_dir=cand_dir,
        out_root=out_root, baseline_ids=baseline_ids, budget_jpy=args.budget_jpy, cost_log=cost_log, dry_run=args.dry_run)
    cs = lib.cost_summary(cost_log)
    summary = {"candidate": args.candidate, "sample": args.sample, "dry_run": args.dry_run, "status": meta["status"], "cand_dir": cand_dir,
               "cost": cs, "selected_fact_ids": (meta.get("analysis") or {}).get("selected_fact_ids"),
               "supplement_fact_ids": (meta.get("analysis") or {}).get("supplement_fact_ids"),
               "prompt_user_sha256": [c["user_prompt_sha256"] for c in meta["calls"]]}
    lib.write_json(os.path.join(cand_dir, "run_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
