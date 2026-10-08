import json,glob,os,re
R='er052_output/'
gens=[
 ('G01',R+'all6_writer_redesign_necessity_01/runs/meta/control/b1__all6__r2','b1b'),
 ('G02',R+'all6_writer_redesign_necessity_01/runs/meta/control/b2__all6__r2','b1b'),
 ('G03',R+'all6_writer_redesign_necessity_01/runs/meta/control/b3__all6__r1','b1b'),
 ('G04',R+'all6_writer_redesign_necessity_01/runs/meta/control/b3__all6__r2','b1b'),
 ('G05',R+'all6_writer_redesign_necessity_01/runs/space_weapons/control/b3__baseline__r1','a2'),
 ('G06',R+'factlock_writer_trial_01/runs/hormuz/control/b1__factlock__r2','b1b'),
 ('G07',R+'factlock_writer_trial_01/runs/meta/control/b1__factlock__r1','b1b'),
 ('G08',R+'factlock_writer_trial_01/runs/meta/control/b1__factlock__r2','b1b'),
 ('G09',R+'factlock_writer_trial_01/runs/meta/control/b4__factlock__r1','b1b'),
 ('G10',R+'factlock_writer_trial_01/sweep_01/runs/hormuz/control/b4__S2__r1','b1b'),
 ('G11',R+'factlock_writer_trial_01/sweep_01/runs/meta/control/b2__S11__r1','b1b'),
 ('G12',R+'factlock_writer_trial_01/sweep_01/runs/meta/control/b2__S3__r1','b1b'),
 ('G13',R+'factlock_writer_trial_01/sweep_01/runs/space_weapons/control/b3__S10__r1','b1b'),
 ('G14',R+'gpt6_wiring_e2e_01/run_01','b1b'),
]
def ledger_block(run,fid):
    f=run+'/research_ledger/verified_fact_ledger.txt'
    if not os.path.exists(f): return None
    t=open(f,encoding='utf-8').read()
    m=re.search(r'\[[A-Z]+\] '+re.escape(fid)+r':.*?(?=\n\[[A-Z]+\] |\Z)',t,re.S)
    return m.group(0).strip() if m else None
out=[]
for g,run,sub in gens:
    ad=run+'/'+sub+'/audit'
    rec={'gen':g,'run':run,'attempts':[]}
    fs=sorted(glob.glob(ad+'/deviation_checks/*attempt*.json'))+[ad+'/deviation_check.json']
    for f in fs:
        if not os.path.exists(f): continue
        d=json.load(open(f,encoding='utf-8')); p=d.get('parsed',d)
        devs=[x for x in p.get('deviations',[]) if x.get('origin')=='translation' and x.get('severity')=='MAJOR']
        rec['attempts'].append({'file':f,'status':p.get('overall_status'),'devs':[{k:x.get(k) for k in ('claim_in_article','issue','explanation','related_fact_id','severity')}|{'flags':[k for k in x if (k.startswith('changed_') or k=='unsupported_new_claim') and x.get(k)]} for x in devs]})
    fids={x['related_fact_id'] for a in rec['attempts'] for x in a['devs']}
    rec['ledger']={fid:ledger_block(run,fid) for fid in fids if fid}
    art=run+'/'+sub+'/article.md'
    rec['final_article_exists']=os.path.exists(art)
    if os.path.exists(art):
        t=open(art,encoding='utf-8').read(); i=t.lower().find('in one line'); rec['final_summary']=t[i:i+400] if i>=0 else None
    rej=glob.glob(ad+'/rejected_*attempt*.md')
    rec['rejected']=[os.path.basename(x) for x in rej]
    out.append(rec)
json.dump(out,open(R+'open243_translation_ng_analysis_01/_s0_summary14.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for r in out:
    print('=====',r['gen'],r['run'].replace(R,''),'article' ,r['final_article_exists'],'rejected',r['rejected'])
    for a in r['attempts']:
        print(' --',os.path.basename(a['file']),a['status'])
        for x in a['devs']: print('    CLAIM:',x['claim_in_article'][:200]); print('    ISSUE:',x['issue'][:260]); print('    FLAGS:',x['flags'],x['related_fact_id'])
    for k,v in r['ledger'].items(): print('  LEDGER',k,':',(v or 'NA')[:420].replace('\n',' | '))
    print('  FINAL_SUMMARY:',(r.get('final_summary') or '')[:260].replace('\n',' '))
