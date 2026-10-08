# OPEN-243-TRANSLATION-NG-ANALYSIS-01 stats script (read-only, API cost 0). run from repo root.
import json, glob, re, collections, os
BS = chr(92)
OUT = 'er052_output/open243_translation_ng_analysis_01'
rows = [json.loads(l) for l in open(OUT + '/items.jsonl', encoding='utf8')]
C = [r for r in rows if r['counted']]
S = {}

# ---- unique judged EN articles (both trials) ----
arts = {}
for t in ['all6_writer_redesign_necessity_01', 'factlock_writer_trial_01']:
    m = json.load(open(f'er052_output/{t}/eval/_private/MAP.json', encoding='utf8'))['articles']
    judged = {os.path.basename(f)[:-5] for f in glob.glob(f'er052_output/{t}/eval/judgments/*.json')}
    for k, v in m.items():
        if v['code'] not in judged: continue
        run = v['run_dir'].replace(BS, '/')
        cell = v.get('arm') or v.get('cell')
        theme = 'meta' if 'meta' in k else ('hormuz' if 'hormuz' in k else 'space_weapons')
        ens = run + '/b1b/article.md'
        en = open(ens, encoding='utf8').read() if os.path.exists(ens) else ''
        mods = set()
        lf = run + '/raw_usage_log.jsonl'
        if os.path.exists(lf):
            for l in open(lf, encoding='utf8'):
                try: x = json.loads(l)
                except Exception: continue
                if x.get('stage') == 'advanced': mods.add(x.get('model_id'))
        if not en: continue
        arts.setdefault(run, dict(run=run, cell=cell, theme=theme, en=en, models=sorted(mods), trials=set()))['trials'].add(t[:4])
S['unique_en_articles'] = len(arts)
S['by_cell'] = dict(collections.Counter(a['cell'] for a in arts.values()))
S['by_theme'] = dict(collections.Counter(a['theme'] for a in arts.values()))
S['by_model'] = dict(collections.Counter(str(a['models']) for a in arts.values()))
S['judgments_total'] = dict(A=sum(1 for a in arts.values() if 'all6' in a['trials']), B=sum(1 for a in arts.values() if 'fact' in a['trials']))

def sents(t):
    t = t.replace('U.S.', 'US')
    body = re.split(r'\n## In one line', t)[0]
    body = re.sub(r'^# .*\n', '', body)
    return [x for x in re.split(r'(?<=[.!?”])\s+|\n+', body) if x.strip()]
S['body_sentences_total'] = sum(len(sents(a['en'])) for a in arts.values())
S['summary_lines_total'] = sum(1 for a in arts.values() if '## In one line' in a['en'])

# ---- events ----
E = {}
for r in C: E.setdefault(r['event_id'], []).append(r)
ev = []
for eid, rs in sorted(E.items()):
    r0 = rs[0]
    ev.append(dict(event_id=eid, ids=[x['id'] for x in rs], run_dir=r0['run_dir'], theme=r0['theme'], cell=r0['cell'], models=r0['en_writer_models'],
                   severity=('major' if any(x['severity'] == 'major' for x in rs) else 'minor'),
                   user_or_blind_sev=sorted({x['severity'] for x in rs}), origin=r0['origin'], type=r0['type'], position=r0['position'],
                   cause=r0['linguistic_cause'], loc_class=sorted({x['location_class'] for x in rs}),
                   ed=sorted({(e['severity'], str(e['origin'])) for x in rs for e in x['en_deviation_check']}),
                   has_checker=any(x['checker']['has_checker'] for x in rs),
                   ck_cand=any(x['checker'].get('candidate') for x in rs),
                   ck_mats=sorted({c['materiality'] for x in rs for c in x['checker'].get('cycles', [])}),
                   ck_final_present=[x['checker'].get('sentence_in_final_text') for x in rs if x['checker']['has_checker']][:1],
                   ck_final_state=[x['checker'].get('final_state') for x in rs if x['checker']['has_checker']][:1],
                   judges=sorted({x['judge'] for x in rs}), trials=sorted({x['trial'] for x in rs}),
                   sentence=r0['en_sentence_matched']))
