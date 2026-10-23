import sys,os,re,json,importlib.util,collections
sys.path.insert(0,os.getcwd())
sys.path.insert(0,sys.argv[1])
import er006_preprod_hardening_01_validation as new
spec=importlib.util.spec_from_file_location("er006_old",sys.argv[1]+"/er006_old.py");old=importlib.util.module_from_spec(spec);sys.modules["er006_old"]=old;spec.loader.exec_module(old)
pat=re.compile(r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)[ -](twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)\b",re.I)
exts=(".md",".json",".jsonl",".txt")
hits=collections.defaultdict(list);nfiles=0;nlines=0;diff=0
for root,ds,fs in os.walk("."):
    ds[:]=[d for d in ds if d not in (".git",".venv","node_modules","__pycache__")]
    for f in fs:
        if not f.endswith(exts):continue
        p=os.path.join(root,f)
        try:t=open(p,encoding="utf-8",errors="ignore").read()
        except: continue
        nfiles+=1
        if not pat.search(t):continue
        # unescape json strings
        for line in t.splitlines():
            if not pat.search(line):continue
            try: obj=json.loads(line); 
            except Exception: obj=None
            texts=[line]
            if obj is not None:
                def walk(o):
                    if isinstance(o,str):texts.append(o)
                    elif isinstance(o,dict):[walk(v) for v in o.values()]
                    elif isinstance(o,list):[walk(v) for v in o]
                walk(obj)
            for tx in texts:
                for m in pat.finditer(tx):
                    a=max(0,m.start()-60);seg=tx[a:m.end()+60]
                    nlines+=1
                    o=old.normalize_text(seg);n=new.normalize_text(seg)
                    if o!=n:
                        diff+=1;hits[p].append((m.group(0),o,n))
print("files",nfiles,"segments",nlines,"changed",diff)
for p,v in hits.items():
    c=collections.Counter(x[0].lower() for x in v)
    print(p,len(v),dict(c))
