# Round2 表を analysis_r2.json から機械生成(手書き転記ミス防止)。¥0
import json, os, sys, re
sys.path.insert(0, os.getcwd())
import er064_kp_int_01_eval as EV
OUT = "er064_output/kp_integrated_opt_01/round2"
A = json.load(open(f"{OUT}/analysis_r2.json", encoding="utf-8"))
anch = json.load(open("er064_output/kp_integrated_opt_01/round1/anchors_r1.json", encoding="utf-8"))["anchors"]
order = ["M0P0", "M2P0", "M2P3", "M2P5"]
L = []
def e(lv, c): return A.get(f"coffee_{lv}_{c}")
def runs_n3(ent, k=3):
    """n=3に揃えた集計(run1-3のみ)。"""
    return [r for r in ent["runs"] if r["run"] <= k]
for lv in ("std", "adv"):
    L.append(f"### アンカー採用回数 Coffee {lv.upper()} (full一致、分母=有効run数。M2P5はn={A['coffee_%s_M2P5' % lv]['n']})")
    L.append("| アンカー | " + " | ".join(order) + " |")
    L.append("|---|" + "---|" * len(order))
    present = [a for a in anch if a["rank"] in EV.in_article(open({"std": "er019_output/coffee_prices/run_v5_ms_01/a2/article.md", "adv": "er019_output/coffee_prices/run_v5_ms_01/b1b/article.md"}[lv], encoding="utf-8").read())]
    for a in present:
        cells = []
        for c in order:
            x = e(lv, c)
            full = x["adopt_full"].get(str(a["rank"]), 0); frag = x["adopt_fragment"].get(str(a["rank"]), 0)
            r = {"full": "R", "fragment": "r", None: "x"}[x["reach"].get(str(a["rank"]))]
            cells.append(f"{full}/{x['n_valid']}" + (f"(+断片{frag})" if frag else "") + f" [{r}]")
        L.append(f"| {a['rank']} {a['label']} | " + " | ".join(cells) + " |")
    L.append("[R]=候補にfull到達 [r]=断片のみ到達 [x]=候補に無い"); L.append("")

def rows_for(c, cap=None):
    """cap=3ならrun1-3のみで再計算(M2P5のn=3比較用)。"""
    out = {}
    for lv in ("std", "adv"):
        x = e(lv, c)
        rs = [r for r in x["runs"] if "score" in r and r["score"] and (cap is None or r["run"] <= cap)]
        allr = [r for r in x["runs"] if (cap is None or r["run"] <= cap)]
        out[lv] = {"n": len(allr), "valid": len(rs), "score": sum(r["score"]["score"] for r in rs) / max(len(rs), 1),
                   "low": sum(r["score"]["low_slots"] for r in rs) / max(len(rs), 1),
                   "pump": sum(1 for r in rs if 1 in r["score"]["full_ranks"]), "timelag": sum(1 for r in rs if 4 in r["score"]["full_ranks"]),
                   "sel_pass": sum(1 for r in allr if r["sel_status"] == "KEY_WORDS_STRUCTURE_PASS"),
                   "canon_inv": sum(1 for r in allr if r.get("canon") == "CANONICALIZATION_INVALID"),
                   "red_ng": sum(1 for r in allr if r.get("redundancy") not in (None, "PASS", "REDUNDANCY_QA_PASS", "REDUNDANCY_PASS")),
                   "allpass": sum(1 for r in allr if r["sel_status"] == "KEY_WORDS_STRUCTURE_PASS" and r.get("canon") == "CANONICALIZATION_PASS" and r.get("redundancy") in ("PASS", "REDUNDANCY_QA_PASS", "REDUNDANCY_PASS")),
                   "creative_imp": sum((r.get("creative_important") or 0) for r in rs), "cost": sum(r["cost"] for r in allr)}
    return out
L.append("### M x P 要約(Coffee、Std+Adv合算 score上限84)")
L.append("| 条件 | n/レベル | score合計 | Std score(上限37) | Adv score(上限47) | pump採用 | time lag採用(Adv) | 低優先枠/run Std | Adv | 平均 | 創作比喩Imp | sel PASS | canon INVALID | Redundancy NG | 全gate PASS | 費用/job |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for lab, c, cap in [("M0P0(基準)", "M0P0", None), ("M2P0", "M2P0", None), ("M2P3", "M2P3", None), ("M2P5 n=3(run1-3)", "M2P5", 3), ("M2P5 n=5(全run)", "M2P5", None)]:
    r = rows_for(c, cap); s, a_ = r["std"], r["adv"]
    n = s["n"] + a_["n"]; nv = s["valid"] + a_["valid"]
    L.append(f"| {lab} | {s['n']} | {s['score'] + a_['score']:.1f} | {s['score']:.1f} | {a_['score']:.1f} | {s['pump'] + a_['pump']}/{nv} | {a_['timelag']}/{a_['valid']} | {s['low']:.2f} | {a_['low']:.2f} | {(s['low'] + a_['low']) / 2:.2f} | {s['creative_imp'] + a_['creative_imp']} | {s['sel_pass'] + a_['sel_pass']}/{n} | {s['canon_inv'] + a_['canon_inv']}/{n} | {s['red_ng'] + a_['red_ng']}/{n} | {s['allpass'] + a_['allpass']}/{n} | {(s['cost'] + a_['cost']) / n:.2f} |")
L.append("")
L.append("### 低優先枠(アンカー9-12)の個別採用: Std on a regular basis / right away / take time、Adv hold on / right away / take time(採用/有効run)")
for lv, ranks in (("std", (9, 11, 12)), ("adv", (9, 10, 11, 12))):
    for lab, c, cap in [("M0P0", "M0P0", None), ("M2P0", "M2P0", None), ("M2P3", "M2P3", None), ("M2P5(n=3)", "M2P5", 3), ("M2P5(n=5)", "M2P5", None)]:
        rs = [r for r in e(lv, c)["runs"] if r.get("score") and (cap is None or r["run"] <= cap)]
        L.append(f"- {lv} {lab}: " + ", ".join(f"rank{k}={sum(1 for r in rs if k in r['score']['full_ranks'])}/{len(rs)}" for k in ranks) + f" (低優先枠/run {sum(r['score']['low_slots'] for r in rs) / max(len(rs), 1):.2f})")
L.append("")
L.append("### 他記事回帰(meta/hormuz、n=2。M0P0=前回Phase2 C0 n=3再利用)")
L.append("| 記事 | Lv | 条件 | n | sel PASS | canon INVALID | Redundancy NG | 全gate PASS | 最終5件(run別、display<candidate>) |")
L.append("|---|---|---|---|---|---|---|---|---|")
for art in ("meta", "hormuz"):
    for lv in ("std", "adv"):
        for c in ("M0P0", "M2P0", "M2P3", "M2P5"):
            x = A.get(f"{art}_{lv}_{c}")
            if not x: continue
            rs = x["runs"]
            its = " || ".join("; ".join(f"{i[1][0].upper()}:{i[2]}" for i in r["items"]) if "items" in r else "INVALID" for r in rs)
            L.append(f"| {art} | {lv} | {c} | {x['n']} | {x['sel_pass']}/{x['n']} | {sum(1 for r in rs if r.get('canon') == 'CANONICALIZATION_INVALID')} | {sum(1 for r in rs if 'items' in r and r.get('redundancy') not in (None, 'PASS', 'REDUNDANCY_QA_PASS', 'REDUNDANCY_PASS'))} | {x['all_gate_pass']}/{x['n']} | {its} |")
open(f"{OUT}/report_tables_r2.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
