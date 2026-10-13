# -*- coding: utf-8 -*-
"""H-speed Trial 測定(API呼出なし、費用0、faster-whisper small local)。8way測定を流用し3take化。"""
import os, sys, json, re, hashlib, statistics as st
import numpy as np
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_coffee_v5_pause_01_measure as M
import er057_audio_anomaly_detect_trial_01 as D
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_02")
os.makedirs(os.path.join(OUT, "words"), exist_ok=True); M.OUT = OUT
GL = [json.loads(l) for l in open(os.path.join(OUT, "generation_log_02.jsonl"), encoding="utf-8")]
GL = {r["job"]: r for r in GL if r.get("status") == "OK"}
NW = {"std": 117, "adv": 131}
V5 = {"std": "er057_output/coffee_final_v4/segments/std_part1_slow6.wav", "adv": "er057_output/coffee_final_v4/segments/adv_part1_raw.wav"}
CS = ["H0", "H1", "H2", "H3", "H4", "H5"]

def measure(p, lv, key):
    a = M.analyze(p); a["lv"] = lv
    x, sr = M.load(p); runs, dur = M.silent_runs(x, sr); w = M.words_of(p)
    end_p = [q["pause_ms"] for q in a["sentence_end_pauses"]]
    oth = a["other_internal_runs_ms"]
    long_sil = sum(b - c for c, b in runs if (b - c) > 0.5 and c > 0.005 and b < dur - 0.011)
    inner = [(c, b) for c, b in runs if c > 0.005 and b < dur - 0.011]
    longpos = []
    for c, b in inner:
        if (b - c) >= 0.8:
            prev = [q for q in w if q["e"] <= c + 0.15]; nxt = [q for q in w if q["s"] >= b - 0.15]
            longpos.append({"t": round(c, 2), "ms": round((b - c) * 1000), "prev": prev[-1]["w"] if prev else None, "next": nxt[0]["w"] if nxt else None})
    ref = M.REF[f"{lv}_part1"]["text"]; rt = [M.norm(t) for t in re.findall(r"\S+", ref) if M.norm(t)]
    at = [M.norm(q["w"]) for q in w if M.norm(q["w"])]
    tail_ok = rt[-3:] == at[-3:]
    rms = float(np.sqrt((x ** 2).mean())); peak = float(np.abs(x).max())
    anom, _ = D.analyze(x.astype("float64"), sr, key, True)
    anom_s = [{"symptom": e["symptom"], "conf": e["confidence"], "t": round(float(e["t"]), 2)} for e in anom]
    last = w[-1] if w else None
    return {"path": p, "sha12": a["sha12"], "dur_s": a["dur_s"], "words_ref": NW[lv], "wpm": round(NW[lv] / dur * 60, 1),
            "speech_wpm500": round(NW[lv] / (dur - long_sil) * 60, 1),
            "end_pause_ms": {"n": len(end_p), **{k: v for k, v in M.stats(end_p).items() if k in ("mean", "median", "max", "hist")}} if end_p else None,
            "mid": {"n": len(oth), "total_s": round(sum(oth) / 1000, 2), "n300": sum(1 for v in oth if v >= 300)},
            "long800": longpos, "tail_last3_match": tail_ok, "align_ratio": a["align_ratio"], "asr_words": len(w),
            "last_word": last["w"] if last else None, "last_word_dur_ms": round((last["e"] - last["s"]) * 1000) if last else None,
            "rms_dbfs": round(20 * np.log10(rms + 1e-12), 1), "peak_dbfs": round(20 * np.log10(peak + 1e-12), 1),
            "anomalies": anom_s, "anomaly_medium_plus": sum(1 for e in anom_s if str(e["conf"]).lower() in ("medium", "high"))}

