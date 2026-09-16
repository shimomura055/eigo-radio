# ============================================================
# er013_family_c_production_test_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01
#         (委任A: Family C 2仕様のProduction wiring)
# ============================================================
# `er013_family_c_production_01.py`(Family C Story TTS segmentation原則+
# A2 Comment理解ガイド型Contract)の決定的テスト(API呼び出しなし)。
from __future__ import annotations

import json
import re
import unittest
from unittest import mock

import er013_family_c_production_01 as fam_c


class PlanStorySegmentsUnitTests(unittest.TestCase):
    """plan_story_segmentsの単体テスト(承認原則: 同一Voice統合/Voice境界
    分割/Comment境界分割/目安超過分割/短segment許容理由付与/固定値上書き
    なし)。"""

    def test_same_voice_consecutive_paragraphs_merge(self):
        paragraphs = ["Hello there.", "This continues the same idea.", "And a third sentence."]
        flat = fam_c.build_flat_voice_chunks(paragraphs, {})
        segs = fam_c.plan_story_segments(flat)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0]["voice"], "narrator")
        self.assertEqual(segs[0]["source_paragraph_indices"], [0, 1, 2])

    def test_voice_change_forces_split(self):
        paragraphs = ['She said, "I am ready."', "He nodded."]
        flat = fam_c.build_flat_voice_chunks(paragraphs, {"robot": ["robot"]})
        # 引用符はwindowにkeywordが無いためdefault narrator扱いになるが、
        # override指定で強制的にvoice変化を作れることを確認する。
        flat2 = [(0, "narrator", 'She said, '), (0, "robot", '"I am ready."'), (1, "narrator", "He nodded.")]
        segs = fam_c.plan_story_segments(flat2)
        voices = [s["voice"] for s in segs]
        self.assertEqual(voices, ["narrator", "robot", "narrator"])
        # Voice境界による短segmentが理由付きで許容されること
        self.assertIn("分割不可避", segs[1]["split_reason"])

    def test_comment_or_scene_boundary_forces_split_even_if_same_voice(self):
        flat = [(0, "narrator", "Part one."), (1, "narrator", "Part two."), (2, "narrator", "Part three.")]
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={2})
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0]["source_paragraph_indices"], [0, 1])
        self.assertEqual(segs[1]["source_paragraph_indices"], [2])

    def test_word_guideline_auto_split_at_nearest_paragraph_boundary(self):
        long_word_para = " ".join(f"word{i}" for i in range(80))
        long_word_para2 = " ".join(f"term{i}" for i in range(80))
        flat = [(0, "narrator", long_word_para + "."), (1, "narrator", long_word_para2 + ".")]
        segs = fam_c.plan_story_segments(
            flat, target_words=100, soft_max_words=120, hard_avoid_words=150)
        self.assertEqual(len(segs), 2)
        for s in segs:
            self.assertIn("auto_split_hard_avoid_exceeded", s["warnings"][0])
            self.assertLessEqual(s["word_count"], 90)

    def test_hard_avoid_exceeded_unsplittable_single_paragraph_is_warning_only_no_block(self):
        one_giant_paragraph = " ".join(f"word{i}" for i in range(200))
        flat = [(0, "narrator", one_giant_paragraph)]
        segs = fam_c.plan_story_segments(flat, hard_avoid_words=150)
        self.assertEqual(len(segs), 1)
        self.assertTrue(any("hard_avoid_exceeded_unsplittable" in w for w in segs[0]["warnings"]))

    def test_soft_max_exceeded_records_warning_but_does_not_split(self):
        paragraph = " ".join(f"word{i}" for i in range(130))
        flat = [(0, "narrator", paragraph)]
        segs = fam_c.plan_story_segments(flat, soft_max_words=120, hard_avoid_words=150)
        self.assertEqual(len(segs), 1)
        self.assertTrue(any("soft_max_exceeded" in w for w in segs[0]["warnings"]))

    def test_caller_supplied_boundaries_are_not_overwritten_by_fixed_values(self):
        # force_split_before_paragraphsを変えると結果が追随することを確認
        # (固定値で上書きされていないことの確認)。
        flat = [(0, "narrator", "A."), (1, "narrator", "B."), (2, "narrator", "C.")]
        segs_no_force = fam_c.plan_story_segments(flat)
        segs_forced = fam_c.plan_story_segments(flat, force_split_before_paragraphs={1})
        self.assertEqual(len(segs_no_force), 1)
        self.assertEqual(len(segs_forced), 2)


