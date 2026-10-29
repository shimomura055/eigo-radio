# -*- coding: utf-8 -*-
"""WP-C Phase-0 harness (DEV/measurement only, API 0, local faster-whisper). Not Production code.
Measures the sync methods on finished Std/Adv audio of Family X (moon_shrinking reselect), Y (redelivery_fee run_01), Z (melos_02 / run_e2e_06).

usage: python phase0_sync_01.py run <family:x|y|z> <level:std|adv> <model> <cache_dir>   -> phase0/res_<fam>_<lv>_<model>.json
       python phase0_sync_01.py report                                                  -> prints aggregated tables (json in phase0/summary.json)
"""
import html
import json
import os
import re
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT)
import er135_enduser_sync_01 as S  # noqa: E402

OUT = os.path.join(HERE, 'phase0')

CFG = {
    'x': dict(page='user_test/family_x_moon_shrinking_reselect_01/index.html', h2={'std': 'std', 'adv': 'adv'},
              run='er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01', lv={'std': 'a2', 'adv': 'b1b'}),
    'y': dict(page='er121_output/family_y_production_01/redelivery_fee/run_01/pages/index.html', h2={'std': 'standard', 'adv': 'advanced'},
              run='er121_output/family_y_production_01/redelivery_fee/run_01', lv={'std': 'a2', 'adv': 'b1b'}),
    'z': dict(page='user_test/family_z_melos_02/index.html', h2={'std': 'std', 'adv': 'adv'},
              run='er026_output/family_z_production_e2e_01/melos/run_e2e_06', lv={'std': 'a2', 'adv': 'b1b'}),
}


