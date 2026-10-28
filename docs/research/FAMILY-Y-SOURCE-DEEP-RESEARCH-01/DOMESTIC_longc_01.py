"""cacheテキストから長めのコメントだけ抽出して表示(閲読補助)。
使い方: python DOMESTIC_longc_01.py URL minlen [maxn] [splitregex]"""
import sys,os,re,hashlib
HERE=os.path.dirname(os.path.abspath(__file__)); C=os.path.join(HERE,"_cache_uncommitted")
u=sys.argv[1]; ml=int(sys.argv[2]); mx=int(sys.argv[3]) if len(sys.argv)>3 else 30
rx=sys.argv[4] if len(sys.argv)>4 else r'(?m)^(?=\d+\.\s*匿名)'
t=open(os.path.join(C,hashlib.md5(u.encode()).hexdigest()[:10]+".txt"),encoding="utf-8").read()
parts=re.split(rx,t)
n=0
for p in parts[1:]:
    body=re.sub(r'\s+',' ',p).replace('[ 通報 ] 人による','')
    if len(body)>=ml:
        print('##',body[:int(os.environ.get("MAXC","700"))]); n+=1
        if n>=mx: break
print('total parts',len(parts))