class ApprovedEpisodeReproductionTests(unittest.TestCase):
    """承認済み4 episode(Memory A2/B1、Digital Twins A2/B1)のsegmentationを
    plan_story_segmentsで再現できることを確認する(approved成果物との
    segment数・最長語数一致)。記事本文はProduction module化前のTrial
    出力物(reader_facing_article*.txt)を読むが、本テストはTrial scriptを
    import・実行しない(article_config.jsonの値をここに複製し、production
    moduleのみを検証する)。"""

    def _load_paragraphs(self, path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        return fam_c.split_into_paragraphs(text)

    def test_memory_a2_reproduces_approved_10_segments_max89(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_future_trial_08/memory/reader_facing_article.txt")
        self.assertEqual(len(paragraphs), 29)
        flat = fam_c.build_flat_voice_chunks(
            paragraphs, {"device": ["screen", "device", "robot", "storage unit"], "brother": ["brother"]},
            quote_voice_override_paragraphs={2: "device", 4: "device", 14: "brother"})
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={9, 20, 24})
        self.assertEqual(len(segs), 10)
        self.assertEqual(max(s["word_count"] for s in segs), 89)
        reconstructed = fam_c.reconstruct_article_from_segments(segs, paragraphs)
        self.assertEqual(reconstructed, "\n\n".join(paragraphs))

    def test_memory_b1_reproduces_approved_10_segments_max91(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_episode_trial_10/memory_b1/reader_facing_article_b1.txt")
        self.assertEqual(len(paragraphs), 26)
        flat = fam_c.build_flat_voice_chunks(
            paragraphs, {"device": ["screen", "device", "robot", "storage unit"], "brother": ["brother"]})
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={11, 13, 21})
        self.assertEqual(len(segs), 10)
        self.assertEqual(max(s["word_count"] for s in segs), 91)

    def test_digital_twins_a2_reproduces_approved_22_segments_max99(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt")
        self.assertEqual(len(paragraphs), 33)
        override = {i: "twin" for i in (3, 5, 11, 13, 19, 21, 25)}
        flat = fam_c.build_flat_voice_chunks(
            paragraphs, {"twin": ["echo", "twin", "digital twin"]},
            quote_voice_override_paragraphs=override,
            display_paragraph_voice={16: "twin"},
            restrict_quote_splitting_to_paragraphs=override.keys())
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={23})
        self.assertEqual(len(segs), 22)
        self.assertEqual(max(s["word_count"] for s in segs), 99)
        narrator_n = sum(1 for s in segs if s["voice"] == "narrator")
        twin_n = sum(1 for s in segs if s["voice"] == "twin")
        self.assertEqual((narrator_n, twin_n), (12, 10))

    def test_digital_twins_b1_reproduces_approved_24_segments_max97(self):
        paragraphs = self._load_paragraphs(
            "er013_output/family_c_episode_trial_10/twins_b1/reader_facing_article_b1.txt")
        self.assertEqual(len(paragraphs), 34)
        flat = fam_c.build_flat_voice_chunks(paragraphs, {"twin": ["echo", "twin", "digital twin"]})
        segs = fam_c.plan_story_segments(flat, force_split_before_paragraphs={9})
        self.assertEqual(len(segs), 24)
        self.assertEqual(max(s["word_count"] for s in segs), 97)
        narrator_n = sum(1 for s in segs if s["voice"] == "narrator")
        twin_n = sum(1 for s in segs if s["voice"] == "twin")
        self.assertEqual((narrator_n, twin_n), (13, 11))


class A2CommentQualityCheckTests(unittest.TestCase):
    def test_banned_phrase_detected(self):
        ok, reasons = fam_c.check_a2_comment_quality(
            "さあ、これから始まる物語を聞いてみましょう。" + "あ" * 40)
        self.assertFalse(ok)
        self.assertIn("banned_phrase_found", reasons)

    def test_empty_text_rejected(self):
        ok, reasons = fam_c.check_a2_comment_quality("")
        self.assertFalse(ok)
        self.assertEqual(reasons, ["empty_text"])

    def test_clean_text_within_range_passes(self):
        text = "レナは小さな箱を持っています。" * 3
        ok, reasons = fam_c.check_a2_comment_quality(text, min_chars=10, max_chars=200)
        self.assertTrue(ok)
        self.assertEqual(reasons, [])

    def test_too_short_flagged(self):
        ok, reasons = fam_c.check_a2_comment_quality("短い。", min_chars=40)
        self.assertFalse(ok)
        self.assertTrue(any("too_short" in r for r in reasons))

    def test_prompt_uses_contract_constants(self):
        prompt = fam_c.build_family_c_a2_comment_prompt(1, "テスト事実")
        self.assertIn("テスト事実", prompt)
        self.assertIn("聞いてみましょう", prompt)  # 禁止語句の説明自体は含む(指示文なので正常)


class GenerateFamilyCA2CommentRetryTests(unittest.TestCase):
    """retry/regeneration経路が同一関数(generate_family_c_a2_comment)を
    呼ぶことをモックで確認する(禁止語句が出た場合に同一Contractで
    自動的に再生成し、2回目で合格すれば成功として返すことの確認)。"""

    def test_retries_on_banned_phrase_and_succeeds_with_same_contract(self):
        calls = []

        def fake_run_support_text(client, role_instruction, context_block, model=None):
            calls.append(role_instruction)
            if len(calls) == 1:
                return {"status": "OK", "text": "さあ聞いてみましょう。" + "あ" * 40}
            return {"status": "OK", "text": "レナは小さな銀色の箱を大切に持っています。" * 2}

        result = fam_c.generate_family_c_a2_comment(
            client=None, comment_num=1, article_text="dummy", content_facts="事実X",
            max_retries=1, run_support_text_fn=fake_run_support_text, model="dummy-model")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], calls[1])  # 同一prompt(同一Contract)で再試行
        self.assertTrue(result["ok"])
        self.assertEqual(result["contract"], "FAMILY_C_A2_COMMENT_ROLE_JA_1")

    def test_raises_after_exhausting_retries(self):
        def always_banned(client, role_instruction, context_block, model=None):
            return {"status": "OK", "text": "耳を澄ませてください。" + "い" * 40}

        with self.assertRaises(RuntimeError):
            fam_c.generate_family_c_a2_comment(
                client=None, comment_num=2, article_text="dummy", content_facts="事実Y",
                max_retries=1, run_support_text_fn=always_banned, model="dummy-model")

    def test_b1_comment_not_provided_by_this_contract(self):
        # B1 CommentはこのContractに存在しない(B1誤適用防止の構造的ガード)。
        with self.assertRaises(RuntimeError):
            fam_c.guard_a2_only("b1")
        # 例外を投げない(＝A2は許可)
        fam_c.guard_a2_only("a2")


class TrialScriptIndependenceTests(unittest.TestCase):
    """Production module/runnerがTrial script(er013_family_c_episode_
    trial_1[012]_*.py)をimport・参照しないことのGrepベース確認。"""

    def test_no_trial_script_import_in_production_module(self):
        with open("er013_family_c_production_01.py", encoding="utf-8") as f:
            content = f.read()
        hits = re.findall(r"import\s+er013_family_c_episode_trial|from\s+er013_family_c_episode_trial",
                           content)
        self.assertEqual(hits, [])

    def test_no_trial_script_import_in_runner(self):
        with open("er013_family_c_production_runner_01.py", encoding="utf-8") as f:
            content = f.read()
        hits = re.findall(r"import\s+er013_family_c_episode_trial|from\s+er013_family_c_episode_trial",
                           content)
        self.assertEqual(hits, [])

    def test_no_b1_comment_contract_constants_exist(self):
        """B1 Comment用のFAMILY_C_B1_COMMENT系定数が存在しないこと
        (誤適用防止をコード構造で担保しているという設計の確認)。"""
        with open("er013_family_c_production_01.py", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("FAMILY_C_B1_COMMENT", content)


if __name__ == "__main__":
    unittest.main()
