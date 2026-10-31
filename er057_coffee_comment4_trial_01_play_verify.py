import json, re, time, urllib.request
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_comment4_trial_01/"
OUTP = "er057_output/coffee_comment4_trial_01/play_evidence.json"
for _ in range(30):
    try:
        if urllib.request.urlopen(BASE + "index.html").status == 200: break
    except Exception: time.sleep(20)
out = {"base": BASE}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); out["browser"] = br.version
    pg = br.new_page(); errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    html = pg.content()
    o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "file_scheme_in_html": ("file:///" in html or "C:\\" in html)}
    plays = []
    for i in range(o["audio_count"]):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate("""async (i) => {
            const a = document.querySelectorAll('audio')[i]; a.muted = true;
            await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
            const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
            try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
            const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1200)); const t1 = a.currentTime;
            let seekOk = null; if (d > 8) { const tgt = d - 3; a.currentTime = tgt; await new Promise(r => setTimeout(r, 800)); seekOk = Math.abs(a.currentTime - tgt) < 2.5; }
            a.pause(); return {duration: d, advanced: t1 > t0 + 0.5, error: null, seekOk};
        }""", i)
        res["src"] = src; plays.append(res)
    o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    o["plays"] = [{"src": x["src"], "duration": round(x["duration"], 2), "advanced": x.get("advanced"), "seekOk": x.get("seekOk"), "error": x.get("error")} for x in plays]
    o["http_ge400"] = bad; o["console_errors"] = errs; out["page"] = o
    br.close()
json.dump(out, open(OUTP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: v for k, v in o.items() if k != "plays"})
for x in o["plays"]: print(x)
