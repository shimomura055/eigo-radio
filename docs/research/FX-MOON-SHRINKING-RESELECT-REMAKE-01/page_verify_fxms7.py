# -*- coding: utf-8 -*-
"""FXMS7 候補ページのPlaywright検証(API 0)。用法: python page_verify_fxms7.py <base_url_ending_slash|--local dir> out.json"""
import sys, json, re, functools, http.server, threading
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
arg, out = sys.argv[1], sys.argv[-1]
if arg == "--local":
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=sys.argv[2])
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h); threading.Thread(target=s.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{s.server_address[1]}/"
else: base = arg
errs, bad = [], []
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); pg = br.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    r = pg.goto(base + "index.html", wait_until="networkidle"); text, html = pg.inner_text("body"), pg.content()
    n = pg.locator("audio").count(); plays = []
    for i in range(n):
        res = pg.evaluate("""async (i)=>{const a=document.querySelectorAll('audio')[i];a.muted=true;await new Promise(r=>{if(a.readyState>=1)r();else{a.addEventListener('loadedmetadata',r,{once:true});a.addEventListener('error',r,{once:true});a.load();}});const d=a.duration;if(a.error)return{d,err:a.error.code};try{await a.play();}catch(e){return{d,err:'play'}};const t0=a.currentTime;await new Promise(r=>setTimeout(r,700));const t1=a.currentTime;a.pause();return{d,adv:t1>t0+0.3,err:null}}""", i)
        res["src"] = pg.locator("audio").nth(i).get_attribute("src"); plays.append(res)
    o = {"base": base, "http": r.status, "audio_count": n, "plays_ok": sum(1 for x in plays if x["err"] is None and x.get("adv") and x["d"] > 0),
         "plays_failed": [x["src"] for x in plays if not (x["err"] is None and x.get("adv"))],
         "equals5_count": text.count("====="), "file_scheme": ("file:///" in html or "C:\\" in html),
         "has_candidate_label": "完成候補・ユーザー試聴待ち" in text, "has_not_official": "正式公開ではありません" in text,
         "http_ge400": bad, "console_errors": errs, "audio_srcs": [x["src"] for x in plays]}
    br.close()
json.dump(o, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: v for k, v in o.items() if k != "audio_srcs"})
