# -*- coding: utf-8 -*-
"""委任_05B 試聴ページのPlaywright実再生evidence(GitHub Pages上、費用0円)。出力: er058_output/PLAY_EVIDENCE_05B.md と .json"""
import json, os, re, sys, time, urllib.request
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://shimomura055.github.io/eigo-radio/user_test/asr_misread_listen_01/"
URL = BASE + "index.html"


def status(u):
    try:
        return urllib.request.urlopen(u, timeout=30).status
    except Exception as e:  # noqa
        return getattr(e, "code", str(e))


code = None
for _ in range(50):
    code = status(URL)
    if code == 200:
        break
    time.sleep(15)
res = {"index_url": URL, "index_http": code, "http": {}, "play": {}}
if code == 200:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(URL)
        html = pg.content()
        res["contains_file_scheme_or_Cdrive"] = bool(re.search(r"file:///|[A-Za-z]:\\\\", html))
        rows = pg.query_selector_all(".row")
        res["row_count"] = len(rows)
        res["rows_with_voice_and_script"] = sum(1 for r in rows if "Voice:" in r.inner_text() and "原稿:" in r.inner_text())
        res["rows_with_asr_table"] = sum(1 for r in rows if r.query_selector("table.asr") is not None)
        res["rows_with_radio3"] = sum(1 for r in rows if len(r.query_selector_all("input[type=radio]")) == 3)
        auds = pg.query_selector_all("audio")
        res["audio_count"] = len(auds)
        res["min_audio_width_px"] = min(a.bounding_box()["width"] for a in auds)
        srcs = pg.eval_on_selector_all("audio", "els=>els.map(e=>e.getAttribute('src'))")
        for s in srcs:
            u = urllib.request.urljoin(URL, s)
            res["http"][s] = status(u)
        ok = 0
        for i, a in enumerate(auds):
            a.scroll_into_view_if_needed()
            r = pg.evaluate("""async (i)=>{const e=document.querySelectorAll('audio')[i];e.muted=true;e.preload='auto';
              try{await e.play();}catch(err){return {err:String(err)}}
              const t0=Date.now();while(e.currentTime<0.4&&Date.now()-t0<8000){await new Promise(r=>setTimeout(r,100));}
              const out={t:e.currentTime,dur:e.duration,err:e.error?e.error.code:null};e.pause();return out;}""", i)
            res["play"][srcs[i]] = r
            if r.get("t", 0) >= 0.4 and not r.get("err"):
                ok += 1
        res["play_ok"] = ok
        # 結果テキスト化ボタンの動作確認
        pg.check("input[name=r1][value='不明']")
        pg.click("#mk")
        res["result_text_first_line"] = pg.input_value("#out").splitlines()[0]
        res["visible_text_leak_spec_names"] = re.findall(r"CURRENT_SPEC|APPROVED_FOR_PRODUCTION", pg.inner_text("body"))
        b.close()
    res["all_ok"] = (res["play_ok"] == res["audio_count"] == res["row_count"] and all(v == 200 for v in res["http"].values())
                     and not res["contains_file_scheme_or_Cdrive"] and res["min_audio_width_px"] >= 360
                     and res["rows_with_voice_and_script"] == res["row_count"] and res["rows_with_asr_table"] == res["row_count"])
json.dump(res, open(os.path.join(ROOT, "er058_output", "PLAY_EVIDENCE_05B.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("http", "play")}, ensure_ascii=False, indent=1))
print("http non-200:", [k for k, v in res["http"].items() if v != 200])
