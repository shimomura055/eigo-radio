import json,glob,collections,re
BS=chr(92)
roots=['er052_output/all6_writer_redesign_necessity_01','er052_output/factlock_writer_trial_01','er052_output/gpt6_wiring_e2e_01','er019_output']
files=set()
for r in roots:
    for pat in ['**/b1b/audit/deviation_check.json','**/a2/audit/deviation_check.json','**/b1b/audit/deviation_checks/advanced_*.json','**/a2/audit/deviation_checks/standard_*.json','**/audit/deviation_checks/advanced_*.json','**/audit/deviation_checks/standard_*.json']:
        for f in glob.glob(r+'/'+pat,recursive=True): files.add(f.replace(BS,'/'))
files=sorted(files); print(len(files))
flags=['changed_fact','changed_scope','changed_causality','changed_certainty','changed_number','changed_actor','changed_negation','changed_comparison','changed_time','unsupported_new_claim']
rows=[]; c=collections.Counter(); nofiles=collections.Counter()
for f in files:
    d=json.load(open(f,encoding='utf8'))
    kind='final' if f.endswith('deviation_check.json') else 'attempt'
    if 'parsed' in d: p=d['parsed']
    else: p=d
    if isinstance(p,str): p=json.loads(p)
    devs=p.get('deviations',[]) if isinstance(p,dict) else []
    root=f.split('/')[1]
    c[(root,kind,'files')]+=1
    for dv in devs:
        rows.append(dict(file=f,kind=kind,status=p.get('overall_status'),**dv))
        c[(root,kind,dv.get('severity'),dv.get('origin'))]+=1
for k,v in sorted(c.items(),key=str): print(k,v)
json.dump(rows,open('er052_output/open243_translation_ng_analysis_01/_dev_all.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print()
for r in rows:
    if r.get('origin')=='translation' or r['kind']=='attempt':
        print(r['file'].replace('er052_output/','').replace('/b1b/audit/deviation_checks/','|').replace('/b1b/audit/','|').replace('/a2/audit/','|a2|'),r['kind'],r.get('severity'),r.get('origin'),[k[8:] if k.startswith('changed_') else k for k in flags if r.get(k)],r.get('related_fact_id'),'|',r['claim_in_article'][:110])
