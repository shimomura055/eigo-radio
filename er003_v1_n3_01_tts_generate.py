# ============================================================
# er003_v1_n3_01_tts_generate.py
# ER-003-A2-B1-N3-01: 3テーマ×2レベル 全segment TTS/ASR生成
# ============================================================
# 既存の確立済み生成関数をそのまま再利用する(新しいTTS instructionは
# 設計しない):
#   B1 Charon英語: voice01.generate_charon_english
#   B1/共通 Aoede英語(News本文・Point見出し): news_tail_fix.
#     generate_news_narration_wide_margin / point_headings.generate
#   Key Phrase英語Component: repro01.generate_key_phrase_component_verified
#   Charon日本語+reading-safety: to_tts_safe_japanese_fraction_reading()
#     を通したうえでvoice01.generate_charon_japanese
#   A2英語(単一Aoede): crosslevel_audio_02_common.
#     generate_english_segment_with_fallback
#   A2日本語(単一Aoede、reading-safety経由): repro01.
#     generate_narration_snippet_verified_strict(language="ja")相当を
#     reading-safety wrapperでラップ
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_tts_generate.py <theme_id>
#   (theme_idを省略すると3テーマ全部を実行)

from __future__ import annotations

import json
import os
import sys

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_articles_generate as gen
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er011_human_review_lock_01 as review_lock
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_batch_tts_wiring_01 as batch_wiring
import er007_ja_secondary_asr_01 as ja_secondary
import er003_b1_p9a_audio as p9a
import er006_preprod_hardening_01_validation as en_validator
import er006_secondary_asr_01 as secondary_asr
import er008_a2_postprocess_slowdown_01 as a2_slowdown

# ============================================================
# ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06 Part G: A2英語のみ、
# 既存のemotion/prosody指示(ENGLISH_STYLE_PREFIX)はそのまま維持し、
# 末尾に「わずかに遅く、自然に」という自然言語の追加指示だけを足す
# (数値WPM指定・90%等のspeed factor指定はしない)。B1にはこの追加指示を
# 一切渡さない(B1側の呼び出しはstyle_prefix_overrideを渡さないため、
# 常にENGLISH_STYLE_PREFIXそのまま=無変更)。fallback(minimal
# instruction)経路にも渡さない(generate_english_segment_with_fallback
# 側で明示的に除外済み)。
#
# **補足(2026-08-26、ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11)**:
# ER-008-A2-SPEED-SAME-TEXT-ABC-09のsame-text比較で、この自然言語
# instruction単体では安定した減速効果が出ない(B/CともAより速くなる)
# ことが判明した。そのため下記のPOST-PROCESS(6% time-stretch)を
# 追加したが、ユーザーが試聴・承認したER-008-A2-TIMESTRETCH-ABC-10の
# 音声は「この既存instructionで生成された音声」に6% time-stretchを
# 重ねたものであり、instructionを取り除いたものではない。従って
# このinstructionはPOST-PROCESS方式と併用する形でProduction配線を
# 継続する(単独では置き換えにならない、承認された組み合わせを正確に
# 再現するため)。
A2_SLOWER_PACE_INSTRUCTION = (
    "\nSpeak at a slightly slower, relaxed pace than natural adult narration, while "
    "keeping the delivery smooth, conversational, and natural. Do not exaggerate pauses "
    "or sound instructional.\n"
)
A2_ENGLISH_STYLE_PREFIX_SLOWER = p9a.ENGLISH_STYLE_PREFIX + A2_SLOWER_PACE_INSTRUCTION
common.assert_no_wpm_specification(A2_ENGLISH_STYLE_PREFIX_SLOWER)

# ============================================================
# ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19 Item 5-B: B1 Previewの
# 話し方調整(ユーザー試聴・正式採用済み)。No.8 B1 Previewが他segmentより
# 明確に速い(実測184.5 WPM相当)ことが判明したが、B1にはA2のような
# segment別の速度差別化instructionが一切存在しなかった(現状調査で確認)。
# A2と同じ「自然言語のみ、数値WPM指定はしない」方針を踏襲し、落ち着いた
# トーンを追加する(Full Story/Point/In One Line等の本文Aoede音声には
# 適用しない)。
# ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20: ユーザー
# 正式決定により、同じstyle instructionをComment1-4にも適用対象拡大した
# ため、"this introduction"という限定的な文言を汎用的な文言へ変更。
B1_PREVIEW_CALM_INSTRUCTION = (
    "\nSpeak this in a calm, clear, unhurried tone, giving the listener "
    "time to take in what you are saying, while keeping the delivery natural and "
    "conversational (not slow or robotic).\n"
)
B1_PREVIEW_STYLE_PREFIX_CALM = p9a.ENGLISH_STYLE_PREFIX + B1_PREVIEW_CALM_INSTRUCTION
common.assert_no_wpm_specification(B1_PREVIEW_STYLE_PREFIX_CALM)

# ============================================================
# ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11: A2の「わずかに遅く」に、生成後
# のpost-processing(FFmpeg pitch-preserving time-stretch、6%減速)を
# 追加する。ER-008-A2-TIMESTRETCH-ABC-10でユーザーが試聴の上6%を正式
# 採用した(採用対象は「既存のA2_ENGLISH_STYLE_PREFIX_SLOWER instruction
# で生成された音声」+「6% time-stretch」の組み合わせであり、instruction
# は引き続き使用する)。成功した音声にのみ後段でtime-stretchを適用する。
# time-stretch前の音声は"{name}_original.wav"として保持し、Middle等で
# 現状より速い読み上げが必要な場合にTTS再生成なしで再利用できるように
# する(ユーザー承認時の指摘)。
A2_SLOWDOWN_TARGET_SEGMENTS = (
    "point_one_heading", "point_two_heading",
    "full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line",
)


