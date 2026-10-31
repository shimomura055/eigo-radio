"""PLAYWRIGHT-AUDIO-SAFETY-01: Playwright自動テストの安全ラッパ(音声・孤児プロセス・無期限実行の防止)。API 0。

使い方(既存scriptの差し替えは1行): `from playwright.sync_api import sync_playwright` を
  `from playwright_safe_01 import sync_playwright`(tools/ をsys.pathへ)に置き換える。以降の `with sync_playwright() as p:` は
  そのまま動き、次が自動で効く。
  (a) 音声: [2026-10-31実測] Playwright headless Chromiumは既定で--mute-audioを持つ=無音。実際に音が出るのは **Playwright WebKit**(mute引数が無く、
      JSのplay()でWindows既定デバイスへ実出力する。ROOT_CAUSE_01.md)。よって WebKit/Firefoxにも効くinit scriptが本体。
      既定=headless強制 + `--mute-audio`(Chromium。Playwright既定と二重化) + 全ページにinit script(HTMLMediaElement.play時に muted=true/volume=0 を強制。
      muted解除・volume上げも無効化。WebKit/WebAudioにも効く)。`play()`自体は動くので currentTime/timeupdate 依存の既存testは維持される(無音)。
      `block_play=True`(または env PW_SAFE_BLOCK_PLAY=1)で play() を完全no-op化(音声不要の静的UI testはこちら)。
      実音声が必要なtestだけ `allow_audio=True`(+ env PW_SAFE_ALLOW_AUDIO=1 の両方)で解除(警告ログを出す)。
  (b) 終了保証: try/finally + atexit + signal(SIGINT/SIGTERM/SIGBREAK)で browser/context を閉じ、Playwright系の子孫processを検査して残存はkill。
      Windowsは自processをKILL_ON_JOB_CLOSEのJob Objectへ入れる→ python が強制終了されてもbrowser子processは必ず消える。
      起動時に「親が死んだ孤児のms-playwright browser」を回収。
  (c) 全体hard timeout(既定600秒。引数 hard_timeout_s / env PW_SAFE_HARD_TIMEOUT_S)。超過で browser tree を kill し rc=124 で終了。
      既定のpage操作timeout(既定30000ms=Playwright既定と同じ)は引数 page_timeout_ms / env PW_SAFE_PAGE_TIMEOUT_MS。
  (d) 起動時に「同一command lineの別python process」を検出したら rc=75 で中止(env PW_SAFE_ALLOW_DUP=1 で許可)。引数違いは警告のみ。
  headed起動(headless=False)は env PW_SAFE_ALLOW_HEADED=1 が無い限りheadlessへ強制する。
"""
from __future__ import annotations

import atexit
import ctypes
import os
import signal
import subprocess
import sys
import threading
import time

__version__ = "1.0"
LOG_PREFIX = "[playwright_safe_01]"
DEFAULT_HARD_TIMEOUT_S = 600.0
DEFAULT_PAGE_TIMEOUT_MS = 30000
RC_HARD_TIMEOUT = 124
RC_DUPLICATE = 75

MEDIA_SILENCE_INIT_JS = """(() => {
  if (window.__pwSafeSilence) return; window.__pwSafeSilence = true;
  const P = HTMLMediaElement.prototype;
  const dMuted = Object.getOwnPropertyDescriptor(P, 'muted'), dVol = Object.getOwnPropertyDescriptor(P, 'volume');
  const force = (el) => { try { dMuted.set.call(el, true); dVol.set.call(el, 0); } catch (e) {} };
  try {
    Object.defineProperty(P, 'muted', { configurable: true, enumerable: true, get() { return true; }, set(v) { force(this); } });
    Object.defineProperty(P, 'volume', { configurable: true, enumerable: true, get() { return 0; }, set(v) { force(this); } });
  } catch (e) {}
  const play = P.play;
  P.play = function () { force(this); return play.apply(this, arguments); };
  try { document.addEventListener('play', (ev) => force(ev.target), true); document.addEventListener('loadstart', (ev) => force(ev.target), true); } catch (e) {}
  try {
    const conn = AudioNode.prototype.connect;
    AudioNode.prototype.connect = function (dest) { if (dest instanceof AudioDestinationNode) return dest; return conn.apply(this, arguments); };
  } catch (e) {}
})();"""

