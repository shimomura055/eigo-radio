import json,glob,re,os,collections,importlib.util,sys
sys.path.insert(0,'er112_output/kp_gm_design_05')
spec=importlib.util.spec_from_file_location('rt','er112_output/kp_gm_design_05/t1_referent_table.py')
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    rt=importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
REF=rt.REF
tot=collections.Counter()
for f in glob.glob('er112_output/kp_gm_trial_0*/**/keywords_canonicalized.json',recursive=True):
    f=f.replace(os.sep,'/')
    if not re.search(r'runs/[^/]+/rep\d',f): continue
    for it in json.load(open(f,encoding='utf-8'))['items']:
        dp,kp=it['display_phrase'],it['key_phrase']
        if dp not in REF: continue
        ref=REF[dp][0]; c=rt.cls(kp)
        tot[(ref,c)]+=1
print(sorted(tot.items()))
