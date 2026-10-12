# -*- coding: utf-8 -*-
"""Pages HTTP + Playwright実再生(課金APIなし)。Gate 7(l)(m)(n)の機械確認を含む。"""
import json, urllib.request, time, re
from playwright.sync_api import sync_playwright
B = "https://shimomura055.github.io/eigo-radio/user_test/coffee_ja_style_trial_02/"
html = urllib.request.urlopen(B + "index.html", timeout=60).read().decode("utf8")
srcs = re.findall(r'src="([^"]+\.mp3)"', html)
out = {"index_url": B + "index.html", "http": {}, "play": []}
for u in ["index.html"] + sorted(set(srcs)):
    out["http"][B + u] = urllib.request.urlopen(B + u, timeout=60).status
out["contains_file_scheme_or_Cdrive"] = ("file:///" in html) or ("C:\\" in html)
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    pg = br.new_page(); pg.goto(B + "index.html", wait_until="networkidle")
    n = pg.locator("audio").count(); out["audio_count"] = n
    out["rows_with_voice_and_script"] = pg.evaluate("()=>[...document.querySelectorAll('.a')].filter(r=>r.querySelector('audio')&&r.querySelector('.v').textContent.trim()&&r.querySelector('.s').textContent.trim()).length")
    out["kp_table_cells"] = pg.evaluate("()=>[...document.querySelectorAll('table.kp tr')].map(r=>[...r.children].map(c=>c.textContent))")
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
out["a2_b1_visible_in_user_page"] = bool(re.search(r"\bA2\b|\bB1\b", re.sub(r"<[^>]+>", " ", html)))
out["all_ok"] = (all(r["ok"] for r in out["play"]) and all(v == 200 for v in out["http"].values())
                 and not out["contains_file_scheme_or_Cdrive"] and out["rows_with_voice_and_script"] == out["audio_count"] and not out["label_strings_present"])
json.dump(out, open("er057_output/ja_aoede_style_trial_02/play_evidence_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(out["all_ok"], out["audio_count"], out["rows_with_voice_and_script"], out["label_strings_present"], out["a2_b1_visible_in_user_page"], out["min_audio_width_px"], sum(r["ok"] for r in out["play"]), len(out["http"]))
