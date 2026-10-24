"""はてなブックマークのコメント取得(公開JSON API・HTTP GETのみ)。使い方: hatena_01.py URL...  出力: sources/hatena_<hash>.json (投稿者IDは保存しない)"""
import sys,json,hashlib,requests,os
H={"User-Agent":"Mozilla/5.0 (research; eigo-radio FYT24)"}
OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"sources")
for u in sys.argv[1:]:
    r=requests.get("https://b.hatena.ne.jp/entry/jsonlite/",params={"url":u},headers=H,timeout=25)
    try: d=r.json()
    except Exception: print(u,r.status_code,'nojson'); continue
    if not d: print(u,'none'); continue
    cm=[{"comment":b.get("comment",""),"timestamp":b.get("timestamp")} for b in d.get("bookmarks",[]) if b.get("comment")]
    h=hashlib.md5(u.encode()).hexdigest()[:8]
    json.dump({"url":u,"title":d.get("title"),"count":d.get("count"),"comments":cm},open(os.path.join(OUT,f"hatena_{h}.json"),"w",encoding="utf8"),ensure_ascii=False,indent=0)
    print(u[:80],d.get("count"),len(cm),h)
