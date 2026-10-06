"""委任_05a: 3 workerの budget_state_worker*.json と runs/ を合算し e2e_summary_02.json を出力(¥0、保存済みjsonのみ読む)。"""
from __future__ import annotations

import argparse
import glob
import json
import os


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-dir", default="er052_output/open233_prod_e2e_02")
    args = ap.parse_args()
    base = args.base_dir
    workers, runs = [], {}
    for p in sorted(glob.glob(f"{base}/budget_state_worker*.json")):
        w = json.load(open(p, encoding="utf-8"))
        workers.append({"worker_id": w.get("worker_id"), "instances": w.get("instances"), "cumulative_jpy": w.get("cumulative_jpy"),
                        "elapsed_seconds": w.get("elapsed_seconds"), "budget_jpy": w.get("budget_jpy"),
                        "finished": "finished_at" in w})
        for iid, r in (w.get("runs") or {}).items():
            runs[iid] = {**r, "worker_id": w.get("worker_id")}
    on_disk = sorted(os.path.basename(p)[:-5] for p in glob.glob(f"{base}/runs/*.json"))
    costs = {i: r.get("cost_jpy") or 0.0 for i, r in runs.items() if r.get("status") in ("done", "aborted", "failed")}
    total = round(sum(costs.values()), 4)
    done = [i for i, r in runs.items() if r.get("status") == "done"]
    summary = {
        "n_workers": len(workers), "workers": workers, "runs": runs, "runs_json_on_disk": on_disk,
        "total_cost_jpy": total, "mean_cost_per_run_jpy": round(total / len(costs), 4) if costs else None,
        "n_done": len(done),
        "failed": [i for i, r in runs.items() if r.get("status") == "failed"],
        "aborted": [i for i, r in runs.items() if r.get("status") == "aborted"],
        "skipped": [i for i, r in runs.items() if str(r.get("status", "")).startswith("skipped")],
        "worker_elapsed_seconds": {str(w["worker_id"]): w["elapsed_seconds"] for w in workers},
        "wall_clock_estimate_seconds": max((w["elapsed_seconds"] or 0 for w in workers), default=None),
        "unfinished_workers": [w["worker_id"] for w in workers if not w["finished"]],
    }
    out = f"{base}/e2e_summary_02.json"
    os.makedirs(base, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("runs", "workers")}, ensure_ascii=False, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
