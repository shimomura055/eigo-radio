# -*- coding: utf-8 -*-
"""SELECTION-UI-TWO-TIER-01 公開URL実操作E2E(Playwright, PC 1280x900 / mobile 390x844 touch)。原文§5の12項目。API 0。
usage: py -3 twotier_verify.py --base <URL base> --a twotier-a-18sets-test --b twotier-b-5sets-test --out r.json --shots dir --views pc,mobile"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01'))
import sub04_verify as V  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

check, R = V.check, V.R
B_ONLY_EXCLUDE = ('moon_shrinking__a2', 'moon_shrinking__b1b', 'untidiness_family_resource__a2', 'untidiness_family_resource__b1b', 'melos__b1b')


class C(V.Ctx):
    def top(self, bid, wait=True):
        self.pg.goto(self.base + 'index.html?batch=' + bid, wait_until='load')
        if wait:
            self.pg.wait_for_selector('#list .art', timeout=60000)
            self.pg.wait_for_timeout(600)

    def set_url(self, bid, key):
        return self.base + 'index.html?batch=%s&set=%s' % (bid, key)

    def open_set_by_chip(self, key):
        self.act(self.pg.locator('a.chip[data-key="%s"]' % key))
        self.pg.wait_for_selector('#curbar:not([hidden])', timeout=60000)
        self.pg.wait_for_timeout(500)

    def back_top_btn(self, which):
        self.act(self.pg.locator('#topBack%d' % which))
        self.pg.wait_for_selector('#list .art', timeout=60000)
        self.pg.wait_for_timeout(300)

    def pick3(self):
        pg = self.pg
        have = pg.locator('input[data-term][data-cat="1"]:checked').count()
        for _ in range(max(0, 3 - have)):
            self.act(pg.locator('input[data-term][data-cat="1"]:not(:checked):not([disabled])').first)
            pg.wait_for_timeout(120)
        gn = pg.locator('input[data-grammar-none]')
        if gn.count() and not gn.first.is_checked():
            self.act(gn.first)

    def fill_done(self, ptxt, wtxt, gtxt=None):
        pg = self.pg
        self.pick3()
        pg.fill('#commentPhrase', ptxt)
        pg.fill('#commentWord', wtxt)
        if gtxt is not None:
            pg.fill('#comment', gtxt)
        btn = pg.locator('#doneBtn')
        if 'Doneにする' in btn.inner_text():
            self.act(btn)
        pg.wait_for_timeout(250)

    def complete_set(self, bid, key, ptxt, wtxt, gtxt=None):
        self.top(bid)
        self.open_set_by_chip(key)
        self.fill_done(ptxt, wtxt, gtxt)
        self.back_top_btn(1)

    def progress(self):
        m = re.search(r'Done (\d+)/(\d+)', self.pg.inner_text('#fDone'))
        return (int(m.group(1)), int(m.group(2)))

    def chip_cls(self, key):
        return self.pg.locator('a.chip[data-key="%s"]' % key).get_attribute('class')

    def keys(self):
        return self.pg.eval_on_selector_all('a.chip[data-key]', 'els=>els.map(e=>e.dataset.key)')


def run(c, A, B):
    pg = c.pg
    c.top(A)
    keys = c.keys()
    n = len(keys)
    arts = pg.locator('#list .art').count()
    # 1
    vis_form = pg.evaluate("()=>{const f=document.getElementById('setForm');return f.hidden||getComputedStyle(f).display==='none'}")
    inputs_vis = pg.evaluate("()=>[...document.querySelectorAll('input[data-term],textarea#comment,textarea#commentPhrase,textarea#commentWord,#doneBtn,#topBack1')].filter(e=>e.offsetParent!==null).length")
    check(c.tag('1 トップ: 一覧のみ(記事%d・セット%d)、個別フォーム非表示' % (arts, n)), vis_form and inputs_vis == 0 and n == 18 and arts == 9 and re.search(r'Done\s*0\s*/\s*18', pg.inner_text('#progress')) is not None,
          'form_hidden=%s visible_form_controls=%s progress=%s' % (vis_form, inputs_vis, pg.inner_text('#progress')[:50].replace('\n', ' ')))
    labels = pg.eval_on_selector_all('a.chip', 'els=>els.map(e=>e.textContent.split("｜")[0])')
    check(c.tag('1b チップ文言Standard/Advanced'), set(labels) == {'Standard', 'Advanced'}, str(sorted(set(labels))))
    c.shot('T1_top')
    c.shot('T1_top_full', True)
    # 2
    k0, k1 = keys[0], keys[1]
    c.open_set_by_chip(k0)
    u = pg.url
    shown = pg.evaluate("()=>({form:document.getElementById('setForm').offsetParent!==null,list:document.getElementById('batchTop').offsetParent!==null,cur:document.getElementById('curbar').textContent,n:document.querySelectorAll('input[data-term]').length})")
    check(c.tag('2 Standardクリックで個別ページ(%s)' % k0), ('set=' + k0) in u and 'batch=' + A in u and shown['form'] and not shown['list'] and shown['n'] > 0 and 'Standard' in shown['cur'],
          'url=%s cur=%s n=%d' % (u[-70:], shown['cur'][:50], shown['n']))
    c.top(A)
    c.open_set_by_chip(k1)
    check(c.tag('2b Advancedクリックで個別ページ(%s)' % k1), ('set=' + k1) in pg.url and 'Advanced' in pg.inner_text('#curbar'), pg.inner_text('#curbar')[:60])
    order = pg.evaluate("()=>{const y=id=>document.getElementById(id).getBoundingClientRect().top+scrollY;return ['topBack1','curbar','candPhrase','boxPhrase','candWord','boxWord','comment','doneBox','topBack2'].map(id=>[id,Math.round(y(id))])}")
    ys = [o[1] for o in order]
    check(c.tag('2c 個別ページの順序: 上Top→タイトル/レベル→フレーズ→フレーズコメント→単語→単語コメント→全体→Done→下Top'), ys == sorted(ys), str(order))
    sz = pg.evaluate("()=>['topBack1','topBack2'].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})")
    check(c.tag('11a Topへ戻るボタンが押しやすいサイズ(高さ>=44, 幅>=120)'), all(h >= 44 and w >= 120 for w, h in sz), str(sz))
    c.shot('T2_set_top')
    c.shot('T2_set_full', True)
    pg.evaluate("()=>window.scrollTo(0,document.body.scrollHeight)")
    pg.wait_for_timeout(300)
    inview = pg.evaluate("()=>{const r=document.getElementById('topBack2').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}")
    check(c.tag('4a 最下部で下のTopへ戻るボタンが画面内'), inview)
    c.shot('T3_set_bottom')
    # 3
    pg.evaluate("()=>window.scrollTo(0,0)")
    c.back_top_btn(1)
    check(c.tag('3 上のTopへ戻る→同batchのトップ'), ('batch=' + A) in pg.url and 'set=' not in pg.url and pg.locator('#list .art').count() == 9, pg.url[-60:])
    # 4
    c.open_set_by_chip(k1)
    pg.evaluate("()=>window.scrollTo(0,document.body.scrollHeight)")
    pg.wait_for_timeout(200)
    c.back_top_btn(2)
    check(c.tag('4 下のTopへ戻る→同batchのトップ'), ('batch=' + A) in pg.url and 'set=' not in pg.url and pg.locator('#list .art').count() == 9, pg.url[-60:])
    # 5
    c.open_set_by_chip(k0)
    c.pick3()
    pg.fill('#commentPhrase', 'P-' + k0)
    pg.fill('#commentWord', 'W-' + k0)
    pg.fill('#comment', 'G-' + k0)
    sel_before = pg.eval_on_selector_all('input[data-term]:checked', 'els=>els.map(e=>e.dataset.term+":"+e.dataset.cat)')
    pg.wait_for_timeout(200)
    c.back_top_btn(1)
    c.open_set_by_chip(k0)
    sel_after = pg.eval_on_selector_all('input[data-term]:checked', 'els=>els.map(e=>e.dataset.term+":"+e.dataset.cat)')
    check(c.tag('5 選択(フレーズ/単語)とコメント3種がページ移動後も保持'), sel_before == sel_after and len(sel_after) >= 3 and pg.input_value('#commentPhrase') == 'P-' + k0
          and pg.input_value('#commentWord') == 'W-' + k0 and pg.input_value('#comment') == 'G-' + k0, 'sel=%d' % len(sel_after))
    check(c.tag('12a 既存: 残りをすべて選択ボタンが個別ページに存在(①3件で有効)'), pg.locator('#selRest').count() == 1 and pg.locator('#selRest').is_enabled())
    # 6
    c.fill_done('P-' + k0, 'W-' + k0, 'G-' + k0)
    st_set = pg.inner_text('#doneState')
    c.back_top_btn(1)
    check(c.tag('6 個別でDone→トップの進捗とチップが更新(Done 1/18)'), c.progress() == (1, 18) and 'st-done' in c.chip_cls(k0), 'prog=%s cls=%s | %s' % (c.progress(), c.chip_cls(k0), st_set))
    c.shot('T4_top_done1')
    # 7
    c.open_set_by_chip(k0)
    c.act(pg.locator('input[data-term][data-cat="1"]:checked').first)
    pg.wait_for_timeout(300)
    ds = pg.inner_text('#doneState')
    c.back_top_btn(1)
    check(c.tag('7 Done後に選択変更→Done解除(個別表示・トップ0/18・チップ未完了)'), ('未完了' in ds) and c.progress() == (0, 18) and 'st-done' not in c.chip_cls(k0), '%s | %s | %s' % (ds[:40], c.progress(), c.chip_cls(k0)))
    c.open_set_by_chip(k0)
    c.fill_done('P-' + k0, 'W-' + k0, 'G-' + k0)
    c.back_top_btn(1)
    # 13 戻る/再読み込み
    c.open_set_by_chip(k0)
    pg.go_back()
    pg.wait_for_selector('#list .art', timeout=30000)
    pg.wait_for_timeout(500)
    b1 = ('set=' not in pg.url) and c.progress() == (1, 18)
    pg.go_forward()
    pg.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    pg.wait_for_timeout(500)
    b2 = ('set=' + k0) in pg.url and pg.input_value('#commentPhrase') == 'P-' + k0
    pg.reload(wait_until='load')
    pg.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    pg.wait_for_timeout(700)
    b3 = ('set=' + k0) in pg.url and pg.input_value('#commentPhrase') == 'P-' + k0 and pg.input_value('#comment') == 'G-' + k0 and 'Done です' in pg.inner_text('#doneState') and pg.locator('input[data-term][data-cat="1"]:checked').count() == 3
    check(c.tag('13 ブラウザ戻る→トップ(進捗維持)/進む→個別(入力維持)/個別再読み込み(選択・コメント・Done維持)'), b1 and b2 and b3, 'back=%s fwd=%s reload=%s' % (b1, b2, b3))
    # 直接URL
    pg.goto(c.set_url(A, k1), wait_until='load')
    pg.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    check(c.tag('2d URL直接オープンで指定セットのフォーム表示'), 'Advanced' in pg.inner_text('#curbar') and pg.locator('input[data-term]').count() > 0, pg.inner_text('#curbar')[:60])
    # 14 無効URL
    bonly = [k for k in keys if k not in B_ONLY_EXCLUDE][0]
    for label, url in [('存在しないセット', c.set_url(A, 'no_such__a2')), ('別batchに無いセット', c.set_url(B, bonly)),
                       ('不正batch', c.base + 'index.html?batch=zz'), ('batch無し', c.base + 'index.html')]:
        pg.goto(url, wait_until='load')
        pg.wait_for_selector('#gate:not([hidden])', timeout=30000)
        g = pg.inner_text('#gate')
        hidden = pg.evaluate("()=>document.getElementById('formWrap').hidden")
        okg = hidden and pg.locator('input[data-term]').count() == 0 and (('Top' in g) if ('存在' in label or '別batch' in label) else True)
        check(c.tag('14 無効URL安全案内: ' + label), okg, g[:80].replace('\n', ' '))
        if label == '存在しないセット':
            c.shot('T5_invalid')
    # 8
    ptok = lambda k: 'P-' + k  # noqa: E731
    wtok = lambda k: 'W-' + k  # noqa: E731
    for i, k in enumerate(keys[:-1]):
        if k == k0:
            continue
        c.complete_set(A, k, ptok(k), wtok(k), 'G-' + k if i % 5 == 0 else None)
    c.top(A)
    check(c.tag('8a 17/18時点の進捗'), c.progress() == (17, 18), str(c.progress()))
    c.act(pg.locator('#fCopy'))
    pg.wait_for_timeout(700)
    pop = pg.inner_text('#fpop') if pg.is_visible('#fpop') else ''
    check(c.tag('8b 未完了時は一括コピー拒否+未完了一覧(1件)'), '未完了のセットが1件' in pop and pg.locator('#fpop button[data-jump]').count() == 1, pop[:90].replace('\n', ' '))
    c.shot('T6_copy_refused')
    c.act(pg.locator('#fpop button[data-jump]').first)
    pg.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    check(c.tag('8c 未完了一覧→該当個別ページへ遷移'), ('set=' + keys[-1]) in pg.url, pg.url[-60:])
    c.fill_done(ptok(keys[-1]), wtok(keys[-1]))
    c.back_top_btn(1)
    check(c.tag('8d 18/18 Done'), c.progress() == (18, 18), str(c.progress()))
    c.shot('T7_top_18done')
    c.open_set_by_chip(k0)
    nocopy = pg.evaluate("()=>[...document.querySelectorAll('#batchCopy,#fCopy')].filter(e=>e.offsetParent!==null).length")
    check(c.tag('8e 個別ページには一括コピー/固定フッタを出さない(ページ毎コピー方式にしない)'), nocopy == 0 and pg.evaluate("()=>getComputedStyle(document.getElementById('fbar')).display") == 'none', 'visible=%d' % nocopy)
    c.back_top_btn(1)
    V.copy_checks(c, A, keys, ptok, wtok, 'TT-A 18セット')
    # 10 別batch
    c.top(B)
    kb = c.keys()
    check(c.tag('10a 別batch(B)はA入力と非混在: Done 0/%d・セット%d' % (len(kb), len(kb))), c.progress() == (0, 5) and len(kb) == 5, str(c.progress()))
    c.open_set_by_chip(kb[0])
    sk = pg.evaluate("()=>Object.keys(localStorage).filter(k=>k.indexOf('eigo-kp-form-v3:b:')===0)")
    check(c.tag('10b 同一セット(%s)でもBのフォームは空で、localStorageキーがbatch別' % kb[0]), pg.input_value('#commentPhrase') == '' and pg.locator('input[data-term]:checked').count() == 0
          and ('eigo-kp-form-v3:b:' + A) in sk and ('eigo-kp-form-v3:b:' + B) not in sk, 'keys=%s' % sk)
    c.shot('T8_batchB_set')
    c.fill_done('BP-' + kb[0], 'BW-' + kb[0])
    c.back_top_btn(1)
    pg.goto(c.set_url(A, kb[0]), wait_until='load')
    pg.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    check(c.tag('10c Bで入力後もAの同セットは元のコメントのまま'), pg.input_value('#commentPhrase') == ptok(kb[0]), pg.input_value('#commentPhrase'))
    check(c.tag('15 JSエラー0'), not c.errs, str(c.errs[:3]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--shots', required=True)
    ap.add_argument('--views', default='pc,mobile')
    a = ap.parse_args()
    base = a.base if a.base.endswith('/') else a.base + '/'
    R['meta'] = {'base': base, 'a': a.a, 'b': a.b}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for view in a.views.split(','):
            c = C(br, view, base, a.shots)
            try:
                run(c, a.a, a.b)
            except Exception as e:  # noqa: BLE001
                check(c.tag('例外なく完走'), False, repr(e)[:250])
                try:
                    c.shot('EXC')
                except Exception:  # noqa: BLE001
                    pass
            c.ctx.close()
        br.close()
    R['summary'] = {'total': len(R['checks']), 'pass': sum(1 for x in R['checks'] if x['ok']), 'fail': sum(1 for x in R['checks'] if not x['ok'])}
    json.dump(R, open(a.out, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('SUMMARY', R['summary'])
    return 0 if R['summary']['fail'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
