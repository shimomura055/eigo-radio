# -*- coding: utf-8 -*-
"""OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01 Phase B driver(Trial専用)。36 run同時起動、phase1->phase2(--no-checker)。
停止run(phase1/phase2失敗)は同枠1回だけ再実行、全体の再実行は6回まで。"""
import json, os, subprocess, sys, threading, time, shutil, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
B = "er052_output/open233_note_transfer_matrix_01"
RUNS = f"{B}/runs"
PY = sys.executable
SLUGS = ["meta", "hormuz", "sewer"]
CONDS = [t + m for t in ("T0", "T1", "T2") for m in ("M0", "M1")]
lock = threading.Lock()
state = {"reruns": 0}
MAXRERUN = 6
cells = {}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cmd_for(slug, cond, rep, phase):
    topic = open(f"er052_output/open233_polysemy_trial_02/ledgers/{slug}/topic.txt", encoding="utf-8").read().strip()
    out = f"{RUNS}/{slug}/nb/{cond}/rep{rep}"
    c = [PY, "er052_open233_polysemy_nb_dev_01.py", "--phase", phase, "--slug", slug, "--theme", topic,
         "--ledger-txt", f"er052_output/open233_polysemy_trial_02/ledgers/{slug}/control/research_ledger/verified_fact_ledger.txt",
         "--out-dir", out, "--yes-run-paid"]
    if phase == "phase1":
        c += ["--brief-md", f"{B}/briefs/{slug}/{cond}.md", "--budget-jpy", "8"]
    else:
        c += ["--no-checker", "--budget-jpy", "6"]
    return c, out


def run(slug, cond, rep):
    key = f"{slug}/{cond}/rep{rep}"
    env = dict(os.environ, OPEN233_RUNS_ROOT=RUNS, OPEN233_B3_VARIANT="nb", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    rec = cells[key] = {"slug": slug, "cond": cond, "rep": rep, "attempts": [], "status": "running"}
    for attempt in (1, 2):
        ok = True
        for phase in ("phase1", "phase2"):
            c, out = cmd_for(slug, cond, rep, phase)
            os.makedirs(f"{RUNS}/_logs", exist_ok=True)
            log = f"{RUNS}/_logs/{slug}_{cond}_rep{rep}_{phase}_a{attempt}.log"
            with open(log, "w", encoding="utf-8") as lf:
                rc = subprocess.call(c, stdout=lf, stderr=subprocess.STDOUT, env=env)
            tail = open(log, encoding="utf-8", errors="replace").read()[-600:]
            rec["attempts"].append({"attempt": attempt, "phase": phase, "rc": rc, "log": log, "cmd": " ".join(c[:2]) + " ... " + " ".join(c[-8:])})
            fin = (os.path.exists(f"{out}/ja_writer/revision2.md") if phase == "phase1" else os.path.exists(f"{out}/b1b/article.md"))
            if rc != 0 or not fin:
                ok = False
                rec["attempts"][-1]["stop_tail"] = tail
                break
        if ok:
            rec["status"] = "completed"
            return
        # 停止: 同枠1回再実行
        with lock:
            if attempt == 2 or state["reruns"] >= MAXRERUN:
                rec["status"] = "stopped"
                return
            state["reruns"] += 1
        _, out = cmd_for(slug, cond, rep, "phase1")
        if os.path.exists(out):
            shutil.move(out, out + f"_failed_a{attempt}")
        rec["rerun"] = True
    rec["status"] = "stopped"


def main():
    threads = []
    for s in SLUGS:
        for c in CONDS:
            for r in (1, 2):
                t = threading.Thread(target=run, args=(s, c, r)); t.start(); threads.append(t)
                time.sleep(1.0)
    for t in threads: t.join()
    json.dump({"cells": cells, "reruns": state["reruns"]}, open(f"{RUNS}/driver_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", state)


if __name__ == "__main__":
    main()
