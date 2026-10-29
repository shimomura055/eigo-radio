import json,glob,os,sys
sys.stdout.reconfigure(encoding="utf-8")
for p in sorted(glob.glob(os.path.join(os.path.dirname(__file__),"..","out","*_AUDITV3.audit.json"))):
    a=json.load(open(p,encoding="utf-8")); print("###",a["cell"],a["map"])
    try:
        r=json.loads(a["raw"][a["raw"].index("{"):a["raw"].rindex("}")+1])
    except Exception as e: print("PARSE FAIL",a["raw"][:500]); continue
    for k,v in r["scores"].items(): print(k,a["map"][k],{x:v[x] for x in v if x!="issues"},"|"," / ".join(v.get("issues") or []))
    print("rank",[a["map"].get(x,x) for x in r["ranking_by_learning_value"]],"|",r["comment"])
