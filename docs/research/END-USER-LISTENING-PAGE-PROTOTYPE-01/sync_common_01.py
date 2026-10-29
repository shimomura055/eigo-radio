"""Shared config/loaders for 1-sentence sync data (END-USER-LISTENING-PAGE-PROTOTYPE-01 delegation 01a). DEV only."""
import json, re, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
W = 'er019_output/family_x_audio_production_wiring_01/'
ARTICLES = {
    'ai_std': dict(out='std', run=W + 'ai_island_temple__run_form_prod_01/a2', lv='a2', mp3dir='user_test/family_x_ai_island_form_01/audio', prefix='std',
                   full_mp3='ai_island_temple_standard.mp3', title='AI island (Standard)'),
    'ai_adv': dict(out='adv', run=W + 'ai_island_temple__run_form_prod_01/b1b', lv='b1b', mp3dir='user_test/family_x_ai_island_form_01/audio', prefix='adv',
                   full_mp3='ai_island_temple_advanced.mp3', title='AI island (Advanced)'),
    'moon_adv': dict(out='moon_adv', run=W + 'moon_shrinking__run_reselect_01/b1b', lv='b1b', mp3dir='user_test/family_x_moon_shrinking_reselect_01/audio', prefix='adv',
                     full_mp3='moon_shrinking_advanced.mp3', title='Moon wrinkles reselect (Advanced)'),
}
SEG_RULES = [  # (regex on timeline part name, key template)
    (r'^Topic intro', 'topic_intro'), (r'^Japanese title', 'japanese_title'), (r'^Preview(?! intro)', 'preview'),
    (r'^Comment (\d)', 'comment_{0}'), (r'^Full Story Part (\d)', 'full_story_part{0}'), (r'^In One Line', 'in_one_line'),
]
def j(path):
    return json.load(open(os.path.join(ROOT, path), encoding='utf-8'))
def load_article(key):
    a = ARTICLES[key]
    tl = j(a['run'] + '/audit/timeline.json')
    tts = j(a['run'] + '/audit/tts_generation_results.json')
    asm = j(a['run'] + '/audit/chunk_tts_assembly_%s.json' % a['lv'])
    plan = j(a['run'] + '/audit/chunk_plan_%s.json' % a['lv'])
    parts = [p for p in tl if not p['part'].startswith('pause')]
    units = []
    for idx, p in enumerate(parts):
        segkey = None
        for rx, tpl in SEG_RULES:
            m = re.match(rx, p['part'])
            if m:
                segkey = tpl.format(*m.groups()); break
        if not segkey: continue
        mp3 = '%s/%s_%02d.mp3' % (a['mp3dir'], a['prefix'], idx)
        u = dict(key=segkey, part=p['part'], index=idx, start=p['start_seconds'], duration=p['duration_seconds'], mp3=mp3)
        if segkey.startswith('full_story_part'):
            pid = segkey
            chunks = []
            for ch in plan['plans'][pid]['chunks']:
                chunks.append(dict(chunk_id=ch['chunk_id'], text=tts['segments'][ch['chunk_id']]['text'], display_text=ch['text']))
            u['chunks'] = chunks
            u['gaps'] = asm['parents'][pid]['gap_offsets_in_part_s']
            u['part_start_in_episode_s'] = asm['parents'][pid]['part_start_in_episode_s']
        else:
            u['chunks'] = [dict(chunk_id=segkey, text=tts['segments'][segkey]['text'], display_text=None)]
            u['gaps'] = []
        u['lang'] = 'ja' if re.search(r'[぀-ヿ一-鿿]', ''.join(c['text'] for c in u['chunks'])) else 'en'
        units.append(u)
    return a, units
