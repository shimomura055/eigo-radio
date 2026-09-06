# ============================================================
# er011_open117_keyphrase_display_tts_separation_trial_01.py
# 管理ID: OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-01(Phase 1)
# ============================================================
# 目的: Key Phrase日本語訳について「表示用の辞書的表記」(例: "～を示す")と
# 「TTS読み上げ用テキスト」(例: "なになにを示す")を分離する方式が、
# Production標準TTS(Batch API)で安定して発話できるかを確認する
# (Trial-only, Production変更なし)。
#
# 背景: OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01で、「～」を含む訳語は
# TTSが助詞始まりの断片を安定して読めず3/3不合格(「何かを示す」は1/1合格)と
# 確定した。今回はplaceholder記号を消すのではなく、"なになに"という
# 口語的な不定代名詞に置き換えたTTS用テキストが安定するかを見る。
#
# 実装方針(RECHECK-01と同一のTrial方式を再利用、ユーザー指示厳守):
# - Production関数 er003_v1_sing01_voice01_generate.generate_charon_
#   japanese(voice=Charon、model=p9a.JAPANESE_MODEL_NAME、Batch API、
#   JAPANESE_STYLE_PREFIX)を「そのまま」直接呼ぶ。
# - この関数はplaceholderゲート(detect_gloss_placeholder_notation)より
#   手前・より低レベルにある。今回のTTS用テキストはいずれも「～」等の
#   placeholder記号を含まないため、Production正式経路
#   (generate_charon_japanese_with_reading_safety)を通しても本来ゲートには
#   引っかからない対象である。低レベル関数を直接呼ぶのは、RECHECK-01との
#   手法的一貫性のため。
# - Productionコード自体は一切変更・monkeypatchしない。
# - ASR検証・Cascade判定・Duration異常検知は、generate_charon_japanese
#   内部の既存Production機構がそのまま働く(このTrial scriptは再実装しない)。
# - cost計測はer005_cost_logger.install()経由(Production標準の計測経路)。
# ============================================================
from __future__ import annotations

import json
import os

import er005_cost_logger as cl
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = "er011_output/open117_keyphrase_display_tts_separation_trial_01"
NARRATION_DIR = f"{OUT_DIR}/trial/narration"

# 各caseは (id, display_text, tts_text, note) を持つ。
# display_textはユーザーに見せる表示用表記(TTSへは渡さない、参考記録用)。
# tts_textが実際にTTSへ渡すテキスト。
CASES = [
    # --- 主対象4件、run1(1回目) ---
    {"id": "p1_shimesu_run1", "display": "～を示す", "text": "なになにを示す",
     "note": "主対象1「示す」のTTS用表現。run1。"},
    {"id": "p2_sasu_run1", "display": "～を指す", "text": "なになにを指す",
     "note": "主対象2「指す」のTTS用表現。run1。"},
    {"id": "p3_tsunagaru_run1", "display": "～につながる", "text": "なになににつながる",
     "note": "主対象3「につながる」のTTS用表現。run1。"},
    {"id": "p4_imisuru_run1", "display": "～を意味する", "text": "なになにを意味する",
     "note": "主対象4「意味する」のTTS用表現。run1。"},
    # --- 主対象4件、run2(再現性確認のための2回目) ---
    {"id": "p1_shimesu_run2", "display": "～を示す", "text": "なになにを示す",
     "note": "主対象1の再現性確認run2。"},
    {"id": "p2_sasu_run2", "display": "～を指す", "text": "なになにを指す",
     "note": "主対象2の再現性確認run2。"},
    {"id": "p3_tsunagaru_run2", "display": "～につながる", "text": "なになににつながる",
     "note": "主対象3の再現性確認run2。"},
    {"id": "p4_imisuru_run2", "display": "～を意味する", "text": "なになにを意味する",
     "note": "主対象4の再現性確認run2。"},
    # --- 対照A: RECHECK-01で合格した「何かを示す」(表示用=TTS用、分離なし) ---
    {"id": "control_a_nanika", "display": "何かを示す", "text": "何かを示す",
     "note": "対照A。RECHECK-01で1/1合格した表現。今回のBatch呼び出し内での"
             "「なになに」との比較用に同一run内で再実行する。"},
    # --- 対照B: 複合形(2箇所「なになに」) ---
    {"id": "control_b_compound", "display": "～を示す、～を指し示す",
     "text": "なになにを示す、なになにを指し示す",
     "note": "対照B。Trial-13 kp4_ja実gloss相当の複合形をなになに分離版で確認。"
             "1文中に「なになに」が2回出る場合の安定性を見る。"},
    # --- 追加の代替TTS用表現(比較用、少数) ---
    {"id": "alt1_nanika_hiragana", "display": "～を示す", "text": "なにかを示す",
     "note": "代替1。「何か」のひらがな表記(読みは同じ)。表記差の影響有無を見る。"},
    {"id": "alt2_arumono", "display": "～を示す", "text": "あるものを示す",
     "note": "代替2。「あるものを示す」(不定の対象を表す別の口語表現)。"},
]


def run_one(case: dict) -> dict:
    case_id = case["id"]
    text = case["text"]
    out_path = f"{NARRATION_DIR}/{case_id}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print(f"[OPEN-117-DISPLAY-TTS-SEP] case={case_id} display={case['display']!r} "
          f"tts_text={text!r} -> {out_path}")
    with cl.logging_context("open117_display_tts_separation_trial_01", case_id):
        # Production関数を直接呼ぶ(引数のexpected_substringは関数内部で
        # 未使用の後方互換パラメータであることをRECHECK-01でコード確認済み)。
        result = voice01.generate_charon_japanese(text, out_path, text[:4])
    result["case_id"] = case_id
    result["display_text"] = case["display"]
    result["tts_text"] = text
    result["note"] = case["note"]
    print(f"[OPEN-117-DISPLAY-TTS-SEP] case={case_id}: status={result.get('status')} "
          f"asr_text={result.get('asr_text')!r}")
    return result


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log_open117_display_tts_sep.jsonl")

    results = {}
    for case in CASES:
        results[case["id"]] = run_one(case)

    with open(f"{OUT_DIR}/results_open117_display_tts_sep.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print("\n=== SUMMARY ===")
    for case_id, r in results.items():
        print(f"{case_id}: display={r.get('display_text')!r} tts={r.get('tts_text')!r} "
              f"status={r.get('status')} asr_text={r.get('asr_text')!r}")


if __name__ == "__main__":
    main()
