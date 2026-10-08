# collect all blind judgments (Trial A / Trial B) resolved through MAP.json -> _all_ng_raw.json (read-only). run from repo root.
import json, glob
out = []
for t in ['all6_writer_redesign_necessity_01', 'factlock_writer_trial_01']:
    m = json.load(open(f'er052_output/{t}/eval/_private/MAP.json', encoding='utf8'))
    code2 = {v['code']: (k, v) for k, v in m['articles'].items()}
    for f in sorted(glob.glob(f'er052_output/{t}/eval/judgments/*.json')):
        j = json.load(open(f, encoding='utf8'))
        k, v = code2[j['code']]
        for sec in ('ng_items', 'pending'):
            for it in j['parsed'].get(sec, []):
                it = dict(it); it['_sec'] = sec; it['trial'] = t; it['key'] = k; it['arm'] = v.get('arm') or v.get('cell')
                it['code'] = j['code']; it['judge'] = j['judge_actual']; it['run_dir'] = v['run_dir']
                out.append(it)
json.dump(out, open('er052_output/open243_translation_ng_analysis_01/_all_ng_raw.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(out))
