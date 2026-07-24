# ============================================================
# er003_b1_p3t_audio.py
# ER-003-B1-P3T: 日本語通し音声への英語Key Phrase差し込み検証
# ============================================================
# ER-003-B1-P3Sでは、日本語後半spanを助詞「を」始まりの断片として単独
# 生成した結果、「を」が不自然に聞こえた。本ステージでは、助詞を文脈
# から切り離さず、英語Key Phraseを除いた日本語文全体を1回のTTS callで
# 生成し、別生成した英語Key Phraseを、日本語音声内の自然な間(ポーズ)
# 位置へ差し込む方式を検証する。
#
# 検証対象はER-003-B1-P3Sと同じ一文(shot on target)に限定し、Pattern A
# 全文・B1本文の生成は行わない。
#
# 新しいTTS instruction・別voiceは一切導入しない。B2までに採用済みの
# 同一instruction(er002_common.build_style_prefix、無変更)を日本語・
# 英語の両方に使う。
#
# 再利用するもの(再実装しない):
#   - er002_common.build_style_prefix/SAMPLE_RATE/_call_tts_with_retry/
#     assemble_audio/pcm_to_wav_bytes/pcm_bytes_to_float_mono/
#     write_wav_float/measure_metrics/apply_dynamics3_once/MODEL_NAME
#   - er002_gemini_client.make_tts_call_fn(voice_name)
#   - er003_b1_p3r_audio.sha256_text/VOICE_NAME/build_tts_prompt
#   - er003_b1_p3s_audio.PATTERN_A_SOURCE_PATH/JOIN_PAUSE_SECONDS/
#     MAX_TTS_TECHNICAL_RETRY(P3Sと同一の境界無音・再試行方針)
#
# 新規に追加するのは、(1) 挿入位置を作るための最小限の句読点追加
# (build_tts_japanese_script)と、(2) 生成済み日本語音声内の無音区間を
# 検出するfind_pause_window、(3) その位置で日本語音声を分割して英語を
# 挟み込むsplice_english_into_japaneseの3つのみ(いずれもこの用途の
# 既存実装がないため)。TTS instruction・音声処理(Dynamics3等)は一切
# 再実装しない。

from __future__ import annotations

from typing import Optional

import numpy as np

import er003_b1_p3r_audio as p3r
import er003_b1_p3s_audio as p3s

ARTICLE_ID = "A01"
VOICE_NAME = p3r.VOICE_NAME  # "Aoede"(P3R/P3Sと同一)

PATTERN_A_SOURCE_PATH = p3s.PATTERN_A_SOURCE_PATH
sha256_text = p3r.sha256_text
build_style_prefix = p3r.build_style_prefix
build_tts_prompt = p3r.build_tts_prompt

# ER-003-B1-P3Sで使ったのと同じ一文(spec section 3、ユーザー指定の
# 文字列をそのまま定数化する)。
SOURCE_INTEGRATED_SENTENCE = (
    "前半は激しい接触と緊張が続き、両チームとも枠内シュート、"
    "shot on targetを記録できないまま、静かな均衡が保たれます。"
)
SOURCE_JAPANESE_FULL_SENTENCE = (
    "前半は激しい接触と緊張が続き、両チームとも枠内シュートを記録できないまま、静かな均衡が保たれます。"
)
SOURCE_ENGLISH_KEYWORD = "shot on target"

# 挿入位置を作るための句読点追加は、この1箇所だけに限定する(語彙・
# 語順・助詞は一切変更しない)。
_INSERTION_MARKER = "枠内シュートを記録できないまま"
_INSERTION_REPLACEMENT = "枠内シュート、を記録できないまま"

JOIN_PAUSE_SECONDS = p3s.JOIN_PAUSE_SECONDS  # 0.2秒(P3Sと同一の初回技術値)
MAX_TTS_TECHNICAL_RETRY = p3s.MAX_TTS_TECHNICAL_RETRY  # 1


def build_tts_japanese_script(source_japanese_full_sentence: str = SOURCE_JAPANESE_FULL_SENTENCE) -> str:
    """挿入位置(「枠内シュート」と「を記録できないまま」の間)へ、句読点
    「、」を1つだけ追加する。この位置は元の統合原稿で英語Key Phraseの
    直前にあった読点と同じ位置であり、新しい句読点を恣意的に追加した
    ものではない。語彙・語順・助詞は一切変更しない。"""
    if _INSERTION_MARKER not in source_japanese_full_sentence:
        raise ValueError("挿入位置のマーカーが日本語通し原稿内に見つかりません")
    return source_japanese_full_sentence.replace(_INSERTION_MARKER, _INSERTION_REPLACEMENT, 1)


def find_pause_window(
    samples: "np.ndarray",
    sample_rate: int,
    exclude_start_seconds: float = 0.15,
    exclude_end_seconds: float = 0.15,
    window_ms: float = 20.0,
    silence_rms_threshold: float = 0.02,
) -> Optional[dict]:
    """samples内(先頭・末尾の一定区間を除く)で、RMSがsilence_rms_
    threshold以下となる連続区間のうち最長のものを探し、その開始・終了
    サンプル位置と中心位置を返す。候補が見つからない場合はNoneを返す
    (呼び出し側は「差し込み位置を安全に特定できない」として停止する)。"""
    window_size = max(1, int(sample_rate * window_ms / 1000))
    start_idx = int(exclude_start_seconds * sample_rate)
    end_idx = len(samples) - int(exclude_end_seconds * sample_rate)
    if end_idx <= start_idx:
        return None

    windows = []
    for pos in range(start_idx, end_idx, window_size):
        chunk = samples[pos:min(pos + window_size, end_idx)]
        if len(chunk) == 0:
            continue
        rms = float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))
        windows.append((pos, rms <= silence_rms_threshold))

    best_run = None
    run_start = None
    for pos, silent in windows:
        if silent:
            if run_start is None:
                run_start = pos
        else:
            if run_start is not None:
                run_len = pos - run_start
                if best_run is None or run_len > (best_run[1] - best_run[0]):
                    best_run = (run_start, pos)
                run_start = None
    if run_start is not None:
        run_len = end_idx - run_start
        if best_run is None or run_len > (best_run[1] - best_run[0]):
            best_run = (run_start, end_idx)

    if best_run is None:
        return None

    run_start, run_end = best_run
    return {
        "start_sample": run_start,
        "end_sample": run_end,
        "center_sample": (run_start + run_end) // 2,
        "duration_seconds": round((run_end - run_start) / sample_rate, 4),
        "start_seconds": round(run_start / sample_rate, 4),
        "end_seconds": round(run_end / sample_rate, 4),
    }


def splice_english_into_japanese(
    ja_samples: "np.ndarray",
    en_samples: "np.ndarray",
    pause_window: dict,
    sample_rate: int,
    boundary_pause_seconds: float = JOIN_PAUSE_SECONDS,
) -> "np.ndarray":
    """ja_samplesを、検出済みpause_windowの中心で2つに分割し、その間へ
    en_samplesを境界無音付きで挿入する。分割位置は検出済み無音区間の
    中心であり、「枠内シュート」の途中や「を」の直前音を削らない安全
    マージンとして機能する。"""
    center = pause_window["center_sample"]
    ja_before = ja_samples[:center]
    ja_after = ja_samples[center:]

    pause = np.zeros(int(sample_rate * boundary_pause_seconds), dtype=ja_samples.dtype)
    return np.concatenate([ja_before, pause, en_samples, pause, ja_after])
