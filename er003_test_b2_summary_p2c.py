# ============================================================
# er003_test_b2_summary_p2c.py
# ER-003-P2C: B2概要のPodcast語り口確定・P2B成果物の正式化のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべて既存成果物(ディスク上のファイル)
# の読み込みと決定的な再計算のみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b2_summary_p2c -v

import inspect
import json
import unittest

import er003_b2_summary as s
import er003_ja_to_en_translation as er003
import er003_v1_p2c_approve as approve

P2B_ROOT = "er003_output/p2b"


class ApprovedSummaryExactMatchTests(unittest.TestCase):
    """要求1-3: 承認済み確定文面が指定文面と完全一致する。"""

    def test_a01_matches_specified_text(self):
        with open(f"{P2B_ROOT}/A01/summary_en_approved.md", encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text, approve.APPROVED_SUMMARIES["A01"])

    def test_a02_matches_specified_text(self):
        with open(f"{P2B_ROOT}/A02/summary_en_approved.md", encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text, approve.APPROVED_SUMMARIES["A02"])

    def test_add03_matches_specified_text(self):
        with open(f"{P2B_ROOT}/ADD03/summary_en_approved.md", encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text, approve.APPROVED_SUMMARIES["ADD03"])


class ApprovedSummaryStructureTests(unittest.TestCase):
    """要求4-22: 承認済み概要が固定見出し・第一文開始・語数・文数条件を
    満たす(P2A sentence splitter使用の決定的再計算)。"""

    def _validate(self, topic_id):
        with open(f"{P2B_ROOT}/{topic_id}/summary_en_approved.md", encoding="utf-8") as f:
            text = f.read()
        return s.validate_summary_structure(text)

    def test_all_three_pass_structure_gate(self):
        for topic_id in ("A01", "A02", "ADD03"):
            result = self._validate(topic_id)
            self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_PASS", msg=topic_id)

    def test_all_three_heading_detected_exactly_once(self):
        for topic_id in ("A01", "A02", "ADD03"):
            self.assertTrue(self._validate(topic_id)["heading_present"], msg=topic_id)

    def test_all_three_opening_ok(self):
        for topic_id in ("A01", "A02", "ADD03"):
            self.assertTrue(self._validate(topic_id)["opening_ok"], msg=topic_id)

    def test_all_three_word_count_within_25_35(self):
        for topic_id in ("A01", "A02", "ADD03"):
            wc = self._validate(topic_id)["word_count"]
            self.assertGreaterEqual(wc, 25, msg=topic_id)
            self.assertLessEqual(wc, 35, msg=topic_id)

    def test_all_three_sentence_count_2_or_3(self):
        for topic_id in ("A01", "A02", "ADD03"):
            sc = self._validate(topic_id)["sentence_count"]
            self.assertIn(sc, (2, 3), msg=topic_id)

    def test_heading_excluded_from_body_word_count(self):
        # "Before You Listen"(3語)は概要本文の語数に含まれない
        for topic_id in ("A01", "A02", "ADD03"):
            with open(f"{P2B_ROOT}/{topic_id}/summary_en_approved.md", encoding="utf-8") as f:
                text = f.read()
            metrics = s.compute_summary_metrics(text)
            self.assertGreater(metrics["total_word_count_including_heading"], metrics["word_count"])

    def test_uses_p2a_sentence_splitter(self):
        src = inspect.getsource(s.validate_summary_structure)
        self.assertIn("er003.split_sentences", src)


