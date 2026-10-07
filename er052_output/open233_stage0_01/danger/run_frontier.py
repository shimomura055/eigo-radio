# -*- coding: utf-8 -*-
"""規則部分集合(2^7)を全探索し、負荷と検出率(重大+軽微、auto/oracle)のフロンティアを求める。coverage.jsonへ追記。"""
import json, os, itertools, sys
OUT = os.path.dirname(os.path.abspath(__file__))
RULES = ['NEG', 'UNIV', 'CAUSE', 'NUM', 'LIMIT_HEDGE', 'LIMIT_SCOPE', 'SUBJ']
rows = [json.loads(l) for l in open(OUT + '/sentence_flags.jsonl', encoding='utf8')]
items = json.load(open(OUT + '/ng_detail.json', encoding='utf8'))
sel = []
for it in items:
    if it['src'] == 'past8' or it['sev'] == 'major_human' or (it['src'] == 'ng' and it['sev'] == 'minor'):
        if it['m'] and not it['r0_only']:
            sel.append(it)
N = len(rows)
res = []
for k in range(1, 8):
    for sub in itertools.combinations(RULES, k):
        load = sum(any(r in x['fired'] for r in sub) for x in rows) / N
        load_lax = sum(any(r in x['fired_lax'] for r in sub) for x in rows) / N
        dl = sum(any(any(r in m['lax'] for r in sub) for m in it['m'].values()) for it in sel) / len(sel)
        da = sum(any(any(r in m['auto'] for r in sub) for m in it['m'].values()) for it in sel) / len(sel)
        do = sum(any(any(r in m['oracle'] for r in sub) for m in it['m'].values()) for it in sel) / len(sel)
        res.append(dict(rules='+'.join(sub), load=load, det_auto=da, det_oracle=do, load_lax=load_lax, det_lax=dl))
res.sort(key=lambda x: x['load'])
# ロード<=40% で最大検出
ok = [r for r in res if r['load'] <= 0.40]
best_auto = sorted(ok, key=lambda x: -x['det_auto'])[:5]
best_or = sorted(ok, key=lambda x: -x['det_oracle'])[:5]
ok50 = [r for r in res if r['load'] <= 0.50]
best50 = sorted(ok50, key=lambda x: -x['det_auto'])[:3]
# 成立ライン(検出>=80% & 負荷<=40%)
passing_lax = [r for r in res if r['load_lax'] <= 0.40 and r['det_lax'] >= 0.80]
best_lax = sorted([r for r in res if r['load_lax'] <= 0.40], key=lambda x: -x['det_lax'])[:5]
passing_auto = [r for r in res if r['load'] <= 0.40 and r['det_auto'] >= 0.80]
passing_or = [r for r in res if r['load'] <= 0.40 and r['det_oracle'] >= 0.80]
c = json.load(open(OUT + '/coverage.json', encoding='utf8'))
c['frontier'] = dict(n_items=len(sel), best_auto_load_le_40=best_auto, best_oracle_load_le_40=best_or, best_auto_load_le_50=best50,
                     passing_auto=passing_auto, passing_lax=passing_lax, best_lax_load_le_40=best_lax, passing_oracle=passing_or, all_subsets=res)
json.dump(c, open(OUT + '/coverage.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
for name, lst in (('best_auto<=40', best_auto), ('best_oracle<=40', best_or), ('best_auto<=50', best50)):
    print(name)
    for r in lst:
        print('  ', r['rules'], round(r['load'], 3), round(r['det_auto'], 3), round(r['det_oracle'], 3))
print('best_lax'); [print('  ', r['rules'], round(r['load_lax'],3), round(r['det_lax'],3)) for r in best_lax]
print('passing_lax', len(passing_lax))
print('passing_auto', len(passing_auto), 'passing_oracle', len(passing_or))
