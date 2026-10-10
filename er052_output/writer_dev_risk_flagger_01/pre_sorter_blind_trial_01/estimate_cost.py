# -*- coding: utf-8 -*-
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8"); sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE,"..","detectors"))
import flagger_lib as L
sysp=open(os.path.join(HERE,"prompt_presorter_01.txt"),encoding="utf-8").read()
bt=[open(os.path.join(HERE,"batch_text_%d.txt"%i),encoding="utf-8").read() for i in (1,2,3)]
inp=[L.estimate_tokens(sysp)+L.estimate_tokens("Items (%d):\n\n"%n+t) for n,t in zip((10,10,9),bt)]
IN=sum(inp)
vis=29*130   # 見積: 1件 reason 2-4文+フィールド 約130 tokens
rows=[]
M={"gpt-6-luna":(0.1,0.01,0.5,"登録(PROJECT_INTERNAL_RECORD)"),"gpt-6.1-sol":(2.0,0.1,10.0,"登録(OFFICIAL_PRICING_PAGE_FETCHED)"),"gpt-6-astra":(10.0,1.0,50.0,"登録(OFFICIAL_PRICING_PAGE_FETCHED)")}
scen={"central":vis+3*5000,"high":vis+3*12000}   # 見積: reasoning_tokensはバッチ当たり中央5k/高位12k(Flagger実測は小件数で数百tokenのため上振れ側に置く)
out=dict(input_tokens_est_per_batch=inp,input_tokens_est_total=IN,visible_output_est=vis,scenarios=scen,models={})
for m,(pi,pc,po,src) in M.items():
    r={}
    for k,o in scen.items(): r[k]=dict(out_tok=o, usd=(IN*pi+o*po)/1e6, jpy=(IN*pi+o*po)/1e6*160)
    r["price"]=dict(input=pi,cached=pc,output=po,src=src)
    # 量産参考: 10記事/日 x 2.6件 = 26件/日、1件あたり=Trial/29
    f=26/29
    r["prod_ref_jpy_day_central"]=r["central"]["jpy"]*f; r["prod_ref_jpy_month30_central"]=r["central"]["jpy"]*f*30
    r["prod_ref_jpy_day_high"]=r["high"]["jpy"]*f; r["prod_ref_jpy_month30_high"]=r["high"]["jpy"]*f*30
    out["models"][m]=r
# UNAVAILABLE(参考のみ。単価は未登録=未確認。inventory記載の公式値: Fable 10/50, Sonnet 2/10, Opus 未確認)
ref={"claude-fable-5-1":(10,50),"claude-sonnet-5-5":(2,10)}
out["unavailable_reference"]={m:{k:dict(jpy=(IN*pi+o*po)/1e6*160) for k,o in scen.items()} for m,(pi,po) in ref.items()}
out["unavailable_reference"]["claude-opus-5-5"]="単価 未確認"
tot={k:sum(out["models"][m][k]["jpy"] for m in M) for k in scen}; out["total_runnable_jpy"]=tot
json.dump(out,open(os.path.join(HERE,"cost_estimate_01.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(json.dumps(out,ensure_ascii=False,indent=1))
