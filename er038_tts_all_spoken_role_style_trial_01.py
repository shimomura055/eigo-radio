# ============================================================
# er038_tts_all_spoken_role_style_trial_01.py
# TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(Trial、Production実装なし)
# ============================================================
# 性質: Trial専用script。Production正式path(er0*.py既存ファイル、
# er033_tts_flash_lite_family_x_styles_01.py含む)は一切変更しない。
# 既存Flash-Lite Production関数(voice01/repro01/news_tail_fix/
# point_headings/crosslevel_common/n3_tts/shared_narration)を、
# style_prefix_override引数付きでそのまま呼ぶ(EN側は既存パラメータが
# 機能するためそのまま利用。JA側は既存パラメータが無い、または
# dead parameterであることを実測確認したため、最下層のTTS call関数
# [er033_tts_flash_lite_backend_wiring_01.resolve_tts_call_and_prompt]を
# 同じ引数で直接呼ぶ。詳細根拠はdocs/pm/design_tts_all_spoken_role_
# style_trial_01.md §4参照)。
#
# Master Audio Storeは本script専用path(--out-dir配下)へ実行時に
# モンキーパッチで隔離する(er006_master_audio_store_01.py自体は無変更、
# Production Store[er006_output/master_audio_store_01/]は一切書き込まない)。
#
# 既存の記事・Key Phrase・共有narrationのcanonical textは
# --source-run配下の既存artifactをそのまま再利用する(新規記事生成・
# 新規Key Phrase選定は行わない)。
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as crosslevel_common
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_batch_tts_wiring_01 as batch_wiring
import er006_master_audio_store_01 as store
import er007_ja_secondary_asr_01 as ja_secondary
import er011_human_review_lock_01 as review_lock
import er019_family_x_audio_production_runner_01 as fx_runner
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er025_entity_pronunciation_resolver_core_01 as pron_resolver_core
import er033_tts_flash_lite_backend_wiring_01 as flw

MANAGEMENT_ID = "TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01"

# ------------------------------------------------------------
# Trial Role style表(docs/pm/design_tts_all_spoken_role_style_trial_01.md
# §3、既存6-roleは値を無変更のまま流用する)
# ------------------------------------------------------------
TRIAL_ROLE_STYLE_EN = {
    "TOPIC_INTRO": "brief, clear, engaging news topic introduction",
    "PREVIEW": "calm, conversational",
    "COMMENT": "calm, conversational",
    "FULL_STORY": "calm, steady news narration",
    "HEADING": "brief and clear",
    "IN_ONE_LINE": "concise, clear",
    "PROGRAM_SECTION_INTRO": "warm, brief, welcoming",
    "KEY_PHRASE_INTRO": "brief, clear, inviting",
    "FULL_STORY_INTRO": "brief, clear, transitional",
    "NUMBER_LABEL": "brief, clear, neutral",
    "KEY_PHRASE_EN": "clear, precise, unhurried",
    # 定義のみ(design doc §1-3): Advancedの英語解説テキストartifactが
    # 既存Production/Hormuz run_06のいずれにも存在しないため、本Trialでは
    # このRoleの実音声は生成しない(新規Key Phrase解説テキストの創作は
    # scope外)。
    "KEY_PHRASE_EXPLANATION_EN": "clear, precise, explanatory",
}

TRIAL_ROLE_STYLE_JA = {
    "PREVIEW": "落ち着いた、自然な話し言葉で",
    "COMMENT": "落ち着いた、自然な話し言葉で",
    "NUMBER_LABEL": "簡潔に、はっきりと",
    "TITLE": "はっきりと、聞き取りやすく",
    "KEY_PHRASE_JA": "はっきりと、落ち着いて",
}

for _role, _style in TRIAL_ROLE_STYLE_EN.items():
    common.assert_no_wpm_specification(_style)
for _role, _style in TRIAL_ROLE_STYLE_JA.items():
    common.assert_no_wpm_specification(_style)

# 全spoken segmentのRole割当表(design doc §2、Role漏れ0検証に使う)。
# キーはB1B/A2それぞれの実segment_id(narration_dir上のファイル名から
# 拡張子を除いたもの、KP/shared narrationは専用命名)。
SEGMENT_ROLE_MAP_B1B = {
    "topic_intro": "TOPIC_INTRO", "preview": "PREVIEW",
    "comment_1": "COMMENT", "comment_2": "COMMENT", "comment_3": "COMMENT", "comment_4": "COMMENT",
    "full_story_part1": "FULL_STORY", "full_story_part2": "FULL_STORY", "full_story_part3": "FULL_STORY",
    "full_story_part2_heading": "HEADING", "full_story_part3_heading": "HEADING",
    "in_one_line": "IN_ONE_LINE",
    "welcome": "PROGRAM_SECTION_INTRO", "preview_intro": "PROGRAM_SECTION_INTRO",
    "key_phrases_intro": "KEY_PHRASE_INTRO", "full_story_intro": "FULL_STORY_INTRO",
    "num_one": "NUMBER_LABEL", "num_two": "NUMBER_LABEL", "num_three": "NUMBER_LABEL",
    "num_four": "NUMBER_LABEL", "num_five": "NUMBER_LABEL",
    "kp_english": "KEY_PHRASE_EN", "kp_japanese": "KEY_PHRASE_JA",
}
SEGMENT_ROLE_MAP_A2 = dict(SEGMENT_ROLE_MAP_B1B)
SEGMENT_ROLE_MAP_A2.update({
    "japanese_title": "TITLE",
    "point_explanation": "NUMBER_LABEL",
    "kp_japanese_meaning": "KEY_PHRASE_JA",
})
del SEGMENT_ROLE_MAP_A2["kp_japanese"]

