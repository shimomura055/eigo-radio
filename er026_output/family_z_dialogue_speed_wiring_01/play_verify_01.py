# -*- coding: utf-8 -*-
"""公開試聴ページの全audio: HTTP 200/Content-Length>0 + Playwright実再生(muted、currentTime進行)。API 0。
usage: python play_verify_ab_01.py <url> <out.json>"""
import json, sys, urllib.request
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
url, out = sys.argv[1], sys.argv[2]
res = {"url": url, "page_status": None, "audios": []}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page(); r = pg.goto(url, wait_until="load"); res["page_status"] = r.status
    srcs = pg.eval_on_selector_all("audio", "els=>els.map(e=>e.src)")
    res["audio_count"] = len(srcs)
    for i, s in enumerate(srcs):
        rec = {"i": i, "src": s}
        try:
            req = urllib.request.Request(s, method="GET"); resp = urllib.request.urlopen(req, timeout=60)
            body = resp.read(); rec["http"] = resp.status; rec["bytes"] = len(body)
        except Exception as e:
            rec["http"] = f"ERR {e}"
        r2 = pg.evaluate("""async (i)=>{const a=document.querySelectorAll('audio')[i];a.muted=true;a.preload='auto';
            try{await a.play();}catch(e){return {err:String(e)}}
            const t0=Date.now();while(Date.now()-t0<6000 && a.currentTime<0.6){await new Promise(r=>setTimeout(r,100));}
            const o={t:a.currentTime,dur:a.duration,err:a.error?a.error.code:null};a.pause();return o;}""", i)
        rec["play"] = r2; rec["ok"] = rec.get("http") == 200 and rec.get("bytes", 0) > 1000 and r2.get("t", 0) >= 0.5 and not r2.get("err") and not r2.get("dur") != r2.get("dur")
        res["audios"].append(rec)
    b.close()
res["all_ok"] = res["page_status"] == 200 and all(a["ok"] for a in res["audios"])
res["ok_count"] = sum(a["ok"] for a in res["audios"])
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(res["page_status"], res["audio_count"], res["ok_count"], res["all_ok"])
