# -*- coding: utf-8 -*-
"""委任_21 API 0: Trial_05の対象KP・call数(article単位、本番と同じ最大3KP/call相当)を、既存strata_04.jsonとall_kps()から決定論的に算出。"""
import json, sys, collections, hashlib
sys.path.insert(0, '.')
import er112_kp_gm_trial_04 as X
A = X.all_kps()
S = json.load(open('docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/TRIAL_04/strata_04.json', encoding='utf-8'))
R = ["draw a line", "an unseen clock", "question shaped like a trophy", "greener grass"]
trial_set = S['trial_set']
def art(k): return hashlib.sha256(A[k]['article'].encode('utf-8')).hexdigest()[:10]
def groups(keys):
    g = collections.OrderedDict()
    for k in keys: g.setdefault(art(k), []).append(k)
    return g
# Stage1: R-setを含む記事の、trial_set内KP全部(co-KP込み)
rart = {art(k) for k in R}
s1 = [k for k in trial_set if art(k) in rart]
g1 = groups(s1)
print('Stage1 articles', len(g1), 'KPs', len(s1), 'calls/rep', len(g1))
for a, ks in g1.items(): print('  ', a, ks)
# Stage2: trial_setのうちstage1に含まれないもの
s2 = [k for k in trial_set if k not in s1]
g2 = groups(s2)
print('Stage2 KPs', len(s2), 'articles(calls)', len(g2), 'F', sum(k in S['F_layer'] for k in s2), 'N', sum(k not in S['F_layer'] for k in s2))
print('trial_set', len(trial_set))
json.dump(dict(R=R, stage1_keys=s1, stage2_keys=s2, stage1_calls_per_rep=len(g1), stage2_calls=len(g2)), open('er112_output/kp_gm_design_07/trial05_plan_counts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
