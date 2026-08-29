# -*- coding: utf-8 -*-
# ============================================================
# er008_n8_final_audio_regen_20.py
# ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20
# ============================================================
# No.8(pool_n8_airport_line)のうち、今回のProduction配線で実際に
# 挙動が変わったsegmentだけを対象に、実際の本番生成関数を呼び直して
# 完成版音声へ反映する薄いスクリプト(記事全体・他segmentの再生成は
# しない)。
#   A2: Previewのtext(短縮prompt)を再生成 → 再TTS(日本語)
#   B1: Preview/Comment1-4を、calm styleでTTS再生成(text自体は不変)
from __future__ import annotations

import json
import os
import shutil
import sys

import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_scaffold_generate as scaffold
import er003_v1_n3_01_tts_generate as tg
import er003_v1_sing01_voice01_generate as voice01

BASE = "er006_output/pool_pilot_01/pool_n8_airport_line"


def backup(path: str):
    if os.path.exists(path):
        shutil.copy(path, path + ".pre_final_audio_20.bak")


def regen_a2_preview(client):
    out_dir = f"{BASE}/a2"
    narration_dir = f"{out_dir}/narration"
    support_path = f"{out_dir}/a2_support_texts.json"
    article_text = tg.load_text(f"{out_dir}/article.md")

    with open(support_path, encoding="utf-8") as f:
        support = json.load(f)
    old_preview_text = support["preview"]

    print("[N8-FINAL-AUDIO-20][a2] Preview text再生成開始(短縮prompt)...")
    preview_role = a2gen.PREVIEW_ROLE.format(
        comment_1=support["comment_1"], comment_2=support["comment_2"])
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview_result = a2gen.run_support_text(
        client, preview_role, preview_context, model=scaffold._a2_support_model())
    new_preview_text = preview_result.get("text")
    print(f"[N8-FINAL-AUDIO-20][a2] Preview旧: {len(old_preview_text)}字 / 新: {len(new_preview_text or '')}字")
    print(f"[N8-FINAL-AUDIO-20][a2] 旧文: {old_preview_text!r}")
    print(f"[N8-FINAL-AUDIO-20][a2] 新文: {new_preview_text!r}")

    if not new_preview_text:
        print("[N8-FINAL-AUDIO-20][a2] Preview再生成失敗。中断します。")
        return {"status": "FAILED", "attempts": preview_result.get("attempts")}

    backup(support_path)
    support["preview"] = new_preview_text
    with open(support_path, "w", encoding="utf-8") as f:
        json.dump(support, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/preview_regen_20_attempts.json", "w", encoding="utf-8") as f:
        json.dump(preview_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    print("[N8-FINAL-AUDIO-20][a2] Preview音声(日本語)再TTS開始...")
    r = tg.generate_a2_japanese_with_reading_safety(
        new_preview_text, f"{narration_dir}/preview.wav", tg.expected_substring_ja(new_preview_text))
    print(f"[N8-FINAL-AUDIO-20][a2] Preview音声再TTS結果: status={r.get('status')}")
    return {"status": r.get("status"), "old_text": old_preview_text, "new_text": new_preview_text, "tts_result": r}


def regen_b1_preview_and_comments():
    out_dir = f"{BASE}/b1b"
    narration_dir = f"{out_dir}/narration"
    support = tg.load_json(f"{out_dir}/b1_support_texts.json")

    results = {}
    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        print(f"[N8-FINAL-AUDIO-20][b1b] {name}再TTS開始(calm style)...")
        r = voice01.generate_charon_english(
            tg.tts_safe_number_words_en(tg.tts_safe_en(text)), f"{narration_dir}/{name}.wav",
            style_prefix_override=tg.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        r["canonical_text"] = text
        print(f"[N8-FINAL-AUDIO-20][b1b] {name}再TTS結果: status={r.get('status')} "
              f"disfluency_checked={r.get('disfluency_checked')}")
        results[name] = r
    return results


def main():
    client = a2gen.get_client()

    a2_result = regen_a2_preview(client)
    b1_results = regen_b1_preview_and_comments()

    summary = {
        "a2_preview": {k: v for k, v in a2_result.items() if k != "tts_result"},
        "b1_preview_comments": {k: {kk: vv for kk, vv in v.items() if kk not in ("attempts_log",)}
                                 for k, v in b1_results.items()},
    }
    with open(f"{BASE}/final_audio_regen_20_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[N8-FINAL-AUDIO-20] 完了。")


if __name__ == "__main__":
    main()
