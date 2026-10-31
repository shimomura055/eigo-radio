# -*- coding: utf-8 -*-
import json
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_style_h_speed_04/"
out = {"base": BASE}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); out["browser"] = br.version
    pg = br.new_page(); errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    html = pg.content()
    o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "sections": [e.get_attribute("id") for e in pg.locator("section[id]").all()], "banner_present": ("暫定成果物。採用判断なし(Trial、VALIDATED上限)" in html), "prompt_blocks": pg.locator(".sc").count(), "title": pg.title(), "file_scheme_in_html": ("file:///" in html or "C:\\" in html)}
    plays = []
    for i in range(o["audio_count"]):
        src = pg.locator("audio").nth(i).get_attribute("src")
        r = pg.evaluate("""async (i) => { const a = document.querySelectorAll('audio')[i]; a.muted = true;
          await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
          const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
          try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
          const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1200)); const t1 = a.currentTime; a.pause(); return {duration: d, advanced: t1 > t0 + 0.5, error: null}; }""", i)
        r["src"] = src; plays.append(r)
    ctx = pg.context
    st = {x["src"]: ctx.request.get(BASE + x["src"]).status for x in plays}; o["full_v5_note"] = "audio elements incl. ../coffee_final_v5 full story mp3"
    o["mp3_http"] = {"n": len(st), "all_200": all(v == 200 for v in st.values())}
    o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    o["http_ge400"] = bad; o["console_errors"] = errs; o["plays"] = plays; out["page"] = o; br.close()
json.dump(out, open("er057_output/coffee_tts_style_h_speed_04/round6_listen/play_evidence_r6.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: v for k, v in o.items() if k != "plays"})
