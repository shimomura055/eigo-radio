# -*- coding: utf-8 -*-
"""V3(M3): 保存済みStage 1候補(合流前の経路別候補)から、再分類(OPEN233_RECLASSIFY_PROTECT_FLAGS=changed_actor 有効)→Stage 2 を
Productionの run_instance(承認構成)でそのまま再生する。Stage 1(r3/r5)のLLM呼び出しは行わない(保存済み候補を注入)。
cycle 1 の Stage 2(+第2意見)の結果が確定した時点で打ち切る(Rewrite/Recheck以降は実行しない=誤書き換えは「BLOCKING判定=書き換え対象になる」で数える)。
実行: v3_reclassify_replay.py --proc P1 --runs A,B,C --budget-jpy 12 [--yes-run-paid]
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

sys.path.insert(0, os.path.join(C.ROOT, "er052_output/open233_ledger_clarity_p_trial_01/tools"))
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402
import er052_open233_stage1_coverage_checker_01 as cov  # noqa: E402
import run_checker_after_p01 as rc  # noqa: E402

E = "er052_output/"
TARGETS = {
    "T01_meta_b3_baseline_r1": E + "all6_writer_redesign_necessity_01/runs/meta/control/b3__baseline__r1",
    "T02_space_b2_baseline_r2": E + "all6_writer_redesign_necessity_01/runs/space_weapons/control/b2__baseline__r2",
    "T03_ai_control_p2_rep1": E + "open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep1",
    "T04_ai_control_p2_rep2": E + "open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2",
    "T05_meta_p2_rep1": E + "open233_allfact_note_e2e_02/runs/meta/nb/p2/rep1",
    "T06_meta_p2_rep2": E + "open233_allfact_note_e2e_02/runs/meta/nb/p2/rep2",
    "T07_poly_ai_control_rep1": E + "open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1",
    "T08_poly_meta_rep2": E + "open233_control_checker_polysemy_trial_01/runs/meta/nb/rep2",
    "T09_poly_meta_rep3": E + "open233_control_checker_polysemy_trial_01/runs/meta/nb/rep3",
    "T10_poly_meta_rep6": E + "open233_control_checker_polysemy_trial_01/runs/meta/nb/rep6",
}
V3 = f"{C.TRIAL}/v3"


class StopReplay(Exception):
    pass


_captured = {}
_orig_wobble = runner._wobble_observe


def _wobble_stop(registry, records, cycle, stage2_results, en_text):
    _captured[threading.get_ident()] = {"cycle": cycle, "stage2_results": copy.deepcopy(stage2_results)}
    raise StopReplay()


class FixedCache(dict):
    """run_instance の stage1_cache として、任意キーに対し注入済みStage 1結果を返す(Stage 1のLLMを呼ばせない)。"""

    def __init__(self, parsed):
        super().__init__()
        self._parsed = parsed

    def __contains__(self, k):
        return True

    def __getitem__(self, k):
        return self._parsed

    def __setitem__(self, k, v):
        pass


def replay_one(client, name, run_dir, state, ce, pf_env):
    dump = json.load(open(f"{run_dir}/checker/runs/meta_run03_advanced.json", encoding="utf-8"))
    a = dump["provenance"]["args"]
    inst = rc.build_after_instance("", a["ledger_path"], a["article_path"], a["source_path"])
    fixture = inst["fixture"]
    import hashlib
    assert hashlib.sha256(fixture["article_text"].encode()).hexdigest() == dump["provenance"]["article_sha256"], "article sha mismatch"
    pr = dump["stage1_coverage"]["per_route"]
    pre_union = [copy.deepcopy(c) for k in ("r3", "r5") for c in pr[k]["candidates"]]
    call_log: list = []
    start = state["cumulative_jpy"]
    os.environ["OPEN233_RECLASSIFY_PROTECT_FLAGS"] = pf_env
    filt = runner.make_reclassify_filter(client, state, ce, call_log, f"{name}_stage1", fixture)
    kept, info = cov.apply_candidate_filter(filt, pre_union)
    merged = cov.union_candidates(kept)
    parsed = cov.to_stage1_parsed({"candidates": merged, "api_failure": False,
                                   "audit": {"candidate_filter": info, "union_candidates": merged}})
    parsed["stage1_reclassify"] = runner.reclassify_summary(info)
    reclass_cost = state["cumulative_jpy"] - start
    # 保護された候補(model候補で changed_actor=true のもの)
    prot_keys = [k for k in {reclf_key(c) for c in pre_union if reclf_is_model(c) and (c.get("flags") or {}).get("changed_actor")}]
    res = {"name": name, "run_dir": run_dir, "reclassify_info": {k: v for k, v in info.items() if k != "calls"},
           "n_pre_union": len(pre_union), "n_union_after": len(merged), "protected_keys": prot_keys,
           "reclassify_cost_jpy": round(reclass_cost, 4)}
    captured_err = None
    try:
        runner.run_instance(client, state, ce, inst, enable_s1u=False, stage1_cache=FixedCache(parsed),
                            instances_subdir="after_instances")
    except StopReplay:
        pass
    except Exception as e:  # noqa: BLE001
        captured_err = f"{type(e).__name__}: {e}"
    cap = _captured.pop(threading.get_ident(), None)
    res["error"] = captured_err
    res["total_cost_jpy"] = round(state["cumulative_jpy"] - start, 4)
    res["stage2_cost_jpy"] = round(res["total_cost_jpy"] - res["reclassify_cost_jpy"], 4)
    if cap:
        res["cycle"] = cap["cycle"]
        res["stage2_results"] = [{
            "claim_text": r.get("claim_text"), "materiality": r.get("materiality"), "llm_materiality": r.get("llm_materiality"),
            "basis": r.get("basis"), "floor_reason": r.get("floor_reason"), "related_fact_id": (r.get("dev") or {}).get("related_fact_id"),
            "dev_flags": [k for k in cov.FLAG_KEYS if (r.get("dev") or {}).get(k)], "detected_by": r.get("detected_by"),
            "second_opinion": r.get("second_opinion"), "rewrite_kind": r.get("rewrite_kind"), "rewrite_hint": r.get("rewrite_hint"),
            "stage1_issue": (r.get("dev") or {}).get("issue")} for r in cap["stage2_results"]]
    return res


def reclf_key(c):
    import er052_open233_stage1_reclassify_01 as reclf
    return reclf.ckey(c)


def reclf_is_model(c):
    import er052_open233_stage1_reclassify_01 as reclf
    return reclf.is_model(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proc", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--budget-jpy", type=float, default=12.0)
    ap.add_argument("--protect", default="changed_actor")
    ap.add_argument("--tag", default="")
    ap.add_argument("--yes-run-paid", action="store_true")
    args = ap.parse_args()
    applied = runner.apply_open233_approved_flow_switches()
    runner.assert_open233_approved_flow_switches()
    runner.OUT_DIR = f"{V3}/out_{args.proc}"
    runner.BUDGET_STATE_PATH = f"{V3}/state_{args.proc}.json"
    runner.TOTAL_BUDGET_JPY = args.budget_jpy
    runner._wobble_observe = _wobble_stop
    C.jdump(f"{V3}/switches_{args.proc}.json", {"switches": applied, "OPEN233_RECLASSIFY_PROTECT_FLAGS": args.protect,
                                                "note": "承認構成そのまま(値は変更せず)。Trialスイッチは環境変数のみ"})
    if not args.yes_run_paid:
        print("dry-run OK", args.runs)
        return
    client = C.vfl01.get_client()
    state = runner.load_budget_state()
    ce = [0]
    for name in args.runs.split(","):
        out = f"{V3}/{name}{args.tag}.json"
        if os.path.exists(out):
            print("skip", name)
            continue
        t0 = time.time()
        r = replay_one(client, name, TARGETS[name], state, ce, args.protect)
        r["elapsed_seconds"] = round(time.time() - t0, 1)
        C.jdump(out, r)
        C.record_spend(f"v3.{name}", "gpt-6-luna", {}, cost_jpy=r["total_cost_jpy"])
        print(name, "cost", r["total_cost_jpy"], "err", r["error"], "n_stage2", len(r.get("stage2_results") or []), flush=True)


if __name__ == "__main__":
    main()
