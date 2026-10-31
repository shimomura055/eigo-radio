# -*- coding: utf-8 -*-
"""委任_03: 公開フォームの『実装済みだが未公開』を実証。公開JS/HTML/dataはそのまま、articles.jsonだけをroute差替えで batch 付きにして実操作(公開物は変更しない・API 0)。
14セット(7記事x2レベル)で 一覧/進捗/Done/コメント/切替保持/一括コピー を PC+mobile で確認。出力 gap03_result_batch.json / gap03_shots/*"""
import json, os, re, sys
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright_noplay as sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
HERE = os.path.dirname(os.path.abspath(__file__)); SH = os.path.join(HERE, 'gap03_shots')
BASE = 'https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/'
PAGE = BASE + 'index.html'
R = {'checks': []}


def check(n, ok, obs=''):
    R['checks'].append({'name': n, 'ok': bool(ok), 'obs': str(obs)[:300]})
    print(('PASS ' if ok else 'FAIL ') + n, '|', str(obs)[:140].encode('ascii', 'replace').decode())


def run(view):
    kw = dict(viewport={'width': 1280, 'height': 900}) if view == 'pc' else dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(**kw, permissions=['clipboard-read', 'clipboard-write'])
        ctx.on('dialog', lambda d: d.accept())
        holder = {}

        def h(route):
            r = route.fetch()
            doc = json.loads(r.text())
            stems = [a['data'].split('/')[-1][:-5] for a in doc['articles'] if a.get('data') and a['data'].endswith('__prod.json')]
            slugs = []
            for s in stems:
                sl = s.rsplit('__', 2)[0]
                if sl not in slugs:
                    slugs.append(sl)
            want = [s for s in stems if s.rsplit('__', 2)[0] in slugs[:7]]
            doc['batch'] = {'id': 'GAP03-INJECT', 'date': '2026-10-30', 'members': want}
            holder['members'] = want
            route.fulfill(status=200, body=json.dumps(doc, ensure_ascii=False), content_type='application/json; charset=utf-8')
        ctx.route('**/selection_form_v3/data/articles.json*', h)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(PAGE)
        pg.wait_for_selector('#curbar:not([hidden])', timeout=20000)
        pg.wait_for_timeout(1500)
        n = len(holder['members'])
        v = lambda s: pg.is_visible(s)
        check(f'{view}: batch UI visible when batch key present (progress/list/curbar)', v('#progress') and v('#list') and v('#curbar'))
        check(f'{view}: only batch sets listed (chips == {n})', pg.locator('.chip[data-key]').count() == n, pg.locator('.chip[data-key]').count())
        check(f'{view}: phrase/word comment boxes visible under candidates', v('#commentPhrase') and v('#commentWord'))
        order = pg.evaluate("""()=>{const ids=['candPhrase','boxPhrase','candWord','boxWord','comment','doneBox','batchCopy'];return ids.map(i=>[i,Math.round(document.getElementById(i).getBoundingClientRect().top+scrollY)])}""")
        R[f'{view}_layout_order'] = order
        ys = [y for _, y in order]
        check(f'{view}: layout order cand->phraseComment->cand->wordComment->overall->done->batchCopy', ys == sorted(ys), order)
        pg.screenshot(path=os.path.join(SH, f'inject_{view}_top.png'))
        pg.screenshot(path=os.path.join(SH, f'inject_{view}_full.png'), full_page=True)
        keys = [c.get_attribute('data-key') for c in pg.locator('.chip[data-key]').all()]
        pg.click('#batchCopy')
        pg.wait_for_timeout(500)
        msg = pg.inner_text('#batchMsg')
        check(f'{view}: batchCopy refused when none Done (lists unfinished)', '未完了' in msg or 'Done' in msg, msg[:120])
        fails = []
        for i, k in enumerate(keys):
            pg.locator(f'.chip[data-key="{k}"]').click()
            pg.wait_for_function('k=>document.getElementById("curbar").textContent.length>0', arg=k)
            pg.wait_for_timeout(150)
            c = 0
            boxes = pg.locator('input[data-cat="1"]')
            for j in range(boxes.count()):
                if c >= 3:
                    break
                b = boxes.nth(j)
                if b.is_checked():
                    c += 1
                elif b.is_enabled():
                    b.check()
                    c += 1
            if pg.locator('input[data-grammar]').count():
                pg.locator('input[data-grammar]').first.check()
            pg.fill('#commentPhrase', f'P-{i}-{k}')
            pg.fill('#commentWord', f'W-{i}-{k}')
            pg.click('#doneBtn')
            pg.wait_for_timeout(120)
            cls = pg.locator(f'.chip[data-key="{k}"]').get_attribute('class')
            if 'st-done' not in cls:
                fails.append((k, cls, pg.inner_text('#doneErr')[:120]))
        check(f'{view}: all {n} sets can be completed(Done) with 3 KP + comments', not fails, fails[:3])
        k0 = keys[0]
        pg.locator(f'.chip[data-key="{k0}"]').click()
        pg.wait_for_timeout(300)
        check(f'{view}: phrase/word comment kept after switching sets', pg.input_value('#commentPhrase') == f'P-0-{k0}' and pg.input_value('#commentWord') == f'W-0-{k0}')
        prog = pg.inner_text('#progress')
        check(f'{view}: progress shows Done n/N', re.search(r'Done\s*%d\s*/\s*%d' % (n, n), prog) is not None, prog[:100])
        pg.click('#batchCopy')
        pg.wait_for_timeout(800)
        txt = pg.evaluate('navigator.clipboard.readText()').replace('\r\n', '\n')
        R[f'{view}_copy_len'] = len(txt)
        sets = len(re.findall(r'^════ SET \d+/%d ｜' % n, txt, re.M))
        check(f'{view}: ONE batch copy contains all {n} sets', sets == n, sets)
        check(f'{view}: copy has per-set phrase+word comments, no duplicates', all((f'【フレーズ】P-{i}-{k}' in txt and f'【単語】W-{i}-{k}' in txt and txt.count(f'P-{i}-{k}') == 1) for i, k in enumerate(keys)))
        check(f'{view}: END line with BATCH1 code', re.search(r'════ END 合計%d件 / BATCH1-%d-[0-9a-f]{10} ════' % (n, n), txt) is not None)
        open(os.path.join(HERE, f'gap03_batch_copy_{view}.txt'), 'w', encoding='utf-8').write(txt)
        pg.locator(f'.chip[data-key="{k0}"]').click()
        pg.wait_for_timeout(300)
        pg.fill('#commentWord', 'CHANGED')
        pg.wait_for_timeout(200)
        cls = pg.locator(f'.chip[data-key="{k0}"]').get_attribute('class')
        check(f'{view}: edit after Done auto-releases Done', 'st-done' not in cls, cls)
        pg.click('#batchCopy')
        pg.wait_for_timeout(500)
        m2 = pg.inner_text('#batchMsg')
        check(f'{view}: batchCopy refused again after edit', ('未完了' in m2) or ('Done' in m2), m2[:100])
        R[f'{view}_localStorage_keys'] = pg.evaluate('Object.keys(localStorage)')
        check(f'{view}: no pageerrors', not errs, errs[:2])
        br.close()


for v in ('pc', 'mobile'):
    run(v)
json.dump(R, open(os.path.join(HERE, 'gap03_result_batch.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('TOTAL', len(R['checks']), 'FAILS', [c['name'] for c in R['checks'] if not c['ok']])
