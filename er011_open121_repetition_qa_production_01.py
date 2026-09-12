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

import difflib
import re

import numpy as np
import soundfile as sf

import er006_preprod_hardening_01_validation as en_validator
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

# OPEN-128-METHOD-D-LOCAL-ASR-CONFIRM-PRODUCTION-WIRING-01: ユーザー承認
# 2026-09-08(候補c、OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01_
# REPORT.md §5/§14でVALIDATED)。方式Dのacoustic flag(閾値は上記
# METHOD_D_DECISION_RUN_SECONDS=0.12秒、無変更)後段の局所ASR語句一致度
# 確認用パラメータ(23件データセットでTP8/8・FP0/15、マージン厚い方の
# 構成)。acoustic threshold自体は一切変更しない。
METHOD_D_ASR_CONFIRM_OVERLAP_RATIO_THRESHOLD = 0.5
METHOD_D_ASR_CONFIRM_LCS_WORDS_THRESHOLD = 3
METHOD_D_ASR_CONFIRM_WINDOW_HALF_SECONDS = 1.5
METHOD_D_ASR_CONFIRM_MAX_HALF_WINDOW_SECONDS = 4.0


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


def confirm_by_local_asr_overlap(words, time_a, time_b,
                                  window_half_seconds=METHOD_D_ASR_CONFIRM_WINDOW_HALF_SECONDS,
                                  max_half_window_seconds=METHOD_D_ASR_CONFIRM_MAX_HALF_WINDOW_SECONDS,
                                  overlap_ratio_threshold=METHOD_D_ASR_CONFIRM_OVERLAP_RATIO_THRESHOLD,
                                  lcs_words_threshold=METHOD_D_ASR_CONFIRM_LCS_WORDS_THRESHOLD):
    """OPEN-128候補(c、OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01
    と無変更のロジック)。方式Dがacoustic flagした2箇所(time_a/time_b、
    上位match)の前後の局所ASR word-level tokenを切り出し、語句一致度
    (difflib SequenceMatcher比率+最長連続一致語数)で確認する。
    overlap_ratio>=閾値 OR lcs_words>=閾値で「語句重複が実在する」と判定
    する(acoustic類似のみで語句が異なる誤flagを除外)。時間窓は空なら
    +1.0秒刻み(2.5秒まで)、その後+1.5秒刻みで最大max_half_window_seconds
    まで拡張する(Trial-01 flag15_review_02と同一手順)。wordsは
    `er008_disfluency_qa_18.transcribe_verbatim()`のword-level timestamp
    (方式Aと共有、追加ASR呼び出しなし)。"""
    def extract_window_tokens(center_s, half_window, max_half):
        hw = half_window
        while hw <= max_half:
            toks = [w for w in words if center_s - hw <= (w["start"] + w["end"]) / 2 <= center_s + hw]
            if toks:
                return toks, hw
            hw += 1.0 if hw < 2.5 else 1.5
        return [], hw

    def longest_common_contig_run(a, b):
        best = 0
        for i in range(len(a)):
            for j in range(len(b)):
                k = 0
                while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                    k += 1
                best = max(best, k)
        return best

    toks_a_raw, hw_a = extract_window_tokens(time_a, window_half_seconds, max_half_window_seconds)
    toks_b_raw, hw_b = extract_window_tokens(time_b, window_half_seconds, max_half_window_seconds)
    toks_a = [dq18._normalize_token(w["text"]) for w in toks_a_raw]
    toks_b = [dq18._normalize_token(w["text"]) for w in toks_b_raw]
    overlap_ratio = difflib.SequenceMatcher(None, toks_a, toks_b).ratio() if (toks_a and toks_b) else 0.0
    lcs_words = longest_common_contig_run(toks_a, toks_b) if (toks_a and toks_b) else 0
    confirmed = bool(toks_a and toks_b
                      and (overlap_ratio >= overlap_ratio_threshold or lcs_words >= lcs_words_threshold))
    return {
        "confirmed": confirmed, "overlap_ratio": round(overlap_ratio, 4), "lcs_words": lcs_words,
        "window_half_seconds_a": hw_a, "window_half_seconds_b": hw_b,
        "fragment_a": " ".join(w["text"].strip() for w in toks_a_raw),
        "fragment_b": " ".join(w["text"].strip() for w in toks_b_raw),
        "overlap_ratio_threshold": overlap_ratio_threshold, "lcs_words_threshold": lcs_words_threshold,
    }