# ------------------------------------------------------------
# 修正1回目(ユーザー指示反映、delegation_log
# docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_03.md):
# num_two/num_three("Two."/"Three.")をTrial NUMBER_LABEL styleで毎回
# 再生成せず、Production Master Audio Store
# (er006_output/master_audio_store_01/、read-onlyで参照するのみ、一切
# 書き込まない)内の既存ASR verified OK Master(TTS-GEMINI-3.8-FLASH-LITE-
# PRODUCTION-WIRING-FAMILY-X-02 修正3回目[commit ee280e76]由来、
# FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]スタイル=
# SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION
# "v2_flash_lite_short_style"[er006_audio_cost_pilot_02_shared_narration.py])
# をコピーしてTrial内でreuseする。Master IDは
# er006_output/master_audio_store_01/manifest.jsonから実測特定した値
# (canonical_text_hash=sha256("Two."/"Three.")[:16]で一致確認済み)。
# ASR証跡("2"/"3")はer019_output配下の既存Production実測記録から引用
# (Trialで再ASRは行わない、追加API費用¥0)。
# ------------------------------------------------------------
PRODUCTION_MASTER_REUSE_SHELL_SEGMENTS = {
    "num_two": {
        "master_audio_id": "75d64a8e14e3b8592db99a5a",
        "audio_path": "er006_output/master_audio_store_01/audio/75d64a8e14e3b8592db99a5a.wav",
        "canonical_text": "Two.",
        "style_instruction_id": "charon_english_fixed_shell",
        "style_instruction_version": "v2_flash_lite_short_style",
        "tts_model_id": "gemini-3.8-flash-lite-tts",
        "asr_text_evidence": "2",
        "asr_evidence_source": (
            "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
            "hormuz__run_06_flashlite_full_kp/b1b/audit/tts_generation_results.json#segments.num_two"),
    },
    "num_three": {
        "master_audio_id": "410e12ebe93da7a797860b89",
        "audio_path": "er006_output/master_audio_store_01/audio/410e12ebe93da7a797860b89.wav",
        "canonical_text": "Three.",
        "style_instruction_id": "charon_english_fixed_shell",
        "style_instruction_version": "v2_flash_lite_short_style",
        "tts_model_id": "gemini-3.8-flash-lite-tts",
        "asr_text_evidence": "3",
        "asr_evidence_source": (
            "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
            "hormuz__run_06_flashlite_full_kp/b1b/audit/tts_generation_results.json#segments.num_three"),
    },
}


