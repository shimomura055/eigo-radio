# -*- coding: utf-8 -*-
"""委任_04: Advanced完成版を、KP英語=K2(新規5件)で再組立(委任_03 assemblerを無改変で再利用)。Standardは委任_03完成版のまま(manifest流用)。
出力は part_final/final_04 と *_04.json(委任_03成果物は上書きしない)。"""
import os, sys, json
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03_asm as A
import er002_common as common, er003_b1_p9a_audio as p9a
OUT = A.OUT
K2D = os.path.join(OUT, "kp_adv_k2")
F4 = os.path.join(OUT, "final_04")

def main():
    os.makedirs(F4, exist_ok=True)
    man3 = json.load(open(os.path.join(OUT, "assembly_manifest_03_final.json"), encoding="utf-8"))
    extra = {f"kp{i}_en": (os.path.join(K2D, f"K2_advkp{i}.wav").replace("\\", "/"), "T", "K2(委任_04生成)") for i in range(1, 6)}
    r = A.assemble_level("adv", A.adv_overrides(extra))
    name = "Coffee_Advanced_final_v2"
    wavp, mp3p = os.path.join(F4, name + ".wav"), os.path.join(F4, name + ".mp3")
    common.write_wav_float(wavp, r["assembled"], A.SR, 2)
    A.to_mp3(r["assembled"], mp3p)
    m = common.measure_metrics(r["assembled"][:, 0], A.SR)
    rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    man = {"tag": "final_04", "levels": {"std": man3["levels"]["std"], "adv": {
        "wav": rel(wavp), "wav_sha256": A.sha(wavp), "mp3": rel(mp3p), "mp3_sha256": A.sha(mp3p), "duration_seconds": r["total_duration_seconds"],
        "peak": round(p9a.peak(r["assembled"]), 5), "clipping_detected": m["clipping_detected"], "headroom": r["headroom"], "gain_report": r["gain_report"],
        "timeline": r["timeline"], "provenance": r["prov"], "metrics": {k: (v if isinstance(v, (int, float, bool, str)) else str(v)) for k, v in m.items()}}}}
    json.dump(man, open(os.path.join(OUT, "assembly_manifest_04_final.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    old = man3["levels"]["adv"]
    print("adv dur", old["duration_seconds"], "->", r["total_duration_seconds"], "peak", old["peak"], "->", man["levels"]["adv"]["peak"])
    # 差分(Advanced): 変わったroleのsha
    p3, p4 = old["provenance"], r["prov"]
    diff = {k: {"old": p3[k]["sha256"][:12], "new": p4[k]["sha256"][:12]} for k in p4 if p3[k]["sha256"] != p4[k]["sha256"]}
    unchanged = [k for k in p4 if p3[k]["sha256"] == p4[k]["sha256"]]
    json.dump({"changed_roles": diff, "unchanged_count": len(unchanged), "unchanged_roles": unchanged}, open(os.path.join(OUT, "adv_provenance_diff_04.json"), "w"), ensure_ascii=False, indent=1)
    print("changed", diff)

def qa():
    man = json.load(open(os.path.join(OUT, "assembly_manifest_04_final.json"), encoding="utf-8"))
    import er057_tone_trial_final_build_03_asm as M
    # cmd_qaを04 manifestで実行(出力名のみ切替)
    orig_open = open
    L = man["levels"]["adv"]
    # qa関数を再利用するため一時的に03 manifest名をmonkeypatchせず、同ロジックをadvのみ呼ぶ
    import types
    src = open(os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py"), encoding="utf-8").read()
    src = src.replace("assembly_manifest_03_final.json", "assembly_manifest_04_final.json").replace("qa_03.json", "qa_04.json")
    ns = {"__name__": "asm04", "__file__": os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py")}
    exec(compile(src, "asm04", "exec"), ns)
    ns["cmd_qa"]()

if __name__ == "__main__":
    {"build": main, "qa": qa}[sys.argv[1]]()
