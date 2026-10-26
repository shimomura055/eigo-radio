# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_03: evidence case runner(1 process = 1 group。groupは Family×Level)。

使い方(T-2: STANDARD明示。環境変数とCLI引数の両方):
  $env:TTS_EXECUTION_MODE="STANDARD"; .venv\\Scripts\\python.exe docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_run_01.py \
      --group X-Std --tts-execution-mode STANDARD --budget-jpy 130 [--only X-Std-1,X-Std-2]
各caseは独立したrun dir(run_tru_ev_<case>)で1回だけ実行(起動の自動再試行なし)。出力: evidence_runs/<case>.json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import tru_ev_core_01 as core  # noqa: E402  (importでchdir(ROOT)される)
from tru_ev_core_01 import ROOT, EVD, EVIDENCE_RUNS, Plan, Recorder, clip_of, read_json, read_jsonl  # noqa: E402

TTS_BACKEND = "speech_metadata_flash_lite"
STYLE_PROFILE = "fx_20261017"

X_SRC = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01"
X_ROOT = "er019_output/family_x_audio_production_wiring_01"


def _copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)


def prep_x(case, run_dir):
    """X run dirの最小入力(parts/support/KP/解説text bundle)を既存runからコピー(LLM生成なし・新run dirでcache再利用なし)。"""
    lv = case["level"]
    rels = [f"{lv}/parts.json"] + ([f"{lv}/key_phrases/keywords_canonicalized.json"] if case.get("kp") else [])
    for rel in rels:
        _copy(f"{X_SRC}/{rel}", f"{run_dir}/{rel}")
    import er019_family_x_style_profile_01 as _spm
    _spm.resolve_run_profile(run_dir, STYLE_PROFILE, write=True, tts_backend=TTS_BACKEND)     # runner起動時と同じ固定記録(Gate用)
    if case.get("title_override"):      # 実TTS/ASRの自然なばらつき(Azure Secondaryが特定の題を誤聴する)を避けるため題だけ差替え(本文は元のまま)
        pj = read_json(f"{run_dir}/{lv}/parts.json")
        pj["title"] = case["title_override"]
        if "title_tts" in pj:
            pj["title_tts"] = case["title_override"]
        with open(f"{run_dir}/{lv}/parts.json", "w", encoding="utf-8") as f:
            json.dump(pj, f, ensure_ascii=False, indent=2)
    sup = "a2_support_texts.json" if lv == "a2" else "b1_support_texts.json"
    _copy(f"{X_SRC}/{lv}/{sup}", f"{run_dir}/{lv}/{sup}")


def call_x(case, run_dir):
    import er019_family_x_audio_production_runner_01 as xr
    import er005_cost_logger as cl
    lv = case["level"]
    xr._ONLY_SEGMENTS = None if case.get("kp") else set(case["segments"])      # KP caseは正式のKP closureを直接呼ぶ(ONLY指定のlabelはkp{rank}_{role}で別体系のため設定しない)
    try:
        with cl.logging_context("tru_ev", "tts"):
            if case.get("kp"):
                return call_x_kp(case, run_dir)
            if lv == "a2":
                return xr.generate_family_x_a2_segments(run_dir, japanese_title="コーヒー豆の値下がり", tts_backend=TTS_BACKEND, style_profile=STYLE_PROFILE)
            return xr.generate_family_x_b1_segments(run_dir, tts_backend=TTS_BACKEND, style_profile=STYLE_PROFILE)
    finally:
        xr._ONLY_SEGMENTS = None