MEDIA_BLOCK_INIT_JS = MEDIA_SILENCE_INIT_JS + """
(() => {
  if (window.__pwSafeBlock) return; window.__pwSafeBlock = true;
  window.__pwSafePlayCalls = 0;
  HTMLMediaElement.prototype.play = function () { window.__pwSafePlayCalls++; return Promise.resolve(); };
})();"""


def _log(msg: str) -> None:
    try:
        sys.stderr.write(f"{LOG_PREFIX} {msg}\n")
        sys.stderr.flush()
    except Exception:
        pass
    p = os.environ.get("PW_SAFE_LOG")
    if p:
        try:
            with open(p, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%H:%M:%S')} pid={os.getpid()} {msg}\n")
        except Exception:
            pass


# ------------------------------------------------------------------ Windows process helpers (ctypes only; psutil不要)
_IS_WIN = os.name == "nt"
if _IS_WIN:
    from ctypes import wintypes
    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _k32.CreateJobObjectW.restype = wintypes.HANDLE
    _k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    _k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    _k32.GetCurrentProcess.restype = wintypes.HANDLE
    _k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    _k32.OpenProcess.restype = wintypes.HANDLE
    _k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _k32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]
    _k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
    _k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
    _k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]

    class _PE32(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                    ("szExeFile", ctypes.c_wchar * 260)]

    class _BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64), ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t), ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]

    class _IOC(ctypes.Structure):
        _fields_ = [(n, ctypes.c_uint64) for n in ("ro", "wo", "oo", "rt", "wt", "ot")]

    class _EXT(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", _BASIC), ("IoInfo", _IOC), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

_job_handle = None


def install_kill_on_close_job() -> bool:
    """自processをKILL_ON_JOB_CLOSEのJobへ入れる(子孫=Playwright driver/browserは親が強制終了されても消える)。"""
    global _job_handle
    if not _IS_WIN or _job_handle:
        return bool(_job_handle)
    try:
        h = _k32.CreateJobObjectW(None, None)
        if not h:
            raise OSError(ctypes.get_last_error(), "CreateJobObjectW")
        info = _EXT()
        info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not _k32.SetInformationJobObject(h, 9, ctypes.byref(info), ctypes.sizeof(info)):
            raise OSError(ctypes.get_last_error(), "SetInformationJobObject")
        if not _k32.AssignProcessToJobObject(h, _k32.GetCurrentProcess()):
            raise OSError(ctypes.get_last_error(), "AssignProcessToJobObject")
        _job_handle = h
        return True
    except Exception as e:  # fail-soft(他の保証は残る)
        _log(f"WARN job object not installed: {e}")
        return False


def process_table() -> dict:
    """pid -> (ppid, exe_name)"""
    out: dict = {}
    if not _IS_WIN:
        try:
            for ln in subprocess.run(["ps", "-eo", "pid=,ppid=,comm="], capture_output=True, text=True).stdout.splitlines():
                a = ln.split(None, 2)
                if len(a) == 3:
                    out[int(a[0])] = (int(a[1]), a[2])
        except Exception:
            pass
        return out
    snap = _k32.CreateToolhelp32Snapshot(2, 0)
    if not snap or snap == wintypes.HANDLE(-1).value:
        return out
    try:
        pe = _PE32()
        pe.dwSize = ctypes.sizeof(_PE32)
        ok = _k32.Process32FirstW(snap, ctypes.byref(pe))
        while ok:
            out[pe.th32ProcessID] = (pe.th32ParentProcessID, pe.szExeFile)
            ok = _k32.Process32NextW(snap, ctypes.byref(pe))
    finally:
        _k32.CloseHandle(snap)
    return out


def image_path(pid: int) -> str:
    if not _IS_WIN:
        return ""
    h = _k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        n = wintypes.DWORD(1024)
        return buf.value if _k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)) else ""
    finally:
        _k32.CloseHandle(h)


def descendants(root: int, table: dict | None = None) -> list:
    t = table if table is not None else process_table()
    kids: dict = {}
    for pid, (ppid, _n) in t.items():
        kids.setdefault(ppid, []).append(pid)
    out: list = []
    stack = list(kids.get(root, []))
    while stack:
        p = stack.pop()
        if p in out or p == root:
            continue
        out.append(p)
        stack.extend(kids.get(p, []))
    return out


