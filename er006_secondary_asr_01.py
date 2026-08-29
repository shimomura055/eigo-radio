# ============================================================
# er006_secondary_asr_01.py
# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01: Secondary ASR + Phrase List
# ============================================================
# Primary ASR(OpenAI gpt-4o-mini-transcribe、既存のer006_asr_provider_
# routing_01.py)がFAIL/UNCERTAINを返したsegmentだけを対象に、Azure
# Speech STTをSecondaryとして呼ぶ。Azure呼び出し時、Pronunciation
# Ledgerに登録済みの固有名詞をPhrase Listとして渡せるようにする
# (canonical spellingをヒントとして渡すだけで、それ以外は変更しない)。
#
# 既存の本番Azure呼び出し(er003_b1_p4_audio.get_full_text_via_azure_
# stt_continuous)は変更しない。本モジュールはPhrase List対応の新規
# 関数を追加するのみ(最小Blast Radius)。

from __future__ import annotations

import json
import os
import time
import wave
from typing import Optional

import requests

import er005_cost_logger as cl


def _wav_duration_seconds(wav_path: str) -> Optional[float]:
    try:
        with wave.open(wav_path, "rb") as wf:
            return round(wf.getnframes() / float(wf.getframerate()), 3)
    except Exception:
        return None


def get_full_text_via_azure_stt_with_phrase_list(
    wav_path: str, language: str = "en-US", phrases: Optional[list[str]] = None,
    timeout_seconds: float = 90.0,
) -> tuple[str | None, str | None]:
    """er003_b1_p4_audio.get_full_text_via_azure_stt_continuous()と同じ
    連続認識方式に、Azure PhraseListGrammarを追加したもの。phrasesに
    Pronunciation LedgerのcanonicaL spellingを渡すと、Azureがその語を
    認識しやすくなる(重み付けのみ、認識結果を強制はしない)。"""
    if not os.path.exists(wav_path):
        return None, f"音声ファイルが見つかりません: {wav_path}"

    try:
        from dotenv import load_dotenv
        import azure.cognitiveservices.speech as speechsdk
    except ImportError as exc:
        return None, f"Azure Speech SDKの読み込みに失敗しました: {exc}"

    load_dotenv()
    speech_key = os.getenv("SPEECH_KEY")
    speech_region = os.getenv("SPEECH_REGION")
    if not speech_key or not speech_region:
        return None, "SPEECH_KEY/SPEECH_REGIONが.envに設定されていません"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = language
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    if phrases:
        phrase_list = speechsdk.PhraseListGrammar.from_recognizer(recognizer)
        for phrase in phrases:
            phrase_list.addPhrase(phrase)

    segments = []
    done = {"flag": False, "reason": None}

    def on_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            segments.append(evt.result.text)

    def on_stopped(evt):
        done["flag"] = True
        done["reason"] = str(evt)

    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_stopped)
    recognizer.canceled.connect(on_stopped)

    t0 = time.time()
    recognizer.start_continuous_recognition()
    start = time.time()
    while not done["flag"] and (time.time() - start) < timeout_seconds:
        time.sleep(0.5)
    recognizer.stop_continuous_recognition()
    elapsed = round(time.time() - t0, 3)
    duration = _wav_duration_seconds(wav_path)

    if not done["flag"]:
        cl.record({
            "provider": "azure", "api": "get_full_text_via_azure_stt_with_phrase_list",
            "model_id": "azure-speech-stt", "locale": language, "attempt_number": 1,
            "success": False, "elapsed_seconds": elapsed, "usage_source": "LOCAL_WAV_HEADER_EXACT",
            "audio_duration_submitted_seconds": duration, "phrase_list_size": len(phrases or []),
        })
        return None, f"連続認識がtimeout({timeout_seconds}秒)内に完了しませんでした"

    cl.record({
        "provider": "azure", "api": "get_full_text_via_azure_stt_with_phrase_list",
        "model_id": "azure-speech-stt", "locale": language, "attempt_number": 1,
        "success": True, "elapsed_seconds": elapsed, "usage_source": "LOCAL_WAV_HEADER_EXACT",
        "audio_duration_submitted_seconds": duration, "phrase_list_size": len(phrases or []),
    })
    return "".join(segments), None


