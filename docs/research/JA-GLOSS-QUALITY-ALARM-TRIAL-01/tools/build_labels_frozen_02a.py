# -*- coding: utf-8 -*-
"""委任_02A: ブラインド裁定の集約 -> labels_frozen_01.json, adjudication/stats_02a.json (API 0)。
入力: adjudication/{blind_map.json, pass1_exc.txt, pass2_exc.txt, pass3.txt, pool.json}, eval_set/items.json
使い方: python tools/build_labels_frozen_02a.py  (出力は決定論)"""
import json, os, random, math

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = os.path.join(R, 'adjudication')


def load(p):
    return json.load(open(p, encoding='utf8'))


def rd(f):
    d = {}
    for l in open(f, encoding='utf8'):
        l = l.strip()
        if not l:
            continue
        p = l.split('|')
        d[p[0]] = dict(label={'p': 'problem', 'n': 'normal', 'x': 'exclude'}.get(p[1], p[1]), severity=p[2] or None, category=int(p[3]) if p[3] else None,
                       reason_ja=p[4], suggestion=(p[5] if len(p) > 5 else ''))
    return d


bm = load(os.path.join(A, 'blind_map.json'))
pool = {q['pid']: q for q in load(os.path.join(A, 'pool.json'))}
items = {x['id']: x for x in load(os.path.join(R, 'eval_set', 'items.json'))}
p1 = rd(os.path.join(A, 'pass1_exc.txt'))
p2 = rd(os.path.join(A, 'pass2_exc.txt'))
p3 = rd(os.path.join(A, 'pass3.txt'))
NORMAL = '文脈上の語義と一致し、日本語も自然(好み水準の差のみ)'
BORDER = {
    'BL-016': '説明的だが代入可能で意味は正確', 'BL-049': '婉曲(眠り)で像は変わるが死の意味は保たれる',
    'BL-093': '説得と納得の差はあるが意味は通る', 'BL-106': '笛を警報に置換だが機能は同じ',
    'BL-141': '笛を警報に置換だが機能は同じ', 'BL-115': 'パターン表記で硬いが意味は正確',
    'BL-179': '足を引っ張るはやや悪意含みだが自然', 'BL-184': '『終わりまで』は不要だが全期間の意味は通る',
    'BL-261': '『終わりまで』は不要だが全期間の意味は通る', 'BL-192': 'drownを受身的に訳すが語義として妥当', 'BL-292': 'drownを受身的に訳すが語義として妥当', 'BL-293': '婉曲(眠り)で像は変わるが死の意味は保たれる',
    'BL-257': '定義的だが代入可能', 'BL-213': 'スポンサー支援の言い方は広告の意味と概ね一致',
    'BL-332': '比喩の指す意味を書く承認済み生成仕様に沿う(第3判定でnormal)'}
for k in ('BL-074', 'BL-130', 'BL-198', 'BL-237'):
    BORDER[k] = 'frustrateを『いら立たせる』は感情寄りだが文脈上の意味は通る'


def lab(d, k):
    return d.get(k, dict(label='normal'))['label']


def kappa(a, b):
    cls = ['normal', 'problem', 'exclude']
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cls)
    return ((po - pe) / (1 - pe) if pe < 1 else 1.0), po


ids = sorted(bm)
l1 = [lab(p1, k) for k in ids]
l2 = [lab(p2, k) for k in ids]
kap, po = kappa(l1, l2)
disagree = [k for k, x, y in zip(ids, l1, l2) if x != y]
recs = []
for k in ids:
    if k in disagree:
        f = dict(p3[k]); method = 'pass3(不一致)'
    else:
        f = dict(p1.get(k, dict(label='normal'))); method = 'pass1=pass2'
    if f['label'] == 'normal':
        f['reason_ja'] = BORDER.get(k, NORMAL)
    r = bm[k]
    src = r['src_id']
    if r['src'] == 'eval':
        it = items[src]
        pop = it['tier']; split = it['split']; indev = (it['split'] == 'dev')
        art = it['article_key']; fam = it['family']; devart = indev
    else:
        q = pool[src]
        pop = 'POOL'; split = 'pool'; indev = q['in_dev_set']; art = q['slug']; fam = q['family']; devart = q['dev_article']
    recs.append(dict(source_id=src, blind_id=k, population=pop, split=split, in_dev_set=indev, dev_article=devart,
                     family=fam, article=art, level=r['level'], expression=r['expression'], current_ja=r['current_ja'],
                     sentence_en=r['sentence_en'], label=f['label'], severity=f.get('severity'), category=f.get('category'),
                     reason_ja=f['reason_ja'], suggestion=f.get('suggestion', ''),
                     borderline_normal=(f['label'] == 'normal' and k in BORDER),
                     pass1=lab(p1, k), pass2=lab(p2, k), decided_by=method))
grp = {}
for x in recs:
    grp.setdefault((x['expression'], x['current_ja'], x['sentence_en']), []).append(x)
