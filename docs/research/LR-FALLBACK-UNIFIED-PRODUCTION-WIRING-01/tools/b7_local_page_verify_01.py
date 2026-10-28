# -*- coding: utf-8 -*-
"""委任_12(B7)専用: X候補ページ(index.htmlのみ)のlocal Playwright検証(API 0)。er063_family_z_page_verify_01の再生検査(_play_all)を流用。
検査: HTTP200・audio全件再生(muted)・console error 0・4xx 0・file scheme無し・⏸/赤/青の個数・旧『Local Rewrite採用』注記0。
使い方: python b7_local_page_verify_01.py --dir user_test/<candidate> --out <json>"""
import argparse, functools, http.server, json, os, sys, threading
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er063_family_z_page_verify_01 as pv
from playwright.sync_api import sync_playwright
ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=a.dir))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}/"
out = {"dir": a.dir, "pages": {}}
try:
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"]); out["browser"] = br.version
        pg = br.new_page(); errs, bad = [], []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("response", lambda r: bad.append((r.url, r.status)) if r.status >= 400 else None)
        resp = pg.goto(base + "index.html", wait_until="networkidle"); html = pg.content()
        plays = pv._play_all(pg)
        o = {"http_status": resp.status, "audio_count": pg.locator("audio").count(), "plays_ok": sum(1 for x in plays if not x.get("error") and x.get("advanced")),
             "plays_failed": [x["src"] for x in plays if x.get("error") or not x.get("advanced")], "console_errors": errs, "http_ge400": bad,
             "file_scheme": ("file:///" in html or "C:\\" in html), "chunk_marks": html.count("chunk-mark"), "rpt_lr": html.count("class=\"rpt-lr\""),
             "rpt_fb": html.count("class=\"rpt-fb\""), "old_lr_note": html.count("Local Rewrite採用")}
        out["pages"]["index.html"] = o; br.close()
finally:
    srv.shutdown(); srv.server_close()
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
o = out["pages"]["index.html"]; print(json.dumps(o, ensure_ascii=False)[:600])
ok = o["http_status"] == 200 and not o["plays_failed"] and not o["console_errors"] and not o["http_ge400"] and not o["file_scheme"] and o["old_lr_note"] == 0
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
