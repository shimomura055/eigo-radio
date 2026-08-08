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

ARTICLE_ID = "A02"
OUT_DIR = f"er003_output/b1_p9a/{ARTICLE_ID}"
BODY_OUT_DIR = f"er003_output/b1_p8a/{ARTICLE_ID}"

B1_ARTICLE_PATH = f"er003_output/b1_p1/{ARTICLE_ID}/b1_article_raw.md"

ENGLISH_TITLE_TEXT = "UK Plans Midnight Social Media Break for Teenagers"
# 承認済み日本語マスター(master_ja_approved.md)のタイトル行から、絵文字・
# 「」囲み・見出し記号を除いた本文のみを使用する(A01のJAPANESE_TITLE_TEXT
# と同じ抽出方針)。
JAPANESE_TITLE_TEXT = "午前0時、SNSに“おやすみ”――英国が夜更かしスクロールへ静かな消灯"
JAPANESE_TITLE_SOURCE_PATH = f"er003_output/b1_p1/{ARTICLE_ID}/master_ja_approved.md"


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


if __name__ == "__main__":
    r = stage_a_generate_body_audio()
    print("stage_a status:", r["status"])
    if r["status"] == "OK":
        print(json.dumps(r["metadata"], ensure_ascii=False, indent=2))
    else:
        print("reason:", r.get("reason"))
