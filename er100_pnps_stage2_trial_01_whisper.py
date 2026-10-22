# -*- coding: utf-8 -*-
"""O0(0円): 保存済みwavをローカルWhisper small/mediumで転写(初出のみ。既存音声は変更しない)。"""
import json, os, sys, time
sys.path.insert(0, os.getcwd())
from er100_pnps_stage2_trial_01_common import OUT
from faster_whisper import WhisperModel
d = json.load(open(f"{OUT}/o0_population.json", encoding="utf-8"))
paths = sorted({t["wav_path"] for t in d["table"] if t["wav_exists"]})
res = {}
for size in ("small", "medium"):
    m = WhisperModel(size, device="cpu", compute_type="int8", local_files_only=True)
    for p in paths:
        t0 = time.time()
        segs, _ = m.transcribe(p, language="en", beam_size=5, vad_filter=False)
        res.setdefault(p, {})[size] = " ".join(s.text.strip() for s in segs)
        print(size, p, round(time.time() - t0, 1), flush=True)
    json.dump(res, open(f"{OUT}/o0_whisper.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
