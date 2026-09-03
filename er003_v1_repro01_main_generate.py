# ============================================================
# er003_v1_repro01_main_generate.py
# ER-003-REPRO-01-MAIN: A02 本文・学習セクションまとめて生成
# ============================================================
# A01専用モジュール(er003_b1_p8a_audio.py/er003_b1_p9a_audio.py等)は
# 変更しない。それらの汎用関数(パス・テキストを引数に取るもの)を
# そのままA02へ再利用し、A02固有の値(記事パス・タイトル・Key Phrase等)
# だけをこのスクリプト側で保持する。
#
# 実行方法(段階ごとに関数を個別に呼び出して実行する。単一の
# if __name__=="__main__"一括実行にはしない。理由: 本文TTSが3試行とも
# 不合格になった場合、A01同様ユーザーへの追加試行許可確認が必要になる
# 可能性があるため、各段階の結果を都度確認しながら進める)。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3r_audio as p3r
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p8a_audio as p8a
import er003_b1_p9a_audio as p9a
import er006_asr_provider_routing_01 as routing
import er006_batch_tts_wiring_01 as batch_wiring
import er006_preprod_hardening_01_validation as audio_validation
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er007_ja_secondary_asr_01 as ja_secondary
import er008_disfluency_qa_18 as dq18
import er011_human_review_lock_01 as review_lock

ARTICLE_ID = "A02"
OUT_DIR = f"er003_output/b1_p9a/{ARTICLE_ID}"
BODY_OUT_DIR = f"er003_output/b1_p8a/{ARTICLE_ID}"

B1_ARTICLE_PATH = f"er003_output/b1_p1/{ARTICLE_ID}/b1_article_raw.md"
BODY_DYNAMICS3_PATH = f"{BODY_OUT_DIR}/body_raw/{ARTICLE_ID}_b1_body_dynamics3.wav"

ENGLISH_TITLE_TEXT = "UK Plans Midnight Social Media Break for Teenagers"
# 承認済み日本語マスター(master_ja_approved.md)のタイトル行から、絵文字・
# 「」囲み・見出し記号を除いた本文のみを使用する(A01のJAPANESE_TITLE_TEXT
# と同じ抽出方針)。
JAPANESE_TITLE_TEXT = "午前0時、SNSに“おやすみ”――英国が夜更かしスクロールへ静かな消灯"
JAPANESE_TITLE_SOURCE_PATH = f"er003_output/b1_p1/{ARTICLE_ID}/master_ja_approved.md"

# MFA(english_mfa、mfa_tool/a02_body_output/A02_body.TextGrid)+ASR
# (scratch_a02_seg1/2.wav)で特定した境界(絶対時刻、元のBODY_DYNAMICS3_PATH
# 基準)。ASRで前後の発話内容が数字・時刻の語順ズレなく一致することを
# 確認済み(A01のスコア読み上げ問題の教訓を踏まえた確認)。
TITLE_END_SECONDS = 4.130  # "...Teenagers"(タイトル)の終了
BODY_FIRST_WORD_START_SECONDS = 4.670  # "At"(本文第1文)の開始
NATURAL_LEADING_SECONDS = 0.250  # 元音声冒頭(タイトル"UK"開始前)の自然な無音

# notification2挿入①: "...watch just one more video."の後、
# "Today's Late-Night Scrolling Points"見出しの前
INSERT1_GAP_END_SECONDS = 79.960
INSERT1_GAP_START_SECONDS = 81.290

# notification2挿入②: "...influence people's choices."の後、
# "In One Line"見出しの前
INSERT2_GAP_END_SECONDS = 146.260
INSERT2_GAP_START_SECONDS = 147.560


