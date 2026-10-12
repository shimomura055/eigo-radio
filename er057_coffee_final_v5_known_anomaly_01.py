# -*- coding: utf-8 -*-
"""委任_01A: v3既知異音3件のv3 vs v5(Full Storyはv4音声流用=同一wav)比較(local faster-whisper small, 無料)。v3/v4 の該当Part wavのword timestampsと、検知器候補を比較。"""
import json, os, sys
from faster_whisper import WhisperModel
ROOT = os.path.dirname(os.path.abspath(__file__))
V3 = "er057_output/coffee_final_audio_assembly_01"; V4 = "er057_output/coffee_final_v4"; V5 = "er057_output/coffee_final_v5"
CASES = [("adv", 1, 13.3, "Advanced Part1 'wanna'付近"), ("adv", 3, 39.85, "Advanced Part3"), ("std", 2, 32.07, "Standard Part2")]
def path(ver, lv, n):
    if ver == "v3": return f"er057_output/pace_trial_02/attempts/PD8_adv_part{n}.wav" if lv == "adv" else f"{V3}/segments/std_part{n}_slow6.wav"
    return f"{V4}/segments/adv_part{n}_raw.wav" if lv == "adv" else f"{V4}/segments/std_part{n}_slow6.wav"
m = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)
def words(p):
    segs, _ = m.transcribe(p, language="en", word_timestamps=True, vad_filter=False, beam_size=1, condition_on_previous_text=False)
    return [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in (s.words or [])]
def ctx(ws, t, k=4):
    i = min(range(len(ws)), key=lambda i: abs(ws[i]["s"] - t))
    return i, ws[max(0, i - k):i + k + 1]
out = []
for lv, n, t, label in CASES:
    w3, w4 = words(path("v3", lv, n)), words(path("v4", lv, n))
    i3, c3 = ctx(w3, t)
    # v4 対応位置 = v3の文脈語(前後3語)の語列が最も一致する位置
    key = [x["w"].lower().strip(".,?!") for x in w3[max(0, i3 - 3):i3 + 4]]
    best = None
    for j in range(len(w4)):
        seg = [x["w"].lower().strip(".,?!") for x in w4[max(0, j - 3):j + 4]]
        sc = sum(a == b for a, b in zip(key, seg))
        if best is None or sc > best[0]: best = (sc, j)
    j4 = best[1]
    an3 = json.load(open(f"{V3}/anomaly_v3_{lv}.json", encoding="utf-8"))["candidates"]
    an4 = json.load(open(f"{V5}/anomaly_v5_{lv}.json", encoding="utf-8"))["candidates"]
    pn = f"Full Story Part {n}"
    near3 = [c for c in an3 if c["part"].startswith(pn) and abs((c["t_in_part"] or -99) - t) <= 1.5]
    t4 = w4[j4]["s"]
    near4 = [c for c in an4 if c["part"].startswith(pn) and abs((c["t_in_part"] or -99) - t4) <= 1.5]
    allp4 = [(c["t_in_part"], c["symptom"], c["confidence"]) for c in an4 if c["part"].startswith(pn)]
    out.append({"case": label, "lv": lv, "part": n, "v3_t": t, "v3_context": [(x["w"], x["s"]) for x in c3], "v3_detector_near": [(c["t_in_part"], c["symptom"], c["confidence"]) for c in near3],
                "v4_match_score": f"{best[0]}/{len(key)}", "v4_mapped_t": t4, "v4_context": [(x["w"], x["s"]) for x in w4[max(0, j4 - 4):j4 + 5]],
                "v4_detector_near": [(c["t_in_part"], c["symptom"], c["confidence"]) for c in near4], "v4_all_candidates_in_part": allp4})
json.dump(out, open(f"{V5}/known_anomaly_compare_v5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for o in out: print(json.dumps(o, ensure_ascii=False))
