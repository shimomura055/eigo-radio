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
        # 委任_04A(記録欠落是正): queue「表示」の重複だけを抑止し、記録(Primary/
        # Secondary転写を含むsteps)は消さず、append-onlyのattempt_history.jsonlへ残す。
        review_lock.append_attempt_history_event(detail["wav_path"], "HUMAN_REVIEW_QUEUE_DUPLICATE_SUPPRESSED", {
            "canonical_text": detail["canonical_text"], "steps": detail.get("steps"),
            "final_status": detail.get("final_status")})
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


def _has_latin(text: str) -> bool:
    return any(("a" <= ch.lower() <= "z") or ("ａ" <= ch.lower() <= "ｚ") for ch in (text or ""))


# OPEN-258 SCG 推奨4(2026-10-11ユーザー正式採用 APPROVED_FOR_PRODUCTION): 否定マーカー
# 「ず/ません/ぬ/ざる/まい」による否定差分をSCG重大差分除外へ追加する。SCG内部に限定し、
# 共通ASR判定(protected_check_ja / safety._has_negation_ja)は変更しない。
# 単純な部分文字列判定はしない(「ずっと」「いぬ」「まいにち」等を誤検出するため)。
# 形態素解析(fugashi/unidic)で「否定の助動詞」と解析されたtokenだけを否定表現とみなし、
# 原稿とPrimary転写の文字差分(opcode)の範囲に重なる否定tokenが片側にのみある場合に限り除外する。
# 「ませんか」(疑問・勧誘)の「ん」は否定とみなさない。解析不能(fugashi無し/offset不整合)なら
# この規則では除外しない(従来どおりの挙動、SCG PASSはEXACT/NORMALIZEDのみという別の安全弁がある)。
_SCG_NEG_SURFACES = ("ず", "ぬ", "ん", "ざる", "ざら", "ざれ", "ざり", "まい")
_SCG_NEG_CTYPES = ("助動詞-ヌ", "助動詞-マイ")
_scg_tagger = None


def _scg_negation_ranges(text: str) -> Optional[list]:
    """textの中で否定の助動詞と解析された(start, end)範囲のリスト。解析不能ならNone。"""
    global _scg_tagger
    try:
        if _scg_tagger is None:
            import fugashi
            _scg_tagger = fugashi.Tagger()
        words = list(_scg_tagger(text))
    except Exception:
        return None
    if sum(len(w.surface) for w in words) != len(text):
        return None  # offsetが合わない(空白等)場合は判定しない
    ranges, pos = [], 0
    for i, w in enumerate(words):
        start, end = pos, pos + len(w.surface)
        pos = end
        try:
            pos1 = w.feature.pos1
            ctype = w.feature.cType
        except Exception:
            continue
        if pos1 != "助動詞" or w.surface not in _SCG_NEG_SURFACES or ctype not in _SCG_NEG_CTYPES:
            continue
        if w.surface == "ん" and i + 1 < len(words) and words[i + 1].surface == "か":
            continue  # 「ませんか」=疑問・勧誘用法は否定差分としない
        ranges.append((start, end))
    return ranges


def _scg_negation_marker_diff(canonical_text: str, asr_text: str) -> Optional[str]:
    """原稿とPrimary転写の文字差分(opcode)のうち、否定の助動詞が片側にのみ含まれる差分があれば
    その説明を返す。無ければNone。差分範囲外の否定語、両側に否定がある差分は対象外。"""
    if not canonical_text or not asr_text:
        return None
    import difflib
    c_norm, a_norm = javal.normalize_ja(canonical_text), javal.normalize_ja(asr_text)
    c_rng, a_rng = _scg_negation_ranges(c_norm), _scg_negation_ranges(a_norm)
    if c_rng is None or a_rng is None:
        return None
    sm = difflib.SequenceMatcher(None, c_norm, a_norm, autojunk=False)

    def hit(rngs, i1, i2):
        return any(s < i2 and e > i1 for s, e in rngs) if i2 > i1 else False

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        c_hit, a_hit = hit(c_rng, i1, i2), hit(a_rng, j1, j2)
        if c_hit != a_hit:
            return f"{c_norm[i1:i2]!r}->{a_norm[j1:j2]!r}"
    return None


def _scg_heterophone_candidate(diff: dict) -> bool:
    """C2(同形異音語ガード、2026-10-11ユーザー正式採用 APPROVED_FOR_PRODUCTION):
    差分のPrimary転写側spanの読みが、原稿側漢字spanの辞書上の正当な読み候補に含まれる
    (=TTSが別の正当読みで読んだ可能性がある)場合True。候補が辞書に無い/判定不能はFalse
    (Primary ASRの単なる誤認識を過剰に除外しないため、候補に含まれると確認できた場合のみTrue)。"""
    c, a = diff.get("canonical", ""), diff.get("asr", "")
    if not c or not a:
        return False
    try:
        a_reading = javal._hira_reading(a)
        return ja_kanji_readings.reading_is_candidate(c, a_reading) is True
    except Exception:
        return False


