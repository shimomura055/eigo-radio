import sys,re
sys.path.insert(0,'er052_output/open233_link_precision_01')
import units_lib as U
run=[r for r in U.article_runs(__import__('os').environ.get('KIND','dev')) if sys.argv[1] in r]
assert len(run)==1,run
r,l,a=U.RL.load_run(run[0]); sp=U.split(a)
pat=re.compile(sys.argv[2],re.I)
for u in sp['units']:
    if u['type']!='sentence' and u['id']!='T': continue
    if pat.search(u['text']): print(u['id'],u['text'][:260])