def call_x_kp(case, run_dir, scope_fam="X"):
    """X KP: 正式のKP生成closure(_kp_english_generate_fn / generate_key_phrase_explanation_en_verified)を
    正式のcache/guard関数(_generate_or_reuse_kp)経由・X scope内で呼ぶ。"""
    import er019_family_x_audio_production_runner_01 as xr
    import er109_xz_scope_01 as scope
    import er078_secondary_run_scope_01 as srs
    import er019_family_x_style_profile_01 as spm
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles
    import er005_cost_logger as cl
    lv = case["level"]
    nd = f"{run_dir}/{lv}/narration"
    os.makedirs(nd, exist_ok=True)
    kp = read_json(f"{run_dir}/{lv}/key_phrases/keywords_canonicalized.json")
    item = [i for i in kp["items"] if i["rank"] == 1][0]
    used_form = item["used_form"]
    results = {}

    @srs.with_secondary_run
    def _go():
        with scope.run_scope(scope_fam):
            if case["kp"] == "en":
                fn, k2 = xr._kp_english_generate_fn(STYLE_PROFILE, lv, TTS_BACKEND, used_form, f"{nd}/kp1_en.wav")
                with cl.segment_context("kp1_english"):
                    results["kp1_en"] = xr._generate_or_reuse_kp(None, 1, "english", f"{nd}/kp1_en.wav", fn, expected_text=used_form)
                results["kp1_en"]["canonical_text"] = used_form
                # 正式runner(er019_family_x_audio_production_runner_01 L1770/L2123)と同じ後処理: style_profile記録(M4/S3)。Gate観測用にdriverが同一関数で付与する。
                spm.attach_segment_profile_record(results["kp1_en"], STYLE_PROFILE, spm.ROLE_KP_EN, k2)
            elif case["kp"] == "expl":
                def _base(_r):
                    return fl_styles.KEY_PHRASE_EXPLANATION_EN if TTS_BACKEND == "speech_metadata_flash_lite" else None
                style = spm.resolve_role_style(STYLE_PROFILE, spm.ROLE_KP_EXPLANATION_EN, "b1b", _base)
                text = case["expl_text"]
                with cl.segment_context("kp1_explanation_en"):
                    results["kp1_explanation_en"] = xr._generate_or_reuse_kp(
                        None, 1, "explanation", f"{nd}/kp1_explanation_en.wav",
                        lambda: xr.generate_key_phrase_explanation_en_verified(text, f"{nd}/kp1_explanation_en.wav", style_prefix_override=style, tts_backend=TTS_BACKEND),
                        expected_text=text, require_style_version=False)
                results["kp1_explanation_en"]["explanation_text"] = text
                results["kp1_explanation_en"]["canonical_text"] = text
                spm.attach_segment_profile_record(results["kp1_explanation_en"], STYLE_PROFILE, spm.ROLE_KP_EXPLANATION_EN, style)
    @srs.with_secondary_run
    def _go_min():
        import er003_v1_repro01_main_generate as repro01
        with scope.run_scope(scope_fam):
            for r, text in enumerate(case["expl_texts"], 1):
                nm = f"kp{r}_explanation_en"
                with cl.segment_context(nm):
                    results[nm] = xr._generate_or_reuse_kp(
                        None, r, "explanation", f"{nd}/{nm}.wav",
                        lambda t=text, n=nm: xr.generate_key_phrase_explanation_en_verified(t, f"{nd}/{n}.wav", style_prefix_override=repro01.MINIMAL_INSTRUCTION_PREFIX, tts_backend=TTS_BACKEND),
                        expected_text=text, require_style_version=False)
                results[nm]["explanation_text"] = text
                results[nm]["canonical_text"] = text
    if case["kp"] == "expl_min":
        _go_min()
    else:
        _go()
    os.makedirs(f"{run_dir}/{lv}/audit", exist_ok=True)
    kps = ({str(i + 1): {"explanation": v} for i, v in enumerate(results.values())} if case["kp"] == "expl_min"
           else {"1": {("english" if case["kp"] == "en" else "explanation"): list(results.values())[0]}})
    with open(f"{run_dir}/{lv}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": {}, "key_phrases": kps, "tts_backend": TTS_BACKEND,
                   "style_version": xr.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION}, f, ensure_ascii=False, indent=2, default=str)
    return results


# ============================================================ Y
Y_SRC = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
Y_ROOT = "er121_output/family_y_production_01"


def prep_y(case, run_dir):
    lv = case["level"]
    for rel in (f"{lv}/parts.json", f"{lv}/support_texts.json"):
        _copy(f"{Y_SRC}/{rel}", f"{run_dir}/{rel}")
    if case.get("kp"):
        _copy(f"{Y_SRC}/{lv}/key_phrases/keywords_canonicalized.json", f"{run_dir}/{lv}/key_phrases/keywords_canonicalized.json")
    import er121_family_y_audio_01 as ya
    ya.style_profile_mod.resolve_run_profile(run_dir, ya.Y_APPROVED_STYLE_PROFILE, write=True, tts_backend=ya.TTS_BACKEND)


