# ============================================================
# er011_open121_repetition_qa_production_01.py
# OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01
# ============================================================
# ユーザー承認2026-09-07(APPROVED_FOR_PRODUCTION、範囲限定)。
#
# Trial-01(er011_open121_tts_repetition_general_qa_trial_01.py)・
# Trial-02(er011_open121_tts_repetition_general_qa_trial_02.py)で
# `VALIDATED`となった3方式を、判定ロジックは無変更のまま移植する:
#   - 方式A: n-gram句・文単位反復検知(min_words>=3、canonical
#     crosscheck付き)。Point Two/In One Line型(句・文まるごと反復、
#     gap 8〜10秒超)を検知。
#   - 方式D: スペクトルself-similarity(min_lag=1.0秒、top-k類似度
#     優先探索)。方式Aと同じ型に加え合成phrase/sentence型を検知。
#   - 方式D': 方式Dと**同一の対数スペクトル自己相関という計算
#     primitiveを共有**するが、探索するlag帯域(0.5〜2.0秒)とrun長
#     最大化の探索戦略が異なる派生プロファイル。false start/aborted
#     restart型(語の途中で切れて即再開、B1 FSP1型)を検知。
#
# 統合スペクトル計算(Trial-02 §4/§7-5の実装効率化指摘に対応):
# 方式D・D'は同一音声に対して独立に対数スペクトル自己相関行列を計算
# すると同じFFTフレーム計算を2回行うことになるため、本モジュールでは
# `compute_shared_self_similarity()`で1回だけ計算し、2つの独立した
# プロファイル(D=長lag・top-k類似度優先、D'=短lag・run長優先)で
# 同じ類似度行列を再利用する。検知ロジック自体(パラメータ・閾値・
# 探索アルゴリズム)は一切変更していない。
#
# 適用範囲(ユーザー承認範囲): A2/B1の英語本文segment
# (full_story_part1/2・point_one・point_two)のみ。Key Phrase・日本語・
# Comment/Preview/Title/In One Line等は対象外。呼び出し元が新規opt-in
# フラグ(`enabled=True`)を明示的に渡した場合のみ動作し、既定はFalse
# (対象外segmentへの影響ゼロを保証)。OPEN-122
# (Connected Speech Equivalence Layer)と同じ設計パターン。
#
# 接続パターン: 既存`er008_disfluency_qa_18.apply_disfluency_gate()`と
# 同一のANDゲート(`verified = verified and not flagged`)。新規retry
# 回数・新規Cost Guard予算は一切追加しない。方式A/D/D'はいずれも
# ローカルCPU計算のみ(追加API課金ゼロ)であり、既存
# `review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`予算内でretryが自動発生し、
# 上限到達後は既存のSTOPPED→Human Review Lock自動遷移にそのまま
# 合流する(disfluency QAで実証済みの経路を再利用するだけ)。
#
# 境界値monitoring: flag/非flagにかかわらず、各segmentのMethod D/D'
# それぞれの最大run長・lag・similarityを`evaluate_repetition_qa()`の
# 戻り値(narration audit jsonへ記録される想定)へ常に含める。D'の
# 陽性最小run(0.7秒)と陰性最大run(0.5秒、マージン0.2秒)は、後から
# 閾値再校正する際にこの監査ログを使う。
#
# 未配線(Trial-01方式C-v2、gap<0.5秒の即座の言い直し)は本モジュールの
# 対象外。OPEN_ITEMS.md OPEN-121行へ追跡項目として記録する。
from __future__ import annotations

import re

import numpy as np
import soundfile as sf

import er008_disfluency_qa_18 as dq18

# ============================================================
# 判定閾値(Trial-01/02でVALIDATEDとなった値、無変更のまま移植)
# ============================================================
METHOD_A_MIN_WORDS = 3

METHOD_D_FRAME_MS = 25.0
METHOD_D_HOP_MS = 10.0
METHOD_D_MIN_LAG_SECONDS = 1.0
METHOD_D_TOP_K = 5
# 方式Dのrun長計算用の類似度閾値(top-k類似度優先探索、Trial-01と同一)。
METHOD_D_SIM_THRESHOLD = 0.85
# Trial-01較正値(陰性最大run長0.10秒/検知対象陽性最小run長0.16秒、
# 生データ: er011_output/open121_tts_repetition_general_qa_trial_01/
# results/method_d_threshold_calibration.json)。
METHOD_D_DECISION_RUN_SECONDS = 0.12