def _reuse_production_master_segment(reuse_entry: dict, out_path: str) -> dict:
    """Production Master Audio Store(read-only)の既存ASR verified OK
    master wavをコピーしてTrial側segmentとして使う。コピー先(out_path)
    のみ新規作成し、Production Store側ファイルは一切書き込まない
    (Human Review Lockの共有state[review_lock_state.json]もこの経路では
    一切呼ばないため無変更のまま)。"""
    src = reuse_entry["audio_path"]
    if not os.path.exists(src):
        return {
            "status": "STOPPED",
            "reason": f"reuse対象のProduction Master audioが見つかりません: {src}",
        }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    shutil.copyfile(src, out_path)
    with open(out_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    return {
        "status": "OK",
        "reused": True,
        "reused_from_production_master": True,
        "master_audio_id": reuse_entry["master_audio_id"],
        "production_master_audio_path": src,
        "production_style_instruction_id": reuse_entry["style_instruction_id"],
        "production_style_instruction_version": reuse_entry["style_instruction_version"],
        "production_tts_model_id": reuse_entry["tts_model_id"],
        "asr_text": reuse_entry["asr_text_evidence"],
        "asr_text_evidence_carried_forward": True,
        "asr_evidence_source": reuse_entry["asr_evidence_source"],
        "attempts_log": [],
        "sha256": sha256,
        "human_review_lock_state": "trial_reuse_substitutes_for_lock_resolution_not_unlocked",
        "note": ("Trial NUMBER_LABEL styleでの新規生成ではなく、Production合格Master"
                 "(FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]スタイル)をTrial内でreuseした"
                 "(TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 修正1回目、ユーザー指示)。"
                 "共有Human Review Lock state(review_lock_state.json)はこの経路では"
                 "変更していない(OPEN-223参照、Lock解除ではなくTrial内reuseでの代替)。"),
    }


def _summarize_shared_narration_with_reuse_detail(raw: dict) -> dict:
    """fx_runner._summarize_shared_narration()(Production共有関数、無変更)
    が返す必須field(status/reused/master_audio_id/asr_text/attempts)は
    そのまま維持しつつ、Production Master reuse(修正1回目)の追加証跡
    fieldをTrial側でだけ付加する。"""
    summary = fx_runner._summarize_shared_narration(raw)
    for name, r in raw.items():
        if r.get("reused_from_production_master"):
            summary[name].update({
                "reused_from_production_master": True,
                "production_master_audio_path": r.get("production_master_audio_path"),
                "production_style_instruction_id": r.get("production_style_instruction_id"),
                "production_style_instruction_version": r.get("production_style_instruction_version"),
                "production_tts_model_id": r.get("production_tts_model_id"),
                "asr_text_evidence_carried_forward": r.get("asr_text_evidence_carried_forward"),
                "asr_evidence_source": r.get("asr_evidence_source"),
                "human_review_lock_state": r.get("human_review_lock_state"),
                "note": r.get("note"),
            })
    return summary


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------
# Master Audio Store隔離(design doc §1-5/§4-3)
# ------------------------------------------------------------
@contextlib.contextmanager
def trial_master_audio_store(root_dir: str):
    """er006_master_audio_store_01.py自体は無変更のまま、モジュール
    グローバル定数(呼び出し時に動的解決される)を一時的に上書きし、
    Trial専用Storeへ完全に隔離する。Production Store
    (er006_output/master_audio_store_01/)は一切読み書きしない。"""
    orig = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
    store.STORE_DIR = root_dir
    store.AUDIO_DIR = f"{root_dir}/audio"
    store.MANIFEST_PATH = f"{root_dir}/manifest.json"
    store.TELEMETRY_PATH = f"{root_dir}/reuse_telemetry.jsonl"
    try:
        yield
    finally:
        store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH = orig


# ------------------------------------------------------------
# JA role-style生成(design doc §4-2): 既存の発音/記号/placeholder安全
# 処理・ASR Cascade・fallback関数は無変更のまま再利用する。styleの
# 差し込みだけを、既存パラメータが機能しない箇所(p9a.generate_
# narration_snippetのja分岐)を避けて最下層(resolve_tts_call_and_prompt)
# で行う。
# ------------------------------------------------------------
def _ja_reading_safety_preprocess(text: str, out_path: str, known_key_phrase_terms=None,
                                   source_context: str = "") -> dict:
    placeholder_safe = n3_tts.tts_safe_ja(text)
    placeholder_check = safety.detect_gloss_placeholder_notation(placeholder_safe)
    if placeholder_check["has_placeholder"]:
        return {
            "status": "STOPPED",
            "reason": f"canonical_textに未発話のplaceholder記号が残っています: {placeholder_check['found_chars']}",
            "canonical_text": text, "placeholder_check": placeholder_check,
        }
    symbol_findings = safety.detect_prohibited_symbols(placeholder_safe, language="ja")
    if safety.symbol_gate_requires_stop(symbol_findings):
        return {
            "status": "STOPPED",
            "reason": "canonical_textに音声化禁止記号が残っています(Normalizer通過後の残存): "
                      + ", ".join(f"{f['category']}:{f['token']}" for f in symbol_findings),
            "canonical_text": text, "symbol_findings": symbol_findings,
        }
    ja_pronunciation_resolver_info = pron_resolver_core.resolve_unknown_ja_tokens(
        placeholder_safe, known_key_phrase_terms=known_key_phrase_terms, context=text,
        source_context=source_context)
    foreign_token_findings = safety.classify_foreign_tokens_in_japanese_text(
        placeholder_safe, known_key_phrase_terms=known_key_phrase_terms,
        reading_dictionary=ja_pronunciation_resolver_info["reading_dictionary"])
    if safety.foreign_token_gate_requires_stop(foreign_token_findings):
        safety.log_foreign_token_human_review(text, out_path, foreign_token_findings)
        return {
            "status": "STOPPED",
            "reason": "canonical textに、言い換え・辞書対応・意図的英語発話のいずれとも機械的に判定できない"
                      "外来語/記号表記が残っています(Human Review待ち)。",
            "canonical_text": text, "foreign_token_findings": foreign_token_findings,
            "ja_pronunciation_resolver_info": ja_pronunciation_resolver_info,
        }
    tts_input = safety.to_tts_safe_japanese_fraction_reading(placeholder_safe)
    expected_readings = {
        f["token"].lower(): f["reading"] for f in foreign_token_findings
        if f.get("category") == safety.FOREIGN_TOKEN_READING_DICTIONARY and f.get("reading")
    } or None
    return {
        "status": "OK", "tts_input": tts_input, "expected_readings": expected_readings,
        "foreign_token_findings": foreign_token_findings,
        "ja_pronunciation_resolver_info": ja_pronunciation_resolver_info,
        "reading_safety_changed_text": (tts_input != text),
    }


def generate_ja_role_style(text: str, out_path: str, style_prefix: str, voice_name: str,
                            minimal_fallback_fn, tts_backend: str,
                            max_extra_chars: int = 15, known_key_phrase_terms=None, source_context: str = "",
                            max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
                            standard_attempts: int = review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS) -> dict:
    """既存generate_charon_japanese/generate_a2_japanese_with_fallbackと
    同じ「標準standard_attempts回+fallback(既存minimal instruction関数を
    無変更のまま再利用)」という3回上限契約を維持しつつ、標準経路のstyleを
    Trial Role styleへ差し替える。既知の簡略化(Trial限定): Human Review
    Lockデコレータ・attempt別音声個別保存は適用しない(design doc§4-2)。"""
    pre = _ja_reading_safety_preprocess(text, out_path, known_key_phrase_terms, source_context)
    if pre["status"] != "OK":
        return pre
    tts_input = pre["tts_input"]
    expected_readings = pre["expected_readings"]
    max_attempts = min(max_attempts, review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)
    max_len = len(tts_input) + max_extra_chars
    attempts_log = []

    for attempt in range(1, standard_attempts + 1):
        call_fn, prompt = flw.resolve_tts_call_and_prompt(
            tts_input, style_prefix, p9a.JAPANESE_MODEL_NAME, voice_name, out_path, tts_backend=tts_backend,
            build_tts_prompt=p4c.build_tts_prompt, make_batch_tts_call_fn=batch_wiring.make_batch_tts_call_fn)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        if not ok:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err)})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE,
            safety_margin_seconds=p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間検出失敗"})
            continue
        anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], tts_input, "ja")
        if anomaly["is_anomaly"]:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": anomaly["reason"],
                                  "duration_anomaly": anomaly})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, _ = routing.transcribe(out_path, language="ja-JP")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
            tts_input, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI,
            expected_readings=expected_readings)
        verified = verified_content and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text, "length_ok": length_ok,
                              "audio_classification": cls.classification, "verified": verified})
        if verified:
            metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
            with open(out_path, "rb") as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            return {
                "status": "OK", "text": text, "path": out_path, "voice": voice_name, "asr_verified": True,
                "asr_text": asr_text, "attempts_log": attempts_log, "trim_info": trim_info,
                "clipping_detected": metrics["clipping_detected"], "fallback_used": False,
                "tts_backend": tts_backend,
                "model": flw.resolve_actual_model_name(p9a.JAPANESE_MODEL_NAME, tts_backend),
                "style_prefix_used": style_prefix, "disfluency_checked": True, "sha256": sha256,
                "canonical_text": text, "tts_input_text_after_reading_safety": tts_input,
                "reading_safety_changed_text": pre["reading_safety_changed_text"],
                "ja_pronunciation_resolver_info": pre["ja_pronunciation_resolver_info"],
            }
        if stop_retrying:
            return {
                "status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": voice_name,
                "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                "trim_info": trim_info, "fallback_used": False, "style_prefix_used": style_prefix,
                "canonical_text": text,
                "reason": f"ASR Cascadeを尽くしても解決せず(最終classification={cls.classification})",
            }

    fallback_attempts = []
    fallback_budget = max(0, max_attempts - len(attempts_log))
    for attempt in range(1, fallback_budget + 1):
        r = minimal_fallback_fn(tts_input, out_path, tts_backend=tts_backend)
        if r.get("status") != "OK":
            fallback_attempts.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, _ = routing.transcribe(out_path, language="ja-JP")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
            tts_input, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI,
            expected_readings=expected_readings)
        verified = verified_content and length_ok
        fallback_attempts.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                                   "audio_classification": cls.classification, "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = attempts_log
            r["fallback_attempts_log"] = fallback_attempts
            r["style_prefix_used"] = "minimal_instruction(既存Production fallback、無変更)"
            r["canonical_text"] = text
            r["disfluency_checked"] = True
            r["voice"] = voice_name
            return r
        if stop_retrying:
            r["status"] = "ASR_VALIDATION_UNCERTAIN"
            r["asr_verified"] = False
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = attempts_log
            r["fallback_attempts_log"] = fallback_attempts
            r["canonical_text"] = text
            return r
    return {
        "status": "STOPPED",
        "reason": f"標準{len(attempts_log)}回+fallback{len(fallback_attempts)}回とも不合格",
        "standard_attempts_log": attempts_log, "fallback_attempts_log": fallback_attempts,
        "canonical_text": text,
    }


