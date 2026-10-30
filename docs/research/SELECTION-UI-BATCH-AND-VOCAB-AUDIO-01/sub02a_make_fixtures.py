# -*- coding: utf-8 -*-
"""委任_02A: 一括選定画面のPlaywright検証用fixture生成(本番data/は読取のみ・不変)。
出力: user_test/selection_form_v3/test_fixtures/{data/*.json, articles_b{1,4,9,10}.json, articles_nobatch.json, articles_short.json}
検証時は Playwright の route で `data/articles.json` と `data/<file>` をこのfixtureへ差し替える(本番コード・本番dataは無変更)。"""
import json, os, shutil, copy
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
FD = os.path.join(ROOT, 'user_test', 'selection_form_v3')
OUT = os.path.join(FD, 'test_fixtures')
SLUGS = ['untidiness_family_resource', 'ai_chat_sponsored_persuasion', 'meta_waddle_world', 'jwst_mystery_emission_line', 'surname_choice',
         'in_a_grove', 'yuki_onna', 'moon_shrinking', 'ai_island_temple', 'the_tell_tale_heart']
LV = [('a2', 'Standard'), ('b1b', 'Advanced')]
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, 'data'))
entries = []
for s in SLUGS:
    for lv, ll in LV:
        f = f'{s}__{lv}__prod.json'
        raw = open(os.path.join(FD, 'data', f), 'rb').read().replace(b'\r\n', b'\n')   # 公開Pages(=リポジトリblob)はLF。Windows作業ツリーのCRLFをLFへ正規化(d6=公開と同一)
        open(os.path.join(OUT, 'data', f), 'wb').write(raw)
        d = json.load(open(os.path.join(FD, 'data', f), encoding='utf-8'))
        entries.append({'slug': s, 'level': lv, 'level_label': ll, 'name': d['name'], 'data': 'data/' + f})
# 候補不足(2件)データ: moon b1bの先頭フレーズ1+単語1のみ
d = json.load(open(os.path.join(FD, 'data', 'moon_shrinking__b1b__prod.json'), encoding='utf-8'))
d['slug'] = 'fx_short'; d['name'] = '候補不足テスト記事'; d['phrases'] = d['phrases'][:1]; d['words'] = d['words'][:1]; d['grammar'] = []
for k in ('grammar_spec', 'kp_confirmed'):
    d.pop(k, None)
json.dump(d, open(os.path.join(OUT, 'data', 'fx_short__a2__prod.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
short = {'slug': 'fx_short', 'level': 'a2', 'level_label': 'Standard', 'name': d['name'], 'data': 'data/fx_short__a2__prod.json'}


def idx(members, extra=None, batch=True):
    o = {'schema': 'eigo_radio_selection_index_v1', 'note_ja': 'test fixture (SELECTION-UI-BATCH 02A)', 'default': None, 'articles': entries + ([short] if extra else [])}
    if batch:
        o['batch'] = {'id': 'FX-%d' % len(members), 'date': '2026-10-30', 'members': members}
    return o


for n in (1, 4, 9, 10):
    json.dump(idx([f'{x}__{lv}__prod' for x in SLUGS[:n] for lv, _ in LV]), open(os.path.join(OUT, f'articles_b{n}.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
json.dump(idx([], batch=False), open(os.path.join(OUT, 'articles_nobatch.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(idx(['yuki_onna__a2__prod', 'fx_short__a2__prod'], extra=True), open(os.path.join(OUT, 'articles_short.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('fixtures:', len(os.listdir(os.path.join(OUT, 'data'))), 'data files')
