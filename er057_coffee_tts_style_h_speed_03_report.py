# -*- coding: utf-8 -*-
import os, json
ROOT = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03", "round1")
m = json.load(open(f"{O}/measurements_r1.json", encoding="utf-8")); T = m["takes"]; P = json.load(open(f"{O}/prompts_r1.json", encoding="utf-8"))["candidates"]
TGT = {"std": (157, 6, 498), "adv": (167, 6, 593)}
def judge(t):
    lv = t["level"]; c, tol, em = TGT[lv]; e = t["end_pause_ms"]["mean"]
    sp = abs(t["wpm"] - c) <= tol; pa = e <= em and len(t["long800"]) <= 1
    ok = t["asr_verified"] and t["tail_last3_match"] and not any(a["conf"] in ("medium", "high") and a["symptom"] == "long_gap" for a in t["anomalies"])
    return sp, pa, ok
def cls(t):
    sp, pa, ok = judge(t)
    if not ok: return "不合格(ASR/異音)"
    if sp and pa: return "暫定合格"
    if sp: return "速度のみOK(ポーズ不良)"
    if pa: return "ポーズのみOK(速度外)"
    return "不合格"
rows = []; out = {}
for k, t in sorted(T.items()):
    e = t["end_pause_ms"]; sp, pa, ok = judge(t); c = cls(t); out[k] = c
    med = sum(1 for a in t["anomalies"] if a["conf"] in ("medium", "high"))
    rows.append(f"| {t['cand']} | {t['level']} | {t['wpm']} ({t['wpm']-TGT[t['level']][0]:+.1f}) | {t['speech_wpm500']} | {e['mean']}/{e['median']}/{e['max']} | {t['mid']['n']}/{t['mid']['total_s']}/{t['mid']['n300']} | {len(t['long800'])} | {t['primary_asr'][:22]} | {'OK' if t['tail_last3_match'] else 'NG'} | {med} | {t['pitch_p10_p90_semitones']}/{t['dyn_p10_p90_db']} | {c} |")
hdr = "| 候補 | Lv | WPM(目標差) | 発話WPM | 文末無音 平均/中央/最大ms | 文中無音 本/計s/300ms+ | 800ms+ | Primary ASR | 末尾 | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
base = []
for nm, d in (("H0 Take1(TRIAL-02再利用)", m["H0_t1"]), ("現行v5", m["v5"])):
    for lv in ("std", "adv"):
        t = d[lv]; e = t["end_pause_ms"]
        base.append(f"| {nm} | {lv} | {t['wpm']} | {t['speech_wpm500']} | {e['mean']}/{e['median']}/{e['max']} | {t['mid']['n']}/{t['mid']['total_s']}/{t['mid']['n300']} | {len(t['long800'])} | {t.get('primary_asr','-')} | - | {t['anomaly_medium_plus']} | {t['pitch_p10_p90_semitones']}/{t['dyn_p10_p90_db']} | 基準 |")
prm = "\n".join(f"| {c} | {v['words']} | {v['sha256'][:8]} | " + " / ".join(f"{a}={b}" for a, b in v["axes"].items()) + f" |\n\n> {v['style']}\n\n設計意図: {v['design_intent']} / 想定副作用: {v['expected_side_effects']}\n" if False else f"- **{c}** ({v['words']}語, sha {v['sha256'][:8]}): `{v['style']}`\n  - 軸: " + " / ".join(f"{a}={b}" for a, b in v["axes"].items()) + f"\n  - 意図: {v['design_intent']}\n  - 想定副作用: {v['expected_side_effects']}" for c, v in P.items())
json.dump(out, open(f"{O}/classification_r1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(f"{O}/_tables.md", "w", encoding="utf-8").write("## PROMPTS\n" + prm + "\n\n## MEASURE\n" + hdr + "\n".join(base) + "\n" + "\n".join(rows) + "\n")
for k, c in out.items(): print(k, c)
