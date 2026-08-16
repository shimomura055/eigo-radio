# ============================================================
# er003_v1_jp_reading_safety_verify.py
# ER-003-AUDIO-JP-READING-SAFETY-01: 実TTS/ASRによる限定検証
# ============================================================
# to_tts_safe_japanese_fraction_reading()が実際のTTS生成において
# 技術的に問題なく受理されるか、ASR書き起こし結果がどうなるかを、
# 複数の分数例で記録する(記事Full Audioの再生成・再assembleは行わない、
# 単体segmentのみの検証)。
#
# 重要: ASR書き起こしの一致だけを対策の成功根拠にしない。「ごぶんの
# いち」「ごふんのいち」いずれもAzure STTは分数として認識すると同じ
# 数字表記へ正規化する可能性があるため、ASRはこの読み間違いを区別
# できない(仕様書に明記された構造的限界)。ここでは(1)TTS技術的に
# 問題なく音声化できること、(2)TTS入力に「ぶん」という読みが明示
# されていることをコードレベルで確認できること、の2点を記録する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_jp_reading_safety_verify.py

from __future__ import annotations

import json

import er003_audio_tts_asr_safety as safety
import er003_b1_p4_audio as p4
import er003_b1_p9a_audio as p9a

OUT_DIR = "er003_output/jp_reading_safety_01"
NARRATION_DIR = f"{OUT_DIR}/narration"

FRACTION_EXAMPLES = ["2分の1", "3分の1", "4分の3", "5分の1", "10分の3"]


def main():
    import os
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    results = []
    for i, canonical_text in enumerate(FRACTION_EXAMPLES, start=1):
        tts_input = safety.to_tts_safe_japanese_fraction_reading(canonical_text)
        contains_bun_reading = "ぶんの" in tts_input
        out_path = f"{NARRATION_DIR}/fraction_{i}.wav"

        print(f"[VERIFY] {i}. canonical={canonical_text!r} tts_input={tts_input!r} "
              f"(ぶん明示: {contains_bun_reading})")
        r = p9a.generate_narration_snippet(tts_input, "ja", out_path)
        tts_status = r.get("status")
        asr_text, asr_err = (None, None)
        if tts_status == "OK":
            asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="ja-JP")
        print(f"         TTS status={tts_status} ASR text={asr_text!r} ASR error={asr_err!r}")

        results.append({
            "canonical_display_text": canonical_text,
            "tts_input_text": tts_input,
            "tts_input_contains_explicit_bun_reading": contains_bun_reading,
            "tts_status": tts_status,
            "tts_reason": r.get("reason"),
            "asr_text": asr_text,
            "asr_error": asr_err,
            "note": ("ASR書き起こしは分数として正規化されるため、正しい読み"
                     "(ぶん)と誤った読み(ふん)を区別する証拠にはならない。"
                     "ここではTTSが技術的に問題なく音声化できたこと、および"
                     "入力テキストに明示的な「ぶん」読みが含まれていたことの"
                     "記録のみを目的とする。"),
        })

    with open(f"{OUT_DIR}/audit/verification_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    all_tts_ok = all(r["tts_status"] == "OK" for r in results)
    all_contain_bun = all(r["tts_input_contains_explicit_bun_reading"] for r in results)
    summary = {"status": "OK" if (all_tts_ok and all_contain_bun) else "REVIEW_REQUIRED",
               "all_tts_ok": all_tts_ok, "all_contain_explicit_bun_reading": all_contain_bun,
               "count": len(results)}
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("[VERIFY] 完了。summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