# ============================================================
# ER-006-AUDIO-RETRY-CASCADE-PROD-01: Production Cascade
# Gemini TTS(1回) -> Primary#1 -> Primary#2 -> Secondary#1(+Phrase List)
# -> Secondary#2(+Phrase List) -> Human Review
# 同一音声に対して複数回ASRだけをやり直す(TTSは再生成しない)。
# ============================================================
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_pronunciation_research_01 as pronun_research
import er008_asr_variant_hardening_15_homophone_en as homophone_en

FEATURE_FLAG_SECONDARY_ASR_ENABLED = True  # Production既定でON(ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01。
                                            # 旧OFF状態はOPEN-48で「追加検証待ち」としていたが、
                                            # 同タスクでB1/A2 Sweenyケースとも実音声でCascadeが
                                            # 正しく動作することを確認済みのため有効化した

# SSOT: Cascadeの試行回数上限・Phrase List設定(タスク仕様§11-12)
CASCADE_CONFIG = {
    "max_primary_attempts": 2,
    "max_secondary_attempts": 2,
    "phrase_list_weight": None,  # AzureのPhraseListGrammarはper-phrase重み設定APIを
                                  # 現行SDKでは公開していないため、既定(均等)を使う。
                                  # 将来SDKが対応した場合はここへ重み値を設定する。
}

# Cost Guard(タスク仕様§13): 1 segmentあたりの累積コストがこれを超えたら
# Fail-closedでCascadeを打ち切り、Human Reviewへ送る(異常な費用膨張防止)。
COST_GUARD_MAX_USD_PER_SEGMENT = 0.05


def is_entity_like_mismatch(result: "val.ClassificationResult") -> bool:
    """classify_asr_matchの結果が、固有名詞らしき語のみの音訳差による
    ASR_VALIDATION_UNCERTAINかどうかを判定する。数字・否定・通常の内容語
    差は対象外(それらはprotected_checkで既にTRUE_CONTENT_MISMATCHになる
    ため、ここへは到達しない)。"""
    if result.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = result.protected.content_word_diffs
    return bool(diffs) and all(d["entity_like"] for d in diffs)


def is_homophone_candidate_mismatch(result: "val.ClassificationResult") -> bool:
    """ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part I/J:
    classify_asr_matchの結果が、CMU Pronouncing Dictionary上で発音が
    完全一致する単一語の置換差(homophone_candidate)のみによる
    ASR_VALIDATION_UNCERTAINかどうかを判定する(is_entity_like_mismatch
    の同音異義語版)。"""
    if result.classification != "ASR_VALIDATION_UNCERTAIN":
        return False
    diffs = result.protected.content_word_diffs
    return bool(diffs) and all(d["homophone_candidate"] for d in diffs)


HOMOPHONE_EQUIVALENT = "HOMOPHONE_EQUIVALENT"
PROPER_NOUN_ENTITY_ARPABET_CONFIRMED = "PROPER_NOUN_ENTITY_ARPABET_CONFIRMED"

# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 D-2': Stage 2(Pronunciation
# Ledger lookup/research)専用のentity_type。記事・文脈をまたいで同一
# entityが確実にcache hitするよう、この経路では常にsource_context=""
# (既定値)・entity_typeはこの固定値を使う(記事ごとの分類ゆれで
# cache keyが割れるのを防ぐ)。
_UNRESOLVED_ENTITY_TYPE = "cascade_unresolved_entity"


def _resolve_unresolved_entity_for_review(canonical_span: str) -> dict | None:
    """D-2'(B): CMU辞書で安全に比較できない固有名詞spanについて、
    Pronunciation Ledgerをcache確認(記事横断で再利用)し、無ければ
    その場でresearch_pronunciations()を1回だけ呼び出して永続cacheする。

    **重要**: この関数が返す情報は、Human Reviewパッケージを充実させる
    ためだけに使う。IPA→ARPAbet変換等による自動PASSの根拠には一切
    使わない(D-2'参照。外国語由来の固有名詞をARPAbetへ強制変換すると
    音韻情報が失われ誤PASSのリスクがあるため)。lookup/research失敗時は
    Noneを返し、呼び出し側は追加のTTS呼び出しを一切行わずHuman Reviewへ
    進むこと(安全側)。"""
    key = pronun_ledger.LedgerKey(surface=canonical_span, entity_type=_UNRESOLVED_ENTITY_TYPE, source_context="")
    entry = pronun_ledger.lookup(key)
    if entry is not None:
        return entry
    try:
        research = pronun_research.research_pronunciations([{
            "surface": canonical_span, "entity_type": "unknown",
            "risk_reason": "ASR Cascade(Primary#1/#2, Secondary#1/#2)を尽くしても解決できなかった固有名詞",
        }])
    except requests.exceptions.RequestException:
        # ネットワーク層の失敗のみを「lookup利用不可」として静かに扱う
        # (安全側、TTS再生成はトリガーしない)。cost logger未初期化等の
        # 呼び出し元設定不備はここで揉み消さず、そのまま例外を伝播させる
        # (本番の各generate関数エントリポイントは既にcost loggerを
        # 初期化済みである前提。他のASR/TTS呼び出しと同じ扱い)。
        return None
    if research.get("status") != "OK" or not research.get("items"):
        return None
    item = dict(research["items"][0])
    item["sources"] = research.get("citations", [])
    pronun_ledger.upsert(key, item)
    return pronun_ledger.lookup(key)


