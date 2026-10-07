# -*- coding: utf-8 -*-
"""OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 driver(Trial専用)。18 run(Meta nb x10 + 4テーマ control x2)、phase1->phase2(EN+Checker)。
流用元: er052_output/open233_b3_trial_01/tools/driver_stage2.py。単層ThreadPoolExecutor(既定4)、メモリ降格4->2->1、guard(累計480/1run25/infra連続3/STOPファイル)。
Writer内部Gate STOPは回避せず同枠1回のみ再実行(全体上限MAXRERUN=4)。DRYRUN環境変数で18コマンド表示のみ(0円)。"""
import glob, json, os, shutil, subprocess, sys, threading, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
B = "er052_output/open233_control_checker_polysemy_trial_01"
RUNS = f"{B}/runs"
PY = os.path.abspath(".venv/Scripts/python.exe") if os.path.exists(".venv/Scripts/python.exe") else sys.executable
LEDG = "er052_output/open233_polysemy_trial_02/ledgers/{s}"
META_LEDGER = "er052_output/open233_meta_rollback_minimal_note_01/ledger/nb/research_ledger/verified_fact_ledger.txt"
LEGACY = "legacy_abd16d9a"
MAXRERUN = int(os.environ.get("MAXRERUN", "4"))
CUM_LIMIT = float(os.environ.get("CUM_LIMIT", "480"))
RUN_LIMIT = float(os.environ.get("RUN_LIMIT", "25"))
GATE_TOKENS = ("[STOP]", "JA_RECHECK_REQUIRED", "JA_FACT_CHECK_STOP", "Advanced deviation", "LEDGER_DEVIATION")
MEMSIG = ("1455", "MemoryError")
lock = threading.Lock()
state = {"reruns": 0, "consec_fail": 0, "stop": None, "mem_event": False, "mem_runs": [], "gate_stops_first": 0}
cells = {}


def tasks():
    t = [("meta", "nb", k) for k in range(1, 11)]
    for s in ("hormuz", "space_weapons", "sewer", "ai_control"):
        t += [(s, "control", 1), (s, "control", 2)]
    return t


def rep_dir(s, v, k):
    return f"{RUNS}/{s}/{v}/rep{k}"


def ledger_of(s, v):
    return META_LEDGER if s == "meta" else f"{LEDG.format(s=s)}/control/research_ledger/verified_fact_ledger.txt"


def theme_of(s):
    return open(f"{LEDG.format(s=s)}/topic.txt", encoding="utf-8").read().strip()


def cmd_for(s, v, k, phase):
    c = [PY, "er052_open233_polysemy_nb_dev_01.py", "--phase", phase, "--slug", s, "--theme", theme_of(s),
         "--ledger-txt", ledger_of(s, v), "--out-dir", rep_dir(s, v, k), "--yes-run-paid"]
    c += ["--budget-jpy", "8"] if phase == "phase1" else ["--budget-jpy", "15", "--checker-budget-jpy", "15"]
    return c


def env_for(v):
    e = dict(os.environ, OPEN233_RUNS_ROOT=RUNS, OPEN233_B3_VARIANT=v, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    e.pop("OPEN233_NOTE_PREFIX", None)
    e.pop("OPEN233_NOTE_RULE", None)
    if v == "nb":
        e["OPEN233_NOTE_RULE"] = LEGACY
    return e


def dir_cost(d):
    tot = 0.0
    try:
        tot += json.load(open(f"{d}/cost.json", encoding="utf-8"))["total_jpy"]
    except Exception:
        pass
    try:
        tot += json.load(open(f"{d}/checker/budget_state_checker_after_p01.json", encoding="utf-8"))["cumulative_jpy"]
    except Exception:
        pass
    return tot


def all_costs():
    tot, mx = 0.0, 0.0
    for d in glob.glob(f"{RUNS}/*/*/rep*"):
        c = dir_cost(d)
        tot += c
        mx = max(mx, c)
    return tot, mx


def guard():
    if state["stop"] or os.path.exists(f"{B}/logs/STOP"):
        return True
    tot, mx = all_costs()
    if tot >= CUM_LIMIT:
        state["stop"] = f"cum {tot:.2f} >= {CUM_LIMIT}"
    elif mx > RUN_LIMIT:
        state["stop"] = f"run max {mx:.2f} > {RUN_LIMIT}"
    elif state["consec_fail"] >= 3:
        state["stop"] = "consecutive_failures>=3"
    if state["stop"]:
        open(f"{B}/logs/STOP", "w").close()
        return True
    return False


def done_ok(d):
    return os.path.exists(f"{d}/b1b/article.md") and len(glob.glob(f"{d}/checker/runs/*.json")) == 1


def log_progress(key, status):
    tot, mx = all_costs()
    n_done = sum(1 for c in cells.values() if c.get("status") == "completed")
    with lock:
        with open(f"{RUNS}/cost_progress.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "run": key, "status": status, "completed": n_done,
                                "cum_jpy": round(tot, 3), "max_run_jpy": round(mx, 3)}, ensure_ascii=False) + "\n")


