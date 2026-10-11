# Playwright実再生evidence (Trial 01A)。全<audio>のHTTP200・metadata・実再生(currentTime進行)・combo通し再生・file:////C:\混入なし。
import json, sys, time, re
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
OUT = sys.argv[2]
res = {"url": URL, "audios": [], "console_errors": [], "bad_http": []}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page()
    pg.on("console", lambda m: res["console_errors"].append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: res["bad_http"].append([r.url, r.status]) if r.status >= 400 else None)
    r = pg.goto(URL, wait_until="load")
    res["page_status"] = r.status
    html = pg.content()
    res["has_file_url"] = ("file:///" in html)
    res["has_C_drive"] = bool(re.search(r"[A-Za-z]:\\|C:/", html))
    names = pg.eval_on_selector_all("audio", "els=>els.map(e=>e.dataset.name)")
    res["audio_count"] = len(names)
    for n in names:
        d = pg.evaluate("""async (n)=>{const a=document.querySelector(`audio[data-name="${n}"]`);
          a.preload='auto';
          await new Promise((ok,ng)=>{a.addEventListener('loadedmetadata',ok,{once:true});a.addEventListener('error',()=>ng('err'),{once:true});a.load();setTimeout(()=>ng('timeout'),20000)}).catch(e=>{return});
          const dur=a.duration; let t0=0,t1=0,err=null;
          try{a.muted=true;await a.play();await new Promise(r=>setTimeout(r,900));t1=a.currentTime;a.pause();}catch(e){err=String(e)}
          return {dur:dur,t:t1,err:err,src:a.currentSrc,rowtext:(a.closest('tr')||{}).innerText?.length||0}}""", n)
        d["name"] = n
        d["ok"] = bool(d["dur"] and d["dur"] > 0 and d["t"] > 0.3 and not d["err"])
        res["audios"].append(d)
    # combo通し再生(A3/B4を選択、全5部品が順に再生されること)
    pg.select_option("#selA", "3"); pg.select_option("#selB", "4")
    seen = []
    pg.click("#comboPlay")
    t0 = time.time()
    while time.time() - t0 < 90:
        s = pg.inner_text("#comboStatus")
        if not seen or seen[-1] != s:
            seen.append(s)
        if "再生完了" in s or "エラー" in s:
            break
        time.sleep(0.3)
    res["combo_status_trace"] = seen
    res["combo_ok"] = bool(seen and "再生完了" in seen[-1])
    pg.screenshot(path=OUT + "_screenshot.png", full_page=False)
    b.close()
res["all_audio_ok"] = all(a["ok"] for a in res["audios"])
json.dump(res, open(OUT + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("audio", res["audio_count"], "ok", sum(a["ok"] for a in res["audios"]), "combo", res["combo_ok"], "bad_http", res["bad_http"][:3], "file_url", res["has_file_url"], "Cdrive", res["has_C_drive"], "console_err", len(res["console_errors"]))
