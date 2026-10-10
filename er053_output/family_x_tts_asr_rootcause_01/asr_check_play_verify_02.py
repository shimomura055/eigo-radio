# -*- coding: utf-8 -*-
"""FAMILY-X-TTS-ASR-ROOTCAUSE-01 委任_22: Muse追加5 audioのPages HTTP+Play実再生。課金APIなし。"""
import json, urllib.request, time
from playwright.sync_api import sync_playwright
B="https://shimomura055.github.io/eigo-radio/user_test/meta_regen_01_asr_check/"
names=["muse_comment_2_take2_fail","muse_comment_2_take1_ref","muse_in_one_line_take1","muse_in_one_line_take2","muse_in_one_line_take3"]
out={"index_url":B+"index.html","http":{},"play":[]}
for u in ["index.html"]+[n+".mp3" for n in names]:
    out["http"][B+u]=urllib.request.urlopen(B+u,timeout=60).status
html=urllib.request.urlopen(B+"index.html").read().decode("utf8")
out["contains_file_scheme_or_Cdrive"]=("file:///" in html) or ("C:\\" in html)
with sync_playwright() as p:
    br=p.chromium.launch(headless=True,args=["--autoplay-policy=no-user-gesture-required"])
    pg=br.new_page(); pg.goto(B+"index.html",wait_until="networkidle")
    n=pg.locator("audio").count(); out["audio_count"]=n
    for i in range(3,n):
        pg.evaluate("i=>{document.querySelectorAll('audio').forEach(a=>a.pause());const a=document.querySelectorAll('audio')[i];a.currentTime=0;return a.play()}",i)
        time.sleep(3)
        out["play"].append(pg.evaluate("i=>{const a=document.querySelectorAll('audio')[i];return {src:a.currentSrc,currentTime:a.currentTime,paused:a.paused,readyState:a.readyState,duration:a.duration,error:a.error&&a.error.code}}",i))
    br.close()
json.dump(out,open("er053_output/family_x_tts_asr_rootcause_01/asr_check_play_evidence_02.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False))
