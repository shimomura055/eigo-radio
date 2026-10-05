"""現行Production英語Stage 1(Ledger逸脱check)の実費集計(¥0、既存raw_usage_logのみ)。推定で埋めない。
確定範囲: er003/er019出力のdeviation系stage(Grep指定)。参考(Production確定ではない): er012/er013の同種stage。"""
import glob, json, os, re, statistics
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = {"gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-6-luna": (0.10, 0.01, 0.50)}
JPY = 160.0
RX = re.compile(r"deviation|vfl|ledger", re.I)
def cost(r, model=None):
    p = P.get(model or r.get("model_id"))
    if not p: return None
    it, ct, ot = r.get("input_tokens") or 0, r.get("cached_input_tokens") or 0, r.get("output_tokens") or 0
    return (max(it - ct, 0) * p[0] + ct * p[1] + ot * p[2]) / 1e6 * JPY
def scan(prefixes):
    rows = []
    for pre in prefixes:
        for f in glob.glob(ROOT + f"/{pre}*_output/**/raw_usage_log.jsonl", recursive=True):
            for l in open(f, encoding="utf8", errors="ignore"):
                try: r = json.loads(l)
                except Exception: continue
                s = str(r.get("stage"))
                if "ja_" in s or not RX.search(s): continue
                rows.append({"file": os.path.relpath(f, ROOT), "stage": s, "model_id": r.get("model_id"), "in": r.get("input_tokens"), "cached": r.get("cached_input_tokens"), "out": r.get("output_tokens"), "reasoning": r.get("reasoning_tokens"), "jpy_own_model": cost(r), "jpy_if_gpt6luna": cost(r, "gpt-6-luna"), "ts": (r.get("timestamp") or "")[:10]})
    return rows
conf = scan(["er003", "er019"])
ref = scan(["er012", "er013"])
def summ(rows):
    out = {}
    for s in sorted({r["stage"] for r in rows}):
        v = [r["jpy_own_model"] for r in rows if r["stage"] == s and r["jpy_own_model"] is not None]
        w = [r["jpy_if_gpt6luna"] for r in rows if r["stage"] == s and r["jpy_if_gpt6luna"] is not None]
        out[s] = {"n": len(v), "mean_own_model": round(sum(v)/len(v), 3) if v else None, "median_own_model": round(statistics.median(v), 3) if v else None, "mean_if_gpt6luna": round(sum(w)/len(w), 3) if w else None}
    return out
res = {"usd_jpy": JPY, "confirmed_scope_er003_er019": {"n_rows": len(conf), "by_stage": summ(conf), "rows": conf},
       "reference_only_er012_er013": {"n_rows": len(ref), "by_stage": summ(ref)},
       "verdict": "特定不能(Production 1記事分のStage 1実費として確定できない)",
       "reasons": ["er003_output配下にraw_usage_logなし", "er019の該当stageはfamily_x_section_segmentation_trial/b3 regression(Trial/回帰)で、n=1〜2、Production全記事run(hormuz等)のlogには英語deviation stageなし(ja_*のみ)", "Production英語生成+deviation checkのusageは別出力(er012/er013等)にstage名が異なって分散し、Production現行pathと一対一に対応づけられない"]}
base = os.path.dirname(__file__)
json.dump(res, open(os.path.join(base, "agg_v4a_stage1_actual_cost_01.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
md = ["# 現行Production英語Stage 1 実費集計(委任_11、¥0)", "", "判定: **" + res["verdict"] + "**。推定で埋めない。", "", "## 確定範囲(er003/er019のdeviation/vfl/ledger系stage)", "", "| stage | n | 平均¥(own model) | 平均¥(gpt-6-luna単価換算) |", "|---|---|---|---|"]
for s, v in res["confirmed_scope_er003_er019"]["by_stage"].items(): md.append(f"| {s} | {v['n']} | {v['mean_own_model']} | {v['mean_if_gpt6luna']} |")
md += ["", "## 参考のみ(Production確定ではない: er012/er013)", "", "| stage | n | 平均¥(own model) | 平均¥(gpt-6-luna換算) |", "|---|---|---|---|"]
for s, v in res["reference_only_er012_er013"]["by_stage"].items(): md.append(f"| {s} | {v['n']} | {v['mean_own_model']} | {v['mean_if_gpt6luna']} |")
md += ["", "## 特定不能の理由"] + ["- " + x for x in res["reasons"]]
open(os.path.join(base, "agg_v4a_stage1_actual_cost_01.md"), "w", encoding="utf8").write("\n".join(md) + "\n")
import sys
sys.stdout.reconfigure(encoding="utf-8")
print(chr(10).join(md))
