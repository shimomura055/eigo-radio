import sys,re
t=open(sys.argv[1],encoding='utf8').read()
for cut in ['あわせて知りたい','関連する質問','人気の質問']:
    i=t.find(cut)
    if i>0: t=t[:i]
lim=int(sys.argv[2]) if len(sys.argv)>2 else 6000
t=re.sub(r'\n(なるほど|そうだね|ありがとう|ThanksImg)\n','\n',t)
print(t[:lim])
