import json,re,glob,collections,os
BS=chr(92)
def norm(s): return re.sub(r'[\s"“”‘’\'「」.,]','',s or '').lower()
def toks(s): return set(re.findall(r"[a-z0-9]+",(s or '').lower().replace('’',"'")))
def sim(a,b):
    A,B=toks(a),toks(b)
    j=len(A&B)/max(1,len(A|B))
    na,nb=norm(a),norm(b)
    c=(na in nb or nb in na) and min(len(na),len(nb))>=20
    return j>=0.5 or c
items=[json.loads(l) for l in open('er052_output/open243_translation_ng_analysis_01/items.jsonl',encoding='utf-8')]
ev=collections.OrderedDict()
for it in items: ev.setdefault(it['event_id'] or 'NONE-'+it['id'],[]).append(it)
out=[]
for k,its in ev.items():
    it0=its[0]
    tr=it0['origin'] in ('translation','amplified') and any(i['counted'] for i in its)
    run=it0['run_dir']; f=glob.glob(run+'/checker/runs/*.json')
    rec={'event':k,'ids':[i['id'] for i in its],'run':run.split('runs/')[-1],'origin':it0['origin'],'sev':sorted({i['severity'] for i in its}),'counted':any(i['counted'] for i in its),'is_tr26':tr,
         'type':it0['type'],'position':it0['position'],'sent':its[0]['en_sentence_matched'] or its[0]['ng_text']}
    if not f: rec['has_checker']=False; out.append(rec); continue
    rec['has_checker']=True
    d=json.load(open(f[0],encoding='utf-8')); s=rec['sent']
    cf=d['stage1_coverage']['candidate_filter']
    rec['verdicts']=[dict(key=v['key'],verdict=v['verdict'],excluded=v['excluded'],actor_match=v.get('actor_match')) for v in cf['verdicts'] if sim(v['claim'],s)]
    rec['union']=[dict(ids=u['unit_ids'],sources=u['sources'],sub=u['sub_reasons']) for u in d['stage1_coverage']['union_candidates'] if sim(u['claim_text'],s)]
    rec['stage2']=[dict(cycle=cy['cycle'],mat=x.get('materiality'),llm=x.get('llm_materiality'),fid=x.get('related_fact_id'),basis=x.get('basis'),origin_k=[kk for kk in x if 'sibling' in kk.lower() or 'origin' in kk.lower()]) for cy in d['cycles'] for x in cy.get('stage2_results',[]) if sim(x.get('claim_text',''),s)]
    # stage1 flags for matched candidates (pre-filter)
    fl=set()
    for rt in ('r3','r5'):
        for c in d['stage1_coverage']['per_route'].get(rt,{}).get('candidates',[]) or []:
            if sim(c.get('claim_text',''),s): fl|={a for a,v in (c.get('flags') or {}).items() if v}
    rec['pre_filter_flags']=sorted(fl)
    rec['final_state']=d['final_state']
    out.append(rec)
json.dump(out,open('er052_output/open243_translation_ng_analysis_01/_s0_events.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for r in out:
    if r['is_tr26']:
        print(r['event'],r['sev'],r['type'],r['position'],'|ck',r['has_checker'],'|V',[(v['verdict'],v['excluded']) for v in r.get('verdicts',[])],'|U',[u['sources'] for u in r.get('union',[])],'|S2',[(x['cycle'],x['mat'],x['basis']) for x in r.get('stage2',[])],'|F',r.get('pre_filter_flags'))