def call_y(case, run_dir):
    import er121_family_y_audio_01 as ya
    import er005_cost_logger as cl
    lv = case["level"]
    pid = ya.Y_APPROVED_STYLE_PROFILE
    with cl.logging_context("tru_ev", "tts"):
        if case.get("kp"):
            return call_x_kp(case, run_dir, scope_fam="Y")
        with ya.only_segments_scope(set(case["segments"])):
            if lv == "b1b":
                return ya.generate_y_b1_segments(run_dir, style_profile=pid, guard=None)
            return ya.generate_y_a2_segments(run_dir, "再配達の有料化", style_profile=pid, guard=None)


def gate_y(case, run_dir):
    import er121_family_y_audio_01 as ya
    lv = case["level"]
    try:
        g = ya.y_style_gate(run_dir, lv, ya.Y_APPROVED_STYLE_PROFILE)
    except BaseException as e:      # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"[:500]}
    mine = set(case["segments"]) | {f"{x}_c{i}" for x in case["segments"] for i in range(1, 12)}
    return {"status": g.get("status"), "y_profile_blocked": g.get("y_profile_blocked"),
            "my_segment_checks": [c for c in (g.get("y_body_checks") or []) if c.get("segment") in mine or c.get("name") in mine],
            "my_segment_blocked": [b for b in (g.get("y_body_blocked") or []) if b.get("segment") in mine],
            "x_gate_blocked_mine": [b for b in (g.get("x_gate_blocked_after_filter") or []) if b.get("segment") in mine],
            "note": "Gateは全Y本文segmentを対象にするため、未生成segmentのNO_SEGMENT_RECORDは本evidenceの対象外(my_*のみ参照)"}


def gate_x(case, run_dir):
    import er019_family_x_audio_production_runner_01 as xr
    import er019_family_x_style_profile_01 as spm
    lv = case["level"]
    out_dir = f"{run_dir}/{lv}"
    res = read_json(f"{out_dir}/audit/tts_generation_results.json") or {}
    try:
        g = spm.m3_assembly_gate(STYLE_PROFILE, lv, res, {})
    except BaseException as e:      # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"[:500]}
    mine = set(case["segments"])
    mine |= {f"kp1_{r}" for r in ("english", "explanation", "japanese_meaning")}
    out = {"status_all": g.get("status"), "my_segment_blocked": [b for b in (g.get("blocked") or []) if b.get("segment") in mine],
           "my_segment_warnings": [w for w in (g.get("warnings") or []) if w.get("segment") in mine],
           "note": "m3_assembly_gate(承認済みprofile)を実resultsへ適用。全体statusは未生成segmentのNO_SEGMENT_RECORDを含むため my_* のみ参照"}
    if lv == "a2" and case.get("chunk_gate"):
        try:
            out["std_chunk_slowdown_gate"] = xr._x_std_chunk_slowdown_blocked(out_dir)
        except BaseException as e:      # noqa: BLE001
            out["std_chunk_slowdown_gate"] = {"error": f"{type(e).__name__}: {e}"[:300]}
    return out


# ============================================================ Z
Z_SRC = "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01"
Z_ROOT = "er026_output/family_z_production_e2e_01/the_monkeys_paw"
Z_KEY = "the_monkeys_paw"


def _z_plan(level):
    import er063_family_z_audio_01 as z
    seg = read_json(f"{Z_SRC}/segment_plan_{level}.json")
    sup = read_json(f"{Z_SRC}/support/{level}_support.json")
    kp = read_json(f"{Z_SRC}/{level}/key_phrases/keywords_canonicalized.json")
    res = read_json(f"{Z_SRC}/{level}/audit/tts_generation_results.json")
    comments = {int(k): v for k, v in sup["comments"].items()}
    expl, jt = None, None
    if level == "b1b":
        expl = {int(r): (v.get("explanation") or {}).get("canonical_text") for r, v in res["key_phrases"].items()}
    else:
        jt = res["segments"]["japanese_title"]["canonical_text"]
    return z.build_level_plan(level, seg["clips"], sup["preview"], comments, kp["items"], "The Monkey's Paw", jt, kp_explanations=expl,
                              story_key=Z_KEY), seg


