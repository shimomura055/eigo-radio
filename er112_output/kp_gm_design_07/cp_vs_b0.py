# -*- coding: utf-8 -*-
"""委任_21 API 0: Trial_04のCp(同一call自己監査欄つき生成)を『生成方式』として再評価。B0 rep1との文字列差(churn)とFable確定ラベルの対応を既存データだけで集計。"""
import json, collections, sys
sys.path.insert(0, '.')
import er112_kp_gm_trial_04_gen as G
key = json.load(open('er112_output/kp_gm_trial_04/fable_blind_04_key.json', encoding='utf-8'))
L = json.load(open('docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/TRIAL_04/fable_labels_04.json', encoding='utf-8'))
S = json.load(open('docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/TRIAL_04/strata_04.json', encoding='utf-8'))
cell = {}
for n, v in key.items():
    for col, c in v['cols'].items():
        for ce in c['cells']:
            cell[(v['key'], ce)] = (c['gloss'], L.get(f'{n}:{col}', 'PASS'))
F = set(S['F_layer'])
rows = []
for k in S['trial_set']:
    b = cell.get((k, 'B0/rep1')) or cell.get((k, 'B0/rep2'))
    cp = cell.get((k, 'Cp/rep1'))
    if b and cp:
        rows.append((k, k in F, b, cp))
ch = [r for r in rows if r[2][0] != r[3][0]]
print('KP with B0 and Cp', len(rows), 'string changed', len(ch))
tr = collections.Counter((r[2][1], r[3][1]) for r in rows)
print('label transition B0->Cp (all)', dict(tr))
for r in rows:
    if r[2][1] != 'PASS' or r[3][1] != 'PASS':
        print(' ', r[0], '| B0', r[2], '| Cp', r[3])
