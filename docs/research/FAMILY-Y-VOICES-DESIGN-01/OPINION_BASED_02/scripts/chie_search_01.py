"""Yahoo!知恵袋サイト内検索でQ&A URLを集める(HTTP GETのみ、API 0)。出力: sources/chie_urls_01.json"""
import sys,re,json,time,requests
from bs4 import BeautifulSoup
import search_01 as s
qs=["再配達 有料化","再配達 有料","再配達 有料化 賛成","再配達 有料化 反対","再配達 有料化 配達員","再配達 有料化 共働き","置き配 再配達 有料","宅配ボックス 再配達 有料化","再配達 料金 取るべき","再配達 無料 おかしい","不在票 再配達 有料 家にいたのに","再配達 有料 高齢者","再配達 有料 時間指定 来ない"]
out={}
for q in qs:
    for pg in (1,2,3):
        try:
            r=requests.get("https://chiebukuro.yahoo.co.jp/search",params={"p":q,"type":"smt","page":pg},headers=s.H,timeout=25); r.encoding='utf-8'
        except Exception as e: print('ERR',q,pg,e); continue
        soup=BeautifulSoup(r.text,'html.parser'); n=0
        for a in soup.find_all('a',href=True):
            m=re.search(r'detail\.chiebukuro\.yahoo\.co\.jp/qa/question_detail/(q\d+)',a['href'])
            if m and m.group(1) not in out:
                out[m.group(1)]={"url":"https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/"+m.group(1),"title":a.get_text(' ',strip=True)[:80],"q":q}; n+=1
        print(q,pg,r.status_code,n,len(out)); time.sleep(1.5)
json.dump(out,open('../sources/chie_urls_01.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
