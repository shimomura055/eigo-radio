# ============================================================
# er011_open121_tts_repetition_general_qa_trial_02.py
# OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-02
# (false start型検知方式の追加Trial + 方式A/Dとの統合仕様整理)
# ============================================================
# 隔離Trial(Lane A、ユーザー判断2026-09-07: 方式A+Dは有力候補だが
# "As of Septem... As of September..."型のfalse start/aborted restart
# を検知できるまでOPEN-121は継続、A+Dだけを先行採用しない)。
# Production Validator/QA/retry/Cost Guard/TTS Prompt/適用範囲は一切
# 変更しない。既存Production関数(er003_b1_p4_audio.get_full_text_via_
# azure_stt_continuous / er006_asr_provider_routing_01.transcribe /
# er008_disfluency_qa_18の関数群)を無変更のまま呼び出すだけの独立Trial。
#
# 本ファイルはTrial-01(er011_open121_tts_repetition_general_qa_trial_01.py、
# 無変更のまま)をベースに、そこで使われた既存ヘルパー関数(sha256/wav io/
# 方式A・D本体・text n-gram反復検知・単語duration異常検知)を再掲した上で、
# false start型検知のための新規方式(D拡張・onset二重化・A-ext参照
# corpus拡充・Secondary ASR窓検知)を追加する。Trial-01自体・Trial-01の
# 出力(er011_output/open121_tts_repetition_general_qa_trial_01/)は
# 一切変更しない(読み取りのみ、既存テストセット51件を自分の出力配下へ
# コピーして再利用する)。
#
# 書き込み範囲: 本ファイル(root)、er011_output/
# open121_tts_repetition_general_qa_trial_02/ 配下のみ。Git操作なし
# (統合はFableが実施)。
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er005_cost_logger as cost_logger
import er006_asr_provider_routing_01 as asr_routing  # noqa: F401 (方式C相当は本Trialでは未使用、将来比較用に読み込みのみ)
import er008_disfluency_qa_18 as dq18
import er003_b1_p4_audio as p4_azure

TRIAL01_DIR = "er011_output/open121_tts_repetition_general_qa_trial_01"
TRIAL01_MANIFEST = f"{TRIAL01_DIR}/test_set/manifest.json"

OUT_DIR = "er011_output/open121_tts_repetition_general_qa_trial_02"
TEST_SET_DIR = f"{OUT_DIR}/test_set"
RESULTS_DIR = f"{OUT_DIR}/results"
AUDIT_DIR = f"{OUT_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"
MANIFEST_PATH = f"{TEST_SET_DIR}/manifest.json"

PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 800.0

AZURE_STT_MODEL_LABEL = "real-time transcription (S0/S1 standard tier)"


def log(msg):
    print(msg, flush=True)


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_wav(path):
    data, sr = sf.read(path, always_2d=False)
    return data, sr


def write_wav(path, data, sr):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sf.write(path, data, sr, subtype="PCM_16")


def to_mono(data):
    if data.ndim == 1:
        return data.astype(np.float64)
    return data.mean(axis=1).astype(np.float64)


def duration_seconds(path):
    data, sr = load_wav(path)
    return round(len(data) / sr, 3)


def _copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return dst


# ============================================================
# コスト集計(Trial-01と同じ設計。pricing_snapshot.jsonの公式価格のみ使用。
# azure(audio_hourメーター)分をTrial-01から拡張)
# ============================================================
def _load_pricing():
    prices = json.load(open(PRICING_SNAPSHOT_PATH, encoding="utf-8"))["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter)
    return price


def compute_cost_jpy_so_far():
    """AUDIT_DIR/raw_usage_log.jsonl(このTrial専用のcost_logger出力)から
    累積コストをJPY換算で計算する。Production側raw_usage_log.jsonlには
    一切触れない。"""
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider == "gemini" and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price("gemini", model, "input_tokens") / 1e6 \
                        + out_tok * price("gemini", model, "output_tokens") / 1e6
                elif provider == "openai_asr" and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price("openai_asr", model, "input_tokens") / 1e6 \
                        + out_tok * price("openai_asr", model, "output_tokens") / 1e6
                elif provider == "azure":
                    dur_s = rec.get("audio_duration_submitted_seconds") or 0.0
                    usd = (dur_s / 3600.0) * price("azure", AZURE_STT_MODEL_LABEL, "audio_hour")
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note=""):
    jpy, _ = compute_cost_jpy_so_far()
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.1f} JPY > cap {BUDGET_JPY_CAP} JPY. "
                            f"Stopping ({note}).")
    return jpy


# ============================================================
# Phase 0: Trial-01のテストセット51件を読み取りコピーで再利用する
# (Trial-01のファイル・manifestは一切変更しない)。
# ============================================================
def reuse_trial01_test_set():
    src_manifest = json.load(open(TRIAL01_MANIFEST, encoding="utf-8"))
    manifest = []
    for item in src_manifest:
        src_path = item["path"]
        rel = os.path.relpath(src_path, f"{TRIAL01_DIR}/test_set").replace("\\", "/")
        dst_path = f"{TEST_SET_DIR}/{rel}"
        _copy(src_path, dst_path)
        new_item = dict(item)
        new_item["path"] = dst_path
        new_sha = sha256_of(dst_path)
        assert new_sha == item["sha256"], f"整合性エラー: {item['item_id']}のコピー後sha256が一致しません"
        new_item["reused_from"] = "OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-01"
        manifest.append(new_item)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    log(f"reuse_trial01_test_set: {len(manifest)} items reused (sha256 verified, no new TTS/ASR cost).")
    return manifest


