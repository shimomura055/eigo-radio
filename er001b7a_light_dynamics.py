# ============================================================
# er001b7a_light_dynamics.py
# ER-001B-7A: 軽い音量制御(既存音声への後処理のみ。TTS再生成なし)
# ============================================================
# 目的: er001b6_hanshin_aoede_level2_full.wav(阪神Level 2全文)に対し、
# 抑揚・強調・テンポを維持したまま、冒頭や見出し出だしの瞬間的な
# 音量の飛び出しだけを軽く抑える。TTSは一切呼び出さない、
# 完成WAVに対する音声後処理のみの独立スクリプト。
#
# 処理方式: 軽いソフトニー・コンプレッサー(ピーク検出・非対称
# アタック/リリース、低レシオ、メイクアップゲインなし)。
# しきい値は各音声のエンベロープ分布の90パーセンタイルを基準に
# 自動設定する(絶対dB値を決め打ちしない、再現可能な設計)。
#
# 依存ライブラリ: numpy, scipy(このスクリプトのために.venvへ新規
# インストール。requirements.txt等の依存管理ファイルは本リポジトリに
# 存在しないため追加していない)。
#
# 使い方:
#   python er001b7a_light_dynamics.py

import wave
import json
import numpy as np
from scipy.signal import lfilter
from datetime import datetime

INPUT_WAV = "er001b6_hanshin_aoede_level2_full.wav"
OUTPUT_WAV = "er001b7a_hanshin_level2_light_dynamics.wav"
MANIFEST_PATH = "er001b7a_manifest.json"

# ============================================================
# ブロック1: WAV読み込み・書き出し
# ============================================================
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
    return samples, framerate, channels

def write_wav(path, samples, framerate, channels):
    clipped = np.clip(samples, -1.0, 1.0)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(pcm16.tobytes())

# ============================================================
# ブロック2: 客観指標の計測(処理前後で同一関数を使う)
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

def k_weight(samples, sr):
    """
    ITU-R BS.1770のK-weightingを、24kHz向けにRBJ Audio EQ Cookbookの式で
    再設計した近似実装(公式仕様は48kHz用の固定係数のため、他のサンプル
    レートでは物理パラメータからの再設計が必要)。厳密なBS.1770準拠を
    保証するものではなく、比較用の近似LUFS算出のためのものと明記する。
    """
    b1, a1 = design_rbj_highshelf(sr, 1681.9, 3.999844545, 0.7071752369554193)
    b2, a2 = design_rbj_highpass(sr, 38.13547087613982, 0.5003270373238773)
    y = lfilter(b1, a1, samples)
    y = lfilter(b2, a2, y)
    return y

def integrated_lufs_approx(samples, sr):
    """簡易版の2段階ゲーティング積分ラウドネス(BS.1770-3の近似実装)。"""
    y = k_weight(samples, sr)
    block = int(0.4 * sr)
    hop = int(0.1 * sr)
    if len(y) < block:
        return None
    z_list = []
    for start in range(0, len(y) - block + 1, hop):
        seg = y[start:start + block]
        z_list.append(np.mean(seg ** 2))
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
    return -0.691 + 10 * np.log10(np.mean(gated2))

def loudness_range_approx(samples, sr):
    """簡易版ラウドネスレンジ(3秒窓・1秒ホップの短時間ラウドネスP95-P10。EBU R128完全準拠ではない近似)。"""
    y = k_weight(samples, sr)
    block = int(3.0 * sr)
    hop = int(1.0 * sr)
    if len(y) < block:
        return None
    vals = []
    for start in range(0, len(y) - block + 1, hop):
        seg = y[start:start + block]
        z = np.mean(seg ** 2)
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

def measure_metrics(samples, sr, channels, label):
    mono = samples if channels == 1 else samples.mean(axis=1)
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    clip_count = int(np.sum(np.abs(mono) >= 0.999))
    lufs = integrated_lufs_approx(mono, sr)
    lra = loudness_range_approx(mono, sr)
    metrics = {
        "label": label,
        "duration_seconds": round(len(mono) / sr, 3),
        "sample_rate": sr,
        "channels": channels,
        "peak_dbfs": round(db(peak), 2),
        "rms_dbfs": round(db(rms), 2),
        "integrated_lufs_approx": round(lufs, 2) if lufs is not None else None,
        "loudness_range_approx_lu": round(lra, 2) if lra is not None else None,
        "clipping_sample_count": clip_count,
        "clipping_detected": clip_count > 0,
        "lufs_method_note": (
            "ITU-R BS.1770のK-weightingを24kHz向けにRBJ Audio EQ Cookbookの式で再設計し、"
            "2段階ゲーティングで積分ラウドネスを近似計算したもの。公式のBS.1770準拠測定器とは"
            "完全には一致しない可能性がある近似値。"
        ),
        "loudness_range_method_note": (
            "3秒窓・1秒ホップの短時間ラウドネス分布のP95-P10による簡易近似。EBU R128の"
            "LRA完全準拠アルゴリズムではない。"
        ),
    }
    return metrics

