# -*- coding: utf-8 -*-
"""選定フォームv3 公開URLのlive smoke(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_04、Opus M7/M9/M13)。

公開URL(GitHub Pages)の実物を、ヘッドレスブラウザ(PC 1280x900 / mobile 390x844 touch)で開いて検査する。
コード・fixtureのtestだけでは見落とした「公開に載っていない/操作できない」を、公開URL上の実測で防ぐ恒久ツール。

kind:
  batch  : <base>/index.html?batch=<id>  が members 数のセットだけ出す(全枠フォールバック無し・コメント欄2種可視・固定フッタ・pageerror 0・
           UI版(ASSET_VERSION)がローカルHEADと一致)
  latest : <base>/index.html (パラメータ無し) が latest の batch に解決し、URLが ?batch=<id> に固定される
  none   : <base>/index.html (パラメータ無し) が記事を一切出さず「対象の報告が指定されていません」を出す(latest未設定時)
結果JSON(schema=eigo_radio_selection_live_smoke_v1)を --out へ書く。status=PASS以外は URL を利用者へ提示してはならない
(tools/selection_batch_url_01.issue_batch_url が結果JSONを読んで強制する)。
Pages未反映の間は --wait-sec の範囲で自動再pollする(M9)。API呼出0。"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request

BASE_DEFAULT = 'https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/'
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = 'eigo_radio_selection_live_smoke_v1'


def local_asset_version(form_dir):
    s = open(os.path.join(form_dir, 'form_logic.js'), encoding='utf-8').read()
    m = re.search(r"var ASSET_VERSION = '([^']+)'", s)
    return m.group(1) if m else None


def http_get(url, timeout=30):
    req = urllib.request.Request(url + ('&' if '?' in url else '?') + 'nocache=' + str(int(time.time() * 1000)), headers={'Cache-Control': 'no-cache', 'User-Agent': 'eigo-radio-smoke/1'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def poll_published(base, kind, batch_id, asset_version, wait_sec, interval=15):
    """Pages反映待ち。form_logic.jsのASSET_VERSION一致、(batch/latestなら)batchファイルとindex登録を確認。診断を返す。"""
    t0 = time.time()
    diag = {}
    while True:
        diag = {}
        try:
            st, b = http_get(base + 'form_logic.js')
            m = re.search(r"var ASSET_VERSION = '([^']+)'", b.decode('utf-8', 'replace'))
            diag['live_asset_version'] = m.group(1) if m else None
            diag['js_ok'] = (st == 200 and diag['live_asset_version'] == asset_version)
        except Exception as e:  # noqa: BLE001
            diag['js_ok'] = False
            diag['js_error'] = str(e)[:120]
        idx = None
        try:
            st, b = http_get(base + 'data/batches/index.json')
            idx = json.loads(b.decode('utf-8')) if st == 200 else None
        except Exception as e:  # noqa: BLE001
            diag['index_error'] = str(e)[:120]
        diag['index_ok'] = idx is not None
        if kind == 'batch':
            diag['batch_in_index'] = bool(idx and any(x.get('id') == batch_id for x in idx.get('batches', [])))
            try:
                st, b = http_get(base + 'data/batches/%s.json' % batch_id)
                diag['batch_file_ok'] = (st == 200)
            except Exception as e:  # noqa: BLE001
                diag['batch_file_ok'] = False
                diag['batch_file_error'] = str(e)[:120]
            ok = diag['js_ok'] and diag['index_ok'] and diag['batch_in_index'] and diag['batch_file_ok']
        elif kind == 'latest':
            diag['latest_is_id'] = bool(idx and idx.get('latest') == batch_id)
            ok = diag['js_ok'] and diag['latest_is_id']
        else:  # none
            diag['latest_is_none'] = bool(idx is not None and not idx.get('latest'))
            ok = diag['js_ok'] and (diag['latest_is_none'] or idx is None)
        if ok:
            diag['waited_sec'] = round(time.time() - t0)
            return True, diag, idx
        if time.time() - t0 > wait_sec:
            diag['waited_sec'] = round(time.time() - t0)
            # 原因診断(M9): Pages未反映 / JS版不一致 / データ欠落
            if not diag.get('js_ok'):
                diag['cause'] = 'JS版不一致またはPages未反映(live ASSET_VERSION=%s, local=%s)' % (diag.get('live_asset_version'), asset_version)
            elif kind == 'batch' and not diag.get('batch_file_ok'):
                diag['cause'] = 'batchファイルが公開に無い(データ欠落/未push)'
            elif kind == 'batch' and not diag.get('batch_in_index'):
                diag['cause'] = 'index.jsonにbatch未登録'
            elif kind == 'latest':
                diag['cause'] = 'index.jsonのlatestが期待idでない'
            else:
                diag['cause'] = 'index.jsonのlatestが残っている'
            return False, diag, idx
        time.sleep(interval)


def run_views(base, kind, batch_id, n_members, asset_version, shots_dir=None):
    from playwright.sync_api import sync_playwright
    results = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for view in ('pc', 'mobile'):
            kw = dict(viewport={'width': 1280, 'height': 900}) if view == 'pc' else dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
            ctx = br.new_context(**kw)
            pg = ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            checks = []

            def ck(name, ok, obs=''):
                checks.append({'name': name, 'ok': bool(ok), 'obs': str(obs)[:240]})

            url = base + 'index.html' + ('?batch=%s' % batch_id if kind == 'batch' else '')
            pg.goto(url, wait_until='load')
            if kind == 'none':
                pg.wait_for_selector('#gate:not([hidden])', timeout=30000)
                ck('none: 記事を出さない(chip 0・セレクタ非表示)', pg.locator('.chip[data-key]').count() == 0 and not pg.is_visible('#formWrap'))
                ck('none: 「対象の報告が指定されていません」', '対象の報告が指定されていません' in pg.inner_text('#gate'), pg.inner_text('#gate')[:80])
            else:
                # 2階層UI(SELECTION-UI-TWO-TIER-01): トップ=一覧のみ(個別フォーム非表示)、個別=?set=
                pg.wait_for_selector('#list .art', timeout=60000)
                pg.wait_for_timeout(1500)
                chips = pg.locator('a.chip[data-key]').count()
                ck('%s: セット数==members数(全枠フォールバック無し)' % kind, chips == n_members, 'chips=%d members=%d' % (chips, n_members))
                ck('%s: トップに個別フォーム(コメント欄・候補)を出さない' % kind, not pg.is_visible('#setForm') and not pg.is_visible('#commentPhrase') and pg.locator('input[data-term]').count() == 0)
                ck('%s: 固定フッタ(Done n/M・次の未完了へ・一括コピー)' % kind, pg.is_visible('#fbar') and pg.is_visible('#fDone') and pg.is_visible('#fNext') and pg.is_visible('#fCopy'), pg.inner_text('#fDone'))
                ck('%s: Done 0/%d 表示' % (kind, n_members), ('/%d' % n_members) in pg.inner_text('#fDone'), pg.inner_text('#fDone'))
                av = pg.evaluate('()=>window.__ASSET_VERSION')
                ck('%s: UI版==ローカルHEAD' % kind, av == asset_version, 'live=%s local=%s' % (av, asset_version))
                cur = pg.url
                ck('%s: URLが ?batch=%s に固定' % (kind, batch_id), ('batch=%s' % batch_id) in cur, cur[-80:])
                ck('%s: 画面にbatch idを表示' % kind, batch_id in pg.inner_text('#progress'), pg.inner_text('#progress')[:100])
                if shots_dir:
                    os.makedirs(shots_dir, exist_ok=True)
                    pg.screenshot(path=os.path.join(shots_dir, 'smoke_%s_%s_%s_top.png' % (kind, batch_id or 'none', view)))
                if chips:
                    pg.locator('a.chip[data-key]').first.click()
                    pg.wait_for_selector('#curbar:not([hidden])', timeout=60000)
                    pg.wait_for_timeout(800)
                    ck('%s: 個別ページ(?set=)にフレーズ/単語の独立コメント欄が可視' % kind, ('set=' in pg.url) and pg.is_visible('#commentPhrase') and pg.is_visible('#commentWord'))
                    ck('%s: 個別ページに上下のTopへ戻る(同batchのトップ)' % kind, pg.is_visible('#topBack1') and pg.locator('#topBack2').count() == 1 and ('batch=%s' % batch_id) in (pg.get_attribute('#topBack2', 'href') or '') and 'set=' not in (pg.get_attribute('#topBack2', 'href') or ''))
                    ck('%s: 個別ページに固定フッタ/一括コピーを出さない' % kind, not pg.is_visible('#fbar') and not pg.is_visible('#fCopy'))
            ck('%s: pageerror 0' % kind, not errs, errs[:2])
            if shots_dir and kind == 'none':
                os.makedirs(shots_dir, exist_ok=True)
                pg.screenshot(path=os.path.join(shots_dir, 'smoke_%s_%s_%s.png' % (kind, batch_id or 'none', view)))
            results[view] = checks
            ctx.close()
        br.close()
    return results


def smoke(base, kind, batch_id, n_members, form_dir, wait_sec=480, shots_dir=None):
    av = local_asset_version(form_dir)
    ok, diag, idx = poll_published(base, kind, batch_id, av, wait_sec)
    res = {'schema': SCHEMA, 'kind': kind, 'batch_id': batch_id, 'base_url': base, 'asset_version': av, 'n_members': n_members,
           'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'published_diag': diag, 'views': {}}
    if not ok:
        res['status'] = 'FAIL'
        res['fail_reason'] = diag.get('cause', 'unpublished')
        return res
    res['views'] = run_views(base, kind, batch_id, n_members, av, shots_dir)
    allok = all(c['ok'] for v in res['views'].values() for c in v)
    res['status'] = 'PASS' if allok else 'FAIL'
    if not allok:
        res['fail_reason'] = '; '.join('%s:%s' % (vn, c['name']) for vn, v in res['views'].items() for c in v if not c['ok'])[:400]
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kind', choices=['batch', 'latest', 'none'], required=True)
    ap.add_argument('--id', default='')
    ap.add_argument('--members', type=int, default=0, help='期待セット数')
    ap.add_argument('--base', default=BASE_DEFAULT)
    ap.add_argument('--form-dir', default=os.path.join(HERE, '..', 'user_test', 'selection_form_v3'))
    ap.add_argument('--wait-sec', type=int, default=480)
    ap.add_argument('--shots', default='')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.kind in ('batch', 'latest') and not a.id:
        ap.error('--id required')
    res = smoke(a.base, a.kind, a.id, a.members, a.form_dir, a.wait_sec, a.shots or None)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(res['status'], res.get('fail_reason', ''))
    return 0 if res['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
