import re,difflib,sys
a=open(sys.argv[1],encoding='utf-8').read(); b=open(sys.argv[2],encoding='utf-8').read()
sp=lambda s:re.sub(r'(<)',r'\n\1',s).split('\n')
for l in difflib.unified_diff(sp(a),sp(b),lineterm='',n=0): print(l[:300])
