# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 Trial専用生成(Production非経由)。
Std Full Story part1-3 = PD8(逐語、sha照合)+6%減速、Std/Adv In One Line(新原稿、現行Style踏襲)。
委任_03の run_job と同一ロジック(trim/duration anomaly/Primary ASR+validator/NG時同一Promptで最大2回再生成/技術失敗のみretry)。"""
import os, sys, json, time, shutil, hashlib, threading, concurrent.futures as cf
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
OUT = os.path.join(ROOT, "er057_output", "coffee_final_audio_assembly_01")
ATT, SEG = os.path.join(OUT, "attempts"), os.path.join(OUT, "segments")
GENLOG = os.path.join(OUT, "generation_log_v3_01.jsonl")
BUDGET = 45.0
PD8_SHA = "329ff46a5ec3877f7dc23375e14ee8a806efeff7cfe27963492a3cf95d182226"
_lk = threading.Lock(); _spent = {"jpy": 0.0}


def log(rec):
    with _lk:
        with open(GENLOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_pd8():
    md = open(os.path.join(ROOT, "er057_output", "pace_trial_02", "prompts", "prompts_pace_02.md"), encoding="utf-8").read()
    blk = md[md.index("## PD8 "):].split("```")[1].strip()
    assert B.sha_text(blk) == PD8_SHA, B.sha_text(blk)
    import er057_pace_trial_02_gen as P
    assert P.CANDS["PD8"][1] == blk
    return blk


def iol_styles():
    r = json.load(open(f"{B.TONE}/a2/audit/tts_generation_results.json", encoding="utf-8"))["segments"]["in_one_line"]
    import er033_tts_flash_lite_family_x_styles_01 as fl
    base = fl.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"]
    std = r["style_prefix"]
    assert std.startswith(base)
    r2 = json.load(open(f"{B.TONE}/b1b/audit/tts_generation_results.json", encoding="utf-8"))["segments"]["in_one_line"]
    assert r2["style_prefix"] == base
    return std, base


def jobs():
    import er003_v1_n3_01_tts_generate as n3
    pd8 = load_pd8()
    std_iol, adv_iol = iol_styles()
    iol = json.load(open(os.path.join(OUT, "iol_final_text_01.json"), encoding="utf-8"))
    J = []
    parts = json.load(open(f"{B.TONE}/a2/parts.json", encoding="utf-8"))
    for n in (1, 2, 3):
        raw = parts[f"part{n}"]
        J.append({"id": f"std_part{n}", "level": "std", "role": f"full_story_part{n}", "manuscript": raw, "tts_input": n3.tts_safe_news_en(raw),
                  "style": pd8, "style_name": "PD8", "slow": True})
    for lv, st in (("std", std_iol), ("adv", adv_iol)):
        t = iol[lv]
        J.append({"id": f"{lv}_in_one_line", "level": lv, "role": "in_one_line", "manuscript": t, "tts_input": n3.tts_safe_news_en(t), "style": st,
                  "style_name": "IN_ONE_LINE(既存承認Style" + ("+A2減速指示" if lv == "std" else "") + ")", "slow": lv == "std"})
    return J


def run_job(j, call):
    import er002_common as common, er003_b1_p3u_audio as p3u, er003_audio_tts_asr_safety as safety, er008_a2_postprocess_slowdown_01 as slowdown
    style = j["style"]
    final = None
    for attempt in range(1, B.MAX_REGEN + 2):
        if _spent["jpy"] > BUDGET:
            log({"job": j["id"], "event": "BUDGET_STOP"})
            return {"id": j["id"], "status": "BUDGET_STOP"}
        t0 = time.time()
        samples = usage = None
        for tech in (1, 2):
            try:
                samples, usage = call(j["tts_input"], style, B.VOICE)
                break
            except Exception as e:
                log({"job": j["id"], "attempt": attempt, "tech_try": tech, "event": "TTS_TECH_FAILURE", "error": f"{type(e).__name__}: {str(e)[:200]}"})
        if samples is None:
            continue
        tts_jpy = ((usage["input_tokens"] or 0) * B.PRICE_IN + (usage["output_tokens"] or 0) * B.PRICE_OUT) / 1e6 * B.USD_JPY
        trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": j["id"], "level": j["level"], "role": j["role"], "attempt": attempt, "regen_index": attempt - 1,
               "style_name": j["style_name"], "model_requested": B.MODEL, "model_version": usage["model_version"], "voice": B.VOICE, "tts_backend": B.BACKEND,
               "execution_mode": "STANDARD(sync, DEV Trial; Production既定=Batch)", "style_sha256": B.sha_text(style), "style_text": style,
               "tts_input_sha256": B.sha_text(j["tts_input"]), "tts_input_text": j["tts_input"], "tts_safe_news_en_applied": True,
               "manuscript_sha256": B.sha_text(j["manuscript"]), "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
               "tts_cost_jpy": round(tts_jpy, 4), "elapsed_s": round(time.time() - t0, 1)}
        with _lk:
            _spent["jpy"] += tts_jpy
        if trimmed is None:
            rec.update(status="NO_SPEECH", verified=False)
            log(rec)
            continue
        anomaly = safety.detect_duration_anomaly(ti["raw_duration_seconds"], j["tts_input"], "en")
        wav = os.path.join(ATT, f"{j['id']}_a{attempt}.wav")
        common.write_wav_float(wav, trimmed, common.SAMPLE_RATE, 1)
        rec.update(wav=os.path.relpath(wav, ROOT).replace("\\", "/"), wav_sha256=B.sha_file(wav), raw_duration_s=ti["raw_duration_seconds"],
                   trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3), duration_anomaly=anomaly)
        if anomaly["is_anomaly"]:
            rec.update(status="DURATION_ANOMALY", verified=False)
            log(rec)
            continue
        a = B.asr_and_judge(wav, j["tts_input"], j["role"])
        with _lk:
            _spent["jpy"] += a["asr_cost_jpy_est"]
        rec.update(status="OK", asr_model=B.ASR_MODEL, asr="primary_only(Secondary/cascade/LR/minimal fallback不使用)", **a)
        log(rec)
        if a["verified"]:
            final = (attempt, wav, rec)
            break
    if final is None:
        return {"id": j["id"], "status": "ASR_NG_STOP"}
    attempt, wav, rec = final
    out = os.path.join(SEG, f"{j['id']}_raw.wav")
    shutil.copyfile(wav, out)
    res = {"id": j["id"], "status": "OK", "attempt": attempt, "regen_count": attempt - 1, "raw_wav": out, "raw_sha256": B.sha_file(out),
           "raw_duration_s": rec["trimmed_duration_s"]}
    if j["slow"]:
        slow = os.path.join(SEG, f"{j['id']}_slow6.wav")
        info = slowdown.apply_a2_slowdown(out, slow)
        a2 = B.asr_and_judge(slow, j["tts_input"], j["role"])
        with _lk:
            _spent["jpy"] += a2["asr_cost_jpy_est"]
        info2 = {k: info[k] for k in ("slowdown_pct_target", "slowdown_pct_actual", "src_duration_seconds", "dst_duration_seconds")}
        info2["ratio"] = round(info["dst_duration_seconds"] / info["src_duration_seconds"], 4)
        res.update(slow_wav=slow, slow_sha256=B.sha_file(slow), slowdown=info2,
                   slow_asr={k: a2[k] for k in ("asr_text", "classification", "verified", "length_ok")})
        log({"job": j["id"], "event": "SLOWDOWN_APPLIED", "process": "er008_a2_postprocess_slowdown_01.apply_a2_slowdown (FFmpeg atempo=1/1.06)", **info2,
             "slow_wav": os.path.relpath(slow, ROOT).replace("\\", "/"), "slow_sha256": res["slow_sha256"],
             "post_slowdown_primary_asr": res["slow_asr"], "note": "減速後ASRは参考記録(再生成の根拠にしない)"})
    return res


def main():
    os.makedirs(ATT, exist_ok=True)
    os.makedirs(SEG, exist_ok=True)
    B.patch_validator_telemetry()
    J = jobs()
    only = sys.argv[1:]
    if only:
        J = [j for j in J if j["id"] in only]
    print([j["id"] for j in J], flush=True)
    call = B.make_tts_call()
    t0 = time.time()
    with cf.ThreadPoolExecutor(5) as ex:
        results = list(ex.map(lambda j: run_job(j, call), J))
    summ = {"model_requested": B.MODEL, "voice": B.VOICE, "results": results, "spent_jpy_est": round(_spent["jpy"], 3),
            "elapsed_s": round(time.time() - t0, 1), "validator_telemetry_redirected": B._sem_telemetry}
    name = "gen_summary_v3_01" + ("_" + "_".join(only) if only else "") + ".json"
    json.dump(summ, open(os.path.join(OUT, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in results:
        print(json.dumps(r, ensure_ascii=False)[:500])
    print("spent_jpy_est", summ["spent_jpy_est"], "elapsed", summ["elapsed_s"])


if __name__ == "__main__":
    main()
