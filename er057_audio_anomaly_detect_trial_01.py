# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01C §5: 異音・音声途切れ検知Trial(無料ローカル解析のみ)。

DEV/Trial専用。Production Validator/Gate/Prompt/Routingには一切接続しない(import元もProductionから参照されない)。
API呼出なし(numpy/scipy/soundfile/lameenc/Pillow + 既に取得済みのlocal faster-whisper word timestamps JSONのみ使用)。

検知器(すべて閾値は本ファイル冒頭の定数。ユーザー確認用の「候補」を出すだけで確定はしない):
  clip        : |x|>=CLIP_LEVEL が3サンプル以上連続(音割れ/飽和)。peak>PEAK_WARN は参考(low)。
  click       : 2階差分の局所比(スパイク)が大きく、かつ衝撃的(±1msにエネルギーが集中)。
  dropout     : 発話区間内部のデジタル無音(厳密に0の連続)または急峻な無音化。
  long_gap    : 発話区間内部の長い無音(自然な段落間ポーズを超える)。
  edge_abrupt : segment先頭/末尾が減衰なしで急に始まる/切れる(語頭語末欠落の疑い)。
  level_step  : 無音を挟まずに短時間RMSが階段状に急変(音量の急変)。
  spec_jump   : 発話中の急峻なスペクトル変化(スプライス/グリッチ疑い)。
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import time

import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d, maximum_filter1d

ROOT = os.path.dirname(os.path.abspath(__file__))
P45 = os.path.join(ROOT, "er057_output", "coffee_final_listening_tone_trial_01", "part_45")
SNAP = os.path.join(P45, "evidence_snapshot")

# ---- 閾値(Trial値。Production採用時は別途Trial/承認が必要) ----
CLIP_LEVEL = 0.985
CLIP_MIN_RUN = 3
PEAK_WARN = 0.99
CLICK_RATIO = 40.0          # |d2| / 局所中央値(5ms区間の中央値の近傍最大)
CLICK_ABS_MIN = 0.06        # |d2|の絶対下限
CLICK_ISOLATION = 0.55      # ±1ms内エネルギー/±8ms内エネルギー
DROPOUT_ZERO_MS = 4.0       # 厳密0(|x|<1e-5)がこの長さ以上
DROPOUT_ABRUPT_DB = -30.0   # 零区間の前後5msのRMSが発話p95基準でこれ以上なら『発話中の急な欠落』
GAP_MEDIUM_S = 1.0
GAP_LOW_S = 0.8
EDGE_HEAD_DB = -22.0        # 先頭20ms RMS(発話中央値RMS基準 dB)
EDGE_TAIL_DB = -22.0
STEP_DB = 10.0              # 直前1.2sと直後1.2sの発話フレームRMS中央値差
LEVEL_WIN_S = 1.2
STEP_STABLE_DB = 4.5
STEP_MIN_LEVEL_DB = -34.0   # 両側とも発話レベル(全体発話p90基準 dB)以上
SPEC_JUMP_Z = 8.0


def db(v):
    return 20 * np.log10(np.maximum(v, 1e-9))


def frame_rms(x, sr, win_ms, hop_ms):
    win = max(1, int(sr * win_ms / 1000)); hop = max(1, int(sr * hop_ms / 1000))
    cs = np.concatenate([[0.0], np.cumsum(x.astype(np.float64) ** 2)])
    starts = np.arange(0, max(1, len(x) - win + 1), hop)
    rms = np.sqrt((cs[starts + win] - cs[starts]) / win)
    return starts / sr, rms


def mono(x):
    return x.mean(axis=1) if x.ndim == 2 else x


def runs(mask, min_len):
    """Trueの連続区間[(start_idx, end_idx_exclusive)]のうちmin_len以上。"""
    m = np.concatenate([[0], mask.astype(np.int8), [0]])
    d = np.diff(m)
    st = np.where(d == 1)[0]; en = np.where(d == -1)[0]
    return [(int(s), int(e)) for s, e in zip(st, en) if e - s >= min_len]


def speech_frames(x, sr):
    """20ms窓/10ms hopのRMS dBと発話マスク(動的閾値: p95 - 40dB を下限-60dBで)。"""
    t, r = frame_rms(x, sr, 20, 10)
    d = db(r)
    ref = float(np.percentile(d, 95)) if len(d) else -60.0
    thr = max(ref - 40.0, -60.0)
    return t, d, d > thr, ref, thr


