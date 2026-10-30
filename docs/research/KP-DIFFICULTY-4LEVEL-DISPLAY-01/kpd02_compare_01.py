# -*- coding: utf-8 -*-
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(HERE, 'kpd02_out')
R = json.load(open(os.path.join(O, 'kpd02_llm_results.json'), encoding='utf-8'))
S = json.load(open(os.path.join(O, 'kpd02_sonnet_labels.json'), encoding='utf-8'))
B = json.load(open(os.path.join(O, 'kpd02_candidates_blind.json'), encoding='utf-8'))
expr = {(r['set'], r['candidate_id']): r['expr'] for r in B}
ORD = {'easy': 0, 'medium': 1, 'hard': 2, 'rare': 3}
rows = []
for s, m in S.items():
    for cid, sl in m.items():
        l = R['luna'][s][cid]['level']; g = R['gemini'][s][cid]['level']
        rows.append((s, cid, expr[(s, cid)], sl, l, g))
def gap(a, b): return abs(ORD[a] - ORD[b])
pairs = {'luna-sonnet': lambda r: gap(r[4], r[3]), 'gemini-sonnet': lambda r: gap(r[5], r[3]), 'luna-gemini': lambda r: gap(r[4], r[5])}
out = {'n': len(rows), 'pairs': {}, 'dist': {}, 'ge2_examples': []}
for k, f in pairs.items():
    c = collections.Counter(f(r) for r in rows)
    out['pairs'][k] = {'exact': c[0], 'adjacent(1)': c[1], 'gap>=2': sum(v for g, v in c.items() if g >= 2)}
for nm, i in (('sonnet', 3), ('luna', 4), ('gemini', 5)):
    out['dist'][nm] = dict(collections.Counter(r[i] for r in rows))
for r in rows:
    mx = max(gap(r[4], r[3]), gap(r[5], r[3]), gap(r[4], r[5]))
    if mx >= 2:
        out['ge2_examples'].append({'set': r[0], 'expr': r[2], 'sonnet': r[3], 'luna': r[4], 'gemini': r[5]})
out['three_way_all_within1'] = sum(1 for r in rows if max(gap(r[4], r[3]), gap(r[5], r[3]), gap(r[4], r[5])) <= 1)
out['three_way_exact'] = sum(1 for r in rows if r[3] == r[4] == r[5])
# 同一表現のStd/Adv割れ
by = collections.defaultdict(dict)
for r in rows:
    by[r[2].lower()][r[0]] = r[4]
out['same_expr_std_adv'] = {e: v for e, v in by.items() if len(v) > 1}
out['same_expr_gap'] = {e: max(ORD[x] for x in v.values()) - min(ORD[x] for x in v.values()) for e, v in out['same_expr_std_adv'].items()}
ux = {}
for nm in ('UX-a2', 'UX-b1b'):
    ux[nm] = {expr_: {'luna': R['luna'][nm][cid]['level'], 'luna_reason': R['luna'][nm][cid]['reason_ja'], 'gemini': R['gemini'][nm][cid]['level']} for cid, expr_ in (('ux_rely', 'rely on'), ('ux_room', 'make room for'), ('ux_narrow', 'narrow down'))}
out['user_examples'] = ux
out['rows'] = [dict(zip(('set', 'cid', 'expr', 'sonnet', 'luna', 'gemini'), r)) for r in rows]
json.dump(out, open(os.path.join(O, 'kpd02_compare_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k in ('n', 'pairs', 'dist', 'three_way_all_within1', 'three_way_exact', 'ge2_examples', 'same_expr_gap', 'user_examples'):
    print(k, json.dumps(out[k], ensure_ascii=False))
for r in rows: print(r[0], r[2], r[3], r[4], r[5], sep='\t')
