"""KP再生/Vocabulary音声/『ここから再生』/再生中の英文クリックでのキャプション整合を観察。使い方: py -3.14 observe_extra_caption_trial_01.py <base_url> <out_json>"""
import json, sys
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
base, outp = sys.argv[1].rstrip('/'), sys.argv[2]
S = """() => { const e = window.__EUP || {}; const on = Array.from(document.querySelectorAll('.jhl.on')).map(x => x.textContent).join('');
 const cap = document.getElementById('jcapT').textContent; return {mode: e.mode, jg: e.jg, ok: cap === on, cap: cap.slice(0, 20), paused: document.getElementById('aud').paused}; }"""
R = {}
with sync_playwright() as p:
    br = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    for vw, o in (("pc", dict(viewport={"width": 1280, "height": 900})), ("mobile", dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True))):
        for pg in ("x_adv", "y_std", "z_adv"):
            ctx = br.new_context(**o); page = ctx.new_page()
            page.goto(f"{base}/user_test/enduser_caption_trial_01/{pg}/index.html")
            page.wait_for_function("window.__EUP && window.__EUP.syncKind==='real'")
            res = {}
            def run(name, sel, ms=2500, idx=0):
                els = page.query_selector_all(sel)
                if len(els) <= idx: res[name] = "no-button"; return
                els[idx].scroll_into_view_if_needed(); els[idx].click()
                bad = 0; modes = set(); n = 0; changes = 0; last = None
                for _ in range(ms // 100):
                    page.wait_for_timeout(100); s = page.evaluate(S); n += 1; bad += (not s["ok"]); modes.add(s["mode"])
                    if last is not None and s["cap"] != last: changes += 1
                    last = s["cap"]
                res[name] = {"samples": n, "mismatch": bad, "modes": sorted(modes), "cap_changes": changes, "last_cap": last}
            run("kp_play", "button[data-act=kp]")
            run("vocab_play", "button[data-act=vocab]")
            run("from_here", "button[data-act=full]", 3000, 2)
            # 再生中に英文クリック(選択は一瞬のみで自動ハイライトへ戻る)
            page.evaluate("() => { const s = document.querySelectorAll('.sent'); s[s.length - 1].click(); }")
            page.wait_for_timeout(300); res["click_while_playing"] = page.evaluate(S)
            page.click("#pp"); page.wait_for_timeout(300)
            res["after_pause"] = page.evaluate(S)
            R[f"{vw}:{pg}"] = res; ctx.close()
    br.close()
json.dump(R, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in R.items(): print(k, json.dumps(v, ensure_ascii=False))