# ============================================================
# ブロック3: 軽いソフトニー・コンプレッサー
# ============================================================
def soft_knee_gain_reduction_db(level_db, threshold_db, ratio, knee_db):
    gr = np.zeros_like(level_db)
    lower = threshold_db - knee_db / 2
    upper = threshold_db + knee_db / 2
    below = level_db <= lower
    above = level_db >= upper
    within = ~below & ~above

    # gr(ゲイン補正、dB)は「出力レベル - 入力レベル」。ratio>1では圧縮域で必ず負(減衰)になる。
    gr[above] = (level_db[above] - threshold_db) * (1 / ratio - 1)
    # ニー内は二次補間(Giannoulis et al.のデジタルコンプレッサー設計に基づく定番式)
    x = level_db[within] - lower
    gr[within] = ((1 / ratio - 1) * (x ** 2)) / (2 * knee_db)
    return gr  # 負の値(dB)。0は無圧縮。

def envelope_follower_db(mono, sr, attack_ms, release_ms):
    """ピーク検出+非対称アタック/リリースの一次IIRエンベロープ(dB)。"""
    abs_sig = np.abs(mono)
    attack_coef = np.exp(-1.0 / (sr * attack_ms / 1000.0))
    release_coef = np.exp(-1.0 / (sr * release_ms / 1000.0))
    env = np.zeros_like(abs_sig)
    prev = 0.0
    # 素直な逐次計算(信号長 約190秒×24kHz=約457万サンプルはPythonループでも数秒〜十数秒で完了する規模)
    for i, x in enumerate(abs_sig):
        coef = attack_coef if x > prev else release_coef
        prev = coef * prev + (1 - coef) * x
        env[i] = prev
    env_db = 20 * np.log10(np.maximum(env, 1e-9))
    return env_db

def apply_light_dynamics(mono, sr, params):
    env_db = envelope_follower_db(mono, sr, params["attack_ms"], params["release_ms"])
    threshold_db = float(np.percentile(env_db, params["threshold_percentile"]))
    gr_db = soft_knee_gain_reduction_db(env_db, threshold_db, params["ratio"], params["knee_db"])
    # ゲイン変化そのものも軽く平滑化し、フレーム単位の急峻な変化(耳障りな歪み)を避ける
    smooth_coef = np.exp(-1.0 / (sr * params["gain_smoothing_ms"] / 1000.0))
    gr_db_smoothed = np.zeros_like(gr_db)
    prev = 0.0
    for i, g in enumerate(gr_db):
        prev = smooth_coef * prev + (1 - smooth_coef) * g
        gr_db_smoothed[i] = prev
    gain_linear = 10 ** (gr_db_smoothed / 20)
    processed = mono * gain_linear
    return processed, {
        "threshold_db_used": round(threshold_db, 2),
        "gain_reduction_db": gr_db_smoothed,
    }