def detect_clip(x, sr, name):
    out = []
    mask = np.abs(x) >= CLIP_LEVEL
    for s, e in runs(mask, CLIP_MIN_RUN):
        out.append(dict(symptom="clip", t=s / sr, dur=(e - s) / sr, confidence="high" if (e - s) >= 6 else "medium",
                        metrics=dict(run_samples=e - s, peak=float(np.max(np.abs(x[s:e]))))))
    pk = float(np.max(np.abs(x)))
    if pk > PEAK_WARN and not out:
        i = int(np.argmax(np.abs(x)))
        out.append(dict(symptom="clip", t=i / sr, dur=0.0, confidence="low", metrics=dict(peak=pk, note="peak>%.2f(連続clipなし)" % PEAK_WARN)))
    return out


def detect_click(x, sr, name):
    """2階差分|d2|が『5ms区間の中央値(ロバストな局所スケール)』の CLICK_RATIO 倍以上、かつ±1msへ集中(衝撃的)。"""
    if len(x) < 100:
        return []
    d2 = np.diff(x.astype(np.float64), 2)
    a = np.abs(d2)
    blk = max(1, int(0.005 * sr))
    nb = len(a) // blk
    if nb < 4:
        return []
    med_b = np.median(a[: nb * blk].reshape(nb, blk), axis=1)
    med_b = maximum_filter1d(med_b, size=5, mode="nearest")           # 近傍5ブロック(25ms)の最大中央値=局所スケール
    scale = np.repeat(med_b, blk)
    scale = np.concatenate([scale, np.full(len(a) - len(scale), med_b[-1])])
    scale = np.maximum(scale, 1e-3)
    ratio = a / scale
    cand = np.where((ratio >= CLICK_RATIO) & (a >= CLICK_ABS_MIN))[0]
    out = []
    last = -10 ** 9
    e2 = d2 ** 2
    cs = np.concatenate([[0.0], np.cumsum(e2)])
    for i in cand:
        if i - last < int(0.005 * sr):
            continue
        r1 = int(0.001 * sr)
        r8 = int(0.008 * sr)
        lo1, hi1 = max(0, i - r1), min(len(e2), i + r1 + 1)
        lo8, hi8 = max(0, i - r8), min(len(e2), i + r8 + 1)
        iso = (cs[hi1] - cs[lo1]) / max(cs[hi8] - cs[lo8], 1e-12)
        if iso < CLICK_ISOLATION:
            continue
        last = i
        conf = "high" if (ratio[i] >= 100 and a[i] >= 0.1) else ("medium" if ratio[i] >= 60 else "low")
        out.append(dict(symptom="click", t=(i + 1) / sr, dur=0.0, confidence=conf,
                        metrics=dict(ratio=round(float(ratio[i]), 1), abs_d2=round(float(a[i]), 4), isolation=round(float(iso), 3))))
    return out


def detect_dropout_and_gaps(x, sr, name, is_segment=True):
    out = []
    t, d, sp, ref, thr = speech_frames(x, sr)
    if not sp.any():
        return out, dict(ref_db=ref, thr_db=thr, speech_start=None, speech_end=None)
    s0 = int(np.argmax(sp)); s1 = len(sp) - int(np.argmax(sp[::-1]))
    inner = ~sp[s0:s1]
    # long gaps (frames hop 10ms)。assembled(is_segment=False)は設計上のポーズを含むため対象外。
    if is_segment:
        for a, b in runs(inner, int(GAP_LOW_S / 0.01)):
            gdur = (b - a) * 0.01
            conf = "medium" if gdur >= GAP_MEDIUM_S else "low"
            out.append(dict(symptom="long_gap", t=float(t[s0 + a]), dur=round(gdur, 3), confidence=conf,
                            metrics=dict(gap_seconds=round(gdur, 3), silence_thr_db=round(thr, 1))))
    # digital zero dropouts inside speech region。TTSは文間/語間のポーズを厳密0で出力することがあり
    # (前後が減衰して無音=自然なポーズ)、それは候補にしない。発話レベルのまま急に0へ落ち/0から立ち上がる
    # (前後5msのRMSが発話p95 -30dB以内)ものだけを候補にする。
    xs = x[int(t[s0] * sr): int(t[min(s1, len(t) - 1)] * sr)]
    off = int(t[s0] * sr)
    z = np.abs(xs) < 1e-5
    w5 = max(1, int(0.005 * sr))
    natural = 0
    for a, b in runs(z, int(DROPOUT_ZERO_MS / 1000 * sr)):
        ga, gb = off + a, off + b
        pre = db(np.sqrt(np.mean(x[max(0, ga - w5):ga] ** 2))) - ref if ga > 0 else -99
        post = db(np.sqrt(np.mean(x[gb:gb + w5] ** 2))) - ref if gb < len(x) else -99
        if max(pre, post) >= DROPOUT_ABRUPT_DB:
            out.append(dict(symptom="dropout", t=ga / sr, dur=(gb - ga) / sr,
                            confidence="high" if min(pre, post) >= DROPOUT_ABRUPT_DB else "medium",
                            metrics=dict(zero_run_ms=round((gb - ga) / sr * 1000, 2), pre5ms_rel_db=round(float(pre), 1), post5ms_rel_db=round(float(post), 1))))
        else:
            natural += 1
    return out, dict(ref_db=float(ref), thr_db=float(thr), speech_start=float(t[s0]), speech_end=float(t[min(s1, len(t) - 1)] + 0.02), natural_zero_runs=natural)


