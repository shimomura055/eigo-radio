# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 delegation 08: Playwright real-playback evidence on the PUBLIC GitHub Pages URL.
No paid API (only static page fetch)."""
import json, re
from playwright.sync_api import sync_playwright

BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_new_tone_01"
OUTJ = "er053_output/coffee_new_tone_e2e_01/pages_play_evidence_02.json"
PAGES = (("index", "/index.html"), ("part2_review", "/part2_review/index.html"), ("advanced_player", "/b1b/player.html"))

out = {"base": BASE, "pages": {}}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    out["browser"] = br.version
    for name, url in PAGES:
        pg = br.new_page()
        errs, bad, reqs = [], [], []
        pg.on("console", lambda m, errs=errs: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
        pg.on("response", lambda r, bad=bad: bad.append((r.url, r.status)) if r.status >= 400 else None)
        resp = pg.goto(BASE + url, wait_until="networkidle")
        text = pg.inner_text("body")
        content = pg.content()
        rec = {"url": BASE + url, "http_status": resp.status, "audio_count": pg.locator("audio").count(), "http_ge400": bad,
               "label_check": {"label_EN/English/英語/日本語gloss_present": bool(re.search(r"(English:|\bEN:|英語:|日本語gloss)", text)),
                               "A2_or_B1_level_label_visible": bool(re.search(r"\(A2\)|\(B1\)|\bB1B\b", text)),
                               "has_Standard": "Standard" in text, "has_Advanced": "Advanced" in text,
                               "file_scheme_in_html": "file:///" in content or "C:\\" in content}}
        plays = []
        for i in range(rec["audio_count"]):
            src = pg.locator("audio").nth(i).get_attribute("src")
            res = pg.evaluate("""async (i) => {
                const a = document.querySelectorAll('audio')[i];
                a.muted = true;
                await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
                const d = a.duration; const err = a.error ? a.error.code : null;
                if (err) return {duration: d, error: err};
                try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
                const t0 = a.currentTime;
                await new Promise(r => setTimeout(r, 2500));
                const t1 = a.currentTime;
                let seekOk = null;
                if (d > 20) { a.currentTime = Math.min(d - 5, 15); await new Promise(r => setTimeout(r, 1200)); seekOk = a.currentTime > 14; }
                a.pause();
                return {duration: d, t0: t0, t_after_2_5s: t1, advanced: t1 > t0 + Math.min(1.0, d * 0.8), error: a.error ? a.error.code : null, seekOk, currentSrc: a.currentSrc};
            }""", i)
            res["src"] = src
            plays.append(res)
        rec["plays"] = plays
        rec["console_errors"] = errs
        rec["all_play_ok"] = all((x.get("error") is None and x.get("advanced") and (x.get("duration") or 0) > 0) for x in plays)
        out["pages"][name] = rec
        pg.close()
    br.close()
json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for k, v in out["pages"].items():
    print(k, "http", v["http_status"], "audio", v["audio_count"], "all_play_ok", v["all_play_ok"], "bad", v["http_ge400"], "errs", v["console_errors"][:2], v["label_check"])
    for x in v["plays"]:
        print("  ", x["src"], round(x.get("duration") or 0, 2), x.get("advanced"), x.get("error"), x.get("seekOk"))
