# -*- coding: utf-8 -*-
import json, statistics, collections
R = json.load(open("er052_output/open233_kpi_recovery_02_offline_01/rca_major_rows_01.json", encoding="utf-8"))
def desc(xs):
    xs = sorted(xs)
    if not xs: return "n=0"
    q = lambda p: xs[min(len(xs)-1, int(p*len(xs)))]
    return f"n={len(xs)} min={xs[0]} p25={q(.25)} med={q(.5)} p75={q(.75)} max={xs[-1]}"
out = []
def block(title, rows):
    nb = [r for r in rows if r["llm_materiality"] != "BLOCKING"]
    b = [r for r in rows if r["llm_materiality"] == "BLOCKING"]
    out.append(f"### {title}")
    out.append(f"- LLM非BLOCKING(降格候補): {desc([r['reasoning'] for r in nb if r['reasoning'] is not None])}")
    out.append(f"- LLM BLOCKING: {desc([r['reasoning'] for r in b if r['reasoning'] is not None])}")
    # 低reasoning(<400)での降格率
    for lo, hi in [(0, 400), (400, 700), (700, 1200), (1200, 10**9)]:
        s = [r for r in rows if r["reasoning"] is not None and lo <= r["reasoning"] < hi]
        k = sum(1 for r in s if r["llm_materiality"] != "BLOCKING")
        out.append(f"  - reasoning[{lo},{hi}): n={len(s)} 非BLOCKING={k} 率={k/len(s):.3f}" if s else f"  - reasoning[{lo},{hi}): n=0")
all_rows = [r for r in R if r["reasoning"] is not None]
single = [r for r in all_rows if r["n_major_in_route"] == 1]
block("全MAJOR claim(batch単位reasoning、reasoning記録あり)", all_rows)
block("batch内MAJOR=1件のみ(claimごとのreasoningに近い)", single)
v7b = [r for r in single if r["rubric"] == "V7b"]
block("V7b・単独batch", v7b)
sc = [r for r in all_rows if r["sub_id"]]
block("Safety-critical claim", sc)
scs = [r for r in sc if r["n_major_in_route"] == 1]
block("Safety-critical・単独batch", scs)
# 降格claimのreasoning per claim
out.append("### 降格(最終非BLOCKING)のうちbasis=noneのreasoning")
d_none = [r for r in all_rows if r["materiality"] != "BLOCKING" and r["basis"] == "none"]
d_other = [r for r in all_rows if r["materiality"] != "BLOCKING" and r["basis"] != "none"]
out.append(f"- basis=none: {desc([r['reasoning'] for r in d_none])}")
out.append(f"- basis!=none: {desc([r['reasoning'] for r in d_other])}")
out.append("### Safety-critical誤降格各件のreasoning(batch単位)と同groupのBLOCKING回の中央値")
for r in R:
    if r["sub_id"] and r["materiality"] != "BLOCKING":
        peers = [x["reasoning"] for x in R if x["sub_id"] == r["sub_id"] and x["materiality"] == "BLOCKING" and x["reasoning"] is not None and x["n_major_in_route"] == r["n_major_in_route"]]
        out.append(f"- {r['dir'][-12:]} {r['sub_id']} rub={r['rubric']} reasoning={r['reasoning']} 同sub_id・同batchサイズのBLOCKING回: {desc(peers)}")
open("er052_output/open233_kpi_recovery_02_offline_01/rca_reasoning_01.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
