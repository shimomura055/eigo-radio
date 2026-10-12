# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01: Final v5 組立(v4 build を踏襲、Trial assembler er057_tone_trial_final_build_03_asm 無改変で再利用、role->wav差替えのみ)。
変更role: Std preview/comment_1〜4(R2、Production runner生成)、Adv kp{1..5}_explanation_en(P3、Production runner生成)。
それ以外はv4の音声を流用(sha256をprovenanceに記録)。usage: python er057_coffee_final_v5_build_01.py build adv|std  /  qa"""
import os, sys, json
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03_asm as A
import er002_common as common, er003_b1_p9a_audio as p9a
import er057_coffee_final_v4_build_01 as V4
OUT = os.path.join(ROOT, "er057_output", "coffee_final_v5")
F5 = os.path.join(OUT, "final_v5")
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_v5_ms_01")
V4D = V4.OUT


def p(x):
    return x.replace("\\", "/")


def std_extra():
    e = V4.std_extra()
    e["preview"] = (p(os.path.join(RUN, "a2", "narration", "preview.wav")), "R", "R2(Production runner、coffee_final_v5)")
    for n in range(1, 5):
        e[f"comment_{n}"] = (p(os.path.join(RUN, "a2", "narration", f"comment_{n}.wav")), "R", "R2(Production runner、coffee_final_v5)")
    return e


def adv_extra():
    e = V4.adv_extra()
    for i in range(1, 6):
        e[f"kp{i}_explanation_en"] = (p(os.path.join(RUN, "b1b", "narration", f"kp{i}_explanation_en.wav")), "R", "P3(Production runner、coffee_final_v5)")
    return e


def build(level):
    os.makedirs(F5, exist_ok=True)
    ov = A.adv_overrides(adv_extra()) if level == "adv" else A.std_overrides(std_extra())
    for k, (path, o, s) in ov.items():
        assert os.path.exists(path), (k, path)
    r = A.assemble_level(level, ov)
    name = "Coffee_Advanced_final_v5" if level == "adv" else "Coffee_Standard_final_v5"
    wavp, mp3p = os.path.join(F5, name + ".wav"), os.path.join(F5, name + ".mp3")
    common.write_wav_float(wavp, r["assembled"], A.SR, 2)
    A.to_mp3(r["assembled"], mp3p)
    m = common.measure_metrics(r["assembled"][:, 0], A.SR)
    rel = lambda q: os.path.relpath(q, ROOT).replace("\\", "/")
    L = {"wav": rel(wavp), "wav_sha256": A.sha(wavp), "mp3": rel(mp3p), "mp3_sha256": A.sha(mp3p), "duration_seconds": r["total_duration_seconds"],
         "peak": round(p9a.peak(r["assembled"]), 5), "clipping_detected": m["clipping_detected"], "headroom": r["headroom"], "gain_report": r["gain_report"],
         "timeline": r["timeline"], "provenance": r["prov"], "metrics": {k: (v if isinstance(v, (int, float, bool, str)) else str(v)) for k, v in m.items()}}
    mp = os.path.join(OUT, "assembly_manifest_v5_01.json")
    man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"tag": "final_v5", "levels": {}}
    man["levels"][level] = L
    json.dump(man, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    v4m = json.load(open(os.path.join(V4D, "assembly_manifest_v4_01.json"), encoding="utf-8"))["levels"][level]
    p4, p5 = v4m["provenance"], r["prov"]
    diff = {k: {"v4": p4[k]["sha256"][:12], "v5": p5[k]["sha256"][:12]} for k in p5 if p4[k]["sha256"] != p5[k]["sha256"]}
    same = [k for k in p5 if p4[k]["sha256"] == p5[k]["sha256"]]
    json.dump({"level": level, "changed_roles": diff, "unchanged_count": len(same), "unchanged_roles": same, "v4_duration": v4m["duration_seconds"], "v5_duration": r["total_duration_seconds"]},
              open(os.path.join(OUT, f"provenance_diff_v5_{level}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(level, "dur", v4m["duration_seconds"], "->", r["total_duration_seconds"], "peak", v4m["peak"], "->", L["peak"], "changed", sorted(diff))


def qa():
    src = open(os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py"), encoding="utf-8").read()
    src = src.replace('os.path.join(OUT, "assembly_manifest_03_final.json")', 'os.path.join(%r, "assembly_manifest_v5_01.json")' % OUT)
    src = src.replace('os.path.join(OUT, "qa_03.json")', 'os.path.join(%r, "qa_v5_01.json")' % OUT)
    ns = {"__name__": "asm_v5", "__file__": os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py")}
    exec(compile(src, "asm_v5", "exec"), ns)
    ns["cmd_qa"]()


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(sys.argv[2])
    else:
        qa()
