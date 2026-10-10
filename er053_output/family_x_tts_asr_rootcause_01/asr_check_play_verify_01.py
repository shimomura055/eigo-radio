# -*- coding: utf-8 -*-
"""FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_20: Pages上の3 audio実再生確認。課金APIなし。"""
import json, urllib.request, time
from playwright.sync_api import sync_playwright
B="https://shimomura055.github.io/eigo-radio/user_test/meta_regen_01_asr_check/"
out={"index_url":B+"index.html","http":{},"play":[]}
for u in ["index.html","attempt1.mp3","attempt2.mp3","attempt3.mp3"]:
    out["http"][B+u]=urllib.request.urlopen(B+u,timeout=60).status
html=urllib.request.urlopen(B+"index.html").read().decode("utf8")
out["contains_file_scheme_or_Cdrive"]=("file:///" in html) or ("C:\\" in html)
with sync_playwright() as p:
    br=p.chromium.launch(headless=True,args=["--autoplay-policy=no-user-gesture-required"])
    pg=br.new_page(); pg.goto(B+"index.html",wait_until="networkidle")
    n=pg.locator("audio").count(); out["audio_count"]=n
    for i in range(n):
        pg.evaluate("i=>{document.querySelectorAll('audio').forEach(a=>a.pause());const a=document.querySelectorAll('audio')[i];a.currentTime=0;return a.play()}",i)
        time.sleep(3)
        r=pg.evaluate("i=>{const a=document.querySelectorAll('audio')[i];return {src:a.currentSrc,currentTime:a.currentTime,paused:a.paused,readyState:a.readyState,duration:a.duration,error:a.error&&a.error.code}}",i)
        out["play"].append(r)
    br.close()
json.dump(out,open("er053_output/family_x_tts_asr_rootcause_01/asr_check_play_evidence_01.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False,indent=1))