def _scg_exclusion_reason(cls: "javal.ClassificationResultJA", canonical_text: Optional[str] = None,
                          primary_text: Optional[str] = None, *, u1_released: bool = False) -> Optional[str]:
    """SCGを実行しない理由を返す。実行してよければNone。
    既存の重大差分除外(数字/否定/類似度0.4未満)に加え、Opus独立レビュー必須1(C1)として
    固有名詞・略語系の差分(entity_like、辞書読み不一致、原稿側のラテン文字差分)が1件でも
    あれば除外する(Azureが正しい固有名詞読みと偶然一致して誤PASSするのを防ぐ)。
    u1_released=True(委任_10 U1解放後の診断用。統一judgeのA5/A6撤廃と同じ範囲): 類似度<0.4とC1(entity_like・Latin語)は除外理由にせず、
    残る除外(登録読み辞書不一致=A7→C2同形異音=A4)を先に判定する(U1R-09: 解放後にA4除外のclipがC1表示にならないよう順序を変える)。
    既定(False)は旧SCG経路(evaluate_attempt_ja_with_scg等)と既存testのための旧挙動。"""
    if cls.classification != "TRUE_CONTENT_MISMATCH":
        return "not_true_content_mismatch"
    if cls.protected.number_mismatches:
        return f"number_mismatch:{cls.protected.number_mismatches}"
    if cls.protected.negation_mismatches:
        return f"negation_mismatch:{cls.protected.negation_mismatches}"
    if u1_released:
        for d in (cls.protected.content_diffs or []):
            if d.get("reading_dictionary_mismatch"):
                return f"reading_dictionary_mismatch:{d.get('reading_dictionary_token')}"
        for d in (cls.protected.content_diffs or []):
            if _scg_heterophone_candidate(d):
                return f"heterophone_reading_candidate:{d.get('canonical')}->{d.get('asr')}"
        if canonical_text is not None and primary_text is not None:
            neg = _scg_negation_marker_diff(canonical_text, primary_text)
            if neg:
                return f"negation_marker_diff:{neg}"
        return None
    if cls.similarity_ratio < SCG_MIN_SIMILARITY:
        return f"similarity_lt_{SCG_MIN_SIMILARITY}:{round(cls.similarity_ratio, 3)}"
    for d in (cls.protected.content_diffs or []):
        if d.get("reading_dictionary_mismatch"):
            return f"reading_dictionary_mismatch:{d.get('reading_dictionary_token')}"
        if d.get("entity_like"):
            return f"entity_like_diff:{d.get('canonical')}->{d.get('asr')}"
        if _has_latin(d.get("canonical", "")):
            return f"latin_in_canonical_diff:{d.get('canonical')}"
        if _scg_heterophone_candidate(d):
            return f"heterophone_reading_candidate:{d.get('canonical')}->{d.get('asr')}"
    if canonical_text is not None and primary_text is not None:
        neg = _scg_negation_marker_diff(canonical_text, primary_text)
        if neg:
            return f"negation_marker_diff:{neg}"
    return None


