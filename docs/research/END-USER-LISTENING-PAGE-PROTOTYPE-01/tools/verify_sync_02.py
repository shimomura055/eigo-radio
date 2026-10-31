# -*- coding: utf-8 -*-
"""委任_02: 1文ハイライトの精度/動作検証(Playwright)。py verify_sync_02.py [BASE]  既定 http://127.0.0.1:8767
出力: verify_result_02.json (live時 verify_result_live_02.json), shots/pc_hl_01..03, mobile_hl_01..03 (live時 shots_live/)
精度測定の意味: 各文の境界(start/end)の前後0.3sへ実際にaudioをシークし、ページが点灯するsidが
同期データ(01a由来)の期待と一致するかを見る=「ページ実装+時刻基準変換(全編/パート)」の整合。
同期データ自体の聴感上の正しさ(ASR+無音スナップ精度)は別(01a VERIFY.json、ユーザー聴感未確認)。"""
import json, os, sys, urllib.request
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8767').rstrip('/')
LIVE = BASE.startswith('https://')
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.abspath(os.path.join(HERE, '..'))
SHOTS = os.path.join(OUTD, 'shots_live' if LIVE else 'shots'); os.makedirs(SHOTS, exist_ok=True)
PAGE = BASE + '/user_test/dev_enduser_page_01/index.html'
DATA = BASE + '/user_test/dev_enduser_page_01/data/'
CASES = [('ai_island', 'std'), ('ai_island', 'adv'), ('moon', 'adv')]
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
VIEWS = {'pc': dict(viewport={'width': 1280, 'height': 900}),
         'mobile': dict(viewport={'width': 390, 'height': 844}, user_agent=UA, device_scale_factor=2, is_mobile=True, has_touch=True)}
RES = {'base': BASE, 'precision': {}, 'realtime': {}, 'errors': []}


def getj(u):
    return json.load(urllib.request.urlopen(u))


def expect(rows, g):
    for r in rows:
        if r['start'] <= g < r['end']:
            return r['sid']
    return None


def seek_read(page, t):
    return page.evaluate("""(t) => new Promise(res => { const a=document.getElementById('aud');
      const done=()=>{ requestAnimationFrame(()=>requestAnimationFrame(()=>res({a:(window.__EUP||{}).active, t:a.currentTime}))); };
      a.addEventListener('seeked', done, {once:true}); a.currentTime=t; setTimeout(done, 2000); })""", t)


def points(r):
    d = r['end'] - r['start']
    pin = [r['start'] + 0.3, r['end'] - 0.3] if d >= 0.6 else [(r['start'] + r['end']) / 2]
    return {'inside': pin, 'cross': [r['start'] - 0.3, r['end'] + 0.3]}


def new_page(p, view):
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    page = b.new_context(**VIEWS[view]).new_page()
    page.on('pageerror', lambda e: RES['errors'].append(str(e)))
    return b, page


def open_article(page, aid, lv):
    page.goto(PAGE + '?a=%s&lv=%s' % (aid, lv)); page.wait_for_selector('.sent')
    page.wait_for_function("()=>document.getElementById('syncState').textContent.includes('実同期')")


def precision(p, aid, lv):
    b, page = new_page(p, 'pc')
    rows = getj(DATA + 'sync_%s_%s.json' % (aid, lv))['sentences']
    pinfo = getj(DATA + '%s.json' % aid)['levels'][lv]['parts']
    bykey = {pp['key']: pp for pp in pinfo}
    open_article(page, aid, lv)
    page.evaluate("()=>{document.getElementById('aud').muted=true;}")
    page.click('#playAll'); page.wait_for_function("()=>document.getElementById('aud').readyState>=2", timeout=15000)
    page.evaluate("()=>document.getElementById('aud').pause()")
    out = {m: {k: [] for k in ('inside', 'cross')} for m in ('full', 'part')}
    for r in rows:                                   # 全編(main mp3, 全編時刻)
        for kind, pts in points(r).items():
            for g in pts:
                if g < 0: continue
                got = seek_read(page, g); exp = expect(rows, g)
                out['full'][kind].append(dict(sid=r['sid'], g=round(g, 3), exp=exp, got=got['a'], ok=got['a'] == exp))
    keys = []
    for r in rows:
        k = r['sid'].split('-')[0]
        if k not in keys: keys.append(k)
    for k in keys:                                   # パート(segment mp3, パート局所時刻)
        pp = bykey[k]; prow = [r for r in rows if r['sid'].startswith(k + '-')]
        page.click('button[data-act="part"][data-i="%d"]' % pp['idx'])
        page.wait_for_function("()=>document.getElementById('aud').readyState>=2", timeout=15000)
        page.evaluate("()=>{const a=document.getElementById('aud');a.muted=true;a.pause();}")
        for r in prow:
            for kind, pts in points(r).items():
                for g in pts:
                    lt = g - pp['start']
                    if lt < 0 or lt > pp['dur'] - 0.05: continue
                    got = seek_read(page, lt); exp = expect(prow, g)
                    out['part'][kind].append(dict(sid=r['sid'], g=round(g, 3), exp=exp, got=got['a'], ok=got['a'] == exp))
    b.close()
    summ = {}
    for m in out:
        for kind in out[m]:
            L = out[m][kind]; summ['%s_%s' % (m, kind)] = dict(n=len(L), ok=sum(x['ok'] for x in L), rate=round(sum(x['ok'] for x in L) / max(1, len(L)), 4))
    for m in out:
        bad = {x['sid'] for x in out[m]['inside'] if not x['ok']}
        summ['%s_sentences_tested' % m] = len({x['sid'] for x in out[m]['inside']})
        summ['%s_sentences_inside_all_ok' % m] = len({x['sid'] for x in out[m]['inside']} - bad)
    mism = [dict(mode=m, kind=kind, **x) for m in out for kind in out[m] for x in out[m][kind] if not x['ok']]
    RES['precision']['%s/%s' % (aid, lv)] = dict(summary=summ, mismatches=mism)
    print(aid, lv, summ, 'mismatch', len(mism), flush=True)


