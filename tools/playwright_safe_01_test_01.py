"""PLAYWRIGHT-AUDIO-SAFETY-01: tools/playwright_safe_01.py のtest。API 0。音声は一切鳴らさない(使うwavは無音、かつ--mute-audio)。
実行: python tools/playwright_safe_01_test_01.py  (実Chromiumを起動する。約1-2分。Windows前提のprocess検証を含む)"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import playwright_safe_01 as S  # noqa: E402

IS_WIN = os.name == "nt"
ENV = dict(os.environ, PYTHONUTF8="1", PW_SAFE_NO_DUP_CHECK="1", PW_SAFE_LOG="")
TMP = Path(tempfile.mkdtemp(prefix="pwsafe_test_"))
with wave.open(str(TMP / "silent.wav"), "wb") as w:  # 5秒の無音(音を出さない)
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(b"\x00\x00" * 8000 * 5)
(TMP / "p.html").write_text('<html><body><audio id="a" src="silent.wav" preload="auto"></audio></body></html>', encoding="utf-8")
URL = (TMP / "p.html").as_uri()
PRE = f"import sys, os, time, json\nsys.path.insert(0, {str(HERE)!r})\nfrom playwright_safe_01 import sync_playwright\nimport playwright_safe_01 as S\nURL = {URL!r}\n"


def run_child(body: str, env_extra: dict | None = None, **popen_kw) -> subprocess.Popen:
    f = TMP / f"child_{time.time_ns()}.py"
    f.write_text(PRE + textwrap.dedent(body), encoding="utf-8")
    env = dict(ENV, **(env_extra or {}))
    return subprocess.Popen([sys.executable, str(f)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, **popen_kw)


def read_marker(p: subprocess.Popen, marker: str, timeout: float = 60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        ln = p.stdout.readline()
        if ln.startswith(marker):
            return json.loads(ln[len(marker):])
        if not ln and p.poll() is not None:
            break
    raise AssertionError(f"marker {marker} not seen; rc={p.poll()} err={p.stderr.read()[:1500] if p.poll() is not None else ''}")


def alive(pids) -> list:
    t = S.process_table()
    return [x for x in pids if x in t]


def cmdlines(pids) -> dict:
    ps = "Get-CimInstance Win32_Process | Where-Object { @(%s) -contains $_.ProcessId } | ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }" % ",".join(map(str, pids))
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {int(l.split("\t", 1)[0]): l.split("\t", 1)[1] for l in r.stdout.splitlines() if "\t" in l}


LAUNCH_AND_REPORT = """
with sync_playwright(__KW__) as p:
    br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]) if __AUTOPLAY__ else p.chromium.launch()
    pg = br.new_page(); pg.goto(URL)
    pids = [x for x in S.descendants(os.getpid()) if S.is_playwright_related(x)]
    print("PIDS" + json.dumps({"self": os.getpid(), "pids": pids}), flush=True)
    __AFTER__
