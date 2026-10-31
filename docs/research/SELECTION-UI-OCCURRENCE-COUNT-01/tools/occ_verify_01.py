# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_02: 出現回数表示の公開URL(または local server)実操作E2E(Playwright, PC 1280x900 / mobile 390x844 touch)。API 0。
usage: py occ_verify_01.py --base <URL base> --batch occ-a-test --old twotier-a-18sets-test,twotier-b-5sets-test --out r.json --shots dir --views pc,mobile
検査: (1)トップ (2)全member個別ページの回数行(Phrase/Word・6水準) (3)表示例(実データ)と区分内訳/保留/未集計/確認不能/タイトルのみ (4)既存機能(Done・保持・コメント・一括コピー[er128 dry受入]・Topへ戻る・?set=直接)
(5)旧batch(回数なしdata)が無変更・sha一致で表示できる(M4)。"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'docs', 'research', 'SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01'))
import sub04_verify as V  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

check, R = V.check, V.R

FAMILY_LEVELS = {  # 6水準(family x Standard/Advanced) -> chip key
    'X Standard': 'untidiness_family_resource_occ__a2', 'X Advanced': 'untidiness_family_resource_occ__b1b',
    'Y Standard': 'surname_choice_occ__a2', 'Y Advanced': 'surname_choice_occ__b1b',
    'Z Standard': 'yuki_onna_occ__a2', 'Z Advanced': 'yuki_onna_occ__b1b',
}


class C(V.Ctx):
    def shot(self, name, full=False):
        os.makedirs(self.shots, exist_ok=True)
        self.pg.screenshot(path=os.path.join(self.shots, '%s_%s.png' % (name, self.view)), full_page=full, scale='css')

    def top(self, bid):
        self.pg.goto(self.base + 'index.html?batch=' + bid, wait_until='load')
        self.pg.wait_for_selector('#list .art', timeout=60000)
        self.pg.wait_for_timeout(600)

    def open_set(self, key):
        self.act(self.pg.locator('a.chip[data-key="%s"]' % key))
        self.pg.wait_for_selector('#curbar:not([hidden])', timeout=60000)
        self.pg.wait_for_timeout(500)

    def back_top(self, which=1):
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

    def progress(self):
        m = re.search(r'Done (\d+)/(\d+)', self.pg.inner_text('#fDone'))
        return (int(m.group(1)), int(m.group(2)))

    def occ_rows(self):
        """個別ページの全候補行: [{kind, term, state, text, note, total}]"""
        return self.pg.evaluate("""()=>{const out=[];for(const [box,kind] of [['candPhrase','phrase'],['candWord','word']]){document.querySelectorAll('#'+box+' .item').forEach(it=>{
          const t=it.querySelector('.lab label');const o=it.querySelector('.occ[data-occ]');
          out.push({kind:kind,term:t?t.textContent:'',state:o?o.dataset.occ:null,text:o?o.textContent.replace(/\\s+/g,' ').trim():null,total:o?Number(o.dataset.occTotal):null,
                    rect:o?(r=>[Math.round(r.left),Math.round(r.right)])(o.getBoundingClientRect()):null})})}return out}""")

    def no_hscroll(self):
        return self.pg.evaluate("()=>document.documentElement.scrollWidth<=window.innerWidth+1")


def row(rows, kind, term):
    return next((r for r in rows if r['kind'] == kind and r['term'] == term), None)


