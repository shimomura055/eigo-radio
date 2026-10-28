"""sources_domestic/*.json の short_excerpts が、取得済みcache本文(空白無視)に実在するか照合。cacheはcommit対象外のため、取得直後の同一環境でのみ再現可能。"""
import json,glob,os,re
HERE=os.path.dirname(os.path.abspath(__file__))
cache={}
for f in glob.glob(os.path.join(HERE,"_cache_uncommitted","*.txt")):
    cache[f]=re.sub(r"\s+","",open(f,encoding="utf-8").read())
ok=ng=0
for f in sorted(glob.glob(os.path.join(HERE,"sources_domestic","*.json"))):
    d=json.load(open(f,encoding="utf-8"))
    for e in d["short_excerpts"]:
        k=re.sub(r"\s+","",e)
        hit=any(k in t for t in cache.values())
        if hit: ok+=1
        else: ng+=1; print("NOT FOUND",os.path.basename(f),e[:50])
print("excerpts ok",ok,"notfound",ng)
