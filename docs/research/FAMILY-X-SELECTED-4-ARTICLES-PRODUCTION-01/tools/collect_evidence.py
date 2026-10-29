import json,sys,os,collections
sys.path.insert(0,'.')
import er053_cost_aggregate_01 as ca
slugs=sys.argv[1:]
out=[]
for s in slugs:
    D=f'er019_output/{s}/run_fx4_01'; A=f'er019_output/family_x_audio_production_wiring_01/{s}__run_fx4_01'
    out.append(f'\n## {s}\n')
    def j(p):
        try: return json.load(open(p,encoding='utf-8'))
        except Exception as e: return None
    rl=j(f'{D}/research_ledger/runtime_evidence.json')
    if rl: out.append(f"- research: model={rl['research']['model_id_actual']} web_search_calls={rl['research'].get('web_search_call_count')} / ledger_verification model={rl['ledger_verification']['model_id_actual']} / verdicts={rl['verdict_counts']} kept={rl['kept_facts_count']} reused={rl['reused']}")
    sb=j(f'{D}/storyline_b3/runtime_evidence.json')
    if sb:
        nr=sb.get('numeric_retention_b3',{})
        out.append(f"- storyline_b3: model={sb['model_id_actual']} attempts={sb['attempts']} retried={sb['retried']} dev_sha={sb['prompt_shas']['developer_message_sha256'][:12]} user_tmpl_sha={sb['prompt_shas']['user_prompt_template_sha256'][:12]} numeric_retention variant={nr.get('variant')} m1_retry={nr.get('m1_retry')} field_items={nr.get('field_items')}")
    if os.path.isdir(f'{D}/storyline_b3_attempt1'): out.append('- storyline_b3_attempt1 exists: B3 M1 retry (existing mechanism, 1 time) fired')
    jw=j(f'{D}/ja_writer/runtime_evidence.json')
    if jw:
        out.append(f"- ja_writer: chain={jw.get('chain_method')}/{jw.get('chain_method_detail')} annotated_sha={jw['annotated_md_sha256'][:12]}")
        for k in jw:
            if k in('r0','r1','r2') or 'model' in k: out.append(f"  - {k}: {json.dumps(jw[k],ensure_ascii=False)[:250]}")
    ws=j(f'{D}/writer_run_summary.json')
    for lg in ('raw_usage_log.jsonl',):
        cnt=collections.OrderedDict()
        for fp in (f'{D}/{lg}',f'{A}/{lg}'):
            if not os.path.exists(fp): continue
            tag='stage1' if fp.startswith(D) else 'scaffold'
            for line in open(fp,encoding='utf-8'):
                r=json.loads(line); k=(tag,r.get('stage'),r.get('model_id') or r.get('model'),r.get('provider'))
                c=cnt.setdefault(k,[0,0]); c[0]+=1; c[1]+= 0 if r.get('success',True) else 1
        out.append('- API呼出(stage1/scaffold, stage, model, provider: calls/failed):')
        for k,v in cnt.items(): out.append(f'  - {k[0]} {k[1]} {k[2]} {k[3]}: {v[0]}/{v[1]}')
    for tag,fp in (('stage1',f'{D}/raw_usage_log.jsonl'),('scaffold',f'{A}/raw_usage_log.jsonl')):
        b=ca.compute_stage_cost_breakdown_multi(fp); out.append(f"- cost {tag}: total_jpy={b['total_jpy']}")
print('\n'.join(out))
