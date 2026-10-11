# -*- coding: utf-8 -*-
"""委任_03 Trial assembler(Production非経由)。
er019 runnerの純関数 apply_family_x_{a2,b1}_gain / build_family_x_{a2,b1}_timeline と
asm.assemble_with_timeline / asm.apply_headroom_safety_valve をそのまま呼び、role->wavだけ差替える。
Gate(verify_episode_audio_validation_gate)はProduction run dir/auditに依存するため呼ばない(同等チェックを cmd_qa で計算)。
"""
from __future__ import annotations
import os, sys, json, hashlib, subprocess, tempfile
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03 as B
import er019_family_x_audio_production_runner_01 as run
import er003_v1_n3_01_assemble as asm
import er003_b1_p9a_audio as p9a
import er002_common as common
import imageio_ffmpeg

TONE, OUT, SEG, AEF, BCD = B.TONE, B.OUT, B.SEG, B.AEF, B.BCD
FINAL = os.path.join(OUT, "final")
SR = asm.SR
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rd(path):
    mono, sr, _, _ = common.read_wav_float(path)
    assert sr == common.SAMPLE_RATE, (path, sr)
    return mono


def std_overrides(extra=None):
    """Standard: role名 -> (wav path, origin, style)。origin: T=Trial生成済み / R=本委任F5再生成。"""
    o = {"welcome": (f"{AEF}/raw/A5.wav", "T", "A5"), "preview_intro": (f"{AEF}/raw/B5.wav", "T", "B5"),
         "preview": (f"{BCD}/raw/P2_preview.wav", "T", "P2")}
    for i in range(1, 6):
        o[f"meaning_{i}"] = (f"{BCD}/raw/M2_kp{i}.wav", "T", "M2")
        o[f"kp{i}_en"] = (f"{BCD}/raw/K2_kp{i}.wav", "T", "K2")
    for n in range(1, 5):
        o[f"comment_{n}"] = (f"{BCD}/raw/P2_comment_{n}.wav", "T", "P2")
    for n in range(1, 4):
        o[f"full_story_part{n}"] = (f"{SEG}/std_part{n}_f5_slow6.wav", "R", "F5+6%減速")
    if extra:
        o.update(extra)
    return o


def adv_overrides(extra=None):
    o = {"welcome_charon": (f"{AEF}/raw/A5.wav", "T", "A5"), "preview_intro_charon": (f"{AEF}/raw/B5.wav", "T", "B5"),
         "preview": (f"{AEF}/raw/E1.wav", "T", "E1")}
    for n in range(1, 4):
        o[f"full_story_part{n}"] = (f"{SEG}/adv_part{n}_f5.wav", "R", "F5")
    if extra:
        o.update(extra)
    return o


class Loader:
    def __init__(self, level, ov):
        self.level, self.ov = level, ov
        self.dir = f"{TONE}/{'a2' if level == 'std' else 'b1b'}/narration"
        self.prov = {}

    def get(self, name):
        if name in self.ov:
            p, origin, style = self.ov[name]
            self.prov[name] = {"origin": origin, "style": style, "path": p, "sha256": sha(p)}
            return rd(p)
        p = f"{self.dir}/{name}.wav"
        self.prov[name] = {"origin": "P", "style": "既存承認(変更なし)", "path": p, "sha256": sha(p)}
        return rd(p)


