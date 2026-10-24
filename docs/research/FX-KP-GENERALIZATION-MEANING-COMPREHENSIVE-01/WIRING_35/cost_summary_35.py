"""委任_35 実費集計(runnerと同じ compute_cost_jpy_so_far で token/実額から算出。API 0)。"""
import json, os, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 4)))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er019_family_x_audio_production_runner_01 as xr
K = os.path.dirname(os.path.abspath(__file__))
RUN = "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02"
SINCE = "2026-10-24T13:08"   # UTC。本委任の最初のAPI call(X KP re-run)以降


def cost_of(rows):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        p = f.name
    try:
        return xr.compute_cost_jpy_so_far(p)
    finally:
        os.unlink(p)


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


out = {}
xk = load(f"{K}/cost/usage_log_x.jsonl")
out["X_kp_llm(canon+gloss+redundancy)"] = cost_of(xk)
by_stage = {}
for r in xk:
    by_stage.setdefault(r["stage"], []).append(r)
out["X_kp_by_stage"] = {k: cost_of(v)[0] for k, v in by_stage.items()}
raw = [r for r in load(f"{RUN}/raw_usage_log.jsonl") if r.get("timestamp", "") >= SINCE]
out["X_tts_stage_rows"] = len(raw)
out["X_tts_asr_ner"] = cost_of(raw)
seg = {}
for r in raw:
    seg.setdefault(r.get("segment") or "(none)", []).append(r)
out["X_tts_by_segment_jpy"] = {k: round(cost_of(v)[0], 4) for k, v in seg.items()}
zl = load("er026_output/family_z_production_e2e_01/the_monkeys_paw/run_kpgm35_01/cost_log.jsonl")
out["Z_kp_stage"] = cost_of(zl)
zg = [r for r in zl if r.get("stage") == "kp_gloss_alignment"]
out["Z_gloss_only"] = cost_of(zg)
out["total_jpy"] = round(out["X_kp_llm(canon+gloss+redundancy)"][0] + out["X_tts_asr_ner"][0] + out["Z_kp_stage"][0], 3)
json.dump(out, open(f"{K}/cost_summary_35.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
