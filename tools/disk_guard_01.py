"""disk_guard_01: Cドライブ容量監視+安全な自動整理(DISK-GUARD-AUTO-CLEANUP-01, OPEN-637)。API 0。

閾値: 空き<warn(20GB)=WARN(原因候補列挙のみ) / <crit(10GB)=--apply/--auto時に自動整理 / 回復目標=target(20GB)。
削除対象は許可リスト方式の3種のみ(他のpathは構造的に到達不能):
  (1) Claude task出力 <claude_base>/<project>/<session>/tasks/*.output
  (2) pip cache(venvのpipの `cache purge`、cache dirがLOCALAPPDATA/pip/Cache配下であること)
  (3) scratchpad直下のgit worktree(clean・pushed・merged・60分以上未更新・keep外・locked外・
      親sessionが非稼働(tasks配下の最新mtimeが3時間以上前)・worktree pathを含むprocessなし)
安全条件が1つでも不成立/確認不能なら対象外(保留)。強制削除(--force)は使わない。
既定は--dry-run。--apply/--auto で削除。--simulate-free-gb / --root は検証用(実環境へ触れない)。
--hook: SessionStart hook用。常にexit 0・stdout 1行(+stderr同文)。<crit時の整理は別process(detached)へ委譲。
rc(通常): 0=OK(空き>=warn) / 1=WARN(crit<=空き<warn) / 2=CRITICAL(空き<crit、回復不能) / 3=内部エラー
"""
import argparse
import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

GB = 1024 ** 3
MB = 1024 ** 2
KB = 1024
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
DENY_TOKENS = ("current_spec", "decision_log", "open_items", "history_index", "pagefile", "hiberfil", "swapfile")
BEFORE_REMOVE_HOOK = None  # 検証専用seam(CLIからは到達不能。本番では常にNone)
RECORD_RE = re.compile(r"^\d{8}_\d{6}.*\.json$")
FABLE_MSG = "Fableは即時報告すること"
SID_RE = re.compile(r"^[A-Za-z0-9_-]{8,80}$")


def norm(p):
    return os.path.normcase(os.path.realpath(p))


def is_reparse(p):
    try:
        st = os.lstat(p)
    except OSError:
        return True
    return bool(getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT) or os.path.islink(p)


def under(child, parent):
    c, p = norm(child), norm(parent)
    return c.startswith(p.rstrip("\\/") + os.sep)


def denied(path):
    low = path.lower().replace("\\", "/")
    if any(t in low for t in DENY_TOKENS):
        return True
    return any(x.startswith("er0") and x.endswith("_output") for x in low.split("/"))


def denied_both(path):
    """生pathと実体path(realpath)の両方でdeny判定(junction経由の抜け道を塞ぐ)。"""
    return denied(path) or denied(norm(path))


def file_in_use(path):
    """Windows: dwShareMode=0 で開けなければ他processがhandle保持中。確認不能もTrue(=除外)。"""
    if os.name != "nt":
        return True
    k = ctypes.windll.kernel32
    k.CreateFileW.restype = ctypes.c_void_p
    k.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
                              ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    h = k.CreateFileW(path, 0x80000000, 0, None, 3, 0x80, None)  # GENERIC_READ, share=0, OPEN_EXISTING
    if h in (None, ctypes.c_void_p(-1).value):
        return True
    k.CloseHandle.argtypes = [ctypes.c_void_p]
    k.CloseHandle(h)
    return False


def rm_holders(path):
    """Restart Manager(RmGetList)でfileを開いているprocessを列挙。[(pid, app_name)]、確認不能=None。killはしない。"""
    if os.name != "nt":
        return None
    try:
        from ctypes import wintypes as wt

        class FILETIME(ctypes.Structure):
            _fields_ = [("dwLowDateTime", wt.DWORD), ("dwHighDateTime", wt.DWORD)]

        class RM_UNIQUE_PROCESS(ctypes.Structure):
            _fields_ = [("dwProcessId", wt.DWORD), ("ProcessStartTime", FILETIME)]

        class RM_PROCESS_INFO(ctypes.Structure):
            _fields_ = [("Process", RM_UNIQUE_PROCESS), ("strAppName", ctypes.c_wchar * 256),
                        ("strServiceShortName", ctypes.c_wchar * 64), ("ApplicationType", ctypes.c_int),
                        ("AppStatus", ctypes.c_ulong), ("TSSessionId", wt.DWORD), ("bRestartable", wt.BOOL)]

        rm = ctypes.WinDLL("rstrtmgr")
        sess = wt.DWORD(0)
        key = (ctypes.c_wchar * 33)()
        if rm.RmStartSession(ctypes.byref(sess), 0, key) != 0:
            return None
        try:
            files = (ctypes.c_wchar_p * 1)(path)
            if rm.RmRegisterResources(sess, 1, files, 0, None, 0, None) != 0:
                return None
            needed, have, reasons = wt.UINT(0), wt.UINT(0), wt.DWORD(0)
            r = rm.RmGetList(sess, ctypes.byref(needed), ctypes.byref(have), None, ctypes.byref(reasons))
            if r == 0 and needed.value == 0:
                return []
            if r != 234:  # ERROR_MORE_DATA
                return None
            n = needed.value + 4
            arr = (RM_PROCESS_INFO * n)()
            have = wt.UINT(n)
            r = rm.RmGetList(sess, ctypes.byref(needed), ctypes.byref(have), arr, ctypes.byref(reasons))
            if r != 0:
                return None
            return [(int(arr[i].Process.dwProcessId), arr[i].strAppName) for i in range(have.value)]
        finally:
            rm.RmEndSession(sess)
    except Exception:
        return None


