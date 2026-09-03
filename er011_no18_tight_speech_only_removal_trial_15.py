# ============================================================
# er011_no18_tight_speech_only_removal_trial_15.py
# ER-011-NO18-A2-TIGHT-SPEECH-ONLY-REMOVAL-TRIAL-15
# ============================================================
# 前タスク(ER-011-NO18-A2-TIGHT-SPEECH-ONLY-HISTORY-DIAGNOSTIC-14)の
# 結論を受け、A2 Key Phrase Assemblyの tight_speech_only() 呼び出しを
# 外した状態でNo.18 A2をTrial再assemblyし、
#   1) "be powered off" の語末/fが0.30秒marginを保ったまま残るか
#   2) Key Phrase 1-5全体のpacingに新しい問題が出ないか
# をユーザー試聴で確認できる状態にする。
#
# 重要な制約(このスクリプトが厳守すること):
#   - tight_speech_only() の関数定義自体は変更・削除しない
#     (他の旧one-offスクリプトからの参照が残っているため)。
#   - Production正式経路のファイル(er003_v1_n3_01_assemble.py、
#     er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2/
#     配下の既存assembled成果物)は一切書き換えない。
#     -> Production A2ソース一式を隔離Trialディレクトリへコピーし、
#        そのコピーに対してのみ、実行時にtight_speech_only()を
#        恒等関数へ差し替えた状態でstage_assemble_a2()を呼ぶ
#        (差し替えはcontextmanagerでrun後に必ず元へ戻す)。
#   - TTSは一切再生成しない(Key Phrase 1-5、Full Story/Comment等の
#     既存生成済みwavをそのまま使用。コピー前後でsha256一致を確認する)。
#   - B1には一切触れない。
#
# 正式Production採用は今回のスコープ外。ユーザー試聴後の別タスクで
# 判断する。

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil

import numpy as np

import er002_common as common
import er003_b1_p8a_audio as p8a
import er003_v1_n3_01_assemble as asm
import er008_disfluency_qa_18 as dq18
import er011_no18_specfix_v2_production_run_01 as driver

OUT_DIR = "er011_output/no18_tight_speech_only_removal_trial_15"
TRIAL_THEME_OUT_DIR = f"{OUT_DIR}/theme_root"
PROD_A2_DIR = f"{driver.OUT_DIR}/a2"
TRIAL_A2_DIR = f"{TRIAL_THEME_OUT_DIR}/a2"

KP5_TEXT = "be powered off"


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ------------------------------------------------------------
# §1: Production A2一式を隔離Trialディレクトリへコピー(TTS非再生成)
# ------------------------------------------------------------
def prepare_trial_sources() -> dict:
    assert os.path.isdir(PROD_A2_DIR), f"Production A2ディレクトリが見つかりません: {PROD_A2_DIR}"
    if os.path.exists(TRIAL_A2_DIR):
        shutil.rmtree(TRIAL_A2_DIR)
    os.makedirs(TRIAL_THEME_OUT_DIR, exist_ok=True)
    shutil.copytree(PROD_A2_DIR, TRIAL_A2_DIR)
    # 旧assembled成果物(コピーされたもの)は混同防止のため削除し、
    # stage_assemble_a2()にTrialの出力として新規作成させる。
    assembled_dir = f"{TRIAL_A2_DIR}/assembled"
    if os.path.exists(assembled_dir):
        shutil.rmtree(assembled_dir)
    audit_dir = f"{TRIAL_A2_DIR}/audit"
    for stale in ("timeline.json", "gain_report.json", "run_summary_assemble.json"):
        p = f"{audit_dir}/{stale}"
        if os.path.exists(p):
            os.remove(p)

    # Key Phrase 1-5音声(TTS非再生成の証拠として、コピー前後でsha256一致を確認)
    kp_hash_check = {}
    for i in range(1, 6):
        name = f"kp{i}_en.wav"
        prod_path = f"{PROD_A2_DIR}/narration/{name}"
        trial_path = f"{TRIAL_A2_DIR}/narration/{name}"
        prod_sha = _sha256_file(prod_path)
        trial_sha = _sha256_file(trial_path)
        kp_hash_check[name] = {
            "prod_sha256": prod_sha, "trial_input_sha256": trial_sha,
            "identical_no_regeneration": prod_sha == trial_sha,
        }
    kp5_sha = kp_hash_check["kp5_en.wav"]["prod_sha256"]
    kp_hash_check["kp5_matches_user_approved_030_asset"] = (
        kp5_sha == "3d05cd0e391019ea47ce8efde5e01cb0d59a0ca679661553fe3dc836b5f156f1"
    )
    return kp_hash_check


# ------------------------------------------------------------
# §2: tight_speech_only()の一時的な恒等関数化(Trial範囲のみ)
# ------------------------------------------------------------
_CALL_LOG = {"identity_calls": 0, "original_would_have_cropped": []}


