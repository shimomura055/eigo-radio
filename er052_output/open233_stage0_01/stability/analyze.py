import json,re,unicodedata,itertools,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
D='er052_output/open233_stage0_01/stability/'
S={p['sid']:p for p in json.load(open(D+'sentences.json',encoding='utf-8'))}
R=collections.defaultdict(list)
for l in open(D+'results.jsonl',encoding='utf-8'):
  r=json.loads(l); R[r['sid']].append(r)
def nz(s): return re.sub(r'[\s\W_「」『』、。,.]+','',unicodedata.normalize('NFKC',str(s)).lower())
def bg(s):
  s=nz(s); return {s[i:i+2] for i in range(len(s)-1)} or {s}
def jac(a,b):
  A,B=bg(a),bg(b); return len(A&B)/len(A|B) if A|B else 1
def eq_text(a,b,mode):
  x,y=nz(a),nz(b)
  if x==y: return True
  if mode=='strict': return False
  return (bool(x) and bool(y) and (x in y or y in x)) or jac(a,b)>=0.5
def eq_list(a,b,mode):
  if not a and not b: return True
  if mode=='strict': return {nz(i) for i in a}=={nz(i) for i in b}
  return (bool(a) and bool(b)) and jac(' '.join(sorted(a)),' '.join(sorted(b)))>=0.5 or not a and not b
def nnum(l): return {re.sub(r'[約およそ]|about|approximately','',nz(i)) for i in l}
F={'subject':lambda a,b,m:eq_text(a['subject'],b['subject'],m),
 'predicate':lambda a,b,m:a['predicate_normalized']==b['predicate_normalized'],
 'object':lambda a,b,m:eq_text(a['object'],b['object'],m),
 'polarity':lambda a,b,m:a['polarity']==b['polarity'],
 'scope':lambda a,b,m:eq_list(a['scope_qualifiers'],b['scope_qualifiers'],m),
 'numbers':lambda a,b,m:nnum(a['numbers'])==nnum(b['numbers']),
 'modality':lambda a,b,m:a['modality']==b['modality']}
def level(f,runs,m):
  ps=[F[f](a,b,m) for a,b in itertools.combinations([r['parsed'] for r in runs],2)]
  k=sum(ps); return 3 if k==3 else (2 if k>=1 else 0)
rows=[]
for sid,runs in R.items():
  assert len(runs)==3 and all(r['parsed'] for r in runs),sid
  p=S[sid]; row=dict(sid=sid,lang=p['lang'],type=p['type'],group=p['group'],text=p['text'])
  for m in ('strict','lenient'):
    for f in F: row[f'{f}_{m}']=level(f,runs,m)
  rows.append(row)
json.dump(rows,open(D+'agreement_by_sentence.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
def rate(rs,f,m,lv=3): return (sum(1 for r in rs if r[f'{f}_{m}']>=lv) if lv==3 else sum(1 for r in rs if r[f'{f}_{m}']==lv))/len(rs) if rs else float('nan')
out=[]
def table(title,groups,m):
  out.append(f'\n### {title}({m})\n')
  out.append('| 区分 | n | '+' | '.join(F)+' |'); out.append('|'+'---|'*(len(F)+2))
  for name,rs in groups:
    out.append(f'| {name} | {len(rs)} | '+' | '.join(f'{rate(rs,f,m):.0%}' for f in F)+' |')
types=['否定','全称','因果','主語新規','数値','多義語','other','通常']
for m in ('strict','lenient'):
  table('全体・言語別',[('全60',rows),('JA',[r for r in rows if r['lang']=='JA']),('EN',[r for r in rows if r['lang']=='EN']),('NG由来40',[r for r in rows if r['group']=='NG']),('通常20',[r for r in rows if r['group']=='NORMAL'])],m)
  table('文種別',[(t if t!='other' else 'その他NG(範囲/付加)',[r for r in rows if r['type']==t]) for t in types],m)
  out.append(f'\n### 3段階分布(全60、{m}): 3/3一致 / 2/3一致 / 全不一致\n')
  out.append('| field | 3/3 | 2/3 | 全不一致 |'); out.append('|---|---|---|---|')
  for f in F: out.append(f'| {f} | {rate(rows,f,m,3):.1%} | {rate(rows,f,m,2):.1%} | {rate(rows,f,m,0):.1%} |')
open(D+'_tables.md','w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