def run(cmd, cwd=None, timeout=60):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout, r.stderr


def proc_cmdlines():
    """全processの[(pid, commandline, exe)](Win32_Process)。確認不能=None(=worktreeは保留)。"""
    ps = ("[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
          "Get-CimInstance Win32_Process | ForEach-Object { [pscustomobject]@{p=$_.ProcessId;c=$_.CommandLine;e=$_.ExecutablePath} }"
          " | ConvertTo-Json -Compress")
    try:
        rc, out, _ = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], timeout=60)
        if rc != 0 or not out.strip():
            return None
        d = json.loads(out)
        if isinstance(d, dict):
            d = [d]
        return [(int(x.get("p") or 0), x.get("c") or "", x.get("e") or "") for x in d]
    except Exception:
        return None


def procs_matching(procs, path):
    key = os.path.normcase(os.path.abspath(path)).replace("/", "\\").rstrip("\\")
    hit = []
    for pid, cmd, exe in procs:
        if pid == os.getpid():
            continue
        hay = (cmd + " " + exe).replace("/", "\\").lower()
        if key in hay:
            hit.append({"pid": pid, "cmdline": cmd[:300]})
    return hit


class Ctx:
    def warn(self, msg):
        self.warnings.append(msg)


def build_ctx(a):
    c = Ctx()
    c.warnings = []
    c.root = os.path.abspath(a.root) if a.root else None
    c.local = os.path.join(c.root, "LocalAppData") if c.root else os.environ.get("LOCALAPPDATA", "")
    if not os.path.isabs(c.local):
        raise RuntimeError(f"LOCALAPPDATA_not_absolute:{c.local!r}")
    c.claude_base = os.path.join(c.local, "Temp", "claude")
    c.project_dir = os.path.join(c.claude_base, a.project)
    c.runs_dir = a.runs_dir or os.path.join(c.local, "eigo-radio", "disk_guard", "runs")
    c.state_dir = os.path.dirname(c.runs_dir)
    c.lock_path = os.path.join(c.state_dir, ".lock")
    c.flag_path = os.path.join(c.state_dir, "CRITICAL.flag")
    c.active_state_path = os.path.join(c.state_dir, "active_state.json")
    c.pip_cache_root = os.path.join(c.local, "pip", "Cache")
    here = os.path.dirname(os.path.abspath(__file__))
    c.repo = a.repo or os.path.dirname(here)
    if not a.repo:
        rc, out, _ = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=here)
        if rc == 0 and out.strip():
            c.repo = os.path.dirname(out.strip().replace("/", os.sep))
    c.disk_path = c.root or "C:\\"
    c.a = a
    return c


def free_bytes(c, freed_total):
    if c.a.simulate_free_gb is not None:
        return int(c.a.simulate_free_gb * GB) + freed_total
    return shutil.disk_usage(c.disk_path).free


# ---------- 単一実行lock / 記録 ----------
def lock_fresh(c):
    try:
        return time.time() - os.path.getmtime(c.lock_path) < 3600
    except OSError:
        return False


