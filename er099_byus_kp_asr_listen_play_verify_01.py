# -*- coding: utf-8 -*-
"""FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01: 公開Pages上の試聴ページPlaywright実再生evidence(有料APIなし)。
er019_pp_play_verify_01.py派生(音声が約1秒と短いため、再生判定はended/currentTime>0、seekは0.3秒位置)。"""
import argparse
import json
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--url")
ap.add_argument("--out")
A = ap.parse_args()
BASE = A.url.rsplit("index.html", 1)[0]
out = {"base": BASE}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    out["browser"] = br.version
    pg = br.new_page()
    errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(A.url, wait_until="networkidle")
    html = pg.content()
    out["http_status"] = resp.status
    out["audio_count"] = pg.locator("audio").count()
    out["file_scheme_in_html"] = ("file:///" in html or "C:\\" in html or "C:/" in html)
    out["has_think_up_blurt_highlight"] = ("think up" in html and "blurt" in html and "★新基準で不合格" in html)
    plays = []
    for i in range(out["audio_count"]):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate("""async (i) => {
            const a = document.querySelectorAll('audio')[i]; a.muted = true;
            await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
            const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
            try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
            await new Promise(r => setTimeout(r, 1500)); const t1 = a.currentTime;
            a.currentTime = Math.min(0.3, d / 2); await new Promise(r => setTimeout(r, 200));
            const seekOk = a.currentTime > 0.1 || a.ended;
            a.pause(); return {duration: d, advanced: t1 > 0.1 || a.ended, error: null, seekOk};
        }""", i)
        res["src"] = src
        plays.append(res)
    out["plays"] = plays
    out["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    out["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    out["seek_ok_all"] = all(x.get("seekOk") is True for x in plays)
    out["http_ge400"] = bad
    out["console_errors"] = errs
    br.close()
json.dump(out, open(A.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "plays"}, ensure_ascii=False))
