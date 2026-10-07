import json,re,unicodedata,itertools,collections,sys
sys.stdout.reconfigure(encoding='utf-8')
B='er052_output/open233_stage0_01/'; D=B+'stability_v1/'
S={p['sid']:p for p in json.load(open(B+'stability/sentences.json',encoding='utf-8'))}
R=collections.defaultdict(list)
for l in open(D+'results.jsonl',encoding='utf-8'):
  r=json.loads(l); R[r['sid']].append(r)
def nz(s): return re.sub(r'[\s\W_「」『』、。,.]+','',unicodedata.normalize('NFKC',str(s)).lower())
def bg(s):
  s=nz(s); return {s[i:i+2] for i in range(len(s)-1)} or {s}
def jac(a,b):
  A,B_=bg(a),bg(b); return len(A&B_)/len(A|B_) if A|B_ else 1
def txt(a,b,m):
  x,y=nz(a),nz(b)
  if x==y: return True
  if m=='strict': return False
  return (bool(x) and bool(y) and (x in y or y in x)) or jac(a,b)>=0.5
def subj(a,b,m):
  if a['subject_omitted']!=b['subject_omitted']: return False
  return True if a['subject_omitted'] else txt(a['subject'],b['subject'],m)
F={'subject':lambda a,b,m:subj(a[0],b[0],m),
 'predicate':lambda a,b,m:a[0]['predicate']==b[0]['predicate'],
 'polarity':lambda a,b,m:a[0]['polarity']==b[0]['polarity'],
 'modality':lambda a,b,m:a[0]['modality']==b[0]['modality'],
 'scope_coarse':lambda a,b,m:set(a[1]['qualifier_types'])==set(b[1]['qualifier_types']),
 'scope_any':lambda a,b,m:bool(a[1]['qualifier_types'])==bool(b[1]['qualifier_types'])}
def level(f,runs,m):
  k=sum(F[f](a,b,m) for a,b in itertools.combinations([(r['s1'],r['s2']) for r in runs],2)); return 3 if k==3 else (2 if k else 0)
rows=[]
for sid,runs in R.items():
  assert len(runs)==3 and all(r['s1'] and r['s2'] for r in runs),sid
  p=S[sid]; row=dict(sid=sid,lang=p['lang'],type=p['type'],group=p['group'],text=p['text'])
  for m in ('strict','lenient'):
    for f in F: row[f'{f}_{m}']=level(f,runs,m)
  rows.append(row)
json.dump(rows,open(D+'agreement_by_sentence_v1.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
def rate(rs,f,m): return sum(r[f'{f}_{m}']==3 for r in rs)/len(rs)
out=[]
for m in ('strict','lenient'):
  out.append(f'\n#### {m}\n'); out.append('| 区分 | n | '+' | '.join(F)+' |'); out.append('|'+'---|'*(len(F)+2))
  gs=[('全60',rows),('JA',[r for r in rows if r['lang']=='JA']),('EN',[r for r in rows if r['lang']=='EN']),('NG由来40',[r for r in rows if r['group']=='NG']),('通常20',[r for r in rows if r['group']=='NORMAL'])]
  gs+=[(t,[r for r in rows if r['type']==t]) for t in ['否定','全称','因果','主語新規','数値','多義語','other']]
  for n,rs in gs: out.append(f'| {n} | {len(rs)} | '+' | '.join(f'{rate(rs,f,m):.0%}' for f in F)+' |')
open(D+'_tables_v1.md','w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
# disagreement examples
for f in ('subject','predicate','scope_coarse'):
  print('\n##',f)
  n=0
  for r in rows:
    if r[f'{f}_lenient']<3 and n<8:
      n+=1; rs=R[r['sid']]
      v=[ (x['s1']['subject'] or '(省略)') if f=='subject' else x['s1']['predicate'] if f=='predicate' else ','.join(x['s2']['qualifier_types']) or '-' for x in rs]
      print(r['sid'],r['text'][:40],'|',' / '.join(v))
