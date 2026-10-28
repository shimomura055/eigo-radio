"""FYDR1B 海外情報源の本文取得(API0・LLM0)。HN=Algolia公開API, SE=公開API, Mumsnet=HTML, Reddit=公式RSS(robots.txt全面Disallowのため最小限のみ), Guardian=公開discussion API。
保存: sources_overseas/<site>_<n>.json (URL・取得日時・投稿日時・本文抜粋[短い]・取得方法・全文はlocal_full/へ=git管理外)"""
import requests,re,json,time,sys,os,html,datetime,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
H={"User-Agent":"Mozilla/5.0 (research; low-rate; contact owner) Chrome/120","Accept-Language":"en"}
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"sources_overseas"); FULL=os.path.join(ROOT,"local_full"); os.makedirs(OUT,exist_ok=True); os.makedirs(FULL,exist_ok=True)
def g(u,**k):
    r=requests.get(u,headers=H,timeout=30,**k); time.sleep(2); return r
def clean(t): return re.sub(r'\s+',' ',BeautifulSoup(html.unescape(t or ''),'html.parser').get_text(' ',strip=True))
def save(name,url,posted,method,title,comments,n_total,note=""):
    # comments: list of (author_hidden, date, text)
    now=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    json.dump({"url":url,"title":title,"fetched_at":now,"posted_at":posted,"method":method,"total_items_fetched":n_total,"note":note,
      "excerpts":[{"date":d,"text":t[:260]} for d,t in comments]},open(f"{OUT}/{name}.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
    json.dump([{"date":d,"text":t} for d,t in comments],open(f"{FULL}/{name}.json","w",encoding="utf8"),ensure_ascii=False)
    print("saved",name,n_total)
def hn(name,oid,pick):
    d=g(f"https://hn.algolia.com/api/v1/items/{oid}").json()
    kids=[k for k in d.get("children",[]) if k.get("text")]
    kids.sort(key=lambda k:-len(clean(k["text"])))
    cs=[(k["created_at"][:10],clean(k["text"])) for k in kids[:pick]]
    save(name,f"https://news.ycombinator.com/item?id={oid}",d["created_at"],"Algolia HN API items/<id>",d.get("title"),cs,len(kids))
def se(name,qid,site="workplace"):
    q=g(f"https://api.stackexchange.com/2.3/questions/{qid}?site={site}&filter=withbody").json()["items"][0]
    a=g(f"https://api.stackexchange.com/2.3/questions/{qid}/answers?site={site}&filter=withbody&sort=votes&pagesize=6").json()["items"]
    cs=[(datetime.datetime.utcfromtimestamp(q["creation_date"]).strftime("%Y-%m-%d"),"[QUESTION] "+clean(q["body"]))]+[(datetime.datetime.utcfromtimestamp(x["creation_date"]).strftime("%Y-%m-%d"),f"[ANSWER score={x['score']}] "+clean(x["body"])) for x in a]
    save(name,q["link"],datetime.datetime.utcfromtimestamp(q["creation_date"]).isoformat(),"Stack Exchange API 2.3",html.unescape(q["title"]),cs,len(a)+1)
def mn(name,url):
    r=g(url); s=BeautifulSoup(r.text,"html.parser")
    posts=[clean(x.get_text(" ")) for x in s.select("div[class*=post-content], div.post-body, [data-testid=post-content], article")]
    ttl=s.find("title").get_text() if s.find("title") else ""
    dm=re.search(r'datePublished"?\s*[:=]\s*"([^"]+)"',r.text); 
    posts=[p for p in posts if len(p)>40]
    save(name,url,dm.group(1) if dm else None,"HTML GET + BeautifulSoup",ttl,[(None,p) for p in posts[:8]],len(posts),note=f"http={r.status_code}")
def reddit(name,url):
    r=g(url.rstrip('/')+"/.rss"); 
    if r.status_code!=200: print("reddit fail",r.status_code); return
    ns={"a":"http://www.w3.org/2005/Atom"}; root=ET.fromstring(r.text)
    es=root.findall("a:entry",ns)
    cs=[(e.find("a:updated",ns).text[:10],clean(e.find("a:content",ns).text if e.find("a:content",ns) is not None else "")) for e in es]
    cs=[c for c in cs if len(c[1])>30]
    ttl=root.find("a:title",ns).text
    save(name,url,es[-1].find("a:updated",ns).text if es else None,"Reddit official RSS (comments feed)",ttl,cs[:8],len(cs),note="entries ordered newest-first; robots.txt Disallow:/ ")
def guardian(name,pid,weburl):
    d=g(f"https://discussion.theguardian.com/discussion-api/discussion{pid}?pageSize=40&orderBy=mostRecommended").json()["discussion"]
    cs=[(c["isoDateTime"][:10],clean(c["body"])) for c in d["comments"] if len(c["body"])>150][:8]
    save(name,weburl,None,"Guardian discussion API (public, no key)",d["title"],cs,d["commentCount"],note=f"commentCount={d['commentCount']} sorted by mostRecommended")
if __name__=="__main__":
    exec(open(sys.argv[1]).read())
