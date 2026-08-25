# ============================================================
# er007_ja_secondary_asr_01.py
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01 Part B:
# 日本語ASR CascadeをEnglish(er006_secondary_asr_01.py)と同じ思想へ統一する。
# Primary OpenAI gpt-4o-mini-transcribe #1 -> #2(必要時)
# -> Secondary Azure Speech STT #1 -> #2(必要時) -> Human/User Review
# 同一音声に対して複数回ASRだけをやり直す(TTSは再生成しない)。
# ============================================================
from __future__ import annotations

import json
import os
import time
from typing import Optional

import er003_b1_p4_audio as p4  # Azure STT呼び出し(既存の連続認識関数を再利用)
import er005_cost_logger as cl
import er007_ja_asr_validator_01 as javal

FEATURE_FLAG_JA_PRIMARY_OPENAI = False  # Production既定はOFF(タスク仕様に
                                          # 従い、本タスクの検証結果を報告した
                                          # 上でユーザー判断を待つ。Part Fの
                                          # 6条件を満たすまで無条件ON化しない)

CASCADE_CONFIG_JA = {
    "max_primary_attempts": 2,
    "max_secondary_attempts": 2,
}

HUMAN_REVIEW_LOG_PATH_JA = "er007_output/ja_asr_cascade_01/human_review_queue.jsonl"


def _log_human_review(detail: dict) -> None:
    os.makedirs(os.path.dirname(HUMAN_REVIEW_LOG_PATH_JA), exist_ok=True)
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "canonical_text": detail["canonical_text"], "wav_path": detail["wav_path"],
        "steps": detail["steps"], "final_status": detail["final_status"],
    }
    with open(HUMAN_REVIEW_LOG_PATH_JA, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def is_entity_like_mismatch_ja(result: "javal.ClassificationResultJA") -> bool:
    return javal.is_entity_like_mismatch_ja(result)


def evaluate_attempt_ja_with_cascade_detail(
    canonical_text: str, primary_asr_text: Optional[str], wav_path: str,
    cascade_enabled: bool = FEATURE_FLAG_JA_PRIMARY_OPENAI,
) -> dict:
    """Primary(OpenAI)#1の判定結果を受け取り、entity-likeなASR_VALIDATION_
    UNCERTAINであれば、TTSを再生成せず同じ音声に対してCascade(Primary#2->
    Secondary#1->Secondary#2)を追加実行する。cascade_enabled=Falseなら
    classify_ja_asr_matchの結果をそのまま返す(後方互換)。"""
    cls = javal.classify_ja_asr_match(canonical_text, primary_asr_text)
    steps = [{"step": "primary_1", "provider": "openai_asr", "text": primary_asr_text,
              "classification": cls.classification}]
    result = {
        "verified": cls.should_pass, "stop_retrying": not cls.should_retry and not cls.should_pass,
        "classification": cls, "cascade_invoked": False, "steps": steps,
        "final_status": cls.classification, "human_review_required": False,
        "canonical_text": canonical_text, "wav_path": wav_path,
    }

    if cls.should_pass or not cascade_enabled or not is_entity_like_mismatch_ja(cls):
        return result

    result["cascade_invoked"] = True
    import er006_asr_provider_routing_01 as routing

    # --- Primary #2(同じ音声、OpenAI、TTSは再生成しない) ---
    text_p2, err_p2 = routing._transcribe_openai_mini(wav_path, "ja-JP", "gpt-4o-mini-transcribe")
    cls_p2 = javal.classify_ja_asr_match(canonical_text, text_p2) if text_p2 is not None else None
    steps.append({"step": "primary_2", "provider": "openai_asr", "text": text_p2,
                   "classification": cls_p2.classification if cls_p2 else "TTS_FAILURE"})
    if cls_p2 is not None and cls_p2.should_pass:
        result.update(verified=True, stop_retrying=False, final_status=cls_p2.classification, classification=cls_p2)
        return result

    # --- Secondary #1(Azure) ---
    text_s1, err_s1 = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP", timeout_seconds=90.0)
    cls_s1 = javal.classify_ja_asr_match(canonical_text, text_s1) if text_s1 is not None else None
    steps.append({"step": "secondary_1", "provider": "azure", "text": text_s1,
                   "classification": cls_s1.classification if cls_s1 else "TTS_FAILURE"})
    if cls_s1 is not None and cls_s1.should_pass:
        result.update(verified=True, stop_retrying=False, final_status=cls_s1.classification, classification=cls_s1)
        return result

    # --- Secondary #2(Azure、同じ音声を再度) ---
    text_s2, err_s2 = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP", timeout_seconds=90.0)
    cls_s2 = javal.classify_ja_asr_match(canonical_text, text_s2) if text_s2 is not None else None
    steps.append({"step": "secondary_2", "provider": "azure", "text": text_s2,
                   "classification": cls_s2.classification if cls_s2 else "TTS_FAILURE"})
    if cls_s2 is not None and cls_s2.should_pass:
        result.update(verified=True, stop_retrying=False, final_status=cls_s2.classification, classification=cls_s2)
        return result

    # --- 4 step全て不一致 -> Human Review(TTSは再生成しない) ---
    result.update(human_review_required=True, stop_retrying=True, final_status="ASR_VALIDATION_UNCERTAIN")
    return result


def evaluate_attempt_ja_with_cascade(
    canonical_text: str, primary_asr_text: Optional[str], wav_path: str,
    cascade_enabled: bool = FEATURE_FLAG_JA_PRIMARY_OPENAI,
) -> tuple[bool, bool, "javal.ClassificationResultJA"]:
    """Production retry loop向けのdrop-in互換ラッパー(English版
    evaluate_attempt_with_cascade()と同じ形の戻り値)。"""
    detail = evaluate_attempt_ja_with_cascade_detail(
        canonical_text, primary_asr_text, wav_path, cascade_enabled=cascade_enabled)
    if detail["human_review_required"]:
        _log_human_review(detail)
    return detail["verified"], detail["stop_retrying"], detail["classification"]
