import sys,os,json
sys.dont_write_bytecode=True
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from post_en_common import *
man=load_manifest()
K={ 'U02':['not crude oil prices overall'],'X09':['oil prices shot up','oil prices made a dramatic move'],
 'U03':['has not disclosed their capabilities','no specific system names or attack capabilities'],'X10':['blow up Earth'],
 'U05':['In one line','BYD is recalling 183,211'],'U07':['copyright management information','AI Lawsuits Are About More Than Money'],
 'X11':['put articles together'],'U08':['does not explain how the two are connected']}
out={}
for u in man['units']:
    if u['unit'] in K:
        unit,f,ss=build_unit(u,man)
        out[u['unit']]=[]
        for s in ss:
            if any(k in s['text'] for k in K[u['unit']]): out[u['unit']].append([s['sid'],s['text']])
json.dump(out,open('known_sentence_map_01.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for k,v in out.items():
    for sid,t in v: print(k,sid,t[:230].replace('\n',' '))
print({a:b for a,b in [(x,sha(A.antenna_system(x)) if hasattr(sys.modules['antenna_prompts'],'sha') else 0) for x in (3,4)]})
