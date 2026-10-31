# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02: Family Z の Production TTS段(`er063_family_z_audio_01.run_tts_stage`、runnerの stage_tts が呼ぶ正式関数)を
# 複製run(新規out dir・既存記事/runは無変更)で最小本文(latter等のflap語)に対して実行し、Batch既定(TTS_EXECUTION_MODE未設定=BATCH)で
# 『実送信voice/model -> 出自台帳 -> wav sha束縛 -> 判定context -> sidecar』が実run上で連鎖することを証拠化する。LLM/本文再生成なし。
# 実行: PYTHONUTF8=1 <venv python> <this> --level b1b|a2 --out-run <新規run dir> --clips "<id>:<kind>:<voice>:<speaker>:<text>" ... --budget-jpy N
import argparse, json, os, sys
sys.path.insert(0, ".")
ap = argparse.ArgumentParser()
ap.add_argument("--level", required=True, choices=("a2", "b1b"))
ap.add_argument("--out-run", required=True)
ap.add_argument("--clip", action="append", required=True, help="id|kind|voice|speaker|text")
ap.add_argument("--budget-jpy", type=float, default=3.0)
a = ap.parse_args()
os.environ.pop("TTS_EXECUTION_MODE", None)          # Production既定(BATCH)のまま。STANDARDへ上書きしない
import er005_cost_logger as cl
import er063_family_z_audio_01 as a63
import er078_asr_unified_judge_01 as _uj  # noqa: F401
import er139_flapt_provenance_01 as prov

run_dir = a.out_run.replace("\\", "/")
os.makedirs(f"{run_dir}/{a.level}/narration", exist_ok=True)
os.makedirs(f"{run_dir}/{a.level}/audit", exist_ok=True)
cl.install(f"{run_dir}/raw_usage_log.jsonl")
plan = []
for i, c in enumerate(a.clip, 1):
    cid, kind, voice, speaker, text = c.split("|", 4)
    plan.append(a63.ClipSpec(cid, a.level, kind, text, voice=voice, speaker=speaker, role_key=a63.role_key_for(kind, a.level, speaker),
                             part=1, language="en"))
print("[plan]", [(s.clip_id, s.kind, s.voice, s.role_key) for s in plan], "mode=", os.environ.get("TTS_EXECUTION_MODE", "<unset=BATCH default>"))
out = a63.run_tts_stage(run_dir, a.level, plan, only_clips=None, article_text=None, story_key="melos")
print("[statuses]", json.dumps(out["statuses"]))
print("[results]", out["results_path"])
cov = prov.coverage_path()
print("[coverage]", cov, os.path.exists(cov))
