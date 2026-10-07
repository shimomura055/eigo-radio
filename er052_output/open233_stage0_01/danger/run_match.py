# -*- coding: utf-8 -*-
"""100記事を読み込み、文分割、既知NG項目と文の対応(曖昧一致)を作る。出力: match_dump.json / match_review.txt"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import danger_sentence_rules_v0 as D

ROOT = r'C:/Users/tensh/eigo-radio/er052_output'
OUT = os.path.dirname(os.path.abspath(__file__))
SETS = [
    ('b3', 'open233_b3_trial_01/eval/articles', 'open233_b3_trial_01/eval/blind_stage2'),
    ('ccp', 'open233_control_checker_polysemy_trial_01/eval/articles', 'open233_control_checker_polysemy_trial_01/eval/blind'),
    ('rca', 'open233_ng_root_cause_01/eval/articles', 'open233_ng_root_cause_01/blind'),
]
LEDGER = ROOT + '/open233_polysemy_trial_02/ledgers/{slug}/control/research_ledger/verified_fact_ledger.txt'


def rd(p):
    return open(p, encoding='utf8').read()


def load_articles():
    arts = {}
    for sname, aj, bl in SETS:
        for f in sorted(glob.glob(f'{ROOT}/{aj}/*.json')):
            j = json.load(open(f, encoding='utf8'))
            slug, code = j['slug'], j['code']
            base = f'{ROOT}/{bl}/{slug}/{code}'
            arts[f'{sname}:{slug}/{code}'] = dict(
                set=sname, slug=slug, code=code, json=j,
                r0=rd(base + '/ja_writer/original.md'), r2=rd(base + '/ja_writer/revision2.md'),
                en=rd(base + '/b1b/article.md'))
    return arts


def paren_split(t):
    """括弧の外側テキストと内側テキスト群に分ける"""
    out, ins, depth, cur = [], [], 0, ''
    buf = ''
    for ch in t:
        if ch in '(（':
            if depth == 0:
                out.append(buf); buf = ''
            depth += 1
            if depth > 1:
                buf += ch
        elif ch in ')）':
            depth -= 1
            if depth == 0:
                ins.append(buf); buf = ''
            else:
                buf += ch
        else:
            buf += ch
    if depth == 0:
        out.append(buf)
    else:
        ins.append(buf)
    return ' '.join(out), ins


def frag_ja(t):
    outside, ins = paren_split(t)
    frs = []
    for p in re.findall(r'[「『]([^」』]+)[」』]', t):
        frs.append(p)
    pieces = re.split(r'[/／。\n]|…|\.\.\.|EN[:：]|R0[:：]|R1[:：]|R2[:：]|R0〜EN', outside)
    for p in pieces:
        p = p.strip(' 「」『』、')
        if len(re.findall(r'[ぁ-んァ-ヴ一-龥]', p)) >= 5 and not re.search(r'[A-Za-z]{5,} [A-Za-z]{3,}', p):
            frs.append(p)
    for i in ins:
        if re.match(r'\s*(R0|R2|R1)[:：]', i):
            frs.extend([x.strip(' 「」』『、') for x in re.split(r'[/／。]', i[3:]) if len(x.strip()) >= 5])
    return frs


def frag_en(t):
    frs = []
    for m in re.finditer(r'[A-Za-z][^()（）「」。\n]{15,}', t):
        s = m.group(0).strip()
        if len(re.findall(r'[ぁ-んァ-ヴ一-龥]', s)) == 0:
            frs.append(s)
    return frs


def bigr(s):
    s = re.sub(r'[\s、。,.「」『』…]', '', s)
    return set(s[i:i + 2] for i in range(len(s) - 1))


def dice(a, b):
    if not a or not b:
        return 0.0
    return 2 * len(a & b) / (len(a) + len(b))


def best_match(frags, sents, lang):
    best = (0.0, None, None)
    for fr in frags:
        if lang == 'ja':
            fb = bigr(fr)
            for i, (s, pos) in enumerate(sents):
                sb = bigr(s)
                sc = len(fb & sb) / max(1, len(fb))  # fragment containment
                sc = 0.7 * sc + 0.3 * dice(fb, sb)
                if sc > best[0]:
                    best = (sc, i, fr)
        else:
            fw = set(re.findall(r'[a-z0-9]+', fr.lower()))
            for i, (s, pos) in enumerate(sents):
                sw = set(re.findall(r'[a-z0-9]+', s.lower()))
                sc = 0.7 * len(fw & sw) / max(1, len(fw)) + 0.3 * (2 * len(fw & sw) / max(1, len(fw) + len(sw)))
                if sc > best[0]:
                    best = (sc, i, fr)
    return best


def main():
    arts = load_articles()
    res = []
    for key, a in arts.items():
        a['sents'] = {
            'ja': D.structure(a['r2'], 'ja'),
            'en': D.structure(a['en'], 'en'),
            'r0': D.structure(a['r0'], 'ja'),
        }
        for it in a['json'].get('ng_items', []):
            st = it.get('stage', {})
            s0, s1, s2 = bool(st.get('s0')), bool(st.get('s1')), bool(st.get('s2'))
            text = it['text']
            targets = []
            if s1:
                targets.append(('ja', 'ja'))
            if s2:
                targets.append(('en', 'en'))
            if s0 and not s1 and not s2:
                targets.append(('r0', 'ja'))
            r = dict(key=key, id=it['id'], sev=it['severity'], kind=it.get('kind'), fact_id=it.get('fact_id'),
                     stage=dict(s0=s0, s1=s1, s2=s2), text=text, matches={})
            for tname, lang in targets:
                fr = frag_ja(text) if lang == 'ja' else frag_en(text)
                if lang == 'ja' and not fr:
                    fr = [paren_split(text)[1][0]] if paren_split(text)[1] else []
                sc, i, f = best_match(fr, a['sents'][tname], lang)
                r['matches'][tname] = dict(score=round(sc, 3), idx=i, frag=f,
                                           sent=(a['sents'][tname][i][0] if i is not None else None),
                                           pos=(a['sents'][tname][i][1] if i is not None else None))
            res.append(r)
    json.dump(res, open(OUT + '/match_dump.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    with open(OUT + '/match_review.txt', 'w', encoding='utf8') as w:
        for r in res:
            w.write(f"## {r['id']} [{r['sev']}/{r['kind']}] stage={r['stage']}\nNG: {r['text'][:200]}\n")
            for t, m in r['matches'].items():
                w.write(f"  -> {t} score={m['score']} pos={m['pos']}: {m['sent']}\n")
            w.write('\n')
    print(len(arts), 'articles', len(res), 'ng items')


if __name__ == '__main__':
    main()
