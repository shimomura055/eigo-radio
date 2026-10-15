# -*- coding: utf-8 -*-
"""AUW 委任_06b: 06b 初期 run(固定単価で過小記録)の費用を、実測 token 校正(xrun の raw_usage_log: flash-lite TTS≈0.0243 JPY/音声秒、OpenAI ASR≈0.0047 JPY/音声秒)で再推定する。API 0。
出力: cost/revised_estimates.json。ledger_total は revised があればそれを使う。"""
import glob
import json
import os
import sys
import wave

E = "er058_output/unified_all_roles_production_wiring_01/evidence_06b"
TTS_PER_S, ASR_PER_S = 0.0243, 0.0047
SHELL = {"welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "kp1_number", "kp2_number", "kp3_number", "kp4_number", "kp5_number",
         "num_one", "num_two", "num_three", "num_four", "num_five"}


def dur(p):
    try:
        with wave.open(p, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return 0.0


def clip_seconds(root):
    tot, n = 0.0, 0
    for p in glob.glob(f"{root}/**/narration/*.wav", recursive=True):
        b = os.path.basename(p)[:-4]
        if b in SHELL or b.endswith("_original") or b.startswith("topic_intro_old"):
            continue
        orig = p[:-4] + "_original.wav"
        tot += dur(orig if os.path.exists(orig) else p)
        n += 1
    return tot, n


def usage(run):
    n_tts = n_asr = az = 0
    azjpy = 0.0
    for l in open(f"{E}/{run}/usage_log.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r.get("provider") == "gemini" and "TTS" in str(r.get("api")):
            n_tts += 1
        elif r.get("provider") == "openai_asr":
            n_asr += 1
        elif r.get("provider") == "azure" and not r.get("mock"):
            azjpy += r.get("est_jpy", 0.0)
    return n_tts, n_asr, azjpy


def main():
    out = {}
    for run in sys.argv[1:]:
        secs, n = clip_seconds(f"{E}/{run}")
        n_tts, n_asr, azjpy = usage(run)
        mean = secs / n if n else 0.0
        # TTS 呼出数 >= clip 数(再試行分)。再試行 clip の長さは平均で近似
        est_tts = n_tts * mean * TTS_PER_S
        est_asr = n_asr * mean * ASR_PER_S
        out[run] = {"clips": n, "mean_clip_seconds": round(mean, 2), "n_tts_calls": n_tts, "n_asr_calls": n_asr,
                    "revised_tts_jpy": round(est_tts, 3), "revised_asr_jpy": round(est_asr, 3), "azure_jpy_measured": round(azjpy, 3),
                    "revised_est_jpy": round(est_tts + est_asr + azjpy, 3),
                    "basis": "TTS=n_calls x mean_clip_s x 0.0243 JPY/s, ASR=n_calls x mean_clip_s x 0.0047 JPY/s (校正元=xrun raw_usage_log token実測), Azure=秒数実測x0.0444"}
    p = f"{E}/cost/revised_estimates.json"
    prev = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    prev.update(out)
    json.dump(prev, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