def analyze_profile_d_long_lag(bundle, min_lag_s=METHOD_D_MIN_LAG_SECONDS, top_k=METHOD_D_TOP_K,
                                sim_threshold=METHOD_D_SIM_THRESHOLD, words=None):
    """方式D(Trial-01、acoustic部分は既存・無変更)。lag>=min_lag_sの候補
    ペアを類似度降順で最大top_k件選び(粗い重複除去つき)、上位3件それぞれ
    について類似度>=sim_thresholdが連続する長さ(run長)を測る。最大run長が
    METHOD_D_DECISION_RUN_SECONDS以上ならacoustic_flagged=True。

    OPEN-128: words(方式Aと共有するword-level ASR結果)が渡された場合、
    acoustic_flagged=Trueのときのみ、最大run長を出したmatchのtime_a/time_b
    に対し`confirm_by_local_asr_overlap()`で局所語句一致度を確認し、
    確認できた場合のみ最終flagged=Trueとする(2段判定、Trial-01候補c)。
    words=None(既定、後方互換)の場合はacoustic判定のみを最終flaggedと
    する(既存呼び出し元・既存テストの挙動を変更しない)。acoustic
    threshold(sim_threshold・METHOD_D_DECISION_RUN_SECONDS)自体は
    一切変更しない。"""
    sim = bundle["sim"]
    hop_ms = bundle["hop_ms"]
    if sim is None:
        return {"top_matches": [], "best_run_length_seconds": 0.0, "min_lag_seconds": min_lag_s,
                "sim_threshold": sim_threshold, "decision_threshold_seconds": METHOD_D_DECISION_RUN_SECONDS,
                "acoustic_flagged": False, "local_asr_confirmation": None, "flagged": False}
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
    acoustic_flagged = best_run >= METHOD_D_DECISION_RUN_SECONDS
    result = {"top_matches": top, "best_run_length_seconds": best_run, "min_lag_seconds": min_lag_s,
              "sim_threshold": sim_threshold, "decision_threshold_seconds": METHOD_D_DECISION_RUN_SECONDS,
              "acoustic_flagged": acoustic_flagged}

    if not acoustic_flagged or words is None:
        result["local_asr_confirmation"] = None
        result["flagged"] = acoustic_flagged
        return result

    # 局所ASR確認はtop[0](類似度最上位のmatch)のtime_a/time_bに対して
    # 実行する。OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01
    # (er011_open121_method_d_flag23_review_01.py 221行、`best = top[0]`)・
    # OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01の候補c実装
    # (`row.get("flag_time_a"/"flag_time_b")`、いずれもtop[0]由来)と
    # 同一の対象点を使う(TP8/8・FP0/15の検証はtop[0]に対してのみ行われて
    # おり、run長最大entryを使うのは未検証のロジック変更になるため
    # 採用しない)。
    top0 = top[0]
    confirmation = confirm_by_local_asr_overlap(
        words, top0["time_a_seconds"], top0["time_b_seconds"])
    result["local_asr_confirmation"] = confirmation
    result["flagged"] = acoustic_flagged and confirmation["confirmed"]
    return result


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


