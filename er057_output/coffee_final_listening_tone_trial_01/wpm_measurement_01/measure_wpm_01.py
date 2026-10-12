# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-ADVANCED-FULLSTORY-WPM-MEASUREMENT-01 委任_01 測定script(read-only、API費用0、Trial)。
実行: PYTHONUTF8=1 .venv/Scripts/python.exe er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py
Productionコード・音声・Prompt・Master Storeは変更しない。出力は同ディレクトリの wpm_results_01.json のみ。"""
import os, sys, re, json, hashlib, difflib
import numpy as np, soundfile as sf

ROOT = "C:/Users/tensh/eigo-radio"
sys.path.insert(0, ROOT)
BASE = f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01"
SEG = f"{BASE}/part_final/segments"
OUT = f"{BASE}/wpm_measurement_01"
TONE = "C:/Users/tensh/eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01"
FRAME_MS, HOP_MS = 20, 10
THRESH_DB = -40.0
MIN_PAUSE_MS = (300, 500)

ADV = {1: ("adv_part1_f5.wav", "5b711b91e99a89f4"), 2: ("adv_part2_f5.wav", "2d7c291b5abb6bd9"), 3: ("adv_part3_f5.wav", "fa1f978f68eaef81")}
STD = {1: ("std_part1_f5_slow6.wav", "590c61604404"), 2: ("std_part2_f5_slow6.wav", "9e18c8acf88a"), 3: ("std_part3_f5_slow6.wav", "178e13cdabef")}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---- 語数 ----
def count_primary(text):
    """空白区切りトークンのうち英数字を1文字以上含むもの。ハイフン語・縮約形・数字記号付き語は1語。"""
    return sum(1 for t in text.split() if re.search(r"[A-Za-z0-9]", t))


def count_alt(text):
    """代替: ハイフン/ダッシュ/スラッシュでも分割(ハイフン語=複数語)。"""
    t = re.sub(r"[\u2010-\u2015/-]", " ", text)
    return sum(1 for x in t.split() if re.search(r"[A-Za-z0-9]", x))


def norm_words(text):
    t = text.lower().replace("\u2019", "'")
    t = re.sub(r"[\u2010-\u2015-]", " ", t)
    t = re.sub(r"[^a-z0-9' $%.]", " ", t)
    t = re.sub(r"(?<![0-9])\.|\.(?![0-9])", " ", t)
    return t.split()


# ---- 無音/ポーズ ----
def frame_rms_db(x, sr):
    f, h = int(sr * FRAME_MS / 1000), int(sr * HOP_MS / 1000)
    n = max(0, (len(x) - f) // h + 1)
    db = np.empty(n)
    for i in range(n):
        s = x[i * h:i * h + f]
        r = float(np.sqrt(np.mean(s * s))) if len(s) else 0.0
        db[i] = 20 * np.log10(max(r, 1e-10))
    return db


def find_pauses(db, min_ms, dur):
    sil = db < THRESH_DB
    res, i, n = [], 0, len(sil)
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            s, e = i * HOP_MS / 1000, min(dur, (j - 1) * HOP_MS / 1000 + FRAME_MS / 1000)
            if (e - s) * 1000 >= min_ms:
                res.append({"start": round(s, 3), "end": round(e, 3), "dur": round(e - s, 3),
                            "edge": "head" if i == 0 else ("tail" if j >= n else "mid")})
            i = j
        else:
            i += 1
    return res


# ---- ASR ----
def asr(wav, model_name):
    from faster_whisper import WhisperModel
    m = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, info = m.transcribe(wav, language="en", word_timestamps=True, beam_size=5, vad_filter=False,
                              condition_on_previous_text=False)
    words = []
    for s in segs:
        for w in s.words:
            words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    return words


def diff_report(ref_words, asr_words):
    a = ref_words
    b = norm_words(" ".join(w["w"] for w in asr_words))
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = [(t, " ".join(a[i1:i2]), " ".join(b[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
    return {"ratio": round(sm.ratio(), 4), "ref_n": len(a), "asr_n": len(b),
            "diffs": [{"op": t, "ref": r, "asr": s} for t, r, s in ops]}


def neighbours(asr_words, t0, t1):
    prev = [w for w in asr_words if w["e"] <= t0 + 0.15]
    nxt = [w for w in asr_words if w["s"] >= t1 - 0.15]
    return (" ".join(w["w"] for w in prev[-3:]) or "(start)", " ".join(w["w"] for w in nxt[:3]) or "(end)")


def sentences(asr_words):
    out, cur = [], []
    for w in asr_words:
        cur.append(w)
        if re.search(r"[.!?][\"')]*$", w["w"]) and not re.fullmatch(r"\d+\.", w["w"]):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def window_wpm(asr_words, pauses, dur, win=10.0, step=1.0):
    res = []
    t = 0.0
    while t + win <= dur + 1e-6:
        n = sum(1 for w in asr_words if t <= (w["s"] + w["e"]) / 2 < t + win)
        p = 0.0
        for q in pauses:
            p += max(0.0, min(q["end"], t + win) - max(q["start"], t))
        sp = win - p
        res.append({"t0": round(t, 1), "n": n, "wpm_all": round(n / win * 60, 1),
                    "wpm_speech": round(n / sp * 60, 1) if sp > 1 else None})
        t += step
    return res


def main():
    adv_parts = json.load(open(f"{TONE}/b1b/parts.json", encoding="utf-8"))
    std_parts = json.load(open(f"{TONE}/a2/parts.json", encoding="utf-8"))
    import er003_v1_n3_01_tts_generate as n3
    R = {"threshold_dbfs": THRESH_DB, "frame_ms": FRAME_MS, "hop_ms": HOP_MS, "min_pause_ms": list(MIN_PAUSE_MS),
         "adv": {}, "std": {}}
    for n in (1, 2, 3):
        fn, shp = ADV[n]
        path = f"{SEG}/{fn}"
        s = sha(path)
        assert s.startswith(shp), (fn, s)
        x, sr = sf.read(path, dtype="float32")
        if x.ndim > 1:
            x = x.mean(axis=1)
        dur = len(x) / sr
        raw = adv_parts[f"part{n}"]
        safe = n3.tts_safe_news_en(raw)
        d = {"wav": fn, "sha256": s, "sr": sr, "duration_s": round(dur, 3),
             "words": {"manuscript_primary": count_primary(raw), "manuscript_alt_hyphen_split": count_alt(raw),
                       "tts_safe_primary": count_primary(safe), "tts_safe_alt_hyphen_split": count_alt(safe),
                       "manuscript_sha12": hashlib.sha256(raw.encode()).hexdigest()[:12],
                       "tts_input_sha12": hashlib.sha256(safe.encode()).hexdigest()[:12],
                       "tts_safe_differs": raw != safe},
             "pause_sens": {}}
        wc = count_primary(safe)  # 採用: TTSが実際に読んだ入力(tts_safe適用後)
        d["words_adopted"] = wc
        d["wpm_overall"] = round(wc / dur * 60, 1)
        db = frame_rms_db(x, sr)
        aw = {m: asr(path, m) for m in ("medium", "small")}
        d["asr"] = {m: {"diff_vs_tts_safe": diff_report(norm_words(safe), aw[m]),
                        "diff_vs_manuscript": diff_report(norm_words(raw), aw[m])} for m in aw}
        d["asr_medium_words_n"] = len(aw["medium"])
        for mp in MIN_PAUSE_MS:
            ps = find_pauses(db, mp, dur)
            mid = [p for p in ps if p["edge"] == "mid"]
            edge = [p for p in ps if p["edge"] != "mid"]
            tot = sum(p["dur"] for p in ps)
            speech = dur - tot
            for p in ps:
                p["before"], p["after"] = neighbours(aw["medium"], p["start"], p["end"])
            d["pause_sens"][str(mp)] = {"n_all": len(ps), "n_mid": len(mid), "total_all_s": round(tot, 3),
                                        "total_mid_s": round(sum(p["dur"] for p in mid), 3),
                                        "edge_s": round(sum(p["dur"] for p in edge), 3),
                                        "speech_s": round(speech, 3), "wpm_speech": round(wc / speech * 60, 1),
                                        "pauses": ps}
        d["windows10s"] = window_wpm(aw["medium"], d["pause_sens"]["300"]["pauses"], dur)
        sents = []
        for sw in sentences(aw["medium"]):
            t0, t1 = sw[0]["s"], sw[-1]["e"]
            if t1 - t0 > 0.5:
                sents.append({"t0": t0, "t1": t1, "n": len(sw), "wpm": round(len(sw) / (t1 - t0) * 60, 1),
                              "text": " ".join(w["w"] for w in sw)})
        d["sentences"] = sents
        d["asr_words_medium"] = aw["medium"]
        R["adv"][str(n)] = d
        print("adv", n, round(dur, 2), wc, d["wpm_overall"], d["pause_sens"]["500"]["wpm_speech"], flush=True)
    for n in (1, 2, 3):
        fn, shp = STD[n]
        path = f"{SEG}/{fn}"
        s = sha(path)
        assert s.startswith(shp), (fn, s)
        info = sf.info(path)
        dur = info.frames / info.samplerate
        safe = n3.tts_safe_news_en(std_parts[f"part{n}"])
        R["std"][str(n)] = {"wav": fn, "sha256": s, "duration_s": round(dur, 3),
                            "words_tts_safe_primary": count_primary(safe),
                            "wpm_overall": round(count_primary(safe) / dur * 60, 1)}
    json.dump(R, open(f"{OUT}/wpm_results_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved")


main()
