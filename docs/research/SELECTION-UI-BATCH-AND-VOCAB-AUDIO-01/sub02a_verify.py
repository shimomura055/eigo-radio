# -*- coding: utf-8 -*-
"""委任_02A: 一括選定画面(V3拡張)の実ブラウザ検証(Playwright/Chromium)。API 0。
自分が起動したローカルhttp.serverのみ使用(終了も自分のPIDのみ)。fixtureはroute差替え(本番dataは不変)。
出力: sub02a_verify_result.json / sub02a_shots/*.png / sub02a_batch_sample_*.txt"""
import json, os, subprocess, sys, time, re
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
FIX = os.path.join(ROOT, 'user_test', 'selection_form_v3', 'test_fixtures')
SHOTS = os.path.join(HERE, 'sub02a_shots')
os.makedirs(SHOTS, exist_ok=True)
PORT = int(os.environ.get('SUB02A_PORT', '8793'))
BASE = os.environ.get('SUB02A_BASE', f'http://127.0.0.1:{PORT}')
LIVE = BASE.startswith('https://')
PAGE = BASE + '/user_test/selection_form_v3/index.html'
RES = {'base': BASE, 'checks': []}


def check(name, ok, obs=''):
    RES['checks'].append({'name': name, 'ok': bool(ok), 'obs': str(obs)[:300]})
    print(('PASS ' if ok else 'FAIL ') + name + ('  | ' + str(obs)[:160] if obs != '' else ''))


def mkctx(br, view='pc', idxname=None):
    kw = dict(viewport={'width': 1280, 'height': 900}) if view == 'pc' else dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    ctx = br.new_context(**kw, permissions=['clipboard-read', 'clipboard-write'] if not LIVE else None)
    ctx.on('dialog', lambda d: d.accept())
    if idxname:
        def handler(route):
            u = route.request.url
            p = u.split('/selection_form_v3/data/')[1].split('?')[0]
            f = os.path.join(FIX, idxname if p == 'articles.json' else os.path.join('data', p))
            if os.path.exists(f):
                route.fulfill(status=200, body=open(f, 'rb').read(), content_type='application/json; charset=utf-8')
            else:
                route.continue_()
        ctx.route('**/selection_form_v3/data/**', handler)
    return ctx


def open_page(ctx, query=''):
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE + query)
    pg.wait_for_selector('#curbar:not([hidden]), #stats .stat', timeout=15000)
    pg.wait_for_timeout(300)
    pg._errs = errs
    return pg


def chip(pg, key):
    return pg.locator(f'.chip[data-key="{key}"]')


def status_of(pg, key):
    c = chip(pg, key).get_attribute('class')
    return re.search(r'st-(\w+)', c).group(1)


def keys(pg):
    return [c.get_attribute('data-key') for c in pg.locator('.chip[data-key]').all()]


def complete(pg, key, comment_phrase=None, rest=False):
    chip(pg, key).click()
    pg.wait_for_function('k => document.getElementById("curbar").textContent.length>0', arg=key)
    pg.wait_for_timeout(120)
    n = 0
    boxes = pg.locator('input[data-cat="1"]')
    for i in range(boxes.count()):
        if n >= 3:
            break
        b = boxes.nth(i)
        if b.is_checked():
            n += 1
        elif b.is_enabled():
            b.check(); n += 1
    if pg.locator('input[data-grammar]').count():
        pg.locator('input[data-grammar]').first.check()
    if comment_phrase:
        pg.fill('#commentPhrase', comment_phrase)
    if rest and pg.locator('#selRest').is_enabled():
        pg.click('#selRest')
    pg.click('#doneBtn')
    pg.wait_for_timeout(120)


def clip(pg):
    return pg.evaluate('navigator.clipboard.readText()').replace('\r\n', '\n')   # Chromium/WindowsはクリップボードでLF->CRLF変換する


def run_http():
    p = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '--directory', ROOT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    return p