@contextlib.contextmanager
def tight_speech_only_disabled():
    original = asm.p9a.p7c.tight_speech_only
    _CALL_LOG["identity_calls"] = 0
    _CALL_LOG["original_would_have_cropped"] = []

    def _identity(samples, sample_rate):
        # Trial範囲内での呼び出し回数・入力長を記録しつつ、実際にはtrim
        # せずsamplesをそのまま返す(=生成段階のmarginを保持したまま
        # Assemblyへ渡す)。
        _CALL_LOG["identity_calls"] += 1
        _CALL_LOG["original_would_have_cropped"].append({
            "input_len_samples": int(len(samples)),
            "input_duration_seconds": round(len(samples) / sample_rate, 4),
        })
        return samples

    asm.p9a.p7c.tight_speech_only = _identity
    try:
        yield
    finally:
        asm.p9a.p7c.tight_speech_only = original


# ------------------------------------------------------------
# §3: Trial再assembly(Production正式経路のstage_assemble_a2をそのまま
#     呼ぶが、theme['out_dir']を隔離Trialディレクトリへ向ける)
# ------------------------------------------------------------
def run_trial_assembly() -> dict:
    theme = {"theme_id": driver.THEME_ID, "out_dir": TRIAL_THEME_OUT_DIR}
    with tight_speech_only_disabled():
        summary = asm.stage_assemble_a2(theme)
    summary["sha256"] = p8a.sha256_file(summary["out_path"])
    summary["tight_speech_only_identity_calls"] = _CALL_LOG["identity_calls"]
    summary["tight_speech_only_call_inputs"] = _CALL_LOG["original_would_have_cropped"]
    return summary


# ------------------------------------------------------------
# §4: "be powered off" 語末/f確認(旧Production版 vs Trial版)
# ------------------------------------------------------------
def _acoustic_off_tail_analysis(samples: "np.ndarray", sr: int) -> dict:
    """ER-011-NO18...WIRING-12と同一手法(faster-whisperローカル解析)。
    "off"トークンの終端からセグメント末尾までを10ms窓でRMS・高域比を測定。"""
    tmp_path = f"{OUT_DIR}/_tmp_off_tail_slice.wav"
    common.write_wav_float(tmp_path, samples, sr, 1)
    words = dq18.transcribe_verbatim(tmp_path, language="en", model_size="small")
    total_dur = len(samples) / sr

    off_tok = None
    for w in words:
        t = w["text"].strip().lower().strip(".,;:!?")
        if t == "off":
            off_tok = w
            break
    if off_tok is None:
        return {"segment_duration_seconds": round(total_dur, 4), "off_analysis": None}

    start_s = max(0.0, off_tok["start"] - 0.03)
    i0, i1 = int(start_s * sr), int(total_dur * sr)
    window = samples[i0:i1]
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

    rms_w, hb_w = [], []
    for p in range(0, len(window), win_len):
        chunk = window[p:p + win_len]
        rms_w.append(round(rms(chunk), 5))
        hb = high_band_ratio(chunk, sr)
        hb_w.append(round(hb, 4) if hb is not None else None)

    return {
        "segment_duration_seconds": round(total_dur, 4),
        "off_analysis": {
            "off_start": round(off_tok["start"], 4), "off_end": round(off_tok["end"], 4),
            "off_prob": round(off_tok["probability"], 4),
            "off_duration_ms": round((off_tok["end"] - off_tok["start"]) * 1000, 1),
            "segment_end_minus_off_end_ms": round((total_dur - off_tok["end"]) * 1000, 1),
            "rms_10ms_windows_tail_8": rms_w[-8:],
            "high_band_ratio_10ms_windows_tail_8": hb_w[-8:],
            "trailing_hard_silence": all(v is not None and v < 0.0005 for v in rms_w[-3:]) if rms_w else None,
        },
    }


def _timeline_lookup(timeline: list, part_name: str) -> dict:
    for item in timeline:
        if item["part"] == part_name:
            return item
    raise KeyError(part_name)


