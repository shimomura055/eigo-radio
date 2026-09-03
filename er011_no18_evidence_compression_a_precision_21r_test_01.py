# ============================================================
# er011_no18_evidence_compression_a_precision_21r_test_01.py
# ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-AUDIO-21R
# ============================================================
# ユーザー正式採用のPattern A(Representative Metric + Supporting Trend)
# + Listener-Friendly Numeric Precisionが、Evidence Compression Editorの
# Production Promptへ常時組み込まれていることのプロンプト内容テスト
# (実LLM呼び出しは行わない)。Trial-18/19/20で検証した文言と完全一致
# していること、既存の絶対禁止事項リストがそのまま維持されていること、
# 初回生成・Diagnostic Full Retry共通の単一call siteのみが存在すること
# (Trial-onlyの二重配線が無いこと)を確認する。
import re
import unittest

import er003_v1_n3_01_evidence_compression_editor as ec
import er011_no18_a2_evidence_compression_extension_abc_trial_18 as trial18
import er011_no18_a2_evidence_compression_abc_precision_extension_trial_20 as trial20


class PatternAPrecisionProductionWiringTests(unittest.TestCase):
    def test_prompt_contains_pattern_a_rule_text_verbatim(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn(trial18.PATTERN_A_BLOCK_JA, prompt)

    def test_prompt_contains_purpose_block_verbatim(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn(trial18.COMMON_PURPOSE_BLOCK_EN, prompt)

    def test_prompt_contains_precision_rule_text_verbatim(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn(trial20.PRECISION_BLOCK_EN, prompt)

    def test_pattern_b_and_c_rule_text_not_present(self):
        # Pattern B/CはDEFERRED CANDIDATE/NOT REJECTED、今回未採用のためProduction
        # Promptへ混入していないことを確認する。
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertNotIn(trial18.PATTERN_B_BLOCK_JA, prompt)
        self.assertNotIn(trial18.PATTERN_C_BLOCK_JA, prompt)

    def test_ordering_purpose_then_pattern_a_then_precision_then_forbidden_edits(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        idx_purpose = prompt.find("Compression Purpose Clarification")
        idx_pattern_a = prompt.find("Pattern A - Representative Metric")
        idx_precision = prompt.find("Listener-Friendly Numeric Precision")
        idx_forbidden = prompt.find("絶対に行ってはいけない編集(Fact safety、最優先)")
        self.assertGreater(idx_purpose, -1)
        self.assertGreater(idx_pattern_a, -1)
        self.assertGreater(idx_precision, -1)
        self.assertGreater(idx_forbidden, -1)
        self.assertLess(idx_purpose, idx_pattern_a)
        self.assertLess(idx_pattern_a, idx_precision)
        self.assertLess(idx_precision, idx_forbidden)

    def test_forbidden_edits_marker_appears_exactly_once(self):
        # markerがformat前のtemplate自体にも重複していない(挿入位置の誤りで
        # markerを2回置換してしまうバグの回帰防止)。
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE
        self.assertEqual(prompt.count("絶対に行ってはいけない編集(Fact safety、最優先)"), 1)

    def test_existing_absolute_prohibitions_still_present(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        for phrase in [
            "Factの追加", "Factの削除", "certainty(確からしさ)を強めること",
            "比較の向き(comparison direction", "出来事の時系列の前後関係(temporal direction)",
        ]:
            self.assertIn(phrase, prompt)

    def test_article_text_still_substitutes_correctly(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="UNIQUE_MARKER_TEXT_XYZ")
        self.assertIn("UNIQUE_MARKER_TEXT_XYZ", prompt)
        # article_text自体に{}のようなformat特殊文字が含まれていても壊れないこと
        prompt2 = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="text with {braces}")
        self.assertIn("text with {braces}", prompt2)

    def test_single_production_call_site_for_lossless_editor(self):
        # run_one_pattern()の初回生成・Diagnostic Full Retryはいずれも
        # _generate_and_compress_article()を共通で呼ぶ(単一call site)ため、
        # ec_editor.run_lossless_editorへの参照がProductionコード上に複数
        # 独立実装されていないことをソース走査で確認する。
        import er003_v1_n3_01_articles_generate as artgen
        import inspect

        src = inspect.getsource(artgen)
        self.assertEqual(src.count("ec_editor.run_lossless_editor("), 1)


if __name__ == "__main__":
    unittest.main()
