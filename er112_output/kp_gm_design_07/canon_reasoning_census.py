# -*- coding: utf-8 -*-
"""委任_21 API 0: canonicalizationのfree-text reasoningに比喩/慣用の認識が含まれるか(= gloss段へ渡されていない情報)を既存artifactで数える。"""
import glob, json, re, collections
seen = {}
for f in glob.glob('**/keywords_canonicalized.json', recursive=True):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    for it in d.get('items', []):
        if not it.get('fulltext_source_ref'): continue
        k = (it.get('source_sentence'), it.get('key_phrase'))
        seen.setdefault(k, it)
pat = re.compile(r'比喩|慣用|イディオム|熟語|figurative|idiom')
n = len(seen); hit = [(k, it) for k, it in seen.items() if pat.search(it.get('reasoning') or '')]
print('unique fulltext items', n, 'reasoning mentions figurative/idiom', len(hit), f'{len(hit)/n:.1%}')
print(collections.Counter(it.get('normalization_reason') for it in seen.values()))
for k, it in hit[:12]:
    print('-', it['key_phrase'], '|', it.get('japanese_gloss'), '|', (it.get('reasoning') or '')[:110])
