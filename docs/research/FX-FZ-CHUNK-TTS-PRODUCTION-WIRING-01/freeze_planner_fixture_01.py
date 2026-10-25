# -*- coding: utf-8 -*-
"""I3: 採用Trial planner(er114 plan_run / er113 build_chunk_plan)の出力を、ディスク上の全Z run・全X parts.jsonについて凍結する(API 0)。
Production testはDEVのer113/er114をimportしない(commit 13c640bcのallow-list方針)。期待値はこのfixture(planner_fixture_01.json)に凍結する。
実行: py docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/freeze_planner_fixture_01.py [--check]   (repo root)"""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
OUT = os.path.join(HERE, "planner_fixture_01.json")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main(check=False):
    import er114_fz_narration_chunk_trial_01 as t114
    import er113_fx_paragraph_chunk_trial_01 as t113
    fx = {"frozen_from": "er114.plan_run(B_r1 target_words=100) / er113.build_chunk_plan (Trial, Fable受入済み方式)", "z_runs": {}, "x_parts": {}}
    for sp in sorted(glob.glob("er026_output/**/segment_plan_b1b.json", recursive=True)):
        sp = sp.replace("\\", "/")
        run = sp.rsplit("/", 1)[0]
        art = f"{run}/writer/r2.md"
        if not os.path.exists(art):
            continue
        raw_sp, raw_art = open(sp, "rb").read(), open(art, "rb").read()
        try:
            r = t114.plan_run(run, "b1b", "writer/r2.md")
        except AssertionError as e:   # Trial自身が失敗するrun(別途の既知)は凍結対象外
            fx["z_runs"][run] = {"input_sha": sha(raw_sp + raw_art), "trial_error": str(e)[:80]}
            continue
        clips = {}
        for c in r["clips"]:
            ch = []
            if c["split"]:
                n = len(c["chunks"])
                for j, x in enumerate(c["chunks"], start=1):
                    kind = "paragraph" if (j == n or c["cuts"][j - 1]["priority"] == 0) else "sentence"
                    ch.append([x["words"], kind, hashlib.sha256(x["text"].encode("utf-8")).hexdigest(), x["first_para"], x["last_para"]])
            clips[c["clip_id"]] = {"chunks": ch, "paragraph_info_lost": c["paragraph_info_lost"]}
        fx["z_runs"][run] = {"input_sha": sha(raw_sp + raw_art), "clips": clips}
    for pj in sorted(glob.glob("er0*_output/**/parts.json", recursive=True)) + sorted(glob.glob("er1*_output/**/parts.json", recursive=True)):
        pj = pj.replace("\\", "/")
        try:
            parts = json.load(open(pj, encoding="utf-8"))
            if not all(f"part{n}" in parts for n in (1, 2, 3)):
                continue
            plan = t113.build_chunk_plan(parts)
        except Exception as e:
            continue
        fx["x_parts"][pj] = {"input_sha": sha(open(pj, "rb").read()),
                              "chunks": [[c["part"], c["index"], c["words"], hashlib.sha256(c["text"].encode("utf-8")).hexdigest()] for c in plan]}
    if check:
        old = json.load(open(OUT, encoding="utf-8"))
        print("same" if old == fx else "DIFF")
        return
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fx, f, ensure_ascii=False, indent=0, sort_keys=True)
    nz = sum(len(v.get("clips", {})) for v in fx["z_runs"].values())
    nzs = sum(1 for v in fx["z_runs"].values() for c in v.get("clips", {}).values() if c["chunks"])
    print("z_runs", len(fx["z_runs"]), "clips", nz, "split_clips", nzs, "| x_parts", len(fx["x_parts"]), "size", os.path.getsize(OUT))


if __name__ == "__main__":
    main("--check" in sys.argv)