def apply_a2_slowdown_postprocess(name: str, narration_dir: str, tts_input_text: str, result: dict) -> dict:
    """generate_english_segment_with_fallback()が返した通常ペースの
    結果(status=="OK")に対し、6% time-stretchを適用し、post-process後の
    音声を実際にASRで再検証した上でresultを更新する。post-process後の
    音声がASR不一致になった場合はstatus="STOPPED"とし、既存のAudio
    Validation Gateが正しくブロックできるようにする(未検証音声を
    黙ってPASS扱いにしない、という既存方針を維持)。"""
    if result.get("status") != "OK":
        return result  # 元々失敗している場合はslowdownを試みない

    out_path = f"{narration_dir}/{name}.wav"
    original_path = f"{narration_dir}/{name}_original.wav"
    import shutil
    shutil.copyfile(out_path, original_path)

    stretch_info = a2_slowdown.apply_a2_slowdown(original_path, out_path)

    asr_text, err = routing.transcribe(out_path, language="en-US")
    if err:
        result["status"] = "STOPPED"
        result["reason"] = f"post-process(6%減速)後の音声でASR取得に失敗: {err}"
        result["slowdown_info"] = stretch_info
        return result

    classification = en_validator.classify_asr_match(tts_input_text, asr_text)
    result["original_path"] = original_path
    result["slowdown_applied"] = True
    result["slowdown_info"] = stretch_info
    result["post_slowdown_asr_text"] = asr_text
    result["post_slowdown_classification"] = classification.classification
    # trim_info/duration_secondsはslowdown前の値のままだと実際の最終
    # 音声(narration/{name}.wav)の長さと食い違う(過去のtaskで発見・
    # 記録した既知のデータ不整合パターンを未然に防ぐ)。time-stretch比率
    # で比例配分し、最終音声の実際の長さと一致させる。
    stretch_ratio = stretch_info["dst_duration_seconds"] / stretch_info["src_duration_seconds"]
    if result.get("trim_info"):
        ti = result["trim_info"]
        for key in ("raw_duration_seconds", "trimmed_duration_seconds",
                    "leading_margin_retained_seconds", "trailing_margin_retained_seconds",
                    "raw_leading_silence_seconds", "raw_trailing_silence_seconds"):
            if key in ti and ti[key] is not None:
                ti[key] = round(ti[key] * stretch_ratio, 3)
    if result.get("duration_seconds") is not None:
        result["duration_seconds"] = round(result["duration_seconds"] * stretch_ratio, 3)
    # ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22: sha256はslowdown前の
    # 標準生成直後に一度だけ設定され、その後time-stretchでout_pathの中身が
    # 差し替わってもここまで再計算されていなかった(duration_seconds/
    # trim_infoは上で比例配分しているのに、sha256だけ取り残されていた)。
    # ER-21で追加したAssemble Gateの`_segment_asset_hash_stale()`(記録済み
    # sha256と実ファイルの突き合わせ)が、A2のslowdown対象segmentを再生成
    # するたび必ずASSET_HASH_MISMATCHで誤ってblockしてしまうbugをNo.8実
    # データ(full_story_part1/2の再生成)で発見した。post-process後の実際の
    # ファイルでsha256を再計算する。
    if result.get("sha256") is not None:
        result["sha256"] = p9a.sha256_file(out_path)
    # ER-008-N8-QA-CONTENT-SPEED-HARDENING-18: No.8 A2 point_one_headingの
    # 修復作業中に発見。post-process後の再検証はここまで`classification.
    # should_pass`のみで判定しており、ER-008-ASR-VARIANT-HARDENING-AND-
    # RETRY-15で導入したhomophone等価判定(is_homophone_candidate_mismatch、
    # 例: wait/weight)がこの経路には配線されていなかった(Cascade側には
    # 配線済みだったが、こちらは独立した再検証コードパスだったため)。
    # 同じ既存判定関数をそのまま再利用し、新規ロジックは追加しない。
    homophone_accepted = secondary_asr.is_homophone_candidate_mismatch(classification)
    if classification.should_pass or homophone_accepted:
        result["asr_verified"] = True
        result["asr_text"] = asr_text
        if homophone_accepted:
            result["post_slowdown_homophone_accepted"] = True
    else:
        result["status"] = "STOPPED"
        result["asr_verified"] = False
        result["reason"] = (f"post-process(6%減速)後の音声がASR再検証で不一致: "
                             f"classification={classification.classification}")
    return result


