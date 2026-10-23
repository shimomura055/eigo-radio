import json, sys, os, collections
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\tensh\eigo-radio"); os.chdir(ROOT); sys.path.insert(0, str(ROOT))
D = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
import er112_kp_gm_judge_01 as jd
c = jd.load_cache("sonnet")
R = [json.loads(l) for l in (D / "kp_probe_03_results.jsonl").read_text(encoding="utf-8").splitlines()]
agg = collections.defaultdict(lambda: collections.Counter()); per = collections.defaultdict(dict)
for r in R:
    if r["kind"] != "E": continue
    v = c[jd.rid("E2", r["key"], r["sent"], r["text"])]["verdict"]
    a = agg[r["arm"]]; a["n"] += 1
    a["sense_ok"] += v["sense_ok"]; a["core"] += v["core"]; a["single"] += v["single"]
    a["pass"] += int(v["sense_ok"] and v["core"] and v["single"])
    per[r["key"]][(r["arm"], r["rep"])] = (v["sense_ok"], v["core"], v["single"], v.get("note", ""))
for arm in sorted(agg):
    a = agg[arm]; print(arm, dict(a), "pass=%.0f%% sense=%.0f%% core=%.0f%%" % (100*a["pass"]/a["n"], 100*a["sense_ok"]/a["n"], 100*a["core"]/a["n"]))
print()
for k, d in per.items():
    print(k, {a: "".join(str(x) for x in d[(a, 1)][:3]) + "/" + "".join(str(x) for x in d[(a, 2)][:3]) for a in ("E0", "E1", "E2", "E3", "E4")})
