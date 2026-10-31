# -*- coding: utf-8 -*-
"""JA-GLOSS-NUANCE-01: newgen_records_all_01.json(er019/er026/er121のrun出力から収集した gloss生成記録)の集計(読取専用・API 0)。"""
import json, sys, collections, re
d = json.load(open(sys.argv[1], encoding="utf-8"))
by = collections.OrderedDict()
for r in d:
    by.setdefault(((r["key_phrase"] or "").lower(), r["gloss"]), r)
tilde = lambda s: (s or "").replace("〜", "～")
single = [r for (kp, g), r in by.items() if " " not in kp]
multi = [r for (kp, g), r in by.items() if " " in kp]
print("raw records", len(d), "unique (key_phrase,gloss)", len(by), "single-word", len(single), "multi-word", len(multi))
for name, grp in (("single", single), ("multi", multi)):
    c = collections.Counter(r["conveys"] for r in grp)
    same = sum(1 for r in grp if tilde(r["gloss"]) == tilde(r["naive_ja"]))
    print(name, "conveys", dict(c), "gloss==naive_ja", same, f"({same/len(grp):.0%})")
    for cv in ("yes", "partly", "no"):
        sub = [r for r in grp if r["conveys"] == cv]
        s2 = sum(1 for r in sub if tilde(r["gloss"]) == tilde(r["naive_ja"]))
        print("   ", cv, len(sub), "same", s2, "diff", len(sub) - s2)
print("mean gloss length single", round(sum(len(r["gloss"]) for r in single) / len(single), 2), "multi", round(sum(len(r["gloss"]) for r in multi) / len(multi), 2))
lst = [r for r in by.values() if re.search("[、,，/／]|または|もしくは", r["gloss"]) or re.search("[（(]", r["gloss"])]
print("list-like or parenthesis glosses:", len(lst), [(r["key_phrase"], r["gloss"]) for r in lst])
