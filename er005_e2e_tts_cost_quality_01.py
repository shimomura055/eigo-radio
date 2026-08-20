# ER-005-E2E-TTS-COST-QUALITY-01
# Text Episode(ER-005-SUPPORT-COST-QUALITY-01完成分)→ Audio End-to-End。
# 既存production TTS/Assembly Architecture(er003_v1_n3_01_tts_generate.py /
# er003_v1_n3_01_assemble.py、および両者が依存する下位モジュール)を完全に
# 無変更のまま再利用する。新theme_id用に、SUPPORT-COST-QUALITY-01の出力を
# production側が期待するディレクトリ構造(<out_dir>/b1b、<out_dir>/a2)へ
# コピーし、production関数へ渡すtheme dictのout_dirだけを差し替える。
from __future__ import annotations

import json
import os
import shutil

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_n3_01_assemble as assemble

THEME_ID = "screentime_conflict_e2e01"
OUT_DIR = "er005_output/e2e_tts_cost_quality_01"
SUPPORT_DIR = "er005_output/support_cost_quality_01"

THEME = {"theme_id": THEME_ID, "out_dir": OUT_DIR}

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")


def prepare_directories() -> None:
    """SUPPORT-COST-QUALITY-01の成果物を、production TTS/Assembleが期待する
    <out_dir>/b1b, <out_dir>/a2 構造へコピーする(新規生成ではなく、既存の
    承認済みJSON成果物をそのまま再配置するだけ)。"""
    b1b_dir = f"{OUT_DIR}/b1b"
    a2_dir = f"{OUT_DIR}/a2"
    os.makedirs(f"{b1b_dir}/key_phrases", exist_ok=True)
    os.makedirs(f"{a2_dir}/key_phrases", exist_ok=True)
    os.makedirs(f"{b1b_dir}/audit", exist_ok=True)
    os.makedirs(f"{a2_dir}/audit", exist_ok=True)

    shutil.copyfile(f"{SUPPORT_DIR}/b1/parts.json", f"{b1b_dir}/parts.json")
    shutil.copyfile(f"{SUPPORT_DIR}/b1/b1_support_texts.json", f"{b1b_dir}/b1_support_texts.json")
    shutil.copyfile(f"{SUPPORT_DIR}/b1/key_phrases/keywords_canonicalized.json",
                     f"{b1b_dir}/key_phrases/keywords_canonicalized.json")

    shutil.copyfile(f"{SUPPORT_DIR}/a2/parts.json", f"{a2_dir}/parts.json")
    shutil.copyfile(f"{SUPPORT_DIR}/a2/a2_support_texts.json", f"{a2_dir}/a2_support_texts.json")
    shutil.copyfile(f"{SUPPORT_DIR}/a2/key_phrases/keywords_canonicalized.json",
                     f"{a2_dir}/key_phrases/keywords_canonicalized.json")


# ============================================================
# A2の日本語タイトルはproduction側でtheme_idごとに手書きされた辞書
# (JAPANESE_TITLES)を引くため、新theme_id分をここで用意する。
# 内容は承認済みA2英語タイトルの翻訳のみ(新しいFactは加えない)。
# ============================================================
TITLE_TRANSLATION_DEVELOPER_MESSAGE = (
    "あなたは翻訳者です。与えられた英語のニュースタイトルを、自然な日本語の"
    "ニュースタイトルへ翻訳してください。新しい情報を加えず、意訳し過ぎず、"
    "自然な日本語にしてください。出力は翻訳結果のみとしてください。"
)


def translate_title_to_japanese(client, english_title: str) -> str:
    with cl.logging_context("e2e_tts_cost_quality", "a2_japanese_title_translation"):
        resp = client.responses.create(
            model="gpt-5.6-luna", reasoning={"effort": "low"},
            input=[{"role": "developer", "content": TITLE_TRANSLATION_DEVELOPER_MESSAGE},
                   {"role": "user", "content": english_title}],
        )
    return resp.output_text.strip()


if __name__ == "__main__":
    import sys

    prepare_directories()

    client = vfl01.get_client()
    with open(f"{OUT_DIR}/a2/parts.json", encoding="utf-8") as f:
        a2_parts = json.load(f)
    japanese_title = translate_title_to_japanese(client, a2_parts["title"])
    tts_gen.JAPANESE_TITLES[THEME_ID] = japanese_title
    print(f"[E2E-TTS] A2 japanese_title(翻訳): {japanese_title!r}")
    with open(f"{OUT_DIR}/japanese_title.json", "w", encoding="utf-8") as f:
        json.dump({"english_title": a2_parts["title"], "japanese_title": japanese_title}, f,
                   ensure_ascii=False, indent=2)

    target = sys.argv[1] if len(sys.argv) > 1 else "both"

    if target in ("b1", "both"):
        print("[E2E-TTS] B1 segment生成開始...")
        b1_tts_result = tts_gen.generate_b1_segments(THEME)
        print("[E2E-TTS] B1 assembly開始...")
        b1_assemble_result = assemble.stage_assemble_b1(THEME)
        print(f"[E2E-TTS] B1完了。 {b1_assemble_result}")

    if target in ("a2", "both"):
        print("[E2E-TTS] A2 segment生成開始...")
        a2_tts_result = tts_gen.generate_a2_segments(THEME)
        print("[E2E-TTS] A2 assembly開始...")
        a2_assemble_result = assemble.stage_assemble_a2(THEME)
        print(f"[E2E-TTS] A2完了。 {a2_assemble_result}")

    print("[E2E-TTS] 全工程完了。")