def acquire_lock(c):
    """O_EXCLで作成。既存でmtimeが1時間以内=他実行中(False)。1時間超=stale回収。"""
    os.makedirs(c.state_dir, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(c.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"pid={os.getpid()} ts={time.time()}".encode())
            os.close(fd)
            return True
        except FileExistsError:
            if lock_fresh(c):
                return False
            try:
                os.remove(c.lock_path)
            except OSError:
                return False
        except OSError:
            return False
    return False


def release_lock(c):
    try:
        os.remove(c.lock_path)
    except OSError:
        pass


def rotate(dirpath, keep, pattern=None):
    """自分の記録dirの古いfileを保持件数まで整理(削除対象3種とは別の自己管理)。"""
    try:
        fs = [os.path.join(dirpath, x) for x in os.listdir(dirpath) if (pattern is None or pattern.match(x))]
        fs = [f for f in fs if os.path.isfile(f)]
        fs.sort(key=os.path.getmtime, reverse=True)
        for f in fs[keep:]:
            os.remove(f)
    except OSError:
        pass


def write_record(c, rec, t0, tag=""):
    os.makedirs(c.runs_dir, exist_ok=True)
    rp = os.path.join(c.runs_dir, time.strftime("%Y%m%d_%H%M%S", time.localtime(t0)) + f"_{os.getpid()}{tag}.json")
    rec["record"] = rp
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
    rotate(c.runs_dir, 50, RECORD_RE)
    return rp


def save_excerpt(c, path, t0):
    """A1(巨大.output)削除前に先頭・末尾各64KBを保存。保存先path。失敗時は例外。"""
    d = os.path.join(c.runs_dir, "excerpts")
    os.makedirs(d, exist_ok=True)
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        head = fh.read(64 * KB)
        tail = b""
        if size > 64 * KB:
            fh.seek(max(64 * KB, size - 64 * KB))
            tail = fh.read(64 * KB)
    out = os.path.join(d, time.strftime("%Y%m%d_%H%M%S", time.localtime(t0)) + "_" + os.path.basename(path) + ".txt")
    with open(out, "wb") as fh:
        fh.write(f"# path={path}\n# size={size}\n# ---- HEAD 64KB ----\n".encode("utf-8"))
        fh.write(head)
        fh.write(b"\n# ---- TAIL 64KB ----\n")
        fh.write(tail)
    rotate(d, 100)
    return out


# ---------- active .output の増加速度(早期検知)・書き手 ----------
def load_active_state(c):
    try:
        with open(c.active_state_path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_active_state(c, st):
    try:
        os.makedirs(c.state_dir, exist_ok=True)
        with open(c.active_state_path, "w", encoding="utf-8") as fh:
            json.dump(st, fh)
    except OSError:
        pass


def attach_writers(active_big, limit=3):
    """ACTIVE_BIGの書き手候補(RmGetList)+command line(Win32_Process)を付与。killはしない。"""
    items = [i for i in active_big if not is_reparse(i["path"])][:limit]
    if not items:
        return
    procs = None
    for it in items:
        h = rm_holders(it["path"])
        if h is None:
            it["writers"] = [{"unconfirmable": True}]
            continue
        if h and procs is None:
            procs = proc_cmdlines() or []
        cm = {p: cmd for p, cmd, _ in (procs or [])}
        it["writers"] = [{"pid": pid, "app": name, "cmdline": cm.get(pid, "")[:300]} for pid, name in h]


# ---------- (1) task output ----------
def sessions_of(c):
    try:
        names = os.listdir(c.project_dir)
    except OSError:
        c.warn(f"project_dir_missing_or_unreadable:{c.project_dir}")
        return []
    if is_reparse(c.project_dir):
        c.warn(f"project_dir_is_reparse_refused:{c.project_dir}")
        return []
    out = []
    for d in names:
        sd = os.path.join(c.project_dir, d)
        if not os.path.isdir(sd):
            continue
        if is_reparse(sd):
            c.warn(f"session_dir_is_reparse_skipped:{sd}")
            continue
        out.append(d)
    return out


def tasks_newest_mtime(tdir, limit=20000):
    newest, n = 0.0, 0
    try:
        newest = os.lstat(tdir).st_mtime
        for dp, dn, fs in os.walk(tdir):
            for x in fs + dn:
                n += 1
                if n > limit:
                    return None
                try:
                    newest = max(newest, os.lstat(os.path.join(dp, x)).st_mtime)
                except OSError:
                    pass
    except OSError:
        return None
    return newest


def session_is_active(c, session_dir, now):
    """親sessionが稼働中か。(稼働中か, 理由)。確認不能は稼働中扱い(安全側)。"""
    a = c.a
    s = os.path.basename(session_dir)
    if a.current_session and s == a.current_session:
        return True, "current_session"
    tdir = os.path.join(session_dir, "tasks")
    if not os.path.isdir(tdir):
        return True, "tasks_dir_missing_unconfirmable"
    nm = tasks_newest_mtime(tdir)
    if nm is None:
        return True, "tasks_mtime_unconfirmable"
    if now - nm < a.session_idle_hours * 3600:
        return True, f"session_active_{(now - nm) / 60:.0f}min_ago"
    return False, ""


def scan_outputs(c, now, light=False):
    """returns (candidates, held, active_big)。許可パターン: <project_dir>/<session>/tasks/<name>.output のみ。
    light=True(hook用): 候補/handle確認をせずactive_bigのみ(lstatのみ・高速)。"""
    cands, held, active_big = [], [], []
    a = c.a
    prev = load_active_state(c)
    newstate = {}
    for s in sessions_of(c):
        tdir = os.path.join(c.project_dir, s, "tasks")
        if not os.path.isdir(tdir):
            continue
        entries = []
        for n in os.listdir(tdir):
            f = os.path.join(tdir, n)
            try:
                entries.append((n, f, os.lstat(f)))
            except OSError:
                continue
        recent = any(now - st.st_mtime < a.min_age_min * 60 for _, _, st in entries)
        # 現session不明(hook stdin/環境変数に無い)=全session稼働扱い(A2を行わない安全側)
        session_active = (not a.current_session) or (s == a.current_session) or recent
        for n, f, st in entries:
            if not n.endswith(".output"):
                continue
            age = now - st.st_mtime
            growth = None
            if st.st_size >= a.growth_track_mb * MB:
                newstate[f] = [now, st.st_size]
                p0 = prev.get(f)
                if p0 and 60 <= now - p0[0] <= 6 * 3600 and st.st_size > p0[1]:
                    growth = (st.st_size - p0[1]) / (now - p0[0]) * 600 / GB
            if age < a.min_age_min * 60:
                big = st.st_size > a.active_warn_mb * MB
                grow = growth is not None and growth > a.growth_gb_per_10min
                if big or grow:
                    it = {"path": f, "task_id": n[:-7], "mb": round(st.st_size / MB, 1), "age_min": round(age / 60, 1)}
                    if growth is not None:
                        it["growth_gb_per_10min"] = round(growth, 3)
                        it["growing"] = grow
                    active_big.append(it)
                continue
            if light:
                continue
            cls = None
            if st.st_size > a.min_output_mb * MB:
                cls = "A1"
            elif not session_active and age > 86400:
                cls = "A2"
            if not cls:
                continue
            item = {"kind": "output", "cls": cls, "path": f, "bytes": st.st_size, "session": s}
            why = None
            if is_reparse(f) or not under(f, c.project_dir) or denied_both(f):
                why = "not_in_allowlist"
            elif file_in_use(f):
                why = "in_use_or_unconfirmable"
            if why:
                item["hold"] = why
                held.append(item)
            else:
                cands.append(item)
    save_active_state(c, newstate)
    cands.sort(key=lambda i: -i["bytes"])
    return cands, held, active_big


# ---------- (2) pip cache ----------
def pip_candidate(c):
    a = c.a
    if a.pip_cmd:
        cmd = a.pip_cmd.split("|")
    else:
        py = os.path.join(c.repo, ".venv", "Scripts", "python.exe")
        if not os.path.exists(py):
            return None, {"kind": "pip", "hold": "venv_python_missing"}
        cmd = [py, "-m", "pip"]
    try:
        rc, out, _ = run(cmd + ["cache", "dir"], timeout=30)
    except Exception as e:
        return None, {"kind": "pip", "hold": f"pip_error:{e}"}
    d = out.strip().splitlines()[-1].strip() if rc == 0 and out.strip() else ""
    if not d or not os.path.isdir(d) or is_reparse(d) or not (norm(d) == norm(c.pip_cache_root) or under(d, c.pip_cache_root)):
        return None, {"kind": "pip", "hold": f"cache_dir_not_allowed:{d}"}
    total = 0
    for dp, _, fs in os.walk(d):
        for fn in fs:
            try:
                total += os.path.getsize(os.path.join(dp, fn))
            except OSError:
                pass
    return {"kind": "pip", "path": d, "bytes": total, "cmd": cmd + ["cache", "purge"]}, None


# ---------- (3) worktree ----------
def newest_mtime(path, gitadmin, limit=20000):
    """git管理dir(index/HEAD/logs=git操作の痕跡)全体+worktree直下エントリのmtime最大。
    作業ツリー全走査はしない(未commit変更はgit status、作業中は直近git操作/直下更新で検出)。"""
    newest, n = 0.0, 0
    try:
        newest = max(newest, os.lstat(path).st_mtime)
        for x in os.listdir(path):
            n += 1
            newest = max(newest, os.lstat(os.path.join(path, x)).st_mtime)
    except OSError:
        return None
    if not gitadmin or not os.path.isdir(gitadmin):
        return None
    for dp, dn, fs in os.walk(gitadmin):
        for x in fs + dn:
            n += 1
            if n > limit:
                return None
            try:
                newest = max(newest, os.lstat(os.path.join(dp, x)).st_mtime)
            except OSError:
                pass
    return newest


def keep_set(scratch):
    ks = set()
    try:
        with open(os.path.join(scratch, ".disk_guard_keep"), encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    ks.add(norm(ln if os.path.isabs(ln) else os.path.join(scratch, ln)))
    except OSError:
        pass
    return ks


def worktree_list(c):
    rc, out, _ = run(["git", "worktree", "list", "--porcelain"], cwd=c.repo)
    items, cur = [], {}
    for ln in out.splitlines() + [""]:
        if not ln.strip():
            if cur:
                items.append(cur)
            cur = {}
        elif " " in ln:
            k, v = ln.split(" ", 1)
            cur[k] = v
        else:
            cur[ln] = True
    return rc, items


def check_worktree(c, w, now, main_norm, procs):
    """安全条件を全て検証(判定のみ・worktreeへ副作用なし)。戻り値=(ok, reason)。procs=None=process一覧確認不能=保留。"""
    a = c.a
    p = w["worktree"].replace("/", os.sep)
    parent = os.path.dirname(p)
    sdir = os.path.dirname(parent)
    grand = os.path.dirname(sdir)
    # 許可パターン: <project_dir>/<session>/scratchpad/<name> のみ
    if os.path.basename(parent) != "scratchpad" or norm(grand) != norm(c.project_dir):
        return False, "not_in_scratchpad_allowlist"
    if norm(p) == main_norm or not os.path.isdir(p):
        return False, "main_or_missing"
    if is_reparse(p) or is_reparse(parent) or is_reparse(sdir) or denied_both(p):
        return False, "reparse_or_denied"
    if "locked" in w or "prunable" in w or "bare" in w:
        return False, "locked_or_prunable"
    if norm(p) in keep_set(parent):
        return False, "keep_list"
    active, why = session_is_active(c, sdir, now)
    if active:
        return False, f"parent_session_active:{why}"
    cw, me = norm(os.getcwd()), norm(os.path.abspath(__file__))
    if cw == norm(p) or cw.startswith(norm(p) + os.sep) or me.startswith(norm(p) + os.sep):
        return False, "self_or_cwd"
    if procs is None:
        return False, "process_list_unconfirmable"
    hit = procs_matching(procs, p)
    if hit:
        return False, "in_use_process:" + ",".join(str(h["pid"]) for h in hit[:5])
    rc, gd, _ = run(["git", "rev-parse", "--path-format=absolute", "--git-dir"], cwd=p)
    gitadmin = gd.strip() if rc == 0 else None
    if not gitadmin:
        return False, "gitdir_unknown"
    for st in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "BISECT_LOG"):
        if os.path.exists(os.path.join(gitadmin, st)):
            return False, f"git_op_in_progress:{st}"
    rc, ahead, _ = run(["git", "rev-list", "--count", "origin/main..HEAD"], cwd=p)
    if rc != 0 or ahead.strip() != "0":
        return False, f"ahead_or_unknown:{ahead.strip()}"
    rc, _, _ = run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], cwd=p)
    if rc != 0:
        return False, "not_merged_to_origin_main"
    nm = newest_mtime(p, gitadmin)
    if nm is None:
        return False, "too_many_files_unconfirmable"
    if now - nm < a.min_age_min * 60:
        return False, f"recent_update_{(now - nm) / 60:.0f}min"
    rc, st_out, _ = run(["git", "status", "--porcelain", "--ignored", "--no-renames"], cwd=p, timeout=120)
    if rc != 0:
        return False, "status_failed"
    for ln in st_out.splitlines():
        path_ = ln[3:].replace("\\", "/")
        if ln.startswith("!!") and ("__pycache__/" in path_ or path_.endswith(".pyc")):
            continue
        return False, f"dirty_or_untracked_or_ignored:{ln[:60]}"
    return True, ""


