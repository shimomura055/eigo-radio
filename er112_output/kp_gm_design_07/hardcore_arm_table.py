# -*- coding: utf-8 -*-
"""委任_21 API 0: hard-core 4KP(draw a line / an unseen clock / question shaped like a trophy / greener grass)の字義訳出力を全arm・全Trialで集計(Fable確定ラベルの字義文字列で判定)。"""
import json, re, collections
LIT = {'draw a line': re.compile(r'^(はっきりと)?線を引く$'),
       'an unseen clock': re.compile(r'^(目に)?見えない時計$'),
       'question shaped like a trophy': re.compile(r'^トロフィーの形をした'),
       'greener grass': re.compile(r'(もっと|より)青々とした芝生')}
tab = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
rows = collections.defaultdict(list)
for t in ('02', '03', '04'):
    for l in open(f'er112_output/kp_gm_trial_{t}/results.jsonl', encoding='utf-8'):
        try: r = json.loads(l)
        except ValueError: continue
        k = r.get('key')
        if k in LIT and r.get('gloss') and r.get('kind') == 'G':
            arm = r['arm'] if t != '04' else r['arm']
            is_lit = bool(LIT[k].search(r['gloss']))
            tab[(arm)][k][1] += 1; tab[arm][k][0] += is_lit
for arm in sorted(tab):
    tot = [sum(v[0] for v in tab[arm].values()), sum(v[1] for v in tab[arm].values())]
    print(f'{arm:6s}', ' | '.join(f'{k.split()[1] if k!="question shaped like a trophy" else "trophy"}:{v[0]}/{v[1]}' for k, v in tab[arm].items()), f'|| total {tot[0]}/{tot[1]}')
