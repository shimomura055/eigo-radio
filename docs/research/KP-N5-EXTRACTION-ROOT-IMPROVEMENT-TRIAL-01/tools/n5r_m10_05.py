"""Trial専用(API 0)。委任_05: N5配線後のProduction実run(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 M10、同一本文の3セル)のphrase kind最終候補を参考列として抽出。
usage: python n5r_m10_05.py -> ev05/m10_reference_05.json"""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
W = os.path.join(ROOT, "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01")
OUT = os.path.join(ROOT, "docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01/ev05/m10_reference_05.json")
res = {}
for case in ("untidi_a2", "untidi_b1b", "melos_a2"):
    for ev in ("ev02", "ev03"):
        p = os.path.join(W, ev, "m10", case, "result.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8")).get("doc") or {}
        res[f"{case}/{ev}"] = [{"selection_phrase": c.get("selection_phrase"), "used_form": c.get("used_form"), "japanese_gloss": c.get("japanese_gloss"), "origin": c.get("origin")}
                               for c in d.get("candidates", []) if c.get("kind") == "phrase"]
        res[f"{case}/{ev}_dropped"] = [{"phrase": x.get("selection_phrase") or x.get("phrase"), "stage": x.get("stage"), "reasons": x.get("reasons")} for x in d.get("dropped", [])]
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, len(v))
    for x in v:
        print("   ", x)