METHOD_D_PRIME_LAG_MIN_SECONDS = 0.5
METHOD_D_PRIME_LAG_MAX_SECONDS = 2.0
# 方式D'のrun長優先探索用の類似度閾値(Trial-02推奨構成、full-file)。
METHOD_D_PRIME_SIM_THRESHOLD = 0.7
# Trial-02較正値(陰性最大run長0.5秒[a2_comment_3]/陽性最小run長0.7秒、
# マージン0.2秒、生データ: er011_output/open121_tts_repetition_
# general_qa_trial_02/results/method_d_prime_full.json)。
METHOD_D_PRIME_DECISION_RUN_SECONDS = 0.6


def _load_wav_mono(path):
    data, sr = sf.read(path, always_2d=False)
    mono = data.astype(np.float64) if data.ndim == 1 else data.mean(axis=1).astype(np.float64)
    if np.abs(mono).max() > 0:
        mono = mono / (np.abs(mono).max() + 1e-9)
    return mono, sr


# ============================================================
# 統合スペクトル計算(方式D・D'共通、1回だけ計算する)
# ============================================================
def compute_shared_self_similarity(path, frame_ms=METHOD_D_FRAME_MS, hop_ms=METHOD_D_HOP_MS):
    """対数スペクトル自己相関の類似度行列を1回だけ計算し、方式D
    (long-lag top-k優先)・方式D'(short-lag run長優先)双方から
    再利用する(Trial-02 §4/§7-5)。計算式自体はTrial-01/02の
    spectral_self_similarity()/short_run_priority_autocorrelation()と
    同一(frame25ms/hop10ms、log1pスペクトル、L2正規化後の内積)。"""
    mono, sr = _load_wav_mono(path)
    duration_seconds = len(mono) / sr

    frame_len = int(sr * frame_ms / 1000.0)
    hop_len = int(sr * hop_ms / 1000.0)
    n_frames = 1 + max(0, (len(mono) - frame_len) // hop_len)
    if n_frames < 2:
        return {"path": path, "sample_rate": sr, "duration_seconds": round(duration_seconds, 3),
                "hop_ms": hop_ms, "frame_ms": frame_ms, "sim": None, "n_frames": n_frames}

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
    return {"path": path, "sample_rate": sr, "duration_seconds": round(duration_seconds, 3),
            "hop_ms": hop_ms, "frame_ms": frame_ms, "sim": sim, "n_frames": n_frames}


def analyze_profile_d_long_lag(bundle, min_lag_s=METHOD_D_MIN_LAG_SECONDS, top_k=METHOD_D_TOP_K,
                                sim_threshold=METHOD_D_SIM_THRESHOLD):
    """方式D(Trial-01、既存、無変更)。lag>=min_lag_sの候補ペアを類似度
    降順で最大top_k件選び(粗い重複除去つき)、上位3件それぞれについて
    類似度>=sim_thresholdが連続する長さ(run長)を測る。最大run長が
    METHOD_D_DECISION_RUN_SECONDS以上ならflagged=True。"""
    sim = bundle["sim"]
    hop_ms = bundle["hop_ms"]
    if sim is None:
        return {"top_matches": [], "best_run_length_seconds": 0.0, "min_lag_seconds": min_lag_s,
                "sim_threshold": sim_threshold, "decision_threshold_seconds": METHOD_D_DECISION_RUN_SECONDS,
                "flagged": False}
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
        k = 0
        while (i0 + k < n and i0 + k + lag < n and sim[i0 + k, i0 + k + lag] >= sim_threshold):
            k += 1
        run_lengths.append(round(k * hop_ms / 1000.0, 3))
    run_key = f"run_length_seconds_at_thresh_{sim_threshold}"
    for idx, rl in enumerate(run_lengths):
        top[idx][run_key] = rl

    best_run = max(run_lengths, default=0.0)
    return {"top_matches": top, "best_run_length_seconds": best_run, "min_lag_seconds": min_lag_s,
            "sim_threshold": sim_threshold, "decision_threshold_seconds": METHOD_D_DECISION_RUN_SECONDS,
            "flagged": best_run >= METHOD_D_DECISION_RUN_SECONDS}


def analyze_profile_d_prime_short_lag(bundle, lag_min=METHOD_D_PRIME_LAG_MIN_SECONDS,
                                       lag_max=METHOD_D_PRIME_LAG_MAX_SECONDS,
                                       sim_threshold=METHOD_D_PRIME_SIM_THRESHOLD, time_a_max=None):
    """方式D'(Trial-02、既存、無変更)。方式Dと同一のsim行列を使うが、
    探索するlag帯域を0.5〜2.0秒に制限し、各(開始時刻,lag)ペアでrun長を
    直接最大化する(run長優先探索、false start型のような短いrunを
    見逃しにくい)。time_a_max指定で先頭数秒限定の探索も可能(既定None
    =full-file、Trial-02推奨構成)。"""
    sim = bundle["sim"]
    hop_ms = bundle["hop_ms"]
    if sim is None:
        return {"best_run_length_seconds": 0.0, "time_a": None, "lag": None,
                "similarity_at_start": None, "lag_range_seconds": [lag_min, lag_max],
                "sim_threshold": sim_threshold,
                "decision_threshold_seconds": METHOD_D_PRIME_DECISION_RUN_SECONDS, "flagged": False}
    hop_s = hop_ms / 1000.0
    n = sim.shape[0]
    i_limit = n if time_a_max is None else min(n, int(time_a_max / hop_s) + 1)
    lag_min_f = max(1, int(lag_min / hop_s))
    lag_max_f = int(lag_max / hop_s)

    best = {"run_length_seconds": 0.0, "time_a": None, "lag": None, "similarity_at_start": None}
    for i0 in range(0, i_limit):
        max_lag_f = min(lag_max_f, n - i0 - 1)
        if max_lag_f < lag_min_f:
            continue
        for lag_f in range(lag_min_f, max_lag_f + 1):
            k = 0
            while (i0 + k < n and i0 + k + lag_f < n and sim[i0 + k, i0 + k + lag_f] >= sim_threshold):
                k += 1
            run_s = k * hop_s
            if run_s > best["run_length_seconds"]:
                best = {"run_length_seconds": round(run_s, 3), "time_a": round(i0 * hop_s, 3),
                        "lag": round(lag_f * hop_s, 3),
                        "similarity_at_start": round(float(sim[i0, i0 + lag_f]), 4)}
    best_run_length_seconds = best["run_length_seconds"]
    return {**best, "best_run_length_seconds": best_run_length_seconds,
            "lag_range_seconds": [lag_min, lag_max], "sim_threshold": sim_threshold,
            "decision_threshold_seconds": METHOD_D_PRIME_DECISION_RUN_SECONDS,
            "flagged": best_run_length_seconds >= METHOD_D_PRIME_DECISION_RUN_SECONDS}


def run_spectral_checks(path):
    """方式D・D'を統合スペクトル計算1回で実行する(Trial-02 §4/§7-5)。
    flag/非flagにかかわらず、境界値monitoring用に両プロファイルの
    最大run長・lag・similarityを常に返す。"""
    bundle = compute_shared_self_similarity(path)
    profile_d = analyze_profile_d_long_lag(bundle)
    profile_d_prime = analyze_profile_d_prime_short_lag(bundle)
    return {
        "duration_seconds": bundle["duration_seconds"],
        "profile_d": profile_d,
        "profile_d_prime": profile_d_prime,
    }


# ============================================================
# 方式A: n-gram句・文単位反復検知(Trial-01、既存、無変更移植)
# ============================================================
# OPEN-127-EM-DASH-TOKEN-BOUNDARY-PRODUCTION-WIRING-01: ユーザー承認
# 2026-09-08(candidate1a_emdash_only_split、
# TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01_REPORT.md)。
# em dash(—, U+2014)前後に空白が無い米国式タイポグラフィ(例:
# "...the people I need—or do not need—around me.")の場合、
# text.split()が"need—or"を1 tokenとして扱ってしまい、
# `_canonical_repeat_count()`がcanonical側の意図的な反復出現数を
# 過小カウントし、Voice B並行構文のような正常な意図的反復を誤flagして
# いた(2026-09-08 Trial実データ再現)。em dash **のみ**を空白へ置換して
# token境界として扱う(en dash "–"・hyphen "-"は対象外、汎用regex
# tokenizerへの拡張は禁止、ユーザー承認範囲を超えない)。ASR側token
# (`detect_ngram_repetition`のtokens、word-level ASR出力)は元々1語ずつ
# 独立して現れるため本変更の影響を受けない。
def _normalize_tokens(text):
    text = re.sub("—", " ", text)
    return [dq18._normalize_token(w) for w in text.split()]


def find_repeated_spans(tokens, min_words=1):
    """tokens内で、非隣接も含めた完全一致の反復spanを検出する。各pairに
    ついて最長一致(k)まで貪欲に延長し、既に選ばれたspanと重なる短い
    候補は除外する(最長優先)。"""
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
    """span_tokens(反復として検知されたtoken列)が、canonical_text側にも
    複数回出現するか(=台本自体が意図した反復である可能性)を数える。"""
    if not span_tokens or not canonical_tokens:
        return 0
    n, m = len(canonical_tokens), len(span_tokens)
    count = 0
    for i in range(n - m + 1):
        if canonical_tokens[i:i + m] == span_tokens:
            count += 1
    return count


def detect_ngram_repetition(words, canonical_text=None, min_words=METHOD_A_MIN_WORDS):
    """方式A(Trial-01、既存、無変更)。wordsはfaster-whisper word-level
    timestamps(dq18.transcribe_verbatim()の戻り値)。min_words=3で
    phrase/sentence-level(3語以上)の非隣接反復を検知し、canonicalへの
    照合で意図的反復(台本に元々複数回同じ語句がある場合)を除外する。"""
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
            "word_count": len(words), "canonical_known": canonical_tokens is not None,
            "min_words": min_words}


