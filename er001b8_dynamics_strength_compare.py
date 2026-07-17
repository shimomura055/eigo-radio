# ============================================================
# er001b8_dynamics_strength_compare.py
# ER-001B-8: ダイナミクス制御3段階比較(音声後処理のみ。TTS再生成なし)
# ============================================================
# 目的: er001b6_hanshin_aoede_level2_full.wav(阪神Level 2全文・原音)
# に対し、ER-001B-7Aの軽いソフトニー・コンプレッサーを基準(Dynamics 1)
# とし、しきい値とレシオを段階的に強めたDynamics 2・3を比較する。
# 3条件はすべて同一の原音から個別に生成し(重ね掛けしない)、
# 単なる音量差の比較にならないよう、コンプレッション後に原音のラウドネス
# へ固定ゲインで整合させる(ピーク上限-1.0dBFSを優先)。
#
# サービス仕様やTTSの変更ではなく、音声後処理方法の比較実験。
# 原音・ER-001B-7Aの出力ファイルは一切上書きしない。
#
# 依存関係:
#   Python 3.14.6 / numpy 2.5.1 / scipy 1.18.0 (このリポジトリに
#   requirements.txt等の正式な依存管理ファイルは存在しないため、
#   実験用として.venvへ以下でインストール済み:
#     .venv/Scripts/python.exe -m pip install numpy scipy
#   起動時に両ライブラリの有無とバージョンを確認し、無ければ
#   分かりやすいエラーで停止する)
#
# 使い方:
#   python er001b8_dynamics_strength_compare.py

import sys

try:
    import numpy as np
except ImportError:
    raise SystemExit(
        "エラー: numpyが見つかりません。次のコマンドでインストールしてください:\n"
        "  .venv/Scripts/python.exe -m pip install numpy scipy"
    )
try:
    import scipy
    from scipy.signal import lfilter
except ImportError:
    raise SystemExit(
        "エラー: scipyが見つかりません。次のコマンドでインストールしてください:\n"
        "  .venv/Scripts/python.exe -m pip install numpy scipy"
    )

import wave
import json
import hashlib
import platform
from datetime import datetime

INPUT_WAV = "er001b6_hanshin_aoede_level2_full.wav"
PROTECTED_FILES = [
    "er001b6_hanshin_aoede_level2_full.wav",
    "er001b7a_hanshin_level2_light_dynamics.wav",
]
MANIFEST_PATH = "er001b8_manifest.json"

# ============================================================
# ブロック1: WAV読み込み・書き出し・ハッシュ
# ============================================================
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def read_wav(path):
    with wave.open(path, "rb") as w:
        channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
        raw = w.readframes(nframes)
    assert sampwidth == 2, f"16bit PCM以外は未対応です(sampwidth={sampwidth})"
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels)
    return samples, framerate, channels, nframes

def write_wav(path, samples, framerate, channels):
    assert np.all(np.isfinite(samples)), "出力サンプルにNaN/Infが含まれています"
    peak = np.max(np.abs(samples))
    assert peak <= 1.0 + 1e-9, f"出力にクリッピングの恐れがあります(peak={peak})"
    clipped = np.clip(samples, -1.0, 1.0)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(pcm16.tobytes())

# ============================================================
# ブロック2: 客観指標(ER-001B-7Aと同じ近似K-weighting/LUFS実装を再利用)
# ============================================================
def design_rbj_highshelf(sr, f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2 * q)
    cos_w0 = np.cos(w0)
    sqrtA = np.sqrt(A)
    b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * sqrtA * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
    b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * sqrtA * alpha)
    a0 = (A + 1) - (A - 1) * cos_w0 + 2 * sqrtA * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
    a2 = (A + 1) - (A - 1) * cos_w0 - 2 * sqrtA * alpha
    return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0

def design_rbj_highpass(sr, f0, q):
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2 * q)
    cos_w0 = np.cos(w0)
    b0 = (1 + cos_w0) / 2
    b1 = -(1 + cos_w0)
    b2 = (1 + cos_w0) / 2
    a0 = 1 + alpha
    a1 = -2 * cos_w0
    a2 = 1 - alpha
    return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0

LUFS_METHOD_NOTE = (
    "ITU-R BS.1770のK-weightingを24kHz向けにRBJ Audio EQ Cookbookの式で再設計し、"
    "2段階ゲーティングで積分ラウドネスを近似計算したもの(ER-001B-7Aと同一実装)。"
    "公式のBS.1770準拠測定器とは完全には一致しない可能性がある近似値。"
)
LRA_METHOD_NOTE = (
    "3秒窓・1秒ホップの短時間ラウドネス分布のP95-P10による簡易近似。EBU R128のLRA完全準拠アルゴリズムではない。"
)

