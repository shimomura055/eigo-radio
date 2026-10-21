"""PNMH-01 A-2: er094_pnmh_regression_01.py の head/off/on 出力を比較し差分表を作る(API 0)。"""
import json, sys, os, collections
d = sys.argv[1]
L = lambda n: json.load(open(os.path.join(d, n), encoding="utf-8"))
head, off, on = L("pairs_head.json"), L("pairs_off.json"), L("pairs_on.json")
pairs = [json.loads(l) for l in open("docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/pairs_02.jsonl", encoding="utf-8")]
res = {"n": len(pairs)}
res["off_vs_head_byte_identical"] = (json.dumps(off, sort_keys=True) == json.dumps(head, sort_keys=True))
chg = []
t2f = 0; sp_t2f = 0
for i, (h, o, p) in enumerate(zip(head, on, pairs)):
    if h != o:
        chg.append({"idx": i, "canonical": p["canonical"], "asr": p["asr"], "origins": p.get("origins"),
                    "before": [h["classification"], h["should_pass"], h["final"]], "after": [o["classification"], o["should_pass"], o["final"]],
                    "diff_keys_added": "multiword_homophone" in o["diffs"]})
    if h["should_pass"] and not o["should_pass"]: sp_t2f += 1
    if h["final"].startswith("PASS") and not o["final"].startswith("PASS"): t2f += 1
res["should_pass_True_to_False"] = sp_t2f
res["final_PASS_to_NOT_PASS"] = t2f
res["should_pass_False_to_True"] = sum(1 for h, o in zip(head, on) if (not h["should_pass"]) and o["should_pass"])
res["final_NOT_PASS_to_PASS"] = sum(1 for h, o in zip(head, on) if h["final"] == "NOT_PASS" and o["final"].startswith("PASS"))
res["classification_changed"] = sum(1 for h, o in zip(head, on) if h["classification"] != o["classification"])
res["n_changed_pairs"] = len(chg)
res["changed_pairs"] = chg
uniq = collections.Counter((c["canonical"][:0] + json.dumps(c["before"]) + "->" + json.dumps(c["after"])) for c in chg)
res["transition_counts"] = dict(uniq)
res["origin_totals"] = dict(collections.Counter(o for p in pairs for o in p.get("origins", [])))
json.dump(res, open(os.path.join(d, "pairs_before_after_diff.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("changed_pairs",)}, ensure_ascii=False, indent=1))
for c in chg: print(c["idx"], c["origins"], "|", c["canonical"][:70], "|", c["asr"][:70], c["before"], "->", c["after"])
