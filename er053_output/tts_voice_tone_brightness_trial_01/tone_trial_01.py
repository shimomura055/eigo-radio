# -*- coding: utf-8 -*-
"""FAMILY-X-TTS-VOICE-TONE-BRIGHTNESS-TRIAL-01 委任_01 Trial専用script。
Production backend関数(flw.resolve_tts_call_and_prompt / common._call_tts_with_retry /
p3u.trim_english_keyword_silence / routing.transcribe)を同一条件で呼ぶ。
Master Store・review_lock・human_review_queue・cost_logger(未install=記録なし)へ書かない。
各案1回のみ(再生成なし)。"""
import os, sys, json, time, hashlib, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"   # DEV Standard同期(PM_GOVERNANCE 7節)。Production既定はBATCH
import numpy as np
import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p9a_audio as p9a
import er003_audio_tts_asr_safety as safety
import er003_v1_n3_01_tts_generate as n3
import er003_v1_sing01_voice01_generate as voice01
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er007_ja_asr_validator_01 as javal
import er006_pronunciation_tts_injection_01 as en_inj
import er033_tts_flash_lite_backend_wiring_01 as flw
import er033_tts_flash_lite_family_x_styles_01 as fls
import soundfile as sf

OUT = "er053_output/tts_voice_tone_brightness_trial_01"
AUD = f"{OUT}/audio"
PAGE = "user_test/tts_voice_tone_brightness_01"
JA_TEXT = "コーヒーの価格は、世界の天候や豆の供給など、いくつもの動きに左右されます。値下がりを伝えるニュースの背景をたどり、毎日の買い物とのつながりを見ていきます。"
EN_TEXT = "Coffee prices have been making headlines, but the story can be hard to follow. In this episode, we’ll look at what is behind the news and what it means for people who buy coffee."
JA_STYLES = {
    "J0_CURRENT": "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてください。",
    "J1_BRIGHT": "自然で親しみやすい話し言葉で、少し明るく軽やかな声のトーンで話してください。内容に応じて自然に抑揚をつけ、落ち着きも保ってください。演技がかった話し方は避けてください。",
    "J2_BRIGHT": "明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。",
    "J3_BRIGHT": "明るく生き生きとした声で、軽快なリズムと表情豊かな抑揚をつけて話してください。聞き手が思わず続きを聞きたくなるような、前向きでエネルギーのある語り口にしてください。ただし、大げさな演技や過度なテンションは避けてください。",
}
EN_STYLES = {
    "E0_CURRENT": "calm, conversational",
    "E1_UPBEAT": "slightly upbeat, warm and conversational; natural and relaxed.",
    "E2_UPBEAT": "warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.",
    "E3_UPBEAT": "bright, lively and energetic; cheerful conversational delivery with expressive intonation, without sounding exaggerated.",
}
assert JA_STYLES["J0_CURRENT"] == fls.FAMILY_X_ROLE_STYLE_JA, "J0 != production J3"
assert EN_STYLES["E0_CURRENT"] == fls.FAMILY_X_ROLE_STYLE_EN["PREVIEW"] == fls.FAMILY_X_ROLE_STYLE_EN["COMMENT"]
BACKEND = "speech_metadata_flash_lite"
MARGIN = p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS  # JA(strict既定)=0.35。EN(voice01.SAFETY_MARGIN)=0.35


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def gen_ja(sid, style):
    tts_text = safety.to_tts_safe_japanese_fraction_reading(n3.tts_safe_ja(JA_TEXT))
    out = f"{AUD}/{sid}_raw.wav"
    t0 = time.time()
    r = p9a.generate_narration_snippet(tts_text, "ja", out, safety_margin_seconds=MARGIN,
                                       style_prefix_override=style, tts_backend=BACKEND)
    r["_tts_text_equals_manuscript"] = (tts_text == JA_TEXT)
    r["_elapsed"] = round(time.time() - t0, 1)
    return r


def gen_en(sid, style):
    tts_text = n3.tts_safe_number_words_en(n3.tts_safe_en(EN_TEXT))
    aug, hits = en_inj.augment_style_prefix_with_pronunciation(style, tts_text, min_confidence="medium")
    out = f"{AUD}/{sid}_raw.wav"
    t0 = time.time()
    call_fn, prompt = flw.resolve_tts_call_and_prompt(tts_text, aug, common.MODEL_NAME, voice01.CHARON, out,
                                                      tts_backend=BACKEND)
    pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": str(err)}
    raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(raw, common.SAMPLE_RATE, safety_margin_seconds=voice01.SAFETY_MARGIN)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間検出失敗"}
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], tts_text, "en")
    common.write_wav_float(out, trimmed, common.SAMPLE_RATE, 1)
    return {"status": "OK", "text": tts_text, "path": out, "model": flw.resolve_actual_model_name(common.MODEL_NAME, BACKEND),
            "voice": voice01.CHARON, "call_count": 1 + retries, "retry_count": retries, "trim_info": trim_info,
            "duration_anomaly": anomaly, "style_prefix": aug, "pronunciation_hits": hits,
            "_elapsed": round(time.time() - t0, 1)}