# ------------------------------------------------------------
# Shell(共有narration固定文)segment
# ------------------------------------------------------------
def _en_shell_role(name: str) -> str:
    if name in ("welcome", "preview_intro"):
        return "PROGRAM_SECTION_INTRO"
    if name == "key_phrases_intro":
        return "KEY_PHRASE_INTRO"
    if name == "full_story_intro":
        return "FULL_STORY_INTRO"
    return "NUMBER_LABEL"  # num_one..num_five


def generate_shell_segments(narration_dir: str, level: str, tts_backend: str,
                             reuse_production_master: frozenset = frozenset()) -> dict:
    """FIXED_ENGLISH_TEXTS/FIXED_JAPANESE_TEXTS_A2_ONLY(既存テキスト定数、
    無変更のまま再利用)をTrial Role styleで生成する。ensure_fixed_*_
    segment()は単一固定styleしか渡せないため使わず、同じ下位関数
    (voice01.generate_charon_english/独自JA generator)+Trial専用Store
    (store.get_or_generate)を直接呼ぶ。

    修正1回目(ユーザー指示反映): reuse_production_masterに名前が含まれる
    segment(現状num_two/num_threeのみ想定)は、Trial NUMBER_LABEL styleで
    新規生成せず、PRODUCTION_MASTER_REUSE_SHELL_SEGMENTSのProduction Master
    をread-onlyでコピーして使う(store.get_or_generateは呼ばない=Trial
    専用Storeへも書き込まない)。"""
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    suffix = "_charon" if level == "b1b" else ""
    for name, text in shared_narration.FIXED_ENGLISH_TEXTS.items():
        role = _en_shell_role(name)
        style = TRIAL_ROLE_STYLE_EN[role]
        out_path = f"{narration_dir}/{name}{suffix}.wav"
        reuse_entry = PRODUCTION_MASTER_REUSE_SHELL_SEGMENTS.get(name)
        if name in reuse_production_master and reuse_entry is not None and reuse_entry["canonical_text"] == text:
            results[name] = _reuse_production_master_segment(reuse_entry, out_path)
        else:
            key = store.MasterAudioKey(
                language="en", speaker_voice="Charon",
                tts_model_id=shared_narration._resolve_shared_narration_model("en", tts_backend),
                canonical_text=text, level=None,
                style_instruction_id=f"trial_role_style_{role.lower()}", style_instruction_version="v1_trial",
            )
            results[name] = store.get_or_generate(
                key, out_path,
                lambda p, text=text, style=style: voice01.generate_charon_english(
                    text, p, style_prefix_override=style, tts_backend=tts_backend))
        results[name]["canonical_text"] = text
        results[name]["role"] = role
        results[name]["style_prefix_used"] = style
    if level == "a2":
        for name, text in shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY.items():
            style = TRIAL_ROLE_STYLE_JA["NUMBER_LABEL"]
            out_path = f"{narration_dir}/{name}.wav"
            key = store.MasterAudioKey(
                language="ja", speaker_voice="Charon",
                tts_model_id=shared_narration._resolve_shared_narration_model("ja", tts_backend),
                canonical_text=text, level=None,
                style_instruction_id="trial_role_style_number_label_ja", style_instruction_version="v1_trial",
            )
            results[name] = store.get_or_generate(
                key, out_path,
                lambda p, text=text: generate_ja_role_style(
                    text, p, style, "Charon", voice01.generate_charon_japanese_minimal_instruction,
                    tts_backend))
            results[name]["canonical_text"] = text
            results[name]["role"] = "NUMBER_LABEL"
            results[name]["style_prefix_used"] = style
    return results


