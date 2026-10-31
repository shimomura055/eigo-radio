"""disk_guard_01: Cドライブ容量監視+安全な自動整理(DISK-GUARD-AUTO-CLEANUP-01, OPEN-637)。API 0。

閾値: 空き<warn(20GB)=WARN(原因候補列挙のみ) / <crit(10GB)=--apply/--auto時に自動整理 / 回復目標=target(20GB)。
削除対象は許可リスト方式の3種のみ(他のpathは構造的に到達不能):
  (1) Claude task出力 <claude_base>/<project>/<session>/tasks/*.output
  (2) pip cache(venvのpipの `cache purge`、cache dirがLOCALAPPDATA/pip/Cache配下であること)
  (3) scratchpad直下のgit worktree(clean・pushed・merged・60分以上未更新・keep外・使用中でない)
安全条件が1つでも不成立/確認不能なら対象外(保留)。強制削除(--force)は使わない。
既定は--dry-run。--apply/--auto で削除。--simulate-free-gb / --root は検証用(実環境へ触れない)。
rc: 0=OK(空き>=warn) / 1=WARN(crit<=空き<warn) / 2=CRITICAL(空き<crit、回復不能) / 3=内部エラー
"""
import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time

GB = 1024 ** 3
MB = 1024 ** 2
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
DENY_TOKENS = ("current_spec", "decision_log", "open_items", "history_index", "pagefile", "hiberfil", "swapfile")


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


def dir_in_use(path):
    """同一親dir内のrename往復で、cwd/handle保持中のdirを検出。(使用中か, 往復失敗の異常文言)"""
    tmp = path.rstrip("\\/") + ".dgprobe"
    try:
        os.rename(path, tmp)
    except OSError:
        return True, None
    try:
        os.rename(tmp, path)
    except OSError as e:
        return True, f"PROBE_RESTORE_FAILED {tmp}: {e}"
    return False, None


def run(cmd, cwd=None, timeout=60):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout, r.stderr


class Ctx:
    pass


def build_ctx(a):
    c = Ctx()
    c.root = os.path.abspath(a.root) if a.root else None
    c.local = os.path.join(c.root, "LocalAppData") if c.root else os.environ.get("LOCALAPPDATA", "")
    c.claude_base = os.path.join(c.local, "Temp", "claude")
    c.project_dir = os.path.join(c.claude_base, a.project)
    c.runs_dir = a.runs_dir or os.path.join(c.local, "eigo-radio", "disk_guard", "runs")
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


# ---------- (1) task output ----------
def scan_outputs(c, now):
    """returns (candidates, held, active_big)。許可パターン: <project_dir>/<session>/tasks/<name>.output のみ。"""
    cands, held, active_big = [], [], []
    a = c.a
    try:
        sessions = [d for d in os.listdir(c.project_dir) if os.path.isdir(os.path.join(c.project_dir, d))]
    except OSError:
        return cands, held, active_big
    for s in sessions:
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
        session_active = (s == a.current_session) or recent
        for n, f, st in entries:
            if not n.endswith(".output"):
                continue
            age = now - st.st_mtime
            if age < a.min_age_min * 60:
                if st.st_size > a.active_warn_mb * MB:
                    active_big.append({"path": f, "task_id": n[:-7], "mb": round(st.st_size / MB, 1),
                                       "age_min": round(age / 60, 1)})
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
            if is_reparse(f) or not under(f, c.project_dir) or denied(f):
                why = "not_in_allowlist"
            elif file_in_use(f):
                why = "in_use_or_unconfirmable"
            if why:
                item["hold"] = why
                held.append(item)
            else:
                cands.append(item)
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


def check_worktree(c, w, now, main_norm):
    """安全条件を全て検証。戻り値=(ok, reason)。"""
    a = c.a
    p = w["worktree"].replace("/", os.sep)
    parent = os.path.dirname(p)
    grand = os.path.dirname(os.path.dirname(parent))
    # 許可パターン: <project_dir>/<session>/scratchpad/<name> のみ
    if os.path.basename(parent) != "scratchpad" or norm(grand) != norm(c.project_dir):
        return False, "not_in_scratchpad_allowlist"
    if norm(p) == main_norm or not os.path.isdir(p):
        return False, "main_or_missing"
    if is_reparse(p) or denied(p):
        return False, "reparse_or_denied"
    if "locked" in w or "prunable" in w or "bare" in w:
        return False, "locked_or_prunable"
    if norm(p) in keep_set(parent):
        return False, "keep_list"
    cw, me = norm(os.getcwd()), norm(os.path.abspath(__file__))
    if cw == norm(p) or cw.startswith(norm(p) + os.sep) or me.startswith(norm(p) + os.sep):
        return False, "self_or_cwd"
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
    if not a.apply and not a.auto:
        return True, "probe_pending_in_dry_run"  # dry-runは実rename probeをしない(実worktreeを触らない)
    in_use, err = dir_in_use(p)
    if err:
        return False, err
    if in_use:
        return False, "in_use_dir_probe"
    return True, ""