def main():
    os.makedirs(AUD, exist_ok=True)
    os.makedirs(PAGE, exist_ok=True)
    jobs = [("ja", k, v) for k, v in JA_STYLES.items()] + [("en", k, v) for k, v in EN_STYLES.items()]
    res = {}
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(gen_ja if l == "ja" else gen_en, k, v): (l, k, v) for l, k, v in jobs}
        for f in cf.as_completed(futs):
            l, k, v = futs[f]
            try:
                res[k] = f.result()
            except Exception as e:
                res[k] = {"status": "ERROR", "reason": f"{type(e).__name__}: {e}"}
            print(k, res[k].get("status"), res[k].get("reason", ""), flush=True)
    # 音量正規化: Production assembly(apply_family_x_a2_gain)と同じ
    # gain_to_rms(compute_gain_for_target_rms, max_peak=0.95)。目標RMS=言語内の現行案(J0/E0)のRMS。
    rows = []
    for l, d, base in (("ja", JA_STYLES, "J0_CURRENT"), ("en", EN_STYLES, "E0_CURRENT")):
        target = None
        if res[base].get("status") == "OK":
            target = p9a.rms(common.read_wav_float(res[base]["path"])[0])
        for k, style in d.items():
            r = res[k]
            row = {"sample_id": k, "language": l, "style": style, "status": r.get("status"), "reason": r.get("reason")}
            if r.get("status") == "OK" and target:
                samples = common.read_wav_float(r["path"])[0]
                gain = p9a.compute_gain_for_target_rms(samples, target)
                g = samples * gain
                mp3 = f"{PAGE}/{k}.mp3"
                common.write_wav_float(f"{AUD}/{k}_normalized.wav", g, common.SAMPLE_RATE, 1)
                sf.write(mp3, g, common.SAMPLE_RATE, format="MP3")
                asr_text, asr_err = routing.transcribe(r["path"], language="ja-JP" if l == "ja" else "en-US")
                if l == "ja":
                    cls = javal.classify_ja_asr_match(JA_TEXT, asr_text)
                else:
                    cls = val.classify_asr_match(r["text"], asr_text, segment_id="preview")
                dur = len(samples) / common.SAMPLE_RATE
                est_usd = dur * 25 * 6.0 / 1e6 + (len(r["text"]) / 2.5 + 20) * 0.5 / 1e6  # Standard単価(pricing_snapshot)
                row.update({
                    "model_id": r["model"], "voice": r["voice"], "tts_backend": BACKEND,
                    "tts_execution_mode": "STANDARD(DEV同期、Production既定=BATCH)",
                    "style_actually_sent": r.get("style_prefix"), "manuscript": JA_TEXT if l == "ja" else EN_TEXT,
                    "tts_input_text": r["text"], "call_count": r.get("call_count"), "retry_count": r.get("retry_count"),
                    "duration_s_raw": round(dur, 3), "peak_raw": round(p9a.peak(samples), 4), "rms_raw": round(p9a.rms(samples), 5),
                    "gain_applied": round(float(gain), 4), "target_rms": round(target, 5),
                    "peak_norm": round(p9a.peak(g), 4), "rms_norm": round(p9a.rms(g), 5),
                    "duration_s_norm": round(len(g) / common.SAMPLE_RATE, 3),
                    "trim_safety_margin_s": MARGIN, "sample_rate": common.SAMPLE_RATE, "raw_wav_sha256": sha(r["path"]), "mp3": mp3,
                    "asr_fn": "routing.transcribe(Production primary ASR、1回のみ、cascade/多重照合なし)",
                    "asr_text": asr_text, "asr_error": asr_err, "asr_classification": cls.classification,
                    "asr_similarity": getattr(cls, "similarity", None),
                    "est_cost_usd": round(est_usd, 6), "elapsed_s": r.get("_elapsed"),
                })
            rows.append(row)
    with open(f"{OUT}/results_01.jsonl", "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    print("done")


if __name__ == "__main__":
    main()
