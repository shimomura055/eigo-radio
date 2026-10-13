# -*- coding: utf-8 -*-
"""委任_03 完成版Melos試聴ページ(GitHub Pages)Playwright実再生evidence。費用0円。"""
import json, os, re, time, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright
BASE = "https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_01/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "play_evidence_final.json")
def status(u):
    try: return urllib.request.urlopen(u, timeout=30).status
    except Exception as e: return getattr(e, "code", str(e))
code = None
for _ in range(40):
    code = status(BASE + "standard.html")
    if code == 200: break
    time.sleep(15)
res = {"base": BASE, "pages": {}}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    for name in ("index.html", "standard.html", "advanced.html"):
        U = BASE + name
        r = {"http": status(U), "audio_http": {}, "play": []}
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        errs = []; pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        bad = []; pg.on("response", lambda x: bad.append((x.url, x.status)) if x.status >= 400 else None)
        pg.goto(U, wait_until="load")
        html = pg.content()
        r["file_scheme_or_Cdrive"] = bool(re.search(r"file:///|[A-Za-z]:\\\\", html))
        srcs = pg.eval_on_selector_all("audio", "els=>els.map(e=>e.getAttribute('src'))")
        r["audio_count"] = len(srcs)
        for s in srcs: r["audio_http"][s] = status(urllib.parse.urljoin(U, s))
        for i, s in enumerate(srcs):
            x = pg.evaluate("""async (i)=>{const e=document.querySelectorAll('audio')[i];e.muted=true;e.preload='auto';
              await new Promise(r=>{if(e.readyState>=1)r();else{e.addEventListener('loadedmetadata',r,{once:true});e.addEventListener('error',r,{once:true});e.load();}});
              const d=e.duration; if(e.error) return {dur:d,err:e.error.code};
              try{await e.play();}catch(err){return {dur:d,err:String(err)}}
              const t0=Date.now();while(e.currentTime<0.8&&Date.now()-t0<8000){await new Promise(r=>setTimeout(r,100));}
              const o={t:e.currentTime,dur:d,err:null};e.pause();return o;}""", i)
            x["src"] = s; r["play"].append(x)
        r["play_ok"] = sum(1 for x in r["play"] if x.get("t", 0) >= 0.8 and not x.get("err") and x.get("dur", 0) > 0)
        r["http_ge400"] = bad; r["console_errors"] = errs
        r["all_ok"] = (r["http"] == 200 and not r["file_scheme_or_Cdrive"] and r["play_ok"] == r["audio_count"]
                       and all(v == 200 for v in r["audio_http"].values()) and not bad and not errs)
        res["pages"][name] = r; pg.close()
    b.close()
res["all_ok"] = all(v["all_ok"] for v in res["pages"].values())
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({n: {k: v for k, v in r.items() if k not in ("audio_http", "play")} for n, r in res["pages"].items()}, ensure_ascii=False, indent=1), res["all_ok"])