def prep_z(case, run_dir):
    lv = case["level"]
    os.makedirs(f"{run_dir}/{lv}/audit", exist_ok=True)
    import glob
    prev = sorted(glob.glob(f"{Z_ROOT}/run_tru_ev_z_*/{lv}/audit/dialogue_ctx_notes.json"))
    if prev and case.get("ctx"):      # 感情notes(LLM、level単位1 call)は同一本文なら再利用(費用節約。Z生成の既存仕様どおり保存済みnotesは再利用)
        shutil.copyfile(prev[0], f"{run_dir}/{lv}/audit/dialogue_ctx_notes.json")


def call_z(case, run_dir):
    import er063_family_z_audio_01 as z
    import er005_cost_logger as cl
    lv = case["level"]
    plan, _seg = _z_plan(lv)
    targets = set(case["segments"])
    if case.get("plan_subset", True) and not case.get("ctx"):
        plan = [s for s in plan if s.clip_id in targets]
    with cl.logging_context("tru_ev", "tts"):
        return z.run_tts_stage(run_dir, lv, plan, only_clips=targets, story_key=Z_KEY)


def gate_z(case, run_dir):
    import er063_family_z_audio_01 as z
    lv = case["level"]
    plan, _ = _z_plan(lv)
    sub = [s for s in plan if s.clip_id in set(case["segments"])]
    out = {}
    try:
        out["m2_complete"] = z.assert_tts_results_complete(f"{run_dir}/{lv}", [s.clip_id for s in sub])
    except BaseException as e:      # noqa: BLE001
        out["m2_complete"] = {"BLOCK": f"{type(e).__name__}: {str(e)[:400]}"}
    try:
        out["audio_gate"] = z.run_audio_gate(run_dir, lv, sub, [], article_text="", skip_shared_gate=True)
        out["audio_gate"] = {k: out["audio_gate"].get(k) for k in ("m2_complete", "shared_gate", "audio_text_deviation_clips")}
    except BaseException as e:      # noqa: BLE001
        out["audio_gate"] = {"BLOCK": f"{type(e).__name__}: {str(e)[:400]}"}
    return out


FAMILY_ADAPTERS = {"X": (prep_x, call_x, gate_x), "Y": (prep_y, call_y, gate_y), "Z": (prep_z, call_z, gate_z)}


def gather(case, run_dir, rec, plan, ledger_dir, started, ended, exc_info, ret):
    lv = case["level"]
    level_dir = f"{run_dir}/{lv}"
    ev = {"management_id": core.MANAGEMENT_ID, "case": case["id"], "family": case["family"], "level": lv, "scenario": case["scenario"],
          "leaf": case.get("leaf"), "policy": case.get("policy"), "segments": case["segments"], "run_dir": run_dir,
          "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"), "tts_backend": TTS_BACKEND, "style_profile": STYLE_PROFILE,
          "injection_plan": plan.as_json(), "injected_overrides": rec.overrides, "injected_override_count": len(rec.overrides),
          "started_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(started)), "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ended)),
          "wall_seconds": round(ended - started, 1), "pid": os.getpid()}
    ev["exception"] = exc_info
    ev["tts_attempts"] = rec.tts_resolve
    ev["tts_attempts_count"] = len(rec.tts_resolve)
    ev["tts_api_calls"] = rec.tts_api
    ev["judges"] = rec.judges
    ev["post_slowdown_judges"] = rec.post_judges
    ev["cooldown_events"] = rec.cooldowns
    ev["cooldown_count"] = len(rec.cooldowns)
    ev["sleep_total_seconds"] = round(rec.sleep_total, 1)
    ev["stop_checks"] = rec.stop_checks
    ev["lr_calls"] = rec.lr_calls
    ev["lr_count"] = len(rec.lr_calls)
    hrq = read_jsonl(f"{ledger_dir}/human_review_queue.jsonl") + read_jsonl(f"{ledger_dir}/human_review_queue_ja.jsonl")
    ev["hrq_rows"] = len(hrq)
    ev["hrq_detail"] = [{"canonical_text": r.get("canonical_text"), "wav_path": r.get("wav_path"), "final_status": r.get("final_status"),
                         "lock_canonical_text": r.get("lock_canonical_text")} for r in hrq]
    hist = read_jsonl(f"{ledger_dir}/attempt_history.jsonl")
    ev["attempt_history_actions"] = [h.get("action") for h in hist]
    ev["lock_state"] = read_json(f"{level_dir}/audit/review_lock_state.json")
    prog_dir = f"{level_dir}/audit/tts_block_progress"
    ev["block_progress"] = {fn: read_json(os.path.join(prog_dir, fn)) for fn in os.listdir(prog_dir)} if os.path.isdir(prog_dir) else {}
    res = read_json(f"{level_dir}/audit/tts_generation_results.json") or {}
    mine = set(case["segments"])
    ev["results_segments"] = {k: _slim(v) for k, v in (res.get("segments") or {}).items()
                              if isinstance(v, dict) and v.get("status") is not None and (k in mine or any(k.startswith(m + "_") for m in mine))}
    ev["results_key_phrases"] = {rk: {role: _slim(v) for role, v in (rv or {}).items() if isinstance(v, dict) and v.get("status") is not None}
                                 for rk, rv in (res.get("key_phrases") or {}).items()}
    ev["attempt_sidecars"] = collect_sidecars(level_dir)
    ev["asr_routing"] = _asr_routing()
    ev["cost"] = core.cost_of(f"{run_dir}/raw_usage_log.jsonl")
    if not case.get("kp"):
        ev["results_key_phrases"] = {}      # ONLY指定のため非対象(0 API。gloss整合STOP表示は対象外の無関係entry)
    return ev


