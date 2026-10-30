# -*- coding: utf-8 -*-
"""held-out評価の集計。usage: py kpd04_eval_01.py  (kpd04_{luna1,luna2,gemini1,gemini2}_results.jsonのうち存在するもの)"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpd04_common_01 as k
O = k.OUT; ORD = k.ORD
S = json.load(open(os.path.join(O, 'kpd04_sonnet_labels.json'), encoding='utf-8'))
B = json.load(open(os.path.join(O, 'kpd04_candidates_blind.json'), encoding='utf-8'))
expr = {(r['set'], r['candidate_id']): r['expr'] for r in B}
def load(m):
    f = os.path.join(O, f'kpd04_{m}_results.json')
    return json.load(open(f, encoding='utf-8'))['results'] if os.path.exists(f) else None
out = {}
for m in ('luna1', 'luna3', 'gemini1', 'gemini3'):
    R = load(m)
    if not R: continue
    rows = [(s, cid, expr[(s, cid)], sl, R[s][cid]['level']) for s, mm in S.items() if s in R for cid, sl in mm.items()]
    gaps = [abs(ORD[r[3]] - ORD[r[4]]) for r in rows]
    c = collections.Counter(gaps)
    hs = [r for r in rows if r[3] in ('hard', 'rare')]
    hs_hit = [r for r in hs if r[4] in ('hard', 'rare')]
    by = collections.defaultdict(dict)
    for r in rows: by[r[2].lower()][r[0]] = r[4]
    same = {e: v for e, v in by.items() if len(v) > 1}
    sgap = {e: max(ORD[x] for x in v.values()) - min(ORD[x] for x in v.values()) for e, v in same.items()}
    ux = {}
    for nm in ('UX-a2', 'UX-b1b'):
        if nm in R:
            ux[nm] = {e: R[nm][cid]['level'] for cid, e in (('ux_rely', 'rely on'), ('ux_room', 'make room for'), ('ux_narrow', 'narrow down'))}
    exp = {'rely on': 'easy', 'make room for': 'medium', 'narrow down': 'hard'}
    ux_ok = {nm: all(abs(ORD[v[e]] - ORD[exp[e]]) <= 1 for e in exp) for nm, v in ux.items()}
    out[m] = {'n': len(rows), 'exact': c[0], 'adjacent': c[1], 'ge2': sum(v for g, v in c.items() if g >= 2),
              'adjacent_or_better_rate': round((c[0] + c[1]) / len(rows), 4), 'dist': dict(collections.Counter(r[4] for r in rows)),
              'sonnet_hard_rare_n': len(hs), 'llm_hard_rare_among_sonnet_hard_rare': len(hs_hit),
              'llm_hard_rare_total': sum(1 for r in rows if r[4] in ('hard', 'rare')),
              'ge2_examples': [{'set': r[0], 'expr': r[2], 'sonnet': r[3], 'llm': r[4]} for r in rows if abs(ORD[r[3]] - ORD[r[4]]) >= 2],
              'same_expr_gap': sgap, 'same_expr_levels': same, 'user_examples': ux, 'user_examples_all_adjacent': ux_ok}
    out[m]['rows'] = [dict(zip(('set', 'cid', 'expr', 'sonnet', 'llm'), r)) for r in rows]
json.dump(out, open(os.path.join(O, 'kpd04_eval_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
sd = collections.Counter(v for m in S.values() for v in m.values())
print('sonnet dist', dict(sd))
for m, v in out.items():
    print(m, {a: b for a, b in v.items() if a != 'rows'})
