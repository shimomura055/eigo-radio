# 第1判定(blind)用シート作成。ID/順序をseedで無作為化。ja_source/family/level/how/confはシートに出さない。
import json, random, pathlib, sys
D = pathlib.Path(__file__).parent
rows = [json.loads(l) for l in open(D / 'pairs_all_01.jsonl', encoding='utf8')]
SHORT = {'kp_ja', 'gloss', 'vocab_meaning'}
pool = [r for r in rows if not r.get('unaligned')]
rnd = random.Random(20261031)
ids = rnd.sample(range(1000, 10000), len(pool))
key = {}
body, short = [], []
for r, i in zip(pool, ids):
    key[f'B{i}'] = r['pid']
    (short if r['ttype'] in SHORT else body).append((f'B{i}', r))
rnd.shuffle(body); rnd.shuffle(short)
def write(items, prefix, n):
    for k in range(0, len(items), n):
        with open(D / 'blind' / f'{prefix}_{k // n + 1:02d}.txt', 'w', encoding='utf8') as w:
            for i, r in items[k:k + n]:
                w.write(f"{i} [{r['ttype']}]\nEN: {r['en']}\nJA: {r['ja']}\n\n")
write(body, 'p1_body', 40); write(short, 'p1_short', 100)
json.dump(key, open(D / 'key_p1.json', 'w'))
print(len(body), len(short), len([r for r in rows if r.get('unaligned')]))
