# -*- coding: utf-8 -*-
"""委任_03 異音再検知(Trial専用、無料ローカル解析のみ。API不使用)。
既存検知器 er057_audio_anomaly_detect_trial_01(アルゴリズム追加開発なし、閾値不変)を、新完成版・新segmentへ適用し、
既知位置(FOCUS1=Std part3 coffee / STD-02,STD-20=Std part2 raw bean(s) / STD-06=part2 earlier / STD-24=topic_intro Coffee)の語位置の指標を旧音声と比較する。
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er057_audio_anomaly_detect_trial_01 as D

BASE = os.path.join(ROOT, "er057_output", "coffee_final_listening_tone_trial_01")
OUT = os.path.join(BASE, "part_final")
SEG = os.path.join(OUT, "segments")
SNAP = D.SNAP
FIXED = D.FIXED_ASSET_PARTS if hasattr(D, "FIXED_ASSET_PARTS") else ("Intro", "Notification 1", "Notification 2", "Notification 3", "Outro")


def whisper_words(path, lang="en"):
    from faster_whisper import WhisperModel
    global _m
    try:
        _m
    except NameError:
        _m = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)
    segs, info = _m.transcribe(path, language=lang, word_timestamps=True, vad_filter=False, beam_size=1, condition_on_previous_text=False)
    words = []
    for s in segs:
        for w in (s.words or []):
            words.append({"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)})
    return words


def probe(path, words, targets):
    """targets: list of lowercase word substrings -> 語窓指標(word_window_metrics)。"""
    x, sr = sf.read(path, dtype="float64")
    x = D.mono(x)
    _, _, _, ref, _ = D.speech_frames(x, sr)
    rows = []
    for w in words:
        ww = w["w"].strip().lower().strip(".,?!\"'")
        if any(ww == t or ww.startswith(t) for t in targets):
            m = D.word_window_metrics(x, sr, w["s"], w["e"], ref)
            m.update(word=w["w"].strip(), s=w["s"], e=w["e"], whisper_prob=w["p"])
            rows.append(m)
    return rows


def main():
    t0 = time.time()
    man = json.load(open(os.path.join(OUT, "assembly_manifest_03_final.json"), encoding="utf-8"))
    res = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "detector": "er057_audio_anomaly_detect_trial_01(閾値・アルゴリズム不変)",
           "segments": {}, "assembled": {}, "known_positions": {}, "new_candidates_medium_or_high": []}
    # 1. 新segment
    new_segs = {
        "std_part1": os.path.join(SEG, "std_part1_f5_slow6.wav"), "std_part2": os.path.join(SEG, "std_part2_f5_slow6.wav"),
        "std_part3": os.path.join(SEG, "std_part3_f5_slow6.wav"), "adv_part1": os.path.join(SEG, "adv_part1_f5.wav"),
        "adv_part2": os.path.join(SEG, "adv_part2_f5.wav"), "adv_part3": os.path.join(SEG, "adv_part3_f5.wav"),
        "std_topic_intro_regen": os.path.join(SEG, "std_topic_intro_regen.wav")}
    words = {}
    for k, p in new_segs.items():
        x, sr = sf.read(p, dtype="float64")
        c, info = D.analyze(x, sr, k, True)
        words[k] = whisper_words(p)
        for e in c:
            e["near_words"] = D.near_words(words[k], e["t"])
        res["segments"][k] = {"path": os.path.relpath(p, ROOT).replace("\\", "/"), "duration": round(len(x) / sr, 3), "peak": round(float(np.max(np.abs(x))), 4),
                              "n_candidates": len(c), "candidates": [{**e, "t": round(e["t"], 3)} for e in c]}
        for e in c:
            if e["confidence"] in ("high", "medium"):
                res["new_candidates_medium_or_high"].append({"where": k, **{kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in e.items()}})
        print(k, len(c), flush=True)
    # 2. 既知位置(新旧の語窓指標比較)
    ww_old = json.load(open(os.path.join(D.P45, "whisper_words.json"), encoding="utf-8"))["segments"]
    old_paths = {"std_part2": f"{SNAP}/a2/narration/full_story_part2.wav", "std_part3": f"{SNAP}/a2/narration/full_story_part3.wav",
                 "adv_part3": f"{SNAP}/b1b/narration/full_story_part3.wav", "std_topic_intro": f"{SNAP}/a2/narration/topic_intro.wav"}
    old_keys = {"std_part2": "a2/full_story_part2", "std_part3": "a2/full_story_part3", "adv_part3": "b1b/full_story_part3", "std_topic_intro": "a2/topic_intro"}
    cases = [("FOCUS1 Std part3 coffee", "std_part3", ["coffee"], "std_part3", "std_part3"),
             ("FOCUS2 Adv part3 coffee(対照)", "adv_part3", ["coffee"], "adv_part3", "adv_part3"),
             ("STD-02/STD-20/STD-19 Std part2 raw bean(s)", "std_part2", ["raw", "bean", "beans", "robbing", "robbings", "robbins"], "std_part2", "std_part2"),
             ("STD-06 Std part2 earlier", "std_part2", ["earlier"], "std_part2", "std_part2"),
             ("STD-24 Std topic_intro Coffee", "std_topic_intro", ["coffee"], "std_topic_intro_regen", "std_topic_intro")]
    for label, oldk, tg, newk, _ in cases:
        old_words = ww_old[old_keys[oldk]]["words"]
        old_rows = probe(old_paths[oldk], old_words, tg)
        new_rows = probe(new_segs[newk], words[newk], tg)
        res["known_positions"][label] = {"old": old_rows, "new": new_rows,
                                          "new_transcript_local_whisper": " ".join(w["w"].strip() for w in words[newk])[:1200]}
    # 3. 完成版assembled
    for level, key in (("std", "std"), ("adv", "adv")):
        L = man["levels"][key]
        x, sr = sf.read(os.path.join(ROOT, L["wav"]), dtype="float64")
        xm = D.mono(x)
        c, info = D.analyze(xm, sr, "assembled", False)
        for ch in range(x.shape[1]):
            for e in D.detect_clip(x[:, ch], sr, "assembled"):
                e["metrics"]["channel"] = ch
                c.append(e)
        tl = L["timeline"]
        rows = []
        for e in c:
            part, tin = D.part_at(tl, e["t"])
            rows.append({"t_episode": round(e["t"], 3), "part": part, "t_in_part": round(tin, 3) if tin is not None else None, "symptom": e["symptom"],
                         "confidence": e["confidence"], "metrics": e["metrics"], "fixed_asset": part in FIXED})
        res["assembled"][level] = {"seconds": round(len(xm) / sr, 3), "peak": round(float(np.max(np.abs(x))), 4), "n_candidates": len(rows),
                                    "n_non_fixed": sum(1 for r in rows if not r["fixed_asset"]), "candidates": rows}
        for r in rows:
            if r["confidence"] in ("high", "medium") and not r["fixed_asset"]:
                res["new_candidates_medium_or_high"].append({"where": f"assembled/{level}", **r})
        print(level, len(rows), flush=True)
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(OUT, "anomaly_recheck_03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(words, open(os.path.join(OUT, "whisper_words_03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done", res["elapsed_s"])


if __name__ == "__main__":
    main()
