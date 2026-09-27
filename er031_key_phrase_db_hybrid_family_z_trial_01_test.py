# ============================================================
# er031_key_phrase_db_hybrid_family_z_trial_01_test.py
# KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01
# ============================================================
# 実行: .venv/Scripts/python.exe -m unittest er031_key_phrase_db_hybrid_family_z_trial_01_test -v
#
# 目的: (1) Family Z固有の最終選定ルール(er031_rules)が、Core
# (er029/er028)のStage1候補生成ロジックに一切手を加えていないこと
# (identityチェック)、(2) Z1のprompt文言がZ0(Core標準)と比べて
# category priority(phrase/idiom最低数)だけを意図どおり変更している
# こと、(3) Z1メッセージが決定論的でarticle全文を含まないこと、を
# 実LLM callなしで検証する。
# ============================================================

from __future__ import annotations

import os
import unittest

import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as base
import er029_key_phrase_db_hybrid_trial_04_run as run4
import er031_key_phrase_db_hybrid_family_z_trial_01_rules as z_rules
import er031_key_phrase_db_hybrid_family_z_trial_01_run as z_run

MELOS_PATH = "er026_output/family_z_production_e2e_01/melos/run_01/article.md"
MELOS_TITLE = "The Three-Day Promise"


class CoreUntouchedIdentityTests(unittest.TestCase):
    """er031_rulesがCoreの関数を再実装せず、同一オブジェクトをそのまま
    再利用していること(Stage1候補生成ロジックの二重実装・drift防止)。"""

    def test_z0_message_builder_is_the_same_object_as_core_v4(self):
        self.assertIs(z_rules.build_lightweight_user_message_z0,
                       run4.build_lightweight_user_message_v4)

    def test_z0_core_guidance_is_the_same_object_as_base_selection_guidance(self):
        self.assertIs(z_rules.CORE_SELECTION_GUIDANCE, base.SELECTION_GUIDANCE)

    def test_z1_run_uses_same_stage1_function_object_as_core(self):
        # er031_runモジュールがStage1関数を再実装せず、run4のものを直接
        # importして使っていることをモジュール属性の同一性で確認する。
        self.assertIs(z_run.run4.run_stage1_and_shortlist_v4,
                      run4.run_stage1_and_shortlist_v4)


class FamilyZGuidanceDiffersFromCoreOnlyInWeightingTests(unittest.TestCase):
    """Family Z固有guidanceが、Core標準guidanceと異なる文言であること
    (実質的な差分が存在すること)、かつcategory priorityの重み付け変更
    (phrase/idiom最低数 1個->2個)が意図どおり反映されていること。"""

    def test_family_z_guidance_differs_from_core_guidance(self):
        self.assertNotEqual(z_rules.FAMILY_Z_SELECTION_GUIDANCE, base.SELECTION_GUIDANCE)

    def test_core_guidance_requires_at_least_one_phrase_or_important(self):
        self.assertIn("少なくとも1個", base.SELECTION_GUIDANCE)

    def test_family_z_guidance_raises_phrase_idiom_minimum_to_two(self):
        self.assertIn("少なくとも2個", z_rules.FAMILY_Z_SELECTION_GUIDANCE)
        self.assertIn("phrase / idiom / phrasal verb候補", z_rules.FAMILY_Z_SELECTION_GUIDANCE)

    def test_family_z_guidance_mentions_fiction_and_proper_noun_exclusion(self):
        self.assertIn("物語", z_rules.FAMILY_Z_SELECTION_GUIDANCE)
        self.assertIn("登場人物名", z_rules.FAMILY_Z_SELECTION_GUIDANCE)


class Z1MessageDeterminismAndCandidateEquivalenceTests(unittest.TestCase):
    """Z1メッセージ生成が決定論的であること、かつZ0/Z1で候補一覧
    (shortlist)自体は完全に同一(=Coreは無変更)であり、変わるのは
    guidance文言(末尾)だけであることを確認する。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()
        if not os.path.exists(MELOS_PATH):
            cls.article_text = None
            return
        cls.article_text = open(MELOS_PATH, encoding="utf-8").read()
        cls.s1r = run4.run_stage1_and_shortlist_v4(cls.article_text, cls.dbs, MELOS_TITLE)
        cls.static_instructions = base.extract_static_instructions(
            __import__("er003_b1_p2_keywords").load_prompt_template())

    def setUp(self):
        if self.article_text is None:
            self.skipTest("melos article fixture not present")

    def test_z1_message_is_deterministic(self):
        m1 = z_rules.build_lightweight_user_message_z1(
            MELOS_TITLE, self.s1r["shortlist_info"], self.s1r["shortlist_info"]["sentence_reference"],
            self.static_instructions)
        m2 = z_rules.build_lightweight_user_message_z1(
            MELOS_TITLE, self.s1r["shortlist_info"], self.s1r["shortlist_info"]["sentence_reference"],
            self.static_instructions)
        self.assertEqual(m1, m2)

    def test_z1_message_does_not_contain_full_article_body(self):
        message = z_rules.build_lightweight_user_message_z1(
            MELOS_TITLE, self.s1r["shortlist_info"], self.s1r["shortlist_info"]["sentence_reference"],
            self.static_instructions)
        base.assert_no_full_article_body(message, self.article_text)

    def test_z0_and_z1_share_identical_candidate_sections_only_guidance_differs(self):
        z0_message = z_rules.build_lightweight_user_message_z0(
            MELOS_TITLE, self.s1r["shortlist_info"], self.s1r["shortlist_info"]["sentence_reference"],
            self.static_instructions)
        z1_message = z_rules.build_lightweight_user_message_z1(
            MELOS_TITLE, self.s1r["shortlist_info"], self.s1r["shortlist_info"]["sentence_reference"],
            self.static_instructions)
        z0_head = z0_message.split("【選定方針】")[0]
        z1_head = z1_message.split("【選定方針】")[0]
        self.assertEqual(z0_head, z1_head)
        self.assertNotEqual(z0_message, z1_message)

    def test_melos_proper_nouns_not_selected_as_stage1_candidates(self):
        # Dionysius/Selinuntius/Melosは常に大文字始まりで出現するため、
        # Fix Bのhas_lowercase_occurrenceガードにより候補化されないこと
        # (既存Core仕様、"Echo"の既存回帰と同種の確認)。
        shortlist = self.s1r["shortlist_info"]["shortlist"]
        canonicals = {c["canonical_form"] for c in shortlist}
        for name in ("dionysius", "selinuntius", "melos"):
            self.assertNotIn(name, canonicals)


if __name__ == "__main__":
    unittest.main()
