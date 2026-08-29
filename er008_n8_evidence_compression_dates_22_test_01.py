# ============================================================
# er008_n8_evidence_compression_dates_22_test_01.py
# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22 Item 3: Evidence
# Compression Editorのプロンプトへ「日付・数値も圧縮対象にする」新原則を
# 追加したことのプロンプト内容テスト(実LLM呼び出しは行わない)。
# ============================================================
import unittest

import er003_v1_n3_01_evidence_compression_editor as ec


class DateNumberCompressionPromptTests(unittest.TestCase):
    def test_prompt_mentions_date_and_number_generalization_as_permitted(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn("日付", prompt)
        self.assertIn("hard rule", prompt)

    def test_prompt_still_forbids_changing_temporal_direction_and_comparison_direction(self):
        # 日付・数値の圧縮を許可しても、既存の禁止事項(時系列・比較の向きを
        # 変えないこと)はそのまま残っていなければならない。
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn("出来事の時系列の前後関係(temporal direction)を変えること", prompt)
        self.assertIn("比較の向き(comparison direction", prompt)
        self.assertIn("Factの追加", prompt)
        self.assertIn("Factの削除", prompt)

    def test_prompt_does_not_impose_a_single_date_hard_rule(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn("日付は必ず1個にする", prompt)
        self.assertIn("機械的なhard ruleではない", prompt)


if __name__ == "__main__":
    unittest.main()
