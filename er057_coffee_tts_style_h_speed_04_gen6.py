# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04 委任_03 Round6 listen: K06 Std Take3 + K01 Adv Take3 = 2 call (hard stop JPY8). Trial専用、Production非経由。技術retry合計2まで、監督ループなし。"""
import os, sys, json, time, hashlib, concurrent.futures as cf, threading
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round6_listen"); ATT = os.path.join(OUT, "attempts")
PREV = os.path.join(ROOT, "er057_output", "coffee_tts_style_8way_01")
STOPALL = os.path.join(ROOT, "er026_output", "family_z_production_e2e_01", "STOP_ALL")
GENLOG = os.path.join(OUT, "generation_log_r6.jsonl")
STEP = "R6"
BUDGET = 8.0; MAX_RETRY = 2
_l = threading.Lock(); _retries = {"n": 0}
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
def append(rec):
    with _l: open(GENLOG, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
P2 = json.load(open(os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03", "round2", "prompts_r2.json"), encoding="utf-8"))
CANDS = {}
for k in ("K01", "K06"):
    assert sha(P2["candidates"][k]["style"]) == P2["candidates"][k]["sha256"], k
    CANDS[k] = P2["candidates"][k]["style"]
assert CANDS["K06"].startswith("A warm storyteller") and CANDS["K01"].startswith("A gentle storyteller")
REF = json.load(open(os.path.join(ROOT, "er057_output", "coffee_v5_pause_01", "tts_input_texts.json"), encoding="utf-8"))
STOP_FLAG = {"stop": False}

def stop_present():
    import glob
    return (os.path.exists(os.path.join(OUT, "STOP")) or os.path.exists(os.path.join(OUT, "..", "STOP")) or os.path.exists(STOPALL)
            or os.path.exists(os.path.join(OUT, "..", "round5", "STOP")) or bool(glob.glob(os.path.join(ROOT, "docs", "pm", "delegation_log", "*COFFEE-TTS-STYLE-H-SPEED-TRIAL-04*STOP*"))))

def run(task, call):
    import er002_common as common, er003_b1_p3u_audio as p3u, er003_audio_tts_asr_safety as safety
    import er008_a2_postprocess_slowdown_01 as slowdown
    cand, job, take = task; jid = f"{cand}_{job['id']}_t{take}"; style = CANDS[cand]
    if STOP_FLAG["stop"] or stop_present():
        STOP_FLAG["stop"] = True; return {"id": jid, "status": "STOP"}
    if B._spent["jpy"] > BUDGET:
        append({"job": jid, "event": "BUDGET_STOP"}); return {"id": jid, "status": "BUDGET_STOP"}
    t0 = time.time(); samples = usage = None
    for tech in (1, 2):
        try:
            samples, usage = call(job["tts_input"], style, B.VOICE); break
        except Exception as e:
            append({"job": jid, "tech_try": tech, "event": "TTS_TECH_FAILURE", "error": f"{type(e).__name__}: {str(e)[:200]}"})
            with _l:
                _retries["n"] += 1; ok = _retries["n"] <= MAX_RETRY
            if not ok: break
    if samples is None: return {"id": jid, "status": "TECH_FAIL"}
    tts_jpy = ((usage["input_tokens"] or 0) * B.PRICE_IN + (usage["output_tokens"] or 0) * B.PRICE_OUT) / 1e6 * B.USD_JPY
    with B._lock: B._spent["jpy"] += tts_jpy
    trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "step": STEP, "job": jid, "cand": cand, "level": job["level"], "take": take, "model_requested": B.MODEL,
           "model_version": usage["model_version"], "voice": B.VOICE, "tts_backend": B.BACKEND, "execution_mode": "STANDARD(sync, DEV Trial)",
           "style_sha256": sha(style), "tts_input_sha256": sha(job["tts_input"]), "manuscript_sha256": sha(job["manuscript"]),
           "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"], "tts_cost_jpy": round(tts_jpy, 4), "elapsed_s": round(time.time() - t0, 1)}
    if trimmed is None:
        rec.update(status="NO_SPEECH"); append(rec); return {"id": jid, "status": "NO_SPEECH"}
    raw = os.path.join(ATT, f"{jid}_raw.wav"); common.write_wav_float(raw, trimmed, common.SAMPLE_RATE, 1)
    final = raw
    rec.update(raw_wav=os.path.relpath(raw, ROOT).replace("\\", "/"), raw_sha256=B.sha_file(raw), raw_duration_s=ti["raw_duration_seconds"],
               trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3),
               duration_anomaly=safety.detect_duration_anomaly(ti["raw_duration_seconds"], job["tts_input"], "en"))
    if job["level"] == "std":
        final = os.path.join(ATT, f"{jid}_slow6.wav")
        info = slowdown.apply_a2_slowdown(raw, final)
        rec["slowdown"] = {k: info[k] for k in ("slowdown_pct_target", "slowdown_pct_actual", "src_duration_seconds", "dst_duration_seconds")}
    rec.update(final_wav=os.path.relpath(final, ROOT).replace("\\", "/"), final_sha256=B.sha_file(final))
    a = B.asr_and_judge(raw, job["tts_input"], job["id"])
    with B._lock: B._spent["jpy"] += a["asr_cost_jpy_est"]
    rec.update(status="OK", asr_model=B.ASR_MODEL, asr_target="pre_slowdown_raw", **a)
    append(rec)
    return {"id": jid, "status": "OK", "verified": a["verified"], "cls": a["classification"], "dur": rec["trimmed_duration_s"], "tts_jpy": rec["tts_cost_jpy"]}

def main():
    os.makedirs(ATT, exist_ok=True)
    assert not stop_present(), "STOP present"
    B.patch_validator_telemetry()
    jobs = [j for j in B.jobs_def() if j["id"] in ("std_part1", "adv_part1")]
    assert len(jobs) == 2
    prev_in = {}
    for l in open(os.path.join(PREV, "generation_log_02.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r.get("status") == "OK": prev_in[r["level"]] = r["tts_input_sha256"]
    for j in jobs:
        assert j["tts_input"] == REF[j["id"]]["text"], j["id"]
        assert sha(j["tts_input"]) == prev_in[j["level"]], "tts_input sha != 8way"
    print("tts_input matches v5/8way:", [(j["id"], sha(j["tts_input"])[:12]) for j in jobs], flush=True)
    byid = {j["id"]: j for j in jobs}
    tasks = [("K06", byid["std_part1"], 3), ("K01", byid["adv_part1"], 3)]; assert len(tasks) == 2
    call = B.make_tts_call(); t0 = time.time()
    with cf.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda t: run(t, call), tasks))
    summ = {"step": STEP, "results": results, "spent_jpy_est": round(B._spent["jpy"], 3), "retries_used": _retries["n"], "elapsed_s": round(time.time() - t0, 1),
            "validator_telemetry_redirected": len(B._sem_telemetry)}
    json.dump(summ, open(os.path.join(OUT, f"gen_summary_r6.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in results: print(r)
    print("spent", summ["spent_jpy_est"], "elapsed", summ["elapsed_s"])
if __name__ == "__main__": main()
