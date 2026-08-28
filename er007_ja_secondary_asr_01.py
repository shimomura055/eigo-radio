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
import er008_asr_variant_hardening_15_ja_kanji_readings as ja_kanji_readings

FEATURE_FLAG_JA_PRIMARY_OPENAI = True  # ER-007-JA-ASR-VALIDATOR-REDESIGN-
                                         # AND-CASCADE-01: Part Fの6条件を
                                         # 全て満たし、2026-08-25にユーザーが
                                         # Production配線を明示承認したため
                                         # ON化(Cascade自体も有効化)。

CASCADE_CONFIG_JA = {
    "max_primary_attempts": 2,
    "max_secondary_attempts": 2,
}

HUMAN_REVIEW_LOG_PATH_JA = "er007_output/ja_asr_cascade_01/human_review_queue.jsonl"


def _log_human_review(detail: dict) -> None:
    import er011_human_review_lock_01 as review_lock  # 遅延import(循環import回避)
    # ER-011-HUMAN-REVIEW-COST-GUARD-01 Part G: 同一segment・同一
    # canonical_textのqueue重複投入を防ぐ。
    if review_lock.is_duplicate_queue_entry(HUMAN_REVIEW_LOG_PATH_JA, detail["wav_path"], detail["canonical_text"]):
        return
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


ORTHOGRAPHIC_VARIANT_CONFIRMED = "ORTHOGRAPHIC_VARIANT_CONFIRMED"


def _orthographic_reading_confirmed(cls_step: "javal.ClassificationResultJA") -> bool:
    """ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part G/H: このステップの
    差分が、単なる濁点差の許容(_reading_equal_allowing_voicing、ころ/ごろ
    を常に同一視してしまう)ではなく、「ASR側の表記(漢字span)が辞書上
    持ちうる正当な読み候補の中に、canonical側の期待読みが含まれるか」で
    判定する。entity_like(固有名詞・略語)な差は対象外(Human Review温存)。
    候補一覧が取得できない(辞書に登録が無い)場合はNone相当としてFalse
    を返す(安全側、勝手に一致とみなさない)。"""
    if cls_step.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = cls_step.protected.content_diffs
    if not diffs or any(d["entity_like"] or not d["cascade_eligible"] for d in diffs):
        return False
    for d in diffs:
        # javal._hira_reading()を使う(safety._kakasi_readingはローマ字を
        # 返すため、辞書データ[kanwadict4.db]がひらがなで持つ読み候補
        # 一覧と表現形式を揃える必要がある)。
        canonical_reading = javal._hira_reading(d["canonical"])
        is_candidate = ja_kanji_readings.reading_is_candidate(d["asr"], canonical_reading)
        if not is_candidate:
            return False
    return True


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

    # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part G/H: 「ASR側の表記が
    # 辞書上持ちうる正当な読み候補にcanonicalの期待読みが含まれるか」を
    # 各ステップ個別に確認し(_orthographic_reading_confirmed)、かつ
    # 異なる2エンジン(OpenAI/Azure)以上がその状態に到達した場合のみ
    # ORTHOGRAPHIC_VARIANT_CONFIRMEDとしてPASSする(単一エンジンの
    # 繰り返しだけでは裏付けにしない)。entity_like・読みで説明できない
    # 差分が一度でも出た場合はこの経路を諦める(Human Review温存)。
    orthographic_ok_engines: set[str] = set()
    orthographic_disqualified = False

    def _track_orthographic(cls_step: "javal.ClassificationResultJA", engine: str) -> None:
        nonlocal orthographic_disqualified
        if cls_step is None:
            return
        if _orthographic_reading_confirmed(cls_step):
            orthographic_ok_engines.add(engine)
        else:
            orthographic_disqualified = True

    _track_orthographic(cls, "openai")

    # --- Primary #2(同じ音声、OpenAI、TTSは再生成しない) ---
    text_p2, err_p2 = routing._transcribe_openai_mini(wav_path, "ja-JP", "gpt-4o-mini-transcribe")
    cls_p2 = javal.classify_ja_asr_match(canonical_text, text_p2) if text_p2 is not None else None
    steps.append({"step": "primary_2", "provider": "openai_asr", "text": text_p2,
                   "classification": cls_p2.classification if cls_p2 else "TTS_FAILURE"})
    if cls_p2 is not None and cls_p2.should_pass:
        result.update(verified=True, stop_retrying=False, final_status=cls_p2.classification, classification=cls_p2)
        return result
    _track_orthographic(cls_p2, "openai")

    # --- Secondary #1(Azure) ---
    text_s1, err_s1 = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP", timeout_seconds=90.0)
    cls_s1 = javal.classify_ja_asr_match(canonical_text, text_s1) if text_s1 is not None else None
    steps.append({"step": "secondary_1", "provider": "azure", "text": text_s1,
                   "classification": cls_s1.classification if cls_s1 else "TTS_FAILURE"})
    if cls_s1 is not None and cls_s1.should_pass:
        result.update(verified=True, stop_retrying=False, final_status=cls_s1.classification, classification=cls_s1)
        return result
    _track_orthographic(cls_s1, "azure")
    if not orthographic_disqualified and len(orthographic_ok_engines) >= 2:
        result.update(verified=True, stop_retrying=False, final_status=ORTHOGRAPHIC_VARIANT_CONFIRMED,
                       classification=cls_s1)
        return result

    # --- Secondary #2(Azure、同じ音声を再度) ---
    text_s2, err_s2 = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP", timeout_seconds=90.0)
    cls_s2 = javal.classify_ja_asr_match(canonical_text, text_s2) if text_s2 is not None else None
    steps.append({"step": "secondary_2", "provider": "azure", "text": text_s2,
                   "classification": cls_s2.classification if cls_s2 else "TTS_FAILURE"})
    if cls_s2 is not None and cls_s2.should_pass:
        result.update(verified=True, stop_retrying=False, final_status=cls_s2.classification, classification=cls_s2)
        return result
    _track_orthographic(cls_s2, "azure")
    if not orthographic_disqualified and len(orthographic_ok_engines) >= 2:
        result.update(verified=True, stop_retrying=False, final_status=ORTHOGRAPHIC_VARIANT_CONFIRMED,
                       classification=cls_s2)
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
