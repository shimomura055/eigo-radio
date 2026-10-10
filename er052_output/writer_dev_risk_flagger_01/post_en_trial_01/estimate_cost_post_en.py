# -*- coding: utf-8 -*-
"""API非呼び出し。ANTENNA-TRIAL-01実測(A3 平均out 174tok/A4 平均320tok、max cell JPY3.03)を基礎に、英語入力のtoken見積で補正。"""
import json, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_en_common import *
man = load_manifest()
prices = L.load_prices(FLAGGER_MODEL)
OUT = {3: 174, 4: 320}      # ANTENNA-TRIAL-01実測 平均出力tokens(reasoning込み)
res = dict(model=FLAGGER_MODEL, usd_jpy=L.USD_JPY, prices_in_cached_out_per_Mtok=prices, units=[], levels={})
tot = {3: [0, 0], 4: [0, 0]}
for u in man["units"]:
    unit, facts, ss = build_unit(u, man)
    for lv in (3, 4):
        itok = L.estimate_tokens(A.antenna_system(lv)) + L.estimate_tokens(P.build_user(unit))
        c = L.cost_yen(prices, itok, OUT[lv]); hi = L.cost_yen(prices, int(itok * 1.25), OUT[lv] * 3)
        tot[lv][0] += c; tot[lv][1] += hi
        res["units"].append(dict(unit=u["unit"], level=lv, est_in_tok=itok, central_jpy=round(c, 3), high_jpy=round(hi, 3)))
res["levels"] = {str(k): dict(central=round(v[0], 2), high=round(v[1], 2)) for k, v in tot.items()}
res["total_central_jpy"] = round(sum(v[0] for v in tot.values()), 2)
res["total_high_jpy"] = round(sum(v[1] for v in tot.values()), 2)
res["n_calls"] = len(man["units"]) * 2
res["antenna_reference"] = "ANTENNA-TRIAL-01 実測: A3 9セル JPY17.27(1.919/call, max2.883), A4 9セル JPY19.81(2.201/call, max3.032)"
res["cap_total_jpy"] = round(res["total_central_jpy"] * 1.5, 2)
json.dump(res, open(os.path.join(HERE, "cost_estimate_post_en_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps({k: res[k] for k in ("n_calls", "levels", "total_central_jpy", "total_high_jpy", "cap_total_jpy", "usd_jpy")}, ensure_ascii=False))
