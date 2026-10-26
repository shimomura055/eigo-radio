# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03: Z Std evidence run dir の準備(API 0)。
既存の melos run_fzcw_e1_01(FZ文脈TTS evidence済み、a2/b1b の dialogue・shell・KP・comment がcache済み)を新run dirへ複製する。
元runは変更しない(読取のみ)。持ち込まない: cost_log・stage log・launch log(費用/RESTART_STORM判定は新runだけで集計)・console・pid・STOP/lock・assembly(再組立する)。
複製するのは run が既に持つ TTS cache(results/narration)とtext資産。→ dialogue等は reuse_key 一致で再利用(TTS 0回)、
Std narrator 134語(full_story_part2_c1)だけがchunk planに変わり新規TTSとなる。"""
import fnmatch
import os
import shutil
import sys

SRC = "er026_output/family_z_production_e2e_01/melos/run_fzcw_e1_01"
DST = "er026_output/family_z_production_e2e_01/melos/run_stdchunk_ev_01"
IGN = ["cost_log.jsonl", "e2e_stage_log.jsonl", "run_launch_log.jsonl", "console_*.txt", "_driver_pid.json", "_launch_time.txt", "STOP*", "RUN_LOCK*", "*.lock"]


def ignore(d, names):
    out = set()
    for n in names:
        if any(fnmatch.fnmatch(n, p) for p in IGN):
            out.add(n)
        rel = os.path.relpath(os.path.join(d, n), SRC).replace(chr(92), "/")
        if rel in ("a2/assembly", "b1b/assembly"):
            out.add(n)
    return out


if __name__ == "__main__":
    if os.path.exists(DST):
        print("DST exists; abort", DST)
        sys.exit(2)
    shutil.copytree(SRC, DST, ignore=ignore)
    print("copied files:", sum(len(f) for _, _, f in os.walk(DST)))