def run_spectral_checks(path, words=None):
    """方式D・D'を統合スペクトル計算1回で実行する(Trial-02 §4/§7-5)。
    flag/非flagにかかわらず、境界値monitoring用に両プロファイルの
    最大run長・lag・similarityを常に返す。

    OPEN-128: words(方式Aと共有するword-level ASR結果)が渡された場合、
    方式D(analyze_profile_d_long_lag)へそのまま渡し、acoustic flag後の
    局所ASR確認2段判定を有効化する。方式D'は本Trial・ユーザー承認の
    対象外のため無変更(常にacoustic判定のみ)。"""
    bundle = compute_shared_self_similarity(path)
    profile_d = analyze_profile_d_long_lag(bundle, words=words)
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
#
# OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01:
# ユーザー承認2026-09-12(REPETITION-QA-INTENTIONAL-REPEAT-FALSE-
# POSITIVE-RECONCILE-02_REPORT.md)。Production呼び出し経路では
# canonical_textが`tts_safe_number_words_en()`(er003_v1_n3_01_tts_
# generate.py)により綴り小数(two~twelve)を算用数字へ変換済みの状態で
# 渡される一方、Repetition QA専用のローカルASR(faster-whisper、
# dq18.transcribe_verbatim())は発話された小さな数を綴りのまま書き
# 起こすため、`_canonical_repeat_count()`の完全一致比較が"two"対"2"で
# 常に失敗し、canonicalへ正規に2回登場する語句(例: "after two
# months"が台本に2箇所)が意図的反復と判定されず誤flagされていた
# (タオルTrial-11 B1B full_story_part2、pool_n4_supermarket A2/B1B
# で実データ確認済み、根本原因はEM dash対策[OPEN-127]・%/percent
# 不一致[未修正・別管理]のいずれとも別原因)。
# `_NUM_WORD_TO_DIGIT_EN`は`tts_safe_number_words_en()`の変換対象
# `_EN_NUMBER_WORDS`(er003_v1_n3_01_tts_generate.py)と**完全に同じ
# 語彙(two~twelve)**を複製したもの(モジュール直接import不可: er003_
# v1_n3_01_tts_generate -> er003_v1_sing01_news_tail_fix -> 本モジュール
# という既存の循環importが既に存在するため、逆方向importを追加すると
# 循環参照になる。字面の重複は許容し、範囲がずれないようキー集合を
# `_EN_NUMBER_WORDS`と同一に保つ)。"one"は代名詞としての曖昧性回避の
# ため対象外(既存tts_safe_number_words_en()の方針を踏襲)。"%"/
# "percent"の同値化は対象外(範囲拡張は別途ユーザー判断待ち)。
# canonical側・ASR側のトークンの両方にこの正規化を一様に適用すること
# で、`_canonical_repeat_count()`への入力の表記ゆれのみを吸収し、
# 閾値(canon_count>=2)・判定意味は一切変更しない。
#
# OPEN-121-REPETITION-QA-SYMMETRIC-NORMALIZATION-PRODUCTION-WIRING-01:
# ユーザー承認2026-09-12(REPETITION-QA-INTENTIONAL-REPEAT-FALSE-
# POSITIVE-RECONCILE-03_REPORT.md「修正1回目」節)。上記(2~12専用辞書)は
# Trial-12実データ("twenty-four-hour day"が"24"+"-hour"の2 tokenへASR側で
# 分割される一方、canonical側tokenizerは空白のみで分割するためハイフン
# 複合語"twenty-four-hour"が1 tokenのまま残ってしまう非対称)には
# 構造的に無関係であり、数値レンジ拡張だけでは解消しなかった。以下の
# 2点を組み合わせた対称正規化層へ置き換える(判定閾値canon_count>=2・
# 判定意味は無変更):
#   (i) ハイフン境界の対称正規化: em dash(—)・en dash(–)は既存OPEN-127の
#       em dash処理と同じく前後の空白有無を問わず常に空白へ(en dashへ
#       拡張)。ハイフン(-)は英字/数字が隣接する境界のみ空白へ
#       (digit-digit境界[例: "10-15"という範囲表記]は無関係な数字対の
#       誤結合riskを避けるため明示的に除外)。canonical側・ASR側の
#       両方に同一正規化を適用する(対称性が本質)。
#   (ii) 数詞↔算用数字の同値化を0〜999へ拡張: 専用辞書(2~12)を廃止し、
#       Production既承認・稼働中のASR Validator側の実装(`er006_
#       preprod_hardening_01_validation.py`の`_ONES`/`_TENS`/
#       `_NUM_WORD_VOCAB`/`_words_to_number`)をそのまま再利用する
#       (重複実装によるバグ・語彙drift混入を避けるため。逆方向import
#       ではないため循環importなし、実地確認済み)。canonical側は複数
#       tokenの数詞列を1つの算用数字tokenへ畳み込む(例: "twenty four"→
#       "24"、"one hundred twenty"→"120")。ASR側はタイムスタンプ保持の
#       ため複数token統合はせず、単一token単位の数詞→算用数字変換のみ
#       (0〜99、"one"は代名詞曖昧性のため既存方針通り除外)。
#   %/percentの同値化・序数(first〜ninety-ninth)は引き続き対象外
#   (実例なし、範囲拡張は別途ユーザー判断待ち、RECONCILE-03参照)。
_EM_EN_DASH_RE = re.compile(r"[–—]")
_HYPHEN_BOUNDARY_RE = re.compile(
    r"(?<=[A-Za-z])-(?=[A-Za-z])"
    r"|(?<=[A-Za-z])-(?=[0-9])"
    r"|(?<=[0-9])-(?=[A-Za-z])"
)

