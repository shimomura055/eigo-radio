# -*- coding: utf-8 -*-
"""O0(0円): 保存済みattempt音声(ER-011保持)を母数に追加。各attemptの保存ASR(Primary/cascade)と、ローカルWhisper small/medium転写を取得。既存音声は変更しない。"""
import glob, hashlib, json, os, sys, time
sys.path.insert(0, os.getcwd())
from er100_pnps_stage2_trial_01_common import *

pop = json.load(open(f"{OUT}/o0_population.json", encoding="utf-8"))
rows = load_rows()
items = []
seen = set()
for t in pop["table"]:
    p = t["wav_path"]
    if not t["wav_exists"] or p in seen:
        continue
    seen.add(p)
    dr, seg = os.path.dirname(p), os.path.splitext(os.path.basename(p))[0]
    for wp in sorted(glob.glob(f"{dr}/attempts/{seg}_attempt*.wav")):
        jp = wp[:-4] + ".json"
        meta = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else {}
        words = sorted({x["word"] for x in pop["table"] if x["wav_path"] == p})
        items.append({"wav": wp, "json": jp, "segment_wav": p, "words": words, "language": meta.get("language"), "verified": meta.get("verified"),
                      "route": meta.get("route"), "asr_text": meta.get("asr_text"), "classification": meta.get("audio_classification"),
                      "cascade_steps": meta.get("cascade_steps"), "saved_at": meta.get("saved_at"), "canonical_text": rows[t["row"]]["canonical_text"],
                      "sha256": hashlib.sha256(open(wp, "rb").read()).hexdigest(), "model": meta.get("model"), "voice": meta.get("voice")})
en = [i for i in items if i["language"] in ("en", None)]
print("attempt wavs", len(items), "en", len(en), "distinct sha", len({i['sha256'] for i in items}))
json.dump(items, open(f"{OUT}/o0_attempts_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from faster_whisper import WhisperModel
res = {}
for size in ("small", "medium"):
    m = WhisperModel(size, device="cpu", compute_type="int8", local_files_only=True)
    for i in en:
        t0 = time.time()
        segs, _ = m.transcribe(i["wav"], language="en", beam_size=5, vad_filter=False)
        res.setdefault(i["wav"], {})[size] = " ".join(s.text.strip() for s in segs)
        print(size, i["wav"][-60:], round(time.time() - t0, 1), flush=True)
    json.dump(res, open(f"{OUT}/o0_attempts_whisper.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
