import re,json,os,sys,importlib.util,collections,time
sys.path.insert(0,os.getcwd())
import er078_asr_value_guard_01 as new
spec=importlib.util.spec_from_file_location("er078_old",sys.argv[1]);old=importlib.util.module_from_spec(spec);sys.modules["er078_old"]=old;spec.loader.exec_module(old)
CK=("canonical","canonical_text","expected","expected_text","source_text","script_text","clip_text","src","canon","original_text","tts_input","text")
AK=("asr","asr_text","primary_text","secondary_text","transcript","asr_transcript","primary_asr_text","secondary_asr_text","hyp","adopted_text","transcript_text")
exts=(".json",".jsonl")
pairs={};nfiles=0
for root,ds,fs in os.walk("."):
    ds[:]=[d for d in ds if d not in (".git",".venv","node_modules","__pycache__")]
    for f in fs:
        if not f.endswith(exts):continue
        p=os.path.join(root,f)
        try:t=open(p,encoding="utf-8",errors="ignore").read()
        except: continue
        nfiles+=1
        if not re.search(r"\d",t): continue
        objs=[]
        try: objs=[json.loads(t)]
        except Exception:
            for l in t.splitlines():
                try:objs.append(json.loads(l))
                except Exception:pass
        def walk(o):
            if isinstance(o,dict):
                cs=[o[k] for k in CK if isinstance(o.get(k),str) and re.search(r"\d|\b(one|two|three|ten|twenty|thirty)\b",o[k],re.I)]
                as_=[o[k] for k in AK if isinstance(o.get(k),str)]
                for c in cs:
                    for a in as_:
                        if c!=a and len(c)<3000 and len(a)<3000: pairs.setdefault((c,a),p)
                for v in o.values():walk(v)
            elif isinstance(o,list):[walk(v) for v in o]
        for o in objs:walk(o)
print("files",nfiles,"pairs",len(pairs),flush=True)
OK=("EQUAL","NO_VALUES","AMBIGUOUS")
chg=[];err=0;t0=time.time()
for (c,a),p in pairs.items():
    try:
        o=old.value_guard(c,a,"en").kind;n=new.value_guard(c,a,"en").kind
    except Exception as e:
        err+=1;continue
    if o!=n: chg.append((p,c,a,o,n))
print("errors",err,"changed",len(chg),"sec",int(time.time()-t0))
p2n=[x for x in chg if x[3] in OK and x[4] not in OK]
n2p=[x for x in chg if x[3] not in OK and x[4] in OK]
print("PASS->NG",len(p2n),"NG->PASS",len(n2p),"other",len(chg)-len(p2n)-len(n2p))
for p,c,a,o,n in chg[:40]:
    print("-",p[-70:],o,"->",n);print("   C:",c[:150]);print("   A:",a[:150])