def detect_edges(x, sr, name, info):
    out = []
    if info["speech_start"] is None:
        return out
    t, r = frame_rms(x, sr, 20, 10)
    d = db(r)
    med = float(np.median(d[d > info["thr_db"]])) if (d > info["thr_db"]).any() else info["ref_db"]
    head = d[0]; tail = d[-1]
    if head - med > EDGE_HEAD_DB:
        out.append(dict(symptom="edge_abrupt", t=0.0, dur=0.02, confidence="medium", metrics=dict(edge="head", level_rel_db=round(float(head - med), 1), first_sample=round(float(x[0]), 4))))
    if tail - med > EDGE_TAIL_DB:
        out.append(dict(symptom="edge_abrupt", t=len(x) / sr - 0.02, dur=0.02, confidence="medium", metrics=dict(edge="tail", level_rel_db=round(float(tail - med), 1), last_sample=round(float(x[-1]), 4))))
    return out


def detect_level_step(x, sr, name, info):
    """直前WIN秒と直後WIN秒の『発話フレームのみ』のRMS中央値が STEP_DB 以上階段状に変わり、各側内部は安定している(音量の急変)。"""
    out = []
    hop = 0.025
    t, r = frame_rms(x, sr, 50, 25)
    d = db(r)
    sp = d > info["thr_db"]
    n = int(LEVEL_WIN_S / hop)
    n2 = n // 2
    last = -999
    for i in range(n, len(d) - n):
        bs = sp[i - n:i]
        as_ = sp[i:i + n]
        if bs.sum() < 0.6 * n or as_.sum() < 0.6 * n:
            continue
        before = d[i - n:i][bs]
        after = d[i:i + n][as_]
        mb, ma = float(np.median(before)), float(np.median(after))
        if min(mb, ma) < info["ref_db"] + STEP_MIN_LEVEL_DB:
            continue
        diff = ma - mb
        if abs(diff) < STEP_DB or i - last <= 2 * n:
            continue
        # 各側が安定(前半/後半の中央値差が小さい)=ゆるやかな抑揚ではなく階段
        b1 = d[i - n:i - n2][sp[i - n:i - n2]]
        b2 = d[i - n2:i][sp[i - n2:i]]
        a1 = d[i:i + n2][sp[i:i + n2]]
        a2 = d[i + n2:i + n][sp[i + n2:i + n]]
        if min(len(b1), len(b2), len(a1), len(a2)) < 3:
            continue
        if abs(np.median(b1) - np.median(b2)) > STEP_STABLE_DB or abs(np.median(a1) - np.median(a2)) > STEP_STABLE_DB:
            continue
        last = i
        out.append(dict(symptom="level_step", t=float(t[i]), dur=0.0, confidence="low",
                        metrics=dict(step_db=round(diff, 1), before_db=round(mb, 1), after_db=round(ma, 1))))
    return out