def scan_worktrees(c, now):
    cands, held = [], []
    rc, items = worktree_list(c)
    if rc != 0 or not items:
        return cands, [{"kind": "worktree", "hold": "worktree_list_failed"}]
    main_norm = norm(items[0]["worktree"])
    targets = [w for w in items[1:] if under(w["worktree"].replace("/", os.sep), c.claude_base)]
    procs = proc_cmdlines() if targets else []  # 許可パターン外は列挙もしない(到達不能)
    for w in targets:
        p = w["worktree"].replace("/", os.sep)
        ok, why = check_worktree(c, w, now, main_norm, procs)
        it = {"kind": "worktree", "path": p, "bytes": 0}
        if ok:
            tot = 0
            for dp, _, fs in os.walk(p):
                for fn in fs:
                    try:
                        tot += os.path.getsize(os.path.join(dp, fn))
                    except OSError:
                        pass
            it["bytes"] = tot
            cands.append(it)
        else:
            it["hold"] = why
            held.append(it)
    cands.sort(key=lambda i: -i["bytes"])
    return cands, held


def git_info(p):
    """削除記録用: HEAD sha・branch・reflog(直近20件)。"""
    info = {}
    _, o, _ = run(["git", "rev-parse", "HEAD"], cwd=p)
    info["head"] = o.strip()
    _, o, _ = run(["git", "symbolic-ref", "-q", "--short", "HEAD"], cwd=p)
    info["branch"] = o.strip() or "(detached)"
    _, o, _ = run(["git", "reflog", "-n", "20", "--format=%h %gd %gs"], cwd=p)
    info["reflog"] = o.strip().splitlines()[:20]
    return info