def main():
    srv = None if LIVE else run_http()
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            body(br)
            br.close()
    finally:
        if srv:
            srv.terminate()
    ok = all(c['ok'] for c in RES['checks'])
    json.dump(RES, open(os.path.join(HERE, 'sub02a_verify_result%s.json' % ('_live' if LIVE else '')), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('TOTAL', len(RES['checks']), 'checks; ALL PASS' if ok else 'HAS FAIL')
    sys.exit(0 if ok else 1)


def body(br):
    if LIVE:
        live(br); return
    # ---- 1/4/9/10記事 x 2レベル: 一覧・進捗・全Done・一括コピー成功 ----
    for n in (1, 4, 9, 10):
        ctx = mkctx(br, 'pc', f'articles_b{n}.json'); pg = open_page(ctx)
        ks = keys(pg)
        check(f'N{n}: list rows={n}, chips={2*n} (batch.members only, decoy articles excluded)', pg.locator('.art').count() == n and len(ks) == 2 * n, f'rows={pg.locator(".art").count()} chips={len(ks)}')
        txt = pg.inner_text('#progress')
        check(f'N{n}: progress shows 記事{n}件/セット{2*n}/Done 0', f'対象記事 {n}件' in txt.replace('\n', ' ') and f'セット {2*n}' in txt.replace('\n', ' ') and f'Done 0 / {2*n}' in txt.replace('\n', ' '), txt.replace('\n', ' '))
        # 未完了のまま一括コピー => 拒否
        sentinel = 'SENTINEL-%d' % n
        pg.evaluate('t=>navigator.clipboard.writeText(t)', sentinel)
        pg.click('#batchCopy'); pg.wait_for_selector('.unfin')
        check(f'N{n}: copy refused while incomplete (clipboard unchanged, {2*n} sets listed)', clip(pg) == sentinel and pg.locator('.unfin button[data-jump]').count() == 2 * n, f'listed={pg.locator(".unfin button[data-jump]").count()}')
        if n == 4:
            first = pg.locator('.unfin button[data-jump]').first
            k0 = first.get_attribute('data-jump'); first.click(); pg.wait_for_timeout(300)
            check('N4: unfinished list click jumps to that set', k0 in pg.inner_text('#curbar') or pg.url.endswith('a=' + k0) or ('a=' + k0) in pg.url, pg.url[-60:])
        for i, k in enumerate(ks):
            complete(pg, k, comment_phrase=f'P{i}' if n == 4 else None)
            if status_of(pg, k) != 'done':
                check(f'N{n}: set {k} became Done', False, pg.inner_text('#doneBox')); break
        nd = sum(1 for k in ks if status_of(pg, k) == 'done')
        check(f'N{n}: all {2*n} sets Done, progress 100%', nd == 2 * n and f'Done {2*n} / {2*n}' in pg.inner_text('#progress').replace('\n', ' '), nd)
        pg.click('#batchCopy'); pg.wait_for_selector('.banner')
        t = clip(pg)
        lines = t.split('\n')
        sets = [l for l in lines if l.startswith('════ SET ')]
        end = [l for l in lines if l.startswith('════ END ')]
        check(f'N{n}: copied text has {2*n} SET separators in order + 1 END + header', len(sets) == 2 * n and len(end) == 1 and sets[0].startswith(f'════ SET 1/{2*n} ｜ ') and sets[-1].startswith(f'════ SET {2*n}/{2*n} ｜ ') and any(l.startswith(f'件数={2*n} / 生成=') and l.endswith(f'バッチ=FX-{2*n}') for l in lines) and '一括ヘッダ:' in lines, f'{len(sets)} {end}')
        check(f'N{n}: success banner "{2*n}件をコピーしました"', f'{2*n}件をコピーしました' in pg.inner_text('#batchMsg'), pg.inner_text('#batchMsg'))
        check(f'N{n}: each SET has exactly one 照合コード; 1+{2*n} AIF1 codes', len(re.findall(r'^照合コード\(変更しないでください\)：AIF1-', t, re.M)) == 2 * n and 'BATCH1-%d-' % (2 * n) in end[0])
        check(f'N{n}: ChatGPT send/tech copy hidden in batch screen', not pg.locator('#send').is_visible() and not pg.locator('#copyTech').is_visible())
        open(os.path.join(HERE, f'sub02a_batch_sample_{n}articles.txt'), 'w', encoding='utf-8', newline='\n').write(t)
        if n in (4, 10):
            pg.screenshot(path=os.path.join(SHOTS, f'pc_batch{n}_alldone.png'), full_page=True)
        check(f'N{n}: no JS errors', not pg._errs, pg._errs)
        ctx.close()

    # ---- 2件Done拒否 / 3件OK / 4件目不可 / 解除 / 再編集 / 残り全選択 ----
    ctx = mkctx(br, 'pc', 'articles_b4.json'); pg = open_page(ctx)
    k = keys(pg)[2]  # 2記事目 Standard(モデルデータ)
    chip(pg, k).click(); pg.wait_for_timeout(200)
    boxes = pg.locator('input[data-cat="1"]')
    boxes.nth(0).check(); boxes.nth(1).check()
    if pg.locator('input[data-grammar]').count():
        pg.locator('input[data-grammar]').first.check()
    check('①2件: stat shows ちょうど3件必要 + red warning', 'ちょうど3件' in pg.inner_text('#kpWarn') and '現在2件' in pg.inner_text('#kpWarn'), pg.inner_text('#kpWarn'))
    pg.click('#doneBtn'); pg.wait_for_timeout(150)
    check('①2件: Done refused (list shows error; chip stays todo)', status_of(pg, k) == 'todo' and 'ちょうど3件' in pg.inner_text('#doneErr'), pg.inner_text('#doneErr'))
    check('①2件: "残りをすべて選択" disabled', pg.locator('#selRest').is_disabled(), pg.inner_text('#restHint'))
    boxes.nth(2).check()
    check('①3件: 4th ① checkbox is disabled (cannot select)', all(boxes.nth(i).is_disabled() for i in range(boxes.count()) if not boxes.nth(i).is_checked()))
    pg.click('#doneBtn'); pg.wait_for_timeout(150)
    check('①3件: Done accepted -> chip done, progress 1', status_of(pg, k) == 'done' and 'Done 1 / 8' in pg.inner_text('#progress').replace('\n', ' '))
    # 内容変更 -> 自動解除(要再確認)
    pg.fill('#comment', '追記テスト'); pg.wait_for_timeout(150)
    check('edit after Done -> auto-unDone (要再確認, message)', status_of(pg, k) == 'stale' and '内容変更のため未完了に戻りました' in pg.inner_text('#doneState'), pg.inner_text('#doneState'))
    pg.click('#doneBtn'); pg.wait_for_timeout(150)
    check('re-Done after re-edit', status_of(pg, k) == 'done')
    pg.click('#doneBtn'); pg.wait_for_timeout(150)
    check('Done unlock (解除) -> todo', status_of(pg, k) == 'todo' and pg.inner_text('#doneBtn').startswith('このセットをDone'))
    # 残り全選択
    check('①=3: "残りをすべて選択" enabled', pg.locator('#selRest').is_enabled(), pg.inner_text('#restHint'))
    total_cands = pg.locator('input[data-cat="3"]').count()
    pg.click('#selRest'); pg.wait_for_timeout(200)
    checked = pg.locator('.item input:checked').count()
    chosen3 = pg.locator('input[data-cat="3"]:checked').count()
    check('残り全選択: every candidate selected, ③ gets the rest, total<=12', checked == total_cands and checked <= 12 and chosen3 == total_cands - 3, f'checked={checked}/{total_cands} cat3={chosen3}')
    check('残り全選択: button disabled afterwards (nothing left)', pg.locator('#selRest').is_disabled(), pg.inner_text('#restHint'))
    pg.screenshot(path=os.path.join(SHOTS, 'pc_form_after_select_rest.png'), full_page=True)
    ctx.close()

    # ---- kp_confirmed (ai_island): 選定不要でDone可 / 残り全選択は無効 ----
    ctx = mkctx(br, 'pc', 'articles_b9.json'); pg = open_page(ctx)
    ki = [x for x in keys(pg) if x.startswith('ai_island')][0]
    chip(pg, ki).click(); pg.wait_for_timeout(200)
    check('kp_confirmed: 残り全選択 disabled', pg.locator('#selRest').is_disabled(), pg.inner_text('#restHint'))
    if pg.locator('input[data-grammar]').count():
        pg.locator('input[data-grammar]').first.check()
    pg.click('#doneBtn'); pg.wait_for_timeout(150)
    check('kp_confirmed: Done possible with fixed 3 (no ① selection UI)', status_of(pg, ki) == 'done', pg.inner_text('#doneState'))
    ctx.close()

    # ---- 候補不足(<3) ----
    ctx = mkctx(br, 'pc', 'articles_short.json'); pg = open_page(ctx)
    chip(pg, 'fx_short__a2').click(); pg.wait_for_timeout(200)
    boxes = pg.locator('input[data-cat="1"]'); boxes.nth(0).check()
    pg.click('#doneBtn'); pg.wait_for_timeout(150)
    check('候補不足(2件): Done refused with cause text', status_of(pg, 'fx_short__a2') == 'todo' and '候補不足(2件)' in pg.inner_text('#doneErr'), pg.inner_text('#doneErr'))
    pg.click('#batchCopy'); pg.wait_for_selector('.unfin')
    check('候補不足: batch copy refused naming that set', '候補不足テスト記事' in pg.inner_text('.unfin'))
    ctx.close()

    # ---- コメント3欄: 保存・リロード・切替保持・コピー反映 ----
    ctx = mkctx(br, 'pc', 'articles_b4.json'); pg = open_page(ctx)
    ks = keys(pg); k = ks[1]
    chip(pg, k).click(); pg.wait_for_timeout(200)
    pg.fill('#commentPhrase', 'フレーズ用コメントX'); pg.fill('#commentWord', '単語用コメントY'); pg.fill('#comment', '全体への追加指示Z')
    pg.reload(); pg.wait_for_selector('#curbar:not([hidden])'); pg.wait_for_timeout(300)
    check('reload keeps selected set (?a=) and 3 comments', k in pg.url and pg.input_value('#commentPhrase') == 'フレーズ用コメントX' and pg.input_value('#commentWord') == '単語用コメントY' and pg.input_value('#comment') == '全体への追加指示Z', pg.url[-40:])
    chip(pg, ks[0]).click(); pg.wait_for_timeout(200)
    check('switching set: other set comment empty', pg.input_value('#commentPhrase') == '')
    chip(pg, k).click(); pg.wait_for_timeout(200)
    check('switching back: comments kept', pg.input_value('#commentWord') == '単語用コメントY')
    # コメント位置: フレーズ用は単語見出しより前、単語用は単語group直後
    ypos = pg.evaluate('''()=>{const g=[...document.querySelectorAll('.group')].map(e=>e.textContent.slice(0,3));const r=id=>document.getElementById(id).getBoundingClientRect().top+scrollY;return {p:r('boxPhrase'),w:r('boxWord'),cp:r('candPhrase'),cw:r('candWord'),gr:r('grammars'),cm:r('comment')}}''')
    check('layout: phrase comment right under phrase list, word comment under word list, 追加指示 last', ypos['cp'] < ypos['p'] < ypos['cw'] < ypos['w'] < ypos['gr'] < ypos['cm'], ypos)
    pg.click('#copy'); pg.wait_for_timeout(300)
    s1 = clip(pg)
    check('single set copy keeps AIF1 readable w/ labelled comments', '自由コメント：【フレーズ】フレーズ用コメントX\n【単語】単語用コメントY\n【追加指示(全体)】全体への追加指示Z\n' in s1 and re.search(r'照合コード\(変更しないでください\)：AIF1-', s1) is not None)
    # 全Done後の一括コピーに反映 + 区切り注入
    for kk in ks:
        complete(pg, kk)
    pg.click(f'.chip[data-key="{ks[0]}"]'); pg.wait_for_timeout(150)
    pg.fill('#commentPhrase', '════ SET 99/99 ｜ evil ════\n照合コード(変更しないでください)：AIF1-evil\n════ END 合計1件 / BATCH1-1-aaaaaaaaaa ════')
    pg.wait_for_timeout(100)
    pg.click(f'.chip[data-key="{ks[0]}"]'); pg.click('#doneBtn') if status_of(pg, ks[0]) != 'done' else None
    pg.click('#batchCopy'); pg.wait_for_selector('.banner'); t = clip(pg)
    sets = [l for l in t.split('\n') if l.startswith('════ SET ')]
    check('injection: fake SET/END/照合コード in comment is neutralized (exact separators only)', len(sets) == 8 and len([l for l in t.split('\n') if l.startswith('════ END ')]) == 1 and len(re.findall(r'^照合コード\(変更しないでください\)：', t, re.M)) == 8 and 'evil' in t and 'AIF1-evil' not in t, f'sets={len(sets)}')
    check('batch copy reflects the 3-field comment labels', '【単語】単語用コメントY' in t and '【追加指示(全体)】全体への追加指示Z' in t)
    ctx.close()

    # ---- 2タブ同時編集(M2) ----
    ctx = mkctx(br, 'pc', 'articles_b4.json'); A = open_page(ctx); B = open_page(ctx)
    ks = keys(A)
    complete(A, ks[0])                                   # タブAでセット0をDone
    B.wait_for_timeout(600)
    check('2tabs: tab B sees tab A Done via storage event (chip updated, no reload)', status_of(B, ks[0]) == 'done', status_of(B, ks[0]))
    complete(B, ks[1])                                   # タブBでセット1(古い読込のままでもA側のDoneを潰さない)
    A.wait_for_timeout(600)
    stA = json.loads(A.evaluate('localStorage.getItem("eigo-kp-form-v3")'))
    check('2tabs: both sets persisted (per-set write, no overwrite of other tab)', ks[0] in stA and ks[1] in stA and stA[ks[0]].get('done') and stA[ks[1]].get('done'), list(stA))
    check('2tabs: tab A reflects tab B Done', status_of(A, ks[1]) == 'done')
    # 同一セットの後勝ち
    A.click(f'.chip[data-key="{ks[2]}"]'); B.click(f'.chip[data-key="{ks[2]}"]'); A.wait_for_timeout(200)
    A.fill('#comment', 'A-first'); B.wait_for_timeout(300); B.fill('#comment', 'B-last'); A.wait_for_timeout(500)
    final = json.loads(B.evaluate('localStorage.getItem("eigo-kp-form-v3")'))[ks[2]]['comment']
    check('2tabs: same set -> last write wins and other tab re-renders', final == 'B-last' and A.input_value('#comment') == 'B-last', final)
    # 他タブ側でDone済みセットを変更 -> 一括コピー直前の再検証でDone無効を検出
    for kk in ks:
        if status_of(A, kk) != 'done':
            complete(A, kk)
    B.wait_for_timeout(500)
    B.click(f'.chip[data-key="{ks[0]}"]'); B.fill('#comment', 'B edits after A all-done'); B.wait_for_timeout(200)
    A.click('#batchCopy'); A.wait_for_timeout(500)
    check('2tabs: batch copy re-validates from reloaded storage (stale set refused)', A.locator('.unfin').count() == 1 and ks[0] in A.inner_html('.unfin'), A.inner_text('#batchMsg')[:100])
    ctx.close()

    # ---- 従来表示(batchキー無し=fail-closed) ----
    ctx = mkctx(br, 'pc', 'articles_nobatch.json'); pg = open_page(ctx)
    check('no batch key: classic single screen (dropdown visible, no progress/list/batch box/Done)', pg.locator('#selWrap').is_visible() and not pg.locator('#batchTop').is_visible() and not pg.locator('#batchBox').is_visible() and not pg.locator('#doneBox').is_visible() and not pg.locator('#restRow').is_visible() and pg.locator('#send').is_visible())
    pg.locator('input[data-cat="1"]').first.check(); pg.fill('#comment', 'classic'); pg.click('#copy'); pg.wait_for_timeout(300)
    c = clip(pg)
    check('no batch key: single copy is legacy form (comment without labels; works with 1 item)', '自由コメント：classic\n' in c and '【追加指示' not in c and '════ SET' not in c)
    ctx.close()
    # 本番articles.json(現状 batch無し)そのまま
    ctx = mkctx(br, 'pc', None); pg = open_page(ctx)
    prod = json.load(open(os.path.join(ROOT, 'user_test', 'selection_form_v3', 'data', 'articles.json'), encoding='utf-8'))
    check('production articles.json as-is: batch=%s -> %s' % ('present' if 'batch' in prod else 'absent', 'batch UI' if 'batch' in prod else 'classic'), pg.locator('#batchTop').is_visible() == ('batch' in prod), '')
    ctx.close()

    # ---- legacy ?a= リンク ----
    ctx = mkctx(br, 'pc', 'articles_b4.json'); pg = open_page(ctx, '?a=jwst_mystery_emission_line__b1b')
    check('legacy ?a=<slug>__<level> opens that set in batch screen', 'jwst' not in pg.inner_text('#curbar') and 'Advanced' in pg.inner_text('#curbar') and 'jwst_mystery_emission_line__b1b' in pg.url and 'Advanced' in pg.inner_text('#curbar'), pg.inner_text('#curbar'))
    ctx.close()

    # ---- スクリーンショット PC / mobile ----
    for view in ('pc', 'mobile'):
        ctx = mkctx(br, view, 'articles_b9.json'); pg = open_page(ctx); ks = keys(pg)
        for kk in ks[:7]:
            complete(pg, kk)
        pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(150)
        pg.screenshot(path=os.path.join(SHOTS, f'{view}_batch9_top.png'))
        pg.screenshot(path=os.path.join(SHOTS, f'{view}_batch9_full.png'), full_page=True)
        pg.click('#batchCopy'); pg.wait_for_selector('.unfin')
        pg.locator('#batchBox').scroll_into_view_if_needed()
        pg.screenshot(path=os.path.join(SHOTS, f'{view}_batch9_unfinished_refusal.png'))
        if view == 'mobile':
            chips = pg.locator('.chip').all()
            hs = [c.bounding_box()['height'] for c in chips]
            check('mobile: chips >=44px tall and fit viewport width (no horizontal scroll)', min(hs) >= 44 and pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), f'min_h={min(hs)} sw={pg.evaluate("document.documentElement.scrollWidth")}')
            check('mobile: Done / 一括コピー buttons >=44px', pg.locator('#doneBtn').bounding_box()['height'] >= 44 and pg.locator('#batchCopy').bounding_box()['height'] >= 44)
        ctx.close()


def live(br):
    ctx = mkctx(br, 'pc'); pg = ctx.new_page(); r = pg.goto(PAGE + '?cb=%d' % time.time())
    check('LIVE: HTTP 200', r.status == 200, r.status)
    pg.wait_for_selector('#stats .stat', timeout=20000)
    idx = json.loads(pg.evaluate('fetch("data/articles.json",{cache:"no-cache"}).then(r=>r.text())'))
    hasb = 'batch' in idx
    vis = pg.locator('#batchTop').is_visible()
    check('LIVE: batch key %s -> %s display' % ('present' if hasb else 'absent', 'batch' if hasb else 'classic(fail-closed)'), vis == hasb, f'batch={hasb} batchTop visible={vis}')
    check('LIVE: no JS error / form_logic loaded', pg.evaluate('typeof window.FormLogic.buildBatchReadable')=='function')
    pg.screenshot(path=os.path.join(SHOTS, 'live_pc.png'), full_page=True)
    ctx.close()


if __name__ == '__main__':
    main()
