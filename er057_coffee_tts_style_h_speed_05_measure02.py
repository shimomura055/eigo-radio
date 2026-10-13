# -*- coding: utf-8 -*-
"""LISTEN-COMPARE-01 委任_02: N01/N02 Take2/3 測定(API0)。measure5のmeasure/pitch_dynを同一条件で再利用。判定はround5 report5のjudge/clsと同一ロジック。"""
import os, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_coffee_tts_style_h_speed_04_measure5 as m5
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_05_listen", "gen02")
os.makedirs(os.path.join(OUT, "words"), exist_ok=True); m5.M.OUT = OUT
GL = {r["job"]: r for r in (json.loads(l) for l in open(os.path.join(OUT, "generation_log_02.jsonl"), encoding="utf-8")) if r.get("status") == "OK"}
TGT = {"std": (157, 6, 498), "adv": (167, 6, 593)}
res = {"method": "measure5同一(faster-whisper small local, -40dBFS, 50ms)。Stdは減速後実測", "takes": {}, "classification": {}}
for jid, r in sorted(GL.items()):
    m = m5.measure(r["final_wav"], r["level"], jid); m.update(m5.pitch_dyn(r["final_wav"]))
    m.update(cand=r["cand"], level=r["level"], primary_asr=r["classification"], asr_verified=r["verified"], duration_anomaly=r.get("duration_anomaly"), raw_sha256=r["raw_sha256"], final_sha256=r["final_sha256"], tts_input_sha256=r["tts_input_sha256"], model_version=r["model_version"])
    res["takes"][jid] = m
    c, tol, em = TGT[m["level"]]; e = m["end_pause_ms"]["mean"]
    sp = abs(m["wpm"] - c) <= tol; pa = e <= em and len(m["long800"]) <= 1
    ok = m["asr_verified"] and m["tail_last3_match"] and not any(a["conf"] in ("medium", "high") and a["symptom"] == "long_gap" for a in m["anomalies"])
    cl = "不合格(ASR/異音)" if not ok else "暫定合格" if sp and pa else "速度のみOK(ポーズ不良)" if sp else "ポーズのみOK(速度外)" if pa else "不合格"
    res["classification"][jid] = cl
    print(jid, m["wpm"], e, len(m["long800"]), m["primary_asr"], m["tail_last3_match"], m["anomaly_medium_plus"], cl, flush=True)
json.dump(res, open(os.path.join(OUT, "measurements_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
