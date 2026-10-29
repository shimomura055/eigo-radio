# -*- coding: utf-8 -*-
"""WP-C Phase-0 aggregation (reads phase0/res_*.json written by phase0_sync_01.py; API 0). Writes phase0/summary.json."""
import difflib
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT)
import er135_enduser_sync_01 as S  # noqa: E402

OUT = os.path.join(HERE, 'phase0')


def jl(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(round((len(v) - 1) * p)))] if v else None


def dist(v):
    if not v:
        return dict(n=0)
    return dict(n=len(v), med=round(statistics.median(v), 3), p95=round(pct(v, 0.95), 3), max=round(max(v), 3),
                gt01=sum(1 for x in v if x > 0.1), gt03=sum(1 for x in v if x > 0.3))


def load(fam, lv, model):
    p = os.path.join(OUT, 'res_%s_%s_%s.json' % (fam, lv, model))
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def eps(res, key):
    o = {}
    for r in res['rows']:
        m = r.get(key)
        if m and 'sentences' in m:
            for sid, a, b in m['sentences']:
                o[sid] = (r['data_t'] + a, r['data_t'] + b)
    return o


def diff_between(A, B):
    d = []
    for sid in A:
        if sid in B:
            d += [abs(A[sid][0] - B[sid][0]), abs(A[sid][1] - B[sid][1])]
    return d


def dev_moon_adv(res):
    moon = jl('user_test/dev_enduser_page_01/data/moon.json')
    sy = jl('user_test/dev_enduser_page_01/data/sync_moon_adv.json')['sentences']
    by = {s['sid']: s for s in sy}
    dev = []
    for p in moon['levels']['adv']['parts']:
        for para in p.get('paragraphs', []):
            for s in para:
                if s['sid'] in by:
                    dev.append((S.norm_chars(s['text']), by[s['sid']]['start'], by[s['sid']]['end']))
    mine = {k: [] for k in ('direct', 'two_stage')}
    for r in res['rows']:
        for k in mine:
            m = r.get(k)
            if m and 'sentences' in m:
                for (sid, a, b), t in zip(m['sentences'], r['texts']):
                    mine[k].append((S.norm_chars(t), r['data_t'] + a, r['data_t'] + b))
    out = {}
    for k, L in mine.items():
        sm = difflib.SequenceMatcher(None, [x[0] for x in dev], [x[0] for x in L], autojunk=False)
        d = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for q in range(i2 - i1):
                    d += [abs(dev[i1 + q][1] - L[j1 + q][1]), abs(dev[i1 + q][2] - L[j1 + q][2])]
        out[k] = dict(dev_n=len(dev), mine_n=len(L), paired_boundaries=len(d), diff=dist(d))
    return out


def bucket(n):
    return '<=8' if n <= 8 else ('9-20' if n <= 20 else '21+')


def report():
    summ = {'token': {}, 'bounds': {}, 'timing': {}, 'kp': {}, 'lowconf': {}}
    for model in ('medium', 'small'):
        tm = 0.0
        for fam in 'xyz':
            for lv in ('std', 'adv'):
                r = load(fam, lv, model)
                if r:
                    tm += r['asr_elapsed_sum_s']
                    summ['timing']['%s_%s_%s' % (model, fam, lv)] = r['asr_elapsed_sum_s']
        summ['timing'][model + '_total'] = round(tm, 1)
    for model in ('medium', 'small'):
        for key in ('direct', 'two_stage'):
            tab = {}
            for fam in 'xyz':
                for lv in ('std', 'adv'):
                    r = load(fam, lv, model)
                    if not r:
                        continue
                    for row in r['rows']:
                        m = row.get(key)
                        if not m or 'stat' not in m:
                            continue
                        st = m['stat']
                        k = '%s|%s|%s' % (fam, st['lang'], bucket(st['n_tok']))
                        tab.setdefault(k, []).append((st['n_match'] / st['n_tok'], st['n_tok'], st['n_match'], row['label'], lv, st['min_sentence_ratio'], st['zero_match_sentences']))
            summ['token']['%s|%s' % (model, key)] = {
                k: dict(rows=len(v), min=round(min(x[0] for x in v), 3), med=round(statistics.median(x[0] for x in v), 3),
                        lt090=sum(1 for x in v if x[0] < 0.9), worst=[(x[3], x[4], x[1], x[2]) for x in sorted(v)[:3]],
                        zero_match_sents=sum(x[6] for x in v), min_sent=round(min(x[5] for x in v), 2)) for k, v in sorted(tab.items())}
    sim = {}
    for model in ('medium', 'small'):
        for key in ('direct', 'two_stage'):
            fails = []
            for fam in 'xyz':
                for lv in ('std', 'adv'):
                    r = load(fam, lv, model)
                    if not r:
                        continue
                    for row in r['rows']:
                        m = row.get(key)
                        if m and 'stat' in m and not S.token_gate(m['stat'], S.DEFAULT_THRESHOLDS):
                            st = m['stat']
                            fails.append((fam, lv, row['label'], st['lang'], st['n_match'], st['n_tok']))
                        if m and 'error' in m:
                            fails.append((fam, lv, row['label'], 'ERROR', m['error'][:140]))
            sim['%s|%s' % (model, key)] = fails
    summ['gate_sim_default_thresholds'] = sim
    for fam in 'xyz':
        for lv in ('std', 'adv'):
            med, sm = load(fam, lv, 'medium'), load(fam, lv, 'small')
            if not med:
                continue
            e = {'direct_vs_two_stage(medium)': diff_between(eps(med, 'direct'), eps(med, 'two_stage'))}
            if sm:
                e['medium_vs_small(direct)'] = diff_between(eps(med, 'direct'), eps(sm, 'direct'))
                e['medium_vs_small(two_stage)'] = diff_between(eps(med, 'two_stage'), eps(sm, 'two_stage'))
            summ['bounds']['%s_%s' % (fam, lv)] = {k: dist(v) for k, v in e.items()}
            ts = {'exact': 0, 'merged': 0, 'split': 0}
            for r in med['rows']:
                if 'two_stage' in r and 'stat' in r['two_stage']:
                    for k in ts:
                        ts[k] += r['two_stage']['stat']['display_status'][k]
            summ['lowconf']['%s_%s' % (fam, lv)] = dict(
                sentences=sum(r.get('n_sent', 0) for r in med['rows']),
                direct_low_conf=sum(r['direct']['stat']['low_conf'] for r in med['rows'] if 'direct' in r and 'stat' in r['direct']),
                two_stage_low_conf=sum(r['two_stage']['stat']['low_conf'] for r in med['rows'] if 'two_stage' in r and 'stat' in r['two_stage']),
                min_pause_direct=min([r['direct']['stat']['min_pause'] for r in med['rows'] if 'direct' in r and 'stat' in r['direct'] and r['direct']['stat']['min_pause'] is not None], default=None),
                two_stage_display_status=ts)
    for model in ('medium', 'small'):
        m = load('x', 'adv', model)
        if m:
            summ['dev_final_vs_moon_adv(%s)' % model] = dev_moon_adv(m)
    for fam in 'xyz':
        for lv in ('std', 'adv'):
            r = load(fam, lv, 'medium')
            if not r:
                continue
            summ['kp']['%s_%s' % (fam, lv)] = [dict(label=x['label'], nblocks=len(x['blocks']), kp_en=x.get('kp_en'), err=x.get('kp_error'), expr=x['kp_expr'][:1], asr=x['asr_text'][:80]) for x in r['rows'] if x['kind'] == 'kp']
    json.dump(summ, open(os.path.join(OUT, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    report()