def scan_worktrees(c, now):
    cands, held = [], []
    rc, items = worktree_list(c)
    if rc != 0 or not items:
        return cands, [{"kind": "worktree", "hold": "worktree_list_failed"}]
    main_norm = norm(items[0]["worktree"])
    for w in items[1:]:
        p = w["worktree"].replace("/", os.sep)
        if not under(p, c.claude_base):
            continue  # 許可パターン外は列挙もしない(到達不能)
        ok, why = check_worktree(c, w, now, main_norm)
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


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="削除を実行(既定はdry-run)")
    ap.add_argument("--auto", action="store_true", help="--apply相当(起動経路用)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="出力1行(hook用)")
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
    ap.add_argument("--pip-cmd", default="", help="検証用: '|'区切りのpip起動コマンド")
    ap.add_argument("--skip-pip", action="store_true")
    ap.add_argument("--runs-dir")
    ap.add_argument("--now", type=float, help="検証用: 現在時刻(epoch)")
    a = ap.parse_args(argv)
    if a.dry_run:
        a.apply = False
        a.auto = False
    apply_ = a.apply or a.auto
    c = build_ctx(a)
    t0 = time.time()
    now = a.now or t0
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)), "mode": "apply" if apply_ else "dry-run",
           "simulated": a.simulate_free_gb is not None, "root": c.root,
           "thresholds_gb": {"warn": a.warn_gb, "crit": a.crit_gb, "target": a.target_gb},
           "candidates": [], "deleted": [], "held": [], "warnings": []}
    freed = 0
    free0 = free_bytes(c, 0)
    rec["free_gb_before"] = round(free0 / GB, 2)
    # 早期検知(常時・軽量): 稼働中(直近60分更新)の巨大.output。削除しない
    out_c, out_h, active_big = scan_outputs(c, now)
    rec["active_big_outputs"] = active_big
    for ab in active_big:
        rec["warnings"].append(f"ACTIVE_BIG_OUTPUT {ab['mb']}MB task={ab['task_id']} {ab['path']}")
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
                        if file_in_use(it["path"]) or is_reparse(it["path"]) or not under(it["path"], c.project_dir):
                            rec["held"].append(dict(rec_it, hold="recheck_failed"))
                            continue
                        os.remove(it["path"])
                    elif it["kind"] == "pip":
                        r, _, e = run(it["cmd"], timeout=300)
                        if r != 0:
                            rec["held"].append(dict(rec_it, hold=f"pip_purge_rc{r}:{e[:80]}"))
                            continue
                    else:
                        r, _, e = run(["git", "worktree", "remove", it["path"]], cwd=c.repo, timeout=300)
                        if r != 0:
                            rec["held"].append(dict(rec_it, hold=f"git_refused:{e.strip()[:120]}"))
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
    rec["state"], rec["rc"] = state, rc
    rec["elapsed_s"] = round(time.time() - t0, 2)
    try:  # 動作なし&OKのときは記録を書かない(ログ汚染回避)
        if state != "OK" or rec["deleted"] or rec["warnings"]:
            os.makedirs(c.runs_dir, exist_ok=True)
            rp = os.path.join(c.runs_dir, time.strftime("%Y%m%d_%H%M%S", time.localtime(t0)) + ".json")
            rec["record"] = rp
            with open(rp, "w", encoding="utf-8") as fh:
                json.dump(rec, fh, ensure_ascii=False, indent=1)
    except OSError as e:
        rec["warnings"].append(f"record_write_failed:{e}")
    if a.quiet:
        extra = f" deleted={len(rec['deleted'])}({freed / GB:.1f}GB)" if rec["deleted"] else ""
        extra += f" ACTIVE_BIG={len(active_big)}" if active_big else ""
        print(f"disk_guard: {state} free={free0 / GB:.1f}->{free1 / GB:.1f}GB{extra}")
    else:
        print(json.dumps(rec, ensure_ascii=False, indent=1))
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa
        print(f"disk_guard: ERROR {e}", file=sys.stderr)
        sys.exit(3)
