import re,json,os,collections,sys,importlib.util
sys.path.insert(0,os.getcwd());sys.path.insert(0,sys.argv[1])
import er006_preprod_hardening_01_validation as new
spec=importlib.util.spec_from_file_location("er006_old",sys.argv[1]+"/er006_old.py");old=importlib.util.module_from_spec(spec);sys.modules["er006_old"]=old;spec.loader.exec_module(old)
pat=re.compile(r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)[ -](twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)\b",re.I)
CK=("canonical","canonical_text","expected","expected_text","text","source_text","script_text","clip_text")
AK=("asr","asr_text","primary_text","secondary_text","transcript","asr_transcript","primary_asr_text","secondary_asr_text")
files=[l.strip() for l in open(sys.argv[2]) if l.strip()]
pairs={}
for f in files:
    try:t=open(f,encoding="utf-8").read()
    except:continue
    objs=[]
    try: objs=[json.loads(t)]
    except:
        for l in t.splitlines():
            try:objs.append(json.loads(l))
            except:pass
    def walk(o):
        if isinstance(o,dict):
            cs=[o[k] for k in CK if isinstance(o.get(k),str)]
            as_=[o[k] for k in AK if isinstance(o.get(k),str)]
            for c in cs:
                for a in as_:
                    if pat.search(c) or pat.search(a):
                        pairs[(c,a)]=f
            for v in o.values():walk(v)
        elif isinstance(o,list):[walk(v) for v in o]
    for o in objs:walk(o)
print("pairs",len(pairs))
def j(m,c,a):
    try:
        r=m.classify_asr_match(c,a)
        return (bool(r.should_pass), r.classification if hasattr(r,'classification') else None)
    except Exception as e:
        return ("ERR",str(e)[:50])
chg=[]
for (c,a),f in pairs.items():
    jo=j(old,c,a);jn=j(new,c,a)
    if jo!=jn: chg.append((f,c,a,jo,jn))
print("judgment-changed",len(chg))
for f,c,a,jo,jn in chg:
    print("-",f.split("/")[-2:],jo,"->",jn);print("   C:",c[:160]);print("   A:",a[:160])