def generate_a2_segment_with_slowdown(tts_input: str, out_path: str, expected_substring: str,
                                        max_extra_chars: int = 60, max_slowdown_attempts: int = 3,
                                        style_prefix_override: str = None,
                                        # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: Point見出し/
                                        # In One Line等、短文でpartial repetitionが目立ちやすい
                                        # segmentのみ呼び出し側からTrueを渡す(既定Falseで
                                        # full_story/point本文等の既存挙動には影響しない)。
                                        disfluency_qa: bool = False) -> dict:
    """通常ペースでの生成(generate_english_segment_with_fallback、既存の
    standard/fallback retry込み)→6% time-stretch→post-process後ASR
    再検証、を1セットとして扱い、post-process後の再検証だけが不一致に
    なった場合は最大max_slowdown_attempts回、通常ペースから取り直す
    (実運用で判明した既知の事象: time-stretch自体が稀に語尾の子音や
    近縁語[例: "shared seating"→"hot-desking"のような文脈的な誤認識]の
    ASR誤認識を誘発することがあり、取り直したTTSテイクでは再現しない
    ことを確認済み。既存の他ステップと同じ「ASR不一致は即座に諦めず、
    まず取り直す」という方針を踏襲する)。

    style_prefix_override(既定None): ER-008-A2-TIMESTRETCH-ABC-10で
    ユーザーが試聴・承認したのは「既存の`A2_ENGLISH_STYLE_PREFIX_SLOWER`
    (自然言語の『わずかに遅く』instruction)で生成された現行Production
    音声」に6% time-stretchを重ねたものであり、instruction単体を除去した
    音声ではない。そのため、この関数を呼ぶ側は引き続き
    `A2_ENGLISH_STYLE_PREFIX_SLOWER`を渡し、承認された組み合わせ
    (instruction + 6% time-stretch)を正確に再現すること(instruction
    自体の単独効果がsame-text比較[ABC-09]で不安定だったことは、
    instructionを外してよい理由にはならない、ユーザーが実際に聴いて
    承認したのはinstructionを含む音声である)。"""
    narration_dir = out_path.rsplit("/", 1)[0]
    name = out_path.rsplit("/", 1)[1].removesuffix(".wav")
    slowdown_attempts_log = []
    result = None
    for attempt in range(1, max_slowdown_attempts + 1):
        result = c.generate_english_segment_with_fallback(
            tts_input, out_path, expected_substring, max_extra_chars=max_extra_chars,
            style_prefix_override=style_prefix_override, disfluency_qa=disfluency_qa)
        if result.get("status") != "OK":
            break  # 通常ペース自体が失敗(既存のstandard/fallback両方exhausted)
        result = apply_a2_slowdown_postprocess(name, narration_dir, tts_input, result)
        slowdown_attempts_log.append({
            "attempt": attempt, "status": result.get("status"),
            "post_slowdown_classification": result.get("post_slowdown_classification"),
        })
        if result.get("status") == "OK":
            break
    result["slowdown_attempts_log"] = slowdown_attempts_log
    return result

# ER-006-POOL-PREPROD-HARDENING-01: segment単位のCost Telemetry。
# cl.install()が呼ばれていない通常実行(cost logger未インストール時)は
# cl.segment_context()が_CONTEXT辞書を書き換えるだけで何もログしないため、
# 生成ロジック・retry回数・音声出力には一切影響しない。

JAPANESE_TITLES = {
    "hanshin": "早い先制、そして危なげない勝利。阪神が広島に8対1で完勝",
    "health": "小さな習慣の積み重ねは、健康にどう関係するのか",
    "household": "冷蔵庫の野菜室、2つの設定を使い分けると食品が長持ちする",
}


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def generate_charon_japanese_with_reading_safety(text: str, out_path: str, expected_substring: str,
                                                   max_attempts: int = 6, known_key_phrase_terms=None) -> dict:
    placeholder_safe = tts_safe_ja(text)
    # ER-006-KP5-CANONICAL-BUG-01: 先頭以外に残った項変数記法(「〜」「…」等)は
    # 機械的に削除すると文法が壊れるため、TTS呼び出し自体を行わずSTOPPEDで
    # 止める(gloss自体の再生成・手動修正が必要であることを明示する)。
    placeholder_check = safety.detect_gloss_placeholder_notation(placeholder_safe)
    if placeholder_check["has_placeholder"]:
        return {
            "status": "STOPPED",
            "reason": f"canonical_textに未発話のplaceholder記号が残っています: {placeholder_check['found_chars']}",
            "canonical_text": text,
            "placeholder_check": placeholder_check,
        }
    # ER-009-JA-FOREIGN-TOKEN-GATE-01: 制作内部ラベル("Part 1"等)や未対応の
    # 外来語表記がcanonical textに残っていないかを、TTS呼び出し前に検出する。
    # HUMAN_REVIEW相当の確信が持てる場合のみTTS呼び出し自体を行わずSTOPPED
    # で止める(カテゴリ1〜3は検出・記録のみに留め、生成をブロックしない)。
    foreign_token_findings = safety.classify_foreign_tokens_in_japanese_text(
        placeholder_safe, known_key_phrase_terms=known_key_phrase_terms)
    if safety.foreign_token_gate_requires_stop(foreign_token_findings):
        safety.log_foreign_token_human_review(text, out_path, foreign_token_findings)
        return {
            "status": "STOPPED",
            "reason": "canonical textに、言い換え・辞書対応・意図的英語発話のいずれとも機械的に判定できない"
                      "外来語/記号表記が残っています(Human Review待ち)。",
            "canonical_text": text, "foreign_token_findings": foreign_token_findings,
        }
    tts_input = safety.to_tts_safe_japanese_fraction_reading(placeholder_safe)
    r = voice01.generate_charon_japanese(tts_input, out_path, expected_substring, max_attempts=max_attempts)
    r["canonical_text"] = text
    r["tts_input_text_after_reading_safety"] = tts_input
    r["reading_safety_changed_text"] = (tts_input != text)
    if foreign_token_findings:
        r["foreign_token_findings"] = foreign_token_findings
    return r