def realtime(p, view, aid, lv, partkey, shot, secs=14):
    b, page = new_page(p, view)
    rows = getj(DATA + 'sync_%s_%s.json' % (aid, lv))['sentences']
    pp = [x for x in getj(DATA + '%s.json' % aid)['levels'][lv]['parts'] if x['key'] == partkey][0]
    prow = [r for r in rows if r['sid'].startswith(partkey + '-')]
    open_article(page, aid, lv)
    page.click('button[data-act="part"][data-i="%d"]' % pp['idx'])
    page.wait_for_function("()=>{const a=document.getElementById('aud');return !a.paused&&a.currentTime>0.2}", timeout=10000)
    samples, seq = [], []
    n = int(secs / 0.25)
    for i in range(n):
        s = page.evaluate("()=>({t:document.getElementById('aud').currentTime, e:window.__EUP})")
        g = pp['start'] + s['t']; a = s['e']['active']
        samples.append(dict(t=round(s['t'], 2), got=a, exp=expect(rows, g)))
        if a and (not seq or seq[-1] != a): seq.append(a)
        if i == n // 2 and shot: page.screenshot(path=os.path.join(SHOTS, shot))
        page.wait_for_timeout(250)
    page.click('#pp'); page.wait_for_timeout(300)
    h1 = page.evaluate("()=>window.__EUP.active"); page.wait_for_timeout(1500); h2 = page.evaluate("()=>window.__EUP.active")
    paused = page.evaluate("()=>document.getElementById('aud').paused")
    target = prow[-1]
    loc = page.locator('[data-sid="%s"]' % target['sid']).first
    loc.scroll_into_view_if_needed(); loc.click(); page.wait_for_timeout(1000)
    cs = page.evaluate("()=>({gt:window.__EUP.gt, active:window.__EUP.active, paused:window.__EUP.paused, mode:window.__EUP.mode})")
    b.close()
    order = [r['sid'] for r in rows]
    R = dict(samples=len(samples), mismatch_samples=sum(1 for s in samples if s['got'] != s['exp']), sequence=seq,
             advanced=len(seq) >= 2, in_order=seq == sorted(seq, key=order.index), paused_ok=paused, pause_hold=(h1 == h2 and h1 is not None),
             click=dict(target=target['sid'], target_start=round(target['start'], 3), result=cs,
                        ok=bool(abs(cs['gt'] - target['start']) < 2.5 and cs['active'] is not None)))
    RES['realtime']['%s/%s/%s/%s' % (view, aid, lv, partkey)] = R
    print(view, aid, lv, partkey, R, flush=True)


with sync_playwright() as p:
    for aid, lv in CASES: precision(p, aid, lv)
    plan = [('pc', 'ai_island', 'std', 'std_15', 'pc_hl_01.png'), ('pc', 'ai_island', 'adv', 'adv_16', 'pc_hl_02.png'), ('pc', 'moon', 'adv', 'adv_14', 'pc_hl_03.png'),
            ('mobile', 'ai_island', 'std', 'std_17', 'mobile_hl_01.png'), ('mobile', 'ai_island', 'adv', 'adv_18', 'mobile_hl_02.png'), ('mobile', 'moon', 'adv', 'adv_16', 'mobile_hl_03.png'),
            ('pc', 'ai_island', 'std', 'std_19', None), ('pc', 'moon', 'adv', 'adv_18', None)]
    for v, a, l, k, sh in plan: realtime(p, v, a, l, k, sh)
agg = {}
for m in ('full', 'part'):
    for kind in ('inside', 'cross'):
        n = ok = 0
        for r in RES['precision'].values():
            s = r['summary']['%s_%s' % (m, kind)]; n += s['n']; ok += s['ok']
        agg['%s_%s' % (m, kind)] = dict(n=n, ok=ok, rate=round(ok / max(1, n), 4))
RES['aggregate'] = agg
json.dump(RES, open(os.path.join(OUTD, 'verify_result_live_02.json' if LIVE else 'verify_result_02.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('AGG', agg, 'errors', RES['errors'])