# ============================================================
# Phase 1: false start型 合成陽性(先頭0.7〜1.5秒を語の途中で切って
# 先頭へ前置し、「語途中で切れて再開」を模した音声)。B1 FSP1実データの
# パターン(語の途中で切れる短い言い直し+ほぼ間なしの再開)を模す。
# ============================================================
FALSESTART_SYNTH_SPECS = [
    # (source_item_id, cut_seconds, gap_seconds, label)
    ("a2_point_one_clean", 0.7, 0.0, "cut0.7s_nogap"),
    ("a2_full_story_part1_clean", 1.0, 0.0, "cut1.0s_nogap"),
    ("a2_full_story_part2_clean", 1.3, 0.0, "cut1.3s_nogap"),
    ("a2_topic_intro", 0.9, 0.15, "cut0.9s_gap0.15s"),
    ("b1b_full_story_intro_charon", 1.1, 0.0, "cut1.1s_nogap"),
]


def _word_at_time(words, t):
    for w in words:
        if w["start"] <= t < w["end"]:
            return w
    return None


def build_synthetic_falsestart_positives(manifest=None):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    by_id = {m["item_id"]: m for m in manifest}
    os.makedirs(f"{TEST_SET_DIR}/positives_synthetic_falsestart", exist_ok=True)
    new_items = []
    for src_id, cut_s, gap_s, label in FALSESTART_SYNTH_SPECS:
        src = by_id[src_id]
        words = dq18.transcribe_verbatim(src["path"], language="en", model_size="small")
        data, sr = load_wav(src["path"])
        cut_word = _word_at_time(words, cut_s)
        mid_word_cut = bool(cut_word and cut_word["start"] < cut_s < cut_word["end"])
        fragment = data[:int(round(cut_s * sr))]
        gap = np.zeros(int(round(gap_s * sr)), dtype=data.dtype) if gap_s > 0 else np.zeros(0, dtype=data.dtype)
        out = np.concatenate([fragment, gap, data])
        item_id = f"synth_falsestart_{label}_{src_id}"
        out_path = f"{TEST_SET_DIR}/positives_synthetic_falsestart/{item_id}.wav"
        write_wav(out_path, out, sr)
        new_items.append(dict(
            item_id=item_id, path=out_path, sha256=sha256_of(out_path),
            duration_seconds=round(len(out) / sr, 3), canonical_text=src.get("canonical_text"),
            language="en", label="positive", source="synthetic_falsestart",
            note=(f"clean音声({src_id})の先頭{cut_s}秒を切り出し、gap={gap_s}秒を挟んで"
                  f"元音声全体の先頭へ前置(実在B1 FSP1と同型: 語途中で切れて再開)。"
                  f"切断点はcut_word={cut_word['text'] if cut_word else None!r}の内部"
                  f"[{cut_word['start'] if cut_word else None},{cut_word['end'] if cut_word else None}] "
                  f"で、mid_word_cut={mid_word_cut}(partial-word性の確認)。"),
            synth_falsestart_info=dict(src_item_id=src_id, cut_seconds=cut_s, gap_seconds=gap_s,
                                        cut_word=cut_word, mid_word_cut=mid_word_cut)))
        log(f"  -> {item_id}: cut={cut_s}s gap={gap_s}s mid_word_cut={mid_word_cut} "
            f"(cut_word={cut_word['text'] if cut_word else None!r})")

    existing = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    existing = [m for m in existing if m["source"] != "synthetic_falsestart"]
    existing.extend(new_items)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    log(f"build_synthetic_falsestart_positives: {len(new_items)} items (local TTS-free splice, cost=0)")
    return new_items


# ============================================================
# 方式A・D 本体(Trial-01と同一設計の独立コピー。既存disfluency QA/
# Production音響処理は一切変更しない。Trial-02内で新方式との横並び比較を
# 行うために再掲する)。
# ============================================================
def _normalize_tokens(text):
    return [dq18._normalize_token(w) for w in text.split()]


def find_repeated_spans(tokens, min_words=1):
    n = len(tokens)
    candidates = []
    for i in range(n):
        if not tokens[i]:
            continue
        for j in range(i + 1, n):
            if tokens[i] != tokens[j]:
                continue
            k = 0
            while i + k < j and j + k < n and tokens[i + k] == tokens[j + k]:
                k += 1
            if k >= min_words:
                candidates.append((i, j, k))
    candidates.sort(key=lambda m: -m[2])
    selected = []
    covered = set()
    for i, j, k in candidates:
        rng = set(range(j, j + k)) | set(range(i, i + k))
        if rng & covered:
            continue
        covered |= rng
        selected.append((i, j, k))
    selected.sort(key=lambda m: m[0])
    return selected


def _canonical_repeat_count(span_tokens, canonical_tokens):
    if not span_tokens or not canonical_tokens:
        return 0
    n, m = len(canonical_tokens), len(span_tokens)
    count = 0
    for i in range(n - m + 1):
        if canonical_tokens[i:i + m] == span_tokens:
            count += 1
    return count


