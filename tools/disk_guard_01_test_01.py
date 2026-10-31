"""disk_guard_01 模擬検証(sandbox専用。実環境の削除なし)。証跡=docs/research/DISK-GUARD-AUTO-CLEANUP-01/evidence_01/(委任_01)・evidence_02/(委任_02: Opus M-1〜M-6/R-1〜R-5反映)。

実行: python tools/disk_guard_01_test_01.py [--evidence-dir DIR]
sandbox: tempdir/<root>/{repo(本物のgit)+origin.git, LocalAppData/Temp/claude/<proj>/<session>/{tasks,scratchpad}, LocalAppData/pip/Cache}
大きい.outputは sparse file(論理サイズのみ、実ディスクはほぼ消費しない)。
"""
import contextlib
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(HERE, "disk_guard_01.py")
PY = sys.executable
GB = 1024 ** 3
U = GB // 1000  # 1000倍縮尺: 検証では「1GB」を1000分の1(約1.07MB)のU単位で表し、閾値(GB引数)も1000分の1に縮尺する(論理は同一)
PROJ = "PROJ"
CUR = "SESS_CURRENT_01"   # 現session(稼働中: tasksに直近更新あり)
OLD = "SESS_OLD_000001"     # 旧session(24h超)
WTS = "SESS_WT_0000001"     # worktree置き場の非稼働session(tasks配下が3時間以上前)
JUNCTIONS = []
sys.path.insert(0, HERE)
RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append({"check": name, "pass": bool(cond), "detail": detail})
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    return cond


def git(cwd, *args, check_rc=True):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check_rc and r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r.stdout


