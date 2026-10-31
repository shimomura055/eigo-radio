# -*- coding: utf-8 -*-
"""JA-GLOSS-NUANCE-01: er019/er026/er121のrun出力から、newgen_meaning_v1(gloss生成)の記録
(key_phrase, japanese_gloss, meaning_in_text_en, naive_ja, naive_ja_conveys, source_sentence)を横断収集する(読取専用・API 0)。
入力: find済みfile一覧(1行1path)。出力: 重複除去(run, key_phrase, gloss)済みJSON。"""
import json, sys, os
REPO = os.environ.get("JAG_REPO", r"C:\Users\tensh\eigo-radio")
lst, out = sys.argv[1], sys.argv[2]
seen, recs = set(), []
def walk(o, f):
    if isinstance(o, dict):
        ga = o.get("gloss_alignment")
        if isinstance(ga, dict) and ga.get("meaning_in_text_en") and (o.get("japanese_gloss") or "").strip():
            k = (f.split("/key_phrases")[0], (o.get("key_phrase") or "").lower(), o["japanese_gloss"])
            if k not in seen:
                seen.add(k)
                recs.append({"run": k[0], "key_phrase": o.get("key_phrase"), "gloss": o["japanese_gloss"],
                             "meaning_in_text_en": ga.get("meaning_in_text_en"), "naive_ja": ga.get("naive_ja"),
                             "conveys": ga.get("naive_ja_conveys"), "source_sentence": o.get("source_sentence"),
                             "gloss_reasoning": ga.get("reasoning")})
        for v in o.values(): walk(v, f)
    elif isinstance(o, list):
        for v in o: walk(v, f)
n = 0
for line in open(lst, encoding="utf-8"):
    p = line.strip()
    if not p: continue
    try:
        d = json.load(open(os.path.join(REPO, p), encoding="utf-8"))
    except Exception:
        continue
    n += 1
    walk(d, p.replace("\\", "/"))
json.dump(recs, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(n, "files", len(recs), "unique records")