# ------------------------------------------------------------
# Key Phrase segment
# ------------------------------------------------------------
def generate_kp_segments(kp: dict, narration_dir: str, level: str, tts_backend: str) -> dict:
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_results = {}
    en_style = TRIAL_ROLE_STYLE_EN["KEY_PHRASE_EN"]
    ja_style = TRIAL_ROLE_STYLE_JA["KEY_PHRASE_JA"]
    for i, item in enumerate(kp_items, start=1):
        rank = item["rank"]
        used_form = item["used_form"]
        used_form_tts = n3_tts.tts_safe_kp_en(used_form)
        en_path = f"{narration_dir}/kp{rank}_en.wav"
        # 既存パラメータ無し(generate_key_phrase_component_verifiedは
        # style_prefix_overrideを公開しない、design doc§4-1)のため、
        # 最下層で使われている共有検証関数を同じ主要引数で直接呼ぶ。
        en_r = repro01.generate_narration_snippet_verified_strict(
            used_form_tts, "en", en_path, used_form_tts, max_extra_chars=10,
            max_attempts=2, safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
            style_prefix_override=en_style, disfluency_qa=True,
            asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT, enable_non_latin_cascade=True,
            tts_backend=tts_backend)
        en_r["canonical_text"] = used_form_tts
        en_r["role"] = "KEY_PHRASE_EN"
        en_r["style_prefix_used"] = en_style

        ja_gloss_tts, ja_gloss_tts_fallback = n3_tts.resolve_key_phrase_ja_gloss_tts(item)
        if level == "b1b":
            ja_path = f"{narration_dir}/kp{rank}_ja_charon.wav"
            ja_r = generate_ja_role_style(
                ja_gloss_tts, ja_path, ja_style, "Charon", voice01.generate_charon_japanese_minimal_instruction,
                tts_backend, max_extra_chars=15, known_key_phrase_terms=[used_form])
            ja_key = "japanese"
        else:
            ja_path = f"{narration_dir}/meaning_{i}.wav"
            ja_r = generate_ja_role_style(
                ja_gloss_tts, ja_path, ja_style, "Aoede", n3_tts._generate_a2_japanese_minimal_instruction,
                tts_backend, max_extra_chars=30, known_key_phrase_terms=[used_form])
            ja_key = "japanese_meaning"
        ja_r["display_gloss"] = item["japanese_gloss"]
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        ja_r["role"] = "KEY_PHRASE_JA"
        ja_r["style_prefix_used"] = ja_style
        kp_results[rank] = {"english": en_r, ja_key: ja_r}
    return kp_results


