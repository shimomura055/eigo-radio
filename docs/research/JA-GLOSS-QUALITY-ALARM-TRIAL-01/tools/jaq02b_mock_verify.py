# -*- coding: utf-8 -*-
"""DEV試作の差分検証(API 0)。使い方: jaq02b_mock_verify.py [base_url]  (省略時はworktreeルートをローカルhttpで配信)
検証: (1)form_logic.js sha256一致 (2)警告なし候補行のDOMがProductionと同一(警告ブロック除去後も含む) (3)警告件数=DOMの.qa-alarm数
(4)同じ選択操作で stats/miniStats/コピー文(照合コード行以外)が一致、警告は操作を妨げない (5)スクショ(PC/スマホ)。"""
import json, os, sys, hashlib, http.server, threading, functools, re
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright_noplay as sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
SHOTS = os.path.join(BASE, "trial", "mock_shots"); os.makedirs(SHOTS, exist_ok=True)
sha = lambda p: hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


def serve():
    import mimetypes, urllib.parse
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):   # 公開Pages(blob=LF)と同じバイト列を配信する(Windows作業ツリーのCRLFをLFへ。d6/file sha一致のため)
            pth = os.path.join(ROOT, urllib.parse.unquote(self.path.split("?")[0]).lstrip("/"))
            if not os.path.isfile(pth): self.send_error(404); return
            raw = open(pth, "rb").read()
            if pth.endswith((".json", ".js", ".html", ".css")): raw = raw.replace(bytes([13, 10]), bytes([10]))
            self.send_response(200); self.send_header("Content-Type", (mimetypes.guess_type(pth)[0] or "application/octet-stream") + ("; charset=utf-8" if pth.endswith((".json", ".js", ".html")) else ""))
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    h = functools.partial(Quiet, directory=ROOT)
    class Q(http.server.ThreadingHTTPServer): pass
    srv = Q(("127.0.0.1", 0), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def main():
    out = {"form_logic_sha256_prod": sha("user_test/selection_form_v3/form_logic.js"), "form_logic_sha256_dev": sha("user_test/dev_ja_alarm_mock_01/form_logic.js")}
    out["form_logic_identical"] = out["form_logic_sha256_prod"] == out["form_logic_sha256_dev"]
    srv, base = serve()
    stats = json.load(open(os.path.join(BASE, "trial", "mock_build_stats.json"), encoding="utf-8"))
    PROD = base + "/user_test/selection_form_v3/index.html?dev=all"; DEV = base + "/user_test/dev_ja_alarm_mock_01/index.html?dev=all"
    rows = []; errs = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 1000}); ctx.grant_permissions([])
        pp = ctx.new_page(); pd = ctx.new_page(); pq = ctx.new_page()
        for pg in (pp, pd, pq): pg.on("pageerror", lambda e: errs.append(str(e)))
        pp.goto(PROD); pd.goto(DEV); pq.goto(DEV.replace("dev=all", "dev=all&qa=off")); [pg.wait_for_timeout(2500) for pg in (pp, pd, pq)]
        out["banner_text"] = pd.inner_text(".qa-dev-banner"); out["banner_visible"] = pd.is_visible(".qa-dev-banner")
        key = lambda pg, f: pg.evaluate("f=>{var a=IDX.articles.find(function(a){return a.data==='data/'+f});return a?FL.stateKey(a):null}", f)
        def open_set(pg, url, f):
            k = key(pg, f)
            if k is None: return False
            pg.goto(url + "&set=" + k); pg.wait_for_timeout(900); return True
        warn_total = 0; mism = 0; checked = 0
        for f, st in sorted(stats["per_level"].items()):
            if not (open_set(pp, PROD, f) and open_set(pd, DEV, f) and open_set(pq, DEV + "&qa=off", f)): errs.append("noidx " + f); continue
            hp = pp.evaluate("()=>document.getElementById('candPhrase').innerHTML+document.getElementById('candWord').innerHTML")
            hq = pq.evaluate("()=>document.getElementById('candPhrase').innerHTML+document.getElementById('candWord').innerHTML")
            hd = pd.evaluate("()=>{var c=document.getElementById('candPhrase').cloneNode(true),w=document.getElementById('candWord').cloneNode(true);[c,w].forEach(function(n){n.querySelectorAll('.qa-alarm').forEach(function(e){e.remove()})});return c.innerHTML+w.innerHTML}")
            nal = pd.evaluate("()=>document.querySelectorAll('#candPhrase .qa-alarm, #candWord .qa-alarm').length")
            nal_off = pq.evaluate("()=>document.querySelectorAll('.qa-alarm').length")
            ok1 = (hp == hq); ok2 = (hp == hd)
            checked += 1; warn_total += nal
            if not (ok1 and ok2 and nal == st["warn"] and nal_off == 0): mism += 1; errs.append(f"mismatch {f}: qaoff_eq={ok1} stripped_eq={ok2} nal={nal} expect={st['warn']} off={nal_off}")
            rows.append({"file": f, "n_cand": st["n"], "warn_expected": st["warn"], "warn_dom": nal, "prod_eq_qaoff": ok1, "prod_eq_stripped": ok2})
        out["levels_checked"] = checked; out["levels_mismatch"] = mism; out["warn_total_dom"] = warn_total; out["rows"] = rows
        # 操作パリティ: 警告のあるレベルで同じ選択操作 -> stats/コピー文
        target = next((f for f, s in stats["per_level"].items() if s["warn"] >= 2), None) or next(f for f, s in stats["per_level"].items() if s["warn"] >= 1)
        out["parity_level"] = target
        res = {}
        for pg in (pp, pd, pq): pg.close()
        for name in ("prod", "dev"):
            pg = ctx.new_page()
            pg.goto(PROD if name == "prod" else DEV); pg.wait_for_timeout(1500)
            pg.evaluate("()=>localStorage.clear()")
            open_set(pg, PROD if name == "prod" else DEV, target); pg.wait_for_timeout(500)
            for _ in range(3):
                pg.locator("input[data-cat='1']:not([disabled]):not(:checked)").first.click(); pg.wait_for_timeout(150)
            for _ in range(2):
                pg.locator("input[data-cat='2']:not([disabled]):not(:checked)").first.click(); pg.wait_for_timeout(150)
            res[name] = {"stats": pg.inner_text("#stats"), "mini": pg.inner_text("#miniStats"), "checked": pg.eval_on_selector_all("input[data-term]:checked", "e=>e.map(x=>x.dataset.term+':'+x.dataset.cat)")}
            pg.click("#copy"); pg.wait_for_timeout(700)
            res[name]["copy_text"] = pg.eval_on_selector("#fallback", "e=>e.value")
            res[name]["status"] = pg.inner_text("#status"); pg.close()
        out["parity"] = {"checked_equal": res["prod"]["checked"] == res["dev"]["checked"], "stats_equal": res["prod"]["stats"] == res["dev"]["stats"], "mini_equal": res["prod"]["mini"] == res["dev"]["mini"],
                          "n_checked": len(res["dev"]["checked"])}
        lp = [l for l in res["prod"]["copy_text"].split("\n")]; ld = [l for l in res["dev"]["copy_text"].split("\n")]
        diff = [(a, b2) for a, b2 in zip(lp, ld) if a != b2]
        out["parity"]["copy_text_lines"] = [len(lp), len(ld)]; out["parity"]["copy_text_diff_lines"] = [[a[:80], b2[:80]] for a, b2 in diff][:6]
        out["parity"]["copy_text_diff_only_code_lines"] = all(("照合コード" in a or "sha" in a.lower() or "コード" in a) for a, _ in diff)
        out["parity"]["dev_copy_status"] = res["dev"]["status"]
        open(os.path.join(BASE, "trial", "mock_copy_text_dev.txt"), "w", encoding="utf-8").write(res["dev"]["copy_text"])
        open(os.path.join(BASE, "trial", "mock_copy_text_prod.txt"), "w", encoding="utf-8").write(res["prod"]["copy_text"])
        # 想定表示スクショ(警告のあるレベル): PC / スマホ
        for tag, vp in (("pc", {"width": 1280, "height": 1000}), ("sp", {"width": 390, "height": 844})):
            c2 = b.new_context(viewport=vp, device_scale_factor=2 if tag == "sp" else 1); g = c2.new_page(); g.goto(DEV); g.wait_for_timeout(2500)
            open_set(g, DEV, target); g.wait_for_timeout(800)
            g.screenshot(path=os.path.join(SHOTS, f"dev_mock_{tag}_top.png"), full_page=False)
            el = g.query_selector(".qa-alarm")
            if el: el.scroll_into_view_if_needed(); g.wait_for_timeout(300); g.screenshot(path=os.path.join(SHOTS, f"dev_mock_{tag}_alarm.png"), full_page=False)
            out[f"shot_{tag}_alarms_visible"] = g.evaluate("()=>document.querySelectorAll('.qa-alarm').length")
            c2.close()
        b.close()
    out["page_errors"] = errs[:10]
    json.dump(out, open(os.path.join(BASE, "trial", "mock_verify_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
