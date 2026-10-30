# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_05: 公開(Pages)フォームの実表示確認。API 0。usage: python kpd05_live_verify_01.py <label> <base_url_form_dir> <mode: single|batch|absent>
single: 6エントリ(?a=<slug>__<level>)をPC/mobileで開き、バッジ数=候補数・label一致・スクショ。batch: ?付き無しで一括画面を開き各set chipを切替えて確認。absent: エントリが404/非表示であること(除去確認)。"""
import json, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, 'kpd05_shots'); os.makedirs(SHOTS, exist_ok=True)
label, base, mode = sys.argv[1], sys.argv[2].rstrip('/'), sys.argv[3]
SETS = json.load(open(os.path.join(HERE, 'kpd05_out', 'kpd05_form_entries.json'), encoding='utf-8'))   # [{slug,level,key,n_cand,labels:[...]}]
RES = {'label': label, 'base': base, 'mode': mode, 'checks': []}


def check(name, ok, obs=''):
    RES['checks'].append({'name': name, 'ok': bool(ok), 'obs': str(obs)[:400]}); print(('PASS ' if ok else 'FAIL ') + name + ('  | ' + str(obs)[:200] if obs != '' else ''), flush=True)


def badges(pg):
    return pg.evaluate('()=>Array.from(document.querySelectorAll(".item .diff")).map(e=>({lv:e.dataset.diff,t:e.textContent}))')


def ctxs(br):
    return [('pc', br.new_context(viewport={'width': 1280, 'height': 900})),
            ('mobile', br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True))]


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for view, ctx in ctxs(br):
            if mode in ('single', 'absent'):
                for s in SETS:
                    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
                    pg.goto(f"{base}/index.html?a={s['key']}&_={label}"); pg.wait_for_timeout(2500)
                    if mode == 'absent':
                        n = pg.locator('.item').count(); title = pg.title()
                        txt = pg.evaluate('()=>document.body.innerText')
                        check(f'{label} {view} {s["key"]}: entry removed (no 【表示確認用】 text)', '表示確認用' not in txt, f'items={n}')
                    else:
                        b = badges(pg); ni = pg.locator('.item').count()
                        txt = pg.evaluate('()=>document.body.innerText')
                        check(f'{label} {view} {s["key"]}: items={ni} badges={len(b)} (doc候補={s["n_cand"]})', ni == s['n_cand'] == len(b), f'{ni}/{len(b)}')
                        check(f'{label} {view} {s["key"]}: 【表示確認用】 shown', '表示確認用' in txt)
                        check(f'{label} {view} {s["key"]}: label sequence matches exported doc', sorted(x['t'].lstrip('｜') for x in b) == sorted(s['labels']), [x['t'] for x in b][:12])
                        check(f'{label} {view} {s["key"]}: no horizontal overflow', not pg.evaluate('()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1'))
                        check(f'{label} {view} {s["key"]}: no JS errors', not errs, errs)
                    pg.screenshot(path=os.path.join(SHOTS, f'kpd05_{label}_{view}_{s["key"]}.png'), full_page=True)
                    pg.close()
            else:
                pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.goto(f"{base}/index.html?_={label}"); pg.wait_for_selector('.chip[data-key]', timeout=20000); pg.wait_for_timeout(500)
                keys = [c.get_attribute('data-key') for c in pg.locator('.chip[data-key]').all()]
                check(f'{label} {view} batch: 6 set chips', len(keys) == 6, keys)
                for i, s in enumerate(SETS):
                    pg.locator('.chip[data-key]').nth(i).click(); pg.wait_for_timeout(500)
                    b = badges(pg); ni = pg.locator('.item').count()
                    check(f'{label} {view} batch set{i} {s["key"]}: items={ni} badges={len(b)}', ni == s['n_cand'] == len(b), f'{ni}/{len(b)}')
                    check(f'{label} {view} batch set{i}: labels match doc', sorted(x['t'].lstrip('｜') for x in b) == sorted(s['labels']))
                    pg.screenshot(path=os.path.join(SHOTS, f'kpd05_{label}_{view}_set{i}_{s["key"]}.png'), full_page=True)
                check(f'{label} {view} batch: no JS errors', not errs, errs)
                pg.close()
            ctx.close()
        br.close()
    json.dump(RES, open(os.path.join(HERE, 'kpd05_out', f'kpd05_live_{label}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ok = all(c['ok'] for c in RES['checks']); print('TOTAL', len(RES['checks']), 'ALL PASS' if ok else 'HAS FAIL'); sys.exit(0 if ok else 1)


main()
