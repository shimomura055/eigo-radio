# -*- coding: utf-8 -*-
"""第2巡 試聴ページのGate 7(公開Pages上のPlaywright実再生evidence、API 0)。er019_bape_play_verify_04.py派生。"""
import argparse, json
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

ap = argparse.ArgumentParser(); ap.add_argument("--url"); ap.add_argument("--out"); A = ap.parse_args()
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
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    html = pg.content()
    out.update(http_status=resp.status, audio_count=pg.locator("audio").count(), file_scheme_in_html=("file:///" in html or "C:\\" in html or "C:/" in html))
    plays = []
    for i in range(out["audio_count"]):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate("""async (i) => {
            const a = document.querySelectorAll('audio')[i]; a.muted = true;
            await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
            const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
            try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
            const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1000)); const t1 = a.currentTime;
            a.pause(); a.removeAttribute('src'); a.load(); return {duration: d, advanced: t1 > t0 + 0.4, error: null};
        }""", i)
        res["src"] = src
        plays.append(res)
    out["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    out["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    out["http_ge400"] = bad
    out["console_errors"] = errs
    br.close()
json.dump(out, open(A.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items()}, ensure_ascii=False)[:1200])
