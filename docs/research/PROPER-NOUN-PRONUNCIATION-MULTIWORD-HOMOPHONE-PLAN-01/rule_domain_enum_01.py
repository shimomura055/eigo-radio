"""PNMH-PLAN-01: 提案ルールの『適用域』を可視化(API 0)。保存済み原稿に出る語彙(CMU収録)について、
canonical単語X(3字以上)と等価になる 2語連続(w1 w2) を列挙し(綴りが異なるものに限る)、
(a)主要発音variantのみで成立するか (b)非主要variant(文字読み等)に依存するか を分ける。"""
import sys, os, json, re, itertools, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import proto_multiword_span_01 as P
import pronouncing
vocab = set()
for l in open(os.path.join(HERE, "pairs_01.jsonl"), encoding="utf8"):
    o = json.loads(l)
    for t in P.val.tokenize(o["canonical"]):
        if re.fullmatch(r"[a-z']{2,}", t): vocab.add(t)
vocab = sorted(w for w in vocab if pronouncing.phones_for_word(w))
print("vocab", len(vocab))
def nostress(ph): return tuple(re.sub(r"\d", "", ph).split())
prim = {w: nostress(pronouncing.phones_for_word(w)[0]) for w in vocab}
allv = {w: {nostress(p) for p in pronouncing.phones_for_word(w)} for w in vocab}
byseq = collections.defaultdict(set)
for w in vocab:
    for s in allv[w]: byseq[s].add(w)
res = []
for w1 in vocab:
    for w2 in vocab:
        if len(w1) < 2 or len(w2) < 2: continue
        for s1 in allv[w1]:
            for s2 in allv[w2]:
                for X in byseq.get(s1 + s2, ()):
                    if len(X) >= 3 and X != w1 + w2 and X not in (w1, w2):
                        only_primary = (s1 == prim[w1] and s2 == prim[w2] and X in [x for x in vocab if prim[x] == s1 + s2])
                        res.append((X, w1, w2, only_primary))
res = sorted(set(res))
out = {"vocab": len(vocab), "n_equiv_triples": len(res), "n_primary_only": sum(1 for r in res if r[3]),
       "examples_primary": [r[:3] for r in res if r[3]][:60], "examples_nonprimary": [r[:3] for r in res if not r[3]][:60]}
json.dump(out, open(os.path.join(HERE, "rule_domain_result_01.json"), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
print(out["n_equiv_triples"], out["n_primary_only"]); print(out["examples_primary"][:40]); print(out["examples_nonprimary"][:40])
