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
# OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01(2026-09-12
# ユーザー正式決定 APPROVED_FOR_PRODUCTION): Candidate D-2(voicing許容
# Cascadeの厳密一致引き上げ)は、既存classify_ja_asr_match()自体の
# ASR_VALIDATION_UNCERTAINという返り値の意味を変更せず、この
# Cascade呼び出し元でのpost-processingとして配線する(Trial REPORT
# 「修正2回目」節§6の設計どおり)。
import er011_ja_asr_variant_layer_01 as ja_variant_layer

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

# ============================================================
# OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01(2026-10-11ユーザー正式決定
# APPROVED_FOR_PRODUCTION): SCG(Secondary Confirm Gate)。
# Primary ASR(OpenAI)がTRUE_CONTENT_MISMATCHと判定した音声に対し、既存の重大差分
# 除外条件(数字・否定の不一致、全体類似度0.4未満)に該当しない場合に限り、
# Azure Secondary ASRを1回(Phrase Listなし)だけ独立確認として実行する。
# Secondaryの書き起こしが原稿とEXACT_MATCH/NORMALIZED_MATCHならPASS
# (final_status=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG)。それ以外
# (PHONETIC_MATCH含む不一致・判定不能・Azure例外/空)は従来どおり
# TRUE_CONTENT_MISMATCH(=TTS再生成/fallback/STOP)へ戻す。
# SCGはTTS再生成attemptを消費しない(attempt上限・fallback・Human Review Lockは無変更)。
# 日本語経路専用(英語ASR経路[er006_secondary_asr_01]には触れない)。
# ============================================================
SCG_FINAL_STATUS = "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG"
SCG_PASS_CLASSIFICATIONS = ("EXACT_MATCH", "NORMALIZED_MATCH")  # PHONETIC_MATCH等は自動PASSに含めない
SCG_MIN_SIMILARITY = 0.4  # 既存classify_ja_asr_matchのtts_failure_threshold既定と同値(短文の0.4未満は当面除外)
SCG_AZURE_TIMEOUT_SECONDS = 90.0
# Feature Flag: 既定ON(PRODUCTION_WIRED)。環境変数JA_SCG_ENABLED=0/false/off/noでも即時OFFにできる
# (緊急停止用、コード変更不要)。
FEATURE_FLAG_JA_SCG_ENABLED = True
# 費用見積(Phase 0 Trialと同一の登録単価換算: $1.0/hour x 160円/USD、1回あたり秒切上げ)。
SCG_AZURE_USD_PER_HOUR = 1.0
SCG_JPY_PER_USD = 160.0


def _scg_enabled() -> bool:
    if not FEATURE_FLAG_JA_SCG_ENABLED:
        return False
    env = os.environ.get("JA_SCG_ENABLED")
    if env is not None and env.strip().lower() in ("0", "false", "off", "no"):
        return False
    return True


def _scg_exclusion_reason(cls: "javal.ClassificationResultJA") -> Optional[str]:
    """SCGを実行しない理由(既存の重大差分除外条件)を返す。実行してよければNone。
    新しい除外・緩和は導入しない(数字/否定/類似度0.4未満のみ、既存設計どおり)。"""
    if cls.classification != "TRUE_CONTENT_MISMATCH":
        return "not_true_content_mismatch"
    if cls.protected.number_mismatches:
        return f"number_mismatch:{cls.protected.number_mismatches}"
    if cls.protected.negation_mismatches:
        return f"negation_mismatch:{cls.protected.negation_mismatches}"
    if cls.similarity_ratio < SCG_MIN_SIMILARITY:
        return f"similarity_lt_{SCG_MIN_SIMILARITY}:{round(cls.similarity_ratio, 3)}"
    return None