def detect_spec_jump(x, sr, name, info):
    out = []
    nfft = 512 if sr <= 24000 else 1024
    hop = nfft // 4
    if len(x) < nfft * 2:
        return out
    from scipy.signal import stft
    f, tt, Z = stft(x, fs=sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False)
    M = np.abs(Z)
    lm = np.log1p(M * 50)
    flux = np.sqrt(np.sum(np.diff(lm, axis=1) ** 2, axis=0))
    en = db(np.sqrt(np.mean(M ** 2, axis=0)))
    spv = en[1:] > (info["ref_db"] - 38 if info["ref_db"] > -90 else -80)
    k = int(0.25 / (hop / sr))
    med = uniform_filter1d(flux, size=2 * k + 1, mode="nearest")
    mad = np.maximum(uniform_filter1d(np.abs(flux - med), size=2 * k + 1, mode="nearest"), 1e-6)
    z = (flux - med) / mad
    last = -10
    for i in np.where((z >= SPEC_JUMP_Z) & spv)[0]:
        if i - last < int(0.1 / (hop / sr)):
            continue
        last = i
        out.append(dict(symptom="spec_jump", t=float(tt[i + 1]), dur=0.0, confidence="low", metrics=dict(flux_z=round(float(z[i]), 1))))
    return out


def analyze(x, sr, name, is_segment=True):
    c = []
    c += detect_clip(x, sr, name)
    c += detect_click(x, sr, name)
    gd, info = detect_dropout_and_gaps(x, sr, name, is_segment)
    c += gd
    if is_segment:
        c += detect_edges(x, sr, name, info)
    c += detect_level_step(x, sr, name, info)
    c += detect_spec_jump(x, sr, name, info)
    return c, info


def load_timeline(level):
    tl = json.load(open(os.path.join(SNAP, level, "audit", "timeline.json"), encoding="utf-8"))
    return tl


def seg_name_to_timeline_part(level, seg):
    """narration/{seg}.wav -> timeline part名(Standard/Advanced共通の対応。一意に対応しないものはNone)。"""
    m = {"welcome": "Welcome", "topic_intro": "Topic intro", "japanese_title": "Japanese title", "preview_intro": "Preview intro",
         "preview": "Preview", "key_phrases_intro": "Key phrases intro", "full_story_intro": "Full story intro",
         "comment_1": "Comment 1", "comment_2": "Comment 2", "comment_3": "Comment 3", "comment_4": "Comment 4",
         "full_story_part1": "Full Story Part 1", "full_story_part2": "Full Story Part 2", "full_story_part3": "Full Story Part 3",
         "in_one_line": "In One Line"}
    s = seg
    for suf in ("_charon",):
        s = s.replace(suf, "")
    return m.get(s)


def build_segment_offsets(level, tl):
    """segment名 -> episode上の開始秒(単独segmentのみ。KP/num系はtimelineの複合Block内なので別処理)。"""
    off = {}
    for e in tl:
        off[e["part"]] = (e["start_seconds"], e["duration_seconds"])
    res = {}
    for f in sorted(glob.glob(os.path.join(SNAP, level, "narration", "*.wav"))):
        seg = os.path.basename(f)[:-4]
        if seg.endswith("_original"):
            continue
        p = seg_name_to_timeline_part(level, seg)
        if p and p in off:
            res[seg] = off[p][0]
    return res, off


def part_at(tl, t):
    for e in tl:
        if e["start_seconds"] <= t < e["start_seconds"] + e["duration_seconds"]:
            return e["part"], t - e["start_seconds"]
    return None, None


def near_words(words, t, span=0.45):
    if not words:
        return ""
    pre = [w["w"].strip() for w in words if w["e"] <= t][-3:]
    cur = [w["w"].strip() for w in words if w["s"] - 0.05 <= t <= w["e"] + 0.05]
    post = [w["w"].strip() for w in words if w["s"] > t][:3]
    return (" ".join(pre) + " [" + " ".join(cur) + "] " + " ".join(post)).strip()



_NUM = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}


def _norm_tokens(text):
    t = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("-", " ")
    t = re.sub(r"U\.S\.", "us", t)
    toks = re.findall(r"[A-Za-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?%?", t)
    out = []
    for w in toks:
        w = w.lower()
        out.append(_NUM.get(w, w))
    return out


