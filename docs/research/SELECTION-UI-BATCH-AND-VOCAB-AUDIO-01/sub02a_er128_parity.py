# -*- coding: utf-8 -*-
"""委任_02A: 一括コピーの各SETブロックが、既存er128.restore(無変更)で復元・照合できることを確認(受入互換の実証。er128は読取のみ)。"""
import os, re, sys, hashlib, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT)
import er128_form_readable_restore_01 as er
DD = os.path.join(ROOT, 'user_test', 'selection_form_v3', 'test_fixtures', 'data')
tot = 0
for f in sorted(glob.glob(os.path.join(HERE, 'sub02a_batch_sample_*.txt'))):
    t = open(f, encoding='utf-8').read()
    blocks = re.split(r'^════ SET \d+/\d+ ｜ \S+ ════\n', t, flags=re.M)[1:]
    blocks = [re.split(r'\n════ (?:SET|END) ', b)[0] for b in blocks]
    codes = []
    for b in blocks:
        p, notes = er.restore(b, DD)
        codes.append(re.search(r'AIF1-\S+', b.split('照合コード')[-1]).group(0)); tot += 1
        assert p, 'empty payload'
    end = re.search(r'^════ END 合計(\d+)件 / (BATCH1-\d+-[0-9a-f]{10}) ════$', t, re.M)
    exp = 'BATCH1-%d-%s' % (len(codes), hashlib.sha256(''.join(codes).encode('utf-8')).hexdigest()[:10])
    print(os.path.basename(f), 'sets', len(blocks), 'restore OK; END code', 'match' if end.group(2) == exp else 'MISMATCH', end.group(2))
    assert end.group(2) == exp and int(end.group(1)) == len(blocks)
print('TOTAL SET blocks restored by unchanged er128.restore:', tot)
