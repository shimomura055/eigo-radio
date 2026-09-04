# ============================================================
# er011_no18_tight_speech_and_trim030_production_wiring_23.py
# ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23
# ============================================================
# ユーザー正式採用済みの下記2点を、量産Production仕様として恒久的に
# 固定するための実行スクリプト(Trialではない、コード変更は
# er003_v1_n3_01_assemble.py / er006_audio_cost_pilot_02_shared_
# narration.pyへ別途実施済み)。
#   1. A2 tight_speech_only() removal (load_a2_sources、コード変更のみで
#      完結、再TTS・再Assembly不要)
#   2. Key Phrase trim safety margin = 0.30秒のcache identity保証
#      (Master Audio StoreのMasterAudioKeyへtrim policy versionを追加)
#
# 本スクリプトが行うこと:
#   §A. No.18 A2 kp5("be powered off")のMaster Audio Storeエントリを、
#       旧version key(v1、Wiring-12で0.30秒版へ手動昇格済み)から
#       新version key(KEY_PHRASE_TRIM_POLICY_VERSION)へ一度だけ移行する
#       (既に検証済みの正しい資産を再利用し、無駄な新規TTSを避ける)。
#   §B. 実際のProduction経路(ensure_key_phrase_english_component→
#       Master Audio Store→repro01.generate_key_phrase_component_
#       verified)を、新versionでは未キャッシュのテキストに対して実行し、
#       0.30秒marginが実際にruntimeで使われるevidenceを取得する
#       (新規TTS 1件、小額課金)。
#   §C. No.18 A2を、コード変更後のstage_assemble_a2()(tight_speech_only
#       再cropなし、monkeypatch不使用)で再Assemblyし、ユーザー承認済み
#       21R候補音声とbyte-for-byte一致することを確認する(新規TTS
#       0件、既存承認済み資産のみ使用)。

from __future__ import annotations

import hashlib
import json
import os

import er003_v1_n3_01_assemble as asm
import er003_v1_repro01_main_generate as repro01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er011_no18_evidence_compression_a_precision_21r_production_regen as regen

OUT_DIR = "er011_output/no18_tight_speech_and_trim030_production_wiring_23"
KP5_TEXT = "be powered off"

APPROVED_A2_WAV = (
    f"{regen.NEW_OUT_DIR}/a2/assembled/"
    f"English_Your_Way_A2_{regen.NEW_THEME_ID.upper()}.wav"
)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _kp5_key(style_instruction_version: str) -> store.MasterAudioKey:
    return store.MasterAudioKey(
        language="en", speaker_voice="Aoede", tts_model_id=shared_narration.TTS_MODEL_EN,
        canonical_text=KP5_TEXT, level=None,
        style_instruction_id="key_phrase_english_component",
        style_instruction_version=style_instruction_version,
    )


# ------------------------------------------------------------
# §A: kp5 Master Audio Storeエントリの旧key→新keyへの移行
# ------------------------------------------------------------
def migrate_kp5_master_entry() -> dict:
    old_id = _kp5_key("v1").master_audio_id()
    new_id = _kp5_key(shared_narration.KEY_PHRASE_TRIM_POLICY_VERSION).master_audio_id()

    manifest = store._load_manifest()
    old_entry = manifest.get(old_id)
    assert old_entry is not None, "旧version keyのkp5エントリがMaster Audio Storeに見つかりません"
    assert old_entry["qa_evidence"]["sha256"] is not None

    if new_id in manifest and os.path.exists(manifest[new_id]["audio_path"]):
        return {
            "status": "ALREADY_MIGRATED", "old_master_audio_id": old_id, "new_master_audio_id": new_id,
            "skipped": True,
        }

    old_audio_path = old_entry["audio_path"]
    old_sha256 = _sha256_file(old_audio_path)
    os.makedirs(store.AUDIO_DIR, exist_ok=True)
    new_audio_path = f"{store.AUDIO_DIR}/{new_id}.wav"
    with open(old_audio_path, "rb") as src, open(new_audio_path, "wb") as dst:
        dst.write(src.read())
    new_sha256 = _sha256_file(new_audio_path)
    assert new_sha256 == old_sha256, "移行後のaudio hashが旧資産と一致しません"

    new_entry = dict(old_entry)
    new_entry["audio_path"] = new_audio_path
    new_entry["key"] = _kp5_key(shared_narration.KEY_PHRASE_TRIM_POLICY_VERSION).as_dict()
    new_entry["migrated_from"] = {
        "management_id": "ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23",
        "old_master_audio_id": old_id,
        "reason": "style_instruction_versionをtrim policy versionへ変更(cache identity修正)、"
                  "既に0.30秒版へ昇格済みの資産(Wiring-12)をそのまま新keyへ引き継ぐ",
    }
    manifest[new_id] = new_entry
    store._save_manifest(manifest)

    return {
        "status": "MIGRATED", "old_master_audio_id": old_id, "new_master_audio_id": new_id,
        "old_sha256": old_sha256, "new_sha256": new_sha256, "identity_confirmed": old_sha256 == new_sha256,
        "skipped": False,
    }


