import json,re,collections
def norm(s): return re.sub(r'[\s"“”‘’\'「」]','',s or '').lower()
items=[json.loads(l) for l in open('items.jsonl',encoding='utf-8')]
exc=[json.loads(l) for l in open('s0_excluded_candidates.jsonl',encoding='utf-8')]
byrun=collections.defaultdict(list)
for e in exc: byrun[e['run_key']].append(e)
ev=collections.OrderedDict()
for it in items:
    k=it['event_id'] or ('NONE-'+it['id'])
    ev.setdefault(k,[]).append(it)
rows=[]
for k,its in ev.items():
    it0=its[0]
    runs={i['run_dir'] for i in its}
    sents={norm(i['en_sentence_matched'] or i['ng_text']) for i in its}
    m=[]
    for r in runs:
        for e in byrun.get(r,[]):
            n=norm(e['claim'])
            if any(s and n and (s in n or n in s) for s in sents): m.append(e)
    ck=it0['checker']
    rows.append({'event':k,'ids':[i['id'] for i in its],'run':sorted(runs),'origin':it0['origin'],'counted':any(i['counted'] for i in its),
      'severity':sorted({i['severity'] for i in its}),'type':it0['type'],'position':it0['position'],
      'has_checker':ck.get('has_checker'),'candidate':ck.get('candidate'),'ck_final':ck.get('final_state'),'ck_cycles':[(c.get('materiality'),c.get('related_fact_id')) for c in ck.get('cycles',[])],
      'in_final':ck.get('sentence_in_final_text'),'matched':[{'claim':e['claim'],'verdict':e['verdict'],'flags':e['stage1_flags'],'rel':e['related_fact_ids'],'actor_match':e['actor_match'],'run':e['run_key'],'in_final_text':e['in_final_text']} for e in m]})
json.dump(rows,open('_s0_event_match.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(rows))
tr=[r for r in rows if r['origin'] in ('translation','amplified') and r['counted']]
print('translation/amplified counted events',len(tr))
print(collections.Counter((r['has_checker'],r['candidate']) for r in tr))
print('matched excluded among them',sum(1 for r in tr if r['matched']))
allm=[r for r in rows if r['matched']]
print('all events matched',len(allm),collections.Counter(r['origin'] for r in allm))
for r in tr:
    print(r['event'],r['has_checker'],r['candidate'],r['ck_final'],r['ck_cycles'],'MATCH' if r['matched'] else '')
