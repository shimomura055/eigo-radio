# ============================================================
# er003_v1_crosslevel_audio_02_common.py
# ER-003-CROSSLEVEL-AUDIO-02: A01・ADD03 A2音声プロトタイプ共通処理
# ============================================================
# A01・ADD03は、ER-003-A2-AUDIO-01(A02)と異なり今回が「初めてのA2音声化」
# であるため、Preview/Comment1-4/Full Story/Points/In One Line/
# Key Phraseのすべてを新規生成する必要がある。両記事とも適用する処理
# (5つのCross-level改善+方式L選定済みKey Phraseの音声化)が完全に同一
# であるため、A01/A02のB1組み立てスクリプトが個別記事ごとに複製してきた
# 従来の慣習とは異なり、本ステージに限り共通モジュールへ処理をまとめる
# (重複コピーによる値のずれを避けるため)。
#
# Cross-level改善の実体(Key Phrase語末音素試作instruction・Outro減衰
# 係数・「ポイント解説」後ポーズ0.7秒)は、ER-003-CROSSLEVEL-AUDIO-01で
# 検証済みのer003_v1_a2_audio_02_generate.py(A02再試作)の定義をそのまま
# 再利用する(新しい数値・instructionをここで再設計しない)。
# Key Phrase Component標準生成・Comment/Full Story等のASR strict検証
# 生成は、それぞれer003_v1_repro01_main_generate.py
# (generate_key_phrase_component_verified/
# generate_narration_snippet_verified_strict、いずれも記事非依存の
# 汎用関数)をそのまま再利用する。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_a2_article as a2
import er003_b1_p9a_audio as p9a
import er003_v1_a2_audio_02_generate as audio02
import er003_v1_repro01_main_generate as repro01
import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as audio_validation
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr

generate_narration_snippet_verified_strict = repro01.generate_narration_snippet_verified_strict
generate_key_phrase_component_verified = repro01.generate_key_phrase_component_verified
generate_key_phrase_trial_clarity = audio02.generate_key_phrase_trial_clarity
tail_energy_profile = audio02._tail_energy_profile

# 2026-08-09(ER-003-CROSSLEVEL-AUDIO-02)発見: ADD03のPoint One("$30
# million"等の金額表現を含む)で、標準経路(ENGLISH_STYLE_PREFIX)が6回とも
# 同一の400 INVALID_ARGUMENT("Model tried to generate text, but it
# should only be used for TTS")で失敗した。これはA02の"opt out"等で
# 発生した「文脈のない短いフレーズがモデルを迷わせる」問題と同種の、
# モデルがテキストをそのまま読み上げず応答しようとする現象と判断し、
# 英語Key Phrase Component用に既に確立済みのminimal instruction
# フォールバック(repro01.MINIMAL_INSTRUCTION_PREFIX、声・モデルは
# 変えない)を、Key Phrase以外の英語ナレーションセグメントにも一般化して
# 適用する(新しいinstructionを新設せず、既存の確立済み対症療法を再利用)。
def generate_english_segment_with_fallback(text: str, out_path: str, expected_substring: str,
                                            max_extra_chars: int = 60, max_attempts: int = 6,
                                            style_prefix_override: str = None) -> dict:
    """style_prefix_override(既定None、ER-008-EVIDENCE-COMPRESSION-PROD-
    AND-N7-AUDIO-06 Part Gで追加): standard経路にのみ適用する(A2の
    「わずかに遅く」指示のため)。fallback(minimal instruction)経路には
    渡さない — fallbackは既にprosody指示を持たない最小限の1文のみで、
    速度指示を追加すると簡易fallbackがさらに平板になる恐れがあるため。"""
    standard = generate_narration_snippet_verified_strict(
        text, "en", out_path, expected_substring, max_attempts=max_attempts, max_extra_chars=max_extra_chars,
        style_prefix_override=style_prefix_override)
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
    fallback_classification_history = []
    for attempt in range(1, max_attempts + 1):
        r = repro01.generate_english_component_minimal_instruction(text, out_path)
        if r.get("status") != "OK":
            fallback_attempts.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason")})
            continue
        asr_text, err = routing.transcribe(out_path, language="en-US", timeout_seconds=300.0)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
        # ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04
        # Part C: fallback(minimal instruction)経由の音声はforce_secondary=True
        # で、PrimaryがPASSしてもSecondary ASRの確認を必須にする(standard
        # path側は変更しない、追加コストはfallback発動時のみ)。
        verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
            text, asr_text, fallback_classification_history, out_path, language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED,
            force_secondary=True)
        verified = verified_content and length_ok
        fallback_attempts.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                                   "audio_classification": cls.classification, "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = standard.get("attempts_log")
            r["fallback_attempts_log"] = fallback_attempts
            return r
        if stop_retrying:
            r["status"] = "ASR_VALIDATION_UNCERTAIN"
            r["asr_verified"] = False
            r["asr_text"] = asr_text
            r["fallback_used"] = True
            r["standard_attempts_log"] = standard.get("attempts_log")
            r["fallback_attempts_log"] = fallback_attempts
            r["reason"] = (f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                            f"(最終classification={cls.classification})")
            return r
    return {"status": "STOPPED", "reason": f"標準経路・minimal instruction経路とも{max_attempts}回で不合格",
           "standard_attempts_log": standard.get("attempts_log"), "fallback_attempts_log": fallback_attempts}

