# -*- coding: utf-8 -*-
"""委任_05: 6 docの証跡集計(API 0)+フォームentry用data書出し。出力 kpd05_out/kpd05_evidence.json, kpd05_form_entries.json, kpd05_form_data/*.json"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'docs', 'research', 'KP-GATE-DROP-BACKFILL-PRODUCTION-01', 'tools'))
OUT = os.path.join(HERE, 'kpd05_out'); FD = os.path.join(OUT, 'kpd05_form_data'); os.makedirs(FD, exist_ok=True)
import export_form_data_01 as xf
import er119_kp_difficulty_01 as dg
import er119_kp_human_review_01 as rv
import er006_model_routing_contract_01 as routing
res = json.load(open(os.path.join(OUT, 'kpd05_run_result.json'), encoding='utf-8'))
LAB = {'easy': '易', 'medium': '中', 'hard': '難', 'rare': '激難', 'unknown': 'unknown'}
NAME = {'X': 'ai_island_temple', 'Y': 'redelivery_fee', 'Z': 'melos'}
ev = {'prompt_sha256_expected': dg.PROMPT_SHA256, 'sets': {}}; entries = []
import hashlib
import er119_kp_candidates_01 as kcand
for fam in 'XYZ':
    for lv in ('a2', 'b1b'):
        dp = res[fam]['levels'][lv]['doc_path']; doc = json.load(open(dp, encoding='utf-8'))
        pre = json.load(open(dp.replace('kp_candidates.json', 'kp_candidates.blocked_fail_open.json'), encoding='utf-8'))
        g = doc['difficulty_grading']; cands = doc['candidates']
        dist = collections.Counter(LAB[c['difficulty']['level']] for c in cands)
        same_order = [c['candidate_id'] for c in cands] == [c['candidate_id'] for c in pre['candidates']]
        strip = lambda cs: [{k: v for k, v in c.items() if k != 'difficulty'} for c in cs]
        process = 'A2_SUPPORT' if lv == 'a2' else 'B1_SUPPORT'
        ev['sets'][f'{fam}_{lv}'] = {
            'doc': dp, 'n_cand': len(cands), 'grading': {k: g.get(k) for k in ('version', 'prompt_id', 'prompt_sha256', 'status', 'model_id', 'response_id', 'n_candidates', 'n_graded', 'n_unknown')},
            'distribution': dict(dist), 'source_llm': sum(1 for c in cands if c['difficulty']['source'] == 'llm'),
            'order_ids_unchanged_vs_pre_grading_doc': same_order, 'other_fields_unchanged_vs_pre_grading_doc': strip(cands) == strip(pre['candidates']),
            'p7_w5_prompt_sha_in_doc': doc['prompt_sha256'], 'p7_w5_prompt_sha_equal_pre': doc['prompt_sha256'] == pre['prompt_sha256'],
            'routing_SUPPORT_MODEL': routing.require_model(process, routing.SUPPORT_MODEL), 'process': process,
            'labels': [(c['used_form'], c['difficulty']['label_ja'], c['difficulty']['reason_ja']) for c in cands],
            'candidates_sha256_ok': doc['candidates_sha256'] == rv.candidates_sha256(doc),
            'gen_calls': res[fam]['levels'][lv]['calls'], 'dropped_n': len(doc.get('dropped') or []), 'shortfall': doc.get('shortfall'),
        }
        slug = f'kpd05_{fam.lower()}'
        form = xf.convert(doc, slug=slug, level=lv, name=f'【表示確認用】難易度バッジ確認 {fam} {NAME[fam]}', family=fam, run='kpd05', source_kind='PRODUCTION_FORMAL_PATH',
                          note_ja='【表示確認用】難易度バッジ表示の実表示確認用の一時データです(通常の選定用ではありません。確認後に削除されます)。')
        fp = os.path.join(FD, f'{slug}__{lv}.json'); json.dump(form, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        ents = form['phrases'] + form['words']
        entries.append({'slug': slug, 'level': lv, 'key': f'{slug}__{lv}', 'name': f'【表示確認用】難易度バッジ確認 {fam} {NAME[fam]}', 'data_file': fp,
                        'n_cand': len(ents), 'labels': [e['difficulty']['label_ja'] if e['difficulty']['level'] != 'rare' else '激難(レア)' for e in ents]})
        ev['sets'][f'{fam}_{lv}']['form_entries'] = len(ents)
json.dump(ev, open(os.path.join(OUT, 'kpd05_evidence.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(entries, open(os.path.join(OUT, 'kpd05_form_entries.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in ev['sets'].items():
    print(k, v['n_cand'], v['grading']['status'], v['grading']['model_id'], v['grading']['prompt_sha256'][:8], v['grading']['n_graded'], v['grading']['n_unknown'], v['distribution'], v['order_ids_unchanged_vs_pre_grading_doc'], v['other_fields_unchanged_vs_pre_grading_doc'], v['p7_w5_prompt_sha_equal_pre'], v['routing_SUPPORT_MODEL'], v['candidates_sha256_ok'])
