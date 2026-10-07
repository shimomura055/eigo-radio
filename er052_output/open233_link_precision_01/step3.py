# -*- coding: utf-8 -*-
"""T3 作業3(API無し): 「未提示→不在断定」規則R(事前登録4節)を既知否定型NGに当てる。使い方: step3.py SUMMARY.json OUTNAME TARGETS_MODULE"""
import sys, json, importlib
sys.path.insert(0, 'er052_output/open233_link_precision_01')
import units_lib as U
OUT = U.OUT
summ = json.load(open(OUT / sys.argv[1], encoding='utf-8'))
T = importlib.import_module(sys.argv[3]).STEP3_TARGETS  # [(item, run_substring, unit_id)]
fl = {(f['run'], f['unit']): f for f in summ['flagged']}
outs = {}
import glob, pathlib
for f in glob.glob(str(OUT / 'r3' / '*' / '*.json')):
    d = json.loads(pathlib.Path(f).read_text(encoding='utf-8'))
    if d['rep'] == 1:
        outs[d['run']] = d
rows = []
for it, sub, uid in T:
    runs = [r for r in outs if sub in r.replace(chr(92), '/')]
    assert len(runs) == 1, (it, sub, runs)
    r = runs[0]
    d = outs[r]
    f = fl.get((r, uid))
    rows.append({"item": it, "run": r, "unit": uid, "verdict": (d['model_verdict'] or {}).get(uid), "support": (d['support_fact_ids'] or {}).get(uid),
                 "R1": bool(f and f['R1']), "R2": bool(f and f['R2']), "shared": f['shared'] if f else None})
n = len(rows)
res = {"targets": rows, "n_targets": n, "R1_hits": sum(x['R1'] for x in rows), "R2_hits": sum(x['R2'] for x in rows),
       "load": {k: v for k, v in summ['rule_R'].items() if k != 'per_article'}}
(OUT / f'{sys.argv[2]}.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
for x in rows:
    print(x['item'], x['unit'], x['verdict'], x['support'], 'R1', x['R1'], 'R2', x['R2'], x['shared'])
print('R1', res['R1_hits'], '/', n, 'R2', res['R2_hits'], '/', n)
print(json.dumps(res['load'], ensure_ascii=False))
pa = summ['rule_R']['per_article']
import statistics
for k in ('R1', 'R2'):
    v = [a[k] for a in pa.values()]
    print(k, 'per-article flags mean/median/max', round(statistics.mean(v), 2), statistics.median(v), max(v), 'frac_of_judged', round(sum(v) / max(1, sum(a['n_judged'] for a in pa.values())), 4))
