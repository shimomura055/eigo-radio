# JTA-01B: End User article.json から 英文<->日本語訳ペアを全件抽出(API 0・読取のみ)
import json, glob, re, pathlib, collections, sys
ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('.')
OUT = pathlib.Path(__file__).parent / 'pairs_all_01.jsonl'
def strip(h): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h or '')).strip()
rows = []
def add(**k): rows.append(k)
for f in sorted(glob.glob(str(ROOT / 'user_test/*/enduser/data/article.json'))):
    a = json.load(open(f, encoding='utf8'))
    art = pathlib.Path(f).parts[-4].replace('family_', '')
    fam = a['family']
    add(article=art, family=fam, level='-', ttype='title', ja_source='title_ja', en=a['topic_en'], ja=a['title_ja'], loc='title_ja', how='-', conf=None)
    for lv, L in a['levels'].items():
        for p in L['parts']:
            ja = p.get('ja')
            if ja:
                sm = {s['sid']: s['text'] for pa in p['paragraphs'] for s in pa}
                for g in p.get('ja_align') or []:
                    if g.get('ja') is None:
                        add(article=art, family=fam, level=lv, ttype=p['kind'], ja_source=p.get('ja_source'), en=' '.join(sm[x] for x in g['sids']), ja=None, loc=f"{p['key']}#g{g['g']}", how=g.get('how'), conf=g.get('conf'), nsent=len(g['sids']), unaligned=True)
                        continue
                    pi, s, e = g['ja']
                    add(article=art, family=fam, level=lv, ttype=p['kind'], ja_source=p.get('ja_source'),
                        en=' '.join(sm[x] for x in g['sids']), ja=ja[pi][s:e], loc=f"{p['key']}#g{g['g']}",
                        how=g.get('how'), conf=g.get('conf'), nsent=len(g['sids']))
            for k in p.get('kp') or []:
                if lv == 'std':
                    add(article=art, family=fam, level=lv, ttype='kp_ja', ja_source='kp', en=k['en'], ja=k['text'], loc=p['key'])
            for gl in p.get('glossary') or []:
                add(article=art, family=fam, level=lv, ttype='gloss', ja_source='glossary', en=gl['en'], ja=gl['ja'], loc=p['key'])
        for i, v in enumerate(L['vocab']):
            fl = {x['label']: strip(x['html']) for x in v['fields']}
            if fl.get('本文中の意味'):
                add(article=art, family=fam, level=lv, ttype='vocab_meaning', ja_source='vocab', en=v['heading'], ja=fl['本文中の意味'], loc=f'vocab{i}')
            if fl.get('日本語訳'):
                add(article=art, family=fam, level=lv, ttype='vocab_sentence', ja_source='vocab', en=fl.get('本文の英文', ''), ja=fl['日本語訳'], loc=f'vocab{i}')
        for i, g in enumerate(L['grammar']):
            fl = {x['label']: strip(x['html']) for x in g['fields']}
            ja = fl.get('日本語訳')
            if ja:
                add(article=art, family=fam, level=lv, ttype='grammar_sentence', ja_source='grammar', en=fl.get('対象となる本文英文', ''), ja=ja, loc=f'grammar{i}')
with open(OUT, 'w', encoding='utf8') as w:
    for i, r in enumerate(rows):
        r['pid'] = i
        w.write(json.dumps(r, ensure_ascii=False) + '\n')
c = collections.Counter((r['family'], r['level'], r['ttype'], r['ja_source']) for r in rows)
for k, v in sorted(c.items()): print(k, v)
print('TOTAL', len(rows))
