# 委任_05: 既存Std attempt(API 0、ローカルfaster-whisperのみ)のRepetition QA方式Aを、是正後のcanonical照合で再判定する(読み取りのみ)。
import json, sys, glob
sys.path.insert(0, '.')
import er011_open121_repetition_qa_production_01 as rq
D = 'er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01'
plan = json.load(open(f'{D}/a2/audit/chunk_plan_a2.json', encoding='utf-8'))
chunk = [c for p in plan['plans'].values() for c in p['chunks'] if c['chunk_id'] == 'full_story_part2_k3'][0]['text']
rows = []
for f in sorted(glob.glob(f'{D}/a2/narration/attempts/full_story_part2_k3_attempt[456]_*.json')):
    meta = json.load(open(f, encoding='utf-8'))
    ev = meta.get('repetition_qa_evidence') or {}
    old = ev.get('method_a_ngram') or {}
    wav = f[:-5] + '.wav'
    new = rq.run_ngram_check(wav, chunk)
    rows.append({'attempt': meta['attempt_number'], 'route': meta['route'], 'old_evidence_keys': list(ev.keys())[:8],
                 'old_flagged_matches': [(m.get('span_text'), m.get('canonical_repeat_count')) for m in (old.get('flagged_matches') or [])],
                 'new_flagged': new['flagged'],
                 'new_flagged_matches': [(m['span_text'], m['canonical_repeat_count']) for m in new['flagged_matches']],
                 'new_intentional': [(m['span_text'], m['canonical_repeat_count']) for m in new['matches'] if m['intentional']]})
print(json.dumps(rows, ensure_ascii=False, indent=1))