def _azure_stt_strict(wav_path: str, language: str = "ja-JP", timeout_seconds: float = 90.0):
    """SCG専用のAzure連続認識ラッパー(Opus必須2)。Production共通関数
    p4.get_full_text_via_azure_stt_continuousは変えない。共通関数はcanceledもsession_stoppedと
    同じ扱いで、途中のError cancelでも部分転写をerror=Noneで返す。このラッパーは
    CancellationReason.Error(認証/ネットワーク/サービスエラー等)を検出したらtext=None+errorを返し、
    呼び出し側でUNAVAILABLE扱い(従来動作へ戻す)にする。EndOfStream(ファイル正常終了)は正常。"""
    if not os.path.exists(wav_path):
        return None, f"音声ファイルが見つかりません: {wav_path}"
    try:
        from dotenv import load_dotenv
        import azure.cognitiveservices.speech as speechsdk
    except ImportError as exc:
        return None, f"Azure Speech SDKの読み込みに失敗しました: {exc}"
    load_dotenv()
    key, region = os.getenv("SPEECH_KEY"), os.getenv("SPEECH_REGION")
    if not key or not region:
        return None, "SPEECH_KEY/SPEECH_REGIONが.envに設定されていません"
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_recognition_language = language
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    segments: list = []
    state = {"done": False, "cancel_error": None}

    def on_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            segments.append(evt.result.text)

    def on_stopped(evt):
        state["done"] = True

    def on_canceled(evt):
        try:
            details = evt.cancellation_details
            if details.reason == speechsdk.CancellationReason.Error:
                state["cancel_error"] = f"CancellationReason.Error: {getattr(details, 'error_details', None)}"
        except Exception as exc:  # noqa: BLE001  詳細取得不能=保守側でError扱い
            state["cancel_error"] = f"canceled(詳細取得不能): {exc}"
        state["done"] = True

    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_stopped)
    recognizer.canceled.connect(on_canceled)
    recognizer.start_continuous_recognition()
    start = time.time()
    while not state["done"] and (time.time() - start) < timeout_seconds:
        time.sleep(0.5)
    recognizer.stop_continuous_recognition()
    # 委任_05A(Opus必須M2、OPEN-271): SCG用Azure STTもer006と同形でAzure費用を計上する
    # (旧実装は未計上=0円)。成功/失敗にかかわらず送信した音声秒数を記録する。
    cl.record({
        "provider": "azure", "api": "azure_stt_strict_scg", "model_id": "azure-speech-stt",
        "locale": language, "attempt_number": 1, "success": bool(state["done"] and not state["cancel_error"]),
        "elapsed_seconds": round(time.time() - start, 3), "usage_source": "LOCAL_WAV_HEADER_EXACT",
        "audio_duration_submitted_seconds": _wav_duration_seconds(wav_path),
    })
    if state["cancel_error"]:
        return None, state["cancel_error"]
    if not state["done"]:
        return None, f"連続認識がtimeout({timeout_seconds}秒)内に完了しませんでした"
    return "".join(segments), None


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
        text, err = _azure_stt_strict(
            wav_path, language="ja-JP", timeout_seconds=SCG_AZURE_TIMEOUT_SECONDS)
    except Exception as e:  # noqa: BLE001  安全側: 例外は従来動作へ戻す
        if unified_judge_mod.is_config_stop_error(e):
            raise  # 委任_06c(OF-AUW-C-02): 設定不備(init_logger未呼出/[STOP]単価未登録)は握りつぶさない
        err = f"{type(e).__name__}: {e}"
    info["wall_seconds"] = round(time.time() - t0, 2)
    info["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    info["secondary_transcript"] = text
    info["error"] = err
    if text is None or not str(text).strip():
        info.update(scg_result="UNAVAILABLE", secondary_classification=None,
                    judgement_reason="Secondary取得不能または空(従来どおり再生成/fallback/STOPへ戻す)")
        return info
    # 推奨5: PASSはEXACT/NORMALIZEDのみ=Resolver(LLM)で判定が変わらないため呼ばない
    cls_sec = javal.classify_ja_asr_match(canonical_text, text, expected_readings=expected_readings,
                                          allow_reading_resolver=False)
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


# ============================================================
# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_04: JA統一judge adapter
# ============================================================
# evaluate_attempt_ja_with_cascade_detail は**署名・戻り値dictのキー・呼出元**を維持したまま、内部を統一判定
# (er078_asr_unified_judge_01.unified_judge)へ委譲するadapterに置換された(DESIGN_01 §4-1/§4-3/§4-9、DESIGN_02_ADDENDUM_01 §1/§4/§6)。
#   [Primary P-chain = 既存] javal.classify_ja_asr_match(+Variant層D-2) -> [本委任の追加層] 数値の値等価(三十人=30人等、値ガードEQUAL
#       かつ数値表記を値トークンへ置換した残りが一致のときだけ。DESIGN_01 §5-2) -> 統一judge。
#   Primary PASS -> 最終ANDゲート(値DIFF/否定差。HOMOPHONE_MATCH_NUMBER_EXCEPTION・TIER1_*は再否定しない。READING_MATCHは最終ANDゲートを適用(OPEN-517))。
#   Primary NG   -> P1 保護差(値DIFF・否定差・既存の per-span 否定/数字不一致・fugashi否定マーカー差) -> NG_PROTECTED[Secondary不呼出]
#                   P2 除外表(length NG / C2同形異音 / 登録読み辞書不一致[A7=登録読み保護] / [U1: U1_KEEP_C1_SIMILARITY_EXCLUSIONS=False(解放実装済み、既定は暫定True)のときA5類似度<0.4・A6 C1固有名詞差は除外しない]) -> NG_EXCLUDED[Secondary不呼出]
#                   P3 それ以外 -> Azure Secondary 1回(SecondaryCache共有: 同一wav+engine+lang+phrase_hashで重複呼出なし)。
#                   Secondary許容集合 = EXACT/NORMALIZED(SCG承認済み集合=JAは10/11承認の2ラベル、DESIGN_01 §4-3c)
#                                     + ORTHOGRAPHIC_VARIANT_CONFIRMED(Primary#1+Secondary#1の2エンジン確認、追補§6 OF-AUW-08)。
#                   PASS -> PASS_WITH_WARNING(SECONDARY_CONFIRMED、自動採用+事後試聴リスト)。障害 -> NG_SECONDARY_UNAVAILABLE(PASS不可)。
# 廃止(DESIGN_01 §4-9): Primary#2(同一音声OpenAI再転写) / Secondary#2 / 4段尽き->stop_retrying+HR直行。stop_retrying=False固定、
#   human_review_required=Trueになるのは attempt_ctx.is_last_slot かつNGのときだけ(JA leafが最終slotを伝えない間はFalse。最終STOPPEDは
#   従来どおりleaf側のHR Lock経路 record_outcome)。
# 後方互換: cascade_enabled=False は従来どおり classify_ja_asr_match の結果そのまま(統一judgeを通らない)。
# SCG費用式(SCG_AZURE_USD_PER_HOUR/SCG_JPY_PER_USD)・SCG_MIN_SIMILARITY・SCG_FINAL_STATUS・JA_SCG_ENABLED緊急停止は不変。
import hashlib as _hashlib
import unicodedata as _ud

import er078_asr_unified_judge_01 as unified_judge_mod
import er078_asr_value_guard_01 as value_guard_mod

NUMERIC_VALUE_EQUIVALENT_MATCH = "NUMERIC_VALUE_EQUIVALENT_MATCH"
# Primary PASSのうち「読み一致」を根拠にした equivalence_basis="READING_MATCH"。2026-10-25 OPEN-517: 最終ANDゲートの再否定しない集合(APPROVED_EQUIVALENCE_BASES)から除外し、値DIFF/否定差の最終ゲートを受ける。
_READING_MATCH_CLASSIFICATIONS = ("PHONETIC_MATCH", "READING_RESOLVED_MATCH")
_COST_GUARD_MAX_USD_PER_SEGMENT_FALLBACK = 0.05  # er006_secondary_asr_01.COST_GUARD_MAX_USD_PER_SEGMENT と同値(取得できない場合のみ)


def _ja_wav_sha256(path: Optional[str]) -> Optional[str]:
    try:
        if path and os.path.isfile(path):
            h = _hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest()
    except OSError:
        pass
    return None


def _shared_run_cache_and_state():
    """EN adapterと共有するrun単位のSecondaryCache/RunState(begin_secondary_run()を呼んだ場合のみ非None。runner導入は委任_05/06)。"""
    try:
        import er006_secondary_asr_01 as _en
        return _en._RUN_CACHE, _en._RUN_STATE
    except Exception:  # noqa: BLE001
        return None, None


def _cost_guard_max_usd() -> float:
    try:
        import er006_secondary_asr_01 as _en
        return float(_en.COST_GUARD_MAX_USD_PER_SEGMENT)
    except Exception:  # noqa: BLE001
        return _COST_GUARD_MAX_USD_PER_SEGMENT_FALLBACK


def _scg_c1_reason(cls: "javal.ClassificationResultJA") -> Optional[str]:
    """C1固有名詞差(reading_dictionary_mismatch・entity_like・Latin語)に該当する理由。該当なしはNone。U1_KEEP_C1_SIMILARITY_EXCLUSIONS=FalseのときA6は無効。"""
    for d in (cls.protected.content_diffs or []):
        if d.get("reading_dictionary_mismatch"):
            return f"reading_dictionary_mismatch:{d.get('reading_dictionary_token')}"
        if d.get("entity_like"):
            return f"entity_like_diff:{d.get('canonical')}->{d.get('asr')}"
        if _has_latin(d.get("canonical", "")):
            return f"latin_in_canonical_diff:{d.get('canonical')}"
    return None


NO_SPEECH_SENTINEL = "[NO_SPEECH]"  # Azure正常完了の空転写を表すsentinel(数値・否定を含まない固定文字列)


def _scg_reading_dict_reason(cls: "javal.ClassificationResultJA") -> Optional[str]:
    """A7(登録読み保護、委任_10 R1/U1R-01): Primaryが登録読み辞書expected_readingsとの不一致を具体的に示した場合の理由。なければNone。
    Secondaryの表層EXACT/NORMALIZED一致は読みの正しさを証明しないため、U1解放後もSecondaryへ回さない(2026-10-11安全条件)。"""
    for d in (cls.protected.content_diffs or []):
        if d.get("reading_dictionary_mismatch"):
            return f"reading_dictionary_mismatch:{d.get('reading_dictionary_token')}"
    return None


def _scg_c2_candidate(cls: "javal.ClassificationResultJA") -> bool:
    return any(_scg_heterophone_candidate(d) for d in (cls.protected.content_diffs or []))


def _has_negation_ja_text(text: str) -> bool:
    import er003_audio_tts_asr_safety as _safety
    return bool(_safety._has_negation_ja(text or ""))


def _ja_value_form(text: str) -> Optional[str]:
    """数値atom(数値+助数詞/分数)を『値+単位』の表層非依存トークンへ置換した文字列(NFKC後)。数値atomが無ければNone。"""
    t = _ud.normalize("NFKC", text or "")
    atoms = [a for a in value_guard_mod.extract_atoms_ja(t) if a.kind in ("num", "frac")]
    if not atoms:
        return None
    out, pos = [], 0
    for a in atoms:
        if a.start < pos:
            return None
        out.append(t[pos:a.start])
        out.append(f"【値{a.kind}:{a.value}:{a.unit}】")
        pos = a.end
    out.append(t[pos:])
    return "".join(out)


def _numeric_value_equivalence(canonical_text: str, asr_text: Optional[str], cls: "javal.ClassificationResultJA"):
    """DESIGN_01 §5-2: 表記ではなく値と単位で比較(三十人=30人、百円=100円 等)。
    条件(全て必須): Primaryが数字不一致でTRUE_CONTENT_MISMATCH、否定不一致なし、値ガードがEQUAL(DIFF/AMBIGUOUS/UNKNOWNは対象外)、
    かつ数値表記を値トークンへ置換した両文が(normalize_ja後)完全一致。残りに1文字でも差があれば対象外(既存判定のまま)。"""
    if asr_text is None or cls.classification != "TRUE_CONTENT_MISMATCH":
        return None
    if not cls.protected.number_mismatches or cls.protected.negation_mismatches:
        return None
    vg = value_guard_mod.value_guard(canonical_text, asr_text, "ja")
    if vg.kind != value_guard_mod.EQUAL:
        return None
    cf, af = _ja_value_form(canonical_text), _ja_value_form(asr_text)
    if cf is None or af is None or javal.normalize_ja(cf) != javal.normalize_ja(af):
        return None
    if _has_negation_ja_text(cf) != _has_negation_ja_text(af):
        return None
    return javal.ClassificationResultJA(
        NUMERIC_VALUE_EQUIVALENT_MATCH, cls.similarity_ratio, javal.ProtectedCheckResultJA(passed=True),
        should_pass=True, should_retry=False,
        reason="数値の値と単位が同値(表記差のみ)で、数値以外の部分は完全一致(値ガードEQUAL)")


def evaluate_attempt_ja_with_cascade_detail(
    canonical_text: str, primary_asr_text: Optional[str], wav_path: str,
    cascade_enabled: bool = FEATURE_FLAG_JA_PRIMARY_OPENAI,
    # NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b: 既定None(後方互換)。辞書登録トークンの確定読み(小文字キー、カタカナ値)。
    expected_readings: dict | None = None,
    # OPEN-258 SCG 推奨6: 呼出元で長さ超過(length_ok=False)なら、Azureを無駄に呼ばない。既定True=後方互換。
    # ただし AUW 委任_13(A3是正)以降: attempt_ctx["max_len"]を渡す呼出元では、Primary転写のlength NGでもSecondaryへ回し
    # (Secondary受理時は採用転写[Secondary]の長さで再評価)、最終ANDは呼出元が`unified_judge.final_length_ok`で行う。
    # max_len未指定の呼出元は従来どおり(length_ok=FalseはA3としてSecondary不呼出)。
    length_ok: bool = True,
    # AUW 委任_04(既定None=slot1/script v0/最終slotでない): 統一judgeのattempt文脈。
    # dict: slot / script_version('v0'|'v1') / is_last_slot / segment_key / run_state / cache。
    attempt_ctx: Optional[dict] = None,
) -> dict:
    """統一ASR判定のJA adapter(AUW 委任_04)。署名の既存引数・戻り値dictの既存キーは従来どおり(additiveで`asr_judgement`/
    `cost_guard_triggered`を追加)。cascade_enabled=Falseなら従来のclassify_ja_asr_matchの結果をそのまま返す。"""
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
    if not cascade_enabled:
        return result  # 後方互換: 統一judgeを通らない(従来のclassify結果そのまま)

    actx = dict(attempt_ctx or {})
    result["stop_retrying"] = False  # DESIGN_01 §4-2/§4-9: 同一音声のASR再試行/4段尽きHR直行は廃止(再生成は通算上限が担保)
    result["cost_guard_triggered"] = False
    is_tcm = cls.classification == "TRUE_CONTENT_MISMATCH"

    # ---- Primary側の追加層: 数値の値等価 ----
    eq_cls = None if cls.should_pass else _numeric_value_equivalence(canonical_text, primary_asr_text, cls)
    if eq_cls is not None:
        cls = eq_cls
        is_tcm = False
        result.update(verified=True, classification=cls, final_status=cls.classification)
        steps[0]["classification"] = cls.classification
        steps[0]["numeric_value_equivalence"] = True

    primary_passed = bool(cls.should_pass)
    # ---- 除外表/保護差のsignals(従来のSCG除外条件と同一判定。TRUE_CONTENT_MISMATCH時のみ=従来のSCG適用範囲) ----
    signals: dict = {}
    if is_tcm and primary_asr_text is not None:
        signals["similarity"] = cls.similarity_ratio
        c1 = _scg_c1_reason(cls)
        if c1:
            signals["c1_proper_noun_diff"] = c1  # A6(U1_KEEP_C1_SIMILARITY_EXCLUSIONS=True時のみ有効)
        rd = _scg_reading_dict_reason(cls)
        if rd:
            signals["reading_dictionary_mismatch"] = rd  # A7(登録読み保護): U1解放後も事前除外
        if _scg_c2_candidate(cls):
            signals["c2_homophone_candidate"] = True
        pd = None
        if cls.protected.negation_mismatches:
            pd = f"negation_mismatch:{cls.protected.negation_mismatches}"
        else:
            neg = _scg_negation_marker_diff(canonical_text, primary_asr_text)
            if neg:
                pd = f"negation_marker_diff:{neg}"
        if pd is None and cls.protected.number_mismatches:
            vg0 = value_guard_mod.value_guard(canonical_text, primary_asr_text, "ja")
            if vg0.kind in (value_guard_mod.NO_VALUES, value_guard_mod.UNKNOWN):
                # 値ガードが結論を出せない(UNKNOWN/NO_VALUES)場合は既存protected_checkへ委譲=従来どおり数字不一致は保護差
                pd = f"number_mismatch:{cls.protected.number_mismatches}"
        if pd:
            signals["protected_diff"] = pd
    basis = "READING_MATCH" if (primary_passed and cls.classification in _READING_MATCH_CLASSIFICATIONS) else None
    primary = unified_judge_mod.PrimaryResult(
        passed=primary_passed, text=primary_asr_text, label=cls.classification, equivalence_basis=basis,
        warning_labels=(), signals=signals)

    sha = _ja_wav_sha256(wav_path)
    run_cache, run_state = _shared_run_cache_and_state()
    cache = actx.get("cache") or (run_cache if (run_cache is not None and sha) else unified_judge_mod.SecondaryCache())
    ctx = unified_judge_mod.AttemptCtx(
        canonical_text=canonical_text, wav_path=wav_path, wav_sha256=sha or f"nosha:{id(result)}",
        audio_seconds=_wav_duration_seconds(wav_path), segment_key=str(actx.get("segment_key", "")),
        script_version=actx.get("script_version", "v0"), slot=int(actx.get("slot", 1)),
        is_last_slot=bool(actx.get("is_last_slot", False)), length_ok=bool(length_ok),
        max_len=actx.get("max_len"),  # AUW 委任_13(A3R-01/03): 呼出元のmax_len。None=従来挙動(安全ラッチ)
        force_secondary=False, engine="azure", phrase_list_hash="",
        cache=cache, run_state=actx.get("run_state") or run_state)

    state = {"cost_guard": False, "wall_seconds": None, "flag_off": False}
    captured: dict = {}
    primary_orth_ok = (not primary_passed and cls.classification == "ASR_VALIDATION_UNCERTAIN"
                       and _orthographic_reading_confirmed(cls))

    def _secondary_fn(_ctx):
        if is_tcm and not _scg_enabled():
            state["flag_off"] = True  # 緊急停止(JA_SCG_ENABLED=0/FEATURE_FLAG_JA_SCG_ENABLED=False): Azureを呼ばない
            return unified_judge_mod.SecondaryOutcome(None, error="scg_disabled_by_flag")
        dur = _wav_duration_seconds(wav_path)
        if dur is not None and (dur / 3600.0 * unified_judge_mod.AZURE_USD_PER_HOUR) > _cost_guard_max_usd():
            state["cost_guard"] = True  # COST_GUARD($0.05/segment)を実費(秒数)で等価適用: 超過ならSecondaryを呼ばずfail-closed
            return unified_judge_mod.SecondaryOutcome(None, error="cost_guard_exceeded")
        t0 = time.time()
        text, err = _azure_stt_strict(wav_path, language="ja-JP", timeout_seconds=SCG_AZURE_TIMEOUT_SECONDS)
        state["wall_seconds"] = round(time.time() - t0, 2)
        if err is None and text is not None and not str(text).strip():
            # 委任_10 R2(U1R-02): Azureが「エラーなしで完了したが無音/雑音で空転写」は障害ではなく「原稿を支持しない」結果。
            # NG_SECONDARY_UNAVAILABLE(連続失敗カウント・circuit breaker・最終slotの技術STOP)へ流さず、NG_BOTHへ回す。JA限定(ENは不変)。
            state["no_speech"] = True
            return unified_judge_mod.SecondaryOutcome(NO_SPEECH_SENTINEL, accepted=False, label="NO_SPEECH")
        return unified_judge_mod.SecondaryOutcome(text, error=err)

    def _secondary_accept(canon, stext):
        cls_s = javal.classify_ja_asr_match(canon, stext, expected_readings=expected_readings, allow_reading_resolver=False)
        captured["cls_s"] = cls_s
        if cls_s.classification in SCG_PASS_CLASSIFICATIONS:
            return True, cls_s.classification
        cls_s2 = _apply_variant_layer_voicing_upgrade(canon, stext, cls_s)
        if primary_orth_ok and _orthographic_reading_confirmed(cls_s2):
            # ER-008 Part G/H: 異なる2エンジン(OpenAI Primary#1 / Azure Secondary#1)がともに「辞書上の正当な読み候補にcanonical読みを
            # 含む表記差のみ」に到達した場合のみ(単一エンジンの繰り返しでは確認しない)。
            captured["orth"] = True
            captured["cls_s"] = cls_s2
            return True, ORTHOGRAPHIC_VARIANT_CONFIRMED
        return False, cls_s.classification

    jr = unified_judge_mod.unified_judge(ctx, primary, _secondary_fn, lang="ja", role=None,
                                         secondary_accept_fn=_secondary_accept)
    audit = jr.audit_record
    sec = audit.get("secondary") or {}
    secondary_ran = bool(sec.get("called") or sec.get("cached") or sec.get("error"))
    cls_s = captured.get("cls_s")
    scg_info = None
    if is_tcm:
        # 除外理由は従来のSCG表記(_scg_exclusion_reason / length_not_ok)を診断用に維持し、統一judgeの理由は別キーで併記する。
        legacy_reason = _scg_exclusion_reason(cls, canonical_text, primary_asr_text,
                                              u1_released=not unified_judge_mod.U1_KEEP_C1_SIMILARITY_EXCLUSIONS)
        if legacy_reason is None and not length_ok and not unified_judge_mod._a3_reeval_active(ctx):
            # 委任_13(A3R-05): この診断文はmax_len未指定の呼出元(安全ラッチ=旧挙動)だけに出る。max_len指定時はjudgeの実理由(jr.reason_code)を使う。
            legacy_reason = "length_not_ok(呼出元の長さ判定が不合格、SCG PASSでも不合格になるため不実行。max_len未指定の旧挙動)"
        scg_info = {"scg_applied": False, "scg_result": "NOT_APPLIED", "exclusion_reason": legacy_reason or jr.reason_code,
                    "primary_text": primary_asr_text, "unified_judge_state": jr.state, "unified_reason_code": jr.reason_code}
        if secondary_ran:
            scg_result = ("DISABLED_BY_FLAG" if state["flag_off"] else
                          "UNAVAILABLE" if jr.state == unified_judge_mod.NG_SECONDARY_UNAVAILABLE else
                          "PASS" if jr.verified else "NG")
            audio_seconds = ctx.audio_seconds
            est_jpy = unified_judge_mod.est_jpy_for_seconds(audio_seconds)
            scg_info.update(
                scg_applied=not state["flag_off"], scg_result=scg_result, exclusion_reason=None,
                **_scg_service_info(), audio_seconds=round(audio_seconds, 3) if audio_seconds is not None else None,
                est_cost_jpy=est_jpy, wall_seconds=state["wall_seconds"], timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
                secondary_transcript=sec.get("text"), error=sec.get("error"),
                secondary_classification=cls_s.classification if cls_s else None,
                judgement_reason=f"統一judge({jr.reason_code}): Secondary(Azure) label={sec.get('label')!r}")
        scg_info["scg_info_source"] = "AUW_unified_judge"
        result["scg_applied"] = scg_info["scg_applied"]
        result["scg_result"] = scg_info["scg_result"]
        result["scg_info"] = scg_info
    if secondary_ran:
        result["cascade_invoked"] = True
        step = {"step": "scg_secondary" if is_tcm else "secondary_1", "provider": "azure", "text": sec.get("text"),
                "classification": (cls_s.classification if cls_s else ("TTS_FAILURE" if not sec.get("text") else sec.get("label"))),
                "cached": bool(sec.get("cached")), "unified_judge_state": jr.state}
        if scg_info:
            step["scg_result"] = scg_info["scg_result"]
        steps.append(step)
    if state["cost_guard"]:
        result["cost_guard_triggered"] = True

    result["verified"] = bool(jr.verified)
    if jr.verified:
        if not primary_passed:  # Secondary独立確認で採用(PASS_WITH_WARNING)
            if captured.get("orth"):
                result.update(final_status=ORTHOGRAPHIC_VARIANT_CONFIRMED, classification=captured["cls_s"])
            elif is_tcm:
                scg_cls = javal.ClassificationResultJA(
                    SCG_FINAL_STATUS, cls.similarity_ratio, cls.protected, should_pass=True, should_retry=False,
                    reason=f"Primary(OpenAI)はTRUE_CONTENT_MISMATCHだが、Secondary(Azure)が原稿と一致: {jr.reason_code}")
                scg_cls.scg_info = scg_info
                result.update(final_status=SCG_FINAL_STATUS, classification=scg_cls)
            elif cls_s is not None:
                result.update(final_status=cls_s.classification, classification=cls_s)
        else:
            result.update(final_status=cls.classification, classification=cls)
    else:
        result.update(final_status=cls.classification, classification=cls)
        if scg_info is not None:
            cls.scg_info = scg_info  # NG/不実行/UNAVAILABLE: 従来どおり再生成へ。証跡だけ付与(既存キー不変)
        if audit.get("technical_stop") or jr.secondary_unavailable:
            result["technical_stop"] = audit.get("technical_stop")
        # 委任_06c(OF-AUW-C-06、ADDENDUM §4): NG理由がSecondary障害のみなら技術STOP(HR Lock/queueへ投入しない)。ENと同一規約。
        _tech_only = jr.state == unified_judge_mod.NG_SECONDARY_UNAVAILABLE
        if _tech_only:
            result["human_review_required"] = False
            result["technical_stop"] = audit.get("technical_stop") or {"type": "SECONDARY_UNAVAILABLE", "restartable": True,
                                                                        "approval_required": False}
            result["technical_stop_status"] = "TECHNICAL_STOP_SECONDARY_UNAVAILABLE"
        if bool(actx.get("is_last_slot", False)) and not _tech_only:
            result["human_review_required"] = True
    audit["adapter"] = {"layers": (["numeric_value_equivalence"] if eq_cls is not None else []),
                        "azure_real_calls": 1 if sec.get("called") else 0, "cost_guard_triggered": state["cost_guard"],
                        "language": "ja-JP", "asr_text_present": primary_asr_text is not None,
                        "cache": {"calls": cache.calls, "hits": cache.hits}}
    result["asr_judgement"] = audit
    return result


def evaluate_attempt_ja_with_cascade(
    canonical_text: str, primary_asr_text: Optional[str], wav_path: str,
    cascade_enabled: bool = FEATURE_FLAG_JA_PRIMARY_OPENAI,
    # NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 3b: 既定None(後方互換)。
    expected_readings: dict | None = None,
    length_ok: bool = True,
    # AUW 委任_04(additive、既定None): 統一judgeのattempt文脈 / audit記録用の追加出力(detailをupdate)。
    attempt_ctx: Optional[dict] = None,
    detail_out: Optional[dict] = None,
) -> tuple[bool, bool, "javal.ClassificationResultJA"]:
    """Production retry loop向けのdrop-in互換ラッパー(English版
    evaluate_attempt_with_cascade()と同じ形の戻り値)。detail_out(既定None)を渡すと、
    detailの戻り値全体(asr_judgement等)でその場でupdate()する(戻り値tupleの形は変えない)。"""
    detail = evaluate_attempt_ja_with_cascade_detail(
        canonical_text, primary_asr_text, wav_path, cascade_enabled=cascade_enabled,
        expected_readings=expected_readings, length_ok=length_ok, attempt_ctx=attempt_ctx)
    if detail["human_review_required"]:
        _log_human_review(detail)
    if detail_out is not None:
        detail_out.update(detail)
    return detail["verified"], detail["stop_retrying"], detail["classification"]