# ER-003-N3-ROOT-FIX-01(2026-08-17): A2の短い日本語Key Phrase訳
# (meaning_N)も、B1のkp_ja_charonと同じ「短いフレーズ+長いJAPANESE_
# STYLE_PREFIX」の組み合わせで、voice01.generate_charon_japaneseと同種
# のinstruction leakageに晒されうる(標準経路はvoice=Aoede、
# c.generate_narration_snippet_verified_strict=repro01の同名関数の
# エイリアス)。voice01側に追加したのと同じ考え方のfallbackを、A2の
# Aoede経路にも用意する。
_A2_JA_MINIMAL_INSTRUCTION_PREFIX = (
    "次の文章だけを、翻訳・言い換え・追加をせず、自然で温かいpodcastの"
    "ナレーターの声でそのまま読み上げてください。\n\n"
)


def _generate_a2_japanese_minimal_instruction(text: str, out_path: str) -> dict:
    import er002_common as common
    import er003_b1_p3u_audio as p3u
    import er003_b1_p4c_audio as p4c
    import er003_b1_p9a_audio as p9a
    # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: fallback経路にもStructured
    # Separationを適用する。
    prompt = p4c.build_tts_prompt(text, _A2_JA_MINIMAL_INSTRUCTION_PREFIX)
    # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線
    # (声・モデルはp9a._make_japanese_call_fn()と同一)。
    call_fn = batch_wiring.make_batch_tts_call_fn(p9a.JAPANESE_MODEL_NAME, p9a.VOICE_NAME, output_path=out_path)
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"minimal instructionでもTTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    # ER-005-E2E-TTS-ANALYSIS-FIX-01: 他のA2 fallback経路と揃えて
    # NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS(0.35秒)を明示的に使う。
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    # ER-005-AUDIO-WASTE-REDUCTION-01: hallucinationを疑わせる異常長音声を
    # ASR実行前に検知して破棄する。
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "ja")
    if anomaly["is_anomaly"]:
        return {"status": "STOPPED", "reason": anomaly["reason"], "duration_anomaly": anomaly}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {"status": "OK", "text": text, "path": out_path, "trim_info": trim_info,
            "clipping_detected": metrics["clipping_detected"], "instruction": "minimal (not JAPANESE_STYLE_PREFIX)"}


def generate_a2_japanese_with_fallback(text: str, out_path: str, expected_substring: str,
                                        max_extra_chars: int = 40,
                                        max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS) -> dict:
    """標準経路(JAPANESE_STYLE_PREFIX)が合格しない場合、minimal
    instructionへフォールバックする(声・モデルは変えない)。
    ER-003-N3-ROOT-FIX-01: 短いA2日本語フレーズのinstruction
    leakage対策。

    ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B: standard経路+
    fallback経路の合計試行回数がmax_attempts回を超えないよう、fallback
    には残り予算のみを渡す。"""
    standard = c.generate_narration_snippet_verified_strict(
        text, "ja", out_path, expected_substring, max_attempts=max_attempts, max_extra_chars=max_extra_chars)
    if standard.get("status") == "OK":
        standard["fallback_used"] = False
        return standard
    if standard.get("status") == "HUMAN_REVIEW_LOCKED":
        # ER-011-HUMAN-REVIEW-COST-GUARD-01: standard経路がReview Lockで
        # ブロックされた場合、fallback(minimal instruction)経路へも
        # 進まない(fallbackは未ガードの直接TTS/ASR呼び出しのため、ここで
        # 通過させるとLockの意味が無くなる)。
        standard["fallback_used"] = False
        return standard

    max_len = len(text) + max_extra_chars
    fallback_attempts = []
    fallback_budget = max(0, max_attempts - len(standard.get("attempts_log") or []))
    for attempt in range(1, fallback_budget + 1):
        r = _generate_a2_japanese_minimal_instruction(text, out_path)
        if r.get("status") != "OK":
            fallback_attempts.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err = routing.transcribe(out_path, language="ja-JP")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        # ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01: 旧prefix
        # (substring)+phonetic方式から全文Validator+Cascade方式へ置き換える。
        verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
            text, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI)
        verified = verified_content and length_ok
        fallback_attempts.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                                   "audio_classification": cls.classification,
                                   "reading_resolver_info": getattr(cls, "reading_resolver_info", None),
                                   "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["audio_classification"] = cls.classification
            r["reading_resolver_info"] = getattr(cls, "reading_resolver_info", None)
            r["fallback_used"] = True
            r["standard_attempts_log"] = standard.get("attempts_log")
            r["fallback_attempts_log"] = fallback_attempts
            return r
        if stop_retrying:
            # ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 Part A: Cascadeが尽きて
            # 「これ以上retryしても解決しない」と判定した場合、TTSを再生成
            # せずここで打ち切る(英語側generate_english_segment_with_
            # fallback()と同じ契約)。従来はこの分岐がなく、attempt+1へ
            # 進んで無駄なTTS再生成を繰り返していた(bug)。
            r["status"] = "ASR_VALIDATION_UNCERTAIN"
            r["asr_verified"] = False
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = standard.get("attempts_log")
            r["fallback_attempts_log"] = fallback_attempts
            r["reason"] = (f"ASR Cascadeを尽くしても解決せず、retryでの改善が見込めないため打ち切り"
                           f"(最終classification={cls.classification})")
            return r
    return {"status": "STOPPED",
            "reason": f"標準経路{len(standard.get('attempts_log') or [])}回+fallback経路{len(fallback_attempts)}回"
                      f"(合計上限{max_attempts}回)とも不合格",
            "standard_attempts_log": standard.get("attempts_log"), "fallback_attempts_log": fallback_attempts}


