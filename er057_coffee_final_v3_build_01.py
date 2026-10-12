# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01: Final v3組立(Final v2のTrial assembler er057_tone_trial_final_build_03_asmを無改変で再利用、role->wav差替えのみ)。
usage: python er057_coffee_final_v3_build_01.py build adv|std   /  qa
"""
import os, sys, json
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03_asm as A
import er002_common as common, er003_b1_p9a_audio as p9a
V2 = A.OUT
OUT = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")
SEG = os.path.join(OUT, "segments")
F3 = os.path.join(OUT, "final_v3")
PD8_ADV = os.path.join(ROOT, "er057_output", "pace_trial_02", "attempts")


def p(x):
    return x.replace("\\", "/")


def adv_extra():
    e = {f"kp{i}_en": (p(os.path.join(V2, "kp_adv_k2", f"K2_advkp{i}.wav")), "T", "K2(委任_04生成、Final v2と同一)") for i in range(1, 6)}
    for n in (1, 2, 3):
        e[f"full_story_part{n}"] = (p(os.path.join(PD8_ADV, f"PD8_adv_part{n}.wav")), "T", "PD8(pace_trial_02生成、再利用)")
    e["in_one_line"] = (p(os.path.join(SEG, "adv_in_one_line_raw.wav")), "R", "IN_ONE_LINE既存承認Style・新原稿(2文)")
    return e


def std_extra():
    ex = json.load(open(os.path.join(V2, "extra_overrides_03.json"), encoding="utf-8"))["std"]
    e = {k: tuple(v) for k, v in ex.items()}
    for n in (1, 2, 3):
        e[f"full_story_part{n}"] = (p(os.path.join(SEG, f"std_part{n}_slow6.wav")), "R", "PD8+6%減速")
    e["in_one_line"] = (p(os.path.join(SEG, "std_in_one_line_slow6.wav")), "R", "IN_ONE_LINE既存承認Style+A2減速指示+6%減速・新原稿(2文)")
    return e


def build(level):
    os.makedirs(F3, exist_ok=True)
    ov = A.adv_overrides(adv_extra()) if level == "adv" else A.std_overrides(std_extra())
    for k, (path, o, s) in ov.items():
        assert os.path.exists(path), (k, path)
    r = A.assemble_level(level, ov)
    name = "Coffee_Advanced_final_v3" if level == "adv" else "Coffee_Standard_final_v3"
    wavp, mp3p = os.path.join(F3, name + ".wav"), os.path.join(F3, name + ".mp3")
    common.write_wav_float(wavp, r["assembled"], A.SR, 2)
    A.to_mp3(r["assembled"], mp3p)
    m = common.measure_metrics(r["assembled"][:, 0], A.SR)
    rel = lambda q: os.path.relpath(q, ROOT).replace("\\", "/")
    L = {"wav": rel(wavp), "wav_sha256": A.sha(wavp), "mp3": rel(mp3p), "mp3_sha256": A.sha(mp3p), "duration_seconds": r["total_duration_seconds"],
         "peak": round(p9a.peak(r["assembled"]), 5), "clipping_detected": m["clipping_detected"], "headroom": r["headroom"], "gain_report": r["gain_report"],
         "timeline": r["timeline"], "provenance": r["prov"], "metrics": {k: (v if isinstance(v, (int, float, bool, str)) else str(v)) for k, v in m.items()}}
    mp = os.path.join(OUT, "assembly_manifest_v3_01.json")
    man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"tag": "final_v3", "levels": {}}
    man["levels"][level] = L
    json.dump(man, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    v2 = json.load(open(os.path.join(V2, "assembly_manifest_04_final.json" if level == "adv" else "assembly_manifest_03_final.json"), encoding="utf-8"))["levels"][level]
    p2, p3 = v2["provenance"], r["prov"]
    diff = {k: {"v2": p2[k]["sha256"][:12], "v3": p3[k]["sha256"][:12]} for k in p3 if p2[k]["sha256"] != p3[k]["sha256"]}
    same = [k for k in p3 if p2[k]["sha256"] == p3[k]["sha256"]]
    json.dump({"level": level, "changed_roles": diff, "unchanged_count": len(same), "unchanged_roles": same, "v2_duration": v2["duration_seconds"], "v3_duration": r["total_duration_seconds"]},
              open(os.path.join(OUT, f"provenance_diff_v3_{level}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(level, "dur", v2["duration_seconds"], "->", r["total_duration_seconds"], "peak", v2["peak"], "->", L["peak"], "changed", sorted(diff))


def qa():
    src = open(os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py"), encoding="utf-8").read()
    src = src.replace('os.path.join(OUT, "assembly_manifest_03_final.json")', 'os.path.join(%r, "assembly_manifest_v3_01.json")' % OUT)
    src = src.replace('os.path.join(OUT, "qa_03.json")', 'os.path.join(%r, "qa_v3_01.json")' % OUT)
    ns = {"__name__": "asm_v3", "__file__": os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py")}
    exec(compile(src, "asm_v3", "exec"), ns)
    ns["cmd_qa"]()


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(sys.argv[2])
    else:
        qa()
