"""FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02: 無音区間検出(read-only解析専用、Production非依存)。
wav(PCM16 mono/stereo)を10msフレームのRMS(dBFS)で走査し、threshold未満が min_ms 以上続く区間を列挙する。
文中ポーズ候補の推定位置は、台本(--text-file)の語頭からの文字比率を『発話時間(無音を除く)』に比例させた概算(ASR語タイムスタンプ無し)。
使い方: py -I yfb_silence_scan_01.py --wav <abs> [--text-file <abs txt>] --threshold-dbfs -40 --min-ms 150 --out <json>
"""
import argparse, json, re, sys, wave
import numpy as np


def load(path):
    with wave.open(path, "rb") as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(n)
    if sw != 2:
        raise SystemExit(f"unsupported sampwidth {sw}")
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def scan(x, sr, thr_db, min_ms, frame_ms=10):
    f = int(sr * frame_ms / 1000)
    nf = len(x) // f
    fr = x[: nf * f].reshape(nf, f)
    rms = np.sqrt((fr ** 2).mean(axis=1) + 1e-20)
    db = 20 * np.log10(rms + 1e-12)
    sil = db < thr_db
    runs, i = [], 0
    while i < nf:
        if sil[i]:
            j = i
            while j < nf and sil[j]:
                j += 1
            dur = (j - i) * frame_ms
            if dur >= min_ms:
                runs.append({"start_s": round(i * frame_ms / 1000, 3), "end_s": round(j * frame_ms / 1000, 3), "dur_ms": dur})
            i = j
        else:
            i += 1
    return runs, nf * frame_ms / 1000


SPLIT = re.compile(r"[,.;:?!]")


def boundaries(text):
    """文字index -> 種別。句点系=sentence、カンマ系=comma。"""
    out = []
    for m in re.finditer(r"[.?!]|[,;:]", text):
        out.append((m.end(), "sentence_end" if m.group() in ".?!" else "comma"))
    return out


def attach_text(runs, total_s, text):
    if not text:
        return
    lead = runs[0]["dur_ms"] / 1000 if runs and runs[0]["start_s"] < 0.05 else 0.0
    trail = runs[-1]["dur_ms"] / 1000 if runs and runs[-1]["end_s"] >= total_s - 0.05 else 0.0
    inner = [r for r in runs if r["start_s"] >= 0.05 and r["end_s"] < total_s - 0.05]
    active_total = total_s - lead - trail - sum(r["dur_ms"] for r in inner) / 1000
    b = boundaries(text)
    L = len(text)
    acc = 0.0
    for r in inner:
        speech_before = r["start_s"] - lead - acc
        acc += r["dur_ms"] / 1000
        pos = int(round(L * speech_before / active_total)) if active_total > 0 else 0
        best = min(b, key=lambda t: abs(t[0] - pos)) if b else (pos, "none")
        near = abs(best[0] - pos)
        r["est_char_pos"] = pos
        r["est_context"] = text[max(0, pos - 25):pos] + " | " + text[pos:pos + 25]
        r["nearest_punct"] = {"char_pos": best[0], "kind": best[1], "distance_chars": near}
        r["class_est"] = ("natural_punct" if near <= 12 else "mid_clause_candidate")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--text-file")
    ap.add_argument("--threshold-dbfs", type=float, default=-40)
    ap.add_argument("--min-ms", type=int, default=150)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    x, sr = load(a.wav)
    runs, total = scan(x, sr, a.threshold_dbfs, a.min_ms)
    text = open(a.text_file, encoding="utf8").read().strip() if a.text_file else None
    attach_text(runs, total, text)
    lead = runs[0]["dur_ms"] if runs and runs[0]["start_s"] < 0.05 else 0
    trail = runs[-1]["dur_ms"] if runs and runs[-1]["end_s"] >= total - 0.05 else 0
    inner = [r for r in runs if r["start_s"] >= 0.05 and r["end_s"] < total - 0.05]
    words = len(text.split()) if text else None
    res = {"wav": a.wav, "sr": sr, "duration_s": round(total, 3), "threshold_dbfs": a.threshold_dbfs, "min_ms": a.min_ms,
           "leading_silence_ms": lead, "trailing_silence_ms": trail, "inner_pause_count": len(inner),
           "inner_pause_total_ms": sum(r["dur_ms"] for r in inner), "inner_pause_max_ms": max([r["dur_ms"] for r in inner], default=0),
           "inner_pause_mean_ms": round(sum(r["dur_ms"] for r in inner) / len(inner), 1) if inner else 0,
           "inner_pauses_per_min": round(len(inner) / (total / 60), 2) if total else 0,
           "words": words, "wpm_gross": round(words / (total / 60), 1) if words else None,
           "mid_clause_candidates": sum(1 for r in inner if r.get("class_est") == "mid_clause_candidate"),
           "pauses": runs}
    json.dump(res, open(a.out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(a.out, "pauses", len(inner), "max", res["inner_pause_max_ms"], "lead", lead, "trail", trail)


if __name__ == "__main__":
    main()
