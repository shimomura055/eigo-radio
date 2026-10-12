"""CS audit: 既存wavへのlocal faster-whisper(無料、CPU)転写+word timestamp。API課金0。read-only。"""
import json, sys, glob, os
sys.path.insert(0, ".")
import er008_disfluency_qa_18 as dq
base = "er026_output/family_z_production_e2e_01/melos"
wavs = sorted(set(glob.glob(base + "/run_e2e_0[12]/*/narration/full_story_part1_c5*.wav") +
                  glob.glob(base + "/run_e2e_0[12]/*/narration/attempts/full_story_part1_c5*.wav")))
out = []
for w in wavs:
    for size in ("small", "medium"):
        ws = dq.transcribe_verbatim(w, language="en", model_size=size)
        out.append({"wav": w.replace(base + "/", ""), "model": size,
                    "text": " ".join(x["text"].strip() for x in ws),
                    "words": [{"t": x["text"].strip(), "s": round(x["start"], 2), "e": round(x["end"], 2), "p": round(x["probability"], 2)} for x in ws]})
        print(out[-1]["wav"], size, out[-1]["text"], [(x["t"], x["s"], x["e"]) for x in out[-1]["words"]], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "local_asr_probe_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
