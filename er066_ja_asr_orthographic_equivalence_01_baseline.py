# Baseline: 収集済みpairを現行Production関数(Resolver LLM OFF、API不使用)で分類する。副作用なし。
import json, re, sys, collections
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
OUT = "er066_output/ja_asr_orthographic_equivalence_01"
SYN = re.compile(r"synthetic|test_dataset|additive|counterexample|reproduction_cases|candidate_a_dry|er058_output/ja_local|regression_result|er066_output")
d = json.load(open(f"{OUT}/harvest_raw_01.json", encoding="utf-8"))
rows = []
for x in d:
    r = javal.classify_ja_asr_match(x["canonical"], x["asr"], allow_reading_resolver=False)
    real = any(not SYN.search(s) for s in x["sources"])
    rows.append({**x, "real": real, "prod_cls": r.classification, "prod_pass": r.should_pass,
                 "prod_reason": r.reason[:200], "number_mm": r.protected.number_mismatches,
                 "neg_mm": r.protected.negation_mismatches})
json.dump(rows, open(f"{OUT}/baseline_prod_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
c = collections.Counter((r["real"], r["prod_cls"]) for r in rows)
for k, v in sorted(c.items()): print(k, v)
