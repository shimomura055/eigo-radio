# -*- coding: utf-8 -*-
"""measure + 連続試聴wav/mp3生成(Trial専用、API費用0)。全パターン同一script。"""
import os, sys, json, subprocess, numpy as np
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
import er057_kp_expl_lib_01 as L
import er003_b1_p9a_audio as p9a, er002_common as common
import er057_kp_expl_style_trial_01_gen as G
OUT = ROOT + "/er057_output/kp_en_explanation_style_trial_01"
PUB = ROOT + "/user_test/coffee_kp_explanation_style_trial_01/audio"
os.makedirs(PUB, exist_ok=True)
TARGET_RMS = 0.12584      # v4 Advanced gain_report target_rms(Production同一)
SR = p9a.TARGET_SAMPLE_RATE
PAUSE = p9a.KEY_PHRASE_INTERNAL_PAUSE_SECONDS   # 0.4s(Production assembler同一)
FFMPEG = None
def ffmpeg():
    import er057_tone_trial_final_build_03_asm as A; return A.FFMPEG
TONE = "C:/Users/tensh/eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/b1b/narration/"
V4_PHRASE = ROOT + "/er057_output/coffee_final_listening_tone_trial_01/part_final/kp_adv_k2/K2_advkp%d.wav"
def gained(mono):
    g = p9a.compute_gain_for_target_rms(mono, TARGET_RMS)
    return mono * g, float(g)
def stereo(mono): return p9a.mono_24k_to_stereo_target(mono)
def to_mp3(st, path):
    import soundfile as sf, tempfile
    tmp = path + ".tmp.wav"; sf.write(tmp, np.clip(st, -1, 1), SR, subtype="PCM_16")
    r = subprocess.run([ffmpeg(), "-y", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "128k", path], capture_output=True, text=True); os.remove(tmp)
    assert r.returncode == 0, r.stderr[-300:]
def gen_log():
    d = {}
    for l in open(G.GENLOG, encoding="utf-8"):
        r = json.loads(l)
        if r.get("status") == "OK": d.setdefault((r["kp"], r["cand"]), []).append(r)
    return d
