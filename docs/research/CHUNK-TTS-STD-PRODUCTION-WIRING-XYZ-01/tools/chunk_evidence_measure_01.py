# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02: chunk TTS runtime evidenceの計測(API 0、wav読込のみ)。
入力: <level dir>(narration/ と audit/chunk_plan_<level>.json を持つ。X=…/a2、Y=…/a2 など)。
計測(chunk化した親ごと):
  - 分割位置・語数・chunk数(planから)
  - 各chunkの _original.wav(減速前)/減速後wav の長さと比(Std)。Advは_originalが無いので比なし
  - 親wav = chunk wavの生連結 + 0.2秒(4800サンプル)の完全無音 であること(整数サンプル完全一致・pad区間が全て0)
  - 境界ごとの『可聴無音』= 前chunk末尾の無音 + 0.2秒 + 次chunk先頭の無音(閾値 |x|<=SIL_THR)。Stdは『_original.wavの末尾/先頭無音 x 1.06 + 0.2秒』の推定値を並記
  - pad端のpeak/段差: pad直前・直後 EDGE_MS ms窓のmax|x|と、境界サンプル間の最大|Δx|(クリック有無)
使い方: py chunk_evidence_measure_01.py --level-dir <dir> --level a2 --out <json> [--label <name>]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.getcwd())
import er117_chunk_tts_production_01 as core  # noqa: E402

SR = 24000
SIL_THR = 100          # int16。100/32768 = 約 -50.3 dBFS 以下を無音とみなす
EDGE_MS = 5
PAD = 4800


def lead_trail_silence(x):
    nz = np.flatnonzero(np.abs(x.astype(np.int32)) > SIL_THR)
    if len(nz) == 0:
        return len(x), len(x)
    return int(nz[0]), int(len(x) - 1 - nz[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level-dir", required=True)
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    nd = f"{a.level_dir}/narration"
    plan_doc = json.load(open(f"{a.level_dir}/audit/chunk_plan_{a.level}.json", encoding="utf-8"))
    plans = plan_doc.get("plans") or {}
    res = {"label": a.label, "level_dir": a.level_dir, "level": a.level, "sr": SR, "silence_threshold_int16": SIL_THR,
           "parents": {}}
    edge = int(EDGE_MS * SR / 1000)
    for pid, plan in plans.items():
        if not plan.get("chunked"):
            res["parents"][pid] = {"chunked": False, "paragraphs_reason": plan.get("reason")}
            continue
        ids = [c["chunk_id"] for c in plan["chunks"]]
        words = [c["words"] for c in plan["chunks"]]
        kinds = [c["boundary_kind"] for c in plan["chunks"]]
        pcm = [core.read_pcm16(f"{nd}/{i}.wav") for i in ids]
        orig = [core.read_pcm16(f"{nd}/{i}_original.wav") if os.path.exists(f"{nd}/{i}_original.wav") else None for i in ids]
        parent = core.read_pcm16(f"{nd}/{pid}.wav")
        exp = np.concatenate([np.concatenate([np.zeros(PAD, dtype=pcm[0].dtype), c]) if k else c for k, c in enumerate(pcm)])
        parent_equal = bool(len(parent) == len(exp) and np.array_equal(parent, exp))
        rows, bounds = [], []
        for k, cid in enumerate(ids):
            ls, ts = lead_trail_silence(pcm[k])
            row = {"chunk_id": cid, "words": words[k], "boundary_kind": kinds[k], "samples": int(len(pcm[k])),
                   "seconds": round(len(pcm[k]) / SR, 4), "lead_silence_s": round(ls / SR, 4), "trail_silence_s": round(ts / SR, 4)}
            if orig[k] is not None:
                ols, ots = lead_trail_silence(orig[k])
                row.update({"original_seconds": round(len(orig[k]) / SR, 4), "slowdown_ratio": round(len(pcm[k]) / len(orig[k]), 5),
                            "original_lead_silence_s": round(ols / SR, 4), "original_trail_silence_s": round(ots / SR, 4)})
            rows.append(row)
            if k > 0:
                pad_start = sum(len(c) for c in pcm[:k]) + PAD * (k - 1)    # chunk k-1 の終端(親wav内)
                pad_end = pad_start + PAD
                pad_zero = bool((parent[pad_start:pad_end] == 0).all()) if pad_end <= len(parent) else False
                before = parent[max(0, pad_start - edge):pad_start]
                after = parent[pad_end:pad_end + edge]
                step_a = int(abs(int(parent[pad_start]) - int(parent[pad_start - 1]))) if pad_start >= 1 else 0
                step_b = int(abs(int(parent[pad_end]) - int(parent[pad_end - 1]))) if pad_end < len(parent) else 0
                prev_trail = rows[k - 1]["trail_silence_s"]
                aud = prev_trail + PAD / SR + rows[k]["lead_silence_s"]
                b = {"between": [ids[k - 1], cid], "pad_start_sample": int(pad_start), "pad_samples": PAD, "pad_seconds": round(PAD / SR, 4),
                     "pad_all_zero": pad_zero, "prev_trail_silence_s": prev_trail, "next_lead_silence_s": rows[k]["lead_silence_s"],
                     "audible_silence_s": round(aud, 4),
                     "peak_before_pad_5ms": int(np.abs(before.astype(np.int32)).max()) if len(before) else 0,
                     "peak_after_pad_5ms": int(np.abs(after.astype(np.int32)).max()) if len(after) else 0,
                     "step_at_pad_start": step_a, "step_at_pad_end": step_b,
                     "max_abs_sample_diff_in_edge_windows": int(max(np.abs(np.diff(before.astype(np.int32))).max() if len(before) > 1 else 0,
                                                                   np.abs(np.diff(after.astype(np.int32))).max() if len(after) > 1 else 0))}
                if orig[k] is not None and orig[k - 1] is not None:
                    est = (rows[k - 1]["original_trail_silence_s"] + rows[k]["original_lead_silence_s"]) * 1.06 + PAD / SR
                    b["estimated_audible_silence_from_original_x1.06_plus_0.2s"] = round(est, 4)
                    b["measured_minus_estimated_s"] = round(aud - est, 4)
                bounds.append(b)
        res["parents"][pid] = {"chunked": True, "chunk_count": len(ids), "words": words, "boundary_kinds": kinds,
                               "parent_seconds": round(len(parent) / SR, 4), "parent_samples": int(len(parent)),
                               "parent_equals_chunks_plus_exact_4800_zero_samples": parent_equal,
                               "chunks": rows, "boundaries": bounds,
                               "mean_audible_silence_s": round(float(np.mean([b["audible_silence_s"] for b in bounds])), 4) if bounds else None}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", a.out)


if __name__ == "__main__":
    main()