def _text_ngram_repetition(text, canonical_text=None, min_words=3):
    """ASR transcript(word-level timestampなし、空白split)に対する方式Aの
    text-only版。Secondary ASR(Azure)窓検知で使う。"""
    if not text:
        return {"matches": [], "flagged": False, "flagged_matches": [], "canonical_known": canonical_text is not None}
    tokens = _normalize_tokens(text)
    spans = find_repeated_spans(tokens, min_words=min_words)
    canonical_tokens = _normalize_tokens(canonical_text) if canonical_text else None
    raw_words = text.split()
    matches = []
    for i, j, k in spans:
        span_tokens = tokens[i:i + k]
        span_text = " ".join(raw_words[i:i + k]) if i + k <= len(raw_words) else " ".join(span_tokens)
        canon_count = _canonical_repeat_count(span_tokens, canonical_tokens) if canonical_tokens is not None else None
        intentional = (canon_count is not None and canon_count >= 2)
        category = "word" if k == 1 else ("phrase" if k <= 4 else "sentence")
        matches.append({"span_text": span_text, "n_words": k, "category": category,
                         "canonical_repeat_count": canon_count, "intentional": intentional,
                         "flagged": not intentional})
    flagged = [m for m in matches if m["flagged"]]
    return {"matches": matches, "flagged": bool(flagged), "flagged_matches": flagged,
            "canonical_known": canonical_tokens is not None}


def detect_ngram_repetition(words, canonical_text=None, min_words=3):
    tokens = [dq18._normalize_token(w["text"]) for w in words]
    spans = find_repeated_spans(tokens, min_words=min_words)
    canonical_tokens = _normalize_tokens(canonical_text) if canonical_text else None
    matches = []
    for i, j, k in spans:
        span_tokens = tokens[i:i + k]
        span_text = " ".join(w["text"] for w in words[i:i + k])
        canon_count = _canonical_repeat_count(span_tokens, canonical_tokens) if canonical_tokens is not None else None
        intentional = (canon_count is not None and canon_count >= 2)
        gap_seconds = round(words[j]["start"] - words[i + k - 1]["end"], 3)
        category = "word" if k == 1 else ("phrase" if k <= 4 else "sentence")
        matches.append({
            "span_text": span_text, "n_words": k, "category": category,
            "first_start_s": round(words[i]["start"], 3), "first_end_s": round(words[i + k - 1]["end"], 3),
            "second_start_s": round(words[j]["start"], 3), "second_end_s": round(words[j + k - 1]["end"], 3),
            "gap_seconds": gap_seconds, "canonical_repeat_count": canon_count, "intentional": intentional,
            "flagged": not intentional,
        })
    flagged = [m for m in matches if m["flagged"]]
    return {"matches": matches, "flagged": bool(flagged), "flagged_matches": flagged,
            "word_count": len(words), "canonical_known": canonical_tokens is not None}