A01_NARRATION_DIR = repro01.A01_NARRATION_DIR  # "er003_output/b1_p9a/A01/narration"(サービス共通、記事非依存)
SERVICE_LEVEL_NARRATION_NAMES = repro01.SERVICE_LEVEL_NARRATION_NAMES

SR = p9a.TARGET_SAMPLE_RATE

# Cross-level改善①: 「ポイント解説」後ポーズ0.7秒(ER-003-CROSSLEVEL-AUDIO-01
# でA02にのみ適用した数値をそのまま再利用。記事別ハードコードを増やさない
# ため、この共通モジュール1箇所にのみ定義する)。
POINT_EXPLANATION_PAUSE_SECONDS = audio02.POINT_EXPLANATION_PAUSE_SECONDS

# Cross-level改善②: Outro減衰(同上、ER-003-CROSSLEVEL-AUDIO-01の係数を再利用)
OUTRO_PERCEIVED_LOUDNESS_TARGET = audio02.OUTRO_PERCEIVED_LOUDNESS_TARGET
OUTRO_EXTRA_GAIN_DB = audio02.OUTRO_EXTRA_GAIN_DB
OUTRO_EXTRA_GAIN_LINEAR = audio02.OUTRO_EXTRA_GAIN_LINEAR


# ============================================================
# A2本文の段落抽出(記事ごとに分割位置が異なるため、パラグラフ数を引数で渡す)
# ============================================================
def load_source_texts(article_id: str, part1_paragraph_count: int) -> dict:
    path = f"er003_output/a2_p1_r3/{article_id}/a2_article_raw.md"
    with open(path, encoding="utf-8") as f:
        original = f.read()
    sections = a2.split_article_sections(original)
    paras = [p.strip() for p in sections["full_story"].split("\n\n") if p.strip()]
    body_paras = paras[1:]  # [0]はタイトル

    full_story_part1 = "\n\n".join(body_paras[0:part1_paragraph_count])
    full_story_part2 = "\n\n".join(body_paras[part1_paragraph_count:])

    points = sections["points"]
    idx = points.index("### Point Two")
    point_one = points[:idx].strip().replace("### ", "")
    point_two = points[idx:].strip().replace("### ", "")

    in_one_line_core = sections["in_one_line"].strip()

    return {
        "full_story_part1": full_story_part1,
        "full_story_part2": full_story_part2,
        "point_one": point_one,
        "point_two": point_two,
        "in_one_line_core": in_one_line_core,
        "source_path": path,
    }