def detect_asr_mismatch(words, expected_text):
    """local whisper(small)のword転写と原稿のword差分(発音/欠落/置換の疑い)。数詞表記・U.S.等の表記揺れは正規化して無視。"""
    import difflib
    wt, wi = [], []
    for k, w in enumerate(words):
        for tok in _norm_tokens(w["w"]):
            wt.append(tok)
            wi.append(k)
    # 'u','s' 連続は us に統合
    merged, midx = [], []
    i = 0
    while i < len(wt):
        if wt[i] == "u" and i + 1 < len(wt) and wt[i + 1] == "s":
            merged.append("us"); midx.append(wi[i]); i += 2
        else:
            merged.append(wt[i]); midx.append(wi[i]); i += 1
    exp = _norm_tokens(expected_text)
    sm = difflib.SequenceMatcher(None, exp, merged, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        ew = " ".join(exp[i1:i2])
        aw = " ".join(merged[j1:j2])
        if op == "replace" and j2 > j1:
            ws = words[midx[j1]]["s"]; we = words[midx[j2 - 1]]["e"]
        elif op == "insert" and j2 > j1:
            ws = words[midx[j1]]["s"]; we = words[midx[j2 - 1]]["e"]
        else:  # delete: 近傍語の時刻
            k = midx[min(j1, len(midx) - 1)] if midx else 0
            ws = words[k]["s"]; we = words[k]["e"]
        # 単純な複数形/時制の1文字差は弱い(low)のまま、それ以外も low(音響的確証なし)
        out.append(dict(symptom="asr_mismatch_word", t=(ws + we) / 2, dur=round(we - ws, 3), confidence="low",
                        metrics=dict(op=op, script=ew, whisper=aw)))
    return out


FIXED_ASSET_PARTS = ("Intro", "Notification 1", "Notification 2", "Notification 3", "Outro")
ASR_LOW_P = 0.5


def detect_low_conf_words(words, name):
    """local faster-whisperのword確率が低い語(聞き取りにくい/発音異常の疑い)。音響検知ではなくASR信頼度由来(low)。"""
    out = []
    for w in words or []:
        if w["p"] < ASR_LOW_P:
            out.append(dict(symptom="asr_low_conf_word", t=(w["s"] + w["e"]) / 2, dur=round(w["e"] - w["s"], 3), confidence="low",
                            metrics=dict(word=w["w"].strip(), whisper_prob=w["p"])))
    return out


def ffmpeg_decode(src, dst, sr, ac=1):
    import subprocess
    import imageio_ffmpeg
    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error", "-i", src, "-ar", str(sr), "-ac", str(ac), dst], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])


def expected_text_for(level, seg):
    """原稿が分かるEnglish長文segmentのみ(full_story_part1-3, in_one_line)。A2 part2は実際に読まれたLocal Rewrite後の文面。"""
    parts = json.load(open(os.path.join(SNAP, level, "parts.json"), encoding="utf-8"))
    if level == "a2" and seg == "full_story_part2":
        lr = json.load(open(os.path.join(SNAP, "a2", "local_rewrite_recovery_full_story_part2.json"), encoding="utf-8"))
        return lr["selection"]["selected"]["rewritten_segment"]
    key = {"full_story_part1": "part1", "full_story_part2": "part2", "full_story_part3": "part3", "in_one_line": "in_one_line"}.get(seg)
    return parts.get(key) if key else None


def run_main_analysis():
    t_start = time.time()
    ww = json.load(open(os.path.join(P45, "whisper_words.json"), encoding="utf-8"))
    results = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "thresholds": {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float))},
               "levels": {}, "libs": {"numpy": np.__version__, "soundfile": sf.__version__, "faster_whisper": ww.get("faster_whisper_version"), "whisper_model": ww.get("model")}}
    import scipy
    results["libs"]["scipy"] = scipy.__version__
    cands, seg_stats = [], []
    cid = 0
    for level in ("a2", "b1b"):
        tl = load_timeline(level)
        offs, off_all = build_segment_offsets(level, tl)
        total_audio = 0.0
        ts0 = time.time()
        for f in sorted(glob.glob(os.path.join(SNAP, level, "narration", "*.wav"))):
            seg = os.path.basename(f)[:-4]
            if seg.endswith("_original"):
                continue
            x, sr = sf.read(f, dtype="float64")
            x = mono(x)
            dur = len(x) / sr
            total_audio += dur
            c, info = analyze(x, sr, seg, True)
            words = (ww["segments"].get(f"{level}/{seg}") or {}).get("words", [])
            if (ww["segments"].get(f"{level}/{seg}") or {}).get("lang") == "en":
                c += detect_low_conf_words(words, seg)
                et = expected_text_for(level, seg)
                if et:
                    c += detect_asr_mismatch(words, et)
            for e in c:
                cid += 1
                e.update(id=f"{level}-S{cid:03d}", level=level, source="segment", segment=seg, t_seg=round(e.pop("t"), 3))
                e["t_episode"] = round(offs[seg] + e["t_seg"], 3) if seg in offs else None
                e["near_words"] = near_words(words, e["t_seg"])
                e["dur"] = round(e["dur"], 4)
                e["fixed_asset"] = False
                cands.append(e)
            seg_stats.append(dict(level=level, segment=seg, duration=round(dur, 3), sr=sr, peak=round(float(np.max(np.abs(x))), 4),
                                  ref_db=round(info["ref_db"], 1), natural_zero_runs=info.get("natural_zero_runs", 0), n_cand=len(c)))
        results["levels"][level] = {"segments_audio_seconds": round(total_audio, 2), "segments_analysis_seconds": round(time.time() - ts0, 2)}
        af = glob.glob(os.path.join(SNAP, level, "assembled", "*.wav"))[0]
        xs, sr = sf.read(af, dtype="float64")
        ts1 = time.time()
        xm = mono(xs)
        c, info = analyze(xm, sr, "assembled", False)
        for ch in range(xs.shape[1]):
            for e in detect_clip(xs[:, ch], sr, "assembled"):
                e["metrics"]["channel"] = ch
                c.append(e)
        for e in c:
            cid += 1
            part, tin = part_at(tl, e["t"])
            e.update(id=f"{level}-A{cid:03d}", level=level, source="assembled", segment=part, t_seg=round(tin, 3) if tin is not None else None,
                     t_episode=round(e.pop("t"), 3), dur=round(e["dur"], 4), near_words="")
            e["fixed_asset"] = part in FIXED_ASSET_PARTS
            cands.append(e)
        results["levels"][level].update(assembled_file=os.path.relpath(af, ROOT).replace("\\", "/"), assembled_seconds=round(len(xm) / sr, 3),
                                         assembled_analysis_seconds=round(time.time() - ts1, 2), assembled_peak=round(float(np.max(np.abs(xs))), 4))
    results["candidates"] = cands
    results["segment_stats"] = seg_stats
    results["total_elapsed_seconds"] = round(time.time() - t_start, 2)
    return results


