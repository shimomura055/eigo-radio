# -*- coding: utf-8 -*-
"""OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 段階2 driver(Trial専用)。5条件x3テーマx b1-b4 = 60 run、Writer phase1 -> phase2(--no-checker)。
brief出現を待って起動。停止runは同枠1回再実行(全体の再実行は MAXRERUN まで、B3再実行分を引いた残り)。STOPマーカー(logs/STOP)があれば新規phaseを開始しない。"""
import json, os, subprocess, sys, threading, time, shutil, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
B = "er052_output/open233_b3_trial_01"
RUNS = f"{B}/runs"
PY = sys.executable
SLUGS = ["meta", "hormuz", "space_weapons"]
VARS = ["V0", "V1", "V3", "V5", "V6"]
LED = "er052_output/open233_polysemy_trial_02/ledgers/{s}"
MAXRERUN = int(os.environ.get("MAXRERUN", "8"))
lock = threading.Lock()
state = {"reruns": 0, "consec_fail": 0, "stop": None, "mem_event": False, "mem_runs": []}
# A6: 累計基準=オンディスク実測(brief+w1完了/失敗 ≈299)+クラッシュ前復元不能分推定20 ≈319。A5の二重計上は廃止。
CUM_EST0 = 405.6  # A6b: 319 + A6実費86.6(オンディスク実測385.68-299.04)。削除したinfra失敗分4.66は含む(保守的)
DISK0 = None  # main()開始時のオンディスクw1*合計(以後の増分のみ加算)
GATE_TOKENS = ("[STOP]", "JA_RECHECK_REQUIRED", "JA_FACT_CHECK_STOP", "Advanced deviation")
SKIP_FINAL = {"hormuz/V3/b1": "2回試行済み(A4/A5)・Writer内部Gate STOP", "meta/V5/b2": "A5で試行済み・Writer内部Gate STOP(Advanced deviation MAJOR)",
              "meta/V5/b3": "2回試行済み・JA_FACT_CHECK_STOP", "hormuz/V5/b1": "A6で2回試行済み・Writer内部Gate STOP(LEDGER_DEVIATION MAJOR)", "meta/V5/b4": "ユーザー/Fable指示により再試行対象外(A5で試行済み)"}
CUM_LIMIT = float(os.environ.get("CUM_LIMIT", "480"))
RUN_LIMIT = 15.0
MEMSIG = ("1455", "MemoryError")
cells = {}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def w1_costs():
    import glob
    tot = 0.0; mx = 0.0
    for f in glob.glob(f"{RUNS}/*/nb/*/b*/w1*/cost.json"):
        try:
            c = json.load(open(f, encoding="utf-8"))["total_jpy"]
        except Exception:
            continue
        tot += c; mx = max(mx, c)
    return tot, mx


def guard():
    """STOP条件(累計>=480円見込み/1 run>15円/連続失敗3/STOPファイル)。Trueなら新規phaseを開始しない。"""
    if state["stop"] or os.path.exists(f"{B}/logs/STOP"):
        return True
    tot, mx = w1_costs()
    cum = CUM_EST0 + tot - (DISK0 or 0.0)
    if cum >= CUM_LIMIT:
        state["stop"] = f"cum {cum:.2f} >= {CUM_LIMIT}"
    elif mx > RUN_LIMIT:
        state["stop"] = f"run max {mx:.2f} > {RUN_LIMIT}"
    elif state["consec_fail"] >= 3:
        state["stop"] = "consecutive_failures>=3"
    if state["stop"]:
        open(f"{B}/logs/STOP", "w").close()
        return True
    return False


def cmd_for(slug, v, i, phase):
    topic = open(f"{LED.format(s=slug)}/topic.txt", encoding="utf-8").read().strip()
    out = f"{RUNS}/{slug}/nb/{v}/b{i}/w1"
    brief = f"{RUNS}/{slug}/nb/{v}/b{i}/storyline_b3/selected_brief.md"
    c = [PY, "er052_open233_polysemy_nb_dev_01.py", "--phase", phase, "--slug", slug, "--theme", topic,
         "--ledger-txt", f"{LED.format(s=slug)}/control/research_ledger/verified_fact_ledger.txt",
         "--out-dir", out, "--yes-run-paid"]
    if phase == "phase1":
        c += ["--brief-md", brief, "--budget-jpy", "8"]
    else:
        c += ["--no-checker", "--budget-jpy", "14"]
    return c, out, brief


