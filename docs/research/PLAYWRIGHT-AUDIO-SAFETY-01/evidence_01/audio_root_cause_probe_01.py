"""PLAYWRIGHT-AUDIO-SAFETY-01 ROOT_CAUSE証拠: 旧方式(素のPlaywright)と修正版helperで、ブラウザがWindowsへ音声出力(Audio Session生成)するかを機械確認。API 0。
安全: 再生するwavは振幅±16/32768(約-66dBFS、実質聞こえない)・4秒のみ。Windows Audio Sessionの有無(音量ミキサー登録)で「音声デバイスへ出力しているか」を見る。
使い方: python audio_root_cause_probe_01.py <out_json> [chromium|webkit ...]"""
import json, os, struct, subprocess, sys, tempfile, time, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools" if (HERE.parents[2] / "tools").exists() else HERE))
for q in Path(__file__).resolve().parents:
    if (q / "tools" / "playwright_safe_01.py").exists():
        sys.path.insert(0, str(q / "tools")); break
import playwright_safe_01 as S
PROBE = str(HERE / "audio_session_probe_01.ps1")
tmp = Path(tempfile.mkdtemp(prefix="pwsafe_rc_"))
with wave.open(str(tmp / "q.wav"), "wb") as w:  # 200Hz矩形波 ±16 LSB
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
    w.writeframes(b"".join(struct.pack("<h", 16 if (i // 20) % 2 else -16) for i in range(8000 * 20)))
(tmp / "p.html").write_text('<html><body><audio id="a" src="q.wav" loop preload="auto"></audio></body></html>', encoding="utf-8")
URL = (tmp / "p.html").as_uri()

def sessions():
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PROBE], capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        j = json.loads(r.stdout.strip() or "[]")
    except Exception:
        return [{"error": r.stdout[:200] + r.stderr[:200]}]
    return j if isinstance(j, list) else [j]

def case(label, launch):
    out = dict(label=label)
    with launch() as ctx:
        p, kind = ctx
        br = (p.chromium if kind == "chromium" else p.webkit)
        browser = br.launch(args=["--autoplay-policy=no-user-gesture-required"]) if kind == "chromium" else br.launch()
        page = browser.new_page(); page.goto(URL)
        page.evaluate("async () => { const a = document.getElementById('a'); await a.play(); }")
        time.sleep(2)
        pk = []
        for _ in range(4):  # session peakを複数回サンプル
            pk.append(sessions()); time.sleep(0.3)
        st = page.evaluate("() => { const a = document.getElementById('a'); return {paused: a.paused, t: a.currentTime, muted: a.muted, vol: a.volume}; }")
        desc = set(S.descendants(os.getpid()))
        ss = pk[-1]
        out["peak_samples_in_tree"] = [[x for x in smp if x.get("pid") in desc or x.get("pid") == -1] for smp in pk]
        out["endpoint_master_peak_samples"] = [next((x["peak"] for x in smp if x.get("pid") == -1), None) for smp in pk]
        out["media_state"] = st
        out["browser_tree_pids"] = sorted(desc)
        out["all_sessions"] = ss
        out["sessions_in_browser_tree"] = [s for s in ss if s.get("pid") in desc]
        out["tree_cmd_has_mute_audio"] = None
        browser.close()
    return out

class Raw:
    def __init__(self, kind): self.kind = kind
    def __enter__(self):
        from playwright.sync_api import sync_playwright as sp
        self.cm = sp(); return (self.cm.__enter__(), self.kind)
    def __exit__(self, *a): return self.cm.__exit__(*a)
class Safe:
    def __init__(self, kind): self.kind = kind
    def __enter__(self):
        self.cm = S.sync_playwright(check_duplicate=False); return (self.cm.__enter__(), self.kind)
    def __exit__(self, *a): return self.cm.__exit__(*a)

res = []
kinds = sys.argv[2:] or ["chromium", "webkit"]
for k in kinds:
    res.append(case(f"OLD raw playwright / {k} (no mute)", lambda k=k: Raw(k)))
    res.append(case(f"FIXED playwright_safe_01 / {k}", lambda k=k: Safe(k)))
Path(sys.argv[1]).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
for r in res:
    print(r["label"], "| sessions_in_browser_tree:", r["sessions_in_browser_tree"], "| endpoint_peaks:", r["endpoint_master_peak_samples"], "| media:", r["media_state"])