def run_method_a(manifest=None):
    """方式A(min_words=3、Trial-01で`VALIDATED`)。false start型陽性を
    含む本Trialの全EN項目に対して再実行し、新方式との役割分担・重複を
    実データで確認する(ローカルfaster-whisper、追加課金ゼロ)。"""
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    results = {}
    for item in manifest:
        if item.get("language") != "en":
            continue
        t0 = time.time()
        words = dq18.transcribe_verbatim(item["path"], language="en", model_size="small")
        proposed = detect_ngram_repetition(words, canonical_text=item.get("canonical_text"), min_words=3)
        results[item["item_id"]] = {
            "word_count": len(words),
            "proposed_ngram_min3_canonical_crosscheck": proposed,
            "elapsed_seconds": round(time.time() - t0, 2),
        }
        log(f"  [MethodA] {item['item_id']}: flagged={proposed['flagged']} ({len(proposed['flagged_matches'])} spans)")
    with open(f"{RESULTS_DIR}/method_a_local_verbatim.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


def spectral_self_similarity(path, frame_ms=25.0, hop_ms=10.0, min_lag_s=1.0, top_k=5):
    data, sr = load_wav(path)
    mono = to_mono(data)
    if np.abs(mono).max() > 0:
        mono = mono / (np.abs(mono).max() + 1e-9)

    frame_len = int(sr * frame_ms / 1000.0)
    hop_len = int(sr * hop_ms / 1000.0)
    n_frames = 1 + max(0, (len(mono) - frame_len) // hop_len)
    if n_frames < 2:
        return {"path": path, "sample_rate": sr, "duration_seconds": round(len(mono) / sr, 3), "top_matches": []}

    window = np.hanning(frame_len)
    spec = np.zeros((n_frames, frame_len // 2 + 1))
    for i in range(n_frames):
        start = i * hop_len
        frame = mono[start:start + frame_len]
        if len(frame) < frame_len:
            frame = np.pad(frame, (0, frame_len - len(frame)))
        spec[i] = np.abs(np.fft.rfft(frame * window))

    logspec = np.log1p(spec)
    norms = np.linalg.norm(logspec, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    normed = logspec / norms
    sim = normed @ normed.T

    min_lag_frames = int(min_lag_s * 1000.0 / hop_ms)
    n = sim.shape[0]
    candidates = []
    for i in range(n):
        for j in range(i + min_lag_frames, n):
            candidates.append((sim[i, j], i, j))
    candidates.sort(key=lambda x: -x[0])

    top = []
    seen_pairs = set()
    for score, i, j in candidates:
        key = (i // 20, j // 20)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        top.append({"similarity": round(float(score), 4),
                     "time_a_seconds": round(i * hop_ms / 1000.0, 3),
                     "time_b_seconds": round(j * hop_ms / 1000.0, 3),
                     "lag_seconds": round((j - i) * hop_ms / 1000.0, 3)})
        if len(top) >= top_k:
            break

    run_lengths = []
    for entry in top[:3]:
        i0 = int(round(entry["time_a_seconds"] * 1000.0 / hop_ms))
        lag = int(round(entry["lag_seconds"] * 1000.0 / hop_ms))
        threshold = 0.85
        k = 0
        while (i0 + k < n and i0 + k + lag < n and sim[i0 + k, i0 + k + lag] >= threshold):
            k += 1
        run_lengths.append(round(k * hop_ms / 1000.0, 3))
    for idx, rl in enumerate(run_lengths):
        top[idx]["run_length_seconds_at_thresh_0.85"] = rl

    return {"path": path, "sample_rate": sr, "duration_seconds": round(len(mono) / sr, 3),
            "frame_ms": frame_ms, "hop_ms": hop_ms, "min_lag_seconds": min_lag_s, "top_matches": top}


def run_method_d(manifest=None):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    results = {}
    for item in manifest:
        t0 = time.time()
        sim = spectral_self_similarity(item["path"])
        best_run = max((m.get("run_length_seconds_at_thresh_0.85", 0.0) for m in sim["top_matches"]), default=0.0)
        results[item["item_id"]] = {
            "duration_seconds": sim["duration_seconds"],
            "best_run_length_seconds": best_run,
            "top_matches": sim["top_matches"],
            "elapsed_seconds": round(time.time() - t0, 2),
        }
        log(f"  [MethodD] {item['item_id']}: best_run_length={best_run:.3f}s")
    with open(f"{RESULTS_DIR}/method_d_spectral_self_similarity.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# 方式D拡張(D'): run長優先・短run(0.3〜1.5秒)・低lag(0.5〜2.0秒)の
# 自己相関探索。OPEN-112診断(b1_fsp1_recheck/recheck_script.py の
# short_run_rescan)と同一設計だが、(a)先頭数秒限定ではなく全体、または
# 先頭数秒限定のどちらでも呼べるよう一般化、(b)hop_ms=10で計算量を抑制。
# lag範囲を固定幅に制限しているため、file長に対してほぼ線形時間で動作する
# (Method Dのtop-k類似度優先探索とは異なり、run長そのものを直接最大化する
# ため、run長が短い[似ているが短時間しか続かない]false start型を検知しやすい
# という設計上の狙い)。
# ============================================================
def short_run_priority_autocorrelation(path, time_a_max=None, lag_min=0.5, lag_max=2.0,
                                        frame_ms=25.0, hop_ms=10.0, thresholds=(0.6, 0.7, 0.8)):
    data, sr = load_wav(path)
    mono = to_mono(data)
    if np.abs(mono).max() > 0:
        mono = mono / (np.abs(mono).max() + 1e-9)
    total_dur = len(mono) / sr

    if time_a_max is not None:
        slice_end_s = min(total_dur, time_a_max + lag_max + 0.5)
        mono_scan = mono[:int(slice_end_s * sr)]
    else:
        mono_scan = mono

    frame_len = int(sr * frame_ms / 1000.0)
    hop_len = int(sr * hop_ms / 1000.0)
    n_frames = 1 + max(0, (len(mono_scan) - frame_len) // hop_len)
    if n_frames < 2:
        return {"path": path, "duration_seconds": round(total_dur, 3), "time_a_max": time_a_max,
                "lag_range": [lag_min, lag_max], "best_by_threshold": {}}

    window = np.hanning(frame_len)
    spec = np.zeros((n_frames, frame_len // 2 + 1))
    for i in range(n_frames):
        start = i * hop_len
        frame = mono_scan[start:start + frame_len]
        if len(frame) < frame_len:
            frame = np.pad(frame, (0, frame_len - len(frame)))
        spec[i] = np.abs(np.fft.rfft(frame * window))
    logspec = np.log1p(spec)
    norms = np.linalg.norm(logspec, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    normed = logspec / norms
    sim = normed @ normed.T

    hop_s = hop_ms / 1000.0
    n = sim.shape[0]
    i_limit = n if time_a_max is None else min(n, int(time_a_max / hop_s) + 1)
    lag_min_f = max(1, int(lag_min / hop_s))
    lag_max_f = int(lag_max / hop_s)

    best_by_thresh = {}
    for thr in thresholds:
        best = {"run_length_seconds": 0.0, "time_a": None, "lag": None}
        for i0 in range(0, i_limit):
            max_lag_f = min(lag_max_f, n - i0 - 1)
            if max_lag_f < lag_min_f:
                continue
            for lag_f in range(lag_min_f, max_lag_f + 1):
                k = 0
                while (i0 + k < n and i0 + k + lag_f < n and sim[i0 + k, i0 + k + lag_f] >= thr):
                    k += 1
                run_s = k * hop_s
                if run_s > best["run_length_seconds"]:
                    best = {"run_length_seconds": round(run_s, 3), "time_a": round(i0 * hop_s, 3),
                            "lag": round(lag_f * hop_s, 3), "similarity_at_start": round(float(sim[i0, i0 + lag_f]), 4)}
        best_by_thresh[str(thr)] = best
    return {"path": path, "duration_seconds": round(total_dur, 3), "time_a_max": time_a_max,
            "lag_range": [lag_min, lag_max], "hop_ms": hop_ms, "best_by_threshold": best_by_thresh}


def run_method_d_prime(manifest=None, time_a_max=None, tag="full"):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    results = {}
    for item in manifest:
        t0 = time.time()
        r = short_run_priority_autocorrelation(item["path"], time_a_max=time_a_max)
        r["elapsed_seconds"] = round(time.time() - t0, 2)
        results[item["item_id"]] = r
        best06 = r["best_by_threshold"].get("0.6", {})
        log(f"  [MethodD'/{tag}] {item['item_id']}: run@0.6={best06.get('run_length_seconds')}s "
            f"lag={best06.get('lag')} elapsed={r['elapsed_seconds']}s")
    out_path = f"{RESULTS_DIR}/method_d_prime_{tag}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log(f"run_method_d_prime[{tag}] -> {out_path}")
    return results


# ============================================================
# onset二重化検知: RMSエネルギー包絡のonsetが「話し始め→短い相対的な
# エネルギー低下→再びonset」というパターンを示すかを、ASR非依存・軽量に
# 判定する。lag(2つのonset間隔)が0.4〜2.2秒の範囲にある候補ペアのうち、
# 間のRMS最小値が前後onsetの最大rms_normに対してどれだけ低いか(dip_ratio)
# を計算し、最も低いdip_ratioを検知指標とする(小さいほど「一度弱まって
# 再度立ち上がる」パターンが強い)。
# ============================================================
def rms_envelope(mono, sr, frame_ms=20.0, hop_ms=5.0):
    frame_len = int(sr * frame_ms / 1000.0)
    hop_len = int(sr * hop_ms / 1000.0)
    n_frames = 1 + max(0, (len(mono) - frame_len) // hop_len)
    rms = np.zeros(n_frames)
    times = np.zeros(n_frames)
    for i in range(n_frames):
        start = i * hop_len
        frame = mono[start:start + frame_len]
        rms[i] = np.sqrt(np.mean(frame.astype(np.float64) ** 2)) if len(frame) else 0.0
        times[i] = start / sr
    return times, rms


def detect_onsets(times, rms, min_gap_s=0.15):
    if rms.max() <= 0:
        return []
    norm = rms / rms.max()
    diff = np.diff(norm, prepend=norm[0])
    diff[diff < 0] = 0.0
    pos = diff[diff > 0]
    thresh = (pos.mean() + 1.5 * pos.std()) if len(pos) else 0.05
    thresh = max(thresh, 0.03)
    onsets = []
    last_t = -999.0
    for i in range(1, len(diff) - 1):
        if diff[i] >= thresh and diff[i] >= diff[i - 1] and diff[i] >= diff[i + 1]:
            t = times[i]
            if t - last_t >= min_gap_s:
                onsets.append({"time": round(float(t), 3), "diff": round(float(diff[i]), 4),
                                "rms_norm": round(float(norm[i]), 4)})
                last_t = t
    return onsets


def onset_dual_cluster_detection(path, t_end=6.0, lag_min=0.4, lag_max=2.2):
    data, sr = load_wav(path)
    mono = to_mono(data)
    total_dur = len(mono) / sr
    seg_end = min(t_end, total_dur)
    seg = mono[:int(seg_end * sr)]
    times, rms = rms_envelope(seg, sr)
    if rms.max() <= 0:
        return {"path": path, "onsets": [], "candidates": [], "best": None}
    norm = rms / rms.max()
    onsets = detect_onsets(times, rms)

    candidates = []
    for a in range(len(onsets)):
        for b in range(a + 1, len(onsets)):
            lag = round(onsets[b]["time"] - onsets[a]["time"], 3)
            if not (lag_min <= lag <= lag_max):
                continue
            i_idx = int(round(onsets[a]["time"] / (times[1] - times[0]))) if len(times) > 1 else 0
            j_idx = int(round(onsets[b]["time"] / (times[1] - times[0]))) if len(times) > 1 else 0
            i_idx = max(0, min(i_idx, len(norm) - 1))
            j_idx = max(0, min(j_idx, len(norm) - 1))
            if j_idx <= i_idx:
                continue
            between = norm[i_idx:j_idx + 1]
            local_min = float(between.min())
            ref_peak = max(onsets[a]["rms_norm"], onsets[b]["rms_norm"])
            dip_ratio = round(local_min / ref_peak, 4) if ref_peak > 0 else 1.0
            candidates.append({"onset_a_time": onsets[a]["time"], "onset_b_time": onsets[b]["time"],
                                "lag_seconds": lag, "dip_ratio": dip_ratio})
    best = min(candidates, key=lambda c: c["dip_ratio"]) if candidates else None
    return {"path": path, "duration_seconds": round(total_dur, 3), "onsets": onsets,
            "n_candidates": len(candidates), "best": best}


def run_method_onset(manifest=None, t_end=6.0):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    results = {}
    for item in manifest:
        t0 = time.time()
        r = onset_dual_cluster_detection(item["path"], t_end=t_end)
        r["elapsed_seconds"] = round(time.time() - t0, 2)
        results[item["item_id"]] = r
        best = r.get("best")
        log(f"  [MethodOnset] {item['item_id']}: best_dip_ratio={best['dip_ratio'] if best else None} "
            f"n_candidates={r['n_candidates']}")
    with open(f"{RESULTS_DIR}/method_onset_dual_cluster.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# 方式A-ext v2: 単語duration異常検知の参照corpus拡充。Trial-01の
# 陰性26音声(rerun-02)に加え、既存PASS済み音声(tts_generation_results.json
# でstatus=OK確認済みのnarration wav)を無料で追加する。既知のhallucination
# 汚染源(open112_trend_theme2_b_full_audio_trial_13、Point Two/In One Line
# 重複バグの発生元)と、STOPPED記録のあるsegment(open109の
# full_story_part1系)は明示的に除外する(汚染混入を避ける安全側の設計)。
# ============================================================
EN_WHITELIST_BASENAMES = {
    "kp1_en", "kp2_en", "kp3_en", "kp4_en", "kp5_en",
    "full_story_part1", "full_story_part1_original", "full_story_part2", "full_story_part2_original",
    "full_story_intro", "full_story_intro_charon",
    "in_one_line", "in_one_line_original",
    "point_one", "point_one_original", "point_one_heading", "point_one_heading_original",
    "point_two", "point_two_original", "point_two_heading", "point_two_heading_original",
    "point_explanation", "topic_intro", "welcome", "welcome_charon",
    "key_phrases_intro", "key_phrases_intro_charon", "preview_intro", "preview_intro_charon",
}

# 追加参照corpus元(既存PASS済み、他タスクの成果物を読み取り専用で使うのみ、
# 一切変更しない)。open112_trend_theme2_b_full_audio_trial_13は
# Point Two/In One Line hallucinationバグの発生元そのものであるため、
# 汚染回避のため意図的に除外する。open109の`full_story_part1`系は
# tts_generation_results.jsonでSTOPPED記録があるため除外する。
REFERENCE_EXTRA_DIRS = [
    ("er011_output/assembly_headroom_wiring_01/n18_a2_regress/a2/narration", set()),
    ("er011_output/no18_tight_speech_only_removal_trial_15/theme_root/a2/narration", set()),
    ("er011_output/open109_a2_pre_regenerate_backup_04/a2_before/narration",
     {"full_story_part1", "full_story_part1_original"}),
    ("er011_output/open117_keyphrase_display_tts_separation_trial_02/a2/narration", set()),
    ("er011_output/open117_keyphrase_display_tts_separation_trial_02/b1b/narration", set()),
]


def collect_extra_reference_paths():
    paths = []
    for dir_path, exclude_basenames in REFERENCE_EXTRA_DIRS:
        if not os.path.isdir(dir_path):
            log(f"  [ref_v2, skip missing dir] {dir_path}")
            continue
        for fn in sorted(os.listdir(dir_path)):
            if not fn.endswith(".wav"):
                continue
            base = fn[:-4]
            if base in exclude_basenames:
                continue
            if base not in EN_WHITELIST_BASENAMES:
                continue
            paths.append(os.path.join(dir_path, fn))
    return paths


def build_word_duration_reference_v2(manifest=None):
    """Trial-01の陰性26音声(rerun-02、EN分のみ)+ 上記追加dirのEN
    whitelist音声から、単語(正規化後)ごとの典型duration分布を構築する。"""
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    base_paths = [m["path"] for m in manifest
                  if m.get("language") == "en" and m.get("source") == "reused_production_pass"]
    extra_paths = collect_extra_reference_paths()
    all_paths = base_paths + extra_paths
    log(f"build_word_duration_reference_v2: {len(base_paths)} base(reused Trial-01) + "
        f"{len(extra_paths)} extra = {len(all_paths)} reference audio files")

    ref = {}
    per_source_word_counts = {}
    for path in all_paths:
        words = dq18.transcribe_verbatim(path, language="en", model_size="small")
        per_source_word_counts[path] = len(words)
        for w in words:
            text = dq18._normalize_token(w["text"])
            dur = w["end"] - w["start"]
            if text and dur > 0:
                ref.setdefault(text, []).append(dur)
    reference = {k: {"median": float(np.median(v)), "n": len(v), "max": max(v), "min": min(v)}
                 for k, v in ref.items()}
    with open(f"{RESULTS_DIR}/word_duration_reference_v2.json", "w", encoding="utf-8") as f:
        json.dump(reference, f, ensure_ascii=False, indent=2)
    with open(f"{AUDIT_DIR}/word_duration_reference_v2_sources.json", "w", encoding="utf-8") as f:
        json.dump({"n_files": len(all_paths), "n_unique_words": len(reference),
                    "files": all_paths, "words_per_file": per_source_word_counts}, f, ensure_ascii=False, indent=2)
    log(f"build_word_duration_reference_v2: {len(reference)} unique words "
        f"(Trial-01 v1 had 372 unique words). september -> {reference.get('september')}")
    return reference


def detect_word_duration_anomaly_same_word_ref(words, reference, ratio_threshold=1.8):
    anomalies = []
    for w in words:
        text = dq18._normalize_token(w["text"])
        dur = w["end"] - w["start"]
        ref_entry = reference.get(text)
        if not text or dur <= 0 or ref_entry is None:
            continue
        ratio = dur / ref_entry["median"] if ref_entry["median"] > 0 else 0
        if ratio >= ratio_threshold:
            anomalies.append({"word": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3),
                               "duration_seconds": round(dur, 3), "reference_median_seconds": round(ref_entry["median"], 3),
                               "reference_n": ref_entry["n"], "ratio": round(ratio, 2)})
    return {"flagged": bool(anomalies), "anomalies": anomalies, "method": "same_word_reference_v2"}


def run_method_a_ext_v2(manifest=None, reference=None, ratio_thresholds=(1.8, 2.0, 2.2, 2.5)):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    if reference is None:
        ref_path = f"{RESULTS_DIR}/word_duration_reference_v2.json"
        reference = json.load(open(ref_path, encoding="utf-8"))
    results = {}
    for item in manifest:
        if item.get("language") != "en":
            continue
        t0 = time.time()
        words = dq18.transcribe_verbatim(item["path"], language="en", model_size="small")
        per_thresh = {str(rt): detect_word_duration_anomaly_same_word_ref(words, reference, ratio_threshold=rt)
                      for rt in ratio_thresholds}
        results[item["item_id"]] = {"word_count": len(words), "by_ratio_threshold": per_thresh,
                                     "elapsed_seconds": round(time.time() - t0, 2)}
        log(f"  [MethodA-extV2] {item['item_id']}: flagged@1.8="
            f"{per_thresh['1.8']['flagged']} flagged@2.5={per_thresh['2.5']['flagged']}")
    with open(f"{RESULTS_DIR}/method_a_ext_v2_word_duration.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# Secondary ASR(Azure)窓検知: 先頭N秒の短窓をAzure Speech STT
# (診断専用呼び出し、既存English Primary経路には未採用のまま)へ投入し、
# 生transcript上の反復表記(text-only n-gram)を検出する。false start型
# 向けに範囲を絞った軽量な補完策(Point Two/In One Line等、窓の外で
# 起きる反復は原理的にスコープ外、既知の限界として明記する)。
# ============================================================
def run_method_secondary_asr_window(manifest=None, window_seconds=6.0, min_words_variants=(2, 3)):
    manifest = manifest or json.load(open(MANIFEST_PATH, encoding="utf-8"))
    cost_logger.install(COST_LOG_PATH)
    os.makedirs(f"{AUDIT_DIR}/azure_window_clips", exist_ok=True)
    results = {}
    with cost_logger.logging_context("OPEN-121-TRIAL-02", "secondary_asr_window_azure"):
        for item in manifest:
            if item.get("language") != "en":
                continue
            assert_budget_ok(f"before {item['item_id']}")
            data, sr = load_wav(item["path"])
            total_dur = len(data) / sr
            w1 = min(window_seconds, total_dur)
            clip = data[:int(round(w1 * sr))]
            clip_path = f"{AUDIT_DIR}/azure_window_clips/{item['item_id']}.wav"
            write_wav(clip_path, clip, sr)
            with cost_logger.segment_context(item["item_id"]):
                t0 = time.time()
                text, err = p4_azure.get_full_text_via_azure_stt_continuous(
                    clip_path, language="en-US", timeout_seconds=30.0)
                elapsed = round(time.time() - t0, 2)
            os.remove(clip_path)
            canon = item.get("canonical_text")
            checks = {str(mw): _text_ngram_repetition(text, canon, min_words=mw) for mw in min_words_variants}
            results[item["item_id"]] = {
                "window_seconds": round(w1, 3), "azure_text": text, "error": err,
                "elapsed_seconds": elapsed, "checks_by_min_words": checks,
            }
            log(f"  [Azure-window] {item['item_id']}: text={text!r} "
                f"flagged@min2={checks['2']['flagged']} flagged@min3={checks['3']['flagged']} "
                f"cost_so_far={compute_cost_jpy_so_far()[0]:.2f}JPY")
    with open(f"{RESULTS_DIR}/method_secondary_asr_azure_window.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


# ============================================================
# 結果集計 + player.html
# ============================================================
def _load_json_if_exists(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


def build_results_table():
    manifest = {m["item_id"]: m for m in json.load(open(MANIFEST_PATH, encoding="utf-8"))}
    method_a = _load_json_if_exists(f"{RESULTS_DIR}/method_a_local_verbatim.json")
    method_d = _load_json_if_exists(f"{RESULTS_DIR}/method_d_spectral_self_similarity.json")
    method_d_prime_full = _load_json_if_exists(f"{RESULTS_DIR}/method_d_prime_full.json")
    method_d_prime_head = _load_json_if_exists(f"{RESULTS_DIR}/method_d_prime_head6s.json")
    method_onset = _load_json_if_exists(f"{RESULTS_DIR}/method_onset_dual_cluster.json")
    method_a_ext_v2 = _load_json_if_exists(f"{RESULTS_DIR}/method_a_ext_v2_word_duration.json")
    method_azure = _load_json_if_exists(f"{RESULTS_DIR}/method_secondary_asr_azure_window.json")

    rows = []
    for item_id, item in manifest.items():
        a = method_a.get(item_id)
        d = method_d.get(item_id)
        dpf = method_d_prime_full.get(item_id)
        dph = method_d_prime_head.get(item_id)
        onset = method_onset.get(item_id)
        ext2 = method_a_ext_v2.get(item_id)
        az = method_azure.get(item_id)
        row = {
            "item_id": item_id, "label": item.get("label"), "source": item.get("source"),
            "language": item.get("language"), "duration_seconds": item.get("duration_seconds"),
            "method_a_min3_flagged": a["proposed_ngram_min3_canonical_crosscheck"]["flagged"] if a else None,
            "method_d_best_run_length_seconds": d["best_run_length_seconds"] if d else None,
            "method_d_prime_full_run_at_0.6": dpf["best_by_threshold"].get("0.6", {}).get("run_length_seconds") if dpf else None,
            "method_d_prime_head6s_run_at_0.6": dph["best_by_threshold"].get("0.6", {}).get("run_length_seconds") if dph else None,
            "method_onset_best_dip_ratio": (onset.get("best") or {}).get("dip_ratio") if onset else None,
            "method_a_ext_v2_flagged_at_2.5": ext2["by_ratio_threshold"].get("2.5", {}).get("flagged") if ext2 else None,
            "method_azure_window_flagged_min3": az["checks_by_min_words"].get("3", {}).get("flagged") if az else None,
            "method_azure_window_flagged_min2": az["checks_by_min_words"].get("2", {}).get("flagged") if az else None,
        }
        rows.append(row)
    with open(f"{RESULTS_DIR}/summary_table.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    log(f"summary_table: {len(rows)} rows -> {RESULTS_DIR}/summary_table.json")
    return rows


def build_player_html():
    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    rows = _load_json_if_exists(f"{RESULTS_DIR}/summary_table.json")
    by_id = {r["item_id"]: r for r in rows} if isinstance(rows, list) else {}

    def section(title, items):
        html = [f"<h2>{title}</h2><table border=1 cellpadding=4 style='border-collapse:collapse'>"]
        html.append("<tr><th>item_id</th><th>audio</th><th>lang</th><th>dur(s)</th>"
                     "<th>MethodA min3</th><th>MethodD run(s)</th>"
                     "<th>MethodD' full run@0.6</th><th>MethodD' head6s run@0.6</th>"
                     "<th>Onset best dip_ratio</th><th>A-extV2 flagged@2.5</th>"
                     "<th>Azure-window flagged(min3/min2)</th><th>note</th></tr>")
        for item in items:
            r = by_id.get(item["item_id"], {})
            rel = os.path.relpath(item["path"], OUT_DIR).replace("\\", "/")
            html.append("<tr>"
                         f"<td>{item['item_id']}</td>"
                         f"<td><audio controls src='{rel}'></audio></td>"
                         f"<td>{item.get('language')}</td>"
                         f"<td>{item.get('duration_seconds')}</td>"
                         f"<td>{r.get('method_a_min3_flagged')}</td>"
                         f"<td>{r.get('method_d_best_run_length_seconds')}</td>"
                         f"<td>{r.get('method_d_prime_full_run_at_0.6')}</td>"
                         f"<td>{r.get('method_d_prime_head6s_run_at_0.6')}</td>"
                         f"<td>{r.get('method_onset_best_dip_ratio')}</td>"
                         f"<td>{r.get('method_a_ext_v2_flagged_at_2.5')}</td>"
                         f"<td>{r.get('method_azure_window_flagged_min3')}/{r.get('method_azure_window_flagged_min2')}</td>"
                         f"<td style='max-width:400px;font-size:11px'>{item.get('note', '')}</td>"
                         "</tr>")
        html.append("</table>")
        return "\n".join(html)

    positives_real = [m for m in manifest if m["source"] == "real_confirmed"]
    positives_synth = [m for m in manifest if m["source"] == "synthetic"]
    positives_falsestart = [m for m in manifest if m["source"] == "synthetic_falsestart"]
    negatives_reused = [m for m in manifest if m["source"] == "reused_production_pass"]
    negatives_new = [m for m in manifest if m["source"] in
                      ("new_standard_tts_intentional_repetition", "new_standard_tts_natural_attempt")]

    html = ["<html><head><meta charset='utf-8'><title>OPEN-121 Trial-02 player</title></head><body>",
            "<h1>OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-02</h1>",
            "<p>false start型検知の追加方式(D拡張・onset二重化・A-ext参照corpus拡充・"
            "Secondary ASR窓検知)。方式A/D(Trial-01 VALIDATED)を横並び比較用に再掲。</p>",
            section("1. 陽性(実在、確認済み: Point Two/In One Line/B1 FSP1 false start)", positives_real),
            section("2. 陽性(合成、句・文単位反復)", positives_synth),
            section("3. 陽性(合成、false start型: 先頭を切って前置)", positives_falsestart),
            section("4. 陰性(既存Production PASS音声の再利用)", negatives_reused),
            section("5. 陰性(新規Standard TTS: 意図的反復 / 自然hallucination試行)", negatives_new),
            "</body></html>"]
    out_path = f"{OUT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    log(f"player.html -> {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=[
        "reuse_test_set", "build_synthetic_falsestart_positives",
        "run_method_a", "run_method_d",
        "run_method_d_prime_full", "run_method_d_prime_head6s",
        "run_method_onset",
        "build_word_duration_reference_v2", "run_method_a_ext_v2",
        "run_method_secondary_asr_window",
        "build_results_table", "build_player_html",
    ])
    args = parser.parse_args()
    if args.phase == "reuse_test_set":
        reuse_trial01_test_set()
    elif args.phase == "build_synthetic_falsestart_positives":
        build_synthetic_falsestart_positives()
    elif args.phase == "run_method_a":
        run_method_a()
    elif args.phase == "run_method_d":
        run_method_d()
    elif args.phase == "run_method_d_prime_full":
        run_method_d_prime(time_a_max=None, tag="full")
    elif args.phase == "run_method_d_prime_head6s":
        run_method_d_prime(time_a_max=6.0, tag="head6s")
    elif args.phase == "run_method_onset":
        run_method_onset()
    elif args.phase == "build_word_duration_reference_v2":
        build_word_duration_reference_v2()
    elif args.phase == "run_method_a_ext_v2":
        run_method_a_ext_v2()
    elif args.phase == "run_method_secondary_asr_window":
        run_method_secondary_asr_window()
    elif args.phase == "build_results_table":
        build_results_table()
    elif args.phase == "build_player_html":
        build_player_html()
