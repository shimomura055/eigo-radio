import json,glob,os,re
M='C:/Users/tensh/eigo-radio/'
D='docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/'
def norm(s): return re.sub(r'\s+',' ',s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')).strip()
def sents(par): return [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“"‘\'(])',par) if s.strip()]
def article_text(f):
    d=M+f['source_kp_candidates_path']
    d=os.path.dirname(d) if d.endswith('.json') else d
    gp=sorted(glob.glob(d+'/**/gloss_alignment_prompt.txt',recursive=True))
    for g in gp:
        t=open(g,encoding='utf8').read()
        if '【記事本文(参考)】' in t: return t.split('【記事本文(参考)】',1)[1].strip()
    return None
def ctx(text,ex):
    if not text: return None,None
    ex=norm(ex)
    paras=[norm(p) for p in text.split('\n') if p.strip()]
    flat=[]
    for p in paras: flat+=sents(p)
    for i,s in enumerate(flat):
        if ex in s or s in ex:
            return ' '.join(flat[max(0,i-2):i]),' '.join(flat[i+1:i+3])
    for i,s in enumerate(flat):
        if ex[:30] in s: return ' '.join(flat[max(0,i-2):i]),' '.join(flat[i+1:i+3])
    return None,None
items=json.load(open(D+'eval_set/items.json',encoding='utf8'))
devkeys=set()
def slugof(k):
    return k
pool=[]
for p in sorted(glob.glob('user_test/selection_form_v3/data/*__prod.json')):
    f=json.load(open(p,encoding='utf8'))
    text=article_text(f)
    slug=os.path.basename(p).split('__')[0]
    for it in f['phrases']+f['words']:
        b,a=ctx(text,it['excerpt'])
        pool.append(dict(pid=f"JAQ-P-{len(pool):03d}",file=os.path.basename(p),slug=slug,level=f['level_label'],family=f['family'],
          kind=it['kind'],candidate_id=it['candidate_id'],expression=it['term'],current_ja=it['ja_gloss'],gloss_status=it['ja_gloss_status'],
          sentence_en=it['excerpt'],context_before=b,context_after=a,ctx_found=b is not None))
# dev flag
dev=[x for x in items if x['split']=='dev']
def slugmatch(slug,key): return slug in key
for q in pool:
    q['in_dev_set']=any(slugmatch(q['slug'],x['article_key']) and x['level']==q['level'] and norm(x['expression']).lower()==norm(q['expression']).lower() for x in dev)
    q['dev_article']=any(slugmatch(q['slug'],x['article_key']) for x in dev)
json.dump(pool,open(D+'../../../'+'/dev/null' if False else os.path.join(os.path.dirname(__file__),'pool.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(pool),sum(q['ctx_found'] for q in pool),sum(q['in_dev_set'] for q in pool),sum(q['dev_article'] for q in pool))
