# -*- coding: utf-8 -*-
"""委任_03: 公開GitHub Pages上の最終試聴ページ(v2)のPlaywright実再生evidence。有料APIなし(静的ページ取得のみ)。"""
import json, re
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

BASE = "https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/final_v2/"
PAGES = ["index.html", "standard/index.html", "advanced/index.html"]
OUTJ = "er057_output/coffee_final_listening_tone_trial_01/part_final/pages_play_evidence_04.json"
out = {"base": BASE, "pages": {}}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    out["browser"] = br.version
    for path in PAGES:
        pg = br.new_page()
        errs, bad = [], []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
        resp = pg.goto(BASE + path, wait_until="networkidle")
        text, html = pg.inner_text("body"), pg.content()
        o = {"url": BASE + path, "http_status": resp.status, "audio_count": pg.locator("audio").count(), "row_count": pg.locator("tr[id]").count(),
             "jump_buttons": pg.locator("button.jump").count(), "kp_tables": pg.locator("table.kp").count()}
        o["label_check"] = {
            "EN_JA_gloss_label_present": bool(re.search(r"(English:|\bEN:|英語:|日本語:|日本語gloss|\bJA:)", text)),
            "A2_B1_level_label_visible": bool(re.search(r"\(A2\)|\(B1\)|\bB1B\b|b1b", text + html)),
            "file_scheme_in_html": "file:///" in html or "C:\\" in html or "C:/" in html,
            "has_Standard": "Standard" in text, "has_Advanced": "Advanced" in text,
            "has_roles": all(k in text for k in ("Preview", "Comment 1", "Comment 4", "Full Story Part 1", "Full Story Part 3", "In One Line", "Key Phrase 1", "Key Phrase 5")) if path != "advanced/index.html" and path != "standard/index.html" else all(k in text for k in ("Preview", "Comment 1", "Comment 4", "Full Story Part 1", "Full Story Part 3", "In One Line", "Key Phrase 1", "Key Phrase 5")),
            "tts_mode_stated": "Standard同期" in text, "voice_stated": "Voice:" in text, "slowdown_shown": ("6%減速適用" in text) if path != "advanced/index.html" else ("減速処理なし" in text),
            "origin_regen_reuse_shown": ("再生成" in text and "再利用" in text), "style_names_shown": all(k in text for k in ("A5", "B5")) , "K2_unapplied_text_absent": "K2未適用" not in text, "adv_KP_K2_shown": ("KP英語=K2" in text) if path != "standard/index.html" else None}
        plays = []
        for i in range(o["audio_count"]):
            src = pg.locator("audio").nth(i).get_attribute("src")
            res = pg.evaluate("""async (i) => {
                const a = document.querySelectorAll('audio')[i]; a.muted = true;
                await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
                const d = a.duration; const err = a.error ? a.error.code : null;
                if (err) return {duration: d, error: err};
                try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
                const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1500)); const t1 = a.currentTime;
                let seekOk = null; if (d > 20) { const tgt = Math.min(d - 5, 120); a.currentTime = tgt; await new Promise(r => setTimeout(r, 1000)); seekOk = Math.abs(a.currentTime - tgt) < 2.5; }
                a.pause();
                return {duration: d, advanced: t1 > t0 + Math.min(0.6, d * 0.5), error: a.error ? a.error.code : null, seekOk};
            }""", i)
            res["src"] = src
            plays.append(res)
        o["plays_summary"] = {"n": len(plays), "ok": sum(1 for x in plays if x.get("error") is None and x.get("advanced") and (x.get("duration") or 0) > 0),
                              "failed": [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))], "seek_ok_all_long": all(x.get("seekOk") in (None, True) for x in plays)}
        o["plays"] = plays
        jumps = []
        for k in range(pg.locator("button.jump").count()):
            b = pg.locator("button.jump").nth(k)
            lv, t = b.get_attribute("data-lv"), float(b.get_attribute("data-t"))
            if k % 5 != 0:
                continue
            b.scroll_into_view_if_needed(); b.click(); pg.wait_for_timeout(900)
            cur = pg.evaluate("(lv)=>{const a=document.getElementById('main_'+lv); a.muted=true; a.pause(); return a.currentTime}", lv)
            jumps.append({"level": lv, "target": t, "currentTime_after_click": round(cur, 2), "ok": abs(cur - t) < 3.0})
        o["jump_tests"] = jumps; o["jump_all_ok"] = all(j["ok"] for j in jumps)
        o["http_ge400"] = bad; o["console_errors"] = errs
        out["pages"][path] = o
        print(path, o["http_status"], o["plays_summary"]["ok"], "/", o["plays_summary"]["n"], "jump", o["jump_all_ok"], "bad", bad, "errs", errs[:2], o["label_check"], flush=True)
        pg.close()
    # 資産HTTP 200(episode mp3)
    pg = br.new_page()
    out["asset_status"] = {}
    for a in ("audio/Coffee_Standard_final_v2.mp3", "audio/Coffee_Advanced_final_v2.mp3", "audio/std_topic_intro_OLD.mp3"):
        r = pg.request.get(BASE + a)
        out["asset_status"][a] = {"status": r.status, "bytes": len(r.body())}
    br.close()
json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(out["asset_status"])