def run(s, v, k):
    key = f"{s}/{v}/rep{k}"
    rec = cells[key] = {"slug": s, "variant": v, "rep": k, "attempts": [], "status": "running"}
    env = env_for(v)
    d = rep_dir(s, v, k)
    for attempt in (1, 2):
        ok = True
        for phase in ("phase1", "phase2"):
            if guard() or state["mem_event"]:
                rec["status"] = "halted_mem_downgrade" if state["mem_event"] else "halted_by_STOP_marker"
                return
            c = cmd_for(s, v, k, phase)
            os.makedirs(f"{RUNS}/_logs", exist_ok=True)
            log = f"{RUNS}/_logs/{s}_{v}_rep{k}_{phase}_a{attempt}.log"
            t0 = time.strftime("%H:%M:%S")
            with open(log, "w", encoding="utf-8") as lf:
                try:
                    rc = subprocess.call(c, stdout=lf, stderr=subprocess.STDOUT, env=env)
                except OSError as e:
                    rc = -1
                    lf.write("DRIVER OSError: " + repr(e) + chr(10))
            tail = open(log, encoding="utf-8", errors="replace").read()[-1500:]
            fin = os.path.exists(f"{d}/ja_writer/revision2.md") if phase == "phase1" else done_ok(d)
            att = {"attempt": attempt, "phase": phase, "rc": rc, "log": log, "start": t0, "end": time.strftime("%H:%M:%S"),
                   "cmd": " ".join(c[1:]), "cost_after_jpy": round(dir_cost(d), 3)}
            rec["attempts"].append(att)
            if dir_cost(d) > RUN_LIMIT:
                state["stop"] = f"run {key} cost {dir_cost(d):.2f} > {RUN_LIMIT}"
            bad = (rc != 0 and phase == "phase1") or not fin
            if bad:
                if any(m in tail for m in MEMSIG) or rc == -1:
                    with lock:
                        state["mem_event"] = True
                        state["mem_runs"].append(key)
                    rec["status"] = "mem_failed"
                    att["stop_tail"] = tail
                    return
                ok = False
                att["stop_tail"] = tail
                att["failure_class"] = "WRITER_GATE_STOP" if any(m in tail for m in GATE_TOKENS) else "INFRA"
                break
            if phase == "phase2":
                att["checker_rc"] = rc
        if ok:
            state["consec_fail"] = 0
            rec["status"] = "completed"
            log_progress(key, "completed")
            return
        gate = rec["attempts"][-1].get("failure_class") == "WRITER_GATE_STOP"
        with lock:
            if attempt == 1 and gate:
                state["gate_stops_first"] += 1
            if not gate:
                state["consec_fail"] += 1
            if attempt == 2 or state["reruns"] >= MAXRERUN:
                rec["status"] = "WRITER_GATE_STOP" if gate else "stopped"
                log_progress(key, rec["status"])
                return
            state["reruns"] += 1
        if os.path.exists(d):
            shutil.move(d, d + f"_failed_a{attempt}")
        rec["rerun"] = True
        log_progress(key, f"failed_a{attempt}_rerun")
    rec["status"] = "stopped"


def main():
    from concurrent.futures import ThreadPoolExecutor
    level = min(int(os.environ.get("CCP_WORKERS", "4")), 4)
    os.makedirs(f"{RUNS}/_logs", exist_ok=True)
    if "DRYRUN" in os.environ:
        for (s, v, k) in tasks():
            print(f"[{s}/{v}/rep{k}] NOTE_RULE={LEGACY if v == 'nb' else '(unset)'} VARIANT={v}")
            for ph in ("phase1", "phase2"):
                print("  ", " ".join(x if " " not in x else repr(x) for x in cmd_for(s, v, k, ph)))
        return
    history, retry_at_1 = [], False
    while True:
        todo = [t for t in tasks() if not done_ok(rep_dir(*t))]
        if not todo or guard():
            break
        state["mem_event"] = False
        history.append({"workers": level, "todo": len(todo), "t": time.strftime("%H:%M:%S")})
        print("round workers=%d todo=%d" % (level, len(todo)), flush=True)
        with ThreadPoolExecutor(max_workers=level) as ex:
            list(ex.map(lambda a: run(*a), todo))
        if not state["mem_event"]:
            break
        history[-1]["mem_runs"] = list(state["mem_runs"])
        for t in todo:
            d = rep_dir(*t)
            if os.path.isdir(d) and not done_ok(d):
                shutil.rmtree(d, ignore_errors=True)
        if level == 4:
            level = 2
        elif level == 2:
            level = 1
        else:
            if retry_at_1:
                state["stop"] = "memory_error_at_workers_1_twice"
                break
            retry_at_1 = True
        print("MEM downgrade -> workers=%d" % level, flush=True)
        state["mem_runs"] = []
    tot, mx = all_costs()
    json.dump({"cells": cells, "state": state, "history": history, "cum_jpy": round(tot, 3), "max_run_jpy": round(mx, 3),
               "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S")}, open(f"{RUNS}/driver_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", state, history, flush=True)


if __name__ == "__main__":
    main()
