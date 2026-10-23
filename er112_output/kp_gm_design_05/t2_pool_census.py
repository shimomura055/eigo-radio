import json,glob,os,collections,re
pool={}
for f in glob.glob("**/keywords_canonicalized.json",recursive=True):
    if ".git" in f or "kp_gm_trial" in f: continue
    try: d=json.load(open(f,encoding="utf-8"))
    except Exception: continue
    for it in d.get("items",[]):
        kp=(it.get("key_phrase") or "").strip().lower()
        if not kp: continue
        pool.setdefault(kp,[]).append((f,it.get("japanese_gloss"),it.get("source_sentence")))
print("distinct key_phrase (excl. er112 trial dirs):",len(pool))
wc=collections.Counter(len(k.split()) for k in pool)
print("word counts",sorted(wc.items()))
# distinct by source_sentence+kp
print("distinct (kp,sentence):",len({(k,s) for k,v in pool.items() for _,_,s in v}))
# article dirs holding article.md?
print(len(glob.glob("er019_output/**/article*.md",recursive=True)),"article md in er019")
json.dump({k:[(a,b,c) for a,b,c in v[:1]] for k,v in pool.items()},open("er112_output/kp_gm_design_05/t2_pool_census.json","w",encoding="utf-8"),ensure_ascii=False)
