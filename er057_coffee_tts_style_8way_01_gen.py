# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-8WAY-AB-TRIAL-01 委任_02 Trial専用gen(Production非経由)。
8候補x2take x Std/Adv Part1=32 call、1回起動で完了。再生成なし(技術failure retryは合計4まで)。予算JPY60でハードストップ。"""
import os, sys, json, time, hashlib, shutil, concurrent.futures as cf, threading
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_8way_01"); ATT = os.path.join(OUT, "attempts")
GENLOG = os.path.join(OUT, "generation_log_02.jsonl")
BUDGET = 60.0; MAX_RETRY = 4
_l = threading.Lock(); _retries = {"n": 0}
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
def append(rec):
    with _l: open(GENLOG, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
P = json.load(open(os.path.join(OUT, "prompts_8way_01.json"), encoding="utf-8"))
CANDS = {k: v["style"] for k, v in P["candidates"].items()}
for k, v in P["candidates"].items(): assert sha(v["style"]) == v["sha256"], k
REF = json.load(open(os.path.join(ROOT, "er057_output", "coffee_v5_pause_01", "tts_input_texts.json"), encoding="utf-8"))

def run(task, call):
    import er002_common as common, er003_b1_p3u_audio as p3u, er003_audio_tts_asr_safety as safety
    import er008_a2_postprocess_slowdown_01 as slowdown
    cand, job, take = task; jid = f"{cand}_{job['id']}_t{take}"; style = CANDS[cand]
    if STOP_FLAG["stop"] or os.path.exists(os.path.join(OUT, "STOP")):
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
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": jid, "cand": cand, "level": job["level"], "take": take, "model_requested": B.MODEL,
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
    a = B.asr_and_judge(raw, job["tts_input"], job["id"])   # 減速前Primary ASR 1回のみ(Stdも減速前)
    with B._lock: B._spent["jpy"] += a["asr_cost_jpy_est"]
    rec.update(status="OK", asr_model=B.ASR_MODEL, asr_target="pre_slowdown_raw", **a)
    append(rec)
    return {"id": jid, "status": "OK", "verified": a["verified"], "cls": a["classification"], "dur": rec["trimmed_duration_s"], "tts_jpy": rec["tts_cost_jpy"]}
STOP_FLAG = {"stop": False}

def main():
    os.makedirs(ATT, exist_ok=True)
    B.patch_validator_telemetry()
    jobs = [j for j in B.jobs_def() if j["id"] in ("std_part1", "adv_part1")]
    assert len(jobs) == 2
    for j in jobs:
        assert j["tts_input"] == REF[j["id"]]["text"], j["id"]
    print("tts_input matches v5:", [(j["id"], sha(j["tts_input"])[:12]) for j in jobs], flush=True)
    call = B.make_tts_call(); t0 = time.time()
    tasks = [(c, j, t) for c in CANDS for j in jobs for t in (1, 2)]
    assert len(tasks) == 32
    with cf.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda t: run(t, call), tasks))
    summ = {"results": results, "spent_jpy_est": round(B._spent["jpy"], 3), "retries_used": _retries["n"], "elapsed_s": round(time.time() - t0, 1),
            "validator_telemetry_redirected": len(B._sem_telemetry)}
    json.dump(summ, open(os.path.join(OUT, "gen_summary_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in results: print(r)
    print("spent", summ["spent_jpy_est"], "elapsed", summ["elapsed_s"])
if __name__ == "__main__": main()