incons = [[y['blind_id'] for y in v] for v in grp.values() if len({(y['label'], y['severity'], y['category']) for y in v}) > 1]
t1map = {}
for t in items.values():
    if t['tier'] != 'T1':
        continue
    m = [x for x in recs if x['expression'] == t['expression'] and x['current_ja'] == t['current_ja']]
    t1map[t['id']] = dict(expression=t['expression'], current_ja=t['current_ja'], split=t['split'], severity_agent=t['severity'],
                          matched_blind=[(x['blind_id'], x['population'], x['label'], x['severity'], x['category']) for x in m])


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def cnt(rs):
    n = len(rs)
    p = sum(x['label'] == 'problem' for x in rs)
    return dict(n=n, problem=p, normal=sum(x['label'] == 'normal' for x in rs), exclude=sum(x['label'] == 'exclude' for x in rs),
                rate=round(p / n, 4) if n else None, wilson95=wilson(p, n))


P = [x for x in recs if x['population'] == 'POOL']
stats = dict(
    n=len(recs), kappa=round(kap, 4), observed_agreement=round(po, 4), disagree=disagree,
    pass1={c: l1.count(c) for c in ('normal', 'problem', 'exclude')}, pass2={c: l2.count(c) for c in ('normal', 'problem', 'exclude')},
    by_population={pp: cnt([x for x in recs if x['population'] == pp]) for pp in ('T2', 'T4', 'POOL')},
    pool_all=cnt(P), pool_excl_dev_items=cnt([x for x in P if not x['in_dev_set']]), pool_dev_items=cnt([x for x in P if x['in_dev_set']]),
    pool_excl_dev_articles=cnt([x for x in P if not x['dev_article']]), pool_dev_articles=cnt([x for x in P if x['dev_article']]),
    pool_by_family={f: cnt([x for x in P if x['family'] == f]) for f in 'XYZ'},
    pool_by_level={l: cnt([x for x in P if x['level'] == l]) for l in ('Standard', 'Advanced')},
    pool_excl_dev_by_family={f: cnt([x for x in P if x['family'] == f and not x['in_dev_set']]) for f in 'XYZ'},
    pool_excl_dev_by_level={l: cnt([x for x in P if x['level'] == l and not x['in_dev_set']]) for l in ('Standard', 'Advanced')},
    severity={s: sum(1 for x in recs if x['severity'] == s) for s in ('major', 'minor', 'inconsistent')},
    severity_pop={pp: {s: sum(1 for x in recs if x['population'] == pp and x['severity'] == s) for s in ('major', 'minor')} for pp in ('T2', 'T4', 'POOL')},
    category={str(c): sum(1 for x in recs if x['category'] == c) for c in range(1, 7)},
    category_pop={pp: {str(c): sum(1 for x in recs if x['population'] == pp and x['category'] == c) for c in range(1, 7)} for pp in ('T2', 'T4', 'POOL')},
    borderline_normal=[x['blind_id'] for x in recs if x['borderline_normal']], inconsistent_duplicates=incons, t1_rubric_map=t1map)
rnd = random.Random(20261101)
stats['spot_check_20_seed20261101'] = sorted(rnd.sample(ids, 20))
json.dump(stats, open(os.path.join(A, 'stats_02a.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
meta = dict(schema='jaq_labels_frozen_v1', managed_id='JA-GLOSS-QUALITY-ALARM-TRIAL-01', delegation='02A', frozen_on='2026-10-31',
            rule_ja='本ファイルは凍結。以後の付け替え禁止(Trial実行後の再ラベルを含む)。変更が必要なら変更理由・日時・変更前の結果を別途追記し、本ファイルは書き換えない。',
            rubric='ADJUDICATION_RUBRIC_01.md', blind=True,
            adjudicator='Claude Sonnet(裁定者)。検査器(Luna)出力は一切未使用。第1/第2/第3判定とも同一モデル', n_items=len(recs))
t3p = [dict(source_id=x['id'], population='T3P', split=x['split'], family=x['family'], article=x['article_key'], level=x['level'],
            expression=x['expression'], current_ja=x['current_ja'], synthetic_of=x['synthetic_of'], synthetic_of_id=x['synthetic_of_id'],
            label='problem', severity=x['severity'], category=x['category'], rule_id=x['rule_id'],
            basis='合成による確定(ブラインド裁定の対象外。作成規則=T3PRIME_RULES_02.md)') for x in items.values() if x['tier'] == 'T3P']
open(os.path.join(R, 'labels_frozen_01.json'), 'w', encoding='utf8', newline='').write(
    json.dumps(dict(meta=meta, items=recs, t3prime=t3p), ensure_ascii=False, indent=1, sort_keys=True))
print(json.dumps({k: stats[k] for k in ('n', 'kappa', 'observed_agreement', 'disagree', 'pass1', 'pass2', 'by_population', 'pool_all',
                                         'pool_excl_dev_items', 'pool_excl_dev_articles', 'severity', 'category', 'inconsistent_duplicates')},
                 ensure_ascii=False, indent=1))
print(json.dumps(t1map, ensure_ascii=False, indent=1))
