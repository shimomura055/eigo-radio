# ============================================================
# er011_no18_kp_trim030_production_wiring_12.py
# ER-011-NO18-KEYPHRASE-TRIM-030-PRODUCTION-WIRING-12
# ============================================================
# ユーザー正式決定(Trial-11の0.30秒版を試聴・承認)を受け、Key Phrase
# trim safety marginの0.20→0.30秒をProduction正式経路へ配線する。
#
# このスクリプトが行うこと:
#   §A. Master Audio Store + No.18 A2 kp5_en.wavを、ユーザーが実際に
#       試聴・承認したTrial-11のTrial B音声そのもの(新規別takeではない)
#       へ昇格・差し替える(昇格前にidentity[hash]を確認、旧資産は
#       backupへ退避)。
#   §B. Production正式Key Phrase経路(review_lock guarded、
#       repro01.generate_key_phrase_component_verified、A2/B1で完全に
#       同一の関数)を実際に呼び出し、0.30秒がruntimeで使われることの
#       実証evidenceを取得する(A2的なlayout・B1的なlayoutそれぞれで
#       1回ずつ、隔離されたverify専用theme_idを使い、既存Production
#       のreview_lock状態には一切触れない)。あわせて過去問題となった
#       "follow-up time"(語頭/f/保護)の回帰確認を兼ねる。
#   §C. No.18 A2を正式Production assembly経路(er003_v1_n3_01_assemble.
#       stage_assemble_a2)で再assemblyする(Key Phrase 1-4・他segment
#       は無変更のまま再利用、TTS再生成なし)。
#
# No.18 B1(pool_n18_notifications_specfix_v2/b1b)の完成音声・TTS・
# assemblyは一切実行しない(ユーザー指示、今回は変更しない)。

from __future__ import annotations

import hashlib
import json
import os
import shutil

import numpy as np

import er002_common as common
import er003_b1_p8a_audio as p8a
import er003_v1_n3_01_assemble as asm
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er008_disfluency_qa_18 as dq18
import er003_v1_repro01_main_generate as repro01
import er011_no18_specfix_v2_production_run_01 as driver

OUT_DIR = "er011_output/no18_kp_trim030_production_wiring_12"
BACKUP_DIR = f"{OUT_DIR}/backup_before_promotion"
RUNTIME_EVIDENCE_DIR = f"{OUT_DIR}/runtime_evidence"

TRIAL_ASSET_PATH = "er011_output/no18_kp5_trim_margin_trial_11/audio/kp5_en_trial_margin030.wav"
TRIAL_RESULTS_PATH = "er011_output/no18_kp5_trim_margin_trial_11/trial11_results.json"

A2_OUT_DIR = f"{driver.OUT_DIR}/a2"
A2_NARRATION_DIR = f"{A2_OUT_DIR}/narration"
A2_KP5_PATH = f"{A2_NARRATION_DIR}/kp5_en.wav"
A2_TTS_RESULTS_PATH = f"{A2_OUT_DIR}/audit/tts_generation_results.json"

KP5_TEXT = "be powered off"


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _make_kp5_master_key() -> store.MasterAudioKey:
    return store.MasterAudioKey(
        language="en", speaker_voice="Aoede", tts_model_id=shared_narration.TTS_MODEL_EN,
        canonical_text=KP5_TEXT, level=None,
        style_instruction_id="key_phrase_english_component", style_instruction_version="v1",
    )


def _acoustic_off_tail_analysis(path: str) -> dict:
    """DIAGNOSTIC-10/TRIAL-11と同一手法(faster-whisperローカル解析、
    追加課金なし)。"off"トークンの終端からfile末尾までを10ms窓で
    RMS・高域(>4kHz)スペクトル比を測定する。"""
    words = dq18.transcribe_verbatim(path, language="en", model_size="small")
    samples, sr, channels, _n = common.read_wav_float(path)
    if channels > 1:
        samples = samples.reshape(-1, channels)[:, 0]
    total_dur = len(samples) / sr

    off_tok = None
    for w in words:
        t = w["text"].strip().lower().strip(".,;:!?")
        if t == "off":
            off_tok = w
            break
    if off_tok is None:
        return {"file_duration_seconds": round(total_dur, 4), "off_analysis": None}

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
        "file_duration_seconds": round(total_dur, 4),
        "off_analysis": {
            "off_start": round(off_tok["start"], 4), "off_end": round(off_tok["end"], 4),
            "off_prob": round(off_tok["probability"], 4),
            "off_duration_ms": round((off_tok["end"] - off_tok["start"]) * 1000, 1),
            "file_end_minus_off_end_ms": round((total_dur - off_tok["end"]) * 1000, 1),
            "rms_10ms_windows_tail_5": rms_w[-5:],
            "high_band_ratio_10ms_windows_tail_5": hb_w[-5:],
        },
    }


