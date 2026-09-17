# ============================================================
# er014_output/user_test_news_convenience_ai_01/convenience_ai/finalize_a2_pipeline.py
# 管理ID: USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2
# ============================================================
# 背景: ユーザー正式判断(2026-09-17)により、コンビニAI A2 `point_two`の
# 商品名"Oimo no Canele"読み上げ(FIX-02確認ページでattempt9由来の候補、
# 既に6% time-stretch適用済み)= USER APPROVED。追加TTS再生成は不要。
#
# 本スクリプトが行うこと(TTS新規生成なし):
#   1. narration/point_two.wav が確認ページで提示した候補
#      (attempt9 + 6% slowdown、audit_fix_02/candidate_attempt9_
#      poststretch.wav)とsha256一致することを確認(不一致ならSTOP)。
#   2. narration/point_two_original.wav の存在とsha256(=attempt9生の
#      wav)から、既存Production関数apply_a2_slowdown_postprocess()に
#      よる6% time-stretchが既に適用済みであることを確認し、
#      二重適用を回避する(Tiny Bags CLOSEOUT-03の先例スクリプトが
#      前提とする「未適用」状態とは異なるため、再適用ステップ自体を
#      呼ばない)。
#   3. 内蔵Primary ASR再検証(apply_a2_slowdown_postprocess内部と同一の
#      ロジック、routing.transcribe+en_validator.classify_asr_match)を
#      現在の音声に対して1回実行し、結果を記録する(再生成なし)。
#   4. 既存Production cascade関数(secondary_asr.evaluate_attempt_with_
#      cascade、Ledger Phrase List使用)を1回実行し、"Oimo no Canele"/
#      "AI while"がslowdown後も転写上維持されていることを証跡化する。
#   5. 既存Production関数record_human_approval()でHuman Approvalを記録。
#   6. tts_generation_results.json / review_lock_state.jsonへ、事実を
#      正直に反映するnoteを追記する(隠蔽なし)。
#   7. 既存run_pipeline.pyのassembly_stage/player_stage関数をそのまま
#      呼び、Assembly→Audio Validation Gate→player.html生成を行う。
# ============================================================
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import time
import wave

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as n3_tts
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as en_validator
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr

BASE_DIR = "er014_output/user_test_news_convenience_ai_01/convenience_ai"
A2_DIR = f"{BASE_DIR}/a2"
NARRATION_DIR = f"{A2_DIR}/narration"
AUDIT_DIR = f"{A2_DIR}/audit"
FIX02_DIR = f"{BASE_DIR}/audit_fix_02"
FINALIZE_DIR = f"{A2_DIR}/audit_finalize_a2"
SEGMENT_NAME = "point_two"

# FIX-02確認ページでユーザーが実際に試聴し承認した候補(attempt9 + 6%
# slowdown)のsha256。RESULT_PACKET G6-G14の記述・現物ファイルの両方から
# 独立に確認済み。
EXPECTED_APPROVED_SHA256 = "ed816a60746ba3b52b8414e07a28e70e42f1f48bb57bec9f2c93dc90c6bed4c9"
EXPECTED_RAW_ATTEMPT9_SHA256 = "e233dec4e5fc9fce96efdc584bb9256b30db648cdea0aa5db8469cb38061ca98"


def log(msg):
    print(msg)


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def wav_duration_seconds(path):
    import contextlib
    with contextlib.closing(wave.open(path, "r")) as wf:
        return wf.getnframes() / wf.getframerate()


