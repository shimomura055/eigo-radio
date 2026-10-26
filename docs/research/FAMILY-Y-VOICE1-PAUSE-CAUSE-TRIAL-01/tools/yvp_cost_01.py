# -*- coding: utf-8 -*-
"""本Trialの実費集計(read-only、API 0)。docs/pm/tools/daily_dev_cost_01.py の price_record/load_prices を再利用し、
er121_output/family_y_voice_pause_trial_01/*/cost_log_*.jsonl だけを換算する(並行agent分を含めない)。"""
import glob, json, os, sys
from collections import defaultdict

sys.path.insert(0, "docs/pm/tools")
import daily_dev_cost_01 as d

prices = d.load_prices(".")
tot = 0.0
unpriced = []
by = defaultdict(lambda: [0, 0.0])
for f in sorted(glob.glob("er121_output/family_y_voice_pause_trial_01/*/cost_log_*.jsonl")):
    for line in open(f, encoding="utf-8"):
        rec = json.loads(line)
        r = d.price_record(rec, prices)
        usd = r[0]
        jpy = None if usd is None else usd * d.USD_JPY
        if jpy is None:
            unpriced.append((os.path.basename(f), rec.get("api")))
            continue
        tot += jpy
        k = (os.path.basename(f), rec.get("provider"))
        by[k][0] += 1
        by[k][1] += jpy
print(json.dumps({"total_jpy": round(tot, 2), "unpriced": unpriced[:5], "n_unpriced": len(unpriced),
                  "by": {f"{a}|{b}": [n, round(j, 2)] for (a, b), (n, j) in by.items()}}, ensure_ascii=False, indent=1))
