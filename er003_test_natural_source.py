# ============================================================
# er003_test_natural_source.py
# ER-003-P2 Part A: Natural English Source確定のテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_natural_source -v

import json
import os
import unittest

import er003_natural_source as ns


class A01DiffTests(unittest.TestCase):
    """要求1-2: A01の差分が指定2見出しだけ。本文・数字・固有名詞は不変。"""

    def test_a01_diff_is_exactly_two_headings(self):
        raw = ns.load_p1b_raw_article("A01")
        natural = ns.build_natural_source_text("A01", raw)
        raw_lines = raw.splitlines()
        natural_lines = natural.splitlines()
        self.assertEqual(len(raw_lines), len(natural_lines))
        diff_lines = [(i, r, n) for i, (r, n) in enumerate(zip(raw_lines, natural_lines)) if r != n]
        self.assertEqual(len(diff_lines), 2)

    def test_a01_point_one_heading_changed_to_creator(self):
        raw = ns.load_p1b_raw_article("A01")
        natural = ns.build_natural_source_text("A01", raw)
        self.assertIn("Point One: Messi Wasn't the Scorer—He Was the Creator", natural)
        self.assertNotIn("He Was the Finisher", natural)

    def test_a01_point_two_heading_changed_to_attack(self):
        raw = ns.load_p1b_raw_article("A01")
        natural = ns.build_natural_source_text("A01", raw)
        self.assertIn("Point Two: One Team Substituted to Defend; the Other, to Attack", natural)
        self.assertNotIn("the Other, to Win", natural)

    def test_a01_title_intro_body_unchanged(self):
        raw = ns.load_p1b_raw_article("A01")
        natural = ns.build_natural_source_text("A01", raw)
        # タイトル行・導入・数字(85分, 1966, 39歳相当の"39")は変更されない
        self.assertEqual(raw.splitlines()[0], natural.splitlines()[0])
        for fact in ["85th minute", "1966", "39,", "81st minute"]:
            self.assertIn(fact, raw)
            self.assertIn(fact, natural)

    def test_missing_expected_heading_raises(self):
        with self.assertRaises(ValueError):
            ns.build_natural_source_text("A01", "no matching heading here")


class A02Add03IdenticalTests(unittest.TestCase):
    """要求3-4: A02・ADD03はP1B本文と一致(byte-for-byte)。"""

    def test_a02_identical_to_p1b_raw(self):
        raw = ns.load_p1b_raw_article("A02")
        natural = ns.build_natural_source_text("A02", raw)
        self.assertEqual(raw, natural)

    def test_add03_identical_to_p1b_raw(self):
        raw = ns.load_p1b_raw_article("ADD03")
        natural = ns.build_natural_source_text("ADD03", raw)
        self.assertEqual(raw, natural)


class SavedArtifactTests(unittest.TestCase):
    """要求5-7: sha256保存。P1B raw成果物を上書きしない。legacy attempt
    1本文を推測復元しない。"""

    def test_sha256_files_exist_and_match_content(self):
        for topic_id in ["A01", "A02", "ADD03"]:
            path = f"er003_output/p1b/{topic_id}/natural_source_sha256.txt"
            approved_path = f"er003_output/p1b/{topic_id}/natural_source_approved.md"
            if not (os.path.exists(path) and os.path.exists(approved_path)):
                self.skipTest(f"{path}または{approved_path}が見つかりません")
            with open(path, encoding="utf-8") as f:
                saved_hash = f.read().strip()
            with open(approved_path, encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(saved_hash, ns.sha256_text(content))

    def test_p1b_raw_article_not_overwritten(self):
        for topic_id in ["A01", "A02", "ADD03"]:
            path = ns.P1B_RAW_ARTICLE_PATHS[topic_id]
            if not os.path.exists(path):
                self.skipTest(f"{path}が見つかりません")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            # A01の場合、raw版はFinisher/Winのまま(Creator/Attackへ書き換わっていない)
            if topic_id == "A01":
                self.assertIn("He Was the Finisher", content)
                self.assertIn("the Other, to Win", content)

    def test_legacy_run_note_present_for_a01_and_a02(self):
        for topic_id in ["A01", "A02"]:
            path = f"er003_output/p1b/{topic_id}/natural_source_approval.json"
            if not os.path.exists(path):
                self.skipTest(f"{path}が見つかりません")
            with open(path, encoding="utf-8") as f:
                metadata = json.load(f)
            self.assertIn("ATTEMPT_1_BODY_NOT_PRESERVED_IN_LEGACY_P1B_RUN", metadata.get("legacy_run_note", ""))

    def test_approval_metadata_has_sha256_and_edits(self):
        raw = ns.load_p1b_raw_article("A01")
        natural = ns.build_natural_source_text("A01", raw)
        metadata = ns.build_approval_metadata("A01", raw, natural)
        self.assertEqual(metadata["natural_source_sha256"], ns.sha256_text(natural))
        self.assertEqual(len(metadata["edits"]), 2)

    def test_a02_metadata_carries_forward_qa_notes(self):
        raw = ns.load_p1b_raw_article("A02")
        natural = ns.build_natural_source_text("A02", raw)
        metadata = ns.build_approval_metadata("A02", raw, natural)
        self.assertTrue(metadata["qa_notes_carried_forward"])
        self.assertTrue(metadata["identical_to_p1b_raw"])


if __name__ == "__main__":
    unittest.main()
