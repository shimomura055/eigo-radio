import json,glob,re,random,sys
sys.stdout.reconfigure(encoding='utf-8')
D='er052_output/open233_stage0_01/stability/'
rng=random.Random(233)
u=json.load(open(D+'ng_pool.json',encoding='utf-8'))
# manual type fixes (kanji numerals / 全称 / fragments)
fix={'異常な動きは、見つかってから約一時間で封じ込められました。':'数値','監視も防護も地上発射ミサイルも、広い意味ではカウンタースペースです':'全称',
 '兵器の名前だけでなく、その住所まで明らかになったからです':'全称'}
for p in u:
  p['type']=fix.get(p['text'],p['type'])
u=[p for p in u if not (p['text'].startswith(("'","#")) or p['text'] in ('vice president of Meta\'s artificial intelligence division',) or p['text'].startswith('Meta Tested') and False)]
def pick(lang,quota,allow_rw):
  out=[]
  for t,n in quota.items():
    c=[p for p in u if p['lang']==lang and p['type']==t and (allow_rw or p['kind']!='rewrite') and p not in out]
    rng.shuffle(c); out+=c[:n]
  return out
ja=pick('JA',{'否定':5,'因果':4,'多義語':3,'全称':2,'数値':1,'主語新規':1,'other':4},True)
en=pick('EN',{'否定':3,'数値':4,'全称':2,'多義語':3,'主語新規':2,'other':3},True)
# top up
for lang,lst,N in (('JA',ja,20),('EN',en,20)):
  rest=[p for p in u if p['lang']==lang and p not in lst]; rng.shuffle(rest)
  while len(lst)<N and rest: lst.append(rest.pop())
ng=ja[:20]+en[:20]
for p in ng: p['group']='NG'
# normal
ngtexts=[p['text'] for p in u]
def sents(txt,lang):
  txt=re.sub(r'^#.*$','',txt,flags=re.M)
  ss=re.split(r'(?<=[。！？])|(?<=[.!?])\s+',txt)
  return [s.strip() for s in ss if s and 25<=len(s.strip())<=140]
norm=[]
for lang,pat in (('JA','blind/*/*/ja_writer/original.md'),('EN','blind/*/*/b1b/article.md')):
  c=[]
  for f in sorted(glob.glob('er052_output/open233_control_checker_polysemy_trial_01/eval/'+pat)):
    for s in sents(open(f,encoding='utf-8').read(),lang):
      if lang=='JA' and not re.search(r'[ぁ-ん]',s): continue
      if any(s[:15] in t or t[:15] in s for t in ngtexts): continue
      c.append(dict(src=f.split('/')[-4]+'-'+f.split('/')[-3],lang=lang,type='通常',kind='normal',text=s,group='NORMAL'))
  c=list({x['text']:x for x in c}.values()); rng.shuffle(c); norm+=c[:10]
allp=ng+norm
for i,p in enumerate(allp): p['sid']=f's{i+1:02d}'
json.dump(allp,open(D+'sentences.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
import collections
print(len(allp),collections.Counter((p['group'],p['lang'],p['type']) for p in allp))
for p in allp: print(p['sid'],p['lang'],p['type'],p['kind'],p['text'][:90])
