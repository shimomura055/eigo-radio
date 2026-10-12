# -*- coding: utf-8 -*-
"""委任_01(PACE-02) 公開Pages上の試聴ページPlaywright実再生evidence(有料APIなし)。"""
import json, re
from playwright.sync_api import sync_playwright
BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_pace_trial_02/"
S = json.load(open("er057_output/pace_trial_02/summary_02.json", encoding="utf-8"))
out = {"base": BASE}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); out["browser"] = br.version
    pg = br.new_page(); errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    text, html = pg.inner_text("body"), pg.content()
    o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "row_ids": [e.get_attribute("id") for e in pg.locator("tr[id]").all()],
         "file_scheme_in_html": ("file:///" in html or "C:\\" in html or "C:/" in html),
         "neutral_names_only(PD1-8/F5)": not re.search(r"Standard 6%|Final v2|APPROVED", text),
         "has_prompt_details": pg.locator("details").count(), "has_asr_row": text.count("Primary ASR判定"), "has_warning_row": text.count("警告")}
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
            a.pause(); return {duration: d, advanced: t1 > t0 + 0.5, error: null, seekOk};
        }""", i)
        res["src"] = src; plays.append(res)
    o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    o["seek_ok_all"] = all(x.get("seekOk") in (None, True) for x in plays)
    # 連結音声長 = Part合計+1.6秒 の照合
    chk = []
    for c, r in S.items():
        d = {x["src"]: x["duration"] for x in plays}
        parts = [d[f"audio/{c}_p{n}.mp3"] for n in (1, 2, 3)]; allv = d[f"audio/{c}_all.mp3"]
        chk.append({"cand": c, "sum_parts": round(sum(parts), 2), "all": round(allv, 2), "ok": abs(sum(parts) + 1.6 - allv) < 0.5})
    o["concat_len_check"] = chk; o["concat_ok_all"] = all(x["ok"] for x in chk)
    o["http_ge400"] = bad; o["console_errors"] = errs; o["plays"] = plays
    o["order_slow_first"] = o["row_ids"] == sorted(S, key=lambda c: S[c]["total_wpm"])
    out["page"] = o; br.close()
json.dump(out, open("er057_output/pace_trial_02/pages_play_evidence_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: v for k, v in o.items() if k not in ("plays", "concat_len_check")})
