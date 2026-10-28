import json,sys,collections
tot=collections.Counter(); 
for f in "XYZ":
    d=json.load(open(sys.argv[1]+f"/diff_{f}.json",encoding="utf-8"))
    c=collections.Counter(r["change"].split("(")[0] for r in d["rows"]); print(f,dict(c),"errors",len(d["errors"]))
    for r in d["rows"]:
        if r["change"]!="UNCHANGED":
            print("  ",r["change"][:8],r["path"].split("/",3)[-1][:70],r["segment"],r["old_violations"],"->",r["new_violations"],r["warning"])
