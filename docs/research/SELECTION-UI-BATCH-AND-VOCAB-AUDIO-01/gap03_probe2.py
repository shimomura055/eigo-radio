# -*- coding: utf-8 -*-
"""委任_03: 公開フォーム 切替保持・選定操作の実操作調査(読み取りのみ)。"""
import json, os
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright_noplay as sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout
HERE = os.path.dirname(os.path.abspath(__file__)); SH = os.path.join(HERE, 'gap03_shots')
BASE = 'https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html'
R = {}
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width':1280,'height':900}); pg = ctx.new_page()
    pg.goto(BASE, wait_until='networkidle'); pg.wait_for_timeout(1500)
    R['entry0'] = pg.evaluate('keyOf(entry)')
    pg.fill('#comment', 'GAP03-KEEP-1'); pg.wait_for_timeout(300)
    R['ls_after_fill'] = pg.evaluate('localStorage.getItem(STORE_KEY)')
    pg.select_option('#article', index=2); pg.wait_for_timeout(1200)
    R['entry_after_switch'] = pg.evaluate('keyOf(entry)')
    R['comment_other'] = pg.input_value('#comment')
    pg.select_option('#article', index=0); pg.wait_for_timeout(1200)
    R['entry_back'] = pg.evaluate('keyOf(entry)')
    R['keep_after_back'] = pg.input_value('#comment')
    # 候補の選択操作: 先頭記事で①を何件選べるか
    R['cand_html_sample'] = pg.inner_html('#candPhrase')[:800]
    R['stats'] = pg.inner_text('#stats')
    R['khint'] = pg.inner_text('#khint')[:400]
    R['kpWarn'] = pg.inner_text('#kpWarn')
    pg.screenshot(path=os.path.join(SH,'live_pc_classic_after.png'), full_page=True)
    # 先頭の10記事目などlevelの違いをデータ有無で
    R['options_with_data'] = pg.evaluate('IDX.articles.map(a=>[a.slug,a.level,!!a.data])')
    br.close()
json.dump(R, open(os.path.join(HERE,'gap03_result2.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
for k,v in R.items():
    if k not in ('options_with_data',): print(k, json.dumps(v, ensure_ascii=False)[:400].encode('utf-8','replace').decode('utf-8','replace') if False else '(saved)')