def _wav_duration_seconds(wav_path: str) -> Optional[float]:
    try:
        import wave
        with wave.open(wav_path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


def _scg_service_info() -> dict:
    sdk_version = None
    try:
        import azure.cognitiveservices.speech as speechsdk
        sdk_version = speechsdk.__version__
    except Exception:
        pass
    return {"service": "Azure Speech STT (continuous recognition, no Phrase List)",
            "azure_region": os.environ.get("SPEECH_REGION"), "speech_sdk_version": sdk_version,
            "language": "ja-JP", "phrase_list": False}


def _run_scg_secondary_confirm(canonical_text: str, wav_path: str,
                                expected_readings: dict | None) -> dict:
    """Azure Secondary ASRを1回だけ実行して原稿と照合する(SCG本体)。例外・空・Noneは
    UNAVAILABLE(PASSにも新規STOPにもしない=従来動作へ戻す)。PASSはEXACT/NORMALIZEDのみ。"""
    info = {"scg_applied": True, **_scg_service_info()}
    audio_seconds = _wav_duration_seconds(wav_path)
    info["audio_seconds"] = round(audio_seconds, 3) if audio_seconds is not None else None
    if audio_seconds is not None:
        import math
        info["est_cost_jpy"] = round(math.ceil(audio_seconds) * SCG_AZURE_USD_PER_HOUR / 3600.0 * SCG_JPY_PER_USD, 4)
    else:
        info["est_cost_jpy"] = None
    t0 = time.time()
    text, err = None, None
    try:
        text, err = p4.get_full_text_via_azure_stt_continuous(
            wav_path, language="ja-JP", timeout_seconds=SCG_AZURE_TIMEOUT_SECONDS)
    except Exception as e:  # noqa: BLE001  安全側: 例外は従来動作へ戻す
        err = f"{type(e).__name__}: {e}"
    info["wall_seconds"] = round(time.time() - t0, 2)
    info["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    info["secondary_transcript"] = text
    info["error"] = err
    if text is None or not str(text).strip():
        info.update(scg_result="UNAVAILABLE", secondary_classification=None,
                    judgement_reason="Secondary取得不能または空(従来どおり再生成/fallback/STOPへ戻す)")
        return info
    cls_sec = javal.classify_ja_asr_match(canonical_text, text, expected_readings=expected_readings)
    info["secondary_classification"] = cls_sec.classification
    if cls_sec.classification in SCG_PASS_CLASSIFICATIONS:
        info.update(scg_result="PASS",
                    judgement_reason=f"Secondary(Azure)転写が原稿と{cls_sec.classification}"
                                      f"(Primary不一致・Secondary一致=独立エンジン不一致): {cls_sec.reason}")
    else:
        info.update(scg_result="NG",
                    judgement_reason=f"Secondary転写も原稿と不一致({cls_sec.classification}、"
                                      f"PHONETIC_MATCH等は自動PASSに含めない): {cls_sec.reason}")
    return info


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


def _apply_variant_layer_voicing_upgrade(canonical_text: str, asr_text: Optional[str],
                                          cls_step: Optional["javal.ClassificationResultJA"]
                                          ) -> Optional["javal.ClassificationResultJA"]:
    """OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01: Candidate
    D-2(voicing許容Cascadeの厳密一致引き上げ)。cls_stepがASR_VALIDATION_
    UNCERTAIN(根拠がphonetic_uncertainのみ)の場合に限り、形態素解析
    ベースの厳密一致で裏付けが取れればPHONETIC_MATCHへ引き上げた新しい
    結果を返す。それ以外(対象外・厳密不一致・flag OFF・asr_text無し)は
    元のcls_stepをそのまま返す(既存挙動を変えない)。"""
    if cls_step is None or asr_text is None:
        return cls_step
    upgraded = ja_variant_layer.try_upgrade_voicing_cascade(canonical_text, asr_text, cls_step)
    return upgraded if upgraded is not None else cls_step


def evaluate_attempt_ja_with_cascade_detail(
    canonical_text: str, primary_asr_text: Optional[str], wav_path: str,
    cascade_enabled: bool = FEATURE_FLAG_JA_PRIMARY_OPENAI,
    # NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b: 既定None(後方互換)。
    # 辞書登録トークンの確定読み(小文字キー、カタカナ値)。Primary#1・
    # Primary#2・Secondary#1・Secondary#2の全ステップのclassify_ja_asr_
    # match呼び出しへ同じ値をそのまま転送する。
    expected_readings: dict | None = None,
) -> dict:
    """Primary(OpenAI)#1の判定結果を受け取り、entity-likeなASR_VALIDATION_
    UNCERTAINであれば、TTSを再生成せず同じ音声に対してCascade(Primary#2->
    Secondary#1->Secondary#2)を追加実行する。cascade_enabled=Falseなら
    classify_ja_asr_matchの結果をそのまま返す(後方互換)。"""
    cls = javal.classify_ja_asr_match(canonical_text, primary_asr_text, expected_readings=expected_readings)
    cls = _apply_variant_layer_voicing_upgrade(canonical_text, primary_asr_text, cls)
    steps = [{"step": "primary_1", "provider": "openai_asr", "text": primary_asr_text,
              "classification": cls.classification}]
    result = {
        "verified": cls.should_pass, "stop_retrying": not cls.should_retry and not cls.should_pass,
        "classification": cls, "cascade_invoked": False, "steps": steps,
        "final_status": cls.classification, "human_review_required": False,
        "canonical_text": canonical_text, "wav_path": wav_path,
    }

    # --- OPEN-258 SCG(Secondary Confirm Gate)。既存の早期returnより前、Primaryが
    # TRUE_CONTENT_MISMATCHの場合だけ評価する(ASR_VALIDATION_UNCERTAIN経路は無変更) ---
    if cascade_enabled and not cls.should_pass and cls.classification == "TRUE_CONTENT_MISMATCH":
        exclusion = _scg_exclusion_reason(cls)
        if not _scg_enabled():
            scg_info = {"scg_applied": False, "scg_result": "DISABLED_BY_FLAG", "exclusion_reason": "flag_off"}
        elif exclusion is not None:
            scg_info = {"scg_applied": False, "scg_result": "NOT_APPLIED", "exclusion_reason": exclusion}
        else:
            scg_info = _run_scg_secondary_confirm(canonical_text, wav_path, expected_readings)
            steps.append({"step": "scg_secondary", "provider": "azure", "text": scg_info.get("secondary_transcript"),
                           "classification": scg_info.get("secondary_classification") or "TTS_FAILURE",
                           "scg_result": scg_info["scg_result"]})
        scg_info["primary_text"] = primary_asr_text
        result["scg_applied"] = scg_info["scg_applied"]
        result["scg_result"] = scg_info["scg_result"]
        result["scg_info"] = scg_info
        if scg_info["scg_result"] == "PASS":
            scg_cls = javal.ClassificationResultJA(
                SCG_FINAL_STATUS, cls.similarity_ratio, cls.protected, should_pass=True, should_retry=False,
                reason=f"Primary(OpenAI)はTRUE_CONTENT_MISMATCHだが、Secondary(Azure)が原稿と一致: "
                       f"{scg_info['judgement_reason']}")
            scg_cls.scg_info = scg_info
            result.update(verified=True, stop_retrying=False, final_status=SCG_FINAL_STATUS, classification=scg_cls)
            return result
        cls.scg_info = scg_info  # NG/不実行/UNAVAILABLE: 従来どおり再生成へ。証跡だけ付与(既存キー不変)
        return result

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
    cls_p2 = javal.classify_ja_asr_match(
        canonical_text, text_p2, expected_readings=expected_readings) if text_p2 is not None else None
    cls_p2 = _apply_variant_layer_voicing_upgrade(canonical_text, text_p2, cls_p2)
    steps.append({"step": "primary_2", "provider": "openai_asr", "text": text_p2,
                   "classification": cls_p2.classification if cls_p2 else "TTS_FAILURE"})
    if cls_p2 is not None and cls_p2.should_pass:
        result.update(verified=True, stop_retrying=False, final_status=cls_p2.classification, classification=cls_p2)
        return result
    _track_orthographic(cls_p2, "openai")

    # --- Secondary #1(Azure) ---
    text_s1, err_s1 = p4.get_full_text_via_azure_stt_continuous(wav_path, language="ja-JP", timeout_seconds=90.0)
    cls_s1 = javal.classify_ja_asr_match(
        canonical_text, text_s1, expected_readings=expected_readings) if text_s1 is not None else None
    cls_s1 = _apply_variant_layer_voicing_upgrade(canonical_text, text_s1, cls_s1)
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
    cls_s2 = javal.classify_ja_asr_match(
        canonical_text, text_s2, expected_readings=expected_readings) if text_s2 is not None else None
    cls_s2 = _apply_variant_layer_voicing_upgrade(canonical_text, text_s2, cls_s2)
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
    # NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b: 既定None(後方互換)。
    expected_readings: dict | None = None,
) -> tuple[bool, bool, "javal.ClassificationResultJA"]:
    """Production retry loop向けのdrop-in互換ラッパー(English版
    evaluate_attempt_with_cascade()と同じ形の戻り値)。"""
    detail = evaluate_attempt_ja_with_cascade_detail(
        canonical_text, primary_asr_text, wav_path, cascade_enabled=cascade_enabled,
        expected_readings=expected_readings)
    if detail["human_review_required"]:
        _log_human_review(detail)
    return detail["verified"], detail["stop_retrying"], detail["classification"]