def _asr_routing():
    try:
        import er006_asr_provider_routing_01 as routing
        return {"primary": routing.ASR_ROUTING}
    except Exception as e:      # noqa: BLE001
        return {"error": str(e)}


def collect_sidecars(level_dir):
    """attemptごとのsidecar(TTS 1回ごとのmodel/voice/Style/判定/ASR step)。TTSの実送信内容の一次証跡。"""
    out = []
    nd = f"{level_dir}/narration"
    for root, _d, files in os.walk(nd):
        if os.path.basename(root) != "attempts":
            continue
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            j = read_json(os.path.join(root, fn)) or {}
            it = j.get("instruction_text") or ""
            steps = j.get("cascade_steps") or []
            out.append({"file": fn, "segment_id": j.get("segment_id"), "attempt_number": j.get("attempt_number"), "route": j.get("route"),
                        "saved_at": j.get("saved_at"), "loop_attempt_index": j.get("loop_attempt_index"), "max_attempts": j.get("max_attempts"),
                        "model": j.get("model"), "voice": j.get("voice"), "tts_backend": j.get("tts_backend"),
                        "tts_execution_mode": j.get("tts_execution_mode"), "instruction_head": it[:140], "instruction_sha": core.sha8(it),
                        "instruction_chars": len(it), "verified": j.get("verified"), "audio_classification": j.get("audio_classification"),
                        "asr_text": j.get("asr_text"), "disfluency_checked": j.get("disfluency_checked"),
                        "cascade_providers": [(st.get("step"), st.get("provider"), st.get("classification")) for st in steps if isinstance(st, dict)],
                        "slowdown": {k: j.get(k) for k in j if "slow" in k.lower() or "speed" in k.lower()}})
    return out


def _slim(v):
    keep = ("status", "reason", "fallback_used", "instruction_type", "voice", "model", "tts_model_id", "style_prefix", "asr_verified", "asr_text",
            "canonical_text", "slowdown_applied", "local_rewrite_recovery", "cooldown_events", "path", "script_version", "audio_text_deviation")
    out = {k: v.get(k) for k in keep if k in v}
    if "local_rewrite_recovery" in out and isinstance(out["local_rewrite_recovery"], dict):
        lrr = out["local_rewrite_recovery"]
        out["local_rewrite_recovery"] = {k: lrr.get(k) for k in ("status", "segment_id") if k in lrr}
    if isinstance(out.get("style_prefix"), str):
        out["style_prefix_sha"] = core.sha8(out["style_prefix"])
        out["style_prefix"] = out["style_prefix"][:160]
    for lg in ("attempts_log", "standard_attempts_log", "fallback_attempts_log", "minimal_attempts_log", "english_lock_attempts_log"):
        rows = v.get(lg)
        if isinstance(rows, list):
            out[lg] = [{k: r.get(k) for k in ("attempt", "status", "verified", "instruction_type", "asr_text", "audio_classification", "disfluency_checked",
                                              "tts_mode", "carried_from_prior_process", "post_slowdown_ng") if isinstance(r, dict) and k in r}
                       for r in rows]
    return out