def stage_a_generate_body_audio() -> dict:
    """Full Story(本編)音声を生成する。初回1回、内容起因の追加試行は
    行わない(run_tts_content_attemptsの既存QA契約=最大3試行、のみに
    従う。3試行とも不合格の場合はA01同様、追加試行の可否をユーザーへ
    確認するために一旦停止する)。"""
    os.makedirs(BODY_OUT_DIR, exist_ok=True)
    plan, text, script = p8a.load_and_build_narration_plan(B1_ARTICLE_PATH)

    result = p8a.generate_article_body_audio(plan)

    if result["status"] != "OK":
        with open(f"{BODY_OUT_DIR}/body_generation_stopped.json", "w", encoding="utf-8") as f:
            json.dump({"status": result["status"], "reason": result.get("reason")}, f,
                      ensure_ascii=False, indent=2, default=str)
        return result

    os.makedirs(f"{BODY_OUT_DIR}/body_raw", exist_ok=True)
    raw_path = f"{BODY_OUT_DIR}/body_raw/{ARTICLE_ID}_b1_body_pre_dynamics3.wav"
    dyn_path = f"{BODY_OUT_DIR}/body_raw/{ARTICLE_ID}_b1_body_dynamics3.wav"
    common.write_wav_float(raw_path, result["pre_dynamics3_samples"], result["sample_rate"], 1)
    common.write_wav_float(dyn_path, result["post_dynamics3_samples"], result["sample_rate"], 1)

    metadata = {
        "article_id": ARTICLE_ID,
        "b1_article_path": B1_ARTICLE_PATH,
        "model": result["model"],
        "voice": result["voice"],
        "accepted_attempt": result["accepted_attempt"],
        "attempts_count": result["attempts_count"],
        "num_chunks": result["num_chunks"],
        "pre_dynamics3_path": raw_path,
        "post_dynamics3_path": dyn_path,
        "pre_dynamics3_sha256": p8a.sha256_file(raw_path),
        "post_dynamics3_sha256": p8a.sha256_file(dyn_path),
        "duration_seconds": round(len(result["post_dynamics3_samples"]) / result["sample_rate"], 4),
    }
    with open(f"{BODY_OUT_DIR}/body_raw/generation_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "metadata": metadata}


def stage_b_edit_body_audio() -> dict:
    """Full Story音声へ、notification2挿入2箇所+タイトル除去の計3編集を
    適用する。A01の教訓に従い、時系列で後ろの編集から先に適用する
    (insert2[約147秒] → insert1[約81秒] → title_trim[約4秒])。"""
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    body_full, body_sr, _, _ = common.read_wav_float(BODY_DYNAMICS3_PATH)
    notification2_mono = p9a.load_mono_at_rate(p9a.NOTIFICATION2_WAV_PATH, body_sr)

    insert2_result = p9a.insert_sound_at_internal_gap(
        body_full, body_sr, gap_end_seconds=INSERT2_GAP_END_SECONDS, gap_start_seconds=INSERT2_GAP_START_SECONDS,
        sound_samples=notification2_mono, pause_before_seconds=0.5, pause_after_seconds=0.4)
    body_after_insert2 = insert2_result["result"]

    insert1_result = p9a.insert_sound_at_internal_gap(
        body_after_insert2, body_sr, gap_end_seconds=INSERT1_GAP_END_SECONDS, gap_start_seconds=INSERT1_GAP_START_SECONDS,
        sound_samples=notification2_mono, pause_before_seconds=0.5, pause_after_seconds=0.4)
    body_after_insert1 = insert1_result["result"]

    trim_result = p9a.trim_title_from_body(
        body_after_insert1, body_sr, first_word_start_seconds=BODY_FIRST_WORD_START_SECONDS,
        natural_leading_seconds=NATURAL_LEADING_SECONDS)
    body_final = trim_result["trimmed"]

    out_path = f"{OUT_DIR}/narration/full_story_edited.wav"
    os.makedirs(f"{OUT_DIR}/narration", exist_ok=True)
    common.write_wav_float(out_path, body_final, body_sr, 1)

    info = {
        "article_id": ARTICLE_ID,
        "insert2_info": insert2_result["info"],
        "insert1_info": insert1_result["info"],
        "title_trim_info": trim_result["info"],
        "out_path": out_path,
        "sha256": p8a.sha256_file(out_path),
        "duration_seconds": round(len(body_final) / body_sr, 4),
    }
    with open(f"{OUT_DIR}/audit/full_story_edit_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2, default=str)

    return {"status": "OK", "info": info}


# ------------------------------------------------------------
# サービス共通ナレーションの再利用元(A01)。内容が記事非依存のため、
# 新規TTSを行わず、既存の確立済み音声(ASR確認済み)をそのまま使う
# (指示section5「サービス共通文言と記事固有文言を分離する」に対応)。
# ------------------------------------------------------------
A01_NARRATION_DIR = "er003_output/b1_p9a/A01/narration"
SERVICE_LEVEL_NARRATION_NAMES = (
    "welcome",  # "Welcome to English Your Way."
    "preview_intro",  # "Here's a quick preview."
    "point_explanation",  # "ポイント解説"
    "key_phrases_intro",  # "Here are today's key phrases."
    "full_story_intro",  # "Now, the full story."
    "num_one", "num_two", "num_three", "num_four", "num_five",
)

# A02固有の新規ナレーション原稿(内容は変更しない)
TOPIC_INTRO_TEXT = f"Today's topic is {ENGLISH_TITLE_TEXT}."
KEY_PHRASE_MEANINGS = {
    1: "参加・適用を断る",       # opt out
    2: "規制対象のアプリ",       # covered apps
    3: "見たいという衝動",       # urge to watch(ER-003-KP-02-R1で確定)
    4: "個人向けに選ばれた投稿欄",  # personalized feed
    5: "デジタル利用の停止時間帯",  # digital switch-off period
}
_MEANING_ASR_SUBSTRINGS = {1: "断る", 2: "アプリ", 3: "衝動", 4: "投稿欄", 5: "停止時間帯"}

# 2026-08-08発見: generate_narration_snippet_verified(A01実装、変更不可)は
# expected_substringの部分一致のみを検証するため、"デジタル利用の停止
# 時間帯"を生成させたところ、ASRが目的の文言を含みつつもその後に全く
# 無関係な内容(「ポイント。ワン。日中はいくらでも使える時間帯を設けよう…」
# 等、28.8秒に渡る創作された生活習慣アドバイス)を連ねて返す事例が発生した
# (A01の"Now, the full story."と同種のhallucination)。部分一致だけでは
# この種の「目的の文言を含むが後ろに余計な内容が続く」ケースを検出できない
# ため、ASR文字数が期待文字数を大きく超えていないかも追加で検証する
# strict版のverified生成をこのスクリプト側に追加する(A01専用モジュールは
# 変更しない)。
@review_lock.guarded_generate_with_language_arg
def generate_narration_snippet_verified_strict(
    text: str, language: str, out_path: str, expected_substring: str,
    max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS, max_extra_chars: int = 15,
    # ER-005-E2E-TTS-ANALYSIS-FIX-01: 既定をEN_TRIM_SAFETY_MARGIN_SECONDS
    # (0.08秒)からNARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS(0.35秒、B1の
    # news_tail_fix経路と同じ実績値)へ引き上げる。Key Phrase呼び出し
    # (generate_key_phrase_component_verified)は従来通り
    # KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDSを明示的に渡しており、この
    # 既定値変更の影響を受けない。
    safety_margin_seconds: float = p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS,
    style_prefix_override: str = None,
    # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: Key Phrase/Point見出し/
    # In One Line等、短文でpartial repetitionが目立ちやすいsegmentのみ
    # 呼び出し側からTrueを渡す(既定Falseで既存の全呼び出しに影響なし)。
    disfluency_qa: bool = False,
) -> dict:
    # ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: 英語(language=="en")は、
    # 単純substring一致に代えて正規化+6分類のvalidatorを使う(数字・否定・
    # 固有名詞以外の内容語差は一致率に関わらずPASSさせない一方、発音区別
    # 符号・ハイフン・序数・英米綴り等の表記差だけならPASSする)。同一
    # signatureがmax_same_signature回連続した場合はretryを打ち切り、
    # status="ASR_VALIDATION_UNCERTAIN"として直前のaudioをそのまま返す
    # (STOPPEDとは区別し、Human Review対象として扱う)。日本語(ja)は
    # 既存のphonetic_verdict方式を維持する(このvalidatorは英語専用の
    # ため)。
    asr_language = "en-US" if language == "en" else "ja-JP"
    max_len = len(text) + max_extra_chars
    attempts_log = []
    classification_history = []
    # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Standard同期呼び出し
    # (client.models.generate_content)からGemini Batch API
    # (client.batches.create)へ実行方式を切り替える。model/voiceは
    # p9a.generate_narration_snippet()の既定(_make_english_call_fn/
    # _make_japanese_call_fn)と同一値をそのまま使い、tts_call_fn引数
    # 経由で差し込む(声・モデル・instruction・spoken textは無変更)。
    batch_model_name = p9a.ENGLISH_MODEL_NAME if language == "en" else p9a.JAPANESE_MODEL_NAME
    batch_call_fn = batch_wiring.make_batch_tts_call_fn(batch_model_name, p9a.VOICE_NAME, output_path=out_path)
    for attempt in range(1, max_attempts + 1):
        r = p9a.generate_narration_snippet(text, language, out_path, tts_call_fn=batch_call_fn,
                                            safety_margin_seconds=safety_margin_seconds,
                                            style_prefix_override=style_prefix_override)
        if r.get("status") != "OK":
            attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err = routing.transcribe(out_path, language=asr_language)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        phonetic_verdict = None
        stop_retrying = False
        audio_classification = None
        if language == "en":
            ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
            verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
                text, asr_text, classification_history, out_path, language=asr_language,
                ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
            verified = verified_content and length_ok
            gate = dq18.apply_disfluency_gate(verified, out_path, language="en", enabled=disfluency_qa)
            verified = gate["verified"]
            audio_classification = cls.classification
            substring_ok = None  # 旧フィールド、新方式では使わない(下の記録用に残すだけ)
        else:
            # ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01: 旧prefix
            # (substring)+phonetic方式から、英語と同じ思想の全文Validator+
            # Cascade方式へ置き換える(protected_check_jaが数字・否定・
            # 固有名詞らしさ・読みをopcode単位で個別に判定する)。
            verified_content, stop_retrying, cls = ja_secondary.evaluate_attempt_ja_with_cascade(
                text, asr_text, out_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI)
            verified = verified_content and length_ok
            audio_classification = cls.classification
            substring_ok = None  # 旧フィールド、新方式では使わない(下の記録用に残すだけ)
        attempts_log.append({
            "attempt": attempt, "status": "OK", "duration_seconds": r["duration_seconds"],
            "asr_text": asr_text, "asr_text_length": len(asr_text) if asr_text else None,
            "max_len": max_len, "substring_ok": substring_ok, "length_ok": length_ok,
            "phonetic_verdict": phonetic_verdict, "audio_classification": audio_classification,
            "connected_speech_info": getattr(cls, "connected_speech_info", None) if language == "en" else None,
            "reading_resolver_info": getattr(cls, "reading_resolver_info", None) if language == "ja" else None,
            "verified": verified,
            "disfluency_checked": gate["disfluency_checked"] if language == "en" else False,
            "disfluency_evidence": gate.get("disfluency_evidence") if language == "en" else None,
        })
        if verified:
            # ER-008-N8-FINAL-QA-HARDENING-21 Item 1: disfluency_checkedが
            # attempts_logの中にしか記録されず、Assemble Gateがこの情報を
            # 一切参照していなかったことがNo.8のkp2("uneven choice")取りこぼし
            # の一因だった。asr_verified等と同じtop-levelへ昇格し、Gate側
            # (_segment_missing_mandatory_disfluency_qa)が読めるようにする。
            return {**r, "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                    "audio_classification": audio_classification,
                    "connected_speech_info": getattr(cls, "connected_speech_info", None) if language == "en" else None,
                    "reading_resolver_info": getattr(cls, "reading_resolver_info", None) if language == "ja" else None,
                    "disfluency_checked": gate["disfluency_checked"] if language == "en" else False,
                    "disfluency_evidence": gate.get("disfluency_evidence") if language == "en" else None}
        if stop_retrying:
            return {**r, "status": "ASR_VALIDATION_UNCERTAIN", "asr_verified": False, "asr_text": asr_text,
                    "attempts_log": attempts_log,
                    "reason": f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={audio_classification})"}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証(内容+長さ)に合格しませんでした",
           "attempts_log": attempts_log}


def stage_c_generate_new_narrations() -> dict:
    """A02固有の新規ナレーション(topic_intro/japanese_title/meaning_1-5)
    を、内容一致+長さ妥当性のstrict ASR検証付きで生成する。サービス共通
    文言はA01の既存音声をそのまま参照するため、ここでは生成しない。"""
    narration_dir = f"{OUT_DIR}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    results = {}

    jobs = [
        ("topic_intro", TOPIC_INTRO_TEXT, "en", "Midnight Social Media Break"),
        ("japanese_title", JAPANESE_TITLE_TEXT, "ja", "夜更かし"),
    ]
    for i in range(1, 6):
        jobs.append((f"meaning_{i}", KEY_PHRASE_MEANINGS[i], "ja", _MEANING_ASR_SUBSTRINGS[i]))

    for name, text, language, expected_substring in jobs:
        out_path = f"{narration_dir}/{name}.wav"
        result = generate_narration_snippet_verified_strict(text, language, out_path, expected_substring)
        results[name] = result

    with open(f"{OUT_DIR}/audit/new_narrations_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_ok = all(r.get("status") == "OK" for r in results.values())
    return {"status": "OK" if all_ok else "STOPPED", "results": results}


# ER-003-KP-02-R1で確定したA02の英語Key Phrase(used_form)。A01のような
# 既存流用元がないため、全件新規TTS生成が必要。
KEY_PHRASES_USED_FORM = {
    1: "opt out",
    2: "covered apps",
    3: "urge to watch",
    4: "personalized feed",
    5: "digital switch-off period",
}


# P9A-R1で"Now, the full story."に実際に効果があった対症療法(声・
# モデルは変えず、instructionだけ「そのまま読み上げてください」という
# 最小限のものへ差し替える)と同一の考え方。ENGLISH_STYLE_PREFIX(記事
# 本文からの抜粋を番組の一部として読む前提の長い指示)を、文脈のない
# 短い単独フレーズに使うと、モデルが無関係な内容へ迷い込みやすいことが
# 分かっている(A01の"Now, the full story."、今回の"opt out"で実際に
# 発生: "Don't get into this mindset of letting your mess..."等の
# 完全に無関係な内容が生成された)。
MINIMAL_INSTRUCTION_PREFIX = (
    "Speak the following text aloud naturally and clearly, in a warm podcast "
    "announcer voice. Do not add, omit, or change any words.\n\n"
)


def generate_english_component_minimal_instruction(
    text: str, out_path: str,
    # ER-005-E2E-TTS-ANALYSIS-FIX-01: generate_narration_snippet_verified_
    # strictと同じ理由で既定をNARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS
    # へ引き上げる。generate_key_phrase_component_verifiedのfallback呼び
    # 出しはKEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDSを明示的に渡すため
    # 無影響。generate_english_segment_with_fallback(A2英語segmentの
    # fallback経路)は明示指定していないため、この既定値変更で救われる。
    safety_margin_seconds: float = p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS,
) -> dict:
    # ER-005-AUDIO-INSTRUCTION-SEPARATION-01: fallback経路にもStructured
    # Separationを適用する。
    prompt = p4c.build_tts_prompt(text, MINIMAL_INSTRUCTION_PREFIX)
    # ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01: Batch API配線(声・モデルは
    # p9a._make_english_call_fn()と同一のENGLISH_MODEL_NAME/VOICE_NAMEを使う)。
    call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, p9a.VOICE_NAME, output_path=out_path)
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"minimal instructionでもTTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=safety_margin_seconds)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    # ER-005-AUDIO-WASTE-REDUCTION-01: hallucinationを疑わせる異常長音声を
    # ASR実行前に検知して破棄する。
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        return {"status": "STOPPED", "reason": anomaly["reason"], "duration_anomaly": anomaly}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {
        "status": "OK", "text": text, "path": out_path, "model": p9a.ENGLISH_MODEL_NAME,
        "voice": p9a.VOICE_NAME, "call_count": 1 + retries, "retry_count": retries,
        "sha256": p8a.sha256_file(out_path), "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
        "instruction": "minimal (not ENGLISH_STYLE_PREFIX)",
    }


# ER-003-N3-ROOT-FIX-01(2026-08-17): Key Phrase英語音声専用のhead/tail
# safety margin。follow-up timeの/f/のような無声摩擦音は振幅が小さく、
# 母音onset前提の既定0.08秒(p3u.EN_TRIM_SAFETY_MARGIN_SECONDS)では
# 語頭が一部trimされる実例が確認された。Key Phraseは全体の音声尺への
# 影響が小さいため、0.08秒から0.20秒(約2.5倍)へ拡大した。この定数は
# Key Phrase生成専用であり、他segment(Preview/Comment/Title等、p9a.
# generate_narration_snippetの他の呼び出し元)には波及しない。
#
# ER-011-NO18-KEYPHRASE-TRIM-030-PRODUCTION-WIRING-12(2026-09-03、
# ユーザー正式決定): 0.20秒はhead(語頭)側の実例のみで検証された値で
# あり、tail(語末)側は同じ値を対称に適用していただけだった。No.18 A2
# Key Phrase 5「be powered off」で、語末の無声摩擦音/f/がファイル終端
# まで高域エネルギーを保ったまま(自然な減衰が確認できないまま)切れて
# いる可能性がTrial-11(ER-011-NO18-A2-KP5-TRIM-MARGIN-03-TRIAL-11)の
# 音響解析で確認され、0.30秒版で/f/が自然に減衰してから終端することを
# ユーザーが試聴・承認したため、0.20秒から0.30秒へ正式に拡大する。
# 比較検討の詳細・却下した代替案はDECISION_LOG.md該当エントリを参照。
KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS = 0.30


# ============================================================
# ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22
# ============================================================
# ユーザー正式決定(2026-09-01、Trial-19→Mini-Trial-20-R2→Trial-21を
# 経て採用)。英語Key Phrase Component生成のretry構成を、旧来の
# 「標準経路(ENGLISH_STYLE_PREFIX、フルストーリー本文向けの長い演技
# 指示)→不合格の場合のみminimal instructionへfallback、合計上限は
# PRODUCTION_MAX_TTS_ATTEMPTS(3回)と共有」という構成から、
# 「Minimal instruction(Primary、最大2回)→2回ともNGの場合のみEnglish
# language lock付きMinimal(Fallback、最大2回)、合計最大4回」へ全面的に
# 置き換える。旧構成(ENGLISH_STYLE_PREFIX起点の標準経路)は、この関数
# 以外のsegment(Full Story/News/Point見出し等、
# generate_narration_snippet_verified_strict/
# generate_english_component_minimal_instruction/ENGLISH_STYLE_PREFIX/
# MINIMAL_INSTRUCTION_PREFIXそのもの)には一切適用されない仕様変更で
# あり、それらは無変更のまま残す。
#
# 合計最大4回は、CURRENT_SPEC.md「TTS生成の同一segment総試行回数上限」
# (`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`=3、他7関数のSSOT)に対する
# Key Phrase英語Component専用の明示的な例外(ユーザー正式決定、この
# 関数のみに適用。PRODUCTION_MAX_TTS_ATTEMPTS定数自体・他7関数の
# max_attempts既定値は変更しない)。
KEY_PHRASE_MINIMAL_MAX_ATTEMPTS = 2
KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS = 2
KEY_PHRASE_TOTAL_MAX_ATTEMPTS = KEY_PHRASE_MINIMAL_MAX_ATTEMPTS + KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS  # 4

# Trial(ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-
# ACCOUNTING-FIX-19→MINI-TRIAL-20-R2)で検証・ユーザー承認済みの文言を
# 一字一句そのまま複製する。Trial専用モジュール(er010_no9_*.py)を
# Productionからimportしない設計方針(Dangling Reference防止)のため、
# 文字列としてここへ複製する。変更する場合はTrialを再実施のうえ
# DECISION_LOG.mdへ記録すること(勝手な再設計は禁止)。
KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT = (
    "Speak the following short phrase aloud naturally and clearly, in a warm podcast "
    "announcer voice, exactly once. Say only this phrase — do not add explanations, "
    "examples, introductions, or any other commentary, and do not add, omit, or change "
    "any words. Say it as one natural phrase, not as separate words read one at a time. "
    "Make sure the very last sound of the phrase is actually spoken, not trailed off "
    "into silence, and do not over-emphasize or exaggerate any single sound.\n\n"
)

# ============================================================
# ER-010-NO9-FUNCTION-WORD-REDUCTION-PRODUCTION-WIRING-AND-A2-FINAL-27-R1
# ============================================================
# ユーザー正式決定(2026-09-02、Trial 26で検証・承認)。Key Phrase「a
# catch」で冠詞"a"が独立した強勢語のように強く・長く発音される問題への
# 対策として、function word(article等)を弱く・短く・非強勢で発音し、
# 後続content wordへ自然につなげるという原則を、Key Phrase英語TTSの
# 一般Production仕様として正式採用する。Trial 26で使用した文言を一字
# 一句そのまま複製する(Trial専用モジュールer010_no9_a2_keyphrase_
# article_reduction_trial_26.pyをProductionからimportしない設計方針
# 踏襲、Dangling Reference防止)。「a catch」固有のhardcodeではなく、
# article/function word全般への一般原則として記述する。既存の
# KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXTは一切変更せず、末尾に追加
# するだけ(KEY_PHRASE_ENGLISH_LANGUAGE_LOCK_SUFFIXと同じAND方式)。
FUNCTION_WORD_REDUCTION_SUFFIX = (
    "In natural spoken English, short function words such as articles "
    "(\"a\", \"an\", \"the\") are usually spoken briefly and without stress, "
    "connecting smoothly into the word that follows, while the main content "
    "word carries the natural stress of the phrase. If the phrase contains "
    "such a function word, keep it light and unstressed, and let it flow "
    "naturally into the following word, rather than pronouncing it as its "
    "own separate, stressed beat. Do not omit or drop the function word — "
    "only make it light and unstressed, not silent, and do not let this "
    "affect how clearly the rest of the phrase is spoken.\n\n"
)

# KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIXは実際にPrimary試行で使われる
# 実効instructionであり、CORE_TEXT+FUNCTION_WORD_REDUCTION_SUFFIXで
# ある。KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION(下記)はこの
# KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIXを起点に構築されるため、
# function-word reductionはPrimary(Minimal)・Fallback(English Lock)の
# 両方に自動的に適用される(定義を分岐させない設計、Dangling Reference
# 防止)。
KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX = (
    KEY_PHRASE_MINIMAL_INSTRUCTION_CORE_TEXT + FUNCTION_WORD_REDUCTION_SUFFIX
)

# ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21で検証・ユーザー
# 承認済みの文言を一字一句そのまま複製する。KEY_PHRASE_MINIMAL_
# INSTRUCTION_PREFIXの末尾に追加するだけで、既存文言は一切置換しない
# (AND、ORではない。final consonant/自然さ/1回のみ/phrase一体感の
# 各pronunciation safeguardはFallbackでも維持される)。
KEY_PHRASE_ENGLISH_LANGUAGE_LOCK_SUFFIX = (
    "Pronounce the phrase specifically as an English word or phrase, "
    "using English pronunciation throughout — not as a Japanese, Chinese, "
    "or other non-English reading of it.\n\n"
)
KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION = KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX + KEY_PHRASE_ENGLISH_LANGUAGE_LOCK_SUFFIX


@review_lock.guarded_generate("en")
def generate_key_phrase_component_verified(text: str, out_path: str,
        # ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: Key PhraseはPRODUCTION
        # 承認済みのdisfluency QA対象segmentのため既定True(A2/B1共通)。
        disfluency_qa: bool = True) -> dict:
    """Primary: Minimal instruction(KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)
    で最大KEY_PHRASE_MINIMAL_MAX_ATTEMPTS(2)回まで試行する。2回とも
    不合格の場合のみ、Fallback: Minimal instruction+English language lock
    (KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION)で最大KEY_PHRASE_ENGLISH_LOCK_
    MAX_ATTEMPTS(2)回まで試行する(合計最大KEY_PHRASE_TOTAL_MAX_ATTEMPTS
    =4回)。いずれかの段でverified=Trueになった時点で即座に返し、後続の
    attemptは実行しない。声・モデル・head safety margin(KEY_PHRASE_TRIM_
    SAFETY_MARGIN_SECONDS)・ASR Validator(cascade)・disfluency gateは
    両段で共通(generate_narration_snippet_verified_strictをstyle_prefix_
    overrideだけ差し替えて2回呼ぶ設計、コード重複を避けつつ両段とも
    Production同一のASR/Cascade/disfluency実装を使う)。

    review_lock: この関数自体が@guarded_generate("en")でguardされており、
    内部で呼ぶgenerate_narration_snippet_verified_strict
    (@guarded_generate_with_language_arg)は同一out_pathに対する
    reentrancy guard(OPEN-105)により、外側の呼び出しが進行中の間は
    check_before_generation/record_outcomeを行わずfnへ委譲される。
    したがって、Primary/Fallback 2回の内部呼び出しがあっても
    record_outcome()は最終的に外側で1回だけ発火し、二重会計は発生しない。"""
    primary = generate_narration_snippet_verified_strict(
        text, "en", out_path, text, max_extra_chars=10, max_attempts=KEY_PHRASE_MINIMAL_MAX_ATTEMPTS,
        safety_margin_seconds=KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=disfluency_qa,
        style_prefix_override=KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)
    if primary.get("status") == "OK":
        primary["fallback_used"] = False
        primary["primary_instruction_type"] = "MINIMAL"
        return primary

    fallback = generate_narration_snippet_verified_strict(
        text, "en", out_path, text, max_extra_chars=10, max_attempts=KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS,
        safety_margin_seconds=KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=disfluency_qa,
        style_prefix_override=KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION)
    fallback["fallback_used"] = True
    fallback["primary_instruction_type"] = "ENGLISH_LOCK" if fallback.get("status") == "OK" else "MINIMAL_AND_ENGLISH_LOCK_BOTH_FAILED"
    # record_outcome()のcumulative_tts_attempts集計は
    # result["attempts_log"](ここではEnglish Lock段の実際の試行)に加え、
    # result["fallback_attempts_log"]があれば長さを加算する設計(既存
    # 実装、変更なし)。Minimal段の実際の試行をここへ入れることで、
    # 「実TTS試行回数=cumulative_tts_attempts」を維持する。
    fallback["fallback_attempts_log"] = primary.get("attempts_log")
    # 監査・報告用の分かりやすい別名(record_outcome()は参照しない)。
    fallback["minimal_attempts_log"] = primary.get("attempts_log")
    fallback["english_lock_attempts_log"] = fallback.get("attempts_log")
    if fallback.get("status") == "OK":
        return fallback
    fallback["reason"] = (f"Minimal instruction{KEY_PHRASE_MINIMAL_MAX_ATTEMPTS}回+"
                          f"English language lock{KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS}回"
                          f"(合計上限{KEY_PHRASE_TOTAL_MAX_ATTEMPTS}回)とも不合格。"
                          f"{fallback.get('reason') or ''}").strip()
    return fallback


def stage_d_generate_key_phrase_components() -> dict:
    """A02の英語Key Phrase Component5件を、Aoede+gemini-2.5-pro-preview-tts
    (A01のshot on target等と同一voice/model)でstrict ASR検証付き生成する。
    Primary: Minimal instruction最大2回。Fallback: 2回ともNGの場合のみ
    English language lock付きMinimal最大2回(合計最大4回、ユーザー正式
    決定[ER-010-NO9-KEYPHRASE-MINIMAL-ENGLISHLOCK-PRODUCTION-WIRING-22]、
    詳細はgenerate_key_phrase_component_verified()docstring参照)。"""
    components_dir = f"{OUT_DIR}/key_phrase_components"
    os.makedirs(components_dir, exist_ok=True)
    results = {}
    for i in range(1, 6):
        text = KEY_PHRASES_USED_FORM[i]
        out_path = f"{components_dir}/kp_{i}_{text.replace(' ', '_')}.wav"
        result = generate_key_phrase_component_verified(text, out_path)
        results[i] = result

    with open(f"{OUT_DIR}/audit/key_phrase_components_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_ok = all(r.get("status") == "OK" for r in results.values())
    return {"status": "OK" if all_ok else "STOPPED", "results": results}


# ------------------------------------------------------------
# Stage E: 全体組み立て(A01最終仕様の19パート構成を再利用)
# ------------------------------------------------------------
SR = p9a.TARGET_SAMPLE_RATE
PREVIEW_PATH = f"{OUT_DIR}/narration/preview_japanese_only.wav"  # ユーザー承認済み、無変更
FULL_STORY_EDITED_PATH = f"{OUT_DIR}/narration/full_story_edited.wav"

# A02のKey Phrases(ER-003-KP-02-R1で確定)。number/japanese/component_path
# の対応をここで保持する(p9a.KEY_PHRASESはA01専用、変更しない)。
A02_KEY_PHRASES = (
    {"number": "One", "used_form": "opt out", "japanese": "参加・適用を断る",
     "component_path": f"{OUT_DIR}/key_phrase_components/kp_1_opt_out.wav"},
    {"number": "Two", "used_form": "covered apps", "japanese": "規制対象のアプリ",
     "component_path": f"{OUT_DIR}/key_phrase_components/kp_2_covered_apps.wav"},
    {"number": "Three", "used_form": "urge to watch", "japanese": "見たいという衝動",
     "component_path": f"{OUT_DIR}/key_phrase_components/kp_3_urge_to_watch.wav"},
    {"number": "Four", "used_form": "personalized feed", "japanese": "個人向けに選ばれた投稿欄",
     "component_path": f"{OUT_DIR}/key_phrase_components/kp_4_personalized_feed.wav"},
    {"number": "Five", "used_form": "digital switch-off period", "japanese": "デジタル利用の停止時間帯",
     "component_path": f"{OUT_DIR}/key_phrase_components/kp_5_digital_switch-off_period.wav"},
)


def load_all_sources() -> dict:
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    preview_mono, preview_sr, _, _ = common.read_wav_float(PREVIEW_PATH)
    body_mono, body_sr, _, _ = common.read_wav_float(FULL_STORY_EDITED_PATH)
    assert preview_sr == common.SAMPLE_RATE and body_sr == common.SAMPLE_RATE

    narration = {}
    for name in SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title", "meaning_1", "meaning_2", "meaning_3", "meaning_4", "meaning_5"):
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    key_phrase_components = {}
    for kp in A02_KEY_PHRASES:
        mono, sr, _, _ = common.read_wav_float(kp["component_path"])
        key_phrase_components[kp["number"]] = p9a.p7c.tight_speech_only(mono, sr)

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "body_mono": body_mono, "narration": narration,
        "key_phrase_components": key_phrase_components,
    }


def apply_gain_and_convert(sources: dict) -> dict:
    """PreviewとBody(本編)は無加工のまま基準とする。Intro/notification/
    新規ナレーションは平均RMSへ。Outroだけは特別に、Introの調整後RMSへ
    合わせる(A01 R1で確立した一般的な方法をそのまま適用)。A01固有の
    「聴感2/3」追加調整は、A02ではまだユーザーから同様の指摘を受けて
    いないため適用しない(A01個別のgain値・判断を機械的にコピーしない)。"""
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["body_mono"])) / 2
    gain_report = {"target_rms": round(target_rms, 5)}

    def gain_to_rms(data, target, label):
        gain = p9a.compute_gain_for_target_rms(data, target)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                              "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {}
    result["intro"] = gain_to_rms(sources["intro"]["samples"], target_rms, "intro")
    result["notification"] = gain_to_rms(sources["notification"]["samples"], target_rms, "notification")

    intro_final_rms = p9a.rms(result["intro"])
    result["outro"] = gain_to_rms(sources["outro"]["samples"], intro_final_rms, "outro")
    gain_report["outro"]["matched_to"] = "intro_post_gain_rms"
    gain_report["outro"]["intro_post_gain_rms"] = round(intro_final_rms, 5)

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])  # 無加工(ユーザー承認済み)
    result["body"] = p9a.mono_24k_to_stereo_target(sources["body_mono"])  # 編集済み、内容は無加工

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo = {}
    for number, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{number}")
        key_phrase_stereo[number] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(ユーザー承認済み音声を保持)"}
    gain_report["body"] = {"gain": 1.0, "note": "編集(notification2挿入・タイトル除去)のみ、内容・gainは無加工"}
    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(parts: dict) -> list:
    blocks = []
    for kp in A02_KEY_PHRASES:
        num_key = f"num_{kp['number'].lower()}"
        meaning_key = f"meaning_{A02_KEY_PHRASES.index(kp) + 1}"
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][kp["number"]], parts[meaning_key], SR)
        blocks.append(block)
    return blocks


