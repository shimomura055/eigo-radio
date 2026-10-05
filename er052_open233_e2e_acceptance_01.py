# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_e2e_acceptance_01.py
# OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 / E2E-ACCEPTANCE-01 委任_18作成(**未実行**。有料E2E本番は委任_19)。
# fresh Stage 1(coverage_union: r3 medium + r5 high(full) + 否定案a、F3常時、H1 fail-closed)
#   -> Stage 2 -> 必要なRewrite/Recheck(新仕様coverage_union)/Self-Recovery(rep30有効構成) -> Rewrite発生記事は出口3'-R全文1回 -> 最終出口。
# 禁止(ユーザー指示): frozen Stage 1出力・過去判定の手動差替え・gold変更・Safety-critical候補の除外・Checker甘化・一部Trial artifact代替。
#   -> 全runでStage 1はfresh(stage1_cache=None、reuse/frozen/baseline代替なし)。provenanceを各run jsonへ記録し、集計で機械検証する。
# Trial(DEV)専用・Production未配線。到達最大=VALIDATED(`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。
# 使い方: --stage estimate(¥0) / --stage dryrun(¥0、API stub) / --stage main --yes-run-paid(有料、既定予算JPY98) / --stage agg(¥0)
# 再実行・n増しはしない(既存run jsonがあればskip)。1 run費用>JPY6で停止。Waste検知(cycle上限超過/API異常連続/過大call数/同一候補の過剰再Rewrite)で停止・記録。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import time
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov
import er052_open233_stage1_stageA_01 as stagea

OUT_DIR = "er052_output/open233_e2e_acceptance_01"
PER_RUN_COST_STOP_JPY = 6.0
WORST_RUN_RECORD_JPY = 3.0
MAX_CALLS_PER_RUN = 80          # Waste: 1 runのAPI call数の上限(通常は20前後)。超過=異常発火
MAX_CYCLE_LABEL = 5             # Waste: cycle番号上限(HARD_MAX_CYCLES=3 + 判定だけのcycle + 出口再入)
MAX_API_ERRORS_PER_RUN = 3      # Waste: 1 run内のAPI失敗(retry使い切り)がこれを超えたら停止
SAME_CANDIDATE_REWRITE_MAX = 3  # Waste: 同一claim_identityのRewrite試行がこれを超えたら記録・停止
EXPECTED_NET_INCREASE_PER_SET = 5.4   # 事前見込み(cost_feasibility_open233_stage1_01.md §2-4、mid)
SUBTRACTION_PER_SET = {"hormuz_run03": 0.76, "meta_run03": 0.91}  # 差し引き(現行check、6-luna換算、既存Productionログの実tokens、推計)
SUBTRACTION_MEAN = 0.83

SC_IDS = list(stagea.SC_IDS)
PAIR_SETS = {"hormuz_run03": {"advanced": "hormuz_run03_advanced", "standard": "hormuz_run03_standard"},
             "meta_run03": {"advanced": "meta_run03_advanced", "standard": "meta_run03_standard"}}
PAIR_IDS = [i for p in PAIR_SETS.values() for i in (p["advanced"], p["standard"])]
NORMAL_IDS = ["neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b", "neg7_meta_prodrunner_b1b"]
NORMAL_LIKE = set(NORMAL_IDS) | {"hormuz_run03_advanced", "meta_run03_advanced"}  # 期待=NORMAL(不要Rewrite/誤BLOCKING判定の母集団)
ROLE = {**{i: "sc" for i in SC_IDS}, **{i: "pair" for i in PAIR_IDS}, **{i: "normal" for i in NORMAL_IDS}}


def plan() -> list:
    """20 run(sample-major: sample 1に全14 instance、sample 2にSC 6。途中停止でもStandard/Advancedの対が先に揃う)。
    内訳: SC 6 x n=2 (12) + Standard/Advanced対2組 x n=1 (4) + 負例/NORMAL 4 x n=1 (4)。"""
    return [(1, i) for i in SC_IDS + PAIR_IDS + NORMAL_IDS] + [(2, i) for i in SC_IDS]


def set_key(iid: str):
    for k, p in PAIR_SETS.items():
        if iid in p.values():
            return k
    return None