_ONES = en_validator._ONES
_TENS = en_validator._TENS
_NUM_WORD_VOCAB = en_validator._NUM_WORD_VOCAB
_words_to_number = en_validator._words_to_number


def _dash_unify(text):
    """em/en dashは常に空白へ(既存OPEN-127のem dash処理をen dashへも
    拡張)。ハイフンは英字/数字が隣接する境界のみ空白へ(digit-digit境界
    [範囲表記]は除外)。"""
    text = _EM_EN_DASH_RE.sub(" ", text)
    text = _HYPHEN_BOUNDARY_RE.sub(" ", text)
    return text


def _fold_cardinal_words(tokens):
    """canonical側: 空白区切り済みの生token列(大文字小文字混在・句読点
    付着あり)に対し、連続する数詞語の最大munchを`_words_to_number()`で
    算用数字1 tokenへ畳み込む(既存`en_validator._convert_cardinal_
    words()`と同一アルゴリズムをtoken列に対して直接適用)。句読点は
    ここでは未除去(呼び出し側で個々のtokenへ`dq18._normalize_token`を
    後段適用する前提)。"""
    lower = [t.lower() for t in tokens]
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        bare = re.sub(r"[^a-z]", "", lower[i])
        if bare and bare in _NUM_WORD_VOCAB:
            j = i
            seq = []
            while j < n:
                b = re.sub(r"[^a-z]", "", lower[j])
                if b and b in _NUM_WORD_VOCAB:
                    seq.append(b)
                    j += 1
                else:
                    break
            if len(seq) == 1 and seq[0] == "one":
                out.append(tokens[i])
                i += 1
                continue
            val = _words_to_number(seq)
            if val is None or (len(seq) == 1 and val < 2):
                out.append(tokens[i])
                i += 1
                continue
            out.append(str(val))
            i = j
        else:
            out.append(tokens[i])
            i += 1
    return out


def _normalize_token_numeric_equiv(word):
    """ASR側: 単一token単位の正規化(タイムスタンプ保持のため複数token
    統合はしない)。(a)先頭ハイフン/en-dash/em-dash artifactの除去
    (faster-whisperがハイフン複合語を"word"+"-suffix"の2 tokenへ分割する
    tokenize artifact対策) (b)既存`dq18._normalize_token()`(句読点除去+
    小文字化) (c)単一token数詞→算用数字(0〜99、"one"は代名詞曖昧性の
    ため対象外、既存方針を踏襲)。"""
    w = word
    if len(w) > 1 and w[0] in "-–—" and (w[1].isalpha() or w[1].isdigit()):
        w = w[1:]
    t = dq18._normalize_token(w)
    if t == "one":
        return t
    if t in _ONES:
        return str(_ONES[t])
    if t in _TENS:
        return str(_TENS[t])
    return t


def _normalize_tokens(text):
    """canonical側: (i)ダッシュ境界統一→分割→(ii)数詞畳み込み→
    既存`dq18._normalize_token`(句読点除去+小文字化)。"""
    text = _dash_unify(text)
    raw_tokens = text.split()
    folded = _fold_cardinal_words(raw_tokens)
    return [dq18._normalize_token(t) for t in folded]


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
    # OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01:
    # ASR側token(綴り小数のまま書き起こされる)にも、canonical側
    # `_normalize_tokens()`と同じ`_normalize_token_numeric_equiv()`を
    # 適用し、比較前の表記を揃える(判定ロジック自体は無変更)。
    tokens = [_normalize_token_numeric_equiv(w["text"]) for w in words]
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
    できる形)。

    OPEN-128: `dq18.transcribe_verbatim()`をここで1回だけ呼び、方式A
    (`detect_ngram_repetition`)と方式Dの局所ASR確認
    (`run_spectral_checks`経由で`analyze_profile_d_long_lag`へ共有)の
    両方へ同じword-level ASR結果を渡す(同一音声への二重ASR実行を回避)。
    ASR取得に失敗した場合(`transcribe_verbatim`が例外を送出する場合)は
    従来通り例外がそのまま呼び出し元へ伝播する(方式A単独運用時と同じ
    挙動、新規のfail-open/fail-closed設計は追加していない)。"""
    words = dq18.transcribe_verbatim(path, language=language, model_size="small")
    ngram = detect_ngram_repetition(words, canonical_text=canonical_text, min_words=METHOD_A_MIN_WORDS)
    spectral = run_spectral_checks(path, words=words)
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
