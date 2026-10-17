# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_17: 公開Pages上の試聴ページ(index/standard/advanced)のPlaywright実再生evidence(有料APIなし)。
er019_bape_play_verify_04.py派生。各audio要素を実再生(muted、1.2秒進行)し、長尺は末尾付近へseekして確認する。"""
import argparse
import json

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--url", required=True)
ap.add_argument("--out", required=True)
A = ap.parse_args()
BASE = A.url.rsplit("index.html", 1)[0]
PAGES = ["index.html", "standard.html", "advanced.html"]
JS = """async (i) => {
    const a = document.querySelectorAll('audio')[i]; a.muted = true;
    await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
    const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
    try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
    const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1200)); const t1 = a.currentTime;
    let seekOk = null; if (d > 20) { const tgt = d - 5; a.currentTime = tgt; await new Promise(r => setTimeout(r, 800)); seekOk = Math.abs(a.currentTime - tgt) < 2.5; }
    a.pause(); a.removeAttribute('src'); a.load(); return {duration: d, advanced: t1 > t0 + 0.5, error: null, seekOk};
}"""
out = {"base": BASE, "pages": {}}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    out["browser"] = br.version
    for name in PAGES:
        pg = br.new_page()
        errs, bad = [], []
        pg.on("console", lambda m, errs=errs: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
        pg.on("response", lambda r, bad=bad: bad.append((r.url, r.status)) if r.status >= 400 else None)
        resp = pg.goto(BASE + name, wait_until="networkidle")
        text, html = pg.inner_text("body"), pg.content()
        o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(),
             "file_scheme_in_html": ("file:///" in html or "C:\\" in html or "C:/" in html),
             "kp_tables": pg.locator("table.kp").count(), "has_pww_section": "PASS_WITH_WARNING" in text or "事後試聴" in text,
             "level_label_leak": any(s in text for s in ("(A2)", "(B1)", "B1B")),
             "links": pg.eval_on_selector_all("a", "els => els.map(e => e.getAttribute('href'))")}
        plays = []
        for i in range(o["audio_count"]):
            src = pg.locator("audio").nth(i).get_attribute("src")
            res = pg.evaluate(JS, i)
            res["src"] = src
            plays.append(res)
        o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
        o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
        o["seek_ok_all"] = all(x.get("seekOk") in (None, True) for x in plays)
        o["full_durations"] = {x["src"]: round(x["duration"], 2) for x in plays if x["src"] and "_full.mp3" in x["src"]}
        o["http_ge400"] = bad
        o["console_errors"] = errs
        out["pages"][name] = o
        pg.close()
    br.close()
json.dump(out, open(A.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for n, o in out["pages"].items():
    print(n, json.dumps({k: v for k, v in o.items() if k != "links"}, ensure_ascii=True)[:900])
