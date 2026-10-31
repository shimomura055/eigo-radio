# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICES-DESIGN-01 委任_27: 再配達音声化Trial 限定試聴ページのPlaywright実再生evidence(有料APIなし、DEV/Trial専用)。er110_family_y_audio_play_verify_01.pyの派生(レベル切替のみ・noindex/限定注記の確認を追加)。
er019_nws2_play_verify_01.py派生。全audio実再生+seek、タブ切替(候補×レベル)、console error、HTTP>=400を確認する。"""
import argparse
import json

import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

ap = argparse.ArgumentParser()
ap.add_argument("--url", required=True)
ap.add_argument("--out", required=True)
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
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    html = pg.content()
    o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "section_count": pg.locator("section.lv").count(),
         "file_scheme_in_html": ("file:///" in html or "C:\\" in html or "C:/" in html),
         "trial_label_visible": "Trial・限定試聴・権利確認前のため転載不可" in pg.inner_text("body"), "kp_tables": pg.locator("table.kp").count(),
         "noindex_meta": ("noindex" in html and "nofollow" in html), "external_links": pg.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a=>a.href)")}
    tabs = {}
    for c in ("r0",):
        for l in ("std", "adv"):
            pg.click(f"button[data-k='{l}']")
            vis = pg.evaluate("() => Array.from(document.querySelectorAll('section.lv')).filter(s=>!s.classList.contains('hidden')).map(s=>s.id)")
            tabs[f"{c}_{l}"] = vis
    o["tab_switch_visible_sections"] = tabs
    o["tab_switch_ok"] = all(v == [k] for k, v in tabs.items())
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
        res["src"] = src
        plays.append(res)
    o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    o["seek_ok_all"] = all(x.get("seekOk") in (None, True) for x in plays)
    o["full_durations"] = {x["src"]: round(x["duration"], 2) for x in plays if "_full" in x["src"]}
    o["http_ge400"] = bad
    o["console_errors"] = errs
    out["page"] = o
    br.close()
json.dump(out, open(A.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out["page"], ensure_ascii=False)[:1800])
