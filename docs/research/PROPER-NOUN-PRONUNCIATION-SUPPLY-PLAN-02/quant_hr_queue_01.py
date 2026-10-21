import json,collections,re
rows=[json.loads(l) for l in open('er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl',encoding='utf8')]
real=[r for r in rows if 'Temp' not in r['wav_path'] and 'tmp' not in r['wav_path'].lower()]
print('total',len(rows),'real-path',len(real))
def art(p):
    p=p.replace(chr(92),'/'); m=re.match(r'(er\d+_output/[^/]+/[^/]+)',p); return m.group(1) if m else p[:40]
print(collections.Counter(art(r['wav_path']) for r in real).most_common(30))
pl=collections.Counter(); conf=collections.Counter()
for r in rows:
    d=r.get('pronunciation_lookups')
    if isinstance(d,dict):
        for k,v in d.items():
            pl[k]+=1; conf[(v.get('confidence'),bool(v.get('expected_pronunciation_ipa')))]+=1
print(len(pl),pl.most_common(40)); print(conf)
print('real rows w/ pron lookups:',sum(1 for r in real if r.get('pronunciation_lookups')))
print('real unique canon', len(set(r['canonical_text'] for r in real)))
g=set(); gall=set(); names=collections.Counter()
for r in real:
    a=art(r['wav_path']); gall.add(a)
    d=r.get('pronunciation_lookups')
    if isinstance(d,dict) and d:
        g.add(a)
        for k in d: names[k]+=1
print('real groups',len(gall),'groups w/ pron lookups',len(g)); print(names)
lowonly=0;tot=0
for r in rows:
    d=r.get('pronunciation_lookups')
    if isinstance(d,dict) and d:
        tot+=1
        if all(v.get('confidence') in ('low','unconfirmed') for v in d.values()): lowonly+=1
print('rows with lookups',tot,'rows where all lookups low/unconfirmed',lowonly)
