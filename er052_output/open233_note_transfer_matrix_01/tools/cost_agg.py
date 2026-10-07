import glob,os,json,sys
sys.path.insert(0,'.')
import er019_family_x_entertainment_production_runner_01 as r
B='er052_output/open233_note_transfer_matrix_01'
tot=0;rows={}
stage={}
for d in sorted(glob.glob(f'{B}/runs/*/nb/*/rep*')):
    d=d.replace(chr(92),'/')
    c=r.compute_stage_cost_breakdown(f'{d}/raw_usage_log.jsonl')
    tot+=c['total_jpy']
    for k,v in c.get('by_stage_jpy',c.get('by_stage',{})).items(): stage[k]=stage.get(k,0)+v
    rows[d.split('/runs/')[1]]={'total_jpy':round(c['total_jpy'],3),'by_stage':c.get('by_stage_jpy',c.get('by_stage')),'en':os.path.exists(d+'/b1b/article.md'),'ja_r2':os.path.exists(d+'/ja_writer/revision2.md')}
extra=0
for s in ('meta','hormuz','sewer'):
    for f in (f'{B}/brief_gen/{s}/cost.json',f'{B}/ledger/{s}/notes_summary_meta.json',f'{B}/ledger/{s}/notes_summary_meta_attempt1.json'):
        if os.path.exists(f):
            j=json.load(open(f,encoding='utf-8')); extra+=j.get('cost',j)['total_jpy']
            if 'cost' in j: stage['t1_summary']=stage.get('t1_summary',0)+j['cost']['total_jpy']
            else: stage['b3_brief_gen']=stage.get('b3_brief_gen',0)+j['total_jpy']
out={'runs_total_jpy':round(tot,2),'brief_gen_and_summary_jpy':round(extra,2),'grand_total_jpy':round(tot+extra,2),'by_stage_jpy':{k:round(v,2) for k,v in stage.items()},'runs':rows}
json.dump(out,open(f'{B}/cost.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(out['runs_total_jpy'],out['brief_gen_and_summary_jpy'],out['grand_total_jpy'],out['by_stage_jpy'])
for k,v in rows.items():
    if 'failed' in k: print(k,v['total_jpy'],v['ja_r2'],v['en'])
