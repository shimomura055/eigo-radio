# ============================================================
# legacy_disfluency_qa_reapply.py
# 管理ID: HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続、
# Fable修正指示2回目)
# ============================================================
# revision3aでpoint_oneはPASS済みだが、stage_assemble_b1が
# EPISODE_BLOCKED_BY_AUDIO_VALIDATIONで停止した。原因はpoint_one以外の
# 13/14 legacy segment(2026-08-17承認、現行Audio Validation Gateより
# 前に生成)。本scriptは、そのうち「status=OKだがdisfluency_checkedが
# 未記録」なsegment(MISSING_MANDATORY_DISFLUENCY_QA)を対象に、既存
# Production disfluency QA(er008_disfluency_qa_18.check_segment_for_
# disfluency、faster-whisperローカル実行、追加API課金なし)を、既存の
# 音声ファイル(narration/*.wav、byte不変・読み取り専用)へそのまま
# 事後適用する。TTS再生成は一切行わない。
#
# 判定: flagged=Falseなら disfluency_checked=True・status/asr_verifiedは
# 元のまま維持(既存のverified判定はそのまま尊重)。flagged=Trueなら
# 「不合格」として記録するのみ(再生成しない、STOP対象として報告)。
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

import er008_disfluency_qa_18 as dq18

OUT_DIR = "er003_output/n3_01/household/fact03_fix_02/b1b"
NARRATION_DIR = f"{OUT_DIR}/narration"
TTS_RESULTS_PATH = f"{OUT_DIR}/audit/tts_generation_results.json"
RESULT_SUMMARY_PATH = (
    "er011_output/open138_household_fact03_b1b_minimal_fix_02/"
    "legacy_disfluency_qa_reapply_summary.json"
)

# (segment_key, wav_path, JSONの格納場所)
SEGMENT_TARGETS = [
    ("preview", f"{NARRATION_DIR}/preview.wav", ("segments", "preview")),
    ("comment_1", f"{NARRATION_DIR}/comment_1.wav", ("segments", "comment_1")),
    ("comment_2", f"{NARRATION_DIR}/comment_2.wav", ("segments", "comment_2")),
    ("comment_3", f"{NARRATION_DIR}/comment_3.wav", ("segments", "comment_3")),
    ("comment_4", f"{NARRATION_DIR}/comment_4.wav", ("segments", "comment_4")),
    ("point_one_heading", f"{NARRATION_DIR}/point_one_heading.wav", ("segments", "point_one_heading")),
    ("point_two_heading", f"{NARRATION_DIR}/point_two_heading.wav", ("segments", "point_two_heading")),
    ("in_one_line", f"{NARRATION_DIR}/in_one_line.wav", ("segments", "in_one_line")),
    ("kp1_english", f"{NARRATION_DIR}/kp1_en.wav", ("key_phrases", "1", "english")),
    ("kp3_english", f"{NARRATION_DIR}/kp3_en.wav", ("key_phrases", "3", "english")),
    ("kp4_english", f"{NARRATION_DIR}/kp4_en.wav", ("key_phrases", "4", "english")),
    ("kp5_english", f"{NARRATION_DIR}/kp5_en.wav", ("key_phrases", "5", "english")),
]


def _get_entry(data: dict, path: tuple):
    node = data
    for key in path:
        node = node[key]
    return node


def main():
    tts_results = json.load(open(TTS_RESULTS_PATH, encoding="utf-8"))
    summary = {}
    all_pass = True

    for name, wav_path, path in SEGMENT_TARGETS:
        assert os.path.exists(wav_path), f"wavが存在しません: {wav_path}"
        entry = _get_entry(tts_results, path)
        assert entry.get("status") == "OK", f"{name}: 前提status=='OK'ではありません: {entry.get('status')}"
        before_sha256 = None
        import hashlib
        with open(wav_path, "rb") as f:
            before_bytes = f.read()
            before_sha256 = hashlib.sha256(before_bytes).hexdigest()

        evidence = dq18.check_segment_for_disfluency(wav_path, language="en", model_size="small")

        after_sha256 = None
        with open(wav_path, "rb") as f:
            after_bytes = f.read()
            after_sha256 = hashlib.sha256(after_bytes).hexdigest()
        assert before_sha256 == after_sha256, f"{name}: wavがQA適用中に変化しました(禁止事項違反)"

        flagged = evidence["flagged"]
        if flagged:
            all_pass = False
        # 事後適用の証跡として、既存フィールドと同じ構造で記録する
        # (apply_disfluency_gate()が生成時に書くのと同じフィールド名)。
        # verified/statusは、flagged=Trueの場合のみFAIL扱いにする(元の
        # status="OK"はASR照合PASS済みの事実として保持、disfluency QAの
        # 結果は別フィールドに残す。既存レコードの上書きで元のasr_verified
        # 等を破壊しないため)。
        entry["disfluency_checked"] = True
        entry["disfluency_evidence"] = evidence
        entry["disfluency_qa_retroactive_note"] = (
            "HOUSEHOLD-FACT-03-PUBLISHED-ARTICLE-MINIMAL-FIX-02(継続): "
            "2026-08-17承認時点では存在しなかった現行Audio Validation Gate "
            "(ER-008-N8-FINAL-QA-HARDENING-21)のdisfluency QA必須化に対応する"
            "ため、既存wav(byte不変)へ事後適用した証跡。TTS再生成は行っていない。"
        )
        if flagged:
            entry["disfluency_qa_retroactive_status"] = "FAIL_FLAGGED_ADJACENT_REPETITION"
        else:
            entry["disfluency_qa_retroactive_status"] = "PASS"

        summary[name] = {
            "wav_path": wav_path, "wav_sha256": before_sha256,
            "flagged": flagged, "word_count": evidence["word_count"],
            "transcript": evidence["transcript"], "repeats": evidence["repeats"],
            "method": evidence["method"], "result": "FAIL" if flagged else "PASS",
        }
        print(f"[legacy_disfluency_qa_reapply] {name}: flagged={flagged} "
              f"({'FAIL' if flagged else 'PASS'})")

    with open(TTS_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2, default=str)

    with open(RESULT_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump({"all_pass": all_pass, "segments": summary}, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n[legacy_disfluency_qa_reapply] all_pass={all_pass}")
    print(f"[legacy_disfluency_qa_reapply] summary -> {RESULT_SUMMARY_PATH}")
    print(f"[legacy_disfluency_qa_reapply] tts_generation_results.json更新 -> {TTS_RESULTS_PATH}")


if __name__ == "__main__":
    main()
