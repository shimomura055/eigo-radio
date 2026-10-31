# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_19: 標準フォーマット試聴ページ(index.html)のPlaywright実再生evidence(有料APIなし)。
er026_fz_play_verify_17.py派生。追加検証: 「全編を通し再生」ボタン押下で通し再生が進む / 通し音声のシーク(中盤・末尾付近) /
「全編のこの位置へ」ボタンのシーク再生 / スクリプト表示(Preview・Full Story・Comment・KP英日) / 内部情報非表示 / ASR警告が折りたたみ補助表示。
使い方: --url <公開URL .../index.html> | --local-dir <pages dir>(Range対応の一時localhost serverで検証) / --out <json>"""
import argparse
import functools
import http.server
import json
import os
import re
import threading

import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

ap = argparse.ArgumentParser()
ap.add_argument("--url")
ap.add_argument("--local-dir")
ap.add_argument("--out", required=True)
A = ap.parse_args()


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    """Range対応(GitHub Pages同等のシーク挙動をlocalで検証するため)。"""

    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        size = os.path.getsize(path)
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        f = open(path, "rb")
        f.seek(start)
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        n = getattr(self, "_remaining", None)
        if n is None:
            return super().copyfile(source, outputfile)
        while n > 0:
            buf = source.read(min(65536, n))
            if not buf:
                break
            outputfile.write(buf)
            n -= len(buf)
        self._remaining = None

    def log_message(self, *a):
        pass


srv = None
if A.local_dir:
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(RangeHandler, directory=A.local_dir))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    BASE = f"http://127.0.0.1:{srv.server_address[1]}/"
else:
    BASE = A.url.rsplit("index.html", 1)[0]

JS_PLAY = """async (i) => {
    const a = document.querySelectorAll('audio')[i]; a.muted = true;
    await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
    const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
    try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
    const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1200)); const t1 = a.currentTime;
    a.pause(); a.removeAttribute('src'); a.load(); return {duration: d, advanced: t1 > t0 + 0.5, error: null};
}"""

# 通し再生: ボタン押下(実クリック)後の再生進行 -> 中盤シーク -> 末尾付近シーク -> 「全編のこの位置へ」ジャンプ
JS_MAIN = """async (mid) => {
    const a = document.getElementById(mid); a.muted = true;
    await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
    return {duration: a.duration, error: a.error ? a.error.code : null, paused: a.paused};
}"""
JS_STATE = """(mid) => { const a = document.getElementById(mid); return {t: a.currentTime, paused: a.paused, d: a.duration, ended: a.ended}; }"""
JS_SEEK = """async ([mid, tgt]) => { const a = document.getElementById(mid); a.currentTime = tgt; await new Promise(r => setTimeout(r, 1500));
    return {t: a.currentTime, paused: a.paused, ok: Math.abs(a.currentTime - tgt) < 3.0 && a.currentTime >= tgt - 0.5 }; }"""

out = {"base": BASE, "local_range_server": bool(A.local_dir), "pages": {}, "levels": {}}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    out["browser"] = br.version
    pg = br.new_page()
    errs, bad = [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
    resp = pg.goto(BASE + "index.html", wait_until="networkidle")
    body = pg.inner_text("body")
    html = pg.content()
    o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(),
         "file_scheme_in_html": ("file:///" in html or "C:\\" in html or "C:/" in html),
         "internal_info_in_script": [t for t in pg.locator(".script").all_inner_texts()
                                     if re.search(r"Voice:|Style:|base_sha|読み上げなし|通知音|音楽", t)],
         "playall_buttons": pg.locator("button.playall").count(),
         "aux_details_open_by_default": pg.locator("details.aux[open]").count(),
         "aux_after_levels": pg.evaluate("""() => { const a = document.getElementById('aux'), l = document.getElementById('adv');
             return !!a && !!l && (l.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0; }""")}
    for lid, label, mid in (("std", "Standard", "main_std"), ("adv", "Advanced", "main_adv")):
        L = {"heading": pg.locator(f"h2#{lid}").inner_text()}
        L["script_blocks_visible"] = pg.locator(f"h2#{lid} ~ table").first.locator(".script").count()
        tbl_text = pg.locator(f"h2#{lid} ~ table").first.inner_text()
        L["preview_in_script"] = "Preview" in tbl_text
        L["full_story_in_script"] = "Full Story Part 1" in tbl_text and "Full Story Part 3" in tbl_text
        L["comment_in_script"] = "Comment 1" in tbl_text
        L["kp_tables"] = pg.locator(f"h2#{lid} ~ table").first.locator("table.kp").count()
        L["kp_first"] = pg.locator(f"h2#{lid} ~ table").first.locator("table.kp").first.inner_text().replace("\n", " ")
        meta = pg.evaluate(JS_MAIN, mid)
        L["main_meta"] = meta
        d = meta["duration"] or 0
        btn = pg.locator(f"button.playall[data-target={mid}]")
        btn.scroll_into_view_if_needed()
        btn.click()                                   # 実クリック(通し再生ボタン)
        pg.wait_for_timeout(1800)
        s1 = pg.evaluate(JS_STATE, mid)
        L["playall_click_playing"] = (not s1["paused"]) and s1["t"] > 0.8
        L["playall_t_after_click"] = round(s1["t"], 2)
        seeks = {}
        for name, tgt in (("mid", d / 2), ("near_end", max(d - 8, 0))):
            r = pg.evaluate(JS_SEEK, [mid, tgt])
            seeks[name] = {"target": round(tgt, 1), "t": round(r["t"], 2), "ok": r["ok"], "playing": not r["paused"]}
        L["seeks"] = seeks
        # 「全編のこの位置へ」ボタン(Full Story Part 2の行)
        jb = pg.locator(f"h2#{lid} ~ table").first.locator("tr", has_text="Full Story Part 2").locator("button.jump")
        tgt = float(jb.get_attribute("data-t"))
        jb.click()
        pg.wait_for_timeout(1800)
        s2 = pg.evaluate(JS_STATE, mid)
        L["jump_button"] = {"target": tgt, "t": round(s2["t"], 2), "ok": s2["t"] >= tgt - 0.5 and not s2["paused"]}
        pg.evaluate("(mid)=>{const a=document.getElementById(mid);a.pause();}", mid)
        L["ok"] = bool(L["playall_click_playing"] and all(v["ok"] for v in seeks.values()) and L["jump_button"]["ok"]
                       and L["preview_in_script"] and L["full_story_in_script"] and L["comment_in_script"] and L["kp_tables"] >= 3)
        out["levels"][label] = L
    # 全audio要素の実再生(行ごと・ASR警告リスト内も)
    plays = []
    for i in range(o["audio_count"]):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate(JS_PLAY, i)
        res["src"] = src
        plays.append(res)
    o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
    o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
    o["http_ge400"] = bad
    o["console_errors"] = errs
    out["pages"]["index.html"] = o
    pg.close()
    br.close()
out["overall"] = ("PASS" if (o["http_status"] == 200 and not o["plays_failed"] and not o["console_errors"] and not o["http_ge400"]
                             and not o["file_scheme_in_html"] and not o["internal_info_in_script"] and o["playall_buttons"] == 2
                             and o["aux_details_open_by_default"] == 0 and o["aux_after_levels"]
                             and all(L["ok"] for L in out["levels"].values())) else "FAIL")
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
json.dump(out, open(A.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "pages"}, ensure_ascii=True)[:1800])
print(json.dumps({k: v for k, v in o.items()}, ensure_ascii=True)[:900])
if srv:
    srv.shutdown()
