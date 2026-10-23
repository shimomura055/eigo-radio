# -*- coding: utf-8 -*-
"""委任_21 API 0: gloss段の実Production messageをローカルでPrompt組立関数から再構成し、保存済みartifactとバイト比較 + NG KPの実messageをdump。"""
import json, sys
sys.path.insert(0, '.')
import er003_key_words_gloss_alignment as ga
import er112_kp_gm_trial_04 as X
base = 'er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/a2/key_phrases/'
saved = open(base + 'gloss_alignment_prompt.txt', encoding='utf-8').read()
c = json.load(open(base + 'keywords_canonicalized.json', encoding='utf-8'))
tgt = []
for it in c['items']:
    t = dict(it); t['japanese_gloss'] = None; tgt.append(t)
art = saved[saved.index('【記事本文(参考)】') + len('【記事本文(参考)】\n'):]
msg = ga.build_user_message_corrected(tgt, art)
print('byte-identical to saved production prompt:', msg == saved, len(msg), len(saved))
if msg != saved:
    import difflib
    for l in list(difflib.unified_diff(saved.splitlines(), msg.splitlines(), lineterm=''))[:20]: print(l)
print('DEVELOPER_MESSAGE =', ga.DEVELOPER_MESSAGE)
print('schema property order =', list(ga.GLOSS_ALIGNMENT_JSON_SCHEMA['schema']['properties']['items']['items']['properties']))
# NG KPの実message(本番と同じ組立。Trial gloss_callと同じtgt形式)
A = X.all_kps()
out = []
for k in ['an unseen clock', 'question shaped like a trophy', 'greener grass']:
    kp = A[k]
    tg = [{"rank": 1, "key_phrase": kp["key"], "display_phrase": kp["display"], "japanese_gloss": None, "source_sentence": kp["sent"], "fulltext_source_ref": "fulltext_exact_v1"}]
    m = ga.build_user_message_corrected(tg, kp['article'])
    out.append('#' * 30 + ' ' + k + ' (chars=%d)\n' % len(m) + m)
open('er112_output/kp_gm_design_07/prompt_dump_gloss_ngkp.txt', 'w', encoding='utf-8').write('\n\n'.join(out))
print('saved')
