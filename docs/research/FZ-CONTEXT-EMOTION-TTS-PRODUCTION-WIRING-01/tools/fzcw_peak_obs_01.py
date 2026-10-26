# -*- coding: utf-8 -*-
"""E-1 ctx音声のpeak分布観測(read-only。新基準ではない)。check_clip_audio_quality の peak_max=0.999 超過の有無を数える。"""
import json, os, sys, statistics
import numpy as np
import soundfile as sf

RUN = sys.argv[1]
OUT = sys.argv[2]
res = {"run_dir": RUN, "levels": {}}
for lv in ("a2", "b1b"):
    nd = f"{RUN}/{lv}/narration"
    st = json.load(open(f"{RUN}/{lv}/audit/dialogue_ctx_attempt_state.json", encoding="utf-8"))["clips"]
    tl = json.load(open(f"{RUN}/{lv}/assembly/timeline.json", encoding="utf-8"))
    ctx, other = {}, {}
    for fn in sorted(os.listdir(nd)):
        if not fn.endswith(".wav") or fn.endswith("_original.wav"):
            continue
        cid = fn[:-4]
        x, sr = sf.read(os.path.join(nd, fn))
        pk = round(float(np.max(np.abs(x))), 5) if len(x) else 0.0
        (ctx if cid in st else other)[cid] = pk
    # attempt音声(各attemptの生成直後の音声)も観測
    att = {}
    ad = f"{nd}/attempts"
    if os.path.isdir(ad):
        for fn in sorted(os.listdir(ad)):
            if fn.endswith(".wav") and any(fn.startswith(c + "_attempt") for c in st):
                x, sr = sf.read(os.path.join(ad, fn)); att[fn] = round(float(np.max(np.abs(x))), 5)
    def stats(d):
        v = list(d.values())
        if not v:
            return {}
        return {"n": len(v), "min": min(v), "median": round(statistics.median(v), 5), "max": max(v), "n_gt_0.999": sum(1 for p in v if p > 0.999), "n_ge_0.999": sum(1 for p in v if p >= 0.999)}
    gr = tl.get("gain_report", {})
    res["levels"][lv] = {"ctx_dialogue_final_wav_peak": ctx, "ctx_stats": stats(ctx), "non_ctx_final_wav_peak_stats": stats(other),
                         "ctx_attempt_wav_peak": att, "ctx_attempt_stats": stats(att),
                         "assembly_headroom": tl.get("headroom"),
                         "assembly_gain_report_dialogue_pieces": {k: v for k, v in gr.items() if k in ctx or k.replace("full_story_", "") in ctx or any(k.endswith(c) for c in ctx)}}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for lv, v in res["levels"].items():
    print(lv, "ctx", v["ctx_stats"], "non_ctx", v["non_ctx_final_wav_peak_stats"], "attempts", v["ctx_attempt_stats"], "headroom", v["assembly_headroom"])
