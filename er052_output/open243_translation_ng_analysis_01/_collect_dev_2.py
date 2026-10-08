import json,collections,glob,os,re
BS=chr(92)
rows=json.load(open('er052_output/open243_translation_ng_analysis_01/_dev_all.json',encoding='utf8'))
def toks(s): return set(w for w in re.sub(r'[^a-z0-9]+',' ',s.lower()).split() if len(w)>2)
def jac(a,b):
    A,B=toks(a),toks(b); return len(A&B)/max(1,len(A|B))
def loc_from_prompt(prompt,claim):
    claim=claim.replace('In one line:','').strip(' “”"')
    k=prompt.rfind('## In one line')
    if k<0: return 'body'
    # summary section text: from marker to the next 【
    end=prompt.find('【',k)
    summ=prompt[k:end if end>0 else None]
    c=claim[:40]
    if c and c in summ: return 'summary'
    # title
    t=prompt.find('# ')
    return 'body'
recs=[]
for r in rows:
    f=r['file']; gdir=f.split('/audit/')[0]
    if '/ja_writer' in gdir: continue
    r=dict(r); r['gen']=gdir
    m=re.search(r'attempt(\d)',f); r['attempt']=int(m.group(1)) if m else 99
    if r['kind']=='attempt':
        d=json.load(open(f,encoding='utf8')); r['pos']=loc_from_prompt(d['prompt'],r['claim_in_article'])
    recs.append(r)
# finals: copy pos from the best-matching attempt rec of same gen
for r in recs:
    if r['kind']=='final':
        c=[x for x in recs if x['kind']=='attempt' and x['gen']==r['gen'] and jac(x['claim_in_article'],r['claim_in_article'])>=0.7]
        r['pos']=c[-1]['pos'] if c else 'unknown'
        r['attempt']=max([x['attempt'] for x in recs if x['gen']==r['gen'] and x['kind']=='attempt'],default=1)
# generations
def group(g):
    for k in ['all6_writer_redesign_necessity_01','factlock_writer_trial_01/sweep_01','factlock_writer_trial_01','gpt6_wiring_e2e_01','er019_output']:
        if k in g: return k
    return g
gens=set()
for pat in ['er052_output/all6_writer_redesign_necessity_01/runs/**/b1b/audit/deviation_check.json','er052_output/all6_writer_redesign_necessity_01/runs/**/a2/audit/deviation_check.json','er052_output/factlock_writer_trial_01/runs/**/b1b/audit/deviation_check.json','er052_output/factlock_writer_trial_01/runs/**/a2/audit/deviation_check.json','er052_output/factlock_writer_trial_01/sweep_01/**/b1b/audit/deviation_check.json','er052_output/gpt6_wiring_e2e_01/**/b1b/audit/deviation_check.json','er052_output/gpt6_wiring_e2e_01/**/a2/audit/deviation_check.json','er019_output/**/b1b/audit/deviation_check.json','er019_output/**/a2/audit/deviation_check.json']:
    for f in glob.glob(pat,recursive=True): gens.add(f.replace(BS,'/').split('/audit/')[0])
# also attempt1-only gens (STOP w/o final)
for f in glob.glob('er052_output/**/audit/deviation_checks/*_attempt1.json',recursive=True)+glob.glob('er019_output/**/audit/deviation_checks/*_attempt1.json',recursive=True):
    f=f.replace(BS,'/')
    if '/ja_writer/' in f: continue
    gens.add(f.split('/audit/')[0])
ROOTS=('er052_output/all6_writer_redesign_necessity_01','er052_output/factlock_writer_trial_01','er052_output/gpt6_wiring_e2e_01','er019_output')
gens={g for g in gens if g.startswith(ROOTS)}
print(len(gens))
bygroup=collections.defaultdict(list)
for g in gens: bygroup[group(g)].append(g)
G=collections.defaultdict(list)
for r in recs: G[r['gen']].append(r)
summary=collections.Counter()
detail=[]
for grp,gl in sorted(bygroup.items()):
    n=len(gl)
    ntr=0; ntr_major_a1=0; nsum=0; nstop=0; nbody=0
    for g in gl:
        tr=[x for x in G.get(g,[]) if x.get('origin')=='translation']
        if not tr: continue
        ntr+=1
        a1=[x for x in tr if x['kind']=='attempt' and x['attempt']==1 and x['severity']=='MAJOR']
        fin=[x for x in tr if x['kind']=='final' and x['severity']=='MAJOR']
        if a1: ntr_major_a1+=1
        if any(x['pos']=='summary' for x in tr if x['severity']=='MAJOR'): nsum+=1
        if any(x['pos']!='summary' for x in tr if x['severity']=='MAJOR'): nbody+=1
        if fin: nstop+=1
        detail.append((grp,g.split('/runs/')[-1] if '/runs/' in g else g.split('output/')[-1],[(x['kind'][0]+str(x['attempt']),x['severity'][:3],x['pos'],x.get('related_fact_id'),'|'.join(k[8:] if k.startswith('changed_') else k for k in x if (k.startswith('changed_') or k=='unsupported_new_claim') and x.get(k) is True)) for x in tr]))
    print(grp,'generations',n,'with translation-origin dev (any attempt):',ntr,'MAJOR@attempt1:',ntr_major_a1,'any MAJOR in summary:',nsum,'any MAJOR in body:',nbody,'final MAJOR translation (STOP-class):',nstop)
for d in detail: print(d)
tot=collections.Counter()
for r in recs:
    if r.get('origin')=='translation': tot[(r['kind'],r['severity'],r['pos'])]+=1
print(tot)
json.dump(recs,open('er052_output/open243_translation_ng_analysis_01/_dev_all.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
