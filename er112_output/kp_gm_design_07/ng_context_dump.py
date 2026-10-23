# -*- coding: utf-8 -*-
"""委任_21 API 0: NG-KPの本文文脈(前後文)と全arm/rep出力をローカルデータだけで一覧化する。"""
import json, re, sys
sys.path.insert(0, '.')
import er112_kp_gm_trial_04 as X
A = X.all_kps()
KPS = sys.argv[1:] or ["draw a line", "an unseen clock", "question shaped like a trophy", "greener grass", "take the wheel"]
def ctx(kp):
    art = kp['article']; sent = kp['sent']
    i = art.find(sent[:40])
    return art[max(0, i-260): i+len(sent)+420] if i >= 0 else '(sentence not found)'
res = {}
for t in ('02', '03', '04'):
    for l in open(f'er112_output/kp_gm_trial_{t}/results.jsonl', encoding='utf-8'):
        if l.strip():
            try: r = json.loads(l)
            except ValueError: continue
            if "key" not in r or "arm" not in r: continue
            res.setdefault(r['key'], []).append((t, r["arm"], r.get("rep"), r.get('gloss')))
for k in KPS:
    kp = A[k]
    print('='*70); print(k, '| display:', kp['display'], '| fam', kp['family'], '| tier', kp['tier'], '| run', kp['run'].split('/')[-2:])
    print('SENT:', kp['sent'])
    print('CTX :', ctx(kp).replace('\n', ' / '))
    for t, a, rp, g in res.get(k, []):
        print(f'   T{t} {a} rep{rp}: {g}')
