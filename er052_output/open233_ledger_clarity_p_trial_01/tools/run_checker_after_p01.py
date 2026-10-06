# -*- coding: utf-8 -*-
"""P' After記事を、E2E_02と同一スイッチ(OPEN233_APPROVED_FLOW_SWITCHES既定)のCheckerで1 run判定するDEVラッパ。

新規ファイル。実行しない(委任_01a-2では作成のみ)。E2E_02(e2e_run_02.py)の構成に倣い、
runner.OUT_DIR / BUDGET_STATE_PATH をこのTrial専用dirへ上書きするため、E2Eのstate/出力へ混入しない。
instanceはBefore `meta_run03_advanced` の値(hook_aware/include_related_fact_id/gold_note/group/expected_group_label等)
を踏襲し、ledger_text/article_text/source_article_textのみAfter成果物へ差し替える。有料API=--yes-run-paid時のみ。
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402
import er052_open233_e2e_acceptance_01 as old  # noqa: E402

TRIAL_DIR = "er052_output/open233_ledger_clarity_p_trial_01"
BEFORE_INSTANCE_ID = "meta_run03_advanced"
E2E02_SWITCH_DUMP = "er052_output/open233_prod_e2e_02/approved_switches_dump_worker1.json"


def sha256_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def save(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def build_after_instance(after_dir: str, ledger_path=None, article_path=None, source_path=None) -> dict:
    """E2E_02 prepare_instances()と同形のinstance1件(Before meta_run03_advancedの値を踏襲、3テキストのみAfterへ)。"""
    insts = old.prepare_instances()   # stage1_mode=fresh / stage1_source=None / s1u_eligible=False / substitute=False を適用済み
    inst = copy.deepcopy(insts[BEFORE_INSTANCE_ID])
    ledger_path = ledger_path or f"{after_dir}/research_ledger/verified_fact_ledger.txt"
    article_path = article_path or f"{after_dir}/b1b/article.md"
    source_path = source_path or f"{after_dir}/ja_writer/revision2.md"
    missing = [p for p in (ledger_path, article_path, source_path) if not os.path.exists(p)]
    if missing:
        raise SystemExit(f"After成果物が無い: {missing}")
    fx = inst["fixture"]
    fx["ledger_text"] = read(ledger_path)
    fx["article_text"] = read(article_path)
    fx["source_article_text"] = read(source_path)
    # include_related_fact_id / hook_aware / gold_note はBefore fixtureの値を維持(同一条件)
    fx["baseline_parsed"] = None      # Beforeのbaseline_parsedは別記事の判定結果のため持ち越さない
    fx["id"] = "meta_run03_advanced_after_p01"
    fx["source_path"] = article_path
    fx["source_sha256"] = sha256_file(article_path)
    inst["stage1_mode"] = "fresh"
    inst["stage1_source"] = None
    inst["substitute_baseline_on_stage1_miss"] = False
    inst["s1u_eligible"] = False
    return inst


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--after-dir", default=f"{TRIAL_DIR}/after_pprime_01")
    ap.add_argument("--out-dir", default=f"{TRIAL_DIR}/checker_after_01")
    ap.add_argument("--ledger-path", default=None)
    ap.add_argument("--article-path", default=None)
    ap.add_argument("--source-path", default=None)
    ap.add_argument("--budget-jpy", type=float, default=10.0)
    ap.add_argument("--yes-run-paid", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    base = os.path.normpath(args.out_dir)
    if "open233_prod_e2e" in base.replace("\\", "/") or "open233_e2e_acceptance_01" in base.replace("\\", "/"):
        raise SystemExit("E2E出力dirへは書けない")
    if os.path.exists(f"{base}/runs") or os.path.exists(f"{base}/budget_state_checker_after_p01.json"):
        raise SystemExit(f"既存のChecker出力あり(混同防止でSTOP): {base}")

    applied = runner.apply_open233_approved_flow_switches()      # 既定の承認構成のまま(変更なし)
    runner.assert_open233_approved_flow_switches()
    inst = build_after_instance(args.after_dir, args.ledger_path, args.article_path, args.source_path)

    runner.OUT_DIR = base
    runner.BUDGET_STATE_PATH = f"{base}/budget_state_checker_after_p01.json"
    runner.TOTAL_BUDGET_JPY = args.budget_jpy
    print(f"[checker-after-p01] out={base} budget=JPY{args.budget_jpy} instance={inst['instance_id']} "
          f"ledger_sha={hashlib.sha256(inst['fixture']['ledger_text'].encode()).hexdigest()[:12]}")
    if args.dry_run or not args.yes_run_paid:
        print("[dry-run] 構成assert OK / 有料API呼び出しなし(JPY0)")
        if not args.dry_run:
            raise SystemExit("--yes-run-paid が必要(有料API実行)")
        return 0

    dump_path = f"{base}/approved_switches_dump_after_p01.json"
    save(dump_path, {"switches": applied, "instances": [inst["instance_id"]], "budget_jpy": args.budget_jpy})
    prov = {"switch_dump_sha256": sha256_file(dump_path), "e2e02_switch_dump_worker1_sha256": sha256_file(E2E02_SWITCH_DUMP),
            "switches_equal_e2e02": (json.load(open(E2E02_SWITCH_DUMP, encoding="utf-8")).get("switches") == applied)
            if os.path.exists(E2E02_SWITCH_DUMP) else None,
            "model_id": applied.get("MODEL"), "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "ledger_sha256": hashlib.sha256(inst["fixture"]["ledger_text"].encode()).hexdigest(),
            "article_sha256": hashlib.sha256(inst["fixture"]["article_text"].encode()).hexdigest(),
            "source_article_sha256": hashlib.sha256(inst["fixture"]["source_article_text"].encode()).hexdigest(),
            "args": vars(args)}
    save(f"{base}/checker_after_provenance.json", prov)

    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    state = runner.load_budget_state()
    start = state["cumulative_jpy"]
    result = runner.run_instance(client, state, [0], inst, enable_s1u=False, stage1_cache=None,
                                 instances_subdir="after_instances")
    result["run_cost_jpy"] = round(state["cumulative_jpy"] - start, 4)
    result["provenance"] = prov
    save(f"{base}/runs/{inst['instance_id']}.json", result)
    print(f"[done] final_state={result.get('final_state')} cost=JPY{result['run_cost_jpy']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
