import importlib.util,sys,json,os
sys.path.insert(0,'.')
sp=sys.argv[1]
spec=importlib.util.spec_from_file_location('w_patched',os.path.join(sp,'w_patched.py'));wp=importlib.util.module_from_spec(spec);spec.loader.exec_module(wp)
D='docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/dev_seed'
def rd(p): return open(p,encoding='utf-8',newline='').read().replace('\r\n','\n')
s='the_tell_tale_heart'
seed=json.load(open(f'er026_output/family_z_production_e2e_01/{s}/seed/seed.json',encoding='utf-8'))
dv=json.load(open(f'{D}/{s}/seed.json',encoding='utf-8'))
seed=dv
print('seed==dev_seed:',seed==dv)
ess=wp.build_essentials(seed)
W=f'er026_output/family_z_dev_trials/fz_essence_01/{s}/1b_s1/writer'
p0,_=wp.build_r0_prompt(seed,essentials=ess)
outs={'r0':wp.WRITER_DEVELOPER_MESSAGE+"\n\n---\n\n"+p0}
outs['r1']=wp.build_revise_prompt(rd(f'{W}/r0.md').strip()+"\n",s,essentials=ess)
outs['r2']=wp.build_revise_prompt(rd(f'{W}/r1.md').strip()+"\n",s,essentials=ess)
outs['std']=wp.std_developer()+"\n\n---\n\n"+wp.build_std_prompt(rd(f'{W}/r2.md'),essentials=ess)
for k,f in (('r0','r0_prompt.txt'),('r1','r1_prompt.txt'),('r2','r2_prompt.txt'),('std','std_adjust_prompt.txt')):
    dump=rd(f'{W}/{f}')
    print(' ',k,'byte-equal' if dump==outs[k] else 'DIFF')
    if dump!=outs[k]:
        import difflib
        for l in list(difflib.unified_diff(dump.split('\n'),outs[k].split('\n'),lineterm='',n=0))[:8]: print('   ',l[:200])
print(outs['r1'].split('Without changing')[1][:420])