# ------------------------------------------------------------
# 主記事segment(B1B/A2)。generate_family_x_b1_segments/generate_family_x_
# a2_segments(er019_family_x_audio_production_runner_01.py)と同じ
# segment順序・同じtext source・同じdisfluency_qa/repetition_qa等の
# flagを踏襲し、styleのみをTrial Role styleへ差し替える。
# ------------------------------------------------------------
def generate_b1b_main_segments(theme_out_dir: str, tts_backend: str) -> dict:
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")
    S = TRIAL_ROLE_STYLE_EN
    results = {}

    topic_intro_text = f"Today's topic is {parts['title']}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = voice01.generate_charon_english(
            n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_text)),
            f"{narration_dir}/topic_intro.wav",
            enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for("topic_intro"),
            enable_pronunciation_resolver=True, style_prefix_override=S["TOPIC_INTRO"], tts_backend=tts_backend)
    results["topic_intro"]["canonical_text"] = topic_intro_text
    results["topic_intro"]["role"] = "TOPIC_INTRO"

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        role = "PREVIEW" if name == "preview" else "COMMENT"
        with cl.segment_context(name):
            results[name] = voice01.generate_charon_english(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text)), f"{narration_dir}/{name}.wav",
                style_prefix_override=S[role], disfluency_qa=True,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                enable_pronunciation_resolver=True, tts_backend=tts_backend)
        results[name]["canonical_text"] = text
        results[name]["role"] = role

    for name, text in (("full_story_part1", parts["part1"]), ("in_one_line", parts["in_one_line"])):
        role = "IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"
        with cl.segment_context(name):
            results[name] = news_tail_fix.generate_news_narration_wide_margin(
                n3_tts.tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                enable_repetition_qa=(name in fx_runner._BODY_SEGMENT_NAMES),
                enable_pronunciation_resolver=True, style_prefix_override=S[role], tts_backend=tts_backend)
        results[name]["canonical_text"] = text
        results[name]["role"] = role

    for body_name, heading_text, body_text in (
        ("full_story_part2", parts["heading1"], parts["body2"]),
        ("full_story_part3", parts["heading2"], parts["body3"]),
    ):
        heading_name = f"{body_name}_heading"
        with cl.segment_context(heading_name):
            results[heading_name] = point_headings.generate(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(heading_text)),
                f"{narration_dir}/{heading_name}.wav",
                style_prefix_override=S["HEADING"], tts_backend=tts_backend)
        results[heading_name]["canonical_text"] = heading_text
        results[heading_name]["role"] = "HEADING"

        with cl.segment_context(body_name):
            results[body_name] = news_tail_fix.generate_news_narration_wide_margin(
                n3_tts.tts_safe_news_en(body_text), f"{narration_dir}/{body_name}.wav",
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(body_name),
                enable_repetition_qa=(body_name in fx_runner._BODY_SEGMENT_NAMES),
                enable_pronunciation_resolver=True, style_prefix_override=S["FULL_STORY"], tts_backend=tts_backend)
        results[body_name]["canonical_text"] = body_text
        results[body_name]["role"] = "FULL_STORY"

    return results


