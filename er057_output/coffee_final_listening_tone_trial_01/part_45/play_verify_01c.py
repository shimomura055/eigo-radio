# -*- coding: utf-8 -*-
"""委任_01C: 公開GitHub Pages上の異音候補確認ページのPlaywright実再生evidence。有料APIなし(静的ページ取得のみ)。"""
import json
import re
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/anomaly/index.html"
OUTJ = "er057_output/coffee_final_listening_tone_trial_01/part_45/pages_play_evidence_01c.json"
out = {"url": BASE}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    out["browser"] = br.version
    pg = br.new_page()
    errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(BASE, wait_until="networkidle")
    text = pg.inner_text("body")
    html = pg.content()
    out["http_status"] = resp.status
    out["audio_count"] = pg.locator("audio").count()
    out["img_count"] = pg.locator("img").count()
    out["img_loaded"] = pg.evaluate("Array.from(document.images).filter(i=>i.complete&&i.naturalWidth>0).length")
    out["row_count"] = pg.locator("tr[id]").count()
    out["jump_buttons"] = pg.locator("button.jump").count()
    out["label_check"] = {
        "EN_JA_gloss_label_present": bool(re.search(r"(English:|\bEN:|英語:|日本語gloss)", text)),
        "A2_B1_level_label_visible": bool(re.search(r"\(A2\)|\(B1\)|\bB1B\b", text)),
        "has_Standard": "Standard" in text, "has_Advanced": "Advanced" in text,
        "file_scheme_in_html": "file:///" in html or "C:\\" in html,
        "has_FOCUS": "FOCUS-STD-P3-coffee" in html, "has_timeline_Preview_Comment_FullStory": all(k in text for k in ("Preview", "Comment 1", "Comment 4", "Full Story Part 1", "Full Story Part 3", "In One Line")),
    }
    plays = []
    n = out["audio_count"]
    for i in range(n):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate("""async (i) => {
            const a = document.querySelectorAll('audio')[i];
            a.muted = true;
            await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
            const d = a.duration; const err = a.error ? a.error.code : null;
            if (err) return {duration: d, error: err};
            try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
            const t0 = a.currentTime;
            await new Promise(r => setTimeout(r, 2000));
            const t1 = a.currentTime;
            let seekOk = null;
            if (d > 20) { a.currentTime = Math.min(d - 5, 120); await new Promise(r => setTimeout(r, 1200)); seekOk = a.currentTime > 119; }
            a.pause();
            return {duration: d, t0: t0, t_after_2s: t1, advanced: t1 > t0 + Math.min(0.8, d * 0.6), error: a.error ? a.error.code : null, seekOk, currentSrc: a.currentSrc};
        }""", i)
        res["src"] = src
        plays.append(res)
    out["plays"] = plays
    out["all_play_ok"] = all((x.get("error") is None and x.get("advanced") and (x.get("duration") or 0) > 0) for x in plays)
    # ジャンプボタン: 各levelの最初の1個+FOCUSボタンで全編audioのcurrentTimeが目標へ移るか
    jumps = []
    for k in range(pg.locator("button.jump").count()):
        b = pg.locator("button.jump").nth(k)
        lv, t = b.get_attribute("data-lv"), float(b.get_attribute("data-t"))
        if k % 9 != 0 and k >= 4:
            continue
        b.scroll_into_view_if_needed()
        b.click()
        pg.wait_for_timeout(1500)
        cur = pg.evaluate("(lv)=>{const a=document.getElementById('ep_'+lv); a.pause(); return a.currentTime}", lv)
        jumps.append({"level": lv, "target": t, "currentTime_after_click": round(cur, 2), "ok": abs(cur - t) < 3.0})
    out["jump_tests"] = jumps
    out["jump_all_ok"] = all(j["ok"] for j in jumps)
    out["http_ge400"] = bad
    out["console_errors"] = errs
    br.close()
json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("http", out["http_status"], "audio", out["audio_count"], "imgs", out["img_loaded"], "/", out["img_count"], "rows", out["row_count"], "all_play_ok", out["all_play_ok"],
      "jump_all_ok", out["jump_all_ok"], "bad", out["http_ge400"], "errs", out["console_errors"][:2])
print(out["label_check"])
for x in plays[:4] + plays[-3:]:
    print("  ", x["src"], round(x.get("duration") or 0, 2), x.get("advanced"), x.get("error"), x.get("seekOk"))
print("fails:", [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))])
