# -*- coding: utf-8 -*-
"""SJS4: Pages HTTP + Playwright実再生(課金APIなし)。Gate 7(l)(m)(n)の機械確認を含む。前例 er057_output/ja_aoede_style_trial_02/play_verify_01.py を流用。"""
import json, urllib.request, urllib.error, time, re, argparse, datetime
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
ap = argparse.ArgumentParser()
ap.add_argument("--url", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--wait-min", type=float, default=10)
a = ap.parse_args()
B = a.url.rsplit("/", 1)[0] + "/"
html = None
t0 = time.time()
while True:   # Pages反映待ち(最大wait-min分)
    try:
        r = urllib.request.urlopen(a.url, timeout=60)
        html = r.read().decode("utf8")
        if "Trial 04" in html:
            break
    except urllib.error.URLError:
        pass
    if time.time() - t0 > a.wait_min * 60:
        raise SystemExit("Pages not ready within wait")
    time.sleep(20)
srcs = re.findall(r'src="([^"]+\.mp3)"', html)
out = {"index_url": a.url, "checked_at_jst": (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S"), "http": {}, "play": []}
full = lambda u: u if u.startswith("http") else B + u
for u in ["index.html"] + sorted(set(srcs)):
    out["http"][full(u)] = urllib.request.urlopen(full(u), timeout=60).status
out["contains_file_scheme_or_Cdrive"] = ("file:///" in html) or ("C:\\" in html)
errs = []
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    pg = br.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "index.html", wait_until="networkidle")
    n = pg.locator("audio").count(); out["audio_count"] = n
    out["rows_with_voice_and_script"] = pg.evaluate("()=>[...document.querySelectorAll('.a')].filter(r=>r.querySelector('audio')&&r.querySelector('.v').textContent.trim()&&r.querySelector('.s').textContent.trim()).length")
    body = pg.inner_text("body")
    out["label_strings_present"] = bool(re.search(r"English:|英語:|EN:|日本語:|日本語gloss:|JA:", body))
    out["min_audio_width_px"] = pg.evaluate("()=>Math.min(...[...document.querySelectorAll('audio')].map(a=>a.getBoundingClientRect().width))")
    for i in range(n):
        pg.evaluate("i=>{document.querySelectorAll('audio').forEach(a=>a.pause());const a=document.querySelectorAll('audio')[i];a.currentTime=0;return a.play()}", i)
        time.sleep(1.0)
        r = pg.evaluate("i=>{const a=document.querySelectorAll('audio')[i];return {src:a.currentSrc,currentTime:a.currentTime,paused:a.paused,readyState:a.readyState,duration:a.duration,error:a.error&&a.error.code}}", i)
        r["ok"] = r["currentTime"] > 0 and not r["paused"] and r["readyState"] >= 3 and r["error"] is None
        out["play"].append(r)
    br.close()
out["console_errors"] = errs
out["a2_b1_visible_in_user_page"] = bool(re.search(r"\bA2\b|\bB1\b", re.sub(r"<[^>]+>", " ", html)))
out["all_ok"] = (all(r["ok"] for r in out["play"]) and all(v == 200 for v in out["http"].values()) and not out["contains_file_scheme_or_Cdrive"]
                 and out["rows_with_voice_and_script"] == out["audio_count"] and not out["label_strings_present"] and not errs)
json.dump(out, open(a.out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(out["all_ok"], out["audio_count"], out["rows_with_voice_and_script"], out["label_strings_present"], out["a2_b1_visible_in_user_page"], out["min_audio_width_px"], sum(r["ok"] for r in out["play"]), len(out["http"]), len(errs))