def run_published_analysis(results):
    """公開mp3(ユーザーが実際に再生するepisode.mp3/segments/*.mp3)をdecodeして同じ検知器を適用(wav解析との差=mp3化由来を切り分け)。"""
    import tempfile
    pub = {}
    base = os.path.join(ROOT, "user_test", "coffee_new_tone_01")
    tmpd = tempfile.mkdtemp(prefix="pub_anom_")
    out = []
    cid = 0
    for level in ("a2", "b1b"):
        tl = load_timeline(level)
        ep = os.path.join(base, level, "web", "episode.mp3")
        wav = os.path.join(tmpd, f"{level}_episode.wav")
        ffmpeg_decode(ep, wav, 48000, 1)
        x, sr = sf.read(wav, dtype="float64")
        c, info = analyze(x, sr, "published_episode", False)
        for e in c:
            cid += 1
            part, tin = part_at(tl, e["t"])
            e.update(id=f"{level}-P{cid:03d}", level=level, source="published_episode_mp3", segment=part, t_seg=round(tin, 3) if tin is not None else None,
                     t_episode=round(e.pop("t"), 3), dur=round(e["dur"], 4), near_words="", fixed_asset=part in FIXED_ASSET_PARTS)
            out.append(e)
        pub[level] = {"episode_mp3": os.path.relpath(ep, ROOT).replace("\\", "/"), "seconds": round(len(x) / sr, 3), "peak": round(float(np.max(np.abs(x))), 4)}
        n_seg = 0
        for f in sorted(glob.glob(os.path.join(base, level, "web", "segments", "*.mp3"))):
            seg = os.path.basename(f)[:-4]
            w2 = os.path.join(tmpd, f"{level}_{seg}.wav")
            ffmpeg_decode(f, w2, 24000, 1)
            x, sr = sf.read(w2, dtype="float64")
            c, info = analyze(x, sr, seg, True)
            n_seg += 1
            for e in c:
                cid += 1
                e.update(id=f"{level}-P{cid:03d}", level=level, source="published_segment_mp3", segment=seg, t_seg=round(e.pop("t"), 3), t_episode=None,
                         dur=round(e["dur"], 4), near_words="", fixed_asset=False)
                out.append(e)
        pub[level]["segment_mp3_count"] = n_seg
    results["published_mp3"] = {"files": pub, "candidates": out}
    return results


