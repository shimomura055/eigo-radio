# -*- coding: utf-8 -*-
import json, time, urllib.request
from playwright.sync_api import sync_playwright
BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_kp_explanation_style_trial_01/"
M = json.load(open("er057_output/kp_en_explanation_style_trial_01/measurements.json", encoding="utf-8"))
out = {"base": BASE}
for _ in range(40):
    try:
        if urllib.request.urlopen(BASE + "audio/kp1_P8_solo.mp3").status == 200: break
    except Exception: time.sleep(15)
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); out["browser"] = br.version
    pg = br.new_page(); errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    text, html = pg.inner_text("body"), pg.content()
    o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "row_ids": [e.get_attribute("id") for e in pg.locator("tr[id]").all()],
         "file_scheme_in_html": ("file:///" in html or "C:\\" in html or "C:/" in html), "rows_with_core_wpm": text.count("発話WPM(core"), "rows_with_mean3": text.count("3サンプル平均"), "prompt_details": pg.locator("details").count()}
    plays = []
    for i in range(o["audio_count"]):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate("""async (i) => {
            const a = document.querySelectorAll('audio')[i]; a.muted = true;
            await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
            const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
            try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
            const t0 = a.currentTime; await new Promise(r => setTimeout(r, 900)); const t1 = a.currentTime;
            a.pause(); return {duration: d, advanced: t1 > t0 + 0.4, error: null};
        }""", i)
        res["src"] = src; plays.append(res)
    o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    chk = []
    for x in plays:
        kp = x["src"].split("/")[-1].split("_")[0][2:]; c = x["src"].split("/")[-1].split("_")[1]
        if x["src"].endswith("_solo.mp3"):
            chk.append({"src": x["src"], "page_s": round(x["duration"], 2), "measured_s": M[kp]["rows"][c]["duration_s"], "ok": abs(x["duration"] - M[kp]["rows"][c]["duration_s"]) < 0.6})
        else:
            chk.append({"src": x["src"], "page_s": round(x["duration"], 2), "measured_s": M[kp]["rows"][c]["seq_duration_s"], "ok": abs(x["duration"] - M[kp]["rows"][c]["seq_duration_s"]) < 0.6})
    o["duration_vs_measured"] = chk; o["duration_all_ok"] = all(c["ok"] for c in chk)
    o["http_ge400"] = bad; o["console_errors"] = errs; o["plays"] = plays
    out["page"] = o; br.close()
json.dump(out, open("er057_output/kp_en_explanation_style_trial_01/pages_play_evidence_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: v for k, v in o.items() if k not in ("plays", "duration_vs_measured")})
