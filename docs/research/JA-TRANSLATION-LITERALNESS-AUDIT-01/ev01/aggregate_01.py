import json, pathlib, collections
D = pathlib.Path(__file__).parent
rows = json.load(open(D/'judged_p1.json', encoding='utf8'))
def stat(rs):
    n = len(rs); c = collections.Counter(r['cat'] for r in rs)
    prob = sum(1 for r in rs if r['cat'] not in (6,)); mid = sum(1 for r in rs if r['cat'] != 6 and r['sev'] in ('重大','中'))
    sev = collections.Counter(r['sev'] for r in rs if r['cat'] != 6)
    return n, c, prob, mid, sev
def line(label, rs):
    n, c, prob, mid, sev = stat(rs)
    return f"| {label} | {n} | {c[6]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | {c[5]} | {c[0]} | {prob} ({100*prob/n:.1f}%) | {mid} ({100*mid/n:.1f}%) | {sev['重大']} |"
H = "| 区分 | 件数 | 6適切 | 1欠落 | 2追加 | 3要約統合 | 4意味変化 | 5不適切 | 未表示(ja無) | 問題(広義) | 問題(中以上) | 重大 |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
out = []
def group(title, keyf, rs=rows):
    g = collections.defaultdict(list)
    for r in rs: g[keyf(r)].append(r)
    s = f"### {title}\n\n" + H
    for k in sorted(g): s += line(k, g[k]) + "\n"
    s += line('**合計**', rs) + "\n"
    return s
out.append(group('A. ja_source別(全訳種別)', lambda r: r['ja_source']))
story = [r for r in rows if r['ttype'] in ('story',)]
out.append(group('B. 本文(story)のja_source×Level別', lambda r: f"{r['ja_source']} / {r['level']}", story))
body = [r for r in rows if r['ttype'] in ('story','comment','preview','oneline')]
out.append(group('C. 本文系(story/comment/preview/oneline) ja_source別', lambda r: r['ja_source'], body))
out.append(group('D. Family別(全訳種別)', lambda r: r['family']))
out.append(group('E. 訳種別', lambda r: r['ttype']))
out.append(group('F. Family×Level×訳種別×ja_source', lambda r: f"{r['family']}/{r['level']}/{r['ttype']}/{r['ja_source']}"))
open(D/'aggregate_tables_01.md', 'w', encoding='utf8').write("\n".join(out))
# 例
ex = collections.defaultdict(list)
for r in rows:
    if r['cat'] not in (6,): ex[r['cat']].append(r)
with open(D/'examples_01.md', 'w', encoding='utf8') as w:
    for c in (1,2,3,4,5,0):
        w.write(f"## 分類{c}: {len(ex[c])}件(以下は全件ではなく代表)\n\n")
        for r in ex[c][:6]:
            w.write(f"- [{r['family']}/{r['level']}/{r['ttype']}/{r['ja_source']}/{r['article']}/{r['loc']}] 重大度={r['sev']} note={r['note']}\n  - EN: {r['en']}\n  - JA: {r['ja']}\n")
        w.write("\n")
print(out[0]); print(out[1]); print(out[2]); print(out[3]); print(out[4])
