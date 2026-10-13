# Round1 レポート用の表を analysis_r1.json から機械生成(手書き転記ミス防止)。¥0
import json, os, sys
sys.path.insert(0, os.getcwd())
import er064_kp_int_01_eval as EV
OUT = "er064_output/kp_integrated_opt_01/round1"
A = json.load(open(f"{OUT}/analysis_r1.json", encoding="utf-8"))
anch = json.load(open(f"{OUT}/anchors_r1.json", encoding="utf-8"))["anchors"]
order = ["M0P0", "M1P0", "M2P0", "M0P1", "M0P2", "M0P3", "M0P4", "M2P1", "M2P2", "M2P3", "M2P4", "M3P4"]
L = []
for lv in ("std", "adv"):
    L.append(f"### アンカー採用回数 Coffee {lv.upper()} (full一致、n=3、分母=有効run数)")
    L.append("| アンカー | " + " | ".join(order) + " |")
    L.append("|---|" + "---|" * len(order))
    present = [a for a in anch if a["rank"] in EV.in_article(open({"std": "er019_output/coffee_prices/run_v5_ms_01/a2/article.md", "adv": "er019_output/coffee_prices/run_v5_ms_01/b1b/article.md"}[lv], encoding="utf-8").read())]
    for a in present:
        cells = []
        for c in order:
            e = A.get(f"coffee_{lv}_{c}")
            if not e:
                cells.append("-"); continue
            full = e["adopt_full"].get(str(a["rank"]), 0)
            frag = e["adopt_fragment"].get(str(a["rank"]), 0)
            reach = e["reach"].get(str(a["rank"]))
            r = {"full": "R", "fragment": "r", None: "x"}[reach]
            cells.append(f"{full}/{e['n_valid']}" + (f"(+断片{frag})" if frag else "") + f" [{r}]")
        L.append(f"| {a['rank']} {a['label']} | " + " | ".join(cells) + " |")
    L.append("[R]=候補にfull到達 [r]=断片のみ到達 [x]=候補に無い")
    L.append("")
L.append("### M x P 要約 (Std+Adv合算)")
L.append("| combo | 分類 | score合計(Std+Adv、上限84) | pump採用 | time lag採用(Adv) | 低優先枠/run | sel PASS | 全gate PASS(canon PASS+Red PASS) | Jaccard | 費用/job | reasoning tok(選定)/job |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
cls = {"M0P0": "基準", "M1P0": "機械のみ(guarded)", "M2P0": "機械のみ(+供給)", "M0P1": "Promptのみ", "M0P2": "Promptのみ", "M0P3": "Promptのみ", "M0P4": "Promptのみ", "M2P1": "統合", "M2P2": "統合", "M2P3": "統合", "M2P4": "統合", "M3P4": "統合(+注釈)"}
for c in order:
    es = [A[f"coffee_{lv}_{c}"] for lv in ("std", "adv")]
    sc = sum(e["score_mean"] for e in es)
    pump = sum(e["adopt_full"].get("1", 0) for e in es)
    nv = sum(e["n_valid"] for e in es)
    tl = A[f"coffee_adv_{c}"]["adopt_full"].get("4", 0)
    low = sum(e["low_slots_per_run"] for e in es) / 2
    sp = sum(e["sel_pass"] for e in es)
    n = sum(e["n"] for e in es)
    ap = sum(e["all_gate_pass"] for e in es)
    jac = sum((e["jaccard_mean"] or 0) for e in es) / 2
    cost = sum(e["cost_mean"] for e in es) / 2
    rt = sum((e["reasoning_tokens_sel_mean"] or 0) for e in es) / 2
    L.append(f"| {c} | {cls[c]} | {sc:.1f} | {pump}/{nv} | {tl}/{A[f'coffee_adv_{c}']['n_valid']} | {low:.2f} | {sp}/{n} | {ap}/{n} | {jac:.2f} | {cost:.2f} | {rt:.0f} |")
open(f"{OUT}/report_tables_r1.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
