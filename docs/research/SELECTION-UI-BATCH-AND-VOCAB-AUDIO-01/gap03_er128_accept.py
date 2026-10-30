# -*- coding: utf-8 -*-
"""委任_03: 公開データ+注入batchで取得した一括コピー(PC/mobile)が er128.restore_batch で全件受入できるか(読取のみ・API 0)。"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT)
import er128_form_readable_restore_01 as er
D = os.path.join(ROOT, 'user_test', 'selection_form_v3', 'data')
doc = json.load(open(os.path.join(D, 'articles.json'), encoding='utf-8-sig'))
for view in ('pc', 'mobile'):
    t = open(os.path.join(HERE, f'gap03_batch_copy_{view}.txt'), encoding='utf-8').read()
    import re
    members = re.findall(r'^════ SET \d+/\d+ ｜ (\S+) ════', t, re.M)
    d2 = dict(doc); d2['batch'] = {'id': 'GAP03-INJECT', 'generated': '2026-10-30', 'members': members}
    tmp = os.path.join(D, '_gap03_tmp_articles.json')
    json.dump(d2, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    try:
        out = er.restore_batch(t, articles_json=tmp, data_dir=D, git_lookup=None)
        p = out[0] if isinstance(out, tuple) else out
        print(view, 'restore_batch OK sets=', len(p), 'comment sample:', json.dumps(p[0].get('m8') if isinstance(p[0], dict) else str(p[0])[:200], ensure_ascii=False)[:200])
    except Exception as e:
        print(view, 'restore_batch FAIL', type(e).__name__, str(e)[:800])
    finally:
        os.remove(tmp)
