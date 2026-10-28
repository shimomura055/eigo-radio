import urllib.request,hashlib,json,os,re
base="https://shimomura055.github.io/eigo-radio/user_test/paycheck_personality_e2e_02/"
root="user_test/paycheck_personality_e2e_02"
files=["index.html"]+["audio/"+f for f in sorted(os.listdir(root+"/audio"))]
out={"url":base,"n_assets":len(files)-1,"bad":[],"files":{}}
for f in files:
    d=urllib.request.urlopen(urllib.request.Request(base+f,headers={"Cache-Control":"no-cache"})).read()
    s=urllib.request.urlopen(base+f).status
    loc=open(f"{root}/{f}","rb").read()
    m=hashlib.sha256(d).hexdigest()==hashlib.sha256(loc).hexdigest()
    out["files"][f]={"status":s,"len":len(d),"sha16":hashlib.sha256(d).hexdigest()[:16],"match_repo":m}
    if s!=200 or len(d)==0 or not m: out["bad"].append(f)
h=urllib.request.urlopen(base+"index.html").read().decode()
out["markers"]={k:h.count(k) for k in ["Key Phrase","Preview","Full Story Part 1","Full Story Part 2","Comment 1","Comment 2","Comment 3","Comment 4","In One Line"]}
json.dump(out,open("docs/research/FX-PAYCHECK-PERSONALITY-FINAL-PUBLISH-01/live_verify_01.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(files),"bad",out["bad"],out["markers"])