def main():
    res = {"method": "faster-whisper small local, -40dBFS silence, min 50ms, sentence-end via difflib alignment (same as 8way/coffee_v5_pause_01); Std measured as heard (slow6 applied)",
           "takes": {}, "v5": {}}
    shas = {}
    for jid, r in sorted(GL.items()):
        p = r["final_wav"]; lv = r["level"]
        m = measure(p, lv, jid)
        m.update(cand=r["cand"], take=r["take"], primary_asr=r["classification"], asr_verified=r["verified"], duration_anomaly=r.get("duration_anomaly"),
                 raw_sha256=r["raw_sha256"], final_sha256=r["final_sha256"], tts_input_sha256=r["tts_input_sha256"], model_version=r["model_version"],
                 reused=bool(r.get("reused_from")))
        res["takes"][jid] = m; shas.setdefault(r["raw_sha256"], []).append(jid)
        print(jid, m["wpm"], m["end_pause_ms"] and m["end_pause_ms"]["mean"], m["mid"], flush=True)
    res["raw_sha_all_distinct"] = all(len(v) == 1 for v in shas.values())
    res["n_takes"] = len(res["takes"])
    for lv in ("std", "adv"):
        m = measure(V5[lv], lv, f"v5_{lv}"); m["sha12_expected"] = {"std": "6546b00f7805", "adv": "8b616edca69c"}[lv]; res["v5"][lv] = m
    T = res["takes"]
    # 最終語継続長の外れ判定(同Lv全take中央値の1.5倍超を参考フラグ)
    for lv in ("std", "adv"):
        med = st.median([t["last_word_dur_ms"] for t in T.values() if t["level"] == lv if "level" in t] or [0]) if False else None
    lvmed = {lv: st.median([t["last_word_dur_ms"] for k, t in T.items() if f"_{lv}_" in k and t["last_word_dur_ms"]]) for lv in ("std", "adv")}
    res["last_word_median_ms"] = lvmed
    for k, t in T.items():
        lv = "std" if "_std_" in k else "adv"
        t["last_word_long_flag"] = bool(t["last_word_dur_ms"] and t["last_word_dur_ms"] > 1.5 * lvmed[lv])
    agg = {}
    for c in CS:
        for lv in ("std", "adv"):
            ts = [T[f"{c}_{lv}_part1_t{n}"] for n in (1, 2, 3) if f"{c}_{lv}_part1_t{n}" in T]
            w = [t["wpm"] for t in ts]; fast = max(ts, key=lambda t: t["wpm"])
            agg[f"{c}_{lv}"] = {"wpm": w, "wpm_mean": round(sum(w) / len(w), 1), "wpm_min": min(w), "wpm_max": max(w), "wpm_range": round(max(w) - min(w), 1),
                "fastest_take": fast["take"], "fastest_wpm": fast["wpm"],
                "end_mean": [t["end_pause_ms"]["mean"] for t in ts], "end_mean_avg": round(sum(t["end_pause_ms"]["mean"] for t in ts) / len(ts), 1),
                "end_median_avg": round(sum(t["end_pause_ms"]["median"] for t in ts) / len(ts), 1), "end_max": max(t["end_pause_ms"]["max"] for t in ts),
                "mid_n": [t["mid"]["n"] for t in ts], "mid_total_s": [t["mid"]["total_s"] for t in ts], "mid_total_avg": round(sum(t["mid"]["total_s"] for t in ts) / len(ts), 2),
                "n300": [t["mid"]["n300"] for t in ts], "long800_n": [len(t["long800"]) for t in ts],
                "asr_ng": [t["take"] for t in ts if not t["asr_verified"]], "last_long": [t["take"] for t in ts if t["last_word_long_flag"]]}
    res["by_cand_level"] = agg
    # 基準比較
    base = {}
    for lv in ("std", "adv"):
        h0 = agg[f"H0_{lv}"]
        base[lv] = {"v5_wpm": res["v5"][lv]["wpm"], "h0_t1_wpm": T[f"H0_{lv}_part1_t1"]["wpm"], "h0_mean3": h0["wpm_mean"],
                    "h0_mean_t1t2": round((T[f"H0_{lv}_part1_t1"]["wpm"] + T[f"H0_{lv}_part1_t2"]["wpm"]) / 2, 1)}
    res["baselines"] = base
    pen = {}
    for c in CS:
        for lv in ("std", "adv"):
            a = agg[f"{c}_{lv}"]; b = base[lv]; f = []
            if c != "H0":
                if a["wpm_mean"] > b["h0_mean3"]: f.append("平均がH0 3take平均より速い")
                if a["fastest_wpm"] > b["h0_t1_wpm"]: f.append(f"最速take(T{a['fastest_take']} {a['fastest_wpm']})がH0 Take1({b['h0_t1_wpm']})超")
            if a["fastest_wpm"] > 195: f.append("最速takeがWPM195超")
            pen[f"{c}_{lv}"] = f
    res["speed_penalties"] = pen
    json.dump(res, open(os.path.join(OUT, "measurements_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
if __name__ == "__main__": main()
