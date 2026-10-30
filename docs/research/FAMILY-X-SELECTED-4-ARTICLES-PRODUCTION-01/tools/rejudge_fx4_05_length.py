# 委任_05: 既存attempt(API 0)のASR長さ上限を、是正後のhelperで再判定する(読み取りのみ)。
import json, sys
sys.path.insert(0, '.')
import er021_en_asr_semantic_equivalence_production_01 as e21
D = 'er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01'
plan = json.load(open(f'{D}/b1b/audit/chunk_plan_b1b.json', encoding='utf-8'))
chunk = [c for p in plan['plans'].values() for c in p['chunks'] if c['chunk_id'] == 'full_story_part2_k3'][0]['text']
extra = e21.angstrom_symbol_extra_chars(chunk)
res = json.load(open(f'{D}/b1b/audit/tts_generation_results.json', encoding='utf-8'))
seg = res['segments']['full_story_part2_k3']
out = {'surface_len': len(chunk), 'angstrom_extra': extra, 'rows': []}
for i, a in enumerate(seg['attempts_log']):
    L = (a.get('asr_judgement') or {}).get('length') or {}
    mx = L.get('max_len')
    adopted_len = L.get('secondary_len') if L.get('adopted_from') == 'secondary' else L.get('primary_len')
    new_mx = None if mx is None else mx + extra
    out['rows'].append({'i': i, 'primary_len': L.get('primary_len'), 'secondary_len': L.get('secondary_len'), 'old_max_len': mx, 'new_max_len': new_mx,
                        'old_len_ok': a.get('final_length_ok'), 'new_len_ok': (adopted_len is not None and new_mx is not None and adopted_len <= new_mx),
                        'classification': a.get('audio_classification')})
print(json.dumps(out, ensure_ascii=False, indent=1))