def ancestors(pid: int, table: dict | None = None) -> list:
    t = table if table is not None else process_table()
    out: list = []
    while pid in t and t[pid][0] in t and t[pid][0] not in out and t[pid][0] != pid:
        pid = t[pid][0]
        out.append(pid)
    return out


def is_playwright_related(pid: int) -> bool:
    p = image_path(pid).lower().replace("/", "\\")
    return ("ms-playwright" in p) or ("\\playwright\\driver\\" in p)


def kill_pid(pid: int) -> bool:
    if pid == os.getpid():
        return False
    if _IS_WIN:
        h = _k32.OpenProcess(0x0001, False, pid)  # PROCESS_TERMINATE
        if not h:
            return False
        try:
            return bool(_k32.TerminateProcess(h, 1))
        finally:
            _k32.CloseHandle(h)
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except Exception:
        return False


def kill_playwright_descendants(reason: str) -> list:
    """自processの子孫のうちPlaywright系(ms-playwright配下のbrowser / playwright driver)だけをkill。返値=killしたpid。"""
    t = process_table()
    killed = []
    for pid in descendants(os.getpid(), t):
        if is_playwright_related(pid) and kill_pid(pid):
            killed.append(pid)
    if killed:
        _log(f"killed residual playwright processes ({reason}): {killed}")
    return killed


def reap_orphan_playwright_browsers() -> list:
    """親が既に存在しないms-playwright配下processの木をkill(他workerの稼働中browserは親が生きているため対象外)。"""
    if not _IS_WIN:
        return []
    t = process_table()
    killed = []
    roots = [pid for pid, (ppid, _n) in t.items() if ppid not in t and "ms-playwright" in image_path(pid).lower()]
    for r in roots:
        for pid in descendants(r, t) + [r]:
            if kill_pid(pid):
                killed.append(pid)
    if killed:
        _log(f"reaped orphan ms-playwright processes: {killed}")
    return killed


def python_cmdlines() -> dict:
    """pid -> commandline(python系のみ。PowerShell CIM、約1秒)"""
    if not _IS_WIN:
        return {}
    ps = "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True, timeout=30,
                           encoding="utf-8", errors="replace")
    except Exception:
        return {}
    out = {}
    for ln in r.stdout.splitlines():
        a = ln.split("\t", 1)
        if len(a) == 2 and a[0].strip().isdigit():
            out[int(a[0])] = a[1].strip()
    return out


def find_duplicate_runs() -> tuple:
    """(同一cmdlineの別process pid list, 同一script別引数のpid list)。自分の祖先/子孫(venv launcher等)は除外。"""
    cmds = python_cmdlines()
    me = cmds.get(os.getpid())
    if not me:
        return [], []
    t = process_table()
    skip = set(ancestors(os.getpid(), t)) | set(descendants(os.getpid(), t)) | {os.getpid()}
    script = os.path.basename(os.path.abspath(sys.argv[0])).lower() if sys.argv and sys.argv[0] else ""
    same, similar = [], []
    for pid, c in cmds.items():
        if pid in skip:
            continue
        if c == me:
            same.append(pid)
        elif script and script in c.lower():
            similar.append(pid)
    return same, similar


# ------------------------------------------------------------------ session / watchdog / signals
class _State:
    lock = threading.RLock()
    depth = 0
    browsers: list = []
    stop_event = None
    installed = False
    prev_handlers: dict = {}


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ[name])
    except Exception:
        return default


def _close_tracked(reason: str) -> None:
    with _State.lock:
        bs = list(_State.browsers)
    for b in bs:
        try:
            b._real.close()
        except Exception:
            pass


def emergency_cleanup(reason: str) -> list:
    _close_tracked(reason)
    return kill_playwright_descendants(reason)


def _watchdog(hard_s: float, stop: threading.Event) -> None:
    if stop.wait(hard_s):
        return
    _log(f"HARD TIMEOUT {hard_s:.0f}s exceeded -> killing playwright tree and exiting rc={RC_HARD_TIMEOUT}")
    try:
        kill_playwright_descendants("hard_timeout")
    finally:
        time.sleep(0.5)
        os._exit(RC_HARD_TIMEOUT)


def _signal_handler(signum, frame):
    _log(f"signal {signum} received -> cleanup")
    emergency_cleanup(f"signal{signum}")
    prev = _State.prev_handlers.get(signum)
    if signum == signal.SIGINT and callable(prev):
        return prev(signum, frame)
    raise SystemExit(128 + int(signum))