"""


def scenario(after: str, kw: str = "", autoplay: bool = True) -> str:
    return LAUNCH_AND_REPORT.replace("__KW__", kw).replace("__AUTOPLAY__", str(autoplay)).replace("__AFTER__", after)


class LaunchArgs(unittest.TestCase):
    def test_default_args(self):
        k = S.build_launch_kwargs("chromium", {})
        self.assertTrue(k["headless"]); self.assertIn("--mute-audio", k["args"])
        self.assertIn("--autoplay-policy=user-gesture-required", k["args"])

    def test_caller_autoplay_kept_but_still_muted(self):
        k = S.build_launch_kwargs("chromium", {"args": ["--autoplay-policy=no-user-gesture-required"]})
        self.assertIn("--autoplay-policy=no-user-gesture-required", k["args"]); self.assertIn("--mute-audio", k["args"])

    def test_block_play_forces_user_gesture_policy(self):
        k = S.build_launch_kwargs("chromium", {"args": ["--autoplay-policy=no-user-gesture-required"]}, block_play=True)
        self.assertEqual([a for a in k["args"] if a.startswith("--autoplay-policy=")], ["--autoplay-policy=user-gesture-required"])

    def test_headed_forced_headless(self):
        os.environ.pop("PW_SAFE_ALLOW_HEADED", None)
        self.assertTrue(S.build_launch_kwargs("chromium", {"headless": False})["headless"])

    def test_allow_audio_needs_double_opt_in(self):
        os.environ.pop("PW_SAFE_ALLOW_AUDIO", None)
        self.assertIsNotNone(S._SafeSyncPlaywright(allow_audio=True)._cfg["init_js"])  # double opt-in無し=無視され無音のまま
        self.assertFalse(S._SafeSyncPlaywright(allow_audio=True)._cfg["allow_audio"])


@unittest.skipUnless(IS_WIN, "Windows process検証")
class RealBrowser(unittest.TestCase):
    def test_real_browser_cmdline_has_mute_headless_and_media_forced_silent(self):
        body = """
        with sync_playwright() as p:
            br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]); pg = br.new_page(); pg.goto(URL)
            pids = [x for x in S.descendants(os.getpid()) if S.is_playwright_related(x)]
            print("PIDS" + json.dumps(pids), flush=True)
            r = pg.evaluate('''async () => { const a = document.getElementById('a'); a.muted = false; a.volume = 1; await a.play(); await new Promise(r => setTimeout(r, 1500));
              a.muted = false; return {muted: a.muted, volume: a.volume, paused: a.paused, t: a.currentTime}; }''')
            print("RES" + json.dumps(r), flush=True)
            time.sleep(1);
        """
        pr = run_child(body)
        pids = read_marker(pr, "PIDS")
        cl = cmdlines(pids)
        main = [c for c in cl.values() if "--type=" not in c and "ms-playwright" in c]
        self.assertTrue(main, cl)
        for c in main:
            self.assertIn("--mute-audio", c); self.assertIn("--autoplay-policy=no-user-gesture-required", c)
            self.assertIn("headless", c.lower().replace("_", "-"))
        res = read_marker(pr, "RES")
        self.assertTrue(res["muted"]); self.assertEqual(res["volume"], 0)
        self.assertFalse(res["paused"]); self.assertGreater(res["t"], 0.5)  # 再生自体は進む(既存testの時間依存を維持)
        pr.wait(timeout=60); self.assertEqual(pr.returncode, 0, pr.stderr.read())
        self.assertEqual(alive(pids), [])

    def test_webkit_media_forced_muted_and_playback_still_advances(self):
        wk = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
        if not list(wk.glob("webkit-*")):
            self.skipTest("webkit not installed")
        body = """
        with sync_playwright() as p:
            br = p.webkit.launch(); pg = br.new_page(); pg.goto(URL)
            r = pg.evaluate('''async () => { const a = document.getElementById('a'); a.muted = false; a.volume = 1; await a.play(); await new Promise(r => setTimeout(r, 1500));
              a.muted = false; a.volume = 1; return {muted: a.muted, volume: a.volume, paused: a.paused, t: a.currentTime}; }''')
            print("RES" + json.dumps(r), flush=True)
        """
        pr = run_child(body); res = read_marker(pr, "RES", 90)
        self.assertTrue(res["muted"]); self.assertEqual(res["volume"], 0); self.assertFalse(res["paused"]); self.assertGreater(res["t"], 0.5)
        pr.wait(timeout=60); self.assertEqual(pr.returncode, 0, pr.stderr.read())

    def test_block_play_is_noop(self):
        body = """
        with sync_playwright(block_play=True) as p:
            br = p.chromium.launch(); pg = br.new_page(); pg.goto(URL)
            r = pg.evaluate('''async () => { const a = document.getElementById('a'); const pr = a.play(); await pr; await new Promise(r => setTimeout(r, 800));
              return {paused: a.paused, t: a.currentTime, calls: window.__pwSafePlayCalls}; }''')
            print("RES" + json.dumps(r), flush=True)
        """
        pr = run_child(body); res = read_marker(pr, "RES")
        self.assertTrue(res["paused"]); self.assertEqual(res["t"], 0); self.assertEqual(res["calls"], 1)
        pr.wait(timeout=60); self.assertEqual(pr.returncode, 0)

    def test_normal_exit_leaves_no_children(self):
        pr = run_child(scenario("pass"))
        pids = read_marker(pr, "PIDS")["pids"]
        self.assertTrue(pids)
        pr.wait(timeout=60); self.assertEqual(pr.returncode, 0, pr.stderr.read())
        self.assertEqual(alive(pids), [])

    def test_exception_exit_leaves_no_children(self):
        pr = run_child(scenario("raise RuntimeError('boom')"))
        pids = read_marker(pr, "PIDS")["pids"]
        pr.wait(timeout=60); self.assertNotEqual(pr.returncode, 0)
        self.assertEqual(alive(pids), [])

    def test_forced_kill_of_python_kills_browser_tree(self):
        pr = run_child(scenario("time.sleep(120)"))
        info = read_marker(pr, "PIDS"); pids = info["pids"]
        self.assertTrue(pids); self.assertEqual(alive(pids), pids)
        r = subprocess.run(["taskkill", "/F", "/PID", str(info["self"])], capture_output=True, text=True, encoding="mbcs", errors="replace")  # 子孫を道連れにしない=自processだけ
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        pr.wait(timeout=30); time.sleep(2)
        self.assertEqual(alive(pids), [], "browser/driver children must die with the killed python (Job Object)")

    def test_ctrl_break_cleanup(self):
        import signal
        pr = run_child(scenario("time.sleep(120)"), creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        pids = read_marker(pr, "PIDS")["pids"]
        pr.send_signal(signal.CTRL_BREAK_EVENT)
        pr.wait(timeout=60); time.sleep(1)
        self.assertEqual(alive(pids), [])
        self.assertIn("console ctrl event", pr.stderr.read())

    def test_hard_timeout_kills_and_exits_124(self):
        pr = run_child(scenario("time.sleep(120)", kw="hard_timeout_s=5"))
        pids = read_marker(pr, "PIDS")["pids"]
        t0 = time.time(); pr.wait(timeout=40)
        self.assertEqual(pr.returncode, S.RC_HARD_TIMEOUT)
        self.assertLess(time.time() - t0, 20)
        time.sleep(1); self.assertEqual(alive(pids), [])
        self.assertIn("HARD TIMEOUT", pr.stderr.read())

    def test_duplicate_run_aborts_75(self):
        f = TMP / "dup_child.py"
        f.write_text(PRE + textwrap.dedent("""
            with sync_playwright() as p:
                print("UP", flush=True); time.sleep(40)
        """), encoding="utf-8")
        env = dict(ENV); env.pop("PW_SAFE_NO_DUP_CHECK", None)
        a = subprocess.Popen([sys.executable, str(f)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        try:
            self.assertEqual(a.stdout.readline().strip(), "UP")
            b = subprocess.run([sys.executable, str(f)], capture_output=True, text=True, env=env, timeout=90)
            self.assertEqual(b.returncode, S.RC_DUPLICATE, b.stderr)
            self.assertIn("DUPLICATE", b.stderr)
        finally:
            subprocess.run(["taskkill", "/F", "/PID", str(a.pid)], capture_output=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
