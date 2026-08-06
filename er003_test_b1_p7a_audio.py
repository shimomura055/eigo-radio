# ============================================================
# er003_test_b1_p7a_audio.py
# ER-003-B1-P7A: er003_b1_p7a_audioの回帰テスト
# ============================================================
# 実TTS/Azure STT/API呼び出しは行わない(合成データのみ)。

import unittest

import er003_b1_p7a_audio as p7a


class KeyExpressionCheckTests(unittest.TestCase):
    def test_all_present_when_asr_matches_input(self):
        asr_text = (
            "前半は激しい接触と緊張が続き、両チームとも枠内シュート目印を記録できないまま"
            "静かな均衡が保たれます。後半に試合が動くと、イングランドは選手を交代で下げる"
            "目印という決断で守備を固め、わずかなリード目印を守ろうとします。アルゼンチンの"
            "結晶への道を閉ざすこと。目印が現実になりそうなその時。メッシが流れを変え、"
            "ついにアディショナルタイム目印へ。最後の数分、寒気と痛みの境目で"
            "何が起きるのでしょうか。"
        )
        result = p7a.check_key_expressions(asr_text)
        self.assertTrue(result["all_key_expressions_present"])
        self.assertEqual(result["marker_count"], 5)
        self.assertTrue(result["marker_count_matches_expected"])

    def test_missing_expression_is_detected(self):
        asr_text = "前半は激しい接触と緊張が続き、目印目印目印目印目印"
        result = p7a.check_key_expressions(asr_text)
        self.assertFalse(result["all_key_expressions_present"])
        self.assertFalse(result["守備を固め"]["present"])

    def test_mispronunciation_like_p6b_is_detected_as_absent(self):
        # P6Bで実際に発生した「激しい」→「げきせつな」のような誤発音を
        # ASRが拾った場合、正しい語句「激しい接触」は不在として検出される
        # べき(本テストはロジックの回帰確認、実際のASR出力ではない)。
        asr_text = "前半はげきせつな接触と緊張が続き、目印目印目印目印目印"
        result = p7a.check_key_expressions(asr_text)
        self.assertFalse(result["激しい接触"]["present"])


class DiffInputVsAsrTests(unittest.TestCase):
    def test_identical_text_has_no_diff_ops(self):
        text = "前半は激しい接触と緊張が続き、目印を記録できないまま。"
        diff = p7a.diff_input_vs_asr(text, text)
        self.assertEqual(diff["diff_ops"], [])
        self.assertEqual(diff["similarity_ratio"], 1.0)

    def test_punctuation_only_removal_reports_delete_ops(self):
        input_text = "前半は激しい接触と、緊張が続き。"
        asr_text = "前半は激しい接触と緊張が続き。"
        diff = p7a.diff_input_vs_asr(input_text, asr_text)
        self.assertEqual(len(diff["diff_ops"]), 1)
        self.assertEqual(diff["diff_ops"][0]["tag"], "delete")
        self.assertEqual(diff["diff_ops"][0]["input_segment"], "、")

    def test_kanji_substitution_is_reported_not_silently_dropped(self):
        input_text = "アルゼンチンの決勝への道を閉ざす。"
        asr_text = "アルゼンチンの結晶への道を閉ざす。"
        diff = p7a.diff_input_vs_asr(input_text, asr_text)
        replace_ops = [op for op in diff["diff_ops"] if op["tag"] == "replace"]
        self.assertEqual(len(replace_ops), 1)
        self.assertEqual(replace_ops[0]["input_segment"], "決勝")
        self.assertEqual(replace_ops[0]["asr_segment"], "結晶")


class Sha256HelperTests(unittest.TestCase):
    def test_sha256_text_is_deterministic(self):
        self.assertEqual(p7a.sha256_text("abc"), p7a.sha256_text("abc"))
        self.assertNotEqual(p7a.sha256_text("abc"), p7a.sha256_text("abd"))


class ModuleWideConstantsTests(unittest.TestCase):
    def test_baseline_and_candidate_model_names_differ(self):
        # P7A実行当時の監査結果: baseline(gemini-2.5-pro-preview-tts)は
        # candidate(gemini-3.1-flash-tts-preview)と異なるモデルである
        # ことを前提に検証を実施した。将来baseline自体が3.1へ更新された
        # 場合はこのテストが失敗し、変化に気づけるようにする。
        self.assertNotEqual(p7a.BASELINE_MODEL_NAME, p7a.CANDIDATE_MODEL_NAME)

    def test_expected_marker_count_is_five(self):
        self.assertEqual(p7a.EXPECTED_MARKER_COUNT, 5)


if __name__ == "__main__":
    unittest.main()
