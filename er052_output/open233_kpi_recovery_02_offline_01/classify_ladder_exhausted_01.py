import json,re,difflib,sys
sys.stdout.reconfigure(encoding='utf-8')
paths="""er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/safety_A4.json
er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/safety_A5.json
er052_output/open233_self_recovery_flow_runner_01_iter8/instances_s1/safety_er009_unsupported_new_claim.json
er052_output/open233_self_recovery_flow_runner_01_rep14/instances/safety_A4.json
er052_output/open233_self_recovery_flow_runner_01_rep16/instances_s1/neg3_hormuz_prodrunner_b1b.json
er052_output/open233_self_recovery_flow_runner_01_rep18/instances_s1/safety_A2A3.json
er052_output/open233_self_recovery_flow_runner_01_rep18/instances_s2/safety_A2A3.json
er052_output/open233_self_recovery_flow_runner_01_rep20/instances_s2/meta_run03_standard.json
er052_output/open233_self_recovery_flow_runner_01_rep27/instances_s1/safety_A4.json
er052_output/open233_self_recovery_flow_runner_01_rep27/instances_s1/safety_A5.json""".split()
def norm(s):
    s=re.sub(r'[“”"‘’\u201c\u201d]','',s or ''); return re.sub(r'\s+',' ',s).strip().lower()
out=[]
for p in paths:
    d=json.load(open(p,encoding='utf-8'))
    c=d['cycles'][-1]
    blk=[s for s in c['stage2_results'] if s.get('materiality')=='BLOCKING']
    rws=c['rewrite_records']
    ex=[i for i,r in enumerate(rws) if r.get('ladder_exhausted_without_full_rewrite')]
    rows=[]
    for i in ex:
        if i>=len(blk): rows.append((i,'index_out_of_range')); continue
        t=norm(blk[i].get('claim_text'))
        dup=[]
        for j,b in enumerate(blk):
            if j==i: continue
            u=norm(b.get('claim_text'))
            if not u or not t: continue
            r=difflib.SequenceMatcher(None,t,u).ratio()
            if u in t or t in u or r>=0.8:
                dup.append((j, round(r,2), 'rewritten_ok' if (j<len(rws) and rws[j].get('guard_ok')) else 'not_ok', 'earlier' if j<i else 'later'))
        rows.append((i,blk[i].get('related_fact_id') or (blk[i].get('dev') or {}).get('related_fact_id'),t[:70],dup))
    out.append((p,c['cycle'],len(blk),rows))
    print(p.split('/')[1].replace('open233_self_recovery_flow_runner_01_',''),p.split('/')[-1],'cycle',c['cycle'],'blocking',len(blk))
    for r in rows: print('   ',r)
print('------ methods')
for p in paths:
    d=json.load(open(p,encoding='utf-8'))
    c=d['cycles'][-1]
    sw=d.get('switches')
    print(p.split('/')[1].replace('open233_self_recovery_flow_runner_01_',''),p.split('/')[-1],'switches',sw)
    for i,r in enumerate(c['rewrite_records']):
        if r.get('ladder_exhausted_without_full_rewrite'):
            print('   ',i,r.get('mechanism'),r.get('method'),r.get('section_type'), 'handoff:',json.dumps((r.get('handoff') or {}).get('resolution'),ensure_ascii=False)[:200])