def step1_verify_no_double_apply():
    """承認対象の候補音声のsha256照合と、slowdownが既に適用済みで
    あることの確認のみ(TTS/post-process呼び出しなし)。"""
    target_path = f"{NARRATION_DIR}/{SEGMENT_NAME}.wav"
    original_path = f"{NARRATION_DIR}/{SEGMENT_NAME}_original.wav"
    candidate_path = f"{FIX02_DIR}/candidate_attempt9_poststretch.wav"

    assert os.path.exists(target_path), f"{target_path}が存在しません"
    assert os.path.exists(original_path), (
        f"{original_path}が存在しません。slowdownが未適用の可能性があり、"
        "本スクリプトの前提(FIX-02で既に適用済み)と矛盾するため停止します。")
    assert os.path.exists(candidate_path), f"{candidate_path}が存在しません"

    target_sha = sha256_of(target_path)
    original_sha = sha256_of(original_path)
    candidate_sha = sha256_of(candidate_path)

    assert target_sha == EXPECTED_APPROVED_SHA256 == candidate_sha, (
        f"narration/point_two.wav(sha256={target_sha})が、FIX-02確認ページで"
        f"ユーザーが承認した候補(sha256={EXPECTED_APPROVED_SHA256})と一致しません。STOP。")
    assert original_sha == EXPECTED_RAW_ATTEMPT9_SHA256, (
        f"point_two_original.wav(sha256={original_sha})がattempt9の生音声"
        f"(sha256={EXPECTED_RAW_ATTEMPT9_SHA256})と一致しません。STOP。")

    target_duration = wav_duration_seconds(target_path)
    original_duration = wav_duration_seconds(original_path)
    ratio = target_duration / original_duration
    log(f"[Finalize][Step1] sha256照合OK(承認候補と完全一致)。"
        f"duration比={ratio:.4f}(目標6%=1.0600、pre={original_duration:.3f}s "
        f"post={target_duration:.3f}s) → 既にapply_a2_slowdown_postprocess()"
        "適用済みと判断し、再適用はしない(二重適用を回避)。")

    return {
        "target_sha256": target_sha,
        "original_sha256": original_sha,
        "candidate_sha256": candidate_sha,
        "target_duration_seconds": round(target_duration, 3),
        "original_duration_seconds": round(original_duration, 3),
        "duration_ratio": round(ratio, 4),
        "already_slowdown_applied": True,
        "double_apply_avoided": True,
    }


def step2_fresh_primary_asr_reverification(canonical_text: str):
    """apply_a2_slowdown_postprocess()内部と同一のロジック(routing.
    transcribe + en_validator.classify_asr_match)を、現在の(既に
    slowdown適用済みの)音声に対して1回だけ再実行し、内蔵Primary ASR
    再検証の結果を記録する(post-processの再適用はしない)。"""
    target_path = f"{NARRATION_DIR}/{SEGMENT_NAME}.wav"
    asr_text, err = routing.transcribe(target_path, language="en-US")
    if err:
        return {"asr_verified": False, "error": err}
    classification = en_validator.classify_asr_match(canonical_text, asr_text)
    homophone_accepted = secondary_asr.is_homophone_candidate_mismatch(classification)
    result = {
        "asr_text": asr_text,
        "classification": classification.classification,
        "should_pass": classification.should_pass,
        "homophone_accepted": homophone_accepted,
        "asr_verified": bool(classification.should_pass or homophone_accepted),
    }
    log(f"[Finalize][Step2] 内蔵Primary ASR再検証(単発): classification="
        f"{result['classification']} asr_verified={result['asr_verified']} "
        f"asr_text={asr_text!r}")
    return result


def step3_fresh_secondary_asr_cascade_with_ledger(canonical_text: str, primary_asr_text: str):
    """既存Production cascade関数(fallback経路と同一)を1回実行し、
    Ledger Phrase List使用のSecondary ASRで"Oimo no Canele"/"AI while"が
    slowdown後も転写上維持されていることを証跡化する。"""
    target_path = f"{NARRATION_DIR}/{SEGMENT_NAME}.wav"
    ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(
        canonical_text, min_confidence="low")]
    verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
        canonical_text, primary_asr_text, [], target_path, language="en-US",
        ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED,
        force_secondary=True, enable_connected_speech_equivalence_layer=True)
    result = {
        "ledger_phrases": ledger_phrases,
        "verified_content": verified_content,
        "stop_retrying": stop_retrying,
        "classification": cls.classification,
        "detail": str(cls),
    }
    log(f"[Finalize][Step3] Secondary ASR cascade(Ledger Phrase List使用): "
        f"classification={cls.classification} verified_content={verified_content}")
    return result


def step4_record_human_approval(canonical_text: str):
    asm.record_human_approval(A2_DIR, SEGMENT_NAME, canonical_text,
                               approved_by="user_via_fable_sandwich_pm")
    approvals = load_json(asm.human_approval_path(A2_DIR))
    log(f"[Finalize][Step4] record_human_approval()完了: {approvals.get(SEGMENT_NAME)}")
    return approvals[SEGMENT_NAME]


