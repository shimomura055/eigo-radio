# -*- coding: utf-8 -*-
"""T4 項目構築(APIなし、決定論)。使い方: build_items.py dev|heldout"""
import sys, os, json, re, random, importlib, collections
os.environ["PYTHONUTF8"]="1"
sys.path.insert(0,'er052_output/open233_link_precision_01')
import units_lib as U
import glob, pathlib
class A: pass
A.NEG = re.compile(r"(no|not|nor|never|none|neither|without|nothing|nobody|cannot)|n't|(lack|lacks|unknown|unclear)", re.I)
def _num(s):
    m = re.search(r"(\d+)\s*$", s or ""); return int(m.group(1)) if m else None
def _norm_id(x, ledger_ids):
    if x in ledger_ids: return x
    n=_num(x)
    if n is None: return None
    c=[i for i in ledger_ids if _num(i)==n and i[:1].lower()==(x or '')[:1].lower()]
    return c[0] if len(c)==1 else None
A.norm_id=_norm_id
def _lo(tag):
    out={}
    for f in glob.glob(str(U.OUT/'r3'/tag/'*.json')):
        d=json.loads(pathlib.Path(f).read_text(encoding='utf-8')); out[(d['run'],d['rep'])]=d
    return out
A.load_outputs=_lo
def _ng():
    ng={}
    for l in open('er052_output/open233_stage0_01/reclass/known_relation_ng.jsonl',encoding='utf-8'):
        j=json.loads(l); ng[j['item_id']]=j
    return ng
A.load_ng=_ng
RL, cov = U.RL, U.cov
which = sys.argv[1]
O = importlib.import_module('oracle_dev' if which=='dev' else 'oracle_heldout')
tag = 'dev' if which=='dev' else 'heldout'
outs = A.load_outputs(tag)
runs_all = sorted({k[0] for k in outs})
ng = A.load_ng()
SEED = 20261008
rng = random.Random(SEED)
NEGR=A.NEG
def feat(t):
    f=[]
    if NEGR.search(t): f.append('neg')
    if re.search(r"\b(all|every|always|any|never|each|none)\b",t,re.I): f.append('univ')
    if re.search(r"\b(because|so|therefore|since|led to|caused|due to|as a result|which means)\b",t,re.I): f.append('causal')
    if re.search(r"\d",t): f.append('num')
    return f or ['plain']
def cat(t):
    f=feat(t)
    for k in ('neg','univ','causal','num'):
        if k in f: return k
    return 'plain'
def find_run(sfx):
    key = sfx.split('/runs/')[-1]
    c=[r for r in runs_all if r.replace(chr(92),'/').endswith(key) and sfx.split('/')[0] in r]
    assert len(c)==1,(sfx,c); return c[0]
items=[]; ctrl_pool=collections.defaultdict(list); ng_units_by_run=collections.defaultdict(set)
for it,sfx,uids in O.MAIN:
    r=find_run(sfx); ng_units_by_run[r]|=set(uids)
for it,sfx,uids in O.MAIN:
    j=ng[it]
    if not j['fact_id']: continue
    r=find_run(sfx); d=outs[(r,1)]
    _,led,art=RL.load_run(r)
    blocks=cov.ledger_fact_blocks(led)
    utext={u['id']:u['text'] for u in d['units']}
    text=' '.join(utext[u] for u in uids)
    assert j['fact_id'] in blocks,(it,j['fact_id'])
    verd=[(d['model_verdict'] or {}).get(u) for u in uids]
    items.append({"id":it,"group":"ng","run":r,"units":uids,"sentence":text,"fact_id":j['fact_id'],"fact":blocks[j['fact_id']],
        "type":j['sentence_type'],"list":j['list'],"severity":j['severity_final'],"cat":cat(text),"r3_verdict":verd})
# controls
for r in sorted({i['run'] for i in items}):
    d=outs[(r,1)]; _,led,art=RL.load_run(r); blocks=cov.ledger_fact_blocks(led)
    ids=list(blocks.keys())
    for u in d['units']:
        if not u['judged'] or u['id'] in ng_units_by_run[r]: continue
        sf=(d['support_fact_ids'] or {}).get(u['id']) or []
        sfn=[A.norm_id(x,ids) for x in sf]; sfn=[x for x in sfn if x]
        if not sfn or (d['model_verdict'] or {}).get(u['id'])!='SUPPORTED': continue
        if len(u['text'].split())<5: continue
        ctrl_pool[r].append({"unit":u['id'],"sentence":u['text'],"fact_id":sfn[0],"fact":blocks[sfn[0]],"cat":cat(u['text']),"r3_verdict":'SUPPORTED'})
ctrls=[]; used=set()
for i in items:
    pool=[c for c in ctrl_pool[i['run']] if (i['run'],c['unit']) not in used]
    same=[c for c in pool if c['cat']==i['cat']]
    pick=same or pool or [c for rr in ctrl_pool for c in ctrl_pool[rr] if (rr,c['unit']) not in used and c['cat']==i['cat']]
    pick=sorted(pick,key=lambda c:c['unit']); c=rng.choice(pick)
    rr=i['run'] if c in ctrl_pool[i['run']] else [x for x in ctrl_pool if c in ctrl_pool[x]][0]
    used.add((rr,c['unit']))
    ctrls.append({"id":"ctrl-"+i['id'],"group":"control","run":rr,"units":[c['unit']],"sentence":c['sentence'],"fact_id":c['fact_id'],"fact":c['fact'],
        "type":"control(match:%s)"%i['cat'],"cat":c['cat'],"matched_to":i['id'],"r3_verdict":[c['r3_verdict']],"same_article":rr==i['run'],"cat_match":c['cat']==i['cat']})
json.dump({"seed":SEED,"which":which,"items":items+ctrls},open(f'er052_output/open233_pairwise_judge_01/items_{which}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(items),len(ctrls),collections.Counter(i['type'] for i in items))
print('ctrl same_article',sum(c['same_article'] for c in ctrls),'cat_match',sum(c['cat_match'] for c in ctrls))