def generate_a2_japanese_with_reading_safety(text: str, out_path: str, expected_substring: str,
                                              max_extra_chars: int = 40, max_attempts: int = 6,
                                              known_key_phrase_terms=None) -> dict:
    placeholder_safe = tts_safe_ja(text)
    # ER-006-KP5-CANONICAL-BUG-01: B1側(generate_charon_japanese_with_
    # reading_safety)と同じゲートをA2側にも適用する(japanese_title/
    # comment/Key Phrase meaning等、いずれもLLMが生成する短い日本語text
    # であり、辞書的な項変数記法が正当に必要になるケースはない)。
    placeholder_check = safety.detect_gloss_placeholder_notation(placeholder_safe)
    if placeholder_check["has_placeholder"]:
        return {
            "status": "STOPPED",
            "reason": f"canonical_textに未発話のplaceholder記号が残っています: {placeholder_check['found_chars']}",
            "canonical_text": text,
            "placeholder_check": placeholder_check,
        }
    # ER-009-JA-FOREIGN-TOKEN-GATE-01: 制作内部ラベル("Part 1"等)や未対応の
    # 外来語表記がcanonical textに残っていないかを、TTS呼び出し前に検出する
    # (この関数はgenerate_a2_japanese_with_fallback経由でminimal instruction
    # fallbackも内包するため、ここで1回チェックすれば両経路をカバーできる)。
    # HUMAN_REVIEW相当の確信が持てる場合のみTTS呼び出し自体を行わずSTOPPED
    # で止める(カテゴリ1〜3は検出・記録のみに留め、生成をブロックしない)。
    foreign_token_findings = safety.classify_foreign_tokens_in_japanese_text(
        placeholder_safe, known_key_phrase_terms=known_key_phrase_terms)
    if safety.foreign_token_gate_requires_stop(foreign_token_findings):
        safety.log_foreign_token_human_review(text, out_path, foreign_token_findings)
        return {
            "status": "STOPPED",
            "reason": "canonical textに、言い換え・辞書対応・意図的英語発話のいずれとも機械的に判定できない"
                      "外来語/記号表記が残っています(Human Review待ち)。",
            "canonical_text": text, "foreign_token_findings": foreign_token_findings,
        }
    tts_input = safety.to_tts_safe_japanese_fraction_reading(placeholder_safe)
    r = generate_a2_japanese_with_fallback(
        tts_input, out_path, expected_substring, max_attempts=max_attempts, max_extra_chars=max_extra_chars)
    r["canonical_text"] = text
    r["tts_input_text_after_reading_safety"] = tts_input
    r["reading_safety_changed_text"] = (tts_input != text)
    if foreign_token_findings:
        r["foreign_token_findings"] = foreign_token_findings
    return r


_EN_STRIP_PUNCT = ",.;:!?“”\"()[]"


def first_words(text: str, n: int = 4) -> str:
    # ASRは引用符・句読点を書き起こしに再現しないことが多いため、
    # 期待文字列側の各語からも同じ記号を取り除く(Health themeの
    # topic_intro/point_one_headingで実際に発生した偽陰性への対応)。
    # 綴られた小さな数もTTS入力側と同じく算用数字へ変換する(Household
    # themeのa2 topic_introで実際に発生した偽陰性: "Two"のままだと
    # TTS入力側で変換済みの"2"というASR書き起こしと一致しなかった)。
    # ER-005-AUDIO-WASTE-REDUCTION-01(2026-08-21)で発見: ハイフン複合語
    # ("parent-child")もASRはハイフンなしの分かち書き("parent child")で
    # 書き起こすことが多く、canonical text側にハイフンが残っていると
    # 常に不一致になる(A2 point_oneで実際に毎回発生し、無関係なTTS再
    # 生成を招いていたことを確認済み)。ハイフンをスペースへ置き換えて
    # から先頭n語を取る(語の欠落・置換ではなく表記統一のみ)。
    safe = tts_safe_number_words_en(tts_safe_en(text)).replace("-", " ")
    words = safe.strip().split()
    cleaned = [w.strip(_EN_STRIP_PUNCT) for w in words[:n]]
    return " ".join(w for w in cleaned if w)


# 既に確立済みの2件のTTS入力専用normalization(canonical textは変更しない):
#   (1) カーリーアポストロフィ(U+2019)→ストレートアポストロフィ
#       (ASRの書き起こしはストレートのみを認識するため、curly混在時に
#       単語トークン化がずれてASR一致検証が失敗する。ER-003-B1-
#       REDESIGN-AUDIO-01のpreview音切れ調査で確立済みのTTS入力限定の
#       置換をここでも再利用する)
#   (2) 先頭の「～」placeholder除去(ER-003-B1-REDESIGN-AUDIO-01系の
#       SING01 kp5で確立済み。「～」は発音されない記号であり、ASR側の
#       書き起こしにも現れないため、期待文字列側からも同じ規則で除去する)
def tts_safe_en(text: str) -> str:
    # カーリーシングル/ダブルクォートはASRの書き起こしに現れない
    # (発音されない記号のため)、期待文字列側からも取り除く。
    return text.replace("’", "'").replace("‘", "'").replace("“", "").replace("”", "")


