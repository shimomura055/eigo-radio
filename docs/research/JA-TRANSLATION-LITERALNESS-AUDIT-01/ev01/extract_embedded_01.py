# 解説文(vocab解説/grammar解説)に埋め込まれた 「英語（日本語訳）」「英語は「日本語」」型の対訳を抽出(API 0)。
import json, glob, re, pathlib, random, collections
ROOT = pathlib.Path(__file__).resolve().parents[4]
out = []
pat1 = re.compile(r'<(?:b|i)>([^<]{2,80})</(?:b|i)>\s*[（(]([^）)]{1,60})[）)]')
pat2 = re.compile(r'<(?:b|i)>([^<]{2,80})</(?:b|i)>\s*(?:は|の)?[、]?「([^」]{1,40})」(?:という意味|の意味|と訳)')
for f in sorted(glob.glob(str(ROOT/'user_test/*/enduser/data/article.json'))):
    a = json.load(open(f, encoding='utf8')); art = pathlib.Path(f).parts[-4].replace('family_', '')
    for lv, L in a['levels'].items():
        blocks = [('vocab', v['heading'], x['label'], x['html']) for v in L['vocab'] for x in v['fields'] if x['label'] == '解説']
        blocks += [('grammar', str(i), x['label'], x['html']) for i, g in enumerate(L['grammar']) for x in g['fields'] if x['label'] in ('文法・構文の仕組み', '意味・ニュアンス・表現効果')]
        for kind, head, label, html in blocks:
            for m in list(pat1.finditer(html)) + list(pat2.finditer(html)):
                en, ja = m.group(1).strip(), m.group(2).strip()
                if not re.search(r'[ぁ-んァ-ン一-龥]', ja): continue
                out.append(dict(article=art, family=a['family'], level=lv, ttype='embedded_'+kind, ja_source='explanation', en=en, ja=ja, loc=f'{kind}:{head}:{label}'))
random.Random(7).shuffle(out)
for i, r in enumerate(out): r['pid'] = 100000 + i
json.dump(out, open(pathlib.Path(__file__).parent/'pairs_embedded_01.json', 'w', encoding='utf8'), ensure_ascii=False)
print(len(out), collections.Counter((r['family'], r['level'], r['ttype']) for r in out))