def jl(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


def clean(t):
    t = re.sub(r"<span class='chunk-mark'>.*?</span>", ' ', t, flags=re.S)
    t = re.sub(r"<span[^>]*>\s*(?:&#9208;|⏸)[^<]*</span>", ' ', t, flags=re.S)   # Y: inline-style pause marker span
    t = re.sub(r'<br\s*/?>', ' ', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t).replace('⏸', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def extract_rows(page, h2id):
    h = open(os.path.join(ROOT, page), encoding='utf-8').read()
    m = re.search(r"<h2 id='%s'>(.*?)(?=<h2|\Z)" % h2id, h, flags=re.S)
    sec = m.group(1)
    rows = []
    for ch in sec.split('<tr><td><b>')[1:]:
        label = clean(ch.split('</b>')[0])
        dt = re.search(r"data-t='([\d.]+)'", ch)
        src = re.search(r"<audio[^>]*src='([^']+)'", ch)
        if not src:
            continue
        scripts = [clean(x) for x in re.findall(r"<div class='script'>(.*?)</div>", ch, flags=re.S)]
        scripts = [x for x in scripts if x]
        kp = None
        if re.match(r'Key Phrase \d', label):
            kp = [clean(x) for x in re.findall(r"<tr><td>(.*?)</td><td>", ch.split("class='kp'")[1], flags=re.S)] if "class='kp'" in ch else []
        rows.append(dict(label=label, data_t=float(dt.group(1)) if dt else None, audio=src.group(1), scripts=scripts, kp=kp))
    return rows


def tts_key(fam, label):
    m = re.match(r'(Topic intro|Japanese title|Preview|Comment (\d)|In One Line|Full Story Part (\d)|Full Story: (Lead|Closing|Voice (\d) Introduction|Voice (\d)))', label)
    if not m:
        return None
    if label.startswith('Preview intro'):
        return None
    g = m.group(1)
    if g == 'Topic intro':
        return 'topic_intro_en' if fam == 'z' else 'topic_intro'
    if g == 'Japanese title':
        return 'japanese_title'
    if g == 'Preview':
        return 'preview'
    if g == 'In One Line':
        return 'in_one_line'
    if m.group(2):
        return 'comment_' + m.group(2)
    if m.group(3):
        return 'full_story_part' + m.group(3)
    if m.group(4):
        return {'Lead': 'y_lead', 'Closing': 'y_closing'}.get(m.group(4)) or ('y_intro_' + m.group(5) if m.group(5) else 'y_voice_' + m.group(6))
    return None


def tts_texts(fam, run, lv, label, cache={}):
    k = (run, lv)
    if k not in cache:
        A = os.path.join(run, lv, 'audit')
        seg = jl(A + '/tts_generation_results.json')['segments']
        plan = None
        pf = A + '/chunk_plan_%s.json' % lv
        if os.path.exists(os.path.join(ROOT, pf)):
            plan = jl(pf)['plans']
        cache[k] = (seg, plan)
    seg, plan = cache[k]
    key = tts_key(fam, label)
    if not key:
        return None
    if key.startswith('full_story_part'):
        if fam == 'x':
            ids = [c['chunk_id'] for c in plan[key]['chunks']]
        else:
            ids = sorted([s for s in seg if re.match(r'%s_c\d+$' % key, s)], key=lambda s: int(s.rsplit('_c', 1)[1]))
        return [seg[i].get('text') or seg[i].get('canonical_text') for i in ids if i in seg]
    if key in seg:
        v = seg[key].get('text') or seg[key].get('canonical_text'); return [v] if v else None
    return None


def build_rows(fam, lv):
    c = CFG[fam]
    base = os.path.dirname(os.path.join(ROOT, c['page']))
    rows = []
    for i, r in enumerate(extract_rows(c['page'], c['h2'][lv])):
        row = dict(row_id='%s_%d' % (lv, i), label=r['label'], data_t=r['data_t'], audio_path=os.path.join(base, r['audio']))
        if r['kp'] is not None:
            row.update(kind='kp', sentences=[], kp={'expressions': r['kp']})
        elif r['scripts']:
            row['kind'] = 'script'
            ss = []
            for d, txt in enumerate(r['scripts']):
                lang = 'ja' if S.has_cjk(txt) else 'en'
                for sent in S.split_sentences(txt, lang):
                    ss.append(dict(sid='%s_%d-s%d' % (lv, i, len(ss) + 1), text=sent, div=d))
            row['sentences'] = ss
            row['n_divs'] = len(r['scripts'])
            t = tts_texts(fam, c['run'], c['lv'][lv], r['label'])
            if t:
                row['tts_text'] = t
        else:
            continue
        rows.append(row)
    return rows


def run(fam, lv, model, cache_dir):
    rows = build_rows(fam, lv)
    th = {'en': {'min_ratio': 0.0}, 'ja': {'min_ratio': 0.0}}   # measurement: never gate here
    th = S._merge_thresholds(th)
    audios, jobs, kpw = {}, [], {}
    for r in rows:
        au = S.load_audio(r['audio_path'])
        audios[r['row_id']] = au
        sha = S.sha256_file(r['audio_path'])
        if r['kind'] == 'kp':
            try:
                ks, ke, ksrc, nb = S.kp_window(r, au, th)
                kpw[r['row_id']] = (ks, ke, ksrc, nb)
                jobs.append((r['audio_path'], sha, 'en', S.kp_slice(ks, ke, len(au) / S.SR)))
            except S.EnduserSyncError as e:
                kpw[r['row_id']] = e
                jobs.append(None)
        else:
            jobs.append((r['audio_path'], sha, S._row_lang(r)))
    t0 = time.time()
    raws = S.asr_raw_many([j for j in jobs if j], cache_dir, model)
    def key(j):
        return (j[1], S._job_label(j[2], j[3] if len(j) > 3 else None))
    asr_elapsed = sum(raws[key(j)].get('elapsed', 0) for j in jobs if j)
    res = dict(family=fam, level=lv, model=model, n_rows=len(rows), asr_elapsed_sum_s=round(asr_elapsed, 1), wall_s=round(time.time() - t0, 1), rows=[])
    for r, j in zip(rows, jobs):
        raw = raws[key(j)] if j else None
        audio = audios[r['row_id']]
        ent = dict(row_id=r['row_id'], label=r['label'], kind=r['kind'], data_t=r['data_t'], audio_s=round(len(audio) / S.SR, 3),
                   asr_elapsed=raw.get('elapsed') if raw else None, has_tts=bool(r.get('tts_text')), n_divs=r.get('n_divs'))
        if r['kind'] == 'kp':
            blocks = S.speech_blocks(audio)
            ent['blocks'] = [(round(a, 3), round(b, 3)) for a, b in blocks]
            kw = kpw[r['row_id']]
            if isinstance(kw, S.EnduserSyncError):
                ent['kp_error'] = kw.code + ': ' + kw.message[:300]
            else:
                try:
                    ent['kp_en'] = S.kp_verify(r, raw, kw[0], kw[1], kw[2], kw[3], th)
                except S.EnduserSyncError as e:
                    ent['kp_error'] = e.code + ': ' + e.message[:300]
            ent['kp_expr'] = r['kp']['expressions']
            ent['asr_text'] = raw['text'] if raw else ''
        else:
            ent['n_sent'] = len(r['sentences'])
            for mode in ('direct', 'auto'):
                if mode == 'auto' and not r.get('tts_text'):
                    continue
                try:
                    sents, st = S.sync_row(r, raw, audio, th, mode)
                    S.check_structure(r['row_id'], sents, len(audio) / S.SR, th['audio_len_tol_s'])
                    ent[mode if mode == 'direct' else 'two_stage'] = dict(stat=st, sentences=[(s['sid'], s['start'], s['end']) for s in sents])
                except S.EnduserSyncError as e:
                    ent[mode if mode == 'direct' else 'two_stage'] = dict(error=e.code + ': ' + e.message[:300])
            ent['texts'] = [s['text'] for s in r['sentences']]
        res['rows'].append(ent)
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, 'res_%s_%s_%s.json' % (fam, lv, model)), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('done', fam, lv, model, 'rows', len(rows), 'asr_sum_s', res['asr_elapsed_sum_s'], 'wall', res['wall_s'])


if __name__ == '__main__':
    if sys.argv[1] == 'run':
        run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


def e2e(cache_dir, model):
    """Run the real public API sync_level() (default thresholds) per family/level, direct and auto(two-stage where tts_text exists)."""
    out = {}
    for fam in 'xyz':
        for lv in ('std', 'adv'):
            rows = build_rows(fam, lv)
            for mode in ('direct', 'auto'):
                k = '%s_%s_%s_%s' % (fam, lv, model, mode)
                t0 = time.time()
                try:
                    r = S.sync_level(os.path.dirname(rows[0]['audio_path']), rows, cache_dir=cache_dir, model=model, align_mode=mode)
                    out[k] = dict(status=r['gate']['status'], min_row_ratio=r['gate']['token_match']['min_row_ratio'], warnings=len(r['gate']['warnings']),
                                  low_conf_total=sum(w['low_conf_boundaries'] for w in r['gate']['warnings']),
                                  sentences=sum(len(x['sentences']) for x in r['rows']), kp_rows=sum(1 for x in r['rows'] if 'kp_en' in x),
                                  wall_s=round(time.time() - t0, 1), asr_transcribed=r['cost']['asr_transcribed'])
                except S.EnduserSyncError as e:
                    out[k] = dict(status='STOP', code=e.code, msg=e.message[:300])
                print(k, out[k])
    json.dump(out, open(os.path.join(OUT, 'e2e_%s.json' % model), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__' and sys.argv[1] == 'e2e':
    e2e(sys.argv[2], sys.argv[3])
