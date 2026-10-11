# -*- coding: utf-8 -*-
"""OPEN-258 Phase0 委任_02: 試聴ページのPages HTTP+Play実再生。課金APIなし。"""
import json, urllib.request, time, re
from playwright.sync_api import sync_playwright
B="https://shimomura055.github.io/eigo-radio/user_test/open258_phase0_listen_01/"
html=urllib.request.urlopen(B+"index.html",timeout=60).read().decode("utf8")
srcs=re.findall(r'src="([^"]+\.mp3)"',html)
out={"index_url":B+"index.html","http":{},"play":[]}
for u in ["index.html"]+srcs: out["http"][B+u]=urllib.request.urlopen(B+u,timeout=60).status
out["contains_file_scheme_or_Cdrive"]=("file:///" in html) or ("C:\\" in html)
with sync_playwright() as p:
    br=p.chromium.launch(headless=True,args=["--autoplay-policy=no-user-gesture-required"])
    pg=br.new_page(); pg.goto(B+"index.html",wait_until="networkidle")
    out["audio_count"]=pg.locator("audio").count()
    for i in range(out["audio_count"]):
        pg.evaluate("i=>{document.querySelectorAll('audio').forEach(a=>a.pause());const a=document.querySelectorAll('audio')[i];a.currentTime=0;return a.play()}",i)
        time.sleep(1.2)
        r=pg.evaluate("i=>{const a=document.querySelectorAll('audio')[i];return {src:a.currentSrc,currentTime:a.currentTime,paused:a.paused,readyState:a.readyState,duration:a.duration,error:a.error&&a.error.code}}",i)
        r["ok"]=r["currentTime"]>0 and not r["paused"] and r["readyState"]>=3 and r["error"] is None
        out["play"].append(r)
    br.close()
out["all_ok"]=all(r["ok"] for r in out["play"]) and all(v==200 for v in out["http"].values())
json.dump(out,open("er053_output/open258_phase0_trial_01/listen_play_evidence_01.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
print(out["all_ok"],out["audio_count"])
