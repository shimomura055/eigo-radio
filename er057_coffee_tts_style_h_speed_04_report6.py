# -*- coding: utf-8 -*-
"""Round6 listen 判定(API0)。Round5 report5と同一判定基準。"""
import os, json, statistics as st
ROOT = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round6_listen")
m = json.load(open(f"{O}/measurements_r6.json", encoding="utf-8")); T = m["takes"]
TGT = {"std": (157, 6, 498), "adv": (167, 6, 593)}
def judge(t):
    c, tol, em = TGT[t["level"]]; e = t["end_pause_ms"]["mean"]
    sp = abs(t["wpm"] - c) <= tol; pa = e <= em and len(t["long800"]) <= 1
    ok = t["asr_verified"] and t["tail_last3_match"] and not any(a["conf"] in ("medium", "high") and a["symptom"] == "long_gap" for a in t["anomalies"])
    cl = "不合格(ASR/異音)" if not ok else "暫定合格" if sp and pa else "速度のみOK(ポーズ不良)" if sp else "ポーズのみOK(速度外)" if pa else "不合格"
    return {"cls": cl, "speed_ok": sp, "pause_ok": pa, "quality_ok": ok, "wpm": t["wpm"], "raw_wpm": round(t["wpm"] / 0.94, 1) if t["level"] == "std" else t["wpm"],
            "end_mean": e, "long800_n": len(t["long800"]), "asr": t["primary_asr"]}
out = {k: judge(t) for k, t in T.items()}
agg = {}
for c, lv in (("K06", "std"), ("K01", "adv")):
    ks = [f"{c}_{lv}_part1_t{i}" for i in (1, 2, 3)]
    w = [T[k]["wpm"] for k in ks]; e = [T[k]["end_pause_ms"]["mean"] for k in ks]
    agg[f"{c}_{lv}"] = {"pass_count": sum(out[k]["cls"] == "暫定合格" for k in ks), "wpm": w, "wpm_range": [min(w), max(w)], "wpm_spread": round(max(w) - min(w), 1),
                        "end_mean": e, "end_range": [min(e), max(e)], "end_spread": max(e) - min(e), "classes": [out[k]["cls"] for k in ks]}
json.dump({"per_job": out, "agg": agg, "criteria": "Std 157+-6 / Adv 167+-6 / 文末平均 Std<=498 Adv<=593 / 800ms+<=1 / ASR verified+tail+long_gap異音なし (Round5同一)"}, open(f"{O}/classification_r6.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items(): print(k, v)
print(json.dumps(agg, ensure_ascii=False, indent=1))
