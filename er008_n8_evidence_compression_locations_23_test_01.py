# ============================================================
# er008_n8_evidence_compression_locations_23_test_01.py
# ER-008-N8-FINAL-PRODUCTION-HARDENING-23 §1: Evidence Compression
# Editorのプロンプトへ「地名・施設名も圧縮対象にする」新原則を追加した
# ことのプロンプト内容テスト(実LLM呼び出しは行わない)。
# ============================================================
import unittest

import er003_v1_n3_01_evidence_compression_editor as ec


class LocationFacilityCompressionPromptTests(unittest.TestCase):
    def test_prompt_mentions_location_and_facility_generalization_as_permitted(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn("地名・空港名・施設名", prompt)
        self.assertIn("Dallas Fort Worth International Airport", prompt)

    def test_prompt_does_not_impose_a_hard_delete_rule_for_locations(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn("地名は必ず削除", prompt)
        self.assertIn("機械的なhard ruleではない", prompt)

    def test_prompt_still_forbids_changing_geographic_meaning_and_facts(self):
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn("地理的な意味", prompt)
        self.assertIn("Factの追加", prompt)
        self.assertIn("Factの削除", prompt)

    def test_prompt_still_forbids_changing_temporal_and_comparison_direction(self):
        # ER-22で追加した日付/数値ルールとの共存確認(既存禁止事項が
        # 引き続き残っていること)。
        prompt = ec.EVIDENCE_COMPRESSION_EDITOR_PROMPT_TEMPLATE.format(article_text="dummy")
        self.assertIn("出来事の時系列の前後関係(temporal direction)を変えること", prompt)
        self.assertIn("比較の向き(comparison direction", prompt)


if __name__ == "__main__":
    unittest.main()
