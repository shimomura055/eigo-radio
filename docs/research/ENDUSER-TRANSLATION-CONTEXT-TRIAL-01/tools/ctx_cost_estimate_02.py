# 方式別の追加input token・費用/記事セット見積(API 0)。換算=probe実測 0.25 token/英字(ev04_probe)。単価=gpt-6-luna input 16円/1Mtoken(er009 pricing)。
import json, glob, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__)); import ctx_methods_02 as CM
TPC, YEN_IN = 0.25, 16.0 / 1e6
rows = collections.defaultdict(lambda: collections.defaultdict(list)); sets = collections.defaultdict(lambda: collections.defaultdict(float))
ncalls = collections.defaultdict(int)
for f in sorted(glob.glob("user_test/*/enduser/data/article.json")):
    art = json.load(open(f, encoding="utf-8")); d = os.path.normpath(f).split(os.sep)[1]
    for lv, L in art["levels"].items():
        for p in L["parts"]:
            if p.get("ja_source") != "generated": continue
            ncalls[d] += 1
            for m in "ABCDE":
                c = CM.build_context(m, art, lv, p["key"]); ch = sum(len(x["en"]) for x in c)
                rows[m][art["family"]].append(ch); sets[d][m] += ch
out = {"tokens_per_char": TPC, "yen_per_input_token": YEN_IN, "per_method_family": {}, "per_article_set": {}}
for m in "ABCDE":
    out["per_method_family"][m] = {fam: {"parts": len(v), "mean_ctx_chars": round(sum(v) / len(v)), "max_ctx_chars": max(v), "mean_extra_input_tokens": round(sum(v) / len(v) * TPC)} for fam, v in rows[m].items()}
for d in sets:
    out["per_article_set"][d] = {"translate_calls_min": ncalls[d], **{m: {"extra_input_tokens": round(sets[d][m] * TPC), "extra_cost_jpy_min": round(sets[d][m] * TPC * YEN_IN, 3)} for m in "ABCDE"}}
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for m in "ABCDE": print(m, out["per_method_family"][m])
for d, v in out["per_article_set"].items(): print(d, v["translate_calls_min"], {m: v[m]["extra_cost_jpy_min"] for m in "BCDE"})