_ctrl_handler_ref = None


def _install_console_ctrl_handler() -> None:
    """Windowsコンソールのctrl event(Ctrl+C/Ctrl+Break/閉じる/ログオフ/シャットダウン)で即座にPlaywright木をkill。
    PythonレベルのSIGBREAKはmain threadがbytecodeに戻るまで遅延する(time.sleep/asyncio待機中は届かない)ため別threadのhandlerで補う。"""
    global _ctrl_handler_ref
    if not _IS_WIN or _ctrl_handler_ref is not None:
        return
    HandlerRoutine = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

    def _h(event):
        _log(f"console ctrl event {event} -> kill playwright tree")
        kill_playwright_descendants(f"ctrl_event{event}")
        if event != 0:  # Ctrl+C以外はPython側が処理を遅延させうるので即終了(Jobが残りも回収)
            os._exit(128 + 20 + event)
        return False  # Ctrl+C: 既定のKeyboardInterruptで通常unwind(finallyでclose)
    _ctrl_handler_ref = HandlerRoutine(_h)
    ctypes.windll.kernel32.SetConsoleCtrlHandler(_ctrl_handler_ref, True)


def _install_process_hooks() -> None:
    if _State.installed:
        return
    _State.installed = True
    install_kill_on_close_job()
    _install_console_ctrl_handler()
    atexit.register(lambda: (_close_tracked("atexit"), kill_playwright_descendants("atexit")))
    if threading.current_thread() is threading.main_thread():
        for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
            s = getattr(signal, name, None)
            if s is None:
                continue
            try:
                _State.prev_handlers[s] = signal.getsignal(s)
                signal.signal(s, _signal_handler)
            except Exception:
                pass


def build_launch_kwargs(browser_name: str, kw: dict, allow_audio: bool = False, block_play: bool = False) -> dict:
    """launch引数に安全既定を足す(テスト用に公開)。"""
    kw = dict(kw)
    args = list(kw.get("args") or [])
    if kw.get("headless") is False and os.environ.get("PW_SAFE_ALLOW_HEADED") != "1":
        _log("WARN headless=False requested -> forced headless=True (set PW_SAFE_ALLOW_HEADED=1 to allow)")
        kw["headless"] = True
    kw.setdefault("headless", True)
    if browser_name == "chromium":
        if not allow_audio and "--mute-audio" not in args:
            args.append("--mute-audio")
        if block_play or not any(a.startswith("--autoplay-policy=") for a in args):
            args = [a for a in args if not a.startswith("--autoplay-policy=")] + ["--autoplay-policy=user-gesture-required"]
        kw["args"] = args
    elif browser_name == "firefox" and not allow_audio:  # 未使用だが保険(Playwright Firefoxはmute引数が無いためprefで音量0)
        prefs = dict(kw.get("firefox_user_prefs") or {})
        prefs.setdefault("media.volume_scale", "0.0")
        kw["firefox_user_prefs"] = prefs
    return kw


class _SafeBrowser:
    def __init__(self, real, init_js, page_timeout_ms):
        self._real, self._init_js, self._pt = real, init_js, page_timeout_ms

    def __getattr__(self, n):
        return getattr(self._real, n)

    def _prep(self, ctx):
        if self._init_js:
            ctx.add_init_script(self._init_js)
        ctx.set_default_timeout(self._pt)
        ctx.set_default_navigation_timeout(self._pt)
        return ctx

    def new_context(self, **kw):
        return self._prep(self._real.new_context(**kw))

    def new_page(self, **kw):
        return self.new_context(**kw).new_page()

    def close(self, **kw):
        try:
            return self._real.close(**kw)
        finally:
            with _State.lock:
                if self in _State.browsers:
                    _State.browsers.remove(self)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class _SafeBrowserType:
    def __init__(self, real, name, cfg):
        self._real, self._name, self._cfg = real, name, cfg

    def __getattr__(self, n):
        return getattr(self._real, n)

    def launch(self, **kw):
        c = self._cfg
        kw = build_launch_kwargs(self._name, kw, c["allow_audio"], c["block_play"])
        b = _SafeBrowser(self._real.launch(**kw), c["init_js"], c["page_timeout_ms"])
        with _State.lock:
            _State.browsers.append(b)
        return b


