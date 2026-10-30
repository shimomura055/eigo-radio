import sys,json,glob,math,re
sys.path.insert(0,__import__('os').path.dirname(__file__))
from ejh01_len_aligner_probe_01 import *
allg=[];bad=[]
for f in sorted(glob.glob('user_test/*/enduser/data/article.json')):
    a=json.load(open(f,encoding='utf-8')); nm=f.replace(chr(92),'/').split('/')[1][:30]
    for lv,L in a['levels'].items():
        for p in L['parts']:
            if not p.get('ja'): continue
            prs=list(zip(p['paragraphs'],p['ja'])) if len(p['paragraphs'])==len(p['ja']) else [(sum(p['paragraphs'],[]),'\n'.join(p['ja']))]
            for pa,ja in prs:
                en=[plain(s['html']) for s in pa]; j=jsplit(ja)
                r=sum(map(len,en))/max(1,sum(map(len,j)))
                for (e0,e1),(j0,j1) in align(en,j):
                    if e1==e0 or j1==j0: bad.append((nm,lv,p['label'],'UNPAIRED',en[e0:e1],j[j0:j1])); continue
                    E=' '.join(en[e0:e1]); J=''.join(j[j0:j1])
                    d=abs(math.log((len(E)+5)/(len(J)*r+5)))
                    de=set(re.findall(r'\d+',E.replace(',',''))); dj=set(re.findall(r'\d+',J.replace(',','').replace('，','')))
                    allg.append((d,nm,lv,p['label'],E,J,de!=dj and (de or dj), (e1-e0,j1-j0)))
allg.sort(key=lambda x:-x[0])
print(len(allg),'groups; unpaired',len(bad))
import collections
print(collections.Counter(x[7] for x in allg))
for x in allg[:12]: print(round(x[0],2),x[1],x[2],x[3],x[7],'\n  EN',x[4][:160],'\n  JA',x[5][:90],'\n  dig',x[6])
for x in bad[:5]: print(x)
print('digit-mismatch',sum(1 for x in allg if x[6]))
