"""PLAYWRIGHT-AUDIO-SAFETY-01: 修正版 observe_caption_prod_01.py を1記事で1回だけ実行し、前/中/後のchrome系process数と実引数(Win32_Process cmdline)を保存。API 0。
使い方: python measure_observe_run_01.py <repo_root> <out_json> [--probe-audio] -- <observe args...>
--probe-audio: 各サンプルでaudio_session_probe_01.ps1も実行し、Windows既定デバイスの実出力peak(ENDPOINT_MASTER_METER)とブラウザ子孫のAudio Sessionを記録。"""
import json, os, subprocess, sys, time
PROBE_PS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_session_probe_01.ps1")
root, out = sys.argv[1], sys.argv[2]; PROBE = "--probe-audio" in sys.argv[:sys.argv.index("--")]; obs_args = sys.argv[sys.argv.index("--") + 1:]
PS = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'chrome|chromium|msedge|headless|webkit|MiniBrowser|node' } | "
      "ForEach-Object { \"$($_.ProcessId)`t$($_.ParentProcessId)`t$($_.Name)`t$($_.ExecutablePath)`t$($_.CommandLine)\" }")
def snap():
    r = subprocess.run(["powershell", "-NoProfile", "-Command", PS], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    rows = []
    for ln in r.splitlines():
        a = ln.split("\t", 4)
        if len(a) == 5:
            rows.append(dict(pid=int(a[0]), ppid=int(a[1]), name=a[2], exe=a[3], cmd=a[4]))
    return rows
def summarize(rows):
    pw = [r for r in rows if "ms-playwright" in (r["exe"] or "").lower() or "playwright" in (r["cmd"] or "").lower() and "driver" in (r["cmd"] or "").lower()]
    return dict(chrome_family_total=len([r for r in rows if r["name"].lower().startswith(("chrome", "msedge", "chromium"))]),
                playwright_related=len(pw), playwright_pids=[r["pid"] for r in pw])
before = snap()
t0 = time.time()
p = subprocess.Popen([sys.executable, "docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/tools/observe_caption_prod_01.py"] + obs_args, cwd=root, stdout=open(out + ".stdout.txt", "wb"), stderr=subprocess.STDOUT)
during = []; mains = {}; audio_samples = []
while p.poll() is None:
    if PROBE:
        pr = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PROBE_PS], capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            j = json.loads(pr.stdout.strip() or "[]"); j = j if isinstance(j, list) else [j]
        except Exception:
            j = []
        tree = {r["pid"] for r in snap() if r["name"].lower() not in ("powershell.exe",)}
        audio_samples.append(dict(t=round(time.time() - t0, 1), endpoint_peak=next((x["peak"] for x in j if x["pid"] == -1), None),
                                  sessions=[x for x in j if x["pid"] != -1 and x["process"] in ("chrome-headless-shell", "WebKitWebProcess", "Playwright", "chrome", "MiniBrowser")]))
    time.sleep(2); rows = snap(); s = summarize(rows); during.append(dict(t=round(time.time() - t0, 1), **s))
    for r in rows:
        if "ms-playwright" in (r["exe"] or "").lower() and "--type=" not in r["cmd"] and r["pid"] not in mains:
            mains[r["pid"]] = dict(name=r["name"], cmd=r["cmd"][:600], has_mute_audio="--mute-audio" in r["cmd"], has_headless="headless" in (r["exe"] + r["cmd"]).lower())
rc = p.wait(); time.sleep(3); after = snap()
res = dict(rc=rc, seconds=round(time.time() - t0, 1), before=summarize(before), during_samples=during, browser_main_processes=mains, audio_samples=audio_samples, after=summarize(after))
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1)[:3000])