# ============================================================
# セグメント生成(Preview/Comment1-4/Full Story/Points/In One Line)
# ============================================================
def generate_text_segments(config: dict) -> dict:
    narration_dir = f"{config['out_dir']}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    results = {}
    for name, text, language, expected_substring, max_extra_chars in config["segments"]:
        out_path = f"{narration_dir}/{name}.wav"
        if language == "en":
            result = generate_english_segment_with_fallback(
                text, out_path, expected_substring, max_extra_chars=max_extra_chars)
        else:
            result = generate_narration_snippet_verified_strict(
                text, language, out_path, expected_substring, max_attempts=6, max_extra_chars=max_extra_chars)
        results[name] = result

    os.makedirs(f"{config['out_dir']}/audit", exist_ok=True)
    with open(f"{config['out_dir']}/audit/text_segments_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_ok = all(r.get("status") == "OK" for r in results.values())
    return {"status": "OK" if all_ok else "STOPPED", "results": results}


# ============================================================
# Key Phrase Component生成(標準経路 + 語末音素試作、at_risk=Trueのみ試作追加)
# ============================================================
def generate_key_phrase_components(config: dict) -> dict:
    components_dir = f"{config['out_dir']}/key_phrase_components"
    os.makedirs(components_dir, exist_ok=True)
    results = {}
    tail_comparisons = {}

    for kp in config["key_phrases"]:
        used_form = kp["used_form"]
        safe_name = used_form.replace(" ", "_").replace("'", "")
        standard_path = f"{components_dir}/kp_{kp['number']}_{safe_name}_standard.wav"
        standard_result = generate_key_phrase_component_verified(used_form, standard_path)
        entry = {"used_form": used_form, "at_risk_final_phoneme": kp["at_risk"],
                  "final_phoneme_note": kp["final_phoneme_note"], "standard": standard_result}

        if kp["at_risk"] and standard_result.get("status") == "OK":
            trial_path = f"{components_dir}/kp_{kp['number']}_{safe_name}_trial.wav"
            trial_result = generate_key_phrase_trial_clarity(used_form, trial_path)
            entry["trial"] = trial_result
            if trial_result.get("status") == "OK":
                tail_comparisons[kp["number"]] = {
                    "used_form": used_form,
                    "standard": {"path": standard_path, "profile": tail_energy_profile(standard_path)},
                    "trial": {"path": trial_path, "profile": tail_energy_profile(trial_path)},
                }
            entry["adopted"] = "trial" if trial_result.get("status") == "OK" else "standard"
        else:
            entry["adopted"] = "standard"

        results[kp["number"]] = entry

    os.makedirs(f"{config['out_dir']}/audit", exist_ok=True)
    with open(f"{config['out_dir']}/audit/key_phrase_components_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{config['out_dir']}/audit/key_phrase_tail_energy_comparison.json", "w", encoding="utf-8") as f:
        json.dump(tail_comparisons, f, ensure_ascii=False, indent=2)

    all_ok = all(
        (r["standard"].get("status") == "OK") and (r.get("trial", {}).get("status", "OK") == "OK")
        for r in results.values()
    )
    return {"status": "OK" if all_ok else "STOPPED", "results": results, "tail_comparisons": tail_comparisons}


def _adopted_component_path(config: dict, kp: dict) -> str:
    components_dir = f"{config['out_dir']}/key_phrase_components"
    safe_name = kp["used_form"].replace(" ", "_").replace("'", "")
    if kp["at_risk"]:
        return f"{components_dir}/kp_{kp['number']}_{safe_name}_trial.wav"
    return f"{components_dir}/kp_{kp['number']}_{safe_name}_standard.wav"


# ============================================================
# 全体組み立て
# ============================================================
def load_all_sources(config: dict) -> dict:
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration_dir = f"{config['out_dir']}/narration"
    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{narration_dir}/preview.wav")
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in SERVICE_LEVEL_NARRATION_NAMES:
        # ER-006-MASTER-AUDIO-STORE-01: Master Audio Store経由の生成
        # (er006_audio_cost_pilot_02_shared_narration.ensure_all_shared_
        # narration_a2)が済んでいるテーマは、記事固有narration_dir配下に
        # 既にこの名前のファイルが存在する(B1と完全に同じmasterを共有
        # するため、drift無し)。存在すればそちらを優先し、無い場合のみ
        # 従来通りA01_NARRATION_DIR(記事非依存の共有元)を使う。既存の
        # 他テーマ(hanshin/health/household等)は従来通りA01_NARRATION_DIR
        # を使い続けるため挙動は変わらない。
        local_path = f"{narration_dir}/{name}.wav"
        source_path = local_path if os.path.exists(local_path) else f"{A01_NARRATION_DIR}/{name}.wav"
        mono, sr, _, _ = common.read_wav_float(source_path)
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title"):
        mono, sr, _, _ = common.read_wav_float(f"{config['b1_out_dir']}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for i in range(1, 6):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/meaning_{i}.wav")
        assert sr == common.SAMPLE_RATE
        narration[f"meaning_{i}"] = mono

    key_phrase_components = {}
    for kp in config["key_phrases"]:
        path = _adopted_component_path(config, kp)
        mono, sr, _, _ = common.read_wav_float(path)
        key_phrase_components[kp["number"]] = p9a.p7c.tight_speech_only(mono, sr)

    a2_segments = {}
    for name, _text, _lang, _sub, _max in config["segments"]:
        if name == "preview":
            continue
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "narration": narration,
        "key_phrase_components": key_phrase_components,
        "a2_segments": a2_segments,
    }


