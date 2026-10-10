import json,glob,os
for u in ['U01','U02','U03','U04','U05','U06','U07','U08','X09','X10','X11']:
    for lv in (3,4):
        f=glob.glob('flags/A%d/%s_*.json'%(lv,u))[0]
        d=json.load(open(f,encoding='utf-8'))
        print('=====',u,d['theme'],'A%d'%lv,'n_flags',len(d['flags']),'cost',d['cost_jpy'],d['model_ids'])
        for fl in d['flags']:
            print(' ',fl['sentence_id'],fl['type'],fl['confidence'],fl['fact_ids'])
            print('     S:',d['sentences'][fl['sentence_id']][:260])
            print('     Q:',fl['question'])
