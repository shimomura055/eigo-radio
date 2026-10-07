import json,glob,re,random,os,sys
sys.stdout.reconfigure(encoding='utf-8')
R='er052_output/'
pool=[]
for d in ['open233_control_checker_polysemy_trial_01','open233_b3_trial_01']:
  for f in sorted(glob.glob(R+d+'/eval/articles/*.json')):
    j=json.load(open(f,encoding='utf-8'))
    items=list(j.get('ng_items',[]))+[dict(id=x['id'],kind='pending',text=x['text']) for x in j.get('pending',[])]
    for x in j.get('checker_rewrites',[]):
      for k in ('before','after'):
        if x.get(k): items.append(dict(id=j['slug']+'-'+j['code']+'-rw'+k,kind='rewrite',text=x[k]))
    for it in items:
      t=it['text'].strip()
      if t.startswith(('(','（')): continue
      m=re.search(r'[（(]',t)
      body=t[:m.start()] if m else t
      body=re.sub(r'^(EN(のみ|のみ|の一行要約)?\s*[:：]\s*|EN title:\s*|\(In one line\)\s*)','',body).strip()
      parts=[p.strip() for p in re.split(r'(?<=[。\.])\s*/\s*|\s/\s+',body) if p.strip()]
      for p in parts:
        if '...' in p or '…' in p or len(p)<12 or len(p)>220: continue
        en = len(re.findall(r'[A-Za-z]',p))>len(p)*0.5
        pool.append(dict(src=it['id'],kind=it.get('kind'),lang='EN' if en else 'JA',text=p.rstrip()))
def typ(p):
  t=p['text']
  if re.search(r'ではなく|ありません|ない|なし|no one|not |did not|had no|n\'t|never|no ',t) and p['kind']in('negation','scope','causal','added_fact','object','subject') and re.search(r'ではなく|ありません|ませんでした|not |no |never|n\'t',t): neg=True
  else: neg=False
  if re.search(r'\d',t) and re.search(r'\d+\s*(%|percent|日|月|年|台|万|15|June)|20 percent|since June|15|二十|十五',t): return '数値'
  if re.search(r'ロールバック|元に戻|元の状態|戻し|戻さ|put .*back|rolled back|returned|restor',t): return '多義語'
  if p['kind']=='causal' or re.search(r'ため|because|so that|ので',t): return '因果'
  if re.search(r'ではなく|ありません|ませんでした|ない|did not|had no|not |no one|n\'t',t): return '否定'
  if re.search(r'全体|すべて|全て|all |entire|every|whole|一部',t): return '全称'
  if p['kind']=='subject': return '主語新規'
  return 'other'
for p in pool: p['type']=typ(p)
seen=set(); u=[]
for p in pool:
  if p['text'] in seen: continue
  seen.add(p['text']); u.append(p)
import collections
print(collections.Counter((p['lang'],p['type']) for p in u))
json.dump(u,open('er052_output/open233_stage0_01/stability/ng_pool.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