class ApprovalMetadataTests(unittest.TestCase):
    """要求6,14,23-26: approval metadata・approved metricsの内容と、
    P2B raw成果物・B2本文・Natural Sourceが無変更であることを確認する。"""

    def _approval(self, topic_id):
        with open(f"{P2B_ROOT}/{topic_id}/summary_approval.json", encoding="utf-8") as f:
            return json.load(f)

    def test_approval_type_is_user_approved_light_edit(self):
        for topic_id in ("A01", "A02", "ADD03"):
            self.assertEqual(self._approval(topic_id)["approval_type"], "USER_APPROVED_LIGHT_EDIT", msg=topic_id)

    def test_no_api_regeneration_recorded(self):
        for topic_id in ("A01", "A02", "ADD03"):
            self.assertFalse(self._approval(topic_id)["api_regeneration"], msg=topic_id)

    def test_no_post_approval_llm_rewrite_recorded(self):
        for topic_id in ("A01", "A02", "ADD03"):
            self.assertFalse(self._approval(topic_id)["post_approval_llm_rewrite"], msg=topic_id)

    def test_approved_sha256_file_matches_approved_md_file(self):
        for topic_id in ("A01", "A02", "ADD03"):
            with open(f"{P2B_ROOT}/{topic_id}/summary_approved_sha256.txt", encoding="utf-8") as f:
                saved_hash = f.read().strip()
            with open(f"{P2B_ROOT}/{topic_id}/summary_en_approved.md", encoding="utf-8") as f:
                text = f.read()
            self.assertEqual(saved_hash, er003.sha256_text(text), msg=topic_id)

    def test_source_generated_summary_sha256_matches_p2b_original(self):
        # P2Bのraw生成原稿(summary_en_reading_copy.md)がP2Cで変更されて
        # いないことをsha256で確認する(承認スクリプトと同じテキスト
        # モード読み込み+er003.sha256_textで計算し、改行コード正規化の
        # 差異による偽陽性を避ける)。
        for topic_id in ("A01", "A02", "ADD03"):
            approval = self._approval(topic_id)
            with open(f"{P2B_ROOT}/{topic_id}/summary_en_reading_copy.md", encoding="utf-8") as f:
                current_text = f.read()
            self.assertEqual(er003.sha256_text(current_text), approval["source_generated_summary_sha256"],
                              msg=topic_id)

    def test_p2b_attempt_artifacts_untouched(self):
        for topic_id in ("A01", "A02", "ADD03"):
            for filename in ("attempt_1_raw_response.json", "attempt_1_summary.md",
                              "attempt_1_structure_check.json", "summary_qa.json", "execution_log.json"):
                # 存在確認のみ(内容のsha256基準値は保存していないため、
                # 少なくともP2Cのスクリプトが削除・上書きしていないことを確認する)
                with open(f"{P2B_ROOT}/{topic_id}/{filename}", encoding="utf-8"):
                    pass

    def test_b2_body_sha256_unchanged(self):
        for topic_id, path in s.B2_INPUT_PATHS.items():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            with open(f"er003_output/p2/{topic_id}/sentence_segments.json", encoding="utf-8") as f:
                segments = json.load(f)
            self.assertEqual(er003.sha256_text(text), segments["source_sha256"], msg=topic_id)

    def test_natural_source_untouched_by_p2c_approve_script(self):
        src = inspect.getsource(approve)
        self.assertNotIn("natural_source", src.lower())
        self.assertNotIn("NATURAL_SOURCE_PATHS", src)


class NoApiCallsTests(unittest.TestCase):
    """要求27-29: P2Cはdiff保存・approved文面確定のみで、API・Key Words・
    TTSは一切実行しない。"""

    def test_approve_script_does_not_import_openai(self):
        src = inspect.getsource(approve)
        self.assertNotIn("import openai", src.lower())
        self.assertNotIn("responses.create", src)

    def test_approve_script_has_no_key_words_or_tts(self):
        src = inspect.getsource(approve)
        self.assertNotIn("key_word", src.lower())
        self.assertNotIn("tts", src.lower())


class ReferenceManifestTests(unittest.TestCase):
    """要求30-31: 正式参照先はsummary_en_approved.md、未編集原稿は監査用。"""

    def test_manifest_file_exists_and_names_approved_as_official(self):
        with open("ER-003-P2C_reference_manifest.md", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("summary_en_approved.md", content)
        self.assertIn("正式配信用", content)

    def test_manifest_names_reading_copy_as_audit_only(self):
        with open("ER-003-P2C_reference_manifest.md", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("summary_en_reading_copy.md", content)
        self.assertIn("生成時監査用", content)


class PromptToneInstructionTests(unittest.TestCase):
    """要求32-33: promptにWe起点の語り口指示が1件だけ存在し、既存条件が
    脱落していない。"""

    def test_tone_instruction_present_exactly_once(self):
        template = s.load_summary_prompt_template()
        self.assertEqual(template.count("We'll look at"), 1)
        self.assertIn("This episode", template)  # 禁止例として言及されているのはOK

    def test_existing_conditions_not_dropped(self):
        template = s.load_summary_prompt_template()
        self.assertIn("25", template)
        self.assertIn("35", template)
        self.assertIn("Before You Listen", template)
        self.assertIn("CEFR B1", template)

    def test_second_sentence_not_hardcoded_in_prompt_instruction(self):
        template = s.load_summary_prompt_template()
        tone_paragraph_start = template.index("概要の第一文は")
        tone_paragraph_end = template.index("\n\n", tone_paragraph_start)
        tone_paragraph = template[tone_paragraph_start:tone_paragraph_end]
        self.assertNotIn("As you listen, notice", tone_paragraph)


if __name__ == "__main__":
    unittest.main()
