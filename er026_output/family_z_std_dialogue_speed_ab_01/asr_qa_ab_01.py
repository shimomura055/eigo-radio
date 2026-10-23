# -*- coding: utf-8 -*-
"""B版の会話clip(減速なし)をProduction ASR(routing.transcribe, en-US)で検証。Production state/Lockへは書かない。"""
import json, os, re, sys, difflib
sys.path.insert(0, "C:/Users/tensh/eigo-radio"); os.chdir("C:/Users/tensh/eigo-radio")
import er006_asr_provider_routing_01 as routing
OUT = "er026_output/family_z_std_dialogue_speed_ab_01"
def norm(s): return re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("’", "'")).split()
A = json.load(open(f"{OUT}/analysis.json", encoding="utf-8")); out = {}
for story, v in A.items():
    rows = []
    for r in v["rows"]:
        if r["kind"] != "dialogue": continue
        asr, err = routing.transcribe(f"{OUT}/{story}/B/a2/narration/{r['id']}.wav", language="en-US")
        e, a = norm(r["text"]), norm(asr or "")
        sm = difflib.SequenceMatcher(None, e, a).ratio()
        rows.append({"id": r["id"], "expected": r["text"], "asr_B": asr, "err": err, "exact_norm_match": e == a, "similarity": round(sm, 3)})
        print(story, r["id"], e == a, round(sm, 3), flush=True)
    out[story] = rows
json.dump(out, open(f"{OUT}/asr_qa_B.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