# 追加で確立した2件のTTS入力専用normalization(Health themeで発見):
#   (3) 綴られた小さな数(two〜twelve)→算用数字。ASRは口頭の小さな数を
#       算用数字へ正規化して書き起こすことが多く(例: "two"→"2")、
#       canonical textが綴りのままだと単語トークンが一致せずASR一致
#       検証が失敗する。TTSは算用数字を渡しても綴りと同じ発音になる
#       ため、読み上げ内容には影響しない
#   (4) 段落区切り(空行)を単一の空白へ統合。空行の直後にcolon付きの
#       短いフレーズが続く構造(例: 数値の列挙)で、TTSが不自然な間を
#       置き、ASRが書き起こし上に余計な文区切りを挿入する事例が
#       Hanshin/Healthの両テーマで確認された。地の文として自然に
#       読める形にする(語は一切変更しない)
_EN_NUMBER_WORDS = {
    "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
}
# ER-010-NO9-TTS-NUMBER-WORDS-BUGFIX-AND-AUDIO-RETRY-16: `\b`は
# ハイフン「-」を単語境界とみなすため、修正前は"Forty-four"のような
# ハイフン複合数(20〜99台)の後半("four")だけを独立した数字語として
# 誤マッチし、"Forty-4"のように前半と後半で表記が割れて壊れたtextを
# 生成していた(No.9 A2/B1 point_twoのASR Validation偽陰性の真因、
# DECISION_LOG.md参照)。直前の文字がハイフンの場合はマッチさせない
# 否定後読み`(?<!-)`を追加し、ハイフン複合数は前半・後半とも変換せず
# 綴りのまま残す(この関数の対象はあくまで独立した小さな数であり、
# 複合数の同値判定はProduction ASR Validator側のnormalize_numeric()/
# _convert_cardinal_words()が既に正しく担っているため、ここで複合数を
# 部分的に壊さないことが唯一必要な修正)。
_EN_NUMBER_WORD_RE = __import__("re").compile(
    r"(?<!-)\b(" + "|".join(_EN_NUMBER_WORDS.keys()) + r")\b", flags=__import__("re").IGNORECASE)


def tts_safe_number_words_en(text: str) -> str:
    def _sub(m):
        return _EN_NUMBER_WORDS[m.group(1).lower()]
    return _EN_NUMBER_WORD_RE.sub(_sub, text)


def tts_safe_paragraphs_en(text: str) -> str:
    return " ".join(p.strip() for p in text.split("\n\n") if p.strip())


# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22: No.8 B1 full_story_part1
# ("Psychologist Stephen Reicher explains...")で、独立した4回のASR
# (OpenAI Primary x2、Azure Secondary x2)全てが"Steven Reichert"に近い
# 形で一貫して書き起こし、TTSが正しい発音で読み上げられていない疑いが
# 強い(単発のASR誤認識なら4回とも同じ方向へ揺れることは考えにくい)。
# 既存の固有名詞発音調査機構(Pronunciation Ledger research)により、
# 正しい発音はIPA /ˈraɪkər/("RY-ker"、Star Trekの"Riker"と同じ発音、
# 本人による発音訂正の記録あり、高確信度)と判明した。記事本文の表示用
# 綴り(article.md/parts.json)は正しい"Stephen Reicher"のまま変更せず、
# TTS入力・ASR比較対象のテキストにのみ、発音の近い実在の綴り"Riker"へ
# 差し替える(ER-010の日付safe-reading["April 28"→"April twenty
# eighth"]と同じ、表記と発話を分離する設計)。
_EN_NAME_PRONUNCIATION_OVERRIDES = {"Reicher": "Riker"}
_EN_NAME_PRONUNCIATION_RE = __import__("re").compile(
    r"\b(" + "|".join(_EN_NAME_PRONUNCIATION_OVERRIDES.keys()) + r")\b")


def tts_safe_name_pronunciation_en(text: str) -> str:
    return _EN_NAME_PRONUNCIATION_RE.sub(lambda m: _EN_NAME_PRONUNCIATION_OVERRIDES[m.group(1)], text)


def tts_safe_news_en(text: str) -> str:
    return tts_safe_name_pronunciation_en(tts_safe_number_words_en(tts_safe_paragraphs_en(tts_safe_en(text))))


# Key Phrase英語Componentの既知の失敗パターン(Health themeで発見):
# "healthspan"のような複合語はASRが"Health Span"と2語に分けて書き起こす
# ことが多く、"moderate-to-vigorous"のようなハイフン複合語はASRが
# ハイフンをスペースに正規化して書き起こす。generate_key_phrase_
# component_verified()は与えたtextそのものを比較対象に使うため、
# ハイフン→スペース・既知の複合語→分割語のnormalizationをTTS入力
# (かつ比較対象)として適用する。実際の発音はほぼ変わらない
_KP_COMPOUND_OVERRIDES = {"healthspan": "health span", "lifespan": "life span"}


def tts_safe_kp_en(text: str) -> str:
    safe = tts_safe_en(text).replace("-", " ")
    for compound, split in _KP_COMPOUND_OVERRIDES.items():
        safe = __import__("re").sub(compound, split, safe, flags=__import__("re").IGNORECASE)
    return safe


def tts_safe_ja(text: str) -> str:
    # ER-006-KP5-CANONICAL-BUG-01: 先頭のtilde placeholderは、実際に使われて
    # いる文字がU+FF5E(全角チルダ「～」)とU+301C(波ダッシュ「〜」)の
    # どちらであっても除去する(見た目がほぼ同じため、生成元によって
    # どちらが使われるかが揺れる。従来はU+FF5Eのみを対象にしており、
    # U+301Cを使う出力(kp5_ja等)を取りこぼしていた)。
    return text.lstrip("～〜").replace("’", "'")


_JA_KANJI_NUMERALS = set("一二三四五六七八九十百千万億〇")
_JA_PUNCTUATION = set("、。！？「」『』・…—―‥～")


