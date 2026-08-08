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

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p8a_audio as p8a
import er003_b1_p9a_audio as p9a

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


if __name__ == "__main__":
    r = stage_a_generate_body_audio()
    print("stage_a status:", r["status"])
    if r["status"] == "OK":
        print(json.dumps(r["metadata"], ensure_ascii=False, indent=2))
    else:
        print("reason:", r.get("reason"))
