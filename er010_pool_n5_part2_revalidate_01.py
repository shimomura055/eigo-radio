# -*- coding: utf-8 -*-
# ============================================================
# er010_pool_n5_part2_revalidate_01.py
# ============================================================
# No.5(pool_n5_cafes) B1 full_story_part2は、日付発話形修正
# ("April 28, 2026," -> "April twenty eighth, 2026,")後の再生成で、
# 6回中attempt6が実際には正しく"28th"と発話されたASR結果を得ていたが、
# 当時のnormalize_numeric()に複合序数("twenty eighth"型)の正規化バグ
# (ER-010-DATE-SPOKEN-FORM-POINT-FIX-01で修正)があったため、正しい
# 音声が誤ってTRUE_CONTENT_MISMATCHと判定されていた。
#
# validatorのバグを修正した上で、既に実際に生成済みの音声・ASR結果
# (新規API呼び出しは行わない)を現行のclassify_asr_match()で再判定し、
# 記録を訂正する。音声ファイル自体は変更しない(attempt6の音声が既に
# narration/full_story_part2.wavとしてdisk上に存在する)。
from __future__ import annotations

import json

import er003_v1_n3_01_tts_generate as tg
import er006_preprod_hardening_01_validation as v

OUT_DIR_B1 = "er006_output/pool_pilot_01/pool_n5_cafes/b1b"
RESULTS_PATH = f"{OUT_DIR_B1}/audit/tts_generation_results.json"


def main():
    results = tg.load_json(RESULTS_PATH)
    entry = results["segments"]["full_story_part2"]
    canonical = entry["canonical_text"]
    last_attempt = entry["attempts_log"][-1]
    asr_text = last_attempt["asr_text"]

    cls = v.classify_asr_match(canonical, asr_text)
    print(f"[N5-PART2-REVALIDATE] attempt {last_attempt['attempt']} reclassified as "
          f"{cls.classification} (should_pass={cls.should_pass})")
    if not cls.should_pass:
        raise SystemExit(f"再判定してもPASSしません: {cls.reason}。音声の取り直しが必要です。")

    entry["status"] = "OK"
    entry["asr_verified"] = True
    entry["asr_text"] = asr_text
    entry["reason"] = (
        "attempt6の音声は当初のnormalize_numeric()の複合序数正規化バグ(ER-010-DATE-"
        "SPOKEN-FORM-POINT-FIX-01で修正、'twenty eighth'が'20'+'8th'に分裂していた)"
        "によりTRUE_CONTENT_MISMATCHと誤判定されていた。バグ修正後にclassify_asr_match()"
        "で再判定した結果、実際には正しく'28th'と発話されていたことを確認し、新規TTS/ASR"
        "呼び出し無しでstatus=OKへ訂正した(音声ファイル自体は無変更)。"
    )
    entry["revalidated_after_ordinal_fix"] = True

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_status = {k: v_.get("status") for k, v_ in results["segments"].items()}
    print("[N5-PART2-REVALIDATE] segment_status:", json.dumps(all_status, ensure_ascii=False))


if __name__ == "__main__":
    main()