def apply_switches(budget_jpy: float, out_dir: str) -> dict:
    """rep30有効構成(`rep30_switch_values_01.md`突合済み)+Stage 1(coverage_union)+Recheck新仕様を明示設定し、全値を返す(provenance用)。"""
    runner.OUT_DIR = out_dir
    runner.BUDGET_STATE_PATH = f"{out_dir}/budget_state_e2e_acceptance_01.json"
    runner.TOTAL_BUDGET_JPY = budget_jpy
    applied = runner.apply_kpi_trial_switches()
    runner.RECHECK_BEFORE_AFTER_PAIRS = False
    runner.STAGE2_VERDICT_REUSE_NONBLOCKING = True   # rep30はCLI既定onでTrue(モジュール既定はFalseのため明示)
    runner.STAGE2_SIBLING_LOCATIONS_CYCLE1 = True    # 同上
    runner.STAGE1_MODE = runner.STAGE1_MODE_COVERAGE_UNION   # モジュール既定はlegacy_v4aのため明示
    runner.STAGE1_ROUTES = "both"
    runner.STAGE1_R5_MODE = "full"
    runner.STAGE1_R3_REASONING = "medium"
    runner.STAGE1_R5_REASONING = "high"
    runner.STAGE1_NEGATION_MODE = "a"
    runner.F3_PRECHECK_ALWAYS = True
    runner.STAGE1_FAIL_CLOSED = True
    runner.RECHECK_MODE = runner.RECHECK_MODE_COVERAGE_UNION
    assert runner.RECHECK_MERGE_UNRESOLVED is True and runner.ACTOR_GUARD_MODE == "ag1_strict"
    assert runner.STRUCTURAL_PAIRS_TO_RECHECK is True and runner.STRUCTURAL_ELEMENT_REWRITE is True
    assert runner.STAGE2_DOWNGRADE_VERIFY is False and runner.TIER0_G_L_ENABLED is False
    assert runner.CAUSAL_FLOOR is True and runner.CAUSAL_FLOOR_VOCAB == "known6" and runner.STAGE2_SECOND_OPINION is True
    assert runner.STAGE2_NORMAL_TWO_OF_TWO is False and runner.VS_SENTENCE_RESTORE is True
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3 and runner.MODEL == "gpt-6-luna"
    assert runner.JA_MODE == runner.JA_MODE_ENGLISH_ONLY
    for k_ in ("STAGE4_ALLOWLIST", "LADDER_LOCATION_CARRY", "REWRITE_REVERT_GUARD", "SPAN_FALLBACK_CHAIN",
               "JUDGE_ONLY_CYCLE_AFTER_CAP", "LAST_RESORT_DELETE", "MATERIALITY_BLOCKING_PIN",
               "STAGE2_VERDICT_REUSE_NONBLOCKING", "STAGE2_SIBLING_LOCATIONS_CYCLE1"):
        assert getattr(runner, k_) is True, k_
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
    extra = {k: getattr(runner, k) for k in (
        "RECHECK_BEFORE_AFTER_PAIRS", "STAGE2_VERDICT_REUSE_NONBLOCKING", "STAGE2_SIBLING_LOCATIONS_CYCLE1", "STAGE1_MODE",
        "STAGE1_ROUTES", "STAGE1_R5_MODE", "STAGE1_R3_REASONING", "STAGE1_R5_REASONING", "STAGE1_NEGATION_MODE",
        "F3_PRECHECK_ALWAYS", "STAGE1_FAIL_CLOSED", "RECHECK_MODE", "MAX_CYCLES", "HARD_MAX_CYCLES", "MODEL",
        "STAGE4_ALLOWLIST", "LADDER_LOCATION_CARRY", "REWRITE_REVERT_GUARD", "SPAN_FALLBACK_CHAIN",
        "JUDGE_ONLY_CYCLE_AFTER_CAP", "LAST_RESORT_DELETE", "MATERIALITY_BLOCKING_PIN",
        "STAGE2_DOWNGRADE_VERIFY", "TIER0_G_L_ENABLED", "JA_MODE")}
    return {**applied, **extra, "TOTAL_BUDGET_JPY": budget_jpy, "enable_s1u": False}


def provenance(switches: dict) -> dict:
    """各run jsonへ記録する出所。Stage 1はfresh(frozen/reuse/baseline代替なし)であることを宣言し、集計が結果と照合する。"""
    return {"stage1_source": "fresh", "frozen": False, "reuse": False, "substitution": False,
            "stage1_cache": None, "switches": dict(switches), "model": runner.MODEL,
            "efforts": {"r3": runner.STAGE1_R3_REASONING, "r5": runner.STAGE1_R5_REASONING,
                        "other": vfl01.REASONING_EFFORT},
            "prompt_sha256": cov.PROMPT_SHA256, "coverage_module_version": cov.MODULE_VERSION,
            "kind": "E2E(fresh Stage 1 -> 最終出口)。Trial artifactによる代替なし"}


# ---- Waste検知(実行中フック + 事後検査) ----
class RunWaste(RuntimeError):
    """1 runの異常(構造的Waste)。当該runを停止し、waste_flagsを記録してE2E全体をSTOPする(ユーザー指示: Wasteは別問題としてSTOP報告)。"""

    def __init__(self, flag: str):
        super().__init__(flag)
        self.flag = flag


class RunGuard:
    """`runner.RUN_CALL_HOOK`(各API call直前に呼ばれる)。run開始時点の累計を基準に、1 run内の費用・call数・API失敗数・cycle番号を監視する。"""

    def __init__(self, state: dict):
        self.start_jpy = state["cumulative_jpy"]
        self.start_calls = state["cumulative_calls"]
        self.start_errors = state["cumulative_errors"]

    def __call__(self, state: dict) -> None:
        if state["cumulative_jpy"] - self.start_jpy > PER_RUN_COST_STOP_JPY:
            raise RunWaste(f"per_run_cost_gt_{PER_RUN_COST_STOP_JPY}")
        if state["cumulative_calls"] - self.start_calls > MAX_CALLS_PER_RUN:
            raise RunWaste(f"calls_gt_{MAX_CALLS_PER_RUN}")
        if state["cumulative_errors"] - self.start_errors > MAX_API_ERRORS_PER_RUN:
            raise RunWaste(f"api_errors_gt_{MAX_API_ERRORS_PER_RUN}")
        hist = state.get("history") or []
        m = re.search(r"_c(\d+)_", hist[-1]["label"]) if hist else None
        if m and int(m.group(1)) > MAX_CYCLE_LABEL:
            raise RunWaste(f"cycle_gt_{MAX_CYCLE_LABEL}")