def generate_a2_main_segments(theme_out_dir: str, japanese_title: str, tts_backend: str) -> dict:
    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/a2_support_texts.json")
    S = TRIAL_ROLE_STYLE_EN
    JS = TRIAL_ROLE_STYLE_JA
    results = {}

    topic_intro_tts_title = parts.get("title_tts", parts["title"])
    topic_intro_text = f"Today's topic is {parts['title']}."
    topic_intro_tts_text = f"Today's topic is {topic_intro_tts_title}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = crosslevel_common.generate_english_segment_with_fallback(
            n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_tts_text)),
            f"{narration_dir}/topic_intro.wav", n3_tts.first_words(parts["title"], 3), max_extra_chars=30,
            style_prefix_override=S["TOPIC_INTRO"],
            enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for("topic_intro"),
            tts_backend=tts_backend)
    results["topic_intro"]["canonical_text"] = topic_intro_text
    results["topic_intro"]["role"] = "TOPIC_INTRO"

    with cl.segment_context("japanese_title"):
        results["japanese_title"] = generate_ja_role_style(
            japanese_title, f"{narration_dir}/japanese_title.wav", JS["TITLE"], "Aoede",
            n3_tts._generate_a2_japanese_minimal_instruction, tts_backend, max_extra_chars=30)
    results["japanese_title"]["role"] = "TITLE"

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        role = "PREVIEW" if name == "preview" else "COMMENT"
        with cl.segment_context(name):
            results[name] = generate_ja_role_style(
                text, f"{narration_dir}/{name}.wav", JS[role], "Aoede",
                n3_tts._generate_a2_japanese_minimal_instruction, tts_backend, max_extra_chars=40)
        results[name]["role"] = role

    for name, text in (("full_story_part1", parts["part1"]), ("in_one_line", parts["in_one_line"])):
        role = "IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"
        tts_input = n3_tts.tts_safe_news_en(text)
        sub = n3_tts.first_words(text)
        with cl.segment_context(name):
            results[name] = n3_tts.generate_a2_segment_with_slowdown(
                tts_input, f"{narration_dir}/{name}.wav", sub,
                style_prefix_override=S[role], disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                enable_repetition_qa=(name in fx_runner._BODY_SEGMENT_NAMES), tts_backend=tts_backend)
        results[name]["canonical_text"] = text
        results[name]["role"] = role

    for body_name, heading_text, body_text in (
        ("full_story_part2", parts["heading1"], parts["body2"]),
        ("full_story_part3", parts["heading2"], parts["body3"]),
    ):
        heading_name = f"{body_name}_heading"
        heading_tts_input = n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(heading_text))
        with cl.segment_context(heading_name):
            results[heading_name] = n3_tts.generate_a2_segment_with_slowdown(
                heading_tts_input, f"{narration_dir}/{heading_name}.wav", n3_tts.first_words(heading_text, 3),
                max_extra_chars=20, style_prefix_override=S["HEADING"], disfluency_qa=True,
                tts_backend=tts_backend)
        results[heading_name]["canonical_text"] = heading_text
        results[heading_name]["role"] = "HEADING"

        body_tts_input = n3_tts.tts_safe_news_en(body_text)
        body_sub = n3_tts.first_words(body_text)
        with cl.segment_context(body_name):
            results[body_name] = n3_tts.generate_a2_segment_with_slowdown(
                body_tts_input, f"{narration_dir}/{body_name}.wav", body_sub,
                style_prefix_override=S["FULL_STORY"], disfluency_qa=False,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(body_name),
                enable_repetition_qa=(body_name in fx_runner._BODY_SEGMENT_NAMES), tts_backend=tts_backend)
        results[body_name]["canonical_text"] = body_text
        results[body_name]["role"] = "FULL_STORY"

    return results


# ------------------------------------------------------------
# 入力artifact準備(既存テキストartifact再利用、新規生成なし)
# ------------------------------------------------------------
# KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01(既存Gate、無変更のまま維持)が
# 本文照合に使うarticle.mdが--source-run配下に残っていない場合、同一記事の
# 別run(article本文は同一、title表記のみ後日editorial差分あり)から
# 既存artifactとして補う。新規テキスト生成は一切行わない。
_ARTICLE_MD_FALLBACK_DIR = "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02"


def prepare_text_artifacts(source_dir: str, out_dir: str, level: str) -> None:
    src = f"{source_dir}/{level}"
    dst = f"{out_dir}/{level}"
    os.makedirs(dst, exist_ok=True)
    for name in ("parts.json", "article.md",
                 "b1_support_texts.json" if level == "b1b" else "a2_support_texts.json"):
        s = f"{src}/{name}"
        if os.path.exists(s):
            shutil.copyfile(s, f"{dst}/{name}")
    if not os.path.exists(f"{dst}/article.md"):
        fallback = f"{_ARTICLE_MD_FALLBACK_DIR}/{level}/article.md"
        if os.path.exists(fallback):
            shutil.copyfile(fallback, f"{dst}/article.md")
    kp_src = f"{src}/key_phrases/keywords_canonicalized.json"
    if os.path.exists(kp_src):
        os.makedirs(f"{dst}/key_phrases", exist_ok=True)
        shutil.copyfile(kp_src, f"{dst}/key_phrases/keywords_canonicalized.json")


def derive_japanese_title_reused(source_dir: str) -> str | None:
    """新規生成は行わず、既存artifactのみから日本語titleを得る。
    (1) fx_runner.derive_japanese_title(source_dir)を試す(ja_writer正式
    path)。(2)無ければ、既存Baseline完成音声のaudit記録
    (tts_generation_results.json['segments']['japanese_title']
    ['canonical_text'])を再利用する(Hormuz run_06はja_writer dirが
    残っていないが、Baseline a2は既に完成しておりcanonical_textが実測
    記録済みのため)。"""
    info = fx_runner.derive_japanese_title(source_dir)
    if info["japanese_title"]:
        return info["japanese_title"]
    baseline_audit = f"{source_dir}/a2/audit/tts_generation_results.json"
    if os.path.exists(baseline_audit):
        data = load_json(baseline_audit)
        text = (data.get("segments") or {}).get("japanese_title", {}).get("canonical_text")
        if text:
            return text
    return None


