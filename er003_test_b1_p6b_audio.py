# ============================================================
# er003_test_b1_p6b_audio.py
# ER-003-B1-P6B: 2-Macrochunk・marker境界改善のテスト
# ============================================================
# 実TTS呼び出しは行わない。2-Macrochunk分割・MFA境界の重複確認・
# サンプル位置変換ロジックを対象とする。P6Aのchunk03(RMSベースの
# find_speech_boundsが検出失敗した実データ)を回帰テストの材料として
# 再利用し、新しいMFA境界オンリー方式がその実データに対して問題なく
# 動作することを実証する。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p6b_audio -v

import json
import unittest

import er002_common as common
import er003_b1_p3w_audio as p3w
import er003_b1_p3z_audio as p3z
import er003_b1_p4_audio as p4
import er003_b1_p6b_audio as p6b


def _real_pattern_a_and_used_forms():
    with open("er003_output/b1_p2/A01/listening_preview_raw.md", encoding="utf-8") as f:
        data = json.load(f)
    pattern_a = next(p for p in data["patterns"] if p["pattern_id"] == "A")
    return pattern_a["text"], pattern_a["used_forms"]


class BuildMacrochunkPlanTests(unittest.TestCase):

    def test_produces_two_chunks(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6b.build_macrochunk_plan(text, used_forms)
        self.assertEqual(len(plan), 2)

    def test_reconstructs_pattern_a_exactly(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6b.build_macrochunk_plan(text, used_forms)
        reconstructed = "".join(c["source_text"] for c in plan)
        self.assertEqual(reconstructed, text)

    def test_macrochunk_a_has_three_markers_macrochunk_b_has_two(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6b.build_macrochunk_plan(text, used_forms)
        self.assertEqual(plan[0]["used_forms"], ["shot on target", "take players off", "a narrow lead"])
        self.assertEqual(plan[1]["used_forms"], ["close the door to the final", "stoppage time"])

    def test_static_verification_passes(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6b.build_macrochunk_plan(text, used_forms)
        result = p6b.verify_macrochunk_plan_static(plan, text)
        self.assertTrue(result["all_passed"], msg=result)
        self.assertEqual(result["total_marker_count"], 5)

    def test_macrochunk_a_contains_kanji_target_phrases(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6b.build_macrochunk_plan(text, used_forms)
        self.assertIn("選手を交代で下げる", plan[0]["source_text"])
        self.assertIn("わずかなリード", plan[0]["source_text"])

    def test_macrochunk_b_contains_last_few_minutes_and_nani_ga_okiru(self):
        text, used_forms = _real_pattern_a_and_used_forms()
        plan = p6b.build_macrochunk_plan(text, used_forms)
        self.assertIn("最後の数分", plan[1]["source_text"])
        self.assertIn("何が起きるのでしょうか", plan[1]["source_text"])


class VerifySpansNoOverlapTests(unittest.TestCase):

    def test_real_p6a_chunk03_spans_pass(self):
        # P6Aで実際に生成・保存済みのchunk03(2marker)のTextGridを再利用
        # する(新規TTS/MFA呼び出しなし)。
        words = p3w.parse_textgrid_words_tier("er003_output/b1_p6a/A01/preview/alignment/chunk03_ja.TextGrid")
        marker_specs = [
            {"marker_id": "m1", "token_sequence": p6b.MARKER_TOKEN_SEQUENCE},
            {"marker_id": "m2", "token_sequence": p6b.MARKER_TOKEN_SEQUENCE},
        ]
        spans, errors = p4.find_all_marker_spans(words, marker_specs)
        self.assertEqual(errors, [])
        result = p6b.verify_spans_no_overlap_with_adjacent_tokens(spans)
        self.assertTrue(result["all_passed"], msg=result)

    def test_detects_overlap(self):
        spans = [{
            "marker_id": "m1", "preceding_token": "x", "preceding_end_seconds": 5.0,
            "start_seconds": 4.9, "end_seconds": 5.5,
            "following_token": "y", "following_start_seconds": 5.6,
        }]
        result = p6b.verify_spans_no_overlap_with_adjacent_tokens(spans)
        self.assertFalse(result["all_passed"])
        self.assertFalse(result["per_span_checks"][0]["no_overlap_before"])


class MfaAnchorSampleTests(unittest.TestCase):

    def test_converts_absolute_to_relative_sample(self):
        sr = 24000
        sample = p6b.mfa_anchor_sample(seconds=5.0, segment_start_seconds=3.0, sr=sr)
        self.assertEqual(sample, int(round(2.0 * sr)))

    def test_zero_offset(self):
        sr = 24000
        sample = p6b.mfa_anchor_sample(seconds=3.0, segment_start_seconds=3.0, sr=sr)
        self.assertEqual(sample, 0)


class Chunk03RegressionSpliceTests(unittest.TestCase):
    """P6Aでchunk03停止の原因となった実データ(2件目markerの後が
    「へ。」約0.221秒、RMS最大値0.00119、閾値0.02の約1/17)に対し、
    MFA境界のみを使うadjust_leading_silenceが問題なく成功することを
    実証する回帰テスト(新規TTS/MFA呼び出しなし、既存wav/TextGridを
    再利用)。"""

    def test_mfa_boundary_approach_succeeds_where_rms_failed(self):
        wav_path = "er003_output/b1_p6a/A01/preview/ja_chunks/chunk03_ja.wav"
        textgrid_path = "er003_output/b1_p6a/A01/preview/alignment/chunk03_ja.TextGrid"

        samples, sr, ch, _ = common.read_wav_float(wav_path)
        words = p3w.parse_textgrid_words_tier(textgrid_path)
        marker_specs = [
            {"marker_id": "m1", "token_sequence": p6b.MARKER_TOKEN_SEQUENCE},
            {"marker_id": "m2", "token_sequence": p6b.MARKER_TOKEN_SEQUENCE},
        ]
        spans, errors = p4.find_all_marker_spans(words, marker_specs)
        self.assertEqual(errors, [])

        marker2 = spans[1]
        # segment2 = 2件目marker終了時点からchunk末尾までの区間
        seg2_start_sample = int(round(marker2["end_seconds"] * sr))
        seg2 = samples[seg2_start_sample:]

        # P6A(旧方式)はここでfind_speech_boundsを呼び、Noneが返って
        # いた(実機確認済み)。P6B(新方式)はMFAのfollowing_token開始
        # 時刻を直接使うため、RMS検出を一切必要としない。
        true_content_start_sample = p6b.mfa_anchor_sample(
            seconds=marker2["following_start_seconds"], segment_start_seconds=marker2["end_seconds"], sr=sr)
        self.assertGreaterEqual(true_content_start_sample, 0)
        self.assertLess(true_content_start_sample, len(seg2))

        needed_leading = round(p6b.GAP_AFTER_TARGET_SECONDS - p6b.EN_TRIM_SAFETY_MARGIN_SECONDS, 4)
        adjusted, info = p3z.adjust_leading_silence(seg2, sr, true_content_start_sample, needed_leading)

        self.assertTrue(info["speech_content_unchanged"], msg="「へ」を含む実音声が変更されてはいけない")
        self.assertAlmostEqual(info["achieved_leading_seconds"], needed_leading, places=3)

        # 「へ」の実音声(true_content_start_sample以降)が、変換後も
        # 完全に残っていることを確認する(除去・伸縮されていない)。
        original_tail = seg2[true_content_start_sample:]
        adjusted_tail_start = int(round(needed_leading * sr))
        adjusted_tail = adjusted[adjusted_tail_start:]
        self.assertTrue((original_tail == adjusted_tail).all())


if __name__ == "__main__":
    unittest.main()