def post_run_waste_flags(r: dict) -> list:
    """完走したrunの事後検査(実行中フックで拾えない項目)。"""
    flags = []
    cycles = r.get("cycles") or []
    if len(cycles) > MAX_CYCLE_LABEL:
        flags.append(f"cycles_gt_{MAX_CYCLE_LABEL}")
    n_by_ident: dict = {}
    for c in cycles:
        for rec in c.get("rewrite_records") or []:
            ident = rec.get("claim_identity")
            if ident:
                n_by_ident[ident] = n_by_ident.get(ident, 0) + 1
    if n_by_ident and max(n_by_ident.values()) > SAME_CANDIDATE_REWRITE_MAX:
        flags.append(f"same_candidate_rewrite_gt_{SAME_CANDIDATE_REWRITE_MAX}")
    if len((r.get("recheck_exit_check") or {}).get("log") or []) > 1:
        flags.append("exit_check_repeated")
    if r.get("total_calls", 0) > MAX_CALLS_PER_RUN:
        flags.append(f"calls_gt_{MAX_CALLS_PER_RUN}")
    if r.get("total_cost_jpy", 0) > PER_RUN_COST_STOP_JPY:
        flags.append(f"per_run_cost_gt_{PER_RUN_COST_STOP_JPY}")
    return flags


def provenance_violations(r: dict) -> list:
    """結果側(runner出力)と宣言(provenance)の照合。frozen/reuse/baseline代替/Stage 1 call無しは全てE2E無効。"""
    v = []
    if not r.get("stage1_call_used"):
        v.append("stage1_call_not_used(=frozen/reuse疑い)")
    if r.get("stage1_recall_miss_substituted"):
        v.append("stage1_substituted_by_baseline")
    if (r.get("stage1_coverage") or {}).get("module_version") != cov.MODULE_VERSION:
        v.append("no_stage1_coverage_audit(coverage_union未実行)")
    pv = r.get("provenance") or {}
    if pv.get("stage1_source") != "fresh" or pv.get("frozen") or pv.get("reuse") or pv.get("substitution"):
        v.append("provenance_declaration_invalid")
    sw = pv.get("switches") or {}
    if sw.get("STAGE1_MODE") != "coverage_union" or sw.get("RECHECK_MODE") != "coverage_union":
        v.append("declared_switches_mismatch")
    return v


# ---- 実行(--stage main --yes-run-paid、または--stage dryrunのstub client) ----
def prepare_instances() -> dict:
    """runnerのinstanceを取得し、E2E用に代替・再利用の経路を全て無効化する(fresh Stage 1のみ)。"""
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    for i in insts.values():
        i["stage1_mode"] = "fresh"
        i["stage1_source"] = None
        i["substitute_baseline_on_stage1_miss"] = False   # B3/B2_hormuzのbaseline代替(=substitution)を禁止
        i["s1u_eligible"] = False
    return insts


def _save_aborted(path: str, sample: int, iid: str, flags: list, cost: float, prov: dict, err: str) -> dict:
    rec = {"sample": sample, "instance_id": iid, "role": ROLE.get(iid), "aborted": True, "waste_flags": flags,
           "total_cost_jpy": round(cost, 4), "provenance": prov, "error": err, "final_state": "ABORTED_BY_GUARD"}
    runner.save_json(path, rec)
    return rec