def apply_gain_and_convert(sources: dict) -> dict:
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["a2_segments"]["full_story_part1"])) / 2
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
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_final = outro_matched * OUTRO_EXTRA_GAIN_LINEAR
    result["outro"] = outro_final
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "extra_perceived_loudness_target": OUTRO_PERCEIVED_LOUDNESS_TARGET,
        "extra_gain_db": round(float(OUTRO_EXTRA_GAIN_DB), 3),
        "extra_gain_linear": round(float(OUTRO_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_final), 5), "peak_final": round(p9a.peak(outro_final), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo = {}
    for number, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{number}")
        key_phrase_stereo[number] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo

    a2_stereo = {}
    for name, mono in sources["a2_segments"].items():
        gained = gain_to_rms(mono, target_rms, f"a2_{name}")
        a2_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    result["a2_segments"] = a2_stereo

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(新規Preview音声を保持)"}
    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(config: dict, parts: dict) -> list:
    blocks = []
    for i, kp in enumerate(config["key_phrases"]):
        num_key = f"num_{kp['number'].lower()}"
        meaning_key = f"meaning_{i + 1}"
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][kp["number"]], parts[meaning_key], SR)
        blocks.append(block)
    return blocks


def build_pieces_with_timeline(config: dict, parts: dict) -> list:
    key_phrase_blocks = build_key_phrase_blocks(config, parts)
    a2 = parts["a2_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Japanese title", parts["japanese_title"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Point explanation", parts["point_explanation"]),
        ("pause_0.7_point_explanation", p9a.silence_stereo(POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Preview", parts["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i + 1}" for i in range(len(key_phrase_blocks)))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro", parts["full_story_intro"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 1", a2["comment_1"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 1", a2["full_story_part1"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 2", a2["comment_2"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 2", a2["full_story_part2"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 3", a2["comment_3"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Point One", a2["point_one"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Point Two", a2["point_two"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 4", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Outro", parts["outro"]),
    ]
    return seq


def assemble_with_timeline(config: dict, parts: dict) -> dict:
    seq = build_pieces_with_timeline(config, parts)
    pieces = [samples for _, samples in seq]
    assembled = np.ascontiguousarray(np.concatenate(pieces, axis=0))

    timeline = []
    t = 0.0
    for name, samples in seq:
        dur = len(samples) / SR
        timeline.append({"part": name, "start_seconds": round(t, 3), "duration_seconds": round(dur, 3)})
        t += dur

    return {"assembled": assembled, "timeline": timeline, "total_duration_seconds": round(t, 3)}


def stage_assemble(config: dict) -> dict:
    os.makedirs(f"{config['out_dir']}/assembled", exist_ok=True)
    os.makedirs(f"{config['out_dir']}/audit", exist_ok=True)
    sources = load_all_sources(config)
    parts = apply_gain_and_convert(sources)
    result = assemble_with_timeline(config, parts)
    assembled = result["assembled"]

    out_path = f"{config['out_dir']}/assembled/English_Your_Way_A2_{config['article_id']}.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{config['out_dir']}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{config['out_dir']}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "timeline": result["timeline"],
    }


def run_all(config: dict) -> dict:
    r1 = generate_text_segments(config)
    print(f"[{config['article_id']}] generate_text_segments status:", r1["status"])
    if r1["status"] != "OK":
        return {"text_segments": r1}

    r2 = generate_key_phrase_components(config)
    print(f"[{config['article_id']}] generate_key_phrase_components status:", r2["status"])
    if r2["status"] != "OK":
        return {"text_segments": r1, "key_phrase_components": r2}

    r3 = stage_assemble(config)
    print(f"[{config['article_id']}] stage_assemble status:", r3["status"],
          "duration:", r3["duration_seconds"], "peak:", r3["peak"], "clipping:", r3["clipping_detected"])
    return {"text_segments": r1, "key_phrase_components": r2, "assemble": r3}