def remove_worktree(c, it):
    """remove直前に全安全条件(ahead/status --ignored/使用中判定=lock・keep・session・process)を再確認(TOCTOU対策)。
    戻り値=(removed, hold_reason, git_info)。"""
    p = it["path"]
    if BEFORE_REMOVE_HOOK:
        BEFORE_REMOVE_HOOK(p)
    rc, items = worktree_list(c)
    if rc != 0 or not items:
        return False, "recheck_worktree_list_failed", None
    main_norm = norm(items[0]["worktree"])
    w = next((x for x in items[1:] if norm(x["worktree"].replace("/", os.sep)) == norm(p)), None)
    if w is None:
        return False, "recheck_vanished", None
    ok, why = check_worktree(c, w, c.a.now or time.time(), main_norm, proc_cmdlines())
    if not ok:
        return False, f"recheck:{why}", None
    info = git_info(p)
    r, _, e = run(["git", "worktree", "remove", p], cwd=c.repo, timeout=300)
    if r != 0:
        return False, f"git_refused:{e.strip()[:120]}", info
    return True, "", info


# ---------- hook ----------
def read_stdin_session(timeout=1.5):
    """hook stdin JSONのsession_id。無ければ''。stdinがtty/None/無応答でも固まらない。"""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return ""
    except Exception:
        return ""
    box = []

    def rd():
        try:
            box.append(sys.stdin.read())
        except Exception:
            pass

    t = threading.Thread(target=rd, daemon=True)
    t.start()
    t.join(timeout)
    if not box:
        return ""
    try:
        sid = str(json.loads(box[0]).get("session_id") or "")
    except Exception:
        return ""
    return sid if SID_RE.match(sid) else ""