def run_ngram_check(path, canonical_text, language="en", min_words=METHOD_A_MIN_WORDS, model_size="small"):
    """方式Aをwavファイルへ実行する(ローカルfaster-whisper、追加API課金
    なし)。既存dq18.transcribe_verbatim()を無変更のまま呼び出す。"""
    words = dq18.transcribe_verbatim(path, language=language, model_size=model_size)
    return detect_ngram_repetition(words, canonical_text=canonical_text, min_words=min_words)


# ============================================================
# 統合判定 + Production Gate
# ============================================================
def evaluate_repetition_qa(path, canonical_text, language="en"):
    """方式A + D + D'を1segmentへ実行し、いずれか1つでもflagged=Trueなら
    全体をflagged=Trueとする(Trial-02 §7推奨統合仕様)。flag/非flagに
    かかわらず、方式D/D'それぞれの最大run長・lag・similarityを常に
    含める(境界値monitoring用、narration audit jsonへそのまま記録
    できる形)。"""
    ngram = run_ngram_check(path, canonical_text, language=language)
    spectral = run_spectral_checks(path)
    flagged = bool(ngram["flagged"] or spectral["profile_d"]["flagged"]
                   or spectral["profile_d_prime"]["flagged"])
    return {
        "flagged": flagged,
        "duration_seconds": spectral["duration_seconds"],
        "method_a_ngram": ngram,
        "method_d_spectral_long_lag": spectral["profile_d"],
        "method_d_prime_spectral_short_lag": spectral["profile_d_prime"],
    }


def apply_repetition_qa_gate(verified: bool, out_path: str, canonical_text: str, language: str = "en",
                              enabled: bool = False) -> dict:
    """既存`er008_disfluency_qa_18.apply_disfluency_gate()`と同一のAND
    ゲートパターン。呼び出し側(各generate系関数のretry loop内)は、
    既存のverified変数をこの関数の戻り値で置き換えるだけでよい。
    enabled=Falseの場合は追加コスト・追加処理を一切発生させず元の
    verifiedをそのまま返す(対象外segmentへの影響ゼロを保証する)。
    verified=Falseの場合も評価しない(既に別Validatorで不合格が確定
    しているsegmentへ余計な計算をしない、dq18と同じ安全側の設計)。
    flag時は「TTS再生成→通常ASR+repetition QA再判定」という既存の
    retry loopにそのまま合流させる(新規retry回数・新規Cost Guardは
    追加しない)。"""
    if not enabled or not verified:
        return {"verified": verified, "repetition_qa_checked": False, "repetition_qa_evidence": None}
    evidence = evaluate_repetition_qa(out_path, canonical_text, language=language)
    return {
        "verified": verified and not evidence["flagged"],
        "repetition_qa_checked": True,
        "repetition_qa_evidence": evidence,
    }
