# ============================================================
# er013_family_c_future_qa_test_05.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05
# ============================================================
# 目的: er013_family_c_future_qa_05.py(v5構造契約の決定的診断)の
# offline unittest(API呼び出しなし、¥0)。既存er013_family_c_future_
# qa_01の抽出関数を再利用して、合成テキストで検証する。
# ============================================================
from __future__ import annotations

import unittest

import er013_family_c_future_qa_01 as fcq_v1
import er013_family_c_future_qa_05 as fcq5


def _build_article(between_headings: int, after_headings: int, will_outside: bool) -> str:
    """テスト用の合成記事を組み立てる。between_headings=1つ目と2つ目の
    [[IMAGINED]]ブロックのあいだに置く見出し数、after_headings=2つ目の
    ブロックのあとに置く見出し数。"""
    parts = ["## Scene One\n", "[[IMAGINED: around 2035]]\nShe smiles, then hesitates.\n[[/IMAGINED]]\n"]
    for i in range(between_headings):
        parts.append(f"## Extra Between {i}\nSome connecting text.\n")
    parts.append("## Scene Two\n[[IMAGINED: around 2040]]\nHe pauses, then decides to help.\n[[/IMAGINED]]\n")
    for i in range(after_headings):
        will_text = "It will happen." if (will_outside and i == 0) else "It might happen."
        parts.append(f"## Synthesis {i}\n{will_text}\n")
    return "".join(parts)


class ScanV5StructureGateTests(unittest.TestCase):
    def test_pass_case_3_headings_no_will(self):
        article = _build_article(between_headings=0, after_headings=1, will_outside=False)
        blocks = fcq_v1.extract_imagined_blocks(article)
        reader_text = fcq_v1.strip_markers_for_reader(article)
        result = fcq5.scan_v5_structure_gate(article, reader_text, blocks, unhedged_future_hits=[])
        self.assertEqual(result["overall_status"], "PASS", result["fail_reasons"])
        self.assertEqual(result["heading_count"], 3)

    def test_fail_extra_heading_between_scenes(self):
        article = _build_article(between_headings=2, after_headings=1, will_outside=False)
        blocks = fcq_v1.extract_imagined_blocks(article)
        reader_text = fcq_v1.strip_markers_for_reader(article)
        result = fcq5.scan_v5_structure_gate(article, reader_text, blocks, unhedged_future_hits=[])
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(any("headings_between_scenes" in r for r in result["fail_reasons"]))

    def test_fail_wrong_heading_count_after_scene2(self):
        article = _build_article(between_headings=0, after_headings=2, will_outside=False)
        blocks = fcq_v1.extract_imagined_blocks(article)
        reader_text = fcq_v1.strip_markers_for_reader(article)
        result = fcq5.scan_v5_structure_gate(article, reader_text, blocks, unhedged_future_hits=[])
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(any("headings_after_scene2" in r for r in result["fail_reasons"]))
        self.assertTrue(any("heading_count" in r for r in result["fail_reasons"]))

    def test_fail_unhedged_will_outside_markers(self):
        article = _build_article(between_headings=0, after_headings=1, will_outside=True)
        blocks = fcq_v1.extract_imagined_blocks(article)
        reader_text = fcq_v1.strip_markers_for_reader(article)
        layer1_text = fcq_v1.build_layer1_placeholder_text(article)
        hits = fcq_v1.detect_unhedged_future_claims(layer1_text)
        self.assertTrue(hits, "合成テキストのwillが検出されるはず")
        result = fcq5.scan_v5_structure_gate(article, reader_text, blocks, unhedged_future_hits=hits)
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(any("unhedged_will_outside_markers" in r for r in result["fail_reasons"]))

    def test_fail_wrong_imagined_block_count(self):
        article = "## Only One\n[[IMAGINED: around 2035]]\nShe smiles.\n[[/IMAGINED]]\n## Synthesis\nIt might happen.\n"
        blocks = fcq_v1.extract_imagined_blocks(article)
        reader_text = fcq_v1.strip_markers_for_reader(article)
        result = fcq5.scan_v5_structure_gate(article, reader_text, blocks, unhedged_future_hits=[])
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(any("imagined_blocks_count" in r for r in result["fail_reasons"]))


class CountEventsPerSceneTests(unittest.TestCase):
    def test_counts_sentences_per_block(self):
        blocks = [
            {"timeframe": "around 2035", "body": "She sees the box. She lifts it. She smiles at the result."},
            {"timeframe": "around 2040", "body": "He waits."},
        ]
        result = fcq5.count_events_per_scene(blocks)
        self.assertEqual(result[0]["sentence_count"], 3)
        self.assertEqual(result[1]["sentence_count"], 1)

    def test_empty_blocks(self):
        self.assertEqual(fcq5.count_events_per_scene([]), [])


if __name__ == "__main__":
    unittest.main()
