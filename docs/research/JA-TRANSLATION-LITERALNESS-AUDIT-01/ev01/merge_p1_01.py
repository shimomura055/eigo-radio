import json, pathlib, collections, re
D = pathlib.Path(__file__).parent
rows = {}
for l in open(D/'pairs_all_01.jsonl', encoding='utf8'):
    r = json.loads(l); rows[r['pid']] = r
key = json.load(open(D/'key_p1.json'))
done = [l.split()[1] for l in open(D/'judge_p1.txt', encoding='utf8') if l.startswith('SHEET')]
sheets = sorted(p.stem for p in (D/'blind').glob('p1_*.txt'))
assert set(done) == set(sheets), (set(sheets)-set(done), set(done)-set(sheets))
ex = {}
for l in open(D/'judge_p1.txt', encoding='utf8'):
    if l.startswith('SHEET') or not l.strip(): continue
    i, c, s, n = l.rstrip('\n').split('|', 3); ex[i] = (int(c), s, n)
import os
if os.path.exists(D/'judge_p1_overrides.txt'):
    for l in open(D/'judge_p1_overrides.txt', encoding='utf8'):
        if l.strip():
            i, c, sv, n = l.rstrip().split('|', 3); ex[i] = (int(c), sv, n)
out = []
for i, pid in key.items():
    r = dict(rows[pid]); c, s, n = ex.get(i, (6, '-', ''))
    r.update(bid=i, cat=c, sev=s, note=n); out.append(r)
for r in rows.values():
    if r.get('unaligned'):
        r2 = dict(r); r2.update(bid=None, cat=0, sev='中', note='unaligned: JA非表示(ja_align dropout)'); out.append(r2)
json.dump(out, open(D/'judged_p1.json', 'w', encoding='utf8'), ensure_ascii=False)
print(len(out), len(ex), set(ex) - set(key))
c = collections.Counter(r['cat'] for r in out); print(sorted(c.items()))
