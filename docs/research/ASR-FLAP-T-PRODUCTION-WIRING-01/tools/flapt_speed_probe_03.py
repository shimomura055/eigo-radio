import sys, os, json, math, hashlib
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools")
from dotenv import dotenv_values
for k, v in dotenv_values("C:/Users/tensh/eigo-radio/.env").items(): os.environ.setdefault(k, v or "")
import er008_a2_postprocess_slowdown_01 as slow, er063_family_z_audio_01 as z
import er006_asr_provider_routing_01 as route, er006_secondary_asr_01 as sec, er104_kp_three_asr_vote_01 as v3
import flapt_equivalence_proto_01 as proto
import flapt_voice_probe_02 as P
OUT = "docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01/probe_03c"
import er005_cost_logger as cl; cl.install(OUT + "/cost_log.jsonl")
T = "docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01"
ITEMS = ["latter","metal","betting","atom","waiting","coating","the latter one"]
combos = [("Aoede","fl","probe_02"),("Schedar","fl","probe_02"),("Zephyr","fl","probe_02"),("Fenrir","fl","probe_02"),("Orus","pro","probe_02b"),("Kore","pro","probe_02b")]
fns = [("openai", lambda w: route.transcribe(w,"en")),("azure", lambda w: sec.get_full_text_via_azure_stt_with_phrase_list(w, language="en-US", phrases=None)),("whisper", lambda w: (v3.whisper_transcribe(w), None))]
rows=[]; cost=0
for v,p,d in combos:
    for it in ITEMS:
        src=f"{T}/{d}/wav/{v}_{p}_{it.replace(' ','_')}.wav"
        if not os.path.exists(src): rows.append({"voice":v,"path":p,"item":it,"status":"NO_SRC"}); continue
        dst=f"{OUT}/wav/{v}_{p}_{it.replace(' ','_')}_fast106.wav"
        info=slow.apply_a2_slowdown(src,dst,z.Z_ADV_DIALOGUE_SLOWDOWN_PCT)
        asr=P.asr_all(dst,fns); c=P.asr_cost(info["dst_duration_seconds"]); cost+=c
        cls={s:P.classify(proto,it,o["text"]) for s,o in asr.items()}
        rows.append({"voice":v,"path":p,"item":it,"status":"OK","src_sha256":P.sha(src),"clip_sha256":P.sha(dst),"tempo_actual_pct":info["slowdown_pct_actual"],"asr":asr,"class":cls,"asr_cost_jpy":c})
        print(v,p,it,cls,flush=True)
json.dump({"rows":rows,"asr_cost_jpy":round(cost,3)}, open(f"{OUT}/results.json","w",encoding="utf8"), ensure_ascii=False, indent=1)
print("cost",cost)
