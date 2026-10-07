import json,sys,os,time,threading
sys.path.insert(0,'.')
sys.stdout.reconfigure(encoding='utf-8')
from concurrent.futures import ThreadPoolExecutor
import er052_open233_self_recovery_stage2_production_01 as s2p
import er003_v1_en_direct_vfl_01_generate as vfl
D='er052_output/open233_stage0_01/stability_v1/'
MODEL='gpt-6-luna'; EFFORT='high'; REPS=3; BUDGET=25.0
PRICE=(0.10,0.01,0.50); USD_JPY=156.88
limit=int(sys.argv[1]) if len(sys.argv)>1 else None
out=D+('results_smoke.jsonl' if limit else 'results.jsonl')
sc=json.load(open(D+'schema_v1.json',encoding='utf-8'))
sents=json.load(open('er052_output/open233_stage0_01/stability/sentences.json',encoding='utf-8'))
if limit: sents=sents[:limit]
P1=("次の1文について、主述語節(文の主張の核となる節)を読み取り、その主語・述語分類・肯定/否定・断定/推定/伝聞を答えてください。文以外の情報や常識による補完はしないこと。\n"
"- 主語が文中に語句として無い場合(省略・命令・受身で動作主なし等)は subject_omitted=true、subject は空文字。補って埋めない。\n"
"- subject は文中の表層語句をそのまま使う。\n- 述語は列挙値から最も近いものを1つ。\n\n[文]\n")
P2=("次の1文と、その主語・述語(固定済み)について、主語や述語を限定する語が文中にあるかを答えてください。限定語のタイプ(主体限定=誰が/誰に限る、範囲限定=一部・全体・だけ・のみ等、意図限定=〜のために・つもり等、条件限定=もし・〜なら等、時間限定=当面・現時点・今回等、程度・数量限定=約・少なくとも等)を該当するものだけ列挙し、限定語の表層語句も書いてください。無ければ空配列。文以外の情報は使わない。\n\n")
client=vfl.get_client()
lock=threading.Lock(); st={'cost':0.0,'calls':0,'fail':0,'stop':False}
def cost(u):
  it,ct,ot=(u.get(k) or 0 for k in ('input_tokens','cached_input_tokens','output_tokens'))
  return (max(it-ct,0)/1e6*PRICE[0]+ct/1e6*PRICE[1]+ot/1e6*PRICE[2])*USD_JPY
def call(prompt,s):
  r=client.responses.create(model=MODEL,reasoning={'effort':EFFORT},text={'format':{'type':'json_schema',**s}},input=[{'role':'user','content':prompt}])
  return json.loads(r.output_text),s2p._extract_usage(r)
def one(args):
  p,rep=args
  if st['stop']: return None
  err=None;s1=s2=None;c=0
  for _ in (1,2):
    try:
      s1,u1=call(P1+p['text'],sc['stage1']); c+=cost(u1)
      fixed=f"[文]\n{p['text']}\n[固定済み] 主語: {'(省略)' if s1['subject_omitted'] else s1['subject']} / 述語分類: {s1['predicate']} / {s1['polarity']}"
      s2,u2=call(P2+fixed,sc['stage2']); c+=cost(u2); err=None;break
    except Exception as e: err=repr(e)[:300]
  with lock:
    st['cost']+=c;st['calls']+=1
    if err: st['fail']+=1
    if st['cost']>=BUDGET: st['stop']=True
    open(out,'a',encoding='utf-8').write(json.dumps(dict(sid=p['sid'],rep=rep,s1=s1,s2=s2,jpy=round(c,6),error=err),ensure_ascii=False)+'\n')
if os.path.exists(out): os.remove(out)
jobs=[(p,r) for p in sents for r in range(REPS)]
t0=time.time()
with ThreadPoolExecutor(6) as ex: list(ex.map(one,jobs))
json.dump(dict(model=MODEL,effort=EFFORT,sentence_runs=st['calls'],api_calls_expected=2*st['calls'],failed_runs=st['fail'],total_jpy=round(st['cost'],4),budget_jpy=BUDGET,stopped_by_budget=st['stop'],elapsed_s=round(time.time()-t0,1),note='smoke' if limit else 'full'),open(D+('cost_smoke.json' if limit else 'cost.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(st)
