# ============================================================
# er011_no18_trial15_kp5_precise_tail_analysis.py
# ER-011-NO18-A2-TIGHT-SPEECH-ONLY-REMOVAL-TRIAL-15 補助解析
# ============================================================
# Trial-15本体(er011_no18_tight_speech_only_removal_trial_15.py)の
# 全体assembly比較は、"Key Phrase 5"タイムラインブロック全体(番号読み
# 上げ→英語1回目→日本語意味→英語2回目→block_end_pause)を対象にして
# いたため、ASRの"off"検出が1回目の"be powered off"に一致してしまい、
# 本当に見たい「2回目(ブロック最後、直後に無音)のoff語末」を正しく
# 捉えられていなかった。
#
# このスクリプトは、p9a.build_key_phrase_block()を直接呼び出し(実際の
# Production/Trial assemblyと全く同じ関数・同じpause定数を使用)、
# 「旧Production版(tight_speech_only()でcrop済みのkp5_en)」と
# 「Trial版(tight_speech_only()を通さない生のkp5_en)」それぞれの
# Key Phrase 5ブロックを個別に構築し、2回目(ブロック最後)の英語
# コンポーネント終端 = block_end_pause直前の位置を、ASRに頼らず
# 完全に解析的な offset 計算で特定して比較する。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p7c_audio as p7c
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er008_disfluency_qa_18 as dq18

OUT_DIR = "er011_output/no18_tight_speech_only_removal_trial_15"
TRIAL_A2_DIR = f"{OUT_DIR}/theme_root/a2"
PROD_A2_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2"

NUMBERING_PAUSE_S = asm.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS  # 0.6
INTERNAL_PAUSE_S = p9a.KEY_PHRASE_INTERNAL_PAUSE_SECONDS       # 0.4
BLOCK_END_PAUSE_S = p9a.KEY_PHRASE_BLOCK_END_PAUSE_SECONDS     # 0.8

# build_key_phrase_block()内のpause生成(silence_stereo)はTARGET_SAMPLE_
# RATE(48kHz)基準で行われる。narrationソースwavはcommon.SAMPLE_RATE
# (24kHz)で保存されているが、mono_24k_to_stereo_target()でTARGET_
# SAMPLE_RATEへ変換してから渡すため、ブロック構築・オフセット計算・
# 秒数換算は必ずTARGET_SAMPLE_RATE基準で行う(24kHz基準のまま計算す
# ると秒数が2倍にずれるバグを踏むため注意)。
SR = p9a.TARGET_SAMPLE_RATE


def _load_mono(path: str) -> "np.ndarray":
    mono, sr, _, _ = common.read_wav_float(path)
    assert sr == common.SAMPLE_RATE, f"narration wavは{common.SAMPLE_RATE}Hz保存の想定: {path} sr={sr}"
    return mono


def _resolve_shared_narration_path(name: str) -> str:
    local_path = f"{TRIAL_A2_DIR}/narration/{name}.wav"
    if os.path.exists(local_path):
        return local_path
    import er003_v1_repro01_main_generate as repro01
    return f"{repro01.A01_NARRATION_DIR}/{name}.wav"