def run(c, bid, old_ids, obs):
    pg = c.pg
    c.top(bid)
    keys = c.keys()
    n = len(keys)
    vis_form = pg.evaluate("()=>{const f=document.getElementById('setForm');return f.hidden||getComputedStyle(f).display==='none'}")
    check(c.tag('1 トップ: member %d セット・個別フォーム非表示・occHintなし' % n), n == 10 and vis_form and not pg.is_visible('#occHint'), 'chips=%d' % n)
    c.shot('O1_top')
    # 2/3 全memberの回数行
    per_set = {}
    for k in keys:
        c.open_set(k)
        rows = c.occ_rows()
        per_set[k] = rows
        items = pg.locator('#candPhrase .item, #candWord .item').count()
        hint = pg.inner_text('#occHint') if pg.is_visible('#occHint') else ''
        warn = 'occwarn' in (pg.get_attribute('#occHint', 'class') or '')
        ok_rows = len(rows) == items and items > 0 and all(r['state'] for r in rows)
        kinds = {r['kind'] for r in rows}
        check(c.tag('2 %s: 全候補(%d件)に回数行・Phrase/Word両方・注記表示・集計不能の警告なし' % (k, items)), ok_rows and kinds == {'phrase', 'word'} and hint.startswith('出現回数は') and not warn,
              'rows=%d items=%d kinds=%s hint=%s' % (len(rows), items, sorted(kinds), hint[:30]))
        check(c.tag('2b %s: 横スクロールなし・回数行が画面幅内' % k), c.no_hscroll() and all(r['rect'] and r['rect'][0] >= 0 and r['rect'][1] <= pg.evaluate('()=>window.innerWidth') + 1 for r in rows), str([r['rect'] for r in rows][:2]))
        c.pg.go_back() if False else None
        c.top(bid)
    obs['per_set'] = per_set
    # 6水準
    for lab, key in FAMILY_LEVELS.items():
        rows = per_set.get(key) or []
        good = [r for r in rows if r['state'] == 'ok' and r['text'].startswith('出現 ')]
        check(c.tag('3a 6水準 %s: 「出現 N回｜…」表示あり(%d行)' % (lab, len(good))), len(good) >= 1 and any(r['kind'] == 'phrase' for r in good) and any(r['kind'] == 'word' for r in good), good[0]['text'] if good else '')
    # 表示例(ユーザー指定5表現 x 実本文)
    c.open_set('occ_userfive__b1b')
    rows = c.occ_rows()
    r = row(rows, 'phrase', 'put away')
    check(c.tag('3b put away(Advanced)=出現 6回｜本文4・Comment1・In One Line1・数えた形の行内表示'), r and r['text'].startswith('出現 6回｜本文4・Comment1・In One Line1') and 'put it away' in r['text'], r and r['text'])
    r = row(rows, 'phrase', 'in the way')
    check(c.tag('3c in the way=出現 1回｜本文1(in a way等は数えない)'), r and r['text'].startswith('出現 1回｜本文1') and 'In One Line' not in r['text'], r and r['text'])
    r = row(rows, 'phrase', 'leave out')
    check(c.tag('3d leave out=出現 5回｜本文3・Comment1・Preview1 ＋似た形1（未計上）(保留)'), r and r['text'].startswith('出現 5回｜本文3・Comment1・Preview1') and '＋似た形1（未計上）' in r['text'] and 'left out' in r['text'], r and r['text'])
    r = row(rows, 'phrase', 'in sight')
    check(c.tag('3e in sight=出現 5回｜本文3・Comment1・In One Line1'), r and r['text'].startswith('出現 5回｜本文3・Comment1・In One Line1'), r and r['text'])
    r = row(rows, 'word', 'leave')
    check(c.tag('3f 単語 leave=left等の過去形は保留(＋似た形…未計上、M1)'), r and '＋似た形' in r['text'] and '未計上' in r['text'], r and r['text'])
    c.shot('O2_userfive_b1b_top')
    pg.locator('#candWord').scroll_into_view_if_needed()
    c.shot('O2_userfive_b1b_words')
    c.shot('O2_userfive_b1b_full', True)
    c.open_set_after = None
    c.top(bid)
    c.open_set('occ_userfive__a2')
    rows = c.occ_rows()
    r = row(rows, 'phrase', 'force away')
    check(c.tag('3g Standard force away(本文に無い項目)=「出現回数を確認できません」(0回と断定しない・M5)'), r and r['state'] == 'unconfirmable' and r['text'] == '出現回数を確認できません' and '0回' not in r['text'], r and r['text'])
    r = row(rows, 'phrase', 'put away')
    check(c.tag('3h Standard put away=出現 6回｜本文5・In One Line1(日本語Comment/Previewは英語tokenなし)'), r and r['text'].startswith('出現 6回｜本文5・In One Line1'), r and r['text'])
    c.shot('O3_userfive_a2_top')
    c.top(bid)
    c.open_set('untidiness_family_resource_occ__b1b')
    rows = c.occ_rows()
    r = row(rows, 'phrase', 'Now in Session')
    check(c.tag('3i タイトルのみの候補=「出現 本文等0回・タイトルのみ1回」(M5)'), r and r['state'] == 'title_only' and r['text'] == '出現 本文等0回・タイトルのみ1回', r and r['text'])
    r = row(rows, 'word', 'clutter')
    check(c.tag('3j clutter=出現 5回｜本文2・Comment1・Preview1・In One Line1'), r and r['text'].startswith('出現 5回｜本文2・Comment1・Preview1・In One Line1'), r and r['text'])
    c.shot('O4_untidiness_b1b_top')
    c.top(bid)
    c.open_set('redelivery_fee_occ__b1b')
    rows = c.occ_rows()
    check(c.tag('3k 区分未取得(KP-only evidence run)=全行「※Comment・Preview未集計」(0と偽らない)'), rows and all('※Comment・Preview未集計' in r['text'] for r in rows), [r['text'] for r in rows][:2])
    c.shot('O5_unavailable')
    c.top(bid)
    c.open_set('melos_occ__a2')
    rows = c.occ_rows()
    check(c.tag('3l Z melos Standard=Comment・Preview未集計の行あり'), rows and any('※Comment・Preview未集計' in r['text'] for r in rows), [r['text'] for r in rows][:2])
    # 4 既存機能
    c.top(bid)
    k0 = 'untidiness_family_resource_occ__b1b'
    c.open_set(k0)
    before_rows = c.occ_rows()
    c.fill_done('P-' + k0, 'W-' + k0, 'G-' + k0)
    after_rows = c.occ_rows()
    check(c.tag('4a 選択・コメント入力・Done後も回数行は不変(再描画で消えない)'), [r['text'] for r in before_rows] == [r['text'] for r in after_rows] and len(after_rows) > 0, '%d rows' % len(after_rows))
    sel_before = pg.eval_on_selector_all('input[data-term]:checked', 'els=>els.map(e=>e.dataset.term+":"+e.dataset.cat)')
    pg.reload(wait_until='load')
    pg.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    pg.wait_for_timeout(700)
    sel_after = pg.eval_on_selector_all('input[data-term]:checked', 'els=>els.map(e=>e.dataset.term+":"+e.dataset.cat)')
    check(c.tag('4b 再読み込み後も選択・コメント3種・Doneを保持し、回数行も表示'), sel_before == sel_after and len(sel_after) >= 3 and pg.input_value('#commentPhrase') == 'P-' + k0 and pg.input_value('#commentWord') == 'W-' + k0
          and pg.input_value('#comment') == 'G-' + k0 and 'Done です' in pg.inner_text('#doneState') and len(c.occ_rows()) == len(before_rows), 'sel=%d' % len(sel_after))
    c.back_top(2)
    check(c.tag('4c 下のTopへ戻る→同batchのトップ(Done 1/10・チップ更新)'), ('batch=' + bid) in pg.url and 'set=' not in pg.url and c.progress() == (1, 10) and 'st-done' in (pg.locator('a.chip[data-key="%s"]' % k0).get_attribute('class') or ''), str(c.progress()))
    pg.goto(c.base + 'index.html?batch=%s&set=%s' % (bid, FAMILY_LEVELS['Y Advanced']), wait_until='load')
    pg.wait_for_selector('#curbar:not([hidden])', timeout=30000)
    check(c.tag('4d ?set=個別URL直接オープンで回数行つきフォーム表示'), len(c.occ_rows()) > 0 and 'Advanced' in pg.inner_text('#curbar'), pg.inner_text('#curbar')[:50])
    # 残り全セットDone -> 一括コピー
    for k in keys:
        if k == k0:
            continue
        c.top(bid)
        c.open_set(k)
        c.fill_done('P-' + k, 'W-' + k)
    c.top(bid)
    check(c.tag('4e 全10セットDone'), c.progress() == (10, 10), str(c.progress()))
    txt = V.copy_checks(c, bid, keys, lambda k: 'P-' + k, lambda k: 'W-' + k, 'OCC 10セット')
    check(c.tag('4f 一括コピー本文に出現回数が入らない(受領形式・照合コード無変更)'), not re.search(r'出現 ?\d+回|出現回数を|本文\d|似た形|未集計|occurrence', txt), 'len=%d' % len(txt))      # 記事名の「出現回数テスト」は表示名であって回数データではない
    c.shot('O6_top_all_done')
    # 5 旧batch(回数なしdata)が無変更・sha一致で表示できる
    for ob in old_ids:
        c.top(ob)
        kk = c.keys()
        c.open_set(kk[0])
        sha_hidden = pg.evaluate("()=>document.getElementById('shaBanner').hidden")
        hint = pg.inner_text('#occHint') if pg.is_visible('#occHint') else ''
        rows = c.occ_rows()
        check(c.tag('5 旧batch %s: 無変更dataがsha一致(警告なし)で表示・候補表示・回数なしはページ単位案内' % ob), sha_hidden and pg.locator('input[data-term]').count() > 0 and '集計できませんでした' in hint and all(r['state'] is None for r in rows),
              'sha_hidden=%s hint=%s rows=%d' % (sha_hidden, hint[:30], len(rows)))
        if ob == old_ids[0]:
            c.shot('O7_old_batch_set')
    check(c.tag('6 JSエラー0'), not c.errs, str(c.errs[:3]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--batch', required=True)
    ap.add_argument('--old', default='')
    ap.add_argument('--out', required=True)
    ap.add_argument('--shots', required=True)
    ap.add_argument('--views', default='pc,mobile')
    a = ap.parse_args()
    base = a.base if a.base.endswith('/') else a.base + '/'
    R['meta'] = {'base': base, 'batch': a.batch, 'old': a.old}
    obs = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for view in a.views.split(','):
            c = C(br, view, base, a.shots)
            try:
                run(c, a.batch, [x for x in a.old.split(',') if x], obs)
                R.setdefault('observations', {})[view] = obs.get('per_set')
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
