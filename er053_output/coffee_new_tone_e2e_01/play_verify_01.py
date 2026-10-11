# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 delegation 07 Step4: Playwright real-playback evidence.
Serves user_test/coffee_new_tone_01 via a local http.server (GitHub Pages deploys from main only; branch not yet merged)
and plays Advanced episode + segments + Standard passed segments in headless Chromium. No paid API."""
import functools, http.server, json, re, socketserver, threading
from playwright.sync_api import sync_playwright

ROOT = "user_test/coffee_new_tone_01"
OUTJ = "er053_output/coffee_new_tone_e2e_01/pages_play_evidence_01.json"
PORT = 8765


class Q(http.server.SimpleHTTPRequestHandler):
    """Range(206)対応の簡易server(GitHub Pagesと同様にseek可能にするため)。"""
    def log_message(self, *a):
        pass

    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        import os
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        size = os.path.getsize(path)
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._range_left = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, "_range_left", None)
        if left is None:
            return super().copyfile(source, outputfile)
        outputfile.write(source.read(left))
        self._range_left = None


Handler = functools.partial(Q, directory=ROOT)
httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}"

out = {"base": BASE, "note": "local http.server of user_test/coffee_new_tone_01 (same static files as GitHub Pages path)", "pages": {}}
with sync_playwright() as p:
    br = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    for name, url in (("index", "/index.html"), ("advanced_player", "/b1b/player.html")):
        pg = br.new_page()
        errs, bad = [], []
        pg.on("console", lambda m, errs=errs: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
        pg.on("response", lambda r, bad=bad: bad.append((r.url, r.status)) if r.status >= 400 else None)
        pg.goto(BASE + url, wait_until="networkidle")
        text = pg.inner_text("body")
        rec = {"url": BASE + url, "audio_count": pg.locator("audio").count(), "http_ge400": bad,
               "label_check": {"English:/EN:/英語:": bool(re.search(r"(English:|\bEN:|英語:|日本語gloss)", text)),
                               "A2/B1 visible": bool(re.search(r"\(A2\)|\(B1\)|\bB1B\b", text)),
                               "has_Standard": "Standard" in text, "has_Advanced": "Advanced" in text,
                               "file_scheme": "file:///" in pg.content()}}
        plays = []
        n = pg.locator("audio").count()
        for i in range(n):
            a = pg.locator("audio").nth(i)
            src = a.get_attribute("src")
            # segment/episode: play and measure
            res = pg.evaluate("""async (i) => {
                const a = document.querySelectorAll('audio')[i];
                a.muted = true;
                await new Promise(r => { if (a.readyState >= 1) r(); else { a.addEventListener('loadedmetadata', r, {once:true}); a.addEventListener('error', r, {once:true}); a.load(); } });
                const d = a.duration; const err = a.error ? a.error.code : null;
                if (err) return {duration: d, error: err};
                try { await a.play(); } catch (e) { return {duration: d, error: 'play:' + e.message}; }
                const t0 = a.currentTime;
                await new Promise(r => setTimeout(r, 2500));
                const t1 = a.currentTime;
                const paused = a.paused;
                let seekOk = null;
                if (d > 20) { a.currentTime = Math.min(d - 5, 15); await new Promise(r => setTimeout(r, 1200)); seekOk = a.currentTime > 14; }
                a.pause();
                return {duration: d, t_after_2_5s: t1, advanced: t1 > t0 + Math.min(1.0, d * 0.8), paused_after_play: paused, error: a.error ? a.error.code : null, seekOk};
            }""", i)
            res["src"] = src
            plays.append(res)
        rec["plays"] = plays
        rec["console_errors"] = errs
        rec["all_play_ok"] = all((x.get("error") is None and x.get("advanced") and (x.get("duration") or 0) > 0) for x in plays)
        out["pages"][name] = rec
        pg.close()
    br.close()
httpd.shutdown()
json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for k, v in out["pages"].items():
    print(k, "audio", v["audio_count"], "all_play_ok", v["all_play_ok"], "bad", v["http_ge400"], "errs", v["console_errors"][:2], v["label_check"])
    for x in v["plays"]:
        print("  ", x["src"], round(x.get("duration") or 0, 2), x.get("advanced"), x.get("error"), x.get("seekOk"))
