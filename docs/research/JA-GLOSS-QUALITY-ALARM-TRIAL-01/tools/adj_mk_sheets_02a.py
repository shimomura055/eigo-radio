import json,random,re
D='docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/'
J='../jaq_run/'
items=json.load(open(D+'eval_set/items.json',encoding='utf8'))
pool=json.load(open(J+'pool.json',encoding='utf8'))
def sents(par): return [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“"‘\'(])',par) if s.strip()]
def last2(t): s=sents(t or ''); return ' '.join(s[-2:])
def first2(t): s=sents(t or ''); return ' '.join(s[:2])
recs=[]
for x in items:
    if x['tier'] in ('T2','T4'):
        recs.append(dict(src_id=x['id'],src='eval',expression=x['expression'],current_ja=x['current_ja'],sentence_en=x['sentence_en'],before=last2(x['context_before']),after=first2(x['context_after']),level=x['level']))
for q in pool:
    recs.append(dict(src_id=q['pid'],src='pool',expression=q['expression'],current_ja=q['current_ja'],sentence_en=q['sentence_en'],before=last2(q['context_before']),after=first2(q['context_after']),level=q['level']))
print(len(recs))
rnd=random.Random(20261031); order=list(range(len(recs))); rnd.shuffle(order)
bl={}
sheet1=[]
for n,i in enumerate(order,1):
    b=f"BL-{n:03d}"; bl[b]=recs[i]; 
json.dump(bl,open(J+'blind_map.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
def fmt(b,r):
    return f"[{b}] {r['level']} | {r['expression']} => {r['current_ja']}\n EN: {r['sentence_en']}\n 前: {r['before']}\n 後: {r['after']}\n"
ids=sorted(bl)
for c in range(0,len(ids),58):
    open(J+f'sheet1_{c//58+1}.txt','w',encoding='utf8').write('\n'.join(fmt(b,bl[b]) for b in ids[c:c+58]))
# pass2 sheet: different order, no pre-label
rnd2=random.Random(20261101); ids2=ids[:]; rnd2.shuffle(ids2)
json.dump(ids2,open(J+'order2.json','w'))
for c in range(0,len(ids2),58):
    open(J+f'sheet2_{c//58+1}.txt','w',encoding='utf8').write('\n'.join(fmt(b,bl[b]) for b in ids2[c:c+58]))
