# -*- coding: utf-8 -*-
"""RISK-FLAGGER-PRODUCTION-WIRING-01 delegation 18: GitHub Pages public verification (7 items) + Play real-playback evidence.
No paid API. Run from repo root with .venv python (PYTHONUTF8=1)."""
import json, re, sys, io, urllib.request, urllib.parse
import soundfile as sf
from playwright.sync_api import sync_playwright

BASE = "https://shimomura055.github.io/eigo-radio"
D = BASE + "/user_test/coffee_prices_l3_01"
R = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01"
EV = "er053_output/risk_flagger_production_wiring_01/l3_run_01"
q = lambda s: urllib.parse.quote(s, safe="")
JA = "相場は下落、値札は居残り。コーヒー価格の「時差ぼけ」"
EN = {"a2": "Coffee Prices Fall, but Store Prices Stay: Coffee’s “Jet Lag”",
      "b1b": "Market Prices Fall, Price Tags Stay Put: Coffee Prices’ “Jet Lag”"}
LEVEL = {"a2": "A2", "b1b": "B1"}
UNI = {lv: f"{BASE}/user_test/unified.html?src=user_test%2Fcoffee_prices_l3_01%2F{lv}%2Fplayer.html&level={LEVEL[lv]}&en={q(EN[lv])}&ja={q(JA)}" for lv in EN}
norm = lambda s: re.sub(r"\s+", " ", s).strip()


def head(url):
    req = urllib.request.Request(url, method="GET")
    try:
        r = urllib.request.urlopen(req, timeout=60)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code


def get(url):
    return urllib.request.urlopen(url, timeout=120).read()


out = {"base": BASE, "unified_urls": UNI, "index_url": D + "/index.html"}
# (1) HTTP 200
urls = [D + "/index.html", D + "/a2/player.html", D + "/b1b/player.html", D + "/a2/web/episode.mp3", D + "/b1b/web/episode.mp3"] + list(UNI.values())
out["item1_http"] = {u: head(u) for u in urls}
# metadata
meta = {lv: json.load(open(f"{R}/{lv}/audit/tts_generation_results.json", encoding="utf-8")) for lv in EN}
styles = {}
for lv, m in meta.items():
    s = set()
    for v in m["segments"].values():
        s.add(v["style_prefix"])
    for r, kp in m["key_phrases"].items():
        for part in kp.values():
            if isinstance(part, dict) and part.get("style_prefix"):
                s.add(part["style_prefix"])
    styles[lv] = s

with sync_playwright() as p:
    br = p.chromium.launch(headless=True)
    pg = br.new_page()
    pg.goto(D + "/index.html", wait_until="networkidle")
    dom = pg.content()
    text = pg.inner_text("body")
    open(f"{EV}/pages_index_dom_dump_01.html", "w", encoding="utf-8").write(dom)
    out["item2_dom_dump"] = {"path": f"{EV}/pages_index_dom_dump_01.html", "bytes": len(dom)}
    out["item3_existing_count"] = len(re.findall(r"\(existing", dom))
    ntext = norm(text)
    miss = []
    for lv, ss in styles.items():
        for s in ss:
            if norm(s) not in ntext:
                miss.append((lv, s[:80]))
    out["item4_style_full_text"] = {"unique_styles": {lv: len(ss) for lv, ss in styles.items()}, "missing_in_dom": miss, "pass": not miss}
    out["item5_player"] = {"index_audio_count": pg.locator("audio").count(),
                           "index_audio_src": pg.eval_on_selector_all("audio", "els=>els.map(e=>e.getAttribute('src'))"),
                           "a2_player_audio": None, "b1b_player_audio": None}
    for lv in EN:
        pp = br.new_page()
        pp.goto(f"{D}/{lv}/player.html", wait_until="networkidle")
        out["item5_player"][f"{lv}_player_audio"] = pp.locator("audio").count()
        pp.close()
    # (7) displayed style vs metadata: per-segment row on index
    mism = []
    for lv, m in meta.items():
        pass
    rows = pg.eval_on_selector_all("table.seg tbody tr", "els=>els.map(e=>[...e.children].map(c=>c.innerText))")
    seg_rows = {}
    for r in rows:
        seg_rows.setdefault(r[0], []).append(r)
    # segment tables come in order a2 then b1b; split by repeated names
    cnt = {}
    for lv in ["a2", "b1b"]:
        cnt[lv] = 0
    tables = pg.eval_on_selector_all("table.seg", "els=>els.map(t=>[...t.querySelectorAll('tbody tr')].map(r=>[...r.children].map(c=>c.innerText)))")
    seg_tables = [t for t in tables if t and t[0][0] == "topic_intro"]
    for lv, t in zip(["a2", "b1b"], seg_tables):
        for r in t:
            ms = meta[lv]["segments"][r[0]]
            if norm(r[-1]) != norm(ms["style_prefix"]) or r[3] != ms["voice"] or r[2] != ms["model"]:
                mism.append((lv, r[0]))
    out["item7_style_metadata_match"] = {"segment_tables_found": len(seg_tables), "mismatch": mism, "pass": len(seg_tables) == 2 and not mism}
    br.close()

