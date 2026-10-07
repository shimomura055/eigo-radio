import sys,re,glob
sys.path.insert(0,'er052_output/open233_link_precision_01')
import units_lib as U
d='er052_output/open233_b3_trial_01/runs/'+sys.argv[1]
a=open(d+'/b1b/article.md',encoding='utf-8').read(); sp=U.split(a)
pat=re.compile(sys.argv[2],re.I)
for u in sp['units']:
    if pat.search(u['text']): print(u['id'],u['text'][:240])
