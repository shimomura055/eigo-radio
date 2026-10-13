# ============================================================
# er064_kp_int_01_run.py をRound2用に再利用するrunner(Trial専用・Production非接続)。出力先・予算・組合せをpatchするだけ。
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_int_02_run.py --stage prep|1|2
#  Stage1 = Coffee M2P5 n=3(Std/Adv) + meta/hormuz M2P5 n=2(Std/Adv)  /  Stage2 = Coffee M2P5 run4-5(n=3->5)
# retry/監督ループ/timeoutラッパなし。各Stageは1回だけ起動。外部停止後の再起動禁止。
# ============================================================
from __future__ import annotations
import argparse, concurrent.futures as cf, glob, json, os, sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_run as RUN  # noqa: E402
import er064_kp_int_01_prompts as PR  # noqa: E402

OUT = "er064_output/kp_integrated_opt_01/round2"
R1 = "er064_output/kp_integrated_opt_01/round1"
HARD_STOP_R2 = 70.0   # Round2 ハードストップ(Round2累計)
BUDGET_R2 = 65.0
TRIAL_CAP_PRIOR = 80.7198  # Round1実績
TRIAL_SPENT_CAP = 150.72   # 本Trial累計上限(委任文)
RUN.OUT = OUT
RUN.COST_PATH = f"{OUT}/cost_r2.json"
RUN.HARD_STOP = HARD_STOP_R2
RUN.COMBOS["M2P5"] = ("M2", "P5")


def stop_present():
    return (glob.glob(f"{OUT}/STOP") + glob.glob("er026_output/family_z_production_e2e_01/STOP_ALL")
            + glob.glob("docs/pm/delegation_log/*STOP_NOTICE*KP-INTEGRATED*"))
RUN.stop_present = stop_present


def stage_specs(stage):
    if stage == 1:
        s = [("coffee", lv, "M2P5", k) for lv in RUN.LEVELS for k in (1, 2, 3)]
        s += [(a, lv, "M2P5", k) for a in ("meta", "hormuz") for lv in RUN.LEVELS for k in (1, 2)]
    else:
        s = [("coffee", lv, "M2P5", k) for lv in RUN.LEVELS for k in (4, 5)]
    return s


def ctx_for(specs):
    ctx = {}
    for a in sorted({s[0] for s in specs}):
        ctx.update(RUN.build_ctx(a, ["M2P5"]))
    return ctx


def guard(label):
    p = f"{OUT}/state_guard_r2.json"
    g = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    g[label] = RUN.state_hashes()
    if "before" in g and label != "before":
        g[f"unchanged_{label}"] = g[label] == g["before"]
    json.dump(g, open(p, "w", encoding="utf-8"), indent=1)


def run(stage, prep_only):
    os.makedirs(OUT, exist_ok=True)
    stops = stop_present()
    if stops:
        sys.exit(f"STOP present {stops}")
    specs = stage_specs(stage)
    ctx = ctx_for(specs)
    est = RUN.est_cost(specs)
    sp = RUN.spent()
    if not os.path.exists(f"{OUT}/state_guard_r2.json"):
        guard("before")
    info = {"stage": stage, "n_jobs": len(specs), "est_cost_jpy": est, "spent_round2_jpy": sp,
            "trial_cumulative_if_est": round(TRIAL_CAP_PRIOR + sp + est, 2),
            "prompts": {f"{a}_{lv}_{cn}": {"msg_sha256": c["prompt_sha256"], "rows_sha256": c["rows_sha256"], "n_candidates": c["n_candidates"]} for (a, lv, cn), c in ctx.items()},
            "jobs": [list(s) for s in specs], "stop_files_present": stops}
    assert sp + est <= HARD_STOP_R2 and TRIAL_CAP_PRIOR + sp + est <= TRIAL_SPENT_CAP, f"budget guard {sp}+{est}"
    json.dump(info, open(f"{OUT}/prep_stage{stage}_r2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: info[k] for k in ("n_jobs", "est_cost_jpy", "spent_round2_jpy", "trial_cumulative_if_est")}), flush=True)
    if prep_only:
        return
    res, err = [], []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(RUN.job, s, ctx): s for s in specs}
        for f in cf.as_completed(futs):
            try:
                res.append(f.result())
            except Exception as e:
                err.append({"job": list(futs[f]), "error": f"{type(e).__name__}: {e}"})
    res.sort(key=lambda r: (r["article"], r["level"], r["combo"], r["run"]))
    json.dump({"stage": stage, "runs": res, "errors": err, "cumulative_round2_jpy": RUN.spent()},
              open(f"{OUT}/stage{stage}_summary_r2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for r in res:
        print(r["tag"], r["selection_status"], r.get("canonicalization_status"), r.get("redundancy_status"),
              [i["display_phrase"] for i in r.get("selected_items", [])], r["cost_jpy"], r["elapsed_sec"])
    print("errors", err, "cum_round2", RUN.spent())
    guard(f"after_stage{stage}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["prep1", "prep2", "1", "2"])
    a = ap.parse_args()
    run(int(a.stage[-1]), a.stage.startswith("prep"))
