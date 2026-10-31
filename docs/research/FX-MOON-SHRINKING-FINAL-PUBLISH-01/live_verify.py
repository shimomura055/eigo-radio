import urllib.request,hashlib,json,os,re,time
base="https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/"
root="user_test/family_x_moon_shrinking_reselect_01"
files=["index.html"]+["audio/"+f for f in sorted(os.listdir(root+"/audio"))]
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u+("&" if "?" in u else "?")+"cb=%d"%time.time(),headers={"Cache-Control":"no-cache"}),timeout=60)
    return r.status,r.read()
out={"url":base,"n_audio":len(files)-1,"bad":[],"files":{}}
for _ in range(10):
    s,d=get(base+"index.html"); h=d.decode()
    if "正式公開(2026-10-29)" in h: break
    time.sleep(60)
for f in files:
    s,d=get(base+f)
    loc=open(f"{root}/{f}","rb").read()
    m=hashlib.sha256(d).hexdigest()==hashlib.sha256(loc).hexdigest()
    out["files"][f]={"status":s,"len":len(d),"match_repo":m}
    if s!=200 or not d or not m: out["bad"].append(f)
out["new_text_count"]=h.count("正式公開(2026-10-29)")+0
out["new_text2_count"]=h.count("ユーザー試聴PASS・公開承認 2026-10-29")
out["old_text_count"]=sum(h.count(k) for k in ["完成候補","試聴待ち","試聴PASSは未取得"])
out["equals_count"]=h.count("=====")
out["std_adv_audio_urls"]=len(re.findall(r"src='audio/[^']+'",h))
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.on("response",lambda r: errs.append("HTTP%d %s"%(r.status,r.url)) if r.status>=400 else None)
    pg.goto(base+"index.html?cb=%d"%time.time(),wait_until="load"); pg.wait_for_timeout(1500)
    out["playwright_text_new"]=pg.inner_text("div.note")
    b.close()
out["console_errors"]=errs
json.dump(out,open("docs/research/FX-MOON-SHRINKING-FINAL-PUBLISH-01/live_verify_01.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(files),"bad",out["bad"],{k:v for k,v in out.items() if k not in("files",)})
