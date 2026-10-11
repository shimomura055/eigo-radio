# -*- coding: utf-8 -*-
"""委任_01C: local faster-whisper(小, CPU int8, local_files_only)で各segment wavのword timestampsを取得(¥0、API不使用)。"""
import json, glob, os, time, sys
from faster_whisper import WhisperModel
import faster_whisper
S = "er057_output/coffee_final_listening_tone_trial_01/part_45/evidence_snapshot"
OUT = "er057_output/coffee_final_listening_tone_trial_01/part_45/whisper_words.json"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "small"
JA = ("japanese_title", "preview", "comment_", "meaning_")
m = WhisperModel(MODEL, device="cpu", compute_type="int8", local_files_only=True)
res = {"model": MODEL, "faster_whisper_version": faster_whisper.__version__, "segments": {}}
t0 = time.time()
for lv in ("a2", "b1b"):
    for f in sorted(glob.glob(f"{S}/{lv}/narration/*.wav")):
        name = os.path.basename(f)[:-4]
        if name.endswith("_original"):
            continue
        lang = "ja" if (name.startswith(JA) and not name.startswith("preview_intro")) else "en"
        segs, info = m.transcribe(f, language=lang, word_timestamps=True, vad_filter=False, beam_size=1, condition_on_previous_text=False)
        words = []
        for s in segs:
            for w in (s.words or []):
                words.append({"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)})
        res["segments"][f"{lv}/{name}"] = {"lang": lang, "duration": round(info.duration, 3), "words": words}
        print(lv, name, lang, len(words), round(time.time() - t0, 1), flush=True)
res["elapsed_seconds"] = round(time.time() - t0, 1)
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
