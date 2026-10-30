# -*- coding: utf-8 -*-
"""委任_02A: フォームの一括コピー出力(sub02a_batch_sample_*.txt)が、02Bの restore_batch(er128、無変更・読取のみ)で全件受入できることの確認。
使い方: python sub02a_er128_batch_accept.py  (er128は作業ツリーのものを使う。02Bが未統合の作業ツリーでは SKIP と表示)"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT)
import er128_form_readable_restore_01 as er
if not hasattr(er, 'restore_batch'):
    print('SKIP: er128.restore_batch not in this working tree'); sys.exit(0)
FIX = os.path.join(ROOT, 'user_test', 'selection_form_v3', 'test_fixtures')
n_ok = 0
for n in (1, 4, 9, 10):
    t = open(os.path.join(HERE, f'sub02a_batch_sample_{n}articles.txt'), encoding='utf-8').read()
    out = er.restore_batch(t, articles_json=os.path.join(FIX, f'articles_b{n}.json'), data_dir=os.path.join(FIX, 'data'), git_lookup=None)
    payloads = out[0] if isinstance(out, tuple) else out
    print(f'batch {n} articles: restore_batch OK, sets={len(payloads)}'); assert len(payloads) == 2 * n; n_ok += len(payloads)
print('TOTAL sets accepted by 02B restore_batch:', n_ok)
