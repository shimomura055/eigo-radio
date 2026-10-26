# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01: 停止計測ライブラリ(read-only、API 0)。
FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01の既存tool(yfb_silence_scan_01 / yfb_pause_stats_01 / yfb_pause_align_01)をそのままimportして使う
(-40 dBFS・10msフレーム・>=150ms・<120msの有音は前後を結合)。計測ロジックは再実装しない。"""
import glob, json, os, re, sys

_T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01", "tools")
sys.path.insert(0, os.path.abspath(_T))
import yfb_silence_scan_01 as sc      # noqa: E402
import yfb_pause_stats_01 as ps       # noqa: E402
import yfb_pause_align_01 as al       # noqa: E402

THR_DB, MIN_MS = -40, 150
RUN01 = "er121_output/family_y_production_01/redelivery_fee/run_01"


def body_text(level, body):
    p = json.load(open(f"{RUN01}/{level}/parts.json", encoding="utf-8"))
    return p["segments"][f"y_voice_{body}"]


def measure_wav(path, text):
    x, sr = sc.load(path)
    runs, total = sc.scan(x, sr, THR_DB, MIN_MS)
    lead = runs[0]["dur_ms"] if runs and runs[0]["start_s"] < 0.05 else 0
    trail = runs[-1]["dur_ms"] if runs and runs[-1]["end_s"] >= total - 0.05 else 0
    inner = [r for r in runs if r["start_s"] >= 0.05 and r["end_s"] < total - 0.05]
    meas = {"duration_s": round(total, 3), "leading_silence_ms": lead, "trailing_silence_ms": trail, "pauses": runs, "words": len(text.split())}
    merged = ps.merge(inner)
    st = ps.stats(meas, text)
    aligned = al.align(meas, text)
    tot_pause_ms = sum(p["dur_ms"] for p in merged)
    active = max(total - lead / 1000 - trail / 1000 - tot_pause_ms / 1000, 1e-6)
    words = len(text.split())
    long1000 = [a for a in aligned if a["dur_ms"] >= 1000]
    mid500 = [a for a in aligned if (not a["at_punctuation"]) and a["dur_ms"] >= 500]
    return {
        "dur_s": round(total, 2), "words": words, "n_pauses": len(merged), "ge700": st["ge700"], "ge1000": st["ge1000"],
        "ge1000_per100w": round(100 * st["ge1000"] / words, 2), "max_ms": st["max_ms"], "pause_total_s": round(tot_pause_ms / 1000, 2),
        "occ_pct": st["pause_ratio_pct"], "mean_pause_ms": st["mean_ms"], "gross_wpm": round(words / (total / 60), 1),
        "speech_wpm": round(words / (active / 60), 1), "mid_ge500": len(mid500), "lead_ms": lead, "trail_ms": trail,
        "long1000_pos": [{"t": a["start_s"], "ms": a["dur_ms"], "after": a["after_word"], "before": a["before_word"], "punct": a["at_punctuation"]} for a in long1000],
        "pause_list": [{"t": a["start_s"], "ms": a["dur_ms"], "after": a["after_word"], "before": a["before_word"], "punct": a["at_punctuation"]} for a in aligned],
    }


def route_kind(name):
    n = name.lower()
    if "minimalfallback" in n:
        return "fallback"
    return "main"


def collect_samples(trial_root="er121_output/family_y_voice_pause_trial_01"):
    """全rawサンプル(1 attempt wav = 1 独立TTS draw)を列挙。返却: list of dict(level, body, voice, src, take, attempt, kind, wav)。
    src: run01_final(HR前のproduction attempt群) / v1cand(Voice1候補take) / trial(本Trial新規)。Std attemptは減速前のraw。"""
    out = []
    names = {1: "Algieba", 2: "Zephyr", 3: "Schedar"}
    for lv in ("a2", "b1b"):
        for i in (1, 2, 3):
            for f in sorted(glob.glob(f"{RUN01}/{lv}/narration/attempts/y_voice_{i}_attempt*.wav")):
                m = re.search(r"attempt(\d+)_(.*)\.wav$", f)
                out.append(dict(level=lv, body=i, voice=i, src="run01_prod", take=0, attempt=int(m.group(1)), kind=route_kind(f), wav=f.replace("\\", "/")))
        for k in (1, 2, 3):
            for f in sorted(glob.glob(f"{RUN01}/{lv}/hr_adopt_prep/voice1_candidates/take{k}/narration/attempts/y_voice_1_attempt*.wav")):
                m = re.search(r"attempt(\d+)_(.*)\.wav$", f)
                out.append(dict(level=lv, body=1, voice=1, src="v1cand", take=k, attempt=int(m.group(1)), kind=route_kind(f), wav=f.replace("\\", "/")))
        for d in sorted(glob.glob(f"{trial_root}/{lv}/body*_voice*/take*")):
            m = re.search(r"body(\d)_voice(\d)/take(\d+)$", d.replace(chr(92), "/"))
            if not m:
                continue
            b, v, k = int(m.group(1)), int(m.group(2)), int(m.group(3))
            for f in sorted(glob.glob(f"{d}/narration/attempts/*_attempt*.wav")):
                m2 = re.search(r"attempt(\d+)_(.*)\.wav$", f)
                out.append(dict(level=lv, body=b, voice=v, src="trial", take=k, attempt=int(m2.group(1)), kind=route_kind(f), wav=f.replace("\\", "/")))
    return out
