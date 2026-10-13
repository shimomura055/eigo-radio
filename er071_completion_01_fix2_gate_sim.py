# -*- coding: utf-8 -*-
"""是正②のdry-run(API 0円): validation_state_rebuilt_01.jsonの引継ぎ結果を、現在のb1b results(コピー)へ
メモリ上でマージし、既存のAudio Validation Gate(無変更)にかける。実ファイルは一切変更しない(一時dirで評価)。"""
import json, os, shutil, tempfile
import er003_v1_n3_01_assemble as asm

D = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/b1b"
OUT = "er071_output/m2p0_n01_production_wiring_01/completion_01/fix2_gate_sim_01.json"
rep = json.load(open(f"{D}/validation_state_rebuilt_01.json", encoding="utf-8"))
cur = json.load(open(f"{D}/audit/tts_generation_results.json", encoding="utf-8"))

def run(segments_override, tag):
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(f"{tmp}/audit")
        doc = json.loads(json.dumps(cur))
        doc["segments"].update(segments_override)
        json.dump(doc, open(f"{tmp}/audit/tts_generation_results.json", "w", encoding="utf-8"))
        try:
            asm.verify_episode_audio_validation_gate(tmp, "B1", article_text=None)
            return {"tag": tag, "result": "PASS(段階1: segment判定)"}
        except RuntimeError as e:
            msg = str(e)
            i = msg.find("['")
            return {"tag": tag, "result": "BLOCK", "detail": msg[i: msg.find("]。", i) + 1] if i >= 0 else msg[:200]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

res = {"before_current_state": run({}, "現状(SKIPPED_NOT_SELECTED)"),
       "after_inheritance": run(rep["merged_segments"], "引継ぎ後(証拠が揃う5 segmentのみ)"),
       "inherited": rep["inherited"], "not_inherited": {k: rep["labels"][k]["reason"] for k in rep["not_inherited"]},
       "note": "KP source gate(段階2)はsegment判定通過後に実行される。not_inheritedが残る限りGateはBLOCKを維持する(緩和なし)。"}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