HUMAN_REVIEW_LOG_PATH = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"


def _log_human_review(detail: dict) -> None:
    import er011_human_review_lock_01 as review_lock  # 遅延import(循環import回避)
    # ER-011-HUMAN-REVIEW-COST-GUARD-01 Part G: 同一segment・同一
    # canonical_textのqueue重複投入を防ぐ(重複していれば既存entryを
    # 再利用し、新規追記しない)。
    if review_lock.is_duplicate_queue_entry(HUMAN_REVIEW_LOG_PATH, detail["wav_path"], detail["canonical_text"]):
        return
    os.makedirs(os.path.dirname(HUMAN_REVIEW_LOG_PATH), exist_ok=True)
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "canonical_text": detail["canonical_text"],
        "wav_path": detail["wav_path"],
        "steps": detail["steps"],
        "cost_guard_triggered": detail["cost_guard_triggered"],
        "final_status": detail["final_status"],
        # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part K: 固有名詞
        # (CMU辞書に無い外国由来名等)でHuman Reviewへ落ちた場合、
        # Pronunciation Ledgerから得られたcanonical_spelling/expected_
        # pronunciation_ipa/pronunciation_hint/confidence/sources等を
        # そのまま添付する(「正しく聞こえますか?」だけを提示しない)。
        "pronunciation_lookups": detail.get("pronunciation_lookups", {}),
    }
    with open(HUMAN_REVIEW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def evaluate_attempt_with_cascade(
    canonical_text: str, asr_text: Optional[str], prior_results: list,
    wav_path: str, language: str = "en-US", ledger_phrases: Optional[list[str]] = None,
    max_same_signature: int = 3, cascade_enabled: bool = FEATURE_FLAG_SECONDARY_ASR_ENABLED,
    force_secondary: bool = False,
) -> tuple[bool, bool, "val.ClassificationResult"]:
    """Production retry loop向けのdrop-in互換ラッパー。val.evaluate_attempt()
    と同じ(verified, stop_retrying, classification)のタプルを返す
    (既存呼び出し元のコードをほぼ変更せずに差し替えられる)。
    Cascadeが起動してHuman Review行きになった場合、詳細(§14の一覧項目)を
    HUMAN_REVIEW_LOG_PATHへ追記する。

    force_secondary(ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-
    COMPRESSION-AB-04 Part Cで追加、既定False)は、fallback(minimal
    instruction)経由の音声にのみ使う想定の引数。Trueの場合、Primaryが
    PASS(verified=True)であっても、Secondary ASRで1回だけ追加確認する
    (No.7 point_one_headingで実際に起きた「Primaryは正しく書き起こし
    たが実音声はSecondaryだと全く別物に聞こえる」誤PASSを防ぐため)。
    standard path(force_secondary=False)の挙動・追加コストは一切変わ
    らない。"""
    detail = evaluate_attempt_with_cascade_detail(
        canonical_text, asr_text, prior_results, wav_path, language=language,
        ledger_phrases=ledger_phrases, max_same_signature=max_same_signature,
        cascade_enabled=cascade_enabled, force_secondary=force_secondary)
    if detail["human_review_required"]:
        _log_human_review(detail)
    return detail["verified"], detail["stop_retrying"], detail["classification"]


def _case_a_entity_pass(cls_step: "val.ClassificationResult") -> bool:
    """D-2'(A): このステップのASR結果が、entity_like差分の全構成語について
    CMU Pronouncing Dictionaryの代表発音同士で完全一致するか判定する
    (canonical綴りと直接比較するため、他ステップの結果は不要。1ステップ
    だけで判定できる)。entity_like差分が無い場合はFalse。"""
    entity_diffs = [d for d in cls_step.protected.content_word_diffs if d["entity_like"]]
    if not entity_diffs:
        return False
    for d in entity_diffs:
        match = homophone_en.entity_span_arpabet_match(d["canonical"], d["asr"])
        if not (match.resolved and match.matched):
            return False
    return True


def _step_alternate_pass(cls_step: "val.ClassificationResult") -> str | None:
    """should_pass以外の経路でこのステップをPASS扱いにできるか判定する。
    戻り値は採用したclassification名(PASS不可ならNone)。

    ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15での再設計:
      - homophone(wait/weight等): CMU辞書上の発音完全一致は、canonical
        綴りとASR綴りを直接比較する強い根拠のため、このステップ単独で
        判定してよい。
      - 固有名詞Case A(Kristie/Christy等): 同じくCMU辞書上の代表発音
        同士の完全一致で、canonical綴りと直接比較する強い根拠のため、
        このステップ単独で判定してよい。
      - 固有名詞Case B(CMU辞書に無い外国由来名、例: Tse)は、この関数
        では絶対にPASSさせない(D-2'参照。ASR結果同士の収束は自動PASSの
        根拠にしない)。Ledgerでの発音情報蓄積はHuman Reviewパッケージ
        (Part K)の充実のみに使う。
    """
    # entity_like(固有名詞らしき大文字始まりの語)とhomophone_candidateは
    # 独立に判定しているため、両方に該当する語(例: "Kristie"/"Christie"の
    # ように固有名詞かつCMU辞書上も完全一致)もありうる。その場合は、より
    # 情報量の多い固有名詞側のラベルを優先する(Human Reviewパッケージで
    # 「名前として確認済み」と分かるようにするため)。
    if is_entity_like_mismatch(cls_step) and _case_a_entity_pass(cls_step):
        return PROPER_NOUN_ENTITY_ARPABET_CONFIRMED
    if is_homophone_candidate_mismatch(cls_step):
        return HOMOPHONE_EQUIVALENT
    return None


def _unresolved_entity_spans(cls_step: "val.ClassificationResult") -> list[str]:
    """entity_like差分のうち、Case A(CMU辞書直接比較)で解決できなかった
    canonical spanの一覧を返す(Case Bのlookup対象、Part K package用)。"""
    spans = []
    for d in cls_step.protected.content_word_diffs:
        if not d["entity_like"]:
            continue
        match = homophone_en.entity_span_arpabet_match(d["canonical"], d["asr"])
        if not (match.resolved and match.matched):
            spans.append(d["canonical"])
    return spans


def evaluate_attempt_with_cascade_detail(
    canonical_text: str, asr_text: Optional[str], prior_results: list,
    wav_path: str, language: str = "en-US", ledger_phrases: Optional[list[str]] = None,
    max_same_signature: int = 3, cascade_enabled: bool = FEATURE_FLAG_SECONDARY_ASR_ENABLED,
    force_secondary: bool = False,
) -> dict:
    """既存のval.evaluate_attempt()(Primary ASR 1回分の判定)をラップし、
    その結果が「固有名詞由来のASR_VALIDATION_UNCERTAIN」であれば、TTSを
    再生成せず同じ音声に対してCascade(Primary#2 -> Secondary#1 ->
    Secondary#2)を追加実行する。cascade_enabled=Falseなら既存のval.
    evaluate_attempt()と完全に同じ挙動(後方互換、Production既定)。

    force_secondary=Trueの場合、Primaryが最初からPASSしたケースでも
    (is_entity_like_mismatch判定を経由せず)Secondary ASRを1回だけ
    追加で呼び、両方が一致した場合のみ最終的にverified=Trueとする
    (Part C参照)。既存のcascade_enabled/entity-like判定によるルート
    (Primary不一致時の4-step cascade)には一切影響しない。

    戻り値のdictには、Human Review用に全stepのtranscriptを保持する
    (canonical_text/TTS audioパス/Primary#1-2/Secondary#1-2の書き起こし)。
    """
    verified, stop_retrying, cls = val.evaluate_attempt(
        canonical_text, asr_text, prior_results, max_same_signature=max_same_signature)

    steps = [{"step": "primary_1", "provider": "openai_asr", "text": asr_text,
              "classification": cls.classification}]
    cumulative_cost_usd = 0.0

    result = {
        "verified": verified, "stop_retrying": stop_retrying, "classification": cls,
        "cascade_invoked": False, "steps": steps, "final_status": cls.classification,
        "human_review_required": False, "canonical_text": canonical_text, "wav_path": wav_path,
        "cost_guard_triggered": False,
    }

    if verified and force_secondary:
        # ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04
        # Part C: fallback経由の音声はPrimaryがPASSしても無条件でSecondary
        # を1回追加実行し、両方が一致した場合のみ最終的にPASSとする。
        result["cascade_invoked"] = True
        text_s_forced, err_s_forced = get_full_text_via_azure_stt_with_phrase_list(
            wav_path, language=language, phrases=ledger_phrases)
        cls_s_forced = val.classify_asr_match(canonical_text, text_s_forced) if text_s_forced is not None else None
        steps.append({"step": "secondary_forced", "provider": "azure", "text": text_s_forced,
                       "classification": cls_s_forced.classification if cls_s_forced else "TTS_FAILURE",
                       "phrase_list_used": bool(ledger_phrases)})
        if cls_s_forced is not None and cls_s_forced.should_pass:
            # Primary/Secondaryが一致 -> 従来どおりPASS
            return result
        # SecondaryがPrimaryのPASS判定に同意しない -> 無条件PASSさせない
        result["verified"] = False
        result["stop_retrying"] = False
        result["human_review_required"] = True
        result["final_status"] = cls_s_forced.classification if cls_s_forced else "TTS_FAILURE"
        result["classification"] = cls_s_forced if cls_s_forced else cls
        return result

    cascade_eligible = is_entity_like_mismatch(cls) or is_homophone_candidate_mismatch(cls)
    if verified or not cascade_enabled or not cascade_eligible:
        # 固有名詞由来・homophone由来でない不一致(数字・否定・通常内容語の
        # 差等)は、既存のblind TTS retryへ委ねる(Cascadeの対象外、§8の
        # 限定条件を守る)。
        return result

    # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15: Primary#1の時点で既に
    # homophone/固有名詞Case Aが判定できる場合、追加のASR呼び出し無しで
    # PASSする(canonical綴りとASR綴りをCMU辞書経由で直接比較する強い
    # 根拠のため、複数ステップの収束を待つ必要が無い。コストゼロ)。
    immediate_label = _step_alternate_pass(cls)
    if immediate_label:
        result["verified"] = True
        result["stop_retrying"] = False
        result["final_status"] = immediate_label
        return result

    result["cascade_invoked"] = True

    # --- Primary #2(同じ音声、TTSは再生成しない) ---
    text_p2, err_p2 = routing.transcribe(wav_path, language=language)
    cost_guess = 0.000002  # OpenAI mini ASRの概算単価(1呼び出しあたり数十秒の音声で1円未満)
    cumulative_cost_usd += cost_guess
    cls_p2 = val.classify_asr_match(canonical_text, text_p2) if text_p2 is not None else None
    steps.append({"step": "primary_2", "provider": "openai_asr", "text": text_p2,
                   "classification": cls_p2.classification if cls_p2 else "TTS_FAILURE"})
    if cls_p2 is not None and cls_p2.should_pass:
        result["verified"] = True
        result["stop_retrying"] = False
        result["final_status"] = cls_p2.classification
        result["classification"] = cls_p2
        return result
    if cls_p2 is not None:
        label = _step_alternate_pass(cls_p2)
        if label:
            result["verified"] = True
            result["stop_retrying"] = False
            result["final_status"] = label
            result["classification"] = cls_p2
            return result

    if cumulative_cost_usd > COST_GUARD_MAX_USD_PER_SEGMENT:
        result["cost_guard_triggered"] = True
        result["human_review_required"] = True
        result["final_status"] = "ASR_VALIDATION_UNCERTAIN"
        return result

    # --- Secondary #1(Azure + Phrase List) ---
    text_s1, err_s1 = get_full_text_via_azure_stt_with_phrase_list(
        wav_path, language=language, phrases=ledger_phrases)
    cumulative_cost_usd += 0.00001  # Azure概算単価(1秒あたり約$0.00028、数十秒想定)
    cls_s1 = val.classify_asr_match(canonical_text, text_s1) if text_s1 is not None else None
    steps.append({"step": "secondary_1", "provider": "azure", "text": text_s1,
                   "classification": cls_s1.classification if cls_s1 else "TTS_FAILURE",
                   "phrase_list_used": bool(ledger_phrases)})
    if cls_s1 is not None and cls_s1.should_pass:
        result["verified"] = True
        result["stop_retrying"] = False
        result["final_status"] = cls_s1.classification
        result["classification"] = cls_s1
        return result
    if cls_s1 is not None:
        label = _step_alternate_pass(cls_s1)
        if label:
            result["verified"] = True
            result["stop_retrying"] = False
            result["final_status"] = label
            result["classification"] = cls_s1
            return result

    if cumulative_cost_usd > COST_GUARD_MAX_USD_PER_SEGMENT:
        result["cost_guard_triggered"] = True
        result["human_review_required"] = True
        result["final_status"] = "ASR_VALIDATION_UNCERTAIN"
        return result

    # --- Secondary #2(Azure + Phrase List、同じ音声を再度) ---
    text_s2, err_s2 = get_full_text_via_azure_stt_with_phrase_list(
        wav_path, language=language, phrases=ledger_phrases)
    cumulative_cost_usd += 0.00001
    cls_s2 = val.classify_asr_match(canonical_text, text_s2) if text_s2 is not None else None
    steps.append({"step": "secondary_2", "provider": "azure", "text": text_s2,
                   "classification": cls_s2.classification if cls_s2 else "TTS_FAILURE",
                   "phrase_list_used": bool(ledger_phrases)})
    if cls_s2 is not None and cls_s2.should_pass:
        result["verified"] = True
        result["stop_retrying"] = False
        result["final_status"] = cls_s2.classification
        result["classification"] = cls_s2
        return result
    if cls_s2 is not None:
        label = _step_alternate_pass(cls_s2)
        if label:
            result["verified"] = True
            result["stop_retrying"] = False
            result["final_status"] = label
            result["classification"] = cls_s2
            return result

    # --- 4 step全て不一致 -> Human Review(TTSは再生成しない、§9の通り
    # 固有名詞だけの表記差ではretryしない) ---
    result["human_review_required"] = True
    result["stop_retrying"] = True
    result["final_status"] = "ASR_VALIDATION_UNCERTAIN"

    # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 D-2'(B): CMU辞書で解決
    # できなかったentity_like固有名詞spanについて、Human Reviewパッケージ
    # (Part K)を充実させるためだけにPronunciation Ledgerをlookup/research
    # する(自動PASSの根拠には使わない。lookup失敗時も追加のTTS/ASR呼び
    # 出しは一切発生しない)。is_entity_like_mismatch(cls)は最初のPrimary
    # #1時点の判定を使う(canonical_textは全stepで共通のため、spanの
    # 特定はPrimary#1の差分で十分)。
    if is_entity_like_mismatch(cls):
        unresolved_spans = _unresolved_entity_spans(cls)
        pronunciation_lookups = {}
        for span in unresolved_spans:
            info = _resolve_unresolved_entity_for_review(span)
            # ER-008-N8-FINAL-PRODUCTION-HARDENING-23: lookup/research失敗時に
            # spanをそのまま省略すると、Human Reviewパッケージにその固有名詞の
            # 発音情報が一切表示されない(「調べたが分からなかった」のか
            # 「調べていない」のか区別がつかない)。ユーザーの新運用ルール
            # (固有名詞のHuman Review依頼には必ずIPA/pronunciation guide/
            # source/confidenceを添付し、確定不能ならその旨を明記する)に
            # 従い、失敗時も明示的なunconfirmed markerを必ず残す。
            pronunciation_lookups[span] = info if info is not None else {
                "expected_pronunciation_ipa": "", "pronunciation_hint": "",
                "confidence": "unconfirmed",
                "ambiguity_note": (
                    "Pronunciation Ledger lookupおよびresearch_pronunciations()が"
                    "いずれも情報を返さなかった(ネットワーク不可またはresearch結果0件)。"
                    "IPA/pronunciation guideは確定できていません。"),
                "sources": [],
            }
        result["pronunciation_lookups"] = pronunciation_lookups
    return result
