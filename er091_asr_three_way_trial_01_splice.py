# ============================================================
# er091_asr_three_way_trial_01_splice.py
# ASR-THREE-WAY-COMPARISON-TRIAL-01: 正常wavから語を削除/重複させた「脱落・追加」問題音声を作る(API 0、TTS 0、ローカルのみ)。
# 正解ラベルは構成ラベル(削除/重複した語は物理的に存在しない/重複している)。切断位置のみfaster-whisper word timestampを使う
# (ラベル根拠ではない)。接合部は12msクロスフェード。量産音声ではなく意図的合成音声として区別する。
# ============================================================
from __future__ import annotations
import hashlib
import json
import os
import wave
import numpy as np

OUT = "er091_output/asr_three_way_trial_01"
DST = os.path.join(OUT, "audio", "splice")
os.makedirs(DST, exist_ok=True)
import er008_disfluency_qa_18 as dq18  # noqa: E402

# (new_id, source normal id, 操作, 対象語[正規化], 誤りの種類)
ITEMS = [
    ("spl_body_almost_deleted", "body_melos_a2_full_story_part3_c6", "delete", "almost", "word_omission_meaning_change"),
    ("spl_body_not_deleted", "body_yemen_b1b_comment_1", "delete", "not", "negation_omitted"),
    ("spl_kp_in_deleted", "kp_melos_a2_3", "delete", "in", "kp_function_word_omission"),
    ("spl_body_late_deleted", "body_melos_a2_full_story_part1_c8", "delete", "late", "word_omission_meaning_change"),
    ("spl_body_sword_duplicated", "body_melos_a2_full_story_part3_c8", "dup", "sword", "word_repetition_added"),
]
XF = 0.012
MODE = os.environ.get("SPLICE_MODE", "v1")   # v1=Whisper語境界中点 / v2=±50ms内のRMS最小点


def rms_min(x, sr, center, half=0.05, frame=0.01):
    lo, hi = max(0, int((center - half) * sr)), min(len(x), int((center + half) * sr))
    f = int(frame * sr)
    best, bi = 1e9, int(center * sr)
    for i in range(lo, max(lo + 1, hi - f), max(1, f // 2)):
        v = float(np.sqrt(np.mean(x[i:i + f] ** 2) + 1e-12))
        if v < best:
            best, bi = v, i + f // 2
    return bi / sr


def norm(w):
    return "".join(ch for ch in w.lower() if ch.isalnum() or ch == "'")


def read(p):
    with wave.open(p, "rb") as w:
        assert w.getsampwidth() == 2 and w.getnchannels() == 1
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return x, sr


def write(p, x, sr):
    y = (np.clip(x, -1, 1) * 32767.0).astype(np.int16)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(y.tobytes())


def join(a, b, sr):
    n = int(XF * sr)
    if len(a) < n or len(b) < n:
        return np.concatenate([a, b])
    fo = np.linspace(1, 0, n, dtype=np.float32)
    mix = a[-n:] * fo + b[:n] * (1 - fo)
    return np.concatenate([a[:-n], mix, b[n:]])


def main():
    man = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(OUT, "dataset_manifest_normal.jsonl"), encoding="utf-8")}
    rows = []
    for nid, src_id, op, target, etype in ITEMS:
        src = man[src_id]
        x, sr = read(src["wav"])
        words = dq18.transcribe_verbatim(src["wav"], language="en", model_size="small")
        idx = [i for i, w in enumerate(words) if norm(w["text"]) == target]
        assert idx, (nid, [w["text"] for w in words])
        i = idx[0]
        # 語区間の境界は前後語の間の中点で切る(語頭の子音を欠かさない)
        s_prev = words[i - 1]["end"] if i > 0 else 0.0
        s = (s_prev + words[i]["start"]) / 2 if i > 0 else max(0.0, words[i]["start"] - 0.02)
        e_next = words[i + 1]["start"] if i + 1 < len(words) else len(x) / sr
        e = (words[i]["end"] + e_next) / 2 if i + 1 < len(words) else min(len(x) / sr, words[i]["end"] + 0.02)
        if MODE == "v2":
            s = rms_min(x, sr, words[i]["start"])
            e = rms_min(x, sr, words[i]["end"])
        a, w_, b = x[: int(s * sr)], x[int(s * sr): int(e * sr)], x[int(e * sr):]
        if op == "delete":
            y = join(a, b, sr)
            canon = src["canonical"]
        else:
            y = join(join(a, w_, sr), join(w_, b, sr), sr) if False else join(join(a, w_, sr), np.concatenate([w_, b]), sr)
            canon = src["canonical"]
        if MODE == "v2":
            nid = nid.replace("spl_", "spl2_", 1)
        out = os.path.join(DST, nid + ".wav")
        write(out, y, sr)
        rows.append({"id": nid, "source_id": src_id, "op": op, "target_word": target, "error_type": etype, "canonical": canon,
                     "cut_s": [round(s, 3), round(e, 3)], "words_whisper": [w["text"] for w in words], "wav": out.replace("\\", "/"),
                     "wav_sha256": hashlib.sha256(open(out, "rb").read()).hexdigest(), "duration_s": round(len(y) / sr, 3),
                     "kind": src["kind"], "family": src["family"], "level": src["level"]})
        print(rows[-1]["id"], rows[-1]["cut_s"], rows[-1]["duration_s"], flush=True)
    json.dump(rows, open(os.path.join(OUT, "splice_log.json" if MODE == "v1" else "splice_log_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
