# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01 指標計測(API 0、read-only)。
生成wav(audio/<p>/kpNN.wav)と既存Production完成音声5本(参照、read-only)を同一手法で計測する。

手法(RMS閾値ベース。既存Productionに文中ポーズ専用の計測関数が無いため新設。閾値は全clip共通で固定):
  - フレーム: 窓20ms / hop10ms のRMS(モノラル化後)。
  - 発話フレーム: RMS_dB > (clip内p95 RMS_dB) - 35dB。
  - 無音run: 発話フレームでない連続区間。80ms以上を「ポーズ」として数える。
  - 先頭無音 = 最初の発話フレームより前、文末無音 = 最後の発話フレームより後(Production trim余白0.30s由来を含む)。
  - 文中ポーズ = 最初と最後の発話フレームの間にある無音run(80ms以上)。文末無音とは分離して集計。
  - 発話区間(speech_span) = 最初〜最後の発話フレーム。WPM = 語数 / speech_span x 60(語数は原稿をsplitした数)。
    補助として全長ベースWPM(語数 / total x 60)も記録。
"""
import argparse, json, os, sys
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
WIN, HOP = 0.020, 0.010
REL_DB = -35.0
PAUSE_MIN_S = 0.080
LONG_PAUSE_S = 0.200


def measure(path, text):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    n, w, h = len(x), int(WIN * sr), int(HOP * sr)
    rms = np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) for i in range(0, max(n - w, 1), h)]) + 1e-9
    db = 20 * np.log10(rms)
    thr = np.percentile(db, 95) + REL_DB
    act = db > thr
    total = n / sr
    idx = np.where(act)[0]
    if len(idx) == 0:
        return {"total_s": round(total, 3), "error": "no_speech_frames"}
    f0, f1 = int(idx[0]), int(idx[-1])
    lead = f0 * HOP
    tail = max(total - (f1 * HOP + WIN), 0.0)
    span = (f1 - f0) * HOP + WIN
    # 文中の無音run
    runs, cur = [], 0
    for a in act[f0:f1 + 1]:
        if not a:
            cur += 1
        else:
            if cur:
                runs.append(cur * HOP)
            cur = 0
    pauses = [r for r in runs if r >= PAUSE_MIN_S]
    words = len(text.split())
    return {"total_s": round(total, 3), "speech_span_s": round(span, 3), "speech_active_s": round(float(act.sum()) * HOP, 3),
            "words": words, "wpm_span": round(words / span * 60, 1), "wpm_total": round(words / total * 60, 1),
            "lead_silence_s": round(lead, 3), "tail_silence_s": round(tail, 3),
            "inner_pause_count": len(pauses), "inner_pause_total_s": round(float(sum(pauses)), 3),
            "inner_pause_max_s": round(float(max(pauses)), 3) if pauses else 0.0,
            "inner_pause_ge200ms_count": int(sum(1 for r in pauses if r >= LONG_PAUSE_S)),
            "inner_pause_list_s": [round(float(r), 3) for r in pauses], "threshold_db": round(float(thr), 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    inp = a.inp.replace("\\", "/").rstrip("/")
    plan = json.load(open(f"{inp}/audit/plan.json", encoding="utf-8"))
    texts = {r["kp"]: r for r in plan["texts"]}
    res = {"method": {"window_s": WIN, "hop_s": HOP, "speech_threshold": f"clip内RMS dB p95 {REL_DB:+.0f}dB", "pause_min_s": PAUSE_MIN_S,
                      "long_pause_s": LONG_PAUSE_S, "wpm_basis": "語数/発話区間(first-last speech frame)x60。wpm_totalは全長基準(補助)"},
           "clips": {}, "reference_production": {}}
    for p in plan["prompts"]:
        for kp, r in texts.items():
            f = f"{inp}/audio/{p}/kp{kp:02d}.wav"
            if os.path.isfile(f):
                res["clips"][f"{p}/kp{kp}"] = measure(f, r["text"])
    for kp, r in texts.items():
        res["reference_production"][f"kp{kp}"] = measure(r["prod_wav"], r["text"])
    # prompt別平均
    agg = {}
    keys = ["total_s", "speech_span_s", "wpm_span", "wpm_total", "lead_silence_s", "tail_silence_s", "inner_pause_count",
            "inner_pause_total_s", "inner_pause_max_s", "inner_pause_ge200ms_count"]
    for p in plan["prompts"]:
        cl = [v for k, v in res["clips"].items() if k.startswith(p + "/") and "error" not in v]
        if cl:
            agg[p] = {"n": len(cl), **{k: round(float(np.mean([c[k] for c in cl])), 3) for k in keys}}
    rf = [v for v in res["reference_production"].values() if "error" not in v]
    if rf:
        agg["prod_existing"] = {"n": len(rf), **{k: round(float(np.mean([c[k] for c in rf])), 3) for k in keys}}
    res["per_prompt_mean"] = agg
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for p, v in agg.items():
        print(p, v)


if __name__ == "__main__":
    main()
