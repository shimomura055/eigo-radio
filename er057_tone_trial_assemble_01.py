# ============================================================
# er057_tone_trial_assemble_01.py  (Trial専用、委任_01A)
# 生成済みraw wav + 既存run dir(read-only)の既存音声から、試聴用mp3(通し・単独)を作る。
# Production成果物へは書き込まない。出力: user_test/coffee_tone_trial_01/intro_preview_fullstory/audio/
# ============================================================
from __future__ import annotations
import hashlib, json, os, subprocess, tempfile, wave
import numpy as np
import soundfile as sf
import imageio_ffmpeg

import er057_tone_trial_tts_gen_01 as G
import er003_b1_p9a_audio as p9a
import er002_common as common
import er008_a2_postprocess_slowdown_01 as slowdown

RUN = G.RUN if hasattr(G, "RUN") else None
RUN = "C:/Users/tensh/eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01"
WEB = os.path.join(G.ROOT, "user_test", "coffee_tone_trial_01", "intro_preview_fullstory")
AUD = os.path.join(WEB, "audio")
SLOW = os.path.join(G.OUT, "slowed_6pct")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = p9a.TARGET_SAMPLE_RATE


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rd(path):
    mono, sr, _, _ = common.read_wav_float(path)
    assert sr == common.SAMPLE_RATE, (path, sr)
    return mono


def to_mp3(stereo, name):
    os.makedirs(AUD, exist_ok=True)
    tmp = os.path.join(tempfile.gettempdir(), f"er057_{name}.wav")
    sf.write(tmp, np.clip(stereo, -1, 1), SR, subtype="PCM_16")
    out = os.path.join(AUD, name + ".mp3")
    r = subprocess.run([FFMPEG, "-y", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "128k", out], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-500:]
    os.remove(tmp)
    return round(len(stereo) / SR, 3)


def main():
    os.makedirs(AUD, exist_ok=True); os.makedirs(SLOW, exist_ok=True)
    man = {"sources_readonly": {}, "items": {}, "gain": {}}
    src = {
        "welcome": f"{RUN}/a2/narration/welcome.wav", "preview_intro": f"{RUN}/a2/narration/preview_intro.wav",
        "topic_intro": f"{RUN}/a2/narration/topic_intro.wav", "japanese_title": f"{RUN}/a2/narration/japanese_title.wav",
        "a2_preview": f"{RUN}/a2/narration/preview.wav", "a2_part1": f"{RUN}/a2/narration/full_story_part1.wav",
        "b1b_preview": f"{RUN}/b1b/narration/preview.wav", "b1b_part1": f"{RUN}/b1b/narration/full_story_part1.wav",
    }
    for k, p in src.items():
        man["sources_readonly"][k] = {"path": p.replace("C:/Users/tensh/", ""), "sha256": sha(p)}
    W = {k: rd(p) for k, p in src.items()}
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)["samples"]
    notif = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)["samples"]
    # runner(apply_family_x_a2_gain)と同じ: target_rms = (Standard preview + Standard part1)/2
    target = (p9a.rms(W["a2_preview"]) + p9a.rms(W["a2_part1"])) / 2
    man["target_rms"] = round(target, 5)

    def gain_stereo_from_mono(mono, label):
        g = p9a.compute_gain_for_target_rms(mono, target)
        man["gain"][label] = round(float(g), 4)
        return p9a.mono_24k_to_stereo_target(mono * g)

    def gain_stereo(st, label):
        g = p9a.compute_gain_for_target_rms(st, target)
        man["gain"][label] = round(float(g), 4)
        return st * g

    intro_g = gain_stereo(intro, "intro"); notif_g = gain_stereo(notif, "notification")
    topic = gain_stereo_from_mono(W["topic_intro"], "topic_intro")
    jtitle = gain_stereo_from_mono(W["japanese_title"], "japanese_title")
    sil = p9a.silence_stereo

    # --- A / B ---
    A = {"A0": gain_stereo_from_mono(W["welcome"], "A0")}
    B = {"B0": gain_stereo_from_mono(W["preview_intro"], "B0")}
    for i in range(1, 6):
        A[f"A{i}"] = gain_stereo_from_mono(rd(f"{G.RAW}/A{i}.wav"), f"A{i}")
        B[f"B{i}"] = gain_stereo_from_mono(rd(f"{G.RAW}/B{i}.wav"), f"B{i}")
    for k, v in {**A, **B}.items():
        man["items"][k] = {"seconds": to_mp3(v, k)}
    # 通し(runner build_family_x_a2_timelineと同じ順序・pause): Intro, Welcome, .5, Topic, .65, JA title, .5, Notification1, .4, Preview intro, .65
    mid = np.concatenate([sil(0.5), topic, sil(0.65), jtitle, sil(0.5), notif_g, sil(0.4)])
    tail = sil(0.65)
    man["items"]["part_head"] = {"seconds": to_mp3(intro_g, "part_head")}
    man["items"]["part_mid"] = {"seconds": to_mp3(mid, "part_mid")}
    man["items"]["part_tail"] = {"seconds": to_mp3(tail, "part_tail")}
    for n in range(0, 6):
        full = np.concatenate([intro_g, A[f"A{n}"], mid, B[f"B{n}"], tail])
        man["items"][f"pattern_{n}"] = {"seconds": to_mp3(full, f"pattern_{n}")}
    # --- E ---
    man["items"]["E0"] = {"seconds": to_mp3(gain_stereo_from_mono(W["b1b_preview"], "E0"), "E0")}
    for i in range(1, 6):
        man["items"][f"E{i}"] = {"seconds": to_mp3(gain_stereo_from_mono(rd(f"{G.RAW}/E{i}.wav"), f"E{i}"), f"E{i}")}
    # --- F (Advanced相当 + Standard相当6%減速) ---
    man["items"]["F_existing_adv"] = {"seconds": to_mp3(gain_stereo_from_mono(W["b1b_part1"], "F_existing_adv"), "F_existing_adv")}
    man["items"]["F_existing_std"] = {"seconds": to_mp3(gain_stereo_from_mono(W["a2_part1"], "F_existing_std"), "F_existing_std")}
    for k in ["F0", "F1", "F2", "F3", "F4", "F5", "F0S"]:
        raw = f"{G.RAW}/{k}.wav"
        if k != "F0S":
            man["items"][k] = {"seconds": to_mp3(gain_stereo_from_mono(rd(raw), k), k)}
        slowed = f"{SLOW}/{k}_slow6.wav"
        info = slowdown.apply_a2_slowdown(raw, slowed)   # Production既存処理: FFmpeg atempo 6%
        man["items"][f"{k}_std"] = {"seconds": to_mp3(gain_stereo_from_mono(rd(slowed), f"{k}_std"), f"{k}_std"), "slowdown": info}
    man["slowdown_process"] = "er008_a2_postprocess_slowdown_01.apply_a2_slowdown (FFmpeg atempo=1/1.06, A2_SLOWDOWN_PERCENT=6.0)"
    for k in ("F0S",):   # F0Sは生成時点で減速指示付き。単独advは作らずstdのみ
        pass
    json.dump(man, open(os.path.join(G.OUT, "assembly_manifest_01A.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v["seconds"] for k, v in man["items"].items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