class _SafePlaywright:
    def __init__(self, real, cfg):
        self._real = real
        self.chromium = _SafeBrowserType(real.chromium, "chromium", cfg)
        self.webkit = _SafeBrowserType(real.webkit, "webkit", cfg)
        self.firefox = _SafeBrowserType(real.firefox, "firefox", cfg)

    def __getattr__(self, n):
        return getattr(self._real, n)


class _SafeSyncPlaywright:
    def __init__(self, hard_timeout_s=None, page_timeout_ms=None, allow_audio=False, block_play=None, check_duplicate=True):
        from playwright.sync_api import sync_playwright as _real_sp
        self._real_cm = _real_sp()
        if allow_audio and os.environ.get("PW_SAFE_ALLOW_AUDIO") != "1":
            _log("WARN allow_audio=True ignored: env PW_SAFE_ALLOW_AUDIO=1 is also required (explicit double opt-in)")
            allow_audio = False
        if block_play is None:
            block_play = os.environ.get("PW_SAFE_BLOCK_PLAY") == "1"
        if allow_audio:
            _log("WARN audible mode enabled explicitly (allow_audio=True + PW_SAFE_ALLOW_AUDIO=1)")
        init_js = None if allow_audio else (MEDIA_BLOCK_INIT_JS if block_play else MEDIA_SILENCE_INIT_JS)
        self._cfg = dict(allow_audio=allow_audio, block_play=bool(block_play), init_js=init_js,
                         page_timeout_ms=int(page_timeout_ms or _env_float("PW_SAFE_PAGE_TIMEOUT_MS", DEFAULT_PAGE_TIMEOUT_MS)))
        self._hard = float(hard_timeout_s or _env_float("PW_SAFE_HARD_TIMEOUT_S", DEFAULT_HARD_TIMEOUT_S))
        self._check_dup = check_duplicate
        self._pw = None

    def start(self):
        with _State.lock:
            first = _State.depth == 0
            _State.depth += 1
        if first:
            _install_process_hooks()
            reap_orphan_playwright_browsers()
            if self._check_dup and os.environ.get("PW_SAFE_ALLOW_DUP") != "1" and os.environ.get("PW_SAFE_NO_DUP_CHECK") != "1":
                same, similar = find_duplicate_runs()
                if similar:
                    _log(f"WARN same script already running with different args: pids={similar}")
                if same:
                    _log(f"DUPLICATE run detected (same command line already running: pids={same}) -> abort rc={RC_DUPLICATE} "
                         f"(PW_SAFE_ALLOW_DUP=1 to override)")
                    with _State.lock:
                        _State.depth -= 1
                    raise SystemExit(RC_DUPLICATE)
            _State.stop_event = threading.Event()
            threading.Thread(target=_watchdog, args=(self._hard, _State.stop_event), daemon=True, name="pw_safe_watchdog").start()
            mode = "ALLOWED" if self._cfg["allow_audio"] else ("blocked-play" if self._cfg["block_play"] else "muted")
            _log(f"session start hard_timeout={self._hard:.0f}s page_timeout={self._cfg['page_timeout_ms']}ms audio={mode} "
                 f"job={'on' if _job_handle else 'off'}")
        try:
            self._pw = _SafePlaywright(self._real_cm.start(), self._cfg)
        except BaseException:
            self._finish()
            raise
        return self._pw

    def _finish(self):
        with _State.lock:
            _State.depth -= 1
            last = _State.depth <= 0
        _close_tracked("session_end")
        if last:
            if _State.stop_event is not None:
                _State.stop_event.set()
                _State.stop_event = None
            time.sleep(0.2)
            left = kill_playwright_descendants("session_end_residual")
            _log(f"session end residual_killed={left}")

    def stop(self):
        try:
            self._real_cm.stop()
        finally:
            self._finish()

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        try:
            self._real_cm.__exit__(*exc)
        finally:
            self._finish()
        return False


def sync_playwright(**kw) -> _SafeSyncPlaywright:
    """playwright.sync_api.sync_playwright のdrop-in。引数は任意: hard_timeout_s / page_timeout_ms / allow_audio / block_play / check_duplicate。"""
    return _SafeSyncPlaywright(**kw)


def sync_playwright_noplay(**kw) -> _SafeSyncPlaywright:
    """音声再生を一切使わないtest用(play()をno-op化)。"""
    kw.setdefault("block_play", True)
    return _SafeSyncPlaywright(**kw)
