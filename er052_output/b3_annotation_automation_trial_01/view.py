import sys,os,re,json
sys.dont_write_bytecode=True
sys.argv=['x']
sys.path.insert(0,'.')
import annot_driver as D
def lenient(txt):
    t=txt.replace('\r\n','\n')
    m1=re.search(r"=== ANNOTATED_BRIEF_BEGIN ===\n(.*?)\n=== ANNOTATED_BRIEF_END ===",t,re.S)
    return m1.group(1) if m1 else None
def get(m,t,r):
    d=f'runs/{m}/{t}/rep{r}'
    if os.path.exists(d+'/annotated.md'): return D.rd(d+'/annotated.md'),'ok'
    rt=D.rd(d+'/reply.txt'); l=lenient(rt)
    return (l,'LENIENT(format-fail)') if l else (None,'STOP/none')
def show(t, which=None):
    p=D.paths(t); print('#'*10,t); print('--- BRIEF'); print(D.rd(p['brief']))
    inv={r['theme']:r for r in json.load(open('gt_inventory.json',encoding='utf-8'))}
    if t in inv and inv[t].get('final'): print('--- GT'); print(D.rd('../../'+inv[t]['final']))
    for m in ('luna','sonnet55'):
        for r in (1,2):
            if which and (m,r) not in which: continue
            x,st=get(m,t,r); print(f'--- {m} rep{r} [{st}] check=',[l for l in D.rd('cost_ledger_annot_01.jsonl').splitlines() if f'"{m}"' in l and f'"theme": "{t}"' in l and f'"rep": {r}' in l][0].split('"check": ')[1][:12])
            if x:
                # sections after Selected Facts only vs storyline
                print(x)
if __name__=='__main__': pass
def sf(x):
    i=x.find('## Selected Facts'); return x[i:] if i>=0 else x
def story(x):
    i=x.find('## Storyline'); j=x.find('## Selected Facts'); return x[i:j]
def show2(t):
    p=D.paths(t); print('#'*10,t); print('--- BRIEF'); print(D.rd(p['brief']))
    inv={r['theme']:r for r in json.load(open('gt_inventory.json',encoding='utf-8'))}
    gt=D.rd('../../'+inv[t]['final']) if t in inv and inv[t].get('final') else None
    if gt: print('--- GT'); print(gt)
    for m in ('luna','sonnet55'):
        for r in (1,2):
            x,st=get(m,t,r); ch=[l for l in D.rd('cost_ledger_annot_01.jsonl').splitlines() if f'"{m}"' in l and f'"theme": "{t}"' in l and f'"rep": {r}' in l][0].split('"check": ')[1][:12]
            print(f'--- {m} rep{r} [{st}] check={ch}')
            if not x: print('(no annotation)'); continue
            if gt and story(x)==story(gt): print('(storyline same as GT)')
            else: print(story(x))
            print(sf(x))
