"""ev01 step1/4: 公開Advanced本文(enduser article.json adv)から5表現の使用箇所(分離形含む)と、句動詞・定型表現候補の機械列挙を行う。API 0。
usage: python occurrences.py <repo_root> (cwd不問)。出力: occurrences.json / mech_enum.json"""
import json, re, sys, os
R = sys.argv[1]
A = json.load(open(os.path.join(R, "user_test/family_x_untidiness_family_resource_01/enduser/data/article.json"), encoding="utf-8"))["levels"]["adv"]
OUT = os.path.dirname(os.path.abspath(__file__))
sents = []
for p in A["parts"]:
    for para in p.get("paragraphs") or []:
        for s in para:
            sents.append({"sid": s["sid"], "part": p["label"], "text": re.sub(r"<[^>]+>", "", s["html"]).replace("’", "'").replace("“", '"').replace("”", '"')})
PATS = {
 "put away": r"\bput(?:s|ting)?\b(?:\s+\w+){0,2}?\s+away\b",
 "in the way": r"\bin the way\b",
 "force away": r"\bforc(?:e|es|ed|ing)\b(?:\s+\w+){0,2}?\s+away\b",
 "leave out": r"\b(?:leave|leaves|leaving|left)\b(?:\s+\w+){0,2}?\s+out\b",
 "in sight": r"\bin sight\b",
}
occ = {}
for k, pat in PATS.items():
    occ[k] = [{"sid": s["sid"], "part": s["part"], "match": m.group(0), "sentence": s["text"]} for s in sents for m in re.finditer(pat, s["text"], re.I)]
json.dump({"n_sentences": len(sents), "occurrences": occ}, open(os.path.join(OUT, "occurrences.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in occ.items():
    print(k, len(v))
    for o in v: print("   ", o["sid"], o["part"], "|", o["match"], "|", o["sentence"])
# 機械列挙: 動詞+副詞的小辞(最大1語を挟む)、前置詞句の固定表現候補(in/on/at/by/for + (the) + 名詞)、文頭談話標識
PART = {"up","down","out","off","away","back","in","on","over","through","around","into","along","apart","aside","forward","ahead","by","with","for","to"}
STOP = {"the","a","an","this","that","these","those","it","its","they","them","he","she","we","you","i","is","are","was","were","be","been","being","and","or","but","as","at","of","if","so","than","then","there","here","not","no","to","in","on","for","with","by","from","what","which","who","how","why","where","when","one","some","any","each","every","many","more","most","too","very","just","only","also","still","even","all","both","can","could","may","might","will","would","should","must","do","does","did","have","has","had","my","your","his","her","our","their","me","him","us","who","whom","whose"}
cands = {}
for s in sents:
    toks = re.findall(r"[A-Za-z']+", s["text"])
    low = [t.lower() for t in toks]
    for i in range(len(low) - 1):
        a, b = low[i], low[i+1]
        if b in {"up","down","out","off","away","back","over","through","around","into","along","apart","aside","forward","ahead"} and a not in STOP:
            cands.setdefault("verb+particle: " + toks[i] + " " + toks[i+1], []).append(s["sid"])
        if i + 2 < len(low) and low[i+2] in {"up","down","out","off","away","back","over","through","around","along","apart","aside"} and a not in STOP and b in {"it","that","them","something","things","him","her","this","one"}:
            cands.setdefault("verb+obj+particle: " + " ".join(toks[i:i+3]), []).append(s["sid"])
        if a in {"in","on","at","by","for","under","out","off"} and b not in STOP and i + 1 < len(low):
            cands.setdefault("prep+X: " + toks[i] + " " + toks[i+1], []).append(s["sid"])
        if a in {"in","on","at","by","for","under"} and b in {"the","a"} and i + 2 < len(low):
            cands.setdefault("prep+det+X: " + " ".join(toks[i:i+3]), []).append(s["sid"])
    for m in re.finditer(r"\b(no wonder|in other words|in a way|not so fast|end up|get heated|gets heated|rely on|relied on|help with|helps with|deserve|test whether|without question|just because|straight into|take .{0,25} seriously|turn into|bring(?:ing)? out|take up|taking up|keep(?:s|ing)? .{0,12} in sight|it's not so simple)\b", s["text"], re.I):
        cands.setdefault("pattern: " + m.group(0), []).append(s["sid"])
json.dump({k: sorted(set(v)) for k, v in sorted(cands.items())}, open(os.path.join(OUT, "mech_enum.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(cands), "mech candidates")
for k, v in sorted(cands.items()): print("  ", k, sorted(set(v)))
