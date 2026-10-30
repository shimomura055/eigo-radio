# -*- coding: utf-8 -*-
"""委任_04: 選定UI 実操作E2E(Playwright、PC 1280x900 / mobile 390x844 touch)。シナリオA(18セット)/B(5セット)/C(未完了・変更・切替・M1/M2/M5/M12)。
--base: ローカルserver(http://127.0.0.1:PORT/) または公開URL(https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/)。
test batch(sub04-a-18sets-test / sub04-b-5sets-test / sub04-c-overlap-test)を使う。クリップボード内容は er128 confirm-batch --dry-run で受入検査(本確定しない)。API 0。
出力: --out(JSON)、--shots(スクショdir)。"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
FORM_DATA = os.path.join(REPO, 'user_test', 'selection_form_v3', 'data')
R = {'checks': [], 'meta': {}}


def check(n, ok, obs=''):
    R['checks'].append({'name': n, 'ok': bool(ok), 'obs': str(obs)[:300]})
    print(('PASS ' if ok else 'FAIL ') + n, '|', str(obs)[:150].encode('ascii', 'replace').decode(), flush=True)


class Ctx:
    def __init__(self, br, view, base, shots):
        self.view, self.base, self.shots = view, base, shots
        kw = dict(viewport={'width': 1280, 'height': 900}) if view == 'pc' else dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        self.ctx = br.new_context(**kw, permissions=['clipboard-read', 'clipboard-write'])
        self.ctx.on('dialog', lambda d: d.accept())
        self.pg = self.ctx.new_page()
        self.errs = []
        self.pg.on('pageerror', lambda e: self.errs.append(str(e)[:200]))

    def tag(self, s):
        return '%s: %s' % (self.view, s)

    def act(self, loc):
        if self.view == 'mobile':
            loc.evaluate("el=>el.scrollIntoView({block:'center'})")
            loc.tap()
        else:
            loc.click()

    def shot(self, name, full=False):
        os.makedirs(self.shots, exist_ok=True)
        self.pg.screenshot(path=os.path.join(self.shots, '%s_%s.png' % (name, self.view)), full_page=full)

    def open(self, qs, wait=True):
        self.pg.goto(self.base + 'index.html' + qs, wait_until='load')
        if wait:
            self.pg.wait_for_selector('#curbar:not([hidden])', timeout=60000)
            self.pg.wait_for_timeout(1200)

    def chips(self):
        return self.pg.locator('.chip[data-key]').count()

    def done_text(self):
        return self.pg.inner_text('#fDone')

    def done_n(self):
        m = re.search(r'Done (\d+)/(\d+)', self.done_text())
        return (int(m.group(1)), int(m.group(2))) if m else (None, None)

    def keys(self):
        return self.pg.eval_on_selector_all('.chip[data-key]', 'els=>els.map(e=>e.dataset.key)')

    def jump(self, key):
        self.act(self.pg.locator('.chip[data-key="%s"]' % key))
        self.pg.wait_for_timeout(500)

    def cur_key(self):
        return self.pg.evaluate("()=>new URL(location.href).searchParams.get('a')")

    def complete_set(self, key, ptxt, wtxt, gtxt=None):
        """key のセットを開き、①を3件選び、文法0件を選び、コメント2種(+全体)を入力してDone。"""
        self.jump(key)
        pg = self.pg
        have = pg.locator('input[data-term][data-cat="1"]:checked').count()
        for _ in range(max(0, 3 - have)):
            self.act(pg.locator('input[data-term][data-cat="1"]:not(:checked):not([disabled])').first)
            pg.wait_for_timeout(120)
        gn = pg.locator('input[data-grammar-none]')
        if gn.count() and not gn.first.is_checked():
            self.act(gn.first)
        if ptxt is not None:
            pg.fill('#commentPhrase', ptxt)
        if wtxt is not None:
            pg.fill('#commentWord', wtxt)
        if gtxt is not None:
            pg.fill('#comment', gtxt)
        btn = pg.locator('#doneBtn')
        if 'Doneにする' in btn.inner_text():
            self.act(btn)
        pg.wait_for_timeout(250)
        cls = pg.locator('.chip.cur').first.get_attribute('class')
        if 'st-done' not in (cls or ''):
            self.shot('DBG_' + key.replace('_', '')[:12], full=False)
            R.setdefault('debug', []).append({'view': self.view, 'key': key, 'cls': cls, 'err': pg.inner_text('#doneErr')[:200], 'state': pg.inner_text('#doneState')[:80], 'kp': pg.locator('input[data-term][data-cat="1"]:checked').count()})
        return cls

    def clip(self):
        return self.pg.evaluate('()=>navigator.clipboard.readText()')


def er128_dry(text):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8', newline='\n') as f:
        f.write(text)
        p = f.name
    r = subprocess.run([sys.executable, os.path.join(REPO, 'er128_form_readable_restore_01.py'), 'confirm-batch', '--from-readable-batch', p,
                        '--articles-json', os.path.join(FORM_DATA, 'articles.json'), '--dry-run', '--data-dir', FORM_DATA], capture_output=True, cwd=REPO)
    os.unlink(p)
    out = r.stdout.decode('utf-8', 'replace')
    try:
        j = json.loads(out)
    except Exception:  # noqa: BLE001
        j = {}
    return r.returncode, j, r.stderr.decode('utf-8', 'replace')[:300]


def copy_checks(c, bid, keys, ptok, wtok, label):
    """全Done後の一括コピー: SET数・stem一意・コメント各1回・END・er128 dry受入"""
    pg = c.pg
    c.act(pg.locator('#fCopy'))
    pg.wait_for_timeout(1200)
    txt = c.clip()
    if os.environ.get('SUB04_SAVE_COPY'):
        os.makedirs(os.environ['SUB04_SAVE_COPY'], exist_ok=True)
        with open(os.path.join(os.environ['SUB04_SAVE_COPY'], 'sub04_copy_%s_%s.txt' % (label.split()[0], c.view)), 'w', encoding='utf-8', newline='') as f:
            f.write(txt)
    sets = re.findall(r'════ SET (\d+)/(\d+) ｜ (\S+) ════', txt)
    n = len(keys)
    check(c.tag('%s: 一括コピー=SET %d件・連番・stem一意' % (label, n)), len(sets) == n and [int(s[0]) for s in sets] == list(range(1, n + 1)) and len({s[2] for s in sets}) == n and all(int(s[1]) == n for s in sets), 'sets=%d' % len(sets))
    check(c.tag('%s: ヘッダ バッチ=%s と END 合計%d件' % (label, bid, n)), ('バッチ=%s' % bid) in txt and ('END 合計%d件' % n) in txt)
    pc = [txt.count('【フレーズ】' + ptok(k)) for k in keys]
    wc = [txt.count('【単語】' + wtok(k)) for k in keys]
    check(c.tag('%s: フレーズ/単語コメントが各セット1回ずつ(欠落0・重複0)' % label), all(x == 1 for x in pc) and all(x == 1 for x in wc), 'p=%s w=%s' % (pc[:3], wc[:3]))
    ok_banner = pg.is_visible('#fpop') and ('コピーしました' in pg.inner_text('#fpop'))
    check(c.tag('%s: コピー成功の表示(フッタ直上)' % label), ok_banner, pg.inner_text('#fpop')[:80] if pg.is_visible('#fpop') else 'hidden')
    c.shot('A_copy_ok' if label.startswith('A') else label.replace(' ', '_') + '_copy_ok')
    rc, j, err = er128_dry(txt)
    check(c.tag('%s: er128 confirm-batch --dry-run で受入(全%d件)' % (label, n)), rc == 0 and j.get('n') == n and j.get('dry_run') is True, 'rc=%s n=%s batch=%s %s' % (rc, j.get('n'), j.get('batch_id'), err[:120]))
    return txt


def scenario_a(c, bid='sub04-a-18sets-test'):
    pg = c.pg
    c.open('?batch=' + bid)
    keys = c.keys()
    n = len(keys)
    arts = pg.locator('.art').count()
    check(c.tag('A: 18セット(9記事x2)のみ表示'), n == 18 and arts == 9, 'chips=%d art=%d' % (n, arts))
    names = pg.eval_on_selector_all('.art .aname', 'els=>els.map(e=>e.textContent)')
    check(c.tag('A: 過去記事(猿の手/ダミー/slot等)が混ざらない'), not any(('猿' in x or 'UI確認用' in x or '未登録' in x) for x in names), names[:3])
    check(c.tag('A: 画面に報告idと対象数を表示'), bid in pg.inner_text('#progress') and '18' in pg.inner_text('#progress'), pg.inner_text('#progress')[:90])
    check(c.tag('A: 初期Done 0/18・固定フッタ可視'), c.done_n() == (0, 18) and pg.is_visible('#fbar'), c.done_text())
    c.shot('A_open')
    ptok = lambda k: 'P-' + k   # noqa: E731
    wtok = lambda k: 'W-' + k   # noqa: E731
    # コメント欄は各セットのフレーズ/単語候補の直下にある(配置順)
    c.jump(keys[0])
    order = pg.evaluate("""()=>['candPhrase','boxPhrase','candWord','boxWord','comment','doneBox'].map(i=>[i,Math.round(document.getElementById(i).getBoundingClientRect().top+scrollY)])""")
    check(c.tag('A: 配置順 フレーズ欄→フレーズコメント→単語欄→単語コメント→全体コメント→Done'), [o[1] for o in order] == sorted(o[1] for o in order), order)
    pg.locator('#boxPhrase').scroll_into_view_if_needed()
    c.shot('A_comment_boxes')
    for i, k in enumerate(keys):
        c.complete_set(k, ptok(k), wtok(k), 'G-' + k if i % 5 == 0 else None)
        if i == 7:   # 切替で保持: 先頭セットへ戻り、コメントが残っている
            c.jump(keys[0])
            check(c.tag('A: セット切替で入力保持(フレーズ/単語/全体コメント・Done)'), pg.input_value('#commentPhrase') == ptok(keys[0]) and pg.input_value('#commentWord') == wtok(keys[0]) and pg.input_value('#comment') == 'G-' + keys[0] and 'Done' in pg.locator('.chip.cur').first.inner_text(), pg.input_value('#commentPhrase'))
        if i == 16:
            nd = c.done_n()
            c.act(pg.locator('#fCopy'))
            pg.wait_for_timeout(500)
            check(c.tag('A: 17/18時点の一括コピーは拒否され、未完了1件を列挙'), nd == (17, 18) and pg.is_visible('#fpop') and '1件' in pg.inner_text('#fpop') and pg.locator('#fpop button[data-jump]').count() == 1, '%s %s' % (nd, pg.inner_text('#fpop')[:60]))
            c.shot('A_reject_17of18')
            pg.evaluate("()=>document.getElementById('fpx')&&document.getElementById('fpx').click()")
    check(c.tag('A: 全18セットDone(進捗 18/18)'), c.done_n() == (18, 18), c.done_text())
    c.shot('A_all_done')
    txt = copy_checks(c, bid, keys, ptok, wtok, 'A')
    check(c.tag('A: 全体コメントも該当セットのみに入る(G-…が5件・各1回)'), all(txt.count('【追加指示(全体)】G-' + k) == 1 for i, k in enumerate(keys) if i % 5 == 0) and txt.count('【追加指示(全体)】') == 4, txt.count('【追加指示(全体)】'))
    check(c.tag('A: pageerror 0'), not c.errs, c.errs[:2])
    return keys, txt


def scenario_b(c, bid='sub04-b-5sets-test'):
    pg = c.pg
    c.open('?batch=' + bid)
    keys = c.keys()
    check(c.tag('B: 5セット(3記事・計5レベル)のみ表示・集計'), len(keys) == 5 and pg.locator('.art').count() == 3 and c.done_n() == (0, 5), 'chips=%d art=%d %s' % (len(keys), pg.locator('.art').count(), c.done_text()))
    c.shot('B_open')
    ptok = lambda k: 'BP-' + k   # noqa: E731
    wtok = lambda k: 'BW-' + k   # noqa: E731
    for k in keys:
        c.complete_set(k, ptok(k), wtok(k))
    check(c.tag('B: 5/5 Done'), c.done_n() == (5, 5), c.done_text())
    copy_checks(c, bid, keys, ptok, wtok, 'B')
    check(c.tag('B: pageerror 0'), not c.errs, c.errs[:2])


def scenario_c(c, bid='sub04-c-overlap-test', other='sub04-a-18sets-test'):
    pg = c.pg
    c.open('?batch=' + bid)
    keys = c.keys()
    check(c.tag('C: 3セット表示・別batch(A)の入力状態と混ざらない(同stemが未完了)'), len(keys) == 3 and c.done_n() == (0, 3), c.done_text())
    # 未完了コピー拒否+未完了一覧の可視性(M12)
    c.act(pg.locator('#fCopy'))
    pg.wait_for_timeout(500)
    vis = pg.is_visible('#fpop')
    bb = pg.evaluate("()=>{const p=document.getElementById('fpop').getBoundingClientRect(),f=document.getElementById('fbar').getBoundingClientRect();return {pt:p.top,pb:p.bottom,ft:f.top,vh:innerHeight}}")
    check(c.tag('C: 未完了コピー拒否: 未完了3件が一覧され、フッタ直上で画面内に見える(M12)'), vis and pg.locator('#fpop button[data-jump]').count() == 3 and 0 <= bb['pt'] and bb['pb'] <= bb['ft'] + 1 and bb['ft'] <= bb['vh'], bb)
    c.shot('C_reject_unfinished')
    c.act(pg.locator('#fpop button[data-jump]').nth(1))
    pg.wait_for_timeout(500)
    check(c.tag('C: 未完了一覧のボタンで該当セットへ移動'), c.cur_key() == keys[1], c.cur_key())
    ptok = lambda k: 'CP-' + k   # noqa: E731
    wtok = lambda k: 'CW-' + k   # noqa: E731
    c.complete_set(keys[0], ptok(keys[0]), wtok(keys[0]))
    c.complete_set(keys[1], ptok(keys[1]), wtok(keys[1]))
    c.act(pg.locator('#fCopy'))
    pg.wait_for_timeout(500)
    check(c.tag('C: 2/3時点: 拒否・残り1件のみ列挙'), c.done_n() == (2, 3) and pg.locator('#fpop button[data-jump]').count() == 1 and keys[2].split('__')[0] in pg.locator('#fpop button[data-jump]').first.get_attribute('data-jump'), pg.inner_text('#fpop')[:80])
    # 次の未完了へ
    pg.evaluate("()=>document.getElementById('fpx')&&document.getElementById('fpx').click()")
    c.jump(keys[0])
    c.act(pg.locator('#fNext'))
    pg.wait_for_timeout(500)
    check(c.tag('C: 「次の未完了へ」で未完了セットへ'), c.cur_key() == keys[2], c.cur_key())
    c.complete_set(keys[2], ptok(keys[2]), wtok(keys[2]))
    check(c.tag('C: 3/3 Done'), c.done_n() == (3, 3), c.done_text())
    # Done後の選定変更 -> 自動解除
    c.jump(keys[0])
    first_sel = pg.locator('input[data-term][data-cat="1"]:checked').first
    c.act(first_sel)
    pg.wait_for_timeout(300)
    chip_cls = pg.locator('.chip[data-key="%s"]' % keys[0]).get_attribute('class')
    check(c.tag('C: Done後の選定変更で自動解除(要再確認)・進捗2/3'), 'st-stale' in chip_cls and c.done_n() == (2, 3), '%s %s' % (chip_cls, c.done_text()))
    c.act(pg.locator('#fCopy'))
    pg.wait_for_timeout(400)
    check(c.tag('C: 解除後の一括コピーは拒否(再コピー拒否)'), pg.locator('#fpop button[data-jump]').count() == 1, pg.inner_text('#fpop')[:60])
    c.shot('C_stale_reject')
    pg.evaluate("()=>document.getElementById('fpx')&&document.getElementById('fpx').click()")
    # 再選定して再Done
    c.jump(keys[0])
    c.complete_set(keys[0], ptok(keys[0]), wtok(keys[0]))
    check(c.tag('C: 再選定→再Doneで3/3へ復帰'), c.done_n() == (3, 3), c.done_text())
    # コメント編集 -> 要再確認 -> 再Done
    pg.fill('#commentWord', 'CW-EDITED-' + keys[0])
    pg.wait_for_timeout(300)
    check(c.tag('C: Done後のコメント編集で要再確認(2/3)'), c.done_n() == (2, 3), c.done_text())
    pg.locator('#doneBtn').scroll_into_view_if_needed()
    c.act(pg.locator('#doneBtn'))
    pg.wait_for_timeout(300)
    check(c.tag('C: 再Doneで3/3'), c.done_n() == (3, 3), c.done_text())
    # リロード保持
    c.open('?batch=' + bid)
    check(c.tag('C: リロードで状態保持(Done 3/3・編集後コメント)'), c.done_n() == (3, 3), c.done_text())
    c.jump(keys[0])
    check(c.tag('C: リロード後もコメント保持'), pg.input_value('#commentWord') == 'CW-EDITED-' + keys[0], pg.input_value('#commentWord'))
    c.act(pg.locator('#fCopy'))
    pg.wait_for_timeout(1200)
    txt = c.clip()
    check(c.tag('C: コピーに編集後コメントのみ(旧コメント0・新1)・全セット1回'), txt.count('【単語】CW-EDITED-' + keys[0]) == 1 and txt.count('【単語】CW-' + keys[0]) == 0 and len(re.findall(r'════ SET \d+/3 ', txt)) == 3, '')
    rc, j, err = er128_dry(txt)
    check(c.tag('C: er128 confirm-batch --dry-run 受入(3件)'), rc == 0 and j.get('n') == 3, 'rc=%s %s' % (rc, err[:100]))
    # 別batchで同stemの状態が混ざらない
    c.open('?batch=' + other)
    c.jump(keys[0]) if keys[0] in c.keys() else None
    same = keys[0] in c.keys()
    check(c.tag('C: 別batch(A)を開いても、同じセット(%s)はCで入力した状態を持たない' % keys[0]), same and pg.input_value('#commentWord') == '' and 'todo' in (pg.locator('.chip[data-key="%s"]' % keys[0]).get_attribute('class') or ''), pg.input_value('#commentWord'))
    ls = pg.evaluate("()=>Object.keys(localStorage)")
    check(c.tag('C: localStorageキーが報告単位(eigo-kp-form-v3:b:<id>)'), ('eigo-kp-form-v3:b:' + bid) in ls and 'eigo-kp-form-v3' not in ls and all(k.startswith('eigo-kp-form-v3:') for k in ls), ls)
    # M1: member欠落 -> エラー画面(部分表示しない)
    c2 = c.ctx.new_page()
    def bad_batch(route):
        r = route.fetch()
        d = json.loads(r.text())
        d['members'] = d['members'] + ['moon_shrinking__zz__prod']
        route.fulfill(status=200, body=json.dumps(d, ensure_ascii=False), content_type='application/json; charset=utf-8')
    c2.route('**/data/batches/' + bid + '.json*', bad_batch)
    c2.goto(c.base + 'index.html?batch=' + bid, wait_until='load')
    c2.wait_for_selector('#gate:not([hidden])', timeout=30000)
    check(c.tag('C/M1: member1件が未解決→記事を出さずエラー画面(部分表示禁止)'), c2.locator('.chip[data-key]').count() == 0 and '部分表示はしません' in c2.inner_text('#gate') and not c2.is_visible('#formWrap'), c2.inner_text('#gate')[:100])
    c2.screenshot(path=os.path.join(c.shots, 'C_M1_error_%s.png' % c.view))
    # M2: パラメータ無し→latest解決→URL固定、別id→最新帯
    def with_latest(route):
        r = route.fetch()
        d = json.loads(r.text())
        d['latest'] = bid
        route.fulfill(status=200, body=json.dumps(d, ensure_ascii=False), content_type='application/json; charset=utf-8')
    c2.unroute('**/data/batches/' + bid + '.json*')
    c2.route('**/data/batches/index.json*', with_latest)
    c2.goto(c.base + 'index.html', wait_until='load')
    c2.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    c2.wait_for_timeout(800)
    check(c.tag('C/M2: パラメータ無し→latestに解決しURLを ?batch=<id> に固定'), ('batch=' + bid) in c2.url and c2.locator('.chip[data-key]').count() == 3, c2.url[-60:])
    c2.reload(wait_until='load')
    c2.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    check(c.tag('C/M2: リロードしても同じ報告'), ('batch=' + bid) in c2.url, c2.url[-60:])
    c2.goto(c.base + 'index.html?batch=' + other, wait_until='load')
    c2.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    check(c.tag('C/M2: latestと異なる報告を開くと「最新の報告ではありません」帯'), c2.is_visible('#staleBanner') and bid in c2.inner_text('#staleBanner'), c2.inner_text('#staleBanner')[:80])
    c2.screenshot(path=os.path.join(c.shots, 'C_M2_stale_%s.png' % c.view))
    c2.unroute('**/data/batches/index.json*')
    # M5: 旧 ?a= のみ -> 記事を出さない
    c2.goto(c.base + 'index.html?a=moon_shrinking__a2', wait_until='load')
    c2.wait_for_selector('#gate:not([hidden])', timeout=30000)
    check(c.tag('C/M5: 旧形式 ?a= のみ→記事を出さず「旧形式のリンク」表示'), c2.locator('.chip[data-key]').count() == 0 and '旧形式のリンク' in c2.inner_text('#gate'), c2.inner_text('#gate')[:60])
    c2.screenshot(path=os.path.join(c.shots, 'C_M5_legacy_%s.png' % c.view))
    c2.goto(c.base + 'index.html?batch=' + bid + '&a=melos__b1b', wait_until='load')
    c2.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    check(c.tag('C/M5: ?batch+?a でaが対象外→明示表示'), c2.is_visible('#notinBanner') and '対象外' in c2.inner_text('#notinBanner'), c2.inner_text('#notinBanner')[:60])
    c2.goto(c.base + 'index.html?batch=' + '../etc', wait_until='load')
    c2.wait_for_selector('#gate:not([hidden])', timeout=30000)
    check(c.tag('C/M6: 不正batch id(../)は拒否'), '形式が正しくありません' in c2.inner_text('#gate'), c2.inner_text('#gate')[:60])
    c2.goto(c.base + 'index.html?batch=nosuch-batch-zz', wait_until='load')
    c2.wait_for_selector('#gate:not([hidden])', timeout=30000)
    check(c.tag('C: 存在しないbatch→「見つかりません」'), '見つかりません' in c2.inner_text('#gate'), c2.inner_text('#gate')[:60])
    # ?dev=all の状態キー分離と新機能の描画
    c2.goto(c.base + 'index.html?dev=all', wait_until='load')
    c2.wait_for_selector('#curbar:not([hidden])', timeout=60000)
    c2.wait_for_timeout(800)
    k2 = c2.evaluate("()=>Object.keys(localStorage)")
    check(c.tag('C/dev: ?dev=all は赤帯表示・コメント欄/Done/フッタが同じ描画経路で出る'), c2.is_visible('#devBanner') and c2.is_visible('#commentPhrase') and c2.is_visible('#doneBox') and c2.is_visible('#fbar'), '')
    c2.close()
    # M12: モバイル固定フッタとキーボード
    c.open('?batch=' + bid)
    c.jump(keys[0])
    pg.evaluate('()=>window.scrollTo(0,document.body.scrollHeight)')
    pg.wait_for_timeout(300)
    ov = pg.evaluate("()=>{const f=document.getElementById('fbar').getBoundingClientRect();const a=document.getElementById('assetv').getBoundingClientRect();return {ft:f.top,ab:a.bottom,fb:f.bottom,vh:innerHeight}}")
    check(c.tag('C/M12: 本文末尾がフッタに隠れない(余白)'), ov['ab'] <= ov['ft'] + 1 and abs(ov['fb'] - ov['vh']) <= 1, ov)
    c.shot('C_footer_bottom')
    if c.view == 'mobile':
        c.act(pg.locator('#commentPhrase'))
        pg.wait_for_timeout(300)
        hidden = not pg.is_visible('#fbar')
        pg.evaluate("()=>document.activeElement&&document.activeElement.blur()")
        pg.wait_for_timeout(300)
        check(c.tag('C/M12: 入力欄フォーカス中はフッタを隠し(キーボード重なり回避)、blurで戻る'), hidden and pg.is_visible('#fbar'), hidden)
    check(c.tag('C: pageerror 0'), not c.errs, c.errs[:2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--shots', required=True)
    ap.add_argument('--views', default='pc,mobile')
    ap.add_argument('--scen', default='A,B,C')
    a = ap.parse_args()
    base = a.base if a.base.endswith('/') else a.base + '/'
    R['meta'] = {'base': base, 'views': a.views, 'scen': a.scen}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for view in a.views.split(','):
            for sc in a.scen.split(','):
                c = Ctx(br, view, base, a.shots)
                try:
                    {'A': scenario_a, 'B': scenario_b, 'C': scenario_c}[sc](c)
                except Exception as e:  # noqa: BLE001
                    check(c.tag('%s: 例外なく完走' % sc), False, repr(e)[:250])
                    try:
                        c.shot('EXC_%s' % sc)
                    except Exception:  # noqa: BLE001
                        pass
                c.ctx.close()
        br.close()
    ok = all(x['ok'] for x in R['checks'])
    R['summary'] = {'total': len(R['checks']), 'pass': sum(1 for x in R['checks'] if x['ok']), 'fail': sum(1 for x in R['checks'] if not x['ok'])}
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(R, f, ensure_ascii=False, indent=1)
    print('SUMMARY', R['summary'])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
