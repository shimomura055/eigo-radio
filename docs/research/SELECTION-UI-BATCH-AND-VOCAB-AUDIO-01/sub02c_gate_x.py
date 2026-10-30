# 委任_02C 証跡(X): コピーrunのAssembly入口(load_family_x_*_sources = 既存Audio Validation Gate + er137 gate hook)をAPI 0で実走する。
import json
import os
import sys

WT, MAIN = sys.argv[1], sys.argv[2]
sys.path.insert(0, WT)
os.chdir(MAIN)
import er019_family_x_audio_production_runner_01 as xr  # noqa: E402

OUT = "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_vocab_ev_02c_01"
SRC = "er019_output/moon_shrinking/run_reselect_01"
res = {}
for lv, fn in (("b1b", xr.load_family_x_b1_sources), ("a2", xr.load_family_x_a2_sources)):
    try:
        fn(OUT, source_dir=SRC) if lv == "b1b" else fn(OUT, source_dir=SRC)
        res[lv] = "GATE_PASS"
    except Exception as e:  # noqa: BLE001
        res[lv] = f"{type(e).__name__}: {str(e)[:300]}"
    p = f"{OUT}/{lv}/vocab_audio/vocab_audio.json"
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        res[lv + "_vocab_audio"] = {"complete": d["complete"], "errors": d["errors"], "items": [(i["vocab_index"], i["term"], i["source"], i.get("dur")) for i in d["items"]]}
print(json.dumps(res, ensure_ascii=False, indent=1))
