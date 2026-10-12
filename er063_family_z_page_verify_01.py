# -*- coding: utf-8 -*-
"""Family Z 試聴ページのPlaywright検証(Gate 7 (a)〜(n) の機械確認、有料API 0)。
使い方:
  .venv/Scripts/python.exe er063_family_z_page_verify_01.py --base https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_01/ --out <json>
  .venv/Scripts/python.exe er063_family_z_page_verify_01.py --local user_test/family_z_melos_01 --out <json>   # 一時localhost serverで検証
(m)の『ユーザー環境から実際に開けるリンク』は--base に公開URL(GitHub Pages)を指定した場合のみ確認対象。--local は内部証跡。"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import re
import threading

from playwright.sync_api import sync_playwright

PAGES = ("index.html", "standard.html", "advanced.html")


def _play_all(pg) -> list:
    plays = []
    n = pg.locator("audio").count()
    for i in range(n):
        src = pg.locator("audio").nth(i).get_attribute("src")
        res = pg.evaluate("""async (i) => {
            const a = document.querySelectorAll('audio')[i]; a.muted = true;
            await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
            const d = a.duration; if (a.error) return {duration: d, error: a.error.code};
            try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
            const t0 = a.currentTime; await new Promise(r => setTimeout(r, 1000)); const t1 = a.currentTime;
            let seekOk = null; if (d > 20) { const tgt = d - 5; a.currentTime = tgt; await new Promise(r => setTimeout(r, 700)); seekOk = Math.abs(a.currentTime - tgt) < 2.5; }
            a.pause(); a.removeAttribute('src'); a.load(); return {duration: d, advanced: t1 > t0 + 0.4, error: null, seekOk};
        }""", i)
        res["src"] = src
        plays.append(res)
    return plays


def verify(base: str, internal_only: bool = False) -> dict:
    out = {"base": base, "internal_only_local": internal_only, "pages": {}}
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        out["browser"] = br.version
        for path in PAGES:
            pg = br.new_page()
            errs, bad = [], []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
            resp = pg.goto(base + path, wait_until="networkidle")
            text, html = pg.inner_text("body"), pg.content()
            o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "tr_count": pg.locator("tr[id]").count(),
                 "(m)_no_file_scheme": not ("file:///" in html or "C:\\" in html or "C:/" in html),
                 "(i)_no_A2_B1_label": not re.search(r"\(A2\)|\(B1\)|B1B", text),
                 "(n)_kp_two_column": pg.locator("table.kp").count(),
                 "(n)_no_kp_label": not re.search(r"English:|英語:|EN:|日本語:|JA:", text)}
            if path != "index.html":
                o.update({
                    "(a)_full_episode_audio": pg.locator("#main").count() == 1,
                    "(b)_preview_row": "Preview" in text,
                    "(c)_comment_rows": len(re.findall(r"Comment [123]", text)),
                    "(d)_story_rows": pg.locator("tr[id]").filter(has_text="full_story_part").count(),
                    "(e)_kp_rows": pg.locator("table.kp").count(),
                    "(f)_intro_outro_noted": "読み上げなし" in text,
                    "(g)_seek_buttons": pg.locator("button.jump").count(),
                    "(h)_voice_labels": text.count("Voice:"),
                    "(j)_unfetched_marked": ("未取得" in text) or "no_unfetched_segments",
                    "(k)_tts_mode_stated": "TTS方式" in text,
                    "(l)_audio_in_same_row_as_script": pg.locator("tr[id]:has(audio):has(.script)").count() == o["tr_count"],
                })
            plays = _play_all(pg)
            o["plays_ok"] = sum(1 for x in plays if x.get("error") is None and x.get("advanced") and x.get("duration", 0) > 0)
            o["plays_failed"] = [x["src"] for x in plays if not (x.get("error") is None and x.get("advanced"))]
            o["seek_ok_all"] = all(x.get("seekOk") in (None, True) for x in plays)
            o["http_ge400"] = bad
            o["console_errors"] = errs
            out["pages"][path] = o
            pg.close()
        br.close()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--local")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    srv = None
    if a.local:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=a.local)
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}/"
    else:
        base = a.base
    res = verify(base, internal_only=bool(a.local))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    for k, v in res["pages"].items():
        print(k, {x: y for x, y in v.items() if x not in ("plays_failed",)})
    if srv:
        srv.shutdown()


if __name__ == "__main__":
    main()