def std_sources(ov):
    L = Loader("std", ov)
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    preview_mono = L.get("preview")
    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "num_one", "num_two", "num_three", "num_four", "num_five",
                 "topic_intro", "japanese_title"):
        narration[name] = L.get(name)
    kp = json.load(open(f"{TONE}/a2/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    comps = {}
    for i, it in enumerate(kp_items, start=1):
        comps[it["rank"]] = L.get(f"kp{it['rank']}_en")
        narration[f"meaning_{i}"] = L.get(f"meaning_{i}")
    segs = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4", "full_story_part1", "full_story_part2", "full_story_part3", "in_one_line"):
        segs[name] = L.get(name)
    return ({"intro": intro, "notification": notification, "outro": outro, "preview_mono": preview_mono, "narration": narration,
             "key_phrase_components": comps, "a2_segments": segs, "kp_items": kp_items}, L.prov)


def adv_sources(ov):
    L = Loader("adv", ov)
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        narration[name] = L.get(f"{name}_charon")
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        narration[name] = L.get(f"{name}_charon")
    narration["topic_intro"] = L.get("topic_intro")
    b1 = {}
    for name in ("full_story_part1", "full_story_part2", "full_story_part3", "comment_1", "comment_2", "comment_3", "comment_4", "preview", "in_one_line"):
        b1[name] = L.get(name)
    kp = json.load(open(f"{TONE}/b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    comps, means = {}, {}
    for it in kp_items:
        r = it["rank"]
        comps[r] = L.get(f"kp{r}_en")
        means[r] = L.get(f"kp{r}_explanation_en")
    return ({"intro": intro, "notification": notification, "outro": outro, "narration": narration, "b1_segments": b1,
             "key_phrase_components": comps, "key_phrase_meanings": means, "kp_items": kp_items}, L.prov)


def assemble_level(level, ov):
    if level == "std":
        src, prov = std_sources(ov)
        parts = run.apply_family_x_a2_gain(src)
        seq = run.build_family_x_a2_timeline(parts)
    else:
        src, prov = adv_sources(ov)
        parts = run.apply_family_x_b1_gain(src)
        seq = run.build_family_x_b1_timeline(parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    return {"assembled": headroom["assembled"], "timeline": result["timeline"], "headroom": headroom["report"],
            "gain_report": parts["gain_report"], "prov": prov, "total_duration_seconds": result["total_duration_seconds"]}


def cmd_regress():
    """既存音声のみで組立て、既存完成版wavと一致するか(assembler回帰)。"""
    res = {}
    for level, d, fn in (("std", "a2", "Family_X_Audio_A2_COFFEE_PRICES__RUN_E_TONE_01.wav"), ("adv", "b1b", "Family_X_Audio_B1_COFFEE_PRICES__RUN_E_TONE_01.wav")):
        r = assemble_level(level, {})
        ex_path = f"{TONE}/{d}/assembled/{fn}"
        if not os.path.exists(ex_path):
            import glob
            ex_path = glob.glob(f"{TONE}/{d}/assembled/*.wav")[0]
        tmp = os.path.join(OUT, f"regress_{level}.wav")
        common.write_wav_float(tmp, r["assembled"], SR, 2)
        a, sra = sf.read(tmp, dtype="float64"); b, srb = sf.read(ex_path, dtype="float64")
        same_len = a.shape == b.shape
        mx = float(np.max(np.abs(a - b))) if same_len else None
        res[level] = {"existing": ex_path.replace("C:/Users/tensh/", ""), "sha_existing": sha(ex_path), "sha_trial_assembler": sha(tmp),
                      "byte_identical": sha(tmp) == sha(ex_path), "same_shape": same_len, "shape": [list(a.shape), list(b.shape)],
                      "max_abs_diff": mx, "sr": [sra, srb]}
        # 後続ディスク節約のためregress wavは残さない
        os.remove(tmp)
        print(level, res[level])
    json.dump(res, open(os.path.join(OUT, "regression_check_03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def to_mp3(stereo, out_path, br="128k"):
    tmp = os.path.join(tempfile.gettempdir(), f"er057_03_{os.getpid()}_{abs(hash(out_path))}.wav")
    sf.write(tmp, np.clip(stereo, -1, 1), SR, subtype="PCM_16")
    r = subprocess.run([FFMPEG, "-y", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out_path], capture_output=True, text=True)
    os.remove(tmp)
    assert r.returncode == 0, r.stderr[-400:]


def cmd_assemble(tag="final"):
    """Standard/Advanced完成版を組立て(wav+mp3)、timeline/gain/headroom/由来をmanifestへ。"""
    os.makedirs(FINAL, exist_ok=True)
    extra_std, extra_adv = {}, {}
    ex = os.path.join(OUT, "extra_overrides_03.json")
    if os.path.exists(ex):
        e = json.load(open(ex, encoding="utf-8"))
        extra_std = {k: tuple(v) for k, v in e.get("std", {}).items()}
        extra_adv = {k: tuple(v) for k, v in e.get("adv", {}).items()}
    man = {"tag": tag, "levels": {}}
    for level, ov in (("std", std_overrides(extra_std)), ("adv", adv_overrides(extra_adv))):
        r = assemble_level(level, ov)
        name = "Coffee_Standard_final_v2" if level == "std" else "Coffee_Advanced_final_v2"
        wavp, mp3p = os.path.join(FINAL, name + ".wav"), os.path.join(FINAL, name + ".mp3")
        common.write_wav_float(wavp, r["assembled"], SR, 2)
        to_mp3(r["assembled"], mp3p)
        metrics = common.measure_metrics(r["assembled"][:, 0], SR)
        man["levels"][level] = {"wav": os.path.relpath(wavp, ROOT).replace("\\", "/"), "wav_sha256": sha(wavp),
                                 "mp3": os.path.relpath(mp3p, ROOT).replace("\\", "/"), "mp3_sha256": sha(mp3p),
                                 "duration_seconds": r["total_duration_seconds"], "peak": round(p9a.peak(r["assembled"]), 5),
                                 "clipping_detected": metrics["clipping_detected"], "headroom": r["headroom"], "gain_report": r["gain_report"],
                                 "timeline": r["timeline"], "provenance": r["prov"], "metrics": {k: (v if isinstance(v, (int, float, bool, str)) else str(v)) for k, v in metrics.items()}}
        print(level, r["total_duration_seconds"], man["levels"][level]["peak"], metrics["clipping_detected"])
    json.dump(man, open(os.path.join(OUT, f"assembly_manifest_03_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def cmd_qa():
    """完成版QA(Audio Validation Gate相当チェックをTrial隔離で計算): peak/clipping/headroom/長さ/timeline整合/内部無音/RMS/mp3整合。"""
    man = json.load(open(os.path.join(OUT, "assembly_manifest_03_final.json"), encoding="utf-8"))
    qa = {}
    for level, L in man["levels"].items():
        x, sr = sf.read(os.path.join(ROOT, L["wav"]), dtype="float64")
        tl = L["timeline"]
        total_tl = sum(e["duration_seconds"] for e in tl)
        peak = float(np.max(np.abs(x)))
        clip_n = int(np.sum(np.abs(x) >= 0.999))
        # 内部の長い無音(デジタル0 or <-60dB)がpause以外のpartに無いか
        mono = x.mean(axis=1)
        win = int(0.01 * sr)
        n = len(mono) // win
        rms = np.sqrt((mono[:n * win].reshape(n, win) ** 2).mean(axis=1))
        silent = rms < 10 ** (-60 / 20)
        long_sil = []
        for e in tl:
            if e["part"].startswith("pause") or e["part"] in ("Intro", "Outro"):
                continue
            a, b = int(e["start_seconds"] * 100), int((e["start_seconds"] + e["duration_seconds"]) * 100)
            run = best = 0
            for v in silent[a:b]:
                run = run + 1 if v else 0
                best = max(best, run)
            if best * 0.01 > 1.0:
                long_sil.append({"part": e["part"], "longest_silence_s": best * 0.01})
        mp3_dur = sf.info(os.path.join(ROOT, L["mp3"])).duration
        part_db = {}
        for e in tl:
            if e["part"].startswith("pause"):
                continue
            a, b = int(e["start_seconds"] * sr), int((e["start_seconds"] + e["duration_seconds"]) * sr)
            seg = mono[a:b]
            part_db[e["part"]] = round(float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)), 1)
        qa[level] = {"wav_seconds": round(len(x) / sr, 3), "timeline_total_seconds": round(total_tl, 3), "len_matches_timeline": abs(len(x) / sr - total_tl) < 0.02,
                     "mp3_seconds": round(mp3_dur, 3), "sr": sr, "channels": x.shape[1], "peak": round(peak, 5), "clipping_samples(|x|>=0.999)": clip_n,
                     "headroom_safety_valve": L["headroom"], "headroom_threshold_ok": peak <= 0.98, "long_internal_silence_gt1s": long_sil,
                     "target_rms": L["gain_report"].get("target_rms"), "part_rms_db": part_db}
        print(level, {k: v for k, v in qa[level].items() if k not in ("part_rms_db",)})
    json.dump(qa, open(os.path.join(OUT, "qa_03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
