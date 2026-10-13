# -*- coding: utf-8 -*-
import json, hashlib, sys
fs = ["er006_output/master_audio_store_01/manifest.json", "er006_output/master_audio_store_01/reuse_telemetry.jsonl", "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", "er011_output/attempt_history.jsonl", "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl", "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl", "er006_output/pronunciation_ledger_01/ledger.json", "er005_output/cost_baseline_01/cost_summary.json"]
O = "er057_output/coffee_tts_style_h_speed_02/"
d = {f: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in fs}
if sys.argv[1] == "pre": json.dump(d, open(O + "state_guard_pre.json", "w"), indent=1)
else:
    json.dump(d, open(O + "state_guard_post.json", "w"), indent=1)
    pre = json.load(open(O + "state_guard_pre.json"))
    json.dump({"pre": pre, "post": d, "changed": [k for k in pre if pre[k] != d[k]], "note": "本Trialは上記へ書込まない"}, open(O + "state_guard_02.json", "w"), indent=1)
    print("changed:", [k for k in pre if pre[k] != d[k]])
