# -*- coding: utf-8 -*-
"""委任_04 異音再検知(無料ローカル解析のみ、検知器・閾値不変)。Advanced新完成版+新KP英語5件。Standard/他segmentは委任_03結果が有効(音声不変)。"""
import os, sys, json
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_audio_anomaly_detect_trial_01 as D
OUT = os.path.join(ROOT, "er057_output", "coffee_final_listening_tone_trial_01", "part_final")
FIXED = D.FIXED_ASSET_PARTS if hasattr(D, "FIXED_ASSET_PARTS") else ("Intro", "Notification 1", "Notification 2", "Notification 3", "Outro")
def conf(c): return {"high": 3, "medium": 2, "low": 1}.get(c, 0)
def main():
    man = json.load(open(os.path.join(OUT, "assembly_manifest_04_final.json"), encoding="utf-8"))
    old = json.load(open(os.path.join(OUT, "anomaly_recheck_03.json"), encoding="utf-8"))
    res = {"detector": "er057_audio_anomaly_detect_trial_01(閾値・アルゴリズム不変)", "kp_segments": {}, "assembled_adv": {}, "new_candidates_medium_or_high": []}
    for i in range(1, 6):
        p = os.path.join(OUT, "kp_adv_k2", f"K2_advkp{i}.wav")
        x, sr = sf.read(p, dtype="float64")
        c, _ = D.analyze(x, sr, f"K2_advkp{i}", True)
        res["kp_segments"][f"K2_advkp{i}"] = {"duration": round(len(x) / sr, 3), "peak": round(float(np.max(np.abs(x))), 4), "n_candidates": len(c),
                                              "candidates": [{**e, "t": round(e["t"], 3)} for e in c]}
        for e in c:
            if e["confidence"] in ("high", "medium"):
                res["new_candidates_medium_or_high"].append({"where": f"K2_advkp{i}", **{k: (round(v, 3) if isinstance(v, float) else v) for k, v in e.items()}})
    L = man["levels"]["adv"]
    x, sr = sf.read(os.path.join(ROOT, L["wav"]), dtype="float64")
    c, _ = D.analyze(D.mono(x), sr, "assembled", False)
    for ch in range(x.shape[1]):
        for e in D.detect_clip(x[:, ch], sr, "assembled"):
            e["metrics"]["channel"] = ch; c.append(e)
    rows = []
    for e in c:
        part, tin = D.part_at(L["timeline"], e["t"])
        rows.append({"t_episode": round(e["t"], 3), "part": part, "t_in_part": round(tin, 3) if tin is not None else None, "symptom": e["symptom"],
                     "confidence": e["confidence"], "metrics": e["metrics"], "fixed_asset": part in FIXED})
    res["assembled_adv"] = {"n_candidates": len(rows), "n_non_fixed": sum(1 for r in rows if not r["fixed_asset"]), "candidates": rows}
    o = old["assembled"]["adv"]
    res["assembled_adv_03_n_candidates"] = o["n_candidates"]
    kp = [r for r in rows if r["part"].startswith("Key Phrase")]
    res["assembled_adv_key_phrase_candidates_04"] = kp
    res["assembled_adv_key_phrase_candidates_03"] = [r for r in o["candidates"] if r["part"].startswith("Key Phrase")]
    for r in rows:
        if r["confidence"] in ("high", "medium") and not r["fixed_asset"]:
            res["new_candidates_medium_or_high"].append({"where": "assembled/adv", **r})
    # 03時点で既に存在した同一候補は新規扱いにしない(part・symptomで照合)
    old_keys = {(r["part"], r["symptom"]) for r in o["candidates"] if r["confidence"] in ("high", "medium")}
    res["new_vs_03_medium_or_high"] = [r for r in res["new_candidates_medium_or_high"] if r["where"] == "assembled/adv" and (r["part"], r["symptom"]) not in old_keys] + \
                                       [r for r in res["new_candidates_medium_or_high"] if r["where"].startswith("K2_adv")]
    json.dump(res, open(os.path.join(OUT, "anomaly_recheck_04.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({k: v for k, v in res.items() if k.startswith("assembled_adv_0") or k == "new_vs_03_medium_or_high"})
    print({k: v["n_candidates"] for k, v in res["kp_segments"].items()}, res["assembled_adv"]["n_candidates"], res["assembled_adv"]["n_non_fixed"])
main()
