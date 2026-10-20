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

import copy
import json
import os
import re
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


# ============================================================
# KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01
# ============================================================
# 「非ラテン文字主体」判定(KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-
# TRIAL-01_REPORT.md §2の判定式をそのまま移植、無変更)。適用範囲は
# 呼び出し元(evaluate_attempt_with_cascade/_detail)が明示的に
# enable_non_latin_cascade=Trueを渡した経路のみ(英語Key Phrase
# Component経路限定、他のASR経路[本文segment等]では既定Falseのため
# この判定自体が呼ばれない)。
_NON_LATIN_LATIN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")
_NON_LATIN_CJK_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿가-힣]")
NON_LATIN_DOMINANT_THRESHOLD = 0.5


def non_latin_dominance_info(text: Optional[str]) -> dict:
    """ASR出力中のラテン文字数とCJK/かな/ハングル文字数を数え、
    (CJK系文字数)/(ラテン文字数+CJK系文字数) >= NON_LATIN_DOMINANT_
    THRESHOLD(両方0ならFalse)を「非ラテン文字主体」と判定する。"""
    text = text or ""
    latin_n = len(_NON_LATIN_LATIN_RE.findall(text))
    cjk_n = len(_NON_LATIN_CJK_RE.findall(text))
    total = latin_n + cjk_n
    ratio = (cjk_n / total) if total > 0 else 0.0
    is_dominant = total > 0 and cjk_n > 0 and ratio >= NON_LATIN_DOMINANT_THRESHOLD
    return {"latin_chars": latin_n, "cjk_chars": cjk_n, "ratio_cjk": round(ratio, 3),
            "is_non_latin_dominant": is_dominant, "threshold": NON_LATIN_DOMINANT_THRESHOLD}


def is_non_latin_dominant_mismatch(asr_text: Optional[str]) -> bool:
    return non_latin_dominance_info(asr_text)["is_non_latin_dominant"]


# Azure Phrase List重み(SDK 1.50.0 PhraseListGrammar.setWeight、範囲0.0〜2.0。SDK既定=1.0)。
# 2026-10-20 ユーザー正式決定 APPROVED_FOR_PRODUCTION(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01)で2.0を採用。
# Trial(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、Fable判定REJECTED)で観測した副作用(有効負例33wav中、重み2.0で新規誤PASS+3、
# 例: Mullos->Melos)はユーザーが承知のうえ採用(安全網=既存のPASS_WITH_WARNING+試聴リスト運用、変更なし)。
# 正式採用のため既定ON固定: flag/環境変数/関数引数では切替えない(Family X/Y/Z共通、_AzureShared経由の全Azure呼出に適用)。
AZURE_PHRASE_LIST_WEIGHT: float = 2.0


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
        # 2026-10-20 APPROVED_FOR_PRODUCTION: 重み2.0(定数。PLが空ならPL未作成=bias送信なしのまま)
        phrase_list.setWeight(float(AZURE_PHRASE_LIST_WEIGHT))

    segments = []
    done = {"flag": False, "reason": None, "cancel_error": None}

    def on_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            segments.append(evt.result.text)

    def on_stopped(evt):
        done["flag"] = True
        done["reason"] = str(evt)

    def on_canceled(evt):
        # 委任_06c(OF-AUW-C-02): canceledをsession_stoppedと同等に扱って部分転写をerr=Noneで返さない
        # (JA `er007_ja_secondary_asr_01._azure_stt_strict`と同じ。CancellationReason.Error=認証/ネットワーク/サービス
        # エラーはtext=None+err。EndOfStream[ファイル正常終了]は正常)。部分転写はPASS根拠にしない。
        try:
            details = evt.cancellation_details
            if details.reason == speechsdk.CancellationReason.Error:
                done["cancel_error"] = f"CancellationReason.Error: {getattr(details, 'error_details', None)}"
        except Exception as exc:  # noqa: BLE001  詳細取得不能=保守側でError扱い
            done["cancel_error"] = f"canceled(詳細取得不能): {exc}"
        done["flag"] = True
        done["reason"] = "canceled"

    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_stopped)
    recognizer.canceled.connect(on_canceled)

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

    if done["cancel_error"]:
        cl.record({
            "provider": "azure", "api": "get_full_text_via_azure_stt_with_phrase_list",
            "model_id": "azure-speech-stt", "locale": language, "attempt_number": 1,
            "success": False, "elapsed_seconds": elapsed, "usage_source": "LOCAL_WAV_HEADER_EXACT",
            "audio_duration_submitted_seconds": duration, "phrase_list_size": len(phrases or []),
        })
        return None, done["cancel_error"]

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
import er008_disfluency_qa_18 as disfluency_qa
import er011_connected_speech_equivalence_layer_production_01 as cs_equivalence
# EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Phase A+B、
# APPROVED_FOR_PRODUCTION 2026-09-27): Tier 3(規則的複数形・固有名詞ASR
# 表記差のcorroboration付き救済)。このmoduleはval/er006_secondary_asr_01を
# 一切importしないため、module-level importでも循環importは発生しない。
import er021_en_asr_semantic_equivalence_production_01 as semantic_equivalence
# ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01(APPROVED_FOR_PRODUCTION 2026-10-13):
# CMU未収録語の複数発音候補(Ledger由来、segment開始前に凍結)によるM1判定。
import er006_m1_multi_candidate_01 as m1_multi


# --- M1 複数発音候補(ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01) -------------
_M1_FROZEN_CACHE: dict = {}


def _reset_m1_freeze_cache() -> None:
    _M1_FROZEN_CACHE.clear()
    _M1_SNAPSHOT_CACHE.clear()


# 注: _M1_FROZEN_CACHE / _M1_SNAPSHOT_CACHE はプロセス内で保持され(_reset_m1_freeze_cache()でのみ消去)、別segment・別runでも
# 同一canonical_textなら古い凍結を使い回す(結果はより厳しい側=古い時刻境界に倒れるだけで無害。Opus_H論点2 任意改善、委任_03で記録)。
_M1_SNAPSHOT_CACHE: dict = {}


