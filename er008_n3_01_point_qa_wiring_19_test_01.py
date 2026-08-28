# ============================================================
# er008_n3_01_point_qa_wiring_19_test_01.py
# ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19 Item 3: Point-only
# regenerationのProduction配線(er003_v1_n3_01_articles_generate.py内の
# split_common_sections_for_point_qa/run_point_overlap_qa_and_regenerate)
# の単体テスト。実LLM呼び出しは行わない(fakeクライアントで置き換える)。
# ============================================================
import json
import os
import shutil
import tempfile
import unittest

import er003_v1_n3_01_articles_generate as gen

SAMPLE_ARTICLE = """# A Small Habit At The Gate

Passengers have started lining up before boarding even begins. Airline staff say the
queue often forms minutes before the gate agent calls any group. A few travelers say
they simply want to avoid missing a connection.

### Why do people queue this early

Passengers queue early because they fear missing a connection before boarding even
begins. Airline staff and travelers both say the small chance of missing a connection
outweighs the minor cost of lining up minutes before the gate agent calls any group.

### A different kind of signal

Long lines can also signal distrust in how fairly boarding order will be enforced.

## In one line...

People queue early partly out of habit, and partly out of doubt.
"""


class FakeResponse:
    def __init__(self, text):
        self.output_text = text
        self.model = "fake-model"
        self.id = "fake-id"


class FakeClient:
    def __init__(self, texts):
        self._texts = list(texts)
        self.calls = 0

    class _Responses:
        def __init__(self, outer):
            self._outer = outer

        def create(self, **kwargs):
            self._outer.calls += 1
            return FakeResponse(self._outer._texts.pop(0))

    @property
    def responses(self):
        return FakeClient._Responses(self)


class SplitCommonSectionsTests(unittest.TestCase):
    def test_extracts_full_story_and_both_points(self):
        sections = gen.split_common_sections_for_point_qa(SAMPLE_ARTICLE)
        self.assertIsNotNone(sections)
        self.assertIn("Passengers have started lining up", sections["full_story"])
        self.assertEqual(sections["point_one_heading"], "Why do people queue this early")
        self.assertIn("fear missing a connection", sections["point_one_body"])
        self.assertEqual(sections["point_two_heading"], "A different kind of signal")
        self.assertIn("distrust", sections["point_two_body"])
        # In one lineの本文がpoint_two_bodyへ混入していないことを確認
        self.assertNotIn("People queue early partly", sections["point_two_body"])

    def test_returns_none_for_unexpected_structure(self):
        self.assertIsNone(gen.split_common_sections_for_point_qa("# Title\n\nJust a paragraph, no headings."))


class RunPointOverlapQaAndRegenerateTests(unittest.TestCase):
    def setUp(self):
        self.out_dir = tempfile.mkdtemp(prefix="er008_point_qa_test_")

    def tearDown(self):
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_flags_and_regenerates_the_paraphrasing_point(self):
        # Point One(SAMPLE_ARTICLE)はFull Storyの"missing a connection"ロジックを
        # ほぼそのまま繰り返しているため、overlap_qaでflagされるはず。
        client = FakeClient(["A genuinely different angle about airport culture and imitation."])
        result = gen.run_point_overlap_qa_and_regenerate(
            client, SAMPLE_ARTICLE, "FACT-01: some ledger fact",
            model="fake-model", reasoning_effort=None, out_dir=self.out_dir)
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["report"]["point_one"]["before_overlap"]["flagged"])
        self.assertTrue(result["report"]["point_one"]["applied"])
        self.assertIn("genuinely different angle", result["patched_article_text"])
        self.assertNotIn("outweighs the minor cost of lining up", result["patched_article_text"])
        # Full Story/Point Two/In One Lineは変更されていないこと
        self.assertIn("Passengers have started lining up", result["patched_article_text"])
        self.assertIn("distrust in how fairly boarding order", result["patched_article_text"])
        self.assertIn("People queue early partly out of habit", result["patched_article_text"])
        self.assertEqual(client.calls, 1)
        # 監査ファイルが書き出されていること
        with open(f"{self.out_dir}/point_overlap_qa.json", encoding="utf-8") as f:
            audit = json.load(f)
        self.assertTrue(audit["point_one"]["applied"])

    def test_does_not_call_llm_when_no_point_is_flagged(self):
        # Point Twoは既にFull Storyと重複が低い(distrust/signalという新角度)ため、
        # flagされずLLM呼び出しも発生しないはず。
        client = FakeClient([])
        # Point Oneだけ手動で低重複な文へ差し替えた記事を使う
        low_overlap_article = SAMPLE_ARTICLE.replace(
            "Passengers queue early because they fear missing a connection before boarding even\n"
            "begins. Airline staff and travelers both say the small chance of missing a connection\n"
            "outweighs the minor cost of lining up minutes before the gate agent calls any group.",
            "Group behavior researchers note that queuing can spread through imitation alone.")
        result = gen.run_point_overlap_qa_and_regenerate(
            client, low_overlap_article, "FACT-01: some ledger fact",
            model="fake-model", reasoning_effort=None, out_dir=self.out_dir)
        self.assertEqual(result["status"], "OK")
        self.assertFalse(result["report"]["point_one"]["applied"])
        self.assertFalse(result["report"]["point_two"]["applied"])
        self.assertEqual(client.calls, 0)
        self.assertEqual(result["patched_article_text"], low_overlap_article)


if __name__ == "__main__":
    unittest.main()