def word_window_metrics(x, sr, s, e, ref):
    a = max(0, int((s - 0.03) * sr))
    b = min(len(x), int((e + 0.03) * sr))
    w = x[a:b]
    if len(w) < 64:
        return {}
    d2 = np.abs(np.diff(w, 2))
    loc = np.sqrt(uniform_filter1d(np.diff(w, 2) ** 2, size=int(0.02 * sr) | 1, mode="nearest"))
    t, r = frame_rms(w, sr, 10, 5)
    d = db(r)
    F = np.abs(np.fft.rfft(w * np.hanning(len(w))))
    fr = np.fft.rfftfreq(len(w), 1 / sr)
    tot = np.sum(F ** 2) + 1e-12
    return dict(dur_ms=round((e - s) * 1000), peak=round(float(np.max(np.abs(w))), 3), rms_db=round(float(db(np.sqrt(np.mean(w ** 2)))), 1),
                min10ms_db_rel=round(float(np.min(d) - ref), 1), max_d2_ratio=round(float(np.max(d2 / np.maximum(loc, 1e-6))), 1),
                hf4k_ratio=round(float(np.sum(F[fr > 4000] ** 2) / tot), 4), centroid_hz=round(float(np.sum(fr * F ** 2) / tot)),
                zero_samples=int(np.sum(np.abs(w) < 1e-5)))


def run_focus_probe(results):
    ww = json.load(open(os.path.join(P45, "whisper_words.json"), encoding="utf-8"))
    rows = []
    for level in ("a2", "b1b"):
        for seg in ("full_story_part1", "full_story_part2", "full_story_part3"):
            x, sr = sf.read(os.path.join(SNAP, level, "narration", seg + ".wav"), dtype="float64")
            x = mono(x)
            _, _, _, ref, _ = speech_frames(x, sr)
            for w in ww["segments"][f"{level}/{seg}"]["words"]:
                if "coffee" in w["w"].lower():
                    m = word_window_metrics(x, sr, w["s"], w["e"], ref)
                    m.update(level=level, segment=seg, word=w["w"].strip(), s=w["s"], e=w["e"], whisper_prob=w["p"])
                    rows.append(m)
    results["focus_probe_coffee"] = rows
    return results


