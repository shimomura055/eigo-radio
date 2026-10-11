# ============================================================
# er003_v1_sing01_voice01_generate.py
# ER-003-B1-NOVEL-AUDIO-01-VOICE-01: Voice role再配置 + Point見出し追加
# ============================================================
# 既存ER-003-B1-NOVEL-AUDIO-01のFact/Ledger/B1 Scaffold/記事本文は一切
# 変更しない。Aoede=本文Listening対象、Charon=Navigator/Explanationと
# いう役割分担へ、以下を新規Charon生成する:
#   Welcome / Topic intro / Preview intro / Point explanation /
#   Key phrases intro / Full story intro / num_one〜five(番号ラベル、
#   ユーザー確認済み) / Key Phrase日本語meaning5件 / Point One・Two本文 /
#   In One Line / 新規 "Point One." "Point Two." 見出し
# Aoedeのまま維持(無変更で再利用): Preview本文、Key Phrase英語
# Component5件、Full Story Part1/2
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_voice01_generate.py

from __future__ import annotations

import json

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er007_ja_secondary_asr_01 as ja_secondary
import er006_preprod_hardening_01_validation as audio_validation
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er008_disfluency_qa_18 as dq18
import er011_human_review_lock_01 as review_lock
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er025_entity_pronunciation_resolver_core_01 as pron_resolver_core

OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"
CHARON = "Charon"
SAFETY_MARGIN = 0.35  # AUDIO-03/NOVEL-AUDIO-01のtail切れ修正と同じ値を継承


