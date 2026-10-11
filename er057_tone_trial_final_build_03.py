# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_03 Trial専用script(Production非経由・Productionから参照されない)。

目的: ユーザー選択Style(A5/B5/E1/F5/K2/M2/P2)を反映したCoffee Standard/Advanced最終試聴版の作成。
modes:
  gen       : Full Story 6 segmentをF5(逐語)で再生成(Aoede, gemini-3.8-flash-lite-tts, speech_metadata, Standard同期)。
              Primary ASR(gpt-4o-mini-transcribe)+既存validator(val.evaluate_attempt)で内容QA。NG時は同一Promptで最大2回再生成。
              Standardには既存6%減速(er008 apply_a2_slowdown)を適用。
  regress   : 既存音声のみで組立て、既存完成版wavとサンプル一致するか確認(assembler回帰)。
  assemble  : Trial assemblerで Standard/Advanced 完成版を組立てmp3化。
Master Store/manifest/telemetry/human_review_queue/attempt_history/cost_loggerへは一切書かない。
validatorが書くtelemetry(semantic_equivalence.append_telemetry_log)はプロセス内でTrial専用ファイルへ差替える。
"""
from __future__ import annotations
import os, sys, json, time, wave, hashlib, shutil, threading, concurrent.futures as cf

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
import numpy as np
import soundfile as sf

TONE = "C:/Users/tensh/eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01"
BASE = os.path.join(ROOT, "er057_output", "coffee_final_listening_tone_trial_01")
OUT = os.path.join(BASE, "part_final")
ATT = os.path.join(OUT, "attempts")
SEG = os.path.join(OUT, "segments")
AEF, BCD = os.path.join(BASE, "part_AEF"), os.path.join(BASE, "part_BCD")
GENLOG = os.path.join(OUT, "generation_log_03.jsonl")
MODEL = "gemini-3.8-flash-lite-tts"
VOICE = "Aoede"
BACKEND = "speech_metadata_flash_lite"
USD_JPY = 160.0
PRICE_IN, PRICE_OUT = 0.5, 6.0          # Gemini TTS Standard(USD/1M tok)
ASR_PRICE_IN, ASR_PRICE_OUT = 1.25, 5.0  # gpt-4o-mini-transcribe(USD/1M tok)
BUDGET_JPY = 20.0
MAX_REGEN = 2                            # NG時の同一Prompt再生成上限(初回+2回=最大3 call/segment)
ASR_MODEL = "gpt-4o-mini-transcribe"

_lock = threading.Lock()
_spent = {"jpy": 0.0}
_sem_telemetry = []


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def append_log(rec):
    with _lock:
        with open(GENLOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_f5_style():
    """prompts_F.md の F5 style(逐語)を取得し、Trial生成scriptのSPECSと一致をassertする。"""
    import er057_tone_trial_tts_gen_01 as G
    md = open(os.path.join(AEF, "prompts", "prompts_F.md"), encoding="utf-8").read()
    i = md.index("## F5 ")
    blk = md[i:].split("```")[1].strip()
    spec = G.SPECS["F"]["items"]["F5"][2]
    assert blk == spec, "prompts_F.md F5 と SPECS F5 が不一致"
    return blk


def jobs_def():
    import er003_v1_n3_01_tts_generate as n3
    J = []
    for lv, d in (("std", "a2"), ("adv", "b1b")):
        parts = json.load(open(f"{TONE}/{d}/parts.json", encoding="utf-8"))
        for n in (1, 2, 3):
            raw = parts[f"part{n}"]
            J.append({"id": f"{lv}_part{n}", "level": lv, "role": f"full_story_part{n}", "manuscript": raw,
                      "tts_input": n3.tts_safe_news_en(raw)})
    return J


def make_tts_call():
    import er033_tts_flash_lite_backend_wiring_01 as flw
    import er006_model_routing_contract_01 as rc
    import er002_gemini_client as gclient
    import er002_common as common
    from google.genai import types
    flw.assert_sdk_supports_speech_metadata()
    model = rc.require_model(flw.FAMILY_X_FLASH_LITE_TTS_PROCESS, MODEL)
    client = gclient.make_client()

    def call(text, style, voice):
        content = types.Content(parts=[types.Part(text=text, speech_metadata=types.SpeechMetadata(style=style))], role="user")
        resp = client.models.generate_content(
            model=model, contents=content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(language_code=common.LANGUAGE_CODE, voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))),
                http_options=types.HttpOptions(timeout=gclient.TTS_TIMEOUT_MS)))
        parts = resp.candidates[0].content.parts
        raw = b"".join(p.inline_data.data for p in parts if p.inline_data and p.inline_data.data)
        if not raw:
            raise RuntimeError("empty audio")
        samples, fr = flw._decode_audio_defensive(raw)
        samples = flw._resample_to_common_rate(samples, fr)
        u = getattr(resp, "usage_metadata", None)
        return samples, {"model_version": getattr(resp, "model_version", None),
                         "input_tokens": getattr(u, "prompt_token_count", None),
                         "output_tokens": getattr(u, "candidates_token_count", None)}
    return call


def patch_validator_telemetry():
    """validatorが失敗時に書くtelemetry追記先を、プロセス内でTrial専用リストへ差替える(Production telemetry不変)。"""
    import er021_en_asr_semantic_equivalence_production_01 as semeq
    semeq.append_telemetry_log = lambda record, path=None: _sem_telemetry.append(record)


def asr_and_judge(wav_path, text, role):
    import er006_asr_provider_routing_01 as routing
    import er006_preprod_hardening_01_validation as val
    asr_text, err = routing.transcribe(wav_path, language="en-US")
    length_ok = asr_text is not None and len(asr_text) <= len(text) + 15
    verified_content, stop_retry, cls = val.evaluate_attempt(text, asr_text, [], segment_id=role)
    dur = sf.info(wav_path).duration
    cost = ((dur * 10) * ASR_PRICE_IN + (len(asr_text or "") / 4.0) * ASR_PRICE_OUT) / 1e6 * USD_JPY  # 推定(10tok/s入力、出力≒字数/4)
    return {"asr_text": asr_text, "asr_error": err, "classification": cls.classification, "should_pass": bool(cls.should_pass),
            "length_ok": bool(length_ok), "verified": bool(verified_content and length_ok), "asr_cost_jpy_est": round(cost, 4),
            "classification_reason": getattr(cls, "reason", None)}


def run_job(j, call, style):
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er003_audio_tts_asr_safety as safety
    import er008_a2_postprocess_slowdown_01 as slowdown
    style_sha = sha_text(style)
    in_sha = sha_text(j["tts_input"])
    final = None
    for attempt in range(1, MAX_REGEN + 2):
        if _spent["jpy"] > BUDGET_JPY:
            append_log({"job": j["id"], "event": "BUDGET_STOP", "spent_jpy": round(_spent["jpy"], 3)})
            return {"id": j["id"], "status": "BUDGET_STOP"}
        t0 = time.time()
        samples = usage = err = None
        for tech in (1, 2):   # 技術失敗(例外・空応答)時のみ1回retry
            try:
                samples, usage = call(j["tts_input"], style, VOICE)
                break
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:200]}"
                append_log({"job": j["id"], "attempt": attempt, "tech_try": tech, "event": "TTS_TECH_FAILURE", "error": err})
        if samples is None:
            continue
        usd = ((usage["input_tokens"] or 0) * PRICE_IN + (usage["output_tokens"] or 0) * PRICE_OUT) / 1e6
        tts_jpy = usd * USD_JPY
        trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE,
                                                       safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": j["id"], "level": j["level"], "role": j["role"], "attempt": attempt,
               "regen_index": attempt - 1, "style_name": "F5", "model_requested": MODEL, "model_version": usage["model_version"],
               "voice": VOICE, "tts_backend": BACKEND, "execution_mode": "STANDARD(sync, DEV Trial; Production既定=Batch)",
               "style_sha256": style_sha, "style_text": style, "tts_input_sha256": in_sha, "tts_safe_news_en_applied": True,
               "manuscript_sha256": sha_text(j["manuscript"]), "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"],
               "tts_cost_jpy": round(tts_jpy, 4), "elapsed_s": round(time.time() - t0, 1)}
        with _lock:
            _spent["jpy"] += tts_jpy
        if trimmed is None:
            rec.update(status="NO_SPEECH", verified=False); append_log(rec); continue
        anomaly = safety.detect_duration_anomaly(ti["raw_duration_seconds"], j["tts_input"], "en")
        wav = os.path.join(ATT, f"{j['id']}_a{attempt}.wav")
        common.write_wav_float(wav, trimmed, common.SAMPLE_RATE, 1)
        rec.update(wav=os.path.relpath(wav, ROOT).replace("\\", "/"), wav_sha256=sha_file(wav), raw_duration_s=ti["raw_duration_seconds"],
                   trimmed_duration_s=round(len(trimmed) / common.SAMPLE_RATE, 3), duration_anomaly=anomaly)
        if anomaly["is_anomaly"]:
            rec.update(status="DURATION_ANOMALY", verified=False); append_log(rec); continue
        a = asr_and_judge(wav, j["tts_input"], j["role"])
        with _lock:
            _spent["jpy"] += a["asr_cost_jpy_est"]
        rec.update(status="OK", asr_model=ASR_MODEL, asr="primary_only(Secondary/cascade/LR/minimal fallback不使用)", **a)
        append_log(rec)
        if a["verified"]:
            final = (attempt, wav, rec)
            break
    if final is None:
        return {"id": j["id"], "status": "ASR_NG_STOP"}
    attempt, wav, rec = final
    out = os.path.join(SEG, f"{j['id']}_f5.wav")
    shutil.copyfile(wav, out)
    res = {"id": j["id"], "status": "OK", "attempt": attempt, "regen_count": attempt - 1, "f5_wav": out, "f5_sha256": sha_file(out)}
    if j["level"] == "std":
        slow = os.path.join(SEG, f"{j['id']}_f5_slow6.wav")
        info = slowdown.apply_a2_slowdown(out, slow)
        a2 = asr_and_judge(slow, j["tts_input"], j["role"])
        with _lock:
            _spent["jpy"] += a2["asr_cost_jpy_est"]
        info2 = {k: info[k] for k in ("slowdown_pct_target", "slowdown_pct_actual", "src_duration_seconds", "dst_duration_seconds")}
        info2["ratio"] = round(info["dst_duration_seconds"] / info["src_duration_seconds"], 4)
        res.update(slow_wav=slow, slow_sha256=sha_file(slow), slowdown=info2, slow_asr={k: a2[k] for k in ("asr_text", "classification", "verified", "length_ok")})
        append_log({"job": j["id"], "event": "SLOWDOWN_APPLIED", "process": "er008_a2_postprocess_slowdown_01.apply_a2_slowdown (FFmpeg atempo=1/1.06)",
                    **info2, "slow_wav": os.path.relpath(slow, ROOT).replace("\\", "/"), "slow_sha256": res["slow_sha256"],
                    "post_slowdown_primary_asr": res["slow_asr"], "note": "減速後ASRは参考記録(再生成の根拠にしない)"})
    return res


def cmd_gen():
    os.makedirs(ATT, exist_ok=True); os.makedirs(SEG, exist_ok=True)
    style = load_f5_style()
    patch_validator_telemetry()
    J = jobs_def()
    done = set()
    sumpath = os.path.join(OUT, "gen_summary_03.json")
    print("F5 style sha", sha_text(style)[:12], "jobs", [j["id"] for j in J], flush=True)
    call = make_tts_call()
    t0 = time.time()
    with cf.ThreadPoolExecutor(6) as ex:
        results = list(ex.map(lambda j: run_job(j, call, style), J))
    summary = {"model_requested": MODEL, "voice": VOICE, "style_sha256": sha_text(style), "results": results,
               "spent_jpy_est": round(_spent["jpy"], 3), "elapsed_s": round(time.time() - t0, 1), "validator_telemetry_records_redirected": _sem_telemetry}
    json.dump(summary, open(sumpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in results:
        print(json.dumps(r, ensure_ascii=False)[:400])
    print("spent_jpy_est", summary["spent_jpy_est"], "elapsed", summary["elapsed_s"])


def cmd_gen_topic():
    """異音対処(STD-24, Standard topic_intro、TTS由来と切り分け済み): 既存承認Style・既存原稿で1回だけ再生成。"""
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er003_audio_tts_asr_safety as safety
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles
    patch_validator_telemetry()
    r = json.load(open(f"{TONE}/a2/audit/tts_generation_results.json", encoding="utf-8"))["segments"]["topic_intro"]
    text, logged_style = r["text"], r["style_prefix"]
    style = fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"]
    assert style == logged_style, (style, logged_style)
    call = make_tts_call()
    t0 = time.time()
    samples, usage = call(text, style, "Aoede")
    usd = ((usage["input_tokens"] or 0) * PRICE_IN + (usage["output_tokens"] or 0) * PRICE_OUT) / 1e6
    trimmed, ti = p3u.trim_english_keyword_silence(samples, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
    wav = os.path.join(SEG, "std_topic_intro_regen.wav")
    common.write_wav_float(wav, trimmed, common.SAMPLE_RATE, 1)
    a = asr_and_judge(wav, text, "topic_intro")
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job": "std_topic_intro_regen", "purpose": "ANOMALY_REMEDIATION_STD-24(TTS由来と切り分け済み、既存承認Style・原稿変更なし、1回のみ)",
           "role": "topic_intro", "level": "std", "attempt": 1, "style_name": "既存承認 TOPIC_INTRO(変更なし)", "model_requested": MODEL,
           "model_version": usage["model_version"], "voice": "Aoede", "tts_backend": BACKEND, "execution_mode": "STANDARD(sync, DEV Trial; Production既定=Batch)",
           "style_sha256": sha_text(style), "style_text": style, "tts_input_sha256": sha_text(text), "tts_input_text": text,
           "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"], "tts_cost_jpy": round(usd * USD_JPY, 4),
           "trimmed_duration_s": round(len(trimmed) / common.SAMPLE_RATE, 3), "wav": os.path.relpath(wav, ROOT).replace("\\", "/"),
           "wav_sha256": sha_file(wav), "elapsed_s": round(time.time() - t0, 1), **a}
    append_log(rec)
    print(json.dumps({k: rec[k] for k in ("model_version", "trimmed_duration_s", "tts_cost_jpy", "asr_text", "classification", "verified", "asr_cost_jpy_est")}, ensure_ascii=False))


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "gen":
        cmd_gen()
    elif m == "gen_topic":
        cmd_gen_topic()
    else:
        import er057_tone_trial_final_build_03_asm as A  # assemble/regress/qa(別ファイルに分離)
        getattr(A, "cmd_" + m)(*sys.argv[2:])
