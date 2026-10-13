# -*- coding: utf-8 -*-
"""Round2 判定・表生成(API呼出なし)。Std減速後実測 / raw換算(Std/0.94) / Adv実測 の3列併記。"""
import os, json
ROOT = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round5")
m = json.load(open(f"{O}/measurements_r5.json", encoding="utf-8")); T = dict(m["takes"]); P = json.load(open(f"{O}/prompts_r5.json", encoding="utf-8"))["candidates"]
m4 = json.load(open(f"{O}/../round4/measurements_r4.json", encoding="utf-8"))
for k in ("M05_std_part1_t1", "M05_adv_part1_t1"): T[k] = m4["takes"][k]
TGT = {"std": (157, 6, 498), "adv": (167, 6, 510)}   # 文末平均上限: 委任文指定=Round1値踏襲(Std 498 / Adv 510相当)
TGT_ADV_END_R1 = 593
RAW_T = 167; RAW_TOL = 6
def raw_of(t): return round(t["wpm"] / 0.94, 1) if t["level"] == "std" else t["wpm"]
def judge(t):
    lv = t["level"]; c, tol, em = TGT[lv]; e = t["end_pause_ms"]["mean"]
    sp = abs(t["wpm"] - c) <= tol
    # 委任文: 文末平均<=H0 T1(Std 498ms/Adv 510ms相当、Round1の値を踏襲)。Round1の分類基準はAdv 593(H0 T1実測)。両方を記録し、主判定は593(Round1同一)、510は参考列。
    pa = e <= (498 if lv == "std" else TGT_ADV_END_R1) and len(t["long800"]) <= 1
    pa_strict = e <= em and len(t["long800"]) <= 1
    ok = t["asr_verified"] and t["tail_last3_match"] and not any(a["conf"] in ("medium", "high") and a["symptom"] == "long_gap" for a in t["anomalies"])
    return sp, pa, ok, pa_strict
def cls(t):
    sp, pa, ok, _ = judge(t)
    if not ok: return "不合格(ASR/異音)"
    if sp and pa: return "暫定合格"
    if sp: return "速度のみOK(ポーズ不良)"
    if pa: return "ポーズのみOK(速度外)"
    return "不合格"
rows = []; out = {}
for k, t in sorted(T.items()):
    e = t["end_pause_ms"]; sp, pa, ok, pas = judge(t); c = cls(t); out[k] = {"cls": c, "speed_ok": sp, "pause_ok": pa, "pause_ok_adv510": pas, "quality_ok": ok, "raw_wpm": raw_of(t), "raw_ok": abs(raw_of(t) - RAW_T) <= RAW_TOL}
    med = sum(1 for a in t["anomalies"] if a["conf"] in ("medium", "high"))
    rows.append(f"| {t['cand']} | {k.rsplit('_t', 1)[1]} | {t['level']} | {t['wpm']} ({t['wpm']-TGT[t['level']][0]:+.1f}) | {raw_of(t)} ({raw_of(t)-RAW_T:+.1f}) | {t['speech_wpm500']} | {e['mean']}/{e['median']}/{e['max']} | {t['mid']['n']}/{t['mid']['total_s']}/{t['mid']['n300']} | {len(t['long800'])} | {t['primary_asr'][:22]} | {'OK' if t['tail_last3_match'] else 'NG'} | {med} | {t['pitch_p10_p90_semitones']}/{t['dyn_p10_p90_db']} | {c} |")
hdr = "| 候補 | take | Lv | WPM実測(目標差) | raw換算(167差) | 発話WPM | 文末無音 平均/中央/最大ms | 文中無音 本/計s/300ms+ | 800ms+ | Primary ASR | 末尾 | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
base = []
for nm, d in (("H0 Take1(TRIAL-02再利用)", m["H0_t1"]), ("現行v5", m["v5"])):
    for lv in ("std", "adv"):
        t = d[lv]; e = t["end_pause_ms"]; r = round(t["wpm"] / 0.94, 1) if lv == "std" else t["wpm"]
        base.append(f"| {nm} | - | {lv} | {t['wpm']} | {r} | {t['speech_wpm500']} | {e['mean']}/{e['median']}/{e['max']} | {t['mid']['n']}/{t['mid']['total_s']}/{t['mid']['n300']} | {len(t['long800'])} | {t.get('primary_asr','-')} | - | {t['anomaly_medium_plus']} | {t['pitch_p10_p90_semitones']}/{t['dyn_p10_p90_db']} | 基準 |")
# 候補別 両レベル判定
cands = sorted({t["cand"] for t in T.values()}); pj = {}
for c in cands:
    takes = sorted({k.rsplit("_t", 1)[1] for k, t in T.items() if t["cand"] == c})
    per = {}
    for tk in takes:
        s = out.get(f"{c}_std_part1_t{tk}"); a = out.get(f"{c}_adv_part1_t{tk}")
        if not s or not a: continue
        per[tk] = {"std": s["cls"], "adv": a["cls"], "both_pass": s["cls"] == "暫定合格" and a["cls"] == "暫定合格",
                   "std_wpm": T[f"{c}_std_part1_t{tk}"]["wpm"], "std_raw": s["raw_wpm"], "adv_wpm": T[f"{c}_adv_part1_t{tk}"]["wpm"],
                   "raw_gap_mean": round((abs(s["raw_wpm"] - RAW_T) + abs(a["raw_wpm"] - RAW_T)) / 2, 1), "raw_gap_std_vs_adv": round(s["raw_wpm"] - a["raw_wpm"], 1)}
    pj[c] = per
json.dump({"per_job": out, "per_candidate": pj, "note": "文末平均基準は主判定=Round1同一(Std<=498/Adv<=593=H0 T1実測)。pause_ok_adv510は委任文のAdv 510ms相当を厳格に当てた参考判定。"}, open(f"{O}/classification_r5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
prm = "\n".join(f"- **{c}** ({v['words']}語, sha {v['sha256'][:8]}, maxJaccard(J)={v['max_jaccard_vs_prior']['cand']}:{v['max_jaccard_vs_prior']['jaccard']}, H0={v['jaccard_vs_H0']}): `{v['style']}`\n  - 軸: " + " / ".join(f"{a}={b}" for a, b in v["axes"].items()) + f"\n  - 意図: {v['design_intent']}\n  - 根拠(Round1知見): {v['prior_basis']}\n  - 想定副作用: {v['expected_side_effects']}" for c, v in P.items())
open(f"{O}/_tables_r5.md", "w", encoding="utf-8").write("## PROMPTS\n" + prm + "\n\n## MEASURE\n" + hdr + "\n".join(base) + "\n" + "\n".join(rows) + "\n\n## PER_CAND\n" + json.dumps(pj, ensure_ascii=False, indent=1) + "\n")
for k, c in out.items(): print(k, c["cls"], "raw", c["raw_wpm"], "speed", c["speed_ok"], "pause", c["pause_ok"], "p510", c["pause_ok_adv510"], "q", c["quality_ok"])
for c, p in pj.items(): print(c, p)
