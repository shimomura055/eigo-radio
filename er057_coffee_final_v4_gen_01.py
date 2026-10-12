# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-P8-FINAL-AUDIO 委任_01A Trial専用(Production非経由、v3と同一経路)。
Full Story Part1-3 x Std/Adv をP8(Aoede Style Trial-03、逐語sha照合)で再生成。Std は生成後 apply_a2_slowdown(6%)。
ASR=Primary -> 非verifiedならSecondary cascade(Production承認済み)。最大3 attempt/clip。HR到達は採択しない。"""
import os, sys, json, time, shutil, threading, concurrent.futures as cf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
OUT = os.path.join(ROOT, "er057_output", "coffee_final_v4")
ATT, SEG = os.path.join(OUT, "attempts"), os.path.join(OUT, "segments")
GENLOG = os.path.join(OUT, "generation_log_v4.jsonl")
BUDGET = 28.0
_lk = threading.Lock(); _spent = {"jpy": 0.0}
V3 = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")


def log(rec):
    with _lk:
        open(GENLOG, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_p8():
    md = open(os.path.join(ROOT, "er057_output", "aoede_style_trial_03", "prompts", "prompts_aoede_style_03.md"), encoding="utf-8").read()
    i = md.index("## P8 ")
    blk = md[i:].split("```")[1].strip()
    import er057_aoede_style_trial_03_gen as G
    assert G.style_of("P8") == blk
    return blk


def v3_sha_map():
    m = {}
    for l in open(os.path.join(V3, "generation_log_v3_01.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r.get("tts_input_sha256"): m[r["job"]] = r["tts_input_sha256"]
    for l in open(os.path.join(ROOT, "er057_output", "pace_trial_02", "generation_log_02.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r.get("cand") == "PD8" and r.get("tts_input_sha256"): m[r["part"]] = r["tts_input_sha256"]
    return m


def jobs():
    p8 = load_p8(); sm = v3_sha_map(); J = []
    for j in B.jobs_def():
        assert B.sha_text(j["tts_input"]) == sm[j["id"]], ("canonical mismatch", j["id"])
        j.update(style=p8, slow=(j["level"] == "std"))
        J.append(j)
    return J


def cascade(j, rec, wav):
    import er006_secondary_asr_01 as sec
    import soundfile as sf
    d = sec.evaluate_attempt_with_cascade_detail(j["tts_input"], rec["asr_text"], [], wav, language="en-US", ledger_phrases=None,
        cascade_enabled=True, enable_connected_speech_equivalence_layer=True, segment_id=j["role"])
    az = sum(1 for s in d["steps"] if s.get("provider") == "azure")
    cost = az * sf.info(wav).duration * 0.0003 * 160
    with _lk: _spent["jpy"] += cost
    return {"verified": bool(d["verified"]), "final_status": d["final_status"], "cascade_invoked": d["cascade_invoked"],
            "human_review_required": bool(d["human_review_required"]), "azure_calls": az, "azure_cost_jpy_est": round(cost, 3),
            "steps": [{k: v for k, v in s.items() if k in ("step", "provider", "text", "classification", "sub_reason")} for s in d["steps"]]}


def run_job(j, call):
    import er002_common as common, er003_b1_p3u_audio as p3u, er003_audio_tts_asr_safety as safety, er008_a2_postprocess_slowdown_01 as slowdown
    final = None; hr = False; hist = []
    for attempt in range(1, 4):
        if _spent["jpy"] > BUDGET:
            log({"job": j["id"], "event": "BUDGET_STOP"}); return {"id": j["id"], "status": "BUDGET_STOP"}
        t0 = time.time(); samples = usage = None
        for tech in (1, 2):
            try: samples, usage = call(j["tts_input"], j["style"], B.VOICE); break
            except Exception as e: log({"job": j["id"], "attempt": attempt, "tech_try": tech, "event": "TTS_TECH_FAILURE", "error": f"{type(e).__name__}: {str(e)[:200]}"})
        if samples is None: continue
        tts_jpy = ((usage["input_tokens"] or 0) * B.PRICE_IN + (usage["output_tokens"] or 0) * B.PRICE_OUT) / 1e6 * B.USD_JPY
        with _lk: _spent["jpy"] += tts_jpy
        trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": j["id"], "level": j["level"], "role": j["role"], "attempt": attempt,
               "style_name": "P8", "model_requested": B.MODEL, "model_version": usage["model_version"], "voice": B.VOICE, "tts_backend": B.BACKEND,
               "execution_mode": "STANDARD(sync, DEV Trial)", "style_sha256": B.sha_text(j["style"]), "style_text": j["style"],
               "tts_input_sha256": B.sha_text(j["tts_input"]), "manuscript_sha256": B.sha_text(j["manuscript"]),
               "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"], "tts_cost_jpy": round(tts_jpy, 4), "elapsed_s": round(time.time() - t0, 1)}
        if trimmed is None:
            rec.update(status="NO_SPEECH", verified=False); log(rec); continue
        anomaly = safety.detect_duration_anomaly(ti["raw_duration_seconds"], j["tts_input"], "en")
        wav = os.path.join(ATT, f"{j['id']}_a{attempt}.wav")
        common.write_wav_float(wav, trimmed, common.SAMPLE_RATE, 1)
        rec.update(wav=os.path.relpath(wav, ROOT).replace("\\", "/"), wav_sha256=B.sha_file(wav), raw_duration_s=ti["raw_duration_seconds"],
                   trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3), duration_anomaly=anomaly)
        if anomaly["is_anomaly"]:
            rec.update(status="DURATION_ANOMALY", verified=False); log(rec); continue
        a = B.asr_and_judge(wav, j["tts_input"], j["role"])
        with _lk: _spent["jpy"] += a["asr_cost_jpy_est"]
        rec.update(status="OK", asr_model=B.ASR_MODEL, **a)
        if not a["verified"] and a["asr_text"]:
            c = cascade(j, rec, wav); rec["secondary_cascade"] = c
            if c["human_review_required"]: hr = True
            if c["verified"]: rec["verified_by"] = "secondary_cascade"; rec["verified"] = True
        else:
            rec["verified_by"] = "primary"
        log(rec); hist.append({k: rec.get(k) for k in ("attempt", "classification", "verified", "verified_by")})
        if rec["verified"]:
            final = (attempt, wav, rec); break
        if hr:
            log({"job": j["id"], "event": "HUMAN_REVIEW_REACHED", "attempt": attempt}); break
    if final is None:
        return {"id": j["id"], "status": "HR_REACHED" if hr else "ASR_NG_STOP", "history": hist}
    attempt, wav, rec = final
    out = os.path.join(SEG, f"{j['id']}_raw.wav"); shutil.copyfile(wav, out)
    res = {"id": j["id"], "status": "OK", "attempt": attempt, "regen_count": attempt - 1, "classification": rec["classification"], "verified_by": rec.get("verified_by"),
           "raw_wav": out, "raw_sha256": B.sha_file(out), "raw_duration_s": rec["trimmed_duration_s"], "history": hist}
    if j["slow"]:
        slow = os.path.join(SEG, f"{j['id']}_slow6.wav")
        info = slowdown.apply_a2_slowdown(out, slow)
        a2 = B.asr_and_judge(slow, j["tts_input"], j["role"])
        with _lk: _spent["jpy"] += a2["asr_cost_jpy_est"]
        info2 = {k: info[k] for k in ("slowdown_pct_target", "slowdown_pct_actual", "src_duration_seconds", "dst_duration_seconds")}
        info2["ratio"] = round(info["dst_duration_seconds"] / info["src_duration_seconds"], 4)
        res.update(slow_wav=slow, slow_sha256=B.sha_file(slow), slowdown=info2, slow_asr={k: a2[k] for k in ("asr_text", "classification", "verified", "length_ok")})
        log({"job": j["id"], "event": "SLOWDOWN_APPLIED", **info2, "slow_sha256": res["slow_sha256"], "post_slowdown_primary_asr": res["slow_asr"], "note": "参考記録"})
    return res


def main():
    os.makedirs(ATT, exist_ok=True); os.makedirs(SEG, exist_ok=True)
    B.patch_validator_telemetry()
    import er006_secondary_asr_01 as sec
    sec._resolve_unresolved_entity_for_review = lambda span: None
    import er005_cost_logger as cl
    cl.init_logger(os.path.join(OUT, "cost_log_secondary_v4.jsonl"))
    J = jobs(); only = sys.argv[1:]
    if only: J = [j for j in J if j["id"] in only]
    print([j["id"] for j in J], flush=True)
    call = B.make_tts_call(); t0 = time.time()
    with cf.ThreadPoolExecutor(6) as ex: results = list(ex.map(lambda j: run_job(j, call), J))
    summ = {"model_requested": B.MODEL, "voice": B.VOICE, "style": "P8", "results": results, "spent_jpy_est": round(_spent["jpy"], 3), "elapsed_s": round(time.time() - t0, 1)}
    name = "gen_summary_v4" + ("_" + "_".join(only) if only else "") + ".json"
    json.dump(summ, open(os.path.join(OUT, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for r in results: print(json.dumps(r, ensure_ascii=False, default=str)[:400])
    print("spent", summ["spent_jpy_est"], summ["elapsed_s"])


if __name__ == "__main__": main()