# ------------------------------------------------------------
# §A: Trial B資産のMaster Audio Store + Production A2昇格
# ------------------------------------------------------------
def promote_trial_b_asset() -> dict:
    os.makedirs(BACKUP_DIR, exist_ok=True)

    trial_results = json.load(open(TRIAL_RESULTS_PATH, encoding="utf-8"))
    trial_sha256 = trial_results["trial_sha256"]
    assert trial_sha256 == _sha256_file(TRIAL_ASSET_PATH), "Trial資産のhashが記録と不一致(改変検知)"

    key = _make_kp5_master_key()
    master_id = key.master_audio_id()
    manifest = store._load_manifest()
    entry = manifest.get(master_id)
    assert entry is not None, "Master Audio Storeに既存のbe powered offエントリが見つかりません"

    old_master_audio_path = entry["audio_path"]
    old_master_sha256 = _sha256_file(old_master_audio_path)
    old_prod_sha256 = _sha256_file(A2_KP5_PATH)
    identity_confirmed = (old_master_sha256 == old_prod_sha256 == entry["qa_evidence"]["sha256"])
    assert identity_confirmed, "旧Production資産とMaster Audio Storeの内容が一致しません(想定外の状態)"

    # backup(rollback用、Production側の実ファイルは書き換え前に必ず退避する)
    shutil.copyfile(old_master_audio_path, f"{BACKUP_DIR}/master_audio_{master_id}_020_original.wav")
    shutil.copyfile(A2_KP5_PATH, f"{BACKUP_DIR}/a2_kp5_en_020_original.wav")
    with open(f"{BACKUP_DIR}/manifest_020_original_entry.json", "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
    shutil.copyfile(A2_TTS_RESULTS_PATH, f"{BACKUP_DIR}/a2_tts_generation_results_020_original.json")

    # 1) Master Audio Storeの実体音声を、ユーザー承認済みTrial B音声で置換
    shutil.copyfile(TRIAL_ASSET_PATH, old_master_audio_path)
    new_qa_evidence = {
        "sha256": trial_sha256,
        "asr_verified": trial_results["generation_result"]["asr_verified"],
        "asr_text": trial_results["generation_result"]["asr_text"],
        "disfluency_checked": trial_results["generation_result"]["disfluency_checked"],
        "disfluency_evidence": trial_results["generation_result"]["disfluency_evidence"],
    }
    entry["qa_evidence"] = new_qa_evidence
    entry["promoted_from_trial"] = {
        "management_id": "ER-011-NO18-A2-KP5-TRIM-MARGIN-03-TRIAL-11",
        "promoted_by_management_id": "ER-011-NO18-KEYPHRASE-TRIM-030-PRODUCTION-WIRING-12",
        "trial_asset_path": TRIAL_ASSET_PATH,
        "trailing_margin_retained_seconds": trial_results["generation_result"]["trim_info"]["trailing_margin_retained_seconds"],
        "previous_sha256_020": old_master_sha256,
    }
    manifest[master_id] = entry
    store._save_manifest(manifest)

    # 2) No.18 A2の実アセットも同じTrial B音声へ差し替え
    shutil.copyfile(TRIAL_ASSET_PATH, A2_KP5_PATH)

    # 3) tts_generation_results.json(Assemble Gateが参照する監査記録)の
    #    kp5.englishエントリを、新しい実体と一致するよう更新する
    #    (ASSET_HASH_MISMATCH/MISSING_MANDATORY_DISFLUENCY_QAでGateに
    #    ブロックされないようにするための必須更新)。
    results_doc = json.load(open(A2_TTS_RESULTS_PATH, encoding="utf-8"))
    old_kp5_entry = results_doc["key_phrases"]["5"]["english"]
    results_doc["key_phrases"]["5"]["english"] = {
        "status": "OK",
        "path": A2_KP5_PATH,
        "reused": True,
        "master_audio_id": master_id,
        "cache_miss_reason": None,
        "sha256": trial_sha256,
        "asr_verified": new_qa_evidence["asr_verified"],
        "asr_text": new_qa_evidence["asr_text"],
        "disfluency_checked": new_qa_evidence["disfluency_checked"],
        "disfluency_evidence": new_qa_evidence["disfluency_evidence"],
        "promoted_from_trial": entry["promoted_from_trial"],
    }
    with open(A2_TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results_doc, f, ensure_ascii=False, indent=2, default=str)

    return {
        "master_audio_id": master_id,
        "old_sha256_020": old_master_sha256,
        "new_sha256_030": trial_sha256,
        "old_kp5_entry_020": old_kp5_entry,
        "identity_confirmed_before_promotion": identity_confirmed,
    }


# ------------------------------------------------------------
# §B: Production正式Key Phrase経路のruntime evidence
# ------------------------------------------------------------
def run_runtime_evidence() -> dict:
    os.makedirs(RUNTIME_EVIDENCE_DIR, exist_ok=True)
    cl.init_logger(f"{OUT_DIR}/cost_log_runtime_evidence.jsonl")

    results = {}
    # A2的なlayoutでの実行 + "follow-up time"語頭/f/回帰確認を兼ねる
    a2_style_path = f"{RUNTIME_EVIDENCE_DIR}/kp_trim030_verify_a2_theme/A2/narration/followup_time_verify.wav"
    os.makedirs(os.path.dirname(a2_style_path), exist_ok=True)
    with cl.logging_context("kp_trim030_verify_a2_theme", "keyphrase_trim030_runtime_evidence_a2"):
        r_a2 = repro01.generate_key_phrase_component_verified("follow-up time", a2_style_path)
    results["a2_path_verify"] = {
        "text": "follow-up time", "out_path": a2_style_path,
        "status": r_a2.get("status"), "trim_info": r_a2.get("trim_info"),
        "asr_text": r_a2.get("asr_text"), "asr_verified": r_a2.get("asr_verified"),
        "disfluency_checked": r_a2.get("disfluency_checked"),
        "fallback_used": r_a2.get("fallback_used"),
    }

    # B1的なlayoutでの実行(A2/B1が完全に同一関数を共有していることの
    # 独立した2件目のevidence)
    b1_style_path = f"{RUNTIME_EVIDENCE_DIR}/kp_trim030_verify_b1_theme/B1/narration/settle_routine_verify.wav"
    os.makedirs(os.path.dirname(b1_style_path), exist_ok=True)
    with cl.logging_context("kp_trim030_verify_b1_theme", "keyphrase_trim030_runtime_evidence_b1"):
        r_b1 = repro01.generate_key_phrase_component_verified("settle into a routine", b1_style_path)
    results["b1_path_verify"] = {
        "text": "settle into a routine", "out_path": b1_style_path,
        "status": r_b1.get("status"), "trim_info": r_b1.get("trim_info"),
        "asr_text": r_b1.get("asr_text"), "asr_verified": r_b1.get("asr_verified"),
        "disfluency_checked": r_b1.get("disfluency_checked"),
        "fallback_used": r_b1.get("fallback_used"),
    }

    with open(f"{OUT_DIR}/runtime_evidence_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results


# ------------------------------------------------------------
# §C: No.18 A2再assembly(Production正式経路)
# ------------------------------------------------------------
def reassemble_a2() -> dict:
    theme = {"theme_id": driver.THEME_ID, "out_dir": driver.OUT_DIR}
    summary = asm.stage_assemble_a2(theme)
    summary["sha256"] = p8a.sha256_file(summary["out_path"])
    with open(f"{OUT_DIR}/a2_reassemble_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    return summary


def run_all() -> dict:
    trial_sha256 = json.load(open(TRIAL_RESULTS_PATH, encoding="utf-8"))["trial_sha256"]
    if os.path.exists(A2_KP5_PATH) and _sha256_file(A2_KP5_PATH) == trial_sha256:
        # promote_trial_b_asset()は非冪等(backupを上書きしうる)ため、既に
        # 昇格済み(A2資産のhashがTrial B音声と一致)ならスキップする。
        print("promote_trial_b_asset: already promoted (A2 kp5_en.wav sha256 matches Trial B), skipping.")
        manifest = store._load_manifest()
        master_id = _make_kp5_master_key().master_audio_id()
        promotion = {"master_audio_id": master_id, "new_sha256_030": trial_sha256, "skipped_already_promoted": True}
    else:
        promotion = promote_trial_b_asset()
    runtime_evidence = run_runtime_evidence()
    kp5_acoustic_after = _acoustic_off_tail_analysis(A2_KP5_PATH)
    assemble = reassemble_a2()
    final = {
        "promotion": promotion,
        "runtime_evidence": runtime_evidence,
        "kp5_acoustic_after_promotion": kp5_acoustic_after,
        "a2_reassemble": assemble,
        "production_constant_now": repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
    }
    with open(f"{OUT_DIR}/wiring12_final_result.json", "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2, default=str)
    print("promotion:", promotion.get("old_sha256_020", "(skipped)")[:12], "->", promotion["new_sha256_030"][:12])
    print("runtime_evidence a2:", runtime_evidence["a2_path_verify"]["status"],
          runtime_evidence["a2_path_verify"]["trim_info"])
    print("runtime_evidence b1:", runtime_evidence["b1_path_verify"]["status"],
          runtime_evidence["b1_path_verify"]["trim_info"])
    print("a2_reassemble:", assemble["status"], assemble["duration_seconds"], assemble["sha256"][:12])
    return final


if __name__ == "__main__":
    run_all()