def main():
    glog = gen_log(); res = {}
    cands = ["P0v4"] + G.cand_list() + [f"P{i}r{n}" for i in range(1, 9) for n in (2, 3)]
    for kp in G.TARGETS:
        text = G.tts_input(kp); words = L.count_words(text)
        ph, _ = L.load(V4_PHRASE % kp); phg, phgain = gained(ph); ph_m = L.measure(V4_PHRASE % kp, 1)
        rows = {}
        for c in cands:
            path = (TONE + f"kp{kp}_explanation_en.wav") if c == "P0v4" else f"{OUT}/audio/kp{kp}_{c}.wav"
            m = L.measure(path, words); x, sr = L.load(path); xg, gx = gained(x)
            m["gain"] = round(gx, 4); m["peak_after_gain"] = round(float(np.max(np.abs(xg))), 4); m["headroom_ok_after_gain"] = bool(m["peak_after_gain"] <= 0.98)
            m["gap_before_s"] = round(ph_m["tail_s"] + PAUSE + m["head_s"], 3); m["gap_after_s"] = round(m["tail_s"] + PAUSE + ph_m["head_s"], 3)
            if c != "P0v4":
                g = glog[(kp, c)][-1]; m["asr"] = {"asr_text": g["asr_text"], "classification": g["classification"], "verified": g["verified"], "attempt": g["attempt"],
                                                  "tts_cost_jpy": g["tts_cost_jpy"], "asr_cost_jpy_est": g["asr_cost_jpy_est"], "model_version": g["model_version"], "style_sha256": g["style_sha256"], "wav_sha256": g["wav_sha256"]}
            # 連続試聴 Phrase->解説->Phrase(Production assembler同一: 0.4s pause、Productionと同じgain rule)
            ps, es = stereo(phg), stereo(xg); sil = np.zeros((int(SR * PAUSE), 2))
            comp = np.concatenate([ps, sil, es, sil, ps])
            pk = float(np.max(np.abs(comp)))
            if pk > 0.98: comp = comp * (0.98 / pk)
            tag = f"kp{kp}_{c}"
            if c in ("P0v4", "P0") or (c[0] == "P" and "r" not in c): to_mp3(comp, f"{PUB}/{tag}_seq.mp3"); to_mp3(es, f"{PUB}/{tag}_solo.mp3")
            m["seq_duration_s"] = round(len(comp) / SR, 3)
            rows[c] = m
        base = rows["P0"]; noise = [rows[k] for k in ("P0", "P0r2", "P0r3")]
        agg = {}
        for pn in ["P0"] + [f"P{i}" for i in range(1, 9)]:
            ms = [rows[pn], rows[pn + "r2"], rows[pn + "r3"]]; mean = lambda k: round(float(np.mean([m[k] for m in ms])), 3)
            agg[pn] = {"n": 3, "core_wpm_mean": mean("speech_wpm_core"), "core_wpm_each": [m["speech_wpm_core"] for m in ms], "wpm500_mean": mean("speech_wpm500"), "wpm_total_mean": mean("wpm_total"),
                       "duration_mean": mean("duration_s"), "mid150_total_mean_s": mean("mid150_total_s"), "mid150_total_each": [m["mid150_total_s"] for m in ms], "mid150_n_each": [m["mid150_n"] for m in ms],
                       "mid_max_each": [max([q["dur"] for q in m["mid150"]], default=0) for m in ms], "gap_before_mean": mean("gap_before_s"), "gap_after_mean": mean("gap_after_s"),
                       "all_asr_verified": all(m["asr"]["verified"] for m in ms), "peak_after_gain_max": max(m["peak_after_gain"] for m in ms)}
        for pn, a in agg.items():
            a["d_core_wpm_pct_vs_P0mean"] = round((a["core_wpm_mean"] / agg["P0"]["core_wpm_mean"] - 1) * 100, 1)
            a["d_wpm_total_pct_vs_P0mean"] = round((a["wpm_total_mean"] / agg["P0"]["wpm_total_mean"] - 1) * 100, 1)
            a["d_duration_s_vs_P0mean"] = round(a["duration_mean"] - agg["P0"]["duration_mean"], 3)
            a["d_mid150_total_s_vs_P0mean"] = round(a["mid150_total_mean_s"] - agg["P0"]["mid150_total_mean_s"], 3)
        for c, m in rows.items():
            m["d_core_wpm_pct"] = round((m["speech_wpm_core"] / base["speech_wpm_core"] - 1) * 100, 1)
            m["d_wpm500_pct"] = round((m["speech_wpm500"] / base["speech_wpm500"] - 1) * 100, 1)
            m["d_wpm_total_pct"] = round((m["wpm_total"] / base["wpm_total"] - 1) * 100, 1)
            m["d_duration_s"] = round(m["duration_s"] - base["duration_s"], 3)
        res[kp] = {"text": text, "words": words, "phrase_gain": round(phgain, 4), "phrase_head_tail": [ph_m["head_s"], ph_m["tail_s"]], "rows": rows, "agg3": agg,
                   "noise_P0_3samples": {"core_wpm": [r["speech_wpm_core"] for r in noise], "duration": [r["duration_s"] for r in noise], "mid150_total_s": [r["mid150_total_s"] for r in noise]}}
    json.dump(res, open(OUT + "/measurements.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for kp, r in res.items():
        print("KP", kp, r["text"], r["words"], "noise", r["noise_P0_3samples"])
        for pn, a in r["agg3"].items(): print("AGG", pn, a)
        for c, m in r["rows"].items():
            if "r" in c[1:] and c != "P0v4": continue
            print(f"{c:5} dur{m['duration_s']:5.2f} coreWPM{m['speech_wpm_core']:6.1f}({m['d_core_wpm_pct']:+5.1f}%) wpm500 {m['speech_wpm500']:6.1f} wpmT {m['wpm_total']:5.1f}({m['d_wpm_total_pct']:+5.1f}%) mid150 n{m['mid150_n']} {m['mid150_total_s']:.2f}s max300 {m['mid300_max_s']:.2f} head{m['head_s']} tail{m['tail_s']} gapB{m['gap_before_s']} gapA{m['gap_after_s']} pk{m['peak_after_gain']}")
if __name__ == "__main__": main()
