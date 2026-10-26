# -*- coding: utf-8 -*-
"""組立後wav内の0.2秒gapを実測する(API 0)。chunk_tts_assembly_<level>.json の gap_offsets_in_episode_s を使い、各gap区間の長さ(秒)と
区間内max|x|(完全無音かの確認)、gap直前/直後の5ms窓のmax|x|を出す。使い方: py assembled_gap_check_01.py --assembled <wav> --assembly-json <json> --out <json>"""
import argparse
import json

import numpy as np
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("--assembled", required=True)
ap.add_argument("--assembly-json", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
x, sr = sf.read(a.assembled, dtype="float32", always_2d=True)
doc = json.load(open(a.assembly_json, encoding="utf-8"))
rows = []
w = int(0.005 * sr)
for pid, p in doc["parents"].items():
    for i, (s, e) in enumerate(p.get("gap_offsets_in_episode_s") or []):
        i0, i1 = int(round(s * sr)), int(round(e * sr))
        seg = np.abs(x[i0:i1])
        rows.append({"parent": pid, "gap_index": i + 1, "start_s": s, "end_s": e, "length_s": round(e - s, 4),
                     "max_abs_inside_gap": float(seg.max()) if seg.size else None,
                     "max_abs_5ms_before": float(np.abs(x[max(0, i0 - w):i0]).max()), "max_abs_5ms_after": float(np.abs(x[i1:i1 + w]).max())})
res = {"assembled": a.assembled, "sr": int(sr), "duration_s": round(len(x) / sr, 3), "gaps": rows,
       "all_gaps_length_0_2s": all(abs(r["length_s"] - 0.2) < 0.002 for r in rows),
       "max_abs_inside_any_gap": max((r["max_abs_inside_gap"] for r in rows), default=None)}
json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "gaps"}, ensure_ascii=False), len(rows), "gaps")