# (6) mp3 200 + decode
dec = {}
for lv in EN:
    for name in ["episode.mp3"]:
        u = f"{D}/{lv}/web/{name}"
        b = get(u)
        i = sf.info(io.BytesIO(b))
        d, sr = sf.read(io.BytesIO(b))
        dec[u] = {"http": 200, "bytes": len(b), "duration_sec": round(len(d) / sr, 3), "samplerate": sr, "decode": "OK"}
    segs = json.load(open(f"{EV}/pages_build_manifest_01.json", encoding="utf-8"))[lv]["segment_mp3"]
    ok = 0
    for n in segs:
        b = get(f"{D}/{lv}/web/segments/{n}.mp3")
        sf.read(io.BytesIO(b))
        ok += 1
    dec[f"{lv}_segments"] = {"decoded_ok": ok, "total": len(segs)}
out["item6_mp3"] = dec

# Play real playback evidence (unified.html + index.html audio)
play = {}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    for lv, u in list(UNI.items()):
        pg = br.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(u, wait_until="networkidle")
        pg.wait_for_selector("audio#episode", timeout=30000)
        before = pg.evaluate("()=>{const a=document.getElementById('episode');return {currentTime:a.currentTime,paused:a.paused,readyState:a.readyState,src:a.currentSrc,duration:a.duration,error:a.error&&a.error.code}}")
        btn = pg.locator("button:has-text('再生'), button:has-text('Play'), .play, button[aria-label*='Play']").first
        try:
            btn.click(timeout=3000)
        except Exception:
            pg.evaluate("()=>document.getElementById('episode').play()")
        pg.wait_for_timeout(5000)
        after = pg.evaluate("()=>{const a=document.getElementById('episode');return {currentTime:a.currentTime,paused:a.paused,readyState:a.readyState,src:a.currentSrc,duration:a.duration,error:a.error&&a.error.code}}")
        # seek test
        pg.evaluate("()=>{const a=document.getElementById('episode');a.currentTime=60;}")
        pg.wait_for_timeout(2500)
        seek = pg.evaluate("()=>{const a=document.getElementById('episode');return {currentTime:a.currentTime,paused:a.paused,readyState:a.readyState}}")
        play[f"unified_{lv}"] = {"url": u, "before": before, "after_5s": after, "after_seek60_2.5s": seek, "console_errors": errs,
                                 "pass": (after["currentTime"] > 1 and after["paused"] is False and after["readyState"] >= 3 and not after["error"] and seek["currentTime"] >= 60)}
        pg.close()
    # index.html standard players
    for lv in EN:
        pg = br.new_page()
        pg.goto(D + "/index.html", wait_until="networkidle")
        idx = 0 if lv == "a2" else 1
        a = pg.locator("audio").nth(idx)
        pg.evaluate("(i)=>document.querySelectorAll('audio')[i].play()", idx)
        pg.wait_for_timeout(4000)
        st = pg.evaluate("(i)=>{const a=document.querySelectorAll('audio')[i];return {currentTime:a.currentTime,paused:a.paused,readyState:a.readyState,error:a.error&&a.error.code,src:a.currentSrc}}", idx)
        st["pass"] = st["currentTime"] > 1 and st["paused"] is False and st["readyState"] >= 3 and not st["error"]
        play[f"index_{lv}"] = st
        pg.close()
    br.close()
out["play_evidence"] = play
out["overall_play_pass"] = all(v["pass"] for v in play.values())
out["overall_item_pass"] = all(v == 200 for v in out["item1_http"].values()) and out["item3_existing_count"] == 0 and out["item4_style_full_text"]["pass"] and out["item7_style_metadata_match"]["pass"] and out["item5_player"]["index_audio_count"] >= 2
json.dump(out, open(f"{EV}/pages_play_evidence_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps({k: out[k] for k in out if k.startswith("overall") or k in ("item3_existing_count",)}, ensure_ascii=False))
print(json.dumps(out["item1_http"], ensure_ascii=False)[:1500])
print(json.dumps(out["item4_style_full_text"], ensure_ascii=False)[:600])
print(json.dumps(out["item7_style_metadata_match"], ensure_ascii=False))
print(json.dumps(out["item6_mp3"], ensure_ascii=False)[:800])
print(json.dumps({k: (v.get("after_5s") or v) for k, v in play.items()}, ensure_ascii=False)[:1500])
