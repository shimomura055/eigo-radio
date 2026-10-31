# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_03: Family Y の Production TTS段(`er121_family_y_audio_01.generate_y_a2_segments`/`generate_y_b1_segments`、
# どちらも `@er109_scope.family_scope("Y")` 付きの正式関数でYの正式runnerが stage_tts で呼ぶもの)を、既存Y runの入力(parts/support)を
# 新規run dirへ複製し、対象segmentのみ最小本文(latter入り1文)に置換して直接実行する。Batch既定(TTS_EXECUTION_MODE未設定)。LLM/本文再生成なし。
# 実行: PYTHONUTF8=1 <venv python> <this> --level a2|b1b --run-dir <新規dir> --segments y_intro_1,y_voice_1 --budget-jpy N
import argparse, json, os, shutil, sys
sys.path.insert(0, ".")
ap = argparse.ArgumentParser()
ap.add_argument("--level", required=True, choices=("a2", "b1b"))
ap.add_argument("--run-dir", required=True)
ap.add_argument("--segments", default="y_intro_1,y_voice_1")
ap.add_argument("--dry-prep", action="store_true", help="入力複製とplan表示のみ(API 0)")
a = ap.parse_args()
os.environ.pop("TTS_EXECUTION_MODE", None)          # Production既定(BATCH)のまま。STANDARDへ上書きしない
Y_SRC = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
TEXTS = {"y_intro_1": "First, hear from the latter speaker.",
         "y_voice_1": "Many people choose the latter option."}
import er121_family_y_audio_01 as ya
import er005_cost_logger as cl
import er078_asr_unified_judge_01 as _uj  # noqa: F401
import er139_flapt_provenance_01 as prov

run = a.run_dir.replace("\\", "/")
lv = a.level
sel = [s for s in a.segments.split(",") if s]
os.makedirs(f"{run}/{lv}/narration", exist_ok=True)
os.makedirs(f"{run}/{lv}/audit", exist_ok=True)
for rel in (f"{lv}/parts.json", f"{lv}/support_texts.json"):
    shutil.copyfile(f"{Y_SRC}/{rel}", f"{run}/{rel}")
shutil.copyfile(f"{Y_SRC}/voice_assignment.json", f"{run}/voice_assignment.json")
pj = json.load(open(f"{run}/{lv}/parts.json", encoding="utf-8"))
for s in sel:
    pj["segments"][s] = TEXTS[s]
json.dump(pj, open(f"{run}/{lv}/parts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pid = ya.Y_APPROVED_STYLE_PROFILE
ya.style_profile_mod.resolve_run_profile(run, pid, write=True, tts_backend=ya.TTS_BACKEND)
vmap = ya.segment_voice_map(f"{run}/{lv}", lv)
print("[plan]", [(s, vmap[s], pj["segments"][s]) for s in sel], "backend=", ya.TTS_BACKEND, "profile=", pid,
      "mode=", os.environ.get("TTS_EXECUTION_MODE", "<unset=BATCH default>"))
if a.dry_prep:
    sys.exit(0)
cl.install(f"{run}/raw_usage_log.jsonl")
with cl.logging_context("flapt_ev03", "tts"):
    with ya.only_segments_scope(set(sel)):
        if lv == "b1b":
            out = ya.generate_y_b1_segments(run, style_profile=pid, guard=None)
        else:
            out = ya.generate_y_a2_segments(run, "再配達の有料化", style_profile=pid, guard=None)
print("[statuses]", json.dumps({k: v for k, v in (out.get("statuses") or out.get("status") or {}).items() if k in sel} if isinstance(out, dict) else str(out)[:300]))
cov = prov.coverage_path()
print("[coverage]", cov, os.path.exists(cov))
