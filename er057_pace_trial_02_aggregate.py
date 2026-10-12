# -*- coding: utf-8 -*-
"""委任_01(PACE-02) 集計(無料)。wpm/*.json + 基準F5(wpm_results_01.json) -> summary_02.json / WPM_TABLE_02.md"""
import json, os, statistics as st
ROOT = "C:/Users/tensh/eigo-radio"; OUT = f"{ROOT}/er057_output/pace_trial_02"
f5 = json.load(open(f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/wpm_results_01.json", encoding="utf-8"))["adv"]
gl = [json.loads(l) for l in open(f"{OUT}/generation_log_02.jsonl", encoding="utf-8")]
asrj = {(r["cand"], r["part"]): r for r in gl if r.get("cand")}
anom = json.load(open(f"{OUT}/anomaly_02.json", encoding="utf-8"))
def row(parts, name, ps500=None):
    dur = sum(p["duration_s"] for p in parts); wc = sum(p.get("words_adopted", p.get("words_adopted")) for p in parts)
    sp = sum(p["pause_sens"]["500"]["speech_s"] for p in parts)
    wins = [w for p in parts for w in p["windows10s"]]
    sents = [s for p in parts for s in p["sentences"]]
    mid = [p for p in parts]
    r = {"cand": name, "part_wpm": [p["wpm_overall"] for p in parts], "dur": round(dur, 2), "words": wc, "total_wpm": round(wc / dur * 60, 1),
         "speech_wpm500": round(wc / sp * 60, 1), "speech_wpm300": round(wc / sum(p["pause_sens"]["300"]["speech_s"] for p in parts) * 60, 1),
         "max_win_wpm": max(w["wpm_all"] for w in wins), "win_std": round(st.pstdev([w["wpm_all"] for w in wins]), 1),
         "max_sent_wpm": max(s["wpm"] for s in sents), "mid_pauses500": sum(p["pause_sens"]["500"]["n_mid"] for p in parts),
         "mid_pause_total500": round(sum(p["pause_sens"]["500"]["total_mid_s"] for p in parts), 2),
         "mid_pauses300": sum(p["pause_sens"]["300"]["n_mid"] for p in parts), "mid_pause_total300": round(sum(p["pause_sens"]["300"]["total_mid_s"] for p in parts), 2),
         "part_spread": round(max(p["wpm_overall"] for p in parts) - min(p["wpm_overall"] for p in parts), 1)}
    return r
res = {}
for c in [f"PD{i}" for i in range(1, 9)]:
    P = json.load(open(f"{OUT}/wpm/{c}.json", encoding="utf-8")); parts = [P[k] for k in "123"]
    r = row(parts, c)
    r["asr_primary"] = [f"{asrj[(c, f'adv_part{n}')]['classification']}" for n in (1, 2, 3)]
    r["asr_ng"] = [n for n in (1, 2, 3) if not asrj[(c, f'adv_part{n}')]["verified"]]
    r["whisper_diff"] = {m: [(P[k]["asr"][m]["ratio"], len(P[k]["asr"][m]["diffs"])) for k in "123"] for m in ("medium", "small")}
    r["anomaly_n"] = {"all": sum(len(anom[f"{c}_adv_part{n}"]) for n in (1, 2, 3)),
                      "medium_plus": sum(1 for n in (1, 2, 3) for e in anom[f"{c}_adv_part{n}"] if e["confidence"] in ("medium", "high"))}
    w = []
    if max(r["part_wpm"]) > 200: w.append("Part>200")
    if r["max_win_wpm"] > 250: w.append("window>250")
    r["warnings"] = w
    t = r["total_wpm"]
    r["primary"] = "最優先(175-185)" if 175 <= t <= 185 else "試聴候補(185-190)" if 185 < t <= 190 else "目標未達(>190)" if t > 190 else "品質確認要(<175)"
    res[c] = r
fp = [{**f5[k], "words_adopted": f5[k]["words_adopted"]} for k in "123"]
for p in fp:
    p["pause_sens"] = {m: {**v, "mean_mid_s": 0} for m, v in p["pause_sens"].items()}
b = row(fp, "F5"); b["anomaly_n"] = {"all": sum(len(anom[f"F5_adv_part{n}"]) for n in (1, 2, 3)), "medium_plus": 0}; res["F5"] = b
json.dump(res, open(f"{OUT}/summary_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
L = ["| 候補 | P1 | P2 | P3 | 合計WPM | 発話WPM(500) | 発話WPM(300) | 文間ポーズ(500ms) 数/計s | 最速10s窓 | 窓std | 文最大 | Part差 | 判定 | 警告 |", "|" + "---|" * 14]
for c, r in sorted(res.items(), key=lambda kv: kv[1]["total_wpm"]):
    L.append(f"| {c} | {r['part_wpm'][0]} | {r['part_wpm'][1]} | {r['part_wpm'][2]} | **{r['total_wpm']}** | {r['speech_wpm500']} | {r['speech_wpm300']} | {r['mid_pauses500']}/{r['mid_pause_total500']} | {r['max_win_wpm']} | {r['win_std']} | {r['max_sent_wpm']} | {r['part_spread']} | {r.get('primary','基準')} | {','.join(r.get('warnings', [])) or '-'} |")
open(f"{OUT}/WPM_TABLE_02.md", "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
