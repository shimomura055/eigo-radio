"""PNPS-PLAN-02: 同綴り衝突フラグ候補(内部大文字=CamelCase)の保存原稿での出現数(読取専用・API 0)。"""
import json, re, collections, pronouncing
pairs = [json.loads(l) for l in open('docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/pairs_02.jsonl', encoding='utf8')]
canon = {p['canonical'] for p in pairs if not re.search(r'[぀-ヿ一-鿿]', p['canonical'])}
cnt = collections.Counter()
for c in canon:
    for w in set(re.findall(r"[A-Za-z][A-Za-z0-9]*", c)):
        if re.search(r'[a-z][A-Z]', w): cnt[w] += 1
rows = sorted(cnt.items(), key=lambda x: -x[1])
print('distinct CamelCase tokens', len(rows))
for w, n in rows:
    print(f"{w:22} texts={n:3} cmu={'Y' if pronouncing.phones_for_word(w.lower()) else 'N'}")
