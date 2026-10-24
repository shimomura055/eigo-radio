"""FYT24 委任_24 収集: 検索(Yahoo!JAPAN/Bing)でURL候補を集める。API 0・LLM 0。結果は sources/search_*.json"""
import sys, json, re, requests, urllib.parse, base64, os
from bs4 import BeautifulSoup
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36","Accept-Language":"ja"}
OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"sources")
def yahoo(q, pages=(1,11)):
    res=[]
    for b in pages:
        r=requests.get("https://search.yahoo.co.jp/search",params={"p":q,"b":b},headers=H,timeout=25); r.encoding='utf-8'
        s=BeautifulSoup(r.text,'html.parser')
        for a in s.select('div.sw-Card__titleInner a, p.Algo__textListLinks a, div.sw-Card__title a, a.sw-Card__titleInner'):
            h=a.get('href') or ''
            if h.startswith('http') and 'yahoo.co.jp/search' not in h and 'search.yahoo' not in h: res.append((a.get_text(' ',strip=True),h))
        for a in s.select('div.AnswerVideoUniversal__listItemLink, a.AnswerVideoUniversal__listItemLink'):
            h=a.get('href') or ''
            if h.startswith('http'): res.append((a.get_text(' ',strip=True),h))
    return res
def bing(q):
    r=requests.get("https://www.bing.com/search",params={"q":q,"setlang":"ja","count":30},headers=H,timeout=25); r.encoding='utf-8'
    s=BeautifulSoup(r.text,'html.parser'); res=[]
    for a in s.select('li.b_algo h2 a'):
        h=a.get('href') or ''
        m=re.search(r'[?&]u=a1([^&]+)',h)
        if m:
            b=m.group(1); b+='='*(-len(b)%4)
            try: h=base64.urlsafe_b64decode(b).decode()
            except Exception: pass
        res.append((a.get_text(' ',strip=True),h))
    return res
def ddg(q):
    r=requests.post("https://html.duckduckgo.com/html/",data={"q":q},headers=H,timeout=25); r.encoding='utf-8'
    s=BeautifulSoup(r.text,'html.parser'); res=[]
    for a in s.select('a.result__a'):
        h=a.get('href') or ''
        m=re.search(r'uddg=([^&]+)',h)
        if m: h=urllib.parse.unquote(m.group(1))
        if h.startswith('//'): h='https:'+h
        res.append((a.get_text(' ',strip=True),h))
    return res


if __name__=="__main__":
    qs=[l.strip() for l in open(sys.argv[1],encoding='utf8') if l.strip()]
    allr={}
    import time
    for q in qs:
        time.sleep(4)
        for fn in (ddg,):
            try:
                for t,u in fn(q): allr.setdefault(u,{"title":t,"q":q,"engine":fn.__name__})
            except Exception as e: print("ERR",fn.__name__,q,e)
    json.dump(allr,open(sys.argv[2],'w',encoding='utf8'),ensure_ascii=False,indent=0)
    print(len(allr))
