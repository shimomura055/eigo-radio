# ============================================================
# er011_open117_keyphrase_tilde_gate_recheck_01.py
# 管理ID: OPEN-117-KEYPHRASE-TILDE-GATE-RECHECK-01
# ============================================================
# 目的: Key Phrase日本語gloss中の「～」(placeholder疑い)について、
# (1) Production TTSが実際にどう発話するか、を切り分けて確認する
# (read-only調査+Trial-only TTS確認)。
#
# 実装方針(ユーザー指示厳守):
# - Production関数(er003_v1_sing01_voice01_generate.generate_charon_
#   japanese、voice=Charon、model=p9a.JAPANESE_MODEL_NAME、Batch API、
#   JAPANESE_STYLE_PREFIX)を「そのまま」直接呼ぶ。
# - 呼び出し経路は generate_charon_japanese_with_reading_safety
#   (er003_v1_n3_01_tts_generate.py)ではなく、その内部が最終的に
#   呼んでいる generate_charon_japanese そのもの。したがって
#   tts_safe_ja()によるlstrip、detect_gloss_placeholder_notation()に
#   よるゲートのどちらも通らない(=「ゲートを迂回する」のではなく、
#   ゲートより手前・より低レベルの関数を直接呼ぶことで、TTSモデルが
#   与えたテキストへ実際にどう反応するかだけを見る)。
# - Productionコード自体は一切変更・monkeypatchしない。
# - ASR検証・Cascade判定・Duration異常検知は、generate_charon_japanese
#   内部の既存Production機構(ja_secondary.evaluate_attempt_ja_with_
#   cascade、safety.detect_duration_anomaly)がそのまま働く(このTrial
#   scriptはそれを再実装しない)。
# - cost計測はer005_cost_logger.install()経由(Production標準の
#   計測経路をそのまま使う)。
#
# 対象テキスト:
#   (a) "～を示す"                          単一の先頭「～」(全角チルダ)
#   (b) "～を示す、～を指し示す"             Trial-13 kp4_ja実gloss(先頭+
#                                            読点直後の2箇所に「～」)
#   (c) "何かを示す"                         対照: placeholderを「何か」で
#                                            解決した自然な日本語
#   (d) "〜を示す"                          対照: (a)と同じだが波ダッシュ
#                                            (U+301C)を使用
# ============================================================
from __future__ import annotations

import json
import os

import er005_cost_logger as cl
import er003_v1_sing01_voice01_generate as voice01

OUT_DIR = "er011_output/open117_keyphrase_tilde_gate_recheck_01"
NARRATION_DIR = f"{OUT_DIR}/trial/narration"

CASES = [
    {"id": "a_single_leading_fullwidth_tilde", "text": "～を示す",
     "note": "単一の先頭「～」(U+FF5E)。tts_safe_ja()を通せば本来lstripされる文字を、"
             "意図的に未加工のままTTSへ渡す。"},
    {"id": "b_trial13_kp4_ja_full_gloss", "text": "～を示す、～を指し示す",
     "note": "Trial-13 kp4_ja(\"point to\")の実canonical gloss全体。先頭+読点直後の2箇所に「～」。"
             "現行Production経路ではdetect_gloss_placeholder_notation()でSTOPPEDになり、"
             "そもそもTTS呼び出しへ到達しない(このTrialはその手前の低レベル関数を直接呼び、"
             "仮にゲートが無かった場合にTTSが実際にどう読むかを確認する)。"},
    {"id": "c_control_replaced_with_nanika", "text": "何かを示す",
     "note": "対照: placeholderを「何か」で解決した自然な日本語(比較基準)。"},
    {"id": "d_control_wave_dash", "text": "〜を示す",
     "note": "対照: (a)と同じ意味だが波ダッシュ(U+301C)を使用。"
             "Production側のdetect_gloss_placeholder_notation()/tts_safe_ja()は"
             "U+FF5E/U+301Cの両方を対象にしている(既存コード確認済み)。"},
]


def run_one(case: dict) -> dict:
    case_id = case["id"]
    text = case["text"]
    out_path = f"{NARRATION_DIR}/{case_id}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print(f"[OPEN-117] case={case_id} text={text!r} -> {out_path}")
    with cl.logging_context("open117_tilde_gate_recheck", case_id):
        # Production関数を直接呼ぶ(引数のexpected_substringは関数内部で
        # 未使用の後方互換パラメータであることをコード確認済み。判定へは
        # 影響しない)。
        result = voice01.generate_charon_japanese(text, out_path, text[:4])
    result["case_id"] = case_id
    result["input_text"] = text
    result["note"] = case["note"]
    print(f"[OPEN-117] case={case_id}: status={result.get('status')} "
          f"asr_text={result.get('asr_text')!r}")
    return result


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log_open117.jsonl")

    results = {}
    for case in CASES:
        results[case["id"]] = run_one(case)

    with open(f"{OUT_DIR}/results_open117.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print("\n=== SUMMARY ===")
    for case_id, r in results.items():
        print(f"{case_id}: status={r.get('status')} asr_text={r.get('asr_text')!r} "
              f"asr_verified={r.get('asr_verified')}")


if __name__ == "__main__":
    main()