def compare_kp5_old_vs_trial(prod_timeline: list, trial_timeline: list,
                              prod_wav_path: str, trial_wav_path: str) -> dict:
    prod_kp5 = _timeline_lookup(prod_timeline, "Key Phrase 5")
    trial_kp5 = _timeline_lookup(trial_timeline, "Key Phrase 5")

    prod_samples, prod_sr, prod_ch, _ = common.read_wav_float(prod_wav_path)
    trial_samples, trial_sr, trial_ch, _ = common.read_wav_float(trial_wav_path)
    if prod_ch > 1:
        prod_samples = prod_samples.reshape(-1, prod_ch)[:, 0]
    if trial_ch > 1:
        trial_samples = trial_samples.reshape(-1, trial_ch)[:, 0]

    def slice_seg(samples, sr, item, pad=0.15):
        i0 = max(0, int((item["start_seconds"] - pad) * sr))
        i1 = min(len(samples), int((item["start_seconds"] + item["duration_seconds"] + pad) * sr))
        return samples[i0:i1]

    prod_seg = slice_seg(prod_samples, prod_sr, prod_kp5)
    trial_seg = slice_seg(trial_samples, trial_sr, trial_kp5)

    os.makedirs(f"{OUT_DIR}/kp5_compare", exist_ok=True)
    common.write_wav_float(f"{OUT_DIR}/kp5_compare/prod_kp5_in_assembled.wav", prod_seg, prod_sr, 1)
    common.write_wav_float(f"{OUT_DIR}/kp5_compare/trial_kp5_in_assembled.wav", trial_seg, trial_sr, 1)

    prod_off = _acoustic_off_tail_analysis(prod_seg, prod_sr)
    trial_off = _acoustic_off_tail_analysis(trial_seg, trial_sr)

    return {
        "prod_timeline_entry": prod_kp5,
        "trial_timeline_entry": trial_kp5,
        "duration_delta_seconds": round(trial_kp5["duration_seconds"] - prod_kp5["duration_seconds"], 4),
        "prod_off_tail_analysis": prod_off,
        "trial_off_tail_analysis": trial_off,
    }


# ------------------------------------------------------------
# §5: Key Phrase 1-5全体のpacing比較(旧Production timeline vs Trial)
# ------------------------------------------------------------
def compare_kp_pacing(prod_timeline: list, trial_timeline: list) -> dict:
    names = [f"Key Phrase {i}" for i in range(1, 6)]
    rows = []
    for n in names:
        p = _timeline_lookup(prod_timeline, n)
        t = _timeline_lookup(trial_timeline, n)
        rows.append({
            "part": n,
            "prod_duration_seconds": p["duration_seconds"],
            "trial_duration_seconds": t["duration_seconds"],
            "delta_seconds": round(t["duration_seconds"] - p["duration_seconds"], 4),
        })
    prod_total = _timeline_lookup(prod_timeline, "Outro")
    trial_total = _timeline_lookup(trial_timeline, "Outro")
    prod_end = prod_total["start_seconds"] + prod_total["duration_seconds"]
    trial_end = trial_total["start_seconds"] + trial_total["duration_seconds"]
    return {
        "per_key_phrase": rows,
        "episode_total_duration_prod": round(prod_end, 3),
        "episode_total_duration_trial": round(trial_end, 3),
        "episode_total_delta_seconds": round(trial_end - prod_end, 3),
    }


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_all() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)

    kp_hash_check = prepare_trial_sources()
    assert all(v["identical_no_regeneration"] for k, v in kp_hash_check.items() if k.endswith(".wav")), \
        "Key PhraseソースがコピーでSha256不一致(想定外の変化)"
    assert kp_hash_check["kp5_matches_user_approved_030_asset"], \
        "kp5_en.wavがユーザー承認済み0.30秒版と一致しません"

    trial_assembly = run_trial_assembly()
    assert trial_assembly["tight_speech_only_identity_calls"] >= 5, \
        "tight_speech_only()バイパスがKey Phrase 1-5すべてに適用された証拠がありません"

    prod_timeline = load_json(f"{PROD_A2_DIR}/audit/timeline.json")
    trial_timeline = load_json(f"{TRIAL_A2_DIR}/audit/timeline.json")

    prod_summary = load_json(f"{PROD_A2_DIR}/run_summary_assemble.json")
    prod_wav_path = f"{PROD_A2_DIR}/assembled/English_Your_Way_A2_{driver.THEME_ID.upper()}.wav"
    prod_summary["sha256"] = p8a.sha256_file(prod_wav_path)

    kp5_compare = compare_kp5_old_vs_trial(prod_timeline, trial_timeline, prod_wav_path, trial_assembly["out_path"])
    kp_pacing = compare_kp_pacing(prod_timeline, trial_timeline)

    result = {
        "management_id": "ER-011-NO18-A2-TIGHT-SPEECH-ONLY-REMOVAL-TRIAL-15",
        "kp_source_hash_check": kp_hash_check,
        "prod_assembly_summary": prod_summary,
        "trial_assembly_summary": trial_assembly,
        "kp5_old_vs_trial": kp5_compare,
        "kp_pacing_comparison": kp_pacing,
        "b1_touched": False,
        "production_files_modified": False,
    }
    with open(f"{OUT_DIR}/trial15_final_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print("kp_source_hash_check OK:", all(v["identical_no_regeneration"] for k, v in kp_hash_check.items() if k.endswith(".wav")))
    print("trial_assembly:", trial_assembly["status"], trial_assembly["duration_seconds"], trial_assembly["sha256"][:12],
          "identity_calls=", trial_assembly["tight_speech_only_identity_calls"])
    print("prod kp5 off-tail:", kp5_compare["prod_off_tail_analysis"]["off_analysis"])
    print("trial kp5 off-tail:", kp5_compare["trial_off_tail_analysis"]["off_analysis"])
    print("episode duration delta:", kp_pacing["episode_total_delta_seconds"])
    return result


if __name__ == "__main__":
    run_all()
