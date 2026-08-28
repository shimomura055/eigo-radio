# ============================================================
# er008_point_overlap_qa_18_test_01.py
# ER-008-N8-QA-CONTENT-SPEED-HARDENING-18
# ============================================================
import json
import os
import unittest

import er008_point_overlap_qa_18 as ov

N8_A2 = "er006_output/pool_pilot_01/pool_n8_airport_line/a2/audit/tts_generation_results.json"
N8_B1 = "er006_output/pool_pilot_01/pool_n8_airport_line/b1b/audit/tts_generation_results.json"


class LexicalOverlapLogicTests(unittest.TestCase):
    def test_clearly_different_angle_is_not_flagged(self):
        full_story = ("The company raised prices by 10 percent last quarter. Analysts said the increase "
                       "was driven by higher shipping costs. Customers reacted with complaints on social media.")
        point = ("This kind of pricing decision often reveals how much power a company believes it has over "
                 "loyal customers who are unlikely to switch brands easily.")
        r = ov.flag_possible_paraphrase(point, full_story)
        self.assertFalse(r["flagged"], r)

    def test_near_verbatim_paraphrase_is_flagged(self):
        full_story = ("If a passenger waits too long, there may be a small chance of missing a flight. "
                       "If they stand early, the cost is much smaller: a few unnecessary minutes of waiting.")
        point = ("Waiting too long brings a small chance of missing a flight, while standing early only "
                 "costs a few unnecessary minutes of waiting.")
        r = ov.flag_possible_paraphrase(point, full_story)
        self.assertTrue(r["flagged"], r)

    def test_empty_point_text_does_not_crash(self):
        r = ov.flag_possible_paraphrase("", "Some full story text here.")
        self.assertFalse(r["flagged"])
        self.assertEqual(r["overlap_ratio"], 0.0)


@unittest.skipUnless(os.path.exists(N8_A2) and os.path.exists(N8_B1), "No.8 fixture data not present in this environment")
class No8RealDataTests(unittest.TestCase):
    """No.8実データに基づく回帰テスト(手動レビューで確認済みの重複/
    非重複パターンが、以後もこの検知ロジックで再現されることを守る)。"""

    def test_b1_point_one_flagged_as_paraphrase(self):
        data = json.load(open(N8_B1, encoding="utf-8"))
        segs = data["segments"]
        full_story = segs["full_story_part1"]["canonical_text"] + " " + segs["full_story_part2"]["canonical_text"]
        r = ov.flag_possible_paraphrase(segs["point_one"]["canonical_text"], full_story)
        self.assertTrue(r["flagged"], r)

    def test_point_two_has_lower_overlap_than_point_one(self):
        for path in (N8_A2, N8_B1):
            data = json.load(open(path, encoding="utf-8"))
            segs = data["segments"]
            full_story = segs["full_story_part1"]["canonical_text"] + " " + segs["full_story_part2"]["canonical_text"]
            r_one = ov.lexical_overlap_ratio(segs["point_one"]["canonical_text"], full_story)
            r_two = ov.lexical_overlap_ratio(segs["point_two"]["canonical_text"], full_story)
            self.assertLess(r_two["overlap_ratio"], r_one["overlap_ratio"], (path, r_one, r_two))


if __name__ == "__main__":
    unittest.main()
