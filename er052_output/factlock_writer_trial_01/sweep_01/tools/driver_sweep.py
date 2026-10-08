# -*- coding: utf-8 -*-
"""FACTLOCK sweep driver(Trial専用、委任_04b)。driver_fl.py相当: 単層ThreadPool(既定4並列)+メモリエラーで4->2->1自動降格。
11変種 x 3 brief = 33本(smoke済み・既存manifestはskip)。infra失敗のみ同枠1回再実行(全体MAXRERUN)、Gate STOPは観測結果として保持。"""
import glob, json, os, shutil, subprocess, sys, threading, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
BASE = "er052_output/factlock_writer_trial_01"
SWEEP = f"{BASE}/sweep_01"
RUNS = f"{SWEEP}/runs"
B3 = "er052_output/open233_b3_trial_01/runs"
LED = "er052_output/open233_b3_trial_01/runs/{s}/nb/V0/b{b}/research_ledger/verified_fact_ledger.txt"
THEME = "er052_output/open233_polysemy_trial_02/ledgers/{s}/topic.txt"
VARIANTS = ["S1", "S2", "S3", "S4", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
BRIEFS = [("meta", 2), ("hormuz", 4), ("space_weapons", 3)]
PY = sys.executable
SLUGS = ["meta", "hormuz", "space_weapons"]
REPS = [1, 2]
BS = [1, 2, 3, 4]
MAXRERUN = int(os.environ.get("MAXRERUN", "5"))
CUM_LIMIT = float(os.environ.get("CUM_LIMIT", "300"))   # 見込み累計(JPY)。到達時は新規runを止めて報告判断(Guardrail)
RUN_LIMIT = 15.0
MEMSIG = ("1455", "MemoryError")
GATE_TOKENS = ("[STOP]", "JA_RECHECK_REQUIRED", "JA_FACT_CHECK_STOP", "Advanced deviation")
PRICE = {"gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-6-luna": (0.10, 0.01, 0.50)}
USD_JPY = 160.0
lock = threading.Lock()
state = {"reruns": 0, "stop": None, "mem_event": False, "mem_runs": [], "consec_fail": 0}
cells = {}


def run_cost_jpy(d):
    tot = 0.0
    p = f"{d}/raw_usage_log.jsonl"
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try: r = json.loads(line)
            except Exception: continue
            pr = PRICE.get(r.get("model_id"))
            if not pr: continue
            inp = r.get("input_tokens") or 0; cached = r.get("cached_input_tokens") or 0; out = r.get("output_tokens") or 0
            tot += ((inp - cached) * pr[0] + cached * pr[1] + out * pr[2]) / 1e6 * USD_JPY
    bs = f"{d}/checker/budget_state_checker_after_p01.json"
    if os.path.exists(bs):
        try: tot += json.load(open(bs, encoding="utf-8")).get("cumulative_jpy", 0.0)
        except Exception: pass
    return tot


def all_costs():
    tot = mx = 0.0
    for d in glob.glob(f"{RUNS}/*/control/b*__S*__r*"):
        c = run_cost_jpy(d); tot += c; mx = max(mx, c)
    return tot, mx


def guard():
    if state["stop"] or os.path.exists(f"{SWEEP}/logs/STOP"):
        return True
    tot, mx = all_costs()
    if tot >= CUM_LIMIT: state["stop"] = f"cum {tot:.1f} >= {CUM_LIMIT}"
    elif mx > RUN_LIMIT: state["stop"] = f"run max {mx:.1f} > {RUN_LIMIT}"
    elif state["consec_fail"] >= 3: state["stop"] = "consecutive_infra_failures>=3"
    if state["stop"]:
        os.makedirs(f"{SWEEP}/logs", exist_ok=True); open(f"{SWEEP}/logs/STOP", "w").close(); return True
    return False


def outdir(slug, b, v):
    return f"{RUNS}/{slug}/control/b{b}__{v}__r1"


def cmd(slug, b, rep):
    v = rep   # 第3要素=変種ID
    return [PY, "-X", "utf8", "er052_factlock_sweep_01_run.py", "--variant", v, "--slug", slug, "--theme-file", THEME.format(s=slug),
            "--brief-md", f"{BASE}/briefs/{slug}/b{b}/selected_brief_factlock.md",
            "--core-numbers-json", f"{BASE}/briefs/{slug}/b{b}/core_numbers.json",
            "--ledger-txt", LED.format(s=slug, b=b), "--out-dir", outdir(slug, b, rep),
            "--budget-jpy", "12", "--yes-run-paid"]


def run(job):
    slug, b, rep = job
    key = f"{slug}/b{b}/{rep}"
    rec = cells[key] = {"slug": slug, "b": b, "rep": rep, "attempts": [], "status": "running"}
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    od = outdir(slug, b, rep)
    for attempt in (1, 2):
        if guard() or state["mem_event"]:
            rec["status"] = "halted"; return
        os.makedirs(f"{RUNS}/_logs", exist_ok=True)
        log = f"{RUNS}/_logs/{slug}_b{b}_{rep}_a{attempt}.log"
        with open(log, "w", encoding="utf-8") as lf:
            try: rc = subprocess.call(cmd(slug, b, rep), stdout=lf, stderr=subprocess.STDOUT, env=env)
            except OSError as e:
                rc = -1; lf.write("DRIVER OSError: " + repr(e) + "\n")
        tail = open(log, encoding="utf-8", errors="replace").read()[-1500:]
        man = f"{od}/manifest.json"
        reason = json.load(open(man, encoding="utf-8")).get("exit_reason") if os.path.exists(man) else "no_manifest"
        rec["attempts"].append({"attempt": attempt, "rc": rc, "exit_reason": reason, "log": log})
        if rc == 0 and reason == "completed":
            state["consec_fail"] = 0; rec["status"] = "completed"; return
        if any(m in tail for m in MEMSIG) or rc == -1:
            with lock:
                state["mem_event"] = True; state["mem_runs"].append(key)
            rec["status"] = "mem_failed"; return
        if any(m in (reason or "") + tail for m in GATE_TOKENS):
            rec["status"] = "WRITER_GATE_STOP"; rec["failure_class"] = "gate"; return
        with lock:
            state["consec_fail"] += 1
            if attempt == 2 or state["reruns"] >= MAXRERUN:
                rec["status"] = "infra_failed"; rec["failure_class"] = "infra"; return
            state["reruns"] += 1
        shutil.move(od, od + f"_failed_a{attempt}")
    rec["status"] = "infra_failed"


def build_jobs():
    return [(s, b, v) for v in VARIANTS for (s, b) in BRIEFS]


def todo_jobs():
    out = []
    for j in build_jobs():
        if os.path.exists(f"{outdir(*j)}/manifest.json"):
            cells[f"{j[0]}/b{j[1]}/{j[2]}"] = {"status": "existing"}; continue
        out.append(j)
    return out


def main():
    from concurrent.futures import ThreadPoolExecutor
    level = min(int(os.environ.get("WORKERS", "4")), 4)
    history = []; retry_at_1 = False
    while True:
        todo = todo_jobs()
        if os.environ.get("DRYRUN"):
            print(len(todo), todo[:6]); return
        if not todo or guard(): break
        state["mem_event"] = False
        history.append({"workers": level, "todo": len(todo), "t": time.strftime("%H:%M:%S")})
        print("round workers=%d todo=%d" % (level, len(todo)), flush=True)
        with ThreadPoolExecutor(max_workers=level) as ex:
            list(ex.map(run, todo))
        if not state["mem_event"]: break
        for j in todo:
            od = outdir(*j)
            if os.path.isdir(od) and not os.path.exists(f"{od}/manifest.json"): shutil.rmtree(od, ignore_errors=True)
        if level == 4: level = 2
        elif level == 2: level = 1
        else:
            if retry_at_1:
                state["stop"] = "memory_error_at_workers_1_twice"; break
            retry_at_1 = True
        print("MEM downgrade -> workers=%d" % level, flush=True)
        state["mem_runs"] = []
    os.makedirs(RUNS, exist_ok=True)
    json.dump({"cells": cells, "state": state, "history": history}, open(f"{RUNS}/driver_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", state, history, flush=True)


if __name__ == "__main__":
    main()
