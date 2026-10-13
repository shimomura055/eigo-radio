# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02: 現在のStd(a2)/Adv(b1b) resultsを既存Gate(無変更)にかけた結果を出力する
(API 0円、実ファイルは読み取りのみ)。使い方: python er071_completion_02_gate_sim.py <tag>"""
import json
import re
import sys

import er003_v1_n3_01_assemble as asm
import er019_family_x_style_profile_01 as sp

RUN = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01"
OUT_DIR = "er071_output/m2p0_n01_production_wiring_01/completion_02"


def blocked_list(level_dir, level):
    try:
        asm.verify_episode_audio_validation_gate(level_dir, level, article_text=None)
        return {"result": "PASS(segment判定)", "blocked": []}
    except RuntimeError as e:
        msg = str(e)
        i = msg.find("['")
        j = msg.find("]。", i)
        blocked = re.findall(r"'([^']+)'", msg[i:j + 1]) if i >= 0 else [msg[:200]]
        return {"result": "BLOCK", "blocked": blocked}


def main(tag):
    res = {"tag": tag}
    for lvl, gate_level in (("a2", "A2"), ("b1b", "B1")):
        d = f"{RUN}/{lvl}"
        r = blocked_list(d, gate_level)
        data = json.load(open(f"{d}/audit/tts_generation_results.json", encoding="utf-8"))
        r["m3_style_gate"] = sp.m3_assembly_gate("coffee_n01_r2_p3", lvl, data)
        r["segment_status"] = {k: (v.get("status"), bool(v.get("validation_inheritance"))) for k, v in data["segments"].items()}
        kp = {}
        for rank, x in (data.get("key_phrases") or {}).items():
            for role, v in x.items():
                kp[f"kp{rank}_{role}"] = v.get("status")
        r["kp_status"] = kp
        res[lvl] = r
    path = f"{OUT_DIR}/fix2_gate_sim_02_{tag}.json"
    json.dump(res, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if k == "tag" else {"result": v["result"], "blocked": v["blocked"], "m3": v["m3_style_gate"]["status"]}) for k, v in res.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
