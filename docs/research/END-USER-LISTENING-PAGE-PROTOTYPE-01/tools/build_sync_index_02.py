# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PROTOTYPE-01 委任_02: 01aのsentences.json -> 試作 data/sync_<article>_<lv>.json + sync_index.json。
文の照合は display_text(正規化)ベース。ページ側の文境界と01a側の文境界が違う場合は文字位置アラインメントで時刻を按分し
(status=merged/split)、一致しない文字は mismatch として記録する(黙って捨てない)。時刻は全編(episode)基準へ変換。
出力: user_test/dev_enduser_page_01/data/sync_*.json, sync_index.json, 照合レポート docs/.../sync_match_report_02.json"""
import difflib, json, os, re, unicodedata, html
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SYNC = os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync')
DATA = os.path.join(ROOT, 'user_test/dev_enduser_page_01/data')
REP = os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync_match_report_02.json')
CFG = [('ai_island', 'std', 'std'), ('ai_island', 'adv', 'adv'), ('moon', 'adv', 'moon_adv')]


def norm(s):
    s = unicodedata.normalize('NFKC', html.unescape(s)).lower()
    return re.sub(r'[\s\W_]+', '', s)


def main():
    idx_out, report = {}, {}
    for aid, lv, sd in CFG:
        art = json.load(open(os.path.join(DATA, aid + '.json'), encoding='utf-8'))
        parts = {p['key']: p for p in art['levels'][lv]['parts']}
        ix = json.load(open(os.path.join(SYNC, sd, 'index.json'), encoding='utf-8'))
        out, rep = [], dict(parts={}, totals=dict(page_sentences=0, exact=0, merged=0, split=0, unmatched=0, sync_sentences=0))
        for ent in ix['parts']:
            key = os.path.basename(ent['audio']).replace('.mp3', '')
            P = parts[key]
            S = json.load(open(os.path.join(SYNC, sd, ent['file']), encoding='utf-8'))
            base = P['start']
            assert abs(base - S['part_start_in_episode_s']) < 0.01, (key, base, S['part_start_in_episode_s'])
            ps = [s for para in P['paragraphs'] for s in para]
            ss = S['sentences']
            # sync側の連結文字列と文字->(sentence idx, 位置)
            sn, smap = '', []
            for k, s in enumerate(ss):
                n = norm(s['display_text'])
                smap += [(k, i, len(n)) for i in range(len(n))]
                sn += n
            pn, pr = '', []
            for s in ps:
                n = norm(s['text']); pr.append((len(pn), len(pn) + len(n))); pn += n
            sm = difflib.SequenceMatcher(None, pn, sn, autojunk=False)
            p2s = [None] * len(pn)
            for tag, a1, a2, b1, b2 in sm.get_opcodes():
                if tag == 'equal':
                    for d in range(a2 - a1): p2s[a1 + d] = b1 + d
            rows, prep = [], []
            for s, (a, b) in zip(ps, pr):
                ok = [p2s[i] for i in range(a, b) if p2s[i] is not None]
                cov = len(ok) / max(1, b - a)
                if not ok or cov < 0.6:
                    st = 'unmatched'; prep.append(dict(sid=s['sid'], status=st, coverage=round(cov, 2), text=s['text'])); continue
                i0, i1 = ok[0], ok[-1]
                k0, o0, n0 = smap[i0]; k1, o1, n1 = smap[i1]
                def tm(k, o, n, edge):
                    x = ss[k]; return x['start'] + (x['end'] - x['start']) * (o / n if edge == 's' else (o + 1) / n)
                t0 = ss[k0]['start'] if o0 == 0 else tm(k0, o0, n0, 's')
                t1 = ss[k1]['end'] if o1 == n1 - 1 else tm(k1, o1, n1, 'e')
                if k0 == k1 and o0 == 0 and o1 == n1 - 1: st = 'exact'
                elif k0 == k1: st = 'split'
                else: st = 'merged' if (o0 == 0 and o1 == n1 - 1) else 'split'
                conf = min(ss[k]['confidence'] for k in range(k0, k1 + 1)) if 'confidence' in ss[k0] else None
                rows.append(dict(sid=s['sid'], start=round(base + t0, 3), end=round(base + t1, 3), status=st, conf=conf, cov=round(cov, 2)))
                prep.append(dict(sid=s['sid'], status=st, coverage=round(cov, 2)))
            used = set()
            for r in rows: pass
            out += rows
            t = rep['totals']; t['page_sentences'] += len(ps); t['sync_sentences'] += len(ss)
            for r in prep: t[r['status']] += 1
            rep['parts'][key] = dict(part=ent['part'], page_n=len(ps), sync_n=len(ss), items=[r for r in prep if r['status'] != 'exact'])
        out.sort(key=lambda r: r['start'])
        fn = 'sync_%s_%s.json' % (aid, lv)
        json.dump(dict(kind='REAL_ASR_SILENCE_SNAP', note='01a sentences.json(ASR+無音スナップ)を全編時刻へ変換。精度はユーザー聴感未確認',
                       article=aid, level=lv, sentences=out), open(os.path.join(DATA, fn), 'w', encoding='utf-8'), ensure_ascii=False)
        idx_out.setdefault(aid, {})[lv] = fn
        report['%s/%s' % (aid, lv)] = rep
        print(aid, lv, rep['totals'])
    json.dump(idx_out, open(os.path.join(DATA, 'sync_index.json'), 'w', encoding='utf-8'), indent=1)
    json.dump(report, open(REP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


main()
