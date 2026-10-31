# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-DEV-REVISION-01: 10項目改修の実操作検証(Playwright)。
使い方: py verify_rev_01.py <BASE_URL> [expected_build_id]
  local: http://127.0.0.1:8771 / live: https://shimomura055.github.io/eigo-radio
出力: ../shots_rev/(live時 shots_rev_live/){pc,mobile}_01..10.png, ../verify_result_rev_{local,live}_01.json
PASS は実ブラウザ操作の観測値がある項目のみ。"""
import json, os, re, sys, time, urllib.request
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8771').rstrip('/')
EXPECT_BUILD = sys.argv[2] if len(sys.argv) > 2 else None
LIVE = BASE.startswith('https://')
HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.abspath(os.path.join(HERE, '..'))
SHOTS = os.path.join(OUTD, 'shots_rev_live' if LIVE else 'shots_rev')
os.makedirs(SHOTS, exist_ok=True)
PAGE = BASE + '/user_test/dev_enduser_page_01/index.html'
DATA = BASE + '/user_test/dev_enduser_page_01/data/'
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
VIEWS = {'pc': dict(viewport={'width': 1280, 'height': 900}),
         'mobile': dict(viewport={'width': 390, 'height': 844}, user_agent=UA, device_scale_factor=2, is_mobile=True, has_touch=True)}
CASES = [('ai_island', 'std'), ('ai_island', 'adv'), ('moon', 'adv')]
RES = {'base': BASE, 'expect_build': EXPECT_BUILD, 'views': {}}
JA = re.compile(r'[ぁ-んァ-ヶ一-龠]')


def getj(u):
    req = urllib.request.Request(u + ('&' if '?' in u else '?') + 'cb=%d' % time.time(), headers={'Cache-Control': 'no-cache'})
    return json.load(urllib.request.urlopen(req))


DATAJ = {a: getj(DATA + a + '.json') for a in ('ai_island', 'moon')}


def parts_of(a, lv):
    return DATAJ[a]['levels'][lv]['parts']


def pidx(a, lv, label):
    return [p['idx'] for p in parts_of(a, lv) if p['label'] == label][0]


def open_article(page, a, lv, wait_sync=True):
    page.goto(PAGE + '?a=%s&lv=%s&cb=%d' % (a, lv, time.time()))
    page.wait_for_selector('.sent')
    if wait_sync:
        page.wait_for_function("()=>document.getElementById('syncState').textContent.includes('実同期')")
    page.wait_for_timeout(300)


def A(page):
    return page.evaluate("() => { const a=document.getElementById('aud'); return {t:a.currentTime, paused:a.paused, src:a.src.split('/').pop(), eup:window.__EUP}; }")


def run_view(p, view, opts):
    browser = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    ctx = browser.new_context(**opts)
    page = ctx.new_page()
    errs, bad = [], []
    page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    page.on('response', lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)
    R = {}
    RES['views'][view] = R

    def rec(item, key, ok, detail=None):
        R.setdefault(item, {})[key] = {'ok': bool(ok), 'detail': detail}
        print(view, item, key, 'OK' if ok else 'NG', detail if detail is not None else '')

    def shot(n, sel=None):
        if sel:
            page.evaluate("(s) => { const e=document.querySelector(s); if(e) e.scrollIntoView({block:'start'}); window.scrollBy(0,-12); }", sel)
            page.wait_for_timeout(250)
        page.screenshot(path=os.path.join(SHOTS, '%s_%02d.png' % (view, n)))

    # ---------- build id ----------
    open_article(page, 'ai_island', 'std')
    bid = page.evaluate("() => [document.body.dataset.build, (document.querySelector('meta[name=build-id]')||{}).content]")
    R['build'] = bid
    if EXPECT_BUILD:
        rec('0_build', 'build_id_matches', bid[0] == EXPECT_BUILD and bid[1] == EXPECT_BUILD, bid)

    # ---------- 1 全体再生ボタン ----------
    open_article(page, 'ai_island', 'std')
    g = page.evaluate("""() => { const t=document.getElementById('tabs').getBoundingClientRect(), b=document.getElementById('playAll').getBoundingClientRect();
      const cs=getComputedStyle(document.getElementById('playAll')); return {tabsBottom:t.bottom, btnTop:b.top, btnW:b.width, btnH:b.height, tabsH:t.height, fs:cs.fontSize, text:document.getElementById('playAll').textContent, vw:innerWidth}; }""")
    rec('1', 'below_tabs', g['btnTop'] >= g['tabsBottom'] - 1, g)
    rec('1', 'enlarged', g['btnH'] >= 60 and float(g['fs'][:-2]) >= 20 and g['btnW'] >= (300 if view == 'mobile' else 400), g)
    page.click('#playAll')
    ok = False
    try:
        page.wait_for_function("() => { const a=document.getElementById('aud'); return !a.paused && a.currentTime>0.5; }", timeout=8000)
        ok = True
    except Exception:
        pass
    rec('1', 'click_plays_full_audio', ok and 'standard.mp3' in A(page)['src'], A(page))
    page.evaluate("document.getElementById('aud').pause()")
    page.evaluate('window.scrollTo(0,0)')
    shot(1)
    # タブ機能は不変
    page.click('#tabs button[data-lv=adv]')
    page.wait_for_timeout(500)
    rec('1', 'tabs_still_switch', 'advanced' in page.text_content('#eyebrow').lower() and 'advanced.mp3' in A(page)['src'], page.text_content('#eyebrow'))

    # ---------- 2 Key Phrase 英語のみ ----------
    for a, lv in CASES:
        open_article(page, a, lv)
        kps = [p for p in parts_of(a, lv) if p['kind'] == 'kp']
        btns = page.query_selector_all('.kpitem button[data-act=kp]')
        rec('2', '%s_%s_kp_buttons' % (a, lv), len(btns) == len(kps) == 3, len(btns))
        for i, p in enumerate(kps):
            ea = p['kp'][0]['en_audio']
            btns[i].scroll_into_view_if_needed()
            btns[i].click()
            t0 = time.time()
            samples = page.evaluate("""(end) => new Promise(res => { const a=document.getElementById('aud'); const out=[]; const t0=performance.now();
              (function f(){ out.push([Math.round(performance.now()-t0), +a.currentTime.toFixed(3), a.paused, /(std|adv)_\d\d\.mp3$/.test(a.src)]); if (performance.now()-t0 > 9000 || (a.paused && out.length>30 && a.currentTime>0)) res(out); else requestAnimationFrame(f); })(); })""", ea['end'])
            segs = [s for s in samples if s[3]]
            started = [s for s in segs if not s[2] and s[1] > 0]
            first_t = started[0][1] if started else None
            maxt = max(s[1] for s in segs)
            stopped = samples[-1][2]
            leftseg = not samples[-1][3]
            played = (maxt - ea['start'])
            st = A(page)
            ok_play = bool(started) and abs(first_t - ea['start']) < 0.6 and stopped and leftseg
            ok_end = maxt <= ea['end'] + 0.35 and maxt >= ea['end'] - 0.2
            # 日本語/英語解説区間(3番目のブロック開始以降)に入っていない
            seg_blocks = None
            rec('2', '%s_%s_%s_plays_english_window_only' % (a, lv, p['label'].replace(' ', '')), ok_play and ok_end,
                dict(window=[ea['start'], ea['end']], first_t=first_t, max_t=round(maxt, 3), played_sec=round(played, 3), stopped_paused=stopped, returned_to_full_audio=leftseg, seg_dur=p['dur'], after_src=st['src']))
    open_article(page, 'ai_island', 'std')
    page.query_selector_all('.kpitem button[data-act=kp]')[0].scroll_into_view_if_needed()
    shot(2, '.kp')
    shot(2, '.kp')

    # ---------- 3 / 4 意味一覧 ----------
    for a, lv in CASES:
        open_article(page, a, lv)
        parts = parts_of(a, lv)
        dom = page.evaluate("""() => [...document.querySelectorAll('[data-part]')].filter(e => e.classList.contains('partblock')).map(b => ({
            part: +b.dataset.part,
            hl: [...new Set([...b.querySelectorAll('.script [data-hl]')].map(x => x.dataset.hl))],
            hl_text: [...new Set([...b.querySelectorAll('.script [data-hl]')].map(x => x.textContent.trim().toLowerCase()))],
            items: [...b.querySelectorAll('.gloss li')].map(li => ({en: li.querySelector('.ge').textContent, ja: li.querySelector('.gj').textContent, link: li.querySelector('.glink') ? li.querySelector('.glink').getAttribute('href') : null})),
            gloss_after_text: (() => { const g=b.querySelector('.gloss'); const s=[...b.querySelectorAll('.script')].pop(); return g && s ? (s.compareDocumentPosition(g) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0 : null; })()
        }))""")
        allen = []
        miss = []
        for d in dom:
            p = parts[d['part']]
            expect_n = len(d['hl'])
            allen += [x['en'] for x in d['items']]
            if len(d['items']) != expect_n:
                miss.append((p['label'], expect_n, len(d['items'])))
            if d['hl'] and not d['gloss_after_text']:
                miss.append((p['label'], 'gloss_not_after_body'))
            for x in d['items']:
                if not x['ja'] or JA.search(x['ja']) is None:
                    miss.append((p['label'], 'no_ja', x['en']))
        vocab = DATAJ[a]['levels'][lv]['vocab']
        kp_en = [k['en'] for p in parts if p['kind'] == 'kp' for k in p['kp']]
        rec('3', '%s_%s_list_covers_underlined_in_each_block' % (a, lv), not miss, dict(blocks=[(parts[d['part']]['label'], len(d['items'])) for d in dom], miss=miss))
        rec('3', '%s_%s_no_duplicates' % (a, lv), len(allen) == len(set(allen)), allen)
        rec('3', '%s_%s_contains_all_KP_and_Vocab' % (a, lv), all(h in allen for h in kp_en) and all(v['heading'] in allen for v in vocab), dict(kp=kp_en, vocab=[v['heading'] for v in vocab]))
        # リンク → 該当表現のアンカー位置へ移動
        links = page.query_selector_all('.gloss a.glink')
        rec('3', '%s_%s_link_count_eq_vocab' % (a, lv), len(links) == len(vocab), len(links))
        bad_link = []
        for li in links:
            en = li.evaluate("e => e.parentElement.querySelector('.ge').textContent")
            href = li.get_attribute('href')
            li.scroll_into_view_if_needed()
            li.click()
            page.wait_for_timeout(900)
            r = page.evaluate("""(href) => { const t=document.getElementById(href.slice(1)); if(!t) return null; const b=t.getBoundingClientRect();
              return {top:b.top, open:t.open, head:t.querySelector('.vh').textContent, vh:innerHeight}; }""", href)
            if not r or r['head'] != en or not r['open'] or not (-5 <= r['top'] <= r['vh'] * 0.75):
                bad_link.append((en, href, r))
        rec('3', '%s_%s_each_link_scrolls_to_that_expression' % (a, lv), not bad_link and len(links) > 0, bad_link or 'all %d links OK' % len(links))
    open_article(page, 'ai_island', 'std')
    li = page.query_selector('.gloss a.glink')
    li.scroll_into_view_if_needed()
    shot(3, '.gloss')
    li.click()
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(SHOTS, '%s_03b_after_link.png' % view))

    # 4 デザイン(ai std)
    open_article(page, 'ai_island', 'std')
    d4 = page.evaluate("""() => { const g=document.querySelector('.gloss'), ul=g.querySelector('ul'), cs=getComputedStyle(g), us=getComputedStyle(ul), sc=getComputedStyle(document.querySelector('.partblock .script'));
      const lis=[...ul.children].map(l => Math.round(l.getBoundingClientRect().left));
      return {cols: us.gridTemplateColumns.split(' ').length, distinctLeft: [...new Set(lis)].length, bg: cs.backgroundColor, border: cs.borderTopWidth + ' ' + cs.borderTopColor, gfs: cs.fontSize, sfs: sc.fontSize,
        ja: getComputedStyle(g.querySelector('.gj')).color, w: g.getBoundingClientRect().width, h: g.getBoundingClientRect().height}; }""")
    want_cols = 2 if view == 'pc' else 1
    rec('4', 'columns_%d' % want_cols, d4['cols'] == want_cols and (d4['distinctLeft'] == want_cols), d4)
    rec('4', 'muted_bg_and_border', d4['bg'] != 'rgb(255, 255, 255)' and d4['border'].startswith('1px'), d4)
    rec('4', 'smaller_than_body', float(d4['gfs'][:-2]) < float(d4['sfs'][:-2]), d4)
    rec('4', 'ja_dark_color', d4['ja'] in ('rgb(31, 41, 51)', 'rgb(16, 24, 40)'), d4['ja'])
    page.evaluate("document.querySelectorAll('.gloss')[1].scrollIntoView({block:'center'})")
    page.wait_for_timeout(300)
    shot(4)

    # ---------- 5 日本語訳 ----------
    miss5 = []
    cnt = dict(approved=0, dev=0, native_ja=0)
    for a, lv in CASES:
        open_article(page, a, lv)
        parts = parts_of(a, lv)
        for p in parts:
            if p['kind'] not in ('comment', 'story', 'oneline'):
                continue
            blk = page.query_selector('[data-part="%d"].partblock, [data-part="%d"].comment' % (p['idx'], p['idx']))
            en_text = ''.join(s['text'] for pa in p['paragraphs'] for s in pa)
            is_en = JA.search(en_text) is None
            info = blk.evaluate("""b => { const tr=b.querySelector('.tr'); const sc=[...b.querySelectorAll('.script')].pop();
               return {tr: tr ? [...tr.querySelectorAll('p')].map(x => x.textContent) : null, src: tr ? tr.dataset.src : null,
                       after: tr && sc ? sc.nextElementSibling === tr : null, empty: tr ? [...tr.querySelectorAll('p')].some(x => !x.textContent.trim()) : null}; }""")
            if is_en:
                if not info['tr'] or info['empty'] or not info['after'] or len(info['tr']) != len(p['paragraphs']) or not all(JA.search(t) for t in info['tr']):
                    miss5.append((a, lv, p['label'], info))
                else:
                    cnt['approved' if info['src'] == 'approved_ja_manuscript' else 'dev'] += 1
            else:
                cnt['native_ja'] += 1
                if info['tr']:
                    miss5.append((a, lv, p['label'], 'unexpected tr on JA block'))
        dummy = page.evaluate("() => /ダミー|TODO|lorem|xxx/i.test(document.body.innerText)")
        if dummy:
            miss5.append((a, lv, 'dummy-like text'))
    rec('5', 'all_en_blocks_have_ja_translation_after_body_no_gap', not miss5, dict(counts=cnt, miss=miss5))
    open_article(page, 'ai_island', 'adv')
    shot(5, '.comment')
    page.evaluate("document.querySelector('.partblock').scrollIntoView({block:'start'}); window.scrollBy(0,-8)")
    page.wait_for_timeout(250)
    page.screenshot(path=os.path.join(SHOTS, '%s_05b_part.png' % view))

    # ---------- 6 ここから再生 ----------
    for a, lv, lab_from, lab_next in [('ai_island', 'adv', 'Comment 1', 'Full Story Part 1'), ('ai_island', 'std', 'Comment 3', 'Full Story Part 3'), ('moon', 'adv', 'Comment 3', 'Full Story Part 3')]:
        open_article(page, a, lv)
        txt = page.evaluate("() => document.body.innerText")
        rec('6', '%s_%s_no_old_labels' % (a, lv), 'このパート' not in txt and '通しで' not in txt, None)
        rows = page.evaluate("""() => [...document.querySelectorAll('[data-part]')].map(e => ({part:+e.dataset.part, n:e.querySelectorAll(':scope > .ph .seek, :scope > .ch .seek, :scope > .sectionhead .seek, :scope .btns .seek').length, t:[...e.querySelectorAll('.btns .seek')].map(b=>b.textContent)})).filter(r => r.t.length)""")
        rec('6', '%s_%s_single_button_each' % (a, lv), all(set(r['t']) == {'▶ ここから再生'} for r in rows) and len(rows) > 5, [r['t'] for r in rows][:4])
        pi, pn = pidx(a, lv, lab_from), pidx(a, lv, lab_next)
        start_from, start_next = parts_of(a, lv)[pi]['start'], parts_of(a, lv)[pn]['start']
        b = page.query_selector('[data-part="%d"] .btns .seek' % pi)
        b.scroll_into_view_if_needed()
        b.click()
        try:
            page.wait_for_function("(t) => { const a=document.getElementById('aud'); return !a.paused && a.currentTime>t-1 && a.currentTime<t+2 && window.__EUP && window.__EUP.mode==='full'; }", arg=start_from, timeout=8000)
        except Exception:
            pass
        s0 = A(page)
        rec('6', '%s_%s_starts_at_part_start_in_full_audio' % (a, lv), (not s0['paused']) and abs(s0['t'] - start_from) < 2.0 and s0['eup']['mode'] == 'full', dict(start=start_from, now=round(s0['t'], 2), src=s0['src']))
        # パート終了を越えて連続再生(実時間)。Comment 1 -> Part 1 開始を実時間で跨ぐ
        need = start_next - start_from
        t0 = time.time()
        crossed = None
        pre_paused = False
        while time.time() - t0 < need + 12:
            s = A(page)
            if s['paused']:
                pre_paused = True
            if s['eup']['gt'] > start_next + 1.0:
                crossed = s
                break
            page.wait_for_timeout(250)
        rec('6', '%s_%s_continues_across_part_boundary' % (a, lv), crossed is not None and not crossed['paused'] and not pre_paused and 'mp3' in crossed['src'] and crossed['eup']['mode'] == 'full',
            dict(from_label=lab_from, to_label=lab_next, boundary=start_next, gt_after=(crossed or {}).get('eup', {}).get('gt'), waited=round(time.time() - t0, 1), ever_paused=pre_paused))
        if crossed:
            act = crossed['eup']['active']
            rec('6', '%s_%s_highlight_moves_into_next_part' % (a, lv), bool(act) and act.startswith(parts_of(a, lv)[pn]['key']), dict(active=act, expect_prefix=parts_of(a, lv)[pn]['key']))
        if lv == 'adv' and a == 'ai_island':
            shot(6)
    # 長いPart内からのシーク後の連続(Part 1 -> Comment 2): シークバー操作で終端近くへ移動し実時間で跨ぐ
    a, lv = 'ai_island', 'adv'
    open_article(page, a, lv)
    pi = pidx(a, lv, 'Full Story Part 1')
    pn = pidx(a, lv, 'Comment 2')
    ps, pe = parts_of(a, lv)[pi]['start'], parts_of(a, lv)[pn]['start']
    b = page.query_selector('[data-part="%d"].partblock .btns .seek' % pi)
    b.scroll_into_view_if_needed()
    b.click()
    page.wait_for_function("() => !document.getElementById('aud').paused && document.getElementById('aud').currentTime>0.3", timeout=8000)
    total = DATAJ[a]['levels'][lv]['total_sec']
    page.evaluate("(v) => { const s=document.getElementById('seek'); s.value=v; s.dispatchEvent(new Event('input',{bubbles:true})); }", int((pe - 3.0) / total * 1000))
    t0 = time.time()
    got = None
    while time.time() - t0 < 12:
        s = A(page)
        if s['eup']['gt'] > pe + 1.0:
            got = s
            break
        page.wait_for_timeout(250)
    rec('6', 'part1_to_comment2_continues_after_seek_near_end', got is not None and not got['paused'], dict(boundary=pe, gt=(got or {}).get('eup', {}).get('gt'), active=(got or {}).get('eup', {}).get('active')))
    page.evaluate("document.getElementById('aud').pause()")

    # ---------- 7 Full Story + In One Line 連結 ----------
    for a, lv in CASES:
        open_article(page, a, lv)
        parts = parts_of(a, lv)
        d7 = page.evaluate("""() => { const h2s=[...document.querySelectorAll('.card h2')].map(h=>h.textContent); const fs=document.getElementById('fullstory');
           const ol=fs.querySelector('.partblock.oneline'); const blocks=[...fs.children].filter(e=>e.dataset.part!==undefined).map(e=>e.dataset.part);
           const c4=[...fs.querySelectorAll('.comment')].pop(); const sects=[...document.querySelectorAll('.card')].map(c=>c.id||c.querySelector('h2').textContent);
           return {h2s, inFs: !!ol, head: ol && ol.querySelector('h3').textContent, order: blocks, c4Label: c4.querySelector('strong').textContent,
                   gap: ol ? Math.round(ol.getBoundingClientRect().top - [...fs.querySelectorAll('.partblock')].slice(-2)[0].getBoundingClientRect().bottom) : null,
                   cardsBetween: sects, sibling_is_oneline: c4.nextElementSibling && c4.nextElementSibling.classList.contains('oneline')}; }""")
        okc = d7['inFs'] and d7['head'] == 'In One Line' and 'In One Line' not in d7['h2s'] and d7['c4Label'] == 'Comment 4'
        # Comment 4 の次の要素が In One Line(間に別カードなし)
        rec('7', '%s_%s_oneline_inside_fullstory_card_after_comment4' % (a, lv), okc and d7['order'][-1] == str(pidx(a, lv, 'In One Line')) and d7['order'][-2] == str(pidx(a, lv, 'Comment 4')), d7)
        ol_idx = pidx(a, lv, 'In One Line')
        st = parts[ol_idx]['start']
        page.evaluate("(t) => { const a=document.getElementById('aud'); a.currentTime=t; a.play(); }", st + 1.0)
        page.wait_for_timeout(1500)
        s = A(page)
        sids = [x['sid'] for pa in parts[ol_idx]['paragraphs'] for x in pa]
        rec('7', '%s_%s_oneline_highlight_works' % (a, lv), s['eup']['active'] in sids, dict(active=s['eup']['active']))
        page.evaluate("document.getElementById('aud').pause()")
        # 日本語訳が In One Line 直後に表示
        trok = page.evaluate("(i) => { const b=document.querySelector('.partblock.oneline'); const t=b.querySelector('.tr'); return !!t && t.textContent.length>20; }", ol_idx)
        rec('7', '%s_%s_oneline_has_ja' % (a, lv), trok, None)
        if (a, lv) == ('ai_island', 'adv'):
            page.evaluate("document.querySelector('.partblock.oneline').scrollIntoView({block:'center'})")
            page.wait_for_timeout(300)
            shot(7)

    # ---------- 8 文法 ----------
    open_article(page, 'moon', 'adv')
    h2 = page.evaluate("() => [...document.querySelectorAll('.card h2')].map(h=>h.textContent)")
    g8 = page.evaluate("""() => { const g=document.getElementById('grammar'); if(!g) return null; const dts=[...g.querySelectorAll('dt')].map(x=>x.textContent); const dds=[...g.querySelectorAll('dd')].map(x=>x.textContent.length);
        return {dts, dds, w:g.getBoundingClientRect().width, overflow: g.scrollWidth > g.clientWidth + 1, fs:getComputedStyle(g.querySelector('dd')).fontSize}; }""")
    gdata = DATAJ['moon']['levels']['adv']['grammar']
    rec('8', 'moon_adv_shows_vocab_and_grammar', 'Vocabulary & Expressions' in h2 and 'Grammar & Sentence Structure' in h2 and g8 and len(g8['dts']) == sum(len(x['fields']) for x in gdata) and all(n > 5 for n in g8['dds']) and not g8['overflow'], dict(h2=h2, g8=g8, data_items=len(gdata)))
    vcount = page.evaluate("() => document.querySelectorAll('#vocab details.vi').length")
    rec('8', 'moon_adv_vocab_items_eq_data', vcount == len(DATAJ['moon']['levels']['adv']['vocab']), vcount)
    page.evaluate("document.getElementById('grammar').scrollIntoView({block:'start'}); window.scrollBy(0,-12)")
    page.wait_for_timeout(300)
    shot(8)
    for lv in ('std', 'adv'):
        open_article(page, 'ai_island', lv)
        h2 = page.evaluate("() => [...document.querySelectorAll('.card h2')].map(h=>h.textContent)")
        has = page.evaluate("() => !!document.getElementById('grammar') || /Grammar/.test(document.body.innerText)")
        rec('8', 'ai_island_%s_grammar_hidden_when_zero' % lv, (not has) and len(DATAJ['ai_island']['levels'][lv]['grammar']) == 0 and 'Vocabulary & Expressions' in h2, h2)
    page.evaluate("document.getElementById('vocab').scrollIntoView({block:'start'})")
    page.screenshot(path=os.path.join(SHOTS, '%s_08b_ai_no_grammar.png' % view))

    # ---------- 9 解説の文字サイズ・色 ----------
    open_article(page, 'moon', 'adv')
    d9 = page.evaluate("""() => { const d=document.querySelector('details.vi'); d.open=true; const dd=d.querySelector('dd'), s=d.querySelector('summary .vm'), h=d.querySelector('summary .vh'), dt=d.querySelector('dt');
       const c=e=>getComputedStyle(e); return {dd_fs:c(dd).fontSize, dd_color:c(dd).color, vm_fs:c(s).fontSize, vm_color:c(s).color, vh_fs:c(h).fontSize, vh_fw:c(h).fontWeight, dt_fs:c(dt).fontSize, body_fs:c(document.body).fontSize, ja_mean_text:s.textContent}; }""")
    rec('9', 'font_enlarged_vs_old_16px_and_old_muted_grey', float(d9['dd_fs'][:-2]) >= 16.5 and float(d9['vm_fs'][:-2]) >= 17, d9)
    rec('9', 'ja_meaning_dark_not_grey', d9['vm_color'] == 'rgb(16, 24, 40)' and d9['dd_color'] == 'rgb(16, 24, 40)', d9)
    rec('9', 'balance_heading_ge_meaning_ge_body', float(d9['vh_fs'][:-2]) >= float(d9['vm_fs'][:-2]) >= float(d9['dd_fs'][:-2]) - 0.6, d9)
    page.evaluate("document.querySelector('details.vi').scrollIntoView({block:'start'}); window.scrollBy(0,-8)")
    page.wait_for_timeout(300)
    shot(9)

    # ---------- 10 凡例削除 / 強調維持 ----------
    for a, lv in CASES:
        open_article(page, a, lv)
        d10 = page.evaluate("""() => { const t=document.body.innerText; const l1=document.querySelector('.lk1'), l2=document.querySelector('.lk2'), l3=document.querySelector('.lk3');
          const g=e=>e?{fw:getComputedStyle(e).fontWeight, td:getComputedStyle(e).textDecorationLine+' '+getComputedStyle(e).textDecorationStyle}:null;
          return {legend_text: /本文の下線/.test(t) || /太字\\+二重下線|太字＋二重下線/.test(t), legend_els: document.querySelectorAll('.legend').length, lk1:document.querySelectorAll('.lk1').length, lk2:document.querySelectorAll('.lk2').length, lk3:document.querySelectorAll('.lk3').length, s1:g(l1), s2:g(l2), s3:g(l3)}; }""")
        okk = (not d10['legend_text']) and d10['legend_els'] == 0 and (d10['lk1'] + d10['lk2'] + d10['lk3']) > 0 \
            and (d10['s1'] is None or (d10['s1']['fw'] in ('700', '800') and 'underline' in d10['s1']['td'] and 'double' in d10['s1']['td'])) \
            and (d10['s2'] is None or (d10['s2']['fw'] in ('700', '800') and 'underline' in d10['s2']['td'])) and (d10['s3'] is None or 'underline' in d10['s3']['td'])
        rec('10', '%s_%s_legend_gone_emphasis_kept' % (a, lv), okk, d10)
        if (a, lv) == ('ai_island', 'adv'):
            page.evaluate("document.getElementById('fullstory').scrollIntoView({block:'start'})")
            page.wait_for_timeout(300)
            shot(10)

    # ---------- Regression ----------
    for a, lv in CASES:
        open_article(page, a, lv)
        L = DATAJ[a]['levels'][lv]
        sync = getj(DATA + json.load(urllib.request.urlopen(DATA + 'sync_index.json'))[a][lv])['sentences']
        # 点灯精度: 各パート3文ずつ(開始+0.3sへシーク)
        step = max(1, len(sync) // 24)
        bad = []
        n = 0
        for r in sync[::step]:
            tt = r['start'] + 0.3 if r['end'] - r['start'] > 0.7 else (r['start'] + r['end']) / 2
            act = page.evaluate("""(t) => new Promise(res => { const a=document.getElementById('aud'); const done=()=>requestAnimationFrame(()=>requestAnimationFrame(()=>res((window.__EUP||{}).active))); a.addEventListener('seeked', done, {once:true}); a.currentTime=t; setTimeout(done, 2000); })""", tt)
            n += 1
            if act != r['sid']:
                bad.append((r['sid'], tt, act))
        rec('R', '%s_%s_highlight_precision_%d_sampled' % (a, lv, n), len(bad) <= max(1, n // 20), dict(n=n, bad=bad[:5]))
        # 文クリック再生
        sid = [x['sid'] for p in L['parts'] if p['kind'] == 'story' for pa in p['paragraphs'] for x in pa][4]
        page.click('[data-sid="%s"]' % sid)
        page.wait_for_timeout(1500)
        s = A(page)
        exp = [r for r in sync if r['sid'] == sid][0]
        rec('R', '%s_%s_sentence_click_plays_from_sentence' % (a, lv), (not s['paused']) and exp['start'] - 0.5 <= s['eup']['gt'] <= exp['end'] + 2.0 and s['eup']['active'] in (sid, None) or s['eup']['active'] == sid, dict(sid=sid, gt=s['eup']['gt'], exp=[exp['start'], exp['end']], active=s['eup']['active']))
        # シーク
        page.evaluate("document.getElementById('aud').pause()")
        page.evaluate("() => { const s=document.getElementById('seek'); s.value=500; s.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.wait_for_timeout(500)
        s = A(page)
        rec('R', '%s_%s_seekbar_moves_to_50pct' % (a, lv), abs(s['t'] / L['total_sec'] - 0.5) < 0.03, round(s['t'] / L['total_sec'], 3))
        page.click('#pp')
        page.wait_for_timeout(800)
        playing = not A(page)['paused']
        page.click('#pp')
        page.wait_for_timeout(300)
        rec('R', '%s_%s_play_pause_button' % (a, lv), playing and A(page)['paused'], None)
    open_article(page, 'ai_island', 'std')
    page.click('#tabs button[data-lv=adv]')
    page.wait_for_timeout(700)
    page.click('#tabs button[data-lv=std]')
    page.wait_for_timeout(700)
    rec('R', 'level_switch_roundtrip', 'standard' in page.text_content('#eyebrow').lower() and 'standard.mp3' in A(page)['src'], page.text_content('#eyebrow'))
    ow = page.evaluate('() => [document.documentElement.scrollWidth, innerWidth]')
    rec('R', 'no_horizontal_overflow', ow[0] <= ow[1], ow)
    rec('R', 'console_errors_0', not errs, errs[:5])
    rec('R', 'http_4xx_5xx_0', not bad, bad[:5])
    browser.close()


if __name__ == '__main__':
    with sync_playwright() as p:
        for v, o in VIEWS.items():
            run_view(p, v, o)
    allr = [(v, it, k, c['ok']) for v, R in RES['views'].items() for it, d in R.items() if isinstance(d, dict) for k, c in d.items()]
    RES['summary'] = dict(total=len(allr), ng=[x for x in allr if not x[3]])
    out = os.path.join(OUTD, 'verify_result_rev_%s_01.json' % ('live' if LIVE else 'local'))
    json.dump(RES, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('TOTAL', len(allr), 'NG', len(RES['summary']['ng']))
    for x in RES['summary']['ng']:
        print('NG', x)
