# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PROTOTYPE-01 委任_01b: DEV試作ページのブラウザ検証(Playwright, ローカル静的サーバ)。
使い方: py verify_page_01.py [BASE_URL]   (既定 http://127.0.0.1:8765)
出力: docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/shots/*.png, verify_result_01.json
"""
import json, os, sys, time
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8766').rstrip('/')
PAGE = BASE + '/user_test/dev_enduser_page_01/index.html'
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.abspath(os.path.join(HERE, '..'))
LIVE = BASE.startswith('https://')
SHOTS = os.path.join(OUTD, 'shots_live' if LIVE else 'shots')
os.makedirs(SHOTS, exist_ok=True)
RES = {'base': BASE, 'runs': {}}

IPHONE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
VIEWS = {
    'pc': dict(viewport={'width': 1280, 'height': 900}),
    'mobile': dict(viewport={'width': 390, 'height': 844}, user_agent=IPHONE_UA, device_scale_factor=3, is_mobile=True, has_touch=True),
}


def wait_playing(page, min_t=0.3, timeout=6000):
    try:
        page.wait_for_function("() => { const a=document.getElementById('aud'); return !a.paused && a.currentTime>%s && a.readyState>=2; }" % min_t, timeout=timeout)
        return True
    except Exception:
        return False


def state(page):
    return page.evaluate("() => { const a=document.getElementById('aud'); return {t:a.currentTime, paused:a.paused, dur:a.duration, src:a.src.split('/').slice(-2).join('/'), eup:window.__EUP}; }")


def run_view(p, name, opts):
    browser = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    ctx = browser.new_context(**opts)
    page = ctx.new_page()
    errs, bad = [], []
    page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    page.on('response', lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)
    R = {'checks': {}}

    def chk(k, v, detail=None):
        R['checks'][k] = {'ok': bool(v), 'detail': detail}
        print(name, k, 'OK' if v else 'NG', detail if detail is not None else '')

    # ---- AI島 Std ----
    page.goto(PAGE + '?a=ai_island&lv=std&sync=off')
    page.wait_for_selector('.sent')
    page.wait_for_timeout(500)
    ow = page.evaluate('() => [document.documentElement.scrollWidth, window.innerWidth]')
    chk('std_no_horizontal_overflow', ow[0] <= ow[1], ow)
    chk('std_level_shown', 'standard' in page.text_content('#eyebrow').lower(), page.text_content('#eyebrow'))
    chk('std_dev_banner', 'DEV試作・正式公開ページではありません' in page.inner_text('.devbar'))
    chk('std_cards', page.evaluate("() => [...document.querySelectorAll('.card h2')].map(h=>h.textContent)"),
        page.evaluate("() => [...document.querySelectorAll('.card h2')].map(h=>h.textContent)"))
    chk('std_no_grammar_card_when_zero', page.locator('#grammar').count() == 0)
    chk('std_vocab_5', page.locator('details.vi').count() == 5, page.locator('details.vi').count())
    chk('std_kp_3', page.locator('.kpitem').count() == 3, page.locator('.kpitem').count())
    chk('std_sentence_spans', page.locator('.sent').count() > 40, page.locator('.sent').count())
    chk('std_kp_header', page.locator('.kpitem .th').first.inner_text() == '英語', page.locator('.kpitem .th').nth(1).inner_text())
    page.screenshot(path=os.path.join(SHOTS, '%s_01_top_std.png' % name))

    # 全体再生
    page.click('#playAll')
    chk('full_play_start', wait_playing(page), state(page))
    page.screenshot(path=os.path.join(SHOTS, '%s_02_playing_full_std.png' % name))
    # シーク(スライダ)
    page.fill('#seek', '500')
    page.wait_for_timeout(600)
    s = state(page)
    chk('seekbar_seek', 140 < s['t'] < 200, s['t'])
    t0 = s['t']
    page.click('#fwd10')
    page.wait_for_timeout(300)
    t1 = state(page)['t']
    chk('skip_fwd10', 9 < t1 - t0 < 12.5, [t0, t1])
    page.click('#back10')
    page.wait_for_timeout(300)
    t2 = state(page)['t']
    chk('skip_back10', 8 < t1 - t2 < 12.5, [t1, t2])
    # 一時停止/再開
    page.click('#pp')
    page.wait_for_timeout(300)
    chk('pause', state(page)['paused'])
    tp = state(page)['t']
    page.wait_for_timeout(500)
    chk('pause_holds_position', abs(state(page)['t'] - tp) < 0.05)
    page.click('#pp')
    chk('resume', wait_playing(page, tp + 0.2), state(page))
    page.click('#pp')

    # 全segment再生(Std)
    n = page.locator('button[data-act=part]').count()
    okseg, fails = 0, []
    seen = set()
    for i in range(n):
        b = page.locator('button[data-act=part]').nth(i)
        idx = b.get_attribute('data-i')
        if idx in seen:
            continue
        seen.add(idx)
        b.scroll_into_view_if_needed()
        b.click()
        if wait_playing(page, 0.15, 5000):
            okseg += 1
        else:
            fails.append(idx)
    chk('std_all_visible_parts_play', not fails, {'ok': okseg, 'fail': fails, 'distinct': len(seen)})
    # パート再生はそのパートだけで止まる(最短のKPで確認)
    page.locator('.kpitem button').first.click()
    wait_playing(page, 0.1)
    page.wait_for_function("() => document.getElementById('aud').paused", timeout=15000)
    chk('part_stops_at_end', state(page)['paused'], state(page))
    chk('part_label', 'パート' in page.inner_text('#nowLabel'), page.inner_text('#nowLabel'))
    # 通しで ▶
    page.locator('#fullstory button[data-act=full]').first.click()
    wait_playing(page, 0.3)
    st = state(page)
    chk('full_from_here', st['eup']['mode'] == 'full' and st['t'] > 70, st['t'])
    page.click('#pp')

    # ---- ダミー同期でハイライトフック確認 ----
    page.goto(PAGE + '?a=ai_island&lv=std&sync=dummy')
    page.wait_for_selector('.sent')
    page.wait_for_function("() => window.__EUP && window.__EUP.syncKind==='dummy'", timeout=5000)
    page.locator('#fullstory button[data-act=full]').first.click()
    wait_playing(page, 0.5)
    page.wait_for_timeout(1200)
    on = page.locator('.sent.on')
    chk('hook_highlight_on_during_play', on.count() == 1, on.count())
    sid1 = on.first.get_attribute('data-sid') if on.count() else None
    sid2 = sid1
    for _ in range(40):
        page.wait_for_timeout(500)
        sid2 = page.locator('.sent.on').first.get_attribute('data-sid') if page.locator('.sent.on').count() else None
        if sid2 and sid2 != sid1:
            break
    chk('hook_highlight_advances', sid1 and sid2 and sid1 != sid2, [sid1, sid2])
    page.screenshot(path=os.path.join(SHOTS, '%s_03_highlight_hook_dummy.png' % name))
    page.click('#pp')
    page.wait_for_timeout(300)
    chk('hook_highlight_stays_when_paused', page.locator('.sent.on').count() == 1)
    page.fill('#seek', '900')
    page.wait_for_timeout(500)
    sid3 = page.locator('.sent.on').first.get_attribute('data-sid') if page.locator('.sent.on').count() else None
    chk('hook_highlight_follows_seek_while_paused', sid3 and sid3 != sid2, [sid2, sid3])

    # ---- Adv ----
    page.goto(PAGE + '?a=ai_island&lv=std&sync=off')
    page.wait_for_selector('.sent')
    page.click('#tabs button[data-lv=adv]')
    page.wait_for_timeout(400)
    chk('adv_level_shown', 'advanced' in page.text_content('#eyebrow').lower())
    chk('adv_kp_header', page.locator('.kpitem .th').first.inner_text() == '英語' and page.locator('.kpitem .th').nth(1).inner_text() == '英語での解説', page.locator('.kpitem .th').nth(1).inner_text())
    chk('adv_no_grammar_card', page.locator('#grammar').count() == 0)
    page.click('#playAll')
    chk('adv_full_play', wait_playing(page), state(page))
    chk('adv_src_is_adv', 'advanced' in state(page)['src'], state(page)['src'])
    page.click('#pp')
    seen, okseg, fails = set(), 0, []
    for i in range(page.locator('button[data-act=part]').count()):
        b = page.locator('button[data-act=part]').nth(i)
        idx = b.get_attribute('data-i')
        if idx in seen:
            continue
        seen.add(idx)
        b.scroll_into_view_if_needed()
        b.click()
        if wait_playing(page, 0.15, 5000):
            okseg += 1
        else:
            fails.append(idx)
    chk('adv_all_visible_parts_play', not fails, {'ok': okseg, 'fail': fails, 'distinct': len(seen)})
    page.click('#pp')
    page.locator('#fullstory').scroll_into_view_if_needed()
    page.screenshot(path=os.path.join(SHOTS, '%s_04_fullstory_adv.png' % name))

    # ---- 月(Adv, 文法1件) ----
    page.goto(PAGE + '?a=moon&sync=off')
    page.wait_for_selector('.sent')
    chk('moon_grammar_shown', page.locator('#grammar').count() == 1)
    chk('moon_grammar_no_delimiter', '=====' not in page.inner_text('#grammar'))
    chk('moon_only_adv_tab', page.locator('#tabs button').count() == 1)
    page.locator('#grammar').scroll_into_view_if_needed()
    page.screenshot(path=os.path.join(SHOTS, '%s_05_grammar_moon.png' % name))
    page.click('#playAll')
    chk('moon_full_play', wait_playing(page), state(page))
    page.click('#pp')
    seen, okseg, fails = set(), 0, []
    for i in range(page.locator('button[data-act=part]').count()):
        b = page.locator('button[data-act=part]').nth(i)
        idx = b.get_attribute('data-i')
        if idx in seen:
            continue
        seen.add(idx)
        b.scroll_into_view_if_needed()
        b.click()
        if wait_playing(page, 0.15, 5000):
            okseg += 1
        else:
            fails.append(idx)
    chk('moon_all_visible_parts_play', not fails, {'ok': okseg, 'fail': fails, 'distinct': len(seen)})
    page.click('#pp')
    ow = page.evaluate('() => [document.documentElement.scrollWidth, window.innerWidth]')
    chk('moon_no_horizontal_overflow', ow[0] <= ow[1], ow)

    R['console_errors'] = errs
    R['http_4xx_5xx'] = bad
    chk('console_error_0', not errs, errs[:5])
    chk('http_4xx_0', not bad, bad[:5])
    RES['runs'][name] = R
    browser.close()


with sync_playwright() as p:
    for name, opts in VIEWS.items():
        run_view(p, name, opts)

ng = [(v, k) for v, r in RES['runs'].items() for k, c in r['checks'].items() if not c['ok']]
RES['ng'] = ng
json.dump(RES, open(os.path.join(OUTD, 'verify_result_live_01.json' if LIVE else 'verify_result_01.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('NG:', ng)
