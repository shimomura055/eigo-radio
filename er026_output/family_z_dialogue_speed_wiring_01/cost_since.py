import json,sys,collections
p,ts=sys.argv[1],sys.argv[2]
c=collections.Counter(); jpy=0
for l in open(p,encoding="utf-8"):
    try:d=json.loads(l)
    except: continue
    if d.get("timestamp","")>=ts:
        c[(d.get("stage"),d.get("provider"),d.get("api"),d.get("model_id"))]+=1
        jpy+=d.get("cost_jpy") or d.get("estimated_cost_jpy") or 0
for k,v in sorted(c.items(),key=str): print(v,k)
print("sum_cost_field",jpy)