def k_weight(samples, sr):
    b1, a1 = design_rbj_highshelf(sr, 1681.9, 3.999844545, 0.7071752369554193)
    b2, a2 = design_rbj_highpass(sr, 38.13547087613982, 0.5003270373238773)
    y = lfilter(b1, a1, samples)
    y = lfilter(b2, a2, y)
    return y

def integrated_lufs_approx(samples, sr):
    y = k_weight(samples, sr)
    block = int(0.4 * sr)
    hop = int(0.1 * sr)
    if len(y) < block:
        return None
    z_list = [np.mean(y[s:s + block] ** 2) for s in range(0, len(y) - block + 1, hop)]
    z = np.array(z_list)
    z = z[z > 0]
    if len(z) == 0:
        return None
    loudness = -0.691 + 10 * np.log10(z)
    gated1 = z[loudness > -70]
    if len(gated1) == 0:
        return None
    ungated_loudness = -0.691 + 10 * np.log10(np.mean(gated1))
    rel_gate = ungated_loudness - 10
    loudness1 = -0.691 + 10 * np.log10(gated1)
    gated2 = gated1[loudness1 > rel_gate]
    if len(gated2) == 0:
        gated2 = gated1
    return float(-0.691 + 10 * np.log10(np.mean(gated2)))

def loudness_range_approx(samples, sr):
    y = k_weight(samples, sr)
    block = int(3.0 * sr)
    hop = int(1.0 * sr)
    if len(y) < block:
        return None
    vals = []
    for s in range(0, len(y) - block + 1, hop):
        z = np.mean(y[s:s + block] ** 2)
        if z > 0:
            vals.append(-0.691 + 10 * np.log10(z))
    if len(vals) < 2:
        return None
    vals = np.array(vals)
    gated = vals[vals > -70]
    if len(gated) < 2:
        gated = vals
    return float(np.percentile(gated, 95) - np.percentile(gated, 10))

def db(x):
    return 20 * np.log10(max(x, 1e-12))

def measure_metrics(mono, sr):
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    clip_count = int(np.sum(np.abs(mono) >= 0.999))
    lufs = integrated_lufs_approx(mono, sr)
    lra = loudness_range_approx(mono, sr)
    crest_factor_db = round(db(peak) - db(rms), 2) if rms > 0 else None
    return {
        "duration_seconds": round(len(mono) / sr, 3),
        "sample_count": int(len(mono)),
        "sample_rate": sr,
        "peak_dbfs": round(db(peak), 2),
        "rms_dbfs": round(db(rms), 2),
        "integrated_lufs_approx": round(lufs, 2) if lufs is not None else None,
        "loudness_range_approx_lu": round(lra, 2) if lra is not None else None,
        "crest_factor_db": crest_factor_db,
        "clipping_sample_count": clip_count,
        "clipping_detected": clip_count > 0,
    }

# ============================================================
# ブロック3: ソフトニー・コンプレッサー(ER-001B-7Aと同じ設計。符号バグ修正済み版)
# ============================================================
def soft_knee_gain_reduction_db(level_db, threshold_db, ratio, knee_db):
    gr = np.zeros_like(level_db)
    lower = threshold_db - knee_db / 2
    upper = threshold_db + knee_db / 2
    below = level_db <= lower
    above = level_db >= upper
    within = ~below & ~above
    # gr(dB) = 出力レベル - 入力レベル。ratio>1では常に負(減衰)。
    gr[above] = (level_db[above] - threshold_db) * (1 / ratio - 1)
    x = level_db[within] - lower
    gr[within] = ((1 / ratio - 1) * (x ** 2)) / (2 * knee_db)
    return gr

def envelope_follower_db(mono, sr, attack_ms, release_ms):
    abs_sig = np.abs(mono)
    attack_coef = np.exp(-1.0 / (sr * attack_ms / 1000.0))
    release_coef = np.exp(-1.0 / (sr * release_ms / 1000.0))
    env = np.zeros_like(abs_sig)
    prev = 0.0
    for i, x in enumerate(abs_sig):
        coef = attack_coef if x > prev else release_coef
        prev = coef * prev + (1 - coef) * x
        env[i] = prev
    return 20 * np.log10(np.maximum(env, 1e-9))

