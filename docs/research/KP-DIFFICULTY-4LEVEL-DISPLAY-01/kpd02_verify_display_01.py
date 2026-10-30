# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_02: V3フォーム(単体・一括)の難易度バッジ表示の実ブラウザ検証。API 0。
自分が起動したローカルhttp.serverのみ。fixtureはroute差替え(本番data不変)。difficulty付与fixtureは一時dirに生成。
出力: kpd02_verify_display_result.json / kpd02_shots/*.png"""
import json, os, re, shutil, subprocess, sys, tempfile, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, 'user_test', 'selection_form_v3', 'test_fixtures')
SHOTS = os.path.join(HERE, 'kpd02_shots'); os.makedirs(SHOTS, exist_ok=True)
PORT = int(os.environ.get('KPD02_PORT', '8795'))
BASE = os.environ.get('KPD02_BASE', f'http://127.0.0.1:{PORT}')
PAGE = BASE + '/user_test/selection_form_v3/index.html'
RES = {'base': BASE, 'checks': []}
LV = ['easy', 'medium', 'hard', 'rare', 'unknown']
LAB = {'easy': '易', 'medium': '中', 'hard': '難', 'rare': '激難(レア)', 'unknown': '未判定'}


def check(name, ok, obs=''):
    RES['checks'].append({'name': name, 'ok': bool(ok), 'obs': str(obs)[:300]})
    print(('PASS ' if ok else 'FAIL ') + name + ('  | ' + str(obs)[:160] if obs != '' else ''))


def build_fix(mode):
    """mode: diff=全候補にdifficulty付与(易/中/難/激難/未判定を循環) / legacy=付与なし / notgraded=source=not_graded"""
    out = tempfile.mkdtemp(prefix='kpd02fix_')
    shutil.copytree(SRC, out, dirs_exist_ok=True)
    dd = os.path.join(out, 'data')
    n = 0
    for f in os.listdir(dd):
        p = os.path.join(dd, f)
        d = json.load(open(p, encoding='utf-8'))
        for it in (d.get('phrases') or []) + (d.get('words') or []):
            if mode == 'diff':
                lv = LV[n % 5]; n += 1
                it['difficulty'] = {'level': lv, 'label_ja': LAB[lv], 'reason_ja': '検証', 'source': 'fail_open' if lv == 'unknown' else 'llm'}
            elif mode == 'notgraded':
                it['difficulty'] = {'level': 'unknown', 'label_ja': '未判定', 'reason_ja': '', 'source': 'not_graded'}
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return out


def mkctx(br, fix, view, idxname):
    kw = dict(viewport={'width': 1280, 'height': 900}) if view == 'pc' else dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    ctx = br.new_context(**kw, permissions=['clipboard-read', 'clipboard-write'])
    ctx.on('dialog', lambda d: d.accept())

    def handler(route):
        p = route.request.url.split('/selection_form_v3/data/')[1].split('?')[0]
        f = os.path.join(fix, idxname if p == 'articles.json' else os.path.join('data', p))
        if os.path.exists(f):
            route.fulfill(status=200, body=open(f, 'rb').read(), content_type='application/json; charset=utf-8')
        else:
            route.continue_()
    ctx.route('**/selection_form_v3/data/**', handler)
    return ctx


def open_page(ctx, query=''):
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE + query)
    pg.wait_for_selector('#curbar:not([hidden]), #stats .stat', timeout=15000)
    pg.wait_for_timeout(300); pg._errs = errs
    return pg


def badges(pg):
    return pg.evaluate('()=>Array.from(document.querySelectorAll(".item .diff")).map(e=>({lv:e.dataset.diff,t:e.textContent}))')


def n_items(pg):
    return pg.locator('.item').count()


def overflow(pg):
    return pg.evaluate('()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1')


def clip(pg):
    return pg.evaluate('navigator.clipboard.readText()').replace('\r\n', '\n')


def body(br):
    fixd = build_fix('diff'); fixl = build_fix('legacy'); fixn = build_fix('notgraded')
    try:
        for view in ('pc', 'mobile'):
            ctx = mkctx(br, fixd, view, 'articles_b4.json'); pg = open_page(ctx)
            ks = [c.get_attribute('data-key') for c in pg.locator('.chip[data-key]').all()]
            pg.locator('.chip[data-key]').first.click(); pg.wait_for_timeout(300)
            b = badges(pg); ni = n_items(pg)
            check(f'{view} batch: every candidate row has exactly one badge (items={ni}, badges={len(b)})', ni > 0 and len(b) == ni, f'{ni}/{len(b)}')
            check(f'{view} batch: badge text = "｜"+label and all 5 kinds appear', all(x['t'] == '｜' + LAB[x['lv']] for x in b) and {x['lv'] for x in b} >= set(LV[:min(5, len(b))]), [x['t'] for x in b][:7])
            check(f'{view} batch: no horizontal overflow with badges', not overflow(pg))
            pg.screenshot(path=os.path.join(SHOTS, f'kpd02_batch_{view}.png'), full_page=True)
            boxes = pg.locator('input[data-cat="1"]'); n = 0
            for i in range(boxes.count()):
                if n >= 3:
                    break
                bx = boxes.nth(i)
                if bx.is_enabled():
                    bx.check(); n += 1
            if pg.locator('input[data-grammar]').count():
                pg.locator('input[data-grammar]').first.check()
            pg.click('#doneBtn'); pg.wait_for_timeout(200)
            cls = pg.locator(f'.chip[data-key="{ks[0]}"]').get_attribute('class') or ''
            check(f'{view} batch: select 3 + Done works with badges present', 'st-done' in cls, cls)
            pg.locator('.chip[data-key]').nth(1).click(); pg.wait_for_timeout(300)
            check(f'{view} batch: switching set keeps badges', len(badges(pg)) == n_items(pg) > 0)
            check(f'{view} batch: no JS errors', not pg._errs, pg._errs)
            ctx.close()
        for view in ('pc', 'mobile'):
            ctx = mkctx(br, fixd, view, 'articles_nobatch.json'); pg = open_page(ctx)
            b = badges(pg); ni = n_items(pg)
            check(f'{view} single: badges on every candidate (items={ni}, badges={len(b)})', ni > 0 and len(b) == ni, f'{ni}/{len(b)}')
            check(f'{view} single: no overflow', not overflow(pg))
            pg.screenshot(path=os.path.join(SHOTS, f'kpd02_single_{view}.png'), full_page=True)
            pg.locator('input[data-cat="1"]').first.check(); pg.fill('#comment', 'c'); pg.click('#copy'); pg.wait_for_timeout(300)
            c = clip(pg)
            check(f'{view} single: copy text has AIF1 code and no difficulty text', 'AIF1-' in c and not re.search(r'易|激難|未判定|difficulty', c), c[:80].replace('\n', ' '))
            ctx.close()
        for nm, fx in (('legacy(no field)', fixl), ('not_graded', fixn)):
            for idx in ('articles_b4.json', 'articles_nobatch.json'):
                ctx = mkctx(br, fx, 'pc', idx); pg = open_page(ctx)
                if idx == 'articles_b4.json':
                    pg.locator('.chip[data-key]').first.click(); pg.wait_for_timeout(300)
                check(f'{nm} {idx}: no badge, rows render ({n_items(pg)} items)', len(badges(pg)) == 0 and n_items(pg) > 0, f'items={n_items(pg)}')
                check(f'{nm} {idx}: no JS errors', not pg._errs, pg._errs)
                ctx.close()
        ctx = br.new_context(viewport={'width': 1280, 'height': 900}); pg = ctx.new_page(); pg.goto(PAGE)
        pg.wait_for_selector('#stats .stat, #curbar:not([hidden])', timeout=15000); pg.wait_for_timeout(500)
        check('repo production data (unchanged): zero badges, rows render', len(badges(pg)) == 0 and n_items(pg) > 0, f'items={n_items(pg)}')
        ctx.close()
    finally:
        for d in (fixd, fixl, fixn):
            shutil.rmtree(d, ignore_errors=True)


def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '--directory', ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(); body(br); br.close()
    finally:
        srv.terminate()
    ok = all(c['ok'] for c in RES['checks'])
    json.dump(RES, open(os.path.join(HERE, 'kpd02_verify_display_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('TOTAL', len(RES['checks']), 'checks; ALL PASS' if ok else 'HAS FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
