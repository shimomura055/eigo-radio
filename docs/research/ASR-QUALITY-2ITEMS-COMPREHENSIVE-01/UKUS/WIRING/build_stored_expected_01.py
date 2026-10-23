# build_stored_expected_01.py -- W-01: 保存rows(+対表sweepの1/50サンプル)の固定expectedをTrial(evaluate_trial)を『オラクル』として作る(Trial撤去前に1回実行)。API 0。
import gzip, json, os, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
import er111_ukus_spelling_trial_01 as T
import er111_ukus_trial_eval_01 as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sweep_trial_vs_prod_01 as S
TBL = S.TBL
rows = [(r["c"], r["a"]) for r in E._collect_rows()]
pj = json.load(open("er109_ukus_pairs_v1.json", encoding="utf-8"))
pairs = [e for e in pj["pairs"] if e.get("active")]
rows += [(c, a) for i, (_, _, c, a) in enumerate(S.cases(pairs)) if i % 50 == 0]
seen, out = set(), []
for c, a in rows:
    if (c, a) in seen: continue
    seen.add((c, a))
    t = T.evaluate_trial(c, a, tbl=TBL)
    exp = {"equivalent": t.equivalent, "reason": t.reason if t.equivalent else None, "rules": sorted(t.rules) if t.equivalent else None,
           "warnings": sorted(t.warnings) if t.equivalent else None, "ukus_pairs": [[p["uk"], p["us"]] for p in t.ukus_pairs]}
    out.append({"c": c, "a": a, "expected": exp})
os.makedirs("er109_output/ukus_wiring_01", exist_ok=True)
p = "er109_output/ukus_wiring_01/stored_regression_expected_01.jsonl.gz"
with gzip.open(p, "wt", encoding="utf-8", newline="\n") as f:
    for d in out: f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n")
print("rows", len(out), "pass", sum(d["expected"]["equivalent"] for d in out), "ukus", sum(1 for d in out if d["expected"]["ukus_pairs"]), os.path.getsize(p))
