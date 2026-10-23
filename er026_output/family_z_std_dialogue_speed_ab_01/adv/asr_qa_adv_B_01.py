# -*- coding: utf-8 -*-
"""Advanced B版会話clipをProduction ASR(routing.transcribe, en-US)で検証。Production state/Lockへ書かない。"""
import json, os, re, sys, difflib, time
import soundfile as sf
sys.path.insert(0, "C:/Users/tensh/eigo-radio"); os.chdir("C:/Users/tensh/eigo-radio")
import er006_asr_provider_routing_01 as routing
OUT = "er026_output/family_z_std_dialogue_speed_ab_01/adv"
def norm(s): return re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("’", "'")).split()
A = json.load(open(f"{OUT}/analysis_adv.json", encoding="utf-8")); out = {}; tot = 0.0
for story, v in A.items():
    rows = []
    for r in v["rows"]:
        if r["kind"] != "dialogue": continue
        p = f"{OUT}/{story}/B/b1b/narration/{r['id']}.wav"; sec = sf.info(p).frames / sf.info(p).samplerate; tot += sec
        asr, err = routing.transcribe(p, language="en-US")
        e, a = norm(r["text"]), norm(asr or "")
        rows.append({"id": r["id"], "expected": r["text"], "asr_B": asr, "err": err, "exact_norm_match": e == a,
                     "similarity": round(difflib.SequenceMatcher(None, e, a).ratio(), 3), "sec": round(sec, 3),
                     "asr_A_stored": r.get("asr_A_stored"), "local_whisper_B": r.get("asr_B")})
        print(story, r["id"], e == a, rows[-1]["similarity"], flush=True)
    out[story] = rows
out["_total_sec"] = round(tot, 3); out["_est_jpy_upper"] = round(tot * 0.0463, 2)
json.dump(out, open(f"{OUT}/asr_qa_adv_B.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out["_total_sec"], out["_est_jpy_upper"])