def run_case(case, *, budget_left, args):
    fam = case["family"]
    prep, call, gate = FAMILY_ADAPTERS[fam]
    cid = case["id"].lower().replace("-", "_")
    pre = f"{case['theme_prefix']}__" if case.get("theme_prefix") else ""
    run_dir = f"{case['root']}/{pre}run_tru_ev_{cid}"
    plan = case["plan"]
    resume = bool(args.resume)
    if os.path.exists(run_dir) != resume:
        raise RuntimeError(f"run dir exists={os.path.exists(run_dir)} but resume={resume} (新run dirで実行/resumeは既存dirを再利用): {run_dir}")
    os.makedirs(run_dir, exist_ok=True)
    rc = core.stop_scope_check(run_dir, f"{EVD}/stop_check_{fam.lower()}_{cid}{'_resume' if resume else ''}.json")
    if rc == 3:
        return {"case": case["id"], "stopped_by_scope_check": True, "rc": 3}
    if args.dry:
        return {"case": case["id"], "dry": True, "run_dir": run_dir}
    if not resume:
        prep(case, run_dir)
    import er005_cost_logger as cl
    cl.install(f"{run_dir}/raw_usage_log.jsonl")
    ledger_dir = f"{run_dir}/_evidence_ledgers"
    rec = Recorder()
    started = time.time()
    exc_info, ret, gate_ev = None, None, None
    with open(f"{run_dir}/_driver_pid.json", "a", encoding="utf-8") as f:
        f.write(json.dumps({"pid": os.getpid(), "case": case["id"], "resume": resume, "kill_in_cooldown": args.kill_in_cooldown,
                            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
    with core.installed(plan, rec, ledger_dir, cost_log=f"{run_dir}/raw_usage_log.jsonl"):
        if case.get("stop_in_cooldown"):
            _install_stop_sentinel(rec, run_dir, case["stop_in_cooldown"])
        kill = args.kill_in_cooldown or (None if resume else case.get("kill_in_cooldown"))
        if kill:
            _install_self_kill(rec, case, run_dir, plan, ledger_dir, started, kill)
        try:
            ret = call(case, run_dir)
        except BaseException as e:      # noqa: BLE001  (TtsBlockStopError等もevidenceに残す)
            exc_info = {"type": type(e).__name__, "message": str(e)[:600], "trace_tail": traceback.format_exc()[-1500:]}
        try:
            gate_ev = gate(case, run_dir)
        except BaseException as e:      # noqa: BLE001
            gate_ev = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    ended = time.time()
    ev = gather(case, run_dir, rec, plan, ledger_dir, started, ended, exc_info, ret)
    ev["gate_observation"] = gate_ev
    ev["resumed_run"] = resume
    if case["scenario"] == "E-N":
        assert ev["injected_override_count"] == 0, "E-Nで上書きが発生した"
    out = f"{EVIDENCE_RUNS}/{case['id']}{'.resume' if resume else ''}.json"
    os.makedirs(EVIDENCE_RUNS, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1, default=str)
    return ev


def _install_stop_sentinel(rec, run_dir, threshold):
    """E-STOP: 累積cooldown待機がthreshold秒に達したら、**run専用のSTOP sentinel**(<run>/STOP。Y/Zのrunnerが待機中に5秒刻みで確認する正式のsentinel)を作る。
    全run共通のSTOP_ALLは作らない(並行agentを止めるため)。作ったsentinelは削除しない(このrun dirは再利用しない証跡専用)。"""
    import er127_tts_block_policy_01 as er127
    prev = er127.RUNTIME.sleep
    done = {"v": False}

    def sleep(sec):
        prev(sec)
        if not done["v"] and rec.sleep_total >= threshold:
            done["v"] = True
            with open(f"{run_dir}/STOP", "w", encoding="utf-8") as f:
                f.write("evidence driver STOP test (TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 delegation_03) " + time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
            rec.events.append({"event": "STOP_SENTINEL_CREATED", "at_sleep_total": rec.sleep_total, "t": time.time()})
    er127.RUNTIME.sleep = staticmethod(sleep)


def _install_self_kill(rec, case, run_dir, plan, ledger_dir, started, threshold):
    """E-S6: 累積cooldown待機が threshold 秒に達したら**自process**を os._exit(137)(SIGKILL相当)。他processには触れない(26-6)。
    終了前に部分evidenceを書く。起動側は同一argsで --resume 付きで1回だけ再開する(手動。監督ループ/自動再試行ラッパなし)。"""
    import er127_tts_block_policy_01 as er127
    prev = er127.RUNTIME.sleep

    def sleep(sec):
        prev(sec)
        if rec.sleep_total >= threshold:
            part = {"case": case["id"], "partial_before_self_terminate": True, "pid": os.getpid(), "sleep_total_seconds": rec.sleep_total,
                    "tts_attempts": rec.tts_resolve, "cooldowns_so_far": rec.cooldowns, "overrides": rec.overrides, "judges": rec.judges,
                    "terminated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "cost": core.cost_of(f"{run_dir}/raw_usage_log.jsonl"),
                    "block_progress_at_kill": {fn: read_json(os.path.join(f"{run_dir}/{case['level']}/audit/tts_block_progress", fn))
                                               for fn in (os.listdir(f"{run_dir}/{case['level']}/audit/tts_block_progress")
                                                          if os.path.isdir(f"{run_dir}/{case['level']}/audit/tts_block_progress") else [])}}
            os.makedirs(EVIDENCE_RUNS, exist_ok=True)
            with open(f"{EVIDENCE_RUNS}/{case['id']}.partial_before_kill.json", "w", encoding="utf-8") as f:
                json.dump(part, f, ensure_ascii=False, indent=1, default=str)
            print(f"[SELF-KILL] {case['id']} pid={os.getpid()} sleep_total={rec.sleep_total}", flush=True)
            os._exit(137)
    er127.RUNTIME.sleep = staticmethod(sleep)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", required=True, help="X-Std / X-Adv / Y-Std / Y-Adv / Z-Std / Z-Adv")
    ap.add_argument("--budget-jpy", type=float, required=True)
    ap.add_argument("--tts-execution-mode", required=True)
    ap.add_argument("--only", default=None)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--resume", action="store_true", help="E-S6: kill後の同一args再開(既存run dirを再利用。1回だけ手動で実行)")
    ap.add_argument("--kill-in-cooldown", type=float, default=None, help="E-S6: 累積cooldown待機がS秒に達したら自processをos._exit(137)")
    args = ap.parse_args(argv)
    if args.tts_execution_mode != "STANDARD" or os.environ.get("TTS_EXECUTION_MODE") != "STANDARD":
        print("[STOP] TTS_EXECUTION_MODE=STANDARD を環境変数とCLI引数の両方で明示してください(T-2)", file=sys.stderr)
        return 2
    import tru_ev_cases_01 as cases
    todo = [c for c in cases.CASES if c["group"] == args.group]
    if args.only:
        sel = set(args.only.split(","))
        todo = [c for c in todo if c["id"] in sel]
    spent = 0.0
    summary = []
    for c in todo:
        if spent >= args.budget_jpy:
            print(f"[BUDGET] group cap {args.budget_jpy} reached (spent {spent:.2f}); remaining cases not started: {[x['id'] for x in todo[len(summary):]]}")
            break
        print(f"[CASE] {c['id']} start {time.strftime('%H:%M:%S')}", flush=True)
        ev = run_case(c, budget_left=args.budget_jpy - spent, args=args)
        j = (ev.get("cost") or {}).get("jpy") or 0.0
        spent += float(j)
        print(f"[CASE] {c['id']} done tts={ev.get('tts_attempts_count')} cd={ev.get('cooldown_count')} lr={ev.get('lr_count')} hrq={ev.get('hrq_rows')} "
              f"jpy={j} exc={(ev.get('exception') or {}).get('type')} spent={spent:.2f}", flush=True)
        summary.append({"case": c["id"], "jpy": j, "exc": (ev.get("exception") or {}).get("type")})
    print(json.dumps({"group": args.group, "spent_jpy": round(spent, 3), "cases": summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