def sparse(path, size):
    """縮尺検証のため通常ファイルを作る(名前は互換のまま)。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.truncate(size)


def age(path, hours):
    t = time.time() - hours * 3600
    os.utime(path, (t, t))


def age_tree(path, hours):
    for dp, dn, fs in os.walk(path):
        for x in fs + dn:
            try:
                age(os.path.join(dp, x), hours)
            except OSError:
                pass
    age(path, hours)


def write(path, text="x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def build(root, n_big=2, held=True):
    """sandboxを構築し path辞書を返す。"""
    repo = os.path.join(root, "repo")
    origin = os.path.join(root, "origin.git")
    os.makedirs(repo)
    git(root, "init", "-q", "--bare", origin)
    git(repo, "init", "-q", "-b", "main")
    write(os.path.join(repo, "a.txt"), "1")
    write(os.path.join(repo, ".gitignore"), "ignored_*.dat\n__pycache__/\n")
    write(os.path.join(repo, "CURRENT_SPEC.md"), "spec")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "c1")
    write(os.path.join(repo, "a.txt"), "2")
    git(repo, "commit", "-q", "-am", "c2")
    git(repo, "remote", "add", "origin", origin)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "fetch", "-q", "origin")
    local = os.path.join(root, "LocalAppData")
    proj = os.path.join(local, "Temp", "claude", PROJ)
    s1, s_old, s_wt = os.path.join(proj, CUR), os.path.join(proj, OLD), os.path.join(proj, WTS)
    t1, t_old, t_wt = os.path.join(s1, "tasks"), os.path.join(s_old, "tasks"), os.path.join(s_wt, "tasks")
    sp = os.path.join(s_wt, "scratchpad")          # 非稼働sessionのscratchpad(worktree削除の対象になり得る)
    sp_active = os.path.join(s1, "scratchpad")     # 稼働中sessionのscratchpad(worktreeは対象外)
    os.makedirs(t1)
    os.makedirs(t_old)
    os.makedirs(t_wt)
    os.makedirs(sp)
    os.makedirs(sp_active)
    write(os.path.join(t_wt, "marker.txt"), "idle")  # .outputでない(削除されない)。mtimeを30h前に
    age(os.path.join(t_wt, "marker.txt"), 30)
    age(t_wt, 30)
    P = {"root": root, "repo": repo, "sp": sp, "sp_active": sp_active, "t1": t1, "t_old": t_old}
    # --- outputs ---
    P["safe_outputs"] = []
    for i in range(n_big):
        f = os.path.join(t1, f"big_old_{i}.output")
        sparse(f, 6 * U)
        age(f, 3)
        P["safe_outputs"].append(f)
    f = os.path.join(t_old, "old_session_small.output")
    write(f, "log")
    age(f, 30)
    P["safe_outputs"].append(f)
    P["prot"] = []
    f = os.path.join(t1, "small_old_current.output")  # 現セッションの小さい古いログ(A2対象外)
    write(f, "log")
    age(f, 30)
    P["prot"].append(f)
    f = os.path.join(t1, "recent_big.output")  # 稼働中(直近更新)の巨大出力: 削除せずWARN
    sparse(f, 3 * U)
    P["prot"].append(f)
    P["recent_big"] = f
    if held:
        f = os.path.join(t1, "held_open_big.output")  # handle保持中(S1でopen)
        sparse(f, 6 * U)
        age(f, 3)
        P["prot"].append(f)
        P["held_open"] = f
    f = os.path.join(t1, "CURRENT_SPEC.md")  # SSOT名(.outputでもない)
    write(f)
    age(f, 30)
    P["prot"].append(f)
    f = os.path.join(t1, "OPEN_ITEMS.output")  # SSOT名を含む.output
    sparse(f, 6 * U)
    age(f, 3)
    P["prot"].append(f)
    f = os.path.join(repo, "er011_output", "huge.output")  # repo配下の成果物(パターン外)
    sparse(f, 6 * U)
    age(f, 30)
    P["prot"].append(f)
    f = os.path.join(root, "LocalAppData", "Temp", "claude", "OTHERPROJ", "S", "tasks", "x.output")
    os.makedirs(os.path.dirname(f), exist_ok=True)
    sparse(f, 6 * U)
    age(f, 30)
    P["prot"].append(f)  # 別project(対象外)
    # --- pip stub ---
    cache = os.path.join(local, "pip", "Cache")
    write(os.path.join(cache, "http", "a.bin"), "y" * 1000)
    stub = os.path.join(root, "pipstub.py")
    write(stub, (
        "import sys,os,shutil\n"
        f"c=r'{cache}'\n"
        "a=sys.argv[1:]\n"
        "if a[:2]==['cache','dir']: print(c)\n"
        "elif a[:2]==['cache','purge']:\n"
        "    [shutil.rmtree(os.path.join(c,x)) for x in os.listdir(c)]\n"
    ))
    P["pip_cmd"] = f"{PY}|{stub}"
    P["pip_file"] = os.path.join(cache, "http", "a.bin")
    # --- worktrees ---
    P["safe_wt"], P["prot_wt"] = [], []

    def add_wt(name, *extra, base=None):
        p = os.path.join(base or sp, name)
        git(repo, "worktree", "add", "-q", *extra[:-1], p, extra[-1]) if extra else None
        return p

    p = add_wt("wt_clean_detached", "--detach", "origin/main")
    P["safe_wt"].append(p)
    p = add_wt("wt_clean_old_commit", "--detach", "origin/main~1")
    P["safe_wt"].append(p)
    p = add_wt("wt_clean_branch_merged", "-b", "feat/merged", "origin/main")
    P["safe_wt"].append(p)
    p = add_wt("wt_clean_pycache", "--detach", "origin/main")
    write(os.path.join(p, "__pycache__", "m.pyc"), "c")
    P["safe_wt"].append(p)
    p = add_wt("wt_dirty_tracked", "--detach", "origin/main")
    write(os.path.join(p, "a.txt"), "modified")
    P["prot_wt"].append(p)
    p = add_wt("wt_untracked", "--detach", "origin/main")
    write(os.path.join(p, "new_evidence.txt"), "evidence")
    P["prot_wt"].append(p)
    p = add_wt("wt_ignored_file", "--detach", "origin/main")
    write(os.path.join(p, "ignored_x.dat"), "valuable ignored output")
    P["prot_wt"].append(p)
    p = add_wt("wt_ahead", "--detach", "origin/main")
    write(os.path.join(p, "b.txt"), "b")
    git(p, "add", "b.txt")
    git(p, "commit", "-q", "-m", "unpushed")
    P["prot_wt"].append(p)
    p = add_wt("wt_keep", "--detach", "origin/main")
    P["prot_wt"].append(p)
    write(os.path.join(sp, ".disk_guard_keep"), "# keep list\nwt_keep\n")
    p = add_wt("wt_locked", "--detach", "origin/main")
    git(repo, "worktree", "lock", p)
    P["prot_wt"].append(p)
    p = add_wt("wt_recent", "--detach", "origin/main")
    P["prot_wt"].append(p)
    P["wt_recent"] = p
    p = add_wt("wt_active_session", "--detach", "origin/main", base=sp_active)  # 稼働中sessionのscratchpad内
    P["prot_wt"].append(p)
    p = add_wt("wt_procheld", "--detach", "origin/main")  # 他は安全。processがpathを保持した時だけ保留(S1で検証)
    P["proc_wt"] = p
    out = os.path.join(root, "outside_scratchpad_wt")  # scratchpad外のworktree(許可パターン外)
    git(repo, "worktree", "add", "-q", "--detach", out, "origin/main")
    P["prot_wt"].append(out)
    # --- 全worktree/gitadminを3時間前へ(wt_recentは除く)、その後recentを更新 ---
    wtadmin = os.path.join(repo, ".git", "worktrees")
    for x in os.listdir(wtadmin):
        age_tree(os.path.join(wtadmin, x), 3)
    for q in P["safe_wt"] + P["prot_wt"] + [P["proc_wt"]]:
        age_tree(q, 3)
    now = time.time()
    adm = os.path.join(wtadmin, os.path.basename(P["wt_recent"]))
    os.utime(os.path.join(adm, "HEAD"), (now, now))
    os.utime(P["wt_recent"], (now, now))
    return P


def base_args(P, runs=None, sess=CUR):
    a = ["--root", P["root"], "--repo", P["repo"], "--project", PROJ,
         "--pip-cmd", P["pip_cmd"], "--runs-dir", runs or os.path.join(P["root"], "runs"),
         "--warn-gb", "0.02", "--crit-gb", "0.01", "--target-gb", "0.02", "--min-output-mb", "4"]
    return a + (["--current-session", sess] if sess else [])


def guard(P, *args, runs=None, sess=CUR, env=None):
    cmd = [PY, "-I", GUARD, *base_args(P, runs, sess), *args]
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=P["root"], env=env)
    el = time.time() - t
    try:
        rec = json.loads(r.stdout) if "--quiet" not in args else None
    except ValueError:
        rec = None
    return r.returncode, rec, r.stdout, r.stderr, el


def hook(P, *args, stdin_text="", env=None, sess=None):
    cmd = [PY, "-I", GUARD, "--hook", *base_args(P, None, sess), *args]
    r = subprocess.run(cmd, input=stdin_text, capture_output=True, text=True, encoding="utf-8", cwd=P["root"], env=env)
    return r.returncode, r.stdout, r.stderr


def wait_child_record(P, timeout=120):
    """hookが起動したdetached子processの実行記録(mode=apply, detached=True)を待つ。"""
    runs = os.path.join(P["root"], "runs")
    end = time.time() + timeout
    while time.time() < end:
        if os.path.isdir(runs):
            for fn in os.listdir(runs):
                if fn.endswith(".json") and "_hook" not in fn:
                    try:
                        with open(os.path.join(runs, fn), encoding="utf-8") as fh:
                            rec = json.load(fh)
                    except ValueError:
                        continue
                    if rec.get("mode") == "apply" and rec.get("detached"):
                        return rec
        time.sleep(1)
    return None


def add_junction(link, target):
    os.makedirs(target, exist_ok=True)
    r = subprocess.run(["cmd", "/c", "mklink", "/J", link, target], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"mklink failed: {r.stdout}{r.stderr}")
    JUNCTIONS.append(link)


def exists_all(paths):
    return all(os.path.exists(p) for p in paths)


def none_exist(paths):
    return not any(os.path.exists(p) for p in paths)


def onerror(fn, path, exc):
    try:
        os.chmod(path, stat.S_IWRITE)
        fn(path)
    except Exception:
        pass


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ev = None
    if "--evidence-dir" in sys.argv:
        ev = sys.argv[sys.argv.index("--evidence-dir") + 1]
        os.makedirs(ev, exist_ok=True)
    base = tempfile.mkdtemp(prefix="dgtest_")
    times = {}
    try:
        # ===== S0: 15GB(予防警戒) apply指定でも削除なし =====
        P = build(os.path.join(base, "s0"))
        rc, rec, out, err, el = guard(P, "--simulate-free-gb", "0.015", "--apply")
        check("S0 15GB: WARN(rc=1)・削除0", rc == 1 and rec and rec["state"] == "WARN" and not rec["deleted"], f"rc={rc}")
        check("S0 15GB: 原因候補を列挙", rec and len(rec["candidates"]) >= 3, f"cand={len(rec['candidates']) if rec else None}")
        check("S0 15GB: 全ファイル/worktree残存", exists_all(P["safe_outputs"] + P["prot"] + P["safe_wt"] + P["prot_wt"]))
        hold_recent = open(P["recent_big"], "rb")  # 書き手PID特定(Restart Manager)の確認用にhandle保持
        rc, rec, *_ = guard(P, "--simulate-free-gb", "0.025", "--apply", "--active-warn-mb", "2")
        hold_recent.close()
        wr = rec["active_big_outputs"][0].get("writers", []) if rec and rec["active_big_outputs"] else []
        check("S0b R-3c: ACTIVE_BIGの書き手PID(Restart Manager)が警告に含まれる(killはしない)",
              any(w.get("pid") == os.getpid() for w in wr), json.dumps(wr, ensure_ascii=False)[:200])
        check("S0b 25GB: OK(rc=0)・候補走査なし・削除0", rc == 0 and rec["state"] == "OK" and not rec["candidates"] and not rec["deleted"])
        check("S0b 25GB: 稼働中>5MB outputをACTIVE_BIG列挙", rec and len(rec["active_big_outputs"]) == 1 and
              rec["active_big_outputs"][0]["task_id"] == "recent_big", str(rec and rec["active_big_outputs"]))
        # ===== S6: 5GB dry-run: 削除なし・候補列挙のみ =====
        rc, rec, *_ = guard(P, "--simulate-free-gb", "0.005", "--dry-run")
        check("S6 5GB dry-run: 候補列挙・削除0・rc=2(未回復)", rec and rec["candidates"] and not rec["deleted"] and rc == 2 and
              exists_all(P["safe_outputs"] + P["safe_wt"] + P["prot"] + P["prot_wt"]))
        # ===== S1: 5GB apply (目標未達=2本12GB+5=17GB) =====
        hold = open(P["held_open"], "rb")  # handle保持
        procwt = subprocess.Popen([PY, "-c", "import time;time.sleep(300)", P["proc_wt"]], cwd=P["proc_wt"])  # worktreeにcwd保持+path付きcommand line
        time.sleep(1.5)
        rc, rec, out, err, el = guard(P, "--simulate-free-gb", "0.005", "--apply", "--active-warn-mb", "2")
        procwt.kill()
        procwt.wait()
        hold.close()
        if ev:
            with open(os.path.join(ev, "S1_run_record_sandbox.json"), "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
        times["S1_apply_full_scan_s"] = round(el, 2)
        check("S1 5GB apply: 自動整理が発動(deleted>0)", rec and len(rec["deleted"]) > 0, f"deleted={len(rec['deleted'])}")
        check("S1 安全な.output(古い巨大2+旧session小)のみ削除", none_exist(P["safe_outputs"]))
        check("S1 pip cacheがpurgeされた", not os.path.exists(P["pip_file"]))
        check("S1 安全worktree4件(detached/old commit/merged branch/pycacheのみ)削除", none_exist(P["safe_wt"]),
              str([os.path.exists(p) for p in P["safe_wt"]]))
        check("S1 保護対象(未commit/untracked/ignored/ahead/keep/locked/recent/scratchpad外/handle保持/SSOT名/repo配下/別project)全残存",
              exists_all(P["prot"] + P["prot_wt"]), str([os.path.basename(p) for p in P["prot"] + P["prot_wt"] if not os.path.exists(p)]))
        holds = {os.path.basename(h.get("path", "")): h["hold"] for h in rec["held"]}
        check("S1 保留理由が記録される(dirty/untracked/ahead/keep/locked/recent/handle)",
              all(k in holds for k in ["wt_dirty_tracked", "wt_untracked", "wt_ahead", "wt_keep", "wt_locked", "wt_recent", "held_open_big.output"]),
              json.dumps(holds, ensure_ascii=False))
        check("S1 M-3: 使用中worktree(Popenでcwd保持+path付きprocess)は保留・残存", os.path.exists(P["proc_wt"]) and
              str(holds.get("wt_procheld", "")).startswith("in_use_process"), str(holds.get("wt_procheld")))
        check("S1 M-3: 稼働中sessionのscratchpad内worktreeは対象外(parent_session_active)",
              str(holds.get("wt_active_session", "")).startswith("parent_session_active"), str(holds.get("wt_active_session")))
        check("S1 M-3: rename往復probe撤去(.dgprobe残骸なし・コード上もdir_in_use無し)",
              not [x for x in os.listdir(P["sp"]) if x.endswith(".dgprobe")] and "def dir_in_use" not in open(GUARD, encoding="utf-8").read())
        a1 = [d for d in rec["deleted"] if d.get("cls") == "A1"]
        check("S1 R-4: A1削除前に先頭・末尾の抜粋が保存される", a1 and all(os.path.exists(d.get("excerpt", "")) and
              "# path=" in open(d["excerpt"], "rb").read(200).decode("utf-8", "replace") for d in a1), str([d.get("excerpt") for d in a1])[:200])
        wdel = [d for d in rec["deleted"] if d["kind"] == "worktree"]
        check("S1 R-2: worktree削除記録にHEAD sha・branch・reflog", wdel and all(len(d["git"]["head"]) == 40 and d["git"]["branch"] and
              isinstance(d["git"]["reflog"], list) and d["git"]["reflog"] for d in wdel), str(wdel[0]["git"])[:200] if wdel else "none")
        check("S1 R-5: current_session引数が記録に残る", rec.get("current_session") == CUR)
        check("S1 整理後に再計測(before=5.0, after=before+freed)", abs(rec["free_bytes_before"] - 5 * U) < U / 100 and
              rec["free_bytes_after"] == rec["free_bytes_before"] + sum(d["bytes"] for d in rec["deleted"]) and
              rec["free_bytes_after"] > 16.9 * U, f"after_U={rec['free_bytes_after'] / U:.2f}")
        check("S1 目標20GB未達=WARN(rc=1)", rc == 1 and rec["state"] == "WARN")
        check("S1 実行記録json出力", rec.get("record") and os.path.exists(rec["record"]))
        check("S1 git worktree list にprotectedが残る(強制削除なし)", all(os.path.basename(p) in git(P["repo"], "worktree", "list") for p in P["prot_wt"]))
        # ===== S1b: 目標到達で停止(最小削除) =====
        P2 = build(os.path.join(base, "s1b"), n_big=3, held=False)
        rc, rec, *_ = guard(P2, "--simulate-free-gb", "0.005", "--apply")
        check("S1b 5U+18U>=20U で目標到達→rc=0、残りworktree/pip/旧session小は未処理(最小削除)",
              rc == 0 and rec["state"] == "OK" and exists_all(P2["safe_wt"]) and os.path.exists(P2["pip_file"]) and
              len(rec["deleted"]) == 3, f"rc={rc} deleted={len(rec['deleted'])}")
        # ===== S5: 回復不能 =====
        P3 = build(os.path.join(base, "s5"), n_big=0, held=False)
        rc, rec, *_ = guard(P3, "--simulate-free-gb", "0.005", "--apply")
        if ev:
            with open(os.path.join(ev, "S5_run_record_sandbox.json"), "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
        check("S5 回復不能(5GB→10GB未満): CRITICAL・rc=2・UNRECOVERED警告・記録あり",
              rc == 2 and rec["state"] == "CRITICAL" and any(w.startswith("UNRECOVERED") for w in rec["warnings"]) and
              rec.get("record") and os.path.exists(rec["record"]), f"rc={rc} after={rec['free_gb_after']}")
        check("S5 回復不能でも保護対象は無傷", exists_all(P3["prot"] + P3["prot_wt"]))
        rc, _, out, _, el = guard(P3, "--simulate-free-gb", "0.05", "--auto", "--quiet")
        times["quiet_ok_path_s"] = round(el, 2)
        check("quiet出力は1行", len(out.strip().splitlines()) == 1 and out.startswith("disk_guard: OK"), out.strip())
        # ===== S7: --dry-run は --auto/--apply より優先 =====
        P4 = build(os.path.join(base, "s7"), n_big=1, held=False)
        rc, rec, *_ = guard(P4, "--simulate-free-gb", "0.005", "--auto", "--dry-run")
        check("S7 --dry-run指定時は--autoでも削除0", rec["mode"] == "dry-run" and not rec["deleted"] and exists_all(P4["safe_outputs"]))
        # ===== S8: R-5 現session不明=全session稼働扱い(A2を行わない) =====
        P8 = build(os.path.join(base, "s8"), n_big=0, held=False)
        rc, rec, *_ = guard(P8, "--simulate-free-gb", "0.005", "--dry-run", sess=None)
        paths8 = {os.path.basename(i["path"]) for i in rec["candidates"] if i["kind"] == "output"}
        check("S8 R-5: current session不明ではA2(旧session小出力)を候補にしない", "old_session_small.output" not in paths8, str(paths8))
        rc, rec, *_ = guard(P8, "--simulate-free-gb", "0.005", "--dry-run")
        paths8 = {os.path.basename(i["path"]) for i in rec["candidates"] if i["kind"] == "output"}
        check("S8 R-5: current session既知ならA2候補になる", "old_session_small.output" in paths8, str(paths8))
        # ===== S9: R-3b 増加速度警告 =====
        P9 = build(os.path.join(base, "s9"), n_big=0, held=False)
        garg = ["--simulate-free-gb", "0.025", "--active-warn-mb", "100000", "--growth-track-mb", "1", "--growth-gb-per-10min", "0.001"]
        guard(P9, *garg)  # 1回目: 状態保存
        stp = os.path.join(P9["root"], "active_state.json")
        st = json.load(open(stp, encoding="utf-8"))
        st = {k: [v[0] - 600, 0] for k, v in st.items()}  # 10分前は0byteだった
        json.dump(st, open(stp, "w", encoding="utf-8"))
        rc, rec, *_ = guard(P9, *garg)
        ab = rec["active_big_outputs"]
        check("S9 R-3b: 増加速度>閾値のactive .outputをACTIVE_BIG(growing)警告", len(ab) == 1 and ab[0].get("growing") is True and
              any("growing=" in w for w in rec["warnings"]), json.dumps(ab, ensure_ascii=False)[:200])
        # ===== S10: R-1 junction拒否 =====
        P10 = build(os.path.join(base, "s10"), n_big=0, held=False)
        tgt = os.path.join(P10["root"], "junc_target")
        big = os.path.join(tgt, "tasks", "big_via_junction.output")
        sparse(big, 6 * U)
        age(big, 3)
        add_junction(os.path.join(P10["root"], "LocalAppData", "Temp", "claude", PROJ, "SESS_JUNCTION_01"), tgt)
        rc, rec, *_ = guard(P10, "--simulate-free-gb", "0.005", "--apply")
        check("S10 R-1: session dirがjunctionなら走査・削除しない(実体の.output無傷)+warning", os.path.exists(big) and
              any("session_dir_is_reparse_skipped" in w for w in rec["warnings"]), str(rec["warnings"])[:200])
        P10b = build(os.path.join(base, "s10b"), n_big=0, held=False)
        envbad = dict(os.environ, LOCALAPPDATA="relative_dir")
        cmd = [PY, "-I", GUARD, "--repo", P10b["repo"], "--dry-run"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=envbad, cwd=P10b["root"])
        check("S10b R-1: LOCALAPPDATA非絶対なら失敗終了(rc=3・黙って無効化しない)", r.returncode == 3 and "LOCALAPPDATA_not_absolute" in r.stderr, f"rc={r.returncode} {r.stderr[:120]}")
        shutil.rmtree(os.path.join(P10b["root"], "LocalAppData", "Temp", "claude", PROJ), onerror=onerror)
        rc, rec, *_ = guard(P10b, "--simulate-free-gb", "0.025")
        check("S10c R-1: project_dir無しはwarning(黙って空にしない)", any("project_dir_missing" in w for w in rec["warnings"]), str(rec["warnings"])[:160])
        # ===== S11: M-4 remove直前の再確認(TOCTOU) =====
        import disk_guard_01 as dg
        for label, mutate in (("untracked追加", lambda p: write(os.path.join(p, "late_evidence.txt"), "evidence")),
                              ("未push commit追加", lambda p: (write(os.path.join(p, "late.txt"), "l"), git(p, "add", "late.txt"), git(p, "commit", "-q", "-m", "late")))):
            P11 = build(os.path.join(base, "s11" + str(len(label))), n_big=0, held=False)
            victim = P11["safe_wt"][0]
            dg.BEFORE_REMOVE_HOOK = lambda p, m=mutate, v=victim: m(p) if os.path.normcase(p) == os.path.normcase(v) else None
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    dg.main([*base_args(P11), "--simulate-free-gb", "0.005", "--apply", "--skip-pip"])
            finally:
                dg.BEFORE_REMOVE_HOOK = None
            rec = json.loads(buf.getvalue())
            hv = [h for h in rec["held"] if h.get("path") == victim]
            check(f"S11 M-4: 候補確認後に{label}されたworktreeはremove直前の再確認で保留・残存",
                  os.path.exists(victim) and hv and hv[0]["hold"].startswith("recheck:") and victim not in [d.get("path") for d in rec["deleted"]],
                  str(hv[0]["hold"]) if hv else "no hold")
        # ===== S12: M-1/M-6 hookモード =====
        P12 = build(os.path.join(base, "s12"), n_big=2, held=False)
        rc, out, err = hook(P12, "--simulate-free-gb", "0.025")
        check("S12 hook 25GB: exit 0・stdout 1行(OK)・stderr同文", rc == 0 and len(out.strip().splitlines()) == 1 and out.startswith("disk_guard: OK") and out.strip() == err.strip(), out.strip()[:120])
        rc, out, err = hook(P12, "--simulate-free-gb", "0.015")
        check("S12 hook 15GB: exit 0(WARNでも)・1行・Fable即時報告文言・記録path", rc == 0 and len(out.strip().splitlines()) == 1 and out.startswith("disk_guard: WARN") and
              "Fableは即時報告すること" in out and "record=" in out and "record=-" not in out, out.strip()[:200])
        check("S12 hook WARN: 整理process起動なし・削除0", exists_all(P12["safe_outputs"] + P12["safe_wt"]))
        rc, out, err = hook(P12, "--simulate-free-gb", "0.005", "--active-warn-mb", "2", stdin_text=json.dumps({"session_id": CUR, "hook_event_name": "SessionStart"}))
        check("S12 hook 5GB: exit 0・1行(CRITICAL)・Fable/ユーザー即時報告文言・整理をdetached起動", rc == 0 and len(out.strip().splitlines()) == 1 and out.startswith("disk_guard: CRITICAL") and
              "Fableは即時報告すること" in out and "cleanup=started" in out, out.strip()[:240])
        crec = wait_child_record(P12)
        check("S12 M-6: 整理は別process(detached)で完走し削除記録が残る", crec is not None and len(crec["deleted"]) > 0, "no child record" if crec is None else f"deleted={len(crec['deleted'])}")
        check("S12 R-5: hook stdin JSONのsession_idが子processへ渡る", crec is not None and crec.get("current_session") == CUR, str(crec and crec.get("current_session")))
        time.sleep(1)
        check("S12 M-6: 単一実行lockが整理完了後に解放される", not os.path.exists(os.path.join(P12["root"], ".lock")))
        rc, out, err = hook(P12, "--simulate-free-gb", "0.005", stdin_text="not json at all")
        check("S12 hook 不正stdinでもexit 0・1行", rc == 0 and len(out.strip().splitlines()) == 1, out.strip()[:120])
        envbad = dict(os.environ, LOCALAPPDATA="relative_dir")
        cmd = [PY, "-I", GUARD, "--hook", "--repo", P12["repo"]]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=envbad, cwd=P12["root"])
        check("S12 hook 内部エラー(LOCALAPPDATA非絶対)でもexit 0・1行ERROR", r.returncode == 0 and r.stdout.startswith("disk_guard: ERROR") and len(r.stdout.strip().splitlines()) == 1, r.stdout.strip()[:140])
        r = subprocess.run([PY, "-I", GUARD, "--hook", "--no-such-option"], capture_output=True, text=True, encoding="utf-8")
        check("S12 hook 不正引数(argparse失敗)でもexit 0", r.returncode == 0, f"rc={r.returncode}")
        # ===== S13: lock多重実行skip / stale回収 =====
        P13 = build(os.path.join(base, "s13"), n_big=2, held=False)
        lockp = os.path.join(P13["root"], ".lock")
        write(lockp, "other")
        rc, _, out, _, _ = guard(P13, "--simulate-free-gb", "0.005", "--auto")
        check("S13 M-6: lock保持中(1時間以内)の多重実行はskip(rc=0・削除0・lock温存)", rc == 0 and "SKIPPED" in out and exists_all(P13["safe_outputs"]) and os.path.exists(lockp), out.strip()[:100])
        rc, out, err = hook(P13, "--simulate-free-gb", "0.005")
        check("S13 hook: lock保持中は整理を起動しない(cleanup=skipped)", rc == 0 and "cleanup=skipped" in out and exists_all(P13["safe_outputs"]), out.strip()[:200])
        age(lockp, 2)
        rc, rec, *_ = guard(P13, "--simulate-free-gb", "0.005", "--auto")
        check("S13 M-6: stale lock(2時間前)は回収して実行し、完了後lock解放", rec and rec["deleted"] and not os.path.exists(lockp), f"deleted={len(rec['deleted']) if rec else None}")
        # ===== S14: CRITICAL flag / rotation / quiet =====
        P14 = build(os.path.join(base, "s14"), n_big=0, held=False)
        rc, rec, *_ = guard(P14, "--simulate-free-gb", "0.005", "--apply")
        flag = os.path.join(P14["root"], "CRITICAL.flag")
        check("S14 R-4: 回復不能CRITICALでflag fileが作られる", rc == 2 and os.path.exists(flag))
        rc, out, err = hook(P14, "--simulate-free-gb", "0.05")
        check("S14 R-4: 次のhookで前回CRITICALを表示(Fable即時報告)し、flagは1回で消える", "PREV_CRITICAL=" in out and "Fableは即時報告すること" in out and not os.path.exists(flag), out.strip()[:200])
        rc, out, err = hook(P14, "--simulate-free-gb", "0.05")
        check("S14 R-4: 2回目のhookはOKのみ", out.startswith("disk_guard: OK") and "PREV_CRITICAL" not in out, out.strip()[:120])
        for i in range(55):  # runs rotation(保持50件)。同秒でも別fileになるようpid付き名のため、mtimeをずらす
            guard(P14, "--simulate-free-gb", "0.015", "--dry-run")
        nrec = len([x for x in os.listdir(os.path.join(P14["root"], "runs")) if x.endswith(".json")])
        check("S14 R-4: runs rotation(保持50件)", nrec <= 50, f"records={nrec}")
        rc, _, out, _, _ = guard(P14, "--simulate-free-gb", "0.015", "--dry-run", "--quiet")
        check("S14 R-4: quiet行に記録path", "record=" in out and "record=-" not in out, out.strip()[:160])
        for k in list(times):
            print(k, times[k])
    finally:
        for j in JUNCTIONS:
            try:
                os.rmdir(j)
            except OSError:
                pass
        shutil.rmtree(base, onerror=onerror)
    ok = all(r["pass"] for r in RESULTS)
    print("ALL PASS" if ok else "FAILURES", f"{sum(r['pass'] for r in RESULTS)}/{len(RESULTS)}")
    if ev:
        with open(os.path.join(ev, "test_results_02.json"), "w", encoding="utf-8") as f:
            json.dump({"scale": "1000x縮尺(1GB=U=GB//1000 bytes)。閾値warn/crit/target=20/10/20U、模擬空き5U等", "results": RESULTS, "times_s": times, "all_pass": ok}, f, ensure_ascii=False, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
