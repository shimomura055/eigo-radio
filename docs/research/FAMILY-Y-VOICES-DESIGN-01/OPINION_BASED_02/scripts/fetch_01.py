"""FYT24 収集: URL一覧を取得して sources/pages/ に保存(HTTP GETのみ・API 0)。使い方: fetch_01.py urls.txt
保存: 連番_ドメイン.txt (先頭に URL/FETCHED/HTTP を付与)"""
import sys, os, re, time, datetime, hashlib, requests, urllib.parse
from bs4 import BeautifulSoup
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36","Accept-Language":"ja"}
OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"sources","pages")
def to_text(html):
    s=BeautifulSoup(html,"html.parser")
    for t in s(["script","style","noscript","nav","footer","header"]): t.decompose()
    return re.sub(r"\n\s*\n+","\n",s.get_text("\n"))
def fetch(u):
    os.makedirs(OUT,exist_ok=True)
    h=hashlib.md5(u.encode()).hexdigest()[:8]
    dom=urllib.parse.urlparse(u).netloc.replace('www.','')
    fn=os.path.join(OUT,f"{dom}_{h}.txt")
    if os.path.exists(fn): return fn,'cached'
    try:
        r=requests.get(u,headers=H,timeout=30); 
        if r.encoding is None or r.encoding.lower() in('iso-8859-1',): r.encoding=r.apparent_encoding
        txt=to_text(r.text); code=r.status_code
    except Exception as e:
        txt='';code=str(e)[:60]
    open(fn,'w',encoding='utf-8').write(f"URL {u}\nFETCHED {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}\nHTTP {code}\nCHARS {len(txt)}\n"+txt)
    return fn,code
if __name__=="__main__":
    for l in open(sys.argv[1],encoding='utf8'):
        u=l.strip()
        if not u: continue
        fn,c=fetch(u); print(c,os.path.basename(fn),u[:90]); time.sleep(1.0)