def build_isolated_kp5_blocks() -> dict:
    num_five = p9a.mono_24k_to_stereo_target(_load_mono(_resolve_shared_narration_path("num_five")))
    meaning_5 = p9a.mono_24k_to_stereo_target(_load_mono(f"{TRIAL_A2_DIR}/narration/meaning_5.wav"))
    kp5_raw_mono = _load_mono(f"{TRIAL_A2_DIR}/narration/kp5_en.wav")  # 未trim(TTS生成時のsafety margin込み)
    # tight_speech_only()はnarration native rate(24kHz、common.SAMPLE_RATE)
    # のmono配列に対して、stereo/target変換より前にProductionが実際に
    # 呼んでいるのと同じ引数構成で呼ぶ(er003_v1_n3_01_assemble.py:520
    # と同一呼び出し形)。
    kp5_cropped_mono = p7c.tight_speech_only(kp5_raw_mono, common.SAMPLE_RATE)  # 旧Production挙動を再現(関数自体は未変更)
    kp5_raw = p9a.mono_24k_to_stereo_target(kp5_raw_mono)
    kp5_cropped = p9a.mono_24k_to_stereo_target(kp5_cropped_mono)

    block_old = p9a.build_key_phrase_block(
        num_five, kp5_cropped, meaning_5, SR, numbering_pause_seconds=NUMBERING_PAUSE_S)
    block_trial = p9a.build_key_phrase_block(
        num_five, kp5_raw, meaning_5, SR, numbering_pause_seconds=NUMBERING_PAUSE_S)

    def second_occurrence_offset(english_len_samples: int) -> int:
        numbering_pause = int(round(NUMBERING_PAUSE_S * SR))
        internal_pause = int(round(INTERNAL_PAUSE_S * SR))
        return len(num_five) + numbering_pause + english_len_samples + internal_pause + len(meaning_5) + internal_pause

    off_old = second_occurrence_offset(len(kp5_cropped))
    off_trial = second_occurrence_offset(len(kp5_raw))

    block_end_pause_samples = int(round(BLOCK_END_PAUSE_S * SR))

    slice_old = block_old[off_old: off_old + len(kp5_cropped) + block_end_pause_samples]
    slice_trial = block_trial[off_trial: off_trial + len(kp5_raw) + block_end_pause_samples]

    # 整合性チェック: 各blockはこのsliceの直後で終わっているはず
    assert off_old + len(kp5_cropped) + block_end_pause_samples == len(block_old), \
        "旧版: 2回目英語+block_end_pauseの直後でブロックが終わっていません"
    assert off_trial + len(kp5_raw) + block_end_pause_samples == len(block_trial), \
        "Trial版: 2回目英語+block_end_pauseの直後でブロックが終わっていません"

    return {
        "block_old_total_seconds": round(len(block_old) / SR, 4),
        "block_trial_total_seconds": round(len(block_trial) / SR, 4),
        "kp5_cropped_seconds": round(len(kp5_cropped) / SR, 4),
        "kp5_raw_seconds": round(len(kp5_raw) / SR, 4),
        "second_occurrence_offset_old_seconds": round(off_old / SR, 4),
        "second_occurrence_offset_trial_seconds": round(off_trial / SR, 4),
        "slice_old": slice_old,
        "slice_trial": slice_trial,
    }


def _off_tail_analysis(samples: "np.ndarray", sr: int, label: str) -> dict:
    tmp_path = f"{OUT_DIR}/_tmp_precise_{label}.wav"
    common.write_wav_float(tmp_path, samples, sr, 1)
    words = dq18.transcribe_verbatim(tmp_path, language="en", model_size="small")
    total_dur = len(samples) / sr

    off_tok = None
    for w in words:
        t = w["text"].strip().lower().strip(".,;:!?")
        if t == "off":
            off_tok = w
    # 2件以上"off"が検出される可能性は排除済み(このsliceには2回目の
    # 英語コンポーネント1つ分しか含まれない)が、念のため最後の一致を使う。

    win_len = int(sr * 10 / 1000)

    def rms(chunk):
        return float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2))) if len(chunk) else 0.0

    def high_band_ratio(chunk, sr_, cutoff=4000):
        if len(chunk) < 8:
            return None
        spec = np.abs(np.fft.rfft(chunk))
        freqs = np.fft.rfftfreq(len(chunk), 1 / sr_)
        total = spec.sum() + 1e-12
        return float(spec[freqs > cutoff].sum() / total)

    # sliceの末尾1.2秒を10ms窓で全部見る(block_end_pauseの無音境界も
    # 含めて、どこで音が切れているかを直接観察するため)。
    tail_span = min(len(samples), int(1.2 * sr))
    tail = samples[-tail_span:]
    rms_w, hb_w = [], []
    for p in range(0, len(tail), win_len):
        chunk = tail[p:p + win_len]
        rms_w.append(round(rms(chunk), 5))
        hb = high_band_ratio(chunk, sr)
        hb_w.append(round(hb, 4) if hb is not None else None)

    result = {
        "segment_duration_seconds": round(total_dur, 4),
        "words_detected": [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words],
        "tail_1200ms_rms_10ms_windows": rms_w,
        "tail_1200ms_high_band_ratio_10ms_windows": hb_w,
    }
    if off_tok is not None:
        off_end = off_tok["end"]
        result["off_analysis"] = {
            "off_start": round(off_tok["start"], 4), "off_end": round(off_end, 4),
            "off_prob": round(off_tok["probability"], 4),
            "off_duration_ms": round((off_tok["end"] - off_tok["start"]) * 1000, 1),
            "segment_end_minus_off_end_ms": round((total_dur - off_end) * 1000, 1),
        }
    else:
        result["off_analysis"] = None
    return result


