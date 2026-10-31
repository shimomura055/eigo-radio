# 仮説: vocab_each_item NG=検査側の競合。endVocab()はmode='full'+pause()を同期で行い、位置復帰(currentTime=at)は通し音声のloadedmetadata後(withMeta)。
# 検査は mode==='full' && paused を待った直後にcurrentTimeを読むため、metadata読込前だとt=0を読む。通し音声の応答を遅延させて決定的に再現する。
import sys, json, time
sys.path.insert(0, sys.argv[1])
import er135_enduser_page_verify_01 as V
from playwright.sync_api import sync_playwright
pub, delay = sys.argv[2], float(sys.argv[3])
srv, base = V.serve(pub)
art = V._get_json(base + "/enduser/data/article.json")
lv = "adv"; L = art["levels"][lv]; main = L["main"]
out = {"delay_s": delay}
with sync_playwright() as p:
    br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]); page = br.new_page(viewport={"width": 1280, "height": 900})
    def slow(route):
        if delay and route.request.url.endswith("/" + main):
            time.sleep(delay)
        route.continue_()
    page.route("**/*.mp3", slow)
    page.goto(base + f"/enduser/index.html?lv={lv}"); page.wait_for_function("() => window.__EUP && window.__EUP.syncKind === 'real'")
    page.wait_for_function("() => document.getElementById('aud').readyState >= 1", timeout=30000)
    btn = page.query_selector_all("#vocab button[data-act=vocab]")[0]
    page.evaluate("(t) => { const a=document.getElementById('aud'); a.currentTime=t; a.play(); }", 20.0); page.wait_for_timeout(500)
    page.evaluate("""() => { window.__log = []; const a = document.getElementById('aud'); const t0 = performance.now();
      a.addEventListener('loadedmetadata', () => window.__log.push(['loadedmetadata', Math.round(performance.now() - t0), a.currentTime]));
      a.addEventListener('seeked', () => window.__log.push(['seeked', Math.round(performance.now() - t0), a.currentTime])); }""")
    btn.scroll_into_view_if_needed(); btn.click()
    page.wait_for_function("() => window.__EUP && window.__EUP.mode === 'vocab' && !document.getElementById('aud').paused", timeout=5000)
    page.wait_for_function("() => window.__EUP && window.__EUP.mode === 'full' && document.getElementById('aud').paused", timeout=15000)   # 現行検査の待ち条件
    imm = page.evaluate("() => { const a = document.getElementById('aud'); return {t: a.currentTime, readyState: a.readyState, src: a.src.slice(-30)}; }")
    page.wait_for_function("() => { const a = document.getElementById('aud'); return a.readyState >= 1 && a.src.indexOf('/audio/vocab_') < 0; }", timeout=15000)
    page.wait_for_timeout(300)
    late = page.evaluate("() => { const a = document.getElementById('aud'); return {t: a.currentTime, readyState: a.readyState, paused: a.paused, mode: window.__EUP.mode}; }")
    out.update(immediately_after_current_wait=imm, after_metadata_wait=late, events=page.evaluate("() => window.__log"))
    br.close()
srv.shutdown()
print(json.dumps(out, ensure_ascii=False))