def apply_compressor(mono, sr, params):
    env_db = envelope_follower_db(mono, sr, params["attack_ms"], params["release_ms"])
    threshold_db = float(np.percentile(env_db, params["threshold_percentile"]))
    gr_db = soft_knee_gain_reduction_db(env_db, threshold_db, params["ratio"], params["knee_db"])

    smooth_coef = np.exp(-1.0 / (sr * params["gain_smoothing_ms"] / 1000.0))
    gr_db_smoothed = np.zeros_like(gr_db)
    prev = 0.0
    for i, g in enumerate(gr_db):
        prev = smooth_coef * prev + (1 - smooth_coef) * g
        gr_db_smoothed[i] = prev

    gain_linear = 10 ** (gr_db_smoothed / 20)
    processed = mono * gain_linear
    return processed, gr_db_smoothed, threshold_db

# ============================================================
# ブロック4: ポンピング等の参考診断
# ============================================================
def diagnose_gain_reduction(gr_db_series, sr):
    step = max(1, int(sr / 100))
    ds = gr_db_series[::step]  # 100Hzへ間引き
    dc_removed = ds - np.mean(ds)

    # 自己相関ベースの周期性(0.1〜2.0秒周期帯)
    if np.allclose(dc_removed, 0) or len(dc_removed) < 20:
        autocorr_info = {"pumping_suspected": False, "max_autocorr": 0.0,
                          "note": "ゲイン変化がほぼ無いため判定対象外"}
    else:
        autocorr = np.correlate(dc_removed, dc_removed, mode="full")
        autocorr = autocorr[len(autocorr) // 2:]
        autocorr = autocorr / (autocorr[0] + 1e-12)
        min_lag, max_lag = 10, min(200, len(autocorr) - 1)
        if min_lag >= max_lag:
            autocorr_info = {"pumping_suspected": False, "max_autocorr": 0.0, "note": "音声が短すぎて判定対象外"}
        else:
            window = autocorr[min_lag:max_lag]
            peak_idx = int(np.argmax(window)) + min_lag
            peak_val = float(window[peak_idx - min_lag])
            autocorr_info = {
                "pumping_suspected": bool(peak_val > 0.5),
                "max_autocorr": round(peak_val, 3),
                "period_seconds_at_peak": round(peak_idx / 100.0, 2),
                "threshold_used": 0.5,
            }

    # 急激なゲイン回復の回数(-3dB以下から-0.5dB超まで、50ms以内に回復した回数)
    window_samples = max(1, int(0.05 * 100))  # 100Hz換算で50ms
    recover_events = 0
    i = 0
    n = len(ds)
    while i < n - window_samples:
        if ds[i] < -3.0:
            future = ds[i:i + window_samples]
            if np.any(future > -0.5):
                recover_events += 1
                i += window_samples
                continue
        i += 1

    # 長い減衰継続時間(gr < -1dBが連続する最長区間、秒)
    below = ds < -1.0
    max_run = 0
    cur_run = 0
    for b in below:
        if b:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 0
    max_sustained_reduction_seconds = round(max_run / 100.0, 2)

    return {
        **autocorr_info,
        "rapid_gain_recovery_event_count": recover_events,
        "max_sustained_reduction_seconds": max_sustained_reduction_seconds,
        "note_full": (
            "自己相関(0.1〜2.0秒周期帯)・急激なゲイン回復回数(50ms以内に-3dB以下→-0.5dB超)・"
            "最長の減衰継続時間(-1dB以下が連続する秒数)を参考として記録。機械検出だけでは"
            "ポンピング/平坦さ/押し込まれ感の不存在を保証しない(タスク仕様どおり)。"
        ),
    }

# ============================================================
# ブロック5: ラウドネス整合(固定ゲインのみ。ピーク上限-1.0dBFSを優先)
# ============================================================
PEAK_CEILING_DB = -1.0

def match_loudness(processed, target_lufs, sr):
    compressed_lufs = integrated_lufs_approx(processed, sr)
    current_peak = float(np.max(np.abs(processed)))
    current_peak_db = db(current_peak)

    if target_lufs is None or compressed_lufs is None:
        desired_gain_db = 0.0
    else:
        desired_gain_db = target_lufs - compressed_lufs

    max_gain_allowed_by_peak_db = PEAK_CEILING_DB - current_peak_db
    final_gain_db = min(desired_gain_db, max_gain_allowed_by_peak_db)
    # 万一desired_gain_dbが負(圧縮後の方が原音より大きい)でも、その負のゲインはそのまま適用してよい
    # (音量整合の趣旨に反しないため)。ただしピーク上限は常に優先する。

    gained = processed * (10 ** (final_gain_db / 20))
    final_peak = float(np.max(np.abs(gained)))
    final_lufs = integrated_lufs_approx(gained, sr)

    shortfall_lu = None
    if target_lufs is not None and final_lufs is not None:
        shortfall_lu = round(target_lufs - final_lufs, 3)

    return gained, {
        "target_lufs": round(target_lufs, 2) if target_lufs is not None else None,
        "compressed_lufs_before_gain": round(compressed_lufs, 2) if compressed_lufs is not None else None,
        "desired_gain_db": round(desired_gain_db, 3),
        "peak_ceiling_db": PEAK_CEILING_DB,
        "max_gain_allowed_by_peak_db": round(max_gain_allowed_by_peak_db, 3),
        "applied_fixed_gain_db": round(final_gain_db, 3),
        "peak_ceiling_prioritized": bool(final_gain_db < desired_gain_db - 1e-9),
        "final_peak_dbfs": round(db(final_peak), 2),
        "final_lufs_approx": round(final_lufs, 2) if final_lufs is not None else None,
        "loudness_shortfall_lu": shortfall_lu,
        "within_0_3_lu_target": (abs(shortfall_lu) <= 0.3) if shortfall_lu is not None else None,
    }

# ============================================================
# ブロック6: 3段階のパラメータ定義
# ============================================================
# Dynamics 1はER-001B-7Aの修正済みパラメータをそのまま基準にする。
# Dynamics 2・3は、しきい値パーセンタイルを下げ、レシオを上げることで段階的に強度を上げる
# (6節の指示どおり「しきい値を下げる」「レシオを上げる」の組み合わせ)。
DYNAMICS_PARAMS = {
    "dynamics1": {
        "label": "Dynamics 1 (ER-001B-7A相当の軽い処理)",
        "type": "soft_knee_compressor",
        "threshold_percentile": 90,
        "ratio": 2.5,
        "knee_db": 6.0,
        "attack_ms": 5.0,
        "release_ms": 200.0,
        "gain_smoothing_ms": 8.0,
    },
    "dynamics2": {
        "label": "Dynamics 2 (Dynamics 1より明確に強い処理)",
        "type": "soft_knee_compressor",
        "threshold_percentile": 75,
        "ratio": 4.0,
        "knee_db": 6.0,
        "attack_ms": 5.0,
        "release_ms": 200.0,
        "gain_smoothing_ms": 8.0,
    },
    "dynamics3": {
        "label": "Dynamics 3 (平坦化の境界を確認するストレステスト)",
        "type": "soft_knee_compressor",
        "threshold_percentile": 60,
        "ratio": 8.0,
        "knee_db": 6.0,
        "attack_ms": 5.0,
        "release_ms": 200.0,
        "gain_smoothing_ms": 8.0,
    },
}

OUTPUT_FILES = {
    "dynamics1": "er001b8_hanshin_level2_dynamics1.wav",
    "dynamics2": "er001b8_hanshin_level2_dynamics2.wav",
    "dynamics3": "er001b8_hanshin_level2_dynamics3.wav",
}

# ============================================================
# ブロック7: 実行
# ============================================================
print("ER-001B-8: ダイナミクス制御3段階比較(音声後処理のみ、TTS再生成なし)")
print(f"Python: {platform.python_version()} / numpy: {np.__version__} / scipy: {scipy.__version__}")
print(f"入力(原音・上書きしない): {INPUT_WAV}")
print()

input_sha256_before = sha256_file(INPUT_WAV)
protected_hashes_before = {p: sha256_file(p) for p in PROTECTED_FILES}

samples, sr, channels, nframes = read_wav(INPUT_WAV)
mono_original = samples if channels == 1 else samples.mean(axis=1)

print("原音の指標を計測中...", flush=True)
original_metrics = measure_metrics(mono_original, sr)
print(json.dumps(original_metrics, ensure_ascii=False, indent=2))
print()

target_lufs = original_metrics["integrated_lufs_approx"]

manifest = {
    "experiment_id": "ER-001B-8",
    "purpose": "音声後処理方法の比較実験(サービス仕様・TTSの変更ではない)",
    "input_file": INPUT_WAV,
    "input_file_sha256": input_sha256_before,
    "tts_regenerated": False,
    "protected_files_not_overwritten": PROTECTED_FILES,
    "chained_processing": False,
    "environment": {
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "install_command": ".venv/Scripts/python.exe -m pip install numpy scipy",
        "dependency_management_note": (
            "本リポジトリにrequirements.txt等の正式な依存関係管理ファイルは存在しないため、"
            "今回の実験用として.venvへ直接インストールした。恒久的な依存関係ファイルの新設は行っていない。"
        ),
    },
    "original_metrics": original_metrics,
    "peak_ceiling_db": PEAK_CEILING_DB,
    "loudness_match_target_lu": 0.3,
    "lufs_method_note": LUFS_METHOD_NOTE,
    "loudness_range_method_note": LRA_METHOD_NOTE,
    "conditions": {},
}

strength_summary = {}

for key in ("dynamics1", "dynamics2", "dynamics3"):
    params = DYNAMICS_PARAMS[key]
    out_wav = OUTPUT_FILES[key]
    print(f"=== {params['label']} を生成中(原音から個別に処理。重ね掛けなし) ===", flush=True)
    print(f"  パラメータ: {json.dumps({k: v for k, v in params.items() if k not in ('label',)}, ensure_ascii=False)}")

    # 必ず「原音」から処理する(前段のDynamics出力を入力にしない)
    processed, gr_db_series, threshold_db_used = apply_compressor(mono_original, sr, params)

    # ---- 安全チェック(12節): 増幅していないか・NaN/Infがないか ----
    assert np.all(gr_db_series <= 1e-6), f"{key}: ゲインリダクションが正(増幅)になっています(想定外)"
    assert np.all(np.isfinite(processed)), f"{key}: 処理直後の信号にNaN/Infが含まれています"
    assert np.all(np.abs(processed) <= np.abs(mono_original) + 1e-9), (
        f"{key}: 処理直後のサンプル絶対値が原音を上回っています(想定外の増幅)"
    )
    print(f"  安全チェック: 減衰のみ・NaN/Infなし・原音超えの増幅なし を確認", flush=True)

    compressed_metrics = measure_metrics(processed, sr)

    # ---- ラウドネス整合(固定ゲインのみ。ピーク上限優先) ----
    matched, loudness_info = match_loudness(processed, target_lufs, sr)

    # ---- クリッピング最終確認 ----
    assert not np.any(np.abs(matched) >= 1.0), f"{key}: ラウドネス整合後にクリッピングの恐れがあります"

    write_wav(out_wav, matched, sr, channels)
    final_metrics = measure_metrics(matched, sr)
    print(f"  -> {out_wav} を保存しました "
          f"(final peak={final_metrics['peak_dbfs']}dBFS, LUFS約{final_metrics['integrated_lufs_approx']}, "
          f"クリッピング={final_metrics['clipping_detected']})", flush=True)

    # ---- ゲインリダクション統計 ----
    max_gr_db = round(float(np.min(gr_db_series)), 2)  # 最も負(最大減衰)
    mean_gr_db = round(float(np.mean(gr_db_series)), 3)
    top10_gr_db = round(float(np.percentile(gr_db_series, 1)), 2)  # 下位1パーセンタイル=最も強く減衰した領域の代表値

    pumping_info = diagnose_gain_reduction(gr_db_series, sr)

    strength_summary[key] = {
        "max_gain_reduction_db": max_gr_db,
        "mean_gain_reduction_db": mean_gr_db,
        "loudness_range_approx_lu": compressed_metrics["loudness_range_approx_lu"],
        "crest_factor_db": compressed_metrics["crest_factor_db"],
    }

    output_sha256 = sha256_file(out_wav)

    manifest["conditions"][key] = {
        "condition_name": params["label"],
        "input_file": INPUT_WAV,
        "input_file_sha256": input_sha256_before,
        "output_file": out_wav,
        "output_file_sha256": output_sha256,
        "compressor": {
            "method": "軽いソフトニー・コンプレッサー(ピーク検出エンベロープ、非対称アタック/リリース、"
                       "しきい値=エンベロープ分布のパーセンタイル、メイクアップゲインなし)",
            "threshold_percentile": params["threshold_percentile"],
            "threshold_db_used_this_file": round(threshold_db_used, 2),
            "ratio": params["ratio"],
            "knee_db": params["knee_db"],
            "attack_ms": params["attack_ms"],
            "release_ms": params["release_ms"],
            "gain_smoothing_ms": params["gain_smoothing_ms"],
            "makeup_gain_before_loudness_match_db": 0.0,
        },
        "loudness_matching": loudness_info,
        "gain_reduction_stats": {
            "max_gain_reduction_db": max_gr_db,
            "mean_gain_reduction_db": mean_gr_db,
            "p1_gain_reduction_db_most_compressed_region": top10_gr_db,
        },
        "metrics_after_compression_before_loudness_match": compressed_metrics,
        "metrics_final": final_metrics,
        "duration_matches_original": final_metrics["duration_seconds"] == original_metrics["duration_seconds"],
        "sample_count_matches_original": final_metrics["sample_count"] == original_metrics["sample_count"],
        "pumping_diagnostics": pumping_info,
        "generated_at": datetime.now().isoformat(),
    }
    print()

# ============================================================
# ブロック8: 強度の単調性確認(Dynamics1 < Dynamics2 < Dynamics3)
# ============================================================
print("=== 強度の単調性確認 ===", flush=True)
monotonic_checks = {}

max_gr = [strength_summary[k]["max_gain_reduction_db"] for k in ("dynamics1", "dynamics2", "dynamics3")]
mean_gr = [strength_summary[k]["mean_gain_reduction_db"] for k in ("dynamics1", "dynamics2", "dynamics3")]
lra = [strength_summary[k]["loudness_range_approx_lu"] for k in ("dynamics1", "dynamics2", "dynamics3")]
crest = [strength_summary[k]["crest_factor_db"] for k in ("dynamics1", "dynamics2", "dynamics3")]

# 「強度が増える」= 減衰量の絶対値が増える(dB値としてはより負に、つまり単調減少)
monotonic_checks["max_gain_reduction_db_monotonic_increasing_strength"] = bool(
    max_gr[0] > max_gr[1] > max_gr[2]
)
monotonic_checks["mean_gain_reduction_db_monotonic_increasing_strength"] = bool(
    mean_gr[0] > mean_gr[1] > mean_gr[2]
)
# LRA・クレストファクターは強い圧縮ほど小さくなる想定(単調減少)
monotonic_checks["loudness_range_monotonic_decreasing"] = bool(
    lra[0] is not None and lra[1] is not None and lra[2] is not None and lra[0] > lra[1] > lra[2]
)
monotonic_checks["crest_factor_monotonic_decreasing"] = bool(
    crest[0] is not None and crest[1] is not None and crest[2] is not None and crest[0] > crest[1] > crest[2]
)

any_monotonic = any(monotonic_checks.values())
print(json.dumps({
    "max_gain_reduction_db": max_gr,
    "mean_gain_reduction_db": mean_gr,
    "loudness_range_approx_lu": lra,
    "crest_factor_db": crest,
    "monotonic_checks": monotonic_checks,
    "at_least_one_metric_monotonic": any_monotonic,
}, ensure_ascii=False, indent=2))

manifest["monotonicity_check"] = {
    "max_gain_reduction_db_by_condition": dict(zip(("dynamics1", "dynamics2", "dynamics3"), max_gr)),
    "mean_gain_reduction_db_by_condition": dict(zip(("dynamics1", "dynamics2", "dynamics3"), mean_gr)),
    "loudness_range_approx_lu_by_condition": dict(zip(("dynamics1", "dynamics2", "dynamics3"), lra)),
    "crest_factor_db_by_condition": dict(zip(("dynamics1", "dynamics2", "dynamics3"), crest)),
    "checks": monotonic_checks,
    "at_least_one_metric_shows_monotonic_strength_increase": any_monotonic,
}

if not any_monotonic:
    print("[警告] いずれの客観指標でもDynamics1<2<3の単調な強度増加が確認できませんでした。"
          "パラメータの見直しが必要な可能性があります。", flush=True)

# ============================================================
# ブロック9: 保護対象ファイルが変更されていないことの最終確認
# ============================================================
protected_hashes_after = {p: sha256_file(p) for p in PROTECTED_FILES}
protected_unchanged = protected_hashes_before == protected_hashes_after
assert protected_unchanged, "保護対象ファイル(原音またはER-001B-7A出力)が変更されています"
manifest["protected_files_verified_unchanged"] = protected_unchanged
manifest["protected_files_sha256"] = protected_hashes_after

manifest["generated_at"] = datetime.now().isoformat()

with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print()
print("-" * 50)
print(f"{MANIFEST_PATH} を保存しました。")
print(f"原音・ER-001B-7A出力が変更されていないことを確認: {protected_unchanged}")