def step5_finalize_tts_generation_results(verify1, primary_check, secondary_check, canonical_text):
    results_path = f"{AUDIT_DIR}/tts_generation_results.json"
    all_results = load_json(results_path)
    prior_entry = all_results["segments"][SEGMENT_NAME]

    final_entry = copy.deepcopy(prior_entry)
    final_entry["canonical_text"] = canonical_text
    final_entry["sha256"] = verify1["target_sha256"]
    final_entry["duration_seconds"] = verify1["target_duration_seconds"]
    final_entry["original_path"] = f"{NARRATION_DIR}/{SEGMENT_NAME}_original.wav"
    final_entry["slowdown_applied"] = True
    final_entry["slowdown_info"] = {
        "slowdown_pct_target": 6.0,
        "src_duration_seconds": verify1["original_duration_seconds"],
        "dst_duration_seconds": verify1["target_duration_seconds"],
        "duration_ratio": verify1["duration_ratio"],
        "note": "FIX-02時点でattempt9(標準cascade PASS)へ既存Production関数"
                 "apply_a2_slowdown_postprocess()で適用済み(本タスクでの再適用なし)。",
    }
    final_entry["post_slowdown_asr_text"] = primary_check.get("asr_text")
    final_entry["post_slowdown_classification"] = primary_check.get("classification")
    final_entry["finalize_a2_fresh_primary_asr_recheck"] = primary_check
    final_entry["finalize_a2_fresh_secondary_asr_cascade_with_ledger"] = secondary_check
    final_entry["FINALIZE_A2_NOTE"] = (
        f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2: "
        "ユーザー正式判断(2026-09-17)により、FIX-02確認ページで提示したattempt9+6%slowdown候補"
        f"(sha256={verify1['target_sha256'][:16]}...)= USER APPROVED(Oimo no Canele/AI while含む)。"
        "TTS新規生成なし。既にapply_a2_slowdown_postprocess()で6% time-stretch適用済み(duration比"
        f"{verify1['duration_ratio']})のため、本タスクでは再適用していない(二重適用回避)。"
        f"内蔵Primary ASR単発再検証(post-process内部と同一ロジック)="
        f"{primary_check.get('classification')}(asr_verified={primary_check.get('asr_verified')})。"
        f"追加のSecondary ASR cascade(Ledger Phrase List使用)="
        f"{secondary_check.get('classification')}(verified_content={secondary_check.get('verified_content')})。"
        "最終statusはASR_VALIDATION_UNCERTAINのまま変更していない(自動判定を独自に上書きしない)。"
        "Gateの許可はaudit/human_approved_segments.jsonのHuman Approval記録"
        "(canonical_text_sha256照合)によるHUMAN_APPROVED分岐で行う(既存設計どおり)。"
    )
    all_results["segments"][SEGMENT_NAME] = final_entry
    save_json(results_path, all_results)
    log(f"[Finalize][Step5] tts_generation_results.json segments.{SEGMENT_NAME} 更新完了。")
    return final_entry


def step6_sync_review_lock_state(final_entry):
    lock_path = f"{AUDIT_DIR}/review_lock_state.json"
    state = load_json(lock_path)
    entry = state[SEGMENT_NAME]
    entry["human_approval_reference"] = (
        "audit/human_approved_segments.json参照(USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2、"
        "approved_by=user_via_fable_sandwich_pm)。"
    )
    entry["FINALIZE_A2_NOTE"] = (
        f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2: "
        "ユーザー正式承認済み(FIX-02確認ページのattempt9+6%slowdown候補、Oimo no Canele/AI while"
        "とも許容)。state/final_status(HUMAN_REVIEW_REQUIRED/ASR_VALIDATION_UNCERTAIN)自体は変更"
        "していない(Gateの実際の許可判定はHuman Approval記録によるHUMAN_APPROVED分岐、既存設計"
        f"どおり)。詳細はtts_generation_results.json segments.{SEGMENT_NAME}参照。"
    )
    save_json(lock_path, state)
    log(f"[Finalize][Step6] review_lock_state.json の{SEGMENT_NAME}エントリへnote追記完了。")


def main():
    os.makedirs(FINALIZE_DIR, exist_ok=True)
    cl.install(f"{BASE_DIR}/raw_usage_log.jsonl")

    parts = load_json(f"{A2_DIR}/parts.json")
    canonical_text = parts["point_two_body"]

    with cl.logging_context("user_test_news_convenience_ai_01_convenience_ai_a2",
                             "finalize_a2_point_two"):
        verify1 = step1_verify_no_double_apply()
        primary_check = step2_fresh_primary_asr_reverification(canonical_text)
        secondary_check = step3_fresh_secondary_asr_cascade_with_ledger(
            canonical_text, primary_check.get("asr_text") or "")

    approval_entry = step4_record_human_approval(canonical_text)
    final_entry = step5_finalize_tts_generation_results(
        verify1, primary_check, secondary_check, canonical_text)
    step6_sync_review_lock_state(final_entry)

    summary = {
        "verify1": verify1,
        "primary_check": primary_check,
        "secondary_check": secondary_check,
        "approval_entry": approval_entry,
    }
    save_json(f"{FINALIZE_DIR}/finalize_a2_point_two_summary.json", summary)
    log("[Finalize] 完了。詳細: " f"{FINALIZE_DIR}/finalize_a2_point_two_summary.json")
    return summary


if __name__ == "__main__":
    main()
