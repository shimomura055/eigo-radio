"""OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_05a: 新仕様E2E実行script_02(3プロセス並列対応、1 workerぶん)。

旧`er052_open233_e2e_acceptance_01.py`は変更せず、その純粋helper(prepare_instances/provenance/post_run_waste_flags/
provenance_violations/plan定数)だけを再利用する。旧との違い:
- 承認構成は`runner.apply_open233_approved_flow_switches()`で適用(旧apply_switches=KPI_TRIAL構成は使わない)。
- 停止条件は(i)技術障害(2回再試行後failed記録→次へ) (ii)1 run費用>run-cap(abort記録→次へ) (iii)プロセス累計>budget(残skipped→終了)のみ。
  Human Review/STAGE4/waste flag/provenance違反/品質問題では止めない(記録のみ)。
- 既存run json skipは--resume指定時のみ。旧出力dirには一切書かない。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402
import er052_open233_e2e_acceptance_01 as old  # noqa: E402  (helper再利用のみ。旧出力dirへは書かない)

OLD_OUT_DIR_MARK = "open233_e2e_acceptance_01"
# 1箇所の定数表: runner側に必要な名前と、E2E開始前にassertする主要スイッチの期待値(実名が違えば明示エラー)
RUNNER_INTERFACE = ("OPEN233_APPROVED_FLOW_SWITCHES", "apply_open233_approved_flow_switches")
REQUIRED_SWITCHES = {"FLOOR_MODE": "number_only", "FLOOR_VERIFY_MODE": "off", "CAUSAL_FLOOR": False,
                     "STAGE2_DOWNGRADE_VERIFY": False, "TIER0_G_L_ENABLED": False,
                     "STAGE1_RECLASSIFY": True, "PRECHECK_MODE": "number_only"}
FIRST9 = old.PAIR_IDS + old.NORMAL_IDS + old.SC_IDS[:1]   # 計画doc §4: 対4+負例4+bgroup_B3
# 旧実績wall秒(neg1 644/meta_std 409/hormuz_std 193 ほか)で均等化: 1246 / 1180 / 1085秒
FIRST9_SPLIT = {1: ["neg1_meta_b3prod_a2", "meta_run03_standard", "hormuz_run03_standard"],
                2: ["neg7_meta_prodrunner_b1b", "meta_run03_advanced", "hormuz_run03_advanced"],
                3: ["bgroup_B3", "neg3_hormuz_prodrunner_b1b", "neg2_meta_refresh_a2"]}
MAX_RETRY = 2


class InterfaceMissing(RuntimeError):
    pass


class RunCapExceeded(RuntimeError):
    pass


def check_interface() -> dict:
    """runner側インターフェース存在確認+承認構成の適用+assert。不一致は明示エラー(旧挙動で黙って走らない)。"""
    miss = [n for n in RUNNER_INTERFACE if not hasattr(runner, n)]
    if miss:
        raise InterfaceMissing(f"インターフェース未検出: runnerに{miss}が無い(委任_04未完了/名前不一致)")
    applied = runner.apply_open233_approved_flow_switches()
    if not isinstance(applied, dict):
        raise InterfaceMissing("apply_open233_approved_flow_switches()がdictを返さない")
    old.STAGE_MAP.setdefault("stage1_reclassify", "stage1")   # 費用のChecker(stage1)関連へ分類(旧moduleファイルは不変、in-processのみ)
    runner.assert_open233_approved_flow_switches()   # 適用後の全承認キーをassert(不一致はAssertionError)
    bad = {k: (applied.get(k, "<absent>"), v) for k, v in REQUIRED_SWITCHES.items() if applied.get(k, "<absent>") != v}
    if bad:
        raise InterfaceMissing(f"主要スイッチ不一致(actual, expected): {bad}")
    return applied


def resolve_instances(args) -> list:
    if args.instances:
        ids = [x.strip() for x in args.instances.split(",") if x.strip()]
    elif args.phase == "first9":
        ids = list(FIRST9_SPLIT[args.worker_id])
    else:
        raise SystemExit("--instances か --phase first9 --worker-id 1/2/3 を指定すること")
    unknown = [i for i in ids if i not in old.ROLE]
    if unknown:
        raise SystemExit(f"未知のinstance: {unknown}")
    return ids


class RunCapHook:
    """runner.RUN_CALL_HOOK。当該instance開始からの費用が上限超ならabort(call数・cycle数では止めない)。"""

    def __init__(self, start_jpy: float, cap: float):
        self.start_jpy, self.cap = start_jpy, cap

    def __call__(self, state: dict) -> None:
        if state["cumulative_jpy"] - self.start_jpy > self.cap:
            raise RunCapExceeded(f"run_cost_gt_{self.cap}")


def save(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def run_one(client, state, insts, iid, args, prov, runs_dir, bs, base) -> str:
    """1 instanceを実行(技術障害は最大MAX_RETRY回再試行)。戻り値=done/aborted/failed。"""
    path = f"{runs_dir}/{iid}.json"
    start_jpy = state["cumulative_jpy"]
    h0 = len(state.get("history") or [])
    t0 = time.time()
    errors = []
    for attempt in range(1 + MAX_RETRY):
        runner.RUN_CALL_HOOK = RunCapHook(start_jpy, args.run_cap_jpy)
        try:
            r = runner.run_instance(client, state, [0], insts[iid], enable_s1u=False, stage1_cache=None,
                                    instances_subdir=f"worker{args.worker_id}_instances")
        except RunCapExceeded as e:
            cost = state["cumulative_jpy"] - start_jpy
            save(path, {"instance_id": iid, "role": old.ROLE.get(iid), "aborted": True, "abort_reason": str(e),
                        "total_cost_jpy": round(cost, 4), "provenance": prov, "final_state": "ABORTED_BY_RUN_CAP",
                        "partial_call_history": list((state.get("history") or [])[h0:])})
            bs["runs"][iid] = {"status": "aborted", "reason": str(e), "cost_jpy": round(cost, 4),
                               "seconds": round(time.time() - t0, 1)}
            return "aborted"
        except Exception as e:  # noqa: BLE001  API障害/TrialAbort(連続エラー)/例外=技術障害として再試行
            if state["cumulative_jpy"] >= runner.TOTAL_BUDGET_JPY:   # プロセスCap backstop到達
                errors.append({"attempt": attempt, "error": repr(e), "kind": "process_cap_backstop"})
                break
            errors.append({"attempt": attempt, "error": repr(e), "tb": traceback.format_exc()[-1200:]})
            print(f"[retry {attempt + 1}/{MAX_RETRY}] {iid}: {e!r}", flush=True)
            continue
        finally:
            runner.RUN_CALL_HOOK = None
        cost = state["cumulative_jpy"] - start_jpy
        flags = old.post_run_waste_flags(r)
        viol = old.provenance_violations({**r, "provenance": prov})
        r.update(role=old.ROLE.get(iid), provenance=prov, waste_flags=flags, provenance_violations=viol,
                 wall_seconds=round(time.time() - t0, 3), worker_id=args.worker_id, attempts=attempt + 1,
                 run_cost_incl_retries_jpy=round(cost, 4))
        save(path, r)
        bs["runs"][iid] = {"status": "done", "final_state": r.get("final_state"), "stage4_reason": r.get("stage4_reason"),
                           "cost_jpy": round(cost, 4), "seconds": round(time.time() - t0, 1), "attempts": attempt + 1,
                           "waste_flags": flags, "provenance_violations": viol}
        print(f"[done] {iid} final={r.get('final_state')} cost=JPY{cost:.3f} flags={flags} viol={viol}", flush=True)
        return "done"
    cost = state["cumulative_jpy"] - start_jpy
    save(f"{base}/failed_worker{args.worker_id}_{iid}.json", {"instance_id": iid, "errors": errors, "cost_jpy": round(cost, 4)})
    bs["runs"][iid] = {"status": "failed", "errors": [e["error"] for e in errors], "cost_jpy": round(cost, 4),
                       "seconds": round(time.time() - t0, 1)}
    return "failed"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="er052_output/open233_prod_e2e_02/runs")
    ap.add_argument("--instances", default=None)
    ap.add_argument("--worker-id", type=int, default=1)
    ap.add_argument("--phase", choices=["first9"], default=None)
    ap.add_argument("--budget-jpy", type=float, default=20.0, help="プロセス別Cap")
    ap.add_argument("--run-cap-jpy", type=float, default=20.0)
    ap.add_argument("--yes-run-paid", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true", help="既存run jsonをskip(既定off)")
    args = ap.parse_args()
    runs_dir = os.path.normpath(args.out_dir)
    base = os.path.dirname(runs_dir)
    if OLD_OUT_DIR_MARK in runs_dir.replace("\\", "/"):
        raise SystemExit("旧E2E出力dirには書けない")
    ids = resolve_instances(args)
    try:
        applied = check_interface()
    except InterfaceMissing as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    # worker別にrunner出力先・budget stateを分離(後でmergeで合算)。プロセスCap超過のbackstopとして+run capぶんの余裕を持たせる
    runner.OUT_DIR = base
    runner.BUDGET_STATE_PATH = f"{base}/budget_state_runner_worker{args.worker_id}.json"
    runner.TOTAL_BUDGET_JPY = args.budget_jpy + args.run_cap_jpy
    prov = old.provenance(applied)
    print(f"worker{args.worker_id} instances={ids} budget=JPY{args.budget_jpy} run_cap=JPY{args.run_cap_jpy} resume={args.resume}")
    print("approved switches:", json.dumps({k: applied[k] for k in REQUIRED_SWITCHES}, ensure_ascii=False))
    insts = old.prepare_instances()
    missing = [i for i in ids if i not in insts]
    if missing:
        print(f"ERROR: runnerのinstance定義に無い: {missing}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"[dry-run] 構成assert OK / runs_dir={runs_dir} / budget_state={runner.BUDGET_STATE_PATH}")
        print(f"[dry-run] run一覧: {ids}")
        print(f"[dry-run] 予算配分: process cap JPY{args.budget_jpy}(backstop JPY{runner.TOTAL_BUDGET_JPY}), run cap JPY{args.run_cap_jpy}")
        return 0
    if not args.yes_run_paid:
        raise SystemExit("--yes-run-paid が必要(有料API実行)")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()
    state = runner.load_budget_state()
    save(f"{base}/approved_switches_dump_worker{args.worker_id}.json", {"switches": applied, "instances": ids,
         "budget_jpy": args.budget_jpy, "run_cap_jpy": args.run_cap_jpy})
    bs = {"worker_id": args.worker_id, "instances": ids, "budget_jpy": args.budget_jpy, "runs": {}, "started_at": time.time()}
    bs_path = f"{base}/budget_state_worker{args.worker_id}.json"
    for n, iid in enumerate(ids):
        if args.resume and os.path.exists(f"{runs_dir}/{iid}.json"):
            print(f"[skip existing] {iid}")
            bs["runs"][iid] = {"status": "skipped_existing", "cost_jpy": 0.0}
        else:
            run_one(client, state, insts, iid, args, prov, runs_dir, bs, base)
        bs["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
        bs["elapsed_seconds"] = round(time.time() - bs["started_at"], 1)
        save(bs_path, bs)
        if state["cumulative_jpy"] > args.budget_jpy:
            for rest in ids[n + 1:]:
                bs["runs"][rest] = {"status": "skipped", "reason": f"process_cap_exceeded(JPY{state['cumulative_jpy']:.2f}>{args.budget_jpy})",
                                    "cost_jpy": 0.0}
            break
    bs["finished_at"] = time.time()
    bs["elapsed_seconds"] = round(bs["finished_at"] - bs["started_at"], 1)
    save(bs_path, bs)
    print(json.dumps({k: v for k, v in bs.items() if k != "runs"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
