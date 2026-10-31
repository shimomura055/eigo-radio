# 仮説: glossary_links_open_the_expression NG=検査側の競合。旧検査は『scrollYが150ms間隔で2回同値』で停止判定するため、smooth scrollの開始が遅れる(CPU負荷)と開始前に判定終了し、目的地到達前の位置(top>0.8vh)を読む。
# CPU throttle下で旧判定/新判定(目的地到達+停止)を各N回実行し、製品の最終到達位置も比較する。
import sys, json
sys.path.insert(0, sys.argv[1])
import er135_enduser_page_verify_01 as V
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright_noplay as sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
pub, rate, N = sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
OLD = """() => new Promise(res => { let last = -1, same = 0; const t0 = performance.now();
  (function f(){ const y = Math.round(scrollY); same = (y === last) ? same + 1 : 0; last = y;
    if (same >= 2 || performance.now() - t0 > 5000) res(y); else setTimeout(f, 150); })(); })"""
NEW = """(href) => new Promise(res => { let last = -1, same = 0; const t0 = performance.now();
  (function f(){ const y = Math.round(scrollY); same = (y === last) ? same + 1 : 0; last = y;
    const t = document.getElementById(href.slice(1)), b = t && t.getBoundingClientRect(), there = !!t && t.open && b.top >= -5 && b.top <= innerHeight * 0.8;
    if ((there && same >= 2) || performance.now() - t0 > 6000) res(y); else setTimeout(f, 150); })(); })"""
POS = "(href) => { const t=document.getElementById(href.slice(1)); const b=t.getBoundingClientRect(); return {top:Math.round(b.top), open:t.open, vh:innerHeight}; }"
srv, base = V.serve(pub)
res = {"rate": rate, "old_ng": 0, "new_ng": 0, "old_samples": [], "new_samples": []}
with sync_playwright() as p:
    br = p.chromium.launch(); page = br.new_context(**V.VIEWS["mobile"]).new_page()
    cdp = page.context.new_cdp_session(page); cdp.send("Emulation.setCPUThrottlingRate", {"rate": rate})
    for mode in ("old", "new"):
        for n in range(N):
            page.goto(base + f"/enduser/index.html?lv=adv&cb={mode}{n}"); page.wait_for_selector(".sent")
            page.wait_for_function("() => window.__EUP && window.__EUP.syncKind === 'real'")
            links = page.query_selector_all(".gloss a.glink"); li = links[n % len(links)]; href = li.get_attribute("href")
            li.scroll_into_view_if_needed(); li.click()
            if mode == "old": page.evaluate(OLD)
            else: page.evaluate(NEW, href)
            r = page.evaluate(POS, href); ok = r["open"] and -5 <= r["top"] <= r["vh"] * 0.8
            res[mode + "_samples"].append(r)
            if not ok: res[mode + "_ng"] += 1
    br.close()
srv.shutdown()
print(json.dumps(res))
