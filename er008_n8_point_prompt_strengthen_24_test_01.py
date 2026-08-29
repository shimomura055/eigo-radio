# ============================================================
# er008_n8_point_prompt_strengthen_24_test_01.py
# ER-008-N8-FINAL-CLOSEOUT-24 Item 2:
# Writer Point Balance prompt強化(Full Storyの言い換え禁止・生成手順の
# 明示・Point One/Two役割分担の明示)の内容を検証する(無料、API呼び出し
# 無し)。
# ============================================================
import unittest

import er003_v1_n3_01_articles_generate as gen


def _prompt() -> str:
    return gen.build_common_block("MASTER_TEXT", "TOPIC_JA", "LEDGER_TEXT")


class TestPointPromptStrengthen24(unittest.TestCase):
    def test_prompt_prohibits_paraphrased_restatement_of_main_story_logic(self):
        prompt = _prompt()
        self.assertIn("言い換えによる重複の禁止", prompt)
        self.assertIn("本文の中心的なlogic・結論の言い換えによる再説明", prompt)

    def test_prompt_lists_expanded_point_content_categories(self):
        prompt = _prompt()
        for category in ("心理", "社会的含意", "別の因果", "実生活上の解釈"):
            self.assertIn(category, prompt)

    def test_prompt_instructs_identifying_main_story_points_before_writing(self):
        prompt = _prompt()
        self.assertIn("生成手順", prompt)
        self.assertIn("まずMain Storyで既に説明した中心的な論点", prompt)

    def test_prompt_requires_point_one_and_two_distinct_roles(self):
        prompt = _prompt()
        self.assertIn("Point One・Point Two同士が互いに同じ役割", prompt)

    def test_prompt_still_forbids_new_facts_outside_ledger_for_points(self):
        prompt = _prompt()
        self.assertIn("Verified Fact Ledgerに無い新しいFactの追加", prompt)

    def test_prompt_still_contains_original_point_balance_prohibitions(self):
        # 既存(強化前)の禁止事項が、強化後も後退していないことを確認する。
        prompt = _prompt()
        self.assertIn("本文の長い再説明", prompt)
        self.assertIn("Fact Ledgerの詳細を網羅的に再掲すること", prompt)
        self.assertIn("Point内で新しい第二の本文を作ること", prompt)

    def test_prompt_still_contains_length_target_unchanged(self):
        # 語数target(30-60/25-70)はER-24の対象外であり、変更していないことを確認する。
        prompt = _prompt()
        self.assertIn("それぞれ30〜60語、許容範囲は25〜70語", prompt)

    def test_default_call_still_backward_compatible_without_blueprint_or_compression(self):
        # shared_point_blueprint_block/evidence_compression未指定時は、
        # 強化後もblueprint/compression blockが挿入されないことを確認する
        # (COMMON_BLOCK_TEMPLATE自体への強化と、オプション機能は独立)。
        prompt = _prompt()
        self.assertNotIn("Shared Point Blueprint", prompt)
        self.assertNotIn("Evidence Compression(今回の記事にのみ適用する追加方針)", prompt)


if __name__ == "__main__":
    unittest.main()
