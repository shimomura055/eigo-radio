import json,sys,os,glob,re,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from _s0_scan import load_all
BS=chr(92)
OUT='er052_output/open243_translation_ng_analysis_01/'
FLAGS=['changed_fact','changed_scope','changed_causality','changed_certainty','changed_number','changed_actor','changed_negation','changed_comparison','changed_time','unsupported_new_claim']
def norm(s): return re.sub(r'[\s"“”‘’\'「」]','',s or '').lower()
def runkey(f):
    if '/checker/' in f: return f.split('/checker/')[0]
    return f.rsplit('/runs/',1)[0]+'|'+os.path.basename(f)
dumps={}
for f in glob.glob('er052_output/**/approved_switches_dump*.json',recursive=True):
    f=f.replace(BS,'/'); dumps[f]=json.load(open(f,encoding='utf-8'))
def find_dump(f):
    parts=f.split('/')
    for n in range(len(parts)-1,1,-1):
        dd='/'.join(parts[:n]); c=[k for k in dumps if os.path.dirname(k)==dd]
        if c: return c
    return []
rows=load_all()
# dedupe: prefer runs/ over after_instances/
best={}
for f,d in rows:
    k=runkey(f)
    if k not in best or ('/after_instances/' in best[k][0] and '/after_instances/' not in f): best[k]=(f,d)
out=[]; perdump=[]
for k,(f,d) in sorted(best.items()):
    dd=find_dump(f); sw=[dumps[x]['switches'] for x in dd]
    approved=bool(sw) and all(s.get('STAGE1_RECLASSIFY') is True and s.get('FLOOR_MODE')=='number_only' for s in sw)
    cf=d['stage1_coverage']['candidate_filter']; sr=d.get('stage1_reclassify') or {}
    cands={}
    for rt in ('r3','r5'):
        for c in d['stage1_coverage']['per_route'].get(rt,{}).get('candidates',[]) or []:
            if not any(str(s).startswith('model_') for s in c.get('sources',[])): continue
            key='|'.join(c.get('unit_ids') or []) or 'TXT:'+(c.get('claim_text') or '')
            e=cands.setdefault(key,{'flags':set(),'issues':[],'related':[],'routes':[]})
            e['flags']|={a for a,v in (c.get('flags') or {}).items() if v}
            for i in c.get('issues') or []:
                if i not in e['issues']: e['issues'].append(i)
            for r in c.get('related_fact_ids') or []:
                if r not in e['related']: e['related'].append(r)
            if rt not in e['routes']: e['routes'].append(rt)
    cyc=d.get('cycles') or []
    texts=[c.get('en_text_after_rewrite') for c in cyc if c.get('en_text_after_rewrite')]
    final_text=texts[-1] if texts else (cyc[0].get('en_text_before_rewrite') if cyc else '')
    input_text=cyc[0].get('en_text_before_rewrite') if cyc else ''
    rex=[c.get('reclassify') for c in cyc if c.get('reclassify')]
    exitlog=(d.get('recheck_exit_check') or {}).get('log') or []
    later=[]  # recheck/exit reclassify counts
    for l in exitlog:
        if l.get('reclassify'): later.append(('exit_c%s'%l.get('cycle'),l['reclassify']))
    for i,c in enumerate(cyc):
        rc=c.get('recheck_coverage')
        if isinstance(rc,dict):
            for kk,v in rc.items():
                if isinstance(v,dict) and 'n_excluded_claims' in v: later.append(('recheck_c%s_%s'%(c.get('cycle'),kk),v))
        if c.get('reclassify'): later.append(('cycle%s'%c.get('cycle'),c['reclassify']))
    verd=cf.get('verdicts') or []
    perdump.append({'run_key':k,'file':f,'approved':approved,'dump_files':dd,'status':cf.get('status'),
        'n_targets':cf.get('n_targets'),'n_excl_claims':cf.get('n_excluded_claims'),'n_excl_entries':cf.get('n_excluded_entries'),
        'n_excl_changed_number':cf.get('n_excluded_with_changed_number'),'final_state':d.get('final_state'),
        'later':[(a,{kk:b.get(kk) for kk in ('reclassify_status','n_targets','n_protected_keys','n_excluded_claims','n_excluded_entries','n_excluded_with_changed_number')}) for a,b in later]})
    for v in verd:
        if not v.get('excluded'): continue
        e=cands.get(v['key'],{'flags':set(),'issues':[],'related':[],'routes':[]})
        n=norm(v['claim'])
        out.append({'run_key':k,'file':f,'approved':approved,'key':v['key'],'claim':v['claim'],'verdict':v['verdict'],
            'actor_match':v.get('actor_match'),'counterpart_match':v.get('counterpart_match'),'scope_match':v.get('scope_match'),'qualifier_match':v.get('qualifier_match'),
            'reclass_reason':v.get('reason'),'fact_tags':v.get('fact_tags'),'stage1_flags':sorted(e['flags']),'stage1_issues':e['issues'],
            'related_fact_ids':e['related'],'routes':e['routes'],'flag_found_in_cands':v['key'] in cands,
            'run_final_state':d.get('final_state'),'in_input_text':bool(n and n in norm(input_text)),'in_final_text':bool(n and n in norm(final_text))})
json.dump(perdump,open(OUT+'_s0_perdump.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
with open(OUT+'s0_excluded_candidates.jsonl','w',encoding='utf-8') as fo:
    for o in out: fo.write(json.dumps(o,ensure_ascii=False)+'\n')
print('dumps',len(perdump),'approved',sum(p['approved'] for p in perdump),'excluded',len(out),'no-flag-join',sum(not o['flag_found_in_cands'] for o in out))
