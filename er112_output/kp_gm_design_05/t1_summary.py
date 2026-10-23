import json,re,collections,io,contextlib,importlib.util,glob,os
spec=importlib.util.spec_from_file_location('rt','er112_output/kp_gm_design_05/t1_referent_table.py')
with contextlib.redirect_stdout(io.StringIO()):
    rt=importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
items=json.load(open('er112_output/kp_gm_design_05/t1_possessive_items.json',encoding='utf-8'))
def gold(ref): return {"self":"one's","self_group":"one's","other":"someone's","nonperson":"NONE","keep":"NONE"}[ref]
def grp(f):
    f=f.replace(os.sep,'/')
    return 'er112_trial' if 'kp_gm_trial' in f else 'production_artifacts'
tab=collections.defaultdict(lambda:[0,0,0])  # group -> distinct,ok,mismatch
art=collections.defaultdict(lambda:[0,0])
mm=[]
for r in items:
    ref=rt.REF[r['display']][0]; c=rt.cls(r['kp'])
    if c=='kept': continue
    g=grp(r['file']); ok= (gold(ref)==c)
    tab[g][0]+=1; tab[g][1 if ok else 2]+=1
    art[g][0]+=r['nfiles']; 
    if not ok: art[g][1]+=r['nfiles']; mm.append((g,r['display'],r['kp'],ref,r['nfiles']))
print(dict(tab)); print(dict(art)); 
for m in mm: print(m)
# its->one's
its=[r for r in items if re.search(r'\bits\b',r['display'].lower()) and rt.cls(r['kp'])=="one's"]
print('its->one\'s distinct',len(its),[ (r['display'],rt.REF[r['display']][0]) for r in its])
kept=[(r['display'],rt.REF[r['display']][0]) for r in items if rt.cls(r['kp'])=='kept']
print('kept (not generalized) distinct',len(kept),collections.Counter(k[1] for k in kept))
