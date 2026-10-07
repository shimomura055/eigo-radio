# -*- coding: utf-8 -*-
"""STAGE2-01 委任_03 T2: ①v3(OPEN233_STRUCTURAL_REWRITE_RULES=2)のreplay。段階2と同じ7対象×3反復、v3のみ実API(Rewrite→4照合→Recheck)。
Trial専用。段階2の保存値(replay_dev/stage3_rewrite/)は変更しない。出力: v3/runs/t{i}_r{rep}.json、v3/cost_v3.json
使い方: .venv/Scripts/python.exe er052_output/open233_stage2_01/v3/rewrite_v3.py --n 3 --budget-jpy 22"""
import argparse
import json
import os
import pathlib
import sys
import threading
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
os.environ["STAGE2_RULES_ON_LEVEL"] = "2"
import replay_lib as L  # noqa: E402
import replay_stage2 as R  # noqa: E402
import rewrite_stage3 as S3  # noqa: E402

runner, cap2, OUT = L.runner, L.cap2, L.OUT
TAG = os.environ.get("TARGETS_TAG", "v2")
RUNS = HERE / "runs"
COST = HERE / "cost_v3.json"
_lock = threading.Lock()


def total_cost():
    if not COST.exists():
        return 0.0
    return round(sum(e["cost_jpy"] for e in json.loads(COST.read_text(encoding="utf-8"))["entries"]), 4)


def add_cost(name, cost):
    d = json.loads(COST.read_text(encoding="utf-8")) if COST.exists() else {"entries": []}
    d["entries"].append({"name": name, "cost_jpy": round(cost, 4), "t": time.strftime("%Y-%m-%d %H:%M:%S")})
    COST.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--budget-jpy", type=float, default=22.0)
    ap.add_argument("--only", default="", help="例: 0:0,5:1 (i:rep)。空=全件")
    a = ap.parse_args()
    for k, v in (("OPEN233_FIX_W1_TITLE_MARKUP", "1"), ("OPEN233_FIX_W2_STRUCTURAL_RECHECK", "1"), (cap2.SW_SAVE_R3, "1"),
                 (cap2.SW_STRUCT_RULES, "2")):
        os.environ[k] = v
    os.environ.pop(cap2.SW_READER_BELIEF, None)  # ②はOFFのまま(打ち止め)
    client = L.setup(a.budget_jpy)
    targets = S3.collect_targets(TAG, "dev")
    saved = json.loads((OUT / "eval" / "stage3_targets.json").read_text(encoding="utf-8"))
    assert [t["claim"]["claim_text"] for t in targets] == [x["claim"] for x in saved], "対象が段階2と一致しない"
    RUNS.mkdir(exist_ok=True, parents=True)
    only = {tuple(map(int, x.split(":"))) for x in a.only.split(",") if x}
    print("targets", len(targets), "budget", a.budget_jpy, "spent so far", total_cost())
    for rep in range(a.n):
        for i in range(len(targets)):
            if only and (i, rep) not in only:
                continue
            f = RUNS / f"t{i}_r{rep}.json"
            if f.exists():
                continue
            if total_cost() >= a.budget_jpy:
                print("STOP budget", total_cost())
                return
            os.environ[cap2.SW_STRUCT_RULES] = "2"
            out, art, ledger, state, ce, call_log = S3.one(client, targets[i], rep, True, a.budget_jpy)
            cost = out["cost_jpy"]
            if out["guard_ok"] and out["_pair"]:
                st2, ce2, cl2 = L.new_state(), [0], []
                rc = runner.run_recheck_coverage(client, st2, ce2, cl2, f"v3_rc_{i}_{rep}", {"ledger_text": ledger, "article_text": out["_updated_text"]},
                                                 out["_updated_text"], out["_prior"], art,
                                                 structural_pairs=[{"before": out["_pair"]["before"], "after": out["_pair"]["after"]}])
                au = rc.get("recheck_coverage_audit") or {}
                out["recheck"] = {"overall_status": rc.get("overall_status"), "scope_ids": au.get("scope_ids"),
                                  "n_deviations": len(rc.get("deviations") or []),
                                  "deviations": [{"claim": (d.get("claim_in_article") or "")[:120], "issue": (d.get("issue") or "")[:160],
                                                  "severity": d.get("severity")} for d in (rc.get("deviations") or [])][:8],
                                  "all_prior_resolved": rc.get("all_prior_issues_resolved"), "api_failure": bool(rc.get("_recheck_api_failure")),
                                  "cost_jpy": round(st2["cumulative_jpy"], 4)}
                cost += st2["cumulative_jpy"]
            out["updated_text"] = out.pop("_updated_text", None)
            out.pop("_pair", None)
            out.pop("_prior", None)
            out["i"], out["target_claim"] = i, targets[i]["claim"]["claim_text"]
            out["total_cost_jpy"] = round(cost, 4)
            f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            add_cost(f"t{i}_r{rep}", cost)
            sr = out.get("structural_rules") or {}
            print(f"t{i} r{rep} guard_ok={out['guard_ok']} exhausted={out['exhausted']} regen={sr.get('regen_calls')} "
                  f"viol={(out.get('diff_flags') or {}).get('violations')} cost={cost:.2f} total={total_cost():.2f}", flush=True)
    print("done total", total_cost())


if __name__ == "__main__":
    main()
