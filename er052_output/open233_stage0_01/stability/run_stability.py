import json,sys,os,time,threading
sys.path.insert(0,'.')
sys.stdout.reconfigure(encoding='utf-8')
from concurrent.futures import ThreadPoolExecutor
import er052_open233_self_recovery_stage2_production_01 as s2p
import er003_v1_en_direct_vfl_01_generate as vfl
D='er052_output/open233_stage0_01/stability/'
MODEL='gpt-6-luna'; EFFORT='high'; REPS=3; BUDGET=90.0
PRICE=(0.10,0.01,0.50); USD_JPY=156.88
limit=int(sys.argv[1]) if len(sys.argv)>1 else None
out=D+('results_smoke.jsonl' if limit else 'results.jsonl')
schema=json.load(open(D+'schema_v0.json',encoding='utf-8'))
sents=json.load(open(D+'sentences.json',encoding='utf-8'))
if limit: sents=sents[:limit]
PROMPT=("次の1文から、関係(誰が/何を/どうした)を構造化して抽出してください。文以外の情報(台帳・前後文・常識による補完)は使わず、この文だけから読み取ってください。\n"
"- subject/object/scope_qualifiers は文中の表層語句をそのまま使う(言い換え・翻訳・補完をしない)。主語が文に無ければ subject は『(省略)』。\n"
"- predicate_normalized は列挙値から最も近いものを1つ選ぶ。\n"
"- polarity は文の主張が否定(〜ない/〜ではなく/〜ありません等)か肯定か。\n"
"- scope_qualifiers には限定語(一部・当面・全体・意図・条件・時間・場所の限定など)を列挙。\n"
"- numbers は数値表現を算用数字+単位に正規化。\n- modality は断定/推定(かもしれない等)/伝聞(と説明した等)。\n\n[文]\n")
client=vfl.get_client()
lock=threading.Lock(); st={'cost':0.0,'calls':0,'fail':0,'stop':False}
def cost(u):
  it,ct,ot=(u.get(k) or 0 for k in ('input_tokens','cached_input_tokens','output_tokens'))
  return (max(it-ct,0)/1e6*PRICE[0]+ct/1e6*PRICE[1]+ot/1e6*PRICE[2])*USD_JPY
def one(args):
  p,rep=args
  if st['stop']: return None
  err=None;parsed=None;usage={}
  for _ in (1,2):
    try:
      r=client.responses.create(model=MODEL,reasoning={'effort':EFFORT},text={'format':{'type':'json_schema',**schema}},
        input=[{'role':'user','content':PROMPT+p['text']}])
      parsed=json.loads(r.output_text);usage=s2p._extract_usage(r);err=None;break
    except Exception as e: err=repr(e)[:300]
  c=cost(usage)
  with lock:
    st['cost']+=c;st['calls']+=1
    if err: st['fail']+=1
    if st['cost']>=BUDGET: st['stop']=True
    rec=dict(sid=p['sid'],rep=rep,parsed=parsed,usage=usage,jpy=round(c,6),error=err)
    open(out,'a',encoding='utf-8').write(json.dumps(rec,ensure_ascii=False)+'\n')
  return rec
if os.path.exists(out): os.remove(out)
jobs=[(p,r) for p in sents for r in range(REPS)]
t0=time.time()
with ThreadPoolExecutor(6) as ex: list(ex.map(one,jobs))
json.dump(dict(model=MODEL,effort=EFFORT,calls=st['calls'],failed_calls=st['fail'],total_jpy=round(st['cost'],4),budget_jpy=BUDGET,
 stopped_by_budget=st['stop'],pricing='gpt-6-luna in0.10/cached0.01/out0.50 USD per 1M, USD_JPY 156.88 (same as s2p)',elapsed_s=round(time.time()-t0,1),
 note='smoke' if limit else 'full'),open(D+('cost_smoke.json' if limit else 'cost.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(st)
