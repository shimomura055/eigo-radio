# -*- coding: utf-8 -*-
"""費用見積(API非呼び出し)。入力=実測char数(prompts/*, out/*/reply.md)。tokens/char比は未確認の仮定(low/mid/high)。"""
import json, os
R="../factlock_astra_e2e_trial_01/annotation"; USDJPY=160
inv=json.load(open("gt_inventory.json",encoding="utf-8"))
P=json.load(open("../writer_dev_risk_flagger_01/meta_rollback_crossmodel_01/xm_prices_01.json",encoding="utf-8"))["prices"]
# gpt-6-astra: er005_output/cost_baseline_01/pricing_snapshot.json (OFFICIAL_PRICING_PAGE_FETCHED) in10/cached1/out50
P["gpt-6-astra"]=dict(**{"in":10.0,"cached":1.0,"out":50.0},src="er005_output/cost_baseline_01/pricing_snapshot.json")
themes=[]
for r in inv:
    s=r["theme"]; pc=len(open(f"{R}/prompts/{s}__A.md",encoding="utf-8").read())-700  # 先頭のRead指示(約700字)を除いた依頼文
    rc=[len(open(f"{R}/out/{N}/{s}/reply.md",encoding="utf-8").read()) for N in "AB"]
    themes.append((s,pc,sum(rc)/2))
IN=sum(t[1] for t in themes)/len(themes); OUT=sum(t[2] for t in themes)/len(themes)
SC=dict(low=dict(tpc=0.5,reason=0,cache=0.0),mid=dict(tpc=0.75,reason=3000,cache=0.0),high=dict(tpc=1.0,reason=8000,cache=0.0))
def cost(model,calls,in_extra=1.0,sc="mid"):
    s=SC[sc]; pr=P[model]; it=IN*s["tpc"]*in_extra; ot=OUT*s["tpc"]+s["reason"]
    usd=calls*(it*pr["in"]+ot*pr["out"])/1e6
    return dict(calls=calls,in_tok_per_call=round(it),out_tok_per_call=round(ot),usd=round(usd,3),jpy=round(usd*USDJPY,1))
methods={"M-A/M-B shared A+B calls (verbatim)":(40,1.0),"M-C new-prompt sidecar-only (A only)":(20,1.15)}
res={"basis":dict(themes=len(themes),avg_prompt_chars=round(IN),avg_reply_chars=round(OUT),usdjpy=USDJPY,
     note="tokens/char(0.5/0.75/1.0)とreasoning tokens(0/3000/8000)は未確認の仮定。キャッシュ割引は見込まない。"),"prices":{k:P[k] for k in ("claude-sonnet-5","gpt-6.1-sol","gpt-6-astra")},"matrix":{}}
for m in ("claude-sonnet-5","gpt-6.1-sol","gpt-6-astra"):
    for name,(calls,ex) in methods.items():
        res["matrix"][f"{m} | {name}"]={sc:cost(m,calls,ex,sc) for sc in SC}
tot={sc:round(sum(v[sc]["jpy"] for k,v in res["matrix"].items() if "A+B" in k and not k.startswith("gpt-6-astra")),1) for sc in SC}
res["total_verbatim_2models_sonnet5_sol_jpy"]=tot
tot2={sc:round(sum(v[sc]["jpy"] for k,v in res["matrix"].items() if "A+B" in k),1) for sc in SC}
res["total_verbatim_3models_incl_astra_jpy"]=tot2
json.dump(res,open("estimate_01.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(json.dumps(res,ensure_ascii=False,indent=1))