def expected_substring_ja(text: str, n: int = 2) -> str:
    """先頭N文字を機械的に使うと、句読点(ASRが書き起こしで再現しない
    ことが多い)や漢数字(ASRが算用数字へ正規化することが多い)を含む
    ことがあり、実際には内容が正しいのに部分一致検証が偽陰性になる
    (このN3-01タスクのHanshin previewで実際に発生: 期待文字列
    "今回は、"の読点がASR書き起こしに現れず不一致になった)。句読点・
    漢数字・算用数字を含まない、最初の安全な連続N文字を探して使う。
    Health themeでは、2つの2文字語が連結した4文字語(例:「観察研究」)
    の自然な語境界にASRが読点を挿入する例が見つかったため、既定のNは
    その語境界をまたがない2文字とする(元は4→3で試したが、いずれも
    「観察」「研究」の境界をまたぐ3文字窓が選ばれ解決しなかった)。"""
    safe = tts_safe_ja(text)
    for i in range(len(safe) - n + 1):
        window = safe[i:i + n]
        if any(ch in _JA_PUNCTUATION or ch in _JA_KANJI_NUMERALS or ch.isdigit() for ch in window):
            continue
        return window
    return safe[:n]


# ============================================================
# B1 segment生成
# ============================================================
def generate_b1_segments(theme: dict) -> dict:
    theme_id = theme["theme_id"]
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")

    # ER-006-MASTER-AUDIO-STORE-01: 完全固定segment(welcome等)をMaster
    # Audio Store経由で取得する。既にStoreにmasterがあればTTSを呼ばず
    # narration_dirへコピーするだけ(_charon suffix、既存のcopy_b1_shared_
    # assets()と互換な命名)。
    shared_narration.ensure_all_shared_narration_b1(narration_dir)

    results = {}

    topic_intro_text = f"Today's topic is {parts['title']}."
    print(f"[N3-TTS][{theme_id}/b1b] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = voice01.generate_charon_english(
            tts_safe_number_words_en(tts_safe_en(topic_intro_text)), f"{narration_dir}/topic_intro.wav")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        print(f"[N3-TTS][{theme_id}/b1b] {name}生成(Charon、Connected Speech Validator配線済み)...")
        with cl.segment_context(name):
            # ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08:
            # OPEN-107 Ending-Clarity fallbackはユーザー正式決定によりProduction
            # から撤去した。代わりに、classify_asr_match()内でconnected-speech
            # パターン(歯擦音連続/破裂音連続/再分節)による再判定が働く
            # (er011_b1_connected_speech_validator_01、Trial-07でVALIDATED)。
            # ここでの呼び出し自体はvoice01.generate_charon_englishへの直接
            # 呼び出しに戻し、fallback wrapperは経由しない。
            results[name] = voice01.generate_charon_english(
                tts_safe_number_words_en(tts_safe_en(text)), f"{narration_dir}/{name}.wav",
                # ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20:
                # Previewで採用済みのcalm/clear/unhurried style instructionを
                # Comment1-4にも正式採用(ユーザー試聴・承認済み)。
                style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM,
                disfluency_qa=True)
        results[name]["canonical_text"] = text

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        # ER-005-E2E-TTS-ANALYSIS-FIX-01 Part D: Point番号ラベルが万一
        # 残っていた場合、TTS API呼び出し自体を行わずここで止める。
        sc.assert_no_point_number_label(text, name)
        print(f"[N3-TTS][{theme_id}/b1b] {name}生成(Aoede、semantic heading)...")
        with cl.segment_context(name):
            results[name] = point_headings.generate(
                tts_safe_number_words_en(tts_safe_en(text)), f"{narration_dir}/{name}.wav")
        results[name]["canonical_text"] = text

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        ("point_one", parts["point_one_body"]), ("point_two", parts["point_two_body"]),
        ("in_one_line", parts["in_one_line"]),
    ):
        if name in ("point_one", "point_two"):
            sc.assert_no_point_number_label(text, name)
        print(f"[N3-TTS][{theme_id}/b1b] {name}生成(Aoede、News本文、Connected Speech Validator配線済み)...")
        with cl.segment_context(name):
            # ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08:
            # OPEN-107 Ending-Clarity fallbackはユーザー正式決定によりProduction
            # から撤去した(news_tail_fix.py自体は無変更のまま直接呼び出す)。
            results[name] = news_tail_fix.generate_news_narration_wide_margin(
                tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
                # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: in_one_lineのみ対象
                # (full_story/point本文は「短文」対象外、承認済み範囲を超えない)。
                disfluency_qa=(name == "in_one_line"))
        results[name]["canonical_text"] = text

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[N3-TTS][{theme_id}/b1b] Key Phrase {rank} 英語Component生成(Aoede、Master Audio Store経由): {used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav")
        print(f"[N3-TTS][{theme_id}/b1b] Key Phrase {rank} 日本語meaning生成(Charon、reading-safety): {ja_gloss!r}...")
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = generate_charon_japanese_with_reading_safety(
                ja_gloss, f"{narration_dir}/kp{rank}_ja_charon.wav", expected_substring_ja(ja_gloss),
                known_key_phrase_terms=[used_form])
        kp_results[rank] = {"english": en_r, "japanese": ja_r}

    all_status = {k: v.get("status") for k, v in results.items()}
    kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                 for r, v in kp_results.items()}
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": results, "key_phrases": kp_results}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump({"segment_status": all_status, "key_phrase_status": kp_status}, f, ensure_ascii=False, indent=2)
    print(f"[N3-TTS][{theme_id}/b1b] 完了。segment_status={all_status} kp_status={kp_status}")
    return {"segment_status": all_status, "key_phrase_status": kp_status}


