# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03 T-2追記(1)(2)(4): 有料run前の事前確認(API 0)。
evidence run dir を一時dirへ複製し、正式 load_level_inputs(for_tts=True) のplanで run_tts_stage を『偽generator』で実行する。
偽generatorはnarrator chunkだけ許可(呼出を記録しtoneを書く)、それ以外(dialogue・shell・KP・comment等)が呼ばれたら例外=再生成が起きる見込みを検知。
結果: 呼ばれたclip id一覧(期待=full_story_part2_c1_k1/k2のみ)。run dir本体には一切書かない。"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.getcwd())
import numpy as np

import er002_common as common
import er026_family_z_fiction_production_runner_01 as r
import er063_family_z_audio_01 as z

SRC = "er026_output/family_z_production_e2e_01/melos/run_stdchunk_ev_01"
only = {"full_story_part2_c1"}
tmp = tempfile.mkdtemp()
dst = f"{tmp}/melos/run_stdchunk_ev_01"
shutil.copytree(SRC, dst)
ctx = r.E2EContext(story_key="melos", slug="melos", run="run_stdchunk_ev_01", mode="dry-run", run_root=f"{tmp}")
ctx.run_root = tmp
inp = r.load_level_inputs(ctx, "a2", for_tts=True)
plan = inp["plan"]
calls = []


def fake(kind):
    def fn(spec, out_path):
        calls.append((spec.clip_id, spec.kind))
        if not (spec.kind == "narrator" and (spec.extra or {}).get("chunk")):
            raise RuntimeError(f"UNEXPECTED_REGENERATION:{spec.clip_id}")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        t = np.arange(24000) / 24000
        common.write_wav_float(out_path, (0.2 * np.sin(2 * np.pi * 220 * t)).astype("float32"), 24000, 1)
        shutil.copyfile(out_path, out_path.replace(".wav", "_original.wav"))
        return {"status": "OK", "asr_text": spec.text, "text": spec.text, "slowdown_applied": True,
                "slowdown_info": {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.06, "slowdown_pct_target": 6.0},
                "standard_attempts_log": [], "tts_generations_used": 1}
    return fn


gens = {k: fake(k) for k in ("narrator", "dialogue", "topic_intro", "preview", "comment", "japanese_title", "kp_en", "kp_ja", "kp_expl_en")}
out = {"chunk_plan": {p: [(c["chunk_id"], c["words"], c["boundary_kind"]) for c in pl["chunks"]] for p, pl in inp["chunk_plans"].items()},
       "plan_chunk_specs": [s.clip_id for s in plan if (s.extra or {}).get("chunk")]}
try:
    z.run_tts_stage(dst, "a2", plan, generators=gens, only_clips=only, article_text=inp["article_text"], story_key="melos")
    out["result"] = "OK"
except Exception as e:  # noqa: BLE001
    out["result"] = f"{e.__class__.__name__}: {e}"
out["calls"] = calls
seg = json.load(open(f"{dst}/a2/audit/tts_generation_results.json", encoding="utf-8"))["segments"] if os.path.exists(f"{dst}/a2/audit/tts_generation_results.json") else {}
out["dialogue_reused"] = sorted(k for k, v in seg.items() if v.get("clip_kind") == "dialogue" and v.get("reused_from_previous_run"))
out["n_dialogue_entries"] = sum(1 for v in seg.values() if v.get("clip_kind") == "dialogue")
print(json.dumps(out, ensure_ascii=False, indent=1))
shutil.rmtree(tmp, ignore_errors=True)
