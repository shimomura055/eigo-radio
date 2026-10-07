# -*- coding: utf-8 -*-
"""ALL-6-LUNA T-A driver(Trial専用)。driver_stage2.pyと同方式: 単層ThreadPool(既定4並列)+メモリエラーで4->2->1自動降格。
12 brief x 2群 x 2反復=48本(smoke済みは skip)。両群を交互に投入。infra失敗のみ同枠1回再実行(全体MAXRERUN)、
Writer内部Gate STOPは観測結果として保持(再実行しない)。logs/STOPがあれば新規runを開始しない。"""
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
BASE = "er052_output/all6_writer_redesign_necessity_01"
RUNS = f"{BASE}/runs"
B3 = "er052_output/open233_b3_trial_01/runs"
LED = "er052_output/open233_polysemy_trial_02/ledgers/{s}/control/research_ledger/verified_fact_ledger.txt"
PY = sys.executable
SLUGS = ["meta", "hormuz", "space_weapons"]
ARMS = ["baseline", "all6"]
REPS = [1, 2]
BS = [1, 2, 3, 4]
MAXRERUN = int(os.environ.get("MAXRERUN", "8"))
CUM_LIMIT = float(os.environ.get("CUM_LIMIT", "400"))   # T-A累計見込み(¥)。到達時は新規runを止めてFableへ報告(自動STOPではなく判断待ち)
RUN_LIMIT = 15.0
MEMSIG = ("1455", "MemoryError")
GATE_TOKENS = ("[STOP]", "JA_RECHECK_REQUIRED", "JA_FACT_CHECK_STOP", "Advanced deviation")
PRICE = {"gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-6-luna": (0.10, 0.01, 0.50)}   # $/1M in, cached, out
USD_JPY = 160.0
lock = threading.Lock()
state = {"reruns": 0, "stop": None, "mem_event": False, "mem_runs": [], "consec_fail": 0}
cells = {}


def run_cost_jpy(d):
    tot = 0.0
    p = f"{d}/raw_usage_log.jsonl"
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            pr = PRICE.get(r.get("model_id"))
            if not pr:
                continue
            inp = r.get("input_tokens") or 0
            cached = r.get("cached_input_tokens") or 0
            out = r.get("output_tokens") or 0
            tot += ((inp - cached) * pr[0] + cached * pr[1] + out * pr[2]) / 1e6 * USD_JPY
    bs = f"{d}/checker/budget_state_checker_after_p01.json"
    if os.path.exists(bs):
        try:
            tot += json.load(open(bs, encoding="utf-8")).get("cumulative_jpy", 0.0)
        except Exception:  # noqa: BLE001
            pass
    return tot


def all_costs():
    tot = mx = 0.0
    for d in glob.glob(f"{RUNS}/*/control/b*__*__r*"):
        c = run_cost_jpy(d)
        tot += c
        mx = max(mx, c)
    return tot, mx


def guard():
    if state["stop"] or os.path.exists(f"{BASE}/logs/STOP"):
        return True
    tot, mx = all_costs()
    if tot >= CUM_LIMIT:
        state["stop"] = f"cum {tot:.1f} >= {CUM_LIMIT}"
    elif mx > RUN_LIMIT:
        state["stop"] = f"run max {mx:.1f} > {RUN_LIMIT}"
    elif state["consec_fail"] >= 3:
        state["stop"] = "consecutive_infra_failures>=3"
    if state["stop"]:
        os.makedirs(f"{BASE}/logs", exist_ok=True)
        open(f"{BASE}/logs/STOP", "w").close()
        return True
    return False


def outdir(slug, b, arm, rep):
    return f"{RUNS}/{slug}/control/b{b}__{arm}__r{rep}"


def cmd(slug, b, arm, rep):
    return [PY, "er052_all6_writer_trial_01_run.py", "--arm", arm, "--slug", slug,
            "--brief-md", f"{B3}/{slug}/nb/V0/b{b}/storyline_b3/selected_brief.md",
            "--ledger-txt", LED.format(s=slug), "--out-dir", outdir(slug, b, arm, rep),
            "--budget-jpy", "12", "--yes-run-paid"]