@review_lock.guarded_generate("en")
def generate_charon_english(text: str, out_path: str,
                             max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
                             style_prefix_override: str = None,
                             # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: B1 Previewなど
                             # 短文でpartial repetitionが目立ちやすいsegmentのみ呼び出し側
                             # からTrueを渡す(既定Falseで既存の全呼び出しに影響なし)。
                             disfluency_qa: bool = False,
                             # TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01:
                             # 呼び出し側は必ずer020_tts_retry_local_rewrite_01.
                             # connected_speech_enabled_for(segment_id)の戻り値を渡す
                             # (既定False、他の全呼び出し元は無変更)。この関数自身が
                             # Comment/Preview/Topic introの生成経路であるため、本引数の
                             # 追加により、これら3 roleが初めてConnected Speech
                             # Equivalence Layer(OPEN-122)の対象になれる(従来は
                             # secondary_asr.evaluate_attempt_with_cascadeへこの引数
                             # 自体を渡せていなかった、docs/pm/recon_connected_speech_
                             # scope_01.md「事実1」参照)。同じ引数値で、10分cool-down
                             # (attempt3の直前のみ)とLocal Rewrite回復(3回とも不合格
                             # だった場合、Human Review Lock到達前)もあわせて有効になる。
                             enable_connected_speech_equivalence_layer: bool = False,
                             # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-
                             # PUNCT-01(OPEN-197是正、既定False): Family X production
                             # runner(topic_intro/preview/comment_1-4呼び出し)のみが明示的に
                             # Trueを渡す。Family A/B/C(legacy)の既存呼び出し元は無変更のまま。
                             enable_pronunciation_resolver: bool = False,
                             # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01
                             # (2026-09-27、既定"structured_separation"で既存挙動と
                             # byte-identical): Family X runnerのみが明示的に
                             # "speech_metadata_flash_lite"を渡す(Family A/B/C
                             # [legacy]は無変更)。標準経路・minimal fallback経路・
                             # Local Rewrite回復経路のいずれにも転送する。
                             tts_backend: str = "structured_separation") -> dict:
    """ENGLISH_STYLE_PREFIX主経路(voice=Charon)+MINIMAL_INSTRUCTION
    fallback。trim安全マージンはNOVEL-AUDIO-01のtail切れ修正と同じ
    0.35秒を使う。"""
    # ER-008-N8-QA-CONTENT-SPEED-HARDENING-18: No.8のB1 Comment 2で
    # "In Part 2, ..."という制作内部ラベルが英語canonical textへ残って
    # いた事故を受け、TTS呼び出し前に検出する(発生源[Comment生成prompt
    # のcontext]の修正[er003_v1_n3_01_scaffold_generate.py]に加える
    # 第二の防御線、rule-based・追加API呼び出し無し)。本関数はA2/B1
    # 双方のCharon英語音声で共通利用されるため、この位置での検出は
    # 両レベルへ同時に適用される。
    label_findings = safety.detect_internal_production_labels_in_english_text(text)
    if safety.english_internal_label_gate_requires_stop(label_findings):
        return {
            "status": "STOPPED",
            "reason": "canonical textに制作内部のsegment名/章番号ラベルが残っています"
                      "(Human Review待ち): " + ", ".join(f["token"] for f in label_findings),
            "canonical_text": text, "internal_label_findings": label_findings,
        }
    # TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 4
    # Gate、2026-09-27): 呼び出し側(tts_generate.py等)がtts_safe_en/
    # tts_safe_news_enでNormalizerを適用した後のtextがここへ渡る想定。
    # Normalizer通過後になお残る禁止記号(括弧・スラッシュ・URL/email・
    # 絵文字・未変換のplaceholder/ポーズ記号残存)を検出する。%$¥は
    # observe専用でブロックしない(Fableレビュー決定3)。
    symbol_findings = safety.detect_prohibited_symbols(text, language="en")
    if safety.symbol_gate_requires_stop(symbol_findings):
        return {
            "status": "STOPPED",
            "reason": "canonical textに音声化禁止記号が残っています(Normalizer通過後の残存): "
                      + ", ".join(f"{f['category']}:{f['token']}" for f in symbol_findings),
            "canonical_text": text, "symbol_findings": symbol_findings,
        }
    # EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01(既定None、
    # out_pathが標準命名慣習に従わない場合[単体テストのダミーパス等]は
    # Noneのまま=role gate非適用、既存挙動と完全に同じ): narration wav
    # パスから機械的にsegment_idを導出し、classify_asr_matchのrole
    # gating(Tier1/Tier3)へ渡す。_local_rewrite_recovery_for_charon_
    # english()と同じ導出方法(review_lock.derive_segment_key)を使う。
    segment_id = None
    if review_lock._has_valid_narration_layout(out_path):
        _, _, segment_id = review_lock.derive_segment_key(out_path)
    # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01
    # (OPEN-197是正): A2英語標準経路(repro01.generate_narration_snippet_
    # verified_strict)と同一のhook(同じ関数・同じconfidence gate[augment_
    # style_prefix_with_pronunciationのmin_confidence="medium"]・同じ
    # telemetry形状en_pronunciation_resolver_info)を、opt-in引数が
    # Trueの場合のみ適用する。hintが1件も無い場合はstyle_prefix_override
    # を一切変更しない(既存呼び出し元・既存promptへの影響をゼロに保つ)。
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、Opus L2所見MAJOR-2/
    # MINOR-A是正): 呼び出し元がstyle_prefix_overrideを実際に指定したか
    # どうかを、以降の(発音resolverによる)再代入より前に固定しておく
    # (runtime evidence記録の既定/override判定用。既存挙動には無影響)。
    _caller_provided_style_override = style_prefix_override is not None
    en_pronunciation_resolver_info = None
    if enable_pronunciation_resolver:
        base_style_prefix = style_prefix_override if style_prefix_override is not None else p9a.ENGLISH_STYLE_PREFIX
        augmented_style_prefix, en_pronunciation_resolver_info = pron_resolver_core.resolve_and_augment_en_style_prefix(
            base_style_prefix, text)
        if en_pronunciation_resolver_info.get("hints_applied"):
            style_prefix_override = augmented_style_prefix
    import er033_tts_flash_lite_backend_wiring_01 as flw
    max_len = len(text) + 15
    attempts_log = []
    classification_history = []
    cooldown_events = []
    for attempt in range(1, max_attempts + 1):
        # TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01: ユーザー
        # 承認済みcool-down(attempt1->即時attempt2->NG->10分固定cool-down->
        # attempt3)。enable_connected_speech_equivalence_layer=Falseの
        # 既存呼び出し元には一切影響しない(即座にNoneを返すだけ)。
        cooldown_record = retry_primitive.maybe_cooldown_before_attempt(
            attempt, max_attempts, enable_connected_speech_equivalence_layer)
        if cooldown_record:
            cooldown_events.append(cooldown_record)
        # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
        # (声・モデルはgclient.make_tts_call_fn(CHARON)と同一)。
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01: 既定
        # backendでは上記2行とbyte-identical。
        standard_style_prefix = style_prefix_override or p9a.ENGLISH_STYLE_PREFIX
        # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、MAJOR-2是正):
        # 実際にTTSへ渡した最終文字列をruntime evidence用に保持する。
        _active_style_prefix = standard_style_prefix
        call_fn, prompt = flw.resolve_tts_call_and_prompt(
            text, standard_style_prefix, common.MODEL_NAME, CHARON, out_path, tts_backend=tts_backend,
            build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=batch_wiring.make_batch_tts_call_fn)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        instruction_type = "english_style_prefix"
        trimmed = None
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": str(err) if not ok else "発話区間検出失敗",
                                  "instruction_type": instruction_type})
            # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: fallback経路にも
            # Structured Separationを適用する。
            # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02
            # (修正3回目、2026-09-28、Opus L2所見BL-3是正): Flash-Lite
            # backend時のみ、er003_v1_repro01_main_generate.py:536-540
            # (generate_english_component_minimal_instruction)と同じ方式で
            # 短いfallback style(FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]、新規
            # style文言は考案しない)を使う。既定backend(structured_
            # separation)はMINIMAL_INSTRUCTION_PREFIXのまま(byte-identical)。
            if tts_backend == "speech_metadata_flash_lite":
                import er033_tts_flash_lite_family_x_styles_01 as fl_styles
                fallback_style_prefix = fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]
            else:
                fallback_style_prefix = repro01.MINIMAL_INSTRUCTION_PREFIX
            # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-
            # VALIDATOR-PUNCT-01(修正2回目、Opus L2所見S3是正・非対称
            # 解消): 標準style_prefix(style_prefix_override)側にのみ
            # 発音ヒントが注入され、この技術的fallback(MINIMAL_
            # INSTRUCTION_PREFIX)には反映されない非対称を解消する。関数
            # 冒頭で既に算出済みのcache_hitsを、新規Ledger読み取り・
            # 新規web lookupなしで同一hookによりそのまま適用する。
            if enable_pronunciation_resolver and en_pronunciation_resolver_info \
                    and en_pronunciation_resolver_info.get("cache_hits"):
                fallback_style_prefix = pron_resolver_core.augment_style_prefix_with_cached_hits(
                    fallback_style_prefix, en_pronunciation_resolver_info["cache_hits"])
            # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、MAJOR-2是正):
            # fallback発火時は、こちらが実際にTTSへ渡した最終文字列になる。
            _active_style_prefix = fallback_style_prefix
            call_fn2, prompt2 = flw.resolve_tts_call_and_prompt(
                text, fallback_style_prefix, common.MODEL_NAME, CHARON, out_path, tts_backend=tts_backend,
                build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=batch_wiring.make_batch_tts_call_fn)
            pcm2, retries2, ok2, err2 = common._call_tts_with_retry(
                call_fn2, prompt2, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
            instruction_type = "minimal_fallback"
            if not ok2:
                attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err2),
                                      "instruction_type": instruction_type})
                continue
            samples_raw2 = common.pcm_bytes_to_float_mono(pcm2)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw2, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
            if trimmed is None:
                attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間検出失敗(fallback)",
                                      "instruction_type": instruction_type})
                continue

        # ER-005-AUDIO-WASTE-REDUCTION-01: hallucinationを疑わせる異常長
        # 音声を、ASR実行前に検知して破棄する(kp5_en実例: association
        # という1語が17秒超の無関係な内容になった)。
        anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
        if anomaly["is_anomaly"]:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": anomaly["reason"],
                                  "instruction_type": instruction_type, "duration_anomaly": anomaly})
            continue

        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = routing.transcribe(out_path, language="en-US")
        # ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: safety.validate_asr_match
        # (word-subsequence一致)から、正規化+6分類+Protected Check+同一
        # signature retry guardrail方式へ切り替える。
        length_ok = asr_text is not None and len(asr_text) <= max_len
        ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
        verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
            text, asr_text, classification_history, out_path, language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED,
            # TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01: 従来
            # この関数はこの引数自体を渡せず、Comment/Preview/Topic intro
            # 経路(この関数経由)ではOPEN-122 Equivalence Layerが構造的に
            # 発火し得なかった(docs/pm/recon_connected_speech_scope_01.md
            # 「事実1」)。呼び出し側がconnected_speech_enabled_for()で
            # 判定した値をそのまま転送する。
            enable_connected_speech_equivalence_layer=enable_connected_speech_equivalence_layer,
            segment_id=segment_id)
        verified = verified_content and length_ok
        gate = dq18.apply_disfluency_gate(verified, out_path, language="en", enabled=disfluency_qa)
        verified = gate["verified"]
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "audio_classification": cls.classification,
                              "connected_speech_info": getattr(cls, "connected_speech_info", None),
                              "semantic_equivalence": getattr(cls, "semantic_equivalence_info", None),
                              "length_ok": length_ok, "verified": verified, "trim_info": trim_info,
                              "disfluency_checked": gate["disfluency_checked"],
                              "disfluency_evidence": gate.get("disfluency_evidence")})
        # ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01: このattemptで
        # out_pathへ実際に書き込まれた音声を、上書きせず個別保存する。
        _attempt_audio_path = review_lock.save_tts_attempt_audio(out_path, instruction_type, {
            "loop_attempt_index": attempt, "max_attempts": max_attempts, "language": "en",
            "model": flw.resolve_actual_model_name(common.MODEL_NAME, tts_backend), "voice": CHARON,
            "tts_execution_mode": batch_wiring.resolve_tts_execution_mode(), "tts_backend": tts_backend,
            "asr_text": asr_text, "audio_classification": cls.classification,
            "length_ok": length_ok, "verified": verified,
            "disfluency_checked": gate["disfluency_checked"],
            "disfluency_evidence": gate.get("disfluency_evidence"),
        })
        attempts_log[-1]["attempt_audio_path"] = _attempt_audio_path
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "clipping_detected": metrics["clipping_detected"],
                    "audio_classification": cls.classification,
                    "connected_speech_info": getattr(cls, "connected_speech_info", None),
                    # ER-008-N8-FINAL-QA-HARDENING-21 Item 1: top-levelへ昇格。
                    "disfluency_checked": gate["disfluency_checked"],
                    "disfluency_evidence": gate.get("disfluency_evidence"),
                    "en_pronunciation_resolver_info": en_pronunciation_resolver_info,
                    "cooldown_events": cooldown_events, "tts_backend": tts_backend,
                    "model": flw.resolve_actual_model_name(common.MODEL_NAME, tts_backend),
                    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、Opus L2
                    # 所見MAJOR-2/MINOR-A是正): 実際に渡した最終style文字列
                    # (override指定時のみ)・model_idのruntime evidence。
                    "style_prefix": (_active_style_prefix if _caller_provided_style_override
                                      else "<default:ENGLISH_STYLE_PREFIX>"),
                    "tts_model_id": flw.resolve_actual_model_name(common.MODEL_NAME, tts_backend)}
        if stop_retrying:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            if enable_connected_speech_equivalence_layer:
                recovered = _local_rewrite_recovery_for_charon_english(
                    text, out_path, asr_text, style_prefix_override, disfluency_qa,
                    enable_connected_speech_equivalence_layer, attempts_log,
                    en_pronunciation_resolver_info=en_pronunciation_resolver_info, tts_backend=tts_backend)
                if recovered is not None:
                    recovered["cooldown_events"] = cooldown_events
                    return recovered
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "clipping_detected": metrics["clipping_detected"],
                    "reason": f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification})",
                    "en_pronunciation_resolver_info": en_pronunciation_resolver_info,
                    "cooldown_events": cooldown_events,
                    "style_prefix": (_active_style_prefix if _caller_provided_style_override
                                      else "<default:ENGLISH_STYLE_PREFIX>"),
                    "tts_model_id": flw.resolve_actual_model_name(common.MODEL_NAME, tts_backend)}
    if enable_connected_speech_equivalence_layer:
        last_asr_text = attempts_log[-1].get("asr_text") if attempts_log else None
        recovered = _local_rewrite_recovery_for_charon_english(
            text, out_path, last_asr_text, style_prefix_override, disfluency_qa,
            enable_connected_speech_equivalence_layer, attempts_log,
            en_pronunciation_resolver_info=en_pronunciation_resolver_info, tts_backend=tts_backend)
        if recovered is not None:
            recovered["cooldown_events"] = cooldown_events
            return recovered
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log, "en_pronunciation_resolver_info": en_pronunciation_resolver_info,
            "cooldown_events": cooldown_events}