# ------------------------------------------------------------
# Orchestration
# ------------------------------------------------------------
def run_tts_stage(source_dir: str, out_dir: str, level: str, tts_backend: str,
                   reuse_production_master: frozenset = frozenset()) -> dict:
    prepare_text_artifacts(source_dir, out_dir, level)
    level_dir = f"{out_dir}/{level}"
    narration_dir = f"{level_dir}/narration"

    trial_store_dir = f"{out_dir}/trial_master_audio_store"
    with trial_master_audio_store(trial_store_dir):
        shared_raw = generate_shell_segments(narration_dir, level, tts_backend,
                                              reuse_production_master=reuse_production_master)
        shared_status = _summarize_shared_narration_with_reuse_detail(shared_raw)

        kp_path = f"{level_dir}/key_phrases/keywords_canonicalized.json"
        kp = load_json(kp_path) if os.path.exists(kp_path) else None
        kp_results = generate_kp_segments(kp, narration_dir, level, tts_backend) if kp is not None else {}
        kp_scaffold_status = "OK" if kp is not None else "KP_SCAFFOLD_JSON_MISSING"

        if level == "b1b":
            results = generate_b1b_main_segments(out_dir, tts_backend)
        else:
            japanese_title = derive_japanese_title_reused(source_dir) or "(japanese title unavailable)"
            results = generate_a2_main_segments(out_dir, japanese_title, tts_backend)

    all_status = {k: v.get("status") for k, v in results.items()}
    if level == "b1b":
        kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                     for r, v in kp_results.items()}
    else:
        kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")}
                     for r, v in kp_results.items()}

    production_master_reuse_note = {
        name: {
            "reused_from_production_master": True,
            "master_audio_id": v.get("master_audio_id"),
            "human_review_lock_state": v.get("human_review_lock_state"),
            "note": v.get("note"),
        }
        for name, v in shared_status.items() if v.get("reused_from_production_master")
    }
    save_json(f"{level_dir}/audit/tts_generation_results.json", {
        "segments": results, "key_phrases": kp_results, "shared_narration": shared_status,
        "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend,
        "management_id": MANAGEMENT_ID, "trial_role_style_en": TRIAL_ROLE_STYLE_EN,
        "trial_role_style_ja": TRIAL_ROLE_STYLE_JA,
        "production_master_reuse_note": production_master_reuse_note,
    })
    save_json(f"{level_dir}/run_summary_tts.json", {
        "segment_status": all_status, "key_phrase_status": kp_status,
        "shared_narration_status": {k: v["status"] for k, v in shared_status.items()},
        "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend,
    })
    fx_runner._assert_shared_narration_ok(shared_status, level)
    return {"segment_status": all_status, "key_phrase_status": kp_status,
            "shared_narration_status": {k: v["status"] for k, v in shared_status.items()},
            "kp_scaffold_status": kp_scaffold_status}


def run_assemble_stage(out_dir: str, level: str, theme_id: str, source_dir: str) -> dict:
    if level == "b1b":
        return fx_runner.stage_assemble_family_x_b1(out_dir, theme_id, source_dir=source_dir)
    return fx_runner.stage_assemble_family_x_a2(out_dir, theme_id, source_dir=source_dir)


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run", required=True,
                         help="既存テキストartifactのある er019_output配下run directory")
    parser.add_argument("--level", required=True, choices=("a2", "b1b"))
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--tts-backend", default="speech_metadata_flash_lite",
                         choices=("structured_separation", "speech_metadata_flash_lite"))
    parser.add_argument("--budget-jpy", type=float, required=True)
    parser.add_argument("--stage", default="tts", choices=("tts", "assemble", "all"))
    parser.add_argument("--theme-id", default="tts_all_spoken_role_style_trial_01")
    parser.add_argument("--reuse-production-master", default="",
                         help="修正1回目(ユーザー指示反映): カンマ区切りのshared narration"
                              "segment名(現状num_two,num_threeのみ対応)。指定segmentは"
                              "Trial NUMBER_LABEL styleで再生成せず、"
                              "PRODUCTION_MASTER_REUSE_SHELL_SEGMENTSのProduction Master"
                              "(read-only参照)をコピーしてreuseする。")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")
    reuse_production_master = frozenset(
        s.strip() for s in args.reuse_production_master.split(",") if s.strip())

    if args.stage in ("tts", "all"):
        with cl.logging_context(args.theme_id, "tts"):
            run_tts_stage(args.source_run, args.out_dir, args.level, args.tts_backend,
                           reuse_production_master=reuse_production_master)
        fx_runner.assert_budget_ok(args.out_dir, args.budget_jpy, "after tts")

    if args.stage in ("assemble", "all"):
        summary = run_assemble_stage(args.out_dir, args.level, args.theme_id, args.source_run)
        print(f"[ER038-TRIAL] assemble summary: {summary}")

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[ER038-TRIAL] stage={args.stage} level={args.level} out_dir={args.out_dir} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")


if __name__ == "__main__":
    main()
