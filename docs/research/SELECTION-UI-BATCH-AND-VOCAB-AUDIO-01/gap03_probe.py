# -*- coding: utf-8 -*-
"""委任_03: 公開フォームv3の実操作調査(読み取りのみ・公開物は変更しない・API 0)。出力: gap03_result.json / gap03_shots/*.png"""
import json, os, sys
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright_noplay as sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, 'gap03_shots'); os.makedirs(SH, exist_ok=True)
BASE = 'https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html'
R = {}
def run(view):
    kw = dict(viewport={'width': 1280, 'height': 900}) if view == 'pc' else dict(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(**kw); ctx.on('dialog', lambda d: d.accept())
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE, wait_until='networkidle'); pg.wait_for_timeout(1500)
        o = {}
        o['title'] = pg.title()
        o['subtitle'] = pg.inner_text('#subtitle')
        o['n_options'] = pg.eval_on_selector_all('#article option', 'e=>e.length')
        o['options_head'] = pg.eval_on_selector_all('#article option', 'e=>e.slice(0,40).map(x=>x.textContent)')
        o['option_names_unique'] = len(set(pg.eval_on_selector_all('#article option', r'e=>e.map(x=>x.textContent.replace(/^[0-9]+[.] /,"").split("|")[0])')))
        for sid in ['batchTop','batchBox','selWrap','boxPhrase','boxWord','doneBox','send','copy','copyTech','restRow','selRest','resetBox','goNext','progress','list']:
            try:
                o['vis_'+sid] = pg.is_visible('#'+sid)
            except Exception as e:
                o['vis_'+sid] = 'ERR'
        o['has_batchCopy_el'] = pg.locator('#batchCopy').count()
        o['js_BS'] = pg.evaluate('typeof BS!=="undefined"?String(BS):"undef"')
        o['js_idx_has_batch'] = pg.evaluate('!!(IDX&&IDX.batch)')
        o['url_batch_param_supported'] = pg.evaluate('document.documentElement.outerHTML.indexOf("get(\'batch\')")>=0')
        o['pageerrors'] = errs
        pg.screenshot(path=os.path.join(SH, f'live_{view}_top.png'), full_page=False)
        pg.screenshot(path=os.path.join(SH, f'live_{view}_full.png'), full_page=True)
        # 候補のある実記事(先頭)で select + comment 実操作
        try:
            o['cand_items'] = pg.locator('#candPhrase .cand, #candPhrase [class*=cand], #candPhrase .item').count()
            o['text_len_form'] = len(pg.inner_text('main'))
        except Exception as e:
            o['cand_err'] = str(e)
        # コピー: 選定結果をコピーの対象 (単体)
        o['copy_btn_text'] = pg.inner_text('#copy')
        o['commentPhrase_visible'] = pg.is_visible('#commentPhrase')
        o['commentWord_visible'] = pg.is_visible('#commentWord')
        o['doneBtn_visible'] = pg.is_visible('#doneBtn')
        o['sendHelp_visible'] = pg.is_visible('#sendHelp')
        # 記事切替保持テスト: 先頭記事で自由コメント入力→別記事→戻る
        pg.fill('#comment', 'GAP03-KEEP-1')
        n = o['n_options']
        pg.select_option('#article', index=2); pg.wait_for_timeout(600)
        v2 = pg.input_value('#comment')
        pg.select_option('#article', index=0); pg.wait_for_timeout(600)
        o['keep_after_switch'] = pg.input_value('#comment')
        o['comment_on_other_article'] = v2
        pg.fill('#comment', '')
        # 単体コピーの内容サンプル
        try:
            ctx.grant_permissions(['clipboard-read','clipboard-write'], origin='https://shimomura055.github.io')
            pg.click('#copy'); pg.wait_for_timeout(800)
            o['copy_sample'] = pg.evaluate('navigator.clipboard.readText()')[:1500]
        except Exception as e:
            o['copy_sample'] = 'ERR '+str(e)[:200]
            o['fallback_text'] = (pg.input_value('#fallback') if pg.is_visible('#fallback') else '')[:1500]
        o['status_text'] = pg.inner_text('#status')
        R[view] = o
        br.close()
for v in ('pc','mobile'): run(v)
json.dump(R, open(os.path.join(HERE,'gap03_result.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1)[:6000])