def _m1_frozen_for(canonical_text: str, *, anchor_text: str | None = None):
    """segment最初の試行前に1回だけ候補集合を凍結する(OF-179)。同一canonical_textの
    2回目以降(retry/fallback/regen/減速後)は同じ凍結物を返し、再計算しない。
    失敗時はNone(M1不発=従来挙動、fail-closed)。

    anchor_text(委任_03、Opus_H条件1[論点2 M5]、OF-179): Local Rewrite(LR)後の再TTS・減速後再検証は、書換え後の文が
    新しいcanonical_textになる。これを『現在時刻』で凍結すると、同じsegment内でLR前に調べた(upsertした)Ledgerエントリが
    『開始前』扱いで候補に入る(OF-179違反)。そこでanchor_text(=LR前の元原稿)が**凍結済み**ならその`segment_started_at`
    (と保存済みsnapshot)で書換え後の文を凍結する。anchorが未凍結/凍結失敗(None)の場合は現在時刻やNoneで凍結せず
    M1不発(None=安全側)を返す。anchor_text未指定(または canonical_text と同一)は従来どおり(挙動不変)。"""
    if anchor_text is not None and anchor_text != canonical_text:
        key = ("anchor", anchor_text, canonical_text)
        if key in _M1_FROZEN_CACHE:
            return _M1_FROZEN_CACHE[key]
        anchor_fz = _M1_FROZEN_CACHE.get(anchor_text)
        started = getattr(anchor_fz, "segment_started_at", None) if anchor_fz is not None else None
        if anchor_fz is None or not started:
            return None  # anchor不在: キャッシュしない(後でanchorが凍結されれば使える)。M1不発=安全側
        try:
            snap = _M1_SNAPSHOT_CACHE.get(anchor_text)
            if snap is None:
                snap = copy.deepcopy(pronun_ledger._load())
            fz = m1_multi.freeze_candidates(canonical_text, ledger_snapshot=snap, segment_started_at=started)
        except Exception:
            fz = None
        _M1_FROZEN_CACHE[key] = fz
        return fz
    if canonical_text in _M1_FROZEN_CACHE:
        return _M1_FROZEN_CACHE[canonical_text]
    try:
        snap = copy.deepcopy(pronun_ledger._load())
        fz = m1_multi.freeze_candidates(
            canonical_text, ledger_snapshot=snap, segment_started_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
        _M1_SNAPSHOT_CACHE[canonical_text] = snap
    except Exception:
        fz = None
    _M1_FROZEN_CACHE[canonical_text] = fz
    return fz


def _m1_try(canonical_text, asr_text, cls_step, frozen, *, language, m1_enabled, secondary_text=None, step_name):
    """M1を試し、(accepted, audit)を返す。例外はfail-closed(accepted=False)。
    追加のASR/TTS呼出は一切行わない(コスト0)。"""
    if frozen is None or not m1_enabled or cls_step is None or asr_text is None:
        return False, None
    try:
        r = m1_multi.m1_multi_candidate_judge(
            canonical_text, asr_text, frozen, base_cls=cls_step, secondary_asr_text=secondary_text,
            m1_enabled=m1_enabled, lang=language)
    except Exception as exc:  # fail-closed
        return False, {"m1_layer_invoked": True, "m1_error": f"{type(exc).__name__}: {exc}", "step": step_name}
    audit = dict(r.audit)
    audit.update({"step": step_name, "reason": r.reason, "m1_layer_invoked": bool(r.applicable or r.audit),
                  "accepted": bool(r.accepted)})
    if not r.accepted and r.no_match_reason and "no_match_reason" not in audit:
        audit["no_match_reason"] = r.no_match_reason
    return bool(r.accepted), audit


def _m1_accept(result, steps, audit, cls_step):
    """M1受理: 既存ラベルと同形でPASS_WITH_WARNING相当の結果にする。"""
    result["verified"] = True
    result["stop_retrying"] = False
    result["final_status"] = m1_multi.ACCEPT_REASON
    result["m1_multi_candidate"] = audit
    if cls_step is not None:
        result["classification"] = cls_step
    steps.append({**audit, "step": "m1_multi_candidate", "provider": "local", "at_step": audit.get("step")})
    return result


def _m1_note_reject(result, audit):
    if audit is not None:
        result.setdefault("m1_multi_candidate_rejected", []).append(audit)

FEATURE_FLAG_SECONDARY_ASR_ENABLED = True  # Production既定でON(ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01。
                                            # 旧OFF状態はOPEN-48で「追加検証待ち」としていたが、
                                            # 同タスクでB1/A2 Sweenyケースとも実音声でCascadeが
                                            # 正しく動作することを確認済みのため有効化した

# SSOT: Cascadeの試行回数上限・Phrase List設定(タスク仕様§11-12)
CASCADE_CONFIG = {
    "max_primary_attempts": 2,
    "max_secondary_attempts": 2,
    "phrase_list_weight": AZURE_PHRASE_LIST_WEIGHT,  # SDK 1.50.0のPhraseListGrammar.setWeight(範囲0〜2、list全体の重み)を使用。
                                  # per-phrase重みではない。2026-10-20ユーザー採用で2.0(旧記述「SDKは重みAPI非公開」は誤りで訂正)。
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
    使わない(D-2'参照。ただし2026-10-13ユーザー承認『辞書未収録語は既存
    Pronunciation Ledgerや利用可能な発音情報から合理的な候補を取得する』による
    D-2'限定置換: 自動PASSの根拠に使うのは、M1(er006_m1_multi_candidate_01)が
    CMU未収録語かつLedgerのexpected/alternate IPA(canonical_spelling一致・
    sources非空・segment開始前のエントリ)を凍結候補として、F1の全差分点検と
    Pattern A/B/C(f1_explained)で説明できる場合に限る。Tier3の調査結果の即時
    利用・ASR側転写からの後付け候補・綴りからの推定は引き続き自動PASSの根拠にしない)。外国語由来の固有名詞をARPAbetへ強制変換すると
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
        # 委任_04A(記録欠落是正): queue「表示」の重複だけを抑止し、記録(Primary/
        # Secondary転写を含むsteps)は消さず、append-onlyのattempt_history.jsonlへ残す。
        review_lock.append_attempt_history_event(detail["wav_path"], "HUMAN_REVIEW_QUEUE_DUPLICATE_SUPPRESSED", {
            "canonical_text": detail["canonical_text"], "steps": detail.get("steps"),
            "final_status": detail.get("final_status")})
        return
    os.makedirs(os.path.dirname(HUMAN_REVIEW_LOG_PATH), exist_ok=True)
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "canonical_text": detail["canonical_text"],
        "wav_path": detail["wav_path"],
        "steps": detail["steps"],
        "cost_guard_triggered": detail["cost_guard_triggered"],
        "final_status": detail["final_status"],
        # 委任_03(Opus_H条件3、追加のみ): 減速後再検証でLR採用済みの場合、queueのcanonical_textは判定に使った文(書換え後)。
        # Lock/承認(record_human_approval)のkeyは元の原稿なので、その元原稿と正解原稿の出典を併記する(キー無し=従来行と同一)。
        **({"lock_canonical_text": detail["lock_canonical_text"]} if detail.get("lock_canonical_text") is not None else {}),
        **({"expected_text_source": detail["expected_text_source"]} if detail.get("expected_text_source") is not None else {}),
        # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part K: 固有名詞
        # (CMU辞書に無い外国由来名等)でHuman Reviewへ落ちた場合、
        # Pronunciation Ledgerから得られたcanonical_spelling/expected_
        # pronunciation_ipa/pronunciation_hint/confidence/sources等を
        # そのまま添付する(「正しく聞こえますか?」だけを提示しない)。
        "pronunciation_lookups": detail.get("pronunciation_lookups", {}),
        # S3(additive、PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-
        # AND-ASR-ENTITY-LIKE-01 修正1回目): 最終classificationのentity_like
        # 根拠カテゴリ(capitalized/loanword等)。各stepにも同名キーが個別に
        # 付与済み(steps[*].entity_like_source)なので、ここは「最終判定」の
        # 要約として追加する(既存キーは無変更)。
        "entity_like_source": (
            val.aggregate_entity_like_sources(detail["classification"].protected.content_word_diffs)
            if detail.get("classification") is not None else []),
    }
    with open(HUMAN_REVIEW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


# ============================================================
# OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01
# ============================================================
# ユーザー正式承認(2026-09-07、APPROVED_FOR_PRODUCTION、範囲=A2/B1英語
# 本文segmentのみ)。CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-
# TRIAL-01/02でVALIDATEDと判定された多証拠判定(er011_connected_speech_
# equivalence_layer_production_01.classify_connected_speech_equivalence、
# Trialから無変更で移植)を、既存3パターン(csv3.classify_connected_speech)
# のUNCLASSIFIED後段として追加する。

# Trial-01/02と同じlocal ASRモデル(faster-whisper small、CPU、無料)。
CONNECTED_SPEECH_EQUIVALENCE_LAYER_LOCAL_ASR_MODEL_SIZE = "small"


def _connected_speech_equivalence_local_asr_text(wav_path: str) -> str | None:
    """既存er008_disfluency_qa_18.transcribe_verbatim()(faster-whisper、
    ローカルCPU実行、追加API課金なし)を、独立ASR corroboration源として
    再利用する。失敗時はNoneを返し、呼び出し側はcorroboration無し
    (=acceptしない)として安全側に処理する。"""
    try:
        words = disfluency_qa.transcribe_verbatim(
            wav_path, language="en", model_size=CONNECTED_SPEECH_EQUIVALENCE_LAYER_LOCAL_ASR_MODEL_SIZE)
        return " ".join(w["text"].strip() for w in words).strip()
    except Exception as exc:  # ローカルモデル読み込み失敗等、安全側でNone
        return None


def _connected_speech_equivalence_layer_attempt(
        canonical_text: str, asr_text: Optional[str], wav_path: str, language: str,
        ledger_phrases: Optional[list[str]], azure_fn=None) -> Optional[dict]:
    """TRUE_CONTENT_MISMATCH(かつprotected_check通過済み、既存3パターン
    UNCLASSIFIED)のfallthrough時のみ呼ばれる。まずSecondary/local ASRを
    呼ばずに音韻環境カテゴリの該当有無だけを確認し(追加課金なし)、
    NEVER_ELIGIBLE_JUDGMENTSに該当する場合はNoneを返して即座に諦める
    (Secondary ASR呼び出し条件=fallthrough時かつカテゴリ候補時のみ、
    コスト増はその時だけに限定する)。候補である場合のみSecondary Azure
    (Phrase List付き、既存呼び出しと同じ関数を再利用)+local faster-
    whisperを1回ずつ呼び、実corroborationで最終判定する。"""
    cheap_check = cs_equivalence.classify_connected_speech_equivalence(canonical_text, asr_text or "")
    if cheap_check["layer_judgment"] in cs_equivalence.NEVER_ELIGIBLE_JUDGMENTS:
        return None

    # AUW 委任_03: azure_fn(共有SecondaryCache経由の(text, err))が渡されれば同一wavのAzure重複呼出を防ぐ。
    # 未指定(直接呼出)は従来どおり直接呼出。
    if azure_fn is not None:
        secondary_text, secondary_err = azure_fn()
    else:
        secondary_text, secondary_err = get_full_text_via_azure_stt_with_phrase_list(
            wav_path, language=language, phrases=ledger_phrases)
    local_text = _connected_speech_equivalence_local_asr_text(wav_path)

    final = cs_equivalence.classify_connected_speech_equivalence(
        canonical_text, asr_text or "", secondary_asr_text=secondary_text, local_asr_text=local_text)
    final["secondary_asr_text"] = secondary_text
    final["secondary_asr_error"] = secondary_err
    final["local_asr_text"] = local_text
    return final


def evaluate_attempt_with_cascade(
    canonical_text: str, asr_text: Optional[str], prior_results: list,
    wav_path: str, language: str = "en-US", ledger_phrases: Optional[list[str]] = None,
    max_same_signature: int = 3, cascade_enabled: bool = FEATURE_FLAG_SECONDARY_ASR_ENABLED,
    force_secondary: bool = False, enable_non_latin_cascade: bool = False,
    enable_connected_speech_equivalence_layer: bool = False,
    detail_out: Optional[dict] = None,
    # EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(既定None):
    # evaluate_attempt_with_cascade_detail()へそのまま転送する。
    segment_id: Optional[str] = None,
    m1_enabled: bool = True,
    # AUW 委任_03(既定None): 統一judgeのattempt文脈(slot/script_version/is_last_slot等)。
    attempt_ctx: Optional[dict] = None,
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
    らない。

    enable_non_latin_cascade(KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-
    PROD-WIRING-01で追加、既定False)は、英語Key Phrase Component経路
    (generate_key_phrase_component_verified経由)のみが明示的にTrueを
    渡す想定の引数。詳細はevaluate_attempt_with_cascade_detail()参照。
    既定Falseのため、この引数を渡さない既存の全呼び出し元(本文segment
    等)の挙動は完全に無変更。

    enable_connected_speech_equivalence_layer(OPEN-122-CONNECTED-SPEECH-
    EQUIVALENCE-LAYER-PRODUCTION-WIRING-01で追加、既定False): Trueの
    場合のみ、A2/B1英語本文segment限定でユーザー承認済みのConnected
    Speech Equivalence Layer(ARPAbetカテゴリA〜G+Secondary/local ASR
    corroboration)を、既存3パターンのUNCLASSIFIED fallthrough後段として
    追加で試みる。既定Falseのため、この引数を渡さない既存の全呼び出し元
    (Key Phrase・日本語segment・A2/B1以外の英語segment等)の挙動は
    完全に無変更。詳細はevaluate_attempt_with_cascade_detail()参照。

    detail_out(同タスクで追加、既定None): dictを渡すと、
    evaluate_attempt_with_cascade_detail()の戻り値全体(steps/
    cascade_invoked/non_latin_cascade_invoked等)でその場でupdate()する
    (呼び出し元がaudit記録用に参照するための追加出力、戻り値のtupleの
    形は変えない)。既定Noneのため、渡さない既存の全呼び出し元は無影響。"""
    detail = evaluate_attempt_with_cascade_detail(
        canonical_text, asr_text, prior_results, wav_path, language=language,
        ledger_phrases=ledger_phrases, max_same_signature=max_same_signature,
        cascade_enabled=cascade_enabled, force_secondary=force_secondary,
        enable_non_latin_cascade=enable_non_latin_cascade,
        enable_connected_speech_equivalence_layer=enable_connected_speech_equivalence_layer,
        segment_id=segment_id, m1_enabled=m1_enabled, attempt_ctx=attempt_ctx)
    if detail["human_review_required"]:
        _log_human_review(detail)
    if detail_out is not None:
        detail_out.update(detail)
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


# ============================================================
# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_03: EN統一judge adapter
# ============================================================
# evaluate_attempt_with_cascade_detail は**署名・戻り値dict・呼出元**を維持したまま、内部を統一判定
# (er078_asr_unified_judge_01.unified_judge)へ委譲するadapterに置換された(DESIGN_01 §4-1/§4-3/§4-9、
# DESIGN_02_ADDENDUM_01 §1/§4)。構造:
#   [Primary P-chain = 既存層を現行順のまま] val.evaluate_attempt(Tier1[5role]+baseline+contraction+B1 CS)
#       -> CS Equivalence層[flag] -> Tier3 -> 非ラテンKP -> CMU Case A/homophone -> M1(Primary)
#       ※これらのAzure補強は全て同一wavの共有SecondaryCache経由(重複呼出なし)。
#   [統一judge] Primary PASS -> 最終ANDゲート(値DIFF/否定差) / Primary NG -> P1保護差・P2除外・P3 Secondary 1回。
#       Secondary許容集合は既存should_pass集合([Secondary転写をclassify_asr_match]+CMU Case A/homophone+M1)を
#       `secondary_accept_fn`として注入(judgeへ再実装しない)。Secondary PASS -> PASS_WITH_WARNING(自動採用)。
# 廃止(DESIGN_01 §4-9、C-C(i)): Primary#2(同一音声のOpenAI再転写) / Secondary#2 / 4段尽き->stop_retrying+HR直行。
# 後方互換: cascade_enabled=False は従来どおりval.evaluate_attempt()と完全に同じ(統一judgeを通らない)。
import hashlib as _hashlib

import er078_asr_unified_judge_01 as unified_judge_mod

# Secondary重複呼出防止: 同一wav(sha256)+engine+lang+phrase_hash のAzure呼出を1回にする(成功のみcache、失敗はcacheしない)。
# 既定は**呼出単位のcache**(P-chainの補強層[CS Equivalence/Tier3/非ラテンKP/force_secondary]とjudgeのSecondaryが同一wavで
# 1回に収束する。process内の別呼出・別testへ結果を持ち越さない)。run単位の共有cache+circuit breaker/技術STOP記録は
# `begin_secondary_run()`を呼んだ場合のみ有効(opt-in。runner導入は委任_05/06で判断)。
_RUN_CACHE: Optional["unified_judge_mod.SecondaryCache"] = None
_SECONDARY_CACHE_MAX_ENTRIES = 512
_RUN_STATE: Optional["unified_judge_mod.RunState"] = None


def begin_secondary_run(circuit_breaker_threshold: int = unified_judge_mod.CIRCUIT_BREAKER_THRESHOLD) -> "unified_judge_mod.RunState":
    """run開始時にrun単位のRunState(circuit breaker・技術STOP記録・Secondary費用集計)と共有SecondaryCacheを導入する(opt-in)。"""
    global _RUN_STATE, _RUN_CACHE
    _RUN_STATE = unified_judge_mod.RunState(circuit_breaker_threshold=circuit_breaker_threshold)
    _RUN_CACHE = unified_judge_mod.SecondaryCache()
    return _RUN_STATE


def end_secondary_run() -> None:
    """run単位の状態を破棄する(既定の呼出単位cacheへ戻る)。"""
    global _RUN_STATE, _RUN_CACHE
    _RUN_STATE, _RUN_CACHE = None, None


def reset_secondary_cache() -> None:
    end_secondary_run()


def _wav_sha256(path: Optional[str]) -> Optional[str]:
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


def _phrase_hash(phrases: Optional[list]) -> str:
    return _hashlib.sha1("\n".join(sorted(phrases or [])).encode("utf-8")).hexdigest()[:12]


# Primary classificationラベル -> warningラベル(自動採用+事後試聴リスト対象)。ACCEPT系/完全一致系は警告なし。
_PRIMARY_WARNING_BY_CLASSIFICATION = {
    "CONNECTED_SPEECH_PASS_WITH_WARNING": "CONNECTED_SPEECH",
    "CONNECTED_SPEECH_EQUIVALENCE_PASS_WITH_WARNING": "CS_EQUIVALENCE",
    "SECONDARY_ASR_CORROBORATED_MATCH": "SECONDARY_CORROBORATED",
}


def _equivalence_basis_of(cls: "val.ClassificationResult") -> Optional[str]:
    """承認済みequivalence(最終ANDゲートが再否定しない根拠)を、classificationから導出する。"""
    if cls.classification == "HOMOPHONE_MATCH_NUMBER_EXCEPTION":
        return "HOMOPHONE_MATCH_NUMBER_EXCEPTION"
    if cls.classification == "NUMERIC_EQUIVALENCE_MATCH":
        info = cls.semantic_equivalence_info or {}
        spans = info.get("diff_spans") or {}
        return "TIER1_DIFF_ANCHORED" if (isinstance(spans, dict) and spans.get("diff_anchored")) else "TIER1_NUMERIC_EQUIVALENCE"
    return None


class _AzureShared:
    """同一wavに対するAzure(Phrase List付き)呼出を共有cache経由に一本化する(P-chainの補強層とjudgeのSecondaryで共有)。"""

    def __init__(self, wav_path, language, phrases, sha, cache):
        self.wav_path, self.language, self.phrases = wav_path, language, phrases
        self.sha, self.cache = sha, cache
        self.real_calls = 0
        self.cost_guard_triggered = False
        # judgeのSecondaryCacheキー(sha256, engine, lang, phrase_hash)と同一にする(P-chain補強層で取得済みのAzure結果を
        # judgeのSecondaryが再利用でき、監査recordのsecondary.cachedが実態を表す)。
        self.key = (sha, "azure", "ja" if str(language).lower().startswith("ja") else "en", _phrase_hash(phrases))

    def _call(self):
        dur = _wav_duration_seconds(self.wav_path)
        if dur is not None and (dur / 3600.0 * unified_judge_mod.AZURE_USD_PER_HOUR) > COST_GUARD_MAX_USD_PER_SEGMENT:
            # COST_GUARD($0.05/segment)を実費(秒数ベース)で等価適用: 1回分の見積が上限超ならSecondaryを呼ばずfail-closed。
            self.cost_guard_triggered = True
            return unified_judge_mod.SecondaryOutcome(None, error="cost_guard_exceeded")
        self.real_calls += 1
        try:
            text, err = get_full_text_via_azure_stt_with_phrase_list(self.wav_path, language=self.language, phrases=self.phrases)
        except Exception as exc:  # 委任_06c(OF-AUW-C-02): CS/Tier3/非ラテン3層+監査recordを一括でSecondary障害として扱う
            if unified_judge_mod.is_config_stop_error(exc):
                raise  # 設定不備(cost logger未init/単価未登録)は握りつぶさず伝播(er003:152-154と同方針)
            return unified_judge_mod.SecondaryOutcome(None, error=f"{type(exc).__name__}: {exc}")
        return unified_judge_mod.SecondaryOutcome(text, error=err)

    def outcome(self) -> "unified_judge_mod.SecondaryOutcome":
        out, _hit = self.cache.get_or_call(self.key, self._call)
        return out

    def text(self):
        """(text, err): 従来のget_full_text_via_azure_stt_with_phrase_list()と同じ形(空文字は空文字のまま返す)。"""
        out = self.outcome()
        return out.text, out.error


def evaluate_attempt_with_cascade_detail(
    canonical_text: str, asr_text: Optional[str], prior_results: list,
    wav_path: str, language: str = "en-US", ledger_phrases: Optional[list[str]] = None,
    max_same_signature: int = 3, cascade_enabled: bool = FEATURE_FLAG_SECONDARY_ASR_ENABLED,
    force_secondary: bool = False, enable_non_latin_cascade: bool = False,
    enable_connected_speech_equivalence_layer: bool = False,
    # EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(既定None): Tier 1
    # (val.classify_asr_matchのrole gating)とTier 3(下記)の両方へ転送する。
    # Noneの既存呼び出し元は挙動無変更(role gate非適用)。
    segment_id: Optional[str] = None,
    # ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01: 既定True(全英語ASR経路、KP含む)。
    m1_enabled: bool = True,
    # AUW 委任_03(既定None=slot1/script v0/最終slotでない): 統一judgeのattempt文脈。
    # dict: slot / script_version('v0'|'v1') / is_last_slot / length_ok / run_state / cache。
    attempt_ctx: Optional[dict] = None,
) -> dict:
    """統一ASR判定のEN adapter(AUW 委任_03)。署名と戻り値dictのキーは従来どおり(additiveで`asr_judgement`
    を追加)。cascade_enabled=Falseなら従来のval.evaluate_attempt()と完全に同じ(後方互換、統一judgeを通らない)。

    Primary P-chain(既存層を現行順で維持): Tier1[5role]+baseline+contraction+B1 CS -> CS Equivalence層
    (enable_connected_speech_equivalence_layer、A2/B1本文限定) -> Tier3 -> 非ラテンKP(enable_non_latin_cascade)
    -> CMU Case A/homophone -> M1。その後に統一judge: Primary PASSは最終ANDゲート(値DIFF/否定差)を通してPASS/
    PASS_WITH_WARNING、Primary NGは保護差(値DIFF/否定差)ならNG_PROTECTED(Secondary不呼出)、length NG等の除外表に
    該当すればNG_EXCLUDED、それ以外はAzure Secondaryを**1回**(同一wav+engine+lang+phrase_hashはSecondaryCacheで重複
    呼出なし)。Secondary許容集合PASSならPASS_WITH_WARNING(SECONDARY_CONFIRMED、自動採用+事後試聴リスト)、取得不能
    (例外/空転写/timeout/cost guard)はPASS不可のNG_SECONDARY_UNAVAILABLE(技術STOP記録)。

    force_secondary(既定False): Trueの場合、Primary PASSでもSecondaryの許容集合PASSを必須にする(従来の保護を維持)。
    Secondaryが同意しなければNG(従来のHR直行ではなく次attempt/slotへ)。

    戻り値の差分(DESIGN_01 §4-2/§4-9): stop_retrying=False固定(同一signature打切りは通算上限と重複)、
    Primary#2/Secondary#2/4段尽き->HR直行は廃止。human_review_required=Trueになるのは attempt_ctx.is_last_slot が
    Trueでかつ最終NGの場合のみ(leafが最終slotを伝えない間はFalse。最終STOPPEDは従来どおりleaf側のHR Lock経路)。
    """
    if not cascade_enabled:
        verified, stop_retrying, cls = val.evaluate_attempt(
            canonical_text, asr_text, prior_results, max_same_signature=max_same_signature, segment_id=segment_id)
        return {
            "verified": verified, "stop_retrying": stop_retrying, "classification": cls,
            "cascade_invoked": False,
            "steps": [{"step": "primary_1", "provider": "openai_asr", "text": asr_text,
                       "classification": cls.classification,
                       "entity_like_source": val.aggregate_entity_like_sources(cls.protected.content_word_diffs)}],
            "final_status": cls.classification, "human_review_required": False, "canonical_text": canonical_text,
            "wav_path": wav_path, "cost_guard_triggered": False, "non_latin_cascade_invoked": False,
            "connected_speech_equivalence_layer_invoked": False}

    actx = dict(attempt_ctx or {})
    lang = "ja" if str(language).lower().startswith("ja") else "en"
    verified, stop_retrying, cls = val.evaluate_attempt(
        canonical_text, asr_text, prior_results, max_same_signature=max_same_signature,
        segment_id=segment_id)

    steps = [{"step": "primary_1", "provider": "openai_asr", "text": asr_text,
              "classification": cls.classification,
              # S3(additive、修正1回目): entity_like判定の根拠カテゴリ。
              "entity_like_source": val.aggregate_entity_like_sources(cls.protected.content_word_diffs)}]
    # M1: segment単位の凍結(最初の呼出時のみ生成、以降は再利用)。en-US以外は不発。
    # 委任_03(Opus_H条件1): LR後の再TTS/減速後再検証はattempt_ctx["m1_anchor_text"](=元原稿)を渡し、元segment開始時刻で凍結する。
    # 未指定時は従来の呼出(引数1つ)のまま=挙動不変。
    _m1_anchor = actx.get("m1_anchor_text")
    if m1_enabled and language == "en-US":
        _m1_frozen = (_m1_frozen_for(canonical_text, anchor_text=_m1_anchor) if _m1_anchor
                      else _m1_frozen_for(canonical_text))
    else:
        _m1_frozen = None

    result = {
        "verified": verified, "stop_retrying": False, "classification": cls,
        "cascade_invoked": False, "steps": steps, "final_status": cls.classification,
        "human_review_required": False, "canonical_text": canonical_text, "wav_path": wav_path,
        "cost_guard_triggered": False, "non_latin_cascade_invoked": False,
        "connected_speech_equivalence_layer_invoked": False,
    }

    sha = _wav_sha256(wav_path)
    cache = actx.get("cache") or (_RUN_CACHE if (_RUN_CACHE is not None and sha) else unified_judge_mod.SecondaryCache())
    if cache is _RUN_CACHE and len(cache._store) > _SECONDARY_CACHE_MAX_ENTRIES:
        cache._store.clear()
    az = _AzureShared(wav_path, language, ledger_phrases, sha or f"nosha:{id(result)}", cache)
    primary_warnings: list = []
    layers: list = []
    adopted_text: Optional[str] = None  # 委任_06c(OF-AUW-C-01): 非ラテン層でAzure転写が採用根拠のとき、その転写(最終ANDゲート対象)

    if (not verified and enable_connected_speech_equivalence_layer
            and cls.classification == "TRUE_CONTENT_MISMATCH" and cls.protected.passed):
        # OPEN-122-CONNECTED-SPEECH-EQUIVALENCE-LAYER-PRODUCTION-WIRING-01(無変更の判定、Azureのみ共有cache経由)。
        eq_result = _connected_speech_equivalence_layer_attempt(
            canonical_text, asr_text, wav_path, language, ledger_phrases, azure_fn=az.text)
        if eq_result is not None:
            result["connected_speech_equivalence_layer_invoked"] = True
            layers.append("cs_equivalence")
            steps.append({
                "step": "connected_speech_equivalence_secondary", "provider": "azure",
                "text": eq_result.get("secondary_asr_text"),
                "layer_judgment": eq_result["layer_judgment"],
            })
            steps.append({
                "step": "connected_speech_equivalence_local", "provider": "local_faster_whisper",
                "text": eq_result.get("local_asr_text"),
                "layer_judgment": eq_result["layer_judgment"],
            })
            if eq_result["layer_judgment"] in cs_equivalence.ACCEPT_JUDGMENTS:
                new_classification = ("CONNECTED_SPEECH_EQUIVALENCE_ACCEPT"
                                       if eq_result["layer_judgment"] == "EQUIVALENCE_LAYER_ACCEPT"
                                       else "CONNECTED_SPEECH_EQUIVALENCE_PASS_WITH_WARNING")
                cls = val.ClassificationResult(
                    new_classification, cls.normalized_ratio, cls.protected,
                    should_pass=True, should_retry=False,
                    reason=f"Connected Speech Equivalence Layer(OPEN-122、A2/B1本文限定、"
                           f"corroboration>=1件+音韻環境カテゴリ該当): {eq_result['layer_judgment']} "
                           f"info={eq_result.get('equivalence_layer_info')}",
                    connected_speech_info=eq_result)
                verified = True
                result["verified"] = True
                result["final_status"] = cls.classification
                result["classification"] = cls
            else:
                # accept未達: 既存判定は変えず、診断情報だけをconnected_speech_infoへ付与する。
                cls = val.ClassificationResult(
                    cls.classification, cls.normalized_ratio, cls.protected,
                    should_pass=cls.should_pass, should_retry=cls.should_retry,
                    reason=cls.reason, connected_speech_info=eq_result)
                result["classification"] = cls

    if (not verified and segment_id is not None and cls.classification == "ASR_VALIDATION_UNCERTAIN"):
        # EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(Phase B、APPROVED_FOR_PRODUCTION 2026-09-27): Tier 3
        # (判定は無変更。Azureのみ共有cache経由=Secondary重複呼出なし)。
        import er020_tts_retry_local_rewrite_01 as _role_gate
        resolved_role = _role_gate.resolve_narrative_role(segment_id)
        if resolved_role in semantic_equivalence.FIVE_ROLES_APPLICABLE:
            canon_tokens = val.tokenize(canonical_text)
            asr_tokens = val.tokenize(asr_text) if asr_text is not None else []
            sub_reason, diff_loc = semantic_equivalence.determine_sub_reason(
                classification=cls.classification, should_pass=cls.should_pass,
                content_word_diffs=cls.protected.content_word_diffs,
                number_mismatches=cls.protected.number_mismatches,
                negation_mismatches=cls.protected.negation_mismatches,
                canon_tokens=canon_tokens, asr_tokens=asr_tokens)
            if sub_reason in ("plural_only", "entity_only") and diff_loc:
                result["cascade_invoked"] = True
                layers.append("tier3")
                text_corr, err_corr = az.text()
                steps.append({"step": "tier3_corroboration_secondary", "provider": "azure",
                               "text": text_corr, "sub_reason": sub_reason,
                               "entity_like_source": val.aggregate_entity_like_sources(
                                   cls.protected.content_word_diffs)})
                corroborated_by = []
                if text_corr is not None:
                    supports = semantic_equivalence.corroboration_supports(
                        canon_tokens, diff_loc["index"], val.tokenize(text_corr))
                    if supports is True:
                        corroborated_by.append("secondary")
                semantic_equivalence_record = {
                    "tier_applied": "tier3_corroboration" if corroborated_by else "tier3_attempted_no_corroboration",
                    "sub_reason": sub_reason, "corroborated_by": corroborated_by,
                    "warning": bool(corroborated_by), "role": resolved_role, "diff_spans": diff_loc,
                }
                if corroborated_by:
                    cls = val.ClassificationResult(
                        "SECONDARY_ASR_CORROBORATED_MATCH", cls.normalized_ratio, cls.protected,
                        should_pass=True, should_retry=False,
                        reason=(f"Tier3救済(sub_reason={sub_reason}): 独立ASR({corroborated_by})が"
                                f"diff位置でcanonical語'{diff_loc['canonical_word']}'を支持"),
                        semantic_equivalence_info=semantic_equivalence_record)
                    verified = True
                    result["verified"] = True
                    result["final_status"] = cls.classification
                    result["classification"] = cls
                else:
                    cls = val.ClassificationResult(
                        cls.classification, cls.normalized_ratio, cls.protected,
                        should_pass=cls.should_pass, should_retry=cls.should_retry,
                        reason=cls.reason, connected_speech_info=cls.connected_speech_info,
                        semantic_equivalence_info=semantic_equivalence_record)
                    result["classification"] = cls
                try:
                    semantic_equivalence.append_telemetry_log({
                        "canonical": canonical_text, "asr": asr_text, "role": resolved_role,
                        "classification": cls.classification, "sub_reason": sub_reason,
                        "diff_span": diff_loc, "corroborated_by": corroborated_by,
                        "step": "tier3_corroboration",
                        "entity_like_source": val.aggregate_entity_like_sources(
                            cls.protected.content_word_diffs),
                    })
                except OSError:
                    pass  # telemetry書き込み失敗は判定・retry挙動に影響させない(安全側)

    if not verified and enable_non_latin_cascade and is_non_latin_dominant_mismatch(asr_text):
        # KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01 対策(a)(判定は無変更、Azureは共有cache経由)。
        result["cascade_invoked"] = True
        result["non_latin_cascade_invoked"] = True
        layers.append("non_latin")
        text_nl, err_nl = az.text()
        cls_nl = val.classify_asr_match(canonical_text, text_nl, segment_id=segment_id) if text_nl is not None else None
        steps.append({"step": "non_latin_secondary", "provider": "azure", "text": text_nl,
                       "classification": cls_nl.classification if cls_nl else "TTS_FAILURE",
                       "phrase_list_used": bool(ledger_phrases),
                       "azure_phrase_list_weight": (AZURE_PHRASE_LIST_WEIGHT if ledger_phrases else None),
                       "azure_phrase_list": list(ledger_phrases or []),
                       "non_latin_info": non_latin_dominance_info(asr_text),
                       "entity_like_source": (val.aggregate_entity_like_sources(cls_nl.protected.content_word_diffs)
                                               if cls_nl else [])})
        if cls_nl is not None and cls_nl.should_pass:
            result["verified"] = True
            result["final_status"] = cls_nl.classification
            result["classification"] = cls_nl
            verified = True
            cls = cls_nl
            adopted_text = text_nl
            primary_warnings.append(unified_judge_mod.W_SECONDARY_CONFIRMED)  # Secondaryが救済した=事後試聴対象

    if not verified:
        cascade_eligible = is_entity_like_mismatch(cls) or is_homophone_candidate_mismatch(cls)
        if cascade_eligible:
            # 追加ASR無しで判定できる層(CMU辞書Case A/homophone、M1)。コストゼロ。
            immediate_label = _step_alternate_pass(cls)
            if immediate_label:
                verified = True
                result["verified"] = True
                result["final_status"] = immediate_label
                layers.append("cmu_alternate")
            else:
                _ok, _au = _m1_try(canonical_text, asr_text, cls, _m1_frozen, language=language,
                                   m1_enabled=m1_enabled, secondary_text=None, step_name="primary_1")
                if _ok:
                    verified = True
                    _m1_accept(result, steps, _au, cls)
                    primary_warnings.append("M1_MULTI_CANDIDATE")
                    layers.append("m1_primary")
                else:
                    _m1_note_reject(result, _au)

    # ---- 統一judge ----
    if verified and cls.classification in _PRIMARY_WARNING_BY_CLASSIFICATION:
        primary_warnings.append(_PRIMARY_WARNING_BY_CLASSIFICATION[cls.classification])
    signals = {"c1_proper_noun_diff": bool(is_entity_like_mismatch(cls)),
               "c2_homophone_candidate": bool(is_homophone_candidate_mismatch(cls)),
               "similarity": cls.normalized_ratio}
    primary = unified_judge_mod.PrimaryResult(
        passed=bool(verified), text=asr_text, label=str(result.get("final_status") or cls.classification),
        equivalence_basis=_equivalence_basis_of(cls) if verified else None,
        warning_labels=tuple(dict.fromkeys(primary_warnings)), signals=signals,
        adopted_text=adopted_text if verified else None)
    ctx = unified_judge_mod.AttemptCtx(
        canonical_text=canonical_text, wav_path=wav_path, wav_sha256=az.sha, audio_seconds=_wav_duration_seconds(wav_path),
        segment_key=segment_id or "", script_version=actx.get("script_version", "v0"), slot=int(actx.get("slot", 1)),
        is_last_slot=bool(actx.get("is_last_slot", False)), length_ok=bool(actx.get("length_ok", True)),
        max_len=actx.get("max_len"),  # AUW 委任_13(A3R-01/03): 呼出元のmax_len。None=従来挙動(安全ラッチ)
        force_secondary=bool(force_secondary), engine="azure", phrase_list_hash=_phrase_hash(ledger_phrases),
        cache=cache, run_state=actx.get("run_state") or _RUN_STATE)
    try:
        import er020_tts_retry_local_rewrite_01 as _rg
        judge_role = _rg.resolve_narrative_role(segment_id)
    except Exception:
        judge_role = None
    captured: dict = {}
    # 従来のstep名を維持(audit/HR packageの互換): force_secondary経路="secondary_forced"、通常="secondary_1"。
    _sec_step_name = "secondary_forced" if (force_secondary and verified) else "secondary_1"

    def _secondary_fn(_ctx):
        return az.outcome()

    def _secondary_accept(canon, stext):
        """既存のSecondary許容集合(should_pass+CMU Case A/homophone+M1[Secondary転写])。judgeへ再実装しない。"""
        cls_s = val.classify_asr_match(canon, stext, segment_id=segment_id)
        captured["cls_s"] = cls_s
        if cls_s.should_pass:
            return True, cls_s.classification
        label = _step_alternate_pass(cls_s)
        if label:
            captured["alt_label"] = label
            return True, label
        _ok2, _au2 = _m1_try(canon, stext, cls_s, _m1_frozen, language=language, m1_enabled=m1_enabled,
                             secondary_text=asr_text, step_name=_sec_step_name)
        if _ok2:
            captured["m1_audit"] = _au2
            return True, "M1_MULTI_CANDIDATE"
        _m1_note_reject(result, _au2)
        return False, cls_s.classification

    jr = unified_judge_mod.unified_judge(ctx, primary, _secondary_fn, lang=lang, role=judge_role,
                                         secondary_accept_fn=_secondary_accept)
    audit = jr.audit_record
    sec = audit.get("secondary") or {}
    secondary_ran = bool(sec.get("called") or sec.get("cached") or sec.get("error"))
    if secondary_ran:
        result["cascade_invoked"] = True
        cls_s = captured.get("cls_s")
        # 従来のstep名を維持: force_secondary経路は"secondary_forced"、通常のSecondaryは"secondary_1"(audit/HR packageの互換)。
        steps.append({"step": _sec_step_name,
                       "provider": "azure", "text": sec.get("text"),
                       "classification": cls_s.classification if cls_s else ("TTS_FAILURE" if not sec.get("text") else sec.get("label")),
                       "phrase_list_used": bool(ledger_phrases),
                       "azure_phrase_list_weight": (AZURE_PHRASE_LIST_WEIGHT if ledger_phrases else None),
                       "azure_phrase_list": list(ledger_phrases or []), "cached": bool(sec.get("cached")),
                       "unified_judge_state": jr.state,
                       "entity_like_source": (val.aggregate_entity_like_sources(cls_s.protected.content_word_diffs) if cls_s else [])})
    if az.cost_guard_triggered:
        result["cost_guard_triggered"] = True

    result["verified"] = bool(jr.verified)
    result["stop_retrying"] = False
    if jr.verified:
        if "m1_audit" in captured:
            _m1_accept(result, steps, captured["m1_audit"], captured.get("cls_s"))
        elif "alt_label" in captured:
            result["final_status"] = captured["alt_label"]
            result["classification"] = captured["cls_s"]
        elif "cls_s" in captured and not primary.passed:
            result["final_status"] = captured["cls_s"].classification
            result["classification"] = captured["cls_s"]
    else:
        result["final_status"] = cls.classification
        result["classification"] = cls
        if audit.get("technical_stop") or jr.secondary_unavailable:
            result["technical_stop"] = audit.get("technical_stop")
        # 委任_06c(OF-AUW-C-06、ADDENDUM §4): NG理由が**Secondary障害のみ**(NG_SECONDARY_UNAVAILABLE)の最終slotは、人間が聞いて判断する
        # 品質問題ではなく技術障害のため、Human Review(Lock/queue)へ投入しない。`technical_stop`(truthy dict)+status名で
        # 技術STOP(承認不要・再実行で再開可)として返し、runnerがcircuit_open/technical_stopを読んで残りclipを停止・報告する。
        _tech_only = jr.state == unified_judge_mod.NG_SECONDARY_UNAVAILABLE
        if _tech_only:
            result["human_review_required"] = False
            result["technical_stop"] = audit.get("technical_stop") or {"type": "SECONDARY_UNAVAILABLE", "restartable": True,
                                                                        "approval_required": False}
            result["technical_stop_status"] = "TECHNICAL_STOP_SECONDARY_UNAVAILABLE"
        if bool(actx.get("is_last_slot", False)) and not _tech_only:
            result["human_review_required"] = True
            if is_entity_like_mismatch(cls):
                pronunciation_lookups = {}
                for span in _unresolved_entity_spans(cls):
                    info = _resolve_unresolved_entity_for_review(span)
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
    audit["adapter"] = {"layers": layers, "azure_real_calls": az.real_calls, "cost_guard_triggered": az.cost_guard_triggered,
                        "language": language, "segment_id": segment_id, "asr_text_present": asr_text is not None,
                        "cache": {"calls": cache.calls, "hits": cache.hits}}
    result["asr_judgement"] = audit
    return result
