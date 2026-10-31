import json, pathlib, collections
D = pathlib.Path(__file__).parent
rows = {r['pid']: r for r in json.load(open(D/'judged_p1.json', encoding='utf8')) if r['cat'] != 0}
key = json.load(open(D/'key_p2.json'))
done = [l.split()[1] for l in open(D/'judge_p2.txt', encoding='utf8') if l.startswith('SHEET')]
assert len(done) == len(list((D/'blind').glob('p2_*.txt'))) == 7
p2 = {}
for l in open(D/'judge_p2.txt', encoding='utf8'):
    if l.startswith('SHEET') or not l.strip(): continue
    i, c, s = l.strip().split('|'); p2[i] = (int(c), s)
res = []
for i, pid in key.items():
    c, s = p2.get(i, (6, '-')); r = rows[pid]
    res.append(dict(pid=pid, c1=r['cat'], s1=r['sev'], c2=c, s2=s, **{k: r[k] for k in ('family', 'level', 'ttype', 'ja_source')}))
json.dump(res, open(D/'judged_p2.json', 'w'), ensure_ascii=False)
n = len(res)
cat_eq = sum(r['c1'] == r['c2'] for r in res)
bin_eq = sum((r['c1'] == 6) == (r['c2'] == 6) for r in res)
mid_eq = sum(((r['c1'] != 6 and r['s1'] in ('重大', '中'))) == ((r['c2'] != 6 and r['s2'] in ('重大', '中'))) for r in res)
print('N', n, 'cat一致', cat_eq, round(cat_eq/n, 3), '適切/不適切2値一致', bin_eq, round(bin_eq/n, 3), '中以上2値一致', mid_eq, round(mid_eq/n, 3))
# kappa binary problem
a = [r['c1'] != 6 for r in res]; b = [r['c2'] != 6 for r in res]
po = sum(x == y for x, y in zip(a, b))/n; pa = sum(a)/n; pb = sum(b)/n
pe = pa*pb + (1-pa)*(1-pb); print('kappa(問題広義)', round((po-pe)/(1-pe), 3), 'p1 prob', sum(a), 'p2 prob', sum(b))
a = [r['c1'] != 6 and r['s1'] in ('重大', '中') for r in res]; b = [r['c2'] != 6 and r['s2'] in ('重大', '中') for r in res]
po = sum(x == y for x, y in zip(a, b))/n; pa = sum(a)/n; pb = sum(b)/n
pe = pa*pb + (1-pa)*(1-pb); print('kappa(中以上)', round((po-pe)/(1-pe), 3), 'p1', sum(a), 'p2', sum(b))
dis = [r for r in res if (r['c1'] == 6) != (r['c2'] == 6)]
print('2値不一致', len(dis)); 
ct = collections.Counter((r['c1'], r['c2']) for r in res if r['c1'] != r['c2']); print(sorted(ct.items()))
