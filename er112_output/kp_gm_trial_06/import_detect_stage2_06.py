# -*- coding: utf-8 -*-
"""委任_30(F/E): Stage 2 54KP の B0(Trial_04 2rep) と X2p(Trial_05) に record-only 持ち込み検出(detect_import)を適用して件数を数える(API 0)。"""
import sys, json, collections
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import er112_kp_gm_trial_06 as T6
import er112_kp_gm_trial_05 as T5
import er112_kp_gm_trial_05_report as R5
st = json.load(open(T5.RD / 'TRIAL_04/strata_04.json', encoding='utf-8'))
s2 = [k for k in st['trial_set'] if k not in T5.R_KEYS]
A = T5.all_kps5()
rc = R5.ref_cells(set(s2))
nc = R5.new_cells()
res = {'B0': collections.Counter(), 'X2p': collections.Counter()}
ex = {'B0': [], 'X2p': []}
n = {'B0': 0, 'X2p': 0}
for k in s2:
    for (arm, kk, rep), g in rc.items():
        if arm == 'B0_t4' and kk == k:
            n['B0'] += 1
            f = T6.detect_import(A[k]['key'], g)
            for x in f: res['B0'][x] += 1
            if f: ex['B0'].append((k, g, f))
    r = nc.get(('X2p', k, 1))
    if r:
        n['X2p'] += 1
        f = T6.detect_import(A[k]['key'], r['gloss'])
        for x in f: res['X2p'][x] += 1
        if f: ex['X2p'].append((k, r['gloss'], f))
print('B0 outputs', n['B0'], dict(res['B0']), '| X2p outputs', n['X2p'], dict(res['X2p']))
for arm in ex:
    print(arm)
    for e in ex[arm]: print('  ', e)
json.dump({'n': n, 'counts': {a: dict(c) for a, c in res.items()}, 'examples': ex}, open('er112_output/kp_gm_trial_06/import_detect_stage2_06.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
