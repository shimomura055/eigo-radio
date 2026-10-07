# -*- coding: utf-8 -*-
"""T4 集計(API無し)。使い方: analyze.py dev|heldout"""
import json, sys, glob, collections, pathlib
D = pathlib.Path('er052_output/open233_pairwise_judge_01'); which = sys.argv[1]
items = json.load(open(D / f'items_{which}.json', encoding='utf-8'))['items']
ng = [i for i in items if i['group'] == 'ng']; ct = [i for i in items if i['group'] == 'control']
def load(c):
    r = {}
    for f in sorted(glob.glob(str(D / f'out/{which}/{c}_rep*.json'))):
        d = json.load(open(f, encoding='utf-8')); r[d['rep']] = d['results']
    return r
R = {c: load(c) for c in 'AB'}
def v(c, rep, i): return (R[c].get(rep, {}).get(i['id']) or {}).get('verdict')
def flag(x): return x is not None and x != 'consistent'
S = {"n_ng": len(ng), "n_ctrl": len(ct)}
for c in 'AB':
    if 1 not in R[c]: continue
    det = [i for i in ng if flag(v(c, 1, i))]; fp = [i for i in ct if flag(v(c, 1, i))]
    s = {"detect_rep1": [len(det), len(ng)], "false_pos_rep1": [len(fp), len(ct)],
         "verdict_counts_ng": dict(collections.Counter(v(c, 1, i) for i in ng)), "verdict_counts_ctrl": dict(collections.Counter(v(c, 1, i) for i in ct)),
         "unclear_rep1": sum(1 for i in items if v(c, 1, i) == 'unclear'),
         "detect_by_type": {}, "missed_ng": [i['id'] for i in ng if not flag(v(c, 1, i))], "fp_ctrl": [i['id'] for i in fp],
         "severe": {i['id']: v(c, 1, i) for i in ng if 'major' in str(i.get('severity'))}}
    for t in sorted({i['type'] for i in ng}):
        g = [i for i in ng if i['type'] == t]; s["detect_by_type"][t] = [sum(flag(v(c, 1, i)) for i in g), len(g)]
    reps = sorted(R[c])
    ids = [i for i in items if all(i['id'] in R[c][r] for r in reps)]
    if len(reps) >= 3:
        full = [i for i in items if all(i['id'] in R[c].get(r, {}) for r in (1, 2, 3))]
        s["stability"] = {"n_items": len(full), "same_verdict_3of3": sum(len({v(c, r, i) for r in (1, 2, 3)}) == 1 for i in full),
                          "same_flag_3of3": sum(len({flag(v(c, r, i)) for r in (1, 2, 3)}) == 1 for i in full)}
        ngf = [i for i in full if i['group'] == 'ng']; ctf = [i for i in full if i['group'] == 'control']
        s["majority"] = {"detect": [sum(sum(flag(v(c, r, i)) for r in (1, 2, 3)) >= 2 for i in ngf), len(ngf)],
                         "false_pos": [sum(sum(flag(v(c, r, i)) for r in (1, 2, 3)) >= 2 for i in ctf), len(ctf)],
                         "any_detect": [sum(any(flag(v(c, r, i)) for r in (1, 2, 3)) for i in ngf), len(ngf)]}
    S[c] = s
# 現行r3(参考): verdictはSUPPORTED以外=検出
r3d = [i for i in ng if any(x != 'SUPPORTED' for x in i['r3_verdict'])]
S['r3_current'] = {"detect": [len(r3d), len(ng)], "false_pos": [sum(any(x != 'SUPPORTED' for x in i['r3_verdict']) for i in ct), len(ct)],
                   "ng_r3_verdicts": dict(collections.Counter("+".join(map(str,i["r3_verdict"])) for i in ng)), "note": "対照はr3 SUPPORTEDで選んだため誤検出0は構成上自明"}
cost = sum(json.loads(l)['cost_jpy'] for l in open(D / 'out/cost_log.jsonl', encoding='utf-8'))
S['cost_total_jpy_all'] = round(cost, 3)
json.dump(S, open(D / f'summary_{which}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
