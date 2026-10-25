# DEV read-only集計(API 0): 現行run_sf_prod_01の全作品のclip語数・秒数・WPM分布。出力=clip_distribution_01.json
import json, os, statistics as S
base = 'er026_output/family_z_production_e2e_01'
out = {}
rows = []
for w in sorted(os.listdir(base)):
    for lv in ('b1b', 'a2'):
        sp = f'{base}/{w}/run_sf_prod_01/segment_plan_{lv}.json'
        tl = f'{base}/{w}/run_sf_prod_01/{lv}/assembly/timeline.json'
        if not (os.path.exists(sp) and os.path.exists(tl)):
            continue
        plan = json.load(open(sp, encoding='utf-8')); t = json.load(open(tl, encoding='utf-8'))
        dur = {e['part']: e['duration_seconds'] for e in t['timeline']}
        for c in plan['clips']:
            rows.append({'work': w, 'level': lv, 'id': c['id'], 'voice': c['voice'], 'words': c['word_count'],
                         'paras': len(c['source_paragraph_indices']), 'dur': dur.get(c['id'])})
out['clips'] = rows
def bucket(r):
    n = r['words']
    return 'lt30' if n < 30 else ('30_59' if n < 60 else ('60_99' if n < 100 else 'ge100'))
summ = {}
for lv in ('b1b', 'a2'):
    for b in ('lt30', '30_59', '60_99', 'ge100'):
        xs = [r for r in rows if r['level'] == lv and r['voice'] == 'narrator' and bucket(r) == b and r['dur']]
        if xs:
            summ[f'{lv}/narrator/{b}'] = {'n': len(xs), 'mean_wpm': round(S.mean(r['words'] / r['dur'] * 60 for r in xs), 1),
                                         'agg_wpm': round(sum(r['words'] for r in xs) / sum(r['dur'] for r in xs) * 60, 1)}
out['summary'] = summ
out['narrator_ge100'] = [r for r in rows if r['voice'] == 'narrator' and r['words'] >= 100]
out['narrator_ge80'] = [(r['work'], r['level'], r['id'], r['words'], r['dur']) for r in rows if r['voice'] == 'narrator' and r['words'] >= 80]
json.dump(out, open('er026_output/family_z_dev_trials/fz_narration_chunk_01/clip_distribution_01.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False, indent=1)); print(out['narrator_ge80'])