def hook_main(a, raw_argv):
    """SessionStart hook。常にrc=0・1行出力。重い整理は別process(detached)。"""
    t0 = time.time()
    sid = read_stdin_session() or os.environ.get("DISK_GUARD_CURRENT_SESSION", "") or os.environ.get("CLAUDE_SESSION_ID", "")
    if sid and not a.current_session:
        a.current_session = sid
    c = build_ctx(a)
    now = a.now or t0
    free0 = free_bytes(c, 0)
    _, _, active_big = scan_outputs(c, now, light=True)
    attach_writers(active_big)
    if free0 < a.crit_gb * GB:
        state = "CRITICAL"
    elif free0 < a.warn_gb * GB:
        state = "WARN"
    elif active_big:
        state = "ACTIVE_BIG"
    else:
        state = "OK"
    spawned = None
    if free0 < a.crit_gb * GB and not a.dry_run:
        if lock_fresh(c):
            spawned = "skipped(別の整理が実行中)"
        else:
            args = [x for x in raw_argv if x not in ("--hook", "--dry-run", "--quiet", "--auto", "--apply", "--detached")]
            if a.current_session and "--current-session" not in args:
                args += ["--current-session", a.current_session]
            cmd = [sys.executable, os.path.abspath(__file__)] + args + ["--auto", "--detached", "--quiet"]
            flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            try:
                subprocess.Popen(cmd, creationflags=flags, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, close_fds=True)
                spawned = "started(別process)"
            except Exception as e:
                spawned = f"spawn_failed:{e}"
    prev = ""
    try:
        if os.path.exists(c.flag_path):
            with open(c.flag_path, encoding="utf-8") as fh:
                prev = fh.read().strip().replace("\n", " ")[:300]
            os.remove(c.flag_path)  # 1回表示で消す
    except OSError:
        pass
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)), "mode": "hook", "state": state,
           "free_gb": round(free0 / GB, 2), "current_session": a.current_session, "active_big_outputs": active_big,
           "cleanup": spawned, "prev_critical": prev, "warnings": list(c.warnings)}
    rp = "-"
    if state != "OK" or prev or c.warnings:
        try:
            rp = write_record(c, rec, t0, "_hook")
        except OSError as e:
            rp = f"record_write_failed:{e}"
    parts = [f"disk_guard: {state}", f"free={free0 / GB:.1f}GB", f"record={rp}"]
    if active_big:
        top = max(active_big, key=lambda i: i["mb"])
        w = ""
        wr = top.get("writers") or []
        if wr and "pid" in wr[0]:
            w = " writer=" + ";".join(f"{x['pid']}:{x['app']}:{x['cmdline'][:80]}" for x in wr[:2])
        parts.append(f"ACTIVE_BIG={len(active_big)}(top {top['mb']}MB task={top['task_id']}"
                     + (f" growing {top['growth_gb_per_10min']}GB/10min" if top.get("growing") else "") + f"{w})")
    if spawned:
        parts.append(f"cleanup={spawned}")
    if prev:
        parts.append(f"PREV_CRITICAL={prev}")
    if state != "OK" or prev:
        parts.append(FABLE_MSG + ("(CRITICALはユーザーへも即時報告)" if state == "CRITICAL" or prev else ""))
    return " ".join(parts).replace("\r", " ").replace("\n", " ")


