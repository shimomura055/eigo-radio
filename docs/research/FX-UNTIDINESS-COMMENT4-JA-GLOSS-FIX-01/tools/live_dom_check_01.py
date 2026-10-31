# 公開URLでAdv Comment 4(adv_19)の英文と日本語訳の表示・クリック連動(英文クリックで日本語側ハイライト)を確認する(Playwright)
import json, sys
from playwright.sync_api import sync_playwright
url, out = sys.argv[1], sys.argv[2]
res = {"url": url}
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (("pc", {"width": 1280, "height": 900}), ("mobile", {"width": 390, "height": 844})):
        pg = b.new_page(viewport=vp)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        resp = pg.goto(url, wait_until="networkidle")
        pg.wait_for_selector("[data-part='19']", state="attached", timeout=20000)
        blk = pg.query_selector("[data-part='19']")
        txt = blk.inner_text()
        ids = pg.evaluate("() => [...document.querySelectorAll(\"[data-part='19'] [data-sid]\")].map(e=>e.dataset.sid)")
        r = {"status": resp.status, "text": txt, "sids": ids,
             "has_new_ja": "出しっぱなしになっている物にも目的" in txt, "has_old_ja": "省かれた" in txt, "console_errors": errs}
        res[name] = r
        pg.close()
    b.close()
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if k == "url" else {kk: vv for kk, vv in v.items() if kk != "text"}) for k, v in res.items()}, ensure_ascii=False))