def _local_rewrite_recovery_for_charon_english(
        text: str, out_path: str, last_asr_text: str | None,
        style_prefix_override: str, disfluency_qa: bool,
        enable_connected_speech_equivalence_layer: bool, main_loop_attempts_log: list | None = None,
        # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-
        # PUNCT-01(修正2回目、Opus L2所見S2是正): 呼び出し元(generate_
        # charon_english)が関数冒頭で算出済みのtelemetryをそのまま渡す。
        # hint自体(style_prefix_override)は既にこの関数の引数として保持
        # されているため再TTSのpromptには反映済みだが、telemetryフィールド
        # 自体はこの関数配下の__wrapped__呼び出し(enable_pronunciation_
        # resolver既定False)からは伝播されないため、戻りdictへ別途注入する。
        en_pronunciation_resolver_info: dict | None = None,
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01(既定
        # "structured_separation"で既存挙動とbyte-identical、設計書§(b):
        # regeneration経路も同一backend経由)。
        tts_backend: str = "structured_separation") -> dict | None:
    """generate_charon_english()専用のLocal Rewrite回復ヘルパー(ユーザー
    承認済み仕様D: Human Review Lock到達前の回復経路)。3回とも(または
    stop_retryingで)ASR検証に合格しなかった場合のみ呼ばれる。回復成功時は
    status="OK"の完全なdictを返す(呼び出し元はそのままreturnし、
    review_lock.record_outcomeはRESOLVEDへ遷移する)。回復不可の場合は
    Noneを返し、呼び出し元は従来通りHuman Review Lockへ進む。"""
    if not review_lock._has_valid_narration_layout(out_path):
        return None
    theme_id, level, segment_id = review_lock.derive_segment_key(out_path)

    def _retts_fn(rewritten_text: str) -> dict:
        return generate_charon_english.__wrapped__(
            rewritten_text, out_path, max_attempts=1,
            style_prefix_override=style_prefix_override, disfluency_qa=disfluency_qa,
            enable_connected_speech_equivalence_layer=enable_connected_speech_equivalence_layer,
            tts_backend=tts_backend)

    recovery = retry_primitive.run_local_rewrite_recovery(
        segment_id=segment_id, canonical_text=text, last_asr_text=last_asr_text,
        retts_fn=_retts_fn, out_dir=f"er011_output/local_rewrite_recovery/{theme_id}/{level}")
    if recovery["status"] != "RESOLVED_BY_LOCAL_REWRITE":
        return None
    resolved = dict(recovery["retts_result"])
    resolved["local_rewrite_recovery"] = recovery
    resolved["canonical_text_before_local_rewrite"] = text
    # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-
    # PUNCT-01(修正2回目、Opus L2所見S2是正): __wrapped__呼び出しは
    # enable_pronunciation_resolver既定Falseのため、resolved自身の
    # en_pronunciation_resolver_infoは常にNoneのまま返る。呼び出し元
    # (generate_charon_english)が既に算出済みの値を、resolvedが未設定
    # (None)の場合のみ注入する(hint自体はstyle_prefix_override経由で
    # 既にpromptへ反映済み、ここではtelemetryフィールドのみを補う)。
    if resolved.get("en_pronunciation_resolver_info") is None:
        resolved["en_pronunciation_resolver_info"] = en_pronunciation_resolver_info
    # TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01(runtime
    # evidence実行時に発見): retts_result単独のattempts_log(1件)だけを
    # 上位へ返すと、review_lock.record_outcome()の累積TTS/ASR call数
    # guard(Part F、MAX_CUMULATIVE_TTS_ATTEMPTS)が、実際に消費した
    # メインループ分のattemptを数え落とす。メインループ+re-TTSの両方を
    # 連結し、実消費回数を正しく反映する。
    resolved["attempts_log"] = list(main_loop_attempts_log or []) + (resolved.get("attempts_log") or [])
    return resolved


# ER-003-N3-ROOT-FIX-01(2026-08-17): 短い単独の日本語フレーズ(Key
# Phraseの日本語訳・語句)にJAPANESE_STYLE_PREFIX(長い演技指示、約1800
# 文字)を使うと、モデルが指示文自体を読み上げてしまう事例が高頻度で
# 確認された(POINT_LABEL_FIDELITY_RULE除去後も、Health B1「modeled
# differences」で5回中5回再現。同じ検証で、文単位の長さを持つJapanese
# Titleは0回中5回で再現せず — 短いフレーズに固有の問題と判明)。
# 英語Key Phraseに既存のMINIMAL_INSTRUCTION_PREFIX(repro01、"Speak the
# following text aloud naturally...")と同じ考え方を、日本語の短い
# フレーズにも適用する。
MINIMAL_INSTRUCTION_PREFIX_JA = (
    "次の文章だけを、翻訳・言い換え・追加をせず、自然で温かいpodcastの"
    "ナレーターの声でそのまま読み上げてください。\n\n"
)


def generate_charon_japanese_minimal_instruction(
        text: str, out_path: str,
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01(既定
        # "structured_separation"で既存挙動とbyte-identical)。
        tts_backend: str = "structured_separation") -> dict:
    # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: fallback経路もStructured
    # Separationを適用する(instruction内容・text内容は無変更)。
    # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
    # (声・モデルはp7a.make_tts_call_fn_for_modelと同一)。
    # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01: 既定
    # backendでは上記2行とbyte-identical。
    import er033_tts_flash_lite_backend_wiring_01 as flw
    call_fn, prompt = flw.resolve_tts_call_and_prompt(
        text, MINIMAL_INSTRUCTION_PREFIX_JA, p9a.JAPANESE_MODEL_NAME, CHARON, out_path, tts_backend=tts_backend,
        build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=batch_wiring.make_batch_tts_call_fn)
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"minimal instructionでもTTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
            "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
            "instruction": "minimal (not JAPANESE_STYLE_PREFIX)", "tts_backend": tts_backend,
            "model": flw.resolve_actual_model_name(p9a.JAPANESE_MODEL_NAME, tts_backend)}


@review_lock.guarded_generate("ja")
def generate_charon_japanese(text: str, out_path: str, expected_substring: str,
                              max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
                              standard_attempts: int = review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS,
                              expected_readings: dict | None = None,
                              # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01
                              # (2026-09-27、既定"structured_separation"で既存挙動と
                              # byte-identical): Family X runnerのみが明示的に
                              # "speech_metadata_flash_lite"を渡す。
                              tts_backend: str = "structured_separation") -> dict:
    """JAPANESE_STYLE_PREFIX経路、voice=Charon。既存generate_narration_
    snippet_verified_strictと同じ判定方式(部分一致+長さ)を使うが、
    voiceだけCharonへ差し替える(p9a.generate_narration_snippetは
    voice固定のため直接組み立てる)。標準経路がstandard_attempts回で
    合格しない場合、minimal instructionへフォールバックする(声・モデルは
    変えない、テキストも変えない。ER-003-N3-ROOT-FIX-01)。

    ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25(2026-09-04、
    ユーザー正式決定): 標準経路には常にstandard_attempts回(既定
    PRODUCTION_STANDARD_TTS_ATTEMPTS=2)しか予算を与えない。以前は
    「標準経路にmax_attempts回すべてを使わせ、fallbackには残り予算」
    という設計(ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B)だったが、
    標準経路が早期returnせず最後まで回ると`len(attempts_log)==
    max_attempts`になるため、fallback予算が構造的に常に0になり
    minimal instructionが実質的に発火しない不具合があった(日本語側で
    実Production incident 2件を確認)。fallback側の予算計算式自体は
    変えず(`max_attempts - len(attempts_log)`)、標準経路の消費量を
    standard_attempts回に固定することで、既定値では必ず
    PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS(1)回分がfallbackへ残る。
    ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-FINAL-26(2026-09-04、
    ユーザー正式決定・上記25の方針を撤回): wiring-25では「callerが
    max_attemptsに6・10等を渡す既存呼び出し元(共有shared segment・
    過去の個別対症療法script等)のtotal予算は縮小しない」としていたが、
    これは対象Production経路(標準+fallbackの2段構成を持つ本関数)に
    ついて「例外なくTOTAL3回上限に統一する」というユーザーの再確認済み
    正式仕様と矛盾するため、今回撤回する。callerが何を渡しても、この
    関数自身がmax_attemptsをPRODUCTION_MAX_TTS_ATTEMPTS(3)で上限
    クランプすることで、fallback予算(`max_attempts - len(attempts_log)`)
    が3を超えて発火する余地を構造的に無くす(共有shared segment
    (ensure_fixed_japanese_segment)・過去の一回限りscript
    (er003_v1_iran01_b1_kp_homophone_fix.py)を含め例外なし)。"""
    import er033_tts_flash_lite_backend_wiring_01 as flw
    max_attempts = min(max_attempts, review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)
    max_len = len(text) + 15
    attempts_log = []
    for attempt in range(1, standard_attempts + 1):
        # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
        # (声・モデルはp7a.make_tts_call_fn_for_modelと同一)。
        # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: build_tts_prompt()経由
        # にする(以前は直接連結、Structured Separationの抜け穴だった)。
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01: 既定
        # backendでは上記2行とbyte-identical。
        call_fn, prompt = flw.resolve_tts_call_and_prompt(
            text, p9a.JAPANESE_STYLE_PREFIX, p9a.JAPANESE_MODEL_NAME, CHARON, out_path, tts_backend=tts_backend,
            build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=batch_wiring.make_batch_tts_call_fn)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        if not ok:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err)})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE, safety_margin_seconds=SAFETY_MARGIN)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間検出失敗"})
            continue
        # ER-005-AUDIO-WASTE-REDUCTION-01: hallucination(指示文の
        # パラフレーズ等、無関係な内容の生成)を疑わせる異常長音声を、
        # ASR実行前に検知して破棄する(kp5_ja実例: 数秒のはずが100秒超)。
        anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "ja")
        if anomaly["is_anomaly"]:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": anomaly["reason"], "duration_anomaly": anomaly})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, err2 = routing.transcribe(out_path, language="ja-JP")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        # ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01: 旧prefix+length
        # (文頭一致+文字数)方式を廃止し、全文sequence比較+Protected Check
        # (数字/否定/内容語/固有名詞)による新Validatorを使う。固有名詞・
        # 略語らしき語のみの差はTTSを再生成せず、Cascade(Primary#2->
        # Secondary Azure#1->#2)で同じ音声のASRだけをやり直す。
        verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
            text, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI,
            expected_readings=expected_readings, length_ok=length_ok)
        verified = verified_content and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "length_ok": length_ok, "audio_classification": cls.classification,
                              # OPEN-258 SCG証跡(TRUE_CONTENT_MISMATCH時のみ非None)
                              "scg_info": getattr(cls, "scg_info", None),
                              "verified": verified, "trim_info": trim_info})
        # ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01: このattemptで
        # out_pathへ実際に書き込まれた音声を、上書きせず個別保存する。
        _attempt_audio_path = review_lock.save_tts_attempt_audio(out_path, "standard", {
            "loop_attempt_index": attempt, "max_attempts": max_attempts, "language": "ja",
            "model": flw.resolve_actual_model_name(p9a.JAPANESE_MODEL_NAME, tts_backend), "voice": CHARON,
            "tts_execution_mode": batch_wiring.resolve_tts_execution_mode(), "tts_backend": tts_backend,
            "asr_text": asr_text, "audio_classification": cls.classification,
            "length_ok": length_ok, "verified": verified,
            "scg_info": getattr(cls, "scg_info", None),
        })
        attempts_log[-1]["attempt_audio_path"] = _attempt_audio_path
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
                    "fallback_used": False, "tts_backend": tts_backend,
                    "model": flw.resolve_actual_model_name(p9a.JAPANESE_MODEL_NAME, tts_backend)}
        if stop_retrying:
            # ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part A: Cascadeが尽きて
            # 「これ以上retryしても解決しない」と判定した場合、TTSを再生成
            # せずここで打ち切る(英語側generate_english_segment_with_
            # fallback()と同じ契約)。従来はこの分岐がなく、attempt+1へ
            # 進んで無駄なTTS再生成を繰り返していた(bug)。
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": CHARON,
                    "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                    "trim_info": trim_info, "fallback_used": False,
                    "reason": f"ASR Cascadeを尽くしても解決せず、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification})"}

    fallback_attempts = []
    fallback_budget = max(0, max_attempts - len(attempts_log))
    for attempt in range(1, fallback_budget + 1):
        r = generate_charon_japanese_minimal_instruction(text, out_path, tts_backend=tts_backend)
        if r.get("status") != "OK":
            fallback_attempts.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err2 = routing.transcribe(out_path, language="ja-JP")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
            text, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI,
            expected_readings=expected_readings, length_ok=length_ok)
        verified = verified_content and length_ok
        fallback_attempts.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                                   "length_ok": length_ok, "audio_classification": cls.classification,
                                   "scg_info": getattr(cls, "scg_info", None),
                                   "verified": verified})
        # ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01: このattemptで
        # out_pathへ実際に書き込まれた音声を、上書きせず個別保存する。
        _attempt_audio_path = review_lock.save_tts_attempt_audio(out_path, "minimal_fallback", {
            "loop_attempt_index": attempt, "max_attempts": max_attempts, "language": "ja",
            "model": flw.resolve_actual_model_name(p9a.JAPANESE_MODEL_NAME, tts_backend), "voice": CHARON,
            "tts_execution_mode": batch_wiring.resolve_tts_execution_mode(), "tts_backend": tts_backend,
            "asr_text": asr_text, "audio_classification": cls.classification,
            "length_ok": length_ok, "verified": verified,
            "scg_info": getattr(cls, "scg_info", None),
        })
        fallback_attempts[-1]["attempt_audio_path"] = _attempt_audio_path
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = attempts_log
            r["fallback_attempts_log"] = fallback_attempts
            return r
        if stop_retrying:
            r["status"] = "ASR_VALIDATION_UNCERTAIN"
            r["asr_verified"] = False
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = attempts_log
            r["fallback_attempts_log"] = fallback_attempts
            r["reason"] = (f"ASR Cascadeを尽くしても解決せず、retryでの改善が見込めないため打ち切り"
                           f"(最終classification={cls.classification})")
            return r
    return {"status": "STOPPED",
            "reason": f"標準経路{len(attempts_log)}回+fallback経路{len(fallback_attempts)}回"
                      f"(合計上限{max_attempts}回)とも不合格",
            "standard_attempts_log": attempts_log, "fallback_attempts_log": fallback_attempts}


