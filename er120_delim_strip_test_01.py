"""OPEN-591 第2段: 生成側parse_stepb末尾strip + 表示側(render_html_block/render_markdown)共通strip回帰test。"""
import unittest
import er120_part2_grammar_production_01 as g


class T(unittest.TestCase):
    def test_parse_stepb_strips_final_item_tail(self):
        r = g.parse_stepb("=====ITEM 1=====\n【日本語訳】\nA\n=====\n", 1)
        self.assertEqual(r[1], "【日本語訳】\nA")

    def test_parse_stepb_internal_delim_unchanged(self):
        r = g.parse_stepb("=====ITEM 1=====\nA\n=====ITEM 2=====\nB\n=====", 2)
        self.assertEqual(r, {1: "A", 2: "B"})

    def test_parse_stepb_no_delim_bytes_unchanged(self):
        r = g.parse_stepb("=====ITEM 1=====\n  a = b == c\nd  \n", 1)
        self.assertEqual(r[1], "a = b == c\nd")

    def test_strip_helper(self):
        self.assertEqual(g.strip_trailing_delim("x\n====="), "x")
        s = "=====ITEM 2=====\nx ===== y"
        self.assertEqual(g.strip_trailing_delim(s), s)

    def _result(self, tail):
        sel = {"sentence": "I run.", "candidate_id": "c1"}
        sec = {h: "本文です。" for h in g.EXPLANATION_HEADINGS}
        sec[g.EXPLANATION_HEADINGS[-1]] = "最後の本文です。" + tail
        return {"status": "SELECTED", "selection": sel, "sections": sec}

    def test_render_hides_frozen_tail_delim(self):
        for tail in ("\n=====", " =====", "\n=====\n"):
            res = self._result(tail)
            self.assertNotIn("=====", g.render_html_block(res))
            self.assertNotIn("=====", g.render_markdown(res))
            self.assertNotIn("=====", g.compose_study_html("", res))
        # 凍結データ自体は不変
        self.assertTrue(res["sections"][g.EXPLANATION_HEADINGS[-1]].rstrip().endswith("====="))

    def test_render_no_delim_unchanged(self):
        res = self._result("")
        self.assertIn("最後の本文です。", g.render_html_block(res))


if __name__ == "__main__":
    unittest.main()
