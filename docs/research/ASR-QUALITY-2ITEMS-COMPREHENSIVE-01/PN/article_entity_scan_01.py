# -*- coding: utf-8 -*-
"""保存済みX記事本文(a2/b1b article.md)+Z脚本(std.md/r2.md)の英語本文から、大文字始まり語(一般語を除く)を
D1=本文中で文中(文頭/引用直後/見出し以外)に大文字で現れた語 / D2=文頭・引用直後・見出しにしか大文字で現れない語 に分け、
現行PNAP proper_noun_evidence(per article全文を1 segmentとみなした近似でなくsentence単位)で根拠が出るかを数える。API 0, read-only。"""
import glob, re, sys, json, collections, os
sys.path.insert(0, ".")
import er103_proper_noun_alarm_policy_01 as pol
files = []
for g in ("er019_output/*/run_*/a2/article.md", "er019_output/*/run_*/b1b/article.md",
          "er026_output/family_z_production_e2e_01/*/run_*/writer/std.md", "er026_output/family_z_production_e2e_01/*/run_*/writer/r2.md"):
    files += glob.glob(g)
# 同一slug/最新runのみ(重複回避): slugごとに最終更新が最新のrunを採用
best = {}
for f in files:
    fn = f.replace("\\", "/")
    parts = fn.split("/")
    key = (parts[1], parts[2], parts[-1]) if "er019" in fn else (parts[2], parts[-1])
    if key not in best or os.path.getmtime(f) > os.path.getmtime(best[key]):
        best[key] = f
files = sorted(best.values())
print("articles", len(files))
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")
mid, init, low = collections.defaultdict(set), collections.defaultdict(set), collections.defaultdict(set)
for f in files:
    t = open(f, encoding="utf-8").read()
    t = re.sub(r"^#+ .*$", lambda m: m.group(0), t, flags=re.M)
    for line in t.splitlines():
        heading = line.startswith("#")
        for m in WORD.finditer(line):
            w = m.group(0).strip("'’-")
            if len(w) < 2: continue
            lw = pol._fold(w)
            before = line[:m.start()].rstrip()
            if not w[0].isupper():
                low[lw].add(f); continue
            sent_init = heading or before == "" or bool(re.search(r"[.!?:]['\"’”)\]]*$", before)) or bool(re.search(r"[\"“‘'(\[]$", before))
            (init if sent_init else mid)[lw].add(f)
res = {"D1": {}, "D2": {}}
for lw in set(mid) | set(init):
    if pol.is_general_word(lw.strip("'")):   # CMU & zipf>=4 は一般語(名詞の疑い薄 or 同形名はここでは別枠)
        general = True
    else:
        general = False
    oov = not pol._default_cmu_has(lw.split("'")[0]) if lw else False
    rec = {"general": general, "cmu_oov": oov, "arts": len(mid.get(lw, set()) | init.get(lw, set())), "lower_seen": lw in low, "zipf": round(pol._default_zipf(lw), 2)}
    (res["D1"] if lw in mid else res["D2"])[lw] = rec
def summ(name, d):
    ng = {k: v for k, v in d.items() if not v["general"]}
    print(name, "all", len(d), "non-general", len(ng), "cmu_oov", sum(v["cmu_oov"] for v in ng.values()), "cmu_in-vocab", sum(not v["cmu_oov"] for v in ng.values()))
summ("D1(mid-sentence capital)", res["D1"]); summ("D2(only start/quote/heading)", res["D2"])
d2 = {k: v for k, v in res["D2"].items() if not v["general"] and not v["lower_seen"]}
print("D2 non-general, never lowercase in corpus:", len(d2))
print(sorted(f"{k}({v['zipf']}{',OOV' if v['cmu_oov'] else ''})" for k, v in d2.items()))
d2l = {k for k, v in res["D2"].items() if not v["general"] and v["lower_seen"]}
print("D2 non-general but lowercase seen (=ordinary word):", len(d2l))
json.dump(res, open("docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/article_entity_scan_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