def main():
    with open(f"{OUT_DIR}/article/support_texts.json", encoding="utf-8") as f:
        support = json.load(f)  # noqa: F841 (未使用、Support本文は無変更のため参照のみ)
    with open(f"{OUT_DIR}/audit/article_parts.json", encoding="utf-8") as f:
        parts = json.load(f)
    with open(f"{OUT_DIR}/keyphrases/keywords_canonicalized.json", encoding="utf-8") as f:
        kp = json.load(f)
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])

    jobs_english = {
        "welcome": "Welcome to English Your Way.",
        "topic_intro": "Today's topic is Sam Altman Says We're in the Singularity. Not Everyone Agrees.",
        "preview_intro": "Here's a quick preview.",
        "point_explanation_en": "Here's the point.",
        "key_phrases_intro": "Here are today's key phrases.",
        "full_story_intro": "Now, the full story.",
        "num_one": "One.", "num_two": "Two.", "num_three": "Three.", "num_four": "Four.", "num_five": "Five.",
        "point_one_heading": "Point One.",
        "point_two_heading": "Point Two.",
        "point_one": f"{parts['point_one_heading']}. {parts['point_one_body']}",
        "point_two": f"{parts['point_two_heading']}. {parts['point_two_body']}",
        "in_one_line": parts["in_one_line"],
    }

    results = {}
    for name, text in jobs_english.items():
        print(f"[VOICE01] {name}(Charon)生成: {text[:40]!r}...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = generate_charon_english(text, out_path)
        results[name] = r
        print(f"[VOICE01] {name}: status={r.get('status')}")

    for item in kp_items:
        rank = item["rank"]
        ja_gloss = item["japanese_gloss"]
        ja_tts_text = ja_gloss.lstrip("～~・")
        name = f"kp{rank}_ja"
        print(f"[VOICE01] {name}(Charon)生成: {ja_tts_text!r}...")
        out_path = f"{NARRATION_DIR}/{name}_charon.wav"
        r = generate_charon_japanese(ja_tts_text, out_path, ja_tts_text[:4])
        results[name] = r
        print(f"[VOICE01] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/voice01_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    if failed:
        print(f"[VOICE01] 生成失敗segmentあり: {failed}")
    else:
        print("[VOICE01] 全件成功。")


if __name__ == "__main__":
    main()