def assemble(parts: dict) -> "np.ndarray":
    key_phrase_blocks = build_key_phrase_blocks(parts)

    pieces = [
        parts["intro"],
        p9a.silence_stereo(0.0),
        parts["welcome"],
        p9a.silence_stereo(0.5),
        parts["topic_intro"],
        p9a.silence_stereo(0.65),
        parts["japanese_title"],
        p9a.silence_stereo(0.5),
        parts["notification"],
        p9a.silence_stereo(0.4),
        parts["preview_intro"],
        p9a.silence_stereo(0.65),
        parts["point_explanation"],
        p9a.silence_stereo(0.5),
        parts["preview"],
        p9a.silence_stereo(0.5),
        parts["notification"],
        p9a.silence_stereo(0.4),
        parts["key_phrases_intro"],
        p9a.silence_stereo(0.5),
    ]
    for block in key_phrase_blocks:
        pieces.append(block)
    pieces += [
        parts["notification"],
        p9a.silence_stereo(0.4),
        parts["full_story_intro"],
        p9a.silence_stereo(0.7),
        parts["body"],
        p9a.silence_stereo(0.5),
        parts["outro"],
    ]
    return np.ascontiguousarray(np.concatenate(pieces, axis=0))


def stage_e_assemble() -> dict:
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    sources = load_all_sources()
    parts = apply_gain_and_convert(sources)
    assembled = assemble(parts)

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_A02.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": round(len(assembled) / SR, 4),
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }


if __name__ == "__main__":
    r = stage_a_generate_body_audio()
    print("stage_a status:", r["status"])
    if r["status"] == "OK":
        print(json.dumps(r["metadata"], ensure_ascii=False, indent=2))
    else:
        print("reason:", r.get("reason"))
