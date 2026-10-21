# -*- coding: utf-8 -*-
"""FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01 Trial専用。Production moduleはimportのみ(diff 0)。
Family Z Dialogue実経路(er063 dialogue(): generate_voice_body_wide_margin、style_prefix_override=None、減速なし)で10 Voice x 2セリフを生成。"""
import os, sys, json, time, wave
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
from concurrent.futures import ThreadPoolExecutor
import er005_cost_logger as cl
OUT = "er087_output/family_z_voice_candidates_trial_01"
os.makedirs(OUT, exist_ok=True)
cl.install(f"{OUT}/cost_log.jsonl")
import er012_b_family_voices_production_01 as bv
import er003_b1_p9a_audio as p9a
import er008_a2_timestretch_abc_10 as f0mod

LINES = {
 "calm": "I think we should take the earlier train tomorrow morning. That way we can have a quiet breakfast together before the long meeting starts.",
 "emotional": "I can't believe you did that without telling me! I was so worried, and now I'm just really, really happy you're safe.",
}
CANDS = {
 "male": [("Algieba", "既存"), ("Schedar", "既存候補"), ("Fenrir", "新規"), ("Orus", "新規"), ("Puck", "新規")],
 "female": [("Erinome", "既存"), ("Sulafat", "既存候補"), ("Kore", "新規"), ("Leda", "新規"), ("Zephyr", "新規")],
}
def one(args):
    voice, line = args
    d = f"{OUT}/{voice}"; os.makedirs(d, exist_ok=True)
    p = f"{d}/{line}.wav"
    t0 = time.time()
    try:
        r = bv.generate_voice_body_wide_margin(LINES[line], p, voice)
    except Exception as e:
        r = {"status": "EXC", "reason": repr(e)[:300]}
    rec = {"voice": voice, "line": line, "status": r.get("status"), "reason": r.get("reason"), "asr_text": r.get("asr_text"),
           "attempts": len(r.get("attempts_log") or []), "elapsed_s": round(time.time() - t0, 1)}
    if os.path.exists(p) and r.get("status") == "OK":
        with wave.open(p) as w: rec["duration_s"] = round(w.getnframes() / w.getframerate(), 2)
        rec["size_bytes"] = os.path.getsize(p)
        rec["median_f0_hz"] = f0mod.estimate_median_f0(p)["median_f0_hz"]
    return rec
if __name__ == "__main__":
    voices = sys.argv[1].split(",") if len(sys.argv) > 1 else [v for g in CANDS.values() for v, _ in g]
    jobs = [(v, l) for v in voices for l in LINES]
    with ThreadPoolExecutor(4) as ex: res = list(ex.map(one, jobs))
    mp = f"{OUT}/manifest.json"
    man = json.load(open(mp, encoding="utf8")) if os.path.exists(mp) else {"lines": LINES, "model": p9a.ENGLISH_MODEL_NAME,
        "style": "p9a.ENGLISH_STYLE_PREFIX(既定Dialogue Style、減速なし)", "candidates": CANDS, "clips": {}}
    for r in res: man["clips"][f"{r['voice']}/{r['line']}"] = r
    json.dump(man, open(mp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for r in res: print(r)