# ============================================================
# A2 segment生成
# ============================================================
def generate_a2_segments(theme: dict) -> dict:
    theme_id = theme["theme_id"]
    out_dir = f"{theme['out_dir']}/a2"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/a2_support_texts.json")
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")

    # ER-006-MASTER-AUDIO-STORE-01: B1と同じMasterAudioKey(level=None)を
    # 使うため、generate_b1_segments()が先に実行済みであれば、ここでは
    # TTSを一切呼ばずStoreからコピーするだけになる。
    shared_narration.ensure_all_shared_narration_a2(narration_dir)

    results = {}

    topic_intro_text = f"Today's topic is {parts['title']}."
    print(f"[N3-TTS][{theme_id}/a2] topic_intro生成(Aoede、A2既存単一Voice)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = c.generate_english_segment_with_fallback(
            tts_safe_number_words_en(tts_safe_en(topic_intro_text)), f"{narration_dir}/topic_intro.wav",
            first_words(parts["title"], 3), max_extra_chars=30)
    results["topic_intro"]["canonical_text"] = topic_intro_text

    ja_title = JAPANESE_TITLES[theme_id]
    print(f"[N3-TTS][{theme_id}/a2] japanese_title生成: {ja_title!r}...")
    with cl.segment_context("japanese_title"):
        results["japanese_title"] = generate_a2_japanese_with_reading_safety(
            ja_title, f"{narration_dir}/japanese_title.wav", expected_substring_ja(ja_title), max_extra_chars=30)

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        print(f"[N3-TTS][{theme_id}/a2] {name}生成(日本語)...")
        with cl.segment_context(name):
            results[name] = generate_a2_japanese_with_reading_safety(
                text, f"{narration_dir}/{name}.wav", expected_substring_ja(text))

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        # ER-005-E2E-TTS-ANALYSIS-FIX-01 Part D: Point番号ラベルが万一
        # 残っていた場合、TTS API呼び出し自体を行わずここで止める。
        sc.assert_no_point_number_label(text, name)
        tts_input = tts_safe_number_words_en(tts_safe_en(text))
        print(f"[N3-TTS][{theme_id}/a2] {name}生成(英語、semantic heading、わずかに遅く+6%減速)...")
        with cl.segment_context(name):
            results[name] = generate_a2_segment_with_slowdown(
                tts_input, f"{narration_dir}/{name}.wav", first_words(text, 3), max_extra_chars=20,
                style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=True)
        results[name]["canonical_text"] = text

    for name, text, sub in (
        ("full_story_part1", parts["part1"], first_words(parts["part1"])),
        ("full_story_part2", parts["part2"], first_words(parts["part2"])),
        ("point_one", parts["point_one_body"], first_words(parts["point_one_body"])),
        ("point_two", parts["point_two_body"], first_words(parts["point_two_body"])),
        ("in_one_line", parts["in_one_line"], first_words(parts["in_one_line"])),
    ):
        if name in ("point_one", "point_two"):
            sc.assert_no_point_number_label(text, name)
        tts_input = tts_safe_news_en(text)
        print(f"[N3-TTS][{theme_id}/a2] {name}生成(英語News本文、わずかに遅く+6%減速)...")
        with cl.segment_context(name):
            results[name] = generate_a2_segment_with_slowdown(
                tts_input, f"{narration_dir}/{name}.wav", sub, style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER,
                # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: in_one_lineのみ対象
                # (full_story/point本文は「短文」対象外、承認済み範囲を超えない)。
                disfluency_qa=(name == "in_one_line"))
        results[name]["canonical_text"] = text

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_results = {}
    for i, item in enumerate(kp_items, start=1):
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[N3-TTS][{theme_id}/a2] Key Phrase {rank} 英語Component生成(Aoede、Master Audio Store経由): {used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav")
        print(f"[N3-TTS][{theme_id}/a2] meaning_{i}生成(日本語): {ja_gloss!r}...")
        with cl.segment_context(f"kp{rank}_japanese_meaning"):
            ja_r = generate_a2_japanese_with_reading_safety(
                ja_gloss, f"{narration_dir}/meaning_{i}.wav", expected_substring_ja(ja_gloss), max_extra_chars=30,
                known_key_phrase_terms=[used_form])
        kp_results[rank] = {"english": en_r, "japanese_meaning": ja_r}

    all_status = {k: v.get("status") for k, v in results.items()}
    kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")}
                 for r, v in kp_results.items()}
    with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": results, "key_phrases": kp_results}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/run_summary_tts.json", "w", encoding="utf-8") as f:
        json.dump({"segment_status": all_status, "key_phrase_status": kp_status}, f, ensure_ascii=False, indent=2)
    print(f"[N3-TTS][{theme_id}/a2] 完了。segment_status={all_status} kp_status={kp_status}")
    return {"segment_status": all_status, "key_phrase_status": kp_status}


def run_theme(theme: dict) -> dict:
    b1_result = generate_b1_segments(theme)
    a2_result = generate_a2_segments(theme)
    return {"b1b": b1_result, "a2": a2_result}


def main():
    theme_ids = sys.argv[1:] or [t["theme_id"] for t in gen.THEMES]
    themes_by_id = {t["theme_id"]: t for t in gen.THEMES}
    for theme_id in theme_ids:
        run_theme(themes_by_id[theme_id])
    print("[N3-TTS] 完了。")


if __name__ == "__main__":
    main()
