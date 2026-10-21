import json,re,collections,pronouncing,unicodedata,sys
D='docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/'
pairs=[json.loads(l) for l in open(D+'pairs_02.jsonl',encoding='utf8')]
L=json.load(open('er006_output/pronunciation_ledger_01/ledger.json',encoding='utf8'))
def fold(s): return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
led={}
for e in L.values():
    if e.get('ledger_disabled'): continue
    ipa=(e.get('expected_pronunciation_ipa') or '').strip()
    led.setdefault(fold(e['surface']),[]).append((e['entity_type'],e['confidence'],bool(ipa)))
def art(src):
    src=src.replace(chr(92),'/')
    m=re.match(r'((?:er\d+_output|docs)/[^/]+/[^/]+)',src); return m.group(1) if m else src[:50]
canon={}
for p in pairs:
    c=p['canonical']
    if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',c): continue
    canon.setdefault(c,set()).update(art(s) for s in p['sources'])
print('unique EN canonical',len(canon))
arts=set().union(*canon.values()); print('distinct source dirs',len(arts))
tokre=re.compile(r"[A-Za-z][A-Za-z0-9'’\.\-]*")
SKIP=set('i a the this that it he she we they in on at as and but or so if when while after before there here today now one two what who how why'.split())
tok_arts=collections.defaultdict(set); tok_kind={}
for c,ar in canon.items():
    sents=re.split(r'(?<=[.!?])\s+',c)
    for s in sents:
        ws=tokre.findall(s)
        for i,w in enumerate(ws):
            w0=w.strip(".-'’")
            if len(w0)<2: continue
            camel=bool(re.search(r'[a-z][A-Z]',w0)) 
            caps=w0[0].isupper() and i>0
            allc=w0.isupper() and len(w0)>=3
            if not(camel or caps or allc): continue
            if w0.lower() in SKIP: continue
            key=re.sub(r"(’|')s$",'',fold(w0)).replace('’',"'")
            if '-' in key or 'xzqw' in key: continue
            tok_arts[key].update(ar)
n=len(tok_arts); cmu=oov=ledin=0; oovled=0; hit=[]
rows=[]
for k,ar in tok_arts.items():
    ws=re.sub(r"[^a-z0-9' ]","",k).split() or [k]
    incmu=bool(pronouncing.phones_for_word(re.sub(r"[^a-z0-9']","",k)))
    inl=k in led
    rows.append((k,incmu,inl,len(ar)))
tot=len(rows); a=sum(1 for r in rows if r[1]); b=sum(1 for r in rows if not r[1]); c_=sum(1 for r in rows if not r[1] and r[2]); d=sum(1 for r in rows if r[1] and r[2])
print('proper-like tokens distinct',tot,'CMU-in',a,'OOV',b,'OOV&in ledger',c_,'CMU-in&in ledger',d)
oovrows=[r for r in rows if not r[1]]
print('OOV tokens by #sourcedirs>=2:',sum(1 for r in oovrows if r[3]>=2),'  single-source:',sum(1 for r in oovrows if r[3]==1))
print('OOV in ledger:',[r[0] for r in oovrows if r[2]])
print('OOV not in ledger sample:',sorted([r for r in oovrows if not r[2]],key=lambda r:-r[3])[:40])
json.dump(rows,open(D.replace('MULTIWORD-HOMOPHONE-PLAN-01','SUPPLY-PLAN-02')+'_q.json','w')) if False else None
