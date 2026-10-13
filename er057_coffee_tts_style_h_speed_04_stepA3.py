# -*- coding: utf-8 -*-
import os, json, collections
ROOT = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round4")
R = json.load(open(f"{O}/silence_rows_r4.json", encoding="utf-8")); rows = R["rows"]; PS = json.load(open(f"{O}/silence_posstats_r4.json"))
n_wav = R["n_wav"]
def cand(j): return j.split("_")[0]
out = {"method": "Round1-3(+H0 T1)の全OK wav(final_wav=Stdはslow6後、Advはraw)を測定条件同一(-40dBFS/50ms/faster-whisper small)で再集計。文末位置は原稿文末→ASR整列、位置名Snnは原稿の第nn文の直後", "n_wav": n_wav, "positions": {}, "top": {}, "counterfactual": PS["counterfactual"], "std_raw_end_target_ms": round(498 / 1.06, 1)}
md = ["# silence_positions_r4 (TRIAL-04 Step A)", "", f"対象: Round1-3 全OK wav (Std {n_wav['std']}本 / Adv {n_wav['adv']}本、H0 T1含む、候補はJ01-13/K01-08/L01-06+Take2)。測定=-40dBFS・50ms・faster-whisper small(local)。Stdは6%減速後(聴取状態)。", ""]
for lv in ("std", "adv"):
    rs = [r for r in rows if r["level"] == lv]
    g = collections.defaultdict(lambda: {"ge800": 0, "r500_800": 0, "cands800": set(), "pair": ""})
    for r in rs:
        k = r["pos"] if r["pos"] != "mid" else "mid:" + r["pair"]
        g[k][r["cat"]] += 1; g[k]["pair"] = r["pair"]
        if r["cat"] == "ge800": g[k]["cands800"].add(cand(r["src"]))
    t8 = sum(v["ge800"] for v in g.values()); t5 = sum(v["r500_800"] for v in g.values())
    order = sorted(g.items(), key=lambda kv: -(kv[1]["ge800"] * 1000 + kv[1]["r500_800"]))
    md += [f"## {lv.upper()} (≥800ms 計{t8}本 / 500-800ms 計{t5}本 / wav {n_wav[lv]}本)", "", "| 位置 | 直前語 -> 直後語 | ≥800ms本数 (占有率) | 500-800ms本数 (占有率) | 位置の平均文末無音ms (全wav) | ≥800が出たPrompt数 |", "|---|---|---|---|---|---|"]
    out["positions"][lv] = {}
    for k, v in order:
        pn = int(k[1:]) if k.startswith("S") else None
        ms = PS["pos_stats"][lv][str(pn)]["mean"] if pn else "-"
        md.append(f"| {k} | {v['pair']} | {v['ge800']} ({v['ge800']*100//max(1,t8)}%) | {v['r500_800']} ({v['r500_800']*100//max(1,t5)}%) | {ms} | {len(v['cands800'])} |")
        out["positions"][lv][k] = {"pair": v["pair"], "ge800": v["ge800"], "r500_800": v["r500_800"], "mean_end_pause_ms": ms, "prompts_with_ge800": sorted(v["cands800"])}
    top2 = sum(v["ge800"] for _, v in order[:2]); top3 = sum(v["ge800"] for _, v in order[:3])
    out["top"][lv] = {"total_ge800": t8, "top2_ge800": top2, "top2_pct": round(top2 * 100 / max(1, t8)), "top3_pct": round(top3 * 100 / max(1, t8)), "top2_positions": [k for k, _ in order[:2]]}
    md += ["", f"上位2位置({', '.join(k for k,_ in order[:2])})で≥800msの {top2}/{t8} = {round(top2*100/max(1,t8))}%、上位3位置で {round(top3*100/max(1,t8))}%。", ""]
cf = PS["counterfactual"]
md += ["## 判定", "",
 f"- **仮説『長無音は原稿内の2箇所の話題転換点の文末に集中』は支持される**: Std ≥800msの{out['top']['std']['top2_pct']}%が第5文末(delay.→The International)と第9文末(continue.→The US)、Advは第7文末(continue.→The US)+第4文末で{out['top']['adv']['top2_pct']}%。両位置は平均文末無音もStd 713/721ms(他位置の平均は約380-590ms)と全wav平均で突出して長い。",
 "- **ただし『段落境界』ではない**: tts_input(Std/Adv)に改行・段落区切りは存在しない(1本の連続テキスト。確認済み)。長いのは『文末』のうち**話題が切り替わる文末**であり、literalな段落指示は入力に対応物がない。Step Bは『paragraph』の語を使わず、『話が次の要点へ移るときも同じ流れで入る』趣旨(位置・語は直接指定しない)へ設計を変える。",
 f"- 反実仮想(この2位置の無音を同wav内の他位置の中央値で頭打ちにした場合): Std 文末平均 {cf['std']['mean_of_means']}ms -> {cf['std']['mean_if_capped']}ms、498ms以内のwav割合 {int(cf['std']['frac_le_target_now']*100)}% -> {int(cf['std']['frac_le_target_capped']*100)}%。Adv {cf['adv']['mean_of_means']} -> {cf['adv']['mean_if_capped']}ms(593ms以内 {int(cf['adv']['frac_le_target_now']*100)}% -> {int(cf['adv']['frac_le_target_capped']*100)}%)。つまりStdは2位置の長無音を抑えるだけで文末平均基準をほぼ満たす構造。Advは元々ほぼ満たしている(2位置の影響は小)。",
 f"- **Std減速後の文末平均を498ms以内に収めるためのraw時点の上限**: 498/1.06 = **{out['std_raw_end_target_ms']}ms**(6%減速で無音も1.06倍になるため)。全wav平均のStd文末平均(減速後)は{cf['std']['mean_of_means']}ms = raw換算約{round(cf['std']['mean_of_means']/1.06)}ms(上限470msに対し約{round(cf['std']['mean_of_means']/1.06)-470}ms超過)。",
 "- 500-800msの無音は、第3-5・7-9文末など文末全般に広く出る(特定位置のみではない)。長無音(≥800ms)のみが2位置に偏る。"]
open(f"{O}/silence_positions_r4.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
json.dump(out, open(f"{O}/silence_positions_r4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(md))
