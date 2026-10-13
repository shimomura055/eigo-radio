# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: Coffee新out_dirへ承認済み成果物をsha照合つきでcopyする(API呼出なし、¥0)。
  support : Q5(iii) `--scaffold-only kp`の前提。承認済みsupport文面(Std Preview/Comment1〜4=R2、Adv Preview/Comment)を新out_dirへcopyしsha一致を確認
  r2      : Std Preview/Comment1〜4(R2、承認済み・v5でProduction runner生成)の音声wavとtts_generation_results entryを
            新out_dirへcopy(V5委任の手順を踏襲)。`_generate_or_reuse`が canonical_text 一致で再利用し、再課金しない。
usage: python er071_coffee_m2p0_n01_seed_01.py support|r2 <dst_out_dir>
provenance: <dst>/audit/seed_provenance_02.json に追記。"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

SRC = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01"


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def prov_append(dst, rec):
    p = f"{dst}/audit/seed_provenance_02.json"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"copies": []}
    d["copies"].append(rec)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def copy_verified(src, dst, dst_root, note):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    before = sha_file(src)
    shutil.copyfile(src, dst)
    after = sha_file(dst)
    assert before == after, f"sha mismatch after copy: {src}"
    prov_append(dst_root, {"src": src, "dst": dst, "sha256": after, "note": note})
    return after


def cmd_support(dst):
    out = {}
    for rel in ("a2/a2_support_texts.json", "b1b/b1_support_texts.json"):
        assert os.path.exists(f"{SRC}/{rel}"), rel
        out[rel] = copy_verified(f"{SRC}/{rel}", f"{dst}/{rel}", dst, "承認済みsupport文面(Q5 iii、sha照合済みcopy)")
    print(json.dumps(out, indent=1))


def cmd_r2(dst):
    src_res = json.load(open(f"{SRC}/a2/audit/tts_generation_results.json", encoding="utf-8"))
    names = ["preview", "comment_1", "comment_2", "comment_3", "comment_4"]
    segs = {}
    for n in names:
        e = dict(src_res["segments"][n])
        assert e.get("status") == "OK", n
        src_wav = f"{SRC}/a2/narration/{n}.wav"
        assert sha_file(src_wav) == e["sha256"], f"{n}: wav sha != entry sha"
        new_wav = f"{dst}/a2/narration/{n}.wav"
        copy_verified(src_wav, new_wav, dst, f"R2 {n} (v5 Production runner生成・承認済み)を再利用")
        e["path"] = new_wav
        e["reseeded_from"] = SRC
        segs[n] = e
    doc = {"segments": segs, "key_phrases": {}, "tts_backend": src_res["tts_backend"], "style_version": src_res["style_version"],
           "kp_scaffold_status": src_res.get("kp_scaffold_status")}
    p = f"{dst}/a2/audit/tts_generation_results.json"
    assert not os.path.exists(p), "既存のtts_generation_resultsがあります(上書き禁止)"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    prov_append(dst, {"seeded_results": p, "segments": names, "note": "R2 Std Preview/Comment1-4のentryを再利用用にseed(pathのみ新out_dirへ書換え、他は不変)"})
    print("seeded", names)


if __name__ == "__main__":
    cmd, dst = sys.argv[1], sys.argv[2]
    {"support": cmd_support, "r2": cmd_r2}[cmd](dst)
