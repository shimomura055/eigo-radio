# ============================================================
# er003_v1_repro02_main_generate.py
# ER-003-REPRO-02-MAIN: ADD03 本文・学習セクションまとめて生成
# ============================================================
# A01/A02専用モジュールは変更しない。それらの汎用関数(パス・テキストを
# 引数に取るもの)をそのままADD03へ再利用し、ADD03固有の値(記事パス・
# タイトル・Key Phrase等)だけをこのスクリプト側で保持する
# (ER-003-REPRO-01のA02向けスクリプトと同一パターン)。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p8a_audio as p8a
import er003_b1_p9a_audio as p9a

ARTICLE_ID = "ADD03"
OUT_DIR = f"er003_output/b1_p9a/{ARTICLE_ID}"
BODY_OUT_DIR = f"er003_output/b1_p8a/{ARTICLE_ID}"

B1_ARTICLE_PATH = f"er003_output/b1_p1/{ARTICLE_ID}/b1_article_raw.md"
BODY_DYNAMICS3_PATH = f"{BODY_OUT_DIR}/body_raw/{ARTICLE_ID}_b1_body_dynamics3.wav"

ENGLISH_TITLE_TEXT = "20% Hormuz Fee Dropped, but Oil Market Remains Nervous"
# 承認済み日本語マスター(master_ja_approved.md)のタイトル行から絵文字・
# 「」・見出し記号を除いたもの(A01/A02と同じ抽出方針)。
JAPANESE_TITLE_TEXT = "20％の料金所は一夜で撤去。それでも、原油市場は静まらない"
JAPANESE_TITLE_SOURCE_PATH = f"er003_output/b1_p1/{ARTICLE_ID}/master_ja_approved.md"

# MFA(english_mfa、mfa_tool/add03_body_output/ADD03_body.TextGrid)+ASR
# (scratch_add03_title/seg1/seg2.wav)で特定した境界(絶対時刻、元の
# BODY_DYNAMICS3_PATH基準)。数字・金額・日付を多く含む記事のため、3箇所
# ともASRで前後の発話内容が書字順どおりであることを確認済み。
TITLE_END_SECONDS = 5.120  # "...Nervous"(タイトル)の終了
BODY_FIRST_WORD_START_SECONDS = 5.740  # "Imagine"(本文第1文)の開始
NATURAL_LEADING_SECONDS = 0.240  # 元音声冒頭(タイトル"20"開始前)の自然な無音

# notification2挿入①: "...ships could pass through safely."の後、
# "Today's Hormuz Risk Points"見出しの前
INSERT1_GAP_END_SECONDS = 98.670
INSERT1_GAP_START_SECONDS = 99.960

# notification2挿入②: "...freedom of navigation."の後、
# "In One Line"見出しの前
INSERT2_GAP_END_SECONDS = 149.160
INSERT2_GAP_START_SECONDS = 150.540


def stage_a_generate_body_audio() -> dict:
    """Full Story(本編)音声を生成する。初回1回、内容起因の追加試行は
    行わない(run_tts_content_attemptsの既存QA契約=最大3試行、のみに
    従う)。"""
    os.makedirs(BODY_OUT_DIR, exist_ok=True)
    plan, text, script = p8a.load_and_build_narration_plan(B1_ARTICLE_PATH)

    result = p8a.generate_article_body_audio(plan)

    if result["status"] != "OK":
        attempts_detail = []
        run_result = result.get("result")
        if run_result is not None:
            for a in run_result.attempts:
                attempts_detail.append({
                    "attempt_number": a.tts_content_attempt_number,
                    "outcome": a.outcome,
                    "reasons": a.reasons,
                    "tts_api_retry_count": a.tts_api_retry_count,
                })
        with open(f"{BODY_OUT_DIR}/body_generation_stopped.json", "w", encoding="utf-8") as f:
            json.dump({"status": result["status"], "reason": result.get("reason"),
                       "attempts_detail": attempts_detail}, f, ensure_ascii=False, indent=2, default=str)
        return {**result, "attempts_detail": attempts_detail}

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
    適用する。A01/A02の教訓に従い、時系列で後ろの編集から先に適用する
    (insert2[約149秒] → insert1[約99秒] → title_trim[約5秒])。"""
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
# Stage C/D: 新規ナレーション・Key Phrase Component生成
# ------------------------------------------------------------
# ER-003-REPRO-01(A02)で確立したstrict ASR検証(部分一致+文字数上限の
# 両方を検証し、meaning_5の28.8秒hallucinationを検出できた仕組み)と、
# minimal instructionフォールバック(opt outのhallucinationを解決した
# 仕組み)を、article非依存の汎用関数としてそのまま再利用する
# (ADD03固有の例外処理は追加しない)。
import er003_v1_repro01_main_generate as repro01

generate_narration_snippet_verified_strict = repro01.generate_narration_snippet_verified_strict
generate_key_phrase_component_verified = repro01.generate_key_phrase_component_verified

A01_NARRATION_DIR = repro01.A01_NARRATION_DIR
SERVICE_LEVEL_NARRATION_NAMES = repro01.SERVICE_LEVEL_NARRATION_NAMES

TOPIC_INTRO_TEXT = f"Today's topic is {ENGLISH_TITLE_TEXT}."

# ER-003-REPRO-02で承認されたKey Phrase 5件(方式L+KP-02-R1)。
# 日本語訳は、canonicalization出力のjapanese_glossが読点区切りで2案
# 提示されている項目(be in place/smell of gunpowder)について、最初の
# 案をそのまま採用した(意訳の追加改善はしていない、A01の"close the
# door to"のような文脈語の補完も行っていない)。
KEY_PHRASES_USED_FORM = {
    1: "blockade",
    2: "be in place",
    3: "freedom of navigation",
    4: "tollbooth",
    5: "smell of gunpowder",
}
KEY_PHRASE_MEANINGS = {
    1: "海上封鎖",
    2: "実施中である",
    3: "航行の自由",
    4: "料金所",
    5: "火薬のにおい",
}
_MEANING_ASR_SUBSTRINGS = {1: "封鎖", 2: "実施中", 3: "航行", 4: "料金所", 5: "火薬"}


def stage_c_generate_new_narrations() -> dict:
    narration_dir = f"{OUT_DIR}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    results = {}

    jobs = [
        ("topic_intro", TOPIC_INTRO_TEXT, "en", "Hormuz Fee Dropped"),
        ("japanese_title", JAPANESE_TITLE_TEXT, "ja", "料金所"),
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


def stage_d_generate_key_phrase_components() -> dict:
    components_dir = f"{OUT_DIR}/key_phrase_components"
    os.makedirs(components_dir, exist_ok=True)
    results = {}
    for i in range(1, 6):
        text = KEY_PHRASES_USED_FORM[i]
        safe_name = text.replace(" ", "_")
        out_path = f"{components_dir}/kp_{i}_{safe_name}.wav"
        result = generate_key_phrase_component_verified(text, out_path)
        results[i] = result

    with open(f"{OUT_DIR}/audit/key_phrase_components_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_ok = all(r.get("status") == "OK" for r in results.values())
    return {"status": "OK" if all_ok else "STOPPED", "results": results}


if __name__ == "__main__":
    r = stage_a_generate_body_audio()
    print("stage_a status:", r["status"])
    if r["status"] == "OK":
        print(json.dumps(r["metadata"], ensure_ascii=False, indent=2))
    else:
        print("reason:", r.get("reason"))