def run_main(budget_jpy: float, out_dir: str, est_total_mid: float | None = None, client=None, plan_rows=None) -> dict:
    applied = apply_switches(budget_jpy, out_dir)
    prov = provenance(applied)
    os.makedirs(out_dir, exist_ok=True)
    client = client or vfl01.get_client()
    state = runner.load_budget_state()
    ce = [0]
    insts = prepare_instances()
    rows = plan_rows or plan()
    log = {"switches": applied, "stopped": False, "stop_reason": None, "runs": [], "exceptions": [], "runs_over_3jpy": [],
           "waste_events": [], "provenance_violations": []}
    n_api_fail_runs = 0
    for sample, iid in rows:
        path = f"{out_dir}/runs/s{sample}/{iid}.json"
        if os.path.exists(path):
            print(f"[skip existing] s{sample}/{iid}")
            continue
        guard = RunGuard(state)
        runner.RUN_CALL_HOOK = guard
        t0 = time.time()
        try:
            r = runner.run_instance(client, state, ce, insts[iid], enable_s1u=False, stage1_cache=None,
                                    instances_subdir=f"runs/s{sample}")
        except RunWaste as e:
            rec = _save_aborted(path, sample, iid, [e.flag], state["cumulative_jpy"] - guard.start_jpy, prov, repr(e))
            log["waste_events"].append({"sample": sample, "instance_id": iid, "flag": e.flag})
            log.update(stopped=True, stop_reason=f"Waste: {e.flag} in s{sample}/{iid}")
            break
        except runner.TrialAbort as e:
            cost = state["cumulative_jpy"] - guard.start_jpy
            if "API error" in str(e):
                _save_aborted(path, sample, iid, ["api_error_consecutive"], cost, prov, repr(e))
                log["waste_events"].append({"sample": sample, "instance_id": iid, "flag": "api_error_consecutive"})
            log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
            break
        except Exception as e:  # noqa: BLE001  例外は記録(再実行しない)。2 instance以上でSTOP
            log["exceptions"].append({"sample": sample, "instance_id": iid, "error": repr(e), "tb": traceback.format_exc()[-1500:]})
            if len({x["instance_id"] for x in log["exceptions"]}) >= 2:
                log.update(stopped=True, stop_reason="exceptions in >=2 instances")
                break
            continue
        finally:
            runner.RUN_CALL_HOOK = None
        flags = post_run_waste_flags(r)
        viol = provenance_violations({**r, "provenance": prov})
        r.update(sample=sample, role=ROLE.get(iid), provenance=prov, waste_flags=flags, provenance_violations=viol,
                 wall_seconds=round(time.time() - t0, 3))
        runner.save_json(path, r)
        cost = r["total_cost_jpy"]
        print(f"[done] s{sample}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} cost=JPY{cost} "
              f"cum=JPY{state['cumulative_jpy']:.3f} waste={flags} viol={viol}", flush=True)
        log["runs"].append({"sample": sample, "instance_id": iid, "final_state": r["final_state"], "stage4_reason": r.get("stage4_reason"),
                            "cost": cost, "waste_flags": flags})
        if cost > WORST_RUN_RECORD_JPY:
            log["runs_over_3jpy"].append({"sample": sample, "instance_id": iid, "cost_jpy": cost})
        if r.get("stage4_reason") == "api_failure":
            n_api_fail_runs += 1
        if viol:
            log["provenance_violations"].append({"sample": sample, "instance_id": iid, "violations": viol})
            log.update(stopped=True, stop_reason=f"provenance violation: {viol}")
            break
        if flags:
            log["waste_events"].extend({"sample": sample, "instance_id": iid, "flag": f} for f in flags)
            log.update(stopped=True, stop_reason=f"Waste: {flags} in s{sample}/{iid}")
            break
        if cost > PER_RUN_COST_STOP_JPY:
            log.update(stopped=True, stop_reason=f"per-run cost>{PER_RUN_COST_STOP_JPY}: {cost}")
            break
        if n_api_fail_runs > 2:
            log.update(stopped=True, stop_reason="API failure in >2 runs")
            break
        done = len(log["runs"])
        if est_total_mid and done >= 6 and state["cumulative_jpy"] > 1.3 * est_total_mid * done / len(rows):
            log.update(stopped=True, stop_reason=f"cumulative cost exceeds estimate+30% at run {done}")
            break
    runner.RUN_CALL_HOOK = None
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    log["worst_run_jpy"] = max((x["cost"] for x in log["runs"]), default=None)
    runner.save_json(f"{out_dir}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:4000])
    return log


# ---- 集計(¥0、保存済みrun jsonのみ読む) ----
STAGE_MAP = {"stage1_initial": "stage1", "stage2_second_judge": "stage2", "floor_verify": "stage2", "downgrade_verify": "stage2",
             "stage3_rewrite": "rewrite", "stage1_recheck": "recheck", "stage1_recheck_confirm": "recheck", "local_qa": "recheck",
             "stage1_exit_check": "exit_3r"}
STAGES = ("stage1", "stage2", "rewrite", "recheck", "exit_3r", "other")


def load_runs(out_dir: str) -> list:
    out = []
    base = f"{out_dir}/runs"
    for s in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        for f in sorted(os.listdir(f"{base}/{s}")):
            with open(f"{base}/{s}/{f}", encoding="utf-8") as fh:
                out.append(json.load(fh))
    return out


def cost_by_stage(r: dict) -> dict:
    d = {k: 0.0 for k in STAGES}
    for c in r.get("call_log") or []:
        d[STAGE_MAP.get(c.get("recovery_stage"), "other")] += c.get("cost_jpy", 0.0) or 0.0
    return {k: round(v, 4) for k, v in d.items()}


def had_rewrite(r: dict) -> bool:
    return any(c.get("rewrite_records") for c in r.get("cycles") or [])


def gold_rows(runs: list) -> list:
    """gold Safety-critical定義ごと・runごとの(Stage 1検出[M/D区分]、E2E出口時点の残存)。
    重大見逃し=最終出口がPASS系(人間確認なし)かつ最終本文に当該gold本文が残存(`residual_at_pass`の`remains_in_final_en_pattern`)。
    Stage 1検出は参考(最終見逃しの原因分析用)。M=モデル判定(sources=model_*)、D=決定論のみ。"""
    rows = []
    for r in runs:
        if r.get("aborted"):
            continue
        iid = r["instance_id"]
        defs = runner._safety_critical_defs(iid)
        cands = (r.get("stage1_coverage") or {}).get("union_candidates") or []
        res = {d["sub_id"]: d for d in (r.get("residual_at_pass") or {}).get("defs", [])}
        for d in defs:
            hit = [c for c in cands if stagea.claim_matches_def(d, c["claim_text"])]
            m = any(stagea.is_model_cand(c) for c in hit)
            rp = res.get(d["sub_id"]) or {}
            passed = r["final_state"] in runner.PASS_FINAL_STATES
            rows.append({"instance_id": iid, "sample": r.get("sample"), "sub_id": d["sub_id"], "stage1_detected_any": bool(hit),
                         "stage1_detected_M": m, "stage1_detected_D_only": bool(hit) and not m, "final_state": r["final_state"],
                         "final_is_pass": passed, "remains_in_final": bool(rp.get("remains_in_final_en_pattern")),
                         "critical_miss_at_exit": bool(passed and rp.get("remains_in_final_en_pattern")),
                         "ever_blocking_flagged": bool(rp.get("ever_blocking_flagged"))})
    return rows


def _mean(xs: list):
    return round(sum(xs) / len(xs), 4) if xs else None


def cost_section(runs: list) -> dict:
    ok = [r for r in runs if not r.get("aborted")]
    per = [{"instance_id": r["instance_id"], "sample": r["sample"], "total": round(r["total_cost_jpy"], 4), "by_stage": cost_by_stage(r),
            "had_rewrite": had_rewrite(r)} for r in ok]
    by_stage_mean = {k: _mean([p["by_stage"][k] for p in per]) for k in STAGES}
    mean_article = _mean([p["total"] for p in per])
    # セット(Standard+Advanced): 対が揃うinstance(sample 1)=実測合算。揃わないinstance=1記事x2(推計)。2列を分離して出す。
    measured = []
    for k, p in PAIR_SETS.items():
        a = next((x for x in per if x["instance_id"] == p["advanced"] and x["sample"] == 1), None)
        s = next((x for x in per if x["instance_id"] == p["standard"] and x["sample"] == 1), None)
        if a and s:
            tot = round(a["total"] + s["total"], 4)
            measured.append({"set": k, "advanced_jpy": a["total"], "standard_jpy": s["total"], "set_total_jpy": tot,
                             "subtraction_jpy": SUBTRACTION_PER_SET[k], "net_increase_jpy": round(tot - SUBTRACTION_PER_SET[k], 4),
                             "rewrite_fired": [a["had_rewrite"], s["had_rewrite"]]})
    est_set = round(mean_article * 2, 4) if mean_article is not None else None
    non_pair = [p["total"] for p in per if set_key(p["instance_id"]) is None]
    no_rw = [p["total"] for p in per if not p["had_rewrite"]]
    rw = [p["total"] for p in per if p["had_rewrite"]]
    net_est = round(est_set - SUBTRACTION_MEAN, 4) if est_set is not None else None
    meas_net = _mean([m["net_increase_jpy"] for m in measured])
    ref = meas_net if meas_net is not None else net_est
    top = sorted(per, key=lambda x: -x["total"])
    return {"total_jpy": round(sum(p["total"] for p in per), 4), "n_runs": len(per), "mean_jpy_per_article": mean_article,
            "mean_by_stage_jpy_per_article": by_stage_mean,
            "per_set": {"measured_pairs": measured, "measured_mean_set_total_jpy": _mean([m["set_total_jpy"] for m in measured]),
                        "measured_mean_net_increase_jpy": meas_net,
                        "estimated_set_jpy(1記事平均x2、全run)": est_set, "estimated_set_non_pair_only_jpy": (
                            round(_mean(non_pair) * 2, 4) if non_pair else None),
                        "estimated_net_increase_jpy(差し引き平均0.83)": net_est,
                        "note": "実測対(sample1のStd+Adv)と推計(1記事x2)は別列。差し引きは既存Productionログのtokens x 6-luna単価換算(推計、shadow V4A省略)。"},
            "vs_expected": {"expected_net_increase_per_set_jpy": EXPECTED_NET_INCREASE_PER_SET, "observed_net_increase_per_set_jpy": ref,
                            "delta_jpy": round(ref - EXPECTED_NET_INCREASE_PER_SET, 4) if ref is not None else None,
                            "large_deviation(>+3 or <-3)": bool(ref is not None and abs(ref - EXPECTED_NET_INCREASE_PER_SET) > 3.0)},
            "normal_vs_upswing": {"mean_no_rewrite_jpy": _mean(no_rw), "n_no_rewrite": len(no_rw), "mean_rewrite_fired_jpy": _mean(rw),
                                  "n_rewrite_fired": len(rw)},
            "worst_run": top[0] if top else None, "runs_over_3jpy": [x for x in top if x["total"] > WORST_RUN_RECORD_JPY],
            "top3": top[:3]}


def aggregate(runs: list) -> dict:
    done = [r for r in runs if not r.get("aborted")]
    aborted = [r for r in runs if r.get("aborted")]
    gold = gold_rows(done)
    misses = [g for g in gold if g["critical_miss_at_exit"]]
    s4 = [{"instance_id": r["instance_id"], "sample": r["sample"], "reason": r.get("stage4_reason")}
          for r in done if r["final_state"] == "STAGE4_ESCALATION"]
    nl = [r for r in done if r["instance_id"] in NORMAL_LIKE]
    nl_rw = [r for r in nl if had_rewrite(r)]
    nl_fb = [r for r in nl if any((c.get("blocking_count") or 0) > 0 for c in r.get("cycles") or [])]
    reached2 = [r for r in done if (r.get("cycles") or [])]
    cyc: dict = {}
    for r in done:
        cyc[len(r.get("cycles") or [])] = cyc.get(len(r.get("cycles") or []), 0) + 1
    cands_c1 = [len((r["cycles"][0].get("stage2_results") or [])) for r in done if r.get("cycles")]
    exit_logs = [e for r in done for e in ((r.get("recheck_exit_check") or {}).get("log") or [])]
    rc = [c.get("recheck_coverage") for r in done for c in r.get("cycles") or [] if c.get("recheck_coverage")]
    viol = [{"instance_id": r["instance_id"], "sample": r["sample"], "violations": r.get("provenance_violations")}
            for r in done if r.get("provenance_violations")]
    waste = [{"instance_id": r["instance_id"], "sample": r.get("sample"), "flags": r.get("waste_flags")}
             for r in runs if r.get("waste_flags")]
    pairs_present = {k: bool(any(r["instance_id"] == p["advanced"] for r in done) and any(r["instance_id"] == p["standard"] for r in done))
                     for k, p in PAIR_SETS.items()}
    kpi = {"safety_critical_miss_at_exit": len(misses), "safety_pass": len(misses) == 0 and bool(gold),
           "human_review_or_stage4_exits": len(s4), "human_review_pass": len(s4) == 0 and bool(done),
           "cost": "合否Gateではない(2026-10-05ユーザー例外承認)。実測は cost 欄", "provenance_all_fresh": not viol and bool(done),
           "no_aborted_runs": not aborted, "no_waste": not waste}
    return {
        "n_runs": len(done), "n_aborted": len(aborted), "n_planned": len(plan()),
        "provenance": {"violations": viol, "all_fresh_stage1": not viol and bool(done),
                       "stage1_call_used_all": all(r.get("stage1_call_used") for r in done),
                       "baseline_substitution_any": any(r.get("stage1_recall_miss_substituted") for r in done)},
        "kpi_summary": kpi,
        "safety": {"gold_rows": gold, "n_gold_checks": len(gold), "critical_miss_at_exit": misses,
                   "stage1_detect_M": f"{sum(g['stage1_detected_M'] for g in gold)}/{len(gold)}",
                   "stage1_detect_D_only": sum(g["stage1_detected_D_only"] for g in gold),
                   "stage1_detect_none": sum(not g["stage1_detected_any"] for g in gold),
                   "note": "重大見逃し=E2E出口時点(PASS系の最終本文)に残存した重大逸脱。Stage 1検出(M/D)は原因分析用の参考値で合否に使わない。"},
        "human_review": {"stage4_exits": s4, "n": len(s4), "api_failure_exits": sum(1 for x in s4 if x["reason"] == "api_failure"),
                         "t_used_runs": sum(1 for r in done if (r.get("stage4_allowlist") or {}).get("t_used")),
                         "note_OF018": "T使用済み時sub_reason欠落(OPEN-233-OF018-SUBREASON-01)は本E2Eで是正しない。t_used_runsで発生機会を観測する。"},
        "rewrite": {"n_rewrite_runs": sum(had_rewrite(r) for r in done), "rate": round(sum(had_rewrite(r) for r in done) / len(done), 4) if done else None,
                    "normal_like_n": len(nl), "normal_like_rewrite_rate(不要Rewrite率)": round(len(nl_rw) / len(nl), 4) if nl else None,
                    "normal_like_false_blocking_rate(誤BLOCKING率)": round(len(nl_fb) / len(nl), 4) if nl else None},
        "stage2": {"runs_reaching_stage2": len(reached2), "rate": round(len(reached2) / len(done), 4) if done else None,
                   "mean_cycle1_candidates_per_article": _mean(cands_c1)},
        "cycles": {"distribution": {str(k): v for k, v in sorted(cyc.items())}, "ge2": sum(v for k, v in cyc.items() if k >= 2),
                   "ge3": sum(v for k, v in cyc.items() if k >= 3)},
        "recheck_new_spec": {"n_recheck_scope_runs": len(rc), "mean_scope_units": _mean([x.get("n_scope") or 0 for x in rc]),
                             "n_exit_checks": len(exit_logs), "exit_check_with_candidates": sum(1 for e in exit_logs if e.get("n_candidates")),
                             "exit_check_api_failure": sum(1 for e in exit_logs if e.get("api_failure"))},
        "cost": cost_section(done),
        "runtime": {"total_elapsed_seconds": round(sum(r.get("elapsed_seconds", 0) for r in done), 1),
                    "mean_elapsed_seconds": _mean([r.get("elapsed_seconds", 0) for r in done]),
                    "max_elapsed_seconds": max((r.get("elapsed_seconds", 0) for r in done), default=None)},
        "waste": {"runs_with_flags": waste, "aborted": [{"instance_id": r["instance_id"], "flags": r["waste_flags"]} for r in aborted]},
        "std_adv_pairs_present": pairs_present,
        "set_unit_note": "Standard+Advanced 1セット=対が揃うinstance(hormuz_run03/meta_run03)は実測合算、他はper_set.estimated(1記事x2、推計)と列分離。"}


# ---- 費用見積(¥0。推計) ----
# Stage 1 = stageA `estimate_cost_v2`(r3 medium + r5 high(full)、段階A/G arm実測のreasoning平均x倍率x帯、未検証の推計)。
# 後段(Stage 2/Rewrite/Recheck/出口3'-R)=cost_feasibility §2-2の新フロー表(Stage 1 1.23を除く): low 1.22 / mid 1.88 / high 2.49 円/記事。
BACKEND_PER_ARTICLE_LOW_MID_HIGH = (1.22, 1.88, 2.49)


def estimate(rows=None) -> dict:
    insts = prepare_instances()
    rows = rows or plan()
    s1 = stagea.estimate_cost_v2(insts, rows, "full", "medium", "high", None)
    n = len(rows)
    tot = [round(s1["total_jpy_low_mid_high"][k] + BACKEND_PER_ARTICLE_LOW_MID_HIGH[k] * n, 2) for k in range(3)]
    per_set = [round((tot[k] / n) * 2, 2) for k in range(3)]
    return {"n_runs": n, "stage1_total_jpy_low_mid_high": s1["total_jpy_low_mid_high"],
            "backend_per_article_low_mid_high": list(BACKEND_PER_ARTICLE_LOW_MID_HIGH),
            "total_jpy_low_mid_high": tot, "per_set_jpy_low_mid_high(1記事平均x2)": per_set,
            "plan": [{"sample": s, "instance_id": i, "role": ROLE[i]} for s, i in rows],
            "assumptions": "推計。Stage 1=stageA estimate_cost_v2(未検証のeffort倍率)、後段=cost_feasibility §2-2(Rewrite率0.53、候補21.8/記事等)。"
                           "E2E実測で置換する。shadow V4Aは省略(差し引きは既存Productionログ換算の推計)。",
            "stage1_rows": s1["rows"]}


# ---- dry-run(¥0): API呼び出しを全てstub。runnerの本物の経路(Stage 1/Recheck新仕様/出口3'-R/出口処理)をfixtureの実記事で通す ----
class _Usage:
    def __init__(self, i, o):
        self.input_tokens, self.output_tokens = i, o
        self.input_tokens_details = None
        self.output_tokens_details = None


class _Resp:
    def __init__(self, payload: dict, in_chars: int):
        self.output_text = json.dumps(payload, ensure_ascii=False)
        self.usage = _Usage(int(in_chars * 0.66), 3000)


class FakeClient:
    """`client.responses.create`の偽物。3'-R/5-lite/r5-Vのschemaにだけ応答する(gold定義の本文を含む単位=CANDIDATE、他=SUPPORTED)。"""

    def __init__(self):
        self.n_calls = 0
        self.gold_subs = [d["text_substring"] for ii in runner.SAFETY_CRITICAL_CLAIM_DEFS
                          for d in runner._safety_critical_defs(ii)]

        outer = self

        class responses:  # noqa: N801
            @staticmethod
            def create(**kw):
                return outer._create(**kw)
        self.responses = responses

    def _create(self, **kw):
        self.n_calls += 1
        name = kw["text"]["format"]["name"]
        prompt = kw["input"][-1]["content"]
        zero = {k: False for k in cov.FLAG_KEYS}
        if name == cov.R3_JSON_SCHEMA["name"]:
            ids = re.search(r"【判定必須の単位ID\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
            lines = {m.group(1): m.group(2) for m in re.finditer(r"\[([^\]]+)\] ([^\n]*)", prompt)}
            ledger = prompt.split("【単位ID付き記事】")[0] if "【単位ID付き記事】" in prompt else prompt
            fid = (re.findall(r"\[VERIFIED\] ([A-Za-z0-9_-]+):", prompt) or ["HF-001"])[0]
            quote = (re.search(r"\[VERIFIED\] " + re.escape(fid) + r": ([^\n]{0,12})", prompt) or re.search(r"(.{6})", "xxxxxx")).group(1)
            items = []
            for i in ids:
                gold = any(s in lines.get(i, "") for s in self.gold_subs)
                items.append({"unit_id": i, "verdict": "CANDIDATE" if gold else "SUPPORTED", "support_fact_ids": [] if gold else [fid],
                              "ledger_quotes": [] if gold else [quote], "issue": "dry-run gold" if gold else "",
                              "claim_in_article": lines.get(i, "") if gold else "", "related_fact_id": fid if gold else "",
                              "flags": dict(zero, changed_fact=True) if gold else dict(zero)})
            return _Resp({"unit_verdicts": items}, len(prompt))
        fids = re.search(r"【factID一覧\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
        return _Resp({"facts": [{"fact_id": f, "matches": []} for f in fids]}, len(prompt))


def _dry_stage2(client, state, ce, call_log, label, fixture, claims):
    out = []
    for c in claims:
        gold = any(d["text_substring"] in (c.get("claim_text") or "")
                   for ii in runner.SAFETY_CRITICAL_CLAIM_DEFS for d in runner._safety_critical_defs(ii))
        mat = "BLOCKING" if gold else "QUALITY"
        out.append({**c, "materiality": mat, "llm_materiality": mat, "basis": "ledger_fact", "rewrite_kind": "narrow_scope",
                    "rewrite_hint": "h", "floor_reason": None, "section_type": "body", "stage2_route": "body",
                    "floor_cited_materiality": mat, "floor_cited_reason": None})
    call_log.append({"label": f"{label}_dry_stage2", "recovery_stage": "stage2_second_judge", "cost_jpy": 0.3})  # 1 batch = 1 entry
    return out


def _dry_stage3(client, state, ce, call_log, label, fixture, en, ja, claim_rec):
    claim = (claim_rec.get("claim_text") or "").strip()
    new = "This point was not confirmed."
    call_log.append({"label": f"{label}_dry_stage3", "recovery_stage": "stage3_rewrite", "cost_jpy": 0.01})
    return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": en.replace(claim, new) if claim else en, "ja_text": ja,
            "method": "dry-run", "guard_ok": True, "before_fragment": claim, "after_fragment": new,
            "ladder_level_used": "1_word_connective", "target_not_locatable": False, "span_unverified": False,
            "ladder_exhausted_without_full_rewrite": False, "handoff": {"level_attempts": [], "text_lang": "EN"}}


def run_dryrun(out_dir: str) -> dict:
    """全20 runを偽client/偽Stage 2・3(判定規則はテスト用の単純規則)で最終出口まで通し、provenance・集計欄が埋まることを確認する。API 0 call、¥0。"""
    from unittest import mock
    patches = [mock.patch.object(runner, "run_stage2", _dry_stage2),
               mock.patch.object(runner, "apply_stage2_two_of_two", lambda *a, **k: (a[6], [])),
               mock.patch.object(runner, "run_stage3_for_claim", _dry_stage3),
               mock.patch.object(runner, "run_local_qa_fastpath", lambda *a, **k: {"success": False, "results": []}),
               mock.patch.object(runner, "time", mock.Mock(wraps=time, sleep=lambda *_: None))]
    for p in patches:
        p.start()
    try:
        fake = FakeClient()
        log = run_main(1000.0, out_dir, client=fake)
    finally:
        for p in reversed(patches):
            p.stop()
    agg = aggregate(load_runs(out_dir))
    checks = {"all_20_runs_completed": agg["n_runs"] == len(plan()) and agg["n_aborted"] == 0,
              "provenance_all_fresh": agg["provenance"]["all_fresh_stage1"],
              "no_baseline_substitution": not agg["provenance"]["baseline_substitution_any"],
              "std_adv_pairs_present": all(agg["std_adv_pairs_present"].values()),
              "measured_pairs_n": len(agg["cost"]["per_set"]["measured_pairs"]),
              "aggregate_fields_filled": all(agg[k] is not None for k in ("safety", "human_review", "rewrite", "stage2", "cycles", "cost", "runtime")),
              "exit_checks_ran": agg["recheck_new_spec"]["n_exit_checks"], "recheck_scope_runs": agg["recheck_new_spec"]["n_recheck_scope_runs"],
              "fake_api_calls": fake.n_calls, "run_log_stopped": log["stopped"], "stop_reason": log["stop_reason"]}
    with open(f"{out_dir}/dryrun_report.json", "w", encoding="utf-8") as f:
        json.dump({"checks": checks, "aggregate": agg}, f, ensure_ascii=False, indent=2)
    print(json.dumps(checks, ensure_ascii=True, indent=2))
    return {"checks": checks, "aggregate": agg}


def run_agg(out_dir: str) -> dict:
    res = aggregate(load_runs(out_dir))
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/e2e_aggregate.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(json.dumps(res["kpi_summary"], ensure_ascii=True, indent=2))
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["estimate", "dryrun", "main", "agg"], default="estimate")
    ap.add_argument("--budget-jpy", type=float, default=98.0, help="累計Guardrail(現管理ID残予算約JPY98.29)。E2E見込みは約JPY62")
    ap.add_argument("--yes-run-paid", action="store_true", help="有料API実行の明示確認(mainで必須)")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--estimate-out", default=None)
    args = ap.parse_args()
    if args.stage == "agg":
        run_agg(args.out_dir)
        return
    if args.stage == "dryrun":
        run_dryrun(args.out_dir)
        return
    est = estimate()
    print(json.dumps({k: est[k] for k in ("n_runs", "total_jpy_low_mid_high", "per_set_jpy_low_mid_high(1記事平均x2)")},
                     ensure_ascii=True), flush=True)
    if args.stage == "estimate":
        out = args.estimate_out or f"{args.out_dir}/estimate.json"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(est, f, ensure_ascii=False, indent=2)
        return
    if not args.yes_run_paid:
        raise SystemExit("--stage main は有料です。--yes-run-paid を付けて明示確認してください(未実行)。")
    run_main(args.budget_jpy, args.out_dir, est_total_mid=est["total_jpy_low_mid_high"][1])


if __name__ == "__main__":
    main()
