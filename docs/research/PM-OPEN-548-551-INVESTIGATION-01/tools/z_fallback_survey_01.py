import json,glob,collections
rows=[]
for p in glob.glob('*/run_*/*/audit/tts_generation_results.json'):
    p=p.replace(chr(92),'/'); parts=p.split('/')
    if 'preserve' in parts[1] or 'mock' in parts[1]: continue
    d=json.load(open(p,encoding='utf-8'))
    ents=list(d['segments'].items())
    for kp,v in d.get('key_phrases',{}).items():
        if isinstance(v,dict):
            for k2,e in v.items():
                if isinstance(e,dict) and 'style' in e: ents.append((f'kp{kp}_{k2}',e))
    for n,e in ents:
        if isinstance(e,dict) and (e.get('style') or {}).get('fallback_used'):
            rows.append((parts[0],parts[1],parts[2],n,e.get('role_style_key'),e.get('z_adoption'),e.get('status'),[a['instruction_label'] for a in e['attempts'] if a['phase']=='fallback'][:1]))
c=collections.Counter((r[0],r[1],r[2]) for r in rows)
for k,v in sorted(c.items()): print(k,v)
print(len(rows))
for r in rows:
    if r[1] in('run_sf_prod_01','run_sf_prod_02'): print(r)
