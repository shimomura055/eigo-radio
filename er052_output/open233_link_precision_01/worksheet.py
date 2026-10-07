# -*- coding: utf-8 -*-
import sys, re, json
sys.path.insert(0, 'er052_output/open233_link_precision_01')
import units_lib as U
kind = sys.argv[1]
ng = {}
for l in open('er052_output/open233_stage0_01/reclass/known_relation_ng.jsonl', encoding='utf-8'):
    j = json.loads(l); ng[j['item_id']] = j
def words(s): return set(re.findall(r"[A-Za-z][A-Za-z\-']{2,}|\d[\d,\.]*", s.lower()))
for run, its in U.article_runs(kind).items():
    r, led, art = U.RL.load_run(run)
    sp = U.split(art)
    print('=' * 100); print(run, len(sp['units']), 'units')
    for it in its:
        n = ng[it['item_id']]
        t = n['text']
        m = re.findall(r'EN:\s*([^)]*)', t)
        q = ' '.join(m) if m else ''
        key = words(q) | words(it.get('matched_claim') or '')
        sc = sorted(((len(words(u['text']) & key), u['id'], u['text'][:110]) for u in sp['units']), reverse=True)[:3]
        print('--', it['item_id'], it['status'], 'fact', n['fact_id'], n['sentence_type'], '|', t[:200].replace('\n', ' '))
        print('   reason:', (n.get('reason') or '')[:160].replace('\n', ' '))
        for s in sc: print('   cand', s)
