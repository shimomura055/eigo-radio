# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: Coffee M2P0+N01 試聴版の組立(v5 build `er057_coffee_final_v5_build_01.py` を踏襲)。
Trial assembler `er057_tone_trial_final_build_03_asm`(無改変)で、role->wavだけ差替える。差替えroleは Production runner が新out_dirで生成したもの:
  Std: full_story_part1-3(N01逐語+6%減速、runner経由)、kp{1..5}_en / meaning_{1..5}(新KP=M2P0)、preview/comment_1-4(R2・v5承認済みの再利用copy)
  Adv: full_story_part1-3(N01逐語、runner経由)、kp{1..5}_en / kp{1..5}_explanation_en(新KP=M2P0、P3)
それ以外(shell/固定音源/topic_intro/japanese_title/in_one_line/Adv Preview・Comment等)はv5の音声を再利用(sha256をprovenanceに記録)。
KP項目は新out_dirの keywords_canonicalized.json を読む(assemblerのKP読込部をこのscript内で差替え)。
注意: これはTrial assembler経由の試聴版組立であり、runner `--stage assemble`(M3 Gate/Audio Validation Gate)は通さない。
M3 Gateはオフラインで別実行(`gate_evidence`)。usage: python er071_coffee_m2p0_n01_build_01.py build std|adv <out_dir> / qa"""
import os
import sys
import json

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03_asm as A  # noqa: E402
import er002_common as common  # noqa: E402
import er003_b1_p9a_audio as p9a  # noqa: E402
import er057_coffee_final_v5_build_01 as V5  # noqa: E402

OUT = os.path.join(ROOT, "er071_output", "m2p0_n01_production_wiring_01", "coffee_build_02")
FINAL = os.path.join(OUT, "final")
RUN = None  # main()で設定


def p(x):
    return x.replace("\\", "/")


def narr(level_dir, name):
    return p(os.path.join(RUN, level_dir, "narration", name))


def std_extra():
    e = V5.std_extra()
    for n in (1, 2, 3):
        e[f"full_story_part{n}"] = (narr("a2", f"full_story_part{n}.wav"), "R", "N01逐語+6%減速(Production runner、coffee_n01_r2_p3)")
    for i in range(1, 6):
        e[f"kp{i}_en"] = (narr("a2", f"kp{i}_en.wav"), "R", "KP英語(Production runner、M2P0 KP)")
        e[f"meaning_{i}"] = (narr("a2", f"meaning_{i}.wav"), "R", "KP日本語意味(Production runner、M2P0 KP)")
    e["preview"] = (narr("a2", "preview.wav"), "R", "R2(v5承認済み・新out_dirへ再利用copy)")
    for n in range(1, 5):
        e[f"comment_{n}"] = (narr("a2", f"comment_{n}.wav"), "R", "R2(v5承認済み・新out_dirへ再利用copy)")
    return e


def adv_extra():
    e = V5.adv_extra()
    for n in (1, 2, 3):
        e[f"full_story_part{n}"] = (narr("b1b", f"full_story_part{n}.wav"), "R", "N01逐語(Production runner、coffee_n01_r2_p3)")
    for i in range(1, 6):
        e[f"kp{i}_en"] = (narr("b1b", f"kp{i}_en.wav"), "R", "KP英語(Production runner、M2P0 KP)")
        e[f"kp{i}_explanation_en"] = (narr("b1b", f"kp{i}_explanation_en.wav"), "R", "P3(Production runner、M2P0 KP)")
    return e


def kp_items(level_dir):
    kp = json.load(open(os.path.join(RUN, level_dir, "key_phrases", "keywords_canonicalized.json"), encoding="utf-8"))
    return sorted(kp["items"], key=lambda it: it["rank"])


def std_sources(ov):
    """A.std_sources と同一だが、KP項目だけ新out_dirから読む。"""
    L = A.Loader("std", ov)
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    preview_mono = L.get("preview")
    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "num_one", "num_two", "num_three", "num_four", "num_five",
                 "topic_intro", "japanese_title"):
        narration[name] = L.get(name)
    items = kp_items("a2")
    comps = {}
    for i, it in enumerate(items, start=1):
        comps[it["rank"]] = L.get(f"kp{it['rank']}_en")
        narration[f"meaning_{i}"] = L.get(f"meaning_{i}")
    segs = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4", "full_story_part1", "full_story_part2", "full_story_part3", "in_one_line"):
        segs[name] = L.get(name)
    return ({"intro": intro, "notification": notification, "outro": outro, "preview_mono": preview_mono, "narration": narration,
             "key_phrase_components": comps, "a2_segments": segs, "kp_items": items}, L.prov)


def adv_sources(ov):
    L = A.Loader("adv", ov)
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        narration[name] = L.get(f"{name}_charon")
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        narration[name] = L.get(f"{name}_charon")
    narration["topic_intro"] = L.get("topic_intro")
    b1 = {}
    for name in ("full_story_part1", "full_story_part2", "full_story_part3", "comment_1", "comment_2", "comment_3", "comment_4", "preview", "in_one_line"):
        b1[name] = L.get(name)
    items = kp_items("b1b")
    comps, means = {}, {}
    for it in items:
        r = it["rank"]
        comps[r] = L.get(f"kp{r}_en")
        means[r] = L.get(f"kp{r}_explanation_en")
    return ({"intro": intro, "notification": notification, "outro": outro, "narration": narration, "b1_segments": b1,
             "key_phrase_components": comps, "key_phrase_meanings": means, "kp_items": items}, L.prov)


def build(level):
    os.makedirs(FINAL, exist_ok=True)
    A.std_sources, A.adv_sources = std_sources, adv_sources
    ov = A.adv_overrides(adv_extra()) if level == "adv" else A.std_overrides(std_extra())
    for k, (path, o, s) in ov.items():
        assert os.path.exists(path), (k, path)
    r = A.assemble_level(level, ov)
    name = "Coffee_Advanced_m2p0_n01" if level == "adv" else "Coffee_Standard_m2p0_n01"
    wavp, mp3p = os.path.join(FINAL, name + ".wav"), os.path.join(FINAL, name + ".mp3")
    common.write_wav_float(wavp, r["assembled"], A.SR, 2)
    A.to_mp3(r["assembled"], mp3p)
    m = common.measure_metrics(r["assembled"][:, 0], A.SR)
    rel = lambda q: os.path.relpath(q, ROOT).replace("\\", "/")
    L = {"wav": rel(wavp), "wav_sha256": A.sha(wavp), "mp3": rel(mp3p), "mp3_sha256": A.sha(mp3p), "duration_seconds": r["total_duration_seconds"],
         "peak": round(p9a.peak(r["assembled"]), 5), "clipping_detected": m["clipping_detected"], "headroom": r["headroom"], "gain_report": r["gain_report"],
         "timeline": r["timeline"], "provenance": r["prov"], "metrics": {k: (v if isinstance(v, (int, float, bool, str)) else str(v)) for k, v in m.items()}}
    mp = os.path.join(OUT, "assembly_manifest_m2p0_n01_02.json")
    man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"tag": "coffee_m2p0_n01_01", "run_out_dir": RUN, "levels": {}}
    man["levels"][level] = L
    json.dump(man, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    v5m = json.load(open(os.path.join(V5.OUT, "assembly_manifest_v5_01.json"), encoding="utf-8"))["levels"][level]
    p5, pn = v5m["provenance"], r["prov"]
    diff = {k: {"v5": p5[k]["sha256"][:12], "new": pn[k]["sha256"][:12]} for k in pn if k in p5 and p5[k]["sha256"] != pn[k]["sha256"]}
    same = [k for k in pn if k in p5 and p5[k]["sha256"] == pn[k]["sha256"]]
    json.dump({"level": level, "changed_roles": diff, "unchanged_count": len(same), "unchanged_roles": same, "v5_duration": v5m["duration_seconds"],
               "new_duration": r["total_duration_seconds"]}, open(os.path.join(OUT, f"provenance_diff_vs_v5_{level}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(level, "dur", v5m["duration_seconds"], "->", r["total_duration_seconds"], "peak", v5m["peak"], "->", L["peak"], "changed", sorted(diff))


def qa():
    src = open(os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py"), encoding="utf-8").read()
    src = src.replace('os.path.join(OUT, "assembly_manifest_03_final.json")', 'os.path.join(%r, "assembly_manifest_m2p0_n01_02.json")' % OUT)
    src = src.replace('os.path.join(OUT, "qa_03.json")', 'os.path.join(%r, "qa_m2p0_n01_02.json")' % OUT)
    ns = {"__name__": "asm_m2p0", "__file__": os.path.join(ROOT, "er057_tone_trial_final_build_03_asm.py")}
    exec(compile(src, "asm_m2p0", "exec"), ns)
    ns["cmd_qa"]()


if __name__ == "__main__":
    if sys.argv[1] == "build":
        RUN = sys.argv[3]
        build(sys.argv[2])
    else:
        qa()
