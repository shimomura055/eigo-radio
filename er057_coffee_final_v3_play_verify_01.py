# -*- coding: utf-8 -*-
"""委任_02 公開Pages上のFinal v3試聴ページPlaywright実再生evidence(有料APIなし)。"""
import json, re, sys
from playwright.sync_api import sync_playwright
BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_final_v3/"
OUTP = "er057_output/coffee_final_audio_assembly_01/pages_play_evidence_v3_01.json"
M = json.load(open("er057_output/coffee_final_audio_assembly_01/assembly_manifest_v3_01.json", encoding="utf-8"))["levels"]
out = {"base": BASE, "pages": {}}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); out["browser"] = br.version
    for path in ("index.html", "standard/index.html", "advanced/index.html"):
        pg = br.new_page(); errs, bad = [], []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
        resp = pg.goto(BASE + path, wait_until="networkidle")
        text, html = pg.inner_text("body"), pg.content()
        o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "tr_count": pg.locator("tr[id]").count(),
             "file_scheme_in_html": ("file:///" in html or "C:\\" in html or "C:/" in html),
             "A2_B1_label_visible": bool(re.search(r"\(A2\)|\(B1\)|B1B", text)),
             "has_standard_label": "Standard" in text, "has_advanced_label": "Advanced" in text,
             "kp_two_column_tables": pg.locator("table.kp").count(), "kp_label_strings": bool(re.search(r"English:|英語:|EN:|日本語:|JA:", text)),
             "has_slowdown_text": "6%減速" in text, "has_IOL_new": "Other costs also matter" in text or "cups and labor" in text,
             "has_secondary_note": "Secondary" in text, "has_known_click_note": "13.3秒" in text or "39.85秒" in text,
             "has_voice_label": text.count("Voice:"), "has_start_seconds": len(re.findall(r"秒〜", text)), "jump_buttons": pg.locator("button.jump").count()}
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
        o["full_durations"] = {x["src"]: round(x["duration"], 2) for x in plays if "final_v3" in x["src"]}
        o["http_ge400"] = bad; o["console_errors"] = errs
        out["pages"][path] = o; pg.close()
    br.close()
for lv, nm in (("std", "Coffee_Standard_final_v3"), ("adv", "Coffee_Advanced_final_v3")):
    out.setdefault("expected_full_duration", {})[nm] = M[lv]["duration_seconds"]
json.dump(out, open(OUTP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out["pages"].items(): print(k, {a: b for a, b in v.items() if a not in ("plays_failed",)})
