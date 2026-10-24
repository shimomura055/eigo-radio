import glob,re,os,sys,json
done={'d87b7a28','b48379b8','6e26dc46','6ff4a03c','ca97af7c','e752b894','63b8462a','824ed907'}
urls=json.load(open('../sources/chie_urls_01.json',encoding='utf8'))
out=[]
for f in sorted(glob.glob('../sources/pages/detail.chiebukuro*.txt')):
    h=f.split('_')[-1][:-4]
    if h in done: continue
    t=open(f,encoding='utf8').read()
    u=t.split('\n')[0][4:]
    for cut in ['あわせて知りたい','AIからのお助け回答','人気の質問']:
        i=t.find(cut)
        if i>0: t=t[:i]
    if '再配達' not in t: continue
    L=[l.strip() for l in t.split('\n')[4:]]
    keep=[]
    prev=None
    for l in L:
        if not l or re.fullmatch(r'[\d,]+',l) or l in('なるほど','そうだね','ありがとう','ThanksImg','共感した','さん','違反報告','間違いかも','質問者','並び順を変更する','新しい順','古い順','なるほど順') or l.startswith('この回答はいかがでしたか') or l==prev or l.startswith('xmlns'): continue
        keep.append(l); prev=l
    s='\n'.join(keep)
    if not re.search(r'有料|料金|手数料|お金',s): continue
    out.append(f"=== {os.path.basename(f)} {u[:75]}\n{s[:2600]}")
open('../sources/chie_digest_01.txt','w',encoding='utf8').write('\n\n'.join(out))
print(len(out),sum(len(x) for x in out))
