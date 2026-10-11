# -*- coding: utf-8 -*-
"""FAMILY-X-TTS-FULL-STORY-TONE-TRIAL-01 委任_01 Trial専用script。
Standard(Aoede) Full Story 経路のうち「6%減速post-process/slowerinstruction/verified_strict(Review Lock・Store書込)」を
除いた素の生成(p9a.generate_narration_snippet: Production内部と同じ呼出)をStyleだけ変えて各案1回呼ぶ。
共有ログ・Master Store・cost_logger へ書かない。"""
import os, sys, json, time, hashlib, concurrent.futures as cf
sys.path.insert(0, os.getcwd())
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_b1_p3u_audio as p3u
import er003_v1_n3_01_tts_generate as n3
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er033_tts_flash_lite_family_x_styles_01 as fls
import soundfile as sf

OUT = "er053_output/tts_full_story_tone_trial_01"
AUD = f"{OUT}/audio"
PAGE = "user_test/tts_full_story_tone_01"
MANUSCRIPT = ("“Coffee prices are falling!” Great! Maybe spring will finally come to my wallet, too. But supermarket prices do not change. "
 "They look calm, as if saying, “News? I haven’t heard any.” If bean prices have fallen, why don’t we pay less?\n\n"
 "First, let’s go back to when high prices caused a stir. Bad weather in Brazil and Vietnam hurt the supply. Few beans were for sale, and stocks were low. "
 "Then demand around the world was strong. It was a hard mix for prices to settle down.")
STYLES = {
 "F0": "calm, steady news narration with natural emphasis at key points and turns; not dramatic.",
 "F1": "slightly upbeat, warm and conversational; natural and relaxed, while maintaining the clarity of news narration.",
 "F1.5": "warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration.",
 "F2": "warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.",
}
assert STYLES["F0"] == fls.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"], "F0 != production FULL_STORY"
BACKEND = "speech_metadata_flash_lite"
MARGIN = p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS
TTS_TEXT = n3.tts_safe_news_en(MANUSCRIPT)

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def gen(k, style):
    out = f"{AUD}/{k}_raw.wav"
    t0 = time.time()
    r = p9a.generate_narration_snippet(TTS_TEXT, "en", out, safety_margin_seconds=MARGIN,
                                       style_prefix_override=style, tts_backend=BACKEND)
    r["_elapsed"] = round(time.time() - t0, 1)
    r["_out"] = out
    return r

def main():
    os.makedirs(AUD, exist_ok=True); os.makedirs(PAGE, exist_ok=True)
    res = {}
    with cf.ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(gen, k, v): k for k, v in STYLES.items()}
        for f in cf.as_completed(futs):
            k = futs[f]
            try: res[k] = f.result()
            except Exception as e: res[k] = {"status": "ERROR", "reason": f"{type(e).__name__}: {e}"}
            print(k, res[k].get("status"), res[k].get("reason", ""), flush=True)
    target = None
    if res["F0"].get("status") == "OK":
        target = p9a.rms(common.read_wav_float(res["F0"]["_out"])[0])
    rows = []
    for k, style in STYLES.items():
        r = res[k]
        row = {"sample_id": k, "style": style, "status": r.get("status"), "reason": r.get("reason")}
        if r.get("status") == "OK" and target:
            path = r["_out"]
            s = common.read_wav_float(path)[0]
            gain = p9a.compute_gain_for_target_rms(s, target)
            g = s * gain
            mp3 = f"{PAGE}/{k}.mp3"
            common.write_wav_float(f"{AUD}/{k}_normalized.wav", g, common.SAMPLE_RATE, 1)
            sf.write(mp3, g, common.SAMPLE_RATE, format="MP3")
            asr_text, asr_err = routing.transcribe(path, language="en-US")
            cls = val.classify_asr_match(TTS_TEXT, asr_text, segment_id="full_story_part1")
            dur = len(s) / common.SAMPLE_RATE
            est_usd = dur * 25 * 6.0 / 1e6 + (len(TTS_TEXT) / 4 + 30) * 0.5 / 1e6
            asr_words = len((asr_text or "").split()); ms_words = len(TTS_TEXT.split())
            row.update({"model_id": r.get("model"), "voice": r.get("voice"), "tts_backend": BACKEND,
                "tts_execution_mode": "STANDARD(DEV同期)", "speed": "通常速度(6%減速・slower instruction不適用)",
                "language_code": common.LANGUAGE_CODE, "style_actually_sent": style, "tts_input_text": TTS_TEXT,
                "call_count": r.get("call_count"), "retry_count": r.get("retry_count"),
                "duration_s_raw": round(dur, 3), "peak_raw": round(p9a.peak(s), 4), "rms_raw": round(p9a.rms(s), 5),
                "gain_applied": round(float(gain), 4), "target_rms": round(target, 5),
                "peak_norm": round(p9a.peak(g), 4), "rms_norm": round(p9a.rms(g), 5),
                "trim_safety_margin_s": MARGIN, "raw_wav_sha256": sha(path), "mp3": mp3,
                "asr_text": asr_text, "asr_error": asr_err, "asr_classification": cls.classification,
                "asr_similarity": getattr(cls, "similarity", None), "asr_words": asr_words, "manuscript_words": ms_words,
                "est_cost_usd": round(est_usd, 6), "elapsed_s": r.get("_elapsed")})
        rows.append(row)
    with open(f"{OUT}/results_01.jsonl", "w", encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    print("done")

if __name__ == "__main__":
    main()