def main(argv=None):
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="削除を実行(既定はdry-run)")
    ap.add_argument("--auto", action="store_true", help="--apply相当(起動経路用)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="出力1行")
    ap.add_argument("--hook", action="store_true", help="SessionStart hook用: 常にexit 0・1行・整理は別process")
    ap.add_argument("--detached", action="store_true", help="hookから別processで起動された印(記録のみ)")
    ap.add_argument("--simulate-free-gb", type=float)
    ap.add_argument("--root", help="検証用sandbox。LOCALAPPDATA相当を<root>/LocalAppDataに差替え")
    ap.add_argument("--repo")
    ap.add_argument("--project", default="C--Users-tensh-eigo-radio")
    ap.add_argument("--current-session", default=os.environ.get("DISK_GUARD_CURRENT_SESSION", ""))
    ap.add_argument("--warn-gb", type=float, default=20.0)
    ap.add_argument("--crit-gb", type=float, default=10.0)
    ap.add_argument("--target-gb", type=float, default=20.0)
    ap.add_argument("--min-age-min", type=float, default=60.0)
    ap.add_argument("--min-output-mb", type=float, default=200.0)
    ap.add_argument("--active-warn-mb", type=float, default=1024.0)
    ap.add_argument("--session-idle-hours", type=float, default=3.0, help="親sessionの非稼働判定(tasks配下最新mtime)")
    ap.add_argument("--growth-gb-per-10min", type=float, default=1.0)
    ap.add_argument("--growth-track-mb", type=float, default=50.0)
    ap.add_argument("--pip-cmd", default="", help="検証用: '|'区切りのpip起動コマンド")
    ap.add_argument("--skip-pip", action="store_true")
    ap.add_argument("--runs-dir")
    ap.add_argument("--now", type=float, help="検証用: 現在時刻(epoch)")
    a = ap.parse_args(raw_argv)
    if a.hook:
        try:
            line = hook_main(a, raw_argv)
        except BaseException as e:  # hookは何があってもexit 0
            line = f"disk_guard: ERROR {type(e).__name__}: {e} (整理・監視は未実行。{FABLE_MSG})".replace("\n", " ")
        print(line)
        print(line, file=sys.stderr)
        return 0
    if a.dry_run:
        a.apply = False
        a.auto = False
    apply_ = a.apply or a.auto
    c = build_ctx(a)
    t0 = time.time()
    now = a.now or t0
    if apply_ and not acquire_lock(c):
        print(f"disk_guard: SKIPPED 別の整理が実行中(lock={c.lock_path})")
        return 0
    try:
        return run_main(a, c, apply_, t0, now)
    finally:
        if apply_:
            release_lock(c)


def run_main(a, c, apply_, t0, now):
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)), "mode": "apply" if apply_ else "dry-run",
           "simulated": a.simulate_free_gb is not None, "root": c.root, "detached": a.detached,
           "current_session": a.current_session,
           "thresholds_gb": {"warn": a.warn_gb, "crit": a.crit_gb, "target": a.target_gb},
           "candidates": [], "deleted": [], "held": [], "warnings": []}
    freed = 0
    free0 = free_bytes(c, 0)
    rec["free_gb_before"] = round(free0 / GB, 2)
    # 早期検知(常時・軽量): 稼働中(直近60分更新)の巨大/急増.output。削除しない
    out_c, out_h, active_big = scan_outputs(c, now)
    attach_writers(active_big)
    rec["active_big_outputs"] = active_big
    for ab in active_big:
        wr = ";".join(f"{x.get('pid')}:{x.get('app')}" for x in ab.get("writers", []) if "pid" in x)
        rec["warnings"].append(f"ACTIVE_BIG_OUTPUT {ab['mb']}MB task={ab['task_id']}"
                               + (f" growing={ab.get('growth_gb_per_10min')}GB/10min" if ab.get("growing") else "")
                               + (f" writers={wr}" if wr else "") + f" {ab['path']}")
    if free0 < a.warn_gb * GB:
        cands = list(out_c)
        rec["held"] += out_h
        if not a.skip_pip:
            pc, ph = pip_candidate(c)
            if pc:
                cands.append(pc)
            if ph:
                rec["held"].append(ph)
        wc, wh = scan_worktrees(c, now)
        cands += wc
        rec["held"] += wh
        rec["candidates"] = [{k: v for k, v in i.items() if k != "cmd"} for i in cands]
        rec["warnings"].append(f"LOW_DISK free={free0 / GB:.2f}GB < warn {a.warn_gb}GB; candidates={len(cands)}"
                               f" ({sum(i['bytes'] for i in cands) / GB:.2f}GB)")
        if free0 < a.crit_gb * GB and apply_:
            order = {"output": 0, "pip": 1, "worktree": 2}
            cands.sort(key=lambda i: (order[i["kind"]], -i["bytes"]))
            for it in cands:
                if free_bytes(c, freed) >= a.target_gb * GB:
                    break
                rec_it = {k: v for k, v in it.items() if k != "cmd"}
                try:
                    if it["kind"] == "output":
                        if file_in_use(it["path"]) or is_reparse(it["path"]) or not under(it["path"], c.project_dir) \
                                or denied_both(it["path"]):
                            rec["held"].append(dict(rec_it, hold="recheck_failed"))
                            continue
                        if it.get("cls") == "A1":
                            try:
                                rec_it["excerpt"] = save_excerpt(c, it["path"], t0)
                            except Exception as e:
                                rec["held"].append(dict(rec_it, hold=f"excerpt_failed:{e}"))
                                continue
                        os.remove(it["path"])
                    elif it["kind"] == "pip":
                        r, _, e = run(it["cmd"], timeout=300)
                        if r != 0:
                            rec["held"].append(dict(rec_it, hold=f"pip_purge_rc{r}:{e[:80]}"))
                            continue
                    else:
                        removed, why, info = remove_worktree(c, it)
                        if info:
                            rec_it["git"] = info
                        if not removed:
                            rec["held"].append(dict(rec_it, hold=why))
                            continue
                    freed += it["bytes"]
                    rec["deleted"].append(rec_it)
                except Exception as e:
                    rec["held"].append(dict(rec_it, hold=f"error:{e}"))
        elif free0 < a.crit_gb * GB:
            rec["warnings"].append("CRITICAL but dry-run: 削除は実行していない")
    free1 = free_bytes(c, freed)
    rec["free_bytes_before"], rec["free_bytes_after"] = free0, free1
    rec["free_gb_after"] = round(free1 / GB, 2)
    rec["freed_gb"] = round(freed / GB, 3)
    if free1 >= a.warn_gb * GB:
        rc, state = 0, "OK"
    elif free1 >= a.crit_gb * GB:
        rc, state = 1, "WARN"
    else:
        rc, state = 2, "CRITICAL"
    if state == "CRITICAL":
        rec["warnings"].append(f"UNRECOVERED free={free1 / GB:.2f}GB < crit {a.crit_gb}GB: 追加対応要(原因調査・報告)")
    rec["warnings"] += c.warnings
    rec["state"], rec["rc"] = state, rc
    rec["elapsed_s"] = round(time.time() - t0, 2)
    rp = "-"
    try:  # 動作なし&OKのときは記録を書かない(ログ汚染回避)
        if state != "OK" or rec["deleted"] or rec["warnings"]:
            rp = write_record(c, rec, t0)
        if state == "CRITICAL" and (a.simulate_free_gb is None or c.root):  # 次のhookで1回表示(R-4)。実環境の模擬実行では作らない
            with open(c.flag_path, "w", encoding="utf-8") as fh:
                fh.write(f"{rec['ts']} CRITICAL free={free1 / GB:.2f}GB record={rp}")
    except OSError as e:
        rec["warnings"].append(f"record_write_failed:{e}")
    try:  # 生存確認(schtasksが回っているかの証跡)。OK時もこの小fileだけ更新
        os.makedirs(c.state_dir, exist_ok=True)
        with open(os.path.join(c.state_dir, "last_run.json"), "w", encoding="utf-8") as fh:
            json.dump({"ts": rec["ts"], "mode": rec["mode"], "state": state, "free_gb": round(free1 / GB, 2),
                       "detached": a.detached, "record": rp}, fh, ensure_ascii=False)
    except OSError:
        pass
    if a.quiet:
        extra = f" deleted={len(rec['deleted'])}({freed / GB:.1f}GB)" if rec["deleted"] else ""
        extra += f" ACTIVE_BIG={len(active_big)}" if active_big else ""
        print(f"disk_guard: {state} free={free0 / GB:.1f}->{free1 / GB:.1f}GB{extra} record={rp}")
    else:
        print(json.dumps(rec, ensure_ascii=False, indent=1))
    return rc


if __name__ == "__main__":
    _hook = "--hook" in sys.argv[1:]
    try:
        _rc = main()
    except SystemExit as e:  # argparse等
        _rc = e.code if isinstance(e.code, int) else 3
    except BaseException as e:  # noqa
        print(f"disk_guard: ERROR {e}", file=sys.stderr)
        _rc = 3
    if _hook:  # stdin読取threadが残っていても確実に終了する
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
        os._exit(0)
    sys.exit(_rc)