def run(slug, v, i):
    key = f"{slug}/{v}/b{i}"
    env = dict(os.environ, OPEN233_RUNS_ROOT=RUNS, OPEN233_B3_VARIANT="nb", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    rec = cells[key] = {"slug": slug, "variant": v, "b": i, "attempts": [], "status": "waiting_brief"}
    _, _, brief = cmd_for(slug, v, i, "phase1")
    while not os.path.exists(brief):
        if os.path.exists(f"{B}/logs/B3_DONE"):
            time.sleep(5)
            if not os.path.exists(brief):
                rec["status"] = "no_brief"; return
        time.sleep(10)
    time.sleep(2)
    rec["status"] = "running"
    rec["brief_sha256"] = sha(brief)
    first = 2 if os.path.isdir(f"{RUNS}/{slug}/nb/{v}/b{i}/w1_failed_a1") else 1  # 既にa1試行済みならa2のみ
    for attempt in range(first, 3):
        ok = True
        for phase in ("phase1", "phase2"):
            if guard() or state["mem_event"]:
                rec["status"] = "halted_by_STOP_marker" if not state["mem_event"] else "halted_mem_downgrade"; return
            c, out, _ = cmd_for(slug, v, i, phase)
            os.makedirs(f"{RUNS}/_logs", exist_ok=True)
            log = f"{RUNS}/_logs/{slug}_{v}_b{i}_{phase}_a{attempt}.log"
            with open(log, "w", encoding="utf-8") as lf:
                try:
                    rc = subprocess.call(c, stdout=lf, stderr=subprocess.STDOUT, env=env)
                except OSError as e:
                    rc = -1; lf.write("DRIVER OSError: " + repr(e) + chr(10))
            tail = open(log, encoding="utf-8", errors="replace").read()[-600:]
            rec["attempts"].append({"attempt": attempt, "phase": phase, "rc": rc, "log": log, "cmd": " ".join(c[1:])})
            fin = (os.path.exists(f"{out}/ja_writer/revision2.md") if phase == "phase1" else os.path.exists(f"{out}/b1b/article.md"))
            if rc != 0 or not fin:
                if any(m in tail for m in MEMSIG) or (rc == -1):
                    with lock:
                        state["mem_event"] = True; state["mem_runs"].append(key)
                    rec["status"] = "mem_failed"; rec["attempts"][-1]["stop_tail"] = tail
                    return
                ok = False
                rec["attempts"][-1]["stop_tail"] = tail
                rec["attempts"][-1]["failure_class"] = "WRITER_GATE_STOP" if any(m in tail for m in GATE_TOKENS) and rc != -1 else "INFRA"
                break
        if ok:
            state["consec_fail"] = 0
            rec["status"] = "completed"; return
        gate = rec["attempts"][-1].get("failure_class") == "WRITER_GATE_STOP"
        with lock:
            if not gate:
                state["consec_fail"] += 1  # infra失敗のみカウント(Gate発火は観測結果)
        with lock:
            if attempt == 2 or (not gate and state["reruns"] >= MAXRERUN):
                rec["status"] = "WRITER_GATE_STOP" if gate else "stopped"; return
            state["reruns"] += 1
        _, out, _ = cmd_for(slug, v, i, "phase1")
        if os.path.exists(out):
            shutil.move(out, out + f"_failed_a{attempt}")
        rec["rerun"] = True
    rec["status"] = "stopped"


def main():
    """A5: 単層ThreadPoolExecutor(xargs併用なし)。STAGE2_WORKERS(既定4)から、メモリ不足(WinError 1455/MemoryError)検知で 4->2->1 へ自動降格し未完了分を再起動。
    並列1で再発した場合は、並列1で1回だけ再試行し、以後STOP。完了済みrunはスキップ。"""
    from concurrent.futures import ThreadPoolExecutor
    level = min(int(os.environ.get("STAGE2_WORKERS", "4")), 4)
    global DISK0
    DISK0 = w1_costs()[0]
    json.dump(SKIP_FINAL, open(f"{RUNS}/writer_gate_stop_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    history = []
    retry_at_1 = False
    while True:
        todo = []
        for v in VARS:
            for s_ in SLUGS:
                for i in (1, 2, 3, 4):
                    if f"{s_}/{v}/b{i}" in SKIP_FINAL:
                        cells[f"{s_}/{v}/b{i}"] = {"slug": s_, "variant": v, "b": i, "status": "WRITER_GATE_STOP_FINAL_SKIPPED", "reason": SKIP_FINAL[f"{s_}/{v}/b{i}"]}
                        continue
                    base = f"{RUNS}/{s_}/nb/{v}/b{i}/w1"
                    if os.path.exists(f"{base}/writer_run_summary.json") and os.path.exists(f"{base}/b1b/article.md"):
                        cells[f"{s_}/{v}/b{i}"] = {"slug": s_, "variant": v, "b": i, "status": "completed_skipped_existing"}
                    else:
                        todo.append((s_, v, i))
        if "DRYRUN" in os.environ:
            print("todo", len(todo), [k for k in cells if cells[k]["status"].startswith("WRITER")]); return
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
        # 中断w1(未完了)を run単位で削除して同枠再実行
        for (s_, v, i) in todo:
            base = f"{RUNS}/{s_}/nb/{v}/b{i}/w1"
            if os.path.isdir(base) and not os.path.exists(f"{base}/b1b/article.md"):
                shutil.rmtree(base, ignore_errors=True)
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
    json.dump({"cells": cells, "state": state, "history": history}, open(f"{RUNS}/driver_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", state, history, flush=True)


if __name__ == "__main__":
    main()