def inject_faults(x, sr):
    """正常音声(A2 part3 24kHz mono)へ既知の異常を注入して検知器の感度(positive control)を測る。"""
    t, d, sp, ref, thr = speech_frames(x, sr)

    def voiced_near(t0):
        i = int(t0 / 0.01)
        win = d[i:i + 60]
        k = int(np.argmax(win)) if len(win) else 0
        return (i + k) * 0.01

    def clip_fn(gain):
        def f(y, t0):
            a = int(t0 * sr)
            b = a + int(0.4 * sr)
            y[a:b] = np.clip(y[a:b] * gain, -1, 1)
            return y
        return f

    def click_fn(amp, n=1):
        def f(y, t0):
            a = int(t0 * sr)
            y[a:a + n] += amp
            return y
        return f

    def dropout_fn(ms):
        def f(y, t0):
            a = int(t0 * sr)
            y[a:a + int(ms / 1000 * sr)] = 0.0
            return y
        return f

    def step_fn(gain_db):
        def f(y, t0):
            a = int(t0 * sr)
            y[a:] = y[a:] * (10 ** (gain_db / 20))
            return y
        return f

    def noise_fn(ms, rel_db):
        def f(y, t0):
            a = int(t0 * sr)
            n = int(ms / 1000 * sr)
            rng = np.random.default_rng(7)
            y[a:a + n] += rng.standard_normal(n) * 10 ** ((ref + rel_db) / 20)
            return y
        return f

    def gap_fn(sec):
        def f(y, t0):
            a = int(t0 * sr)
            return np.concatenate([y[:a], np.zeros(int(sec * sr)), y[a:]])
        return f

    def cut_fn(y, t0):
        return y[: int(t0 * sr)]

    def head_fn(y, t0):
        return y[int(t0 * sr):]

    sp_start = float(t[int(np.argmax(sp))])
    cases = [
        ("clip", "clip", "gain x8 400ms", clip_fn(8), voiced_near(5.0)),
        ("clip", "clip", "gain x3 400ms", clip_fn(3), voiced_near(5.0)),
        ("click", "click", "amp 0.5 1sample", click_fn(0.5), voiced_near(10.0)),
        ("click", "click", "amp 0.3 1sample", click_fn(0.3), voiced_near(10.0)),
        ("click", "click", "amp 0.2 1sample", click_fn(0.2), voiced_near(10.0)),
        ("click", "click", "amp 0.1 1sample", click_fn(0.1), voiced_near(10.0)),
        ("click", "click", "amp 0.2 3sample", click_fn(0.2, 3), voiced_near(11.0)),
        ("dropout", "dropout", "zero 30ms", dropout_fn(30), voiced_near(15.0)),
        ("dropout", "dropout", "zero 10ms", dropout_fn(10), voiced_near(15.0)),
        ("dropout", "dropout", "zero 5ms", dropout_fn(5), voiced_near(15.0)),
        ("level_step", "level_step", "-12dB step", step_fn(-12), voiced_near(20.0)),
        ("level_step", "level_step", "-9dB step", step_fn(-9), voiced_near(20.0)),
        ("level_step", "level_step", "-6dB step", step_fn(-6), voiced_near(20.0)),
        ("level_step", "level_step", "+4dB step", step_fn(4), voiced_near(20.0)),
        ("noise_burst", "spec_jump|click|level_step", "40ms noise -20dB rel", noise_fn(40, -20), voiced_near(25.0)),
        ("noise_burst", "spec_jump|click|level_step", "40ms noise -10dB rel", noise_fn(40, -10), voiced_near(25.0)),
        ("mid_gap", "long_gap|dropout", "insert 1.2s silence", gap_fn(1.2), voiced_near(30.0)),
        ("mid_gap", "long_gap|dropout", "insert 0.5s silence", gap_fn(0.5), voiced_near(30.0)),
        ("truncate", "edge_abrupt", "cut mid-speech at 40s", cut_fn, voiced_near(40.0)),
        ("head_chop", "edge_abrupt", "start 60ms into word onset", head_fn, sp_start + 0.06),
    ]
    out = []
    for name, exp, sev, fn, t0 in cases:
        y = x.copy()
        y2 = fn(y, t0)
        c, info = analyze(y2, sr, "inject", True)
        if name == "head_chop":
            tt = 0.0
        elif name == "truncate":
            tt = len(y2) / sr - 0.02
        else:
            tt = t0
        tol = 0.6 if name == "level_step" else 0.35
        hits = [e for e in c if abs(e["t"] - tt) <= tol]
        exp_set = exp.split("|")
        hit_exp = [e for e in hits if e["symptom"] in exp_set]
        out.append(dict(fault=name, severity=sev, t0=round(float(tt), 2), expected=exp, detected_expected=bool(hit_exp),
                        detected_any=bool(hits), detected_symptoms=sorted({e["symptom"] for e in hits}),
                        best_conf=(sorted([e["confidence"] for e in hit_exp], key=lambda z: ["high", "medium", "low"].index(z))[0] if hit_exp else None)))
    return out


def run_injection(results):
    x, sr = sf.read(os.path.join(SNAP, "a2", "narration", "full_story_part3.wav"), dtype="float64")
    x = mono(x)
    base, _ = analyze(x, sr, "base", True)
    results["injection_test"] = {"source": "a2/full_story_part3.wav(24kHz mono, 48.36s)", "baseline_candidates_on_clean": len(base), "cases": inject_faults(x, sr)}
    return results


def main():
    results = run_main_analysis()
    results = run_published_analysis(results)
    results = run_focus_probe(results)
    results = run_injection(results)
    json.dump(results, open(os.path.join(P45, "ANOMALY_CANDIDATES_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print("candidates", len(results["candidates"]), "published", len(results["published_mp3"]["candidates"]), "elapsed", results["total_elapsed_seconds"])
    print(Counter((c["level"], c["source"], c["symptom"], c["confidence"]) for c in results["candidates"]))
    print(Counter((c["level"], c["source"], c["symptom"], c["confidence"]) for c in results["published_mp3"]["candidates"]))
    for r in results["injection_test"]["cases"]:
        print(r)
    for r in results["focus_probe_coffee"]:
        print(r)


if __name__ == "__main__":
    main()
