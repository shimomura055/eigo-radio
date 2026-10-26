# -*- coding: utf-8 -*-
"""FZCW Phase 2 evidence 集計(read-only)。run dir群からstate/attempt/cooldown/HR Lock/STOP/費用/peak/ledgerを表化しJSONを出力する。
使い方: py fzcw_evidence_summarize_01.py --runs-root er026_output/.../melos --prefix run_fzcw_ --json out.json
"""
import argparse, glob, json, os, sys


def rj(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def rjl(p):
    out = []
    if os.path.exists(p):
        for l in open(p, encoding="utf-8", errors="replace"):
            l = l.strip()
            if l:
                try:
                    out.append(json.loads(l))
                except Exception:
                    pass
    return out


def summarize_run(run_dir, evidence_dir):
    name = os.path.basename(run_dir)
    r = {"run": name, "run_dir": run_dir}
    r["policy"] = (rj(f"{run_dir}/audit/dialogue_tts_policy.json") or {}).get("policy")
    r["STOP_exists"] = os.path.exists(f"{run_dir}/STOP")
    r["RESTART_STORM_LOCK"] = os.path.exists(f"{run_dir}/RESTART_STORM_LOCK.json")
    sl = rjl(f"{run_dir}/e2e_stage_log.jsonl")
    r["stages"] = [{"stage": x.get("stage"), "elapsed_sec": x.get("elapsed_sec"), "spent_jpy_cumulative": x.get("spent_jpy_cumulative")} for x in sl]
    r["spent_jpy"] = max([x.get("spent_jpy_cumulative") or 0 for x in sl] or [0])
    try:
        sys.path.insert(0, os.getcwd())
        import er019_family_x_audio_production_runner_01 as x_runner      # compute_cost_jpy_so_far(読み取り専用)
        cj = x_runner.compute_cost_jpy_so_far(f"{run_dir}/cost_log.jsonl")
        r["cost_jpy_from_cost_log"] = round(float(cj[0]), 4)
    except Exception as e:      # noqa: BLE001
        r["cost_jpy_from_cost_log"] = f"error:{e.__class__.__name__}"
    by = {}
    for x in rjl(f"{run_dir}/cost_log.jsonl"):
        k = f"{x.get('provider')}|{x.get('api')}|{x.get('model_id')}"
        by[k] = by.get(k, 0) + 1
    r["cost_log_calls_by_api"] = by
    r["launches"] = [x.get("at") for x in rjl(f"{run_dir}/run_launch_log.jsonl") if x.get("event") == "LAUNCH"]
    r["levels"] = {}
    for lv in ("a2", "b1b"):
        d = f"{run_dir}/{lv}"
        if not os.path.isdir(d):
            continue
        L = {}
        st = rj(f"{d}/audit/dialogue_ctx_attempt_state.json") or {}
        clips = {}
        for cid, c in (st.get("clips") or {}).items():
            atts = []
            for a in c.get("attempts", []):
                atts.append({k: a.get(k) for k in ("n", "mode", "effective_mode", "verified", "technical_failure", "started_at", "finished_at",
                                                    "started_epoch", "finished_epoch", "final_ng_epoch", "instruction_type", "counted")})
                rows = a.get("log_rows") or []
                atts[-1]["asr_states"] = [((x.get("asr_judgement") or {}).get("state")) for x in rows]
                atts[-1]["status_rows"] = [x.get("status") for x in rows]
            clips[cid] = {"status": c.get("status"), "policy": c.get("policy"), "ctx_style_sha256": c.get("ctx_style_sha256"), "n_started": c.get("n_started"),
                          "cooldown": c.get("cooldown"), "attempts": atts, "history": c.get("history")}
        L["clips"] = clips
        res = rj(f"{d}/audit/tts_generation_results.json")
        if isinstance(res, dict):
            items = res.get("results") if isinstance(res.get("results"), (list, dict)) else res
            vals = items.values() if isinstance(items, dict) else items
            cnt = {}
            for v in vals:
                if isinstance(v, dict):
                    cnt[v.get("status")] = cnt.get(v.get("status"), 0) + 1
            L["tts_results_status_counts"] = cnt
        L["review_lock_state"] = rj(f"{d}/audit/review_lock_state.json")
        L["narration_wavs"] = len([f for f in os.listdir(f"{d}/narration") if f.endswith(".wav") and not f.endswith("_original.wav")]) if os.path.isdir(f"{d}/narration") else 0
        L["minimal_fallback_attempts"] = sum(1 for c in clips.values() for a in c["attempts"] if a.get("instruction_type") and "minimal" in str(a.get("instruction_type")))
        L["instruction_types"] = sorted({str(a.get("instruction_type")) for c in clips.values() for a in c["attempts"]})
        r["levels"][lv] = L
    r["evidence_jsons"] = sorted(os.path.basename(p) for p in glob.glob(f"{evidence_dir}/RUNTIME_EVIDENCE_*_{name}*.json"))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-root", required=True)
    ap.add_argument("--prefix", default="run_fzcw_")
    ap.add_argument("--evidence-dir", default="docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01")
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    runs = [summarize_run(d, a.evidence_dir) for d in sorted(glob.glob(f"{a.runs_root}/{a.prefix}*")) if os.path.isdir(d)]
    with open(a.json, "w", encoding="utf-8") as f:
        json.dump({"runs": runs}, f, ensure_ascii=False, indent=1, default=str)
    for r in runs:
        print(r["run"], "policy=", r["policy"], "spent=", r["spent_jpy"], "STOP=", r["STOP_exists"])
        for lv, L in r["levels"].items():
            for cid, c in L["clips"].items():
                print("  ", lv, cid, c["status"], [(x["n"], x["mode"], x["verified"]) for x in c["attempts"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