# ------------------------------------------------------------
# §B: 新versionでのcache miss→実Production生成のruntime evidence
# ------------------------------------------------------------
VERIFY_TEXT = "put the phone away"  # 過去99件のcache済みKey Phraseと重複しない新規テキスト


def capture_new_key_phrase_runtime_evidence() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.init_logger(f"{OUT_DIR}/cost_log_runtime_evidence.jsonl")
    out_path = f"{OUT_DIR}/runtime_evidence/{VERIFY_TEXT.replace(' ', '_')}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    key_before = _kp5_key(shared_narration.KEY_PHRASE_TRIM_POLICY_VERSION)  # 同一schemaで存在有無を確認するのみ
    manifest_before = store._load_manifest()
    new_style_key = store.MasterAudioKey(
        language="en", speaker_voice="Aoede", tts_model_id=shared_narration.TTS_MODEL_EN,
        canonical_text=VERIFY_TEXT, level=None,
        style_instruction_id="key_phrase_english_component",
        style_instruction_version=shared_narration.KEY_PHRASE_TRIM_POLICY_VERSION,
    )
    existed_before = new_style_key.master_audio_id() in manifest_before

    with cl.logging_context("wiring23_kp_trim030_cache_verify", "keyphrase_trim030_new_version_runtime_evidence"):
        result = shared_narration.ensure_key_phrase_english_component(VERIFY_TEXT, out_path)

    evidence = {
        "text": VERIFY_TEXT, "out_path": out_path,
        "existed_in_manifest_before_this_run": existed_before,
        "reused": result.get("reused"), "cache_miss_reason": result.get("cache_miss_reason"),
        "master_audio_id": result.get("master_audio_id"),
        "status": result.get("status"), "trim_info": result.get("trim_info"),
        "asr_verified": result.get("asr_verified"), "asr_text": result.get("asr_text"),
        "disfluency_checked": result.get("disfluency_checked"),
        "fallback_used": result.get("fallback_used"),
        "sha256": result.get("sha256"),
        "production_constant_kep_phrase_trim_margin": repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
    }
    with open(f"{OUT_DIR}/runtime_evidence_result.json", "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2, default=str)
    return evidence


# ------------------------------------------------------------
# §C: No.18 A2の再Assembly(コード変更後、monkeypatch不使用)
# ------------------------------------------------------------
def reassemble_a2_and_compare() -> dict:
    theme = {"theme_id": regen.NEW_THEME_ID, "out_dir": regen.NEW_OUT_DIR}
    approved_sha256_before = _sha256_file(APPROVED_A2_WAV)

    summary = asm.stage_assemble_a2(theme)
    new_sha256 = _sha256_file(summary["out_path"])

    result = {
        "approved_candidate_path": APPROVED_A2_WAV,
        "approved_candidate_sha256": approved_sha256_before,
        "reassembled_path": summary["out_path"],
        "reassembled_sha256": new_sha256,
        "byte_identical_to_approved_candidate": new_sha256 == approved_sha256_before,
        "duration_seconds": summary["duration_seconds"], "peak": summary["peak"],
        "clipping_detected": summary["clipping_detected"],
    }
    with open(f"{OUT_DIR}/a2_reassemble_comparison.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


def run_all() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    migration = migrate_kp5_master_entry()
    runtime_evidence = capture_new_key_phrase_runtime_evidence()
    reassemble = reassemble_a2_and_compare()
    final = {
        "migration": migration, "runtime_evidence": runtime_evidence, "a2_reassemble": reassemble,
        "production_constant_now": repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
        "key_phrase_trim_policy_version_now": shared_narration.KEY_PHRASE_TRIM_POLICY_VERSION,
    }
    with open(f"{OUT_DIR}/wiring23_final_result.json", "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2, default=str)
    print("migration:", migration["status"])
    print("runtime_evidence:", runtime_evidence["status"], runtime_evidence["reused"],
          runtime_evidence["cache_miss_reason"], runtime_evidence["trim_info"])
    print("a2_reassemble byte_identical:", reassemble["byte_identical_to_approved_candidate"],
          reassemble["duration_seconds"], reassemble["peak"], reassemble["clipping_detected"])
    return final


if __name__ == "__main__":
    run_all()