def detect_pumping(gr_db_series, sr, threshold=0.5):
    """
    ゲインリダクション時系列(dB)を100Hzへ間引き、直流成分を除いた上で
    0.5〜10Hz帯(周期0.1〜2秒)の周期性を自己相関で調べる。目立つピークが
    あれば「ポンピングの可能性」として報告する(機械的な簡易検出)。
    """
    step = max(1, int(sr / 100))
    ds = gr_db_series[::step]
    ds = ds - np.mean(ds)
    if np.allclose(ds, 0) or len(ds) < 20:
        return {"pumping_suspected": False, "max_autocorr": 0.0, "note": "ゲイン変化がほぼ無いため判定対象外"}
    autocorr = np.correlate(ds, ds, mode="full")
    autocorr = autocorr[len(autocorr) // 2:]
    autocorr = autocorr / (autocorr[0] + 1e-12)
    min_lag = int(0.1 * 100)  # 0.1秒 = 100Hz換算で10サンプル
    max_lag = int(2.0 * 100)  # 2.0秒
    max_lag = min(max_lag, len(autocorr) - 1)
    if min_lag >= max_lag:
        return {"pumping_suspected": False, "max_autocorr": 0.0, "note": "音声が短すぎて判定対象外"}
    window = autocorr[min_lag:max_lag]
    peak_idx = int(np.argmax(window)) + min_lag
    peak_val = float(window[peak_idx - min_lag])
    suspected = peak_val > threshold
    return {
        "pumping_suspected": bool(suspected),
        "max_autocorr": round(peak_val, 3),
        "period_seconds_at_peak": round(peak_idx / 100.0, 2),
        "threshold_used": threshold,
        "note": (
            "0.1〜2.0秒周期帯における自己相関のピークが閾値を超えた場合にポンピングの可能性ありとする簡易判定。"
            "音楽的なコンプレッサー用ポンピング検出の代替として、機械的な参考情報として扱うこと。"
        ),
    }

# ============================================================
# ブロック4: 実行
# ============================================================
PARAMS = {
    "type": "soft_knee_compressor",
    "threshold_percentile": 90,   # エンベロープ分布の上位10%だけを対象にする(絶対dB値の決め打ちを避ける)
    "ratio": 2.5,                 # 低レシオ(軽い制御)
    "knee_db": 6.0,                # ソフトニー幅
    "attack_ms": 5.0,              # 立ち上がりの飛び出しを捉えるための速いアタック
    "release_ms": 200.0,           # 抑揚を壊さないための緩やかなリリース
    "gain_smoothing_ms": 8.0,      # ゲイン変化自体の平滑化(耳障りな歪み防止)
    "makeup_gain_db": 0.0,         # メイクアップゲインなし(小さい箇所を持ち上げない)
}

print("ER-001B-7A: 軽い音量制御(既存音声への後処理のみ)")
print(f"入力: {INPUT_WAV}")
print(f"出力: {OUTPUT_WAV}")
print(f"処理パラメータ: {json.dumps(PARAMS, ensure_ascii=False)}")
print()

samples, sr, channels = read_wav(INPUT_WAV)
mono_in = samples if channels == 1 else samples.mean(axis=1)

print("処理前の指標を計測中...", flush=True)
before_metrics = measure_metrics(samples, sr, channels, "before")
print(json.dumps(before_metrics, ensure_ascii=False, indent=2))
print()

print("軽いダイナミクス制御を適用中(数十秒かかる場合があります)...", flush=True)
processed, dyn_info = apply_light_dynamics(mono_in, sr, PARAMS)
processed = processed * (10 ** (PARAMS["makeup_gain_db"] / 20))

# 安全確認: 圧縮器は常に減衰(gr<=0)のみを行い、増幅しないことを保証する
assert np.all(dyn_info["gain_reduction_db"] <= 1e-6), "ゲイン補正が正(増幅)になっています(想定外)"
# 入力にクリッピングがなくゲインが常に1.0以下であれば、出力もクリッピングし得ない
assert np.max(np.abs(processed)) <= np.max(np.abs(mono_in)) + 1e-6, "処理後のピークが処理前を上回っています(想定外)"

pumping_info = detect_pumping(dyn_info["gain_reduction_db"], sr)
print("ポンピング検出(簡易):", json.dumps(pumping_info, ensure_ascii=False))
print()

write_wav(OUTPUT_WAV, processed, sr, channels)
print(f"→ {OUTPUT_WAV} を保存しました", flush=True)

print("処理後の指標を計測中...", flush=True)
after_samples, after_sr, after_channels = read_wav(OUTPUT_WAV)
after_metrics = measure_metrics(after_samples, after_sr, after_channels, "after")
print(json.dumps(after_metrics, ensure_ascii=False, indent=2))

# ============================================================
# ブロック5: マニフェスト保存
# ============================================================
manifest = {
    "experiment_id": "ER-001B-7A",
    "input_file": INPUT_WAV,
    "output_file": OUTPUT_WAV,
    "tts_regenerated": False,
    "input_file_overwritten": False,
    "processing": {
        "method": "軽いソフトニー・コンプレッサー(ピーク検出エンベロープ、非対称アタック/リリース、"
                   "しきい値=エンベロープ分布の90パーセンタイル、メイクアップゲインなし)",
        "library": "numpy + scipy(このタスクのため.venvへ新規インストール。requirements.txt等は本リポジトリに存在しないため未追加)",
        "params": PARAMS,
        "threshold_db_used_this_file": dyn_info["threshold_db_used"],
    },
    "unchanged": [
        "再生速度", "ピッチ", "セクション間の0.8秒無音の位置", "音声の開始・終了位置",
        "台本", "TTS生成内容", "話者", "感情演技", "サンプルレート(24000Hz)", "チャンネル数(モノラル)",
    ],
    "metrics_before": before_metrics,
    "metrics_after": after_metrics,
    "duration_difference_seconds": round(after_metrics["duration_seconds"] - before_metrics["duration_seconds"], 3),
    "pumping_check": pumping_info,
    "generated_at": datetime.now().isoformat(),
}

with open("er001b7a_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print()
print("-" * 50)
print("er001b7a_manifest.json を保存しました。")
