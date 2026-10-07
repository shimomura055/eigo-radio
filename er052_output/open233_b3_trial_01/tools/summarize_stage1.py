import json,glob,os
rows=[];tot=0
for p in sorted(glob.glob("runs/*/nb/*/b*/cost.json")):
    c=json.load(open(p,encoding="utf-8"));parts=p.replace("\\","/").split("/")
    pv=json.load(open(os.path.dirname(p)+"/b3_variant_provenance.json",encoding="utf-8"))
    rows.append({"slug":parts[1],"variant":parts[3],"b":parts[4],"total_jpy":c.get("total_jpy"),"exit_reason":pv.get("exit_reason"),"instruction_sha256":pv.get("instruction_sha256"),"full_prompt_sha256":pv.get("full_prompt_sha256"),"sent_match":(pv.get("b3_prompt_sent_sha256_list") or [None])[0]==pv.get("full_prompt_sha256"),"n_sent":len(pv.get("b3_prompt_sent_sha256_list") or [])})
    tot+=c.get("total_jpy") or 0
json.dump({"stage":"1_b3_brief_generation","runs":len(rows),"total_jpy":round(tot,2),"rows":rows},open("cost.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(rows),round(tot,3),sum(r["sent_match"] for r in rows),[r for r in rows if r["exit_reason"]!="completed"])
