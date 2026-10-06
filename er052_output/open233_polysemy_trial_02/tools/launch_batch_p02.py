# -*- coding: utf-8 -*-
"""P0c バッチ起動補助(DEV)。テーマ x 条件 x repeat をN並列で起動し runs/batch_log.jsonl に集約。
使い方: python launch_batch_p02.py --phase phase1 --jobs "meta=<topic>|<ledger.txt>" --jobs "hormuz=..." \
        --variants control nb --repeats 3 --parallel 3 [--yes-run-paid]
--yes-run-paid 無しは各runを --dry-run で起動(¥0)。
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUNS = "er052_output/open233_polysemy_trial_02/runs"
DEV = "er052_open233_polysemy_nb_dev_01.py"


def one(job):
    slug, topic, ledger, variant, rep, phase, paid = job
    out = f"{RUNS}/{slug}/{variant}/rep{rep}"
    cmd = [sys.executable, DEV, "--theme", topic, "--slug", slug, "--ledger-txt", ledger,
           "--out-dir", out, "--phase", phase]
    cmd.append("--yes-run-paid" if paid else "--dry-run")
    env = dict(os.environ, OPEN233_B3_VARIANT=variant)
    t0 = time.time()
    p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    cost = None
    cj = os.path.join(ROOT, out, "cost.json")
    if os.path.exists(cj):
        with open(cj, encoding="utf-8") as f:
            cost = json.load(f).get("total_jpy")
    return {"slug": slug, "variant": variant, "rep": rep, "phase": phase, "out_dir": out,
            "exit_code": p.returncode, "cost_jpy": cost, "seconds": round(time.time() - t0, 1),
            "stderr_tail": (p.stderr or "")[-300:], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("phase1", "phase2"), default="phase1")
    ap.add_argument("--jobs", action="append", required=True, help="slug=topic|ledger_txt_path")
    ap.add_argument("--variants", nargs="+", default=["control", "nb"])
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--yes-run-paid", action="store_true")
    a = ap.parse_args()
    jobs = []
    for j in a.jobs:
        slug, rest = j.split("=", 1)
        topic, ledger = rest.split("|", 1)
        for v in a.variants:
            for r in range(1, a.repeats + 1):
                jobs.append((slug, topic, ledger, v, r, a.phase, a.yes_run_paid))
    os.makedirs(os.path.join(ROOT, RUNS), exist_ok=True)
    log = os.path.join(ROOT, RUNS, "batch_log.jsonl")
    with cf.ThreadPoolExecutor(max_workers=a.parallel) as ex, open(log, "a", encoding="utf-8") as lf:
        for res in ex.map(one, jobs):
            lf.write(json.dumps(res, ensure_ascii=False) + "\n")
            lf.flush()
            print(res["slug"], res["variant"], res["rep"], "exit", res["exit_code"], "cost", res["cost_jpy"])


if __name__ == "__main__":
    main()
