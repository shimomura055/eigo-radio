# 第2判定(blind, ID再採番・順序再シャッフル・第1判定結果/理由非表示)。対象=第1判定で6以外の全件 + 第1判定=6の層別無作為(各層最大8)
import json, random, collections, pathlib
D = pathlib.Path(__file__).parent
rows = json.load(open(D/'judged_p1.json', encoding='utf8'))
rnd = random.Random(20261101)
non6 = [r for r in rows if r['cat'] not in (0, 6)]
st = collections.defaultdict(list)
for r in rows:
    if r['cat'] == 6: st[(r['family'], r['level'], r['ttype'], r['ja_source'])].append(r)
samp6 = []
for k, v in sorted(st.items()):
    samp6 += rnd.sample(v, min(8, len(v)))
sel = non6 + samp6
rnd.shuffle(sel)
ids = rnd.sample(range(1000, 10000), len(sel))
key = {}
(D/'blind').mkdir(exist_ok=True)
for k in range(0, len(sel), 60):
    with open(D/'blind'/f'p2_{k//60+1:02d}.txt', 'w', encoding='utf8') as w:
        for r, i in zip(sel[k:k+60], ids[k:k+60]):
            key[f'C{i}'] = r['pid']
            w.write(f"C{i} [{r['ttype']}]\nEN: {r['en']}\nJA: {r['ja']}\n\n")
json.dump(key, open(D/'key_p2.json', 'w'))
print(len(non6), len(samp6), len(sel))
