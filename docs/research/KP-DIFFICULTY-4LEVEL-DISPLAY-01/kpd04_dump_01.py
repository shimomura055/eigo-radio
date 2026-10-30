import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpd04_common_01 as k
rows = []
for s in k.load_sets():
    for c in s['cands']:
        rows.append({'set': s['name'], 'candidate_id': c['candidate_id'], 'expr': c.get('used_form') or c.get('selection_phrase'),
                     'kind': c.get('kind') or 'phrase', 'gloss': c.get('japanese_gloss'), 'example': c.get('source_sentence')})
json.dump(rows, open(os.path.join(k.OUT, 'kpd04_candidates_blind.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in rows: print(f"{r['set']}\t{r['expr']}\t{r['kind']}\t{r['gloss']}\t| {r['example']}")
print('N', len(rows))
