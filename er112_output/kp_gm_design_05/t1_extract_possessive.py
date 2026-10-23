import json,glob,re,sys,collections
POSS={"my","your","his","her","its","their","our","yours","theirs"}
PRON={"you","they","he","she"}
REFL={"yourself","himself","herself","themselves"}
rows={}
for f in glob.glob("**/keywords_canonicalized.json",recursive=True):
    if ".git" in f: continue
    try: d=json.load(open(f,encoding="utf-8"))
    except Exception: continue
    for it in d.get("items",[]):
        disp=it.get("display_phrase") or ""; kp=it.get("key_phrase") or ""
        toks=re.findall(r"[A-Za-z']+",disp.lower())
        if not any(t in POSS|PRON|REFL for t in toks): continue
        key=(it.get("source_sentence"),disp,kp)
        r=rows.setdefault(key,{"display":disp,"kp":kp,"sent":it.get("source_sentence"),"reason":it.get("normalization_reason"),"files":[]})
        r["files"].append(f)
out=[]
for k,r in rows.items():
    r["nfiles"]=len(r["files"]); r["file"]=r["files"][0]; del r["files"]
    out.append(r)
json.dump(out,open("er112_output/kp_gm_design_05/t1_possessive_items.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(rows))
c=collections.Counter()
for r in out:
    dt=[t for t in re.findall(r"[A-Za-z']+",r["display"].lower()) if t in POSS|PRON|REFL]
    kt=[t for t in re.findall(r"[A-Za-z']+",r["kp"].lower()) if t in ("one's","someone's","somebody's","someone","one","oneself","somebody")]
    c[(tuple(dt),tuple(kt))]+=1
for k,v in sorted(c.items(),key=lambda x:-x[1]): print(v,k)