json.dump(ev, open(OUT + '/_events.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
S['events_total'] = len(ev)
S['events_by_origin'] = dict(collections.Counter(e['origin'] for e in ev))
S['events_by_origin_sev'] = {f"{k[0]}/{k[1]}": v for k, v in collections.Counter((e['origin'], e['severity']) for e in ev).items()}
S['judgments_by_origin'] = dict(collections.Counter(r['origin'] for r in C))
S['judgments_by_loc_sev'] = {f"{k[0]}/{k[1]}": v for k, v in collections.Counter((r['location_class'], r['severity']) for r in C).items()}
NJ = [e for e in ev if e['origin'] != 'ja']
S['nonja_events'] = len(NJ)
for key in ['type', 'position', 'theme', 'cell', 'severity']:
    S['nonja_by_' + key] = dict(collections.Counter(e[key] for e in NJ))
S['nonja_by_model'] = dict(collections.Counter(str(e['models']) for e in NJ))
S['nonja_type_x_pos'] = {f"{k[0]}/{k[1]}": v for k, v in collections.Counter((e['type'], e['position']) for e in NJ).items()}
S['nonja_cause_head'] = dict(collections.Counter(re.split(r'[\(+]', e['cause'])[0].strip() for e in NJ))
S['ja_events_by_type'] = dict(collections.Counter(e['type'] for e in ev if e['origin'] == 'ja'))
S['ja_events_by_cell'] = dict(collections.Counter(e['cell'] for e in ev if e['origin'] == 'ja'))
S['ja_events_by_theme'] = dict(collections.Counter(e['theme'] for e in ev if e['origin'] == 'ja'))
# rates per article
def rate(counter, base):
    return {k: f"{v}/{base.get(k, 0)}={v / base[k]:.2f}" for k, v in counter.items() if base.get(k)}
S['nonja_per_article_by_cell'] = rate(S['nonja_by_cell'], S['by_cell'])
S['nonja_per_article_by_theme'] = rate(S['nonja_by_theme'], S['by_theme'])
S['nonja_per_article_by_model'] = rate(S['nonja_by_model'], S['by_model'])
S['nonja_summary_rate'] = f"{S['nonja_by_position'].get('summary', 0)}/{S['summary_lines_total']} summary lines"
S['nonja_body_rate'] = f"{S['nonja_by_position'].get('body', 0)}/{S['body_sentences_total']} body sentences"
# detection (non-JA events)
d = collections.Counter()
for e in NJ:
    d['events'] += 1
    d['ed_flagged'] += bool(e['ed'])
    d['ed_flagged_origin_translation'] += any(o == 'translation' for _, o in e['ed'])
    d['ed_flagged_origin_ja_source'] += any(o == 'ja_source' for _, o in e['ed'])
    d['ed_major'] += any(s == 'MAJOR' for s, _ in e['ed'])
    if e['has_checker']:
        d['has_checker'] += 1
        d['ck_candidate'] += e['ck_cand']
        d['ck_blocking'] += ('BLOCKING' in e['ck_mats'])
        d['ck_blocking_removed'] += ('BLOCKING' in e['ck_mats'] and e['ck_final_present'] and e['ck_final_present'][0] is False)
        d['ck_quality'] += ('QUALITY' in e['ck_mats'] and 'BLOCKING' not in e['ck_mats'])
        d['ck_acceptable_only'] += (e['ck_mats'] == ['ACCEPTABLE'])
        d['either_ed_or_ck_candidate'] += bool(e['ed']) or e['ck_cand']
        d['neither_ed_nor_ck_candidate'] += (not e['ed']) and (not e['ck_cand'])
    else:
        d['no_checker_data'] += 1
S['detection_nonja'] = dict(d)
dj = collections.Counter()
for e in [x for x in ev if x['origin'] == 'ja']:
    dj['events'] += 1; dj['ed_flagged'] += bool(e['ed'])
    if e['has_checker']:
        dj['has_checker'] += 1; dj['ck_candidate'] += e['ck_cand']; dj['ck_blocking'] += ('BLOCKING' in e['ck_mats'])
S['detection_ja_origin_events'] = dict(dj)
# major only
S['major_events'] = [dict(event_id=e['event_id'], ids=e['ids'], origin=e['origin'], type=e['type'], position=e['position'], ed=e['ed'], ck_mats=e['ck_mats'], ck_final_present=e['ck_final_present'], sentence=e['sentence']) for e in ev if e['severity'] == 'major']

# ---- deviation-check records (translation origin) ----
dev = json.load(open(OUT + '/_dev_all.json', encoding='utf8'))
tr = [x for x in dev if x.get('origin') == 'translation']
S['dev_translation_records'] = len(tr)
S['dev_translation_by_kind_sev_pos'] = {f"{k[0]}/{k[1]}/{k[2]}": v for k, v in collections.Counter((x['kind'], x['severity'], x['pos']) for x in tr).items()}
S['dev_all_origin_counts'] = {f"{k[0]}/{k[1]}": v for k, v in collections.Counter((x['kind'], str(x.get('origin'))) for x in dev).items()}
flagc = collections.Counter()
for x in tr:
    if x['kind'] != 'attempt' or x['attempt'] != 1: continue
    for k in x:
        if (k.startswith('changed_') or k == 'unsupported_new_claim') and x[k] is True: flagc[(k, x['pos'])] += 1
S['dev_translation_attempt1_flags_x_pos'] = {f"{k[0]}/{k[1]}": v for k, v in flagc.items()}
json.dump(S, open(OUT + '/_stats.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
