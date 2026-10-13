# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-V5-PAUSE-ROOT-CAUSE-01: (a) 全role segment音声のlead/trail/内部無音統計、(b) 最終wavの実効segment間gap(timeline pause位置の無音run実測)。API呼出なし。"""
import os, sys, json, hashlib
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er057_coffee_v5_pause_01_measure as M
ROOT, OUT = M.ROOT, M.OUT
MAN = {"v3": "er057_output/coffee_final_audio_assembly_01/assembly_manifest_v3_01.json", "v4": "er057_output/coffee_final_v4/assembly_manifest_v4_01.json",
       "v5": "er057_output/coffee_final_v5/assembly_manifest_v5_01.json", "F5": "er057_output/coffee_final_listening_tone_trial_01/part_final/assembly_manifest_03_final.json"}


def seg_stats(path):
    x, sr = M.load(path); runs, dur = M.silent_runs(x, sr)
    lead = runs[0][1] if runs and runs[0][0] < 0.005 else 0.0
    trail = dur - runs[-1][0] if runs and runs[-1][1] >= dur - 0.011 else 0.0
    internal = [round((b - a) * 1000) for a, b in runs if a > 0.005 and b < dur - 0.011]
    return {"dur_s": round(dur, 2), "lead_ms": round(lead * 1000), "trail_ms": round(trail * 1000), "n_internal_ge50": len(internal),
            "n_ge300": sum(1 for v in internal if v >= 300), "n_ge500": sum(1 for v in internal if v >= 500), "max_internal_ms": max(internal) if internal else 0,
            "sum_internal_ms": sum(internal)}


def main():
    res = {"segments": {}, "effective_gaps": {}}
    for tag, f in MAN.items():
        d = json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
        for lv, L in d["levels"].items():
            key = f"{tag}_{lv}"
            res["segments"][key] = {}
            for role, v in L["provenance"].items():
                p = v["path"]
                p = os.path.relpath(p, ROOT) if os.path.isabs(p) else p
                if not os.path.exists(os.path.join(ROOT, p)):
                    p = p.replace("\\", "/")
                try:
                    s = seg_stats(p)
                except Exception as e:
                    s = {"error": str(e)}
                s.update(origin=v["origin"], style=v["style"], sha12=v["sha256"][:12])
                res["segments"][key][role] = s
            # effective gaps on final wav
            wavp = L["wav"]
            x, sr = M.load(wavp); runs, dur = M.silent_runs(x, sr)
            gaps = []
            tl = L["timeline"]
            for i, e in enumerate(tl):
                t_end = e["start_seconds"] + e["duration_seconds"]
                if e["part"].startswith("pause") or i + 1 >= len(tl): continue
                nxt = tl[i + 1]
                # 区間境界(次segment開始)を含む/最も近い無音run
                best = None
                for a, b in runs:
                    if a <= t_end + 0.02 and b >= t_end - 0.02:
                        if best is None or (b - a) > (best[1] - best[0]): best = (a, b)
                gaps.append({"after": e["part"], "before": nxt["part"] if not nxt["part"].startswith("pause") else (tl[i + 2]["part"] if i + 2 < len(tl) else "END"),
                             "timeline_pause_s": nxt["duration_seconds"] if nxt["part"].startswith("pause") else 0.0, "effective_gap_ms": round((best[1] - best[0]) * 1000) if best else 0})
            res["effective_gaps"][key] = gaps
            print(key, "gaps", len(gaps), "mean_eff", round(np.mean([g["effective_gap_ms"] for g in gaps])), "max", max(g["effective_gap_ms"] for g in gaps))
    json.dump(res, open(os.path.join(OUT, "segment_silence_and_effective_gaps.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
