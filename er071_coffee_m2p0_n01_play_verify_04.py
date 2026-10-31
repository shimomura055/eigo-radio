# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_04: 公開Pages上の試聴ページPlaywright実再生evidence(有料APIなし)。er057_coffee_final_v5_play_verify_01.py派生。"""
import json, re, sys
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_m2p0_n01_final_03/"
OUTP = "er071_output/m2p0_n01_production_wiring_01/completion_04/pages_play_evidence_04.json"
EXPECT = {"Coffee_Advanced_final_03.mp3": 315.43, "Coffee_Standard_final_03.mp3": 314.865}
out = {"base": BASE, "pages": {}}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); out["browser"] = br.version
    pg = br.new_page(); errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    text, html = pg.inner_text("body"), pg.content()
    o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "file_scheme_in_html": ("file:///" in html or "C:\\" in html or "C:/" in html),
         "kp_tables": pg.locator("table.kp").count(), "has_metrics_table": "文末ポーズ" in text and "WPM" in text, "has_gloss_aligned": "インタビューをもとにした" in text, "has_based_on_interviews": "based on interviews" in text, "has_pause_unit_note": "合否基準ではありません" in text}
    plays = []
    for i in range(o["audio_count"]):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate("""async (i) => {
            const a = document.querySelectorAll('audio')[i]; a.muted = true;
            await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
            const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
            try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
            const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1200)); const t1 = a.currentTime;
            let seekOk = null; if (d > 20) { const tgt = d - 5; a.currentTime = tgt; await new Promise(r => setTimeout(r, 800)); seekOk = Math.abs(a.currentTime - tgt) < 2.5; }
            a.pause(); a.removeAttribute('src'); a.load(); return {duration: d, advanced: t1 > t0 + 0.5, error: null, seekOk};
        }""", i)
        res["src"] = src; plays.append(res)
    o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    o["seek_ok_all"] = all(x.get("seekOk") in (None, True) for x in plays)
    o["full_durations"] = {x["src"]: round(x["duration"], 2) for x in plays if "final_03.mp3" in x["src"]}
    o["http_ge400"] = bad; o["console_errors"] = errs
    out["pages"]["index.html"] = o
    br.close()
out["expected_full_durations"] = EXPECT
json.dump(out, open(OUTP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({a: b for a, b in o.items() if a != "plays_failed"}, o["plays_failed"])