def run_all() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    blocks = build_isolated_kp5_blocks()
    slice_old_stereo, slice_trial_stereo = blocks.pop("slice_old"), blocks.pop("slice_trial")
    slice_old, slice_trial = slice_old_stereo[:, 0], slice_trial_stereo[:, 0]

    os.makedirs(f"{OUT_DIR}/kp5_compare", exist_ok=True)
    common.write_wav_float(f"{OUT_DIR}/kp5_compare/prod_kp5_2nd_occurrence_precise.wav", slice_old_stereo, SR, 2)
    common.write_wav_float(f"{OUT_DIR}/kp5_compare/trial_kp5_2nd_occurrence_precise.wav", slice_trial_stereo, SR, 2)

    old_analysis = _off_tail_analysis(slice_old, SR, "old")
    trial_analysis = _off_tail_analysis(slice_trial, SR, "trial")

    # PCM相関(重なる長さ分だけ、先頭を揃えて比較。Trial版はsafety margin
    # 分だけ英語コンポーネントが長いため、単純長さ比較ではなく、
    # 「旧版の音声内容がTrial版の対応区間にそのまま含まれているか」を
    # 相互相関で確認する。
    def cross_correlate_containment(short, long_):
        if len(short) == 0 or len(long_) < len(short):
            return None
        # 旧版(short)をTrial版(long_)内でスライドさせて最大相関位置を探す
        best_corr, best_offset = -1.0, None
        step = max(1, len(short) // 2000)  # 粗探索→精密化の2段階は行わず、粗刻みで十分な精度を確認
        for offset in range(0, len(long_) - len(short) + 1, step):
            seg = long_[offset:offset + len(short)]
            denom = (np.linalg.norm(short) * np.linalg.norm(seg))
            corr = float(np.dot(short, seg) / denom) if denom > 0 else 0.0
            if corr > best_corr:
                best_corr, best_offset = corr, offset
        return {"best_correlation": round(best_corr, 5), "best_offset_seconds": round(best_offset / SR, 4)}

    kp5_cropped_len = int(round(blocks["kp5_cropped_seconds"] * SR))
    containment = cross_correlate_containment(slice_old[:kp5_cropped_len], slice_trial)

    result = {
        "blocks": blocks,
        "prod_2nd_occurrence_tail_analysis": old_analysis,
        "trial_2nd_occurrence_tail_analysis": trial_analysis,
        "old_content_containment_in_trial": containment,
    }
    with open(f"{OUT_DIR}/kp5_precise_tail_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(json.dumps({
        "blocks": blocks,
        "prod_off": old_analysis["off_analysis"],
        "trial_off": trial_analysis["off_analysis"],
        "containment": containment,
    }, ensure_ascii=False, indent=2, default=str))
    return result


if __name__ == "__main__":
    run_all()