def run(job):
    slug, b, arm, rep = job
    key = f"{slug}/b{b}/{arm}/r{rep}"
    rec = cells[key] = {"slug": slug, "b": b, "arm": arm, "rep": rep, "attempts": [], "status": "running"}
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    od = outdir(slug, b, arm, rep)
    for attempt in (1, 2):
        if guard() or state["mem_event"]:
            rec["status"] = "halted"; return
        os.makedirs(f"{RUNS}/_logs", exist_ok=True)
        log = f"{RUNS}/_logs/{slug}_b{b}_{arm}_r{rep}_a{attempt}.log"
        with open(log, "w", encoding="utf-8") as lf:
            try:
                rc = subprocess.call(cmd(slug, b, arm, rep), stdout=lf, stderr=subprocess.STDOUT, env=env)
            except OSError as e:
                rc = -1; lf.write("DRIVER OSError: " + repr(e) + "\n")
        tail = open(log, encoding="utf-8", errors="replace").read()[-1500:]
        man = f"{od}/manifest.json"
        reason = json.load(open(man, encoding="utf-8")).get("exit_reason") if os.path.exists(man) else "no_manifest"
        rec["attempts"].append({"attempt": attempt, "rc": rc, "exit_reason": reason, "log": log})
        if rc == 0 and reason == "completed":
            state["consec_fail"] = 0
            rec["status"] = "completed"; return
        if any(m in tail for m in MEMSIG) or rc == -1:
            with lock:
                state["mem_event"] = True; state["mem_runs"].append(key)
            rec["status"] = "mem_failed"; return
        gate = any(m in (reason or "") + tail for m in GATE_TOKENS)
        if gate:
            rec["status"] = "WRITER_GATE_STOP"; rec["failure_class"] = "gate"; return   # 観測結果。再実行しない
        with lock:
            state["consec_fail"] += 1
            if attempt == 2 or state["reruns"] >= MAXRERUN:
                rec["status"] = "infra_failed"; rec["failure_class"] = "infra"; return
            state["reruns"] += 1
        shutil.move(od, od + f"_failed_a{attempt}")
    rec["status"] = "infra_failed"


def build_jobs():
    jobs = []
    for rep in REPS:
        for b in BS:
            for slug in SLUGS:
                for arm in (ARMS if (rep + b) % 2 == 0 else ARMS[::-1]):
                    jobs.append((slug, b, arm, rep))
    return jobs


def todo_jobs():
    out = []
    for j in build_jobs():
        od = outdir(*j[:1], j[1], j[2], j[3])
        if os.path.exists(f"{od}/manifest.json"):
            cells[f"{j[0]}/b{j[1]}/{j[2]}/r{j[3]}"] = {"status": "existing"}
            continue
        out.append(j)
    return out


def main():
    from concurrent.futures import ThreadPoolExecutor
    level = min(int(os.environ.get("WORKERS", "4")), 4)
    history = []
    retry_at_1 = False
    while True:
        todo = todo_jobs()
        if os.environ.get("DRYRUN"):
            print(len(todo), todo[:6]); return
        if not todo or guard():
            break
        state["mem_event"] = False
        history.append({"workers": level, "todo": len(todo), "t": time.strftime("%H:%M:%S")})
        print("round workers=%d todo=%d" % (level, len(todo)), flush=True)
        with ThreadPoolExecutor(max_workers=level) as ex:
            list(ex.map(run, todo))
        if not state["mem_event"]:
            break
        for j in todo:
            od = outdir(*j[:1], j[1], j[2], j[3])
            if os.path.isdir(od) and not os.path.exists(f"{od}/manifest.json"):
                shutil.rmtree(od, ignore_errors=True)
        if level == 4:
            level = 2
        elif level == 2:
            level = 1
        else:
            if retry_at_1:
                state["stop"] = "memory_error_at_workers_1_twice"; break
            retry_at_1 = True
        print("MEM downgrade -> workers=%d" % level, flush=True)
        state["mem_runs"] = []
    json.dump({"cells": cells, "state": state, "history": history},
              open(f"{RUNS}/driver_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", state, history, flush=True)


if __name__ == "__main__":
    main()
