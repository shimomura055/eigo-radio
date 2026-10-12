# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_10 客観チェック(read-only、API費用0)。
実行: PYTHONUTF8=1 .venv/Scripts/python.exe er026_output/family_z_production_e2e_01/melos/evidence_10/measure_z_01.py
出力: 同ディレクトリ measure_z_01.json / MEASURE_Z_01.md。音声・Prompt・Master Storeは変更しない。
WPM方式は er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py と同じ
(20msフレーム・-40dBFS無音・500ms以上のポーズを除いた発話WPMと全体WPM。ASRではなく計画テキスト語数を使用)。"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

ROOT = "C:/Users/tensh/eigo-radio"
RUN = f"{ROOT}/er026_output/family_z_production_e2e_01/melos/run_e2e_01"
OUT = f"{ROOT}/er026_output/family_z_production_e2e_01/melos/evidence_10"
FRAME_MS, HOP_MS, THRESH_DB, MIN_PAUSE_MS = 20, 10, -40.0, 500
CLIP_RE = re.compile(r"full_story_part([1-3])_c(\d+)")


def read(path):
    x, sr = sf.read(path, dtype="float64", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x, sr


def frame_db(x, sr):
    f, h = int(sr * FRAME_MS / 1000), int(sr * HOP_MS / 1000)
    n = max(0, (len(x) - f) // h + 1)
    out = np.empty(n)
    for i in range(n):
        s = x[i * h:i * h + f]
        out[i] = 20 * np.log10(max(float(np.sqrt(np.mean(s * s))) if len(s) else 0.0, 1e-10))
    return out


def pauses(db, min_ms):
    sil = db < THRESH_DB
    res, i, n = [], 0, len(sil)
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            d = (j - i) * HOP_MS / 1000
            if d * 1000 >= min_ms:
                res.append({"start": round(i * HOP_MS / 1000, 3), "dur": round(d, 3),
                            "edge": "head" if i == 0 else ("tail" if j >= n else "mid")})
            i = j
        else:
            i += 1
    return res


def words(t):
    return sum(1 for w in t.split() if re.search(r"[A-Za-z0-9]", w))


def main():
    R = {"threshold_dbfs": THRESH_DB, "min_pause_ms": MIN_PAUSE_MS, "levels": {}}
    md = ["# MEASURE_Z_01 客観チェック(委任_10、費用0、read-only)", ""]
    for lv, label in (("a2", "Standard"), ("b1b", "Advanced")):
        plan = json.load(open(f"{RUN}/segment_plan_{lv}.json", encoding="utf-8"))
        res = json.load(open(f"{RUN}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
        tl = json.load(open(f"{RUN}/{lv}/assembly/timeline.json", encoding="utf-8"))
        narr = f"{RUN}/{lv}/narration"
        L = {"label": label, "total_duration_seconds": tl["duration_seconds"], "headroom": tl["headroom"], "parts": {}, "clips": {}}
        # --- assembled wav: peak / 無音 ---
        x, sr = read(tl["wav"])
        L["assembled"] = {"sr": sr, "peak": round(float(np.max(np.abs(x))), 4), "rms": round(float(np.sqrt(np.mean(x * x))), 5),
                          "duration": round(len(x) / sr, 2)}
        long_sil = pauses(frame_db(x, sr), 2000)
        L["assembled"]["silences_ge_2s"] = long_sil
        # --- Part別(Full Story clip) ---
        per_part = {1: [], 2: [], 3: []}
        for c in plan["clips"]:
            m = CLIP_RE.fullmatch(c["id"])
            per_part[int(m.group(1))].append(c)
        story_total_words = story_total_dur = story_total_speech = 0.0
        for n, clips in per_part.items():
            w = sum(words(c["text"]) for c in clips)
            dur = speech = 0.0
            for c in clips:
                cx, csr = read(f"{narr}/{c['id']}.wav")
                d = len(cx) / csr
                db = frame_db(cx, csr)
                p = pauses(db, MIN_PAUSE_MS)
                pd = sum(q["dur"] for q in p)
                dur += d
                speech += d - pd
                ent = (res.get("segments") or {}).get(c["id"], {})
                L["clips"][c["id"]] = {"words": words(c["text"]), "dur": round(d, 3), "peak": round(float(np.max(np.abs(cx))), 4),
                                       "sec_per_word": round(d / max(1, words(c["text"])), 3),
                                       "pauses_ge_500ms": len(p), "status": ent.get("status"),
                                       "slowdown_ratio": ent.get("slowdown_ratio"), "reused": ent.get("reused_from_previous_run")}
            L["parts"][n] = {"words": w, "duration_seconds": round(dur, 2), "speech_seconds": round(speech, 2),
                             "wpm_all": round(w / dur * 60, 1), "wpm_speech": round(w / speech * 60, 1)}
            story_total_words += w
            story_total_dur += dur
            story_total_speech += speech
        L["story_total"] = {"words": int(story_total_words), "duration_seconds": round(story_total_dur, 2),
                            "wpm_all": round(story_total_words / story_total_dur * 60, 1),
                            "wpm_speech": round(story_total_words / story_total_speech * 60, 1)}
        # --- Std英語Story clip減速比 ---
        if lv == "a2":
            ratios = []
            for c in plan["clips"]:
                ent = (res.get("segments") or {}).get(c["id"], {})
                orig = f"{narr}/{c['id']}_original.wav"
                if os.path.exists(orig):
                    ox, osr = read(orig)
                    nx, nsr = read(f"{narr}/{c['id']}.wav")
                    ratios.append({"clip": c["id"], "ratio_measured": round((len(nx) / nsr) / (len(ox) / osr), 4),
                                   "recorded": ent.get("slowdown_ratio"), "applied": ent.get("slowdown_applied")})
                else:
                    ratios.append({"clip": c["id"], "ratio_measured": None, "recorded": ent.get("slowdown_ratio"), "applied": ent.get("slowdown_applied")})
            L["slowdown"] = ratios
            L["slowdown_summary"] = {"n": len(ratios), "missing_original": sum(1 for r in ratios if r["ratio_measured"] is None),
                                     "min": min((r["ratio_measured"] for r in ratios if r["ratio_measured"]), default=None),
                                     "max": max((r["ratio_measured"] for r in ratios if r["ratio_measured"]), default=None)}
        # --- anomaly: clip別 秒/語 の外れ値、peak>0.98、ポーズ多発 ---
        spw = [v["sec_per_word"] for k, v in L["clips"].items() if v["words"] >= 3]
        mu, sd = float(np.mean(spw)), float(np.std(spw))
        L["anomaly"] = {"sec_per_word_mean": round(mu, 3), "sec_per_word_std": round(sd, 3),
                        "outliers_gt_2sd": [k for k, v in L["clips"].items() if v["words"] >= 3 and abs(v["sec_per_word"] - mu) > 2 * sd],
                        "clips_peak_gt_0_98": [k for k, v in L["clips"].items() if v["peak"] > 0.98],
                        "clips_pauses_ge_3": [k for k, v in L["clips"].items() if v["pauses_ge_500ms"] >= 3]}
        # --- timeline Part尺(通し) ---
        L["timeline_pieces"] = [{"part": t["part"], "dur": t["duration_seconds"]} for t in tl["timeline"] if not t["part"].startswith("_silence_")]
        R["levels"][lv] = L
        md += [f"## {label}({lv})", f"- 通し尺 {tl['duration_seconds']} 秒 / peak {L['assembled']['peak']} / headroom {json.dumps(tl['headroom'], ensure_ascii=False)[:200]}",
               f"- 2秒以上の無音: {len(long_sil)} 件 {long_sil[:5]}",
               f"- Full Story 合計 {L['story_total']}",
               "- Part別: " + "; ".join(f"Part{n}: {v['words']}語/{v['duration_seconds']}s WPM全体{v['wpm_all']}/発話{v['wpm_speech']}" for n, v in L["parts"].items()),
               ]
        if lv == "a2":
            md.append(f"- Std英語Story clip減速: {L['slowdown_summary']}")
        md += [f"- anomaly: {json.dumps(L['anomaly'], ensure_ascii=False)}", ""]
    with open(f"{OUT}/measure_z_01.json", "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    with open(f"{OUT}/MEASURE_Z_01.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    sys.exit(main())
